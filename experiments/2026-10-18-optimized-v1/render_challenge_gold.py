"""Render draft challenge gold without showing model predictions."""

import argparse
from pathlib import Path

from grounding_verifier.dataset import dataset_hash, load_cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "experiments/2026-10-18-optimized-v1/challenge-gold-review.md",
        ),
    )
    args = parser.parse_args()
    cases = load_cases(Path("data/development-challenges-v1/dev.jsonl"))
    parts = [
        "# Draft challenge gold review",
        "",
        "Five development cases / twelve proposed facts. AI-authored, not owner-approved.",
        "Review meaning, atomicity, qualifiers, label, explanation and complete evidence.",
        "No predictions appear here. Approving gold does not approve model outputs.",
        f"Dataset hash: `{dataset_hash(cases)}`.",
        "",
    ]
    for case in cases:
        parts += [
            f"## {case.id}",
            "",
            f"Source group: `{case.source_group}`. Category: `{case.category}`.",
            "",
            case.provenance,
            "",
        ]
        for i, passage in enumerate(case.context_passages):
            parts += [f"### Passage [{i}]", "", "```text", passage, "```", ""]
        parts += ["### Generated answer", "", "```text", case.generated_answer, "```", ""]
        for claim in case.gold_claims:
            parts += [
                f"### {claim.id} · {claim.verdict.value}",
                "",
                claim.claim_text,
                "",
                f"Reasoning: {claim.reasoning}",
                "",
                f"Annotation reason: {claim.annotation_reason}",
                "",
            ]
            if not claim.citations:
                parts += ["Citations: `[]`.", ""]
            for citation in claim.citations:
                parts += [f"Citation [{citation.index}]:", "", "```text", citation.quote, "```", ""]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as output:
        output.write("\n".join(parts))
    print(f"Saved draft-only review: {args.out}")


if __name__ == "__main__":
    main()
