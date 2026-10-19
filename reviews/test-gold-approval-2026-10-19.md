# Test gold approval and freeze

- Reviewer: Michael (personal GitHub account: mikestarruk-lab).
- Date: 2026-10-19, Europe/London.
- Scope: test-01 through test-20, 20 cases and 32 gold facts (19 SUPPORTED,
  7 CONTRADICTED, 6 UNSUPPORTED), including fact boundaries, qualifiers,
  verdicts, evidence and explanations.
- Canonical dataset hash:
  `cbeb222ac9160b048f90d9a12f42286a9ef0b6e514bfc1b67bfd0e1dc806712a`.
- Source version presented for review: repository commit `16d5718`, generated
  `reviews/gold-dataset-review.md`, plus an AI case-by-case review document shared
  with the owner that recommended keeping all 32 labels.
- Changes made before approval, each at the owner's request: test-18 reasoning
  (sufficient vs. necessary condition), test-04 answer wording, test-03/g2
  wording, and the test-17 and test-19 source passages.
- Open review items: the owner decided to keep test-05's g1/g3/g2 ID order and to
  add no new test cases. The limited difficulty of the short cases will be stated
  in the evaluation report.
- Confirmation provenance: the project owner wrote in this chat **“批准 test gold，
  哈希 cbeb222ac9160b048f90d9a12f42286a9ef0b6e514bfc1b67bfd0e1dc806712a。剩下两个决定事项保持原样。”**
  and asked for the split to be frozen.

This is owner approval after AI review feedback, not independent external
validation. The test split is frozen from this point: no test data edits, and no
method, prompt or threshold tuning based on test results. Final test runs still
wait for the optimized method to be selected. Model-output alignment and evidence
sufficiency on test outputs require their own reviews. Any change to test data
invalidates this hash-bound approval.
