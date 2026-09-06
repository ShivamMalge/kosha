# kosha — Architecture

**Status:** draft
**Date:** 2026-09-06
**Companion to:** `prd.md` (what and why), `techstack.md` (kosha's own tooling), `benchmark.md` (proof)

---

## 1. Design constraints this document is bound by

These are inputs, not proposals. Nothing below relaxes them.

1. Triggers at planning time, never mid-implementation.
2. Threshold-gated. Correctly **not** firing is a requirement.
3. Catalog uses progressive disclosure: thin always-loaded index plus per-domain files loaded only on match. It must not become one large file.
4. Entries separate rotting facts from stable facts. Only rotting facts are re-verified, and only past a staleness window.
5. Rejections are recorded with reasons, not just adoptions.
6. Default bias against adding a dependency: `stdlib > small focused package > write it yourself > large framework`.
7. No recommendation without an executed smoke test against the real API. Raw output only.

---

## 2. Directory layout

```
kosha/
├── SKILL.md                          # trigger + threshold gate + routing. Loaded on activation.
├── catalog/
│   ├── INDEX.md                      # thin domain index. Loaded on every activation past the gate.
│   ├── SCHEMA.md                     # entry schema. Loaded only when writing back.
│   └── domains/
│       ├── retry-and-backoff.md      # loaded only on domain match
│       ├── cli-and-config.md
│       ├── tabular-validation.md
│       ├── http-clients.md
│       ├── rust-async-retry.md
│       └── rust-csv-typed.md
├── references/
│   ├── rubric.md                     # gates + weights + anchors. Cache-miss path only.
│   ├── research-protocol.md          # source order, caps, stop conditions. Cache-miss path only.
│   ├── smoke-test-protocol.md        # what a valid smoke test is. Any path that recommends.
│   └── techstack-template.md         # output template. Any path that recommends.
└── scripts/
    ├── smoke_test.py                 # isolated install + run + raw output. Never interprets.
    ├── catalog_lint.py               # schema, index/domain consistency, size caps.
    └── staleness_check.py            # offline; reports expired fields per tier.
```

**Output location.** The per-project `techstack.md` is written to the **target project's** repo root, not into `kosha/`. It is a project artifact, versioned with the project, reviewable in a diff. *(Marked [OPEN] in `prd.md` §5.)*

### File responsibilities

| File | Owns | Must not |
| --- | --- | --- |
| `SKILL.md` | Trigger conditions, threshold gate, the never-fire list, routing to the catalog | Contain catalog data, rubric weights, or research instructions — those load later or not at all |
| `catalog/INDEX.md` | Domain slug, match keywords, entry count, last-touched date | Contain any library facts. If you can answer a question from INDEX alone, the index is too fat |
| `catalog/domains/*.md` | Full entries for one domain: adoptions and rejections | Exceed the size cap (§4); grow a second domain inside itself |
| `catalog/SCHEMA.md` | The entry schema and field semantics | Be loaded on the read path — it is only needed when writing |
| `references/rubric.md` | Gates, weights, 0–5 anchors, the ladder margin rule, the recommend threshold | Be consulted on a cache hit; a hit already carries a decided score |
| `references/research-protocol.md` | Source order, candidate cap, fetch cap, stop conditions | Be loaded on a hit |
| `references/smoke-test-protocol.md` | What counts as a valid smoke test, and the raw-output rule | Interpret results — that is the agent's job, against raw output |
| `references/techstack-template.md` | The shape of the project artifact | Carry decision logic |
| `scripts/smoke_test.py` | Isolated environment, pinned install, snippet execution, raw stdout/stderr/exit-code | Judge pass or fail. It reports; it does not conclude |
| `scripts/catalog_lint.py` | Structural integrity of the catalog | Touch the network |
| `scripts/staleness_check.py` | Which fields are past their tier window | Touch the network, or re-verify anything itself |

---

## 3. The threshold gate

> **[OPEN]** This definition is proposed, not confirmed. It is the single highest-leverage tuning knob in the design: it decides both F4.1 (never fire on trivia) and F4.3 (always fire when it should).

Evaluated inside `SKILL.md`, **before** `INDEX.md` loads, so a decline costs nothing beyond the SKILL body.

### Fire when at least two of four hold

| Signal | Threshold |
| --- | --- |
| **Size** | The component is estimated at 80+ lines of non-trivial logic |
| **Recognizable domain** | It names a known problem class: retry, backoff, rate limiting, parsing, serialization, validation, scheduling, concurrency primitives, protocol implementation, format handling, caching, diffing |
| **Edge-case density** | Correctness depends on cases the author is unlikely to enumerate: timezones, unicode, floating point, network failure, partial writes, concurrency, encoding |
| **Testability burden** | It would warrant its own test file rather than being covered incidentally |

### Never fire when any of these hold

- The component is under roughly 30 lines.
- It is glue, wiring, configuration plumbing, or type shuffling between two things that already exist.
- It is project-specific business logic — no library can know your invoicing rules.
- The project **already** has a dependency covering this domain. Check the manifest first; recommending a second HTTP client is a defect.
- Implementation has already begun in this session. A plan-time skill that fires at implementation time produces rewrites, not decisions.

### Ambiguity rule

If the two-of-four evaluation is genuinely borderline, **do not fire**. The asymmetry is intentional: a missed fire costs the user the status quo, while a false fire costs tokens *and* trains the user to disable the skill. F4.3 keeps this from degenerating — the six library-available benchmark tasks must fire every time.

---

## 4. Catalog structure and progressive disclosure

### Three levels, three load conditions

| Level | File | Loads when | Size cap (lint-enforced) |
| --- | --- | --- | --- |
| L0 | `SKILL.md` frontmatter | Always resident | 400 chars of description |
| L1 | `catalog/INDEX.md` | Gate fired | 120 lines |
| L2 | `catalog/domains/<slug>.md` | Domain keyword matched | 200 lines / 8 entries |

**The size caps are the mechanism that prevents "one large file."** They are checked by `catalog_lint.py` and are hard failures. When a domain file hits 8 entries, it must be split into narrower domains — `http-clients.md` becomes `http-clients.md` plus `http-rate-limiting.md`. Growth goes sideways into more domain files, never downward into one big one.

### INDEX.md format

Deliberately fact-free. It is a router, not a summary.

```markdown
| domain | match keywords | entries | last touched |
| --- | --- | --- | --- |
| retry-and-backoff | retry, backoff, jitter, exponential, transient failure | 4 | 2026-09-01 |
| cli-and-config | argparse, cli, flags, config layering, env override | 6 | 2026-08-14 |
| tabular-validation | dataframe, schema, column types, tabular validation | 3 | 2026-07-30 |
| rust-async-retry | retry, tokio, async backoff, crates | 3 | 2026-08-22 |
```

If a reader can learn *which library to use* from INDEX.md, the index has leaked L2 content and lint should fail it.

### Domain file layout

```markdown
# Domain: retry-and-backoff
Ecosystems: pypi, crates.io
Scope: transient-failure retry with backoff and jitter. Not circuit breaking (see resilience-patterns).

## Recommended
<entry: tenacity>

## Rejected
<entry: backoff>
<entry: retrying>
<entry: stdlib>
<entry: hand-rolled>
```

Rejections live in the same file as adoptions on purpose. The value of "we looked at `backoff` and it has been unmaintained since 2022" is only realized if it is found at the same moment the question is asked.

---

## 5. Catalog entry schema

Entries are fenced **TOML** blocks inside the domain markdown file. TOML because `tomllib` is Python stdlib from 3.11 and reads it with no dependency — see `techstack.md` for the read/write asymmetry this creates and how it is handled.

The schema's central feature is that `[stable]` and `[rotting]` are separate tables. Nothing in `[stable]` is ever touched by a staleness sweep; everything in `[rotting]` carries a verification date and a tier.

### Adopted entry

````markdown
```toml
id = "tenacity"
ecosystem = "pypi"
domain = "retry-and-backoff"
status = "adopted"          # adopted | rejected | conditional

[stable]                     # never auto-expires
license = "Apache-2.0"
install_name = "tenacity"
import_name = "tenacity"
api_shape = """
@retry(stop=stop_after_attempt(n), wait=wait_exponential(multiplier, max=s))
Imperative form: Retrying(...) / AsyncRetrying(...)
Predicates: retry_if_exception_type(...)
"""
entry_points = ["tenacity.retry", "tenacity.Retrying", "tenacity.stop_after_attempt", "tenacity.wait_exponential"]
smoke_test_file = "scripts/smoke/pypi_tenacity.py"
smoke_verified_version = "9.1.2"
smoke_verified_on = 2026-09-01
decided_on = 2026-09-01
decision_reason = """
No stdlib backoff primitive exists. Hand-rolled equivalent is ~60 LOC and
jitter/cap interaction is a recurring source of thundering-herd bugs.
Zero transitive dependencies, so the ladder penalty is nil.
"""

[[stable.rejected_alternatives]]
id = "stdlib"
reason = "No retry or backoff primitive in the standard library. time.sleep loop is the hand-rolled case, scored separately."

[[stable.rejected_alternatives]]
id = "backoff"
reason = "Maintenance stalled; last release predates the staleness horizon and open issues are unanswered. Gate `maintained` = fail."

[[stable.rejected_alternatives]]
id = "hand-rolled"
reason = "~60 LOC including jitter, cap, and predicate handling, plus its own test file. Loses to a zero-dependency package on the ladder."

[rotting]                    # each field carries a tier; see section 6
latest_version = "9.1.2"     # tier A
last_release = 2026-07-14    # tier A
downloads_30d = 142_000_000  # tier B
open_issues = 31             # tier B
stars = 7400                 # tier B
tier_a_verified_on = 2026-09-01
tier_b_verified_on = 2026-07-20

[scores]
gate_license_ok = "pass"
gate_maintained = "pass"
gate_installs_clean = "pass"
gate_importable = "pass"
api_fit = 5
dep_weight = 5
adoption = 5
maintenance = 4
docs_typing = 4
weighted = 4.75
transitive_deps = 0
```
````

### Rejected entry

Lighter. A rejection needs enough to stop the question being re-asked, and no more.

````markdown
```toml
id = "backoff"
ecosystem = "pypi"
domain = "retry-and-backoff"
status = "rejected"

[stable]
license = "MIT"
rejected_on = 2026-09-01
rejected_because = "gate:maintained"
rejection_detail = """
Last release 2022-10; 40+ open issues with no maintainer response in 18 months.
API itself is fine — if maintenance resumes this is worth re-examining.
"""
revisit_if = "a release lands after 2026-09-01"

[rotting]
latest_version = "2.2.1"
last_release = 2022-10-05
tier_a_verified_on = 2026-09-01
```
````

`revisit_if` matters: a rejection without a re-entry condition is a permanent ban based on a moment in time, which is exactly the kind of stale fact this design is trying to avoid.

### Field semantics

| Field | Table | Why it sits there |
| --- | --- | --- |
| `license` | stable | Changes are rare and are news, not drift |
| `api_shape`, `entry_points` | stable | Verified by execution, not recall. Invalidated only by a major-version escalation (§6) |
| `decision_reason`, `rejected_alternatives`, `rejection_detail` | stable | These are *judgments*. They do not expire; they are superseded |
| `smoke_test_file`, `smoke_verified_version` | stable | The evidence and what it was evidence *of* |
| `latest_version`, `last_release` | rotting, tier A | Changes weekly; drives the major-version escalation |
| `downloads_30d`, `open_issues`, `stars` | rotting, tier B | Drift slowly; a 90-day-old value is still directionally right |
| `scores.*` | derived | Recomputed only when an input to it is re-verified |

---

## 6. Staleness rules

**Tiered by fact volatility.** One window for all facts is wrong in both directions at once: too slow for versions, needlessly churny for download counts.

| Tier | Fields | Window | On expiry |
| --- | --- | --- | --- |
| **A** | `latest_version`, `last_release` | **30 days** | Re-verify these two fields only — a single registry call per package |
| **B** | `downloads_30d`, `open_issues`, `stars` | **90 days** | Re-verify these fields only |
| **Stable** | `license`, `api_shape`, `entry_points`, all reasons and rationale | **Never** | Only invalidated by escalation or human edit |

### Four rules that make the tiers work

**R1 — Partial re-verification, never re-research.** An expired field triggers a targeted fetch of that field. It does not re-open the candidate set, re-score rejected alternatives, or re-run research. Full re-research on expiry would destroy the entire caching benefit and turn every hit into a miss on a 30-day cycle.

**R2 — Major-version escalation.** If a Tier A re-verify finds the major version has advanced past `smoke_verified_version`, `api_shape` and `entry_points` are marked invalid, the smoke test is re-run against the new version, and `api_shape` is rewritten from the raw output. This is the one path by which a "never expires" fact expires — and it is driven by evidence rather than by a clock, which is the correct trigger for an API-shape change.

**R3 — Staleness never blocks.** A stale entry remains usable. If re-verification is impossible (offline, registry down, rate-limited), the recommendation proceeds and `techstack.md` records the actual verification date with an explicit staleness note. Refusing to answer because a download count is 91 days old would be a worse failure than answering with a slightly old number.

**R4 — Rejections age differently.** A rejection carrying `revisit_if` is re-evaluated only when that condition could plausibly have been met — for a maintenance rejection, when a Tier A re-verify shows a newer `last_release`. Rejections are otherwise not swept.

### `staleness_check.py`

Offline and read-only. Walks the catalog, compares `tier_a_verified_on` / `tier_b_verified_on` against today, prints expired fields per entry. It performs no verification itself — the agent decides whether an expired field is worth a network call for the question actually being asked. A Tier B expiry on an entry that is winning on `api_fit` and `dep_weight` may simply not be worth fetching, and that judgment does not belong in a script.

---

## 7. Control flows

### 7.1 Trigger evaluation (common prefix)

```
plan step drafted
   │
   ├─ implementation already begun in session? ──── yes ──▶ EXIT (never fire)
   │
   ├─ evaluate never-fire list (§3) ──────────────── hit ──▶ EXIT, no further load
   │
   ├─ evaluate two-of-four (§3) ────────────── under bar ──▶ EXIT, no further load
   │                                                          [cost ends here: ~1.2k tok]
   └─ fired ──▶ load catalog/INDEX.md ──▶ keyword match?
                                              │
                              ┌───────────────┴───────────────┐
                            match                          no match
                              │                                │
                         §7.2 CACHE HIT                 §7.3 CACHE MISS
```

### 7.2 Cache-hit path

```
1. Load catalog/domains/<slug>.md              (only the matched domain)
2. Read the `adopted` entry and the rejections in the same file
3. Run staleness_check.py on that entry        (offline, no network)
4. Any tier expired?
      no  ──▶ step 6
      yes ──▶ 5. Partial re-verify expired fields only  (R1)
                 └─ major version advanced?  (R2)
                       no  ──▶ update rotting fields, keep stable intact
                       yes ──▶ re-run smoke_test.py against new version
                               rewrite api_shape from raw output
                               update smoke_verified_version
                               [if this fails: entry drops to `rejected`,
                                fall through to §7.3 for the next candidate]
6. Confirm the recommendation still respects the ladder against the
   *current* project — an existing project dependency may now cover this
   domain, which flips the answer to "reuse what is already here"
7. Emit techstack.md entry: decision, rejected alternatives (from cache),
   smoke evidence, verification dates, staleness notes if any (R3)
8. Write back only changed rotting fields + verification dates
```

Note step 6. A cache hit is a hit on the *domain*, not on the *project*. The catalog cannot know what this project already depends on, so the project manifest is always consulted before the cached answer is emitted.

### 7.3 Cache-miss path

```
 1. Load references/research-protocol.md and references/rubric.md
 2. Enumerate candidates, capped (§8). The stdlib is ALWAYS a candidate.
    "Hand-rolled" is ALWAYS a candidate, with an LOC estimate.
 3. Fetch registry + repo facts per candidate  (PyPI / crates.io, then GitHub)
 4. Apply HARD GATES — eliminate outright:
       license_ok      OSI-compatible, no unexpected copyleft
       maintained      release within the Tier A horizon, issues answered
       installs_clean  install exits 0 in an isolated environment
       importable      import / link succeeds
    Every elimination is recorded with which gate failed. This is the
    raw material for the `rejected_alternatives` list.
 5. SCORE survivors 0–5 on: api_fit(×3) dep_weight(×2) adoption(×1)
    maintenance(×1) docs_typing(×1);  weighted = Σ(w·s)/8
 6. Apply the LADDER MARGIN (§8) — this is where the bias against
    dependencies is actually enforced, not merely stated
 7. Top candidate ≥ 3.2 after margin?
       no  ──▶ recommendation is "stdlib" or "write it yourself".
               Record it in the catalog as an entry. A pass with no
               library adopted is a RESULT, not a failure. (prd F1.4)
       yes ──▶ 8. Run smoke_test.py against the top candidate
                  ├─ exit 0 ──▶ step 9
                  └─ exit ≠0 ─▶ candidate → rejected with raw output as
                                 the reason; return to step 7 with the
                                 next-ranked candidate (max 3 attempts)
 9. Write api_shape and entry_points FROM the raw smoke output
10. Emit techstack.md
11. Write back to catalog:
      - create catalog/domains/<slug>.md if absent
      - add adopted entry + one rejected entry per eliminated candidate
      - add the domain row to INDEX.md
      - run catalog_lint.py; if the domain file exceeds its cap, split it
```

Step 11 is what makes research a one-time cost per domain. It is also the step most likely to be skipped once the answer is in hand, so it is part of the protocol rather than an afterthought.

### 7.4 What a smoke test must be

Full rules in `references/smoke-test-protocol.md`. The architectural constraints:

- Runs in an environment isolated from the target project — a throwaway venv or a temp cargo crate. It must not mutate the project it is advising.
- Installs the **exact pinned version** that will be recorded.
- Exercises the specific API surface the recommendation depends on, not merely `import x`. An import proves the package exists; it proves nothing about the decorator signature you are about to put in a plan.
- Emits raw stdout, stderr, and exit code. `smoke_test.py` prints; it never concludes.
- The agent reads that raw output. A summary of a smoke test is not a smoke test.

---

## 8. Rubric

Full anchors in `references/rubric.md`, loaded only on the miss path. Summarized here because it determines control flow.

### Hard gates — pass/fail, eliminate outright

| Gate | Pass condition |
| --- | --- |
| `license_ok` | OSI-approved and compatible with the target project; no unexpected copyleft |
| `maintained` | A release within the Tier A staleness horizon, or clear evidence of deliberate stability rather than abandonment |
| `installs_clean` | Isolated install exits 0 |
| `importable` | Import or link succeeds in that isolated environment |

A gate failure is recorded as `rejected_because = "gate:<name>"`. Gates run before scoring, so a failing candidate never consumes scoring effort.

### Weighted score

| Dimension | Weight | 5 means | 0 means |
| --- | --- | --- | --- |
| `api_fit` | ×3 | Does exactly the needed thing; the call site reads like the requirement | The need is reachable only by fighting the abstraction |
| `dep_weight` | ×2 | 0 transitive deps (or stdlib) | > 20 transitive deps |
| `adoption` | ×1 | Widely depended on; ecosystem-standard | Effectively unused |
| `maintenance` | ×1 | Active commits, issues triaged, releases regular | Barely inside the `maintained` gate |
| `docs_typing` | ×1 | Real docs and shipped type information | Source-reading required |

`weighted = Σ(weight × score) / 8`. **Recommend threshold: 3.2.**

`dep_weight` anchors: 5 → 0 deps · 4 → 1–2 · 3 → 3–5 · 2 → 6–10 · 1 → 11–20 · 0 → 20+.

### The ladder margin — how the bias is enforced

The preference ladder is applied as a **handicap**, not as advice. Tiers, best to worst:

```
T1 stdlib   T2 small focused package   T3 write it yourself   T4 large framework
```

> A "large framework" (T4) is any candidate with >20 transitive dependencies, or one that requires the project to be structured around it.

**Rule:** a candidate in a less-preferred tier must beat the best qualifying candidate in every more-preferred tier by **at least 0.5 weighted points** to win.

This is what stops "it scores 4.1, ship it" when the stdlib scores 3.8. Without the margin the ladder is a sentence in a document that the scoring silently ignores.

### Research caps

Enforced so the miss path cannot expand indefinitely (`prd.md` F5).

| Cap | Value |
| --- | --- |
| Candidates shortlisted | 6 (stdlib and hand-rolled always occupy 2 of these) |
| Network fetches | 12 |
| Smoke test attempts | 3 (top candidate, then next-ranked on failure) |
| Ecosystems per pass | 1 — the project's own |

---

## 9. Context cost per path

Rough estimates for budgeting, ±30%. Measured values replace these once `benchmark.md` runs.

| Path | What loads | Est. tokens |
| --- | --- | --- |
| **Idle** — skill never activates | Frontmatter only | ~60 |
| **Gate declines** — trigger considered, threshold not met | `SKILL.md` body | ~1,200 |
| **Cache hit, fresh** | above + `INDEX.md` (~800) + one domain file (~1,100) + `techstack-template.md` (~300) | **~3,400** |
| **Cache hit, stale Tier A** | above + `staleness_check` output (~150) + 1–2 registry fetches (~1,200) + write-back (~400) | **~5,150** |
| **Cache hit + major-version escalation** | above + smoke protocol (~600) + smoke raw output (~800) + rewrite (~400) | **~6,950** |
| **Cold miss** | gate + `INDEX.md` (~800) + `rubric.md` (~900) + `research-protocol.md` (~1,000) + 8–12 fetches (8,000–16,000) + `smoke-test-protocol.md` (~600) + smoke raw output (~800) + `SCHEMA.md` (~700) + write-back (~900) | **~14,000–22,000** |

Two things this table is meant to make obvious:

1. **The gate is the cheapest thing in the system.** A correct non-fire costs ~1.2k. This is what makes F4.2 achievable and why the threshold is evaluated before `INDEX.md` loads rather than after.
2. **Cold miss is roughly 4–6× a hit.** That ratio *is* the economic argument, and it is a hypothesis, not a fact — `benchmark.md` computes the actual break-even hit count rather than asserting one. If measured cold-miss cost is not recovered within a plausible number of reuses, `prd.md` F5.3 fails and the kill criteria apply.

---

## 10. Open questions

- **[OPEN]** Threshold definition (§3) — the two-of-four rule and the 80-LOC / 30-LOC boundaries are proposed, not confirmed. Benchmark C2 and T1–T6 are the tuning signal.
- **[OPEN]** Catalog seeding: shipped curated vs. empty-and-accreting. Affects whether the benchmark's hit path is exercisable at all.
- **[OPEN]** `techstack.md` at target-project repo root (§2).
- **[OPEN]** Ladder margin of 0.5 is a starting value with no evidence behind it yet. If F1.4 never fires across the benchmark, the margin is too small.
- Cross-domain components (something spanning `http-clients` and `retry-and-backoff`) currently load two domain files. Acceptable at two; needs a rule before it becomes four.
