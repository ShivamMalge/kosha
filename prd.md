# kosha — Product Requirements

**Status:** draft
**Date:** 2026-09-06
**Scope of this document:** what kosha must do and what "working" means. Design lives in `architecture.md`; proof lives in `benchmark.md`.

---

## 1. Problem

Coding agents reimplement solved problems. Asked to add retry-with-backoff, an agent writes sixty lines of sleep-loop with a jitter bug rather than reaching for a library that has been correct for a decade. Asked to validate a dataframe, it writes a column-by-column assertion cascade. The reimplementation usually passes the tests it was written against, so nothing in the loop catches it.

The failure is not ignorance. The agent generally *knows* the library exists. The failure is one of sequencing and cost: at the moment implementation starts, writing the loop is the path of least resistance, and checking what exists costs a research detour with uncertain payoff. So the check never happens.

The naive fix — "always search for a library first" — trades one failure for three worse ones: dependency bloat, hallucinated APIs asserted with confidence, and research overhead on tasks where a library was never the answer. kosha only helps if it avoids all three.

## 2. What kosha is

A Claude Code skill that fires **at planning time**, before implementation begins, for **components above a size/complexity bar**. It consults a local curated catalog of libraries. On a hit, it answers immediately from cache. On a miss, it researches PyPI / crates.io / GitHub, scores candidates against a fixed rubric, **executes a smoke test against the real API**, writes a per-project `techstack.md`, and caches the finding — adoptions *and* rejections — back into the catalog so the research cost is paid once per domain, not once per project.

### Governing bias

kosha's default answer is **no new dependency**. The preference ladder, in order:

```
stdlib  >  small focused package  >  write it yourself  >  large framework
```

A recommendation must beat everything to its left, not merely be usable. "Write it yourself" outranking a large framework is deliberate: a framework that solves your problem plus forty others imposes its own architecture on the project, and that cost does not show up in a line count.

## 3. Users

| User | Need |
| --- | --- |
| Agent operating in a project | A fast, cheap, correct answer to "is this already solved" at the moment the plan is drafted |
| Human reviewing the plan | A written, auditable rationale — including what was rejected and why — before code exists |
| Maintainer of the catalog | Entries that decay predictably instead of silently going wrong |

## 4. Scope

### In scope

- A planning-time trigger with an explicit threshold gate, including an explicit definition of when **not** to fire.
- A curated local catalog under progressive disclosure: a thin always-loaded index plus per-domain files loaded only on match.
- Catalog entries that separate **rotting facts** (version, last release, downloads, open issues, stars) from **stable facts** (license, API shape, decision rationale, rejection reasons).
- Research on cache miss across **PyPI and crates.io**, with GitHub as the corroborating source for maintenance signals.
- A two-tier rubric: hard pass/fail gates, then a weighted score over survivors.
- A mandatory executed smoke test against the real API of the top candidate, reported as raw output.
- A per-project `techstack.md` recording the decision, the rejected alternatives, and the verification dates.
- Write-back of findings — adoptions and rejections both — into the catalog.

### Out of scope

| Not in scope | Why |
| --- | --- |
| Installing dependencies into the target project | kosha recommends and evidences; the human or the implementing agent installs. Separating the two keeps kosha's output reviewable before it is irreversible. |
| Mid-implementation rescue | A trigger that fires while code is being written produces rewrites, not decisions. Explicitly excluded by design (§6, F4). |
| Continuous dependency monitoring, CVE watch, upgrade PRs | That is Dependabot's job, and it is a runtime concern rather than a planning concern. |
| Architecture-level selection (which web framework, which database, which queue) | These are governed by team standards, deployment constraints, and existing infrastructure — none of which a library rubric can see. kosha targets component-level choices. |
| npm / Go / Maven ecosystems | v1 is PyPI + crates.io. Each ecosystem multiplies smoke-runner surface; adding one is a v2 decision made on evidence, not up front. |
| General-purpose web research | The research path is narrow and protocol-bound. kosha is not a browsing skill. |

## 5. Assumptions requiring confirmation

Marked so they are not mistaken for settled decisions.

- **[OPEN] Threshold definition.** Proposed in `architecture.md` §3 as a two-of-four rule over estimated LOC, domain recognizability, edge-case density, and whether the component would need its own test suite. Not yet confirmed.
- **[OPEN] Catalog seeding.** Whether the catalog ships with curated entries or starts empty and accretes. The benchmark's cache-hit arm is only meaningful if seeded; assumed seeded with the benchmark domains.
- **[OPEN] `techstack.md` location** in the target project. Assumed repo root.

Confirmed and closed: rubric structure (hard gates + weighted score), staleness policy (tiered by fact volatility), benchmark task set (8 tasks, Python + Rust).

---

## 6. Failure modes and acceptance criteria

