"""Local privacy boundaries for the everyday CLI product.

This module is deliberately conservative: plain SQLite is reported as plain
SQLite, held records require an explicit local-authentication seam, and export
and deletion are audited.  It never stores credentials or message bodies.
"""
from __future__ import annotations

import json
import os
import tempfile
import shutil
from contextlib import contextmanager
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
import uuid


class LocalAuthRequired(PermissionError):
    """Held/protected material cannot be opened without local authentication."""


@dataclass(frozen=True)
class EncryptionCapability:
    encrypted: bool
    mechanism: str
    warning: str


def encryption_capability(conn: sqlite3.Connection) -> EncryptionCapability:
    """Describe encryption support without making claims about plain SQLite."""
    try:
        row = conn.execute("PRAGMA cipher_version").fetchone()
        version = row[0] if row else None
    except sqlite3.DatabaseError:
        version = None
    if version and getattr(conn, "_graph_agent_encrypted", False):
        return EncryptionCapability(True, f"sqlcipher-{version}", "")
    if version:
        return EncryptionCapability(
            False, "unverified-sqlcipher",
            "SQLCipher is loaded, but keyed encryption has not been verified "
            "for this connection.",
        )
    return EncryptionCapability(
        False,
        "plain-sqlite",
        "SQLite is not encrypted at rest; use an encrypted volume or SQLCipher.",
    )


def create_privacy_schema(conn: sqlite3.Connection) -> None:
    """Create the append-only audit stream used by privacy operations."""
    conn.execute(
        """CREATE TABLE IF NOT EXISTS privacy_audit_events (
            event_id TEXT PRIMARY KEY,
            action TEXT NOT NULL,
            subject TEXT NOT NULL,
            user_id TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )


def _audit(conn: sqlite3.Connection, action: str, subject: str,
           user_id: str, details: dict[str, Any]) -> None:
    create_privacy_schema(conn)
    conn.execute(
        "INSERT INTO privacy_audit_events VALUES (?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), action, subject, user_id,
         json.dumps(details, sort_keys=True), datetime.now(timezone.utc).isoformat()),
    )


def _authenticate(authenticate: Callable[[], bool] | None) -> None:
    if authenticate is None:
        raise LocalAuthRequired(
            "local authentication is required to access held/protected material"
        )
    try:
        allowed = bool(authenticate())
    except Exception as exc:  # an unavailable auth provider is a refusal
        raise LocalAuthRequired("local authentication is unavailable") from exc
    if not allowed:
        raise LocalAuthRequired("local authentication was not approved")


def held_item_fields(conn: sqlite3.Connection, item_id: str, *,
                     authenticate: Callable[[], bool] | None = None) -> dict[str, Any]:
    """Return item metadata, requiring local auth for held items."""
    cursor = conn.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()
    if row is None:
        return {}
    fields = {column[0]: row[index] for index, column in enumerate(cursor.description)}
    from items.mailbox import path_is_protected
    if (fields.get("typing_state") == "held"
            or path_is_protected(fields.get("open_target") or "")):
        _authenticate(authenticate)
    return fields


# Explicit metadata allowlist: unknown tables, nested payloads, evidence, audit
# history, embeddings, and FTS shadow storage cannot enter a sanitized export.
_EXPORT_COLUMNS = {
    "items": ("item_id", "item_type", "display_label", "file_id", "open_target",
              "presence", "typing_state", "type_schema", "profile_id", "created_at",
              "content_hash", "freshness_state"),
    "item_versions": ("item_id", "file_id", "content_hash", "became_live_at"),
    "item_headers": ("item_id", "kind", "happened_at", "ended_at", "status"),
    "relationships": ("relationship_id", "rel_type", "from_item_id", "to_item_id",
                      "confidence", "source", "state", "created_at"),
    "files": ("file_id", "current_path", "filename", "extension", "content_hash",
              "observed_size", "mime_type", "scan_state"),
}


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    # All callers supply internal table names, never user-provided SQL.
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}


@contextmanager
def _privacy_transaction(conn: sqlite3.Connection):
    nested = conn.in_transaction
    name = "privacy_" + uuid.uuid4().hex
    conn.execute(f"SAVEPOINT {name}" if nested else "BEGIN IMMEDIATE")
    try:
        yield
        conn.execute(f"RELEASE SAVEPOINT {name}" if nested else "COMMIT")
    except BaseException:
        if nested:
            conn.execute(f"ROLLBACK TO SAVEPOINT {name}")
            conn.execute(f"RELEASE SAVEPOINT {name}")
        else:
            conn.rollback()
        raise


def _export_metadata(conn: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    if not _has_table(conn, "items"):
        return tables
    from items.mailbox import path_is_protected
    item_rows = conn.execute(
        "SELECT item_id, typing_state, open_target FROM items").fetchall()
    held = {r[0] for r in item_rows if r[1] == "held" or path_is_protected(r[2] or "")}
    allowed = {r[0] for r in item_rows if r[0] not in held}
    allowed_files: set[str] = set()
    held_files: set[str] = set()
    for table in ("items", "item_versions"):
        if {"item_id", "file_id"} <= _columns(conn, table):
            for item_id, file_id in conn.execute(f'SELECT item_id, file_id FROM "{table}"'):
                if file_id:
                    if item_id in allowed:
                        allowed_files.add(file_id)
                    if item_id in held:
                        held_files.add(file_id)
    allowed_files -= held_files
    for table, permitted in _EXPORT_COLUMNS.items():
        columns = _columns(conn, table)
        keep = [c for c in permitted if c in columns]
        if not keep:
            continue
        quoted = ", ".join(f'"{c}"' for c in keep)
        rows = []
        for values in conn.execute(f'SELECT {quoted} FROM "{table}"'):
            row = dict(zip(keep, values))
            if table == "relationships":
                eligible = (row["from_item_id"] in allowed
                            and row["to_item_id"] in allowed)
            elif table == "files":
                eligible = row["file_id"] in allowed_files
            else:
                eligible = row["item_id"] in allowed
                # A shared held file must not leak through a second item/version.
                if row.get("file_id") in held_files:
                    eligible = False
            if eligible:
                rows.append(row)
        tables[table] = rows
    return tables


def export_database(conn: sqlite3.Connection, destination: Path, *,
                    user_id: str = "local") -> dict[str, Any]:
    """Export non-held metadata only; this is not a database backup.

    Audit and reads share a transaction. Nested callers retain ownership of
    their transaction; filesystem publication cannot be undone by their later
    rollback. The output is atomically replaced with an owner-only file.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    backup = None
    published = False
    try:
        with _privacy_transaction(conn):
            tables = _export_metadata(conn)
            payload = {
                "format": "graph-agent-sanitized-export-v1",
                "encrypted_at_rest": encryption_capability(conn).encrypted,
                "scope": "non-held metadata only; excludes content and audit history",
                "tables": tables,
            }
            fd, temporary = tempfile.mkstemp(prefix=".privacy-export-", dir=destination.parent)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            _audit(conn, "export", "metadata", user_id, {"table_count": len(tables)})
            if destination.exists():
                backup_fd, backup = tempfile.mkstemp(
                    prefix=".privacy-export-previous-", dir=destination.parent)
                os.close(backup_fd)
                shutil.copyfile(destination, backup)
            os.replace(temporary, destination)
            temporary = None
            published = True
    except BaseException:
        # A failed COMMIT must not leave an unaudited output or destroy the
        # previous export. Cross-filesystem/DB crash atomicity is not promised.
        if published:
            if backup is not None:
                os.replace(backup, destination)
                backup = None
            else:
                destination.unlink(missing_ok=True)
        raise
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)
        if backup is not None:
            Path(backup).unlink(missing_ok=True)
    return {"destination": str(destination), "tables": len(tables), "audited": True}


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name = ?", (name,)
    ).fetchone() is not None


