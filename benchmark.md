# kosha — Benchmark

**Status:** draft, pre-registered
**Date:** 2026-09-06
**Companions:** `prd.md` (acceptance criteria F1–F5) · `architecture.md` (paths and costs) · `techstack.md` · `phases.md` (P7)

---

## Methodology header

| | |
| --- | --- |
| **Question** | Does kosha reduce hand-written implementation code without degrading correctness, at a token cost that amortizes? |
| **Hypothesis** | On tasks where a library exists, the skill-on arm writes materially less hand-written code at equal acceptance, and the token overhead of a cache hit is small enough that a one-time research cost is recovered within a plausible number of reuses. |
| **Primary metric** | **Hand-written implementation LOC, with acceptance held constant.** |
| **Secondary metrics** | Token usage, split four ways (fresh input / cache creation / cache read / output); dependencies added, direct and transitive; wall-clock. |
| **Design** | Paired A/B. Same task, fresh session per arm, skill on vs. off. |
| **Reps** | 3 per task per arm, minimum. Escalation rule in §8. |
| **Runs** | 48 primary (8 tasks × 2 arms × 3 reps) + 3–9 supplementary (§6, depends on the routing dry-run) = **51–57**. Plus 3 trigger-eval passes, which execute no tasks. |
| **Unit of analysis** | One run. Cells are reported as three raw values, not only as a mean. |
| **Controlled** | Identical task prompt per task across arms; acceptance tests supplied by the harness and identical across arms; fresh git checkout per run; one model version across the entire batch; one machine, one operator. Catalog **contents** are fixed for the batch; catalog **path per run** is measured, not assigned (§6). |
| **Not controlled** | Model nondeterminism (the reason reps exist); network latency and registry availability on the miss path; wall-clock contention. |
| **Pre-registration** | Task set, metrics, thresholds, and kill criteria in this document are fixed **before** the first run. Post-hoc metric changes invalidate the result and must be published as a separate amended run. |

### Why LOC is primary and tokens are secondary

Tokens are a cost paid once, by one session, in a market where the price falls. Hand-written code is a liability carried for the life of the project: reviewed, tested, debugged, ported, and maintained by people, indefinitely. Spending 20k extra tokens once to avoid 200 lines of hand-rolled retry logic is a clear win even though the token column looks bad. The inverse — fewer tokens, same code written — is no win at all.

So tokens are **bounded and reported, never traded against LOC**. `prd.md` F5.2/F5.3/F5.4 set token ceilings; if a ceiling is breached the result is reported as a breach, not netted against an LOC gain.

The condition **"with acceptance held constant"** is what stops this from being trivially gameable. LOC drops to zero if the agent writes nothing that works. A run only contributes to the primary metric if `acceptance_pass` is true (`prd.md` F5.5).

---

## 1. Two instruments, two jobs

The harness is two scripts that do different things. Neither executes paired runs.

| Instrument | Script | Answers | Executes tasks? |
| --- | --- | --- | --- |
| **A — Trigger evaluation** | `run_eval.py` | F4.1 (over-trigger), F4.3 (under-trigger) | No. Tests whether a skill *description* fires on a query |
| **B — Paired A/B** | `aggregate_benchmark.py` + runner + sidecar | F1, F2, F3.4, F4.2, F5 | The runner does; the aggregator only reads results off disk |

Instrument A is cheap — no task execution — so it takes more reps and a much wider query set than the A/B can afford. Instrument B is expensive and is reserved for what genuinely needs a paired comparison.

C2 (the trivial control) appears in **both**, measuring different things: Instrument A checks that the trigger stays silent across many phrasings; Instrument B measures the token cost of that correct silence (F4.2).

---

## 2. Instrument A — trigger evaluation

### Eval-set format

Flat list, each object exactly `{"query", "should_trigger"}`.

```json
[
  {"query": "add retry logic with backoff to the ingest client", "should_trigger": true},
  {"query": "rename this variable to something clearer", "should_trigger": false}
]
```

### Three passes, because one threshold governs both directions

`run_eval.py` applies a single `--trigger-threshold` to every query: `should_trigger: true` passes when `trigger_rate >= threshold`; `should_trigger: false` passes when `trigger_rate < threshold`. At the default 0.5 with 3 runs, a query that fires 1 time in 3 still *passes* as a non-trigger — far too lenient for F4.1, which demands zero fires.

The fix is to split the eval set by direction and run each with a threshold that makes the criterion strict.

| Pass | Eval set | `--runs-per-query` | `--trigger-threshold` | Pass condition it enforces | Criterion |
| --- | --- | --- | --- | --- | --- |
| **A1 over-trigger** | `no-fire.json` — all `should_trigger: false` | 5 | **0.01** | `trigger_rate < 0.01`, i.e. **0 fires out of 5** | F4.1 |
| **A2 under-trigger** | `must-fire.json` — all `should_trigger: true` | 5 | **0.99** | `trigger_rate >= 0.99`, i.e. **5 fires out of 5** | F4.3 |
| **A3 borderline** | `borderline.json` | **15** | 0.5 | `trigger_rate` must land **≤ 0.2 or ≥ 0.8**. Anything in between is a coin-flipping gate | Consistency |

### What Instrument A actually measures — a known bias

