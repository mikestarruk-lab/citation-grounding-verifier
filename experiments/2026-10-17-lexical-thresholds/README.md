# Development-only lexical threshold sensitivity

**Current disposition, 2026-10-18:** the owner retained the reviewed starting
threshold 0.65, stopped further lexical tuning and waived additional review of
unadopted candidates. This study is sensitivity analysis only. The original
records and pending review states remain intact. The F1-first nomination below
describes the historical experiment, not the selected baseline. See the
[baseline decision](../baseline-freeze-2026-10-18.json).

This study varies only the TF-IDF acceptance threshold. Sentence extraction,
negation logic, source selection, prompts and gold data are unchanged. It makes
no model calls and never reads the test cases. The service default remains 0.65.

## Method and provenance

The original run is `../2026-10-16-dev-v2/lexical-dev-v2.json`, with owner
alignments from `../../reviews/dev-v2/dev-v2-A-approved.json`. Both content
digests and the current development dataset hash are recorded in `study.json`.
The original run and all approved packets were validated with the existing
scorer before projection. Re-running threshold 0.65 reproduced every original
output hash exactly.

We evaluated 22 thresholds: all distinct maximum-similarity boundaries, the
endpoints 0 and 1, interior midpoints and the original 0.65. Thus every distinct
decision region is represented, including equality at a boundary. Near-identical
values close to 1 are retained to expose floating-point behavior rather than
silently round it away. Threshold-independent negation decisions still apply.

For each new run, claim text and order must exactly match the reviewed original.
Only then are the owner's semantic alignment and compound split reused for an
**exploratory label projection**. No new evidence judgment is inferred. This is
not new human approval or a complete reviewed quality score.

## Results and tradeoff

All runs succeeded on 8/8 development cases. Projected coverage is 12/12.
The candidate has 9/9 legal citations, but legality does not establish sufficiency.

| Configuration | Fact + label F1 | TP / FP / FN | False support | S to U rejection | Review status |
|---|---:|---:|---:|---:|---|
| Original 0.65 | 0.583333 | 7 / 5 / 5 | 0/4 | 3/8 | Owner reviewed |
| Best F1 region: 0.26600227007264704 | 0.833333 | 10 / 2 / 2 | 2/4 | 0/8 | Projected; changed outputs pending |
| Lower-risk region: 0.5967592242416415 | 0.666667 | 8 / 4 / 4 | 0/4 | 2/8 | Projected; not selected |

The highest projected F1 holds for
`0.1749613917148542 < threshold <= 0.3570431484304399`.
The nominated threshold is the midpoint of this region, avoiding an equality
boundary. Its many decimal places describe this development experiment; they
do not imply generalization precision. Ranking follows the plan: F1, then false
support. Evidence and runtime do not resolve any remaining output-equivalent tie.
At study creation, final selection was pending review. The subsequent owner
decision retains 0.65 instead; neither a default change nor a service reliability
improvement is claimed.

The lower-risk region has
`0.5769463580615581 < threshold <= 0.616572090421725`.
It is shown to make the cost of the planned F1-first criterion explicit, not to
silently replace that criterion after seeing results.

Five predictions change in the best-F1 candidate:

| Case / prediction index | Previous -> candidate | Gold | What the output shows |
|---|---|---|---|
| dev-01 / 0 | U -> S | S | Hourly and every hour refer to the same schedule. |
| dev-01 / 1 | U -> S | S | Retention paraphrase; attribution is resolved within the paragraph. |
| dev-03 / 0 | U -> S | C | Five workers is accepted using a quote that says at most four. |
| dev-04 / 0 | U -> S | C | Persists is accepted using a quote that says does not persist. |
| dev-08 / 0 | U -> S | S | Label becomes correct, but the citation still omits the Maple-to-West premise. |

This is a limitation of similarity as entailment. Lowering the threshold recovers
paraphrases, but cannot repair numeric comparison, morphology-sensitive negation,
compound extraction or evidence spanning multiple passages. The current minimal
LLM's reviewed development F1 is 1.0 on the same eight cases; this small result
does not demonstrate an optimization gain or replace final evaluation.

## Review and reproduction

- `study.json`: thresholds, projected counts, provenance and exact changed predictions.
- `threshold-*.json`: real offline runs, including source/version/configuration metadata.
- `threshold-*.summary.json`: automatic metrics; semantic review remains pending.
- `candidate-review.md`: full fields for the four changed case outputs.
- `candidate-reviews.json`: four exact-hash approvals reused verbatim and four
  pending packets. Unchanged semantic alignment is prefilled in pending packets;
  evidence judgments and reviewer remain unset.
- `candidate.summary.json`: the normal scorer correctly reports
  `pending_human_review` and emits no complete F1 or evidence-sufficiency score.

If these unadopted outputs are revisited in a future experiment, review all units
in each changed packet before approving it. That review is no longer required
for the current baseline. The complete fields and original approvals are preserved.
No claim of blind or independent review is made.

From the repository root, reproduce into a new directory (existing evidence is
never overwritten):

```sh
uv run python -m grounding_verifier.threshold_study --run experiments/2026-10-16-dev-v2/lexical-dev-v2.json --reviews reviews/dev-v2/dev-v2-A-approved.json --out runs/lexical-threshold-reproduction
uv run python -m grounding_verifier.cli score --run experiments/2026-10-17-lexical-thresholds/threshold-03.json --reviews experiments/2026-10-17-lexical-thresholds/candidate-reviews.json
```

Fresh timestamps and measured local latency will differ; outputs, thresholds and
label projections should match while inputs and source are unchanged. Do not
interpret these sub-millisecond lexical measurements as a controlled latency
comparison. The test split remains unfrozen and was not run. Artifacts are local
until separately committed and pushed.
