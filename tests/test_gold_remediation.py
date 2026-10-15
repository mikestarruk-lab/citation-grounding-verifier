import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from grounding_verifier.dataset import dataset_hash, load_cases
from grounding_verifier.evaluation import review_template, score
from grounding_verifier.gold_review import render_gold_review


def endpoint_fixture():
    case = next(c for c in load_cases(Path("data/test.jsonl")) if c.id == "test-05")
    expected = [
        ("g1", "GET /status returns HTTP 200."),
        ("g3", "GET /status returns a JSON body."),
        ("g2", "GET /status requires no authentication."),
    ]
    assert [(g.id, g.claim_text) for g in case.gold_claims] == expected
    claims = [
        g.model_dump(mode="json", exclude={"id", "annotation_reason"}) for g in case.gold_claims
    ]
    run = {
        "mode": "e2e",
        "method": "regression fixture, not a live model result",
        "dataset_hash": dataset_hash([case]),
        "records": [{"case_id": case.id, "status": "ok", "output": {"claims": claims}}],
    }
    return case, run


def reviewed_score(case, run, gold_ids):
    reviews = review_template(run, {case.id: case})
    reviews[0].update(status="approved", reviewer="synthetic regression fixture")
    for unit, gid in zip(reviews[0]["units"], gold_ids, strict=True):
        unit.update(gold_id=gid, evidence_sufficient=True)
    return score(run, [case], reviews)


def test_correct_fine_split_gets_full_credit():
    case, run = endpoint_fixture()
    result = reviewed_score(case, run, ["g1", "g3", "g2"])
    assert result["f1"] == result["coverage"] == result["atomicity"] == 1
    assert result["counts"]["tp"] == 3


def test_compound_output_can_match_without_receiving_atomic_credit():
    case, run = endpoint_fixture()
    claim = run["records"][0]["output"]["claims"][0]
    claim.update(
        claim_text=case.generated_answer,
        citations=[{"index": 0, "quote": case.context_passages[0]}],
    )
    run["records"][0]["output"]["claims"] = [claim]
    reviews = review_template(run, {case.id: case})
    reviews[0].update(
        status="approved",
        reviewer="synthetic regression fixture",
        units=[
            {
                "prediction_index": 0,
                "text": g.claim_text,
                "gold_id": g.id,
                "evidence_sufficient": True,
            }
            for g in case.gold_claims
        ],
    )
    result = score(run, [case], reviews)
    assert result["f1"] == 1 and result["atomicity"] == 0


def test_missing_body_is_still_an_omission():
    case, run = endpoint_fixture()
    del run["records"][0]["output"]["claims"][1]
    result = reviewed_score(case, run, ["g1", "g2"])
    assert result["counts"]["fn"] == 1 and result["counts"].get("fp", 0) == 0
    assert result["f1"] == 0.8


def test_repeated_body_is_still_an_extra_prediction():
    case, run = endpoint_fixture()
    claims = run["records"][0]["output"]["claims"]
    claims.append(copy.deepcopy(claims[1]))
    result = reviewed_score(case, run, ["g1", "g3", "g2", "g3"])
    assert result["counts"]["tp"] == 3 and result["counts"]["fp"] == 1
    assert result["counts"]["fn"] == 0


def test_old_dataset_cannot_reuse_current_reviews():
    case, run = endpoint_fixture()
    # Annotation-only changes also invalidate the canonical hash.
    changed = case.model_copy(deep=True)
    changed.gold_claims[0].reasoning += " Revised explanation."
    with pytest.raises(ValueError, match="dataset hash mismatch"):
        score(run, [changed])


def test_review_document_is_current_and_contains_every_explanation():
    rendered = render_gold_review(Path("data"))
    assert Path("reviews/gold-dataset-review.md").read_text(encoding="utf-8") == rendered
    cases = load_cases(Path("data/dev.jsonl")) + load_cases(Path("data/test.jsonl"))
    assert sum(len(c.gold_claims) for c in cases) == 44
    assert rendered.count("**reasoning:**") == rendered.count("**annotation_reason:**") == 44
    for case in cases:
        assert case.source_group in rendered and case.provenance in rendered
        assert case.generated_answer in rendered
        for passage in case.context_passages:
            assert passage in rendered
        for claim in case.gold_claims:
            assert claim.reasoning in rendered and claim.annotation_reason in rendered
            assert claim.reasoning not in {
                "The cited specification entails this assertion, including its conditions.",
                "The supplied specification directly rules out this assertion.",
                "The supplied specification does not establish this assertion.",
            }


def test_review_check_detects_an_explanation_edit(tmp_path):
    directory = tmp_path / "data"
    shutil.copytree("data", directory)
    out = tmp_path / "review.md"
    out.write_text(render_gold_review(directory), encoding="utf-8")
    path = directory / "dev.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    rows[0]["gold_claims"][0]["annotation_reason"] += " Human correction pending."
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "grounding_verifier.cli",
            "gold-review",
            "--data",
            str(directory),
            "--out",
            str(out),
            "--check",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "stale" in result.stderr
