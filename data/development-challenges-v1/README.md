# Development challenges v1 (draft gold)

Five new synthetic cases / twelve proposed facts, authored before the first
comparison calls. This is a development diagnostic extension, not the final test,
an independent validation set, or a replacement for the approved eight dev cases.
No test source or observed test model output was used to tune these prompts.
The project had already inspected test gold in a separate audit; no blindness
claim is made.

- challenge-01: numeric scope and a missing retention fact.
- challenge-02: multi-hop refutation with explicit exclusive placement premises.
- challenge-03: retry-condition applicability and scope-preserving decomposition.
- challenge-04: embedded instructions as untrusted data, not factual evidence.
- challenge-05: supported compound actions and a transaction relation, with curly
  punctuation that quotations must preserve.

`manifest.json` deliberately stays draft/unreviewed. Gold content is an AI
proposal requiring owner review before complete quality scores. A passing schema
or exact citation check does not validate that proposal's meaning. Review the
exclusivity premises and independently testable transaction relation carefully.
Original `data/dev.jsonl`, its approval hash and baseline records are unchanged.

`boundaries.json` contains three engineering checks excluded from main benchmark
counts and F1: unresolved same-condition conflict, empty context and a non-factual
answer. Conflict handling is the project's explicit policy, not a precedence rule
specified in the assignment. Its automatic checks do not measure fact coverage.

Plans, raw runs, automatic diagnostics and the pending full-field review are in
`../../experiments/2026-10-18-optimized-v1/`. The focused repeat there reuses two
of these cases intentionally; it is not extra independent data.
