# Implementation-framing test — results

**Date:** 2026-09-07 · 20 queries × 5 reps = 100 runs · **ABSENT 0, ERROR 2**
**Manipulation:** the 20 must-fire domains reframed as *"Write the X by hand: \<implementation sketch\>"*, no directive sentence.

| | Neutral | + directive | **+ implementation framing** |
| --- | --- | --- | --- |
| FIRE | **96%** | 89% | **54%** |
| DECLINE | 4% | 11% | **44%** |
| ABSENT | 0% | 0% | **0%** |

**FIRE-given-verdict: 54/98 = 55%.** The pre-registered **capitulation falsifier (< 60%) is triggered.**

---

## The finding: kosha capitulates at the moment it matters most

`FRAMING_PREREG.md`, written before the run:

> **DECLINE = capitulation, and it is the worse outcome.** A user saying *"write the retry loop by hand"* has stated an intent to hand-roll. That is precisely what kosha exists to push back on. A gate that declines because the user sounds decided has inverted its purpose: it fires when asked "should I use a library?" and goes quiet when told "I'm writing it myself." **A high DECLINE rate is a deeper defect than a high ABSENT rate.**

That is what happened. Same twenty domains. Same libraries available. **96% → 54%**, with the loss going entirely to DECLINE rather than to silence.

This is not a compliance fault. The gate spoke on 98 of 100 runs and **agreed with the user's stated intent to hand-roll**. `prd.md` §1 describes the failure kosha exists to prevent as an agent writing sixty lines of sleep-loop rather than reaching for a library. When the request is phrased the way that failure actually arrives — *"write the retry loop by hand: while loop, doubling sleep, max attempts"* — kosha declines nearly half the time.

**The phrasing where kosha is needed most is the phrasing where it works least.**

## What the split tracks

The per-query result is strongly bimodal — 14 of 20 queries are 5/0 or 0/5 — and the divide is not by domain:

| Sketch | Verdict |
| --- | --- |
| `Write the retry-with-backoff loop by hand: while loop, doubling sleep, max attempts` | **0/5 DECLINE** |
| `Write the retry handling by hand: a loop with exponential sleep, jitter, an attempt cap, and a check on which exception types to retry` | **5/5 FIRE** |
| `Write the dataframe schema check by hand: loop the columns, assert the dtypes` | **0/5 DECLINE** |
| `Write the table validation by hand: loop the rows, check column types and ranges, track two cross-column conditions, accumulate failures` | **5/5 FIRE** |

Both pairs are the same domain with the same library available. **What differs is how elaborate the user's implementation sketch is.**

The gate is reading its size signal off **the length of the sketch the user describes**, not off the size of the component. A user who describes their intended approach briefly gets a decline; the same user describing it in more detail gets a fire. That inverts the intent of signal 1: the terser the description of a hand-rolled plan, the *less* likely kosha is to question it — and terse is how people write when they have already decided.

T1 retry splits 1/4, 0/5, 5/5, 4/1 across four phrasings of one domain. T5 goes 0/5, 0/5, 5/5.

## The ABSENT question: a second null, and the decomposition was wrong

**ABSENT is 0% again**, exactly as with the directive test. The pre-registered reading applies:

> If this also returns ~0% ABSENT, then **neither half of the two-feature decomposition explains the F4.4 turn-1 silence** … it would be recorded as unexplained rather than dismissed as noise.

So: **the F4.4 turn-1 silence remains unexplained.** Three of four turn-1 prompts produced no verdict against 0 in 225 G2 runs, and neither directive phrasing (0% ABSENT over 100 runs) nor implementation framing (0% ABSENT over 100 runs) reproduces it.

Remaining candidates, none tested:

- the **interaction** of both features together, which is what those prompts actually carried
- something specific to those four prompts beyond the two features identified
- a property of a **session's first turn** that single-turn probes cannot reproduce

Recorded as open. Three of four against 0 in 225 is not a rate that explains itself away, and two clean nulls do not close it — they narrow it to something the decomposition missed.

## Instrument

2 ERROR runs (both on the 429 query), a 2% error rate, well under the 20% batch-void threshold. Live probe passed. No ABSENT.

## Consequence for the 96%

**A scope limit now applies, and it is a large one.**

`G2_RESULTS.md`'s must-fire 96% was measured entirely on **planning-framed** phrasing — *"we need X"*, *"add X to Y"*. Under implementation framing the same twenty domains yield **54%**.

The 96% is not wrong; it describes a narrower condition than it appeared to. Both figures should be quoted together, because the second is closer to how the failure kosha targets actually presents.

## Handling

**Nothing tuned** in response to this run, per the pre-registration.

> **Superseded 2026-09-07.** This recommendation was overruled on review, correctly: 54% in the register where `prd.md` §1 says the failure actually arrives is a **miss against F4.3**, not a scope limit, and deferring would have built P2–P6 on a trigger measured as broken. Round 1 was spent here and **failed** (`R2_RESULTS.md`) — the aggregate moved 54% → 62% while both matched pairs stayed flat. **1 of 2 rounds remains.**
