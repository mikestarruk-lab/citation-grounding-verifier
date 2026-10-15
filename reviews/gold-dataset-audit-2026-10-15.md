# Gold 数据集与审阅页面复核

复核日期：2026-10-15。范围：`data/dev.jsonl`、`data/test.jsonl`、`reviews/gold-dataset-review.canvas.tsx`。以 `assignment.md` 的合同为主要标准，参考当前校验与评分代码判断实际影响。没有修改这三个输入文件，没有调用模型，没有把本次 AI 审查登记为人工批准或冻结测试集。

结论：28 个案例的 43 个现有 gold verdict，按原文通常语义逐条复核，未发现必须直接翻转的标签。结构与引用校验通过，页面展示的全部数据与 JSONL 一致。主要缺陷是 `test-05` 的 claim 粒度和评分匹配规则不协调，以及全部 reasoning 缺少针对具体证据的解释。全文引用合法，不能仅因引用整段判错。当前数据适合做小规模、短文本的合成基准；修正标注解释和粒度后再进行人工确认、冻结更稳妥。

## 可重复检查及边界

执行记录和完整代码见 `gold-dataset-audit-2026-10-15.ipynb`，机器可读结果见 `gold-dataset-audit-2026-10-15.checks.json`。Notebook 内含实际输出，且可从项目根目录或 reviews 目录使用项目 Python 与本机 Node 重跑。代码只解析 Canvas 中的静态 CASES 数组，不执行组件、不访问网络。三个输入文件的 SHA-256 在检查前后一致。

| 检查 | 实际结果 | 解读 |
|---|---|---|
| 开发集 | 8 cases、12 gold claims；四个 category 各 2 条 | 符合当前拆分规则 |
| 测试集 | 20 cases、31 gold claims；四个 category 各 5 条 | 满足作业案例数和类型覆盖要求 |
| 标签分布 | dev：8 S / 2 C / 2 U；test：18 S / 7 C / 6 U | 案例类型均衡不等于 claim 标签均衡；作业没有要求三标签等量 |
| Schema、ID 与拆分 | Pydantic 校验通过，case ID 唯一、case 内 gold ID 唯一，dev/test ID 和 source_group 不交叉 | 这是结构与标识符检查，不能证明语义独立性 |
| 引用 | 43/43 索引合法且是非空逐字子串；43/43 等于对应 passage 全文 | 全文也是子串，合同允许；短引用也应允许 |
| 引用与 verdict 的数量关系 | 35 个 S/C claim 都有引用；8 个 U claim 都为 `[]` | 符合合同；43 是 citation 数，同时恰好也是 claim 总数，两者含义不同 |
| 页面与 JSONL | 28 cases、43 claims 的 split/category/passages/answer/claim ID/text/verdict/格式化 citations 全部一致 | 未发现当前静态副本的抄写或转义差异 |
| 精确重复 | 没有完整 context_passages 重复，也没有 generated_answer 精确重复 | 不能据此断言没有近似模板或同类推理重叠 |
| 原文长度 | 每个 passage 31–137 字符；21 cases 为 1 段，7 cases 为 2 段 | 测试结论仅覆盖短证据，不能外推为长文证据定位能力 |
| 人工审阅状态 | manifest 仍是 draft，test frozen=false | 与当前页面显示一致；AI 复核不等于独立人工验收 |

语义判断采用所给合成规格，不借用真实产品知识。逐字检查不证明 entailment；下文的语义结论来自本次逐条阅读。没有运行浏览器或验证 Canvas 组件在特定宿主中的渲染效果，因此不声称界面运行已验收。数据没有业务时间序列字段，时效或趋势检查不适用。

## 需要修正或补足的事项

### F1：test-05 把两个独立可检验事实合成一个 gold claim，影响细拆答案的评分

