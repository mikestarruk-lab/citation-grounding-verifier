"""Serial stability repeats for three optimized candidates (see PLAN.md)."""

import argparse
import asyncio
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv

from grounding_verifier.cli import run_benchmark

DIRECTORY = Path("experiments/2026-10-19-stability")
CANDIDATES = {
    "refined-v1": ("refined-v1", "span"),
    "refined-v2": ("refined-v2", "span"),
    "lean": ("lean-v1", "passage"),
}
DATASETS = {"dev": Path("data"), "challenges": Path("data/development-challenges-v2")}
REPEATS = (1, 2, 3)


def planned():
    for repeat in REPEATS:
        for name in CANDIDATES:
            for dataset in DATASETS:
                yield repeat, name, dataset, DIRECTORY / f"{name}-{dataset}-r{repeat}.json"


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="skip outputs that already exist")
    args = parser.parse_args()
    runs = list(planned())
    if not args.resume and any(path.exists() for *_, path in runs):
        raise ValueError("outputs exist; use --resume to run only missing phases")
    load_dotenv()
    for repeat, name, dataset, path in runs:
        if path.exists():
            continue
        variant, policy = CANDIDATES[name]
        print(f"Starting {name}/{dataset}/r{repeat}", flush=True)
        await run_benchmark(
            SimpleNamespace(
                method="optimized",
                prompt_variant=variant,
                citation_policy=policy,
                data=DATASETS[dataset],
                split="dev",
                mode="e2e",
                threshold=0.65,
                out=path,
                experiment_note=str(DIRECTORY / "PLAN.md"),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
