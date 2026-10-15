"""Generate a complete, offline gold-review document from canonical JSONL."""

import json
import re
from pathlib import Path

from .dataset import load_cases, validate_splits


def fenced(text: str, language: str = "text") -> str:
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{language}\n{text}\n{fence}"


def paragraph(text: str) -> str:
    return re.sub(r"([\\`*_\[\]<>])", r"\\\1", text)


def render_gold_review(directory: Path) -> str:
    summary = validate_splits(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    lines = [
        "# Gold dataset review",
        "",
        "Generated from dev.jsonl, test.jsonl and manifest.json. "
        "Edit those sources, then regenerate.",
        "This document does not approve annotations or freeze the test split.",
        "Review each fact's meaning, qualifiers, verdict, explanation and complete evidence chain.",
        "",
        "| Split | Cases | Gold facts | S / C / U | Review status |",
        "|---|---:|---:|---|---|",
    ]
    for split, info in summary.items():
        labels = info["labels"]
        distribution = " / ".join(
            str(labels.get(label, 0)) for label in ("SUPPORTED", "CONTRADICTED", "UNSUPPORTED")
        )
        lines.append(
            f"| {split} | {info['cases']} | {sum(labels.values())} | {distribution} | "
            f"{paragraph(manifest[split]['review_status'])} |"
        )
    lines += ["", "## Source versions", ""]
    for split, info in summary.items():
        lines.append(f"- {split} canonical dataset hash: `{info['hash']}`")
    lines += ["", "### Full approval manifest", "", fenced(json.dumps(manifest, indent=2), "json")]
    for split in ("dev", "test"):
        lines += ["", f"## {split}"]
        for case in load_cases(directory / f"{split}.jsonl"):
            lines += ["", f"### {case.id}", ""]
            metadata = case.model_dump(
                exclude={"context_passages", "generated_answer", "gold_claims"}
            )
            lines += [fenced(json.dumps(metadata, ensure_ascii=False, indent=2), "json"), ""]
            for index, passage in enumerate(case.context_passages):
                lines += [f"**context_passages[{index}]**", "", fenced(passage), ""]
            lines += ["**generated_answer**", "", fenced(case.generated_answer), ""]
            for claim in case.gold_claims:
                lines += [
                    f"#### {claim.id} — {claim.verdict.value}",
                    "",
                    f"**claim_text:** {paragraph(claim.claim_text)}",
                    "",
                    f"**reasoning:** {paragraph(claim.reasoning)}",
                    "",
                    f"**annotation_reason:** {paragraph(claim.annotation_reason)}",
                    "",
                    "**citations (original indices and verbatim quotes):**",
                    "",
                    fenced(
                        json.dumps(
                            [citation.model_dump() for citation in claim.citations],
                            ensure_ascii=False,
                            indent=2,
                        ),
                        "json",
                    ),
                    "",
                ]
    return "\n".join(lines).rstrip() + "\n"
