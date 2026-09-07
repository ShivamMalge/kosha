# Paper checks before the last round — both candidates die, and the real target appears

**Date:** 2026-09-07 · Zero cost. Method that turned option C from plausible into falsified in one pass.
**Evidence:** the decline *clause* each run cited, reconstructed from the persisted raw streams (`scripts/tally_declines.py`).

## The decisive measurement

Every DECLINE names the clause it fired on. Tallying them answers "what would removing signal 1 actually change?" without running anything.

| Clause cited | Framed run (post-change) | Framed run (pre-change) |
| --- | --- | --- |
| **NEVER-FIRE: under ~30 lines** | **17 (59%)** | **18 (60%)** |
| NEVER-FIRE: glue / config plumbing | 3 (10%) | 7 (23%) |
| **SIGNAL 1: under 80 lines** | **3 (10%)** | **1 (3%)** |
| **STATED INTENT — not a clause in the rule** | **3 (10%)** | 0 |
| AMBIGUITY RULE | 1 (3%) | 0 |
| unparsed | 2 (7%) | 4 (13%) |
| **NEVER-FIRE total (hard veto)** | **69%** | **83%** |

## Candidate 1 — two-of-two (signals 2 and 3 only): **DEAD**

Signal 1 is cited in **3 of 29 declines (10%)**. Removing it entirely could address at most those three.

**69% of declines come from never-fire clauses**, which are a *hard veto evaluated first*. Whatever the signals say, the veto ends evaluation. Two-of-two changes the counting stage while the vetoing stage does the work.

Worse, the dominant veto is **"under roughly 30 lines" — which requires the very same size estimate that round 1 established is unanswerable from a terse request.** Removing signal 1 leaves the identical unanswerable judgment in place one layer up, now as an unappealable veto rather than one vote of three.

This was the candidate I would have backed. The tally kills it for free, which is exactly what the check is for.

## Candidate 2 — default size to met when signals 2 and 3 hold: **DEAD, same reason**

It operates on signal 1's contribution to the count. The never-fire veto fires **before** the count is reached (`SKILL.md` §1: *"Checked first. A never-fire match ends evaluation regardless of the three signals."*).

A query declining on `under-30-lines` never reaches the two-of-three tally, so defaulting a signal inside that tally cannot reach it. It would fix the 10% and leave the 59% untouched.

## Candidate 3 — ask when underdetermined: **RULED OUT, on cost**

Not tested; rejected on reasoning, and the reason recorded so it is not re-proposed.

It converts a silent decline into an **interruption on the most common phrasing there is**. Terse implementation requests are the modal case, so kosha would be asking a clarifying question constantly. That trades a false negative for a cost `prd.md` **F4.2 does not cover** — F4.2 bounds the *token* cost of a correct non-fire and says nothing about the *interaction* cost of a question, which users tolerate far less. A gate that interrupts to ask "how big is this?" before most requests gets disabled, and a disabled gate scores zero on everything.

## The real target: the never-fire size clause

The tally relocates the problem. Round 1 aimed at signal 1 because the matched pairs pointed there; the clause data shows signal 1 was never the binding constraint.

**"Under roughly 30 lines" is:**

1. **the dominant decline cause** in the framed register (59–60%, both runs),
2. **an unappealable hard veto**, not one vote of three, and
3. **dependent on exactly the estimate round 1 proved is unavailable** from a terse request.

That is a far better-aimed hypothesis than either candidate, and it explains the flat matched pairs precisely: both terse pair members declined on the veto, so no change to the signal tally could have moved them.

**Not adopted.** The last round should be aimed here, with its own pre-registration, and only after the reverted baseline is re-measured.

## An unplanned finding: the gate invents a clause

**3 of 29 declines (10%) cite "the user explicitly asked for a hand-written implementation."**

There is **no such clause anywhere in the rule.** Not in the never-fire list, not in the three signals. The model added a deference of its own.

Example: `genuinely borderline — you've already chosen hand-rolled, and a loop + sleep + deadline…`

This is the capitulation mechanism, and it is not a wording defect in any existing clause — it is an *addition*. It appeared 0/30 before the signal-1 change and 3/29 after, which is far too small a difference to attribute; what matters is that it appears at all, and that no rule change to signal 1 or the never-fire list would remove it. Filed with `AMBIGUITY_RULE_GAP.md`, where the same pattern already lives.
