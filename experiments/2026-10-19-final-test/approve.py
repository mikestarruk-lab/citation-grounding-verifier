"""Write owner-approved test review records from the confirmed AI alignment.

The owner replied "确认" to the AI alignment document on 2026-10-19 without editing
any decision. The scorer also needs evidence judgments for S/C units that are extra or
wrongly labelled; those five are filled here (EXTRA_EVIDENCE) and disclosed.
"""

import hashlib
import json
from pathlib import Path

from ai_align import METHODS, U

REVIEWER = "Michael (mikestarruk-lab)"
ALIGNMENT = Path("reviews/test-final/ai-alignment-2026-10-19.json")
DOCUMENT = "https://claude.ai/code/artifact/6117427c-fe43-418b-8682-002a58f0cf6f"
EXTRA_EVIDENCE = {
    ("minimal", "test-16", 0): (True, "Its own premise sentence is quoted verbatim."),
    ("minimal", "test-20", 0): (True, "Its own routing sentence is quoted verbatim."),
    ("lexical", "test-07", 0): (False, "The quote states the opposite of the claim."),
    ("lexical", "test-08", 0): (False, "The quote states the opposite of the claim."),
    ("lexical", "test-20", 0): (False, "V1 claim: the quote states that Azure rejects V1."),
}


def main():
    alignment_sha = hashlib.sha256(ALIGNMENT.read_bytes()).hexdigest()
    gold = {}
    for line in Path("data/test.jsonl").read_text(encoding="utf-8").splitlines():
        case = json.loads(line)
        gold[case["id"]] = {g["id"]: g["claim_text"] for g in case["gold_claims"]}
    for method in METHODS:
        pending = json.loads(
            Path(f"reviews/test-final/{method}-test-pending.json").read_text(encoding="utf-8")
        )
        approved = []
        for packet in pending:
            cid = packet["case_id"]
            predictions = packet["prediction"]["claims"]
            units = []
            for index, gid, evidence, note, _ in sorted(U[method][cid], key=lambda u: u[0]):
                split = sum(u[0] == index for u in U[method][cid]) > 1
                text = gold[cid][gid] if split and gid else predictions[index]["claim_text"]
                if predictions[index]["verdict"] != "UNSUPPORTED" and evidence is None:
                    evidence, extra = EXTRA_EVIDENCE[(method, cid, index)]
                    note = f"{note} {extra}".strip()
                units.append(
                    {
                        "prediction_index": index,
                        "text": text,
                        "gold_id": gid,
                        "evidence_sufficient": evidence
                        if predictions[index]["verdict"] != "UNSUPPORTED"
                        else None,
                        "note": note,
                    }
                )
            approved.append(
                {
                    **packet,
                    "status": "approved",
                    "reviewer": REVIEWER,
                    "units": units,
                    "reviewed_on": "2026-10-19",
                    "review_source": str(ALIGNMENT.as_posix()),
                    "review_source_sha256": alignment_sha,
                    "review_document": DOCUMENT,
                    "owner_confirmation": "确认",
                    "review_process": "Owner confirmed the AI-proposed rev2 alignment as written, "
                    "after reading the structured review document; not an independent blind "
                    "review. Evidence for five extra or mislabelled S/C units was filled "
                    "mechanically afterwards because the scorer requires it.",
                }
            )
        out = Path(f"reviews/test-final/{method}-test-approved.json")
        with out.open("x", encoding="utf-8") as handle:
            json.dump(approved, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(out)


if __name__ == "__main__":
    main()
