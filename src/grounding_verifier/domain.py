"""Public contract and deterministic invariants. No model or HTTP dependencies."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Verdict(StrEnum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNSUPPORTED = "UNSUPPORTED"


class VerifyRequest(StrictModel):
    context_passages: list[str]
    generated_answer: str = Field(max_length=10_000)

    @model_validator(mode="after")
    def limits(self):
        if sum(map(len, self.context_passages)) > 50_000:
            raise ValueError("context_passages exceed the 50,000-character limit")
        return self


class Citation(StrictModel):
    index: StrictInt
    quote: str = Field(min_length=1)


class Claim(StrictModel):
    claim_text: str = Field(min_length=1)
    verdict: Verdict
    reasoning: str = Field(min_length=1)
    citations: list[Citation]

    @model_validator(mode="after")
    def invariant(self):
        if not self.claim_text.strip() or not self.reasoning.strip():
            raise ValueError("claim_text and reasoning must contain text")
        if (self.verdict == Verdict.UNSUPPORTED) != (len(self.citations) == 0):
            raise ValueError("UNSUPPORTED requires []; other verdicts require citations")
        if any(not c.quote.strip() for c in self.citations):
            raise ValueError("citations cannot contain blank quotes")
        return self


class VerificationReport(StrictModel):
    claims: list[Claim]


def validate_report(report: VerificationReport, passages: list[str]) -> VerificationReport:
    for claim in report.claims:
        for citation in claim.citations:
            if not 0 <= citation.index < len(passages):
                raise ValueError("citation index is outside context_passages")
            if citation.quote not in passages[citation.index]:
                raise ValueError("citation quote is not an exact verbatim substring")
    return report


class VerifyError(Exception):
    def __init__(self, code: str, message: str, status: int = 502):
        super().__init__(message)
        self.code, self.status = code, status


def bind_claim_ids(
    claims: list[str], judgments: list[dict], passages: list[str]
) -> VerificationReport:
    """Reject missing/duplicate/foreign IDs; never let a judgment rewrite a claim."""
    expected = [f"c{i}" for i in range(len(claims))]
    ids = [item.get("id") for item in judgments]
    if len(ids) != len(expected) or set(ids) != set(expected):
        raise ValueError("judgments must contain every claim ID exactly once")
    by_id = {item["id"]: item for item in judgments}
    result = []
    for claim_id, claim_text in zip(expected, claims, strict=True):
        item = dict(by_id[claim_id])
        item.pop("id")
        if "claim_text" in item:
            raise ValueError("judgment cannot rewrite claim_text")
        result.append(Claim(claim_text=claim_text, **item))
    return validate_report(VerificationReport(claims=result), passages)
