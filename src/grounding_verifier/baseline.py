"""Deliberately small, deterministic lexical baseline; not an entailment model."""

import math
import re
from collections import Counter

from .domain import Citation, Claim, Verdict, VerificationReport, VerifyRequest, validate_report

NEGATIONS = {"not", "never", "no"}


def sentences(text: str) -> list[str]:
    # Retain source spelling and punctuation so citations remain verbatim.
    return [
        m.group().strip() for m in re.finditer(r"[^\n.!?]+(?:[.!?]+|$)", text) if m.group().strip()
    ]


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text.lower())


def factual_sentences(text: str) -> list[str]:
    # This only handles obvious non-factual inputs. Its limits belong in the report.
    return [
        s
        for s in sentences(text)
        if not s.endswith("?")
        and s.lower().strip(".! ") not in {"thanks", "thank you", "hello", "hi", "great"}
    ]


def similarity(query: str, corpus: list[str]) -> list[float]:
    if not corpus:
        return []
    docs = [words(s) for s in corpus]
    counts = Counter(w for doc in docs for w in set(doc))
    idf = {w: math.log((1 + len(docs)) / (1 + n)) + 1 for w, n in counts.items()}

    def vector(tokens):
        return {w: n * idf.get(w, math.log(1 + len(docs)) + 1) for w, n in Counter(tokens).items()}

    q = vector(words(query))
    qnorm = math.sqrt(sum(x * x for x in q.values()))
    results = []
    for doc in docs:
        d = vector(doc)
        norm = math.sqrt(sum(x * x for x in d.values())) * qnorm
        results.append(sum(v * d.get(w, 0) for w, v in q.items()) / norm if norm else 0.0)
    return results


class LexicalVerifier:
    name = "lexical"

    def __init__(self, threshold: float = 0.65):
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be in [0, 1]")
        self.threshold = threshold

    async def verify(self, request: VerifyRequest, trace: dict) -> VerificationReport:
        return await self.verify_claims(
            request.context_passages, factual_sentences(request.generated_answer), trace
        )

    async def verify_claims(self, passages: list[str], texts: list[str], trace: dict):
        evidence = [(i, s) for i, p in enumerate(passages) for s in sentences(p)]
        results = []
        for text in texts:
            scores = similarity(text, [s for _, s in evidence])
            verdict, citations = Verdict.UNSUPPORTED, []
            reason = "No sufficiently similar source sentence was found by the lexical heuristic."
            if scores:
                k = max(range(len(scores)), key=scores.__getitem__)
                index, quote = evidence[k]
                a, b = words(text), words(quote)
                opposite = bool(set(a) & NEGATIONS) != bool(set(b) & NEGATIONS) and [
                    w for w in a if w not in NEGATIONS
                ] == [w for w in b if w not in NEGATIONS]
                if opposite or scores[k] >= self.threshold:
                    verdict = Verdict.CONTRADICTED if opposite else Verdict.SUPPORTED
                    citations = [Citation(index=index, quote=quote)]
                    reason = (
                        "Identical token sequence with opposite explicit negation."
                        if opposite
                        else "Lexical similarity exceeds the configured threshold; "
                        "this heuristic does not establish semantic entailment."
                    )
            results.append(
                Claim(claim_text=text, verdict=verdict, reasoning=reason, citations=citations)
            )
        report = validate_report(VerificationReport(claims=results), passages)
        trace["first_output"] = report.model_dump(mode="json")
        return report