- 严重程度：中；问题与影响的置信度：高。位置：`data/test.jsonl:5`，`gold-dataset-review.canvas.tsx:300`；影响机制：`src/grounding_verifier/evaluation.py:183` 附近的 gold ID 单次匹配。
- 当前 g1 是 `GET /status returns HTTP 200 with a JSON body.`，同时包含状态码和响应体格式。二者可以分别成立或失败，应在本项目的 independently testable assertions 标准下拆开。
- 当前 g2 是无需认证，判定正确，应保留。建议该案例变为三个 SUPPORTED claim：`GET /status returns HTTP 200.`、`GET /status returns a JSON body.`、`GET /status requires no authentication.`。前两项可以引用原文第一句，第三项可引用整段以保留 `This endpoint` 的主体。
- 这不是现有 SUPPORTED 标签错，也不是源文支持不足，而是 gold 与项目声称的原子粒度不一致。
- 已用当前评分代码做隔离的构造复现：沿用原来的两个 gold，原粒度的完美输出得 F1=1.0；正确拆成三个输出，并宽松地将状态码和 JSON 两项都映射到 g1，第二次使用 g1 会算 FP，F1=0.8。该数字仅说明这一案例的粒度敏感性，不是实测模型成绩，也不是整个测试集下降 0.2。
- 最小修复：先统一此 gold 的粒度，再同步页面。如果保留较粗 gold，则需要明确允许多个预测合并匹配一个 gold 的审阅/计分规则；不能一边要求细拆，一边把细拆的第二项当额外事实。

### F2：43 条 reasoning 均由三种 verdict 模板填充，未记录具体的证据推理

- 严重程度：中；置信度：高。范围：两个 JSONL 的全部 43 claims。
- 26 条 S 都是 `The cited specification entails this assertion, including its conditions.`；9 条 C 都是 `The supplied specification directly rules out this assertion.`；8 条 U 都是 `The supplied specification does not establish this assertion.`。
- 这些句子通过非空字段校验，但只是复述结论。作业要求 brief explanation linking the cited evidence (or lack thereof) to the verdict；当前解释没有说清数字冲突、条件匹配、缺失信息或跨段推理链。`annotation_reason` 也只有三种通用模板，不能补足这些内容。
- 最小修复是为各 claim 写出实际理由，不必长。例如：test-06 明确写“源文是 exactly 30 days，答案是 exactly 31 days，两者不相容”；test-18 写“知道 Finch 使用 Ember，但不知道 secure mode 是否启用，因此不能推出加密，也不能推出不加密”；test-19 写“总数 12，已占 7，状态二分，因此可用为 12−7=5”。
- 此问题降低标注的可审计性，并不意味着 43 个 verdict 都错误。下方逐案记录给出了本次复核的具体理由，可作为后续修订依据。

### F3：审阅页不展示 reasoning 和 annotation_reason，审查内容不完整

- 严重程度：低；置信度：高。位置：`gold-dataset-review.canvas.tsx:23`、`:739`。
- 页面 GoldClaim 类型只保留 id、claim_text、verdict、字符串 citations，表格也只有这些列。当前页面与 JSONL 在其实际展示的字段上完全同步，但使用页面的人看不到 F2 所述的解释质量问题。
- 作业没有规定这个辅助页面的列，所以这是审阅流程的缺口，不是 API 合同违反。
- 最小修复：加入 reasoning，并提供 annotation_reason 的可读展示。若仍维护静态 CASES，应在修改数据时重新生成或运行一致性检查。页面当前的 8/20/draft 文案为硬编码，此刻正确，后续可能过期；本次没有发现已经过期。

## 需要说明，但不应判为缺陷的事项

### 全段引用合法；精简是按语义选择，不是统一删到一句

`assignment.md:86` 要求 exact verbatim substring，没有“必须全文”或“必须最短”的规则。现有全部引用都合法，且人工逐案检查没有发现现有证据无法支撑其 S/C verdict。

