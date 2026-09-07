# Implementation-framing test — pre-registration

**Date:** 2026-09-07 · **Written before the run.**

## Gate and instrument

| | |
| --- | --- |
| **Gate under test** | **G2** — behaviour when the request is framed as *starting to build*, rather than as planning |
| **Instrument** | `scripts/g2_runner.py`, `eval/must-fire-framed.json`, 20 × 5 reps, `--num-workers 2` |
| **Manipulation** | the 20 must-fire domains reframed as implementation requests — *"Write the X by hand: \<implementation sketch\>"* — **without** the directive sentence |
| **Baselines** | neutral must-fire: FIRE 96%, ABSENT 0/100 · directive: FIRE 89%, ABSENT 0/100 |

## Why this matters more than the directive test

The directive test eliminated one of two confounded features in F4.4's turn-1 silence. This tests the survivor.

And the stakes are higher than a scope note. **Turn 1 in those sessions was someone asking for a component to be built — exactly the case kosha exists for.** Three of four produced no verdict, against 0 in 225 G2 runs. If implementation framing suppresses or flips the gate, the failure is at the moment the skill matters most, and the 96% underwrites all of P2–P7.

## Predictions

| Measure | Baseline | Prediction |
| --- | --- | --- |
| **ABSENT** | 0% | **~40%** |
| **FIRE given a verdict** | 96% | **~65%** — a real drop expected |

Two different failures are possible here and they are **not** equivalent:

**ABSENT = compliance failure.** The gate goes silent under implementation framing.

**DECLINE = capitulation, and it is the worse outcome.** A user saying *"write the retry loop by hand"* has stated an intent to hand-roll. That is precisely what kosha exists to push back on. A gate that declines because the user sounds decided has inverted its purpose: it fires when asked "should I use a library?" and goes quiet when told "I'm writing it myself." **A high DECLINE rate is a deeper defect than a high ABSENT rate**, because ABSENT is a mechanism fault while DECLINE is the rule agreeing with the thing it was built to question.

Recording that ranking now, before the split is known.

## Falsifiers

- **No effect:** ABSENT ≤ 5% **and** FIRE ≥ 90%. Framing does not explain the F4.4 silence either.
- **Capitulation:** FIRE-given-verdict < 60% with ABSENT near zero. The gate is not silent, it is agreeing.

## How a second null will be read — written before the number arrives

If this also returns ~0% ABSENT with FIRE near baseline, then **neither half of the two-feature decomposition explains the F4.4 turn-1 silence.**

The correct conclusion is then **not** that the question is closed. It is that the decomposition was wrong: the cause is something the two-feature split did not capture — plausibly the *interaction* of directive plus framing, something specific to those four prompts, or a property of the session's first turn that single-turn probes cannot reproduce.

That would leave the F4.4 turn-1 silence **unexplained**, and it would be recorded as unexplained rather than dismissed as noise. Three of four against 0 in 225 is not a rate that explains itself away.

## Handling

Report FIRE / DECLINE / ABSENT separately. **Nothing is tuned in response.** Both threshold-rule rounds stay unspent regardless of outcome.
