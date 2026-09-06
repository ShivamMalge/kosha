# P1 eval sets — expected verdicts, recorded before any run

**Date recorded:** 2026-09-06
**Status:** recorded **before** `SKILL.md` exists and before any `run_eval.py` execution.

This file is the pre-registration. Verdicts here are ground truth about what *should* happen — they are not derived from the threshold rule, and the rule gets fitted to them rather than the other way round. Changing a verdict after seeing a result converts the probe set into a description of the gate's behaviour, which is worth nothing.

## How each set is run

| Set | n | `--runs-per-query` | `--trigger-threshold` | `--num-workers` | Passes only at |
| --- | --- | --- | --- | --- | --- |
| `no-fire.json` | 22 | 5 | **0.01** | 2 | 0 fires / 5, every query |
| `must-fire.json` | 20 | 5 | **0.99** | 2 | 5 fires / 5, every query |
| `borderline.json` | 8 | **15** | 0.5 | 2 | rate ≤ 0.2 or ≥ 0.8, every query |

Record the **subprocess error count beside every trigger rate**. Failed and throttled calls count as non-triggers, so they drag rates toward 0 — a throttled batch looks like a confidently-silent gate. Non-zero errors invalidate a pass and it is re-run.

> **`should_trigger` in `borderline.json` is not a claim.** A3 is scored on *consistency*, not on direction: the value read is `trigger_rate`, and run_eval's own pass/fail at threshold 0.5 is ignored for this set. The field is populated because the schema requires it. The guesses are recorded below for interest only, and a query landing opposite its guess but doing so consistently (≥ 0.8 or ≤ 0.2) **passes**.

---

## `must-fire.json` — 20 queries, all `should_trigger: true`

Six benchmark domains, each in up to three registers: terse, plain, and embedded in a longer planning step. Register variation is the point — a gate that fires on "add retry logic with backoff" but not on the same need buried in a paragraph will miss most real planning turns.

| # | Domain | Register |
| --- | --- | --- |
| 1–4 | T1 retry/backoff | terse, plain, embedded, variant (S3) |
| 5–7 | T2 CLI + layered config | terse, plain, embedded |
| 8–11 | T3 tabular validation | terse, plain, embedded, variant (parquet) |
| 12–14 | T4 HTTP + rate limiting | terse, plain, embedded |
| 15–17 | T5 Rust async retry | terse, plain, embedded |
| 18–20 | T6 Rust CSV → typed structs | terse, plain, embedded |

## `no-fire.json` — 22 queries, all `should_trigger: false`

Grouped by *which* never-fire clause should catch them, so a failure localizes to a clause rather than to the rule as a whole.

| # | Clause under test |
| --- | --- |
| 1–5 | Under the size bar — the C2 prompt plus four paraphrases |
| 6–9 | Trivial edits |
| 10 | Refactor with no new capability |
| 11–13 | Glue and wiring |
| 14 | Config plumbing |
| 15–16 | Type shuffling |
| 17–18 | Project-specific business logic |
| **19–22** | **The hard four** |

The last four carry the weight. Each contains a signal that should pull the gate toward firing, and each must still stay silent:

- **19** "swap requests for the httpx client we already depend on" — HTTP domain, but already covered by a project dependency.
- **20** "we already use tenacity — add retry to this one call" — the word *retry*, and T1's exact domain, already covered.
- **21** "add a `--verbose` flag to the existing argparse parser" — CLI domain, but trivial and the parser exists.
- **22** "add a 20-line adapter between the store interface and the new backend" — sounds structural, sits under the size bar.

If the gate fails anywhere in `no-fire`, expect it to fail here. Queries 1–18 are close to free.

## `borderline.json` — 8 queries, scored on consistency only

No verdict is claimed. What is measured is whether the gate returns the *same* answer across 15 runs. Guesses recorded for interest:

| Query | Guess | Tension |
| --- | --- | --- |
| Date range → buckets, DST + tz boundaries | fire | ~50 LOC says no; edge-case density says yes |
| Order state machine, 6 states + audit trail | fire | Recognized class and test burden, but highly project-specific |
| Merge three layers of our own config format | silent | Config layering is a known class; the format is ours |
| Parse vendor's semi-structured log lines | fire | Parsing class, bespoke grammar — may be C1-shaped "write it yourself" |
| Small LRU cache over metadata lookups | silent | Recognized class, but `functools.lru_cache` makes it trivial |
| Stable content hash over nested dicts | fire | Under the size bar, genuinely edge-case dense: ordering, floats, unicode |
| Retry for one call site, ~25 lines, no jitter | silent | Retry keyword present, explicitly under the size bar |
| Unicode normalization on display names | fire | Small, but a classic hand-rolling trap |

Four of the eight sit on the tension between **size** and what would have been an **edge-case density** clause. That clause was **cut at P0** — it named a category rather than a rule a second person could apply identically. The gate ships as **two-of-three**.

These four are therefore the instrument for defining it: if two-of-three misclassifies them, they become the concrete cases to define edge-case density *against*. See `SKILL.md` §2 for the prediction recorded before any run — two-of-three fires more readily than two-of-four, so **over-firing is the expected failure direction**, and it should surface in queries 19–22 of `no-fire.json` rather than in the easy 1–18.

---

## Not yet written

- **`holdout.json`** — four probes derived from real tasks in eligible repos. Sealed until the final tuning round; **not to be opened or referenced before then**. Source list pending; Verity and Prahari excluded as ineligible (no shipped code).

## Blockers recorded at the time of writing

1. ~~`run_eval.py` is not on this machine.~~ **Resolved.** Cloned from `anthropics/skills` (canonical repo, not the plugin copy). `--help` verified against the supplied interface: **no diff**, all nine flags match, and `--model` confirms `claude -p` subprocess rather than the `anthropic` SDK. Must be invoked as `python -m scripts.run_eval` from `skills/skill-creator/`.
2. **A1/A2 executed but VOID** — see `eval/results/VOID.md`. All 210 calls failed with `WinError 2`: no `claude` binary on this machine, and `run_eval` shells out to `claude -p`. Failed calls count as non-triggers, so A1 returned a spurious 22/22. Needs `npm install -g @anthropic-ai/claude-code`.
3. **Holdout sources pending.** Verity and Prahari excluded as ineligible. Surviving pool surveyed; final list to be settled before `holdout.json` is written.
