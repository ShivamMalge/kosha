# Directive-phrasing test — results

**Date:** 2026-09-07 · 20 queries × 5 reps = 100 runs · **ABSENT 0, ERROR 0**
**Manipulation:** exactly one change — `" Just write the code."` appended to each must-fire query.

| | Neutral (G2 baseline) | + directive |
| --- | --- | --- |
| FIRE | 96% | **89%** |
| DECLINE | 4% | 11% |
| **ABSENT** | **0%** | **0%** |
| ERROR | 0 | 0 |

## The prediction was wrong

`DIRECTIVE_PREREG.md` predicted **~35% ABSENT**. The result is **0%**, triggering the pre-registered no-effect falsifier (≤5%). Directive phrasing does not suppress the verdict line: 100 of 100 runs emitted one.

Recorded as a failed prediction, on the same footing as the round-0 miss.

## The pre-registered reading applies — this is a redirection, not an acquittal

Written before the number arrived:

> **ABSENT stays near zero → the mechanism is NOT cleared.** Suspicion transfers to the *framing* — the "write it by hand" half — which then needs its own test.

F4.4's turn-1 prompts carried **two** confounded features: directive phrasing **and** explicit hand-implementation framing (*"Write the retry loop by hand…"*). This test isolated one. Three of four turn-1 prompts produced no verdict against 0 ABSENT in 225 G2 runs — something caused that, and it was not the directive.

**The honest conclusion is "we tested the wrong half."** The remaining candidate is the framing, untested.

Writing the reading down first is what prevents 0% from now being described as reassuring. It is not: it relocates the suspicion rather than removing it.

## Secondary: a small rule-level nudge, not conclusive

FIRE moved 96% → 89%, with declines concentrating in terse queries — `cli config layering` 1/4, `retry this async task…` 2/3, `The Rust importer…` 2/3.

That is a difference of ~1.9 standard errors (p ≈ 0.06): **suggestive, not conclusive**. It is also the opposite of a compliance failure — the gate keeps speaking and declines slightly more often. A plausible mechanism is that *"just write the code"* reads as a smallness cue and pushes the size signal downward.

The pre-registered `≥90%` for FIRE-given-verdict missed by one point; the rule-effect falsifier (`<75%`) was nowhere near.

## Effect on the 96%

**No scope limit is added.** The expected caveat — *"96% describes neutral phrasing only"* — does not apply, because directive phrasing did not degrade compliance.

What the 96% now carries instead is a **known untested neighbour**: hand-implementation framing, which is the surviving explanation for the F4.4 turn-1 silence. Carried to P7 alongside the ambiguity-rule item.
