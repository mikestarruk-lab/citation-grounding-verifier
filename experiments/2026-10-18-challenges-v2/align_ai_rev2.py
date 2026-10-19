"""Revise the AI alignment draft with one reference rule and original-citation evidence.

Revision 1 (align_ai.py) stays unchanged as historical evidence. This script reuses
its decisions, applies the explicit revisions below and writes separate rev2 files.
"""

import json
import sys
from collections import Counter
from pathlib import Path

from grounding_verifier.cli import read_json, write_json
from grounding_verifier.dataset import dataset_hash, digest, load_cases
from grounding_verifier.evaluation import output_hash, score
from grounding_verifier.gold_review import fenced

sys.path.insert(0, str(Path(__file__).resolve().parent))
from align_ai import BUNDLE_DIGEST, HERE, align  # noqa: E402

REV1 = HERE / "ai-alignment-2026-10-19.json"

REFERENCE_RULE = (
    "预测文本中的指代只能解析到实体（如本案例唯一的请求或回执事务），"
    "匹配 gold 所需的命题内容必须出现在该预测自己的文本中，不能从另一条预测借入。"
    "引文中的指代同样只解析对象；独立必要的前提必须出现在该预测自己的引文里，"
    "这与 challenge-02 要求引用单 host/单 region 前提、以及 refined-v2 提示词的规则一致。"
)

# Original (pre-expansion) citation judgments for passage configurations, keyed by
# (case, configuration, prediction index, gold id). Span configurations have identical
# first/final citations, so their original judgment equals the final one.
ORIGINAL = {
    ("challenge-02", "refined-v2-passage", 0, "g1"): (
        False,
        "原始引文含单 region 与 East/West 不同，但缺“每个 worker 只有一个 host”，"
        "与 refined-v2 片段配置相同，排除 West 的前提不完整。",
    ),
    ("challenge-02", "lean-v1-passage", 0, "g1"): (
        False,
        "原始引文只有 Quartz→Delta→East 正向链，与 minimal 相同，缺单 host、单 region、"
        "East/West 不同三个排除前提；理由也未使用这些前提。",
    ),
    ("challenge-05", "lean-v1-passage", 0, "g1"): (
        False,
        "原始引文只含动作与 one transaction，缺“提交后才报告成功”的条件，"
        "与 minimal/refined-v1 第一条的判断口径相同。",
    ),
    ("challenge-05", "lean-v1-passage", 1, "g2"): (
        False,
        "原始引文只有删除动作片段，缺提交后才报告成功的条件。",
    ),
    ("challenge-05", "lean-v1-passage", 2, "g3"): (
        False,
        "原始引文只有提交句，缺“两个动作在同一事务”这一独立必要前提；"
        "this transaction 只能解析对象，不能代替该前提。",
    ),
}


