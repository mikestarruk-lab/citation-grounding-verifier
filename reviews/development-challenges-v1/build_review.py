"""Build a source-bound AI review and editable owner checklist, without approval."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from grounding_verifier.dataset import dataset_hash, load_cases
from grounding_verifier.evaluation import raw_citations
from grounding_verifier.gold_review import fenced

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def main():
    source = ROOT / "data/development-challenges-v1/dev.jsonl"
    manifest_path = source.parent / "manifest.json"
    notes_path = HERE / "ai-review-notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8"))
    cases = load_cases(source)
    current_hash = dataset_hash(cases)
    assert current_hash == notes["dataset_hash"], "Source changed; repeat the semantic review"
    by_id = {entry["case_id"]: entry for entry in notes["cases"]}
    assert len(by_id) == len(notes["cases"]) == len(cases)
    assert set(by_id) == {case.id for case in cases}
    packets, labels, actions = [], Counter(), Counter()
    quote_valid = quote_total = 0
    for case in cases:
        review = by_id[case.id]
        assert [g.id for g in case.gold_claims] == [g["id"] for g in review["claims"]]
        valid, total = raw_citations(
            case.model_dump(mode="json")
            | {"claims": [g.model_dump(mode="json") for g in case.gold_claims]},
            case.context_passages,
        )
        quote_valid += valid
        quote_total += total
        labels.update(g.verdict.value for g in case.gold_claims)
        actions.update(g["action"] for g in review["claims"])
        packets.append(
            {
                "source": case.model_dump(mode="json"),
                "ai_review": review,
                "owner_review": {
                    "status": "pending",
                    "reviewer": None,
                    "reviewed_at": None,
                    "claims": [
                        {"id": g.id, "decision": None, "comment": ""} for g in case.gold_claims
                    ],
                },
            }
        )
    assert quote_valid == quote_total
    checks = {
        "case_count": len(cases),
        "fact_count": sum(labels.values()),
        "passage_count": sum(len(c.context_passages) for c in cases),
        "verdict_counts": dict(labels),
        "valid_quotes": quote_valid,
        "total_quotes": quote_total,
        "ai_actions": dict(actions),
        "schema_and_citation_rules": "passed",
        "semantic_review": "AI only",
        "owner_approval": "pending",
    }
    bundle = {
        "schema_version": 1,
        "created_on": notes["date"],
        "status": "ai_review_only_owner_pending",
        "dataset_hash": current_hash,
        "source_path": source.relative_to(ROOT).as_posix(),
        "source_file_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "notes_sha256": hashlib.sha256(notes_path.read_bytes()).hexdigest(),
        "manifest_snapshot": json.loads(manifest_path.read_text(encoding="utf-8")),
        "provenance": "AI rereview after prior access to challenge model outputs; not blind.",
        "checks": checks,
        "cases": packets,
    }
    lines = [
        "# 新增开发挑战 gold：AI 审阅与人工二次复核",
        "",
        f"审阅日期：{notes['date']}。范围：5 个新增开发案例、12 条拟议事实。",
        "",
        "本文是给你的中文审阅工作稿，原始英文文本逐字保留。AI 已看到之前实验的模型输出，"
        "这次是对照 assignment 定义的再次审阅，不称独立盲审。本文没有批准 gold、修改数据、"
        "重新运行模型或给新输出计算完整语义分数。",
        "",
        "## 先看结论",
        "",
        "没有发现必须翻转现有 verdict 的充分依据。8 条建议保留；4 条先明确理由或评分范围："
        "challenge-02/g1 的标签和引用可保留，建议补全排除 West 的理由；challenge-05 的三条"
        "需要统一成功/提交的时间语义，并明确事务关系的独立计分。4 条待明确不等于4条错标。",
        "",
        "确定性检查：5 案例、13 段原文、12 条事实；S=7、C=2、U=3；"
        f"{quote_valid}/{quote_total} 个引用对象的整数索引、范围、非空和逐字匹配通过。"
        "S/C 有引用、U 无引用。确定性通过不证明语义正确。",
        "",
        "## 你怎样复核",
        "",
        "先读每个案例的全部原文和待核验答案，再看每条原 gold 与 AI 意见。"
        "在每条的“你的决定”和“你的意见/替换文本”填写即可，也可以在聊天里按案例/事实编号回复。"
        "建议决定用：同意原标注 / 同意建议修改 / 我有不同修改 / 暂不确定。"
        "阅读或勾选本文不自动写入程序批准记录；保存后再核对你的实际决定及数据版本。",
        "",
        "先判断答案真正声称了什么，再判断来源是否充分支持、明确反驳或不足以判断。"
        "引用可采用不同但有效的组合；不要求逐字等同 gold 引用。"
        "不要把来源中的其他信息补成答案事实，也不要把条件删掉后给不完整的事实计分。",
        "",
        "## 版本与边界",
        "",
        f"- 数据：`{bundle['source_path']}`。",
        f"- 规范化数据哈希：`{current_hash}`。",
        f"- 源文件 SHA-256：`{bundle['source_file_sha256']}`。",
        "- 原始 manifest：draft，reviewed_by=null；"
        "原 dev 8 案例与最终 test 20 案例不在本次审批范围。",
        "- 结构化副本：[review-bundle.json](review-bundle.json)，"
        "保存全部来源、AI 意见和空白人工决定。",
        "- 本文与 JSON 是两种载体，不会自动互相同步；请选本文填写，后续以你实际保存的意见导入。",
        "- 修改来源或 gold 后应产生新版本/哈希。只改 gold 时保存的原始模型输出仍是历史证据，"
        "但旧评测绑定需要重新核对；改输入则须重跑受影响配置，不能直接沿用旧评测分数。",
        "",
        "## 全部事实导航",
        "",
        "| 案例 / 事实 | 原标签 | AI 建议 | 人工决定 |",
        "|---|---|---|---|",
    ]
    action_labels = {"retain": "保留", "clarify": "先明确"}
    for packet in packets:
        case = packet["source"]
        for gold, review in zip(case["gold_claims"], packet["ai_review"]["claims"], strict=True):
            lines.append(
                f"| {case['id']} / {gold['id']} | {gold['verdict']} | "
                f"{action_labels[review['action']]} | 待你填写 |"
            )
    for packet in packets:
        case, review = packet["source"], packet["ai_review"]
        lines += [
            "",
            f"## {case['id']}",
            "",
            f"来源分组：`{case['source_group']}`；类别：`{case['category']}`。",
            "",
            "原始来源说明：",
            "",
            case["provenance"],
            "",
            "### 完整原文（索引从 0 开始）",
            "",
        ]
        for index, passage in enumerate(case["context_passages"]):
            lines += [f"**Passage [{index}]**", "", fenced(passage, "text"), ""]
        lines += [
            "### 原始待核验答案",
            "",
            fenced(case["generated_answer"], "text"),
            "",
            "### AI 对整个案例的判断",
            "",
            review["overview"],
            "",
        ]
        for gold, item in zip(case["gold_claims"], review["claims"], strict=True):
            lines += [
                f"### {case['id']} / {gold['id']}",
                "",
                f"**原 gold 标签：{gold['verdict']}；AI 建议：{action_labels[item['action']]}。**",
                "",
                "**原 claim_text**",
                "",
                fenced(gold["claim_text"], "text"),
                "",
                "**原 reasoning**",
                "",
                gold["reasoning"],
                "",
                "**原 annotation_reason**",
                "",
                gold["annotation_reason"],
                "",
                "**原 citations（完整，不截断）**",
                "",
            ]
            if not gold["citations"]:
                lines += ["`[]`", ""]
            for citation in gold["citations"]:
                lines += [f"索引 [{citation['index']}]", "", fenced(citation["quote"], "text"), ""]
            for label, key in [
                ("AI 语义判断", "analysis"),
                ("AI 证据审查", "evidence"),
                ("需要注意的边界", "risk"),
            ]:
                lines += [f"**{label}**", "", item[key], ""]
            if item.get("proposed_reasoning"):
                lines += [
                    "**建议替换 reasoning（尚未写入数据）**",
                    "",
                    fenced(item["proposed_reasoning"], "text"),
                    "",
                ]
            lines += [
                "**请你确认的具体问题**",
                "",
                item["question"],
                "",
                "| 你的复核字段 | 填写处 |",
                "|---|---|",
                "| 你的决定 | 待填写 |",
                "| 你的意见 / 替换文本 | 待填写 |",
                "",
            ]
    lines += [
        "## 最后确认",
        "",
        "| 字段 | 填写处 |",
        "|---|---|",
        "| 复核人 | 待填写 |",
        "| 复核日期 | 待填写 |",
        "| 实际审阅耗时（如有记录） | 待填写；不估填 |",
        "| 尚未解决的案例 / 事实 | 待填写 |",
        "",
        "若决定修改 challenge-05 的输入，建议在新版本中明确：本例只描述正常成功提交路径，"
        "成功提交后能观察到 delivered 状态及记录删除；提交前崩溃属于另一路径。"
        "同时协调原文、答案和 gold 的先后顺序，不只在解释里偷偷补一个原文没有的条件。"
        "当前版本和所有旧运行继续保留。",
        "",
    ]
    outputs = {
        HERE / "review-bundle.json": json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        HERE / "gold-ai-review.zh-CN.md": "\n".join(lines),
    }
    if any(path.exists() for path in outputs):
        raise FileExistsError("Review output exists; never overwrite owner annotations")
    for path, body in outputs.items():
        with path.open("x", encoding="utf-8") as handle:
            handle.write(body)
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()
