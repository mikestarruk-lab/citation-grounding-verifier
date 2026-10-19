# Citation Grounding & Faithfulness Verifier

An interview project implementing `POST /verify`: extract factual claims from an
answer and classify them using only the supplied passages. The contract is in
[assignment.md](assignment.md).

Three approaches are implemented and evaluated on a frozen, owner-approved test
split: a lexical baseline, a minimally prompted LLM and an optimized LLM verifier.
See the [evaluation report](#evaluation-report) below.

## Run locally

Requires Python 3.12 and [uv](https://docs.astral.sh/uv/).

```sh
uv sync --locked
uv run python -m pytest -q
uv run python -m ruff check .
uv run python -m ruff format --check .
uv run python -m grounding_verifier.cli validate-data
uv run python -m grounding_verifier.cli gold-review --check
```

Offline checks require no API key. To run the default LLM service, copy
`.env.example` to `.env` and set `ANTHROPIC_API_KEY` locally. Never commit the key.

```sh
uv run uvicorn grounding_verifier.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the request/response schema. Set
`VERIFIER_METHOD=lexical` in the environment for a key-free service; other choices
are `minimal` (default) and `optimized` (lean-v1). Both LLM paths use `claude-haiku-5-5` with
the same inference configuration. Local citation validation rejects invalid
indices, fabricated quotes and incompatible verdict/citation combinations.
Technical failures return HTTP errors rather than factual verdicts.

## Review and evaluate

[The complete gold review](reviews/gold-dataset-review.md) contains every source,
answer, fact, verdict, explanation, annotation rationale and citation. It is
generated from `data/dev.jsonl`, `data/test.jsonl` and `data/manifest.json`:

```sh
uv run python -m grounding_verifier.cli gold-review
```

Edit the source files, then regenerate. This command does not approve or freeze
data. There are 8 development cases (12 facts) and 20 test cases (32 facts), in
four balanced categories with disjoint source groups. These short synthetic
specifications are a limited benchmark, not evidence of production accuracy.

Example offline development run and review export:

```sh
uv run python -m grounding_verifier.cli run --method lexical --split dev --out runs/dev-lexical-v2.json
uv run python -m grounding_verifier.cli review-template --run runs/dev-lexical-v2.json --out reviews/dev-lexical-v2.json
uv run python -m grounding_verifier.cli score --run runs/dev-lexical-v2.json --reviews reviews/dev-lexical-v2.json
```

Run files refuse replacement. A pending review produces no complete semantic
score. Human reviewers align fact meanings, preserve qualifiers when splitting
compound predictions, and judge evidence sufficiency. End-to-end fact-and-label
F1 penalizes omissions, duplicates and wrong verdicts; coverage, false support,
false rejection, citation legality, evidence sufficiency, atomicity and runtime
metrics are reported separately. Fixed-gold-fact diagnostics (`--mode gold`)
isolate verification quality and do not replace end-to-end evaluation.

Scoring checks canonical data and output hashes. Old v1 runs and
`reviews/archive/dev-lexical-pending.json` are historical pre-remediation artifacts and
cannot be replayed against the revised gold. Test runs require a human-approved,
hash-bound frozen manifest. Final test execution also waits for method freeze.
Paid runs share the local $20 budget ledger; retain it across experiments.

## Evaluation report

**Result.** On the frozen 20-case test split, the optimized verifier (lean-v1)
reached end-to-end fact + label F1 1.000 with 92% evidence sufficiency, minimal
0.970 with 79%, and the lexical baseline 0.400 with three false supports. Both LLM
methods scored 1.000 when given the gold facts directly, so the short test cases
mainly separate them on claim extraction and evidence, not on verdicts.

### Benchmark and metrics

- **Data.** 28 synthetic technical-specification cases in four balanced
  categories (supported, subtle distortion, extrinsic hallucination,
  multi-passage synthesis): 8 dev cases (12 facts) for development and 20 test
  cases (32 facts: 19 SUPPORTED, 7 CONTRADICTED, 6 UNSUPPORTED). Test gold was
  audited twice, edited only before freezing, approved by the project owner and
  hash-bound ([approval](reviews/test-gold-approval-2026-10-19.md)). Five extra
  development challenges (12 draft-gold facts) target failure modes found on dev.
- **End-to-end fact + label F1** (primary). Each predicted claim is aligned to at
  most one gold fact by meaning, keeping qualifiers. A matched claim with the
  right verdict is a true positive; a wrong verdict counts as both a false
  positive and a false negative; extra or duplicate claims are false positives.
  Alignment rule: references may resolve to entities, but content needed to
  match a gold fact must appear in the prediction's own text.
- **Evidence sufficiency.** Every SUPPORTED/CONTRADICTED unit's own quotes must
  contain every independently necessary premise (for example both links of a
  multi-hop chain). Citation legality (index in range, verbatim substring) is
  enforced in code and is 100% for every method, so it is reported separately.
- **Fixed-gold diagnostic.** Each method classifies the gold facts directly
  (`--mode gold`); macro-F1 needs no alignment and isolates verification.
- **Process.** Every method, prompt and selection rule was frozen before the
  test runs, which ran once each with no reruns
  ([plan](experiments/2026-10-19-final-test/PLAN.md)). Alignments were
  AI-proposed and then confirmed by the owner; this is not independent blind
  annotation.

### Results on the frozen test split

| Method | E2E F1 | Precision / recall | False support | False rejection | Evidence sufficiency | Fixed-gold macro-F1 |
|---|---:|---|---:|---:|---:|---:|
| Lexical (TF-IDF, threshold 0.65) | 0.400 | 0.394 / 0.406 | 3 | 12 | 3/10 (30%) | 0.368 |
| Minimal LLM | 0.970 | 0.941 / 1.000 | 0 | 0 | 22/28 (79%) | 1.000 |
| **Optimized LLM (lean-v1)** | **1.000** | 1.000 / 1.000 | 0 | 0 | **24/26 (92%)** | 1.000 |

| Method | p50 / p95 latency (s) | Cost per case (USD) | Tokens per case (in / out) | Request failures |
|---|---|---:|---|---:|
| Lexical | < 0.001 | 0 | none | 0/20 |
| Minimal LLM | 1.75 / 2.29 | 0.00020 | 847 / 230 | 0/20 |
| Optimized LLM | 2.50 / 3.55 | 0.00026 | 971 / 316 | 0/20 |

Both LLM methods use `claude-haiku-5-5` with medium effort. Cost is a
configured-rate estimate from recorded token usage, not an invoice; latency
is one run per method on the same day. The optimized prompt is longer, so it
costs about 28% more and is about 0.75 s slower at the median. Full records:
[test runs](experiments/2026-10-19-final-test/README.md) and the approved
reviews in `reviews/test-final/`.

### From minimal to optimized

1. **Baselines first.** On the approved dev split the reviewed minimal LLM
   already scored F1 1.000 (lexical 0.583). Prompting harder against eight
   solved cases would only overfit, so both comparators were frozen
   ([decision](experiments/baseline-freeze-2026-10-18.json)) and five
   development challenges were written around gaps seen in dev outputs:
   scoped quantities, a refutation that needs exclusivity premises, a sufficient
   (not necessary) condition, an embedded prompt injection, and a compound
   transactional claim.
2. **refined-v1** (the existing refined prompt plus one validated repair) and
   minimal both dropped conditions and cited incomplete premise chains on the
   challenges.
3. **refined-v2** added explicit rules for conditions, rule strength and
   refutation premises. It cited more premises but began over-refusing: on dev-08
   it demanded an unstated rule that a worker runs in its host's region.
4. **Full-passage citations** (a deterministic post-processing ablation) made
   evidence look complete by inclusion rather than selection, so evidence is
   always judged on the model's original quotes and the policy was not adopted.
5. **lean-v1** keeps the minimal prompt and adds four lines: keep conditions
   attached, preserve rule strength, flag irreconcilable conflicts, and allow
   valid multi-passage inference.
6. **Selection by preregistered repeats.** Three candidates ran three times on
   dev and challenges ([plan](experiments/2026-10-19-stability/PLAN.md),
   [results](experiments/2026-10-19-stability/README.md)). refined-v2 was excluded
   for repeating the dev-08 false rejection (2 of 5 runs) and one unrecovered
   contract violation; refined-v1 and lean tied on dev, and lean led on challenge
   F1 (0.906 vs 0.880) and evidence (91% vs 81%). Minimal, repeated afterwards
   for comparison only, scored 1.000 on dev and 0.878 on challenges.
7. **Repair path.** One validated retry is the optimized method's engineering
   gain. On six scripted invalid-then-valid responses, minimal fails all six and
   the repair path recovers all six; two consecutive invalid responses still
   fail ([controlled faults](experiments/2026-10-18-optimized-v1/controlled-faults.json)).
   No live test request needed it.

### Key failure cases

- **Lexical misses contradictions.** test-06 (31 vs 30 days) and test-09 become
  UNSUPPORTED, and test-07, test-08 and the V1 half of test-20 become SUPPORTED
  because the refuting sentence overlaps heavily with the claim. Sentence
  splitting also scores compound answers all-or-nothing, and it broke
  "Apache 2.0" at the period in test-15.
- **Minimal restates premises as claims.** In test-16 and test-20 it outputs
  source premises the answer never asserted ("The Acorn project uses the bronze
  retention policy."), costing precision. In multi-hop cases it quotes one
  passage only: test-17 omits Lina's role, test-19 the one-state-per-slot
  premise, and test-20 the exclusive routing rule.
- **Optimized still misses premises.** test-17's contradiction quotes only
  "cannot delete logs" without Lina's sole role, and test-01 quotes "Larger files
  are rejected." without the 8 MiB threshold that defines "larger".
- **Development failures that the test split does not show.** refined-v2's
  over-refusal on dev-08; lean once turned the challenge-03 missing-condition
  case into a contradiction (as did minimal once); refined-v1 and lean each judged
  "three additional queued jobs" UNSUPPORTED once against a source that says
  "up to three", a gold boundary worth stating.

### Limitations

- The cases are short (5–22 words of context) and mostly single-sentence
  evidence, so both LLMs hit the verdict ceiling; differences are small and
  rest on 20 test cases and one run per method.
- Gold and alignments were owner-approved after AI review, not independently
  annotated; challenge gold remains draft and is used only for development.
- The comparison is one model at one effort setting; latency and cost come from
  single runs.

### Reproducing the test results

Scoring needs no API key; it replays saved runs against the approved reviews:

```sh
uv run python -m grounding_verifier.cli score --run experiments/2026-10-19-final-test/optimized-test.json --reviews reviews/test-final/optimized-test-approved.json
```

New paid runs write to new paths (existing files are never overwritten); the
CLI refuses test data whose hash does not match the frozen manifest:

```sh
uv run python -m grounding_verifier.cli run --method optimized --split test --experiment-note experiments/method-freeze-2026-10-19.json --out runs/optimized-test-new.json
```

## Project records

- [First optimized-method development cycle](experiments/2026-10-18-optimized-v1/README.md):
  actual variant/repeat runs, controlled repair faults and live boundary checks.
  Added development challenges retain draft gold; no new complete semantic F1 or
  final winner is claimed. [Gold-only review](experiments/2026-10-18-optimized-v1/challenge-gold-review.md).

- [Baseline decision, 2026-10-18](experiments/baseline-freeze-2026-10-18.json):
  retain the owner-reviewed lexical starting threshold 0.65 and fixed minimal
  LLM comparator. The 22-threshold study is sensitivity analysis; neither
  unadopted candidate requires additional review. This is a scope decision,
  not a claim that 0.65 is optimal. Optimization work targets the third approach.

- [Local error explorer](tools/error-explorer/USAGE.md): inspect reviewed baseline
  errors, threshold tradeoffs, confusion matrices and complete evidence. On this
  Windows workstation, run `./tools/error-explorer/start.ps1 -Refresh` from the
  repository root. [Baseline adjustment rationale, Chinese](docs/baseline-adjustment.zh-CN.md).

- [Development v2 reviewed results](experiments/2026-10-16-dev-v2/reviewed-results-2026-10-17.md):
  owner-reviewed end-to-end F1 is 0.5833 for lexical and 1.0 for minimal LLM on
  these eight development cases. Evidence sufficiency is 3/5 and 10/10.
  [The completed workbook](reviews/dev-v2/dev-v2-alignment.xlsx), approved JSON
  records and import receipt preserve the review decisions. This was review after
  AI feedback, not independent blind annotation or final test evaluation.
- [Optimized method selection, 2026-10-19](experiments/method-freeze-2026-10-19.json),
  from [stability repeats](experiments/2026-10-19-stability/README.md) of three
  candidates on approved dev and development challenges.
- [Owner approval and freeze of test gold](reviews/test-gold-approval-2026-10-19.md).
- [Owner approval of development gold](reviews/dev-gold-approval-2026-10-16.md).

- [Gold audit](reviews/gold/gold-dataset-audit-2026-10-15.md) and
  [remediation plan](reviews/gold/gold-audit-remediation-plan-2026-10-15.md).
- [Design rationale, Chinese](docs/design-rationale.zh-CN.md).
- [Implementation decisions and change history, Chinese](docs/change-history.zh-CN.md).
