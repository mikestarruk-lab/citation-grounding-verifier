# Final test runs: preregistered plan

Decision date: 2026-10-19, Europe/London. Committed before any test call.

## Preconditions (all met)

- Test gold approved and frozen: hash
  `cbeb222ac9160b048f90d9a12f42286a9ef0b6e514bfc1b67bfd0e1dc806712a`
  ([approval](../../reviews/test-gold-approval-2026-10-19.md)); the CLI's
  freeze gate refuses any other test data.
- Comparators frozen: lexical threshold 0.65 and fixed minimal
  ([baseline freeze](../baseline-freeze-2026-10-18.json)).
- Optimized method frozen: lean-v1, span citations, one validated repair
  ([method freeze](../method-freeze-2026-10-19.json)).

## Runs

Each method runs **once** on all 20 test cases, serially, with the frozen
configuration:

| Method | Mode | Calls |
|---|---|---:|
| lexical | end-to-end | 0 (local) |
| minimal | end-to-end | 20 |
| optimized (lean-v1) | end-to-end | 20 (+ repairs if needed) |
| lexical, minimal, optimized | fixed-gold-fact diagnostic (`--mode gold`) | 0 + 20 + 20 |

End-to-end runs are the primary result; fixed-gold diagnostics isolate
verification from claim extraction and are reported separately. Expected cost
is under $0.05 against the shared $20 ledger.

## Rules

- No rerun to obtain a better result. A request that fails is recorded as a
  failure and scored as such; a run is repeated only if it could not complete
  for an infrastructure reason unrelated to the method (for example the process
  was interrupted), and that is disclosed.
- No prompt, threshold, configuration, data or gold change after seeing test
  outputs.
- End-to-end semantic scores need owner review of alignment and evidence. The
  runs produce pending review packets; any AI pre-alignment is labelled as such
  and never substitutes for that review.
