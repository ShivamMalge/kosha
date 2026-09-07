# Timeout check — was the G1 record deflated by silent timeouts?

**Date:** 2026-09-07 · **Scope:** must-fire only, 20 queries × 5 reps, `run_eval.py --timeout 120`
**Baseline:** round 1, identical description, no CLAUDE.md directive, `--timeout 30` (default)

## The question

`run_eval.py` does not redirect stdin, sets `stderr=subprocess.DEVNULL`, defaults to a 30-second timeout, and scores a timeout as a **silent non-trigger** — no error, no warning. Its error count sees one failure class out of five (`techstack.md` §6b clause 4).

So the G1 figures that motivated the move to deterministic invocation were produced by an instrument with a known silent-failure mode. The question was never whether the *decision* was right, but whether the *record* was sound.

## Why must-fire only

`run_eval` streams and detects triggers early, so a call that **does** trigger finishes fast and the ~3-second stdin penalty never binds. A call that does not trigger runs long and may reach 30s — but a timeout there is scored as a non-trigger, which is the verdict it would have received anyway.

The only mis-scored case is a call that **would have triggered late**, past roughly 27 seconds. That case lives almost entirely in must-fire. Re-running no-fire would spend 110 calls confirming a number that structurally cannot move much.

## Result: **no material change. The record stands.**

| | round 1 (t=30) | t=120 | delta |
| --- | --- | --- | --- |
| **Overall** | 29/100 (29%) | **30/100 (30%)** | **+1pp** |

Subprocess failures: **0**.

### By register

| Register | t=30 | t=120 | delta |
| --- | --- | --- | --- |
| terse | 27% | 27% | 0 |
| plain | 25% | 18% | −8pp |
| embedded | 37% | 50% | +13pp |

### By domain

| Domain | t=30 | t=120 | delta |
| --- | --- | --- | --- |
| T1 retry/backoff | 15% | 15% | 0 |
| T2 CLI + config | 13% | 33% | +20pp |
| T3 tabular validation | 30% | 30% | 0 |
| T4 HTTP + rate limiting | 33% | 33% | 0 |
| T5 Rust async retry | 40% | 33% | −7pp |
| T6 Rust CSV → typed | 47% | 40% | −7pp |

## Why this is noise, not a residual artifact

**The deltas go both ways, and that settles it.**

A longer timeout can only ever *add* fires. If timeouts had been mis-scoring late triggers as non-triggers, quadrupling the budget could not have reduced any query's count — every delta would be zero or positive.

Instead five queries went **down** (−2, −2, −1, −1, −1) and four went **up** (+2, +2, +2, +1), summing to +7 and −7 for a net of +1. Negative deltas are causally impossible under the timeout hypothesis, so the movement is run-to-run variance at n=5, which round 1 already documented as large enough that per-query rates are not individually readable.

Nine of twenty queries were completely unchanged.

## Conclusions

1. **The G1 record is sound.** The 29% figure was not deflated by silent timeouts. The stdin defect is real and remains a genuine hazard in the instrument, but it did not materially distort this measurement.
2. **The mechanism decision was never in question, and this does not reopen it.** F4.3 requires effectively 100%. No plausible instrument artifact carries autonomous triggering from 29–47% to there; the gap is roughly seventy points. This settled whether the record was trustworthy, not whether the choice should change.
3. **Clause 4 stands regardless.** The audit that prompted this check was correct on its own terms — `run_eval.py` genuinely cannot see four of five failure classes. It happened not to bite here. That is luck confirmed by measurement rather than a reason to trust the accounting next time.

## What this does not clear

Rounds 0 and 1 remain measured through an instrument that discards stderr and cannot see non-zero exits, timeouts, or auth failures delivered as assistant text. This check tested **one** hypothesis — timeout-induced deflation on must-fire — and refuted it. It does not certify the instrument.
