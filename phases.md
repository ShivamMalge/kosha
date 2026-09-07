# kosha — Build Phases

**Status:** draft
**Date:** 2026-09-06
**Companions:** `prd.md` (what and why) · `architecture.md` (design) · `techstack.md` (tooling) · `benchmark.md` (proof)

This is a build order, not a schedule. No implementation code here.

---

## Ordering principle

**Test the assumption that would invalidate everything else, first and cheapest.**

The riskiest thing in kosha is not the catalog or the research protocol — it is the **threshold gate**. If the gate cannot reliably fire on real work while staying silent on trivia, then every downstream component is machinery attached to a trigger nobody wants running. The gate is also the cheapest thing to test: it needs no catalog, no network, no smoke runner, and no benchmark harness.

So the gate comes first, before anything it would gate. Everything after is ordered by dependency, with the two paths (hit, then miss) built in the order that lets the cheaper one be exercised end-to-end sooner.

```
P0 close open questions
     │
P1 trigger gate  ◀── riskiest assumption, zero dependencies, hand-testable
     │
     ├──────────────┬──────────────┐
P2 catalog       P3 smoke        (ordering-free — neither blocks the other)
   substrate        runner
     │              │
     └──────┬───────┘
P4 cache-hit path
     │
P5 cache-miss path + write-back
     │
P6 catalog seeding  ◀── from real projects, NOT the benchmark domains
     │
P6.5 routing dry-run  ◀── go/no-go: ≥3 of 8 tasks must hit
     │
P7 benchmark  ◀── pre-registered; Run 0 calibration gates the batch
     │
P8 verdict
```

Every phase carries a **Stop here if** line. These are early kill points that fire before the benchmark, cheaply. The benchmark's own kill criteria (in `benchmark.md`) are the last gate, not the only one.

---

## P0 — Close the open questions

**Goal.** Resolve the four `[OPEN]` items so downstream work is not built on a guess.

| Item | Where it is raised | Why it blocks |
| --- | --- | --- |
| Threshold definition | `architecture.md` §3 | P1 is unbuildable without it. **Closed: two-of-three**; edge-case density cut for being a category, not an applicable rule |
| Catalog seeding | `prd.md` §5 | Decides whether P7's cache-hit arm exists at all. **Closed: ships seeded from real project decisions** |
| `techstack.md` at target-project repo root | `prd.md` §5 | Cheap, but P4 emits into it. **Closed: repo root** |
| Ladder margin = 0.5 | `architecture.md` §10 | Starting value with no evidence. **Still open** — blocks P5, not P1 |

**Exit.** All four written into `architecture.md` with the `[OPEN]` markers removed.

**Stop here if:** the threshold cannot be stated as a rule someone else could apply to a task list and get the same answer you would. A gate that only works when its author operates it is not a gate.

---

## P1 — Trigger gate in isolation

**Goal.** `SKILL.md` fires correctly, with no catalog, no network, no scripts behind it.

**Deliverables**
- `SKILL.md`: frontmatter, the **two-of-three** rule, the never-fire list, the ambiguity rule (borderline → do not fire), and a stub where routing will later go.
- **Three eval-set JSON files** driven by `run_eval.py`, not hand-operated sessions. Each is a flat list of `{"query": "...", "should_trigger": bool}`. Expected verdicts are recorded *before* any run.
- **Four holdout probes**, sealed (§ *Holdout* below).
- **~4 mid-implementation probe sessions**, hand-operated (§ *F4.4* below).

### The three eval sets

`run_eval.py` applies one `--trigger-threshold` to every query in a set — `should_trigger: true` passes at `trigger_rate >= threshold`, `false` passes at `< threshold`. One threshold cannot be strict in both directions, so the probes are split by direction and each set is run at a threshold that makes its own criterion strict. Same configuration as `benchmark.md` §2, so P1 and P7 use one instrument.

