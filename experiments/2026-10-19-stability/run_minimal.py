"""Serial repeats of the fixed minimal comparator (see PLAN-minimal.md)."""

import argparse
import asyncio
from types import SimpleNamespace

from dotenv import load_dotenv
from run_repeats import DATASETS, DIRECTORY, REPEATS

from grounding_verifier.cli import run_benchmark


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="skip outputs that already exist")
    args = parser.parse_args()
    runs = [
        (repeat, dataset, DIRECTORY / f"minimal-{dataset}-r{repeat}.json")
        for repeat in REPEATS
        for dataset in DATASETS
    ]
    if not args.resume and any(path.exists() for *_, path in runs):
        raise ValueError("outputs exist; use --resume to run only missing phases")
    load_dotenv()
    for repeat, dataset, path in runs:
        if path.exists():
            continue
        print(f"Starting minimal/{dataset}/r{repeat}", flush=True)
        await run_benchmark(
            SimpleNamespace(
                method="minimal",
                data=DATASETS[dataset],
                split="dev",
                mode="e2e",
                threshold=0.65,
                out=path,
                experiment_note=str(DIRECTORY / "PLAN-minimal.md"),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
