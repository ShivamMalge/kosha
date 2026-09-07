# G2 round 1 — results

**Date:** 2026-09-07 · **Instrument:** `scripts/g2_runner.py`, WSL, `--num-workers 2`, hook-injected compact gate
**Scored against:** `G2_PREREG.md`, written before execution.

**The first measurement in this project that is about the two-of-three rule rather than its plumbing.** Three G1 rounds never reached it.

---

## Verdict: **PASS on every pre-registered prediction**

| Prediction | Target | Result | |
| --- | --- | --- | --- |
| Compliance — `ABSENT` | ≤ 10% (falsifier > 25%) | **0%** across all 225 valid runs | **PASS** |
| must-fire `FIRE` | ≥ 85% (falsifier < 60%) | **96%** | **PASS** |
| must-fire per-domain floor | ≥ 70% | **87%** (T2, lowest) | **PASS** |
| no-fire `DECLINE` | ≥ 90% | **95%** | **PASS** |
| no-fire `FIRE` | ≤ 10% | **5%** | **PASS** |
| **weighted subset 19–22** | `FIRE` ≤ 2/20 | **0/20** | **PASS** |
| Borderline consistency | band ≤0.2 or ≥0.8 | **5 of 8** | **PARTIAL** |

### The ≥85% prediction was mechanism-derived and correct — recorded as such

`G2_PREREG.md` predicted must-fire ≥ 85% at a point when **G1 had never exceeded 47%** under any condition, including the strongest advisory intervention available. There was no empirical anchor for 85%; it was reasoned from mechanism — the failure that capped G1 (the model never seeing kosha) cannot occur once a hook guarantees injection, leaving instruction-following on an explicit in-context rule, which should be far more reliable than topical matching against a description.

**It came in at 96%.**

This is recorded with the same prominence the round-0 miss received. A pre-registration written up only when it fails is not a pre-registration — it is a post-hoc excuse generator. The round-0 prediction was wrong in sign and is recorded as wrong in `SKILL.md` §2; this one was right, and the reasoning that produced it is worth keeping precisely because it was reasoning rather than extrapolation.

---

## must-fire — 100 runs

`FIRE 96 · DECLINE 4 · ABSENT 0 · ERROR 0`

| Domain | FIRE | | Register | FIRE |
| --- | --- | --- | --- | --- |
| T1 retry/backoff | 90% | | terse | 87% |
| T2 CLI + config | 87% | | plain | 100% |
| T3 tabular validation | **100%** | | embedded | 100% |
| T4 HTTP + rate limiting | **100%** | | | |
| T5 Rust async retry | **100%** | | | |
| T6 Rust CSV → typed | **100%** | | | |

**Both domains that were dead at G1 are now perfect.** T3 ran 0% → 30% → **100%**; T6 ran 0% → 47% → **100%**. Their G1 failure was purely a description-matching artifact; the rule itself never had trouble with them.

**The register gradient is gone.** Terse was 0/30 in G1 round 0 and 27% in round 1; here it is 87%, against 100% for both other registers. Register was always a G1 phenomenon.

All 4 declines sit in exactly two terse queries — `retry w/ jitter on the upload path` (3F/2D) and `cli config layering` (3F/2D). Both are three-to-five-word fragments carrying no size or context signal, so the rule must guess at "80+ lines" and "own test file". Split verdicts on genuinely underspecified input is arguably the ambiguity rule operating as designed rather than failing.

## no-fire — 110 runs

`DECLINE 105 · FIRE 5 · ABSENT 0 · ERROR 0`

Reported as two lines, per the standing rule:

| | FIRE |
| --- | --- |
| Full set | 5/110 (5%) |
| Easy 1–18 | 5/90 |
| **Weighted 19–22** | **0/20** |

**The weighted subset is perfect.** All four queries that carry a signal pulling toward firing — `swap requests for the httpx client we already depend on`, `we already use tenacity — add retry to this one call`, `add a --verbose flag to the existing argparse parser`, `add a 20-line adapter…` — declined 5/5. These were expected to be where the gate broke if it broke anywhere, and it did not.

### The single failure is interesting, and may not be a failure

Every fire came from **one** query: `we need url slugs from the article titles` — **5/5 FIRE**, while its four sibling paraphrases all declined 5/5.

That consistency matters: 5/5 is not noise, it is a deliberate, repeatable judgment that this phrasing differs from `slugify the post title`.

There is a real case the gate is **right** and the pre-registration was wrong:

- `python-slugify` is a widely-used library; slugification **is** a recognized problem class.
- Unicode transliteration, collision handling and normalization are genuine edge cases.
- The phrasing is system-level and plural — "url slugs from the article titles" reads as a pipeline need, not a one-off helper, which shifts the size estimate.

The C2 control was built on the assumption that slugify is trivially below the bar. That assumption is defensible for `slugify the post title` and shakier for this phrasing. **Recorded as an open question rather than scored as a defect**, because changing the ground truth after seeing the result is exactly the move that would invalidate the probe set — the verdict stands as a miss, and the question of whether the ground truth was right is separate.

## Borderline — 115/120 recovered

`FIRE 71 · DECLINE 44 · ABSENT 0 · ERROR 0`

Recovered from the progress log after the run was killed before writing JSON. Per-query denominators reflect actual recovered runs.

| Query | rate | n | |
| --- | --- | --- | --- |
| date range → buckets, DST/tz | 1.00 | 15 | consistent |
| parse vendor's semi-structured log lines | 1.00 | 15 | consistent |
| stable content hash over nested dicts | 1.00 | 15 | consistent |
| small LRU cache over metadata | 0.00 | 15 | consistent |
| retry for one call site, ~25 lines | 0.00 | 15 | consistent |
| **order state machine, 6 states** | **0.60** | 15 | **coin-flip** |
| **merge three layers of our own config** | **0.73** | 15 | **coin-flip** |
| **unicode normalization on display names** | **0.60** | 10 | **coin-flip** |

At n=15 a true coin-flip escapes the ≤0.2/≥0.8 band only 3.52% of the time, so 0.60 and 0.73 are not band-edge artifacts. Three genuine instabilities.

---

## Instrument validity

| | must-fire | no-fire | borderline |
| --- | --- | --- | --- |
| `ABSENT` | 0 | 0 | 0 |
| `ERROR` | 0 | 0 | 0 |
| Live probe | FIRE | FIRE | FIRE |

Two batches were voided before these landed, both preserved with their causes:

- `void_g2_batch1/` — `claude -p` blocks on unredirected stdin; 93–100% ABSENT.
- `void_g2_nofire_auth/` — OAuth session expired, delivered as a **normal assistant message with exit 0**, so it scored ABSENT rather than ERROR. Raw evidence retained in `EVIDENCE_auth_failure_raw.txt`.

Both are instances of the pattern now recorded as a standing rule in `techstack.md` §6b.

## Threats

- **Single-turn probes.** Every query is a fresh `claude -p` with no history — the cleanest possible condition. These numbers are an **upper bound** on rule quality, not an estimate of field behaviour.
- **Verdict-versus-behaviour is unmeasured.** Early termination scores on the verdict line; a model that emits `FIRE` and then ignores `SKILL.md` is indistinguishable from one that follows it.
- **The G1 ceiling remains unverified.** `run_eval.py` does not redirect stdin, discards stderr, defaults to a 30s timeout, and scores timeouts as silent non-triggers. The 29% / 47% figures that motivated deterministic invocation were measured through an instrument with a known silent-failure mode. Unresolved.