| Set | Contents | `--runs-per-query` | `--trigger-threshold` | Passes only at |
| --- | --- | --- | --- | --- |
| `no-fire.json` | slugify helper, wiring two existing functions, project-specific pricing rules, a domain already covered by a project dependency, a 20-line adapter | 5 | **0.01** | 0 fires / 5 |
| `must-fire.json` | retry/backoff, layered CLI config, tabular validation, rate-limited HTTP client, Rust async retry, typed CSV parsing | 5 | **0.99** | 5 fires / 5 |
| `borderline.json` | ~50-LOC date-range helper with real timezone edges; a small state machine; a bespoke-but-large config merge | **15** | 0.5 | rate ≤ 0.2 or ≥ 0.8 |

This replaces the 48 hand-operated runs of the earlier plan. It is cheaper, stricter, and reproducible.

### Borderline is scored, not just observed

The borderline set makes no claim about *which* verdict is right — only that the gate returns the same one. That is falsifiable, so it carries a band rather than being descriptive.

It runs at **15** reps because at 5 the band is close to noise: a genuinely coin-flipping gate escapes "≤ 0.2 or ≥ 0.8" **37.5%** of the time. At 15, a true p = 0.5 gate escapes **3.52%** of the time and a consistent p = 0.9 gate is falsely flagged **5.56%**. The extra reps execute no tasks and cost almost nothing. `benchmark.md` §2 states the same band and the same reps.

**Log subprocess errors.** Failed or throttled calls count as non-triggers, dragging `trigger_rate` toward 0 — a throttled batch looks like a confidently-silent gate. Keep `--num-workers` low (2) and record the error count beside every trigger rate. Non-zero errors invalidate a pass and it is re-run.

### F4.4 needs a different probe shape

F4.4 is "never fires mid-implementation," which is a property of **session state**, not of a query string. `run_eval.py` takes the query and nothing else, so session state cannot be expressed in an eval set at all — every probe above is a planning scenario and none of them test F4.4.

So F4.4 gets **~4 hand-operated sessions**: each already several turns deep into writing an implementation, at which point a component crosses the size and complexity bar. The gate must stay silent. Small enough to run by hand, and there is no mechanism that would automate it.

### Holdout

The gate and the probes have the same author, and tuning the gate against probes that author wrote fits it to its own assumptions.

**Four holdout probes, one per eligible repo** — derived from what each project actually resolved in shipped code, not invented scenarios. They are **sealed until the final round** and are not inspected before then.

The source list changed after the graded-eligibility rule: **Verity and Prahari were excluded** (documentation only, no code), and the set became **LighteningParser, DevScout, Batchbird (grade B), swarm_drone_framework**. Provenance and per-probe independence weighting: `eval/results/HOLDOUT_PROVENANCE.md`.

**The gate must separate the holdout on first exposure.** Tuning after the holdout is opened collapses it back into the fitted set and forfeits the only unbiased signal in P1.

**Exit criteria**
- `no-fire.json` passes at threshold 0.01 with zero subprocess errors. Retires the pre-benchmark half of `prd.md` **F4.1**.
- `must-fire.json` passes at threshold 0.99. Retires the pre-benchmark half of **F4.3**.
- Every `borderline.json` query lands ≤ 0.2 or ≥ 0.8. A rate in between is a defect regardless of which verdict is right.
- All ~4 mid-implementation sessions stay silent. **F4.4** — the only place it is exercised before P7.
- The four holdout probes separate correctly **on first exposure**, with no tuning afterward.
- Non-fire cost measured and at or under **300 tokens** — `prd.md` **F4.2**. Measured cost is ~260 (compact gate 246 + verdict line ~14), so the bound carries ~15% headroom: enough for wording drift, not enough to absorb a regression.

**Risk burned down.** The single assumption capable of making the whole design unwanted.

### Two tuning budgets, drawn separately

P1 tunes two different artifacts, and they must not share a budget.

| Budget | Tunes | Fixes | Counts against the two-round limit? |
| --- | --- | --- | --- |
| **Description scope (G1)** | the frontmatter description | the skill fails to load, or loads on the wrong things | **No** — but capped at **3 rounds total** (see below) |
| **Threshold rule (G2)** | the two-of-three rule in the `SKILL.md` body | the skill loads and then decides wrongly | **Yes** |

