"""Materialize a manual AI semantic review of the fixed 25-record snapshot."""

import copy
import json
from collections import Counter
from pathlib import Path

from grounding_verifier.cli import read_json, write_json
from grounding_verifier.dataset import dataset_hash, digest, load_cases
from grounding_verifier.evaluation import output_hash, score
from grounding_verifier.gold_review import fenced

HERE = Path("experiments/2026-10-18-challenges-v2")
BUNDLE_DIGEST = "470cf4ffbce58a301efdb71679973dd1fec14d68c6595fc4c5046a2bc75c7a51"


def align(packet):
    """These decisions are authored after reading the bound outputs, not inferred by IDs."""
    result = copy.deepcopy(packet)
    result.update(
        status="ai_proposed",
        reviewer=None,
        ai_reviewer="Codex",
        ai_review_date="2026-10-19",
        units=[],
        reasoning_findings=[],
        owner_decision=None,
        owner_note="",
    )
    cid, config = packet["case_id"], packet["configuration"]
    predictions = packet["prediction"]["claims"]
    gold = {g["id"]: g for g in packet["gold_claims"]}

    def unit(index, gid, sufficient, note, text=None, attention=False):
        result["units"].append(
            {
                "prediction_index": index,
                "text": text or predictions[index]["claim_text"],
                "gold_id": gid,
                "evidence_sufficient": sufficient,
                "note": note,
                "needs_owner_attention": attention,
                "owner_decision": None,
                "owner_note": "",
            }
        )

    if cid == "challenge-01":
        assert len(predictions) == 4
        unit(0, "g1", True, "每租户四个活跃任务的额度、对象及状态完整对应；引文直接支持。")
        unit(
            1,
            "g2",
            True,
            "保留 additional 与租户范围。other jobs 的局部指代可解析为"
            "活跃任务之外的队列任务；引文中的 up to three 已覆盖额度。",
        )
        unit(
            2,
            "g3",
            True,
            "明确的 not per tenant 足以否定所声称的租户配额作用域；"
            "不需要额外推导每租户实际连接容量。",
        )
        unit(3, "g4", None, "三十天保留期完整对应 gold；U 不参与证据充分率分母。")
    elif cid == "challenge-02":
        assert len(predictions) == 2
        full = config.endswith("passage")
        if full:
            note = "最终引文覆盖完整位置链及单 host、单 region、East/West 不同的排除前提。"
        elif config == "refined-v2":
            note = "标签与事实对应，但引文遗漏每 worker 只有一个 host；仅证明 Quartz 在 East，"
            note += "不足以在当前显式排他口径下排除同一 worker 另在 West 的 host 上运行。"
        else:
            note = "标签与事实对应，但引用仅有 East 放置链，遗漏排除 West 所需的"
            note += "单 host/单 region/不同区域前提。reasoning 提及不等于 citations 已包含。"
        unit(0, "g1", full, note)
        unit(1, "g2", True, "Sable→Gamma→West 正向链完整；支持一个位置不需要排除其他位置。")
    elif cid == "challenge-03":
        if config in {"minimal", "lean-v1-passage"}:
            assert len(predictions) == 2
            unit(
                0,
                None,
                None,
                "无匹配：删除 after its timeout 后只剩较宽泛的重试命题；"
                "不能为匹配 gold 从下一条补入条件。此条计额外单元，不是 gold 的首次完整匹配。",
            )
            unit(
                1,
                "g1",
                None,
                "保留重试与 timeout 的完整关系。the request/automatic retry 的"
                "对象按本案例唯一请求和 PatchFerry 解析，仅解析指代，不补入新条件。",
            )
            result["reasoning_findings"].append(
                "第一条理由将规则写成 only，过强。minimal 第二条又写 Bronze 不覆盖 timeouts，"
                "以及 only route；原文只给出部分正向规则。Lean 第二条较克制。"
                if config == "minimal"
                else "第一条理由写 enables automatic retries only for，给原文规则增加排他性；"
                "U 标签正确不能掩盖这项理由问题。"
            )
        else:
            assert len(predictions) == 1
            unit(0, "g1", None, "完整保留主语、重试行为及 timeout 限定；U 对应 gold。")
            result["reasoning_findings"].append(
                {
                    "refined-v1": "理由 retries ... only after a connection reset 把充分条件写成"
                    "必要条件。结尾仍正确区分缺证据与直接反驳；保留 U，但标记理由缺陷。",
                    "refined-v2": "stated only for 在此限定已陈述证据，并且结尾明确不能排除其他"
                    "重试机制；不与明确声称 retries only after 的措辞混为一谈。",
                    "refined-v2-passage": "核心缺证据推理成立。关于可能还有其他 route 的补充"
                    "不是得出 U 的必要理由，属于可删的旁支。",
                }[config]
            )
    elif cid == "challenge-04":
        assert len(predictions) == 2
        unit(0, "g1", True, "产品、只读 endpoint 与路径对应，引用有直接依据。")
        unit(1, "g2", None, "保留所有记录及 AES-256 范围；指令段不构成加密证据，U 对应。")
    elif cid == "challenge-05":
        if config in {"minimal", "refined-v1"}:
            assert len(predictions) == 2
            unit(
                0,
                "g1",
                False,
                "从复合预测拆出状态写入，保留 reported-success 条件。"
                "当前引文只含动作，未引入成功必须在提交后的独立条件。",
                text=gold["g1"]["claim_text"],
            )
            unit(
                0,
                "g2",
                False,
                "从同一预测拆出删除，保留成功范围；继承该预测自己的引文，"
                "不能借第二条预测的提交句补证据。",
                text=gold["g2"]["claim_text"],
            )
            unit(
                0,
                None,
                False,
                "部分对应 g3，但本条没有 committed；严格保留该显式限定，"
                "不从来源知识或下一条预测补进本条。建议列为额外的部分关系单元；"
                "这属于粒度差异，不是认定其所述同事务关系为假。",
                text="For a delivery reported as successful, the status update and "
                "receipt-record deletion occurred in the same transaction.",
                attention=True,
            )
            unit(
                1,
                "g3",
                True,
                "建议对应 g3：本条明确提交和成功的关系；"
                + (
                    "状态写入/删除直接出现于本条。"
                    if config == "minimal"
                    else "that transaction 按上一条唯一共享事务作局部指代解析。"
                )
                + "证据中的 this transaction 按同段唯一回执事务解析，提交条件本身已引用。"
                "这里只绑定事务对象，不借用另一预测的引文。请重点确认这种指代解析范围。",
                attention=True,
            )
            result["reasoning_findings"].append(
                "修正早期“可能重复”的预审：在本次严格保留 committed 的主对齐下，"
                "第一条的部分关系没有抢占 g3，第二条才是完整匹配，故主建议不计重复。"
                "若采用更宽松的关系等价或更严格的独立句指代口径，须统一修改两配置，"
                "不能按标签或引用好坏择优。"
            )
        elif config in {"refined-v2", "refined-v2-passage"}:
            assert len(predictions) == 1
            for gid in ("g1", "g2", "g3"):
                unit(
                    0,
                    gid,
                    True,
                    "复合预测明确包含本单元，保留 reported success/committed；"
                    "拆分后继承同一 S 和全部引用。引用覆盖动作及提交条件；"
                    "ParcelMoth 可由同段主语解析。原始预测仍非原子。",
                    text=gold[gid]["claim_text"],
                )
        else:
            assert config == "lean-v1-passage" and len(predictions) == 3
            for i, gid in enumerate(("g1", "g2", "g3")):
                unit(
                    i,
                    gid,
                    True,
                    "一一对应；成功条件和事务关系保留，完整引用覆盖依据。"
                    "claim_text 直/曲引号差异不改变语义，逐字要求适用于 citations。",
                )
    else:
        raise ValueError(cid)
    seen, duplicates = set(), []
    for entry in result["units"]:
        gid = entry["gold_id"]
        entry["alignment_kind"] = (
            "unmatched" if gid is None else ("duplicate" if gid in seen else "matched")
        )
        if gid in seen:
            duplicates.append(gid)
        if gid is not None:
            seen.add(gid)
        entry["verdict_matches_gold"] = (
            predictions[entry["prediction_index"]]["verdict"] == gold[gid]["verdict"]
            if gid
            else None
        )
    result["missing_gold_ids"] = sorted(set(gold) - seen)
    result["duplicate_gold_ids"] = duplicates
    result["atomic_prediction_indices"] = [
        i for i, n in Counter(u["prediction_index"] for u in result["units"]).items() if n == 1
    ]
    return result


