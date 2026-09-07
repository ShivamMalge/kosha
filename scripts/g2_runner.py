#!/usr/bin/env python3
"""G2 runner - measures whether the injected gate is ACTED ON.

run_eval.py measures G1: does the skill description cause the skill to LOAD.
Under deterministic invocation a UserPromptSubmit hook makes loading certain,
so G1 is no longer in doubt and run_eval no longer tests anything uncertain.

This runner measures G2: given a guaranteed injection, does the model apply
the two-of-three rule correctly. It is new code written ALONGSIDE the harness;
run_eval.py is never modified.

Continuity: it consumes the existing eval sets VERBATIM, at the same reps, so
every register/domain breakdown and all pre-registration continuity from
rounds 0 and 1 carries over.

THREE OUTCOMES, NOT TWO
    FIRE     the model emitted `KOSHA: FIRE <domain>`
    DECLINE  the model emitted `KOSHA: DECLINE <clause>`
    ABSENT   neither line appeared

ABSENT is counted separately and never folded into DECLINE. They look alike
in aggregate and mean opposite things: a DECLINE is the rule working, an
ABSENT is the model ignoring the gate entirely. Collapsing them would report
a compliance failure as correct behaviour - the same class of error as
reading the void batch's zeros as a disciplined gate.

Usage:
    g2_runner.py --eval-set eval/must-fire.json --skill-path . \
                 --runs-per-query 5 --out eval/results/G2_must-fire.json
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOOKS = os.path.join(ROOT, "hooks")

VERDICT_RE = re.compile(r"KOSHA:\s*(FIRE|DECLINE)\s*(.*)", re.IGNORECASE)


# --------------------------------------------------------------------------
# setup checks - fail before spending calls, not after
# --------------------------------------------------------------------------
def setup_check(skill_path):
    """Assert the instrument is alive and correctly shaped.

    The lesson from the void batch: a run that produces well-formed output
    while measuring nothing is worse than a crash. Everything cheap that can
    be verified in advance is verified in advance.
    """
    problems = []

    gate = os.path.join(HOOKS, "gate_prompt.txt")
    hook = os.path.join(HOOKS, "kosha_gate_hook.py")
    for path in (gate, hook):
        if not os.path.isfile(path):
            problems.append("missing: %s" % path)

    # Envelope assertion, shared with the hook itself.
    if os.path.isfile(hook):
        sys.path.insert(0, HOOKS)
        try:
            import kosha_gate_hook

            with open(gate, encoding="utf-8") as fh:
                kosha_gate_hook.assert_envelope(kosha_gate_hook.build_envelope(fh.read()))
        except AssertionError as exc:
            problems.append("envelope assertion failed: %s" % exc)
        except Exception as exc:
            problems.append("hook import failed: %s" % exc)

    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(skill_md):
        problems.append("missing SKILL.md at %s" % skill_path)
    else:
        with open(skill_md, encoding="utf-8") as fh:
            if "KOSHA: FIRE" not in fh.read():
                problems.append("SKILL.md does not specify the verdict line")

    if _which("claude") is None:
        problems.append("`claude` not on PATH")

    return problems


def live_probe(project_root, timeout=180):
    """One real call before the batch. Static checks cannot catch a dead instrument.

    The first G2 batch passed every static check and still measured nothing.
    This asserts the pipeline actually returns a verdict before spending 300+ calls.
    """
    verdict, detail, error = run_once(
        "csv to typed structs with per-row errors", project_root, timeout)
    return verdict, detail, error


def _which(name):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        cand = os.path.join(d, name)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


# --------------------------------------------------------------------------
# hook installation
# --------------------------------------------------------------------------
def make_project(skill_path):
    """A throwaway project whose settings register the gate hook."""
    proj = tempfile.mkdtemp(prefix="kosha_g2_")
    claude_dir = os.path.join(proj, ".claude")
    os.makedirs(claude_dir)
    cmd = '"%s" "%s"' % (sys.executable, os.path.join(HOOKS, "kosha_gate_hook.py"))
    settings = {
        "hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": cmd}]}]}
    }
    with open(os.path.join(claude_dir, "settings.json"), "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)
    # Make SKILL.md reachable for the FIRE path.
    with open(os.path.join(proj, "SKILL_PATH"), "w", encoding="utf-8") as fh:
        fh.write(os.path.abspath(skill_path))
    return proj


# --------------------------------------------------------------------------
# one run
# --------------------------------------------------------------------------
def run_once(query, project_root, timeout, model=None, raw_dir=None, tag=""):
    """Return (verdict, detail, error): FIRE | DECLINE | ABSENT | ERROR.

    STREAMS and terminates early. The verdict line is the first thing the model
    emits; the rest of the answer can run for another 60-90 seconds and tells us
    nothing. Waiting for completion made a 330-run batch a ~4 hour job whose
    calls sat marginally under the timeout -- so this reads streamed events and
    kills the process the moment a verdict appears. Same technique run_eval.py
    uses, and the reason its passes finished in minutes.

    ERROR is separate from ABSENT on purpose. A call that fails fast -- non-zero
    exit, empty output, a quota message -- produces no verdict line, and folding
    that into ABSENT reports an instrument failure as model behaviour. That is
    exactly how the first G2 batch returned 93-100% ABSENT: `claude -p` blocks
    reading stdin unless it is redirected, and the runner could not tell a hung
    call from genuine non-compliance.
    """
    cmd = ["claude", "-p", query,
           "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,   # REQUIRED: claude -p otherwise blocks on stdin
            cwd=project_root,
            env=env,
            text=True,
            bufsize=1,
        )
    except Exception as exc:
        return "ERROR", "", "spawn: %s" % exc

    accumulated = []
    verdict = None
    detail = ""
    deadline = time.time() + timeout

    try:
        for line in proc.stdout:
            accumulated.append(line)
            # Cheap: search the raw event line. Text deltas carry the characters
            # verbatim, so the token appears without needing to parse the schema.
            m = VERDICT_RE.search(line)
            if m:
                verdict = m.group(1).upper()
                detail = m.group(2).strip().strip('"\\ ,}')[:80]
                break
            if time.time() > deadline:
                break
    except Exception as exc:
        return "ERROR", "", "read: %s" % exc
    finally:
        if proc.poll() is None:
            proc.kill()
        try:
            proc.wait(timeout=10)
        except Exception:
            pass

    raw = "".join(accumulated)

    if raw_dir:
        try:
            os.makedirs(raw_dir, exist_ok=True)
            with open(os.path.join(raw_dir, "%s.txt" % tag), "w", encoding="utf-8") as fh:
                fh.write("verdict=%s\n--- stream ---\n%s" % (verdict, raw[:20000]))
        except Exception:
            pass

    if verdict:
        return verdict, detail, None
    if not raw.strip():
        return "ERROR", "", "empty stream"

    # Infrastructure failures arrive as a normal assistant message with exit 0,
    # so returncode and emptiness checks both pass and the run scores ABSENT --
    # a model behaviour. That is how the no-fire set returned 110/110 ABSENT on
    # expired credentials. Anything here is an instrument event, not a verdict.
    low = raw.lower()
    for needle, label in (
        ("failed to authenticate", "auth"),
        ("oauth session expired", "auth"),
        ("invalid api key", "auth"),
        ("rate limit", "rate-limit"),
        ("usage limit", "quota"),
        ("overloaded", "overloaded"),
        ("insufficient credit", "quota"),
    ):
        if needle in low:
            return "ERROR", "", label

    if time.time() > deadline:
        return "ERROR", "", "timeout"
    return "ABSENT", "", None


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Measure G2: is the injected gate acted on?")
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--skill-path", required=True)
    ap.add_argument("--runs-per-query", type=int, default=5)
    ap.add_argument("--num-workers", type=int, default=2)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--model", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-probe", action="store_true",
                    help="skip the pre-batch live call (not recommended)")
    args = ap.parse_args()

    if args.runs_per_query < 1:
        sys.stderr.write("--runs-per-query must be >= 1\n")
        return 2

    problems = setup_check(args.skill_path)
    if problems:
        sys.stderr.write("SETUP CHECK FAILED - not running:\n")
        for p in problems:
            sys.stderr.write("  - %s\n" % p)
        return 2
    sys.stderr.write("setup check: OK\n")

    with open(args.eval_set, encoding="utf-8") as fh:
        queries = json.load(fh)

    project = make_project(args.skill_path)
    sys.stderr.write("project: %s\n" % project)

    if not args.skip_probe:
        # Retry: a single transient timeout should not discard a whole eval set.
        # The rule is "prove the instrument is alive", not "fail on one slow call" --
        # in batch 1 the no-fire set was refused on one timeout while borderline,
        # run minutes later against the same instrument, probed clean.
        # The probe query is a known 5/5 FIRE case (must-fire T6 terse), so the
        # bar is a VERDICT, not merely "not ERROR". Accepting ABSENT here is how
        # a dead instrument was cleared to spend 110 calls: the probe returned
        # ABSENT on expired credentials and the batch proceeded anyway.
        v = None
        for attempt in range(1, 4):
            v, _d, e = live_probe(project, args.timeout)
            sys.stderr.write("live probe %d/3: %s%s\n" % (attempt, v, (" (%s)" % e) if e else ""))
            if v in ("FIRE", "DECLINE"):
                break
            time.sleep(3)
        if v not in ("FIRE", "DECLINE"):
            sys.stderr.write("LIVE PROBE FAILED 3x (last=%s) - instrument is not returning "
                             "verdicts; not spending the batch.\n" % v)
            return 3

    jobs = [(q["query"], q.get("should_trigger"), r)
            for q in queries for r in range(args.runs_per_query)]

    raw_dir = os.path.join(os.path.dirname(args.out),
                           "raw_" + os.path.basename(args.out).replace(".json", ""))
    query_index = {q['query']: i for i, q in enumerate(queries)}
    started = time.time()
    done = [0]

    def work(j):
        query, expected, rep = j
        tag = "q%03d_rep%d" % (query_index[query], rep)
        res = run_once(query, project, args.timeout, args.model, raw_dir, tag)
        done[0] += 1
        # Progress to stderr as runs complete. The first batch was opaque from
        # outside for its whole duration, which made a stalled run and a slow
        # run indistinguishable.
        sys.stderr.write("[%d/%d] %s  %s\n" % (done[0], len(jobs), res[0], query[:48]))
        sys.stderr.flush()
        return (query, expected, rep) + res

    with ThreadPoolExecutor(max_workers=args.num_workers) as ex:
        raw = list(ex.map(work, jobs))

    err_runs = sum(1 for r in raw if r[3] == "ERROR")
    if err_runs > len(jobs) * 0.2:
        sys.stderr.write(
            "\nABORT-WORTHY: %d/%d runs were ERROR (>20%%). Results are not "
            "trustworthy; treat this batch as void.\n" % (err_runs, len(jobs)))

    per_query = {}
    for query, expected, _rep, verdict, detail, error in raw:
        d = per_query.setdefault(query, {
            "query": query, "should_trigger": expected,
            "FIRE": 0, "DECLINE": 0, "ABSENT": 0, "ERROR": 0, "errors": 0, "details": [],
        })
        d[verdict] += 1
        if error:
            d["errors"] += 1
        if detail:
            d["details"].append(detail)

    results = []
    for q in queries:
        d = per_query[q["query"]]
        runs = args.runs_per_query
        d["runs"] = runs
        d["fire_rate"] = d["FIRE"] / runs
        d["decline_rate"] = d["DECLINE"] / runs
        d["absent_rate"] = d["ABSENT"] / runs
        d["error_rate"] = d["ERROR"] / runs
        results.append(d)

    total = len(jobs)
    payload = {
        "eval_set": os.path.basename(args.eval_set),
        "runs_per_query": args.runs_per_query,
        "gate_tokens_est": len(open(os.path.join(HOOKS, "gate_prompt.txt"),
                                   encoding="utf-8").read()) // 4,
        "summary": {
            "queries": len(queries),
            "total_runs": total,
            "FIRE": sum(r["FIRE"] for r in results),
            "DECLINE": sum(r["DECLINE"] for r in results),
            "ABSENT": sum(r["ABSENT"] for r in results),
            "ERROR": sum(r["ERROR"] for r in results),
            "errors": sum(r["errors"] for r in results),
            "wall_seconds": round(time.time() - started, 1),
        },
        "results": results,
    }

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    s = payload["summary"]
    sys.stderr.write(
        "\n%s: FIRE %d  DECLINE %d  ABSENT %d  ERROR %d  (of %d runs)\n"
        % (payload["eval_set"], s["FIRE"], s["DECLINE"], s["ABSENT"], s["ERROR"], total)
    )
    for r in results:
        sys.stderr.write("  F%d/D%d/A%d/E%d  %s\n"
                         % (r["FIRE"], r["DECLINE"], r["ABSENT"], r["ERROR"], r["query"][:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