def revise(review):
    cid, config = review["case_id"], review["configuration"]
    first = review["first_output"]["claims"]
    final = review["prediction"]["claims"]
    passage = config.endswith("passage")
    review["revision"] = "rev2"
    review["revision_changes"] = []

    if cid == "challenge-05" and config in {"minimal", "refined-v1"}:
        unit = next(u for u in review["units"] if u["prediction_index"] == 1)
        assert unit["gold_id"] == "g3" and unit["evidence_sufficient"] is True
        unit["evidence_sufficient"] = False
        if config == "refined-v1":
            unit["gold_id"] = None
            unit["note"] = (
                "rev2 改为无完整匹配：本条只断言 that transaction 已提交；“状态写入与删除在"
                "同一事务”是 g3 的核心命题，只出现在第一条预测中。按统一口径，that 只能解析"
                "对象，不能借入另一条预测的命题内容。rev1 曾借上一条完成匹配，与 challenge-03"
                "拒绝从下一条补入 timeout 的处理不一致。证据另判不充分：引文只有提交句。"
            )
            review["revision_changes"].append("[1]→g3 改为无完整匹配；g3 变为遗漏；证据改为不充分")
        else:
            unit["note"] = (
                "建议对应 g3：本条文本自身包含状态写入、删除、同一事务及提交后才报告成功。"
                "rev2 将证据改为不充分：引文只有提交句，“两个动作在同一事务”是独立必要前提，"
                "this transaction 只能解析对象，不能代替该前提；口径同 challenge-02。"
            )
            review["revision_changes"].append("[1]→g3 证据由充分改为不充分")
        unit["needs_owner_attention"] = True

    if cid == "challenge-05" and config in {"minimal", "refined-v1"}:
        partial = next(
            u for u in review["units"] if u["prediction_index"] == 0 and u["gold_id"] is None
        )
        partial["note"] += (
            " rev2 补充：该单元按主建议计为额外单元（误报）。另一可选规则是把它视为同一输出中"
            "完整关系的较弱表述而不计分；无论选哪种，须同时适用于 minimal 与 refined-v1，"
            "且在看到分数前确定。"
        )

    for unit in review["units"]:
        i, gid = unit["prediction_index"], unit["gold_id"]
        if unit["evidence_sufficient"] is None:
            unit["evidence_sufficient_original_citations"] = None
            continue
        if not passage:
            assert first[i]["citations"] == final[i]["citations"]
            unit["evidence_sufficient_original_citations"] = unit["evidence_sufficient"]
            continue
        key = (cid, config, i, gid)
        if key in ORIGINAL:
            value, note = ORIGINAL[key]
            unit["evidence_sufficient_original_citations"] = value
            unit["original_citation_note"] = note
        else:
            unit["evidence_sufficient_original_citations"] = unit["evidence_sufficient"]
            unit["original_citation_note"] = "模型原始片段引文已包含所需前提，判断与扩展后相同。"
        if unit["evidence_sufficient"] and not unit["evidence_sufficient_original_citations"]:
            unit["note"] += (
                " rev2：最终引文充分仅因程序把已引用段落扩展为整段；模型原始引文不充分。"
            )
    if passage and any(
        u["evidence_sufficient"] != u["evidence_sufficient_original_citations"]
        for u in review["units"]
    ):
        review["revision_changes"].append("补充原始引文证据判断；扩展前不充分的单元已标注")

    seen, duplicates = set(), []
    for entry in review["units"]:
        gid = entry["gold_id"]
        entry["alignment_kind"] = (
            "unmatched" if gid is None else ("duplicate" if gid in seen else "matched")
        )
        if gid in seen:
            duplicates.append(gid)
        if gid is not None:
            seen.add(gid)
        entry["verdict_matches_gold"] = (
            final[entry["prediction_index"]]["verdict"]
            == next(g for g in review["gold_claims"] if g["id"] == gid)["verdict"]
            if gid
            else None
        )
    review["missing_gold_ids"] = sorted({g["id"] for g in review["gold_claims"]} - seen)
    review["duplicate_gold_ids"] = duplicates
    return review


def ev_label(value):
    return "不适用（U）" if value is None else ("充分" if value else "不充分")


