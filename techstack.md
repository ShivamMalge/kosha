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

*Platform:* development runs on **WSL Ubuntu**, so the runner targets POSIX layout (`bin/`). The move was forced by the benchmark harness, not chosen: `run_eval.py` streams subprocess output through `select()` on a pipe, which on Windows accepts sockets only.

> **DEFERRED — Windows support for the smoke runner.** Not solved and not obsolete. If kosha is used by anyone but its author it comes back as its own problem: venv binaries under `Scripts\`, `.exe` suffixes, and `CreateProcess` declining to resolve `.cmd` from PATH. Absence from the current scope is a consequence of a single-developer environment, not evidence the problem was handled.

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

> **"No fork" is partial, and the distinction matters.** What is preserved is the harness's *internals* — in particular `run_eval.py`'s streaming trigger-detection loop, which is the code that defines pass/fail. Forking that would mean a silent upstream change could stop results being comparable without anyone noticing.
>
> What is still written here: an A/B **runner**, because `aggregate_benchmark.py` executes nothing and only reads results off disk; and a **sidecar aggregator**, because its three metrics are hardcoded and the primary metric is not among them. The line is **writing code alongside the harness, never modifying it**. A later reader should not take this section as a claim that the benchmark is fully off-the-shelf.

**Reused, not rebuilt** — the existing skill-creator harness:

| Script | Job |
| --- | --- |
| `run_eval.py` | Trigger evaluation only. Does the skill description fire on a query set |
| `aggregate_benchmark.py` | A/B aggregation over `eval-N/<arm>/run-M/grading.json` discovered from the filesystem |

**New, and minimal.** The harness executes no paired runs and its aggregated metrics are hardcoded to three, none of which is LOC. Two small pieces close that gap:

- **Runner** — sets up each task × arm × rep, launches a fresh session, collects results. Stdlib only (`subprocess`, `venv`, `json`, `pathlib`).
- **Sidecar aggregator** (~40 lines) — mean/stddev/min/max over the four fields `grading.json` cannot represent: the four-way token split, `loc_handwritten`, `deps_transitive`, `acceptance_pass`.

The alternatives were forking `aggregate_results` to accept a metric list, or encoding LOC as a boolean `expectations[]` assertion. Both were rejected in `benchmark.md` §4.3 — the second would make the primary metric unmeasurable.

## 6b. Standing rule: live-probe before every batch

**No batch runs until one live call has produced the exact artifact the batch will parse.**

Static setup checks do not satisfy this. The probe must exercise the full path end to end — spawn the real subprocess, in the real working directory, with the real hook installed — and assert on the real output. A check that validates file existence, JSON shape and PATH entries can pass completely while the instrument is dead.

### Why this is a rule and not a fix

Three separate failures, all the same shape: **a well-formed result produced by a dead or unvalidated instrument.**

| # | Incident | Presented as | Actually was |
| --- | --- | --- | --- |
| 1 | Void batch | A1 22/22, A2 0/20, clean JSON | All 210 calls failed — no `claude` binary. Failed calls scored as non-triggers |
| 2 | 22/22 confound | A perfect over-trigger score | Equally consistent with an invisible skill; the positive control proved the *detector* fired, never that *that description* did |
| 3 | G2 batch 1 | 93–100% ABSENT, 0 errors | `claude -p` blocked on unredirected stdin; the runner recorded no returncode and discarded raw output, so instrument failure hid inside ABSENT |

Each was caught late, by noticing a number was too clean or a timing was too fast. None was caught by a setup check, because all three passed their setup checks.

Instance 3 is the sharpest lesson: the runner deliberately separated `ABSENT` from `DECLINE` so a compliance failure could not hide inside a correct-looking outcome — and then left a larger hole one level down, where instrument failure hid inside `ABSENT`.

### Scope — mandatory for every runner

| Runner | Probe must assert |
| --- | --- |
| **G2 runner** (`scripts/g2_runner.py`) | One real call returns a parseable `KOSHA:` verdict. Implemented; refuses the batch on `ERROR` |
| **A/B runner** (`benchmark.md` §5) | One task × one arm × one rep produces a `grading.json` **and** a `timing.json` carrying a numeric non-zero `total_tokens` — this is Run 0 (§5.3), and the silent `output_chars` fallback is exactly this failure mode |
| **Sidecar aggregator** | One `metrics.json` parses and its token buckets sum to `timing.json:total_tokens` |

### Clause 2 — the probe must accept only a POSITIVE result

**A probe passes only on the artifact the batch parses. "Not an error" is not a pass.**

The G2 no-fire set was cleared to spend 110 calls by a probe that returned `ABSENT` — the runner refused only on `ERROR`, and `ABSENT` looked survivable. It was not: the instrument was dead. The probe query is a known 5/5 `FIRE` case, so the only acceptable probe results are `FIRE` or `DECLINE`.

Generalized: if the batch's purpose is to collect X, the probe must produce an X. A probe that merely fails to crash proves nothing.

### Clause 3 — infrastructure failures arrive as valid, successful output

**Exit code and non-emptiness are not evidence of a real result.**

Three times now a failure has arrived with **exit 0 and no error count**:

| Failure | How it presented |
| --- | --- |
| Missing `claude` binary | Well-formed JSON, 22/22 pass |
| Stdin block | Clean stream, `ABSENT` |
| **Expired OAuth** | A normal assistant message, exit 0, `ABSENT` — `"Failed to authenticate: OAuth session expired and could not be refreshed"` |

The third is the sharpest: an auth failure is delivered *as model output*. Every structural check passes, because structurally nothing is wrong.

So every runner scans the response body for infrastructure strings and classifies them as `ERROR`, never as a negative outcome:

```
failed to authenticate | oauth session expired | invalid api key
rate limit | usage limit | insufficient credit | overloaded
```

And every batch reports its `ERROR` rate; above 20% the batch is void by default rather than by judgment.

> **"Zero errors" has stopped meaning what it appears to mean.** It counts only subprocess exceptions. It does not count timeouts scored as non-triggers, blocked stdin, or authentication failures rendered as prose. Any claim resting on a zero error count must say which failures that count can actually see.

### Corollaries

- **Record `returncode` and persist raw output for every run.** Batch 1's most costly gap was not the stdin bug but discarding the evidence that would have attributed it in seconds instead of after the fact.
- **A fast-failing call is `ERROR`, never a negative outcome.** Timeouts, non-zero exits and empty output are instrument events, not model behaviour.
- **Emit per-run progress.** Batch 1 was opaque from outside for its entire duration, making a stalled run indistinguishable from a slow one.

---

## 7. Verified environment — pinned

The `UserPromptSubmit` injection path has a **silent** failure mode: an open report describes the hook executing normally while `additionalContext` never reaches model context in the VS Code extension. It was verified working here (`eval/results/SENTINEL_GATE.md`), but a silent regression leaves no trace, so the passing configuration is pinned to give a future failure something concrete to diff against.

| Component | Version at PASS |
| --- | --- |
| **Date verified** | **2026-09-06** |
| VS Code | **1.136.1** (commit `a44adf7f53e0`) |
| Claude Code VS Code extension | **anthropic.claude-code-2.1.263-win32-x64** (2.1.261 also present) |
| Claude Code CLI (WSL Ubuntu) | **2.1.263** |
| WSL authentication | **`claude setup-token`** (long-lived), NOT copied credentials |
| OS | Windows 11 Home Single Language 10.0.26200 / WSL2 Ubuntu |
| Node (WSL, nvm) | v24.20.0, npm 11.19.0 |

### Authentication: WSL holds its own session

WSL authentication was originally bootstrapped by **copying `.credentials.json` from the Windows side**. That was expedient and it failed twice — the copied session is not refreshable from WSL, so it silently expires mid-campaign and every subsequent call returns an auth error *as ordinary model output* (Clause 3). It voided a 110-run batch.

The durable fix is a **WSL-native long-lived token**: `claude setup-token`, run once in an interactive WSL terminal. `/login` is unavailable non-interactively, so this cannot be automated from an agent session.

Copying credentials from Windows is **deprecated** — it is a stopgap that reintroduces a known silent failure mode, not a supported configuration.

**Re-run the sentinel test after any of these change.** `hooks/sentinel_hook.py` plus `hooks/sentinel_runs.log` reproduce the check in about a minute, and the log is what distinguishes "injection dropped" from "hook never ran" — the distinction that makes a negative result diagnosable instead of merely alarming.

---

## 8. Benchmark tooling

**Token capture** is Claude Code OpenTelemetry: `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER=console`, `OTEL_METRIC_EXPORT_INTERVAL=5000` ([docs](https://code.claude.com/docs/en/monitoring-usage)). Environment variables, not dependencies — §2 is unchanged.
