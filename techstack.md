# kosha — Tech Stack

**Status:** draft
**Date:** 2026-09-06
**Scope:** the tooling kosha itself is built from. Not the libraries kosha recommends, and not the per-project `techstack.md` it emits.

> **Naming collision, on purpose.** This file is kosha's *own* stack. The artifact kosha writes into a target project is also called `techstack.md` and lives at that project's repo root. Same format, different subject.

---

## 1. Principle: kosha applies its own ladder to itself

`stdlib > small focused package > write it yourself > large framework`

kosha is mostly markdown. The executable surface is three small scripts, and every one of them lands on **stdlib**. There are zero third-party runtime dependencies. A skill whose entire premise is dependency restraint cannot arrive carrying a dependency tree.

---

## 2. Runtime

| Component | Choice | Why |
| --- | --- | --- |
| Content | Markdown | It is a Claude Code skill. Almost all of the artifact is prose the model reads |
| Scripts | **Python 3.11+**, stdlib only | 3.11 is the floor because `tomllib` (catalog parsing) landed there |
| Modules used | `tomllib`, `subprocess`, `venv`, `pathlib`, `argparse`, `json`, `datetime`, `re` | All stdlib |
| Rust smoke path | System `cargo` | Invoked as a subprocess for crates.io candidates. Required only when a Rust candidate is tested |
| kosha's own tests | `unittest` | stdlib. Adding `pytest` to test a dependency-restraint tool would be a poor advertisement |

**Rejected for kosha itself:** `PyYAML` (superseded by choosing TOML), `requests`/`httpx` (scripts never touch the network — §4), `pytest` (stdlib `unittest` is sufficient at this size), `click`/`typer` (`argparse` handles three scripts fine).

---

## 3. Catalog format

**TOML in fenced code blocks inside markdown domain files.**

- **Markdown outer layer** so the file the model reads and the file the script parses are the same file. A separate machine-readable sidecar would drift from the prose.
- **TOML inner layer** because `tomllib` parses it with no dependency. YAML would need `PyYAML`; JSON is unreadable with multi-line rationale text in it, and rationale text is most of an entry.

### The write asymmetry

`tomllib` is **read-only** — Python's stdlib has no TOML writer. Rather than adding `tomli-w`, entries are **emitted from a template** by the agent (which is writing prose into the same file anyway) and then **round-trip validated**: `catalog_lint.py` parses every fenced block back with `tomllib` and fails on anything malformed.

This is a deliberate instance of "write it yourself beats adding a dependency": the writer is a template plus a validator, and the validator is the part that actually matters.

---

## 4. Scripts

Three, all stdlib, all offline. Network access belongs to the **agent** (`WebFetch`/`WebSearch`), never to a script — which keeps every script deterministic, testable without fixtures, and safe to run in a sandbox.

### `scripts/smoke_test.py`

Executes a candidate's real API in an isolated environment and reports raw output.

```
smoke_test.py --ecosystem pypi --package tenacity --version 9.1.2 --snippet <path>
smoke_test.py --ecosystem crates --package backon --version 1.2.0 --snippet <path>
```

- **pypi:** `venv` → `pip install <pkg>==<ver>` → run snippet
- **crates:** temp `cargo new` → pinned dependency → `cargo run`
- Emits **raw stdout, raw stderr, exit code**, and the resolved version, verbatim
- **Never interprets.** It has no notion of pass or fail. The agent reads the raw output and decides. This is the mechanism behind `prd.md` F2 (hallucinated APIs) — a script that reported "success" would reintroduce exactly the self-report the design forbids
- Isolation is mandatory: the environment is a temp directory, never the target project

*Windows note:* venv binaries live under `Scripts\` rather than `bin/`. The runner resolves the interpreter path from `sys.platform` — the primary development machine is Windows, so this is the default path, not an afterthought.

### `scripts/catalog_lint.py`

Structural integrity. Run after every write-back (`architecture.md` §7.3 step 11).

- Every fenced TOML block round-trip parses
- Required fields present per `status`; `adopted` entries must carry `smoke_test_file` and `smoke_verified_version` (`prd.md` F2.1 — hard failure)
- Every `adopted` entry has a `rejected_alternatives` item with `id = "stdlib"` (F1.1)
- Every entry carries a `rubric_version`, and every **scored** rejection carries its per-criterion raws — the precondition for offline regeneration (`architecture.md` §6)
- **Size caps:** `INDEX.md` ≤ 120 lines; each domain file ≤ 340 lines and ≤ 6 entries. This is the enforcement point for progressive disclosure — without it the catalog silently becomes one large file
- Index/domain consistency: no orphan index rows, no unindexed domain files

### `scripts/staleness_check.py`

Offline, read-only tier report.

```
staleness_check.py --entry tenacity        # or --domain, or --all
```

Compares `tier_a_verified_on` / `tier_b_verified_on` against today and prints which fields have expired. It **re-verifies nothing** — the agent decides whether an expired field is worth a network call for the question actually being asked (`architecture.md` §6, R1).

---

## 5. What is deliberately absent

| Absent | Reason |
| --- | --- |
| A database or index format for the catalog | Files in git. The corpus is dozens of entries, not millions; grep and progressive disclosure are the access path |
| A package manager or lockfile for kosha | Zero runtime dependencies means nothing to lock |
| A network layer in the scripts | The agent already has one, and offline scripts are trivially testable |
| CI | Deferred until after `benchmark.md` produces a result worth protecting |

---

## 6. Benchmark tooling

Development-time only. None of this ships with the skill, and none of it adds a runtime dependency.

**Reused, not rebuilt** — the existing skill-creator harness:

| Script | Job |
| --- | --- |
| `run_eval.py` | Trigger evaluation only. Does the skill description fire on a query set |
| `aggregate_benchmark.py` | A/B aggregation over `eval-N/<arm>/run-M/grading.json` discovered from the filesystem |

**New, and minimal.** The harness executes no paired runs and its aggregated metrics are hardcoded to three, none of which is LOC. Two small pieces close that gap:

- **Runner** — sets up each task × arm × rep, launches a fresh session, collects results. Stdlib only (`subprocess`, `venv`, `json`, `pathlib`).
- **Sidecar aggregator** (~40 lines) — mean/stddev/min/max over the four fields `grading.json` cannot represent: the four-way token split, `loc_handwritten`, `deps_transitive`, `acceptance_pass`.

The alternatives were forking `aggregate_results` to accept a metric list, or encoding LOC as a boolean `expectations[]` assertion. Both were rejected in `benchmark.md` §4.3 — the second would make the primary metric unmeasurable.

**Token capture** is Claude Code OpenTelemetry: `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER=console`, `OTEL_METRIC_EXPORT_INTERVAL=5000` ([docs](https://code.claude.com/docs/en/monitoring-usage)). Environment variables, not dependencies — §2 is unchanged.
