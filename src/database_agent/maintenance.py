"""Backup, restore, integrity check, index rebuild (everyday ops T9)."""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from database_agent.db import SCHEMA_VERSION, open_database
from database_agent.encryption import open_encrypted, open_encrypted_existing


def _open_existing(path: Path, *, key: bytes | None = None):
    """Open an existing DB without creating it or running migrations."""
    if not path.is_file():
        raise FileNotFoundError(path)
    if key is not None:
        return open_encrypted_existing(path, key)
    # `mode=ro` is a hard boundary: checking a path must never create it or
    # mutate its schema.  SQLCipher accepts the same SQLite URI form.
    conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    # sqlite3.Row is tied to the stdlib connection type; SQLCipher's DB-API
    # cursor rejects it.  Maintenance queries use positional fields, so leave
    # the cipher connection's default tuple rows in place.
    conn.row_factory = sqlite3.Row
    # Force the key to be checked before callers inspect sqlite_master.
    conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
    return conn


def _publish_new(tmp: Path, dest: Path) -> None:
    """Publish a new backup without ever overwriting a racing destination."""
    os.link(tmp, dest)  # atomic O_EXCL-like publication on one filesystem
    tmp.unlink()
    _durable_path(dest)


def _durable_path(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())
    dir_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def _staging_path(parent: Path, label: str) -> Path:
    fd, name = tempfile.mkstemp(prefix=f".{label}.", suffix=".tmp", dir=parent)
    os.close(fd)
    return Path(name)


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


def check_database(path: Path, *, encryption_key: bytes | None = None) -> CheckReport:
    conn = _open_existing(path, key=encryption_key)
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
        except Exception:
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
        except Exception:
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
        except Exception:
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


def backup_database(src: Path, dest: Path, *, encryption_key: bytes | None = None) -> dict[str, Any]:
    """Snapshot src with SQLite backup API, optionally into SQLCipher."""
    dest = dest.expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError(f"backup target exists: {dest}")
    src_conn = _open_existing(src, key=encryption_key)
    tmp = _staging_path(dest.parent, dest.name + ".backup")
    try:
        dest_conn = open_encrypted(tmp, encryption_key) if encryption_key else sqlite3.connect(str(tmp))
        try:
            src_conn.backup(dest_conn)
            dest_conn.commit()
        finally:
            dest_conn.close()
        _publish_new(tmp, dest)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    finally:
        src_conn.close()
    report = check_database(dest, encryption_key=encryption_key)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(src.resolve()),
        "schema_version_constant": SCHEMA_VERSION,
        "encrypted": encryption_key is not None,
        "check": report.as_dict(),
    }
    dest.with_suffix(dest.suffix + ".manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    return manifest


def restore_database(
        backup: Path, target: Path, *, replace: bool = False,
        encryption_key: bytes | None = None,
) -> dict[str, Any]:
    """Restore backup into target. Refuses overwrite unless replace=True."""
    backup = backup.expanduser().resolve()
    target = target.expanduser().resolve()
    if not backup.is_file():
        raise FileNotFoundError(backup)
    report = check_database(backup, encryption_key=encryption_key)
    if report.integrity != "ok":
        raise RuntimeError(f"backup failed integrity: {report.integrity}")
    if target.exists() and not replace:
        raise FileExistsError(
            f"target exists: {target} — pass replace=True / --replace"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    if replace and (
        target.with_name(target.name + "-wal").exists()
        or target.with_name(target.name + "-shm").exists()
    ):
        raise RuntimeError("refusing restore over a target with a live SQLite WAL/SHM sidecar")
    tmp = _staging_path(target.parent, target.name + ".restore")
    source_conn = _open_existing(backup, key=encryption_key)
    # Replace atomically.  Removing the previous target first creates a window
    # in which an interrupted restore destroys the only known-good database.
    # `os.replace` leaves the old target untouched if the replacement fails.
    try:
        dest_conn = open_encrypted(tmp, encryption_key) if encryption_key else sqlite3.connect(str(tmp))
        try:
            source_conn.backup(dest_conn)
            dest_conn.commit()
        finally:
            dest_conn.close()
        source_conn.close()
        if replace:
            os.replace(tmp, target)
            _durable_path(target)
            dir_fd = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        else:
            _publish_new(tmp, target)
    except BaseException:
        # A failed copy/rename is recoverable; do not leave a misleading
        # restore-tmp database that a later run could mistake for a backup.
        tmp.unlink(missing_ok=True)
        source_conn.close()
        raise
    after = check_database(target, encryption_key=encryption_key)
    return {"ok": after.ok, "target": str(target), "check": after.as_dict()}


def rebuild_index(path: Path, *, encryption_key: bytes | None = None) -> dict[str, Any]:
    conn = (open_encrypted(path, encryption_key)
            if encryption_key is not None else open_database(path, scan_roots=[]))
    try:
        from items.hot_index import rebuild_fts
        n = rebuild_fts(conn)
        conn.commit()
        return {"ok": True, "fts_rows": n, "moved": False}
    finally:
        conn.close()
