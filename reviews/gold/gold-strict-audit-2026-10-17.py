"""Read-only canonical-data audit; temporary manifests stay under .cache.

Run from repository root with .venv/Scripts/python.exe <this file>.
No model calls, approval changes, or benchmark execution.
"""

import copy
import hashlib
import json
import re
import statistics
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from grounding_verifier.dataset import (  # noqa: E402
    Case,
    dataset_hash,
    load_cases,
    require_frozen_test,
    validate_splits,
)
from grounding_verifier.gold_review import render_gold_review  # noqa: E402


def normalized(text):
    return " ".join(text.casefold().split())


def audit():
    data = ROOT / "data"
    splits = {name: load_cases(data / f"{name}.jsonl") for name in ("dev", "test")}
    manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))
    result = {
        "scope": "Current working tree; AI audit, not human approval",
        "splits": validate_splits(data),
        "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [data / "dev.jsonl", data / "test.jsonl", data / "manifest.json"]
        },
        "generated_review_current": (ROOT / "reviews/gold-dataset-review.md").read_text(
            encoding="utf-8"
        )
        == render_gold_review(data),
        "dev_approval_hash_matches": manifest["dev"]["dataset_hash"] == dataset_hash(splits["dev"]),
        "profiles": {},
    }
    for name, cases in splits.items():
        claims = [g for c in cases for g in c.gold_claims]
        citations = [(c, q) for c in cases for g in c.gold_claims for q in g.citations]
        words = [len(re.findall(r"\b\w+\b", " ".join(c.context_passages))) for c in cases]
        result["profiles"][name] = {
            "facts": len(claims),
            "passage_counts": dict(Counter(len(c.context_passages) for c in cases)),
            "source_words_min_median_max": [min(words), statistics.median(words), max(words)],
            "citation_objects": len(citations),
            "valid_verbatim_citations": sum(
                q.quote in c.context_passages[q.index] for c, q in citations
            ),
            "whole_passage_citations": sum(
                q.quote == c.context_passages[q.index] for c, q in citations
            ),
            "blank_annotation_reasons": sum(not g.annotation_reason.strip() for g in claims),
            "duplicate_normalized_inputs": len(cases)
            - len(
                {
                    (
                        tuple(normalized(p) for p in c.context_passages),
                        normalized(c.generated_answer),
                    )
                    for c in cases
                }
            ),
            "claims_with_multiple_cited_passages": sum(
                len({q.index for q in g.citations}) > 1 for g in claims
            ),
        }
    result["cross_split_exact_source_overlap"] = sorted(
        {normalized(p) for c in splits["dev"] for p in c.context_passages}
        & {normalized(p) for c in splits["test"] for p in c.context_passages}
    )
    probes = {}
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gold-audit-", dir=cache) as temporary:
        directory = Path(temporary)
        for label, test_state in {
            "current_draft": manifest["test"],
            "draft_with_reviewer_frozen_and_matching_hash": {
                "review_status": "draft",
                "reviewed_by": "audit fixture",
                "frozen": True,
                "dataset_hash": dataset_hash(splits["test"]),
            },
            "rejected_with_reviewer_frozen_and_matching_hash": {
                "review_status": "rejected",
                "reviewed_by": "audit fixture",
                "frozen": True,
                "dataset_hash": dataset_hash(splits["test"]),
            },
            "string_false_frozen": {
                "review_status": "approved",
                "reviewed_by": "audit fixture",
                "frozen": "false",
                "dataset_hash": dataset_hash(splits["test"]),
            },
            "whitespace_reviewer": {
                "review_status": "approved",
                "reviewed_by": "   ",
                "frozen": True,
                "dataset_hash": dataset_hash(splits["test"]),
            },
        }.items():
            (directory / "manifest.json").write_text(
                json.dumps({"test": test_state}), encoding="utf-8"
            )
            try:
                require_frozen_test(directory, splits["test"])
                probes[label] = "ACCEPTED"
            except ValueError:
                probes[label] = "REJECTED"
    result["freeze_gate_probes_synthetic_only"] = probes
    original = splits["dev"][0].model_dump(mode="json")
    blank = copy.deepcopy(original)
    blank["gold_claims"][0]["annotation_reason"] = "   "
    try:
        Case.model_validate(blank)
        result["blank_annotation_reason_probe"] = "ACCEPTED"
    except ValueError:
        result["blank_annotation_reason_probe"] = "REJECTED"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    audit()
