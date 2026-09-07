# Holdout — first exposure. **3 valid probes passed; 1 invalid by construction.**

> **Scoring correction (2026-09-07).** Not 4/4 and not 3/4. **H4 is invalid by construction** — see *H4's label was never establishable* below. The score is **3 valid probes, all passed; 1 probe that could not have been valid.**

**Date:** 2026-09-07 · 4 probes × 5 reps = 20 runs · **ABSENT 0, ERROR 0**
**Condition:** first exposure, no tuning afterward, whatever the result. Provenance and independence weighting fixed in advance in `HOLDOUT_PROVENANCE.md`.

| # | Repo | Domain | Expected | Got | |
| --- | --- | --- | --- | --- | --- |
| H1 | LighteningParser | PDF → OCR extraction | FIRE | **5/5 FIRE** | PASS *(weakest independence)* |
| H2 | DevScout | schema migrations | FIRE | **5/5 FIRE** | PASS |
| H3 | Batchbird | SQL → AST | FIRE | **5/5 FIRE** | **PASS — strongest probe** |
| **H4** | swarm_drone_framework | control adaptation | *(unestablishable)* | 5/5 FIRE | **INVALID — not scored** |

P1's exit criterion is *"the four holdout probes separate correctly on first exposure."* **Three valid probes met it. The fourth could not have.**

## H4: what it returned, and why it cannot be read

The gate did not waver. It fired 5/5 and named the domain:

```
KOSHA: FIRE swarm-consensus-control-with-safe-set-projection
```

That is a competent reading of the request — consensus control and safe-set projection *are* recognized techniques. But the project it was derived from **hand-wrote** `stability_tuner.py`, `safety_projector.py` and `hybrid_supervisor.py`, having adopted `scipy` and `numpy` freely everywhere a library fit. The write-it-yourself decision there was deliberate and correct.

H4 has the *shape* of the collision `BORDERLINE_GAP.md` describes — a recognized problem class applied to something only one project has. On the borderline set that collision produced instability (0.60, 0.73, 0.60); here the gate was unanimous and fluent.

**But that reading requires knowing DECLINE was correct, and we do not.** With the label unestablishable, 5/5 FIRE is equally consistent with the gate being right. It cannot be cited as evidence of over-firing, and it is not cited that way below.

### H4's label was never establishable by the method used

The derivation method was *"what each project actually resolved in shipped code."* That method is sound for a **FIRE** probe and unsound for a **DECLINE** probe, and the asymmetry is structural:

| Probe direction | What the evidence shows | Sound? |
| --- | --- | --- |
| **FIRE** (H1–H3) | the project adopted a library, so a suitable library **demonstrably exists** | yes |
| **DECLINE** (H4) | the project hand-wrote it — equally consistent with **(a)** no library existed and **(b)** the author missed one | **no** |

H4's ground truth rests on the author's own past decision having been correct. **kosha exists precisely to catch the cases where it was not.** Using a hand-written component as proof that no library was warranted assumes away the failure kosha is built to detect.

**This argument does not depend on the outcome.** It was true when the probe was designed and is statable without reference to what H4 returned — which is exactly what separates it from re-reading the slug label after the fact. The QP-solver argument *was* post-hoc and was correctly rejected; this is a different objection, aimed at the derivation rather than the verdict.

### The consequence: over-firing was never tested on unfitted data

H4 existed because three FIRE probes test only under-firing — a gate that fired on everything would have passed. With H4 invalid, **the holdout never tested the over-firing direction at all.**

That gap is real and is **not repaired now.** Deriving a replacement after seeing these results contaminates it, and the holdout is spent either way. Carried to **P7** as a known untested property, filed alongside the option-D question and the ambiguity-rule gap.

A sound DECLINE probe would need ground truth from something other than a past authoring decision — a domain where the absence of a library is verifiable rather than inferred.

## What the holdout bought

Three unfitted FIRE probes passed on first exposure, two of them on domains the gate had never been measured against. That is a real generalization result, and it is the whole of what this holdout established.

The passes in order of weight: **H3 is the strongest positive** — an unseen domain, deliberately chosen over `csv` to avoid overlapping T6. H2 is a clean unseen-domain pass. **H1 counts for least**, exactly as recorded before the run: the author's own published library, its core path, vocabulary overlapping a description that already lists parsing and format handling.

The shape to have worried about was *"H1 passes, others fail."* That did not happen — the two strongest FIRE probes passed on unseen domains.

## Option D — the apparent evidence dissolves with the label

An earlier draft recorded H4 as *the first unfitted evidence in D's favour*: D's swap test says the swarm's difficulty is project-specific, so D would have declined, so D would have "got H4 right."

**That claim does not survive the invalidity argument, and the same reasoning kills it.** "D would have got it right" presupposes DECLINE was the correct answer. If H4's label was never establishable, then neither is the claim that D would have matched it. The probe cannot confirm D any more than it can convict the gate.

Recorded because the inference was drawn and then withdrawn on its own logic, not because the conclusion changed.

**The handling is unchanged and now rests on firmer ground:** both threshold-rule rounds stay unspent. Previously that was a judgment against thin evidence; now there is no unfitted evidence bearing on D at all. The paper validation still shows D destabilizing the vendor log parser, and the holdout is spent. P7, against real usage, remains the place to test it.

## P1 status

**Three of three valid holdout probes passed on first exposure**, including H3, the strongest and most independent. Every other criterion is met: G2 must-fire 96%, no-fire 95% with the weighted subset 0/20, 0 ABSENT across 225 runs, F4.4 4/4.

What P1 does **not** carry is any unfitted evidence about **over-firing** — the one property H4 was meant to supply. That is recorded as an open gap rather than counted as a pass or a failure.