- dev-02/g1 可以只引 `RelayGate retries GET requests after a connection reset.`，因为主体与重试条件都完整。
- dev-02/g2 的 `It never retries POST requests.` 依赖上一句给出的主体，保留两句有合理价值；不能机械地把两句引用都判为冗余。
- test-01/g2 的 `Larger files are rejected.` 依赖上一句给出的 8 MiB 阈值，完整两句可以避免条件不清。
- test-03/g2 的 `Existing segments are unchanged.` 与上一句的 compact mode 条件有关；test-05 认证句中的 `This endpoint` 也需要指代上下文。
- test-16、17、19、20 的推导需要两段。截短时必须保留连接主体、规则和必要前提。test-19 的状态二分句尤其不能为了变短而删掉。

因此，建议采用“相关且充分、保留必要条件和指代”的引用方式。没有依据给当前 43 条引文统一判错，也没有依据强制全部截成单句。当前评分代码没有要求预测引文逐字等于 gold 引文，合法的不同长度引文仍应按证据充分性判断。

### test-04 的 first 有轻微范围歧义，适合消歧，不宜直接翻 verdict

原文说高优先级在普通优先级之前；答案说 high-priority messages first；gold 恢复为 before normal-priority messages。在此短规格语境下，把 first 理解为相对普通消息的先后是合理的，保留 S/S 有根据。但 first 字面上比原文少了比较对象，若以后引入其他优先级会变得不清楚。可将 generated_answer 的第一部分直接写为 `BirchQueue processes high-priority messages before normal-priority messages`。这属于低严重度的措辞改进，不能声称已有一个确定的错误标签。

### test-19 的算术结论可以保留

在通常规格语言中，`Seven slots are occupied` 给出已占用数量，`either occupied or available` 给出状态二分；因此 12−7=5，SUPPORTED 合理。若追求形式化无歧义，可以写 `Exactly seven slots are occupied. Each slot is in exactly one of two states: occupied or available.`。这是可选消歧，不应为推翻正确的常规理解而虚构“槽位同时占用和可用”的产品行为。

### 覆盖基本达标，但不能把该集当成全面的鲁棒性证明

案例类型均衡，包含数量偏差、条件对调、否定反转、外在信息和跨段推理，满足作业列出的核心覆盖。使用合成技术规格也是作业允许的。test-18 虽不能成功推出事实，仍是有价值的跨段缺条件负例，不需要为了类别整齐将其强改为 SUPPORTED。

观察到的范围限制是文本短、实体与关系简单、没有干扰段或相互冲突的证据。若后续需要比较长文证据定位、复杂条件或冲突处理，可以另加相应挑战案例；这些不是当前作业暗含的硬性配额，也不应为了凑覆盖临时改动已冻结的测试集。目前测试集未冻结。

## 逐案语义记录

S=SUPPORTED，C=CONTRADICTED，U=UNSUPPORTED。表中结论是本次 AI 复核意见，不是人工签字状态。除明确标记的粒度问题外，保持现有 gold。

