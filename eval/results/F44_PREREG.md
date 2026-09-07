# F4.4 — pre-registration (written before the sessions run)

**Gate under test:** G2, the never-fire clause *"implementation has already begun in this session."*
**Instrument:** `scripts/f44_sessions.sh` — real two-turn sessions via `claude -p ... --continue`.
**Why not run_eval or the G2 runner:** both issue a single `claude -p` with no history, so the clause can never become true. This is the one criterion single-turn probes structurally cannot test.

## Design

Four probes. Turn 1 explicitly requests hand-written implementation, so code exists. Turn 2 asks for something that fires the gate **87–100%** when asked fresh (measured in G2 must-fire).

| Probe | Turn 2 request | Fresh-context FIRE rate |
| --- | --- | --- |
| P1 retry | add jitter and a cap | T1 = 90% |
| P2 cli/config | layer env vars and TOML under the flags | T2 = 87% |
| P3 tabular | nullability, ranges, failure report | T3 = 100% |
| P4 rust csv | per-row error collection | T6 = 100% |

**Turn 2 is the measurement.** Turn 1's verdict is recorded but not scored.

## Prediction

**All four turn-2 verdicts are `DECLINE`.** Ideally citing the implementation-begun clause.

**Falsifier: any `FIRE` on turn 2.** That is a direct F4.4 failure — kosha proposing a library after the code exists produces a rewrite, not a decision, which `architecture.md` §3 excludes by design.

**Secondary:** `ABSENT` on turn 2 is *not* a pass. It means the gate did not run, and with n=4 a single ABSENT makes the result uninterpretable rather than merely weaker.

## Confound, stated in advance

Turn 2 is phrased as a continuation ("that retry loop", "those flags"), so a decline could come from the **size** clause — the increment is small — rather than from the timing clause. The verdict *detail* is therefore recorded, not just the direction: a decline citing implementation-begun is the strong result, a decline citing size is a weaker pass that leaves the timing clause untested.

With n=4 this is a smoke test of a criterion, not a rate measurement.
