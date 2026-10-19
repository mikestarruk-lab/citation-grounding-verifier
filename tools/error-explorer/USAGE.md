# Local development error explorer

This is an optional analysis tool, separate from the Python HTTP service. It
reads saved development evidence and makes no model calls. No API key is needed.
Chinese reader-facing labels help the owner inspect the original English data.

## Open and refresh on this Windows workstation

From the repository root:

```powershell
# Serve the existing compiled snapshot. Stop with Ctrl+C.
./tools/error-explorer/start.ps1

# Validate source evidence, regenerate, build, then serve.
./tools/error-explorer/start.ps1 -Refresh
```

The default URL is `http://127.0.0.1:4173/`. If another preview already occupies
the port, use `-Port 4174`; do not stop unrelated servers. Serving is loopback
only. The refresh path uses the installed Codex Data plugin and bundled Node;
the verifier itself does not gain a Node or frontend dependency.

For a fresh checkout, first create the Python environment with `uv sync --locked`.
The visualizer source and lock file are included. Its shared UI runtime is
plugin-provided scaffolding. In an ordinary Node environment, the copied package
also defines `npm ci` and `npm run build`; that independent source-build path was
not exercised in this task. The verified build here uses Codex's bundled prebuilt
runtime without downloading packages.

The evidence-only exporter is independently runnable:

```sh
uv run python -m grounding_verifier.error_explorer --out tools/error-explorer/src/data.json --build-status complete
```

Regenerating JSON does not rebuild HTML. Use `-Refresh` for the complete workflow.
Export fails on stale run/review/data hashes rather than displaying mixed versions.
Refresh currently targets the named v2 study; a new experiment lineage needs an
explicit exporter update. Browser filters change only the view, never approvals.

## What to inspect

1. Compare the original lexical and minimal LLM baselines against two lexical
   candidates. Owner-reviewed and projected scores are labeled separately.
2. Inspect all 22 actual threshold configurations on numeric scatter axes.
3. Select a method and click a confusion-matrix cell to find its fact units.
4. Filter by issue or case category; clear filters to recover the whole method.
5. Click a record to inspect the complete context, answer, gold explanations,
   original prediction, reasoning, citations and output hash. Source/copy actions
   use the same scoped rows as their component.

Compound predictions inherit their original verdict and citations after the
owner's semantic split. Error kinds overlap. A correct label can still have
insufficient evidence. Candidate-wide unknown evidence is not displayed as zero.
Exact unchanged output approvals remain valid; changed outputs remain pending.

The benchmark is only 8 short synthetic dev cases / 12 gold facts. The owner
review followed AI feedback. Neither independence nor production accuracy is
claimed. Test cases, credentials and API budgets are not read by this exporter.
Raw historical metadata may mention the test manifest; no test outputs are used.

The decision rationale is in [baseline-adjustment.zh-CN.md](../../docs/baseline-adjustment.zh-CN.md).
On 2026-10-18 the owner retained the reviewed lexical configuration at 0.65 and
fixed the minimal LLM comparator. Candidate configurations are now unadopted
sensitivity results; their evidence remains unreviewed and no additional review
is required. The tool preserves their historical pending states.
No baseline code, prompt, service default, gold data or review approval is changed.

## Validation performed

- Reconciled the four comparisons with saved review/scoring and threshold evidence.
- Python regression checks cover metrics, evidence unknowns, tamper rejection,
  and absence of reads of `test.jsonl` or `.env`.
- Rendered inspection covers the comparison bars, both threshold scatterplots,
  confusion matrix, full detail, normal/narrow layouts, and representative method,
  issue, category, matrix and reset interactions. Empty filtered results are explicit.
- The original 0.65 and all existing approval files are preserved.

Compiled output, browser-local layout edits and portable exports are not versioned.
No publication, GitHub upload or external sharing is performed by this tool.
