# First optimized-verifier development cycle

2026-10-18. This is a completed experiment cycle, **not a selected final winner**.
The original lexical 0.65 and minimal LLM comparators remain fixed. No final-test
model run or canonical dev/test data change occurred. New complete quality
scores remain pending; additional challenge gold is an AI proposal.

## What the experiment established

The original minimal method already has reviewed F1 1.0 on eight short dev cases.
We added five distinct development challenges (12 proposed facts), kept outside
that approved split. The first actual outputs exposed condition-loss and citation
premise gaps. We evaluated the existing refined prompt, a targeted longer prompt,
a deterministic quotation policy and a shorter-prompt ablation. Plans were saved
before each new variant's calls; failed attempts and focused repeats are retained.

- **More instruction is not uniformly better.** A refined-v2 run returned U for
  approved dev-08, demanding an extra rule that a worker on a host runs in that
  host's region. Another run of the same prompt returned S. The erroneous U was
  present before passage expansion, so expansion did not cause this regression.
- **A valid quote can omit an essential premise.** Both initial prompts cite the
  challenge-02 location chain but omit explicit exclusivity constraints. V2 adds
  region uniqueness/distinctness while still missing single-host exclusivity.
  Complete already-cited passages include all three named constraints in the
  initial run and focused repeat. This exact-premise check is not a general
  semantic-sufficiency metric.
- **Shortening also has tradeoffs.** Lean returns S for dev-08 in its original
  dev run and focused repeat, but its first challenge-03 run again adds an
  unqualified retry claim. Its focused repeat keeps the complete timeout claim.
  The first run also retains an overstated "only" in the explanation. Do not
  present either variant as a stable fix based on the better sample alone.
- **Bounded repair has a separately measured engineering benefit.** On six
  scripted invalid/then-valid response sequences, minimal fails 6/6 after one
  logical call; the existing repair path recovers 6/6 after two. Two invalid
  replies still fail after two calls. These are scripted controls, not natural
  API failures, live latency/cost measurements or proof of semantic correctness.

## Comparable challenge runs

Each row uses the same five inputs, model `claude-haiku-5-5`, adaptive thinking,
medium effort, max output 8192, serial execution and request retry/deadline limits.
No live output repair was needed. Quality F1 is deliberately not generated from
unreviewed alignment or draft gold.

| Configuration | Requests | First/final quote legality | p50 / p95 seconds | Estimated USD | Raw / final quote characters |
|---|---:|---|---:|---:|---:|
| Fixed minimal | 5/5 | 100% / 100% | 3.841 / 5.055 | 0.0023291 | 603 / 603 |
| Refined-v1, spans | 5/5 | 100% / 100% | 3.384 / 4.433 | 0.0023916 | 768 / 768 |
| Refined-v2, spans | 5/5 | 100% / 100% | 4.505 / 6.037 | 0.0032041 | 629 / 629 |
| Refined-v2, full cited passages | 5/5 | 100% / 100% | 3.866 / 5.825 | 0.0028851 | 628 / 1807 |
| Lean-v1, full cited passages | 5/5 | 100% / 100% | 4.385 / 5.585 | 0.0026071 | 908 / 2411 |

Five latency samples do not establish a stable speed ranking. First-client-call
and warm-call values are separate in the JSON summaries. Comparing optimized
original-dev latency with the old reviewed minimal run also crosses run dates.
The same prompt can consume different output/thinking tokens on different calls;
quote postprocessing itself requests no additional model tokens or calls.

Across this cycle: **77 actual API calls**, all returned valid reports; configured
rate usage estimates total **$0.0283299**. Including earlier experiments the local
ledger estimates **$0.0350645**, with zero unsettled reservations and a $20 cap.
These are recorded usage/configured-price calculations, not a checked invoice.
Totals include repeated development inputs and nine boundary calls, not 77
independent benchmark cases. The scripted controls add zero API calls.

## Why full-passage quotation is an experiment

The program validates the original index and verbatim quote before expansion.
Invalid model text cannot be laundered into a legal citation. It then copies only
the full passages at existing cited indices, deduplicating per claim. It preserves
claim text, verdict, reasoning, raw first output and U's empty citation list.
No new source indices or model calls are introduced.

