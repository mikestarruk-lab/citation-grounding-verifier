# Reviews

Human review records. Generated gold text and the development approval stay at
this directory root because code, `data/manifest.json`, and the v2 experiment
files store those exact paths.

## Current task

An [AI-filled v2 alignment draft](../experiments/2026-10-18-challenges-v2/ai-alignment-2026-10-19.zh-CN.md)
now covers all 25 challenge outputs (56 original predictions / 64 scoring units).
It includes full source, gold and outputs, proposed alignment/evidence decisions,
and owner fields. Transaction-reference ambiguities are explicitly flagged.
All records remain AI-proposed; no human approval or complete semantic score is implied.

The changed challenge-05 input has now been rerun under the five fixed
configurations. Use the [v2 complete output review](../experiments/2026-10-18-challenges-v2/output-review.zh-CN.md)
for the five challenge cases: five new records and twenty explicitly checked
reused records. New gold and model-output approvals remain pending; v1 packets
are historical, and the original eight-case optimized reviews remain separate.

The owner accepted the four clarification proposals. They are materialized in
[the complete v2 gold document](development-challenges-v1/clarified-gold-v2.zh-CN.md)
with a separate scope-bound decision record. Only challenge-05 changes model
inputs; prior model-output reviews remain pending. The exact new wording and
remaining gold have not been assigned blanket approval.

The new development challenges now have a [source-complete AI gold rereview and
owner checklist](development-challenges-v1/gold-ai-review.zh-CN.md). It contains
five cases / twelve facts and retains pending owner decisions. Eight facts are
recommended unchanged; four need explanation or scope clarification. This is an
AI rereview after prior output access, not a blind audit or gold approval.

The owner completed [dev-v2/dev-v2-alignment.xlsx](dev-v2/dev-v2-alignment.xlsx)
on 2026-10-17. The approved JSON records and cell-level import receipt are in
`dev-v2/`; [reviewed results](../experiments/2026-10-16-dev-v2/reviewed-results-2026-10-17.md)
can be replayed without an API key. The long
packet is [dev-v2/dev-v2-output-review.md](dev-v2/dev-v2-output-review.md).
`dev-v2/dev-v2-A-pending.json` and `dev-v2/dev-v2-B-pending.json` preserve their
original pending state; approved copies are separate files.

On 2026-10-18 the owner retained the reviewed lexical baseline at 0.65 and
stopped further lexical tuning. The [threshold candidate packets](../experiments/2026-10-17-lexical-thresholds/candidate-review.md)
are historical sensitivity evidence, not the next review task. Their pending
status is preserved; no additional candidate review is required. See the
[baseline decision](../experiments/baseline-freeze-2026-10-18.json).
Final test gold and final three-method output reviews remain separate work.

## Layout

| Folder | What it is |
|---|---|
| `dev-v2/` | Development v2 workbook, original packets and approved alignment |
| `dev-v2/ai/` | AI pre-review suggestions. They do not approve anything |
| `gold/` | 2026-10-15 audit, remediation plan, and validation record |
| `archive/` | `dev-lexical-pending.json`, the pre-remediation review. Do not replay it |
| *(root)* | `gold-dataset-review.md`, `dev-gold-approval-2026-10-16.md` |

During the original A/B review, experiment files were deferred until the
alignment sheet was complete to reduce method-name bias. That review is now done.
The audit notebook still contains its original output path and should not be
rerun as if that path were current.
