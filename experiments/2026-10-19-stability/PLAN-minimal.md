# Minimal comparator repeats: preregistered addendum

Decision date: 2026-10-19, Europe/London. Committed before any call in this
addendum. The optimized method was already selected and frozen
(`../method-freeze-2026-10-19.json`, commit `235b7d6`). **These results are for
report comparison only and cannot change that selection.**

## Why

The fixed minimal comparator has one reviewed dev run and one challenge run. The
three candidates each have three repeats. Repeating minimal on the same inputs
makes the report's minimal-versus-optimized comparison symmetric and shows its
run-to-run variation, including whether its earlier challenge-03 false support
recurs.

## Runs

- Configuration: fixed minimal, unchanged prompt (digest
  `cfedee55daec92b111506accbc65053e162643047b118594ca2e0131b0a179df`), model
  `claude-haiku-5-5`, medium effort, no output repair, span citations.
- Inputs: the same approved dev split and development challenges v2 as
  [PLAN.md](PLAN.md), 3 repeats, serial: 39 calls, expected cost under $0.02.
- Outputs: `minimal-{dev,challenges}-r{1,2,3}.json` in this directory.

## Scoring

Identical to [PLAN.md](PLAN.md): the same rev2 alignment rule, the same premise
table for evidence on original citations, F1 mean and worst repeat, false
support and false rejection counts, cost and latency. Any new prediction text gets
an explicit decision in `alignment-decisions.json`, applied the same way as for
the candidates. Scores remain AI-proposed and pending owner review. The frozen
test split is not read in this addendum.
