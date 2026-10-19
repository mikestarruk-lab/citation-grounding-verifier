# Gold 严格复审 — 2026-10-17

## 结论与范围

当前 gold 可用作小型合成规格基准，但本次不建议直接宣布“严格审查全部通过”或冻结 test。发现一处确定的标注解释逻辑错误、一处可复现的审批门禁缺陷，以及一个较低优先级的标注字段校验缺口。没有找到足够依据要求翻转现有 verdict；这不等于每条表述都没有歧义，也不构成独立人工认证。

本次逐条读取当前工作区的 `data/dev.jsonl` 和 `data/test.jsonl`：28 个案例、44 条 gold；核对来源、答案覆盖、原子性、限定词、S/C/U 判定、引文及两种解释。另检查 assignment、manifest、审批记录、生成审阅页和相关校验代码。审查基于未提交工作区（HEAD `894666f`），不是仅审 HEAD，也不是延用 10 月 15 日审查结论。没有修改 canonical 数据、审批状态、模型方法或既有分数，没有运行付费模型或最终测试基准。

文件级 SHA-256 和规范化哈希见同目录 `gold-strict-audit-2026-10-17.checks.json`。dev 规范化哈希为 `e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c`；test 为 `68d7f4554a71fa9944185a4808782af33887b4125265a72fbc006b3a76c426fa`。

## 确认发现

### F1 — 中：test-18 的 reasoning 把充分条件写成必要条件

位置：`data/test.jsonl:18`，test-18/g1。置信度：高。影响 1/44 条事实的解释，未发现因此必须改变标签。

原文是 `Engine Ember encrypts writes when secure mode is enabled.`，只建立 secure-mode-on → encryption。现有解释却说 `Ember's write encryption requires enabled secure mode`，将其增强为 encryption → secure-mode-on，并称之为 `necessary premise`。源文没有说“只有开启才加密”，也没有排除其他加密条件。

正确结论仍为 U：Finch 使用 Ember 已知，但使现有条件规则可被应用的 secure-mode-on 前提未获证实，其他证明加密的证据也没有；同样没有反证。缺少一条充分推导路径的前提，不等于该前提是现实中结果发生的必要条件。annotation_reason 关于“不证明加密，也不证明未加密”的说法可保留。

建议将 reasoning 改为：

> Finch uses Ember. The source guarantees encrypted writes when secure mode is enabled, but does not establish that this condition holds for Finch or otherwise establish encryption. It also does not refute encryption, so the claim is unsupported.

这是确定的解释修复，不建议把 verdict 改为 CONTRADICTED，也不建议把源文改成 only if 来迎合现有解释。即使只修改 reasoning，规范化 test 哈希也会改变，须同步生成审阅页，并在最终批准时绑定新哈希。

### F2 — 中：测试集冻结门禁会接受 draft/rejected 和错误类型

位置：`src/grounding_verifier/dataset.py:86`，尤其 89–92 行。置信度：高。影响未来 test 放行，不是已发生的测试泄漏。

当前只要求 reviewed_by 和 frozen 为 truthy，以及哈希相等；没有检查 review_status，也没有严格检查类型。使用临时目录中的独立 manifest、当前 test 对象调用真实 require_frozen_test 得到：

| 合成 manifest 条件 | 实际结果 | 应有结果 |
|---|---|---|
| 当前真实 draft 状态的副本 | REJECTED | REJECTED |
| draft + 非空 reviewer + frozen=true + 正确哈希 | ACCEPTED | REJECTED |
| rejected + 非空 reviewer + frozen=true + 正确哈希 | ACCEPTED | REJECTED |
| approved + 非空 reviewer + frozen="false" + 正确哈希 | ACCEPTED | REJECTED |
| approved + 空白 reviewer + frozen=true + 正确哈希 | ACCEPTED | REJECTED |

因此在人工编辑 manifest 留下旧 reviewer/frozen 字段、或把布尔值误写为字符串时，未批准的数据可能进入 test 执行。现有真实 manifest 是 draft/frozen=false，确实被拒绝；没有证据表明现有实验经过该缺口放行。

