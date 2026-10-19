import copy
import math
from types import SimpleNamespace

import pytest

from grounding_verifier.domain import Verdict
from grounding_verifier.threshold_study import project_labels, thresholds


def test_thresholds_cover_boundary_equality_and_both_sides():
    case = SimpleNamespace(context_passages=["A B."], generated_answer="A.")
    values, interiors = thresholds([case], 0.65)
    boundary = next(v for v in values if math.isclose(v, math.sqrt(0.5)))
    assert {0, 0.65, 1, boundary} <= set(values)
    assert any(0 < v < boundary for v in interiors)
    assert any(boundary < v < 1 for v in interiors)


def projection_fixture():
    case = SimpleNamespace(
        id="dev",
        gold_claims=[
            SimpleNamespace(id="g1", verdict=Verdict.SUPPORTED),
            SimpleNamespace(id="g2", verdict=Verdict.CONTRADICTED),
        ],
    )
    original = {
        "records": [
            {
                "case_id": "dev",
                "status": "ok",
                "output": {
                    "claims": [
                        {"claim_text": "Compound fact", "verdict": "UNSUPPORTED"},
                        {"claim_text": "Duplicate fact", "verdict": "SUPPORTED"},
                    ]
                },
            }
        ]
    }
    reviews = [
        {
            "case_id": "dev",
            "units": [
                {"prediction_index": 0, "gold_id": "g1"},
                {"prediction_index": 0, "gold_id": "g2"},
                {"prediction_index": 1, "gold_id": "g1"},
            ],
        }
    ]
    candidate = copy.deepcopy(original)
    candidate["records"][0]["output"]["claims"][0]["verdict"] = "SUPPORTED"
    return case, original, reviews, candidate


def test_projection_preserves_split_duplicate_and_wrong_label_penalties():
    case, original, reviews, candidate = projection_fixture()
    result = project_labels(candidate, original, reviews, [case])
    assert (result["tp"], result["fp"], result["fn"]) == (1, 2, 1)
    assert result["f1"] == 0.4
    assert result["coverage"] == 1
    assert result["false_support_rate"] == 1
    assert result["evidence_sufficiency"] is None
    assert "not_new_output_approval" in result["status"]


def test_projection_refuses_changed_extraction_or_failed_records():
    case, original, reviews, candidate = projection_fixture()
    candidate["records"][0]["output"]["claims"].reverse()
    with pytest.raises(ValueError, match="claim text/order changed"):
        project_labels(candidate, original, reviews, [case])
    candidate["records"][0]["status"] = "error"
    with pytest.raises(ValueError, match="successful records"):
        project_labels(candidate, original, reviews, [case])
