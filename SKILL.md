---
name: kosha
description: Find whether an existing library already solves a component before writing it by hand. Covers retry, backoff and jitter; rate limiting, throttling, HTTP clients and Retry-After; CLI flags, argument parsing, layered config from files and environment variables; validating tables, dataframes, columns, schemas, nullability and value ranges; parsing and serializing CSV, JSON, TOML, YAML and parquet; deserializing rows into typed structs; scheduling, caching, diffing, hashing, date and timezone handling, unicode normalization, and concurrency primitives. Suggests stdlib first, then a small focused package, and is willing to say write it yourself. Python (PyPI) and Rust (crates.io).
---

# kosha

Stops hand-rolling what a library already solves.

Default answer is **no new dependency**:

```
stdlib  >  small focused package  >  write it yourself  >  large framework
```

A candidate must beat everything to its left, not merely be usable.

---

## 0. Timing — check this first

**Fire at planning time only.** If implementation of this component has already begun in this session, **stop here and do nothing.** A plan-time skill firing at implementation time produces rewrites, not decisions.

This constraint lives here, in the body, and not in the frontmatter description, for a specific reason: whether implementation has begun is a property of the **conversation**, not of the query text. A description can only match it on surface form — it would fire on the word "planning" appearing in a sentence and miss the actual state of the session. Round 0 measured exactly that failure: every fire came from queries that read like plan prose, and terse requests never loaded the skill at all.

So the description's job is **topical** — is this turn about choosing or building a component a library might already solve. Timing and threshold are decided here.

Under deterministic invocation the gate is evaluated on **every** turn, so a decline must be cheap. It is: the hook injects the **compact gate** (`hooks/gate_prompt.txt`, ~246 tokens), not this file. This body loads only on a FIRE (~1,496 tokens), so a correct decline costs the gate alone — `prd.md` F4.2, re-based from 1,500 to **400 tokens** on exactly this basis. Session-aggregate cost is bounded by F4.5 and measured in `benchmark.md` §7.4.

---

## 1. Threshold gate

Evaluate before loading anything else. A decline costs only this file.

### Fire when at least two of three hold

| # | Signal | Test |
| --- | --- | --- |
| **1** | **Size** | Estimated 80+ lines of non-trivial logic |
| **2** | **Recognized problem class** | Names a known class: retry, backoff, rate limiting, parsing, serialization, validation, scheduling, concurrency primitives, protocol implementation, format handling, caching, diffing |
| **3** | **Testability burden** | Would warrant its own test file rather than being covered incidentally |

### Never fire when any of these hold

Checked **first**. A never-fire match ends evaluation regardless of the three signals.

- Implementation has already begun in this session (§0).
- Under roughly 30 lines.
- Glue, wiring, config plumbing, or type shuffling between two things that already exist.
- Renaming, reordering, extracting, docstrings, typo fixes — refactors that add no capability.
- Project-specific business logic. No library knows your late-fee rule.
- **The project already depends on a library covering this domain.** Check the manifest first; recommending a second HTTP client is a defect.

> The never-fire list carries weight the description no longer does. `config plumbing` and `type shuffling` were previously in the frontmatter, where they suppressed the very queries kosha exists to catch — "cli config layering" and "csv to typed structs" scored 0/5 against a description containing `config plumbing` and `type conversion`. Negative constraints belong here, applied with the component in view, not in a string matched against raw query text.

### The verdict line — permanent, not a benchmark affordance

Every evaluation of this gate emits **exactly one line**:

```
KOSHA: FIRE <domain>
KOSHA: DECLINE <clause>
```

This stays in the shipped skill permanently, and the reason is not formatting. Stating the decision aloud makes it explicit and output-visible, and **a rule stated aloud is applied more deliberately than one applied silently.** If the line existed only while measuring, the G2 runner would be measuring the rule *under observation* while production ran a different, un-measured condition.

Permanence neutralizes the observer effect by making benchmark and production the same condition. The line is part of the product, not the instrument.

### Ambiguity rule

If the two-of-three evaluation is genuinely borderline, **do not fire**.

The asymmetry is deliberate. A missed fire costs the user the status quo. A false fire costs tokens *and* teaches the user to disable the skill.

---

## 2. Why three signals, not four

An earlier draft carried a fourth: **edge-case density** — correctness turning on cases an author will not enumerate (timezones, unicode, floating point, partial writes, encoding).

It was cut because it could not be stated as a rule a second person would apply the same way. It named a category and left the judgment to taste, which fails the standard the other three meet. Shipping it would have meant only its author could operate the gate.

It is cut, not abandoned. Four probes in `eval/borderline.json` sit on the size-versus-edge-density tension. If two-of-three misclassifies them, those four become concrete cases to define edge-case density **against**, which is how it becomes a rule rather than a category.

### Round-0 prediction: recorded as WRONG

An earlier version of this section predicted that two-of-three would fire **more** readily than two-of-four, so over-firing was the expected failure direction, surfacing in the weighted `no-fire.json` queries.

**The opposite happened.** Round 0 measured severe *under*-firing: 6% of must-fire runs loaded the skill, and the weighted queries returned 0/5. Recorded as a failed prediction rather than reframed.

The error was one of **scope**, not logic: it forecast the behaviour of G2 (the rule) using an instrument that can only see G1 (the load). The rule was never reached, so the claim remains untested — which does not make the prediction right. Subsequent pre-registrations name the gate and the instrument that would falsify them (`eval/results/ROUND1_PREREG.md`).

---

## 3. Routing

**Stub — not yet implemented.** P1 tests the gate in isolation: no catalog, no network, no scripts.

Once the gate fires, control passes to the catalog index and then to at most one domain file. That path arrives in P4 (cache hit) and P5 (cache miss). See `architecture.md` §7.

Until then, a fire produces only the verdict and its reasoning.