最小修复：显式要求 review_status == "approved"、frozen is True、reviewed_by 为 strip 后非空字符串、哈希匹配；增加上述拒绝路径和一个合法批准路径的回归测试。结构化 manifest 模型也可实现这些约束，无需建立大型审批系统。方法冻结目前另属流程约束，不应把该数据门禁描述成已经自动验证方法冻结。

### F3 — 低：annotation_reason 可以为空白而仍通过数据模型

位置：`src/grounding_verifier/dataset.py:20`。置信度：高。

GoldClaim 的 annotation_reason 是普通 str，没有与 reasoning 一样的非空白验证。在 dev-01 的内存副本中将 annotation_reason 设为三个空格，Case.model_validate 仍接受。当前真实数据 0/44 条为空，因此这是防回归缺口，不是现有标注缺失。

最小修复：为 annotation_reason 加非空白检查，并添加拒绝空串/空白的测试。不要将“非空”当成解释语义正确的自动证明；F1 仍需要语义审查。

## 歧义与风险，不冒充确定错标

### test-04/g1：first 的范围由标注者补足

答案写 high-priority messages first；gold 写 before normal-priority messages。原文确实支持相对 normal 的顺序，但没有显式定义全局只有两类优先级。现有 annotation_reason 已公开采用“相对 normal”的理解，所以 S 是合理自然语言判读，不能仅凭虚构其他优先级把它翻成 U。

严格评测的风险是标注者替答案缩窄了 first，另一位审阅者可能保留更宽范围而判 U。建议在 test 冻结前把答案明确写为 `BirchQueue processes high-priority messages before normal-priority messages and uses arrival order within a priority.`，或将当前约定固定到审阅规则；本次仅提出修订建议，没有改变答案。目标是提高审阅一致性，不是证明原标签错误。

### test-03/g2：状态语境被改写成启用动作

答案是 `With compact mode enabled ... leaves existing segments unchanged`，gold 是 `Enabling compact mode leaves ... unchanged`。普通规格语境下现有 S 合理；更忠实的 gold 是 `With compact mode enabled, IrisStore leaves existing segments unchanged.`，可避免 fixed-gold 诊断与端到端提取在“启用瞬间/启用期间”上采用不同表述。属于低优先级的一致性改进，不据此否定数据。

### dev-03/g2、test-19 的审阅边界

dev-03 的 Additional workers 在答案中承接错误的五个 active workers。无论将它解为超出五个的 worker，还是泛指额外 worker，源文对超出四个的 worker 排队规则仍支持排队方向；但对齐时不能自动把五改回四。本次保留 S，提醒审阅者保留答案中的实际阈值和指代。

test-19 的 Seven 与 either occupied or available 按普通资源规格理解为恰好七个及互斥状态，12−7=5 成立。没有依据引入“同一槽位既占用又可用”等设定来翻标签。若追求形式化无歧义，可在冻结前明确 exactly seven / exactly one state；这不是当前必须修复的错误。

## 数据完整性与评测能力

| 检查 | 结果 | 解释 |
|---|---|---|
| dev | 8 案例 / 12 facts；8 S、2 C、2 U | 四类别各 2 案例 |
| test | 20 案例 / 32 facts；19 S、7 C、6 U | 四类别各 5 案例，满足作业的案例数及类别要求 |
| 引用 | 44/44 引文对象合法；42/44 为整段引用 | 44 个引文对象不等于 44 个有引文事实；8 个 U 无引文，多段事实有多个引文 |
| 必填解释 | 44/44 reasoning、annotation_reason 有文本 | 非空不能替代 F1 的语义审查 |
| ID、source_group | 结构校验通过，split 间无重叠 | 不能仅凭不同 source_group 证明语义模板完全独立 |
| 输入重复 | 各 split 内规范化完整输入重复 0；跨 split 完全相同来源段 0 | 仅证明所定义的精确重复检查，没有宣称语义去重完毕 |
| 审阅副本 | gold-review --check 通过 | 与当前 JSONL 和 manifest 完整同步 |
| dev 批准 | 当前哈希与批准记录匹配 | owner review，未升级为独立盲审 |
| test 状态 | draft，未冻结，当前门禁拒绝 | 本次 AI 审查不构成人工批准 |

