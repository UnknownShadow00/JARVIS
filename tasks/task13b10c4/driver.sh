#!/usr/bin/env bash
# Frozen scored order: A-F, G, H, I, J, then unseen K; five repetitions each.
set -uo pipefail
E=/home/jarvis/.hermes-poc/evidence/task13b10c4-action-routing
PY=/home/jarvis/.hermes-poc/hermes-agent/.venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
cd /home/jarvis/.hermes-poc/hermes-agent || exit 1
echo "driver_start_utc=$(date -u +%FT%T.%3NZ)"
idx=0
for suite in orig g h i j k; do
  for rep in 1 2 3 4 5; do
    idx=$((idx + 1))
    echo "block_start_utc=$(date -u +%FT%T.%3NZ) order=$idx suite=$suite rep=$rep attempt=1"
    "$PY" "$E/run.py" "$suite" "$rep" "$idx" 1 2>> "$E/run.stderr"
    rc=$?
    echo "block_end_utc=$(date -u +%FT%T.%3NZ) order=$idx suite=$suite rep=$rep attempt=1 rc=$rc"
    if [ "$rc" -ne 0 ]; then
      echo "DRIVER_STOPPED rc=$rc suite=$suite rep=$rep; full scored run aborted"
      exit "$rc"
    fi
  done
done
echo "driver_end_utc=$(date -u +%FT%T.%3NZ)"
echo DRIVER_COMPLETE
