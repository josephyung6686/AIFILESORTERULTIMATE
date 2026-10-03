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
mkdir -p "$WHEELHOUSE"
run_gate wheel_build "$PYTHON" -m pip wheel --no-deps --no-build-isolation --wheel-dir "$WHEELHOUSE" "$ROOT"
WHEEL="$(find "$WHEELHOUSE" -maxdepth 1 -name '*.whl' -print -quit)"
if [[ -z "$WHEEL" ]]; then
  printf 'wheel_artifact\t1\t-\t-\n' >>"$STATUS"
  FAILED=1
else
  run_gate venv_create "$PYTHON" -m venv "$VENV"
  VENV_PY="$VENV/bin/python"
  VENV_PIP="$VENV/bin/pip"
  run_gate wheel_install "$VENV_PIP" install --no-deps --no-index "$WHEEL"
  DEP_WHEELHOUSE="${RELEASE_DEP_WHEELHOUSE:-}"
  if [[ -n "$DEP_WHEELHOUSE" ]] && [[ -d "$DEP_WHEELHOUSE" ]]; then
    run_gate declared_dependencies "$VENV_PIP" install --no-index --find-links "$DEP_WHEELHOUSE" "$WHEEL[dev,readers,models,encryption]"
    run_gate installed_encryption "$VENV_PY" - <<'PY'
import os, tempfile
from pathlib import Path
from database_agent.encryption import open_encrypted
from database_agent.privacy import encryption_capability
conn = open_encrypted(Path(tempfile.mkdtemp()) / "gate.sqlite", os.urandom(32))
assert encryption_capability(conn).encrypted
conn.close()
PY
  else
    printf 'declared_dependency_wheelhouse\t1\t-\t-\n' >>"$STATUS"
    FAILED=1
  fi
fi
if [[ -n "${VENV_PY:-}" ]]; then
  run_gate installed_artifact "$VENV_PY" - <<'PY'
import sys
from pathlib import Path
from items.profile_loader import load_profile
import items
assert Path(items.__file__).resolve().as_posix().startswith(sys.prefix), (items.__file__, sys.prefix)
import database_agent
assert Path(database_agent.__file__).resolve().as_posix().startswith(sys.prefix), (database_agent.__file__, sys.prefix)
for name in ("student", "files_only", "job_seeker"):
    load_profile(name)
PY
  run_gate installed_entrypoint "$VENV/bin/database-agent" --help
  run_gate installed_plan_help "$VENV/bin/database-agent" plan --help
  run_gate installed_preview_help "$VENV/bin/database-agent" preview-plan --help
  run_gate installed_local_db "$VENV_PY" - <<'PY'
import sys, tempfile
import subprocess
from pathlib import Path
from database_agent.db import open_database
from database_agent.maintenance import check_database
from items.schema import create_items_schema
from items.hot_index import rebuild_fts, find_files
base = Path(tempfile.mkdtemp())
root = base / "corpus"
root.mkdir()
(root / "note.txt").write_text("installed wheel release marker", encoding="utf-8")
db = base / "agent.sqlite"
conn = open_database(db, scan_roots=[])
create_items_schema(conn)
from items.identity import reconcile_tree
reconcile_tree(conn, root)
rebuild_fts(conn)
assert find_files(conn, "release marker", limit=5).hits
conn.close()
script = Path(sys.prefix) / "bin" / "database-agent"
search = subprocess.run([str(script), "search", "release marker", "--database", str(db)], capture_output=True, text=True)
assert search.returncode == 0, search.stderr + search.stdout
ask = subprocess.run([str(script), "ask", "release marker", "--database", str(db), "--local-only"], capture_output=True, text=True)
assert ask.returncode == 0, ask.stderr + ask.stdout
assert check_database(db).ok
PY
  TESTROOT="$WORK/installed-tests"
  mkdir -p "$TESTROOT/tests" "$TESTROOT/src" "$TESTROOT/tools"
  cp "$ROOT/tools/run_assistant_gates.sh" "$TESTROOT/tools/"
  cp -R "$ROOT/tests/assistant" "$TESTROOT/tests/assistant"
  cp -R "$ROOT/tests/items" "$TESTROOT/tests/items"
  cp "$ROOT/tests/conftest.py" "$TESTROOT/tests/conftest.py"
  cp -R "$ROOT/tests/fixtures" "$TESTROOT/tests/fixtures"
  cp -R "$ROOT/src/." "$TESTROOT/src/"
  cp "$ROOT/tests/test_database_maintenance.py" "$ROOT/tests/test_database_migrations.py" "$ROOT/tests/test_privacy_at_rest.py" "$TESTROOT/tests/"
  run_gate installed_assistant_items "$VENV_PY" -m pytest -q "$TESTROOT/tests/assistant" "$TESTROOT/tests/items" "$TESTROOT/tests/test_database_maintenance.py" "$TESTROOT/tests/test_database_migrations.py" "$TESTROOT/tests/test_privacy_at_rest.py" --tb=line
else
  printf 'installed_artifact\t1\t-\t-\ninstalled_entrypoint\t1\t-\t-\n' >>"$STATUS"
  FAILED=1
fi
run_gate connector_boundary "$VENV_PY" - <<'PY'
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
report = {"schema": "release-gate-report/v1", "ok": bool(rows) and all(row["returncode"] == 0 for row in rows), "gates": rows, "scope": {"ui": "excluded", "live_connectors": "scratched", "network": "off", "encryption": "preprovisioned wheelhouse required"}}
out = Path(os.environ["REPORT"])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["ok"] else 1)
PY