全体 44 个标签中 S 占 27/44=61.4%，C 占 9/44=20.5%，U 占 8/44=18.2%。题目要求的是案例类别均衡，不能把标签不等量误报为违反要求；报告仍应分标签展示性能。

主要测量边界：

- 每个案例合计来源仅 5–22 个英文词元（正则 `\b\w+\b`）；dev 中位数 11.5，test 中位数 13.5。21/28 案例只有一段，另外 7 个只有两段；人工全量检查未发现纯干扰段、相互冲突来源或长文检索情境。
- 8 条 gold 需要引用两段，其中 dev 2 条、test 6 条。多段类型还包含 test-18 的条件缺失负例；没有多引文并不使该负例无效。
- 42/44 引文是整段，且原段很短。这些引文均合法且通常充分，但该集难以区分“精准选择证据片段”与“复制整个短段”。不能为拉高难度强行截掉指代、阈值或多段前提。
- dev 的两条 multi_passage 都是 S；它不能单独检验模型对多段反证和缺前提的处理。test 覆盖了这些方向，但这不是允许根据 test 内容继续定向调优的理由。
- 空上下文、没有事实的回答、无 gold facts 的案例不在当前 gold 范围；Case 的 min_length=1 也阻止使用同一数据结构表达零事实案例。服务合同另要求处理这些边界，工程测试包含相关场景，但工程测试存在不代表本次端到端 gold 已测量了这些能力。
- 已有 8 个 dev 案例最简 LLM F1=1.0 的记录会带来区分度上限。它支持“在这组短规格上完成得好”，不支持一般场景准确率、稳定的优化增益或生产可靠性。没有随机抽样设计，不计算看似精确的总体置信区间。

这些是范围限制，不是给作业额外发明硬性案例配额。本次不扩展 test、不调阈值。若后续需要更强结论，应预先定义独立挑战范围和方法冻结方式，并报告其与原基准的关系；不能将本次已经读到的 test 当成未知数据。

## 全量逐条语义复核

S=SUPPORTED，C=CONTRADICTED，U=UNSUPPORTED。引用充分性结论针对当前 gold 引文，而非其他模型输出。U 不要求提供反证。以下为本次 AI 意见，不覆盖人工审批记录。

