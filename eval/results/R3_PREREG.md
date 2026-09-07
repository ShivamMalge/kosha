# Threshold-rule round 2 — pre-registration (the last round)

**Date:** 2026-09-07 · **Written before the rule is changed.**
**Budget: this spends 2 of 2. None remain.** If it misses, `STOP_HERE_IF.md` governs — and "run a third round" is not on that list.

## The revert is verified byte-identical, not merely reverted

`git diff` against both `7606770` and `dcc44de` reports **IDENTICAL** for `hooks/gate_prompt.txt` and `SKILL.md`. The rule is bit-for-bit the state that produced 96% / 95% / 54%.

**The baseline is therefore re-measured for drift, not for rule identity.** Any difference between the fresh baseline and the historical figures is model or environment drift across days — which is itself worth knowing, and is the only thing a re-measure can now show.

## The two changes

Combined in one round because the decline-clause tally separates them for free. Each targets a distinct, separately-countable line.

**Change 1 — E, veto disapplication.** Appended to the `under roughly 30 lines` never-fire clause:

> — but only when the request lets you estimate the size. If the request does not determine how large the component is, this clause does not apply.

**Change 2 — the stated-intent counter.** Added to the gate:

> A stated intention to write it by hand is **not** a reason to decline. That is the case this gate exists for.

Nothing else is touched.

## Per-clause predictions — the primary scoring

Aggregates are the outcome test; **the clause tally is the mechanism test.** Measured by `scripts/tally_declines.py` on the framed run's raw captures, against the round-1 framed distribution.

| Decline clause | Round-1 share | Runs (of ~46) | Prediction | Falsifier |
| --- | --- | --- | --- | --- |
| **`under-30-lines`** | 59% | ~27 | **falls to ≤ 15%** — E's direct target | still ≥ 40% → E did not reach the veto |
| **stated intent** | 10% | ~5 | **falls to ≤ 3%** — counter's direct target | still ≥ 8% → the counter was ignored |
| `config plumbing` | 10% | ~5 | **unchanged** | large movement means an unattributed side effect |
| `signal 1` (80 lines) | 10% | ~5 | **unchanged or slightly up** — declines re-routing here as the veto lifts is expected, not a defect | — |
| ambiguity / unparsed | 10% | ~4 | unchanged | — |

A change that moves the aggregate while its own clause line stays flat is the round-1 failure repeating, and is scored as a failure regardless of the aggregate.

## Aggregate predictions

| Set | Baseline | Prediction | Falsifier |
| --- | --- | --- | --- |
| **Implementation-framed** | 54% | **~85%** (paper ceiling ~86%) | < 70% |
| **Neutral must-fire** | 96% | **≥ 90%** | < 90% |
| **no-fire** | 95% DECLINE, weighted 0/20 | **≥ 90% DECLINE**, weighted ≤ 2/20 | < 90%, or weighted > 2/20 |

**~85% is deliberately below F4.3.** The paper check established that ~14 of 46 declines have causes neither change addresses. Predicting 100% would be predicting something the arithmetic already rules out.

## The known cost, named in advance

**The slugify group (no-fire 1–5) is E's exposure.** The argument making retry underdetermined applies to slugify: done properly, with transliteration, collisions and truncation, it is plausibly 80+ lines. Three of the five state no size; one (`we need url slugs from the article titles`) already fires 5/5.

If E lifts their veto, up to **2 additional queries × 5 runs** could fire, taking no-fire to a ~86% floor and **breaching the ≥90% criterion.**

That is a pre-registered cost, not a discovery. If it happens, E traded precision for recall and the trade is visible rather than hidden in an aggregate.

## If the round misses — the first explanation to check

**Not the wording.** E introduces a meta-judgment — *"can size be estimated from this request?"* — which is more tractable than estimating magnitude (presence of information is easier to agree on than quantity) but is still a judgment, and carries the P0 failure mode.

**If round 2 misses, the first hypothesis is that the meta-judgment is as unstable as the judgment it replaced**, ahead of any claim that the clause was worded badly. That ordering is fixed now so it is not reordered afterwards to protect the approach.

## Run plan

1. `claude setup-token`, then a live probe *(user)*
2. **Baseline re-measure on the unchanged rule** — neutral must-fire + no-fire, 210 runs. Drift check only; the rule is verified identical
3. Apply both changes; measure the gate against F4.2's 300-token bound and report, trimming non-fix wording if needed as in round 1
4. Run framed + neutral + no-fire, 310 runs
5. Report per-clause tally first, then aggregates, then the `STOP_HERE_IF.md` decision if the round misses

Both changes go in **after** this file is committed.