def main():
    bundle = read_json(HERE / "review-bundle.json")
    assert digest(bundle) == BUNDLE_DIGEST, "Review input changed; reread before applying decisions"
    rev1 = read_json(REV1)
    cases = load_cases(Path("data/development-challenges-v2/dev.jsonl"))
    assert dataset_hash(cases) == bundle["dataset_hash"] == rev1["dataset_hash"]
    base = [align(packet) for packet in bundle["packets"]]
    assert base == rev1["reviews"], "rev1 decisions no longer reproduce; do not revise blindly"
    reviews = [revise(json.loads(json.dumps(r))) for r in base]

    counts = Counter()
    per_config = {}
    for review in reviews:
        indices = [u["prediction_index"] for u in review["units"]]
        assert indices == sorted(indices)
        assert set(indices) == set(range(len(review["prediction"]["claims"])))
        counts.update(packets=1, predictions=len(set(indices)), units=len(indices))
        counts.update(missing_gold=len(review["missing_gold_ids"]))
        stats = per_config.setdefault(
            review["configuration"],
            Counter(),
        )
        for u in review["units"]:
            claim = review["prediction"]["claims"][u["prediction_index"]]
            assert (u["evidence_sufficient"] is None) == (claim["verdict"] == "UNSUPPORTED")
            counts[u["alignment_kind"]] += 1
            stats[u["alignment_kind"]] += 1
            if u["gold_id"] and u["evidence_sufficient"] is not None:
                stats["evidence_units"] += 1
                stats["final_sufficient"] += u["evidence_sufficient"]
                stats["original_sufficient"] += u["evidence_sufficient_original_citations"]
        stats["missing_gold"] += len(review["missing_gold_ids"])

    for config in per_config:
        selected = [p for p in reviews if p["configuration"] == config]
        records = [
            {"case_id": p["case_id"], "status": "ok", "output": p["prediction"]} for p in selected
        ]
        assert all(
            output_hash(r) == p["output_hash"] for r, p in zip(records, selected, strict=True)
        )
        result = score(
            {
                "dataset_hash": dataset_hash(cases),
                "mode": "e2e",
                "method": config,
                "records": records,
            },
            cases,
            selected,
        )
        assert result["semantic_status"] == "pending_human_review" and "f1" not in result

    result = {
        "status": "ai_proposed_owner_pending",
        "revision": "rev2",
        "review_date": "2026-10-19",
        "supersedes": str(REV1.as_posix()),
        "input_bundle_digest": BUNDLE_DIGEST,
        "rev1_digest": digest(rev1),
        "dataset_hash": dataset_hash(cases),
        "reference_rule": REFERENCE_RULE,
        "counts": dict(counts),
        "per_configuration": {k: dict(v) for k, v in per_config.items()},
        "reviews": reviews,
        "scope": "All 25 challenge-v2 outputs. Evidence is judged on final citations and, "
        "separately, on the model's original citations before passage expansion.",
        "method": "AI revision of an AI semantic rereview after access to configurations and "
        "earlier outputs; not blind or human-approved. No complete semantic score is emitted.",
    }

    lines = [
        "# 开发挑战 v2：AI 对齐稿修订版（rev2）",
        "",
        "2026-10-19。覆盖五配置的全部 25 份输出、56 条原始预测、64 个评分单元。"
        "全部对齐与证据判断仍是 AI 建议，人工决定留空，不构成批准。"
        "rev1 原稿 `ai-alignment-2026-10-19.*` 原样保留；本稿只做下列修订。",
        "",
        "## 本次修订了什么",
        "",
        "1. **统一指代口径。** " + REFERENCE_RULE,
        "2. **challenge-05 / refined-v1 第二条改为无完整匹配。** 它只说 that transaction 已提交，"
        "g3 的核心命题（两个动作在同一事务）只在第一条里。rev1 借上一条完成匹配，"
        "与 challenge-03 拒绝从下一条补入 timeout 的处理矛盾。结果：g3 变为遗漏。",
        "3. **challenge-05 / minimal 第二条仍对应 g3，但证据改为不充分。** 文本自身完整，"
        "但引文只有提交句，缺“同一事务”这一独立必要前提。refined-v1 第二条同理。",
        "4. **passage 配置补充原始引文的证据判断。** 两个 passage 配置会在模型输出后，"
        "由程序把已引用段落扩展为整段。rev1 只按扩展后的最终引文判断，"
        "因此 challenge-02 与 challenge-05 中有 5 个单元的“充分”来自扩展，"
        "不是模型自己选出了所需前提。现在两列并列呈现。",
        "5. **minimal/refined-v1 第一条拆出的部分关系单元** 仍按主建议计为额外单元，"
        "另注明可选的“不计分”规则；两配置必须同用一种，并在看分数前确定。",
        "",
        "## 修订后的计数",
        "",
        f"共 {counts['matched']} 个首次匹配、{counts['unmatched']} 个无完整匹配单元、"
        f"{counts.get('duplicate', 0)} 个重复、{counts['missing_gold']} 个遗漏 gold"
        "（rev1 为 60 / 4 / 0 / 0）。这是待审对齐数量，不是正式 F1。",
        "",
        "| 配置 | 匹配 | 无匹配 | 遗漏 gold | 证据充分（最终引文） | 证据充分（原始引文） |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for config, s in per_config.items():
        lines.append(
            f"| {config} | {s['matched']} | {s['unmatched']} | {s['missing_gold']} | "
            f"{s['final_sufficient']}/{s['evidence_units']} | "
            f"{s['original_sufficient']}/{s['evidence_units']} |"
        )
    lines += [
        "",
        "证据列只统计已匹配且非 U 的单元。按原始引文看，两个 passage 配置与片段配置的证据"
        "表现接近；最终引文的差距主要来自程序扩展，比较时应同时报告两列，"
        "不能把扩展后的充分率当作模型选证能力的提升。",
        "",
        "## 快速总表",
        "",
        "预测索引从 0 开始；同一索引重复出现表示人工拆分。`无` 表示无完整 gold 匹配。",
        "",
        "| 配置 | 案例 | 预测→gold | 证据不足（最终） | 证据不足（原始） | 遗漏 | rev2 变化 |",
        "|---|---|---|---|---|---|---|",
    ]
    for review in reviews:
        mapping = "; ".join(
            f"[{u['prediction_index']}]→{u['gold_id'] or '无'}" for u in review["units"]
        )

        def insufficient(field):
            return (
                "; ".join(
                    f"[{u['prediction_index']}]/{u['gold_id'] or '部分关系'}"
                    for u in review["units"]
                    if u[field] is False
                )
                or "无"
            )

        lines.append(
            f"| {review['configuration']} | {review['case_id']} | {mapping} | "
            f"{insufficient('evidence_sufficient')} | "
            f"{insufficient('evidence_sufficient_original_citations')} | "
            f"{','.join(review['missing_gold_ids']) or '无'} | "
            f"{'；'.join(review['revision_changes']) or '—'} |"
        )
    lines += [
        "",
        "## 完整逐项对齐（可填写你的意见）",
        "",
        "每个案例先列全部原文与 gold，再按配置展示原预测、模型原始引文（passage 配置）"
        "及本次拆分。JSON 对应文件为 ai-alignment-2026-10-19.rev2.json；"
        "它保持 ai_proposed，标准评分器仍要求人工审核。",
        "",
    ]
    for case in cases:
        lines += [f"## {case.id}", ""]
        for i, passage in enumerate(case.context_passages):
            lines += [f"### 原文 [{i}]", "", fenced(passage, "text"), ""]
        lines += ["### 答案", "", fenced(case.generated_answer, "text"), "", "### gold", ""]
        for g in case.gold_claims:
            lines += [
                f"**{g.id} · {g.verdict.value}**",
                "",
                fenced(g.claim_text, "text"),
                "",
                "Reasoning: " + g.reasoning,
                "",
                "Annotation reason: " + g.annotation_reason,
                "",
            ]
            for q in g.citations:
                lines += [f"Citation [{q.index}]", "", fenced(q.quote, "text"), ""]
            if not g.citations:
                lines += ["Citations: `[]`", ""]
        for review in [r for r in reviews if r["case_id"] == case.id]:
            passage_config = review["configuration"].endswith("passage")
            lines += [
                f"### {review['configuration']}",
                "",
                f"原输出哈希：`{review['output_hash']}`。",
                "",
            ]
            for change in review["revision_changes"]:
                lines += ["**rev2 修订：** " + change, ""]
            for finding in review["reasoning_findings"]:
                lines += ["**理由 / 对齐边界：** " + finding, ""]
            for i, prediction in enumerate(review["prediction"]["claims"]):
                lines += [
                    f"#### 原预测 [{i}] · {prediction['verdict']}",
                    "",
                    fenced(prediction["claim_text"], "text"),
                    "",
                    prediction["reasoning"],
                    "",
                ]
                label = "最终引文（扩展后）" if passage_config else "引文"
                for q in prediction["citations"]:
                    lines += [f"{label} [{q['index']}]", "", fenced(q["quote"], "text"), ""]
                if not prediction["citations"]:
                    lines += ["Citations: `[]`", ""]
                if passage_config and prediction["citations"]:
                    for q in review["first_output"]["claims"][i]["citations"]:
                        lines += [
                            f"模型原始引文 [{q['index']}]",
                            "",
                            fenced(q["quote"], "text"),
                            "",
                        ]
                for n, u in enumerate(
                    [u for u in review["units"] if u["prediction_index"] == i], 1
                ):
                    attention = "；**重点确认**" if u["needs_owner_attention"] else ""
                    original = (
                        f"；原始引文：{ev_label(u['evidence_sufficient_original_citations'])}"
                        if passage_config and u["evidence_sufficient"] is not None
                        else ""
                    )
                    lines += [
                        f"**单元 {n} → {u['gold_id'] or '无完整匹配'}；"
                        f"证据：{ev_label(u['evidence_sufficient'])}{original}{attention}**",
                        "",
                        fenced(u["text"], "text"),
                        "",
                        u["note"],
                        "",
                    ]
                    if u.get("original_citation_note") and passage_config:
                        lines += ["原始引文判断：" + u["original_citation_note"], ""]
                    lines += [
                        "| 你的复核 | 填写处 |",
                        "|---|---|",
                        "| 同意或修改对齐 | 待填写 |",
                        "| 同意或修改证据判断 / 备注 | 待填写 |",
                        "",
                    ]
    write_json(HERE / "ai-alignment-2026-10-19.rev2.json", result)
    with (HERE / "ai-alignment-2026-10-19.rev2.zh-CN.md").open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print(json.dumps({"counts": counts, "per_configuration": result["per_configuration"]}))


if __name__ == "__main__":
    main()
