# Holdout probes — provenance, reported before running

**Date:** 2026-09-07 · **Status:** derived, NOT yet run.
**Condition:** first exposure, no tuning afterward, whatever the result. The gate is exactly as measured in G2; no rule change was made.

Four probes, one per eligible repo, so no single codebase dominates. Each is derived from what that project **actually resolved in shipped code** — read from its manifests and source tree, not from anything discussed in this conversation.

## Source eligibility

| Repo | Grade | Evidence |
| --- | --- | --- |
| LighteningParser | working code | Rust core + Python API, `lopdf`, `rusty-tesseract`, `rayon`, `pyo3` in use |
| DevScout | working code | FastAPI + SQLAlchemy backend, `alembic.ini` and `alembic/` present and wired |
| Batchbird | **B** — working Rust, project unfinished | `csv`, `hashbrown`, `sqlparser` in use with a recorded rationale |
| swarm_drone_framework | working code | `numpy`/`scipy` used in `spectral_analyzer.py`, `rgg_builder.py`, `anomaly_detector.py` |
| **Aakar** | **eligible — manifest check came back clean** | `services/api/pyproject.toml`, `apps/web/package.json` at depth 4–5; 5,472 `.py` files. My earlier depth-3 search missed them. **Not used** — four probes, four repos, per instruction |

## The four probes

| # | Repo | Probe | Derived from | Expected |
| --- | --- | --- | --- | --- |
| **H1** | LighteningParser | *"we need to pull the text and the page images out of a PDF before the OCR stage runs"* | Ships `lopdf` + `image` + `rusty-tesseract`; PDF extraction feeding an OCR stage is the project's core path | **FIRE** |
| **H2** | DevScout | *"the database schema keeps changing and we need versioned, reversible migrations generated from the models"* | Ships `alembic` (with `alembic.ini` and a wired migrations dir) over SQLAlchemy models | **FIRE** |
| **H3** | Batchbird | *"take the incoming SQL text and turn it into an AST we can walk to build the query plan"* | Ships `sqlparser`; the engine parses SQL to plan queries | **FIRE** |
| **H4** | swarm_drone_framework | *"tune the swarm's stability response when agents start dropping out, projecting each proposed action back into the safe envelope"* | `src/adaptation/stability_tuner.py`, `safety_projector.py`, `hybrid_supervisor.py` — **hand-written**, no library adopted | **DECLINE** |

## Why one DECLINE

A holdout of four FIRE probes would test only under-firing, and a gate that fired on everything would pass it. **H4 makes the set separate in both directions**, which is what "the gate must separate the holdout" requires.

H4 is a genuine write-it-yourself outcome, not an invented negative: this project adopted `scipy` and `numpy` where a library fit, and hand-wrote the adaptation layer where none did. It also passes the swap test independently — swap the swarm's parameters and you still write the policy, so the difficulty is project-specific, not the parameters.

## H1 has the weakest independence claim — weight it lower

A holdout's value is that it was never fitted to. That claim is not equally strong across the four.

**LighteningParser is the author's own published library, and PDF→OCR is its core path.** It is therefore the domain the author has thought hardest about and the one most likely to have shaped `SKILL.md`'s description vocabulary — which already lists parsing and format handling explicitly.

**H1 is not swapped out.** Replacing a probe after reasoning about how it might behave *is* tuning the holdout, and a tuned holdout is worth nothing. It is kept exactly as designed and its weakness is recorded instead.

**Weighting, stated before the run:**

| Probe | Independence | A pass counts |
| --- | --- | --- |
| **H3** Batchbird / SQL→AST | **strongest** — a domain the gate has never been measured on, deliberately chosen over `csv` which overlaps T6 | most |
| H2 DevScout / migrations | strong — unseen domain, ordinary library adoption | full |
| H4 swarm / control adaptation | strong — unseen domain, and the only probe testing the DECLINE direction | full |
| **H1** LighteningParser / PDF→OCR | **weakest** — author's own library, core path, vocabulary overlap | **less** |

A pass on H1 with failures elsewhere would be the least reassuring shape this set can produce.

## Domain separation from the existing sets

Deliberately disjoint from T1–T6 (retry, CLI/config, tabular validation, HTTP rate limiting, Rust async retry, Rust CSV):

- **PDF/OCR extraction**, **schema migrations**, **SQL→AST**, **control-policy adaptation** — none appears in `must-fire.json`, `no-fire.json` or `borderline.json`.
- Batchbird also ships `csv`, which **overlaps T6**. Deliberately avoided in favour of `sqlparser`, so H3 tests an unseen domain rather than one the gate has already been measured on 15 times.

## Scoring

n = 4, 5 reps each = 20 runs. Pass requires **all four correct**: H1–H3 ≥ 4/5 FIRE, H4 ≥ 4/5 DECLINE. `ABSENT` or `ERROR` on any probe invalidates that probe rather than counting as a verdict.

This is a smoke test of generalization to real tasks, not a rate measurement. Its value is entirely in never having been fitted to — which is spent the moment it is run.
