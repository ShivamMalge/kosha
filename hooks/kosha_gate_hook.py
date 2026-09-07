#!/usr/bin/env python3
"""kosha UserPromptSubmit hook - injects the compact gate.

Injects `gate_prompt.txt` (~246 tokens), NOT SKILL.md (~1,496). The gate
carries the never-fire list, the two-of-three rule and the verdict-line
instruction, and tells the model to read SKILL.md only on a FIRE. See
benchmark.md 7.4 for the cost derivation.

ENVELOPE ASSERTION -- `additionalContext` MUST be nested inside
`hookSpecificOutput`. At the top level Claude Code SILENTLY ignores it: the
hook exits 0, nothing warns, and the context never arrives. That is
void-results shaped, so the shape is asserted rather than trusted.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "gate_prompt.txt")


def build_envelope(gate_text):
    """Build the hook response. Kept separate so the runner can assert on it."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": gate_text,
        }
    }
    assert_envelope(out)
    return out


def assert_envelope(out):
    """Shared by the hook and the G2 runner's setup check."""
    assert isinstance(out, dict), "envelope must be an object"
    assert "additionalContext" not in out, (
        "additionalContext must NOT be at the top level - Claude Code ignores it silently"
    )
    hso = out.get("hookSpecificOutput")
    assert isinstance(hso, dict), "hookSpecificOutput must be an object"
    assert hso.get("hookEventName") == "UserPromptSubmit", "hookEventName mismatch"
    ctx = hso.get("additionalContext")
    assert isinstance(ctx, str) and ctx.strip(), "additionalContext must be a non-empty string"
    assert "KOSHA:" in ctx, "gate text must instruct the verdict line"
    return True


def main():
    try:
        json.load(sys.stdin)  # payload unused; consumed so the hook does not block
    except Exception:
        pass

    with open(GATE, encoding="utf-8") as fh:
        gate_text = fh.read()

    print(json.dumps(build_envelope(gate_text)))


if __name__ == "__main__":
    main()
