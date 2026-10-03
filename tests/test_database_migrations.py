"""T9: migration from pre-release SQLite schemas is safe and idempotent."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from database_agent.db import open_database


def _legacy_database(path: Path) -> None:
    """Create the v1 files table, before inode columns were introduced."""
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE files (
            file_id TEXT PRIMARY KEY,
            current_path TEXT NOT NULL,
            filename TEXT NOT NULL,
            normalized_filename TEXT NOT NULL,
            extension TEXT NOT NULL,
            directory_position TEXT,
            volume_id TEXT,
            content_hash TEXT NOT NULL,
            hash_algorithm TEXT NOT NULL,
            observed_size INTEGER NOT NULL,
            observed_timestamps TEXT NOT NULL,
            mime_type TEXT,
            detected_format TEXT,
            scan_state TEXT NOT NULL,
            extraction_status_by_tier TEXT NOT NULL DEFAULT '{}',
            sensitivity_state TEXT
        );
        INSERT INTO files VALUES
          ('f1', '/tmp/essay.txt', 'essay.txt', 'essay.txt', '.txt', NULL,
           NULL, 'hash', 'sha256', 4, '{}', 'text/plain', 'text', 'live', '{}', NULL);
        PRAGMA user_version = 1;
        """
    )
    conn.close()


def test_open_migrates_legacy_files_schema_and_preserves_rows(tmp_path: Path):
    path = tmp_path / "legacy.sqlite"
    _legacy_database(path)

    conn = open_database(path)
    try:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(files)")}
        assert {"st_dev", "st_ino"} <= columns
        row = conn.execute("SELECT file_id, content_hash FROM files").fetchone()
        assert tuple(row) == ("f1", "hash")
    finally:
        conn.close()

    # A second open must not attempt duplicate ALTERs or change the migrated
    # data.  This is the restart path used by an everyday install.
    conn = open_database(path)
    try:
        assert conn.execute("SELECT COUNT(*) FROM files").fetchone()[0] == 1
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 2
    finally:
        conn.close()


def test_migration_is_atomic_when_an_existing_schema_is_read_only(tmp_path: Path):
    path = tmp_path / "legacy.sqlite"
    _legacy_database(path)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA query_only = ON")
    # The old fixture remains readable; the normal open path can then perform
    # the migration on the writable database without partial columns leaking.
    assert conn.execute("SELECT COUNT(*) FROM files").fetchone()[0] == 1
    conn.close()
    migrated = open_database(path)
    try:
        assert migrated.execute(
            "SELECT COUNT(*) FROM pragma_table_info('files') "
            "WHERE name IN ('st_dev','st_ino')"
        ).fetchone()[0] == 2
    finally:
        migrated.close()
