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


def test_db_maintenance_importable():
    from database_agent.maintenance import check_database, backup_database
    assert callable(check_database) and callable(backup_database)


def test_release_gate_is_clean_wheel_and_does_not_skip_safety():
    script = (ROOT / "tools/run_release_gates.sh").read_text()
    assert "--system-site-packages" not in script
    assert "export PYTHONPATH" not in script
    assert "installed_local_db" in script
    assert "tests/test_database_migrations.py" in script
    assert "tests/test_privacy_at_rest.py" in script
    assert "|| true" not in script
    assert "release-gate-report/v1" in script


def test_clean_wheel_installs_profiles_and_entrypoint(tmp_path):
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    built = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation",
         "--wheel-dir", str(wheelhouse), str(ROOT)], cwd=ROOT, text=True,
        capture_output=True,
    )
    assert built.returncode == 0, built.stdout + built.stderr
    venv = tmp_path / "venv"
    created = subprocess.run([sys.executable, "-m", "venv", str(venv)],
                             text=True, capture_output=True)
    assert created.returncode == 0, created.stderr
    wheel = next(wheelhouse.glob("*.whl"))
    installed = subprocess.run(
        [str(venv / "bin/pip"), "install", "--no-deps", "--no-index", str(wheel)],
        text=True, capture_output=True,
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr
    probe = subprocess.run(
        [str(venv / "bin/python"), "-c",
         "from items.profile_loader import load_profile; "
         "[load_profile(n) for n in ('student','files_only','job_seeker')]"],
        text=True, capture_output=True,
    )
    assert probe.returncode == 0, probe.stdout + probe.stderr
    help_run = subprocess.run(
        [str(venv / "bin/python"), "-m", "database_agent.entrypoint", "--help"],
        text=True, capture_output=True,
    )
    assert help_run.returncode == 0
    assert "usage: database-agent" in help_run.stdout


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
    assert original.read_text(encoding="utf-8") == "pilot source"
