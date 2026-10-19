# Complete cited-passage experiment

Recorded after the saved refined-v2 runs and focused repeats, before passage-policy
calls. The second prompt consistently quotes region uniqueness/distinctness but
still omits single-host exclusivity in challenge-02. Prompting alone has not
closed this evidence gap. No owner-reviewed quality improvement is claimed.

Test a deterministic policy: validate the original report first, then replace
each legal quote with the exact full passage at its existing index. Deduplicate
repeated indices per claim, preserve claims/verdicts/reasoning, and keep U quotes
empty. This never adds another passage or normalizes text. Invalid original
quotes/indices still fail or invoke the existing bounded repair; expansion must
not hide them. Save both the raw first output and the expanded final output.

The hypothesis is limited: if a necessary premise is present in an already cited
passage, expansion includes it. It does not establish semantic sufficiency,
correct source selection, all necessary passage indices, or verdict correctness.
Costs include larger responses, distracting text and poorer citation precision.
Measure quote characters as well as legality and actual model cost/latency.
This does not apply to the fixed minimal baseline.

Use refined-v2 with passage expansion on all five challenges and eight original
dev cases; repeat the two focused diagnostics once. Compare with the saved span
versions. These are live calls through the complete new path, not replayed model
outputs represented as new API calls. Existing source inputs and draft-gold status
remain unchanged. Do not promote a winner without the remaining review/validation.
