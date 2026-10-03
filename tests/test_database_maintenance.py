"""T9: backup / restore / check / rebuild-index."""
from __future__ import annotations

from pathlib import Path

from database_agent.db import open_database
from database_agent.maintenance import (
    backup_database,
    check_database,
    rebuild_index,
    restore_database,
)
from items.identity import reconcile_tree
from items.schema import create_items_schema


def test_check_backup_restore_rebuild(tmp_path: Path):
    db = tmp_path / "live.sqlite"
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "a.txt").write_text("hello", encoding="utf-8")
    conn = open_database(db, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, lib)
    conn.commit()
    conn.close()

    report = check_database(db)
    assert report.integrity == "ok"

    bak = tmp_path / "backups" / "live.bak.sqlite"
    manifest = backup_database(db, bak)
    assert bak.is_file()
    assert manifest["check"]["integrity"] == "ok"
    assert bak.with_suffix(bak.suffix + ".manifest.json").is_file()

    target = tmp_path / "restored.sqlite"
    result = restore_database(bak, target)
    assert result["ok"] is True
    assert target.is_file()

    reb = rebuild_index(target)
    assert reb["ok"] is True
    assert reb["fts_rows"] >= 1
