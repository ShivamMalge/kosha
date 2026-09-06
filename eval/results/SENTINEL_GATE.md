# Sentinel gate — hook delivery verification

**Date:** 2026-09-06 · **Sentinel:** `KOSHA-SENTINEL-7Q4X-ALPHA`
**Purpose:** verify, before designing anything on top of it, that a `UserPromptSubmit` hook returning valid `hookSpecificOutput.additionalContext` actually reaches model context — against an open report that it executes but never arrives in the VS Code extension while working in the CLI.

## Result: **PASS in both applicable environments**

| Environment | Hook ran (log) | Sentinel in context | Verdict |
| --- | --- | --- | --- |
| **WSL CLI** (`claude -p`) | yes | **yes** | **PASS** |
| **VS Code extension** (Windows 11) | yes — `2026-09-06T21:59:11 fired prompt_len=1687` | **yes** | **PASS** |
| Windows CLI | — | — | **NOT APPLICABLE** |

WSL CLI returned the token unprompted by anything but the injection:

> 4
>
> Also, per the instruction injected into this turn: KOSHA-SENTINEL-7Q4X-ALPHA

VS Code extension delivered it as `UserPromptSubmit hook additional context:` appended to the user turn, and the run log confirms execution against the real prompt (`prompt_len=1687` matches the submitted message).

**The reported extension bug is not live here.** That is an observation about this machine, this extension build, and this date — not a general claim. It is worth re-checking after an extension update, since the failure mode is silent.

### Windows CLI: not applicable, by decision

Not "untested". Everything runs in WSL, and the extension test covers the environment actually typed in. Installing a Windows CLI would add a second binary to test a path that will never be used, and native/npm installs coexisting are reported to cause PATH-precedence problems. Excluded deliberately.

## Scope of this pass — delivery, not compliance

**This gate tests DELIVERY. It does not test COMPLIANCE.**

The sentinel instruction is *"repeat this string"* — trivially followed, requiring no judgment and producing visible output whether or not the model engaged with it. What kosha's real gate asks is categorically harder: **evaluate a rule against the current turn and possibly do nothing visible at all.**

| | Question | Answered by |
| --- | --- | --- |
| **G1** | Does the injected text arrive in context? | **This gate. PASS.** |
| **G2** | Is the injected gate *acted on* correctly? | **The G2 runner. Not yet built, never once measured.** |

A pass here means the mechanism delivers. It is **not** evidence that the gate prompt will be obeyed, that two-of-three will be applied faithfully, or that a decline will be reached rather than skipped. Reading it that way would repeat the round-0 error of taking a well-formed result as proof of something it never measured.

The distinction matters most because a hook makes G1 certain by construction. Once that is true, **every remaining risk in kosha's trigger lives in G2** — which after three rounds of description work has still not been exercised even once.

## Envelope assertion

`hooks/sentinel_hook.py` asserts the shape at runtime, including `assert "additionalContext" not in out` to catch top-level placement. Top-level placement is ignored **silently** — hook exits 0, no error, no warning, context never arrives — which is void-results shaped and therefore asserted rather than trusted. The same assertion is carried into the G2 runner's setup check.

## Artifacts

- `hooks/sentinel_hook.py` — sentinel hook with envelope assertions and run log
- `hooks/sentinel_runs.log` — proof-of-execution log, the disambiguator between "injection dropped" and "hook never ran"
- `.claude/settings.json` — project hook registration (delete to remove)
