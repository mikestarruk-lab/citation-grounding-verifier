# Owner-reviewed development v2 results

On 2026-10-17 the owner completed and revised the alignment workbook, then
confirmed it was saved and closed. The importer validated all 23 prediction rows,
their source fields and the 12 gold facts against the existing v2 records before
creating 16 approved review packets (24 scoring units). No new model calls were
made, and no predictions, gold facts, threshold or prompts were changed.

Source: [completed workbook](../../reviews/dev-v2/dev-v2-alignment.xlsx).
SHA-256: `fb637ff6013726e6ec5c1f11cd7c3dc7c6a893889336739a8843987e44745289`.
Reviewer: Michael (mikestarruk-lab). This was owner review after AI feedback,
not independent blind annotation. Actual review duration was not recorded.

## End-to-end comparison

| Metric | A: lexical, threshold 0.65 | B: minimal LLM |
|---|---:|---:|
| Successful requests | 8/8 | 8/8 |
| TP / FP / FN | 7 / 5 / 5 | 12 / 0 / 0 |
| Fact-and-label micro-F1 | 0.583333 | 1.000000 |
| Fact coverage | 12/12 | 12/12 |
| False support | 0/4 | 0/4 |
| False rejection (S to U) | 3/8 | 0/8 |
| Evidence sufficiency | 3/5 | 10/10 |
| Atomicity | 10/11 | 12/12 |
| Final citation legality | 4/4 | 12/12 |

The owner accepted short citations whose attribution can be resolved locally in
the indexed paragraph, but rejected missing independently necessary premises.
This is the interpretation of the submitted decisions. It does not authorize
adding unquoted substantive evidence when scoring another output.

A/dev-02 prediction 0 is split according to the explicit instruction in
`配对!L6`: GET maps to g1 with sufficient evidence; POST maps to g2 with
insufficient evidence. Both units inherit the original SUPPORTED verdict and
GET-only citation. `配对!J10` maps queued workers to g2, `K17` records sufficient
evidence, and `K21` rejects A's missing Juniper-in-Q premise. The workbook and
original pending packets are preserved without edits.

The lexical method covers all facts but mislabels five. Its compound prediction
and two evidence gaps illustrate why citation legality and zero false support
cannot alone establish reliable grounding. The minimal method has no observed
fact/label or evidence error under the owner's decisions on these eight short
development cases. This is not a final test result, an optimized-method result,
or evidence of statistical significance.

## Records and offline reproduction

- [A approved review](../../reviews/dev-v2/dev-v2-A-approved.json).
- [B approved review](../../reviews/dev-v2/dev-v2-B-approved.json).
- [Import receipt, input cells and provenance](../../reviews/dev-v2/dev-v2-human-review-import-2026-10-17.json).
- `lexical-dev-v2.reviewed.summary.json` and
  `minimal-dev-v2.reviewed.summary.json` contain the replayed complete metrics.

```sh
uv run python -m grounding_verifier.cli score --run experiments/2026-10-16-dev-v2/lexical-dev-v2.json --reviews reviews/dev-v2/dev-v2-A-approved.json
uv run python -m grounding_verifier.cli score --run experiments/2026-10-16-dev-v2/minimal-dev-v2.json --reviews reviews/dev-v2/dev-v2-B-approved.json
```

Run/summary files without `.reviewed` remain the original pre-review snapshots.
Fixed-gold-fact macro-F1 remains a separate diagnostic and is not substituted for
the end-to-end micro-F1 above. Recorded live latency/cost are unchanged by replay.
The test split remains draft and unfrozen. Lexical threshold selection,
optimization comparisons, method freeze and final three-method evaluation are
still separate tasks.
