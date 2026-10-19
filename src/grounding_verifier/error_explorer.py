"""Export validated development evidence for the local error explorer (no API calls)."""

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from .cli import read_json
from .dataset import dataset_hash, digest, load_cases
from .evaluation import output_hash, raw_citations, score
from .threshold_study import project_labels


def build_snapshot(root: Path):
    dev = load_cases(root / "data/dev.jsonl")
    by_case = {case.id: case for case in dev}
    non_supported = sum(g.verdict.value != "SUPPORTED" for c in dev for g in c.gold_claims)
    experiment = root / "experiments/2026-10-16-dev-v2"
    study_dir = root / "experiments/2026-10-17-lexical-thresholds"
    files = []

    def read(path):
        value = read_json(path)
        files.append({"name": path.relative_to(root).as_posix(), "content_digest": digest(value)})
        return value

    original = read(experiment / "lexical-dev-v2.json")
    minimal = read(experiment / "minimal-dev-v2.json")
    a = read(root / "reviews/dev-v2/dev-v2-A-approved.json")
    b = read(root / "reviews/dev-v2/dev-v2-B-approved.json")
    decision = read(root / "experiments/baseline-freeze-2026-10-18.json")
    for name, run, review in (("lexical", original, a), ("minimal", minimal, b)):
        if (
            decision["dataset_hash"] != dataset_hash(dev)
            or decision[name]["run_digest"] != digest(run)
            or decision[name]["review_digest"] != digest(review)
        ):
            raise ValueError("retained baseline differs from the owner decision")
    study = read(study_dir / "study.json")
    if study["source_run_digest"] != digest(original) or study["source_reviews_digest"] != digest(
        a
    ):
        raise ValueError("threshold study references stale baseline/review content")
    if study["dataset_hash"] != dataset_hash(dev):
        raise ValueError("threshold study dataset changed")
    for run, reviews in ((original, a), (minimal, b)):
        if run["split"] != "dev" or score(run, dev, reviews)["semantic_status"] != "reviewed":
            raise ValueError("both development baselines need complete valid reviews")

    thresholds = []
    candidates = {}
    for row in study["rows"]:
        run = read(study_dir / row["run"])
        if digest(run) != row["run_digest"] or run["split"] != "dev":
            raise ValueError("threshold run changed or is not development data")
        score(run, dev)  # Validate dataset hash and full case coverage.
        projected = project_labels(run, original, a, dev)
        if projected != row["projection"] or run["threshold"] != row["threshold"]:
            raise ValueError("stored threshold projection does not reproduce")
        thresholds.append({"threshold": row["threshold"], **projected})
        candidates[row["run"]] = run

    best = study["candidate"]
    if best not in study["rows"]:
        raise ValueError("candidate is not a verified study row")
    safe = min(
        study["rows"],
        key=lambda r: (
            r["projection"]["false_support"],
            -r["projection"]["f1"],
            not r["interior_point"],
            abs(r["threshold"] - original["threshold"]),
        ),
    )
    configs = [
        ("lexical", "Lexical · 0.65", original, a, True),
        ("minimal", "Minimal LLM", minimal, b, True),
        ("f1-candidate", "Lexical · best F1", candidates[best["run"]], a, False),
        ("safe-candidate", "Lexical · zero false support", candidates[safe["run"]], a, False),
    ]
    metrics, units = [], []
    for config_id, label, run, alignments, reviewed in configs:
        summary = score(run, dev, alignments if reviewed else None)
        projection = summary if reviewed else project_labels(run, original, a, dev)
        counts = summary["counts"] if reviewed else projection
        metrics.append(
            {
                "config": config_id,
                "label": label,
                "threshold": run.get("threshold"),
                "score_status": "Owner reviewed" if reviewed else "Projected / not adopted",
                "selection_status": "retained_baseline" if reviewed else "sensitivity_only",
                "f1": projection["f1"],
                "falseSupportRate": projection["false_support_rate"],
                "false_support": counts.get("false_support", 0),
                "non_supported": non_supported,
                "cases": len(dev),
                "gold_facts": sum(len(c.gold_claims) for c in dev),
                "tp": counts.get("tp", 0),
                "fp": counts.get("fp", 0),
                "fn": counts.get("fn", 0),
                "coverage": projection["coverage"],
                "evidenceRate": summary.get("evidence_sufficiency") if reviewed else None,
                "evidence_numerator": counts.get("sufficient_evidence") if reviewed else None,
                "evidence_denominator": counts.get("evidence_units") if reviewed else None,
                "success_rate": summary["success_rate"],
                "quote_validity": summary["final_quote_validity"],
            }
        )
        align_by_case = {review["case_id"]: review for review in alignments}
        for record in run["records"]:
            case = by_case[record["case_id"]]
            review = align_by_case[case.id]
            multiplicity = Counter(u["prediction_index"] for u in review["units"])
            gold = {g.id: g.model_dump(mode="json") for g in case.gold_claims}
            seen = set()
            exact_review = output_hash(record) == review["output_hash"]
            for index, unit in enumerate(review["units"]):
                prediction = record["output"]["claims"][unit["prediction_index"]]
                gid = unit["gold_id"]
                duplicate = gid is not None and gid in seen
                actual = gold.get(gid)
                correct = (
                    actual is not None
                    and not duplicate
                    and actual["verdict"] == prediction["verdict"]
                )
                evidence = unit["evidence_sufficient"] if exact_review else None
                if gid:
                    seen.add(gid)
                valid, total = raw_citations({"claims": [prediction]}, case.context_passages)
                errors = []
                if not correct:
                    errors.append("label" if actual and not duplicate else "extra")
                if evidence is False:
                    errors.append("evidence")
                if multiplicity[unit["prediction_index"]] > 1:
                    errors.append("compound")
                if valid != total:
                    errors.append("citation")
                if not exact_review:
                    errors.append("pending")
                units.append(
                    {
                        "id": f"{config_id}:{case.id}:{index}",
                        "config": config_id,
                        "case_id": case.id,
                        "category": case.category,
                        "gold_id": gid,
                        "prediction_index": unit["prediction_index"],
                        "text": unit["text"],
                        "gold_verdict": actual["verdict"] if actual else "EXTRA",
                        "predicted_verdict": prediction["verdict"],
                        "label_correct": correct,
                        "evidence_sufficient": evidence,
                        "review_status": "reviewed" if exact_review else "pending",
                        "errors": ",".join(errors),
                        "payload": json.dumps(
                            {
                                "context_passages": case.context_passages,
                                "generated_answer": case.generated_answer,
                                "gold": actual,
                                "prediction": prediction,
                                "review_note": unit.get("note", ""),
                                "output_hash": output_hash(record),
                                "alignment_provenance": "owner-reviewed original text alignment",
                            },
                            ensure_ascii=False,
                        ),
                    }
                )

    definitions = [
        {
            "label": "Fact + label F1",
            "definition": (
                "2TP/(2TP+FP+FN). Wrong labels count as both FP and FN. Candidate labels "
                "use unchanged owner-aligned text; this is not new owner approval."
            ),
        },
        {
            "label": "False support",
            "definition": (
                "Non-supported gold facts predicted SUPPORTED / all non-supported gold facts. "
                "Coverage and success remain visible."
            ),
        },
        {
            "label": "Evidence sufficiency",
            "definition": (
                "Sufficient evidence units / all supported or contradicted prediction units. "
                "Unknown for candidate-wide results until reviewed."
            ),
        },
        {
            "label": "Error units",
            "definition": (
                "Scoring units after the owner's compound split. Error types overlap. "
                "Compound marks repeat prediction-level issues; do not add error totals."
            ),
        },
    ]
    source = {
        "label": "Repository development experiment and owner review files",
        "files": [f["name"] for f in files] + ["data/dev.jsonl"],
        "contentDigests": files,
        "datasetHash": dataset_hash(dev),
        "classification": "Synthetic development specifications with real saved method outputs",
        "executedAt": datetime.now(UTC).isoformat(),
        "timezone": "Europe/London",
        "metricDefinitions": definitions,
        "caveats": [
            "Owner retained lexical 0.65 and minimal LLM; other thresholds are sensitivity only.",
            "8 dev cases / 12 gold facts; test not read or run.",
            "Owner review followed AI feedback; not independent blind review.",
            "Candidate evidence is unknown, not zero. No default threshold change.",
        ],
        "evidenceFlow": [
            {
                "title": "Load and validate",
                "detail": (
                    "Load dev.jsonl, saved v2 runs and approved review JSON. "
                    "score() validates dataset/output hashes and review coverage."
                ),
            },
            {
                "title": "Verify threshold study",
                "detail": (
                    "Verify study source digests, every run digest and recomputed "
                    "unchanged-text label projections."
                ),
            },
            {
                "title": "Export snapshot",
                "detail": (
                    "python -m grounding_verifier.error_explorer "
                    "--out tools/error-explorer/src/data.json. "
                    "No model calls, test data access or review writes."
                ),
            },
        ],
    }
    return {
        "title": "Citation verifier · Error explorer",
        "surface": "dashboard",
        "generatedAt": source["executedAt"],
        "status": "local-experiment-evidence",
        "buildStatus": "creating",
        "filters": [],
        "queries": {
            "comparisons": {"rows": metrics, "source": source},
            "thresholds": {"rows": thresholds, "source": source},
            "units": {"rows": units, "payloadColumns": ["payload"], "source": source},
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--build-status", choices=["creating", "updating", "complete", "paused"])
    args = parser.parse_args()
    snapshot = build_snapshot(args.root.resolve())
    if args.out.exists():
        previous = read_json(args.out)
        for field in ("id", "legacyPresentationTitle"):
            if field in previous:
                snapshot[field] = previous[field]
        snapshot["buildStatus"] = "updating"
    if args.build_status:
        snapshot["buildStatus"] = args.build_status
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(snapshot['queries']['units']['rows'])} units from dev evidence only.")


if __name__ == "__main__":
    main()
