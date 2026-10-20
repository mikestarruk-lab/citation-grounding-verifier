# Reviews

Human review records. Generated gold text and the development approval stay at
this directory root because code, `data/manifest.json`, and the v2 experiment
files store those exact paths.

## Status (2026-10-19)

All review work for the delivery is complete. Approval records, newest first:

| Record | Scope |
|---|---|
| [test-final/](test-final/) `*-test-approved.json` | Owner-confirmed end-to-end alignment of the three final test runs |
| [test-gold-approval-2026-10-19.md](test-gold-approval-2026-10-19.md) | Test gold, 20 cases / 32 facts, approved and frozen |
| [development-challenges-v1/challenge-gold-v2-approval-2026-10-19.md](development-challenges-v1/challenge-gold-v2-approval-2026-10-19.md) | Challenge gold v2, the rev2 alignment and its scoring rule |
| [dev-v2/dev-v2-human-review-import-2026-10-17.json](dev-v2/dev-v2-human-review-import-2026-10-17.json) | Owner review of the dev v2 baseline outputs (workbook import) |
| [dev-gold-approval-2026-10-16.md](dev-gold-approval-2026-10-16.md) | Development gold, 8 cases / 12 facts |

Pending files (`*-pending.json`), AI drafts (`ai/`, `ai-alignment-*`) and the
threshold candidate packets are kept unchanged as history; none of them is an
approval. All reviews followed AI feedback and are not independent blind
annotation.

## Layout

| Folder | What it is |
|---|---|
| `dev-v2/` | Development v2 workbook, original packets and approved alignment |
| `dev-v2/ai/` | AI pre-review suggestions. They do not approve anything |
| `gold/` | 2026-10-15 audit, remediation plan and validation record; 2026-10-17 strict audit |
| `test-final/` | Final test review packets: pending, AI alignment and approved records |
| `development-challenges-v1/` | Challenge gold AI review, clarifications and the v2 approval |
| `archive/` | `dev-lexical-pending.json`, the pre-remediation review. Do not replay it |
| *(root)* | `gold-dataset-review.md` and the dev and test gold approvals |

During the original A/B review, experiment files were deferred until the
alignment sheet was complete to reduce method-name bias. That review is now done.
The audit notebook still contains its original output path and should not be
rerun as if that path were current.
