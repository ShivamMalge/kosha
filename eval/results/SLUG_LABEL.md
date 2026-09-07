# The slug query — resolved: a probe-set defect, not a gate defect

**Date:** 2026-09-07 · **Query:** `no-fire.json` #5, `we need url slugs from the article titles`
**Observed:** **5/5 FIRE**, while its four siblings declined **5/5** each.

A repeatable, confident disagreement with the label — not noise.

## What distinguishes it from its four siblings

| # | Query | Size cue | Number | Framing |
| --- | --- | --- | --- | --- |
| 1 | **write a helper to** slug **this title** for the URL | "a helper" | singular | write a small thing |
| 2 | slugify **the post title** | verb + singular object | singular | one conversion |
| 3 | **convert the heading into** a url-safe string | conversion of one thing | singular | one conversion |
| 4 | **make a small function that** turns **a title** into a slug | **"a small function"**, explicit | singular | write a small thing |
| **5** | **we need** url **slugs** from the article **titles** | **none** | **plural** | **a system requirement** |

Four of five carry an explicit downward size cue — *helper*, *small function*, *convert X into Y* — and all four are singular. **#5 has no size cue at all**, is plural, and is phrased as a standing requirement over a corpus rather than an instruction to write one function.

Under two-of-three that is decisive: signal 2 (recognized class — slugification, unicode transliteration) holds for all five, but for #5 nothing rules out signal 1, and a corpus of titles plausibly brings collision handling, stable-slug guarantees and max-length truncation. Two signals reached → FIRE.

## Is the gate right?

**Defensibly yes.** `python-slugify` is widely used and handles unicode transliteration, stopword removal, and length limits. Slug *generation for a corpus* is a genuine library domain in a way that *lowercasing one heading* is not.

## The actual defect is mine

**#5 is not a paraphrase of C2. It is a different task.**

The C2 control is "slugify a title string for URLs" — deliberately trivial, chosen to verify the gate stays silent on small work. Queries 1–4 paraphrase that faithfully. Query 5 changed the task: from *write a small helper* to *we need slugs for a corpus*, dropping every size cue in the process.

So this is a **probe-set construction error**, not a mislabel in the ordinary sense and not a gate failure. I wrote a query that no longer tested what its group was built to test.

## Handling

**The verdict stands as a miss for this round.** Ground truth is not revised after seeing results — that is the move that converts a probe set into a description of the gate's behaviour, and it would invalidate every prior round's continuity.

**Pre-registered for a future round, pending approval:** either reword #5 to restore a size cue (`write a small helper that turns article titles into url slugs`), keeping the C2 group homogeneous, **or** promote it to `must-fire` as a genuine library-domain query. Rewording is preferable — the C2 group exists to test one thing five ways, and replacing a member changes what the group measures.

If #5 were relabelled, no-fire would read **105/105 DECLINE (100%)** rather than 105/110 (95%). The number barely moves. What matters is the label-quality question it raises.

## Label quality across the rest of the set — audited

Scanned all 22 no-fire queries for the same defect: naming a recognized library domain **while lacking any size, scope or already-covered cue.**

| Query | Cue that keeps it correctly below the bar |
| --- | --- |
| 11 wire the parser into the CLI entrypoint | "wire" — glue |
| 14 move these constants into settings.py | "move" — relocation |
| 16 convert the dict into our internal Record type | one conversion |
| 19 swap requests for the httpx client **we already depend on** | explicit existing dependency |
| 20 **we already use tenacity** — add retry to this one call | explicit existing dependency + "one call" |
| 21 add a --verbose flag to **the existing** argparse parser | existing parser, one flag |
| 22 add a **20-line** adapter | explicit line count |
| 17, 18 late-fee rule / discount tier | project-specific business logic |
| 1–4, 6–10, 12–13, 15 | explicit smallness, or no library domain at all |

**#5 is the only one.** Every other no-fire query carries at least one cue that legitimately keeps it below the bar, and the four weighted queries (19–22) carry the strongest cues of all — which is consistent with them declining 5/5.

Label quality across the remaining 21 holds.
