# Optimized-candidate stability repeats

2026-10-19. Three repeats of refined-v1, refined-v2 (span citations) and lean on
the approved dev split (8 cases, 12 facts) and development challenges v2
(5 cases, 12 facts), run as preregistered in [PLAN.md](PLAN.md), committed before
any call (`588911e`). 117 serial calls; configured-rate cost **$0.0396647**;
local ledger total **$0.0770948** of the $20 cap. The frozen test split was not
read or run. Scores below are AI-proposed per unit; the alignment rule and the
challenge gold they rest on were owner-approved on 2026-10-19
([approval](../../reviews/development-challenges-v1/challenge-gold-v2-approval-2026-10-19.md)).

## Results

| Candidate | Dev mean F1 (worst) | Challenge mean F1 (worst) | Label errors over 3 repeats | Evidence, original citations | Failed requests | p50 / p95 s | Cost USD |
|---|---|---|---|---|---:|---|---:|
| minimal (comparator, added after selection) | 1.000 (1.000) | 0.878 (0.800) | challenge-03 U→C once | 45/54 | 0 | 2.162 / 5.890 | 0.0118826 |
| refined-v1 | **1.000** (1.000) | 0.880 (0.800) | challenge-01/g2 S→U once | 44/54 | 0 | 2.361 / 4.693 | 0.0124080 |
| refined-v2 | 0.972 (0.917) | 0.920 (0.800) | dev-08 S→U once | 49/53 | 1 | 2.114 / 4.678 | 0.0151070 |
| lean | **1.000** (1.000) | **0.906** (0.800) | challenge-01/g2 S→U once; challenge-03 U→C once | **50/55** | 0 | 2.364 / 5.361 | 0.0121497 |

Per-run scores, every error and the alignment decisions are in
`stability-summary.json` and `alignment-decisions.json`. `analyze.py` recomputes
them from the saved runs.

## Minimal comparator repeats (addendum)

Run after the selection under [PLAN-minimal.md](PLAN-minimal.md) (`4cc58a9`),
39 calls, for report comparison only. Minimal is also perfect on approved dev in
all three repeats. On challenges it averages 0.878, below lean's 0.906: it never
matches the full challenge-05 same-committed-transaction fact (g3), and once adds
an unsupported contradiction on challenge-03. Its original-citation evidence
(45/54, 83%; challenges alone 15/24) is below lean's (50/55, 91%; challenges 20/25). No false support recurred.
Lean's measurable advantages over minimal are therefore evidence completeness and
a small challenge-F1 gain, plus the repair path; not dev accuracy.

## What the repeats show

- **refined-v2 repeats its dev-08 failure.** Run 3 again calls the worker's
  region UNSUPPORTED, demanding an unstated rule that a process runs in its
  host's region. Across all five dev-08 runs of this prompt, 2 are wrong. Its
  run 3 also failed challenge-01 entirely: the output had a non-verbatim quote
  twice, so the service returned HTTP 502 instead of a report.
- **refined-v1 and lean are both perfect on approved dev in every repeat.**
  They differ on challenges. Refined-v1's challenge-05 output twice relies on a
  cross-sentence reference or drops the reported-success scope; lean once adds a
  contradiction for challenge-03 that the source does not establish.
- **Both share one recurring disagreement with challenge gold.** In one repeat each,
  "three additional queued jobs" is judged UNSUPPORTED because the source says
  "up to three". Gold treats this as SUPPORTED; this boundary should be stated
  in the report.
- **The challenge gap between refined-v1 and lean is small.** 0.906 against
  0.880 is three runs on five cases; counting refined-v1's unscoped compound as
  one extra unit instead of three gives 0.903. Lean's original citations are
  clearly more complete (50/55 against 44/54).

## Decision under the preregistered rule

1. Invariants: refined-v2 had one unrecovered contract violation.
2. Approved dev F1: refined-v1 and lean tie at 1.000; refined-v2 is lower.
3. Challenge F1 breaks the tie: lean 0.906, refined-v1 0.880.
4. False supports: none for any candidate. Evidence and cost also favor lean.

**Recommendation: lean-v1 with span citations.** Labels do not depend on the
citation policy (expansion runs after the model), so these runs support lean
with the model's own spans. Spans keep the evidence claims honest; full-passage
expansion can remain a documented, optional ablation.

This does **not** show that lean beats the fixed minimal comparator: minimal's
reviewed dev F1 is also 1.000, and its single challenge run was not repeated.
The report should present lean as the most stable optimized candidate, with the
repair path as its measured engineering gain, not as a proven quality jump.
Selection needs owner confirmation; the HTTP default is unchanged until then.
