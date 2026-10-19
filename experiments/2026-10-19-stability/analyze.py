"""AI-proposed scoring of the stability repeats (see PLAN.md). Nothing here is approved.

Alignment: a prediction whose normalized text equals a gold claim maps to it. Every
other prediction text needs an explicit decision in alignment-decisions.json, written
after reading it; identical texts reuse one decision. Evidence is judged on the model's
original (pre-expansion) citations against the premises each gold fact requires.
"""

import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

DIRECTORY = Path("experiments/2026-10-19-stability")
DATA = {
    "dev": Path("data/dev.jsonl"),
    "challenges": Path("data/development-challenges-v2/dev.jsonl"),
}
CANDIDATES = ("refined-v1", "refined-v2", "lean")
REPEATS = (1, 2, 3)

# Premises (passage index, required source text) a matched S/C unit's own original
# citations must contain; same standard as the rev2 challenge alignment.
PREMISES = {
    ("dev-01", "g1"): [(0, "every hour")],
    ("dev-01", "g2"): [(0, "retained for seven days")],
    ("dev-02", "g1"): [(0, "retries GET requests after a connection reset")],
    ("dev-02", "g2"): [(0, "never retries POST requests")],
    ("dev-03", "g1"): [(0, "at most four active workers")],
    ("dev-03", "g2"): [(0, "Additional workers remain queued")],
    ("dev-04", "g1"): [(0, "does not persist entries across restarts")],
    ("dev-05", "g1"): [(0, "writes entries to a local file after each update")],
    ("dev-07", "g1"): [(0, "runs in mode Q"), (1, "encrypts its stored payloads")],
    ("dev-08", "g1"): [(0, "runs on host Maple"), (1, "located in region West")],
    ("challenge-01", "g1"): [(0, "four active export jobs")],
    ("challenge-01", "g2"): [(0, "three other jobs may wait")],
    ("challenge-01", "g3"): [(1, "not per tenant")],
    ("challenge-02", "g1"): [
        (0, "Every worker instance has exactly one host"),
        (0, "production restore worker runs on host Quartz"),
        (1, "Quartz belongs to pool Delta"),
        (2, "Every host has exactly one region"),
        (2, "East and West are distinct regions"),
        (2, "Every host in Delta is located in region East"),
    ],
    ("challenge-02", "g2"): [
        (0, "staging restore worker runs on host Sable"),
        (1, "Sable belongs to pool Gamma"),
        (2, "Every host in Gamma is located in region West"),
    ],
    ("challenge-04", "g1"): [(0, "read-only health endpoint at /status")],
    ("challenge-05", "g1"): [(0, "writing status"), (0, "only after this transaction commits")],
    ("challenge-05", "g2"): [
        (0, "deleting the pending receipt record"),
        (0, "only after this transaction commits"),
    ],
    ("challenge-05", "g3"): [(0, "in one transaction"), (0, "only after this transaction commits")],
}


def norm(text):
    text = text.replace("“", '"').replace("”", '"').lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def key(case_id, text):
    return f"{case_id} | {norm(text)}"


def load_gold():
    gold = {}
    for name, path in DATA.items():
        for line in path.read_text(encoding="utf-8").splitlines():
            case = json.loads(line)
            gold[case["id"]] = case
    return gold


def evidence(case_id, gid, citations):
    needed = PREMISES[(case_id, gid)]
    return all(any(c["index"] == i and s in c["quote"] for c in citations) for i, s in needed)


