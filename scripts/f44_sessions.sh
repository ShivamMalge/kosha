#!/usr/bin/env bash
# F4.4 - the gate must not fire once implementation has begun in a session.
#
# This is the ONLY criterion that single-turn probes structurally cannot test.
# `claude -p` is one turn with no history, so "implementation has already begun
# in this session" can never become true. Real session state is required, and
# `-c/--continue` provides it.
#
# Shape of each probe:
#   turn 1  an explicit request to hand-write the implementation  -> code begins
#   turn 2  a request that fires the gate 87-100% when asked fresh
#
# Turn 2 is the measurement. The gate must DECLINE, ideally citing the
# implementation-begun clause. A FIRE on turn 2 is an F4.4 failure: kosha would
# be proposing a library after the code exists, producing a rewrite rather than
# a decision.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/eval/results/F44"
mkdir -p "$OUT"

run_probe () {
  local id="$1" t1="$2" t2="$3"
  local proj; proj="$(mktemp -d -t kosha_f44_XXXXXX)"
  mkdir -p "$proj/.claude"
  cat > "$proj/.claude/settings.json" <<JSON
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python3 $ROOT/hooks/kosha_gate_hook.py" } ] }
    ]
  }
}
JSON

  echo "=== $id ==="
  ( cd "$proj" && timeout 240 claude -p "$t1" < /dev/null > "$OUT/${id}_turn1.txt" 2>&1 )
  ( cd "$proj" && timeout 240 claude -p "$t2" --continue < /dev/null > "$OUT/${id}_turn2.txt" 2>&1 )

  local v1 v2
  v1="$(grep -oE 'KOSHA: (FIRE|DECLINE)[^\n]{0,40}' "$OUT/${id}_turn1.txt" | head -1)"
  v2="$(grep -oE 'KOSHA: (FIRE|DECLINE)[^\n]{0,40}' "$OUT/${id}_turn2.txt" | head -1)"
  echo "  turn1: ${v1:-<no verdict>}"
  echo "  turn2: ${v2:-<no verdict>}   <-- F4.4 measurement"
  echo "$id|${v1:-NONE}|${v2:-NONE}" >> "$OUT/summary.psv"
}

: > "$OUT/summary.psv"

run_probe "P1_retry" \
  "Write the retry loop for the ingest client by hand: a while loop, time.sleep, doubling the delay, max 5 attempts. Just write the code." \
  "Now add jitter and a cap on total delay to that retry loop."

run_probe "P2_cliconfig" \
  "Start the CLI by hand: an argparse parser with --host and --port. Just write the code." \
  "Now layer environment variables and a TOML config file underneath those flags, with flags winning over env winning over file."

run_probe "P3_tabular" \
  "Write the column checks for the input table by hand: loop the rows, assert each column's type. Just write the code." \
  "Now add nullability and value-range checks and a readable report of everything that failed."

run_probe "P4_rustcsv" \
  "Write the CSV row parser in Rust by hand: split on commas, index the fields, build the struct. Just write the code." \
  "Now collect per-row errors into a report instead of failing the whole file on the first bad row."

echo
echo "=== F4.4 summary (turn2 is the criterion) ==="
column -t -s'|' "$OUT/summary.psv"