`run_eval.py` writes the skill's **description** into `.claude/commands/` and detects whether Claude *loads* the skill. It measures **G1 (load)** only. The two-of-three rule lives in the `SKILL.md` body, which is read only after loading, so **G2 (proceed) is not instrumented by A1 or A2 at all.**

The bias runs in both directions and is not symmetric:

| Observation | What it licenses |
| --- | --- |
| **A1 passes** | Strong evidence for F4.1. A query that never loads certainly never proceeds. |
| **A1 fails** | **Inconclusive.** The skill may have loaded and then correctly declined — which `prd.md` F4.1 counts as a pass and F4.2 prices at ~246 tokens under the compact gate. A1 cannot tell a wrong *proceed* from a correct *load-then-decline*. |
| **A2 fails** | Evidence about **description scope**, not about the two-of-three rule. A perfectly good rule scores 0/5 if the description was too narrow to load the skill. |
| **A2 passes** | The description is broad enough to load. Says nothing about whether the rule then fires correctly. |

**F4.1, F4.3 and F4.4 are all G2 criteria** under deterministic invocation. A hook makes G1 certain, so `run_eval.py`'s A1/A2 no longer test anything load-related that is in doubt. All three are measured from transcripts, via the **G2 runner** below and P1's hand-operated mid-implementation sessions.

#### The G2 runner

Reuses `no-fire.json`, `must-fire.json` and `borderline.json` **verbatim**, at the same reps and thresholds, so every register and domain breakdown and all pre-registration continuity carries over, and round-1 numbers stay comparable. It installs the hook, runs `claude -p` over each query, and greps the transcript for the verdict line. Detection stays deterministic even though the decision is model-mediated: no model judging a model.

Written **alongside** the harness; `run_eval.py` is never modified (`techstack.md` §6). Its setup check asserts the same envelope shape the hook does — `additionalContext` nested inside `hookSpecificOutput`, never at top level, because top-level placement is ignored silently.

##### The verdict line is permanent, and that is the point

`SKILL.md` and the gate prompt both instruct emitting exactly one line: `KOSHA: FIRE <domain>` or `KOSHA: DECLINE <clause>`.

This is **not a formatting preference and not a benchmark-only affordance.** Asking the model to state its decision aloud makes that decision explicit and output-visible, and a rule stated aloud is applied more deliberately than one applied silently. If the verdict line existed only during measurement, the G2 runner would be measuring the rule **under observation**, and production would run a different, un-measured condition.

Keeping it permanent neutralizes the observer effect by making benchmark and production **the same condition**. The line is part of the product, not the instrument.

**A1 is therefore a conservative proxy for F4.1:** it can fail on behaviour the PRD considers acceptable, but it cannot pass on behaviour the PRD considers wrong.

#### A1's denominator is inflated — report the weighted subset separately

`no-fire.json` queries 1–18 (slugify paraphrases, renames, docstrings, glue, business rules) are close to free: nothing about them resembles a library-shaped component. Queries **19–22** carry the discriminating load, each containing a signal that pulls toward firing — an already-satisfied domain, a CLI keyword on a trivial task, a structural-sounding change under the size bar.

So a headline "22/22, zero fires across 110 calls" overstates the evidence roughly fivefold. The real test is **4 queries / 20 calls**.

**Reporting rule: every round states A1 as two lines** — the full set, and the weighted subset 19–22 with its own denominator. The headline number cannot then drift into meaning more than it does.

**G2 is instrumented only by transcript inspection** — P1's hand-operated F4.4 sessions, and P7's per-run `trigger_fired` and `kosha_path` fields. Any tuning decision aimed at the two-of-three rule must come from those, never from an A1/A2 rate.

Both strict passes are deliberately unforgiving. A skill that fires 4 times in 5 on "add retry logic" is not reliable enough to build a plan step on, and one that fires once in 5 on "rename this variable" is a skill users will disable.

Failed subprocess calls count as non-triggers, which biases A2 toward failure and A1 toward passing. So an A1 pass with any subprocess errors in the log is **not** a clean pass — the runner must report the error count alongside the result, and A1 is re-run if it is non-zero.

### Query sets

- **`no-fire.json`** — ≥ 20 queries. The P1 probe set's silent half, plus phrasings that *sound* library-shaped but are not: "write a helper to slug this title", "wire the parser into the CLI", "apply our late-fee rule", "add a field to this dataclass", "swap requests for the httpx client we already depend on" (domain already covered), plus the C2 prompt and four paraphrases of it.
- **`must-fire.json`** — ≥ 20 queries. The six library-available benchmark tasks (T1–T6) plus paraphrases in different registers: terse ("retry w/ jitter"), verbose, and embedded in a longer plan step.
- **`borderline.json`** — ~8 queries around the threshold: a ~50-LOC date-range helper with real timezone edges, a small state machine, a bespoke-but-large config merge. No correct answer is claimed; what is measured is whether the rule returns the *same* answer across 15 runs. A trigger rate between 0.2 and 0.8 means the gate is coin-flipping, which is a defect independent of which way it should land.

### Why A3 runs at 15, not 5

A3 makes no claim about *which* verdict a borderline query deserves — only that the gate returns the same one. That is a real, falsifiable property, so A3 carries a pass/fail band rather than being merely descriptive.