| Case/fact | 现有标签 | 本次证据核对及结论 |
|---|---|---|
| dev-01/g1 | S | hourly=every hour，频率保留，整段充分。 |
| dev-01/g2 | S | seven days 保留，It 指 ArchiveBox，保留。 |
| dev-02/g1 | S | GET + connection reset 的条件完全一致，保留。 |
| dev-02/g2 | S | never POST 明示；与 GET 独立，保留。 |
| dev-03/g1 | C | at most four 直接排除 five active，保留。 |
| dev-03/g2 | S | 额外 worker 排队有据；指代范围注意事项见上文，保留。 |
| dev-04/g1 | C | 相同 entries/restarts 下 persist 与 does not persist 相反，保留。 |
| dev-05/g1 | S | 本地文件 + each update 全部明示，保留。 |
| dev-05/g2 | U | 本地写入不能推出 AES-256，也未排除，保留。 |
| dev-06/g1 | U | connection reuse 不决定 Brotli，保留。 |
| dev-07/g1 | S | Juniper∈Q + 所有 Q 加密，双段齐全，保留。 |
| dev-08/g1 | S | worker→Maple→West，同一 host 连接，双段齐全，保留。 |
| test-01/g1 | S | including 8 MiB 支持恰好 8，保留。 |
| test-01/g2 | S | Larger 回指 8 MiB，完整阈值引文充分，保留。 |
| test-02/g1 | S | 15 分钟明确限定 inactivity，没有转成创建后的时长，保留。 |
| test-02/g2 | S | activity resets timer 直接明示，独立于超时间隔，保留。 |
| test-03/g1 | S | enabled + newly written 两个限定均保留，保留。 |
| test-03/g2 | S | existing unchanged 受 compact 语境限定；建议统一状态措辞，保留标签。 |
| test-04/g1 | S | high before normal 明示；first 的范围消歧见上文，保留现有约定下的 S。 |
| test-04/g2 | S | arrival order 仅在同一 priority 内，保留。 |
| test-05/g1 | S | HTTP 200 明示，已与 body 分开，保留。 |
| test-05/g3 | S | JSON body 明示，独立属性，保留。 |
| test-05/g2 | S | no authentication 明示，完整两句解析 endpoint，保留。 |
| test-06/g1 | C | exactly 30 后删除，反驳 exactly 31，保留。 |
| test-07/g1 | C | read-only 拒绝所有写入，不能借 read-write 条款支持，保留。 |
| test-08/g1 | C | 同一 project deletion 对 exported files 的否定被反转，保留。 |
| test-09/g1 | C | both 且 single insufficient 反驳 one 即确认，保留。 |
| test-10/g1 | C | default disabled 与 default enabled 相反，保留。 |
| test-10/g2 | S | operator can enable 独立明示，保留。 |
| test-11/g1 | S | titles indexing 明示；不需要将 source 的 body 事实加进答案，保留。 |
| test-11/g2 | U | indexed fields 不决定 B-tree 结构，保留。 |
| test-12/g1 | U | counter 未给 port 9090，不借外部惯例，保留。 |
| test-13/g1 | S | UTC storage 明示，保留。 |
| test-13/g2 | U | UTC 不推出 NTP，且无反证，保留。 |
| test-14/g1 | U | isolated container 不推出 Kubernetes，保留。 |
| test-15/g1 | S | export+import 包含 export；gold 不必覆盖未出现在答案中的 import，保留。 |
| test-15/g2 | U | commands 不提供 license，保留。 |
| test-16/g1 | S | Acorn→bronze→archived objects 90 days，限定与双段齐全，保留。 |
| test-17/g1 | S | Lina auditor + auditors view，完整双段，保留。 |
| test-17/g2 | C | Lina auditor + cannot delete，完整反证；不添加额外角色，保留。 |
| test-18/g1 | U | 无法确认 secure-mode-on，也无其他加密或不加密证据；保留 U，修复 F1。 |
| test-19/g1 | S | 总 12−占用 7=可用 5，普通互斥资源状态理解成立，保留。 |
| test-20/g1 | C | production exclusively Azure + Azure rejects V1，完整反证链，保留。 |
| test-20/g2 | S | 同一路由链 + accepts V2，完整支持链，保留。 |

未发现新的漏提事实、确定的 compound gold 未拆分，或无关/不足以支撑当前 S/C 的 gold 引文。test-05 现有三条 g1/g3/g2 的顺序是合法标识顺序，不要求重编号。

## 执行证据与最小后续

- `validate-data`：通过。
- `gold-review --check`：通过。
- `pytest tests/test_gold_remediation.py tests/test_evaluation.py -q -x --basetemp=.cache/gold-strict-audit-pytest-20261017`：16 passed，包含旧哈希拒绝、原子化计分、重复和遗漏惩罚、审阅页漂移检查。
- 本次审计脚本的 Ruff 检查通过；合成门禁及空白字段探针结果保存在 checks JSON 和执行过的 notebook。
- 扩大到全套 pytest 的尝试未完成：默认临时目录的首次运行出现 EEE 后停滞；指定工作区 basetemp 的运行完成 19 项后未继续；排除 HTTP 测试的尝试也未完成，均已中断。未取得完整错误栈，原因未定位；不能把这部分记成“全套通过”或确定的产品缺陷。相关 gold/evaluation 的 16 项通过是单独完成的结果。

优先修复 F1 与 F2，F3 可同批处理；在批准 test 前决定 test-04 的消歧措辞。若接受 test-03 的措辞统一，也应在同一版一次完成。修订后重新生成 review，校验新哈希并由真实 reviewer 审批 test；dev 数据无需因为 test 的解释修复而重写或失效。现有历史审查和模型实验保持原始哈希，不回填成新版结果。

复现：从仓库根目录运行 `.venv/Scripts/python.exe reviews/gold/gold-strict-audit-2026-10-17.py`，或打开同名 `.ipynb` 执行。脚本只读取 canonical 数据，在 `.cache` 的临时目录构造探针 manifest；不会批准 gold、修改测试集或调用模型。
