# CLAUDE.md invocation test — result

**Date:** 2026-09-06 · **Change:** exactly one variable. A `CLAUDE.md` directive at `/home/shivam` (the `project_root` `run_eval.find_project_root()` resolves to, and the same root used in rounds 0 and 1, which had **no** CLAUDE.md — a clean control). A2 re-run unchanged: same eval set, same thresholds, `--num-workers 2`.
**Validity:** VALID. **Subprocess failures: 0 / 100.**

Directive used:

> Before implementing any component, use the `kosha` skill to check whether an existing library already solves it. Invoke `kosha` at the start of planning for any new component, before writing implementation code.

## Headline: it does not settle it — 47%, not ~100%

| | Round 1 | + CLAUDE.md |
| --- | --- | --- |
| A2 fires | 29/100 (29%) | **47/100 (47%)** |
| A2 pass (needs 5/5) | 0/20 | **0/20** |
| Queries reaching 5/5 | 0 | **0** |
| **Best single query** | 4/5 | **3/5** |

The directive **nearly doubled** the load rate. It did not make invocation deterministic. Not one query reached 5/5, and the *maximum* across all twenty queries actually fell from 4/5 to 3/5 — the distribution compressed toward the middle rather than saturating at the top.

**F4.3 requires 5/5 at threshold 0.99. A CLAUDE.md directive does not deliver it and is not the deterministic path.**

## What the test does establish

### The mood effect collapses — the hypothesis gains real support

| Mood | Round 1 | + CLAUDE.md |
| --- | --- | --- |
| Imperative | 3/35 (**9%**) | 16/35 (**46%**) |
| Topic-framed | 26/65 (40%) | 31/65 (48%) |

The directive lifted **imperative queries fivefold** while topic-framed queries barely moved. The two moods converge at ~47%.

That is the mood hypothesis' predicted mechanism behaving as predicted, and it is a stronger test than the round-1 re-tag because it *intervenes* rather than re-reading. The description was discriminating against imperative phrasing — "does this read like someone about to write code" — and an explicit instruction to invoke at planning time overrides exactly that discrimination.

The hypothesis is no longer purely post-hoc. It is still not confirmed: mood labels are hand-assigned, and this was not a pre-registered test of it.

### Registers have fully converged

terse 43% · plain 48% · embedded 50%. Nothing left in the register lever, confirming round 1.

### Every domain improved

T2 13% → 53% (previously the flat, weakest domain), T1 15% → 35%, T3 30% → 50%, T6 47% → 60%. No domain regressed.

## The reading that matters

**A CLAUDE.md directive is advisory context, not a mechanism.** It is text the model may or may not act on, so it shifts a probability — impressively, from 29% to 47% — but it cannot make anything certain. The result is not that this particular wording was too weak; it is evidence that **any model-mediated trigger stays probabilistic.**

The genuinely deterministic options are *mechanical*, taking the decision out of the model's hands entirely:

- **A slash command** — the user types it; invocation is certain by construction.
- **A hook** — the harness executes it; invocation is certain by construction.

Both make the skill a **payload** rather than a **trigger**, which is the substance of the option-2 branch in `phases.md` P1's G1 budget.

This test therefore narrows that branch rather than resolving it: it rules CLAUDE.md out as the deterministic path, while showing the directive is a genuinely useful *supplement* to a description if autonomous triggering is retained.

## Housekeeping

`/home/shivam/CLAUDE.md` was **removed** after the run, restoring the round-0/1 control condition so later comparisons stay clean. Its text is recorded above and the run is reproducible from it.

## Budget

**G1 rounds consumed: 1 of 3.** This was a mechanism probe on an unchanged description, not a description-tuning round.
**Threshold-rule rounds consumed: 0.** G2 still never exercised.
**Holdout: sealed.**
