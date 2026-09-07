#!/usr/bin/env python3
"""Tally which clause each DECLINE cited, from persisted raw streams.

The verdict text arrives split across stream deltas ("K" then "OSHA: ..."), so
searching the raw JSON per line finds nothing. Reconstruct the assistant text
by concatenating every "text" field, then search the reconstruction.
"""
import collections
import json
import pathlib
import re
import sys

TXT = re.compile(r'"text":"((?:[^"\\]|\\.)*)"')
VERDICT = re.compile(r"KOSHA:\s*DECLINE\s*(.{0,90})", re.I)


def classify(c):
    if "30" in c:
        return "NEVER-FIRE: under ~30 lines"
    if "80" in c:
        return "SIGNAL 1: under 80 lines"
    if any(w in c for w in ("plumb", "glue", "wiring", "shuffl")):
        return "NEVER-FIRE: glue / config plumbing"
    if "borderline" in c:
        return "AMBIGUITY RULE"
    if "user" in c and any(w in c for w in ("hand", "chose", "scoped", "explicit")):
        return "STATED INTENT (no such clause exists)"
    if "already" in c or "begun" in c:
        return "NEVER-FIRE: implementation begun"
    if "business" in c or "project-specific" in c:
        return "NEVER-FIRE: project-specific"
    return "other"


def main(d):
    d = pathlib.Path(d)
    cats, ex = collections.Counter(), {}
    for f in sorted(d.glob("*.txt")):
        parts = []
        for m in TXT.finditer(f.read_text(errors="replace")):
            try:
                parts.append(json.loads('"' + m.group(1) + '"'))
            except Exception:
                parts.append(m.group(1))
        m = VERDICT.search("".join(parts))
        if not m:
            continue
        c = " ".join(m.group(1).split())[:90].lower()
        k = classify(c)
        cats[k] += 1
        ex.setdefault(k, c)

    tot = sum(cats.values())
    if not tot:
        print("no declines found")
        return
    print(f"DECLINE clauses in {d.name} — {tot} readable\n")
    for k, n in cats.most_common():
        print(f"  {n:3d} ({n / tot:4.0%})  {k}")
        print(f'            e.g. "{ex[k][:76]}"')
    nf = sum(n for k, n in cats.items() if k.startswith("NEVER-FIRE"))
    s1 = cats.get("SIGNAL 1: under 80 lines", 0)
    si = cats.get("STATED INTENT (no such clause exists)", 0)
    am = cats.get("AMBIGUITY RULE", 0)
    print(f"\n  NEVER-FIRE (hard veto, survives any signal change): {nf}/{tot} = {nf / tot:.0%}")
    print(f"  SIGNAL 1  (what two-of-two would remove):           {s1}/{tot} = {s1 / tot:.0%}")
    print(f"  AMBIGUITY RULE:                                     {am}/{tot} = {am / tot:.0%}")
    print(f"  STATED INTENT (not a clause in the rule at all):    {si}/{tot} = {si / tot:.0%}")


if __name__ == "__main__":
    main(sys.argv[1])
