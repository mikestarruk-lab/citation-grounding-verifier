# Gold audit remediation plan

Date: 2026-10-15. Internal delivery deadline: 2026-10-21, 18:00 Europe/London.

Status update: the three required repairs are implemented and pass offline
engineering checks; human gold approval is still pending. See
[implementation history](../docs/change-history.zh-CN.md) and the generated
[complete review](gold-dataset-review.md). The user deleted Canvas; the Markdown
generator and its CI drift check supersede the Canvas implementation proposed
below. Do not restore Canvas. The remaining text preserves the original plan.

Original planning status: planned, not implemented. This document records the response to
[the gold audit](gold-dataset-audit-2026-10-15.md). The audit's recorded SHA-256
values still match both JSONL files and the Canvas file as of this planning pass.
No data, scoring behavior, model prompts, approval status, or freeze status was
changed in this pass. No model calls were made.

## Decision and scope

Repair the gold annotations and their review workflow before collecting new
optimization evidence. The audit did not establish a verdict that must be
flipped. Keep the existing one-to-one matching rule and duplicate penalty;
make the gold consistently atomic instead of adding many-to-many matching.

Keep the 8 development and 20 test cases, their split membership, and their
source groups. Test labels remain unavailable to the verifier. Existing
whole-passage quotations are valid; choose shorter quotations only when their
subject, conditions, referents, and complete evidence chain remain clear.

## Ordered work and acceptance

### 1. Align atomicity and repair test-05 (F1; MIC-103 / MIC-104)

Document the operational rule: split independently testable assertions, while
retaining each assertion's subject and necessary qualifiers. A conjunction is
not automatically a split, and a multi-passage proof does not automatically
make its conclusion multiple claims.

Change test-05 to these three SUPPORTED claims:

| ID | Claim | Identity handling |
|---|---|---|
| g1 | GET /status returns HTTP 200. | Narrow the existing compound g1 |
| g3 | GET /status returns a JSON body. | Add the newly separated assertion |
| g2 | GET /status requires no authentication. | Preserve the existing g2 |

Gold IDs are identifiers, not ordinal positions; the stored order is g1, g3,
g2. Preserve the original answer and source passage. The first sentence is
sufficient for the status and body claims; the authentication evidence may
retain both sentences to resolve "This endpoint".

Review the remaining cases against the same atomicity rule, using the audit's
case notes. Keep test-04 and test-19 under the audit's ordinary specification
reading; do not add optional source/answer rewrites to this required repair.

Acceptance:

- The test split has 20 cases and 32 gold claims: 19 S / 7 C / 6 U. Together
  with development, there are 44 gold claims: 27 S / 9 C / 8 U, assuming no
  additional issue is found during review.
- A deliberately constructed, correct three-claim output for test-05 scores
  F1=1.0 against the corrected gold.
- A correct compound output can be split faithfully by the reviewer into
  three units, inherit its verdict/citations, score F1=1.0, and receive lower
  atomicity. Missing facts still produce FN; actual duplicate assertions
  still produce FP. These are regression fixtures, not model results.

### 2. Replace generic explanations (F2; MIC-103 / MIC-104)

Write a specific English `reasoning` and `annotation_reason` for each resulting
gold claim. Revise the original 43 annotations and author the new one: 44
annotations in total. Keep explanations concise; there is no word-count quota.

- SUPPORTED: name the evidence and the valid inference, including every link
  of a multi-passage proof.
- CONTRADICTED: identify the incompatible number, polarity, condition, or
  default under the same scope.
- UNSUPPORTED: identify the missing information or prerequisite and explain
  why it supplies neither support nor a direct refutation.
- `annotation_reason`: record the reason for this annotation decision, such
  as the retained qualifier or the distinction from a tempting wrong label.
  It must add useful audit context rather than repeat a verdict template.

Examples to preserve from the audit: test-06 compares exactly 30 with exactly
31 days; test-18 lacks the enabled secure-mode prerequisite; test-19 derives
12 - 7 = 5 using the two-state premise. Do not invent external product facts.

Acceptance: every explanation is reviewed against its own source and claim;
the three generic reasoning and annotation templates are gone. A text scan
can catch the known templates, but it cannot certify semantic sufficiency.
Existing S/C quotations remain exact substrings and U quotations remain empty.

### 3. Make the review artifact complete and reproducible (F3; MIC-105)

