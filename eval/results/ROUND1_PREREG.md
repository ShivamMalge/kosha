# Round 1 — pre-registration

**Written before the description rewrite and before any round-1 run.**
Applying the round-0 post-mortem lesson: name the gate, name the instrument, name the falsifier.

## Gate and instrument

| | |
| --- | --- |
| **Gate under test** | **G1 (load)** — does the frontmatter description cause the skill to load |
| **Instrument** | `run_eval.py`, A1 + A2 re-run as a pair, `--runs-per-query 5`, `--num-workers 2` |
| **Not under test** | **G2 (proceed).** The two-of-three rule and the planning-only constraint live in the body and are invisible to this instrument. No round-1 result may consume a threshold-rule budget round. |

## Change being tested

1. **Timing constraint moved out of the description into the body.** Session state is not observable from query text; a description can only match it on surface form, which is what produced the round-0 register gradient.
2. **Topical vocabulary made concrete.** Round-0 evidence: domains fired only where the description contained the query's literal keyword. T6 had *zero* content-word overlap. Adding `csv`, `dataframe`, `column`, `parquet`, `deserialize`, `struct`, `table`, `nullability`.
3. **Suppressors removed** from the DO-NOT clause — `type conversion` (adjacent to T6's "typed structs") and `config plumbing` (adjacent to T2's terse "cli config layering", 0/5 while embedded scored 2/5). The never-fire list stays in the body, where it belongs.

## Predictions

### Primary — the terse register, which is the one that matters

Real turns are terse or plain. A rewrite that lifts embedded and leaves terse near zero has fixed nothing.

| Register | Round 0 | Round 1 prediction |
| --- | --- | --- |
| **terse** | 0/30 (0%) | **≥ 15/30 (50%)** |
| **plain** | 1/30 (3%) | **≥ 15/30 (50%)** |
| embedded | 5/30 (17%) | ≥ 50% |
| variant | 0/10 (0%) | ≥ 50% |

**Falsifier, stated in advance:** **terse < 20%** means the rewrite failed on the criterion that matters, regardless of what the other registers do. Terse 20–50% is a partial result and is reported as partial, not as success.

### Secondary — the two dead domains

T3 (0/20) and T6 (0/15) rise to **≥ 40%** each. Falsified if either stays below 20%.

### A1 — expected to degrade, and that is the trade

Widening the description is exactly the change that can break A1. Round 0 was 22/22, but weak — a description loading on 6% of its own must-fire set declines trivia near-unconditionally.

**Prediction: A1 ≥ 18/22, with any losses concentrated in the four weighted queries** (`swap requests for the httpx client we already depend on`, `we already use tenacity — add retry to this one call`, `add a --verbose flag to the existing argparse parser`, `add a 20-line adapter…`).

A loss in queries 1–18 (slugify, renames, glue) would be a *different and worse* result: it would mean the description went broadly undiscriminating rather than specifically wider.

**A1 failures are not automatically defects.** Per `prd.md` F4, a query that loads and then correctly declines has passed F4.1 and is priced by F4.2. A1 cannot distinguish that from a wrong proceed — so an A1 regression is a flag for transcript inspection, not a verdict.

## What would make me call round 1 a failure

- terse < 20%, or
- A1 losses outside the four weighted queries, or
- T3 or T6 still at 0%, which would mean the lexical diagnosis was wrong and the cause lies elsewhere.

## Sealed

`holdout.json` is not written, not opened, and not exposed to `run_loop`. It tests the **rule**, not the description.