These are the five ways kosha can be worse than nothing. Each has criteria that can actually fail. Measurement columns reference `benchmark.md` where applicable.

### F1 — Dependency bloat

**What it looks like:** kosha recommends a library for something the stdlib already does, or recommends a 40-dependency framework where a zero-dependency package would do. Net effect: the project carries weight it did not need, and kosha caused it.

**Why it happens:** a rubric that rewards "solves the problem" without penalizing what the solution drags in. Adoption metrics favor large popular frameworks over small correct ones.

**Mitigations:** the preference ladder is a scoring rule, not advice — `dep_weight` carries weight 2 and is computed from the actual transitive count; the stdlib is evaluated as a mandatory candidate in every research pass; "write it yourself" is a legitimate recommendation and must be recorded as such in the catalog.

**Acceptance criteria**

| # | Criterion | How measured |
| --- | --- | --- |
| F1.1 | The stdlib is explicitly evaluated and its rejection reason recorded in every research pass that recommends a package. | Catalog audit: every `status: adopted` entry has a `rejected_alternatives` item with `id = stdlib`. 100%, no exceptions. |
| F1.2 | Across the benchmark's library-available tasks, mean transitive dependency count added by the skill-on arm is at most 5. | `deps_transitive` per run, `benchmark.md` |
| F1.3 | No recommendation whose transitive count exceeds 15 without an explicit written justification in `techstack.md`. | Catalog + `techstack.md` audit |
| F1.4 | kosha recommends "write it yourself" or "stdlib" on at least one benchmark task — i.e. the ladder is load-bearing and not decorative. | Benchmark run inspection; control task C1 is the expected trigger |

> F1.4 is the criterion that stops the rubric from degenerating into a library-recommendation machine. If kosha never declines to add a dependency, it is not applying the ladder.

### F2 — Hallucinated APIs

**What it looks like:** kosha recommends a real library with an invented API — a decorator that does not exist, an argument renamed three versions ago, a module path that was never real. The plan looks authoritative and the implementing agent inherits the error.

**Why it happens:** model priors about library APIs are stale and confidently wrong, and a plan document is exactly the artifact where nothing executes to contradict them.

**Mitigations:** no candidate is recommended without an **executed** smoke test against the installed library. The smoke runner emits raw stdout, stderr, and exit code; self-reported success is not accepted as evidence. The `api_shape` stable fact is populated *from* the smoke test, never from recall. A major version bump invalidates `api_shape` and forces a re-run (`architecture.md` §6).

**Acceptance criteria**

| # | Criterion | How measured |
| --- | --- | --- |
| F2.1 | Every `status: adopted` catalog entry carries a smoke-test snippet and the exact version string it was verified against. | `catalog_lint.py` — hard failure, not a warning |
| F2.2 | Every recommendation surfaced to the user includes raw smoke-test output (exit code plus captured streams) in the transcript. | Benchmark transcript inspection, all skill-on runs |
| F2.3 | Zero recommendations pass through on a non-zero smoke exit code. On failure, the candidate is rejected and the next-ranked one is tested. | Smoke runner contract; benchmark transcript audit |
| F2.4 | Across all skill-on benchmark runs, zero acceptance-test failures attributable to an API that does not exist as described. | `acceptance_pass` plus failure triage, `benchmark.md` |

> F2.3 is the criterion most likely to be quietly violated under time pressure, because a failing smoke test is inconvenient at exactly the moment the answer seems obvious. It is stated as zero-tolerance for that reason.

### F3 — Stale cache

**What it looks like:** the catalog confidently reports a version from eighteen months ago, a maintenance status that has since collapsed, or an API shape that a major release changed. Cached wrongness is worse than no cache, because it is asserted without the hedging that fresh uncertainty carries.

**Why it happens:** a single staleness window applied to facts that rot at very different rates — or no window at all.

**Mitigations:** tiered expiry (`architecture.md` §6). Tier A (`latest_version`, `last_release`) expires at 30 days; Tier B (`downloads_30d`, `open_issues`, `stars`) at 90 days; stable facts never auto-expire. Expiry triggers **partial** re-verification of the expired fields only — never a full re-research, which would destroy the caching benefit. A major-version delta escalates: it invalidates `api_shape` and forces a smoke re-run.

**Acceptance criteria**

| # | Criterion | How measured |
| --- | --- | --- |
| F3.1 | No recommendation is made from a Tier A field older than 30 days without either re-verifying it or stating the staleness explicitly in `techstack.md`. | `staleness_check.py` plus `techstack.md` audit |
| F3.2 | A detected major-version bump always invalidates `api_shape` and forces a smoke re-run before the entry is reused. | Fault injection: hand-edit an entry to an old major, confirm the re-verification path executes |
| F3.3 | Partial re-verification touches only expired fields; stable facts and rejection reasons survive unchanged. | Fault injection: expire Tier A on a seeded entry, diff the entry before and after |
| F3.4 | Re-verification of a stale entry costs materially less than a cold research pass. Target: at most 30% of cold-miss token cost. | Token deltas, `benchmark.md` |
| F3.5 | With no network available, a stale entry is still usable, and the staleness is surfaced rather than silently ignored. | Offline run inspection |

