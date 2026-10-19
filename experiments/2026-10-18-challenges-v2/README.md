# Development challenge v2 migration

The owner accepted four clarification proposals. The v2 challenge data makes the
exclusion explanation explicit and removes success/commit ordering ambiguity.
Only challenge-05 changes its model input. This migration keeps all five existing
configurations fixed and does not add prompt variants or select a winner.

Five new serial calls completed successfully, with no output repairs. Both first
and final citations are verbatim and in bounds. Estimated new usage cost is
**$0.0023656**; cumulative local ledger estimate is **$0.0374301**, with no open
reservations against the $20 cap. These are configured-price estimates, not an
invoice audit. Each configuration has one first-client-call latency sample;
do not rank speed from this data or count reused latency as a new execution.

New challenge-05 outputs contain respectively 2 / 2 / 1 / 1 / 3 claims for
minimal, refined-v1, refined-v2, refined-v2-passage, and lean-v1-passage. Lean's
three outputs retain the three gold units in this sample. Refined-v2 variants
cover the content in one compound claim, while minimal/refined-v1 require careful
alignment of compound and potentially repeated transaction assertions. Atomicity,
semantic coverage, duplicate penalties, and evidence sufficiency remain separate.
These are AI observations, not complete human-reviewed quality scores.

## Review artifacts

- [AI-filled alignment draft](ai-alignment-2026-10-19.zh-CN.md) and matching JSON:
  all 25 records, 56 predictions and 64 proposed scoring units. Qualifiers,
  unmatched partial relations and local-reference uncertainties are explicit.
  The scorer continues to treat these AI-proposed records as pending.
- [Complete source and output review](output-review.zh-CN.md): all five cases,
  full source/answer/gold fields and all five configurations, with editable owner
  alignment/evidence fields. It includes an AI prereview of the five new outputs.
- `review-bundle.json`: 25 pending packets with source run, request, code, prompt,
  record and output digests. Twenty records were reused after exact request
  equality checks; five are new. This is a review bundle, not a fabricated new
  full-suite live run. Reused records retain original timestamps, usage and trace.
- `*-challenge05.json`: five new immutable one-case runs and their automatic
  summaries. Their dataset hash identifies the changed-input subset, rather than
  pretending to identify the full five-case dataset.
- [Revised gold](../../reviews/development-challenges-v1/clarified-gold-v2.zh-CN.md)
  and [decision provenance](../../reviews/development-challenges-v1/clarification-decision.json).
  The accepted scope is the clarification approach. Exact v2 wording and remaining
  gold have not been assigned blanket approval; the manifest remains draft.
- `PLAN.md`: stored before the new calls. Original v1 evidence is preserved.

No old human approvals were copied onto new gold/output bindings. No complete
semantic F1 is published, no default is changed, and no final test was run.
The original eight-case optimized runs and stability repeats remain in the first
cycle and still belong in final candidate assessment; this migration does not
replace them or erase earlier over-refusal and condition-loss failures.

## Reproduction

Read and review the saved artifacts offline without an API key. Inspect pending
fields and input identity before applying human decisions. Original data and
experiment paths are recorded in each packet, so preserve the repository layout.

For a genuinely new paid run, first choose a new output directory/version; the
scripts deliberately refuse to overwrite evidence or owner annotations:

```powershell
.venv\Scripts\python.exe experiments/2026-10-18-challenges-v2/rerun_changed_input.py
.venv\Scripts\python.exe experiments/2026-10-18-challenges-v2/build_review.py
```

Those commands created the already-saved artifacts and therefore now refuse
replacement. `--only` is available solely to resume an unexecuted configuration.
They are not zero-cost replay commands. No new paid run is needed to read/review
the existing results.
