#!/usr/bin/env bash
# P0–P2 CI gate: injection + trajectories + addendum + hot index.
# Exit nonzero on any failure. No network required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=src

echo "== Full assistant + items suite =="
python3 -m pytest -q tests/assistant/ tests/items/ --tb=line

echo "== P1 2k scale + CJK recall (50k measured offline) =="
python3 -m pytest -q tests/items/test_find_scale_and_recall.py --tb=line
test -f docs/superpowers/measurements/2026-10-02-find-latency-2k-50k.json

echo "== pass^3 critical (injection / trajectories / addendum / held) =="
for i in 1 2 3; do
  echo "-- seed $i --"
  python3 -m pytest -q \
    tests/assistant/test_injection_fixtures.py \
    tests/assistant/test_injection_files.py \
    tests/assistant/test_addendum_a.py \
    tests/assistant/test_trajectories.py \
    tests/assistant/test_chat_mocked_loop.py \
    tests/assistant/test_held_egress.py \
    tests/assistant/test_local_only_ask.py \
    --tb=line
done

echo "== fixture files present =="
test -f tests/fixtures/injection/INJ-01_ignore_instructions.pdf.txt
test -f tests/fixtures/injection/INJ-08_remote_fetch.txt
test -f tests/fixtures/injection/SYSTEM_apply_moves_now.pdf

echo "== requirement audit =="
python3 -m pytest -q tests/assistant/test_p0_p2_requirement_audit.py --tb=line

echo "== frozen memory precision gate eval =="
python3 tools/run_memory_gate_eval.py

echo "== people merge eval set =="
python3 tools/run_people_merge_eval.py

if [[ -f "${GA_PERFECT_DB:-/tmp/ga-500.sqlite}" ]]; then
  echo "== product perfection gate (real DB; non-UI / non-sorter) =="
  python3 tools/product_perfection_gate.py
  echo "== downloads-scale dogfood (find latency) =="
  python3 tools/run_downloads_scale_dogfood.py
else
  echo "== product perfection gate SKIPPED (no ${GA_PERFECT_DB:-/tmp/ga-500.sqlite}) =="
fi

echo "ALL ASSISTANT GATES GREEN"
