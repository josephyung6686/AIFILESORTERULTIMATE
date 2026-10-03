"""Backup, restore, integrity check, index rebuild (everyday ops T9)."""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from database_agent.db import SCHEMA_VERSION, open_database


@dataclass(frozen=True)
class CheckReport:
    ok: bool
    integrity: str
    schema_version: int | None
    dirty_items: int
    missing_items: int
    indexing_items: int
    nonterminal_journal: int
    notes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "integrity": self.integrity,
            "schema_version": self.schema_version,
            "dirty_items": self.dirty_items,
            "missing_items": self.missing_items,
            "indexing_items": self.indexing_items,
            "nonterminal_journal": self.nonterminal_journal,
            "notes": list(self.notes),
        }


def check_database(path: Path) -> CheckReport:
    conn = open_database(path, scan_roots=[])
    notes: list[str] = []
    try:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        schema_version = None
        try:
            row = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            ).fetchone()
            if row:
                schema_version = int(row[0])
        except sqlite3.OperationalError:
            try:
                row = conn.execute(
                    "SELECT version FROM items_meta LIMIT 1"
                ).fetchone()
                schema_version = int(row[0]) if row else None
            except Exception:
                schema_version = None
                notes.append("schema_version table missing")

        dirty = missing = indexing = 0
        try:
            cols = {
                r[1] for r in conn.execute("PRAGMA table_info(items)")
            }
            if "freshness_state" in cols:
                dirty = conn.execute(
                    "SELECT COUNT(*) FROM items WHERE freshness_state='dirty'"
                ).fetchone()[0]
                indexing = conn.execute(
                    "SELECT COUNT(*) FROM items WHERE freshness_state='indexing'"
                ).fetchone()[0]
            missing = conn.execute(
                "SELECT COUNT(*) FROM items WHERE presence='missing'"
            ).fetchone()[0]
        except sqlite3.OperationalError:
            notes.append("items table missing")

        journal_n = 0
        try:
            # `planned` is an in-flight operation, not a terminal outcome.  A
            # process can die after recording a plan and before applying it;
            # check must surface that state so recovery can reconcile it.
            journal_n = conn.execute(
                "SELECT COUNT(*) FROM assistant_journal "
                "WHERE state NOT IN ('applied','undone')"
            ).fetchone()[0]
        except sqlite3.OperationalError:
            pass

        ok = integrity == "ok" and journal_n == 0
        return CheckReport(
            ok=ok,
            integrity=str(integrity),
            schema_version=schema_version,
            dirty_items=int(dirty),
            missing_items=int(missing),
            indexing_items=int(indexing),
            nonterminal_journal=int(journal_n),
            notes=tuple(notes),
        )
    finally:
        conn.close()


def backup_database(src: Path, dest: Path) -> dict[str, Any]:
    """SQLite backup API → dest; write sidecar manifest."""
    dest = dest.expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError(f"backup target exists: {dest}")
    src_conn = open_database(src, scan_roots=[])
    try:
        dest_conn = sqlite3.connect(str(dest))
        try:
            src_conn.backup(dest_conn)
        finally:
            dest_conn.close()
    finally:
        src_conn.close()
    report = check_database(dest)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(src.resolve()),
        "schema_version_constant": SCHEMA_VERSION,
        "check": report.as_dict(),
    }
    dest.with_suffix(dest.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    return manifest


def restore_database(
        backup: Path, target: Path, *, replace: bool = False,
) -> dict[str, Any]:
    """Restore backup into target. Refuses overwrite unless replace=True."""
    backup = backup.expanduser().resolve()
    target = target.expanduser().resolve()
    if not backup.is_file():
        raise FileNotFoundError(backup)
    report = check_database(backup)
    if report.integrity != "ok":
        raise RuntimeError(f"backup failed integrity: {report.integrity}")
    if target.exists() and not replace:
        raise FileExistsError(
            f"target exists: {target} — pass replace=True / --replace"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".restore-tmp")
    if tmp.exists():
        tmp.unlink()
    shutil.copy2(backup, tmp)
    # Replace atomically.  Removing the previous target first creates a window
    # in which an interrupted restore destroys the only known-good database.
    # `os.replace` leaves the old target untouched if the replacement fails.
    try:
        os.replace(tmp, target)
    except BaseException:
        # A failed copy/rename is recoverable; do not leave a misleading
        # restore-tmp database that a later run could mistake for a backup.
        tmp.unlink(missing_ok=True)
        raise
    after = check_database(target)
    return {"ok": after.ok, "target": str(target), "check": after.as_dict()}


def rebuild_index(path: Path) -> dict[str, Any]:
    conn = open_database(path, scan_roots=[])
    try:
        from items.hot_index import rebuild_fts
        n = rebuild_fts(conn)
        conn.commit()
        return {"ok": True, "fts_rows": n, "moved": False}
    finally:
        conn.close()
