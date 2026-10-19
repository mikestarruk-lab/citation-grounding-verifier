import React, { useState } from "react";
import { DataComponent, DataTable, Dropdown, EvidenceChart, Section, SectionHeader, SortableItem, SortableRegion, useDataApp } from "../../data-app-public.jsx";
import "./error-explorer.css";

const pct = v => v == null ? "待审核" : `${(v * 100).toFixed(1)}%`;
const verdicts = ["SUPPORTED", "CONTRADICTED", "UNSUPPORTED"];
const kinds = { all: "全部事实", issues: "全部问题与待审", label: "标签错误", evidence: "证据不充分", compound: "复合预测", pending: "待人工复核" };
const short = { SUPPORTED: "S 支持", CONTRADICTED: "C 矛盾", UNSUPPORTED: "U 无依据" };
const categories = { all: "全部类型", supported: "完全支持", distortion: "数字 / 否定失真", extrinsic: "外部幻觉", multi_passage: "多段落综合" };
const methods = { lexical: "词法原版 · 0.65", minimal: "最简 LLM", "f1-candidate": "词法候选 · F1 优先", "safe-candidate": "词法候选 · 无误支持" };

function Detail({ row }) {
  if (!row) return <p className="ee-empty">当前筛选无记录。调整筛选后可查看完整原文。</p>;
  const d = JSON.parse(row.payload);
  const quotes = items => items.length ? items.map((c, i) => <blockquote key={i}><b>[{c.index}]</b> {c.quote}</blockquote>) : <p>空引用</p>;
  return <div className="ee-detail" data-reviewed-rows>
    <div className="ee-detail-head"><strong>{row.case_id} · {row.gold_id} · prediction {row.prediction_index}</strong><span className="ee-badge">{row.review_status === "pending" ? "新输出待审" : "原输出已审"}</span></div>
    <div className="ee-verdict-line"><span>Gold <b>{row.gold_verdict}</b></span><span>→ 预测 <b>{row.predicted_verdict}</b></span><span>证据：{row.predicted_verdict === "UNSUPPORTED" ? "N/A" : row.evidence_sufficient == null ? "待审核" : row.evidence_sufficient ? "充分" : "不充分"}</span></div>
    <h4>原始上下文</h4>{d.context_passages.map((text, i) => <div className="ee-passage" key={i}><b>Passage [{i}]</b><p>{text}</p></div>)}
    <h4>完整生成答案</h4><p>{d.generated_answer}</p>
    <div className="ee-detail-grid"><section><h4>Gold 事实与判定依据</h4><p>{d.gold?.claim_text}</p><p>{d.gold?.reasoning}</p><p className="ee-muted">{d.gold?.annotation_reason}</p><h4>Gold 引用</h4>{quotes(d.gold?.citations || [])}</section>
      <section><h4>原始预测与判定理由</h4><p>{d.prediction.claim_text}</p><p>{d.prediction.reasoning}</p><h4>实际输出引用</h4>{quotes(d.prediction.citations)}</section></div>
    {d.review_note && <div className="ee-review-note"><b>原审核备注</b><p>{d.review_note}</p></div>}
    {row.review_status === "pending" && <p className="ee-muted">仅复用不变文本的语义对应；原审核备注不构成对新标签或引用的批准。</p>}
    <details><summary>完整字段与输出哈希</summary><pre>{JSON.stringify(d, null, 2)}</pre></details>
  </div>;
}

