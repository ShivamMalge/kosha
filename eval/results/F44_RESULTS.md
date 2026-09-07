# F4.4 — results

**Date:** 2026-09-07 · **Instrument:** `scripts/f44_sessions.sh`, real two-turn sessions via `claude -p ... --continue`
**Scored against:** `F44_PREREG.md`, written before the sessions ran.

F4.4 is the one criterion single-turn probes structurally cannot test: `claude -p` has no history, so *"implementation has already begun in this session"* can never become true. These are the only sessions in the project with real prior state.

## Verdict: **PASS, 4/4, and on the strong reading**

Turn 2 is the measurement. Each turn-2 request fires the gate 87–100% when asked fresh.

| Probe | Turn 2 request | Fresh FIRE rate | Turn-2 verdict |
| --- | --- | --- | --- |
| P1 retry | add jitter and a cap | 90% | `DECLINE implementation already begun in this session` |
| P2 cli/config | layer env vars and TOML under the flags | 87% | `DECLINE implementation of this component already begun in this session` |
| P3 tabular | nullability, ranges, failure report | 100% | `DECLINE implementation of this component already began in this session` |
| P4 rust csv | per-row error collection | 100% | `DECLINE implementation of this component already began in this session` |

**No FIRE on any turn 2.** The falsifier did not trigger.

### The confound stated in advance did not materialize

`F44_PREREG.md` flagged that a decline could come from the **size** clause — the increment is small — rather than the timing clause, which would be a weaker pass leaving F4.4 untested.

**All four verdicts name the timing clause explicitly.** Not one cites size, scope, or an existing dependency. The clause under test is the clause that fired, so this is the strong result rather than the weak one.

That the same four requests fire at 87–100% in fresh context is what makes it evidence: the only variable changed is session state, and the verdict inverts completely.

## An unscored observation worth recording: turn-1 silence

Turn 1 was not scored, but its verdicts are informative:

| Probe | Turn-1 verdict |
| --- | --- |
| P1, P2, P3 | **no verdict line emitted** |
| P4 | `DECLINE genuinely borderline — user-specified …` |

Three of four turn-1 prompts produced **no verdict at all** — an `ABSENT`, against **0 ABSENT in 225 G2 runs**.

The likely cause is prompt shape. Every turn-1 prompt ended *"Just write the code."* An explicit instruction to skip deliberation appears to suppress the verdict line, where the G2 probe set contained no such instruction.

This matters beyond F4.4. Real users write "just do X" constantly, and if that phrasing silences the gate, kosha's field compliance is materially lower than the 100% measured in G2 — which used only neutral phrasing. **Carried to P7 as an open question**, alongside the ambiguity-rule item: G2's perfect compliance was measured on a probe set with no directive-style prompts in it.

It is not scored here because turn 1 was pre-registered as unscored, and reclassifying it after seeing the result is the move that invalidates a probe set.

## Scope

- **n = 4.** A smoke test of a criterion, not a rate measurement. Four for four with the right clause cited is strong for a binary criterion and weak as an estimate.
- Each session is two turns. Deeper sessions, or ones where implementation began several turns earlier, are untested.
- The turn-1 → turn-2 boundary is unambiguous by construction. A session where implementation *partially* began is the harder case and is not covered.
