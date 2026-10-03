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


def _cipher():
    try:
        from pysqlcipher3 import dbapi2
        return dbapi2
    except ImportError:
        try:
            import sqlcipher3
            return sqlcipher3
        except ImportError:
            return None


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


def test_check_missing_path_does_not_create_database(tmp_path: Path):
    missing = tmp_path / "does-not-exist.sqlite"
    with pytest.raises(FileNotFoundError):
        check_database(missing)
    assert not missing.exists()


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


def test_restore_replace_refuses_live_wal_sidecar(tmp_path: Path):
    source = tmp_path / "source.sqlite"
    conn = open_database(source)
    conn.close()
    backup = tmp_path / "backup.sqlite"
    backup_database(source, backup)
    target = tmp_path / "target.sqlite"
    target.write_bytes(b"known target")
    target.with_name(target.name + "-wal").write_bytes(b"live")
    with pytest.raises(RuntimeError, match="WAL/SHM"):
        restore_database(backup, target, replace=True)
    assert target.read_bytes() == b"known target"


@pytest.mark.skipif(_cipher() is None, reason="SQLCipher is optional")
def test_encrypted_backup_round_trip_covers_wal_without_plaintext(tmp_path: Path):
    cipher = _cipher()
    key = b"c" * 32
    source = tmp_path / "encrypted.sqlite"
    conn = cipher.connect(str(source))
    conn.execute("PRAGMA key = \"x'%s'\"" % key.hex())
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("CREATE TABLE marker (value TEXT NOT NULL)")
    conn.execute("INSERT INTO marker VALUES ('secret-marker')")
    conn.commit()
    # Keep the WAL live so backup must use SQLite's snapshot API rather than a
    # pair of ordinary file copies.
    assert source.with_name(source.name + "-wal").exists()

    backup = tmp_path / "encrypted-backup.sqlite"
    try:
        assert b"secret-marker" not in source.with_name(source.name + "-wal").read_bytes()
        manifest = backup_database(source, backup, encryption_key=key)
    finally:
        conn.close()
    assert manifest["encrypted"] is True
    assert b"secret-marker" not in backup.read_bytes()

    restored = tmp_path / "restored.sqlite"
    result = restore_database(backup, restored, encryption_key=key)
    assert result["ok"] is True
    check = cipher.connect(str(restored))
    check.execute("PRAGMA key = \"x'%s'\"" % key.hex())
    assert check.execute("SELECT value FROM marker").fetchone()[0] == "secret-marker"
    check.close()

    with pytest.raises(Exception):
        restore_database(backup, tmp_path / "wrong.sqlite", encryption_key=b"w" * 32)
    assert not (tmp_path / "wrong.sqlite").exists()


def test_encrypted_maintenance_cli_uses_configured_key(tmp_path, monkeypatch):
    from database_agent.encryption import key_from_file
    from items.commands_db import db_main
    import io

    key_file = tmp_path / "private.key"
    key = key_from_file(key_file)
    source = tmp_path / "source.sqlite"
    conn = open_database(source, encryption=True, encryption_key=key)
    conn.close()
    monkeypatch.setenv("DATABASE_AGENT_KEY_FILE", str(key_file))
    output = io.StringIO()
    backup = tmp_path / "backup.sqlite"
    restored = tmp_path / "restored.sqlite"
    assert db_main(["check", "--database", str(source)], out=output) == 0
    assert db_main(["backup", str(backup), "--database", str(source)], out=output) == 0
    assert db_main(["restore", str(backup), "--database", str(restored)], out=output) == 0
    assert db_main(["check", "--database", str(restored)], out=output) == 0
    assert b"SQLite format 3" not in restored.read_bytes()