Treat JSONL and the manifest as the source of truth. Keep the existing Canvas
as a generated snapshot suitable for its host; do not introduce a frontend
application or require the browser to read local JSONL files.

- Add `reasoning` and `annotation_reason` to the generated claim data and show
  both in readable per-claim detail, alongside the existing verdict/citations.
- Generate the embedded cases and status metadata deterministically. Preserve
  the view's filtering behavior. Derive counts and status text from generated
  data instead of separate 8/20/draft constants.
- Provide a generator check mode that fails when the checked-in snapshot
  differs from JSONL/manifest. Compare all review-relevant fields, including
  both explanation fields and actual citation index/quote values.
- Carry the source dataset hashes in the snapshot and show its draft/review
  status. UI selection or filter state must never approve gold or freeze data.
- Run the consistency check in offline CI. Inspect rendering in the actual
  Canvas host if available; otherwise record that rendering remains unverified
  and provide a generated Markdown fallback with all review fields.

Acceptance: changing an explanation in JSONL causes check mode to fail until
regeneration; the regenerated snapshot matches all 28 cases and 44 claims.
The two explanations are visible in the review artifact, not just in TS types.

### 4. Validate, review, and replace development evidence (MIC-105 / MIC-106 / MIC-107)

1. Preserve the current audit, checks JSON, notebook outputs, and v1 run files
   as historical evidence. Add a separate post-repair validation result.
2. Run dataset validation, the scoring regression fixtures, snapshot drift
   checks, Ruff, and the relevant offline tests.
3. The human reviewer checks all corrected gold facts, labels, evidence, and
   explanations. Record corrections and actual reviewer identity; AI audit
   notes remain AI audit notes. Rejected cases return to annotation repair.
4. Once development gold is accepted, run new development versions of the
   lexical and minimal methods with unchanged model/prompt settings; include
   the fixed-claim diagnostics. Export fresh review packets and measure human
   review time. Do not combine old runs with new gold hashes.
5. Human approval of test gold permits recording its canonical dataset hash
   and freezing the manifest. It does not permit test-driven tuning: final
   test execution still waits for the method/configuration freeze in MIC-109.

The current canonical dataset hash includes explanations and annotations.
Consequently, even annotation-only edits invalidate the old hash-bound review
and scoring inputs. Keep this strict behavior for this project. Do not rewrite
hashes in old evidence or introduce a provenance migration framework for this
small repair. Freeze all intended annotation edits together to avoid repeated
invalidation. The v1 diagnostic macro-F1 values remain historical draft-gold
results, not updated baseline claims.

Acceptance: stale data/review combinations are rejected; new records contain
the new hashes and actual usage; semantic scores stay pending until their
human reviews are complete. Keep the shared $20 ledger and account for v1
spending when running new versions. No paid calls are needed for steps 1-3.

## Schedule, ownership, and scope control

| Window | Work | Ownership and existing Linear issues |
|---|---|---|
| Oct 15-16 | Atomicity, test-05, all explanations | Codex drafts; user reviews gold. MIC-103 / MIC-104 |
| Oct 16 | Regenerated review artifact, regression and drift checks | Codex implements; user verifies review usability. MIC-105 |
| Oct 16-17 | Human sign-off, new development baselines, failure analysis | User owns semantic review; Codex runs and records. MIC-106 / MIC-107 |
| Oct 18 onward | Optimization based on accepted development evidence | Existing MIC-108 through MIC-111 schedule remains |

Allow roughly 3-4 hours for this remediation and focused human review, using
the existing annotation/review allocation first. If it takes longer, reduce
extra optimization rounds before consuming the final-review/reproduction
buffer. Keep the Oct 19 method freeze and Oct 21 delivery target.

The audit's text-length and template-similarity observations are limitations,
not evidence of invalid existing labels or a mandate for a larger test set.
Record the short synthetic benchmark's scope in the README. Add targeted
development/engineering challenges for observed failure modes when useful;
keep unresolved source-conflict cases outside the unambiguous main score.
Do not expand the test set merely to satisfy invented coverage quotas.

## Exit condition

F1-F3 are resolved only when their acceptance evidence exists, the review
artifact matches the corrected data, and human gold approval is recorded.
Remediation completion does not by itself establish model improvement or
complete the final benchmark, report, or submission.