The band needs the reps to mean anything. At `--runs-per-query 5` the possible rates are 0, .2, .4, .6, .8, 1.0, so a band of "≤ 0.2 or ≥ 0.8" fails only on .4 and .6 — a genuinely coin-flipping gate escapes it **37.5%** of the time, and a merely-consistent one (p ≈ 0.8) falls inside it about **26%** of the time. The test would be close to noise.

At 15 runs the same band is sound: a true p = 0.5 gate escapes detection **3.52%** of the time, and a consistent p = 0.9 gate is falsely flagged **5.56%** of the time. The extra cost is 8 queries × 10 runs, with no task execution behind any of them — the cheapest reps in the whole benchmark.

### A3 error logging is mandatory

At 8 × 15 = **120 subprocess calls, A3 is the highest call volume anywhere in this benchmark**, so the rate-limit bias documented above is at its worst precisely where the measurement is most delicate. Every timeout or throttled call counts as a non-trigger, which drags `trigger_rate` toward 0 and makes a throttled batch look like a confidently-silent gate.

So A3 runs with **`--num-workers` held low (2)**, and the **subprocess error count is recorded next to every trigger rate**. A non-zero error count invalidates the A3 result and the pass is re-run — a throttled batch and an inconsistent gate produce similar-looking numbers, and only the error count separates them.

---

## 3. Instrument B — directory layout

`aggregate_benchmark.py` discovers tasks from the filesystem. There is no manifest file.

```
benchmark/
└── runs/
    ├── eval-1/
    │   ├── eval_metadata.json        {"eval_id": "T1-retry-backoff"}
    │   ├── with_skill/
    │   │   ├── run-1/  grading.json  timing.json  metrics.json
    │   │   ├── run-2/  ...
    │   │   └── run-3/  ...
    │   └── without_skill/
    │       ├── run-1/  ...
    │       ├── run-2/  ...
    │       └── run-3/  ...
    ├── eval-2/ ...
    └── eval-8/
```

Task directories are `eval-1` … `eval-8`; the readable identifier comes from `eval_metadata.json`, so the mapping to T1…C2 is explicit rather than inferred from a directory name.

### Arm naming is load-bearing

The delta is `configs[0] - configs[1]` in **alphabetical directory order**. `with_skill` sorts before `without_skill` (`_` < `o`), so the delta reads as *with minus without* — which is the direction every statement in this document assumes.

> **Renaming the arms silently flips the sign.** `baseline` / `kosha` would sort `baseline` first and report `baseline − kosha`, inverting every conclusion with no error and no warning. Use **`with_skill`** and **`without_skill`** verbatim. The pre-flight validator (§5) asserts both directory names exist and that no other arm-shaped directory does.

Any subdirectory containing at least one `run-*` child is treated as an arm, so `inputs/` and `outputs/` siblings are safe — but a stray `with_skill_v2/` would be picked up as a third arm and shift the config ordering. The validator rejects unexpected arm names for that reason.

---

## 4. Per-run artifacts

Three files per run directory. Two are consumed by the aggregator; one is ours.

### 4.1 `grading.json` — consumed by `aggregate_benchmark.py`

```json
{
  "summary":  { "pass_rate": 1.0, "passed": 4, "failed": 0, "total": 4 },
  "execution_metrics": { "total_tool_calls": 23, "output_chars": 41022, "errors_encountered": 0 },
  "expectations": [
    { "text": "acceptance suite passes", "passed": true, "evidence": "pytest: 4 passed in 1.82s" },
    { "text": "no modification to supplied acceptance tests", "passed": true, "evidence": "git diff --stat tests/ -> empty" },
    { "text": "declared deps resolve and install cleanly", "passed": true, "evidence": "pip install -r requirements.txt exit 0" },
    { "text": "no network calls in the implementation path", "passed": true, "evidence": "..." }
  ],
  "user_notes_summary": { "uncertainties": [], "needs_review": [], "workarounds": [] }
}
```

Every `expectations[]` entry carries `text`, `passed`, and `evidence`. Missing fields produce warnings and break the eval viewer, so the validator checks all three on every entry.

**Note the omission: there is no `timing` block.** That is deliberate — see the trap below.

### 4.2 `timing.json` — required on every run, never optional here

```json
{ "total_duration_seconds": 182.4, "total_tokens": 148230 }
```

> ### Trap 1 — the token fallback is silent
>
> If `timing.json` is missing, `tokens` falls back to `execution_metrics.output_chars` — a **character count**, aggregated and reported under a column labelled "Tokens", with no warning. A whole batch can be produced, aggregated, and read as a token result while containing no token data at all.

> ### Trap 2 — `timing.json` is only read under a condition
>
> Per the interface, `timing.json` is read **only if** `grading.timing.total_duration_seconds` is 0 or absent. Composed with the fallback rule above, this yields a consequence worth stating explicitly: **a `grading.json` carrying a valid non-zero duration causes `timing.json` never to be opened, so `total_tokens` is never picked up and tokens silently become `output_chars`.**
>
> **Therefore: omit the `timing` block from `grading.json` entirely**, and put both the real duration and the real token count in `timing.json`. This is the only write pattern that reliably lands real tokens in the aggregate.
>
> This is derived from the two stated rules, not observed. **Run 0 (§5) verifies it empirically before the batch begins.** If the composition does not hold as described, the write pattern changes and this section is amended.