### F4 — Over-triggering

**What it looks like:** kosha fires on a five-line string helper and spends four thousand tokens confirming that yes, you should write the five lines. Every false fire is pure tax, and enough of them make the skill something users disable.

**Why it happens:** trigger descriptions written to maximize recall. A skill that fires on "any implementation task" is trivially easy to write and useless.

**Mitigations:** the threshold gate is evaluated *before* the catalog index loads, so a non-fire costs the SKILL.md body and nothing else. The gate carries an explicit never-fire list (glue code, config wiring, project-specific business logic, anything under roughly 30 LOC, and any domain the project already has a dependency for).

**Acceptance criteria**

| # | Criterion | How measured |
| --- | --- | --- |
| F4.1 | On the trivial control task (C2), the trigger does not fire in **any** repetition of the skill-on arm. | Benchmark C2, all reps — a single fire fails this criterion |
| F4.2 | Token cost of a correct non-fire is at most 1,500 tokens above the skill-off baseline for the same task. | Fresh, cache-read and output token deltas, `benchmark.md` |
| F4.3 | Under-trigger counterpart: on the six library-available tasks, the trigger fires in every repetition. A gate tuned to never fire passes F4.1 vacuously. | Benchmark T1–T6, all reps |
| F4.4 | The trigger never fires once implementation has begun in a session. | Transcript inspection across all skill-on runs |

> F4.1 and F4.3 are stated as a pair on purpose. Either one alone is trivially satisfiable by a degenerate gate; both together constrain it.

### F5 — Research costing more than it saves

**What it looks like:** the skill works exactly as designed and is still not worth running, because a cold research pass costs more than writing the code would have. This is the most likely way kosha fails: not by being broken, but by being uneconomic.

**Why it happens:** research is unbounded by nature. Each additional candidate, each additional fetch, each additional smoke test is locally justifiable.

**Mitigations:** research is protocol-bound and capped (candidate ceiling, fetch ceiling, one smoke test on the top candidate with fallback to the next only on failure). Caching amortizes the cost across projects — which is the entire economic argument, and is therefore the thing the benchmark must actually test rather than assume.

**Acceptance criteria**

| # | Criterion | How measured |
| --- | --- | --- |
| F5.1 | **Primary.** On library-available tasks, hand-written implementation LOC is materially lower in the skill-on arm with acceptance held constant. Target: at least 40% mean reduction. | `loc_written` where `acceptance_pass` is true, `benchmark.md` |
| F5.2 | Cache-hit path total token cost is at most 5,000 tokens above the skill-off baseline. | Token deltas, `benchmark.md` |
| F5.3 | Cold-miss path token cost is bounded and reported. A cold miss is permitted to be expensive, but its cost must be recovered within a stated number of subsequent hits. That break-even count is computed and published, not asserted. | Cold-miss vs. hit token deltas, `benchmark.md` |
| F5.4 | On the no-good-library control (C1), skill-on overhead relative to skill-off is bounded and stated. This measures pure waste, and it is expected to be non-zero. | Benchmark C1, all reps |
| F5.5 | Acceptance-test pass rate in the skill-on arm is no worse than skill-off. LOC reduction bought with broken code is not a win. | `acceptance_pass`, `benchmark.md` |

> **Why LOC is the primary metric and tokens are secondary.** Tokens are a cost paid once, by one session, and are falling. Hand-written code is a liability carried for the life of the project: it is reviewed, tested, debugged, ported, and maintained by people. A skill that spends 20k extra tokens to avoid 200 lines of hand-rolled retry logic is a clear win even though the token line looks bad. The inverse — fewer tokens, same code written — is no win at all. Tokens are therefore reported and bounded (F5.2, F5.3, F5.4) but never traded against LOC. The full justification and the constant-acceptance condition are in `benchmark.md`.

---

## 7. Definition of done

kosha v1 ships when:

1. All F1–F5 acceptance criteria are measured, with results reported including variance rather than as single numbers.
2. The benchmark produces at least one clearly negative result somewhere in the task set — most likely on C1 — demonstrating that the design is capable of failing.
3. Kill criteria (defined in `benchmark.md`) have been evaluated against real data and not met.

## 8. Related documents

- `architecture.md` — layout, control flows, catalog schema, staleness rules, token budget
- `techstack.md` — kosha's own tooling
- `benchmark.md` — experimental design, metrics, kill criteria
- `phases.md` — build order, exit criteria, early kill points
