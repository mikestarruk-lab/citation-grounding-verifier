# Final test runs

2026-10-19. Each frozen method ran once on the 20 frozen test cases (hash
`cbeb222a…`), as preregistered in [PLAN.md](PLAN.md) (`4cc58a9`). All 120
requests succeeded; no output repair was needed and no run was repeated.
Configured-rate cost for these runs is **$0.0190135**; the local ledger total is
**$0.1079909** of the $20 cap.

## Fixed-gold-fact diagnostic (automatic, final)

Each method classifies the 32 approved gold facts directly, so no alignment is
needed. This isolates verification from claim extraction.

| Method | Macro-F1 | S / C / U F1 | Misclassified | p50 / p95 s | Cost USD |
|---|---:|---|---|---|---:|
| lexical (0.65) | 0.368 | 0.625 / 0.000 / 0.480 | 9 S→U, 4 C→U, 3 C→S | <0.001 | 0 |
| minimal | 1.000 | 1.000 / 1.000 / 1.000 | none | 1.710 / 2.879 | 0.0044990 |
| optimized (lean-v1) | 1.000 | 1.000 / 1.000 / 1.000 | none | 2.292 / 4.085 | 0.0054125 |

Both LLM methods hit the ceiling: the short test cases cannot separate them on
verification alone. The lexical baseline never recognizes a contradiction and
calls 3 contradicted facts supported.

## End-to-end results (owner-reviewed, final)

The owner confirmed the AI-proposed rev2 alignment as written on 2026-10-19
(`reviews/test-final/*-test-approved.json`). Scores below come from the
standard scorer (`*-test.reviewed.summary.json`).

| Method | Fact + label F1 | Precision / recall | False support | False rejection | Evidence sufficiency | Atomicity |
|---|---:|---|---:|---:|---:|---:|
| lexical (0.65) | 0.400 | 0.394 / 0.406 | 3 | 12 | 3/10 (30%) | 61% |
| minimal | 0.970 | 0.941 / 1.000 | 0 | 0 | 22/28 (79%) | 100% |
| optimized (lean-v1) | **1.000** | 1.000 / 1.000 | 0 | 0 | **24/26 (92%)** | 100% |

Minimal's two false positives are source premises it restated as claims the
answer never made (test-16, test-20). Its evidence gaps are in multi-passage
cases where it quotes only one passage. Lean misses two premises (test-01
threshold, test-17 role). Evidence for five extra or mislabelled S/C units
was filled mechanically after the owner's confirmation because the scorer
requires it; see `approve.py`. Review followed AI feedback and is not
independent blind annotation.

## End-to-end run details

Extraction, labels and citations from the generated answers. Citation legality
is 100% for every method, enforced in code. The semantic F1 was reviewed as above; the original pending packets are kept in
`reviews/test-final/` (`*-test-pending.json`, cases in shuffled order).

| Method | Predictions (gold: 32) | p50 / p95 s | Cost USD |
|---|---:|---|---:|
| lexical | 23 | <0.001 | 0 |
| minimal | 34 | 1.748 / 2.292 | 0.0039965 |
| optimized (lean-v1) | 32 | 2.500 / 3.546 | 0.0051055 |

AI preview only, not a score: lean's 32 predictions are 27 exact gold texts
plus 5 plain paraphrases. Minimal's 34 include two source premises restated as
claims that the answer never made (test-16 bronze policy, test-20 routing),
which the scoring rules count as extra units. Lexical splits sentences instead of
facts and mislabels 6 of its 12 exact-text matches, including two false
supports (test-07, test-08).

Latency compares single runs on the same day; the optimized prompt is longer, so
it is slower and costs about 28% more per case than minimal.
