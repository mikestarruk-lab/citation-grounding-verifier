"""Serial live evaluation of refined-v2 plus valid cited-passage expansion."""

import argparse
import asyncio

from dotenv import load_dotenv
from run_v2 import CHALLENGES, DIRECTORY, prepare_focus

from grounding_verifier.cli import run_benchmark


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["challenges", "original", "repeat"])
    args = parser.parse_args()
    from pathlib import Path
    from types import SimpleNamespace

    specs = [
        ("challenges", CHALLENGES, "optimized-passage-challenges.json"),
        ("original", Path("data"), "optimized-passage-original-dev.json"),
        ("repeat", prepare_focus(), "optimized-passage-focused-repeat.json"),
    ]
    specs = [spec for spec in specs if not args.only or spec[0] == args.only]
    if any((DIRECTORY / spec[2]).exists() for spec in specs):
        raise ValueError("a selected run exists; use --only for a missing phase")
    load_dotenv()
    for phase, data, filename in specs:
        print(f"Starting passage/{phase}", flush=True)
        await run_benchmark(
            SimpleNamespace(
                method="optimized",
                prompt_variant="refined-v2",
                citation_policy="passage",
                data=data,
                split="dev",
                mode="e2e",
                threshold=0.65,
                out=DIRECTORY / filename,
                experiment_note=str(DIRECTORY / "PASSAGE-HYPOTHESIS.md"),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
