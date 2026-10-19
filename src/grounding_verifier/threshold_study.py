"""Dev-only threshold sensitivity using frozen owner semantic alignments.

Projected label metrics are exploratory: changed outputs still need human review.
This command never edits baseline defaults, data, or existing experiment records.
"""

import argparse
import asyncio
import contextlib
import copy
import io
import json
from pathlib import Path
from types import SimpleNamespace

from .baseline import factual_sentences, sentences, similarity
from .cli import read_json, run_benchmark, write_json
from .dataset import digest, load_cases
from .evaluation import output_hash, review_template, score


def thresholds(cases, baseline):
    """Every decision boundary and an interior point of every nonempty region."""
    boundaries = {0.0, 1.0}
    for case in cases:
        corpus = [s for passage in case.context_passages for s in sentences(passage)]
        for text in factual_sentences(case.generated_answer):
            values = similarity(text, corpus)
            if values:
                boundaries.add(min(1.0, max(0.0, max(values))))
    ordered = sorted(boundaries)
    interiors = {(a + b) / 2 for a, b in zip(ordered, ordered[1:])}
    return sorted(boundaries | interiors | {baseline}), interiors


def project_labels(run, original, reviews, cases):
    """Reuse alignment only while claim text/order is identical; never approve it."""
    records = {r["case_id"]: r for r in original["records"]}
    aligned = {r["case_id"]: r for r in reviews}
    gold = {c.id: {g.id: g.verdict.value for g in c.gold_claims} for c in cases}
    tp = fp = covered = false_support = false_rejection = 0
    for record in run["records"]:
        cid = record["case_id"]
        if record["status"] != "ok" or records[cid]["status"] != "ok":
            raise ValueError("projection requires successful records")
        before, after = records[cid]["output"]["claims"], record["output"]["claims"]
        if [p["claim_text"] for p in before] != [p["claim_text"] for p in after]:
            raise ValueError("claim text/order changed; old alignments cannot be projected")
        seen = set()
        for unit in aligned[cid]["units"]:
            gid = unit["gold_id"]
            if gid is None or gid in seen:
                fp += 1
                continue
            seen.add(gid)
            actual = gold[cid][gid]
            predicted = after[unit["prediction_index"]]["verdict"]
            covered += 1
            tp += actual == predicted
            fp += actual != predicted
            false_support += actual != "SUPPORTED" and predicted == "SUPPORTED"
            false_rejection += actual == "SUPPORTED" and predicted == "UNSUPPORTED"
    total = sum(len(c.gold_claims) for c in cases)
    non_supported = sum(v != "SUPPORTED" for row in gold.values() for v in row.values())
    supported = total - non_supported
    fn = total - tp
    return {
        "status": "projected_from_owner_alignment_not_new_output_approval",
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "f1": 2 * tp / (2 * tp + fp + fn),
        "coverage": covered / total,
        "false_support": false_support,
        "false_support_denominator": non_supported,
        "false_support_rate": false_support / non_supported if non_supported else None,
        "false_rejection": false_rejection,
        "false_rejection_denominator": supported,
        "evidence_sufficiency": None,
    }


