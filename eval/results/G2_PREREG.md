# G2 round 1 — pre-registration

**Written before the runner executes.** Names the gate, the instrument, and the falsifier, per the round-0 post-mortem lesson.

## Gate and instrument

| | |
| --- | --- |
| **Gate under test** | **G2 (proceed)** — given a guaranteed injection, is the two-of-three rule applied correctly |
| **Instrument** | `scripts/g2_runner.py`, `--runs-per-query 5`, `--num-workers 2`; hook installed via `hooks/kosha_gate_hook.py` |
| **Not under test** | **G1 (load).** Deterministic by construction under the hook, and verified end-to-end in `SENTINEL_GATE.md`. |

**This is the first measurement in the project that is actually about the two-of-three rule.** Three rounds of G1 work never reached it once.

## What is measured — three outcomes, not two

| Outcome | Meaning |
| --- | --- |
| `FIRE` | `KOSHA: FIRE <domain>` emitted |
| `DECLINE` | `KOSHA: DECLINE <clause>` emitted |
| `ABSENT` | neither line appeared |

**`ABSENT` is never folded into `DECLINE`.** They look alike in aggregate and mean opposite things: a DECLINE is the rule working, an ABSENT is the model ignoring the gate. Collapsing them would report a compliance failure as correct behaviour — the same error as reading the void batch's zeros as a disciplined gate.

`ABSENT` is therefore its own pre-registered prediction, because it measures something the sentinel gate explicitly could not: the sentinel proved **delivery**, not **compliance**.

## Predictions

### Compliance — does the gate get obeyed at all

**`ABSENT` ≤ 10% across all 50 queries.**

**Falsifier: ABSENT > 25%.** That would mean the gate is frequently ignored, and no FIRE/DECLINE rate computed from the remainder is trustworthy — the denominator would be self-selected. If this falsifies, everything below is void and the finding is about instruction-following, not about the rule.

### F4.3 direction — must-fire (T1–T6, 20 queries, 100 runs)

| | Prediction |
| --- | --- |
| `FIRE` rate | **≥ 85%** |
| Per-domain floor | no domain below **70%** |

Rationale for predicting high, where G1 never exceeded 47%: the gate is now *in context by construction* and states its rule explicitly. The failure mode that capped G1 — the model never seeing kosha at all — cannot occur. What remains is instruction-following on an explicit rule, which should be substantially more reliable than topical matching against a description.

**Falsifier: FIRE < 60%.** Below that, an explicit in-context rule is being applied worse than a coin flip on cases chosen to be clearly above the bar, and the two-of-three rule itself is the problem rather than the trigger.

### F4.1 direction — no-fire (22 queries, 110 runs)

| | Prediction |
| --- | --- |
| `DECLINE` rate | **≥ 90%** |
| `FIRE` rate | **≤ 10%** |
| **Weighted subset 19–22** (the real test — 4 queries, 20 runs) | `FIRE` **≤ 2/20** |

Reported as two lines, per the standing rule: full set, and weighted subset with its own denominator. Queries 1–18 are close to free.

Two never-fire clauses are **untestable in this harness** and are excluded from scoring rather than silently counted:

- *"implementation has already begun in this session"* — `claude -p` is a single turn with no history, so the clause can never trigger. F4.4 remains hand-session work.
- *"the project already depends on a library covering this domain"* — the throwaway project has no manifest. Queries 19–20 state the dependency **in the query text**, so they still test the clause; a real manifest check does not.

**Falsifier: FIRE > 25% on the full no-fire set, or > 5/20 on the weighted subset.**

### Borderline (8 queries)

Consistency only, at **15 reps**, band `fire_rate ≤ 0.2 or ≥ 0.8`, unchanged from `benchmark.md` §2. No claim about direction. At n=15 a true coin-flip escapes the band 3.52% of the time.

## What would make this round a failure

- `ABSENT` > 25% — gate ignored; all other numbers void.
- must-fire `FIRE` < 60% — the rule is the problem.
- no-fire weighted subset `FIRE` > 5/20 — the rule does not discriminate where it matters.

## Threats to this measurement

- **Single-turn probes.** Every query runs as a fresh `claude -p` with no history. Real planning turns carry context, which could push either way. This measures the rule in the cleanest possible condition, so it is an **upper bound** on rule quality, not an estimate of field behaviour.
- **The verdict line is permanent** (`SKILL.md` §1, gate prompt), so benchmark and production are the same condition and the observer effect is neutralized rather than merely acknowledged.
- **n = 5 per query.** Per-query rates are not individually readable; aggregates over register (n=30) and domain (n=15–20) are the trustworthy figures — unchanged from round 1.
- The `should_trigger` field is carried through unused for scoring; direction comes from which eval set a query belongs to.

## Sealed

`holdout.json` remains unwritten and unopened. It tests the **rule**, which this runner finally makes testable — but it is not opened until this round has reported.
