# Holdout — first exposure. **3 of 4. Not a pass.**

**Date:** 2026-09-07 · 4 probes × 5 reps = 20 runs · **ABSENT 0, ERROR 0**
**Condition:** first exposure, no tuning afterward, whatever the result. Provenance and independence weighting fixed in advance in `HOLDOUT_PROVENANCE.md`.

| # | Repo | Domain | Expected | Got | |
| --- | --- | --- | --- | --- | --- |
| H1 | LighteningParser | PDF → OCR extraction | FIRE | **5/5 FIRE** | PASS *(weakest independence)* |
| H2 | DevScout | schema migrations | FIRE | **5/5 FIRE** | PASS |
| H3 | Batchbird | SQL → AST | FIRE | **5/5 FIRE** | **PASS — strongest probe** |
| **H4** | swarm_drone_framework | control adaptation | **DECLINE** | **5/5 FIRE** | **FAIL** |

P1's exit criterion is *"the four holdout probes separate correctly on first exposure."* **It is not met.**

## H4: confident over-firing on a hand-written component

The gate did not waver. It fired 5/5 and named the domain:

```
KOSHA: FIRE swarm-consensus-control-with-safe-set-projection
```

That is a competent reading of the request — consensus control and safe-set projection *are* recognized techniques. But the project it was derived from **hand-wrote** `stability_tuner.py`, `safety_projector.py` and `hybrid_supervisor.py`, having adopted `scipy` and `numpy` freely everywhere a library fit. The write-it-yourself decision there was deliberate and correct.

### This is the borderline collision, and it is worse than the borderline set showed

`BORDERLINE_GAP.md` identified the failure shape: **a recognized problem class applied to something only this project has**, where the never-fire veto and the additive count collide and the rule cannot express the tension.

On the borderline set that collision produced **instability** — 0.60, 0.73, 0.60. Here, on a **real task**, it produced **confident, unanimous over-firing**. 5/5 with a fluent domain label.

That is the more worrying form. An unstable verdict at least signals that something is wrong. A 5/5 verdict signals nothing at all.

### The label question, recorded but not permitted to rescue the result

There is an argument H4 should fire: safe-set projection is a QP, and QP solvers are libraries; consensus protocols are well studied.

**The verdict stands as a FAIL.** The holdout's entire value is that it was never fitted to, and re-reading a label after seeing the result spends exactly that. Same handling as the slug query — the miss is scored, the label question is recorded separately and settles nothing here.

## What the holdout bought

Fifty fitted probes across four rounds did not surface this. One unfitted probe did, on the first try.

The three passes are also informative in order of weight: **H3 is the strongest positive** — an unseen domain, deliberately chosen over `csv` to avoid overlapping T6. H2 is a clean unseen-domain pass. **H1 counts for least**, exactly as recorded before the run: the author's own published library, its core path, vocabulary overlapping a description that already lists parsing and format handling.

The shape to have worried about was *"H1 passes, others fail."* That did not happen — the two strongest FIRE probes passed on unseen domains, and the single failure is in the DECLINE direction.

## First unfitted evidence bearing on option D

Not acted on. Recorded because it is the only evidence of its kind.

Option D's **swap test**: *replace every project-specific value; would a library still have to be written?* Swap the swarm's agents, envelope and dynamics — **you still write the policy.** Difficulty is project-specific, so D says never fire → **DECLINE**.

**D would have gotten H4 right.** Every prior assessment of D came from probes written by the same author as the rule; this one did not.

That is a real update in D's favour, and it does **not** license spending a threshold-rule round now:

- n = 1. One probe is an anecdote with a mechanism, not a result.
- The paper validation still stands: D destabilizes the vendor log parser, currently a clean 1.00.
- The holdout is now **spent**. Any rule change made in response would be fitted to the very probe that was supposed to be unfitted — the failure the holdout exists to prevent, arriving one step later.

**Both threshold-rule rounds remain unspent.** The correct place to test D is P7 against real usage, where H4-shaped tasks occur without anyone selecting them.

## P1 status

**P1 does not close clean.** Every other criterion is met — G2 must-fire 96%, no-fire 95% with the weighted subset 0/20, 0 ABSENT in 225 runs, F4.4 4/4 — and the holdout is 3/4 with a real defect in the DECLINE direction on real-world work.

Recording it as 3/4 rather than rounding to a pass. The failure is the most valuable single data point P1 produced.