The two-round limit was written about the **threshold rule**. Spending it on description scope would trip the kill criterion without the rule ever having been tested — failing the project for a defect in a different artifact.

A1 and A2 measure **G1 only** (`benchmark.md` §2), so **no A1/A2 result may consume a threshold-rule round.** Description work draws on its own budget and may use `improve_description.py` and `run_loop.py`, whose stratified train/test split guards the automated loop against overfitting.

#### The G1 budget is bounded: 3 rounds, then a decision

Description work has no natural stopping point — there is always another phrasing to try — so the limit is written here as a rule rather than left as an intention.

**Three G1 rounds total.** **CLOSED 2026-09-06 at 1 of 3 used — the remaining two are unspent by decision, not by exhaustion.** The CLAUDE.md probe established a ~47% ceiling for model-mediated triggering against a criterion requiring 100%, so further description rounds were judged not worth their cost (`prd.md` §6b). Reopening the G1 budget requires reopening that decision.

At exhaustion, no fourth round. One of two things happens instead:

1. **Accept autonomous triggering as measured**, recording the achieved load rate as a known ceiling and adjusting F4.3 to match what the mechanism can actually deliver; or
2. **Switch to deterministic invocation** — a `CLAUDE.md` directive, a slash command, or a hook — with the skill as the *payload* rather than the *trigger*.

Under (2) the catalog, rubric, smoke runner, graded seeding and benchmark design are all unaffected; only the trigger mechanism changes. F4.1 becomes near-trivial because the body's two-of-three rule does all the gating, and G2 finally gets exercised.

**The sealed holdout stays sealed throughout description work.** It exists to test the *rule's* generalization to real tasks, not the description's. It is not opened, not referenced, and never exposed to `run_loop`.

**Stop here if:** the **threshold rule** cannot separate the probe set after two rounds of tuning. Not "tune it again" — a rule that needs a third round of hand-fitting against known cases will not generalize to unseen ones, and the design needs rethinking rather than adjusting. A holdout failure after the fitted sets pass is the same signal, arriving later and more credibly.

---

## P2 — Catalog substrate

*Ordering-free with respect to P3 — either order, no dependency either way. "Parallel" would require two sessions; this only claims neither blocks the other.*

**Goal.** The catalog can be written, parsed, linted, and aged — before anything writes to it automatically.

**Deliverables**
- `catalog/SCHEMA.md`
- `catalog/INDEX.md` with 2–3 hand-authored rows
- Two **hand-authored** domain files: one with an adopted entry plus rejections, one with rejections only (a domain where "write it yourself" won). The second matters more than the first — it is the case that proves the schema can express a negative result.
- `scripts/catalog_lint.py`, `scripts/staleness_check.py`
- **The catalog under version control**, with every entry recording the `rubric_version` its scores were produced under (`architecture.md` §5). Entries are scored artifacts, not just notes: a later tune that changes gates, weights, or the ladder margin invalidates everything scored under the old rubric, and without a version stamp there is no way to tell which entries those are.

**Exit criteria**
- Every fenced TOML block round-trip parses under `tomllib`. Validates the write-asymmetry decision in `techstack.md` §3.
- Lint fails, as designed, on: a missing `smoke_verified_version` on an adopted entry (**F2.1**), a missing `stdlib` rejection (**F1.1**), an over-cap domain file, an orphan index row.
- `staleness_check.py` correctly reports tier expiry against hand-set dates, including the boundary days (29/30/31, 89/90/91).
- **Fault injection for F3.3:** expire Tier A on a seeded entry, run partial re-verification by hand, diff the entry. Stable facts and rejection reasons must be byte-identical afterward.
- **Regeneration dry-run:** change a rubric weight, bump `rubric_version`, and recompute every entry offline from stored raws (`architecture.md` §6, tier 1). No network call may be needed. This is the check that the *scored rejections* carry their per-criterion values — without them you can recompute the winner and nothing it beat, which is not a re-ranking.

