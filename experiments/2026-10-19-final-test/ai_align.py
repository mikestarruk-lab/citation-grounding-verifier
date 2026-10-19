"""AI-proposed end-to-end alignment of the final test runs (rev2 rule). Not an approval.

Each unit is (prediction index, gold id or None, evidence sufficient or None, note,
needs owner attention). A compound prediction appears once per unit and inherits its
verdict and citations. Evidence is judged on the model's original citations: entity
references may resolve, but independently necessary premises must be quoted.
"""

import json
from pathlib import Path

HERE = Path("experiments/2026-10-19-final-test")
OUT = Path("reviews/test-final/ai-alignment-2026-10-19.json")
METHODS = ("optimized", "minimal", "lexical")

LARGER = (
    "Quote 'Larger files are rejected.' omits the 8 MiB threshold that gives 'larger' its "
    "comparison value; gold keeps both sentences for this reason. Insufficient."
)
THIS_ENDPOINT = "'This endpoint' resolves to GET /status (entity reference). Sufficient."
THEM = "'them' resolves to automatic backups (entity reference). Sufficient."

U = {
    "optimized": {
        "test-01": [(0, "g1", True, "", False), (1, "g2", False, LARGER, True)],
        "test-02": [(0, "g1", True, "", False), (1, "g2", True, "", False)],
        "test-03": [
            (0, "g1", True, "", False),
            (1, "g2", True, "Unconditional source sentence entails the scoped claim.", False),
        ],
        "test-04": [(0, "g1", True, "", False), (1, "g2", True, "", False)],
        "test-05": [
            (0, "g1", True, "", False),
            (1, "g3", True, "", False),
            (2, "g2", True, THIS_ENDPOINT, False),
        ],
        "test-06": [(0, "g1", True, "", False)],
        "test-07": [(0, "g1", True, "", False)],
        "test-08": [(0, "g1", True, "", False)],
        "test-09": [(0, "g1", True, "", False)],
        "test-10": [(0, "g1", True, "", False), (1, "g2", True, THEM, False)],
        "test-11": [(0, "g1", True, "", False), (1, "g2", None, "", False)],
        "test-12": [(0, "g1", None, "", False)],
        "test-13": [(0, "g1", True, "", False), (1, "g2", None, "", False)],
        "test-14": [(0, "g1", None, "", False)],
        "test-15": [(0, "g1", True, "", False), (1, "g2", None, "", False)],
        "test-16": [(0, "g1", True, "Both chain links quoted.", False)],
        "test-17": [
            (0, "g1", True, "Role and permission quoted.", False),
            (
                1,
                "g2",
                False,
                "Only 'cannot delete logs' is quoted: Lina's sole role and the absence of "
                "user-specific permissions are independently necessary and missing.",
                True,
            ),
        ],
        "test-18": [(0, "g1", None, "", False)],
        "test-19": [(0, "g1", True, "Total, exact count and exclusive states all quoted.", False)],
        "test-20": [
            (0, "g1", True, "Exclusive routing and V1 rejection quoted.", False),
            (
                1,
                "g2",
                True,
                "Fragment 'accepts protocol V2' resolves to Release Azure within the same "
                "sentence; routing quoted. Sufficient.",
                True,
            ),
        ],
    },
    "minimal": {
        "test-01": [
            (
                0,
                "g1",
                True,
                "Restates the source rule instead of the answer's wording; it entails that an "
                "8 MiB file is accepted, so it is matched to g1.",
                True,
            ),
            (1, "g2", False, LARGER, True),
        ],
        "test-02": [(0, "g1", True, "", False), (1, "g2", True, "", False)],
        "test-03": [(0, "g1", True, "", False), (1, "g2", True, "", False)],
        "test-04": [(0, "g1", True, "", False), (1, "g2", True, "", False)],
        "test-05": [
            (0, "g1", True, "", False),
            (1, "g3", True, "", False),
            (2, "g2", True, THIS_ENDPOINT, False),
        ],
        "test-06": [(0, "g1", True, "", False)],
        "test-07": [(0, "g1", True, "", False)],
        "test-08": [(0, "g1", True, "", False)],
        "test-09": [(0, "g1", True, "", False)],
        "test-10": [(0, "g1", True, "", False), (1, "g2", True, THEM, False)],
        "test-11": [(0, "g1", True, "", False), (1, "g2", None, "", False)],
        "test-12": [(0, "g1", None, "", False)],
        "test-13": [(0, "g1", True, "", False), (1, "g2", None, "", False)],
        "test-14": [(0, "g1", None, "", False)],
        "test-15": [(0, "g1", True, "", False), (1, "g2", None, "", False)],
        "test-16": [
            (
                0,
                None,
                None,
                "Source premise restated as a claim; the answer never asserts it. Extra unit.",
                True,
            ),
            (1, "g1", True, "Both chain links quoted.", False),
        ],
        "test-17": [
            (
                0,
                "g1",
                False,
                "Only the auditor permission is quoted; Lina's role is missing.",
                False,
            ),
            (1, "g2", False, "Only 'cannot delete logs' is quoted; Lina's role is missing.", False),
        ],
        "test-18": [(0, "g1", None, "", False)],
        "test-19": [
            (
                0,
                "g1",
                False,
                "The exclusive two-state premise is not quoted; gold requires it for 12 - 7.",
                True,
            )
        ],
        "test-20": [
            (
                0,
                None,
                None,
                "Routing premise restated as a claim (and 'exclusively' dropped); the answer "
                "never asserts it. Extra unit.",
                True,
            ),
            (
                1,
                "g1",
                False,
                "Only passage 1 quoted; the exclusive routing premise is missing.",
                False,
            ),
            (2, "g2", False, "Only passage 1 quoted; the routing premise is missing.", False),
        ],
    },
    "lexical": {
        "test-01": [(0, "g1", None, "Compound sentence split.", False), (0, "g2", None, "", False)],
        "test-02": [(0, "g1", None, "", False), (1, "g2", True, "", False)],
        "test-03": [(0, "g1", None, "Compound sentence split.", False), (0, "g2", None, "", False)],
        "test-04": [(0, "g1", None, "Compound sentence split.", False), (0, "g2", None, "", False)],
        "test-05": [
            (0, "g1", True, "Compound sentence split into three units.", False),
            (0, "g3", True, "", False),
            (0, "g2", False, "The authentication sentence is not quoted.", False),
        ],
        "test-06": [(0, "g1", None, "", False)],
        "test-07": [(0, "g1", None, "False support.", False)],
        "test-08": [(0, "g1", None, "False support.", False)],
        "test-09": [(0, "g1", None, "", False)],
        "test-10": [(0, "g1", None, "Compound sentence split.", False), (0, "g2", None, "", False)],
        "test-11": [(0, "g1", None, "Compound sentence split.", False), (0, "g2", None, "", False)],
        "test-12": [(0, "g1", None, "", False)],
        "test-13": [(0, "g1", None, "Compound sentence split.", False), (0, "g2", None, "", False)],
        "test-14": [(0, "g1", None, "", False)],
        "test-15": [
            (0, "g1", None, "Sentence splitter broke 'Apache 2.0' at the period.", True),
            (0, "g2", None, "'Apache 2' read as the Apache 2.0 license claim.", True),
            (
                1,
                None,
                None,
                "'0 license.' is a splitting artifact with no claim. Extra unit.",
                True,
            ),
        ],
        "test-16": [(0, "g1", False, "Only passage 1 quoted; Acorn's policy is missing.", False)],
        "test-17": [(0, "g1", None, "", False), (1, "g2", None, "", False)],
        "test-18": [(0, "g1", None, "", False)],
        "test-19": [
            (0, "g1", False, "Only the total is quoted; the occupied count is missing.", False)
        ],
        "test-20": [
            (0, "g1", None, "Compound sentence split; V1 is a false support.", False),
            (0, "g2", False, "Only passage 1 quoted; routing premise missing.", False),
        ],
    },
}


