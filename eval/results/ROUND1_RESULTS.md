# Round 1 — results

**Date:** 2026-09-06 · **Instrument:** `run_eval.py`, WSL, `--num-workers 2`, A1+A2 re-run as a pair
**Validity:** VALID. **Subprocess failures: 0 on A1 (110 calls), 0 on A2 (100 calls).** Same as round 0. No errors, so no clustering to assess; the copied token has now survived 420 calls.

## Verdict against pre-registration: **PARTIAL**

Scored against `ROUND1_PREREG.md`, written before the rewrite.

| Prediction | Target | Result | Verdict |
| --- | --- | --- | --- |
| **terse register** | ≥ 50% | **27%** (8/30) | **PARTIAL** — inside the pre-declared 20–50% band |
| **plain register** | ≥ 50% | **33%** (10/30) | **PARTIAL** |
| T3 revives | ≥ 40% | 30% (6/20) | PARTIAL — above the 20% falsifier |
| T6 revives | ≥ 40% | **47%** (7/15) | **MET** |
| A1 holds | ≥ 18/22, losses in weighted | **22/22, zero losses** | **MET**, better than predicted |
| **Falsifier** | terse < 20% | 27% | **not triggered** — round is not a failure |

**This is a partial result and is reported as partial.** The pre-registration set 50% as success and 20–50% as partial precisely so a large relative gain could not be talked into a pass. Terse went 0% → 27%, which is a real move and not the target.

## Registers

| Register | Round 0 | Round 1 |
| --- | --- | --- |
| terse | 0/30 (0%) | **8/30 (27%)** |
| plain | 1/30 (3%) | **10/30 (33%)** |
| embedded | 5/30 (17%) | 11/30 (37%) |
| variant | 0/10 (0%) | **0/10 (0%)** |

### The register gradient has collapsed — the primary diagnosis was right

Round 0 read 0% / 3% / 17% across terse/plain/embedded: a steep, monotone gradient. Round 1 reads **27% / 33% / 37%**, which at n=30 per cell is statistically indistinguishable across registers.

**That is the diagnosis confirming itself.** Moving the timing constraint out of the description removed the surface-form penalty on terse phrasing. Terse is no longer punished for not sounding like plan prose; it now performs like every other register.

What remains is a **different problem**: the whole distribution sits near 30% instead of near 50%. This is a general loading-strength deficit, not a register deficit. Round 2 (if authorized) should target overall match strength and must not be aimed at registers — that lever has already been pulled and has stopped moving.

## Domains

| Domain | Round 0 | Round 1 |
| --- | --- | --- |
| T1 retry/backoff | 10% | 15% |
| T2 CLI + config | 13% | **13%** (flat) |
| T3 tabular validation | **0%** | **30%** |
| T4 HTTP + rate limiting | 7% | 33% |
| T5 Rust async retry | 7% | 40% |
| T6 Rust CSV → typed | **0%** | **47%** |

**Both dead domains revived.** T3 0→30%, T6 0→47%. The lexical diagnosis is confirmed: adding `csv`, `dataframe`, `column`, `nullability`, `parquet`, `deserialize` and `struct` moved the two domains that previously shared no vocabulary with the description.

**T2 is flat at 13% and is now the weakest domain.** Removing `config plumbing` from the DO-NOT clause did lift its terse query (0/5 → 2/5), but its embedded query fell 2/5 → 0/5, netting zero. T2 is the one domain the rewrite did not help.

## Lexical presence is necessary but not sufficient

The round-0 diagnosis needs refining, and this is the finding most likely to mislead round 2 if left unstated.

Several queries whose keywords are now explicitly in the description still score 0/5:

| Query | Keywords present in description | Rate |
| --- | --- | --- |
| `add retry logic with backoff to the ingest client` | retry, backoff | **0/5** |
| `add structured retry around the S3 client calls` | retry | **0/5** |
| `we need schema validation on the parquet input…` | schema, validation, parquet | **0/5** |
| `parse this CSV into typed structs in Rust` | csv, typed, structs | **0/5** |

Meanwhile near-synonymous phrasings fire strongly: `csv to typed structs with per-row errors` scores **4/5** while `parse this CSV into typed structs in Rust` scores **0/5**.

So keyword overlap was the right fix for *zero* coverage — it is what revived T3 and T6 — but it does not predict rate above that floor. Something else governs strength, and round 1 does not identify it.

**The `variant` register is the sharpest form of this**: 0/10 across both rounds, unchanged, despite both queries containing description keywords. Two queries at n=5 is thin, but a flat zero while every other register tripled is worth isolating rather than averaging away.

## Statistical caution

**Per-query rates at n=5 should not be read individually.** The resolution is 0/.2/.4/.6/.8/1.0 and the error bars are wide enough that a query at 2/5 and one at 4/5 are not reliably different. The register and domain aggregates (n=15–30) are the trustworthy figures; the per-query table is diagnostic colour, not measurement.

This is the same reasoning that put `borderline.json` at 15 reps. If round 2 needs per-query discrimination, it needs more reps per query, not more queries.

## A1 — held completely

22/22 in both rounds, zero fires on any of 110 calls, including all four weighted queries. Predicted degradation to ≥ 18/22 did not occur.

A1 is also now **stronger evidence** than in round 0. Round 0's pass was weak because a description loading on 6% of its own must-fire set declines trivia near-unconditionally. At a 29% must-fire load rate the description is materially wider, and A1 still holds at 22/22 — so it is discriminating, not merely narrow.

## Budget

**Threshold-rule rounds consumed: 0.** This round drew entirely on the G1 description budget (`phases.md` P1). The two-of-three rule remains untested — G2 has still never been exercised, since `run_eval` cannot see it.

**Holdout: sealed.** Not written, not opened, not exposed to `run_loop`.