`total_tokens` here is the blended scalar the aggregator wants: `input_fresh + cache_creation + cache_read + output`. It is deliberately **not** the number any conclusion in this document rests on — a single input total is exactly what prompt caching makes misleading. It exists to keep the aggregator's "Tokens" column honest. The split in `metrics.json` is what we reason from.

### 4.3 `metrics.json` — sidecar, ours

The aggregator's three metrics are hardcoded, and the primary metric is not representable in its schema at all. This file carries what the schema cannot.

```json
{
  "eval_id": "T1-retry-backoff",
  "arm": "with_skill",
  "rep": 1,
  "model_id": "<recorded verbatim from the run>",
  "catalog_state": "natural",   // natural | induced_cold | induced_stale
  "tokens": { "input_fresh": 18422, "cache_creation": 9110, "cache_read": 118300, "output": 2398 },
  "loc_handwritten": 34,
  "deps_added": ["tenacity==9.1.2"],
  "deps_direct": 1,
  "deps_transitive": 0,
  "acceptance_pass": true,
  "trigger_fired": true,
  "kosha_path": "hit",
  "smoke_test_run": true,
  "smoke_exit_code": 0
}
```

`kosha_path` ∈ `none | gate_declined | hit | stale_hit | miss`. It is what makes the break-even computation (§7) possible, and it is recorded from the transcript rather than inferred from token counts.

### Why a sidecar rather than the alternatives

`aggregate_results` hardcodes `pass_rate`, `time_seconds`, and `tokens`; adding fields to `grading.json` will not get them aggregated. Three options existed:

| Option | Verdict |
| --- | --- |
| Patch `aggregate_results` to take a metric list | Cleanest in the abstract, but forks a script that may be updated upstream. Rejected — the fork's maintenance cost lands on us, and a silent upstream divergence is exactly the kind of stale fact kosha exists to avoid. |
| Encode LOC and deps as `expectations[]` assertions with thresholds | Flows into `pass_rate` for free, but collapses a continuous measure into a boolean. **Fatal for the primary metric**: "LOC under 120: true" cannot express a 40% reduction, and would make F5.1 unmeasurable. Rejected. |
| **Sidecar + ~40-line aggregator** | **Chosen.** `aggregate_benchmark.py` remains the source of truth for the A/B structure, pass_rate, time, and blended tokens; the sidecar covers only the four things its schema cannot represent. |

On the "do not write a new harness" constraint: this does not. `aggregate_benchmark.py` still owns task/arm/rep discovery and the delta. The sidecar aggregator computes mean, stddev, min, max, and the raw triples over four extra fields and has no opinion about experiment structure. Combined with the runner, it is the minimum new code the metrics gap requires.

---

## 5. Runner and pre-flight

Neither script sets up an arm, toggles the skill, or launches Claude Code. A thin runner is required and is the only substantial new code justified.

**Per task × arm × rep, the runner:**

1. Creates a fresh checkout of the task fixture — including the supplied acceptance tests — into a clean directory.
2. Sets the catalog per the run's `catalog_state` (§6). `natural` — the seeded catalog untouched, which is every primary run. `induced_cold` — the domain file **and its `INDEX.md` row** both removed. `induced_stale` — `tier_a_verified_on` aged past the window. For `without_skill`, kosha is absent entirely.
3. Starts a **fresh session** with telemetry enabled (§5.1) and issues the task prompt verbatim.
4. On completion: runs the acceptance suite, verifies `tests/` is unmodified, counts LOC (§5.2), resolves the dependency tree, parses the telemetry stream for the token split, and reads the transcript for `trigger_fired` / `kosha_path` / smoke evidence.
5. Writes `grading.json` (no `timing` block), `timing.json`, and `metrics.json` into `benchmark/runs/eval-N/<arm>/run-M/`.

### 5.1 Token capture

Claude Code OpenTelemetry, console exporter for local single-user runs. Docs: <https://code.claude.com/docs/en/monitoring-usage>

```
CLAUDE_CODE_ENABLE_TELEMETRY=1
OTEL_METRICS_EXPORTER=console
OTEL_METRIC_EXPORT_INTERVAL=5000    # standard OTel; short so metrics flush before exit
```

The runner captures the console metric stream for the session and sums token usage per type into the four `metrics.json` buckets. **Exact metric and attribute names are verified against the docs in Run 0, not assumed here** — a mis-parsed attribute would produce plausible-looking numbers in the wrong buckets, which is worse than a crash.

### 5.2 LOC counting rule

A vague rule makes the primary metric mush, so it is fixed here.

**Counted:** added lines in non-test source files in the final diff, excluding blank lines and comment-only lines.

**Not counted:** anything under `tests/`; dependency manifests and lockfiles; generated or vendored files; deleted lines.

**Explicitly counted even in the skill-on arm:** import statements and library call sites. A library solution still has LOC — it just has less of it. Counting only the hand-rolled arm's lines would build the conclusion into the measurement.

Rationale for excluding tests: acceptance tests are **supplied** and identical across arms, and the agent is instructed not to modify them (asserted as an expectation, §4.1). This makes "acceptance held constant" a controlled fact rather than a hope, and removes the largest confound in an LOC comparison.

