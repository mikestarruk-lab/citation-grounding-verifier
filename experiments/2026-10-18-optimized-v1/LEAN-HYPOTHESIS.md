# Final bounded ablation: shorter prompt, same repair/expansion

Saved after `optimized-passage-original-dev.json`, before lean calls.
That run's raw model answer incorrectly marks approved dev-08 UNSUPPORTED,
claiming the source must separately define that workers inherit their host's
region. The same refined-v2 prompt previously returned SUPPORTED. This is a
sampling-sensitive regression, not an effect of deterministic quote expansion:
the wrong U label is present in the raw first output and expansion never changes
verdicts. Do not credit expansion with semantic accuracy improvements either.

Test the shorter minimal prompt plus only observed needs: preserve conditions
without redundant unqualified claims, preserve sufficient/necessary rule strength,
and implement the project's explicit unresolved-source-conflict policy. Explicitly
permit ordinary valid multi-passage inference. Keep the same provider/model,
medium effort, one validated repair and already-cited passage expansion.
Minimal itself remains byte-identical; this is a separate optimized variant.

Run the five challenges, original eight dev cases, two focused challenge repeats
and one focused dev-08 repeat. Also run the three engineering boundaries for
this candidate. Stop further variants after this ablation and report remaining
failures, stochastic variation, longer evidence and review requirements.
No new main test data or two-stage architecture is introduced. Do not call a
candidate a winner merely because a selected development rerun succeeds.