export default function ErrorExplorer() {
  const { reviewedRows } = useDataApp();
  const comparisons = reviewedRows("comparisons"), thresholds = reviewedRows("thresholds"), units = reviewedRows("units");
  const plottedComparisons = comparisons.map(r => ({...r, f1Rate: r.f1}));
  const baseline = comparisons.find(r => r.config === "lexical");
  const best = comparisons.find(r => r.config === "f1-candidate");
  const safe = comparisons.find(r => r.config === "safe-candidate");
  const [method, setMethod] = useState("lexical"), [kind, setKind] = useState("issues"), [category, setCategory] = useState("all"), [matrix, setMatrix] = useState(null), [selected, setSelected] = useState(null);
  const methodUnits = units.filter(r => r.config === method);
  const rows = methodUnits.filter(r => (category === "all" || r.category === category) && (kind === "all" || (kind === "issues" ? r.errors : r.errors.split(",").includes(kind))) && (!matrix || (r.gold_verdict === matrix[0] && r.predicted_verdict === matrix[1])));
  const active = rows.find(r => r.id === selected) || rows[0];
  const choose = v => { setMethod(v); setMatrix(null); setSelected(null); };
  const reset = () => { setKind("all"); setCategory("all"); setMatrix(null); setSelected(null); };
  const comparisonColumns = [
    { field: "label", label: "方法" }, { field: "score_status", label: "评分状态" },
    { field: "threshold", label: "阈值", renderCell: v => v == null ? "N/A" : v.toFixed(6) },
    { field: "f1", label: "F1", renderCell: pct },
    { field: "false_support", label: "误支持", renderCell: (v, r) => `${v}/${r.non_supported}` },
    { field: "evidenceRate", label: "证据充分", renderCell: (v, r) => v == null ? "待审核" : `${r.evidence_numerator}/${r.evidence_denominator}` },
    { field: "coverage", label: "覆盖率", renderCell: pct }, { field: "success_rate", label: "成功率", renderCell: pct },
  ];
  const unitColumns = [{ field: "case_id", label: "案例" }, { field: "gold_id", label: "事实" }, { field: "text", label: "评分事实单元" }, { field: "gold_verdict", label: "Gold" }, { field: "predicted_verdict", label: "预测" }, { field: "errors", label: "问题", renderCell: v => v ? v.split(",").map(x => kinds[x] || x).join(" / ") : "无已知问题" }];
  return <article className="ee-page">
    <Section id="ee-compare-heading" title="基线与阈值候选" spacing="none">
      <DataComponent id="ee-decision" queryId="comparisons" title="当前建议" kind="custom" displayRows={comparisons} sourceRows={comparisons}>
        <div className="ee-decision" data-reviewed-rows><strong>已确认：保留词法 0.65，停止调参；最简 LLM 保持固定。</strong><p>原版 F1 {pct(baseline.f1)}；未采用的 F1 优先候选投影 {pct(best.f1)}，却将 {best.false_support}/{best.non_supported} 非支持事实放行为支持。未采用的保守候选投影 {pct(safe.f1)}，误支持为 {safe.false_support}/{safe.non_supported}。扫描只作敏感性分析，不再追加候选审核。</p><p className="ee-muted">{baseline.cases} 个开发案例 / {baseline.gold_facts} 条 gold。保留起始配置是范围控制决定，不宣称 0.65 最优。候选历史未审核状态保留；后续优化聚焦第三套 LLM 系统。</p></div>
      </DataComponent>
      <SortableRegion id="ee-overview-layout" variant="canvas" columns={12} spacing="standard" rows={[{ id: "ee-overview-row", items: ["ee-comparison-chart"] }]}>
        <SortableItem id="ee-comparison-chart" label="方法对照" span={12} kind="chart">
          <EvidenceChart id="ee-comparison-chart" queryId="comparisons" title="F1 与误支持率" rows={plottedComparisons} sourceRows={comparisons} height={260} description="F1 用百分数显示，与误支持率共用 0–100% 刻度。F1 越高越好，误支持率越低越好，不能相加。候选为标签投影。"
            spec={{ type: "horizontalBar", x: "label", y: "f1Rate", fields: ["f1Rate", "falseSupportRate"], stackable: false, startAtZero: true, showLegend: true, valueDecimals: 1, legend: { labels: { f1Rate: "事实 + 标签 F1", falseSupportRate: "误支持率 · 越低越好" } }, colors: { f1Rate: "var(--chart-1)", falseSupportRate: "var(--negative)" } }} />
        </SortableItem>
      </SortableRegion>
      <DataComponent id="ee-comparison-table" queryId="comparisons" title="审核状态与完整分母" kind="table" displayRows={comparisons} sourceRows={comparisons}><DataTable rows={comparisons} columns={comparisonColumns} searchable={false} label="基线对照" /></DataComponent>
    </Section>
    <Section id="ee-threshold-heading" title="阈值取舍 · 22 个真实离线配置">
      <Section columns={2} spacing="none">
        <EvidenceChart id="ee-threshold-f1" queryId="thresholds" title="阈值与标签 F1 投影" rows={thresholds} sourceRows={thresholds} height={245} spec={{ type: "scatter", x: "threshold", y: "f1", xLabel: "阈值", yLabel: "F1 投影", valueDecimals: 3, colors: { f1: "var(--chart-1)" }, stackable: false }} />
        <EvidenceChart id="ee-threshold-risk" queryId="thresholds" title="阈值与误支持率投影" rows={thresholds} sourceRows={thresholds} height={245} spec={{ type: "scatter", x: "threshold", y: "false_support_rate", xLabel: "阈值", yLabel: "误支持率", valueDecimals: 3, colors: { false_support_rate: "var(--negative)" }, stackable: false }} />
      </Section>
    </Section>
    <Section id="ee-inspect-heading" title="错误定位与证据核对" filters={<Dropdown label="核查方法" showLabel value={method} choices={Object.keys(methods)} choiceLabels={methods} onChange={choose} />}>
      <DataComponent id="ee-confusion" queryId="units" title="Gold × 预测标签" kind="custom" sourceRows={methodUnits} displayRows={methodUnits} description="行是 Gold，列是预测，按事实单元计数。候选为标签投影。点击格子筛选下方清单。清单筛选不改变此矩阵。">
        <div className="ee-matrix-wrap" data-reviewed-rows><div><p className="ee-muted">{methods[method]} · 全部 {methodUnits.length} 个事实单元 · {method.includes("candidate") ? "标签投影" : "所有者已审"}</p><table className="ee-matrix"><caption>行是 Gold，列是预测；点击格子筛选清单</caption><thead><tr><th>Gold ↓ / 预测 →</th>{verdicts.map(v => <th key={v}>{short[v]}</th>)}</tr></thead><tbody>{verdicts.map(g => <tr key={g}><th scope="row">{short[g]}</th>{verdicts.map(p => { const n = methodUnits.filter(u => u.gold_verdict === g && u.predicted_verdict === p).length; return <td key={p}><button className={`${g === p ? "ee-diagonal" : n ? "ee-offdiagonal" : ""} ${matrix?.[0] === g && matrix?.[1] === p ? "ee-selected" : ""}`} aria-label={`${g} 预测为 ${p}: ${n} 条`} onClick={() => { setMatrix([g, p]); setKind("all"); setCategory("all"); }}>{n}</button></td>; })}</tr>)}</tbody></table></div><div className="ee-matrix-note"><strong>标签对，不代表证据充分</strong><p>dev-07 的词法标签正确，但引用缺少必要前提。dev-08 降阈值后同样如此。继续用下方“证据不充分”和“待人工复核”检查。</p><p>复合预测拆分后继承相同引用。不同问题类型可能重叠，不能相加作为独立错误总数。</p></div></div>
      </DataComponent>
      <SectionHeader id="ee-queue-heading" title={`事实清单 · ${rows.length} 条`} filters={<><Dropdown label="问题" showLabel value={kind} choices={Object.keys(kinds)} choiceLabels={kinds} onChange={setKind} /><Dropdown label="案例类型" showLabel value={category} choices={Object.keys(categories)} choiceLabels={categories} onChange={setCategory} /><button className="ee-reset" onClick={reset}>清除筛选</button></>} />
      {matrix && <p className="ee-muted">矩阵筛选：{matrix[0]} → {matrix[1]} <button className="ee-reset" onClick={() => setMatrix(null)}>取消矩阵筛选</button></p>}
      <DataComponent id="ee-queue" queryId="units" title="可核查的问题记录" kind="table" sourceRows={rows} displayRows={rows}>{rows.length ? <DataTable rows={rows} columns={unitColumns} rowKey="id" selectedRowKey={active?.id} onRowSelect={r => setSelected(r.id)} rowActionLabel={r => `查看 ${r.case_id} ${r.gold_id} 完整证据`} searchable={false} label="错误事实清单" /> : <p className="ee-empty">当前筛选没有记录。这不表示其他方法或其他类别没有错误。</p>}</DataComponent>
      <DataComponent id="ee-detail" queryId="units" title="完整案例与引文" kind="custom" sourceRows={active ? [active] : []} displayRows={active ? [active] : []}><Detail row={active} /></DataComponent>
    </Section>
  </article>;
}
