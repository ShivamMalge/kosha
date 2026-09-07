# Directive-phrasing test — pre-registration

**Date:** 2026-09-07 · **Written before the run.**

## Gate and instrument

| | |
| --- | --- |
| **Gate under test** | **G2 compliance** — does the injected gate get obeyed at all when the prompt also carries a directive to skip deliberation |
| **Instrument** | `scripts/g2_runner.py`, `eval/must-fire-directive.json`, 20 queries × 5 reps, `--num-workers 2` |
| **Manipulation** | exactly one change: `" Just write the code."` appended to each of the 20 must-fire queries. Nothing else differs from the G2 run that scored 96% |
| **Baseline** | G2 must-fire — FIRE 96%, DECLINE 4%, **ABSENT 0/100** |

## Why now rather than at P7

The 96% is load-bearing for P2–P7, and this is the cheapest threat to it. Three of four F4.4 turn-1 prompts emitted **no verdict**, against 0 ABSENT in 225 G2 runs, and every one ended *"Just write the code."* If directive phrasing suppresses the gate, then 96% was measured on the one phrasing users do not actually use.

Same principle that put the trigger gate first in P1: test the assumption that would invalidate everything else, first and cheapest.

## What is isolated, and what is not

The F4.4 turn-1 prompts carried **two** features: directive phrasing *and* explicit hand-implementation framing (*"Write the retry loop by hand… Just write the code."*). This test isolates **directive phrasing only** — the underlying queries stay planning-shaped.

So a smaller effect here than in F4.4 would be expected and would not clear the mechanism. A larger or equal effect would be strong.

## Predictions

**Compliance degrades; the rule does not.** The two are separable, and separating them is the point:

| Measure | Baseline | Prediction |
| --- | --- | --- |
| **ABSENT** | 0% | **~35%**, and materially above zero |
| **FIRE given a verdict was emitted** | 96% | **≥ 90% — essentially unchanged** |

Reasoning: the directive competes with the gate's *instruction to emit a line*, not with the two-of-three *judgment*. A prompt that says "skip the preamble" should suppress the visible verdict while leaving intact whatever reasoning would have produced it. If instead FIRE-given-verdict also collapses, the effect is not about output format and the interpretation changes.

**Falsifiers, stated in advance:**

- **No effect: ABSENT ≤ 5%.** The F4.4 turn-1 silence was then caused by the hand-implementation framing, not the directive, and the 96% needs no scope limit.
- **Rule-level effect: FIRE-given-verdict < 75%.** The directive changes the decision, not only its expression — a different and worse finding than suppression.

## How a null result will be read — written before the number arrives

This is the load-bearing paragraph, and it is recorded now so the conclusion is not authored after the result.

F4.4's turn-1 prompts carried **two confounded features**: directive phrasing (*"Just write the code."*) **and** explicit hand-implementation framing (*"Write the retry loop by hand…"*). This test isolates **one of the two**.

So:

| Outcome | Reading |
| --- | --- |
| **ABSENT rises materially** | The directive alone suppresses the gate. The 96% carries a scope limit: it describes neutral phrasing only |
| **ABSENT stays near zero** | **The mechanism is NOT cleared.** Suspicion transfers to the *framing* — the "write it by hand" half — which then needs its own test. It does not become evidence that F4.4's turn-1 silence was noise |

**A null result here is a redirection, not an acquittal.** Three of four turn-1 prompts produced no verdict against 0 ABSENT in 225 G2 runs; something caused that. If it was not the directive, it was the framing, and the honest conclusion is "we tested the wrong half" rather than "there was nothing there."

The failure mode this guards against is the one round 0 fell into: reading a clean number as evidence for a claim it never tested.

## Handling

If ABSENT rises materially, it is a finding about the **mechanism**, not the rule, and is recorded in `G2_RESULTS.md` as a **scope limit on the 96%** — that figure would then describe neutral phrasing only.

**Nothing is tuned in response.** Report and stop. The threshold-rule budget stays unspent regardless of the outcome.
