# P1 round 0 — A1 / A2 results

**Date:** 2026-09-06 · **Instrument:** `run_eval.py`, WSL Ubuntu, `--num-workers 2`
**Validity:** VALID. Detector confirmed in both directions before the batch (real description → 0/1; universal description → 1/1, 0 failures).

## Headline

| Pass | Threshold | Result | Subprocess failures | Queries firing ≥1 |
| --- | --- | --- | --- | --- |
| A1 no-fire (22 q × 5) | 0.01 | **22/22 pass** | **0 / 110** | 0 |
| A2 must-fire (20 q × 5) | 0.99 | **0/20 pass** | **0 / 100** | 4 |

**Subprocess error count is zero on both passes.** Not low — zero, across 210 calls. No late clustering is possible because there are no errors to cluster; the credentials copied from the Windows side survived the full batch without going stale.

## A2 — the informative pass

Overall fire rate **6/100 runs (6%)**. Four queries fired at all: 2/5, 2/5, 1/5, 1/5.

### By register

| Register | Fires / runs | Rate |
| --- | --- | --- |
| terse | 0 / 30 | **0%** |
| plain | 1 / 30 | 3% |
| **embedded** | **5 / 30** | **17%** |
| variant | 0 / 10 | 0% |

### By domain

| Domain | Fires / runs | Rate |
| --- | --- | --- |
| T1 retry/backoff | 2 / 20 | 10% |
| T2 CLI + layered config | 2 / 15 | 13% |
| T3 tabular validation | **0 / 20** | **0%** |
| T4 HTTP + rate limiting | 1 / 15 | 7% |
| T5 Rust async retry | 1 / 15 | 7% |
| T6 Rust CSV → typed | **0 / 15** | **0%** |

The register gradient is the finding. Every fire but one came from the **embedded** register — the long, explicitly plan-framed queries. Terse never fired once in 30 runs. The description leads with *"during PLANNING only"* and *"when a plan step proposes building something substantial"*, and a terse query does not look like a plan step, so it never loads the skill.

T3 and T6 are dead across every register.

## Per-gate attribution

| Observation | Gate | Reading |
| --- | --- | --- |
| All 20 A2 failures | **G1 (load)** | The skill did not load. Nothing was decided by the two-of-three rule, so this is evidence about **description scope**, not the rule. |
| All 22 A1 passes | **G1 (load)** | Correct declines at the load gate. |
| **G2 (proceed)** | — | **Untested.** In 94 of 100 A2 runs the body was never read. `run_eval` cannot see G2 at all. |

**Zero A1/A2 evidence bears on the two-of-three rule.** Per `phases.md` P1, no part of this result may consume a threshold-rule tuning round.

## A1 status: RESOLVED, but weak

A2 fired somewhere (4 queries, 6 runs), so the description **can** load the skill, the asymmetry behind A1 is restored, and A1's 22/22 is no longer confounded with an invisible skill. `A1_STATUS.md`'s resolution condition is met.

It is nonetheless **weak evidence**. A description that loads on only 6% of queries it was written to catch will decline trivia almost unconditionally — A1 is passing partly on narrowness rather than on discrimination. The four weighted queries (`we already use tenacity…`, `add a --verbose flag…`) held at 0/5, but they were never in danger from a description this narrow.

**A1 must be re-run after any description change.** Its current numbers do not carry forward: widening the description to fix A2 is precisely the change that could break A1, and re-running it is the only way to know.

## Pre-registered prediction: **WRONG IN SIGN**

`SKILL.md` §2 recorded, before any valid run:

> Two-of-three fires more readily than two-of-four. **Over-firing is the predicted failure direction**, and it should surface in the four weighted queries in `no-fire.json`.

**Observed: the opposite.** No over-firing anywhere — the four weighted queries returned 0/5, and the system under-fired so severely that 94% of must-fire runs never loaded the skill.

Recorded as a **failed prediction**, not reframed. Two honest qualifications, neither of which rescues it:

1. The prediction concerned **G2**, and the failure occurred at **G1**. The reasoning about two-of-three versus two-of-four remains untested — it was never reached.
2. The prediction was nonetheless stated as an expectation about *this run's observable*, and that observable came back inverted. A prediction whose mechanism was never exercised is not a prediction that was right.

The lesson is about the prediction's *scope*, not its logic: it forecast the behaviour of a gate that the chosen instrument cannot see. Future pre-registrations should name the gate and the instrument that would falsify them.

## What round 0 establishes

- The instrument is sound and validated in both directions.
- The **description is too narrow** — it loads on plan-framed prose and almost nothing else.
- The **two-of-three rule is entirely untested.**
- P1's *Stop here if* is untouched: **zero threshold-rule rounds consumed.**

Next work, if authorized, is **description scope only** — the G1 budget — and A1 is re-run alongside A2 afterward. The sealed holdout stays sealed: it tests the rule, not the description.
