#!/usr/bin/env python3
"""UserPromptSubmit sentinel hook.

ENVELOPE ASSERTION -- `additionalContext` MUST be nested inside
`hookSpecificOutput`. Placed at the top level, Claude Code SILENTLY ignores
it: no error, no warning, the hook exits 0, and the context never arrives.
That is void-results shaped -- a clean run that measured nothing -- so the
shape is asserted here rather than trusted.
"""
import json
import sys

SENTINEL = "KOSHA-SENTINEL-7Q4X-ALPHA"

try:
    payload = json.load(sys.stdin)
except Exception:
    payload = {}

out = {
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": (
            SENTINEL
            + " :: If you can read this line, reply with the token "
            + SENTINEL
            + " verbatim somewhere in your response."
        ),
    }
}

# Fail loudly rather than emit a silently-ignored envelope.
hso = out.get("hookSpecificOutput")
assert isinstance(hso, dict), "hookSpecificOutput must be an object"
assert hso.get("hookEventName") == "UserPromptSubmit", "hookEventName mismatch"
assert isinstance(hso.get("additionalContext"), str), "additionalContext must be a string"
assert "additionalContext" not in out, "additionalContext must NOT be at top level"

prompt_len = len(str(payload.get("prompt", "")))

# Proof-of-execution log. This is what distinguishes the three outcomes:
#   log written + sentinel seen      -> hook works end to end
#   log written + sentinel NOT seen  -> hook ran, injection dropped (the bug)
#   no log at all                    -> hook never ran (settings not loaded)
# Without it, a missing sentinel is ambiguous and the test proves nothing.
try:
    import datetime
    import os

    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentinel_runs.log")
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(
            "%s fired prompt_len=%d cwd=%s\n"
            % (datetime.datetime.now().isoformat(timespec="seconds"), prompt_len, os.getcwd())
        )
except Exception as exc:  # never let logging break the hook
    sys.stderr.write("[sentinel-hook] log failed: %s\n" % exc)

sys.stderr.write("[sentinel-hook] fired; prompt_len=%d\n" % prompt_len)
print(json.dumps(out))
