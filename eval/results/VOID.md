# A1 and A2 results are VOID — do not read as data

**Date:** 2026-09-06

Both passes executed to exit code 0 and produced well-formed JSON. **Every call inside them failed.**

| Pass | Reported | Calls attempted | Calls failed | Valid |
| --- | --- | --- | --- | --- |
| A1 no-fire | 22/22 pass, all 0/5 | 110 | **110** | no |
| A2 must-fire | 0/20 pass, all 0/5 | 100 | **100** | no |

Cause: `Warning: query failed: [WinError 2] The system cannot find the file specified`, on every call.
`run_eval.run_single_query` shells out to `claude -p`. There is no `claude` executable on this machine —
`shutil.which("claude")` returns `None`, and it is absent from npm global root, AppData, and PATH.
This session runs as a VSCode native extension with a bundled runtime, not via a standalone CLI.

## Why A1's 22/22 is the more dangerous number

A failed subprocess counts as a **non-trigger**. So a total instrumentation failure renders every
`should_trigger: false` query a pass and every `should_trigger: true` query a fail. A1 did not measure
a disciplined gate; it measured nothing, and the shape of "nothing" happens to look exactly like a
perfect over-trigger score.

Read alone, A1 would have been reported as the gate performing flawlessly on the four weighted queries.

## This is the error-count rule working

`benchmark.md` §2 and `eval/EXPECTED.md` both require the subprocess error count to be reported beside
every trigger rate, with any non-zero count invalidating the pass. That rule was written for exactly
this failure and it caught it on first contact. No tuning round was spent on a phantom result.

## Unblocking

`run_eval.py` needs a `claude` binary on PATH: `npm install -g @anthropic-ai/claude-code`.
That is an install on the user's machine and has not been performed. No harness patch is warranted —
the script is correct; the environment lacks its dependency.