def delete_item(conn: sqlite3.Connection, item_id: str, *, user_id: str = "local",
                authenticate: Callable[[], bool] | None = None) -> dict[str, Any]:
    """Remove active item projections, preserving immutable history and sources.

    This is not physical erasure: file inventory, original files, immutable
    evidence, identity events and relationship decisions remain. A later scan
    can rediscover an original file still on disk.
    """
    with _privacy_transaction(conn):
        columns = _columns(conn, "items")
        selected = "typing_state, file_id" if "file_id" in columns else "typing_state, NULL"
        row = conn.execute(f"SELECT {selected} FROM items WHERE item_id = ?", (item_id,)).fetchone()
        if row is None:
            return {"deleted": False, "item_id": item_id, "audited": False}
        state, file_id = row
        if state == "held":
            _authenticate(authenticate)
        file_ids = {file_id} if file_id else set()
        if _has_table(conn, "item_versions"):
            file_ids.update(r[0] for r in conn.execute(
                "SELECT file_id FROM item_versions WHERE item_id = ?", (item_id,)))
        # Shared file versions remain usable by other items.
        for candidate in tuple(file_ids):
            shared = conn.execute(
                "SELECT 1 FROM items WHERE file_id = ? AND item_id != ?",
                (candidate, item_id)).fetchone()
            if not shared and _has_table(conn, "item_versions"):
                shared = conn.execute(
                    "SELECT 1 FROM item_versions WHERE file_id = ? AND item_id != ?",
                    (candidate, item_id)).fetchone()
            if shared:
                file_ids.remove(candidate)
        if _has_table(conn, "vector_embeddings"):
            for candidate in file_ids:
                conn.execute("DELETE FROM vector_embeddings WHERE file_id = ?", (candidate,))
        if _has_table(conn, "vector_arrays"):
            for subject in file_ids | {item_id}:
                conn.execute("DELETE FROM vector_arrays WHERE subject_key = ?", (subject,))
        # Immutable audit/evidence tables are deliberately absent.
        for table, column in (
            ("relationships", "from_item_id"), ("relationships", "to_item_id"),
            ("item_headers", "item_id"), ("item_versions", "item_id"),
            ("item_fts", "item_id"), ("item_chunk_fts", "item_id"),
            ("item_chunk_embeddings", "item_id"), ("item_chunks", "item_id"),
            ("items", "item_id"),
        ):
            if _has_table(conn, table):
                conn.execute(f'DELETE FROM "{table}" WHERE "{column}" = ?', (item_id,))
        _audit(conn, "delete", item_id, user_id, {"retained_history": True})
    return {"deleted": True, "item_id": item_id, "audited": True,
            "retained_history": True, "source_files_retained": True}
