# What "rethinking rather than adjusting" concretely means

**Date:** 2026-09-07 · **Written BEFORE the last round runs**, deliberately.

P1's *Stop here if* reads:

> the **threshold rule** cannot separate the probe set after two rounds of tuning. Not "tune it again" — a rule that needs a third round of hand-fitting against known cases will not generalize to unseen ones, and the design needs rethinking rather than adjusting.

Round 1 is spent and failed. The paper check (`R3_PAPER_CHECK.md`) puts the round-2 ceiling at **~86%** against F4.3's requirement of effectively 100%. **The likely outcome is improvement that still misses**, which fires this criterion.

That is a legitimate result, not a failed round. But it arrives with disappointment attached, and a kill criterion decided under disappointment is a kill criterion being negotiated. So the options are enumerated now, while nothing is at stake.

**These are enumerated, not chosen.** Choosing happens after the data, from this list.

---

## Option 1 — Revisit whether F4.3's threshold is right for a model-mediated decision

F4.3 requires the gate to fire in **every repetition**. That was written when the trigger was assumed deterministic-ish. Everything measured since says a model-mediated judgment is a *distribution*, not a function: 96% / 89% / 54% across registers, three borderline queries stable at 0.60–0.73, verdicts that differ run to run on identical input.

**The question this option asks:** is "effectively 100%" a coherent requirement for a decision made by a model at all, or was it imported from a world of deterministic triggers?

- **For:** no other criterion in `prd.md` demands perfection; F1.2 accepts a mean, F5.1 accepts 40%. F4.3's absolutism may be an unexamined inheritance.
- **Against:** this is the option that most resembles moving the goalposts. It must not be chosen *because* the number came in low. It is only legitimate if the argument would have been made at the same strength before seeing round 2 — and the honest test is that **this file was written before the run.**
- **What would justify it:** a defensible replacement threshold derived from cost, not from the observed number. E.g. "kosha must fire on ≥ X% of real hand-rolling requests for the LOC saving in `benchmark.md` F5.1 to exceed its token cost" — a figure P7 could compute.

## Option 2 — Move gating out of model judgment entirely

The gate becomes deterministic: keyword/AST matching, a manifest check, a static domain list. The model's role shrinks to *researching and recommending* once a deterministic trigger has fired.

- **For:** every failure in P1 is a judgment failure, not a research failure. The catalog, rubric, smoke runner and ladder are untouched by all of this. G1 was made deterministic with a hook and the problem moved to G2; this finishes the same move.
- **Against:** a deterministic gate cannot weigh "recognized problem class" or "would warrant its own test file" — the two signals doing the real work. It would over-fire on keywords, which is where the description started in round 0 and why the gate moved into the body.
- **What it costs:** the two-of-three rule as designed. `architecture.md` §3 would be rewritten, not adjusted.

## Option 3 — Narrow kosha's scope to the register where it works

kosha fires 96% on planning-framed requests and 54% on implementation-framed ones. Option 3 accepts that and **scopes the product to planning**: kosha is a planning-time consultant, invoked when someone is deciding, and explicitly *not* a guardrail that catches you mid-decision.

- **For:** honest about measured behaviour, and it is the register the whole design was built around — `SKILL.md` §0 already says "fire at planning time only."
- **Against:** it concedes the `prd.md` §1 premise. That document describes the failure as an agent hand-rolling *without anyone thinking to check* — and someone who writes "write the retry loop by hand" has not thought to check. **Scoping to planning means kosha helps people who were already going to ask.** This is the same scope reduction identified for the slash-command mechanism, arriving by a different route.
- **What it costs:** `prd.md` §1 must be rewritten, and F4.3 rewritten to apply only to the planning register. If chosen, it ships labelled as a reduced-scope product, exactly as recorded for the slash command.

## Option 4 — Accept a measured miss and continue with it documented

Ship the gate at whatever rate round 2 achieves, record the register-dependent numbers prominently, and let P7 measure the real-world mix of planning-framed versus implementation-framed requests.

- **For:** the true cost depends on a frequency nobody has measured. If real usage is 90% planning-framed, an 86% gate is fine; if it is 90% implementation-framed, it is not. **That number does not exist yet**, and every option above is being chosen without it.
- **Against:** it defers the decision by building P2–P6 on a trigger known to miss — the exact reasoning that justified spending a round now rather than at P7.
- **Distinguishing it from Option 1:** Option 1 changes the standard. Option 4 keeps the standard, records the failure against it, and proceeds with the gap visible. Option 4 is honest; Option 1 is honest only if its argument stands independently of the result.

---

## The decision rule

**If round 2 lands below F4.3's requirement, at least one of these four is chosen and recorded with its reasoning. "Run a third round" is not on the list.**

The one guard worth stating plainly: **Option 1 is the tempting one and the dangerous one.** It resolves the failure by adjusting the measure. It is available, and it may well be correct — the evidence that a model-mediated decision is a distribution is genuinely strong. But it is only legitimate on an argument that would have been made at the same strength before the number arrived, which is why the argument is written here, in advance, rather than assembled afterwards.
