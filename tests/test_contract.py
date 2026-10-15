import asyncio

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from grounding_verifier.api import app
from grounding_verifier.baseline import LexicalVerifier
from grounding_verifier.domain import (
    VerificationReport,
    VerifyRequest,
    bind_claim_ids,
    validate_report,
)


def report(index=0, quote="Hello.", verdict="SUPPORTED"):
    return {
        "claims": [
            {
                "claim_text": "Hello.",
                "verdict": verdict,
                "reasoning": "Evidence.",
                "citations": [{"index": index, "quote": quote}],
            }
        ]
    }


@pytest.mark.parametrize("index", [True, False, "0", 0.0, None])
def test_strict_indices(index):
    with pytest.raises(ValidationError):
        VerificationReport.model_validate(report(index=index))


@pytest.mark.parametrize(
    "index,quote", [(-1, "Hello."), (1, "Hello."), (0, "hello."), (0, "Hello!"), (0, "Hello. ")]
)
def test_raw_evidence_rejected(index, quote):
    with pytest.raises(ValueError):
        validate_report(VerificationReport.model_validate(report(index, quote)), ["Hello."])


@pytest.mark.parametrize("quote", ["", " ", "\n"])
def test_blank_quotes_rejected(quote):
    with pytest.raises(ValueError):
        VerificationReport.model_validate(report(quote=quote))


def test_unsupported_and_supported_citation_constraints():
    with pytest.raises(ValueError):
        VerificationReport.model_validate(report(verdict="UNSUPPORTED"))
    obj = report()
    obj["claims"][0]["citations"] = []
    with pytest.raises(ValueError):
        VerificationReport.model_validate(obj)


def test_unicode_no_normalization():
    with pytest.raises(ValueError):
        validate_report(VerificationReport.model_validate(report(quote="'Hello.'")), ["‘Hello.’"])


def test_ids_complete_and_no_rewrite():
    judgment = {"id": "c0", "verdict": "UNSUPPORTED", "reasoning": "Absent.", "citations": []}
    assert bind_claim_ids(["Fact."], [judgment], []).claims[0].claim_text == "Fact."
    for items in (
        [],
        [judgment, judgment],
        [{**judgment, "id": "c2"}],
        [{**judgment, "claim_text": "Changed"}],
    ):
        with pytest.raises(ValueError):
            bind_claim_ids(["Fact."], items, [])


def test_http_contract(monkeypatch):
    monkeypatch.setenv("VERIFIER_METHOD", "lexical")
    client = TestClient(app)
    body = {
        "context_passages": ["CedarCache does not persist entries across restarts."],
        "generated_answer": "CedarCache persists entries across restarts.",
    }
    assert client.post("/verify", json=body).status_code == 200
    assert client.post("/verify", json={**body, "generated_answer": ""}).json() == {"claims": []}
    assert client.post("/verify", json={**body, "generated_answer": "Thanks!"}).json() == {
        "claims": []
    }
    empty = client.post("/verify", json={**body, "context_passages": []}).json()
    assert empty["claims"][0]["verdict"] == "UNSUPPORTED"
    assert client.post("/verify", json={**body, "generated_answer": "a" * 10001}).status_code == 422
    assert (
        client.post("/verify", json={**body, "context_passages": ["a" * 50001]}).status_code == 422
    )
    assert client.post("/verify", json={"generated_answer": "a"}).status_code == 422


def test_source_permutation_and_removal():
    verifier = LexicalVerifier()

    async def check(passages):
        return await verifier.verify(
            VerifyRequest(
                context_passages=passages, generated_answer="The sky service is available."
            ),
            {},
        )

    a = asyncio.run(check(["Noise only.", "The sky service is available."]))
    b = asyncio.run(check(["The sky service is available.", "Noise only."]))
    assert a.claims[0].citations[0].index == 1
    assert b.claims[0].citations[0].index == 0
    assert asyncio.run(check(["Noise only."])).claims[0].verdict == "UNSUPPORTED"