**Stop here if:** entries cannot be authored by hand in a few minutes each. If the schema is tedious for a human, the write-back step in P5 will be skipped under pressure and the catalog will never accrete.

---

## P3 — Smoke runner

*Ordering-free with respect to P2 (see above).*

**Goal.** `scripts/smoke_test.py` produces trustworthy raw evidence about a real API.

**Deliverables**
- PyPI path: temp venv → pinned install → run snippet → raw stdout/stderr/exit code
- crates.io path: temp cargo crate → pinned dependency → `cargo run`
- POSIX venv/cargo paths only (development moved to WSL Ubuntu)

**Exit criteria**
- **The negative case is the important one.** A snippet written against a deliberately wrong API — a decorator that does not exist, an argument renamed three versions ago — must exit non-zero and surface the real traceback. A runner that only ever reports success proves nothing about **F2**.
- Raw output is emitted verbatim. The script contains no notion of pass or fail, and no summarization. Enforces the raw-output rule in `architecture.md` §7.4.
- Both ecosystems run in a temp directory and leave the target project untouched.
- Version resolution is reported, so what was tested is unambiguous even when the install resolved something other than requested.

> **DEFERRED, not solved: Windows support for the smoke runner.** An earlier draft of P3 required `Scripts\` vs `bin/` path resolution because development was on native Windows. Development moved to WSL Ubuntu (`run_eval.py` uses `select()` on a pipe, which is POSIX-only), so that work item is out of P3's scope — **not because it was done, and not because it stopped mattering.**
>
> If kosha is ever used by anyone but its author, Windows support for `smoke_test.py` returns as its own problem: venv binaries under `Scripts\`, `.exe` suffixes, and `CreateProcess` not resolving `.cmd` from PATH — the same class of issue that forced the move. Recorded now while the reason is fresh, so a later reader does not read its absence as evidence it was handled.

**Stop here if:** isolated installs are too slow or too flaky to sit inside a planning turn. That would make **F5** unwinnable on the miss path regardless of how good the research is, and the design would need an offline evidence strategy instead.

---

## P4 — Cache-hit path end-to-end

**Goal.** The cheap path works completely: gate → index → domain match → staleness → recommendation → `techstack.md`.

**Deliverables**
- Routing from `SKILL.md` into `INDEX.md`, keyword matching into one domain file
- `references/techstack-template.md` and `references/smoke-test-protocol.md`
- Step 6 of `architecture.md` §7.2: consult the **project manifest** before emitting a cached answer

**Exit criteria**
- A hit emits a `techstack.md` carrying the decision, the cached rejections, smoke evidence, and verification dates.
- Measured hit cost is inside the ~3,400-token estimate. Early read on **F5.2**.
- Only the matched domain file loads. Verified by inspection — this is the observable proof that progressive disclosure is real and not just a directory layout.
- Step 6 demonstrably flips the answer when the project already depends on something covering the domain.
- **F3.5:** with the network unavailable, a stale entry still produces a recommendation, and the staleness appears in `techstack.md` rather than being silently dropped.
- **F3.2:** hand-edit an entry so its major version trails `smoke_verified_version`; confirm escalation invalidates `api_shape` and forces a smoke re-run.

**Stop here if:** hit cost lands near miss cost. The entire economic argument is the ratio between them; without it, caching is bookkeeping.

---

## P5 — Cache-miss path and write-back

**Goal.** Research, score, verify, recommend, and — critically — persist.

**Deliverables**
- `references/rubric.md` (gates, weights, 0–5 anchors, ladder margin, threshold 3.2)
- `references/research-protocol.md` (source order, caps, stop conditions)
- Write-back: create the domain file, add the adopted entry plus one rejection per eliminated candidate, add the index row, run lint, split on cap breach

**Exit criteria**
- Gates eliminate before scoring, and every elimination is recorded with which gate failed.
- The stdlib and hand-rolled are candidates in **every** pass (**F1.1**), with an LOC estimate on the hand-rolled option.
- **The ladder margin is observed to change an outcome at least once.** A margin that never flips a decision is not implemented, only documented. This is the pre-benchmark read on **F1.4**.
- A pass that recommends no library completes normally and writes a catalog entry. A negative result must be a first-class outcome, not an error path.
- A non-zero smoke exit rejects the candidate and advances to the next-ranked one (**F2.3**), capped at 3 attempts.
- `api_shape` is written from raw smoke output. Verified by spot-check against the actual library — this is the last place a hallucinated API can enter the system.
- Research caps hold: 6 candidates, 12 fetches, 3 smoke attempts.
- Measured miss cost recorded against the 14k–22k estimate. Feeds **F5.3**.

**Risk burned down.** Write-back is the step most likely to be quietly skipped once the answer is in hand — and skipping it means research is paid every time, which is precisely the failure **F5** describes.

**Stop here if:** measured miss cost exceeds the top of the estimate by more than about 50%. That pushes the break-even hit count somewhere implausible, and the caps need to bind harder before spending a benchmark on it.

---

## P6 — Catalog seeding

**Goal.** Seed the catalog from stack decisions **already made and shipped in existing projects**, and let the benchmark tasks hit or miss naturally.

**Why not seed the benchmark domains.** The earlier plan seeded the six library-available benchmark domains by running the P5 miss path on those exact domains, then measured P7's `with_skill` arm on those same tasks. Every task would have been a guaranteed hit against an entry generated for that precise task: 100% hit rate, perfect domain match, none of the partial matches, adjacent domains, or nearly-fitting index keywords that make up real use. That measures the theoretical ceiling, not steady-state performance.

### Source eligibility — graded, not gated

Evidence strength is a **gradient**, not a completion checkbox. Gating on "is the project finished" would reject a real decision for the unrelated reason that the surrounding project stalled, and a dependency you chose and then wrote code against is a made decision whether or not the project ever shipped.

| Grade | Evidence | Use |
| --- | --- | --- |
| **A — shipped / published** | Released or deployed; the choice survived users | Strongest. Seed freely |
| **B — working code** | Dependency in a manifest *and* used by code that runs, project unfinished | Seed. Record the grade on the entry |
| **— documentation only** | Named in a PRD, architecture doc, or plan; no code | **Not evidence.** Never seed |

The line is between a decision **made** and a decision **described**. Documentation records intent, and intent has not been tested against anything.

**Known determinations** (survey of 2026-09-06, not to be re-litigated):
- **Prahari — excluded.** Five markdown files, zero code files. Documentation only, on its own evidence.
- **Verity — excluded.** Not built; documentation suite, no code.
- **Batchbird — grade B, eligible.** Working Rust with dependencies in actual use. Unfinished, which is irrelevant under a graded rule. It is **not** the Verity/Prahari case.
- **Aakar — eligible (corrected 2026-09-07).** An earlier survey recorded "no manifest found" and excluded it. That was a **search-depth artifact**: `services/api/pyproject.toml` and `apps/web/package.json` sit at depth 4–5, and the survey searched to depth 3. 5,472 `.py` files. Added to the eligible pool.

> **How the correction was found matters.** The manifests surfaced during holdout derivation — a task that was not a source-list decision. The finding is recorded here so the pool is correct, but the source list itself **stays parked**: a repo does not enter the seeding set as a side effect of some other task noticing it. P6 settles the list deliberately or not at all.

Entries carry their source grade so a later reviewer can weigh a B-grade seed differently from an A-grade one without re-deriving where it came from.

**Deliverables.** Entries for the domains the eligible projects actually resolved, each produced by running the **P5 miss path for real** — not hand-written. Hand-seeding would test the schema, not the pipeline.

**Exit criteria**
- Domains seeded from real project decisions, lint clean, every adopted entry carrying smoke evidence, a stdlib rejection, and a `rubric_version`.
- Scored rejections carry their per-criterion raws (P2's regeneration dry-run covers the mechanism; this confirms it on real data).
- Every domain file inside its size cap — 340 lines / 6 entries (`architecture.md` §4).
- **A benchmark task that misses is recorded as a finding, not retried into a hit.** Catalog coverage transferring across projects is the property this seeding exists to measure, and a miss is evidence about it.

**Stop here if:** seeding produces recommendations that contradict what an **eligible** project actually chose in code, without a reason you accept on review. That is rubric miscalibration measured against decisions that survived contact with a running system.

The check is scoped to eligible sources by necessity — "contradicts what the project chose" is unevaluable against a project that only described its intentions. For a documentation-only source there is no decision to contradict, so it provides no signal in either direction.

---

## P6.5 — Routing dry-run (P7 entry gate)

**Goal.** Learn the hit/miss distribution *before* spending 48 runs on it.

The revert carries a risk: if seeding from four real projects yields only one or two natural hits across the eight benchmark tasks, F5.2 has n = 1 and the cache-hit economic argument goes unmeasured — discovered after the batch instead of before.

**Method.** Run all eight benchmark tasks through **routing only** — gate plus index match. No research, no smoke test, no implementation. Nearly free.

**Go/no-go, pre-registered: at least 3 of 8 tasks must route to a hit.** Basis, stated so it is not re-litigated later: three hits at three reps is nine runs, the minimum that gives F5.2 any variance estimate at all. Arbitrary and declared.

> **Noted against this gate, not acted on** (survey of 2026-09-06): no eligible source surveyed so far uses a retry/backoff library — no `tenacity`, `backoff`, or `backon`. If that holds, **T1 and T5 would miss**, while Batchbird's `csv` and DevScout's `click`/`pydantic-settings` suggest T6 and T2 as likely hits. That is roughly 2–3 hits against a bar of 3, before the source list is settled. Recorded so the gate is not a surprise. **No action now** — P6 does not happen at all if P1 fails its *Stop here if*.

**If the bar is missed**, remedies in order:
1. Broaden seeding to **more real-project domains**.
2. Accept F5.2 as unmeasurable in this batch and report it as such.

**Seeding the benchmark domains is not a remedy.** It is the contamination P6 removed, arriving disguised as a fix.

**Stop here if:** neither remedy is acceptable. Running the batch anyway produces 48 runs that cannot answer F5.2, at full cost.

---

## P7 — Benchmark

**Unblocked.** Harness interface confirmed; `benchmark.md` is written and pre-registered.

**Goal.** Measure F1–F5 against a skill-off arm.

**Deliverables**
- The three trigger eval sets: `no-fire.json`, `must-fire.json`, `borderline.json`
- The runner (`benchmark.md` §5) — the only substantial new code the harness gap justifies
- The sidecar aggregator over `metrics.json` (~40 lines, four fields the aggregator's schema cannot represent)
- Task fixtures for T1–T6, C1, C2, each with **supplied** acceptance tests

**Shape.** Two instruments: `run_eval.py` for triggering (three passes at different thresholds, since one threshold governs both directions), `aggregate_benchmark.py` for the A/B. 48 primary runs with `kosha_path` **measured per run**, plus 3–9 induced supplementary runs (COLD only where no natural miss occurred, STALE always induced), all `with_skill` only.

**Exit criteria**
- **P6.5 go/no-go cleared**, and **Run 0 calibration passes** (`benchmark.md` §5.3) — verifying that real tokens reach the aggregate rather than a silent character-count fallback. Nothing else in P7 starts until this holds.
- Batch validator clean on every tree.
- Primary metric computed at constant acceptance and **stratified by measured `kosha_path`** (`benchmark.md` §7.1); the pooled figure is reported only as a labelled blend and no kill criterion reads from it.
- N\* computed and published with its inputs.
- Every result reported as raw per-rep values alongside summary statistics.

**Stop here if:** Run 0 cannot be made to capture tokens reliably. That is `benchmark.md` M2 — fix the instrument before spending the batch on it.

---

## P8 — Verdict

**Goal.** Decide against evidence: ship, tune, or scrap.

**Inputs.** All F1–F5 criteria measured with variance, stratified by measured path; the computed break-even hit count from **F5.3**; kill criteria evaluated against real data; and a negative result meeting the standard below.

### The negative-result requirement

**The negative must appear on a task not constructed to produce one — T1–T6, not C1 or C2.**

The earlier wording ("at least one clearly negative result somewhere in the task set") was vacuous: C1 is *designed* to produce a negative, so the requirement auto-satisfied and constrained nothing. That is the same failure the F4.1/F4.3 pairing exists to prevent — a criterion a degenerate result passes for free.

C1 producing a negative is the instrument working as designed and says nothing about the skill. A benchmark task that **misses naturally** (P6.5) and shows no LOC benefit counts, as does any T1–T6 task where the skill-on arm is neutral or worse.

**Outcomes**
- **Ship** — criteria met, break-even plausible, and a qualifying negative present and explicable.
- **Tune** — a specific criterion missed with a specific cause. Return to the owning phase, not to P0.
- **Scrap** — kill criteria met.

### A tune that touches the rubric triggers regeneration

Changing gates, weights, anchors, or the ladder margin invalidates every catalog entry scored under the old `rubric_version`. Such a tune ships with a regeneration pass (`architecture.md` §6): recompute offline from stored raws where the change permits it, re-verify only the new fact where a gate or dimension was **added**, and **re-decide any entry whose recomputed score crosses the recommend threshold in either direction** rather than silently keeping it.

A tune that leaves stale-scored entries in the catalog has fixed the rubric and corrupted the cache — F3 by another route.

---

## Criteria coverage map

Where each `prd.md` acceptance criterion is first exercised. Everything not retired earlier lands in P7 — which is the argument for the phase ordering: the benchmark should confirm, not discover.

| Criterion | First exercised | Confirmed |
| --- | --- | --- |
| F1.1 stdlib always evaluated | P2 (lint) | P5, P7 |
| F1.2 transitive count bound | P5 | P7 |
| F1.3 justification above 15 deps | P5 | P7 |
| F1.4 ladder actually declines | P5 (margin flips an outcome) | P7 |
| F2.1 smoke evidence on every adoption | P2 (lint) | P6 |
| F2.2 raw output surfaced | P3 | P7 |
| F2.3 non-zero exit rejects | P3, P5 | P7 |
| F2.4 no hallucinated-API failures | P5 | P7 |
| F3.1 Tier A freshness or disclosure | P2 | P4 |
| F3.2 major-version escalation | P4 (fault injection) | — |
| F3.3 partial re-verify preserves stable | P2 (fault injection) | — |
| F3.4 re-verify ≤ 30% of cold cost | P5 | P7 |
| F3.5 offline still answers | P4 | — |
| F4.1 no fire on trivia | P1 (`no-fire.json`, thr 0.01) | P7 (C2) |
| F4.2 non-fire cost bound | P1 | P7 |
| F4.3 always fires when it should | P1 (`must-fire.json`, thr 0.99) | P7 (T1–T6) |
| F4.4 never fires mid-implementation | P1 — **4 hand-operated two-turn sessions, 4/4 pass**, each citing the timing clause explicitly. The same turn-2 requests fire at **87–100% in fresh context**, so the probe demonstrates *inversion under session state*, not merely silence. Session state cannot be expressed in a `run_eval.py` eval set | P7 |
| F5.1 **primary** — LOC avoided | — | **P7 only** |
| F5.2 hit cost bound | P4 | P7 (**conditional on P6.5** — needs ≥ 3 natural hits to be measurable) |
| F5.3 miss cost and break-even | P5 | P7 |
| F5.4 C1 pure overhead | — | **P7 only** |
| F5.5 acceptance not degraded | — | **P7 only** |

Three criteria — F5.1, F5.4, F5.5 — cannot be exercised before P7 by construction. They are comparative: each requires a skill-off arm to compare against. That is the irreducible reason the benchmark cannot be skipped.

One criterion is now **conditional** rather than merely deferred: F5.2 needs natural cache hits, and since P6 no longer seeds the benchmark domains, whether there are enough of them is discovered at P6.5 rather than assumed. That is the cost of the honest seeding, paid deliberately — a guaranteed-hit catalog would have made F5.2 trivially measurable and meaningless.
