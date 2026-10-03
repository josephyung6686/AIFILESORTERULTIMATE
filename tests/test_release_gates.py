"""T12: release harness artifacts exist; connectors stay scratched."""
from __future__ import annotations

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