**Known gaming surface:** LOC is sensitive to line-density style. Mitigation is the non-blank/non-comment rule plus a spot review of the three highest-delta cells; if a delta is driven by formatting rather than substance, it is reported as such.

### 5.3 Run 0 — calibration, before the batch

One throwaway task, both arms, one rep. Not part of the results. It exists to verify:

- The `grading.json` / `timing.json` composition (Trap 2) lands real `total_tokens` in the aggregate and **not** `output_chars`.
- OTel metric and attribute names parse into the four buckets correctly, and the four sum to something consistent with the session.
- `aggregate_benchmark.py` discovers both arms and the delta sign reads *with minus without*.
- LOC counting and dependency resolution produce sane values on a known fixture.

If Run 0 contradicts anything in §4, this document is amended **before** the batch, and the amendment is recorded. That is the honest handling of a specification derived rather than observed.

### 5.4 Batch validator — fails loudly

Run after every batch, before aggregation. Any failure fails the batch.

- Every `run-*` directory has all three files.
- No `grading.json` contains a non-zero `timing.total_duration_seconds`. *(Trap 2 — this is the check that stops silent character-count reporting.)*
- Every `timing.json` has a **numeric, non-zero** `total_tokens`. *(Trap 1.)*
- `metrics.json` token buckets sum to `timing.json:total_tokens`.
- Every `expectations[]` entry has `text`, `passed`, and `evidence`.
- Arm directories are exactly `with_skill` and `without_skill`, and nothing else contains `run-*` children.
- All runs record the same `model_id`.
- Rep counts are equal across arms within a task.

---

## 6. Task set

Eight tasks. Six where a library plainly exists, two controls. Four Python, two Rust — the second ecosystem is there to show the catalog and rubric are not Python-shaped, since the crates.io path exercises a different smoke runner and a different registry.

| ID | Task | Ecosystem | Library expected | Gate should fire |
| --- | --- | --- | --- | --- |
| **T1** | Retry with exponential backoff and jitter around a flaky client, with a predicate for which exceptions retry | Python | yes | yes |
| **T2** | CLI with layered config: flags > env > file > defaults, with typed validation | Python | yes | yes |
| **T3** | Tabular validation: column types, nullability, range and cross-column constraints, readable failure report | Python | yes | yes |
| **T4** | HTTP client with per-host rate limiting and retry on 429 honouring `Retry-After` | Python | yes | yes |
| **T5** | Async retry around a fallible task with backoff and a deadline | Rust | yes | yes |
| **T6** | CSV into typed structs with error reporting per row | Rust | yes | yes |
| **C1** | Parse a bespoke internal deploy-manifest format (grammar supplied in the prompt) into a typed structure | Python | **no** | **yes** |
| **C2** | Slugify a title string for URLs | Python | n/a | **no** |

### The two controls do different jobs

**C1 — no good library available.** The grammar is invented and supplied in the prompt, so no library can exist. It is above the size and complexity bar, so the gate **should** fire: kosha researches, finds nothing that fits, and concludes "write it yourself." This measures **pure overhead** — the full cost of a research pass that correctly buys nothing (F5.4) — and is the expected trigger for F1.4, the criterion that proves the ladder can decline.

**C2 — trivial.** Below the bar. The gate **should not** fire. This measures the cost of a correct non-fire (F4.2) and is the pass/fail case for F4.1.

Conflating these two would hide the more interesting failure. C1 failing means research is uneconomic; C2 failing means the trigger is undisciplined. Different diagnoses, different fixes.

> **A design that cannot produce a negative result is not a benchmark.** C1 is expected to show the skill-on arm strictly worse on tokens and no better on LOC. That is a real, publishable negative, and if it does not appear, §9's meta-criterion applies.

### Catalog state is measured, not assigned

The catalog is seeded from stack decisions already made in four existing projects — LightningParse, Verity, Batchbird, Prahari — **not** from the benchmark's own task domains (`phases.md` P6). Seeding the benchmarked domains would guarantee a hit on every task and measure the theoretical ceiling: 100% hit rate against entries generated for those exact tasks, with none of the partial matches, adjacent domains, and nearly-fitting index keywords that make up real steady-state use.

The consequence for this document is direct: **`kosha_path` is an observed outcome, not a controlled condition.** There is no assignable "warm" arm. Each `with_skill` run routes on its own and records what actually happened — `hit`, `stale_hit`, `miss`, or `gate_declined` — and the analysis stratifies on that (§7.1).

**A benchmark task that misses is a finding, not a failure.** It is evidence about catalog coverage transferring across projects, which is the property the seeding change exists to measure. Re-seeding a missing domain to convert it into a hit is prohibited: it would reintroduce exactly the contamination this design removed, arriving disguised as a fix.

### Entry gate: the routing dry-run

The revert carries its own risk. If seeding from four real projects yields only one or two natural hits across the eight tasks, F5.2 has n = 1 and the cache-hit economic argument goes unmeasured — discovered after 48 runs rather than before.

So after P6 seeding completes and **before any benchmark run**, all eight tasks are dry-run through **routing only**: gate plus index match, no research, no smoke test, no implementation. This is nearly free and it reveals the hit/miss distribution in advance.