This eliminates within-passage omissions by inclusion, not by understanding the
proof. Wrong labels, missing passage indices and irrelevant evidence remain
possible. Longer responses and distracting material are concrete costs: Lean's
five-case quotations grew from 908 to 2411 characters. Do not mistake larger
quotations or 100% legality for complete grounding.

## Engineering boundaries

The unresolved same-condition conflict, empty-context facts and non-factual
answer checks are outside main quality scoring. Minimal meets 2/3 of the
project's policies; refined-v1 and Lean meet 3/3 in their respective runs. The
difference is conflict handling. The assignment does not define conflict
precedence, so this is a project-policy result, not a universal label-error claim.
The empty-context checker tests nonempty U claims/empty citations, not coverage.

## Decision and remaining review

Stop additional prompt variants for this cycle. **Do not promote any candidate
or change the HTTP default yet.** Keep the fixed comparators and the failure
records. The current HTTP optimized path still defaults to refined-v1/spans;
new variants and quotation policy are available explicitly through the benchmark
CLI. Final selection belongs to the next reviewed comparison/reliability step.
No two-stage architecture was added.

Before a full quality comparison, review the five draft gold cases and semantic
alignment/evidence of the chosen candidate, especially challenge-02/03 and the
original dev-08 regression. The primary review document includes minimal
challenge outputs plus Lean challenge/original-dev outputs (18 packets); discarded
variant raw runs and their pending packets remain accessible for comparison.
Its convenience focus is not a selection of Lean as the winner. New output hashes
were not assigned old human approvals.

- [Start with draft gold only](challenge-gold-review.md): five cases, no model predictions.
- [AI gold rereview and owner checklist](../../reviews/development-challenges-v1/gold-ai-review.zh-CN.md):
  full source, original annotations, per-fact AI findings and editable owner fields.
  This later rereview flags reasoning and success/commit scope questions; it does
  not approve or revise the original draft or confer independence from prior outputs.
- [Primary full-field output review](review-ready-complete.md).
- [AI-authored challenge gold and scope](../../data/development-challenges-v1/README.md).
- `experiment-summary-complete.json`: replayed automatic metrics, exact-premise
  diagnostics, usage totals and run digests. No complete new semantic F1.
- `experiment-summary.json`: the earlier 58-call checkpoint, preserved as history.
- `controlled-faults.json`, `live-boundaries.json`, `lean-live-boundaries.json`:
  controlled versus live engineering evidence, explicitly separated.
- Plans: `PLAN.md`, `V2-HYPOTHESIS.md`, `PASSAGE-HYPOTHESIS.md`, `LEAN-HYPOTHESIS.md`.

## Reproduction

Offline tests and scoring use no API key. Existing output paths refuse overwrite.
For scoring a saved run without reviews, for example:

```sh
uv run python -m grounding_verifier.cli score --run experiments/2026-10-18-optimized-v1/optimized-lean-challenges.json --data data/development-challenges-v1
uv run python -m pytest -q
uv run python -m ruff check .
```

The full comparison can be rerun with the standard CLI into new output paths:

```sh
uv run python -m grounding_verifier.cli run --method optimized --prompt-variant lean-v1 --citation-policy passage --data data/development-challenges-v1 --out runs/lean-challenges-reproduction.json --experiment-note experiments/2026-10-18-optimized-v1/LEAN-HYPOTHESIS.md
```

`run_v2.py`, `run_passage.py`, `run_lean.py` contain the exact serial recipes and
explicit focused subsets; their `--only` options resume missing phases. They fail
on existing selected outputs. `run_controls.py` reproduces faults or boundaries;
its pre-Lean source is retained under `archive/`. `summarize.py --out NEW.json
--review-out NEW.md` recomputes automatic metrics from saved runs and exports
review fields; it never manufactures approval. Fresh model replies and latency
may differ. All runs record dirty working-tree status, source hash, Git commit,
exact prompt and data hash; the Git commit alone does not identify this uncommitted
source. No credentials or local budget ledger belong in the public repository.
