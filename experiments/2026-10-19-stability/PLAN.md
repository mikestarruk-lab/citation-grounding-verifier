# Optimized-candidate stability repeats: preregistered plan

Decision date: 2026-10-19, Europe/London. Written and committed before any call
in this experiment. Linear: MIC-109 (reliability validation and method freeze).

## Why

The first optimized cycle left three plausible candidates and one known
instability: the refined-v2 prompt returned a wrong UNSUPPORTED for approved
dev-08 in one run (`optimized-passage-original-dev.json`) and SUPPORTED in
another. Lean once dropped the timeout condition on challenge-03 and kept it on
a repeat. Single samples cannot separate a prompt effect from run-to-run noise,
so the method is chosen from repeated runs instead of the best sample.

## Candidates (no new variants, no prompt edits)

| Candidate | `--prompt-variant` | `--citation-policy` |
|---|---|---|
| refined-v1 | `refined-v1` | `span` |
| refined-v2 | `refined-v2` | `span` |
| lean | `lean-v1` | `passage` (as previously run; evidence is judged on the model's original pre-expansion citations, which every run stores) |

The fixed minimal comparator and lexical baseline are not rerun.

## Inputs and runs

- Approved dev split: `data/dev.jsonl`, hash
  `e39de6a74af6717c5d1ae0621195b730b01e2d969d40581cb2e7ea340962bd6c`, 8 cases.
- Development challenges v2: `data/development-challenges-v2/dev.jsonl`, hash
  `c0a11c4a6c7eb11c5f8f18229cbb323d00e61d8c8f5e97c12772bca4979ad504`, 5 cases
  (draft gold; the owner accepted the clarification approach).
- 3 candidates × 3 repeats × 13 cases = 117 serial calls, in the order
  repeat → candidate → dataset, so time-of-day drift spreads across candidates.
- Fixed configuration: `claude-haiku-5-5`, adaptive thinking, medium effort,
  max output 8192, existing deadline and shared retry budget.
- The frozen test split is not read or run. Shared $20 budget ledger; stop if
  the next attempt cannot be reserved. Expected cost is below $0.10.

## How the results are scored

All scoring of new outputs is AI-proposed and marked pending owner review.

1. **Interface invariants:** every request returns a valid report (citation
   legality is enforced in code; failures and repairs are counted).
2. **Fact + label F1 per run**, aligned with the rev2 rule from
   `../2026-10-18-challenges-v2/ai-alignment-2026-10-19.rev2.zh-CN.md`:
   references resolve to entities only; content needed to match gold must be in
   the prediction's own text. An extra partial-relation unit counts as a false
   positive, applied identically to every candidate. Report dev and challenge
   F1 separately and their mean over the 3 repeats, plus the worst repeat.
3. **False support** (gold C/U predicted S), then **false rejection** (gold S
   predicted C/U, e.g. dev-08), counted over all repeats.
4. **Evidence sufficiency** on the model's original citations for matched S/C
   units, using the challenge-02 premise standard.
5. **Cost and latency:** configured-rate cost and p50/p95 per candidate.

## Decision rule (from `docs/design-rationale.zh-CN.md` §6.3)

Satisfy invariants, then compare development fact+label F1 (mean over repeats,
approved dev and challenges both reported; the approved dev split decides first,
challenges break a dev tie). Ties go to fewer false supports, then evidence
sufficiency, then cost and latency. If no candidate beats minimal's reviewed
dev result and the challenge advantage is not consistent across repeats, prefer
the simplest candidate and say so. A candidate with a dev label error in any
repeat is not excluded automatically, but the error rate is reported next to
its F1. No prompt changes are made after seeing these outputs; the final
choice still needs owner confirmation and owner review of its test outputs.
