"""T9: database maintenance refuses unsafe interruption outcomes."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from database_agent.db import open_database
from database_agent.maintenance import (
    backup_database,
    check_database,
    restore_database,
)


def test_check_reports_planned_journal_as_nonterminal(tmp_path: Path):
    path = tmp_path / "agent.sqlite"
    conn = open_database(path)
    conn.execute(
        "CREATE TABLE assistant_journal (entry_id TEXT PRIMARY KEY, state TEXT NOT NULL)"
    )
    conn.execute("INSERT INTO assistant_journal VALUES ('e1', 'planned')")
    conn.execute("INSERT INTO assistant_journal VALUES ('e2', 'applied')")
    conn.close()

    report = check_database(path)
    assert report.nonterminal_journal == 1
    assert report.ok is False


def test_restore_rejects_corrupt_backup(tmp_path: Path):
    source = tmp_path / "source.sqlite"
    conn = open_database(source)
    conn.close()
    backup = tmp_path / "backup.sqlite"
    backup_database(source, backup)
    data = bytearray(backup.read_bytes())
    data[100:108] = b"CORRUPT!"
    backup.write_bytes(data)

    target = tmp_path / "restored.sqlite"
    with pytest.raises((sqlite3.DatabaseError, RuntimeError)):
        restore_database(backup, target)
    assert not target.exists()


def test_restore_keeps_original_target_when_replace_is_interrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    source = tmp_path / "source.sqlite"
    conn = open_database(source)
    conn.execute("CREATE TABLE marker (value TEXT NOT NULL)")
    conn.execute("INSERT INTO marker VALUES ('backup')")
    conn.close()
    backup = tmp_path / "backup.sqlite"
    backup_database(source, backup)

    target = tmp_path / "target.sqlite"
    conn = open_database(target)
    conn.execute("CREATE TABLE marker (value TEXT NOT NULL)")
    conn.execute("INSERT INTO marker VALUES ('original')")
    conn.close()

    import database_agent.maintenance as maintenance

    def interrupted_replace(_src: str | bytes, _dst: str | bytes) -> None:
        raise OSError("simulated power loss before atomic replace")

    monkeypatch.setattr(maintenance.os, "replace", interrupted_replace)
    with pytest.raises(OSError, match="power loss"):
        restore_database(backup, target, replace=True)

    reopened = sqlite3.connect(target)
    try:
        assert reopened.execute("SELECT value FROM marker").fetchone()[0] == "original"
    finally:
        reopened.close()
    assert not target.with_suffix(target.suffix + ".restore-tmp").exists()
