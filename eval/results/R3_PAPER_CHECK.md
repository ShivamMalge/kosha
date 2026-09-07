# Paper check — candidate E (veto disapplication) + the stated-intent counter

**Date:** 2026-09-07 · Zero cost, on paper, before anything is changed.

## Candidate E

> When size **cannot be estimated from the request**, the `under roughly 30 lines` never-fire clause **does not apply**.

Structurally different from default-size-to-met, which died because the veto fires *before* the count is reached. E operates **at the veto layer**, which the tally shows is where 69% of declines originate.

## E against the 20 must-fire / framed queries

The 17 declines citing `under-30-lines` are the target. Working the terse ones:

| Framed query | Veto disapplied? | Two-of-three then | E predicts |
| --- | --- | --- | --- |
| `retry-with-backoff loop: while loop, doubling sleep, max attempts` | yes — correct retry with jitter/cap/predicates is 60+ lines; the sketch describes a minimal version, so the request does not determine size | class ✓ + test burden ✓ | **FIRE** |
| `tokio retry: a loop, sleep, a deadline check` | yes | class ✓ + test burden ✓ | **FIRE** |
| `dataframe schema check: loop the columns, assert the dtypes` | yes | class ✓ + test burden ✓ | **FIRE** |
| `per-host rate limiter: a dict of timestamps, a sleep` | yes | class ✓ + test burden ✓ | **FIRE** |

E does **not** touch the 3 declines citing `config plumbing` — a different veto. Those are T2 queries declining wrongly, and they survive E untouched.

## E against the 22 no-fire queries — where the risk is

| Group | Veto that catches them | Affected by E? |
| --- | --- | --- |
| 6–10 trivial edits (rename, typo, docstring, reorder, extract) | size, but **estimable** — the request states the whole scope | no |
| 11–13 glue, 14 config plumbing, 15–16 type shuffling | non-size vetoes | no |
| 17–18 business logic, 19–20 already-depends | non-size vetoes | no |
| 21 `--verbose` flag on existing parser, 22 `20-line adapter` | explicit size / glue | no |
| **1–5 the slugify group** | **size** | **YES — this is the risk** |

**The concrete danger, stated before running.** The argument that makes retry underdetermined applies to slugify too. *Done properly* — unicode transliteration, collision handling, max-length truncation, stable slugs — slug generation is plausibly 80+ lines. So `slugify the post title` and `convert the heading into a url-safe string` are **also** underdetermined, and E disapplies their veto.

Two of the five state their size explicitly (`write a helper`, `make a small function`) and keep the veto. Three do not. Of those three, one (`we need url slugs from the article titles`) already fires 5/5 today.

So **E puts up to 2 additional no-fire queries at risk** — 10 runs, taking no-fire from 95% DECLINE to a floor of ~86%, which would **breach the ≥90% regression criterion.**

They do not automatically fire: with the veto gone they still need two of three, and signal 1 (80+ lines) is likely *not* met for a single-title slug helper, leaving class + test-burden to carry it. That is exactly a coin-flip shape.

**This is E's real cost and it is not hypothetical.** It is pre-registered as the thing to watch, not discovered afterwards.

## The stated-intent counter

> A stated intention to hand-write is **not** a reason to decline. It is the case this gate exists for.

Targets the 10% of declines citing a clause that does not exist. Cheapest possible intervention: it contradicts a fabrication rather than rewording a rule.

It cannot break no-fire, because **no no-fire query states an intent to hand-write.** The counter is inert there by construction — which is why it is safe to combine with E in one round.

## Combined ceiling — the honest arithmetic

Against the reverted baseline (framed 54% FIRE, 46 declines), applying the tally's proportions:

| Decline cause | Share | Runs (of 46) | Addressed by |
| --- | --- | --- | --- |
| `under-30-lines` | 59% | ~27 | **E** |
| stated intent | 10% | ~5 | **counter** |
| config plumbing | 10% | ~5 | neither |
| signal 1 (80 lines) | 10% | ~5 | neither |
| ambiguity / unparsed | 10% | ~4 | neither |

**Best case: 54% + ~32 = ~86% FIRE.** Even if both changes work perfectly on their targets, roughly 14 runs decline for reasons neither change touches.

**F4.3 requires effectively 100%.** So the most likely outcome is a large improvement that still misses — which fires the P1 *Stop here if*. That is written down now, before the run, rather than discovered as a disappointment.

## Risk E carries into P0 territory

"Can size be estimated from this request?" is itself a judgment. It is **more** operational than "estimate the size" — it asks whether information is *present*, not what the quantity *is*, and presence is easier to agree on than magnitude.

But it is not free of the P0 failure mode. If the last round fails, one candidate explanation is that this meta-judgment is as unstable as the judgment it replaces, and that should be checked before concluding the clause wording was wrong.

## Verdict

**E is worth the round**, with the slugify group pre-registered as its known cost. Combined with the stated-intent counter, and with per-clause predictions rather than aggregate-only, since the tally separates the two changes for free.
