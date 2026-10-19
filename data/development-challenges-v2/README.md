# Development challenges v2

Five cases / twelve facts, derived from v1 after the owner accepted the AI review's
clarification approach. Canonical hash:
`c0a11c4a6c7eb11c5f8f18229cbb323d00e61d8c8f5e97c12772bca4979ad504`.

- challenge-02/g1 has a complete exclusion explanation; its input is unchanged.
- challenge-05 now explicitly reports success after the transaction commits.
  The answer and gold describe the already completed changes for a reported
  success, preserving action ordering and excluding pre-commit failures.
- The three delivery units score the status update, deletion, and shared committed
  transaction relation. Match each gold once; splitting a compound prediction
  inherits its verdict/citations and does not make its original output atomic.
- All labels and IDs are retained. challenge-01/03/04 are unchanged in full.

The exact owner message and its bounded scope are recorded in
[clarification-decision.json](../../reviews/development-challenges-v1/clarification-decision.json).
Acceptance of the clarification approach is not blanket approval of untouched
units or review of the assistant's newly materialized exact English wording.
The manifest therefore remains draft pending final gold acceptance.

The [complete revised review](../../reviews/development-challenges-v1/clarified-gold-v2.zh-CN.md)
contains every passage, answer, gold field, and citation. v1 and its original runs
remain historical artifacts. Only challenge-05 has a changed model input and needs
new inference. Reusing other outputs requires explicit input identity/provenance
and new review bindings; never rewrite an old run's dataset hash or approvals.
This version does not add independent cases or alter the final test split.
