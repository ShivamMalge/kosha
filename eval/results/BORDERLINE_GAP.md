# The borderline gap — characterization, not a fix

**Date:** 2026-09-07 · **Status:** PROPOSAL ONLY. Nothing in the rule is changed.
**Budget:** the threshold-rule budget still has **both rounds unspent**, and stays unspent until the evidence distinguishes the options.

This is the first finding in four rounds that is about **kosha's logic** rather than its plumbing.

---

## What the three unstable queries share

| Query | rate |
| --- | --- |
| implement the order state machine: six states, guarded transitions, audit trail | 0.60 |
| merge three layers of our own config format with per-key override rules | 0.73 |
| normalize unicode in user-supplied display names before comparison | 0.60 |

Each satisfies **signal 2 (recognized problem class)** *and* a never-fire clause, simultaneously and legitimately:

| Query | Recognized class | Colliding clause |
| --- | --- | --- |
| Order state machine | state machines / workflow engines | **project-specific** — *your* six states, *your* transitions |
| Config merge | config layering — the T2 domain, which fires 87% | **project-specific** — "our own config format" |
| Unicode normalization | unicode handling; `unicodedata` is stdlib | **under ~30 lines** |

The shared shape: **a real library domain applied to something only this project has.**

## Why two-of-three cannot express it

The rule's two stages have different logical types, and the collision falls between them:

```
never-fire list   =  hard veto, any match ends evaluation
two-of-three      =  additive count over independent signals
```

A veto cannot be partial and a count cannot be overridden. When both hold, the rule offers no way to say *how* project-specific, or how much of the domain a library would actually cover. Each evaluation resolves a genuine tension by force, and the direction is unstable — which is what a 0.60 rate looks like.

This is **not** ambiguity about facts. The model is not uncertain whether the config format is bespoke; it is uncertain what that *implies*. The ambiguity rule ("borderline → do not fire") did not catch it because the evaluation does not *feel* borderline from inside: each pass reaches a confident verdict, and different passes reach different ones.

---

## Option C is falsified. My prediction was wrong.

The earlier draft recommended **option C** — *when a recognized class and a never-fire clause both hold, DECLINE* — and predicted **no change in must-fire**. That prediction is wrong, and the data to refute it already existed.

**All 20 must-fire queries satisfy signal 2 by construction.** So C's behaviour on must-fire depends entirely on how many *also* match a never-fire clause. Audited query by query:

| # | Query | Project-specific artifact named | Strict "business logic"? |
| --- | --- | --- | --- |
| 1 | retry w/ jitter on **the upload path** | yes | no |
| 2 | retry with backoff to **the ingest client** | yes | no |
| 3 | **the ingest client** … *which exception types are worth retrying* | yes | borderline |
| 4 | retry around **the S3 client calls** | yes | no |
| 5 | cli config layering | **no** | no |
| 6 | CLI with flags, env vars, **config file** precedence | lexically "config plumbing" | no |
| 7 | **the entrypoint** … TOML config … which layer supplied the bad value | yes + config plumbing | no |
| 8 | validate the dataframe schema before **we load it** | yes (mild) | no |
| 9 | checks on **the input table** | yes | no |
| 10 | **the incoming table** … *two cross-column constraints* | yes | **yes** |
| 11 | **the parquet input** … **the transform step** | yes | no |
| 12 | rate limiting to **the API client** | yes | no |
| 13 | http client that respects Retry-After on 429 | **no** | no |
| 14 | **the outbound HTTP layer** … **the vendor quota** | yes | no |
| 15 | tokio retry with a deadline | **no** | no |
| 16 | retry **this async task** | yes (mild) | no |
| 17 | **the Rust worker** … **the fallible task** | yes | no |
| 18 | csv to **typed structs** | yes (mild) | no |
| 19 | parse **this CSV** into **typed structs** | yes (mild) | no |
| 20 | **The Rust importer** … **vendor CSV** … **a typed struct** | yes | no |

**Counts:**

