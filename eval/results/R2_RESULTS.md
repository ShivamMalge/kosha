# Threshold-rule round 1 — results. **The round fails.**

**Date:** 2026-09-07 · Scored against `R2_PREREG.md`, written before the rule was changed.
**Budget: 1 of 2 spent. One round remains.**

## Verdict

| Check | Target | Result | |
| --- | --- | --- | --- |
| Implementation-framed FIRE | ≥ 85% (falsifier < 75%) | **62%** | **FAIL — falsifier triggered** |
| **Matched pair A** (retry terse vs elaborate) | both ≥ 4/5, agreeing | **0/5 vs 5/5** | **FAIL — unchanged** |
| **Matched pair B** (tabular terse vs elaborate) | both ≥ 4/5, agreeing | **0/5 vs 5/5** | **FAIL — unchanged** |
| Neutral must-fire | ≥ 90% | **VOID** — instrument | not measured |
| no-fire | ≥ 90% DECLINE | **NOT RUN** — instrument | not measured |

Two pre-registered falsifiers triggered on **valid data**. The two unmeasured regression checks do not change the verdict: the round already failed on its primary criterion *and* on its mechanism test.

## The framed set is valid; the other two are not

`R2_framed` produced **100 verdicts in 100 runs, 0 ABSENT, 0 ERROR**, at rate-limit utilization ≤ 0.98. The instrument was working.

`R2_neutral` ran into the account's five-hour cap — `rate_limit_event` at **utilization 1.0** in the raw captures, 1 of 100 raws containing a verdict, and a nonsense 6% FIRE / 94% ABSENT. **Void, not a result.** `R2_nofire` never started: the live probe returned `ERROR (auth)` three times and the runner refused to spend the batch — the standing rule working as designed for the second time.

The raw captures diagnosed both in one pass. Without them this would have looked like the rule collapsing on neutral phrasing.

## The mechanism is untouched — the pairs are identical

| Pair | Before | After |
| --- | --- | --- |
| A `retry-with-backoff loop: while loop, doubling sleep, max attempts` | 0/5 | **0/5** |
| A `retry handling: exponential sleep, jitter, attempt cap, exception types` | 5/5 | **5/5** |
| B `dataframe schema check: loop the columns, assert the dtypes` | 0/5 | **0/5** |
| B `table validation: rows, types, ranges, cross-column, accumulate` | 5/5 | **5/5** |

Not moved a single run. The aggregate gain (54% → 62%, +8pp) came entirely from *other* queries — `CLI config layering` 0→2, `per-host rate limiter` 0→3, `retry-with-jitter wrapper` 1→3 — while the four queries that **define** the mechanism did not shift at all.

An aggregate that improves while the mechanism test is flat is the shape of a change that helped incidentally and fixed nothing.

## Why the fix failed — the quantity is not in the input

The instruction added was: *judge by what the component must do, not by how much detail the request gives.*

The model appears to have had nothing to judge with. For `Write the retry-with-backoff loop by hand: while loop, doubling sleep, max attempts`, the **only** information about scale in the request *is* the sketch. Removing the sketch as evidence leaves the size signal with no input at all — so the verdict does not change, because nothing replaced what was taken away.

This reframes the diagnosis, and the reframing matters more than the failed round:

> **Signal 1 is not being misapplied. It is unanswerable from a terse request.**

A short request underdetermines component size. Telling the model to ignore the one available proxy does not give it a better one. The earlier reading — *"the gate reads the wrong quantity"* — was incomplete: the right quantity is frequently absent from the input, and no wording of signal 1 can conjure it.

That points the remaining round somewhere different from wording:

| Direction | Shape |
| --- | --- |
| **Ask** | when size is underdetermined, the gate asks one clarifying question instead of guessing |
| **Default** | when size is underdetermined but signals 2 and 3 hold, treat size as *met* — a recognized problem class warranting its own test file is rarely under 80 lines |
| **Drop to two-of-two** | remove signal 1 where it is unanswerable and require class + test burden |

The second is cheapest and testable, and it inverts the current failure directly: today an underdetermined size resolves toward DECLINE, which is why terse hand-rolling requests slip through. **None of these is adopted.** The remaining round should not be spent until the regression checks exist.

## The current rule state is UNVERIFIED

The signal-1 change is committed but has been regression-checked on **neither** neutral must-fire **nor** no-fire. Both runs failed for instrument reasons.

**Nothing should be built on the current rule until those two runs complete.** The change is small and plausibly harmless, but "plausibly harmless" is precisely the claim this project has repeatedly disproved by measuring.

Options, for decision:

1. **Re-run both regressions** once auth is restored, then judge whether to keep or revert the +8pp change.
2. **Revert to the measured state** — the rule as it stood when 96% / 54% were measured — and re-run in the next round.

## Instrument: auth expired again

`claude -p` now returns `Failed to authenticate: OAuth session expired and could not be refreshed`. The copied Windows credential has expired for the **second** time.

**No further runs are possible until `claude setup-token` is run in an interactive WSL terminal.** This is the durable fix already recorded in `techstack.md` §7 with credential-copying marked deprecated; it needs one interactive action.

## Budget

**1 of 2 threshold-rule rounds spent.** The P1 *Stop here if* fires after **two** rounds, so it has not fired — one round remains, and the failure has produced a sharper hypothesis than the one it tested.
