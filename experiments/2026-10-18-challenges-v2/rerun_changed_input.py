"""Run only the changed challenge under the five existing configurations."""

import argparse
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv

from grounding_verifier.cli import run_benchmark, write_json
from grounding_verifier.dataset import dataset_hash, digest, load_cases
from grounding_verifier.llm import LLMVerifier

HERE = Path("experiments/2026-10-18-challenges-v2")
OLD = Path("experiments/2026-10-18-optimized-v1")
DATA = Path("data/development-challenges-v2")
SPECS = [
    ("minimal", "minimal", "refined-v1", "span", "minimal-challenges"),
    ("refined-v1", "optimized", "refined-v1", "span", "optimized-challenges"),
    ("refined-v2", "optimized", "refined-v2", "span", "optimized-v2-challenges"),
    ("refined-v2-passage", "optimized", "refined-v2", "passage", "optimized-passage-challenges"),
    ("lean-v1-passage", "optimized", "lean-v1", "passage", "optimized-lean-challenges"),
]


def prepare():
    old = load_cases(Path("data/development-challenges-v1/dev.jsonl"))
    new = load_cases(DATA / "dev.jsonl")
    assert dataset_hash(new) == "c0a11c4a6c7eb11c5f8f18229cbb323d00e61d8c8f5e97c12772bca4979ad504"
    assert [a.id for a, b in zip(old, new, strict=True) if a.request() != b.request()] == [
        "challenge-05"
    ]
    for _, method, variant, policy, prior_name in SPECS:
        prior = json.loads((OLD / f"{prior_name}.json").read_text(encoding="utf-8"))
        verifier = LLMVerifier(
            None,
            optimized=method == "optimized",
            prompt_variant=variant if method == "optimized" else None,
            citation_policy=policy,
        )
        assert prior["prompt"] == verifier.prompt, "Existing prompt changed"
        assert prior["model"] == "claude-haiku-5-5" and prior["effort"] == "medium"
        assert (prior.get("citation_policy") or "span") == policy
    selected = [c for c in new if c.id == "challenge-05"]
    subset = HERE / "changed-input"
    subset.mkdir(parents=True, exist_ok=True)
    content = "".join(c.model_dump_json() + "\n" for c in selected)
    source = subset / "dev.jsonl"
    if source.exists():
        assert source.read_text(encoding="utf-8") == content
    else:
        source.write_text(content, encoding="utf-8")
        write_json(
            subset / "manifest.json",
            {
                "dev": {"review_status": "draft", "reviewed_by": None},
                "parent_dataset_hash": dataset_hash(new),
                "subset_dataset_hash": dataset_hash(selected),
                "request_hash": digest(selected[0].request().model_dump(mode="json")),
                "note": "Changed-input development subset, not independent additional data.",
            },
        )
    return subset


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=[s[0] for s in SPECS])
    args = parser.parse_args()
    subset = prepare()
    selected = [s for s in SPECS if not args.only or s[0] == args.only]
    if any((HERE / f"{s[0]}-challenge05.json").exists() for s in selected):
        raise ValueError("Output exists; choose an unexecuted configuration with --only")
    load_dotenv()
    for name, method, variant, policy, _ in selected:
        print(f"Starting existing configuration {name}", flush=True)
        await run_benchmark(
            SimpleNamespace(
                method=method,
                prompt_variant=variant,
                citation_policy=policy,
                data=subset,
                split="dev",
                mode="e2e",
                threshold=0.65,
                out=HERE / f"{name}-challenge05.json",
                experiment_note=str(HERE / "PLAN.md"),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
