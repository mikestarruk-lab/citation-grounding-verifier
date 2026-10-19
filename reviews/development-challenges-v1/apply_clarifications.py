"""Materialize accepted clarification scope as a new, non-overwriting dataset version."""

import copy
import json
from pathlib import Path

from grounding_verifier.dataset import Case, dataset_hash, load_cases
from grounding_verifier.gold_review import fenced

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    old = load_cases(ROOT / "data/development-challenges-v1/dev.jsonl")
    notes = json.loads((HERE / "ai-review-notes.json").read_text(encoding="utf-8"))
    assert dataset_hash(old) == notes["dataset_hash"]
    rows = [copy.deepcopy(case.model_dump(mode="json")) for case in old]
    rows[1]["gold_claims"][0]["reasoning"] = notes["cases"][1]["claims"][0]["proposed_reasoning"]
    delivery = rows[4]
    delivery["provenance"] = (
        "Synthetic development challenge derived from challenge-delivery v1. "
        "The owner accepted clarification of the successful committed path and "
        "three-unit scoring after AI review and prior model-output access. "
        "The exact revised wording is not independently human-reviewed."
    )
    delivery["context_passages"] = [
        "ParcelMoth processes an application-level receipt by writing status “delivered” "
        "and deleting the pending receipt record in one transaction. It reports the delivery "
        "as successful only after this transaction commits. A transport acknowledgment alone "
        "does not establish delivery success.",
        "If the sender crashes before the transaction commits, the pending receipt record "
        "remains and the delivery has not been reported as successful. This failure path "
        "is separate from a successfully committed delivery.",
    ]
    delivery["generated_answer"] = (
        "For a delivery reported as successful, ParcelMoth has written status “delivered” "
        "and deleted the pending receipt record in the same committed transaction."
    )
    texts = [
        "For a delivery reported as successful, ParcelMoth has written status “delivered”.",
        "For a delivery reported as successful, ParcelMoth has deleted the pending receipt record.",
        "For a delivery reported as successful, the status update and receipt-record deletion "
        "occurred in the same committed transaction.",
    ]
    reasons = [
        "The receipt transaction writes the status, and success is reported only after it commits.",
        "The receipt transaction deletes the pending record, and success is reported only "
        "after it commits. A pre-commit crash is explicitly not a reported success.",
        "The two changes belong to one transaction, which must commit before success is reported.",
    ]
    annotations = [
        "Retain the reported-success qualifier. Score the status-writing fact, not an "
        "unconditional guarantee covering pre-commit crashes. Preserve the curly quotes.",
        "Score deletion separately from the status update while retaining reported success. "
        "Do not treat the pre-commit failure path as a successful delivery.",
        "Score the same-committed-transaction relation separately from the two action facts. "
        "Do not award this unit for merely listing both actions. A compound prediction may "
        "be split for scoring with inherited verdict and citations; atomicity is separate. "
        "Each gold unit can be matched once, and the relation alone does not supply missing "
        "action details. These three units are not statistically independent observations.",
    ]
    quote = delivery["context_passages"][0].split(" A transport acknowledgment")[0]
    for gold, text, reason, annotation in zip(
        delivery["gold_claims"], texts, reasons, annotations, strict=True
    ):
        gold.update(claim_text=text, reasoning=reason, annotation_reason=annotation)
        gold["citations"] = [{"index": 0, "quote": quote}]
    new = [Case.model_validate(row) for row in rows]
    changed_inputs = [a.id for a, b in zip(old, new, strict=True) if a.request() != b.request()]
    assert changed_inputs == ["challenge-05"]
    assert all(a == b for a, b in zip(old[:1] + old[2:4], new[:1] + new[2:4], strict=True))
    assert [g.verdict for c in old for g in c.gold_claims] == [
        g.verdict for c in new for g in c.gold_claims
    ]
    new_hash = dataset_hash(new)
    decision = {
        "owner_message": "我同意你的明确内容",
        "accepted_scope": [
            "challenge-02/g1",
            "challenge-05/g1",
            "challenge-05/g2",
            "challenge-05/g3",
        ],
        "decision": "Clarification approach accepted; materialized as v2 by the assistant.",
        "scope_limit": "Not blanket approval of the other eight units or of exact new wording; "
        "not model-output approval or a completed semantic evaluation.",
        "source_dataset_hash": dataset_hash(old),
        "revised_dataset_hash": new_hash,
        "changed_inputs": changed_inputs,
        "unchanged_inputs": [c.id for c in old if c.id not in changed_inputs],
        "review_provenance": "Owner acceptance after AI rereview; not independent or blind.",
        "model_calls_this_update": 0,
    }
    manifest = {
        "version": 2,
        "dev": {"review_status": "draft", "reviewed_by": None, "dataset_hash": new_hash},
        "clarification_status": "owner_accepted_approach_materialized",
        "decision_record": "reviews/development-challenges-v1/clarification-decision.json",
        "parent_dataset_hash": dataset_hash(old),
        "note": "New exact wording and the remaining gold require final owner approval. "
        "This is a development extension; no final test approval is implied.",
    }
    lines = [
        "# 开发挑战 v2：已同意澄清的落地版本",
        "",
        "你回复“我同意你的明确内容”。本版落实 challenge-02/g1 和 challenge-05 三条的"
        "澄清方案，保留全部标签及 12 条事实。该回复记录为四项澄清方案获同意，"
        "不扩展为其余八条或模型输出的整体批准；新版具体英文文本仍可复核。",
        "",
        f"数据哈希：`{new_hash}`。",
        "",
        "## 变更与结果使用",
        "",
        "- challenge-02/g1：只补全理由；模型输入、标签和引文不变。",
        "- challenge-05：先在事务中写状态/删记录，提交后才报告成功。"
        "答案和 gold 相应改为报告成功时已完成动作，避免误写成提交后才执行动作。",
        "- 三项计分：状态写入、记录删除、同一已提交事务关系。每个 gold 最多匹配一次；"
        "复合预测可拆分计分、继承标签和引文，原子性另报。",
        "- challenge-01/03/04 完整保留；原 v1、旧运行、旧审阅包不覆盖。",
        "- challenge-05 输入已变，后续对照须重跑该案例。其余四例输入完全相同，"
        "旧输出可经显式来源校验后用于新版审核，但不能直接篡改旧运行的数据哈希或审批。",
        "- 本次没有新增模型调用或生成语义分数；此前模型输出审查仍待完成。",
        "",
    ]
    for case in new:
        lines += [
            f"## {case.id}",
            "",
            f"来源分组：`{case.source_group}`；类别：`{case.category}`。",
            "",
            case.provenance,
            "",
        ]
        for i, passage in enumerate(case.context_passages):
            lines += [f"### 原文 [{i}]", "", fenced(passage, "text"), ""]
        lines += ["### 待核验答案", "", fenced(case.generated_answer, "text"), ""]
        for gold in case.gold_claims:
            lines += [
                f"### {gold.id} · {gold.verdict.value}",
                "",
                fenced(gold.claim_text, "text"),
                "",
                "**Reasoning**",
                "",
                gold.reasoning,
                "",
                "**Annotation reason**",
                "",
                gold.annotation_reason,
                "",
            ]
            if not gold.citations:
                lines += ["Citations: `[]`", ""]
            for citation in gold.citations:
                lines += [f"Citation [{citation.index}]", "", fenced(citation.quote, "text"), ""]
    target = ROOT / "data/development-challenges-v2"
    outputs = {
        target / "dev.jsonl": "\n".join(c.model_dump_json() for c in new) + "\n",
        target / "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        HERE / "clarification-decision.json": json.dumps(decision, ensure_ascii=False, indent=2)
        + "\n",
        HERE / "clarified-gold-v2.zh-CN.md": "\n".join(lines),
    }
    if any(path.exists() for path in outputs):
        raise FileExistsError("Clarification artifacts exist; refusing to overwrite")
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            handle.write(content)
    print(json.dumps({"dataset_hash": new_hash, "changed_inputs": changed_inputs}))


if __name__ == "__main__":
    main()
