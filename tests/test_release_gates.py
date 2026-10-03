"""T12: release harness is strict and the pilot is disposable."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_artifacts_present():
    assert (ROOT / "tools/run_release_gates.sh").is_file()
    assert (ROOT / "tools/run_daily_use_pilot.py").is_file()
    assert (ROOT / "docs/operations/everyday-product-runbook.md").is_file()
    assert (ROOT / "docs/operations/release-checklist.md").is_file()
    assert (ROOT / "docs/superpowers/plans/2026-10-03-everyday-product-readiness.md").is_file()


def test_connectors_scratched():
    from items.connectors import CONNECTORS_DISABLED_REASON
    assert "scratched" in CONNECTORS_DISABLED_REASON.lower()


def test_db_maintenance_importable():
    from database_agent.maintenance import check_database, backup_database
    assert callable(check_database) and callable(backup_database)


def test_release_gate_is_clean_wheel_and_does_not_skip_safety():
    text = (ROOT / "tools/run_release_gates.sh").read_text()
    assert "python3 -m venv" in text or '"$PYTHON" -m venv' in text
    assert "--no-index" in text
    assert "--no-build-isolation" in text
    assert "tests/test_database_migrations.py" in text
    assert "tests/test_privacy_at_rest.py" in text
    assert "|| true" not in text
    assert "release-gate-report/v1" in text


def test_pilot_copies_corpus_and_safe_defaults(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    original = source / "keep.txt"
    original.write_text("pilot source", encoding="utf-8")
    report = tmp_path / "pilot.json"
    db = tmp_path / "pilot.sqlite"
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/run_daily_use_pilot.py"),
         "--database", str(db), "--corpus", str(source), "--out", str(report),
         "--cloud", "off", "--memory-steering", "off", "--apply", "off"],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(report.read_text())
    assert payload["ok"] is True
    assert payload["corpus"]["copied"] is True
    assert payload["cloud"] == payload["memory_steering"] == payload["apply"] == "off"
    assert payload["ui"] == "excluded"
    assert payload["connectors"] == "scratched"
    assert original.read_text(encoding="utf-8") == "pilot source"
