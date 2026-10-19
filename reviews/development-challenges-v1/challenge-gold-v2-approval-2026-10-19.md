# Development challenges v2: gold and alignment approval

- Reviewer: Michael (personal GitHub account: mikestarruk-lab).
- Date: 2026-10-19, Europe/London.
- Confirmation provenance: after a summary of the three open items, the project
  owner wrote in this chat **“确认：挑战集 gold v2、对齐稿 rev2、部分关系单元按误报计，都按原样采纳。写批准记录并关闭 MIC-108。”**

## Scope

1. **Challenge gold v2.** `data/development-challenges-v2/dev.jsonl`: 5 cases,
   12 facts (7 SUPPORTED, 2 CONTRADICTED, 3 UNSUPPORTED), canonical hash
   `c0a11c4a6c7eb11c5f8f18229cbb323d00e61d8c8f5e97c12772bca4979ad504`.
   This includes the four clarifications accepted on 2026-10-18
   ([decision](clarification-decision.json)) and the eight facts the AI
   rereview recommended unchanged. Full text:
   [clarified-gold-v2.zh-CN.md](clarified-gold-v2.zh-CN.md)
   (git blob SHA-256 `e560d59b…`).
2. **Alignment draft rev2.** All 25 challenge outputs of the first optimization
   cycle, 64 scoring units (59 matched, 5 unmatched, 1 missing gold):
   `experiments/2026-10-18-challenges-v2/ai-alignment-2026-10-19.rev2.json`
   (git blob SHA-256 `02f4aa92…`), adopted as written. The file keeps its
   original `ai_proposed` status; this record is the owner approval.
3. **Scoring rule.** References resolve to entities only; content needed to match
   gold and independently necessary premises must come from the prediction's own
   text and citations. A partial-relation unit (for example a same-transaction
   relation without “committed”) counts as a false positive. This is the rule
   already applied in the stability repeats
   (`experiments/2026-10-19-stability/alignment-decisions.json`, blob SHA-256
   `dcac19d5…`) and the final test alignment, so no score changes.

## Limits

This is owner approval after AI review, not independent blind annotation. The
challenge set remains development data: it informed method selection and is
never part of the final test score. The stability-repeat scores were computed
under this rule but are not separately owner-reviewed unit by unit. Any change
to the challenge data invalidates this hash-bound approval.
