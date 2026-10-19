import asyncio
import json

import pytest

from grounding_verifier.domain import VerificationReport, VerifyError, VerifyRequest
from grounding_verifier.llm import LLMVerifier, execute, expand_cited_passages, extra_attempt
from grounding_verifier.prompts import LEAN, MINIMAL, REFINED, REFINED_V2

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


def test_prompt_experiments_cannot_modify_minimal_baseline():
    assert LLMVerifier(None).prompt == MINIMAL
    assert LLMVerifier(None, True).prompt == LEAN  # owner-selected default
    assert LLMVerifier(None, True).citation_policy == "span"
    assert LLMVerifier(None, True, prompt_variant="refined-v1").prompt == REFINED
    assert LLMVerifier(None, True, prompt_variant="refined-v2").prompt == REFINED_V2
    assert LLMVerifier(None, True, prompt_variant="lean-v1").prompt == LEAN
    with pytest.raises(ValueError, match="minimal baseline"):
        LLMVerifier(None, prompt_variant="refined-v2")
    with pytest.raises(ValueError, match="unknown"):
        LLMVerifier(None, True, prompt_variant="unrecorded")
    with pytest.raises(ValueError, match="minimal baseline"):
        LLMVerifier(None, citation_policy="passage")


def test_passage_expansion_preserves_raw_output_and_does_not_add_sources():
    original = VerificationReport.model_validate(GOOD)
    expanded = expand_cited_passages(original, ["A works. Only one A exists.", "Uncited text."])
    assert original.claims[0].citations[0].quote == "A works."
    assert expanded.claims[0].citations[0].quote == "A works. Only one A exists."
    assert [c.index for c in expanded.claims[0].citations] == [0]
    assert expanded.claims[0].claim_text == original.claims[0].claim_text


@pytest.mark.parametrize("change", ["quote", "index"])
def test_expansion_rejects_invalid_original_citations(change):
    bad = VerificationReport.model_validate(GOOD)
    if change == "quote":
        bad.claims[0].citations[0].quote = "Fabricated."
    else:
        bad.claims[0].citations[0].index = 9
    with pytest.raises(ValueError):
        expand_cited_passages(bad, ["A works."])


def test_expansion_preserves_unsupported_and_deduplicates_passage_indices():
    raw = {
        "claims": [
            {
                **GOOD["claims"][0],
                "citations": [
                    {"index": 0, "quote": "A works."},
                    {"index": 0, "quote": "one A"},
                ],
            },
            {
                "claim_text": "B works.",
                "verdict": "UNSUPPORTED",
                "reasoning": "Absent.",
                "citations": [],
            },
        ]
    }
    report = expand_cited_passages(
        VerificationReport.model_validate(raw),
        ["A works. Only one A exists."],
    )
    assert len(report.claims[0].citations) == 1
    assert report.claims[1].citations == []


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


def test_llm_expansion_keeps_first_output_and_verdict_without_an_extra_call():
    trace = {}
    provider = FakeProvider([GOOD])
    request = VerifyRequest(
        context_passages=["A works. Only one A exists."], generated_answer="A works."
    )
    report = asyncio.run(
        execute(
            LLMVerifier(provider, True, citation_policy="passage"),
            request,
            trace,
        )
    )
    assert provider.calls == 1
    assert trace["first_output"] == GOOD
    assert report.claims[0].verdict.value == "SUPPORTED"
    assert report.claims[0].citations[0].quote == request.context_passages[0]
    assert trace["citation_expansion"]["original_quote_characters"] == len("A works.")


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