**Pre-registered go/no-go: at least 3 of the 8 tasks must route to a hit.** Basis, so it is not re-litigated later: three hits at three reps is nine runs, the minimum that gives F5.2 any variance estimate at all. The number is arbitrary and declared rather than derived.

If the dry-run misses that bar, the remedies are, in order:

1. Broaden seeding to **more real-project domains** — more of what those four projects actually decided.
2. Accept F5.2 as unmeasurable in this batch and report it as such.

Seeding the benchmark domains is **not** on that list.

### Induced sub-experiments

Natural routing will not produce every path in useful quantity, so two conditions are induced, both `with_skill` only — the skill-off arm is catalog-independent, and its runs serve as the comparison for every path.

| Sub-experiment | Tasks | Runs | Purpose |
| --- | --- | --- | --- |
| **COLD** — induced | Whichever of T1 (PyPI) / T5 (crates.io) does **not** already miss naturally | 0–2 × 3 = 0–6 | Miss-path cost for F5.3 and break-even. A task that misses naturally needs no induced twin |
| **STALE** — induced | One task that routes to a hit in the dry-run | 1 × 3 = 3 | Partial re-verify cost for F3.4 (target: ≤ 30% of cold) |

STALE is induced by ageing `tier_a_verified_on` on the target entry. It cannot be obtained naturally within a batch that runs in a few days.

**An induced COLD removes both the domain file and its `INDEX.md` row.** Removing the file alone would leave an orphan index row — precisely the condition `catalog_lint.py` is built to reject (`architecture.md` §4) — so the run would die on a lint error instead of exercising the miss path. Removing both is the honest simulation of a domain never researched, and it needs **no lint exemption**. The benchmark harness gets no special case in the linter; a harness that requires disabling a correctness check is testing something other than the system.

Total supplementary runs: **3 to 9**, depending on what the dry-run finds. The run count in the methodology header is a range for that reason.

---

## 7. Analysis

### 7.1 Primary — LOC avoided at constant acceptance, stratified by measured path

For each of T1–T6, over runs where `acceptance_pass` is true in **both** arms:

```
loc_reduction = 1 − mean(loc_handwritten | with_skill) / mean(loc_handwritten | without_skill)
```

Reported per task as raw values per arm plus mean and stddev. Target: **≥ 40% mean reduction** (F5.1).

**The headline number is stratified by `kosha_path`.** With the path measured rather than assigned (§6), a single pooled figure blends two different mechanisms — a cache benefit and a research benefit — into one number that describes neither. They have different costs, different failure modes, and different implications: a strong hit result says the catalog transfers across projects, a strong miss result says research is worth doing live, and they are not interchangeable claims.

| Stratum | What it answers |
| --- | --- |
| `hit` | LOC avoided when the catalog already knew the domain — the steady-state case |
| `stale_hit` | Same, with partial re-verification in the path |
| `miss` | LOC avoided when research ran live — the first-encounter case |
| `gate_declined` | Expected to be ~0 by construction. A non-zero value here means the gate declined and the arm still diverged, which is a defect worth chasing |

Each stratum is reported with its own n, since the strata are populated by observed routing rather than by design and will not be balanced. **A pooled figure is reported only after the strata, and only labelled as a blend** — it is not the headline, and no kill criterion reads from it.

`prd.md` F5.1's ≥ 40% target is evaluated **per stratum**, not on the blend. A stratum with n < 2 valid pairs reports its raw values and no mean.

Runs where either arm fails acceptance are **excluded from the primary metric and reported separately**. A cell that loses runs to acceptance failure has its remaining n stated; a pooled mean is not computed over fewer than 2 valid pairs per task.

### 7.2 Secondary — tokens, reported split

Token overheads are computed **per measured stratum**, on the same basis as §7.1. Where a stratum is thin, its n is stated alongside the figure.

Per task and arm: mean ± stddev and raw triples for `input_fresh`, `cache_creation`, `cache_read`, `output`, **each reported separately**. A single input total is not reported as a headline number anywhere, because cache reads and fresh input differ by roughly an order of magnitude in price and mixing them makes a cheap run look expensive.

Overheads, computed on the four buckets and on the blended total:

```
overhead_hit   = tokens(with_skill | path=hit)       − tokens(without_skill)   # F5.2, target ≤ 5,000
overhead_miss  = tokens(with_skill | path=miss)      − tokens(without_skill)   # F5.3
overhead_stale = tokens(with_skill | path=stale_hit) − tokens(without_skill)   # F3.4
overhead_C1    = tokens(with_skill, C1)   − tokens(without_skill, C1) # F5.4, pure waste
overhead_C2    = tokens(with_skill, C2)   − tokens(without_skill, C2) # F4.2, target ≤ 1,500
```

### 7.3 Break-even — computed, not asserted

Research is a one-time cost per domain, amortized across every later use of that domain. Amortized overhead after N uses:

```
amortized(N) = overhead_hit + (overhead_miss − overhead_hit) / N
```

The excess over steady state decays as 1/N. Report **N\***, the number of uses at which the excess falls within 25% of the steady-state hit overhead:

```
N* = (overhead_miss − overhead_hit) / (0.25 × overhead_hit)
```