async def study(args):
    original, reviews = read_json(args.run), read_json(args.reviews)
    if (original["split"], original["method"], original["mode"]) != ("dev", "lexical", "e2e"):
        raise ValueError("only a lexical end-to-end development run is accepted")
    cases = load_cases(args.data / "dev.jsonl")
    checked = score(original, cases, reviews)
    if checked["semantic_status"] != "reviewed":
        raise ValueError("all original outputs need valid owner reviews")
    values, interiors = thresholds(cases, original["threshold"])
    args.out.mkdir(parents=True, exist_ok=False)
    rows, runs = [], []
    for index, threshold in enumerate(values):
        path = args.out / f"threshold-{index:02d}.json"
        config = SimpleNamespace(
            out=path,
            data=args.data,
            split="dev",
            method="lexical",
            mode="e2e",
            threshold=threshold,
            experiment_note="Dev-only lexical threshold sensitivity; unchanged extraction.",
        )
        with contextlib.redirect_stdout(io.StringIO()):
            await run_benchmark(config)
        run = read_json(path)
        if threshold == original["threshold"] and [output_hash(r) for r in run["records"]] != [
            output_hash(r) for r in original["records"]
        ]:
            raise ValueError("baseline outputs changed; investigate before interpreting thresholds")
        rows.append(
            {
                "threshold": threshold,
                "interior_point": threshold in interiors,
                "run": path.name,
                "run_digest": digest(run),
                "projection": project_labels(run, original, reviews, cases),
            }
        )
        runs.append(run)
    # F1 then false support, as planned. Prefer an interior point to a brittle boundary.
    # Evidence is unreviewed, so this is a candidate nomination, not a final selection.
    best = min(
        range(len(rows)),
        key=lambda i: (
            -rows[i]["projection"]["f1"],
            rows[i]["projection"]["false_support"],
            not rows[i]["interior_point"],
            abs(rows[i]["threshold"] - original["threshold"]),
        ),
    )
    candidate = runs[best]
    packets = review_template(candidate, {c.id: c for c in cases})
    old = {p["case_id"]: p for p in reviews}
    deltas = []
    for i, packet in enumerate(packets):
        previous = old[packet["case_id"]]
        if packet["output_hash"] == previous["output_hash"]:
            packets[i] = copy.deepcopy(previous)
            continue
        packet["alignment_source"] = {
            "review_id": previous["review_id"],
            "output_hash": previous["output_hash"],
            "note": "Semantic alignment copied for unchanged text; new output remains pending.",
        }
        packet["units"] = [
            {
                "prediction_index": u["prediction_index"],
                "text": u["text"],
                "gold_id": u["gold_id"],
                "evidence_sufficient": None,
                "note": "New output needs owner evidence review.",
            }
            for u in previous["units"]
        ]
        for j, (before, after) in enumerate(
            zip(
                previous["prediction"]["claims"],
                packet["prediction"]["claims"],
                strict=True,
            )
        ):
            if before != after:
                deltas.append(
                    {
                        "case_id": packet["case_id"],
                        "prediction_index": j,
                        "before": before,
                        "after": after,
                    }
                )
    write_json(args.out / "candidate-reviews.json", packets)
    write_json(args.out / "candidate.summary.json", score(candidate, cases, packets))
    write_json(
        args.out / "study.json",
        {
            "format_version": 1,
            "split": "dev",
            "dataset_hash": original["dataset_hash"],
            "source_run": str(args.run),
            "source_run_digest": digest(original),
            "source_reviews": str(args.reviews),
            "source_reviews_digest": digest(reviews),
            "script_digest": digest(Path(__file__).read_text(encoding="utf-8")),
            "baseline_threshold": original["threshold"],
            "candidate": rows[best],
            "selection_status": "candidate_pending_owner_review_no_default_change",
            "rows": rows,
            "changed_predictions": deltas,
        },
    )
    changed = [p for p in packets if p["status"] == "pending"]
    content = [
        "# Candidate output delta review",
        "",
        "Unchanged exact output hashes retain their existing approvals. Changed packets",
        "remain pending. Alignment is projected only because text/order is unchanged.",
        "Review the full context, verdict, reasoning and citations below before approval.",
        "",
    ]
    for packet in changed:
        content += [
            f"## {packet['case_id']}",
            "",
            "```json",
            json.dumps(packet, ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    (args.out / "candidate-review.md").write_text("\n".join(content), encoding="utf-8")
    print(
        f"Saved {len(rows)} thresholds; candidate={rows[best]['threshold']:.6f}; "
        f"{len(changed)} packets / {len(deltas)} predictions changed. All new outputs pending."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--reviews", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(study(args))


if __name__ == "__main__":
    main()
