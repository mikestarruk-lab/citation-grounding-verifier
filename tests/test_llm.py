import asyncio
import json

import pytest

from grounding_verifier.domain import VerifyError, VerifyRequest
from grounding_verifier.llm import LLMVerifier, execute, extra_attempt

GOOD = {
    "claims": [
        {
            "claim_text": "A works.",
            "verdict": "SUPPORTED",
            "reasoning": "Explicit.",
            "citations": [{"index": 0, "quote": "A works."}],
        }
    ]
}
REQUEST = VerifyRequest(context_passages=["A works."], generated_answer="A works.")


class FakeProvider:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = 0

    async def generate(self, payload, prompt, trace):
        self.calls += 1
        output = next(self.outputs)
        if isinstance(output, Exception):
            raise output
        return json.dumps(output) if isinstance(output, dict) else output


def test_minimal_never_silently_repairs():
    provider = FakeProvider(["not json", GOOD])
    with pytest.raises(VerifyError) as exc:
        asyncio.run(execute(LLMVerifier(provider), REQUEST, {}))
    assert exc.value.status == 502
    assert provider.calls == 1


def test_single_repair_preserves_first_output():
    bad = {"claims": [{**GOOD["claims"][0], "citations": [{"index": 0, "quote": "Invented"}]}]}
    trace = {}
    provider = FakeProvider([bad, GOOD])
    result = asyncio.run(execute(LLMVerifier(provider, optimized=True), REQUEST, trace))
    assert result.claims[0].citations[0].quote == "A works."
    assert trace["first_output"] == bad
    assert trace["repair_count"] == trace["extra_calls"] == 1


def test_repair_failure_remains_error():
    with pytest.raises(VerifyError):
        asyncio.run(execute(LLMVerifier(FakeProvider(["bad", "bad"]), True), REQUEST, {}))


def test_retry_budget_shared():
    trace = {}
    extra_attempt(trace)
    extra_attempt(trace)
    with pytest.raises(VerifyError):
        extra_attempt(trace)


def test_fixed_claims_cannot_be_rewritten():
    with pytest.raises(VerifyError):
        asyncio.run(execute(LLMVerifier(FakeProvider([GOOD])), REQUEST, {}, ["Different fact."]))


def test_empty_answer_no_call():
    p = FakeProvider([])
    result = asyncio.run(
        execute(LLMVerifier(p), VerifyRequest(context_passages=[], generated_answer=""), {})
    )
    assert not result.claims and p.calls == 0


@pytest.mark.parametrize("status", [502, 503, 504])
def test_infrastructure_error_is_not_unsupported(status):
    p = FakeProvider([VerifyError("test", "upstream", status)])
    with pytest.raises(VerifyError) as exc:
        asyncio.run(execute(LLMVerifier(p), REQUEST, {}))
    assert exc.value.status == status
