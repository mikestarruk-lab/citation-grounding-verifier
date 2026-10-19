"""Bounded model calls. Infrastructure errors are never semantic verdicts."""

import asyncio
import json
import os
import time
from pathlib import Path

from anthropic import (
    APIConnectionError,
    APIStatusError,
    AsyncAnthropic,
)
from filelock import Timeout as LockTimeout

from .budget import Budget
from .domain import Citation, VerificationReport, VerifyError, VerifyRequest, validate_report
from .prompts import FIXED, LEAN, MINIMAL, REFINED, REFINED_V2

MODEL = "claude-haiku-5-5"
# Owner-confirmed optimized method (experiments/method-freeze-2026-10-19.json).
SELECTED_VARIANT = "lean-v1"
MAX_OUTPUT = 8192
# Reserve a full 1M input window at the higher rate, plus max output. Actual usage settles it.
MAX_CALL_USD = 0.50 + MAX_OUTPUT * 2.50 / 1_000_000


def schema_for_api():
    def simplify(value):
        if isinstance(value, list):
            return [simplify(v) for v in value]
        if isinstance(value, dict):
            return {
                k: simplify(v)
                for k, v in value.items()
                if k not in {"minLength", "maxLength", "minimum", "maximum", "title"}
            }
        return value

    return simplify(VerificationReport.model_json_schema())


def extra_attempt(trace: dict):
    if trace.get("extra_calls", 0) >= 2:
        raise VerifyError("retry_budget_exhausted", "Request retry budget exhausted", 503)
    trace["extra_calls"] = trace.get("extra_calls", 0) + 1


class AnthropicProvider:
    def __init__(self):
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise VerifyError("configuration", "ANTHROPIC_API_KEY is not configured", 503)
        self.model = os.getenv("VERIFIER_MODEL", MODEL)
        if self.model != MODEL:
            raise VerifyError(
                "configuration", "Model change requires a reviewed price configuration", 503
            )
        try:
            self.budget = Budget(
                Path(os.getenv("VERIFIER_BUDGET_PATH", ".budget/ledger.json")),
                float(os.getenv("VERIFIER_BUDGET_USD", "20")),
            )
        except (ValueError, OSError) as exc:
            raise VerifyError("configuration", "Invalid budget configuration", 503) from exc
        self.client = AsyncAnthropic(max_retries=0, timeout=90)
        self.first = True

    async def close(self):
        await self.client.close()

    async def generate(self, payload: dict, prompt: str, trace: dict) -> str:
        while True:
            try:
                reservation = self.budget.reserve(MAX_CALL_USD)
            except (OSError, ValueError, KeyError, TypeError, LockTimeout) as exc:
                raise VerifyError(
                    "budget_ledger", "Budget ledger is unavailable or invalid", 503
                ) from exc
            attempt = {
                "reservation": reservation,
                "first_request_in_client": self.first,
                "status": "started",
                "cost_usd": None,
                "reserved_usd": MAX_CALL_USD,
            }
            self.first = False
            trace.setdefault("attempts", []).append(attempt)
            started = time.perf_counter()
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=MAX_OUTPUT,
                    system=prompt,
                    messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
                    thinking={"type": "adaptive"},
                    output_config={
                        "effort": "medium",
                        "format": {"type": "json_schema", "schema": schema_for_api()},
                    },
                )
                usage = response.usage.model_dump()
                input_tokens = (
                    usage["input_tokens"]
                    + (usage.get("cache_read_input_tokens") or 0)
                    + (usage.get("cache_creation_input_tokens") or 0)
                )
                input_rate, output_rate = (0.50, 2.50) if input_tokens > 100_000 else (0.10, 0.50)
                # No explicit caching requested. Charge all input conservatively at uncached rate.
                cost = (
                    input_tokens * input_rate + usage["output_tokens"] * output_rate
                ) / 1_000_000
                raw = "".join(block.text for block in response.content if block.type == "text")
                attempt.update(
                    status="received",
                    cost_usd=cost,
                    usage=usage,
                    stop_reason=response.stop_reason,
                    raw_text=raw,
                    response_id=response.id,
                    model=response.model,
                )
                try:
                    self.budget.settle(reservation, cost)
                except (OSError, ValueError, KeyError, TypeError, LockTimeout) as exc:
                    attempt["ledger_settlement_failed"] = True
                    raise VerifyError(
                        "budget_ledger", "Budget settlement failed; audit required", 503
                    ) from exc
                if response.stop_reason != "end_turn":
                    raise VerifyError(
                        "incomplete_output", "Model response was refused or truncated"
                    )
                return raw
            except (APIConnectionError, APIStatusError) as exc:
                status = getattr(exc, "status_code", None)
                attempt.update(
                    status="upstream_error", error_type=type(exc).__name__, http_status=status
                )
                transient = (
                    isinstance(exc, APIConnectionError)
                    or status in {408, 409, 429}
                    or (status is not None and status >= 500)
                )
                if not transient:
                    raise VerifyError(
                        "upstream_rejected", "Provider rejected the request", 502
                    ) from exc
                if trace.get("extra_calls", 0) >= 2:
                    raise VerifyError(
                        "upstream_unavailable",
                        "Upstream retry budget exhausted",
                        503,
                    ) from exc
                extra_attempt(trace)
                await asyncio.sleep(min(trace["extra_calls"], 2))
                # Usage unavailable: leave reservation in ledger rather than assume zero cost.
            finally:
                attempt["latency_seconds"] = time.perf_counter() - started


