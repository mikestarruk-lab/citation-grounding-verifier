# Development baseline v2

Executed serially on 2026-10-16 against owner-approved development gold at
commit `d7f8c52c2a4a5d74fff5b5a59066ab0f41427bed`, with a clean working tree.
Canonical data hash:
`e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c`.
The test split was not run or frozen. This run changes no method, threshold or
prompt relative to the v1 baselines; it replaces evidence tied to draft gold.

## Recorded results

| Method / mode | Successful cases | Final valid citations | Fixed-fact macro-F1 | End-to-end F1 | Recorded cost USD |
|---|---:|---:|---:|---|---:|
| lexical / e2e | 8/8 | 4/4 | N/A | Pending human review | 0 |
| lexical / gold | 8/8 | 6/6 | 0.452381 | N/A | 0 |
| minimal / e2e | 8/8 | 12/12 | N/A | Pending human review | 0.0014240 |
| minimal / gold | 8/8 | 12/12 | 1.000000 | N/A | 0.0018918 |

Check exact counts and latency samples in the accompanying summary JSON files.
Fixed-fact diagnostics supply gold fact text and measure only verification;
they do not measure extraction or evidence sufficiency. Quote legality is a
deterministic substring/index check, not proof of entailment. The eight-case
sample does not establish statistical significance or broad robustness.

Minimal end-to-end p50/p95: 1.6783s / 3.5852s. Fixed-fact p50/p95:
2.2406s / 3.3497s. Both are live measurements; replay does not count as new latency.
The first client call is recorded separately in each summary. The model is
`claude-haiku-5-5`, adaptive thinking, medium effort, max output 8192; the lexical
threshold remains the uncalibrated starting value 0.65.

The 16 new model calls cost USD 0.0033158 based on returned token usage and
the configured price schedule. The shared ledger including v1 totals
USD 0.0067346, with no unsettled reservations. These are recorded cost estimates,
not a provider invoice. Do not reset the ledger when reproducing experiments.

## Human review and replay

Review [the A/B packet](../../reviews/dev-v2-output-review.md) before inspecting
the method-labelled files here. A/B hides names, but output style and accessible
experiment metadata can reveal the method; this is limited blinding. The
reviewer-only assignment map is kept in the ignored local cache. Neither A/B
JSON file contains a method name; all approvals and alignments remain pending.

Every record preserves the source/prompt/configuration, original outputs,
attempts, errors, token usage and hashes. Review templates bind data and output
hashes. The per-method files below can also be identified from matching output
hashes; do not edit run files or copy hashes into stale review records.

For example, reprint a fixed-fact diagnostic offline without an API key:

```sh
uv run python -m grounding_verifier.cli score --run experiments/2026-10-16-dev-v2/minimal-gold-dev-v2.json
```

End-to-end replay without approved reviews reports pending status. Once the
owner finishes alignment/evidence review, use the matching A/B JSON via
`score --run <run.json> --reviews <review.json>`. Incorrect pairings are rejected.
Missing review time is not estimated from artifact timestamps.