def main():
    gold = {}
    for line in Path("data/test.jsonl").read_text(encoding="utf-8").splitlines():
        case = json.loads(line)
        gold[case["id"]] = {g["id"]: g for g in case["gold_claims"]}
    result = {"status": "ai_proposed_owner_pending", "rule": "rev2", "methods": {}}
    for method in METHODS:
        run = json.loads((HERE / f"{method}-test.json").read_text(encoding="utf-8"))
        records = {r["case_id"]: r for r in run["records"]}
        assert set(U[method]) == set(records) == set(gold)
        tp = fp = fn = fs = fr = extra = ev_ok = ev_n = 0
        cases, errors = [], []
        for cid in sorted(gold):
            preds = records[cid]["output"]["claims"]
            units = U[method][cid]
            assert {u[0] for u in units} == set(range(len(preds))), (method, cid)
            seen = set()
            rows = []
            for index, gid, evidence, note, attention in units:
                verdict = preds[index]["verdict"]
                if gid is None or gid in seen:
                    fp += 1
                    extra += 1
                    outcome = "extra"
                else:
                    seen.add(gid)
                    want = gold[cid][gid]["verdict"]
                    if verdict == want:
                        tp += 1
                        outcome = "correct"
                        if want != "UNSUPPORTED":
                            assert isinstance(evidence, bool), (method, cid, gid)
                            ev_n += 1
                            ev_ok += evidence
                    else:
                        fp += 1
                        fn += 1
                        outcome = f"wrong label: {verdict} vs {want}"
                        errors.append(f"{cid}/{gid}: {verdict} vs gold {want}")
                        fs += verdict == "SUPPORTED"
                        fr += want == "SUPPORTED"
                rows.append(
                    {
                        "prediction_index": index,
                        "prediction": preds[index]["claim_text"],
                        "verdict": verdict,
                        "gold_id": gid,
                        "outcome": outcome,
                        "evidence_sufficient": evidence if outcome == "correct" else None,
                        "note": note,
                        "needs_owner_attention": attention,
                        "owner_decision": None,
                    }
                )
            missing = sorted(set(gold[cid]) - seen)
            fn += len(missing)
            errors += [f"{cid}/{g}: missing" for g in missing]
            cases.append({"case_id": cid, "units": rows, "missing_gold_ids": missing})
        f1 = 2 * tp / (2 * tp + fp + fn)
        result["methods"][method] = {
            "f1": round(f1, 4),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "extra_units": extra,
            "false_support": fs,
            "false_rejection": fr,
            "evidence": f"{ev_ok}/{ev_n}",
            "errors": errors,
            "cases": cases,
        }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for method, m in result["methods"].items():
        print(method, {k: v for k, v in m.items() if k != "cases"})


if __name__ == "__main__":
    main()