N\* is published with its inputs, so the arithmetic is checkable. `prd.md` F5.3 requires this number to exist and be plausible — a domain reused three or four times across a codebase is ordinary; one needing forty reuses to pay for itself is not.

### 7.4 Load frequency and aggregate overhead

F4.2 bounds the cost of **one** correct non-fire. Nothing previously bounded **how often** it is paid. Under deterministic invocation the hook fires on *every* user prompt, so the question stops being hypothetical.

#### Compact gate, not the body

The hook injects a **compact gate prompt** (`hooks/gate_prompt.txt`, measured **246 tokens**), not `SKILL.md`. The gate carries the never-fire list, the two-of-three rule, and the verdict-line instruction, and tells the model to read `SKILL.md` **only on a FIRE**. The body (measured **1,496 tokens**) therefore loads only when kosha actually proceeds.

| Model | 20-turn session |
| --- | --- |
| Body injected every turn | 20 x 1,496 = **29,920** |
| Compact gate, 0 fires | 20 x 246 = **4,920** |
| Compact gate, 1 fire | 4,920 + 1,496 = **6,416** |
| Compact gate, 2 fires | 4,920 + 2,992 = **7,912** |
| Compact gate, 4 fires | 4,920 + 5,984 = **10,904** |

**Per-turn floor falls from ~1,496 to ~246 tokens, a 6.1x reduction**, and the aggregate for a realistic session drops roughly four-fold.

Two consequences:

1. **F4.2 is re-based from 1,500 to 400 tokens.** A correct non-fire is now a gate-only decline, and the old bound was sized for a body load that no longer happens on the decline path.
2. **The shell-level regex prefilter is probably unnecessary.** It was proposed to avoid paying ~1,500 tokens per turn; at 246 it buys little and costs a deterministic false-negative surface. Not adopted.

#### Metric

Per-run fields in `metrics.json`:

```
"turns_total":          <turns in the session>
"loads_total":          <turns where the gate was injected>   # = turns_total under a hook
"loads_proceeded":      <turns reaching KOSHA: FIRE>
"gate_tokens":          <measured compact-gate cost>
"body_tokens":          <measured SKILL.md cost when loaded>
"load_overhead_tokens": <loads_total * gate_tokens + loads_proceeded * body_tokens>
```

Reported as `decline_rate = 1 - loads_proceeded / loads_total` alongside `load_overhead_tokens`. Under a hook `load_rate` is 1.0 by construction and carries no information; `decline_rate` replaces it as the interesting figure.

> **F4.5's threshold is deliberately unset.** Same reasoning as the kill criteria: there is not yet a single measurement of aggregate overhead, and choosing a number before there is one would be picking it to look rigorous. The metric is instrumented now so the first real data can set it.

> **No existing kill criterion would catch a bad result here.** K1/K2/K5 are LOC, acceptance and cost-ratio; K3 is hallucinated APIs; K4 is per-task triggering; K6 bounds C1's single-task overhead. Stated rather than patched.

### 7.5 Dependency metrics

Mean and max `deps_transitive` across T1–T6 skill-on runs (F1.2, target ≤ 5); any run above 15 checked for the written justification (F1.3); `deps_added` in the skill-off arm reported too — the hand-rolling arm sometimes reaches for something heavier, and that comparison is part of the bloat question.

### 7.5 Reporting format

Per task, a table of raw per-rep values for both arms across every metric, then the aggregate line. **Raw triples are reported alongside every summary statistic.**

With n = 3 a stddev is a crude estimate — three numbers do not characterize a distribution, and reporting only "mean ± σ" would overstate the precision. The three values are more informative than the statistic computed from them, so both are shown. No result in this benchmark is reported as a single number.

---

## 8. Variance and rep escalation

Run-to-run variance in agent tasks is large, which is why 3 reps is a floor rather than a target.

**Escalation rule, pre-registered:** for any task × arm cell where the spread on the primary metric exceeds **50% of that cell's mean** (`(max − min) / mean > 0.5`), reps are increased to **5** for that cell **and its paired cell in the other arm**. Pairs are escalated together so the comparison stays balanced.

Escalation is decided **only** on the spread of `loc_handwritten`, never on whether the result is going the desired direction. Escalating cells that look unfavourable and stopping at cells that look good is how a benchmark manufactures its conclusion, and pre-registering the trigger is what prevents it.

Escalations are reported: which cells escalated, why, and the values before and after.

---

## 9. Kill criteria

Defined up front, evaluated against real data at `phases.md` P8. Two distinct verdicts — one kills kosha, one kills the benchmark.

### Scrap kosha

| # | Condition | Reasoning |
| --- | --- | --- |
| **K1** | Mean LOC reduction across T1–T6 is **< 15%** at constant acceptance | The primary metric fails. If the skill does not meaningfully reduce hand-written code, nothing else it does justifies its existence. |
| **K2** | Acceptance pass rate is **lower** in `with_skill` than `without_skill` on any task, and the failures are attributable to the recommendation | LOC bought with broken code is not a saving. F5.5. |
| **K3** | Any hallucinated-API acceptance failure in a `with_skill` run | The smoke-test requirement is the design's central defence (F2.4). If it does not hold, the skill is a confident source of wrong API claims — strictly worse than no skill. |
| **K4** | A1 fails after two rounds of threshold tuning, or the trigger fires on C2 in any rep | An undisciplined trigger gets the skill disabled, at which point every other property is moot. F4.1. |
| **K5** | **N\* > 20** (equivalently, cost ratio `r > 6`) | Research does not amortize at any plausible reuse rate. The caching argument is the whole economic case; without it, kosha is a per-project research tax. |
| **K6** | `overhead_C1` exceeds **25,000 tokens** or doubles wall-clock | The cost of correctly concluding "no library" is high enough that users will avoid triggering the skill on anything uncertain — which is exactly where it should be most useful. |

