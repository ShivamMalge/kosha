# Option D — paper validation against cases it was not designed to fix

**Date:** 2026-09-07 · **Method:** on paper, no calls. The swap test applied to every query D was *not* built from.
**Result: D roughly breaks even. It fixes one case cleanly, is ambiguous on a second, and destabilizes one that currently resolves perfectly.**

## The generalized meta-lesson from C

Stated at its proper altitude, because the narrow version is not the useful one:

> **Before proposing any resolution rule, measure how often its trigger condition fires on the POSITIVE set.**

Option C's trigger condition — *a recognized class and a never-fire clause both hold* — fired on **17 of 20 must-fire queries (85%)**. A rule whose condition is nearly universal on the cases you must not break is not a tiebreak; it is a veto wearing a tiebreak's clothes. The check cost nothing: the data was already on disk, and the audit took one pass.

D was validated the same way it was designed — against the three cases it was built to fix. That is the same shape as fitting a gate to probes you wrote. What follows is the check against everything else.

## The swap test

> Replace every project-specific value with different ones. Would a library still have to be written?
> **Yes** → the difficulty is project-specific; never fire. **No** → they are parameters; the clause does not apply.

## Against the 5 stable borderline queries

| Query | Now | Swap test | Under D | |
| --- | --- | --- | --- | --- |
| date range → buckets, DST/tz | 1.00 FIRE | swap range/tz → DST-correct bucketing is generic | FIRE | unchanged |
| stable content hash over nested dicts | 1.00 FIRE | swap the structure → canonical serialization is generic | FIRE | unchanged |
| small LRU cache over metadata | 0.00 DECLINE | governed by **size**, which D does not touch | DECLINE | unchanged |
| retry for one call site, ~25 lines | 0.00 DECLINE | governed by **size** ("about 25 lines") | DECLINE | unchanged |
| **parse the vendor's semi-structured log lines** | **1.00 FIRE** | **contested — see below** | **unstable** | **DESTABILIZED** |

### The vendor log parser is the problem case

Swap the vendor. Do you write a new parser, or a new grok pattern?

- **New parser** → the difficulty is vendor-specific → the swap test says **never fire**.
- **New grok pattern** → the format is a parameter of an existing library → **fire**.

Both readings are defensible, and the query says *"semi-structured"* — precisely the word that leaves it open. So the swap test does not resolve it; **it converts a query that currently resolves at 1.00 into a coin-flip.**

That is D's real cost: the swap test has its own ambiguous zone, and it lands on a query the current rule handles perfectly.

## Against all 20 must-fire queries

Under D, naming a project artifact is explicitly **not** a never-fire match when the difficulty is generic. Applying the swap test to each:

| # | Swap what | Library still needed? | Under D |
| --- | --- | --- | --- |
| 1–4 | the upload path / ingest client / S3 calls / which exceptions retry | no — tenacity handles any | FIRE |
| 5–7 | the flags / the TOML file / the entrypoint | no — typer + pydantic-settings handle any | FIRE |
| 8–11 | the schema / the table / the parquet input | no — pandera handles any | FIRE |
| **10** | **the two cross-column constraints** | **no — `Check` takes arbitrary cross-column predicates** | **FIRE** |
| 12–14 | the API client / the vendor quota | no — limits + httpx handle any | FIRE |
| 15–17 | the async task / the Rust worker | no — backon handles any | FIRE |
| 18–20 | the struct / the vendor CSV | no — serde handles any | FIRE |

**All 20 unchanged.** Notably #10 — the only query matching the never-fire clause under its strict "business logic" reading — comes out FIRE under D, correctly: the constraint *values* are project-specific, the constraint *checking* is generic.

D therefore does what it was designed to do on the positive set: it costs nothing there, which is exactly where C cost 17 of 20.

## Net effect

| Query class | Under D |
| --- | --- |
| order state machine (0.60) | **resolved → FIRE.** Six states are configuration; transition validation, audit and persistence are what a library provides |
| config merge (0.73) | **still ambiguous.** The swap test splits it: format parsing is bespoke, per-key override logic is generic. The query bundles two components with opposite verdicts |
| unicode normalization (0.60) | **unchanged** — governed by size, a clause never in tension here |
| vendor log parsing (1.00) | **destabilized** |
| 4 other stable borderline | unchanged |
| 20 must-fire | unchanged |

**Score: fixes 1, ambiguous on 1, no change on 1, breaks 1.** Stable borderline queries go from 5 to 5 — one gained, one lost.

An earlier draft claimed D "resolves two of three". That was wrong on the config merge: I checked whether the *override logic* was generic and did not notice the query also contains a bespoke *format parser*, so the swap test returns different answers for the two halves. Correcting it here rather than leaving the stronger claim standing.

## Conclusion

**D is not worth a threshold-rule round on this evidence.** It survives the check C failed — it does not touch the positive set — but its net gain on the borderline set is approximately zero, and it introduces a new ambiguous zone of its own on the swap test.

The deeper reading: both C and D try to fix a *wording* problem, and the borderline set's instability may not be a wording problem at all. See `AMBIGUITY_RULE_GAP.md`.

**Recorded as a documented candidate with its prediction intact**, so a future round at P7 starts from this evidence rather than re-deriving it. If D is ever tested, the pre-registration is: state machine → ≥0.8 FIRE, must-fire stays ≥90%, **and the vendor log parser stays ≥0.8** — that third clause is the one this paper check added, and it is the one most likely to fail.
