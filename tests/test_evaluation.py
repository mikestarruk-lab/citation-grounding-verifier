import copy
import json
from pathlib import Path

import pytest

from grounding_verifier.dataset import Case, dataset_hash, require_frozen_test, validate_splits
from grounding_verifier.evaluation import output_hash, raw_citations, review_template, score


def fixture():
    case = Case.model_validate(
        {
            "id": "case",
            "source_group": "one",
            "category": "distortion",
            "provenance": "synthetic",
            "context_passages": ["A works. B does not work."],
            "generated_answer": "A works. B works.",
            "gold_claims": [
                {
                    "id": "g1",
                    "claim_text": "A works.",
                    "verdict": "SUPPORTED",
                    "reasoning": "Explicit",
                    "citations": [{"index": 0, "quote": "A works."}],
                    "annotation_reason": "explicit",
                },
                {
                    "id": "g2",
                    "claim_text": "B works.",
                    "verdict": "CONTRADICTED",
                    "reasoning": "Negated",
                    "citations": [{"index": 0, "quote": "B does not work."}],
                    "annotation_reason": "negated",
                },
            ],
        }
    )
    output = {
        "claims": [
            g.model_dump(mode="json", exclude={"id", "annotation_reason"}) for g in case.gold_claims
        ]
    }
    record = {
        "case_id": case.id,
        "status": "ok",
        "output": output,
        "trace": {"first_output": output},
    }
    run = {
        "dataset_hash": dataset_hash([case]),
        "method": "test",
        "mode": "e2e",
        "records": [record],
    }
    reviews = review_template(run, {case.id: case})
    reviews[0].update(status="approved", reviewer="test reviewer")
    for i, unit in enumerate(reviews[0]["units"]):
        unit.update(gold_id=f"g{i + 1}", evidence_sufficient=True)
    return case, run, reviews


def test_perfect_and_pending():
    case, run, reviews = fixture()
    assert score(run, [case], reviews)["f1"] == 1
    pending = score(run, [case])
    assert pending["semantic_status"] == "pending_human_review"
    assert "f1" not in pending


def test_failed_requests_stay_in_denominator():
    case, run, _ = fixture()
    run["records"][0].update(status="error", output=None, error={"code": "upstream"})
    result = score(run, [case])
    assert result["f1"] == 0 and result["success_rate"] == 0
    assert result["counts"]["fn"] == 2
    assert result["final_quote_validity"] is None


def test_wrong_verdict_fp_and_fn():
    case, run, _ = fixture()
    run["records"][0]["output"]["claims"][1]["verdict"] = "SUPPORTED"
    reviews = review_template(run, {case.id: case})
    reviews[0].update(status="approved", reviewer="test reviewer")
    for i, unit in enumerate(reviews[0]["units"]):
        unit.update(gold_id=f"g{i + 1}", evidence_sufficient=i == 0)
    result = score(run, [case], reviews)
    assert result["f1"] == 0.5
    assert result["counts"]["fp"] == result["counts"]["fn"] == 1
    assert result["false_support_rate"] == 1 and result["coverage"] == 1


def test_duplicate_extra_prediction_is_fp():
    case, run, _ = fixture()
    run["records"][0]["output"]["claims"].append(
        copy.deepcopy(run["records"][0]["output"]["claims"][0])
    )
    reviews = review_template(run, {case.id: case})
    reviews[0].update(status="approved", reviewer="test reviewer")
    for unit, gold_id in zip(reviews[0]["units"], ["g1", "g2", "g1"], strict=True):
        unit.update(gold_id=gold_id, evidence_sufficient=True)
    result = score(run, [case], reviews)
    assert result["counts"]["tp"] == 2 and result["counts"]["fp"] == 1
    assert result["f1"] == 0.8


def test_compound_prediction_gets_semantic_credit_but_not_atomic_credit():
    case, run, _ = fixture()
    claims = run["records"][0]["output"]["claims"]
    claims[0]["claim_text"] = "A works and B works."
    del claims[1:]
    reviews = review_template(run, {case.id: case})
    reviews[0].update(
        status="approved",
        reviewer="test reviewer",
        units=[
            {
                "prediction_index": 0,
                "text": "A works.",
                "gold_id": "g1",
                "evidence_sufficient": True,
            },
            {
                "prediction_index": 0,
                "text": "B works.",
                "gold_id": "g2",
                "evidence_sufficient": False,
            },
        ],
    )
    result = score(run, [case], reviews)
    assert result["coverage"] == 1 and result["f1"] == 0.5 and result["atomicity"] == 0


def test_stale_and_incomplete_reviews_rejected():
    case, run, reviews = fixture()
    reviews[0]["output_hash"] = "stale"
    with pytest.raises(ValueError, match="hash"):
        score(run, [case], reviews)
    reviews[0]["output_hash"] = output_hash(run["records"][0])
    reviews[0]["units"].pop()
    with pytest.raises(ValueError, match="every prediction"):
        score(run, [case], reviews)


def test_independent_citation_oracle_rejects_booleans():
    assert raw_citations(
        {"claims": [{"citations": [{"index": True, "quote": "A"}]}]}, ["A", "A"]
    ) == (0, 1)


def test_fixed_gold_diagnostic_failures_are_wrong():
    case, run, _ = fixture()
    run["mode"] = "gold"
    run["records"][0].update(status="error", output=None, error={"code": "upstream"})
    result = score(run, [case])
    assert result["macro_f1"] == 0
    assert result["confusion"]["SUPPORTED"]["ERROR"] == 1


def test_dataset_structure_and_freeze_gate():
    counts = validate_splits(Path("data"))
    assert counts["dev"]["cases"] == 8 and counts["test"]["cases"] == 20
    from grounding_verifier.dataset import load_cases

    with pytest.raises(ValueError, match="human gold review"):
        require_frozen_test(Path("data"), load_cases(Path("data/test.jsonl")))


APPROVED_TEST = {"review_status": "approved", "reviewed_by": "Owner", "frozen": True}


@pytest.mark.parametrize(
    "change",
    [
        {"review_status": "draft"},
        {"review_status": "rejected"},
        {"frozen": "false"},
        {"frozen": 1},
        {"reviewed_by": "   "},
        {"reviewed_by": None},
        {"dataset_hash": "0" * 64},
    ],
)
def test_freeze_gate_rejects_unapproved_or_mistyped_manifest(tmp_path, change):
    from grounding_verifier.dataset import load_cases

    cases = load_cases(Path("data/test.jsonl"))
    test = {**APPROVED_TEST, "dataset_hash": dataset_hash(cases), **change}
    (tmp_path / "manifest.json").write_text(json.dumps({"test": test}), encoding="utf-8")
    with pytest.raises(ValueError, match="human gold review"):
        require_frozen_test(tmp_path, cases)


def test_freeze_gate_accepts_exact_approval(tmp_path):
    from grounding_verifier.dataset import load_cases

    cases = load_cases(Path("data/test.jsonl"))
    test = {**APPROVED_TEST, "dataset_hash": dataset_hash(cases)}
    (tmp_path / "manifest.json").write_text(json.dumps({"test": test}), encoding="utf-8")
    require_frozen_test(tmp_path, cases)


@pytest.mark.parametrize("blank", ["", "   "])
def test_gold_annotation_reason_must_contain_text(blank):
    raw = fixture()[0].model_dump(mode="json")
    raw["gold_claims"][0]["annotation_reason"] = blank
    with pytest.raises(ValueError, match="annotation_reason"):
        Case.model_validate(raw)
