"""Serial refined-v2 runs and a preregistered focused repeat; no final-test reads."""

import argparse
import asyncio
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv

from grounding_verifier.cli import run_benchmark, write_json
from grounding_verifier.dataset import digest, load_cases

DIRECTORY = Path("experiments/2026-10-18-optimized-v1")
CHALLENGES = Path("data/development-challenges-v1")


def prepare_focus():
    directory = DIRECTORY / "focused-input"
    cases = load_cases(CHALLENGES / "dev.jsonl")
    selected = [c for c in cases if c.id in {"challenge-02", "challenge-03"}]
    if len(selected) != 2:
        raise ValueError("focused repeat needs the two preregistered cases")
    text = "".join(c.model_dump_json() + "\n" for c in selected)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "dev.jsonl"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise ValueError("focused input changed; use a new experiment version")
    if not path.exists():
        path.write_text(text, encoding="utf-8")
        write_json(
            directory / "manifest.json",
            {
                "dev": {"review_status": "draft", "reviewed_by": None},
                "note": "Focused diagnostic repeat, not independent data or main benchmark.",
                "parent_data": str(CHALLENGES / "dev.jsonl"),
                "parent_digest": digest([c.model_dump(mode="json") for c in cases]),
                "case_ids": [c.id for c in selected],
            },
        )
    return directory


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only", choices=["challenges", "original", "minimal-repeat", "v1-repeat", "v2-repeat"]
    )
    args = parser.parse_args()
    focus = prepare_focus()
    specs = [
        ("challenges", "optimized", "refined-v2", CHALLENGES, "optimized-v2-challenges.json"),
        ("original", "optimized", "refined-v2", Path("data"), "optimized-v2-original-dev.json"),
        ("minimal-repeat", "minimal", "refined-v1", focus, "minimal-focused-repeat.json"),
        ("v1-repeat", "optimized", "refined-v1", focus, "optimized-v1-focused-repeat.json"),
        ("v2-repeat", "optimized", "refined-v2", focus, "optimized-v2-focused-repeat.json"),
    ]
    selected = [spec for spec in specs if not args.only or spec[0] == args.only]
    if any((DIRECTORY / spec[4]).exists() for spec in selected):
        raise ValueError("a selected run exists; use --only to run a missing phase")
    load_dotenv()
    for phase, method, variant, data, filename in selected:
        print(f"Starting {phase}", flush=True)
        await run_benchmark(
            SimpleNamespace(
                method=method,
                prompt_variant=variant,
                data=data,
                split="dev",
                mode="e2e",
                threshold=0.65,
                out=DIRECTORY / filename,
                experiment_note=str(DIRECTORY / "V2-HYPOTHESIS.md"),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
