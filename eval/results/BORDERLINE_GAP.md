# The borderline gap — characterization, not a fix

**Date:** 2026-09-07 · **Status:** PROPOSAL ONLY. Nothing in the rule is changed.
**Budget:** the threshold-rule budget still has **both rounds unspent**. This characterizes the gap so that any future change is spent against evidence rather than intuition.

This is the first finding in four rounds that is about **kosha's logic** rather than its plumbing.

---

## What the three unstable queries share

| Query | rate |
| --- | --- |
| implement the order state machine: six states, guarded transitions, audit trail | 0.60 |
| merge three layers of our own config format with per-key override rules | 0.73 |
| normalize unicode in user-supplied display names before comparison | 0.60 |

Each satisfies **signal 2 (recognized problem class)** *and* **a never-fire clause**, simultaneously and legitimately:

| Query | Recognized class | Colliding clause |
| --- | --- | --- |
| Order state machine | state machines / workflow engines | **project-specific business logic** — *your* six states, *your* transitions |
| Config merge | config layering — the T2 domain, which fires 87% | **project-specific** — "our own config format" |
| Unicode normalization | unicode handling; `unicodedata` is stdlib | **under ~30 lines** |

The shared shape: **a real library domain applied to something only this project has.** A state machine library exists; *your* order lifecycle does not ship in it. Config-layering libraries exist; *your* format is not among their loaders.

## Why two-of-three cannot express it

The rule's two stages have different logical types, and the collision falls between them:

```
never-fire list   =  hard veto, any match ends evaluation
two-of-three      =  additive count over independent signals
```

A veto cannot be partial and a count cannot be overridden. So when "recognized problem class" and "project-specific business logic" are **both** true, the rule offers no way to say *how* project-specific, or *how much* of the domain a library would actually cover. Every evaluation must resolve a genuine tension by force, and the direction it resolves is unstable — which is exactly what a 0.60 rate looks like.

Note this is **not** ambiguity about the facts. The model is not uncertain whether the config format is bespoke; it is uncertain what that *implies*. The ambiguity rule ("borderline → do not fire") should have caught this and did not, because the evaluation does not *feel* borderline from inside — each pass reaches a confident verdict, and different passes reach different ones.

## What a fourth clause or tiebreak would have to decide

Any fix must answer one question the rule currently cannot:

> **When a component sits inside a recognized problem class but its specifics are unique to this project, does the library cover the hard part or only the scaffolding?**

Three shapes it could take, none adopted:

| Option | Form | Cost |
| --- | --- | --- |
| **A — coverage clause** | A fourth signal: *"a library would handle the difficult part, not merely the frame."* Fires only if yes | Restates the same judgment in new words; risks the P0 failure of naming a category rather than a rule |
| **B — veto softening** | Make "project-specific" a **scored** dimension rather than a hard veto, so it trades against the others | Weakens the never-fire list, whose strength is that it is unconditional. Would need a margin, like the ladder's 0.5 |
| **C — explicit tiebreak** | Leave the rule; add a deterministic resolution: *when a recognized class and a never-fire clause both hold, DECLINE* | Cheapest and most testable. Consistent with the existing asymmetry (a missed fire costs the status quo; a false fire costs trust). Would flip all three to DECLINE and cost nothing measured so far |

**C is the cheapest to test and the most consistent with the design's existing bias.** It is also falsifiable: it predicts all three queries move to ≥0.8 DECLINE, and predicts no change in must-fire, where no never-fire clause applies.

## The cut fourth signal was cut correctly — for a reason we did not have then

`borderline.json` was built to probe **size versus edge-case density**. Four of its eight queries were chosen for that tension, and edge-case density was the clause cut at P0 for being a category rather than an applicable rule.

**Three of those four resolved perfectly consistently:**

| Query | rate |
| --- | --- |
| date range → buckets, DST/tz boundaries | 1.00 |
| stable content hash over nested dicts | 1.00 |
| parse vendor's semi-structured log lines | 1.00 |

Two-of-three handled all three cleanly with no edge-case clause at all. The fourth, unicode normalization, is unstable — but for the project-specificity/size collision above, not for edge-case density.

**The P0 cut cost nothing, and the evidence says the real ambiguity was somewhere else entirely.** That decision was made on a procedural argument — a rule only its author can apply is not a rule — without any evidence about whether the signal was needed. It now has evidence, and it holds. Worth recording as a decision that turned out right for a reason unavailable at the time, rather than quietly banking it.

## Recommendation

**Characterize now, change nothing.** The gap is real, narrow, and specific: three queries out of fifty, all sharing one structural collision. It does not affect must-fire (96%) or the weighted no-fire subset (0/20).

If a threshold-rule round is spent, spend it on **option C**, pre-registering the prediction that all three move to ≥0.8 DECLINE with no movement in must-fire. That is falsifiable, cheap, and tests one idea rather than rewording the rule.
