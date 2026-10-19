"""Recompute automatic evidence and export pending full-field review packets."""

import argparse
import json
from pathlib import Path

from grounding_verifier.cli import read_json, write_json
from grounding_verifier.dataset import dataset_hash, digest, load_cases
from grounding_verifier.evaluation import review_template, score

ROOT = Path("experiments/2026-10-18-optimized-v1")
CHALLENGES = Path("data/development-challenges-v1")
ORIGINAL = load_cases(Path("data/dev.jsonl"))
DRAFT = load_cases(CHALLENGES / "dev.jsonl")
FOCUSED = load_cases(ROOT / "focused-input/dev.jsonl")
DEV08 = load_cases(ROOT / "dev08-input/dev.jsonl")

SPECS = [
    ("minimal-challenges", DRAFT, "challenge"),
    ("optimized-challenges", DRAFT, "challenge"),
    ("optimized-v2-challenges", DRAFT, "challenge"),
    ("optimized-passage-challenges", DRAFT, "challenge"),
    ("optimized-original-dev", ORIGINAL, "original"),
    ("optimized-v2-original-dev", ORIGINAL, "original"),
    ("optimized-passage-original-dev", ORIGINAL, "original"),
    ("minimal-focused-repeat", FOCUSED, "repeat"),
    ("optimized-v1-focused-repeat", FOCUSED, "repeat"),
    ("optimized-v2-focused-repeat", FOCUSED, "repeat"),
    ("optimized-passage-focused-repeat", FOCUSED, "repeat"),
    ("optimized-lean-challenges", DRAFT, "challenge"),
    ("optimized-lean-original-dev", ORIGINAL, "original"),
    ("optimized-lean-focused-repeat", FOCUSED, "repeat"),
    ("optimized-lean-dev08-repeat", DEV08, "repeat"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "experiment-summary.json")
    parser.add_argument("--review-out", type=Path, default=ROOT / "review-ready.md")
    args = parser.parse_args()
    summaries, diagnostics, sources = [], [], []
    review_groups = {}
    for name, cases, group in SPECS:
        run = read_json(ROOT / f"{name}.json")
        automatic = score(run, cases)
        assert automatic["semantic_status"] == "pending_human_review"
        sources.append({"path": f"{name}.json", "digest": digest(run)})
        before = after = 0
        for record in run["records"]:
            if record["status"] != "ok":
                continue
            first = record["trace"].get("first_output", {})
            before += sum(
                len(c["quote"])
                for claim in first.get("claims", [])
                for c in claim.get("citations", [])
            )
            after += sum(
                len(c["quote"]) for claim in record["output"]["claims"] for c in claim["citations"]
            )
            if record["case_id"] == "challenge-02":
                matches = [
                    c
                    for c in record["output"]["claims"]
                    if "production" in c["claim_text"] and "West" in c["claim_text"]
                ]
                if len(matches) != 1:
                    raise ValueError("diagnostic needs manual identification of production claim")
                quotes = "\n".join(c["quote"] for c in matches[0]["citations"])
                diagnostics.append(
                    {
                        "run": name,
                        "case_id": "challenge-02",
                        "diagnostic_only": True,
                        "quoted_exclusion_premises": {
                            "single_host": "Every worker instance has exactly one host." in quotes,
                            "single_region": "Every host has exactly one region." in quotes,
                            "distinct_regions": "East and West are distinct regions." in quotes,
                        },
                        "note": "Exact required-premise presence only; not a full evidence grade.",
                    }
                )
            if record["case_id"] == "challenge-03":
                diagnostics.append(
                    {
                        "run": name,
                        "case_id": "challenge-03",
                        "diagnostic_only": True,
                        "claims": record["output"]["claims"],
                        "note": "Review the timeout relation and reasoning strength.",
                    }
                )
        summaries.append(
            {
                "run": name,
                "group": group,
                **automatic,
                "raw_quote_characters": before,
                "final_quote_characters": after,
            }
        )
        if name in {
            "minimal-challenges",
            "optimized-challenges",
            "optimized-v2-challenges",
            "optimized-passage-challenges",
            "optimized-passage-original-dev",
            "optimized-lean-challenges",
            "optimized-lean-original-dev",
        }:
            packets = review_template(run, {c.id: c for c in cases})
            if name in {
                "minimal-challenges",
                "optimized-lean-challenges",
                "optimized-lean-original-dev",
            }:
                review_groups[name] = packets
            path = ROOT / f"{name}.pending.json"
            if path.exists():
                if read_json(path) != packets:
                    raise ValueError("existing pending review changed; do not overwrite it")
            else:
                write_json(path, packets)

    boundaries = read_json(ROOT / "live-boundaries.json")
    lean_boundaries = read_json(ROOT / "lean-live-boundaries.json")
    all_boundaries = boundaries["records"] + lean_boundaries["records"]
    fault = read_json(ROOT / "controlled-faults.json")
    boundary_cost = sum(
        a.get("cost_usd") or 0 for r in all_boundaries for a in r["trace"].get("attempts", [])
    )
    calls = sum(s["counts"]["calls"] for s in summaries) + sum(
        len(r["trace"].get("attempts", [])) for r in all_boundaries
    )
    cost = sum(s["confirmed_cost_usd"] for s in summaries) + boundary_cost
    result = {
        "status": "automatic_metrics_and_diagnostics_only_human_quality_pending",
        "original_dev_hash": dataset_hash(ORIGINAL),
        "challenge_hash": dataset_hash(DRAFT),
        "live_calls": calls,
        "configured_rate_estimated_cost_usd": cost,
        "summaries": summaries,
        "diagnostics": diagnostics,
        "sources": sources,
        "boundary_checks": [
            {
                "method": method,
                "passed": sum(
                    r["boundary_passed"] for r in boundaries["records"] if r["method"] == method
                ),
                "total": 3,
            }
            for method in ("minimal", "optimized")
        ],
        "controlled_faults": [
            {
                "method": method,
                "recovered": sum(
                    r["status"] == "ok" for r in fault["records"] if r["method"] == method
                ),
                "total": 6,
            }
            for method in ("minimal", "optimized")
        ],
    }
    result["lean_boundary_checks"] = {
        "passed": sum(r["boundary_passed"] for r in lean_boundaries["records"]),
        "total": 3,
    }
    write_json(args.out, result)
    parts = [
        "# Optimization review: complete source fields",
        "",
        "All new model outputs remain pending. Challenge gold is AI-authored draft.",
        "Review the five new gold cases before interpreting complete quality scores.",
        "Methods are visible; this is not blind or independent annotation.",
        "",
        "Start with challenge-02 exclusion evidence and challenge-03 qualification;",
        "compare passage expansion with the raw response. Output hashes stay bound.",
        "",
    ]
    for name, packets in review_groups.items():
        parts += [f"## {name}", ""]
        for packet in sorted(packets, key=lambda p: p["case_id"]):
            parts += [
                f"<details><summary>{packet['case_id']} · full review packet</summary>",
                "",
                "```json",
                json.dumps(packet, ensure_ascii=False, indent=2),
                "```",
                "",
                "</details>",
                "",
            ]
    args.review_out.write_text("\n".join(parts), encoding="utf-8")
    print(
        json.dumps(
            {"live_calls": calls, "estimated_cost_usd": cost, "status": result["status"]}, indent=2
        )
    )


if __name__ == "__main__":
    main()
