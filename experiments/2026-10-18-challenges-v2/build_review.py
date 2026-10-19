"""Export v2 review packets with exact input checks and explicit record provenance."""

import copy
import json
from pathlib import Path

from rerun_changed_input import DATA, HERE, OLD, SPECS

from grounding_verifier.cli import read_json, write_json
from grounding_verifier.dataset import dataset_hash, digest, load_cases
from grounding_verifier.domain import VerificationReport, validate_report
from grounding_verifier.evaluation import output_hash, review_template, score
from grounding_verifier.gold_review import fenced

AI_NOTES = {
    "minimal": "两条输出。第一条合并写状态、删除及同事务，第二条又表达提交关系。"
    "需先对第一条按语义拆分，确认 g3 是否已覆盖，再处理第二条可能的重复；"
    "不得挑选后一个引文较好的重复来替换首次匹配。第一条引文只有动作句，缺少成功"
    "必须在提交后的独立前提；第二条引文则只有提交句，动作对象依赖局部指代。"
    "按已约定的“局部指代可解析、独立前提不可补引”口径逐单元判断证据。",
    "refined-v1": "两条输出。第一条仍合并两个动作及同事务，引用仅动作片段；"
    "第二条单独表达提交条件。需确认事务事实的对齐、重复及限定条件是否完整。"
    "两个预测之间不自动合并 citations 来修复各自的证据缺口。",
    "refined-v2": "一条复合输出保留报告成功、两个动作及同一已提交事务。"
    "引用同时包含动作和提交前提，AI 倾向证据充分。可拆为三个评分单元并继承"
    "同一标签/引文，但原始输出仍是一条复合事实，原子性应另行记录。",
    "refined-v2-passage": "一条复合输出包含三个 gold 语义单元；完整段落同时包含"
    "动作及提交前提，AI 倾向证据充分。扩展后的引文较长，原子性问题仍存在；"
    "需把原始短引文与最终引文区别开。",
    "lean-v1-passage": "三条独立输出分别表达状态、删除和提交后的共同事务关系，"
    "限定条件保留，完整引文覆盖依据。AI 未发现本次输出的明显语义缺陷。"
    "claim_text 的直引号与原文曲引号语义一致，不要求 claim_text 逐字；"
    "citations 仍须保留原文字符。单例一次成功不能证明此方案整体最优。",
}


