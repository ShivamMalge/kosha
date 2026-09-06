---
name: kosha
description: Check whether a library already solves a component before writing it, during PLANNING only. Use when a plan step proposes building something substantial that a package likely already does - retry with backoff, rate limiting, CLI flag and config layering, schema or tabular validation, parsing and serialization, scheduling, caching, protocol or format handling. Requires at least two of - roughly 80+ lines of non-trivial logic, a recognized problem class, would warrant its own test file. Do NOT use for - anything under ~30 lines, glue and wiring, config plumbing, type conversion, renaming or refactoring, project-specific business rules, a domain the project already depends on a library for, or any point after implementation has started. When borderline, do not use.
---

# kosha

Stops hand-rolling what a library already solves. Fires **at planning time only**, for components above a size and complexity bar.

Default answer is **no new dependency**:

```
stdlib  >  small focused package  >  write it yourself  >  large framework
```

A candidate must beat everything to its left, not merely be usable.

---

## 1. Threshold gate

Evaluate this **before loading anything else**. A decline costs only this file.

### Fire when at least two of three hold

| # | Signal | Test |
| --- | --- | --- |
| **1** | **Size** | Estimated 80+ lines of non-trivial logic |
| **2** | **Recognized problem class** | Names a known class: retry, backoff, rate limiting, parsing, serialization, validation, scheduling, concurrency primitives, protocol implementation, format handling, caching, diffing |
| **3** | **Testability burden** | Would warrant its own test file rather than being covered incidentally |

### Never fire when any of these hold

Checked **first**. A never-fire match ends evaluation regardless of the three signals.

- Under roughly 30 lines.
- Glue, wiring, config plumbing, or type shuffling between two things that already exist.
- Renaming, reordering, extracting, docstrings, typo fixes — refactors that add no capability.
- Project-specific business logic. No library knows your late-fee rule.
- **The project already depends on a library covering this domain.** Check the manifest first; recommending a second HTTP client is a defect.
- **Implementation has already begun in this session.** A plan-time skill firing at implementation time produces rewrites, not decisions.

### Ambiguity rule

If the two-of-three evaluation is genuinely borderline, **do not fire**.

The asymmetry is deliberate. A missed fire costs the user the status quo. A false fire costs tokens *and* teaches the user to disable the skill.

---

## 2. Why three signals, not four

An earlier draft carried a fourth: **edge-case density** — correctness turning on cases an author will not enumerate (timezones, unicode, floating point, partial writes, encoding).

It was cut because it could not be stated as a rule a second person would apply the same way. It named a category and left the judgment to taste, which fails the standard the other three meet. Shipping it would have meant only its author could operate the gate.

It is cut, not abandoned. Four probes in `eval/borderline.json` sit exactly on the size-versus-edge-density tension — a date-range helper with DST boundaries, a stable content hash over nested dicts, unicode normalization on display names, a bespoke log-line parser. If two-of-three misclassifies them, those four become concrete cases to define edge-case density **against**, which is how it becomes a rule rather than a category.

### Expected consequence, recorded before the first run

**Two-of-three fires more readily than two-of-four.** Removing a conjunct can only widen what qualifies: anything that fired under two-of-four still fires, and cases that previously needed the edge-case signal to reach two now reach it on size plus class, or class plus test burden.

So **over-firing is the predicted failure direction**, and it should surface in the four weighted queries in `eval/no-fire.json` — the ones carrying a signal that pulls toward firing:

- `swap requests for the httpx client we already depend on` — HTTP domain, already covered
- `we already use tenacity — add retry to this one call` — retry domain, already covered
- `add a --verbose flag to the existing argparse parser` — CLI domain, trivial, parser exists
- `add a 20-line adapter between the store interface and the new backend` — structural-sounding, under the bar

Each is caught by a **never-fire** clause rather than by the signal count, so they test whether the never-fire list carries the weight that the removed fourth signal used to.

**If A1 fails on these four, that is the instrument working, not a defect.** It localizes the loss to the never-fire list and yields the cases that define the missing signal. A1 failing on queries 1–18 would be a different and worse result: it would mean the gate is broadly undisciplined rather than specifically under-constrained.

---

## 3. Routing

**Stub — not yet implemented.** P1 tests the gate in isolation: no catalog, no network, no scripts.

Once the gate fires, control passes to the catalog index and then to at most one domain file. That path arrives in P4 (cache hit) and P5 (cache miss). See `architecture.md` §7.

Until then, a fire produces only the verdict and its reasoning.