**Two tuning rounds, then stop.** K4's "after two rounds" is the only condition that permits retry, and it is bounded for the reason given in `phases.md` P1: a threshold needing a third round of hand-fitting against known cases will not generalize to unseen ones.

> **Why 20 and not 10.** N\* reduces to an identity: with `r = overhead_miss / overhead_hit`, `N* = (r − 1)/0.25 = 4(r − 1)`. So N\* is purely a function of the cost ratio, and a threshold of 10 is exactly `r > 3.5`. The design's own estimate (`architecture.md` §9) predicts `r = 3.57–5.48`, so a boundary of 10 fires across the entire predicted range including its most optimistic end.
>
> **A kill criterion that fires when the design performs exactly as predicted is not a kill criterion — it is a prediction of failure.** At `r ≤ 6`, K5 fires on divergence from the design rather than on the design itself, which is what makes 20 defensible rather than merely larger. If the measured ratio lands inside the predicted band, K5 stays silent and the other criteria decide.

### Scrap the benchmark, not kosha

| # | Condition | Reasoning |
| --- | --- | --- |
| **M1** | No negative result appears anywhere in the task set — C1 included | A design that only produces favourable results has most likely measured its own assumptions. The instrument is not trusted and must be redesigned before any positive claim is made. |
| **M2** | Run 0 contradicts §4 and the correction is not verifiable | If tokens cannot be captured reliably, the secondary metrics are unreportable, and F5.2/F5.3/F5.4 cannot be evaluated. Fix the instrument first. |
| **M3** | Validator failures cannot be resolved without relaxing a check | The traps in §4 are silent by nature. A benchmark that proceeds past them produces a well-formatted result with no data behind it. |

### Tune, do not scrap

Any single F-criterion missed with an identified cause in a specific component returns to that phase (`phases.md` coverage map), not to P0. Missing F1.2 by a dependency or two is a rubric weight adjustment; missing K1 is not.

---

## 10. Threats to validity

Stated because a benchmark that does not name its weaknesses is advocacy.

| Threat | Mitigation, or acknowledgement |
| --- | --- |
| **n = 3** is small for a high-variance process | Escalation rule (§8); raw triples always reported; no single-number claims |
| **Task set authored by the skill's designer** — selection bias toward tasks kosha handles well | C1 chosen adversarially; acceptance tests written before the catalog is seeded; T1–T6 drawn from domains that are conventionally library-solved rather than from the catalog's contents |
| **Thin strata** — routing is observed, so `hit` and `miss` will not be balanced and either may end up with few runs | Routing dry-run (§6) surfaces the distribution before the batch, with a pre-registered 3-of-8 go/no-go; every stratum reports its own n; F5.1 is evaluated per stratum, never on the blend |
| **Single operator, single machine, single model version** | Model ID recorded per run and asserted identical by the validator; results are not claimed to generalize across model versions |
| **LOC is style-sensitive and gameable** | Non-blank/non-comment rule; spot review of the three highest-delta cells; formatting-driven deltas reported as such |
| **Network variability on the miss path** | Affects COLD runs only; wall-clock reported but not used in any kill criterion except K6's secondary clause |
| **`trigger_fired` and `kosha_path` are read from transcripts** — a human-judgment step | Both are coarse categorical calls; the criteria that depend on them (F4, break-even routing) are unlikely to hinge on a marginal reading |
| **A1's subprocess-error bias** — failed calls count as non-triggers, flattering the over-trigger check | Error count reported alongside A1; a non-zero count invalidates the pass and the eval is re-run (§2) |

---

## 11. Execution checklist

1. Close `phases.md` P0–P6; catalog seeded for T1–T6 and C1 (as a negative).
2. Write `no-fire.json`, `must-fire.json`, `borderline.json`.
3. **Run 0** — calibration (§5.3). Amend this document if contradicted.
4. Instrument A: passes A1, A2, A3. Records F4.1 / F4.3.
5. **Routing dry-run** (§6): all 8 tasks through gate + index match only. Apply the 3-of-8 go/no-go before spending anything.
6. Instrument B primary: 8 tasks × 2 arms × 3 reps = 48 runs; `kosha_path` recorded per run.
7. Instrument B supplementary: induced COLD (0–6 runs, only where a natural miss did not occur), induced STALE (3 runs).
8. Batch validator (§5.4) on every tree. Any failure fails the batch.
9. `aggregate_benchmark.py benchmark/runs -o benchmark/benchmark.json`; repeat per supplementary tree.
10. Sidecar aggregation over `metrics.json`.
11. Apply §8 escalation; re-run escalated pairs; re-validate.
12. Compute §7 including N\*.
13. Evaluate §9 against the results. Record the verdict and the numbers behind it.
