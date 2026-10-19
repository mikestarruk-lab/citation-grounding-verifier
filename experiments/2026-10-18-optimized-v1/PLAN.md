# Optimized verifier v1: preregistered development experiment

Decision date: 2026-10-18, Europe/London. Both comparators remain fixed by
`../baseline-freeze-2026-10-18.json`. This plan precedes new paid calls.

## Evidence, hypotheses and stopping rule

The reviewed minimal LLM has no fact/label errors on eight short development
cases. Lexical failures do not establish LLM failures. Its short citations also
expose a review boundary: local reference resolution is acceptable, independently
necessary uncited premises are not. There is no evidence yet for a two-stage
extractor or a claim of semantic improvement.

Evaluate the existing refined-prompt plus one bounded output-repair candidate.
The refined prompt was implemented before this experiment; it is not a new
change discovered after observing these challenge outputs. Hypotheses:

- Explicit qualification and atomicity instructions may help retain subject,
  condition and quantity when one answer combines supported and distorted facts.
- Explicit complete-link instructions may help citation sufficiency across
  multiple passages and distractors.
- One validated repair can recover a deterministically invalid model output;
  this improves request recovery, not necessarily semantic correctness.

Use five development challenges covering scoped quantities, a multi-hop
refutation, a missing premise, embedded instructions and a fully supported
compound answer with exact-text punctuation. Their source entities are new;
design derives from development/engineering gaps, not final test cases.
AI-authored gold is draft and cannot establish final quality scores without
review. Keep this suite separate from the approved dev split and final test.

Conflict under identical conditions, empty context and a non-factual answer are
separate engineering boundaries, not additions to the main scored benchmark.

Run minimal and optimized on the same challenge inputs, serially, with
claude-haiku-5-5, adaptive thinking, medium effort, max output 8192, the existing
90-second deadline and shared additional-attempt budget. Also run optimized on
the original dev split. Preserve original reviewed minimal runs; any latency
comparison against that historical run must disclose its different run date.
Rerun consequential differing cases on both methods if needed for stability.

Do not tune prompts against these outputs until the first comparison is saved.
No final test calls or gold changes. Stop new calls if the shared $20 budget
cannot reserve the next attempt. Record configured-rate cost estimates and
outstanding reservations; never equate them with an independently checked bill.

## Review and candidate selection

Store raw responses, output hashes, source/configuration metadata and pending
review packets. Automatic quote checks and fixed-gold diagnostic scores are
separate from complete end-to-end human scoring. AI observations remain explicitly
AI observations. New output hashes do not inherit human approval.

Inspect actual extraction, verdict and evidence failures before adding complexity.
If all methods solve these challenges, report the ceiling. Do not invent a
quality improvement. Compare the cost of the refined prompt with its observed
benefit; a repair-only candidate is an available ablation if refinement adds
cost without benefit. No precommitment to refined prompting or two stages.

Controlled output faults use an already legal report and deliberately corrupt
JSON, index, quote or required evidence. The same scripted invalid/valid sequence
is supplied to both implementations. Report recovery and extra logical calls;
these are not live API requests, costs, latency measurements or estimates of
naturally occurring model errors.

End this experiment with evidence, an explicit candidate decision or remaining
review work, and a reproducible report. Final test approval/freezing and separate
audit repairs remain independent delivery tasks.