def main():
    gold = load_gold()
    decisions = json.loads((DIRECTORY / "alignment-decisions.json").read_text(encoding="utf-8"))
    unresolved, results = {}, []
    for candidate in CANDIDATES:
        for dataset in DATA:
            for repeat in REPEATS:
                path = DIRECTORY / f"{candidate}-{dataset}-r{repeat}.json"
                if not path.exists():
                    continue
                run = json.loads(path.read_text(encoding="utf-8"))
                tp = fp = fn = 0
                ev_ok = ev_all = false_support = false_reject = extra = 0
                errors, latencies = [], []
                for rec in run["records"]:
                    case = gold[rec["case_id"]]
                    golds = {g["id"]: g for g in case["gold_claims"]}
                    by_text = {norm(g["claim_text"]): g["id"] for g in case["gold_claims"]}
                    latencies.append(rec["trace"]["latency_seconds"])
                    if rec["status"] != "ok":
                        fn += len(golds)
                        errors.append(f"{rec['case_id']}: request failed")
                        continue
                    final = rec["output"]["claims"]
                    first = rec["trace"]["first_output"]["claims"]
                    seen = set()
                    for pred, raw in zip(final, first, strict=True):
                        k = key(rec["case_id"], pred["claim_text"])
                        if norm(pred["claim_text"]) in by_text:
                            units = [by_text[norm(pred["claim_text"])]]
                        elif k in decisions:
                            units = decisions[k]["units"]
                        else:
                            unresolved[k] = pred["claim_text"]
                            continue
                        for gid in units:
                            if gid is None or gid in seen:
                                fp += 1
                                extra += 1
                                continue
                            seen.add(gid)
                            want = golds[gid]["verdict"]
                            if pred["verdict"] == want:
                                tp += 1
                            else:
                                fp += 1
                                fn += 1
                                errors.append(
                                    f"{rec['case_id']}/{gid}: {pred['verdict']} vs gold {want}"
                                )
                                if pred["verdict"] == "SUPPORTED":
                                    false_support += 1
                                elif want == "SUPPORTED":
                                    false_reject += 1
                            if pred["verdict"] == want and want != "UNSUPPORTED":
                                ev_all += 1
                                ev_ok += evidence(rec["case_id"], gid, raw["citations"])
                    fn += len(set(golds) - seen)
                    for gid in sorted(set(golds) - seen):
                        errors.append(f"{rec['case_id']}/{gid}: missing")
                f1 = 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 1.0
                cost = sum(
                    a.get("cost_usd") or 0 for r in run["records"] for a in r["trace"]["attempts"]
                )
                results.append(
                    {
                        "candidate": candidate,
                        "dataset": dataset,
                        "repeat": repeat,
                        "f1": round(f1, 4),
                        "tp": tp,
                        "fp": fp,
                        "fn": fn,
                        "extra_units": extra,
                        "false_support": false_support,
                        "false_rejection": false_reject,
                        "evidence_sufficient": ev_ok,
                        "evidence_units": ev_all,
                        "repairs": sum(len(r["trace"]["attempts"]) - 1 for r in run["records"]),
                        "failed_requests": sum(r["status"] != "ok" for r in run["records"]),
                        "cost_usd": round(cost, 7),
                        "latencies": latencies,
                        "errors": errors,
                    }
                )
    if unresolved:
        print(json.dumps(unresolved, ensure_ascii=False, indent=1))
        sys.exit(f"{len(unresolved)} prediction texts need an alignment decision")
    summary = defaultdict(dict)
    for candidate in CANDIDATES:
        rows = [r for r in results if r["candidate"] == candidate]
        for dataset in DATA:
            sub = [r for r in rows if r["dataset"] == dataset]
            if not sub:
                continue
            summary[candidate][dataset] = {
                "repeats": len(sub),
                "mean_f1": round(statistics.mean(r["f1"] for r in sub), 4),
                "worst_f1": min(r["f1"] for r in sub),
                "false_support": sum(r["false_support"] for r in sub),
                "false_rejection": sum(r["false_rejection"] for r in sub),
                "extra_units": sum(r["extra_units"] for r in sub),
                "evidence": f"{sum(r['evidence_sufficient'] for r in sub)}/"
                f"{sum(r['evidence_units'] for r in sub)}",
                "errors": [e for r in sub for e in r["errors"]],
            }
        lat = sorted(x for r in rows for x in r["latencies"])
        summary[candidate]["runtime"] = {
            "calls": len(lat),
            "p50_seconds": round(statistics.median(lat), 3),
            "p95_seconds": round(lat[max(0, round(0.95 * len(lat)) - 1)], 3),
            "cost_usd": round(sum(r["cost_usd"] for r in rows), 7),
            "repairs": sum(r["repairs"] for r in rows),
            "failed_requests": sum(r["failed_requests"] for r in rows),
        }
    out = {
        "status": "ai_proposed_owner_pending",
        "plan": "experiments/2026-10-19-stability/PLAN.md",
        "summary": summary,
        "runs": [{k: v for k, v in r.items() if k != "latencies"} for r in results],
    }
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    (DIRECTORY / "stability-summary.json").write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
