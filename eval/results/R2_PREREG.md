# Threshold-rule round 1 — pre-registration

**Date:** 2026-09-07 · **Written before the rule is changed.**
**Budget:** this spends **1 of 2** threshold-rule rounds. One remains.

## Why a round is spent now, when it was refused after H4

| | H4 | This |
| --- | --- | --- |
| Evidence | 1 probe | **100 runs** |
| Pattern | single verdict | **bimodal, 14/20 at 5/0 or 0/5** |
| Isolation | none | **matched pairs, same domain, one variable** |
| Mechanism | inferred | **diagnosed** |
| Probe status | holdout spent; a change would be fitted to it | fresh set, reusable |

`prd.md` §1 says the failure kosha exists to prevent arrives as *"write the retry loop by hand."* In that register the gate fires **54%**, against F4.3's requirement of effectively 100%. That is a **miss**, not a scope limit on the 96%.

Deferring to P7 would build P2–P6 on a trigger measured as broken and rediscover it six phases later. The *Stop here if* governs a rule that **resists** tuning; it has not been tuned once.

## The diagnosed mechanism

Signal 1 keys on **the length of the requester's implementation sketch**, not on the size of the component:

| Same domain, same library | Round-1 result |
| --- | --- |
| `retry-with-backoff loop: while loop, doubling sleep, max attempts` | **0/5** |
| `retry handling: exponential sleep, jitter, attempt cap, which exceptions` | **5/5** |
| `dataframe schema check: loop the columns, assert the dtypes` | **0/5** |
| `table validation: rows, types, ranges, two cross-column, accumulate failures` | **5/5** |

The inversion: the more decided someone is, the more tersely they write, and the less likely kosha is to question them.

## The change

**One change, to signal 1 only**, in both `SKILL.md` §1 and `hooks/gate_prompt.txt`.

*From:*
> roughly 80+ lines of non-trivial logic

*To:*
> the component would take roughly 80+ lines of non-trivial logic. Judge by what the component must do, not by how much detail the request gives — a terse request and a detailed one can describe the same component.

Nothing else is touched. The never-fire list, signals 2 and 3, the ambiguity rule and the verdict line are unchanged, so any movement is attributable to this edit.

**Deliberately not changed:** the "stated intent to hand-roll" effect. A user saying *"by hand"* has declared a decision, and the gate may be treating that as a reason to defer. That is a plausible *second* mechanism, and changing two things at once destroys attribution. If the size fix leaves a residual, that residual is the candidate for the remaining round.

## Predictions

| Set | Baseline | Prediction |
| --- | --- | --- |
| **Implementation-framed** (100 runs) | 54% FIRE | **≥ 85% FIRE** |
| **Neutral must-fire** (100 runs) — regression | 96% FIRE | **≥ 90%**, must not drop materially |
| **no-fire** (110 runs) — regression | 95% DECLINE, weighted 0/20 | **≥ 90% DECLINE, weighted ≤ 2/20 FIRE** |

### Why no-fire is included though it was not requested

Re-anchoring size away from sketch length makes signal 1 **easier to satisfy on tersely-described work** — and every no-fire query is tersely described. The obvious failure mode of this fix is that it lifts implementation framing by making the gate fire on trivia.

This is the lesson from option C stated as a procedure: **measure the change's trigger condition on the set you must not break.** C was falsified precisely because that check had not been run. Skipping it here would repeat the error one round later.

### Matched-pair check — the mechanism test

The aggregate is the outcome test; these are the mechanism test. After the change, **each pair must agree**, both members ≥ 4/5 FIRE:

| Pair | terse | elaborate |
| --- | --- | --- |
| **A** retry | `retry-with-backoff loop…` | `retry handling… exception types` |
| **B** tabular | `dataframe schema check…` | `table validation… cross-column` |

A pair that still disagrees means signal 1 is still reading sketch length, whatever the aggregate does.

## Falsifiers

The round **fails** — and the P1 *Stop here if* fires on evidence — if any of:

- Implementation-framed FIRE **< 75%**
- Neutral must-fire FIRE **< 90%** (fix moved the problem rather than solving it)
- no-fire DECLINE **< 90%**, or weighted subset **> 2/20 FIRE** (bought recall with precision)
- **Either matched pair still disagrees** (mechanism untouched; any aggregate gain is incidental)

**Both framings must clear together.** A fix that lifts one at the other's expense has relocated the defect, not repaired it.

## Cost check

The gate prompt grows. `prd.md` F4.2 bounds a correct non-fire at **300 tokens** (measured ~260 = gate 246 + verdict ~14). The new gate is measured after the edit and reported; if the total exceeds 300, that is an F4.2 breach and is reported as one rather than quietly re-based — 400 was already rejected once for exactly that reason.

## Handling

Report both aggregates, the matched pairs, and per-query rates for all three sets. If the round does not clear, that is the *Stop here if* firing on evidence, which is what the budget existed to produce.