| Reading of "project-specific" | must-fire queries matching | C would decline | must-fire result under C |
| --- | --- | --- | --- |
| **As applied in practice** ("involves this project's specifics") | **17 of 20** | 17 | **~15%** (from 96%) |
| **As literally written** ("business logic") | 3 of 20 (#6, #7, #10) | 3 | **~85%** (from 96%) |

**C is catastrophic under the practical reading and still harmful under the strict one.** Even the charitable reading pushes must-fire to the boundary of its own ≥85% target.

The reason is exactly as diagnosed from outside: **a recognized problem class applied to project-specific particulars is not an edge case, it is what building software is.** Retry for *my* ingest client. CSV into *my* structs. C converts the never-fire list into a near-universal veto and declines precisely the work kosha exists to catch.

**Recorded as a wrong prediction**, on the same footing as the round-0 miss. The error was proposing a resolution rule without first measuring how often its trigger condition fires on the positive set — the cheapest possible check, against data already on disk.

---

## The diagnosis is sharper than options A, B and C

The question the characterization actually raises:

> **When a component sits inside a recognized problem class but its specifics are unique to this project, does the library cover the hard part or only the scaffolding?**

None of the three original options asks it. **C sidesteps it** (declines on collision regardless). **B prices it without defining it.** **A names it without operationalizing it** — the P0 failure already rejected once.

## Option D — the clause may simply be miswritten

`project-specific business logic` is doing two jobs, and only one of them is correct:

| It should exclude | It currently also excludes |
| --- | --- |
| a component whose **difficulty** is project-specific | a component whose difficulty is **generic** and whose **parameters** are project-specific |

Six named states with guarded transitions and an audit trail *is* a state machine. Transition validation, audit trails and persistence are precisely what a library provides. **The six states are configuration, not difficulty.**

### Operationalizing it

The distinction needs a test a second person applies identically, or it repeats the P0 failure:

> **Swap test.** Replace every project-specific value with different ones. Would a library still have to be written?
> - **Yes** → the difficulty is project-specific. Never fire.
> - **No** → the values are parameters. The clause does not apply.

Late-fee rules fail the swap test (no library encodes *any* fee schedule as a domain). Six order states pass it (a state-machine library handles any six states).

### D against the three unstable queries

| Query | Difficulty | Parameters | D predicts |
| --- | --- | --- | --- |
| Order state machine | transition validation, audit, persistence — **generic** | the six states | **FIRE**, consistently |
| Config merge | layering and per-key override — **generic**; format parsing bespoke | the format | **FIRE** (the override logic is the hard part; the format is a loader) |
| Unicode normalization | **generic** — but the **size** clause applies independently | — | **DECLINE**, via size, unchanged |

D resolves two of three and leaves the third governed by a clause that was never in tension.

### D against must-fire

Under D, "names a project artifact" is explicitly **not** a never-fire match, so **all 20 must-fire queries are unaffected**, including #10 — cross-column constraint *values* are yours, constraint *checking* is generic, and it passes the swap test.

### Cost and falsifiability

| | Option C | Option D |
| --- | --- | --- |
| must-fire impact | **17/20 declined** | **none** |
| Resolves the three | yes, all to DECLINE | two to FIRE, one unchanged |
| Risk | guts the positive set | the swap test is still a judgment; could repeat P0 |
| Falsifier | *(already falsified)* | any of the three fails to reach ≥0.8; or must-fire drops below 90% |

**D is not adopted.** It is a different *kind* of bet from C — a rewritten clause versus a new tiebreak — and the evidence does not yet distinguish a miswritten clause from a missing tiebreak. It only rules out C.

---

## The cut fourth signal was cut correctly — for a reason unavailable then

`borderline.json` was built to probe **size versus edge-case density**. Four of its eight queries were chosen for that tension; edge-case density was cut at P0 for being a category rather than an applicable rule.

**Three of those four resolved perfectly consistently** — date range with DST/tz, stable content hash over nested dicts, and vendor log-line parsing, all at **1.00**. Two-of-three handled them cleanly with no edge-case clause at all. The fourth, unicode normalization, is unstable for the size collision above, not for edge-case density.

The P0 cut was made on a procedural argument — *a rule only its author can apply is not a rule* — with no evidence about whether the signal was needed. It now has evidence, and it holds. Recorded as a decision that turned out right for a reason unavailable at the time, rather than quietly banked.

## Recommendation

**Change nothing. Spend no threshold-rule round yet.**

C is eliminated on evidence. D is plausible and cheap but untested, and "miswritten clause" versus "missing tiebreak" are different bets that the current data cannot separate. The gap affects three queries out of fifty and does not touch must-fire (96%) or the weighted no-fire subset (0/20).

When a round is spent, spend it on **D**, pre-registering: all three unstable queries reach ≥0.8 in the direction predicted above, **and** must-fire stays ≥90%. The second half is the one that matters — it is the clause that would have caught C before it was ever proposed.
