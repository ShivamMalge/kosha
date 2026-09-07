# Open item: the ambiguity rule is inoperative

**Date:** 2026-09-07 · **Status:** OPEN, carried to **P7**. Not a proposal; no fix attempted.
**Why it is filed separately:** it is not a clause-wording problem, and both candidate fixes for the borderline gap (C and D) leave it entirely untouched.

## The rule

`SKILL.md` §1 and `hooks/gate_prompt.txt`:

> If the two-of-three evaluation is genuinely borderline, **do not fire**.

Its purpose is to make the gate's failure direction safe. The asymmetry is deliberate and correct: a missed fire costs the user the status quo, a false fire costs tokens *and* teaches them to disable the skill.

## It never engaged

Three borderline queries returned rates of **0.60, 0.73 and 0.60** across 15 runs each. These are precisely the cases the rule exists for. It did not fire on any of them.

**The reason is that the ambiguity is not visible from inside a single evaluation.** Each individual pass reaches a *confident* verdict. The evaluation does not feel borderline while it is happening — the model weighs a recognized problem class against a never-fire clause, resolves it, and states a verdict without hesitation. Different passes resolve the same tension in different directions.

So the ambiguity exists **only in the distribution across runs**, and a single run cannot observe a distribution. The rule asks the model to detect a property of an ensemble from inside one member of it.

## Why this is more interesting than the clause wording

`BORDERLINE_GAP.md` treats the instability as a defect in how `project-specific business logic` is written, and proposes fixes at that level:

- **Option C** — decline on collision. Falsified: its trigger condition fires on 85% of must-fire.
- **Option D** — split the clause by difficulty versus parameters. Paper-validated as roughly break-even: fixes one, destabilizes one.

Both assume the model *knows* it is in a hard case and needs better instructions for resolving it. **The evidence says it does not know.** A clearer clause would produce a confident verdict from a clearer rule — it would not produce hesitation, because nothing in the loop makes hesitation available.

This generalizes past kosha. Any model-mediated rule with an "if unsure, do X" escape hatch has the same structure: **the escape hatch is only reachable if uncertainty is introspectively available at decision time**, and for a confident-but-unstable decision it is not. The rule reads as a safeguard and is closer to decoration.

## What would actually address it

None of these is proposed; they are recorded so a future round starts from options rather than a blank page.

| Approach | Shape | Cost |
| --- | --- | --- |
| **Self-consistency** | Evaluate the gate more than once and require agreement; disagreement *is* the ambiguity signal | Multiplies gate cost per turn — directly against F4.2 (300 tokens) and F4.5 |
| **Make the tension explicit** | Have the gate name the colliding clause as part of its verdict (`KOSHA: DECLINE collision:recognized-class+project-specific`), turning an internal weighing into visible output | Cheap; the verdict line already exists. Does not resolve the tension, but makes it *countable* in transcripts |
| **Pre-enumerate the collisions** | List the known collision shapes in the gate so the model recognizes rather than derives them | Only covers collisions already discovered; the borderline set found three |
| **Accept it** | An unstable verdict on genuinely ambiguous input may be honest behaviour, and the ambiguity rule is retired as unenforceable rather than left as false comfort | Costs the safety asymmetry the rule was written to guarantee |

The second is the cheapest and is diagnostic rather than corrective — it would let P7 measure how often real usage hits a collision, which is the number missing from this entire analysis.

## Why P7 and not now

The borderline set was **built to be ambiguous**. A rule that is stable on clear cases and unstable on three deliberately-constructed ambiguous ones is behaving about as well as a model-mediated rule can. must-fire is 96%, the weighted no-fire subset is 0/20, and the instability is three queries out of fifty in a set written by kosha's own author.

That does not clear the bar for spending a threshold-rule round now. At P7 the same question can be asked against **real usage**, where the frequency of collisions is an observed property rather than a design choice of the probe set.

**Both threshold-rule rounds remain unspent.**
