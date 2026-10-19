# Citation Grounding & Faithfulness Verifier

An interview project implementing `POST /verify`: extract factual claims from an
answer and classify them using only the supplied passages. The contract is in
[assignment.md](assignment.md).

**Work in progress.** The service, lexical baseline, LLM paths and evaluation tools
are implemented. Development gold is owner-approved; test gold remains draft.
Final semantic reviews,
optimization comparisons and final benchmark results are pending. The optimized
path is a candidate, not a demonstrated improvement.

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
are `minimal` (default) and `optimized`. Both LLM paths use `claude-haiku-5-5` with
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

## Project records

- [Development v2 output review](reviews/dev-v2/dev-v2-output-review.md): pending
  alignment/evidence review, with method names hidden as A/B. Review it before
  opening the [method-labelled experiment records](experiments/2026-10-16-dev-v2/README.md).
- [Owner approval of development gold](reviews/dev-gold-approval-2026-10-16.md).

- [Gold audit](reviews/gold/gold-dataset-audit-2026-10-15.md) and
  [remediation plan](reviews/gold/gold-audit-remediation-plan-2026-10-15.md).
- [Design rationale, Chinese](docs/design-rationale.zh-CN.md).
- [Implementation decisions and change history, Chinese](docs/change-history.zh-CN.md).

The current change addresses gold granularity, specific explanations and complete
review fields. No new model-quality claim follows from those repairs. A final
English report with reviewed comparisons, failure cases and clean reproduction
evidence remains a delivery task.
