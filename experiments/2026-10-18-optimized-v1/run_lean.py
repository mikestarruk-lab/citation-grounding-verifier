"""Final predeclared lean development ablation, serial and budgeted."""

import argparse
import asyncio
from pathlib import Path
from types import SimpleNamespace

from dotenv import load_dotenv
from run_v2 import CHALLENGES, DIRECTORY, prepare_focus

from grounding_verifier.cli import run_benchmark, write_json
from grounding_verifier.dataset import load_cases


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["challenges", "original", "repeat", "dev08"])
    args = parser.parse_args()
    dev08 = DIRECTORY / "dev08-input"
    dev08.mkdir(parents=True, exist_ok=True)
    case = next(c for c in load_cases(Path("data/dev.jsonl")) if c.id == "dev-08")
    content = case.model_dump_json() + "\n"
    path = dev08 / "dev.jsonl"
    if path.exists() and path.read_text(encoding="utf-8") != content:
        raise ValueError("dev-08 input changed")
    if not path.exists():
        path.write_text(content, encoding="utf-8")
        write_json(
            dev08 / "manifest.json",
            {
                "dev": {"review_status": "approved", "reviewed_by": "Original dev gold approval"},
                "note": "Explicit dev-08 stability subset, not extra independent data.",
            },
        )
    specs = [
        ("challenges", CHALLENGES, "optimized-lean-challenges.json"),
        ("original", Path("data"), "optimized-lean-original-dev.json"),
        ("repeat", prepare_focus(), "optimized-lean-focused-repeat.json"),
        ("dev08", dev08, "optimized-lean-dev08-repeat.json"),
    ]
    specs = [s for s in specs if not args.only or s[0] == args.only]
    if any((DIRECTORY / s[2]).exists() for s in specs):
        raise ValueError("selected output exists; choose a missing phase")
    load_dotenv()
    for phase, data, filename in specs:
        print(f"Starting lean/{phase}", flush=True)
        await run_benchmark(
            SimpleNamespace(
                method="optimized",
                prompt_variant="lean-v1",
                citation_policy="passage",
                data=data,
                split="dev",
                mode="e2e",
                threshold=0.65,
                out=DIRECTORY / filename,
                experiment_note=str(DIRECTORY / "LEAN-HYPOTHESIS.md"),
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
