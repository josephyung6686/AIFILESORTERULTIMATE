#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="${RELEASE_GATE_REPORT:-$ROOT/docs/operations/release-gate-report.json}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/database-agent-release.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
STATUS="$WORK/status.tsv"
: >"$STATUS"
FAILED=0
run_gate() {
  local name="$1"; shift
  local started ended rc
  started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  set +e; "$@"; rc=$?; set -e
  ended="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '%s\t%s\t%s\t%s\n' "$name" "$rc" "$started" "$ended" >>"$STATUS"
  if [[ "$rc" -ne 0 ]]; then FAILED=1; fi
  return 0
}
PYTHON="${PYTHON:-python3}"
VENV="$WORK/venv"
WHEELHOUSE="$WORK/wheelhouse"
"$PYTHON" -m venv "$VENV"
VENV_PY="$VENV/bin/python"
VENV_PIP="$VENV/bin/pip"
mkdir -p "$WHEELHOUSE"
run_gate wheel_build "$VENV_PY" -m pip wheel --no-deps --no-build-isolation --wheel-dir "$WHEELHOUSE" "$ROOT"
WHEEL="$(find "$WHEELHOUSE" -maxdepth 1 -name '*.whl' -print -quit)"
if [[ -n "$WHEEL" ]]; then
  run_gate wheel_install "$VENV_PIP" install --no-deps --no-index "$WHEEL"
else
  printf 'wheel_artifact\t1\t-\t-\n' >>"$STATUS"
  FAILED=1
fi
run_gate installed_artifact "$VENV_PY" - <<'PY'
from items.profile_loader import load_profile
for name in ("student", "files_only", "job_seeker"):
    load_profile(name)
PY
run_gate installed_entrypoint "$VENV/bin/database-agent" --help
export PYTHONPATH="$ROOT/src"
run_gate provider_resolution "$PYTHON" -m pytest -q tests/assistant/test_provider_resolution.py --tb=line
run_gate relationship_safety "$PYTHON" -m pytest -q tests/items/test_relationship_approval.py tests/items/test_relationship_projections.py tests/items/test_people_merge_migration.py --tb=line
run_gate policy_safety "$PYTHON" -m pytest -q tests/assistant/test_policy_boundary.py tests/assistant/test_deferred_tools_security.py tests/assistant/test_injection_fixtures.py tests/assistant/test_held_egress.py --tb=line
run_gate recovery_safety "$PYTHON" -m pytest -q tests/assistant/test_crash_recovery.py tests/assistant/test_no_clobber_and_hash.py tests/assistant/test_undo.py --tb=line
run_gate database_safety "$PYTHON" -m pytest -q tests/test_database_maintenance.py tests/test_database_migrations.py --tb=line
run_gate privacy_safety "$PYTHON" -m pytest -q tests/test_privacy_at_rest.py --tb=line
run_gate connector_boundary "$PYTHON" - <<'PY'
from items.connectors import CONNECTORS_DISABLED_REASON
assert "scratched" in CONNECTORS_DISABLED_REASON.lower(), CONNECTORS_DISABLED_REASON
print(CONNECTORS_DISABLED_REASON)
PY
REPORT="$REPORT" STATUS="$STATUS" python3 - <<'PY'
import json, os
from pathlib import Path
rows = []
for line in Path(os.environ["STATUS"]).read_text().splitlines():
    name, rc, started, ended = line.split("\t")
    rows.append({"name": name, "returncode": int(rc), "started": started, "ended": ended, "status": "passed" if rc == "0" else "failed"})
report = {"schema": "release-gate-report/v1", "ok": bool(rows) and all(row["returncode"] == 0 for row in rows), "gates": rows, "scope": {"ui": "excluded", "live_connectors": "scratched", "network": "off"}}
out = Path(os.environ["REPORT"])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["ok"] else 1)
PY
