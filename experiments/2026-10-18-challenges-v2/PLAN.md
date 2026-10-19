# Challenge v2 input migration, not another optimization round

Before new calls: rerun only challenge-05 for the five configurations already
tested in the first cycle: minimal/span, refined-v1/span, refined-v2/span,
refined-v2/passage, lean-v1/passage. Use the existing model, medium effort,
schema, budget ledger, retry limits and serial runner. No prompt edits or new
variants. Save five new one-case runs, preserving all v1 evidence.

The new source explicitly places success reporting after transaction commit.
The answer describes the already completed status/deletion actions in the same
committed transaction. This is a changed input, not evidence that a prompt
improved. Its three gold units score status, deletion and transaction relation.

Validate exact request equality before exposing v1 outputs for challenge-01/02/
03/04 against v2 gold. challenge-02 changes reasoning, not its model request.
Export a provenance-bound review bundle: twenty reused records and five new
records. Each record retains its original run hash, input hash, output hash,
configuration and recorded timing/usage. Never present reused records as newly
executed requests or cache replay time as live latency. No inherited approvals.

The owner accepted four clarification proposals. The complete v2 wording and
remaining gold are still draft; semantic alignment/evidence review is pending.
No complete new semantic score, candidate promotion, final-test inference or
additional optimization iterations are authorized by this migration plan.
