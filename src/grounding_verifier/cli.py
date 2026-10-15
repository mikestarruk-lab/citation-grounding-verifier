import argparse
import asyncio
import importlib.metadata
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from .baseline import LexicalVerifier
from .dataset import dataset_hash, digest, load_cases, require_frozen_test, validate_splits
from .domain import VerifyError
from .evaluation import output_hash, review_template, score
from .llm import MODEL, AnthropicProvider, LLMVerifier, execute
from .prompts import MINIMAL, REFINED


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Refuse accidental replacement of experimental evidence.
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


async def run_benchmark(args):
    if args.out.exists():
        raise ValueError("output already exists; select a new run path")
    cases = load_cases(args.data / f"{args.split}.jsonl")
    if args.split == "test":
        require_frozen_test(args.data, cases)
    if args.method == "optimized" and not args.experiment_note:
        raise ValueError(
            "optimized is a candidate: provide --experiment-note documenting dev failures"
        )
    provider = None
    if args.method == "lexical":
        verifier = LexicalVerifier(args.threshold)
    else:
        provider = AnthropicProvider()
        verifier = LLMVerifier(provider, optimized=args.method == "optimized")
    try:
        git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        run = {
            "format_version": 1,
            "created_at": datetime.now(UTC).isoformat(),
            "method": args.method,
            "mode": args.mode,
            "split": args.split,
            "dataset_hash": dataset_hash(cases),
            "gold_status": read_json(args.data / "manifest.json"),
            "model": MODEL if provider else None,
            "effort": "medium" if provider else None,
            "threshold": args.threshold if args.method == "lexical" else None,
            "prompt": (REFINED if args.method == "optimized" else MINIMAL) if provider else None,
            "experiment_note": args.experiment_note,
            "git_commit": git.stdout.strip() if git.returncode == 0 else None,
            "working_tree_dirty": bool(status.stdout),
            "source_hash": digest(
                {str(p): p.read_text(encoding="utf-8") for p in sorted(Path("src").rglob("*.py"))}
            ),
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ("anthropic", "fastapi", "pydantic")
            },
            "lock_hash": digest(Path("uv.lock").read_text(encoding="utf-8")),
            "records": [],
        }
        for case in cases:
            trace = {}
            record = {"case_id": case.id, "trace": trace}
            try:
                fixed = [g.claim_text for g in case.gold_claims] if args.mode == "gold" else None
                report = await execute(verifier, case.request(), trace, fixed)
                record.update(status="ok", output=report.model_dump(mode="json"))
            except VerifyError as exc:
                record.update(
                    status="error",
                    output=None,
                    error={"code": exc.code, "status": exc.status, "message": str(exc)},
                )
            record["output_hash"] = output_hash(record)
            run["records"].append(record)
            print(f"{case.id}: {record['status']}")
            # Crash recovery journal includes every completed attempt. It is not a complete run.
            journal = args.out.with_suffix(".partial.json")
            journal.parent.mkdir(parents=True, exist_ok=True)
            temporary = journal.with_suffix(".tmp")
            temporary.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
            os.replace(temporary, journal)
        write_json(args.out, run)
        summary = score(run, cases)
        summary["gold_review_status"] = run["gold_status"][args.split]["review_status"]
        write_json(args.out.with_suffix(".summary.json"), summary)
        print(json.dumps(summary, indent=2))
    finally:
        if provider:
            await provider.close()


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Auditable grounding verification experiments")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-data")
    validate.add_argument("--data", type=Path, default=Path("data"))
    run = commands.add_parser("run")
    run.add_argument("--method", choices=["lexical", "minimal", "optimized"], required=True)
    run.add_argument("--mode", choices=["e2e", "gold"], default="e2e")
    run.add_argument("--split", choices=["dev", "test"], default="dev")
    run.add_argument("--data", type=Path, default=Path("data"))
    run.add_argument("--threshold", type=float, default=0.65)
    run.add_argument("--experiment-note")
    run.add_argument("--out", type=Path, required=True)
    review = commands.add_parser("review-template")
    review.add_argument("--run", type=Path, required=True)
    review.add_argument("--data", type=Path, default=Path("data"))
    review.add_argument("--out", type=Path, required=True)
    scoring = commands.add_parser("score")
    scoring.add_argument("--run", type=Path, required=True)
    scoring.add_argument("--reviews", type=Path)
    scoring.add_argument("--data", type=Path, default=Path("data"))
    scoring.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "validate-data":
            print(json.dumps(validate_splits(args.data), indent=2))
        elif args.command == "run":
            asyncio.run(run_benchmark(args))
        else:
            run_data = read_json(args.run)
            cases = load_cases(args.data / f"{run_data['split']}.jsonl")
            if run_data["dataset_hash"] != dataset_hash(cases):
                raise ValueError("dataset changed since this run")
            if args.command == "review-template":
                if run_data["mode"] != "e2e":
                    raise ValueError("fixed-claim diagnostics do not require extraction reviews")
                write_json(args.out, review_template(run_data, {c.id: c for c in cases}))
            else:
                result = score(run_data, cases, read_json(args.reviews) if args.reviews else None)
                result["replayed"] = True
                result["latency_note"] = "Recorded live latency; replay performs no model calls."
                if args.out:
                    write_json(args.out, result)
                print(json.dumps(result, indent=2))
    except (ValueError, VerifyError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