def expand_cited_passages(report: VerificationReport, passages: list[str]) -> VerificationReport:
    """Expand only already-valid citations; never use expansion to hide a bad quote/index."""
    validate_report(report, passages)
    expanded = report.model_copy(deep=True)
    for claim in expanded.claims:
        indices = dict.fromkeys(citation.index for citation in claim.citations)
        claim.citations = [Citation(index=i, quote=passages[i]) for i in indices]
    return validate_report(expanded, passages)


class LLMVerifier:
    def __init__(
        self,
        provider,
        optimized: bool = False,
        *,
        prompt_variant: str | None = None,
        citation_policy: str = "span",
    ):
        self.provider = provider
        self.optimized = optimized
        self.name = "optimized" if optimized else "minimal"
        variants = {"refined-v1": REFINED, "refined-v2": REFINED_V2, "lean-v1": LEAN}
        if not optimized and prompt_variant is not None:
            raise ValueError("minimal baseline does not accept prompt variants")
        if optimized and prompt_variant is not None and prompt_variant not in variants:
            raise ValueError("unknown optimized prompt variant")
        self.prompt_variant = (prompt_variant or SELECTED_VARIANT) if optimized else "minimal"
        self.prompt = variants[self.prompt_variant] if optimized else MINIMAL
        if citation_policy not in {"span", "passage"}:
            raise ValueError("unknown citation policy")
        if not optimized and citation_policy != "span":
            raise ValueError("minimal baseline does not accept citation expansion")
        self.citation_policy = citation_policy

    async def verify(self, request: VerifyRequest, trace: dict):
        if not request.generated_answer.strip():
            trace["first_output"] = {"claims": []}
            return VerificationReport(claims=[])
        return await self._run(request.model_dump(), request.context_passages, trace)

    async def verify_claims(self, passages: list[str], claims: list[str], trace: dict):
        return await self._run(
            {"context_passages": passages, "fixed_claims": claims}, passages, trace, claims
        )

    async def _run(self, payload, passages, trace, fixed_claims=None):
        prompt = self.prompt + ("\n" + FIXED if fixed_claims is not None else "")
        for index in range(2 if self.optimized else 1):
            raw = await self.provider.generate(payload, prompt, trace)
            try:
                parsed = json.loads(raw)
                if index == 0:
                    trace["first_output"] = parsed
                report = VerificationReport.model_validate(parsed)
                if (
                    fixed_claims is not None
                    and [c.claim_text for c in report.claims] != fixed_claims
                ):
                    raise ValueError("fixed claims were omitted, reordered, added or rewritten")
                validate_report(report, passages)
                if self.citation_policy == "passage":
                    before = sum(len(c.quote) for claim in report.claims for c in claim.citations)
                    report = expand_cited_passages(report, passages)
                    trace["citation_expansion"] = {
                        "policy": "full_already_cited_passages",
                        "original_quote_characters": before,
                        "final_quote_characters": sum(
                            len(c.quote) for claim in report.claims for c in claim.citations
                        ),
                    }
                return report
            except (ValueError, TypeError) as exc:
                trace.setdefault("validation_errors", []).append(str(exc))
                if not self.optimized or index == 1:
                    raise VerifyError(
                        "invalid_model_output", "Model output violates the contract"
                    ) from exc
                extra_attempt(trace)
                trace["repair_count"] = 1
                payload = {
                    **payload,
                    "invalid_response": raw,
                    "validation_error": str(exc),
                    "repair_instruction": "Correct the invalid response using only original data.",
                }
        raise AssertionError("unreachable")


async def execute(verifier, request: VerifyRequest, trace: dict, fixed_claims=None):
    """One deadline includes every call, backoff, and repair."""
    started = time.perf_counter()
    try:
        async with asyncio.timeout(90):
            if fixed_claims is None:
                report = await verifier.verify(request, trace)
            else:
                report = await verifier.verify_claims(request.context_passages, fixed_claims, trace)
            return validate_report(report, request.context_passages)
    except TimeoutError as exc:
        raise VerifyError(
            "deadline_exceeded", "Request exceeded its 90-second deadline", 504
        ) from exc
    finally:
        trace["latency_seconds"] = time.perf_counter() - started
