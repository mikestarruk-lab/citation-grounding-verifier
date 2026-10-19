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

## End-to-end runs (pending owner review)

Extraction, labels and citations from the generated answers. Citation legality
is 100% for every method, enforced in code. The semantic F1 needs owner
alignment and evidence review; the packets are in `reviews/test-final/`
(`*-test-pending.json`, cases in shuffled order).

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
