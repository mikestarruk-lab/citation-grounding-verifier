# Targeted refined-v2 hypothesis

Written after saving the first minimal/optimized challenge outputs and before
any refined-v2 calls. The first candidate remains preserved with its exact
prompt in `optimized-challenges.json`; it stays the default experimental variant
until a separate selection decision. No minimal prompt or lexical change.

Observed development failures (AI inspection, not owner-reviewed scores):

- Minimal challenge-03 produces an extra unqualified retry fact. The first
  refined candidate retains the timeout condition in one fact. This may vary
  with sampling and needs a focused repeat before a stability claim.
- Both methods add an unstated exclusivity restriction using "only" in the
  retry explanation. A positive retry rule is not an exhaustive policy.
- Both challenge-02 refutations cite the placement chain but omit the explicit
  single-host/single-region/distinct-region constraints needed to exclude West.
- Minimal challenge-05 cites a deletion fragment without its success condition.
  Citation sufficiency should be reviewed separately from correct labels;
  the first refined candidate preserves that condition for deletion.

Refined-v2 adds general instructions to retain conditions, avoid redundant
unqualified claims, distinguish sufficient from necessary conditions, and cite
the exclusion premises for indirect refutations. It contains no case names,
expected verdicts or final-test examples. Same call structure/model/effort and
one-repair bound. No two-stage decomposition is justified yet.

Run refined-v2 on the entire five-case challenge suite and original eight-case
dev split. Compare the exact outputs and quotes with v1, then repeat the two
consequential diagnostic cases (challenge-02/03) across all three methods.
Keep challenge gold draft. No full human F1 claim from automated text matching.
These repeats are development diagnostics, not fresh held-out validation.
