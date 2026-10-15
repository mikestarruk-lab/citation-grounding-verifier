import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from .domain import Claim, VerificationReport, VerifyRequest, validate_report

CATEGORIES = {"supported", "distortion", "extrinsic", "multi_passage"}


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


class GoldClaim(Claim):
    id: str
    annotation_reason: str


class Case(VerifyRequest):
    id: str
    source_group: str
    category: Literal["supported", "distortion", "extrinsic", "multi_passage"]
    provenance: str
    gold_claims: list[GoldClaim] = Field(min_length=1)

    @model_validator(mode="after")
    def gold_valid(self):
        if len({c.id for c in self.gold_claims}) != len(self.gold_claims):
            raise ValueError("duplicate gold claim IDs")
        claims = [
            Claim.model_validate(c.model_dump(exclude={"id", "annotation_reason"}))
            for c in self.gold_claims
        ]
        validate_report(VerificationReport(claims=claims), self.context_passages)
        return self

    def request(self):
        return VerifyRequest(
            context_passages=self.context_passages, generated_answer=self.generated_answer
        )


def load_cases(path: Path) -> list[Case]:
    cases = [
        Case.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len({c.id for c in cases}) != len(cases):
        raise ValueError("duplicate case IDs")
    return cases


def dataset_hash(cases: list[Case]):
    return digest([c.model_dump(mode="json") for c in cases])


def validate_splits(directory: Path):
    dev, test = load_cases(directory / "dev.jsonl"), load_cases(directory / "test.jsonl")
    if {c.source_group for c in dev} & {c.source_group for c in test}:
        raise ValueError("source groups leak across splits")
    if {c.id for c in dev} & {c.id for c in test}:
        raise ValueError("case IDs overlap across splits")
    if len(dev) < 8 or len(test) < 20:
        raise ValueError("expected at least 8 development and 20 test cases")
    result = {}
    for name, cases in (("dev", dev), ("test", test)):
        counts = Counter(c.category for c in cases)
        if set(counts) != CATEGORIES:
            raise ValueError("all four categories are required in each split")
        result[name] = {
            "cases": len(cases),
            "categories": dict(counts),
            "hash": dataset_hash(cases),
            "labels": dict(Counter(c.verdict.value for x in cases for c in x.gold_claims)),
        }
    return result


def require_frozen_test(directory: Path, cases: list[Case]):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    test = manifest.get("test", {})
    if not (
        test.get("reviewed_by")
        and test.get("frozen")
        and test.get("dataset_hash") == dataset_hash(cases)
    ):
        raise ValueError("Test data needs human gold review and a matching frozen manifest first")