def main():
    cases = load_cases(DATA / "dev.jsonl")
    old_cases = load_cases(Path("data/development-challenges-v1/dev.jsonl"))
    old_by_id = {c.id: c for c in old_cases}
    new_by_id = {c.id: c for c in cases}
    packets, sources, summaries = [], [], []
    fresh_calls = 0
    fresh_cost = 0.0
    for name, _, _, _, prior_name in SPECS:
        prior_path = OLD / f"{prior_name}.json"
        fresh_path = HERE / f"{name}-challenge05.json"
        prior, fresh = read_json(prior_path), read_json(fresh_path)
        assert prior["dataset_hash"] == dataset_hash(old_cases)
        assert fresh["dataset_hash"] == dataset_hash([new_by_id["challenge-05"]])
        assert fresh["prompt"] == prior["prompt"]
        assert fresh["model"] == prior["model"] and fresh["effort"] == prior["effort"]
        assert (prior.get("citation_policy") or "span") == fresh["citation_policy"]
        fresh_summary = score(fresh, [new_by_id["challenge-05"]])
        assert fresh_summary["semantic_status"] == "pending_human_review"
        summaries.append(
            {"configuration": name, "run_path": str(fresh_path), "automatic_metrics": fresh_summary}
        )
        fresh_calls += fresh_summary["counts"].get("calls", 0)
        fresh_cost += fresh_summary["confirmed_cost_usd"]
        old_records = {r["case_id"]: r for r in prior["records"]}
        assert len(old_records) == len(cases)
        sources.append(
            {
                "configuration": name,
                "old_run": {"path": str(prior_path), "digest": digest(prior)},
                "new_run": {"path": str(fresh_path), "digest": digest(fresh)},
            }
        )
        for case in cases:
            reused = case.id != "challenge-05"
            if reused:
                assert old_by_id[case.id].request() == case.request(), "Changed input cannot reuse"
            run, path = (prior, prior_path) if reused else (fresh, fresh_path)
            record = old_records[case.id] if reused else fresh["records"][0]
            assert record["output_hash"] == output_hash(record)
            if record["status"] == "ok":
                validate_report(
                    VerificationReport.model_validate(record["output"]), case.context_passages
                )
            stub = {"dataset_hash": dataset_hash(cases), "records": [copy.deepcopy(record)]}
            export = review_template(stub, new_by_id)
            packet = (
                export[0]
                if export
                else {
                    "case_id": case.id,
                    "status": "technical_failure",
                    "error": record.get("error"),
                    "output_hash": output_hash(record),
                    "dataset_hash": dataset_hash(cases),
                    "context_passages": case.context_passages,
                    "generated_answer": case.generated_answer,
                    "gold_claims": [g.model_dump(mode="json") for g in case.gold_claims],
                    "prediction": None,
                    "units": [],
                }
            )
            packet["configuration"] = name
            packet["provenance"] = {
                "execution": "reused_unchanged_request" if reused else "new_v2_request",
                "source_run_path": str(path),
                "source_run_digest": digest(run),
                "source_dataset_hash": run["dataset_hash"],
                "source_code_hash": run["source_hash"],
                "source_created_at": run["created_at"],
                "request_hash": digest(case.request().model_dump(mode="json")),
                "prompt_hash": digest(run["prompt"]),
                "output_hash": output_hash(record),
                "model": run["model"],
                "effort": run["effort"],
                "source_record_digest": digest(record),
            }
            packet["first_output"] = record.get("trace", {}).get("first_output")
            packet["recorded_trace"] = copy.deepcopy(record.get("trace", {}))
            packets.append(packet)
    assert len(packets) == 25 and fresh_calls == 5
    lines = [
        "# 开发挑战 v2：完整输出审阅",
        "",
        "范围：5 个案例 × 5 套既有配置，共 25 份输出。仅 challenge-05 的五份是新增调用，"
        "其他二十份经输入逐项一致性检查后复用；没有继承旧审批。",
        "",
        "gold 仍为 draft。四项澄清方案已获你认可，尚未记录其余 gold 与新版完整措辞的"
        "最终批准；输出事实对齐和证据审核也是独立步骤。先确认 gold，再填写输出意见。",
        "",
        "## 本次新增运行",
        "",
        "| 配置 | 输出条数 | 原/终引文合法数 | 实测秒数 | 本次费用估算 USD |",
        "|---|---:|---|---:|---:|",
    ]
    for summary in summaries:
        name, metrics = summary["configuration"], summary["automatic_metrics"]
        fresh = read_json(HERE / f"{name}-challenge05.json")
        record = fresh["records"][0]
        counts = metrics["counts"]
        legality = (
            f"{counts.get('first_valid_quotes', 0)}/{counts.get('first_quotes', 0)} → "
            f"{counts.get('final_valid_quotes', 0)}/{counts.get('final_quotes', 0)}"
        )
        lines.append(
            f"| {name} | {len((record.get('output') or {}).get('claims', []))} | "
            f"{legality} | {record['trace']['latency_seconds']:.3f} | "
            f"{metrics['confirmed_cost_usd']:.7f} |"
        )
    lines += [
        "",
        f"新增 {fresh_calls} 次 API 调用，配置费率估算合计 ${fresh_cost:.7f}。"
        "每配置只有一个新样本，且是首次客户端调用；不据此排名延迟。旧输出的历史用量"
        "和耗时保存在 JSON 中，不计作本次新增费用，也不当成当前串行评测延迟。",
        "",
        "## AI 对新增 challenge-05 的预审（待你复核）",
        "",
        "这不是人工批准或完整评分。所有方法本次都返回 S；重点审核拆分、重复和证据。",
        "",
    ]
    for name, text in AI_NOTES.items():
        lines += [f"**{name}**", "", text, ""]
    lines += [
        "## 填写规则",
        "",
        "每条预测填 gold ID（g1/g2/g3 等，或无匹配）及证据是否充分；复合预测需要"
        "按事实单元分行，继承原 verdict/citations。重复按输出顺序首次匹配，后续计多余；"
        "不同预测之间不合并引文。限定条件不能丢失，原子性独立记录。"
        "本文按案例给出原文一次，再展示五配置全部预测，引用和理由均不截断。",
        "",
        "[新版 gold 全文字段](../../reviews/development-challenges-v1/clarified-gold-v2.zh-CN.md)。"
        " JSON 包 review-bundle.json 保存逐条来源摘要、哈希、原/终输出、trace 及 pending 字段。"
        "请在本文填写，后续依实际保存意见导入，JSON 不会自动同步。",
        "",
    ]
    for case in cases:
        lines += [f"## {case.id}", "", f"来源分组：`{case.source_group}`。", ""]
        for i, passage in enumerate(case.context_passages):
            lines += [f"### 原文 [{i}]", "", fenced(passage, "text"), ""]
        lines += [
            "### 待核验答案",
            "",
            fenced(case.generated_answer, "text"),
            "",
            "### 本版 gold（全部字段）",
            "",
        ]
        for gold in case.gold_claims:
            lines += [
                f"**{gold.id} · {gold.verdict.value}**",
                "",
                fenced(gold.claim_text, "text"),
                "",
                "Reasoning: " + gold.reasoning,
                "",
                "Annotation reason: " + gold.annotation_reason,
                "",
            ]
            for citation in gold.citations:
                lines += [f"Citation [{citation.index}]", "", fenced(citation.quote, "text"), ""]
            if not gold.citations:
                lines += ["Citations: `[]`", ""]
        for packet in [p for p in packets if p["case_id"] == case.id]:
            name, provenance = packet["configuration"], packet["provenance"]
            origin = (
                "旧输出，输入完全一致"
                if provenance["execution"].startswith("reused")
                else "新增运行"
            )
            lines += [
                f"### {name} · {origin}",
                "",
                f"源运行：`{provenance['source_run_path']}`。",
                "",
                f"输出哈希：`{provenance['output_hash']}`。",
                "",
            ]
            if not packet["prediction"]:
                lines += [fenced(json.dumps(packet.get("error"), ensure_ascii=False), "json"), ""]
                continue
            for i, claim in enumerate(packet["prediction"]["claims"]):
                lines += [
                    f"**预测 [{i}] · {claim['verdict']}**",
                    "",
                    fenced(claim["claim_text"], "text"),
                    "",
                    claim["reasoning"],
                    "",
                ]
                for citation in claim["citations"]:
                    lines += [
                        f"Citation [{citation['index']}]",
                        "",
                        fenced(citation["quote"], "text"),
                        "",
                    ]
                if not claim["citations"]:
                    lines += ["Citations: `[]`", ""]
                lines += [
                    "| 你的审核字段 | 填写处 |",
                    "|---|---|",
                    "| 对齐 gold / 拆分后的各单元 | 待填写 |",
                    "| 各单元证据充分性 | 待填写 |",
                    "| 重复 / 多余 / 遗漏及备注 | 待填写 |",
                    "",
                ]
            if not packet["prediction"]["claims"]:
                lines += ["预测 claims=[]。本案例有事实，需要审查遗漏。", ""]
    ledger = read_json(Path(".budget/ledger.json"))
    bundle = {
        "status": "pending_gold_and_output_owner_review",
        "dataset_hash": dataset_hash(cases),
        "gold_manifest": read_json(DATA / "manifest.json"),
        "sources": sources,
        "new_calls": fresh_calls,
        "reused_records": 20,
        "new_cost_estimate_usd": fresh_cost,
        "ledger_snapshot": ledger,
        "new_run_automatic_summaries": summaries,
        "ai_review_new_case_only": AI_NOTES,
        "packets": packets,
        "note": "No combined live latency or complete semantic scores; records span executions.",
    }
    write_json(HERE / "review-bundle.json", bundle)
    with (HERE / "output-review.zh-CN.md").open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print(
        json.dumps(
            {
                "packets": len(packets),
                "new_calls": fresh_calls,
                "new_cost_estimate_usd": fresh_cost,
                "ledger": ledger,
            }
        )
    )


if __name__ == "__main__":
    main()