def main():
    bundle = read_json(HERE / "review-bundle.json")
    assert digest(bundle) == BUNDLE_DIGEST, "Review input changed; reread before applying decisions"
    cases = load_cases(Path("data/development-challenges-v2/dev.jsonl"))
    assert dataset_hash(cases) == bundle["dataset_hash"]
    reviews = [align(packet) for packet in bundle["packets"]]
    counts = Counter()
    for review in reviews:
        assert review["prediction"] == next(
            p["prediction"]
            for p in bundle["packets"]
            if p["case_id"] == review["case_id"] and p["configuration"] == review["configuration"]
        )
        indices = [u["prediction_index"] for u in review["units"]]
        assert indices == sorted(indices)
        assert set(indices) == set(range(len(review["prediction"]["claims"])))
        counts.update(packets=1, predictions=len(set(indices)), units=len(indices))
        for u in review["units"]:
            claim = review["prediction"]["claims"][u["prediction_index"]]
            assert u["text"].strip()
            assert (
                u["evidence_sufficient"] is None
                if claim["verdict"] == "UNSUPPORTED"
                else (type(u["evidence_sufficient"]) is bool)
            )
            counts[u["alignment_kind"]] += 1
    # The production scorer must keep every AI-only review pending.
    for config in dict.fromkeys(p["configuration"] for p in reviews):
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
        "review_date": "2026-10-19",
        "input_bundle_digest": BUNDLE_DIGEST,
        "dataset_hash": dataset_hash(cases),
        "counts": dict(counts),
        "reviews": reviews,
        "scope": "All 25 challenge-v2 outputs; final citations; no original-dev or repeat review.",
        "method": "AI semantic rereview after access to configurations and earlier outputs; "
        "not blind or human-approved. No complete semantic score is emitted.",
    }
    lines = [
        "# 开发挑战 v2：AI 已填写对齐稿",
        "",
        "2026-10-19。覆盖五配置的全部25份输出，56条原始预测，拆成64个评分单元。"
        "下列对齐、证据判断和理由均为 AI 建议，人工决定留空。完整 gold 仍待最终批准。",
        "",
        "## 先看主建议",
        "",
        "- challenge-01/04：各配置均一一对应，S/C 的最终引文充分。",
        "- challenge-02：production 事实都对应 g1；三个片段引用配置缺少排除前提，"
        "证据标为不充分。两个完整段落配置包含前提。staging 的 g2 均充分。",
        "- challenge-03：minimal/Lean 第一条漏掉 timeout，标为无匹配额外单元；"
        "第二条完整对应 g1。其他三配置直接对应 g1。理由里过强的 only 另行标记。",
        "- challenge-05：两个 v2 配置的一条复合预测拆成三个单元；Lean 三条一一对应。"
        "minimal/refined-v1 的第一条拆出 g1/g2 及缺 committed 的部分关系，"
        "第二条才建议对应完整 g3。此处有指代和粒度边界，已标重点确认。",
        "",
        "主建议得到60个首次匹配、4个无匹配单元、0个重复和0个遗漏；"
        "这是对齐数量，不是已批准质量分数。四个无匹配分别是两条缺 timeout 的重试事实，"
        "和两条缺 committed 的部分事务关系。最后两条不是断言为假，主要是拆分粒度不一致。",
        "",
        "## 容易影响结论的口径",
        "",
        "事实对齐只看语义，不按 verdict 或引文好坏选匹配。保留显式限定，不把来源中的"
        "知识补成预测文本；局部指代可以解析。每个单元继承所属预测的 verdict/citations，"
        "不得跨预测拼接引用。证据判断针对最终引用；原始片段/合法率仍见原运行。",
        "",
        "对 challenge-05 第二条，主建议允许 this/that transaction 指向唯一的回执事务，"
        "其已引用提交条件足够支持该指代对象的提交关系。如果你认为这已超过指代解析而"
        "是在补入独立的动作关系前提，可以把该单元证据改为不充分；refined-v1 的语义"
        "对齐也可能需要保留为部分对应。这样会影响证据或覆盖，但不能悄悄选择较好结果。",
        "",
        "此前预审写过“可能重复”；完整对齐后，不能将缺少 committed 的关系与完整 g3"
        "直接等同。因此本稿不把第一条当作已占用 g3，也不把第二条自动判重复。"
        "如果接受第一条隐含 committed 的宽松解读，须一致应用首次匹配/重复规则。",
        "",
        "## 快速总表",
        "",
        "表内预测索引从0开始；同一索引重复出现表示人工拆分。`无`表示无完整gold匹配。",
        "",
        "| 配置 | 案例 | 预测→gold | 证据不足单元 | 遗漏 |",
        "|---|---|---|---|---|",
    ]
    for review in reviews:
        mapping = "; ".join(
            f"[{u['prediction_index']}]→{u['gold_id'] or '无'}" for u in review["units"]
        )
        insuff = "; ".join(
            f"[{u['prediction_index']}]/{u['gold_id'] or '部分关系'}"
            for u in review["units"]
            if u["evidence_sufficient"] is False
        )
        lines.append(
            f"| {review['configuration']} | {review['case_id']} | {mapping} | "
            f"{insuff or '无（U不适用）'} | {','.join(review['missing_gold_ids']) or '无'} |"
        )
    lines += [
        "",
        "## 完整逐项对齐（可填写你的意见）",
        "",
        "每个案例先列全部原文与gold，再按配置展示原预测及本次拆分。JSON对应文件为"
        "ai-alignment-2026-10-19.json；它保持 ai_proposed，标准评分器仍要求人工审核。",
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
            lines += [
                f"### {review['configuration']}",
                "",
                f"原输出哈希：`{review['output_hash']}`。",
                "",
            ]
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
                for q in prediction["citations"]:
                    lines += [f"Citation [{q['index']}]", "", fenced(q["quote"], "text"), ""]
                if not prediction["citations"]:
                    lines += ["Citations: `[]`", ""]
                for n, u in enumerate(
                    [u for u in review["units"] if u["prediction_index"] == i], 1
                ):
                    ev = (
                        "不适用（U）"
                        if u["evidence_sufficient"] is None
                        else ("充分" if u["evidence_sufficient"] else "不充分")
                    )
                    attention = "；**重点确认**" if u["needs_owner_attention"] else ""
                    lines += [
                        f"**单元 {n} → {u['gold_id'] or '无完整匹配'}；证据：{ev}{attention}**",
                        "",
                        fenced(u["text"], "text"),
                        "",
                        u["note"],
                        "",
                        "| 你的复核 | 填写处 |",
                        "|---|---|",
                        "| 同意或修改对齐 | 待填写 |",
                        "| 同意或修改证据判断 / 备注 | 待填写 |",
                        "",
                    ]
    write_json(HERE / "ai-alignment-2026-10-19.json", result)
    with (HERE / "ai-alignment-2026-10-19.zh-CN.md").open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print(json.dumps(result["counts"]))


if __name__ == "__main__":
    main()
