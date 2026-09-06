# kosha — Build Phases

**Status:** draft
**Date:** 2026-09-06
**Companions:** `prd.md` (what and why) · `architecture.md` (design) · `techstack.md` (tooling) · `benchmark.md` (proof, pending harness)

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
P2 catalog       P3 smoke        (P2 and P3 are independent — parallelizable)
   substrate        runner
     │              │
     └──────┬───────┘
P4 cache-hit path
     │
P5 cache-miss path + write-back
     │
P6 catalog seeding
     │
P7 benchmark  ◀── BLOCKED on harness confirmation
     │
P8 verdict
```

Every phase carries a **Stop here if** line. These are early kill points that fire before the benchmark, cheaply. The benchmark's own kill criteria (in `benchmark.md`) are the last gate, not the only one.

---

## P0 — Close the open questions

**Goal.** Resolve the three `[OPEN]` items so downstream work is not built on a guess.

| Item | Where it is raised | Why it blocks |
| --- | --- | --- |
| Threshold definition (two-of-four rule, 80-LOC / 30-LOC boundaries) | `architecture.md` §3 | P1 is unbuildable without it |
| Catalog seeding: shipped curated vs. empty-and-accreting | `prd.md` §5 | Decides whether P7's cache-hit arm exists at all |
| `techstack.md` at target-project repo root | `prd.md` §5 | Cheap, but P4 emits into it |
| Ladder margin = 0.5 | `architecture.md` §10 | Starting value with no evidence; P5 depends on it |

**Exit.** All four written into `architecture.md` with the `[OPEN]` markers removed.

**Stop here if:** the threshold cannot be stated as a rule someone else could apply to a task list and get the same answer you would. A gate that only works when its author operates it is not a gate.

---

## P1 — Trigger gate in isolation

**Goal.** `SKILL.md` fires correctly, with no catalog, no network, no scripts behind it.

**Deliverables**
- `SKILL.md`: frontmatter, the two-of-four rule, the never-fire list, the ambiguity rule (borderline → do not fire), and a stub where routing will later go.
- A **probe set**: ~16 hand-written planning scenarios, roughly half expected-fire and half expected-silent, with the expected verdict recorded *before* any run. Must include the hard cases, not just the easy ones:
  - Should fire: retry/backoff, layered CLI config, tabular validation, rate-limited HTTP client, Rust async retry, typed CSV parsing.
  - Should not fire: a slugify helper, wiring two existing functions together, project-specific pricing rules, a domain the project already has a dependency for, a 20-line adapter.
  - Deliberately borderline: a ~50-LOC date-range helper with real timezone edge cases. Either verdict is defensible; what matters is that the rule produces it consistently.

**Exit criteria**
- Every should-not-fire probe stays silent across 3 fresh sessions. Retires the pre-benchmark half of `prd.md` **F4.1**.
- Every should-fire probe fires across 3 fresh sessions. Retires the pre-benchmark half of **F4.3**.
- Non-fire cost measured and at or under the ~1,200-token estimate in `architecture.md` §9. Early read on **F4.2**.

**Risk burned down.** The single assumption capable of making the whole design unwanted.

**Stop here if:** the gate cannot separate the probe set after two rounds of tuning. Not "tune it again" — a threshold that needs a third round of hand-fitting against 16 known cases will not generalize to unseen ones, and the design needs rethinking rather than adjusting.

---

## P2 — Catalog substrate

*Independent of P3; the two can run in parallel.*

**Goal.** The catalog can be written, parsed, linted, and aged — before anything writes to it automatically.

**Deliverables**
- `catalog/SCHEMA.md`
- `catalog/INDEX.md` with 2–3 hand-authored rows
- Two **hand-authored** domain files: one with an adopted entry plus rejections, one with rejections only (a domain where "write it yourself" won). The second matters more than the first — it is the case that proves the schema can express a negative result.
- `scripts/catalog_lint.py`, `scripts/staleness_check.py`

**Exit criteria**
- Every fenced TOML block round-trip parses under `tomllib`. Validates the write-asymmetry decision in `techstack.md` §3.
- Lint fails, as designed, on: a missing `smoke_verified_version` on an adopted entry (**F2.1**), a missing `stdlib` rejection (**F1.1**), an over-cap domain file, an orphan index row.
- `staleness_check.py` correctly reports tier expiry against hand-set dates, including the boundary days (29/30/31, 89/90/91).
- **Fault injection for F3.3:** expire Tier A on a seeded entry, run partial re-verification by hand, diff the entry. Stable facts and rejection reasons must be byte-identical afterward.

**Stop here if:** entries cannot be authored by hand in a few minutes each. If the schema is tedious for a human, the write-back step in P5 will be skipped under pressure and the catalog will never accrete.

---

## P3 — Smoke runner

*Independent of P2.*

**Goal.** `scripts/smoke_test.py` produces trustworthy raw evidence about a real API.

**Deliverables**
- PyPI path: temp venv → pinned install → run snippet → raw stdout/stderr/exit code
- crates.io path: temp cargo crate → pinned dependency → `cargo run`
- Windows path resolution (`Scripts\` vs `bin/`) working on the primary dev machine

**Exit criteria**
- **The negative case is the important one.** A snippet written against a deliberately wrong API — a decorator that does not exist, an argument renamed three versions ago — must exit non-zero and surface the real traceback. A runner that only ever reports success proves nothing about **F2**.
- Raw output is emitted verbatim. The script contains no notion of pass or fail, and no summarization. Enforces the raw-output rule in `architecture.md` §7.4.
- Both ecosystems run in a temp directory and leave the target project untouched.
- Version resolution is reported, so what was tested is unambiguous even when the install resolved something other than requested.

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

**Goal.** Seed the domains the benchmark exercises, so P7's hit arm is real rather than hypothetical.

**Deliverables.** Entries for the six library-available benchmark domains (4 Python, 2 Rust), each produced by running the **P5 miss path for real** — not hand-written. Hand-seeding would test the schema, not the pipeline.

**Exit criteria**
- Six domains seeded, lint clean, every adopted entry carrying smoke evidence and a stdlib rejection.
- C1's domain (no good library available) is seeded **as a negative** — the research pass ran and concluded "write it yourself." If C1 cannot be expressed as a catalog entry, the schema cannot represent the thing the benchmark most needs it to represent.
- Every domain file inside its size cap.

**Stop here if:** seeding produces recommendations you would not endorse on review. The rubric is miscalibrated, and benchmarking a miscalibrated rubric measures the wrong thing.

---

## P7 — Benchmark

**BLOCKED.** `/mnt/skills/examples/skill-creator/scripts/` does not exist on this machine; `run_eval.py` and `aggregate_benchmark.py` have not been confirmed. `benchmark.md` is unwritten pending that.

**Settled and ready** once unblocked: 8 tasks (4 Python + 2 Rust + C1 no-good-library + C2 trivial), 2 arms × 3 reps = 48 runs, fresh session per arm, fresh/cache-read/output tokens reported separately, LOC-avoided-at-constant-acceptance as primary with tokens secondary, methodology header, variance reported rather than single numbers, kill criteria stated up front.

**Unblocked by:** the two harness files, or their `--help` output, or one example task manifest plus one example per-run JSON.

---

## P8 — Verdict

**Goal.** Decide against evidence: ship, tune, or scrap.

**Inputs.** All F1–F5 criteria measured with variance; at least one clearly negative result somewhere in the task set (`prd.md` §7.2); the computed break-even hit count from **F5.3**; kill criteria evaluated against real data.

**Outcomes**
- **Ship** — criteria met, break-even plausible, negative result present and explicable.
- **Tune** — a specific criterion missed with a specific cause. Return to the owning phase, not to P0.
- **Scrap** — kill criteria met.

The requirement for a negative result is load-bearing. A benchmark where every arm favors the skill has most likely measured the design's assumptions rather than its performance.

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
| F4.1 no fire on trivia | P1 (probe set) | P7 (C2) |
| F4.2 non-fire cost bound | P1 | P7 |
| F4.3 always fires when it should | P1 (probe set) | P7 (T1–T6) |
| F4.4 never fires mid-implementation | P1 | P7 |
| F5.1 **primary** — LOC avoided | — | **P7 only** |
| F5.2 hit cost bound | P4 | P7 |
| F5.3 miss cost and break-even | P5 | P7 |
| F5.4 C1 pure overhead | — | **P7 only** |
| F5.5 acceptance not degraded | — | **P7 only** |

Three criteria — F5.1, F5.4, F5.5 — cannot be exercised before P7 by construction. They are comparative: each requires a skill-off arm to compare against. That is the irreducible reason the benchmark cannot be skipped, and the reason the harness is a genuine blocker rather than a documentation gap.
