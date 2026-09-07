# A1 result status: RESOLVED (weak) — superseded by P1_ROUND0.md

> **Resolved 2026-09-06.** A2 fired on 4 queries / 6 runs, so the description can load the skill and the asymmetry below is restored. A1 is real evidence for F4.1 at G1, but **weak**: a description loading on 6% of its own must-fire set declines trivia near-unconditionally. **Re-run A1 after any description change** — widening to fix A2 is exactly what could break it.

**Date:** 2026-09-06
**Raw result:** 22/22 pass, every query 0/5, **0 subprocess failures across 110 calls**.

## Why a perfect score is not yet a result

A1's usefulness rests on an asymmetry: a pass is strong evidence for F4.1, because a query that never loads certainly never proceeds. **That asymmetry holds only if the description is capable of loading the skill at all.**

A description too narrow to load anything scores a flawless 22/22. So this result is equally consistent with:

- **(a)** an excellent G1 gate correctly declining 22 trivial queries, and
- **(b)** an invisible skill that would decline anything at all, including every must-fire query.

The harness smoke test returned **0/1 on "add retry logic with backoff to the ingest client"** — an obvious must-fire. One run only, but it points at (b).

## What the positive control did and did not prove

The positive control overrode the description with a deliberately universal string and scored 1/1. That proves **the detector can register a fire**. It says nothing about whether *this* description can, because it did not use this description.

Two things needed proving. Only one was proved.

## Same shape as the void batch, different cause

The void batch produced well-formed JSON out of total instrumentation failure. This is a clean, well-formed, possibly meaningless perfect score from a *working* instrument pointed at a possibly invisible skill. Both look identical at the summary line, which is why neither can be read from the summary line.

## Resolution condition

**A1 is unresolved until A2 shows a non-zero fire rate somewhere.**

- **A2 non-zero anywhere** → the description loads the skill, the asymmetry is restored, and A1's 22/22 becomes real evidence for F4.1 at G1.
- **A2 near-zero across the board** → A1 conveys nothing. It is **re-run after the description is fixed**, and these numbers are discarded rather than carried forward.

Description repair draws on the **description-scope budget**, not the threshold-rule budget (`phases.md` P1). No A1/A2 result may consume a threshold-rule round.
