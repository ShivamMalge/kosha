# Threshold-rule round 2 — pre-registration (the last round)

**Date:** 2026-09-07 · **Written before the rule is changed.**
**Budget: this spends 2 of 2. None remain.** If it misses, `STOP_HERE_IF.md` governs — and "run a third round" is not on that list.

## The revert is verified byte-identical, not merely reverted

`git diff` against both `7606770` and `dcc44de` reports **IDENTICAL** for `hooks/gate_prompt.txt` and `SKILL.md`. The rule is bit-for-bit the state that produced 96% / 95% / 54%.

**Precisely what the diff proves:** the round-1 change was reverted cleanly and the rule is byte-identical to the state that produced 96 / 95 / 54. **What it cannot tell us is whether the model still behaves that way** — which is exactly why the drift check earns its place.

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

### Both disagreement cases, scored in advance

The clause tally and the aggregate can disagree in two directions, and they mean opposite things:

| Clause line | Aggregate | Verdict |
| --- | --- | --- |
| `under-30-lines` ≤ 15% | ≥ 85% | **E worked as modelled.** Round succeeds on its own terms — which is still not an F4.3 pass |
| **`under-30-lines` ≤ 15%** | **< 85%** | **E worked; the ceiling arithmetic was wrong.** The mechanism is fixed and the residual is larger than the paper check modelled. **This is not an E failure** and must not be reported as one — it redirects to whatever the residual turns out to be |
| `under-30-lines` still ≥ 40% | ≥ 85% | **Round-1 failure repeating.** Aggregate moved for unattributed reasons; scored a **failure regardless of the aggregate** |
| `under-30-lines` still ≥ 40% | < 85% | **E failed outright.** First hypothesis is the meta-judgment, per the ordering below |

The second row is the case most likely to be misreported, because a missed aggregate reads as failure at a glance. **It is the arithmetic that failed, not the change.**

## 85% cannot pass F4.3 — stated plainly

**The target is set below the criterion, so this round cannot pass F4.3 by construction.**

The paper check shows ~14 of 46 declines have causes neither change addresses. Predicting 100% would predict something the arithmetic rules out — but setting the target at ~85% means **"success" here is not a pass.** It means the *Stop here if* fires anyway, and we go to `STOP_HERE_IF.md` with a better number and a diagnosed mechanism rather than a worse number and a guess.

85% is not a pass mark. There is no pass mark available in this round.

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

## Run plan — reordered for rate-limit exposure

The account hit its five-hour cap mid-batch during round 1. Total exposure is cut from 520 runs to **410**, and ordered so a mid-batch death still yields the primary result.

1. `claude setup-token`, then a live probe *(user)*
2. **Drift check — framed set only, 100 runs**, on the unchanged rule. This is the number the round is measured against; neutral and no-fire are not re-baselined because both are measured post-change anyway
3. Apply both changes; measure the gate against F4.2's **300-token** bound and report, trimming non-fix wording if needed as in round 1
4. **Framed, 100 runs — the primary result**
5. Neutral, 100 runs — regression
6. no-fire, 110 runs — regression, and where E's known cost lands
7. Per-clause tally first, then aggregates, then `STOP_HERE_IF.md` if the round misses

**Steps 4–6 are ordered so the primary survives a partial batch.** Round 1 died exactly this way: framed completed and was usable, neutral and no-fire were lost. That ordering is now deliberate rather than lucky.

### The one thing dropping the neutral/no-fire baselines costs

Their regression criteria (≥ 90%, weighted ≤ 2/20) are judged against **historical** figures from a different day. If drift is real, that comparison is contaminated.

**The framed drift check covers this.** It measures drift magnitude on the one set with a same-rule historical figure (54%). If framed drift is small, the historical neutral and no-fire baselines remain usable. If framed drift is large, that invalidates the round's comparisons generally — and we would know from 100 runs rather than discovering it after 310.

Both changes go in **after** this file is committed.
