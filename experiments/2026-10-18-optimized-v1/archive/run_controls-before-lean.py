"""Reproduce controlled output faults and optional live, unscored boundaries."""

import argparse
import asyncio
import copy
import json
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from grounding_verifier.cli import read_json, write_json
from grounding_verifier.dataset import digest
from grounding_verifier.domain import (
    VerificationReport,
    VerifyError,
    VerifyRequest,
    validate_report,
)
from grounding_verifier.evaluation import output_hash
from grounding_verifier.llm import MAX_OUTPUT, MODEL, AnthropicProvider, LLMVerifier, execute
from grounding_verifier.prompts import MINIMAL, REFINED


class ScriptedProvider:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = 0

    async def generate(self, payload, prompt, trace):
        self.calls += 1
        return next(self.outputs)


def metadata(kind):
    return {
        "format_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "kind": kind,
        "script_digest": digest(Path(__file__).read_text(encoding="utf-8")),
        "llm_source_digest": digest(Path("src/grounding_verifier/llm.py").read_text("utf-8")),
        "minimal_prompt_digest": digest(MINIMAL),
        "optimized_prompt_digest": digest(REFINED),
        "records": [],
    }


async def run_faults(path):
    run = read_json("experiments/2026-10-16-dev-v2/minimal-dev-v2.json")
    from grounding_verifier.dataset import load_cases

    case = load_cases(Path("data/dev.jsonl"))[0]
    valid = run["records"][0]["output"]
    validate_report(VerificationReport.model_validate(valid), case.context_passages)
    valid_json = json.dumps(valid, ensure_ascii=False)
    faults = {"malformed_json": '{"claims": ['}
    for name in (
        "boolean_index",
        "out_of_range",
        "fabricated_quote",
        "missing_evidence",
        "bad_label",
    ):
        bad = copy.deepcopy(valid)
        claim = bad["claims"][0]
        if name == "boolean_index":
            claim["citations"][0]["index"] = True
        elif name == "out_of_range":
            claim["citations"][0]["index"] = len(case.context_passages)
        elif name == "fabricated_quote":
            claim["citations"][0]["quote"] = "This sentence was never supplied as source evidence."
        elif name == "missing_evidence":
            claim["citations"] = []
        else:
            claim["verdict"] = "PROBABLY_SUPPORTED"
        faults[name] = json.dumps(bad, ensure_ascii=False)
    result = metadata("controlled_scripted_faults_not_live_model_results")
    result["fixture_output_digest"] = digest(valid)
    result["limitations"] = (
        "Provider replies are scripted: these are not API calls, natural error frequencies, "
        "latency or semantic-improvement measurements. A recovered reply is the legal fixture."
    )
    for fault, raw in faults.items():
        for method in ("minimal", "optimized"):
            provider = ScriptedProvider([raw, valid_json])
            trace = {}
            record = {"fault": fault, "method": method, "injected_response": raw}
            try:
                report = await execute(
                    LLMVerifier(provider, method == "optimized"), case.request(), trace
                )
                record.update(status="ok", output=report.model_dump(mode="json"))
            except VerifyError as exc:
                record.update(status="error", error={"code": exc.code, "status": exc.status})
            record.update(logical_calls=provider.calls, trace=trace)
            result["records"].append(record)
    # Recovery is bounded: two invalid replies must still fail, without a third call.
    provider = ScriptedProvider(["bad", "still bad", valid_json])
    try:
        await execute(LLMVerifier(provider, True), case.request(), {})
    except VerifyError as exc:
        result["irrecoverable_control"] = {"status": exc.status, "logical_calls": provider.calls}
    else:
        raise AssertionError("unbounded recovery unexpectedly succeeded")
    assert result["irrecoverable_control"] == {"status": 502, "logical_calls": 2}
    for record in result["records"]:
        assert (record["status"] == "ok") == (record["method"] == "optimized")
        assert record["logical_calls"] == (2 if record["method"] == "optimized" else 1)
    write_json(path, result)
    print(f"Saved {len(result['records'])} controlled fault results; no API calls.")


async def run_boundaries(path):
    cases = read_json("data/development-challenges-v1/boundaries.json")
    result = metadata("live_engineering_boundary_checks_excluded_from_quality_benchmark")
    result.update(model=MODEL, effort="medium", max_output=MAX_OUTPUT, input_digest=digest(cases))
    provider = AnthropicProvider()
    try:
        for method in ("minimal", "optimized"):
            for case in cases:
                trace = {}
                record = {
                    "case_id": case["id"],
                    "method": method,
                    "expected": case["expected"],
                    "request": case["request"],
                    "reason": case["reason"],
                    "trace": trace,
                }
                try:
                    report = await execute(
                        LLMVerifier(provider, method == "optimized"),
                        VerifyRequest.model_validate(case["request"]),
                        trace,
                    )
                    output = report.model_dump(mode="json")
                    claims = output["claims"]
                    passed = (
                        not claims
                        if case["expected"] == "empty_claims"
                        else (
                            bool(claims)
                            and all(
                                c["verdict"] == "UNSUPPORTED" and not c["citations"] for c in claims
                            )
                        )
                    )
                    record.update(status="ok", output=output, boundary_passed=passed)
                except VerifyError as exc:
                    record.update(
                        status="error",
                        output=None,
                        boundary_passed=False,
                        error={"code": exc.code, "status": exc.status},
                    )
                record["output_hash"] = output_hash(record)
                result["records"].append(record)
                path.with_suffix(".partial.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                print(f"{method}/{case['id']}: {record['status']}", flush=True)
        write_json(path, result)
    finally:
        await provider.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--faults-out", type=Path)
    parser.add_argument("--boundaries-out", type=Path)
    args = parser.parse_args()
    if not args.faults_out and not args.boundaries_out:
        parser.error("choose at least one output")
    for path in (args.faults_out, args.boundaries_out):
        if path and path.exists():
            parser.error("output already exists; use a new path")
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
    load_dotenv()
    if args.faults_out:
        asyncio.run(run_faults(args.faults_out))
    if args.boundaries_out:
        asyncio.run(run_boundaries(args.boundaries_out))


if __name__ == "__main__":
    main()