| 案例 | 当前 verdict | 本次复核理由与处理 |
|---|---|---|
| dev-01 | g1 S / g2 S | every hour 与 hourly 同义；保留七天有明确原文。两事实均覆盖，标签与引用充分。g2 整段引用保留 Snapshots 的对象。 |
| dev-02 | g1 S / g2 S | GET 重试保留 connection reset 条件；never POST 有明确否定。but 两侧已正确拆开。g1 可缩引，g2 保留前句主体合理。 |
| dev-03 | g1 C / g2 S | at most four 排除五个 active workers；额外 worker 排队明确成立。答案没有 active 修饰第二项，但回指额外 worker 合理。 |
| dev-04 | g1 C | 原文 does not persist，答案 persists；相同对象和跨重启条件下直接矛盾。 |
| dev-05 | g1 S / g2 U | 每次更新后写本地文件有据；写本地文件不推出 AES-256，也不反驳 AES-256。正确判为缺证据。 |
| dev-06 | g1 U | 连接复用既不推出也不否定 Brotli 压缩，U 与空引用正确。 |
| dev-07 | g1 S | Juniper 属于 Q，所有 Q 服务加密，因此 Juniper 加密。两段都是必要证据，不能只引规则或只引模式。 |
| dev-08 | g1 S | worker 在 Maple，Maple 在 West，合成为 worker 在 West。两个定位前提都已引用。 |
| test-01 | g1 S / g2 S | up to and including 明确保留 8 MiB 边界；Larger 被拒绝对应 >8 MiB。两个事实完整。g2 整段保留阈值合理。 |
| test-02 | g1 S / g2 S | 15 分钟是无活动时长，gold 没丢 inactive 条件；活动重置 inactivity timer 有直接证据。 |
| test-03 | g1 S / g2 S | 新 segment 的压缩保留 compact mode 条件；旧 segment 不变在该操作语境下合理。Enabling 是对此条件的自然转写，不构成独立的时间点预测。 |
| test-04 | g1 S / g2 S | 高优先级相对普通优先级先处理；同一优先级按到达顺序。通常语境下两项可保留；first 的比较范围可更明确，见前文。 |
| test-05 | g1 S / g2 S | 所有现有事实都获支持；但 g1 同时包含 HTTP 200 与 JSON body，应细分为两项，再加无认证共三项。不是 verdict 翻转。 |
| test-06 | g1 C | exactly 30 days 与 exactly 31 days 直接冲突。源文删除动作保证这不是“至少 30 天”的宽泛下界。 |
| test-07 | g1 C | 原文只读模式拒绝所有写入，答案说只读接受写入。不能拿另一种 read-write 模式的允许来支持它。 |
| test-08 | g1 C | 对同一删除项目操作，原文不删除 exported files，答案说删除，直接反转否定。 |
| test-09 | g1 C | 源文明确 both replicas 且单副本 insufficient，排除一个副本一确认就 ACK。两个条件句共同提供清晰反证。 |
| test-10 | g1 C / g2 S | 默认 disabled 与默认 enables 相反；operators can enable 则逐字有据。默认状态和可操作性已正确分开。 |
| test-11 | g1 S / g2 U | 索引标题有直接依据；是否使用 B-tree 无依据。Body 不索引是源文补充，未在答案中提出，不需要额外制造一个 gold。 |
| test-12 | g1 U | completed-jobs counter 未说明端口或 metrics endpoint 的端口，9090 缺证据；不能凭常见端口惯例补证据。 |
| test-13 | g1 S / g2 U | UTC 存储明确成立；UTC 格式不能推出 NTP 校时。两项已正确拆分。 |
| test-14 | g1 U | 启动 isolated container 不决定是否使用 Kubernetes 调度。答案没有声称隔离性，无需把源文额外事实加入 gold。 |
| test-15 | g1 S / g2 U | 源文包括 export 和 import，足以支持答案只说 export；Apache 2.0 未提及。不能因源文另有 import 就判答案不完整或造额外 gold。 |
| test-16 | g1 S | Acorn 使用 bronze，bronze 归档对象保留 90 天；主体、对象范围和期限完整，两个前提都已引用。 |
| test-17 | g1 S / g2 C | Lina 是 auditor，auditors 可以 view、不能 delete。按给定普遍规则直接继承权限。不得引入源文未出现的管理员覆盖等外部假设改标签。 |
| test-18 | g1 U | Finch 使用 Ember，但其配置未知；规则要求 secure mode 开启，缺失此前提，因此既不能证实也不能直接反驳加密。U/[] 正确。 |
| test-19 | g1 S | 总数 12、占用 7、状态二分，推出可用 5。两个段落充分且必要；保留常规规格解释，形式化措辞可选。 |
| test-20 | g1 C / g2 S | production 流量仅至 Azure，Azure 拒 V1、收 V2，分别导出 production 的拒/收。给定两段构成完整路径，不添加其他网关、版本或路由例外。 |

## 后续处理建议

先修正 test-05 的 gold 粒度，并为各 claim 补具体 reasoning；如更新注释理由，也应记录该例实际的证据链。随后同步页面，并把解释字段纳入审阅。全文引用按个案精简即可，不作批量机械截断。完成后重跑结构与副本一致性检查，再由人工决定是否批准、冻结测试集；此次审查没有代替该决定，也没有修改 manifest。
