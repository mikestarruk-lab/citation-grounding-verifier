import copy
from pathlib import Path

import pytest

from grounding_verifier import error_explorer

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_metrics_and_evidence_states_reconcile():
    snapshot = error_explorer.build_snapshot(ROOT)
    metrics = {r["config"]: r for r in snapshot["queries"]["comparisons"]["rows"]}
    assert metrics["lexical"]["f1"] == pytest.approx(7 / 12)
    assert metrics["minimal"]["f1"] == 1
    assert metrics["f1-candidate"]["f1"] == pytest.approx(10 / 12)
    assert metrics["f1-candidate"]["false_support"] == 2
    assert metrics["safe-candidate"]["f1"] == pytest.approx(8 / 12)
    assert metrics["safe-candidate"]["false_support"] == 0
    assert metrics["f1-candidate"]["evidenceRate"] is None
    assert len(snapshot["queries"]["thresholds"]["rows"]) == 22
    units = snapshot["queries"]["units"]["rows"]
    assert len(units) == 48 and len({r["id"] for r in units}) == 48
    dev07 = next(r for r in units if r["config"] == "lexical" and r["case_id"] == "dev-07")
    assert dev07["label_correct"] is True and dev07["evidence_sufficient"] is False
    changed = next(r for r in units if r["config"] == "f1-candidate" and r["case_id"] == "dev-04")
    assert changed["review_status"] == "pending" and changed["evidence_sufficient"] is None
    assert all(r["case_id"].startswith("dev-") for r in units)


def test_dashboard_rejects_modified_threshold_run(monkeypatch):
    original = error_explorer.read_json

    def tampered(path):
        result = original(path)
        if path.name == "threshold-03.json":
            result = copy.deepcopy(result)
            result["records"][0]["output"]["claims"][0]["verdict"] = "UNSUPPORTED"
        return result

    monkeypatch.setattr(error_explorer, "read_json", tampered)
    with pytest.raises(ValueError, match="threshold run changed"):
        error_explorer.build_snapshot(ROOT)


def test_dashboard_does_not_read_test_cases_or_credentials(monkeypatch):
    original = Path.read_text
    paths = []

    def checked_read(path, *args, **kwargs):
        assert path.name not in {"test.jsonl", ".env"}
        paths.append(path)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", checked_read)
    error_explorer.build_snapshot(ROOT)
    assert any(p.name == "dev.jsonl" for p in paths)
