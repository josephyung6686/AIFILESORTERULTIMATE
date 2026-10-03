"""Local privacy boundaries for the everyday CLI product.

This module is deliberately conservative: plain SQLite is reported as plain
SQLite, held records require an explicit local-authentication seam, and export
and deletion are audited.  It never stores credentials or message bodies.
"""
from __future__ import annotations

import json
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
    if version:
        return EncryptionCapability(True, f"sqlcipher-{version}", "")
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
    row = conn.execute("SELECT * FROM items WHERE item_id = ?", (item_id,)).fetchone()
    if row is None:
        return {}
    state = row["typing_state"] if isinstance(row, sqlite3.Row) else row[5]
    if state == "held":
        _authenticate(authenticate)
    return dict(row) if isinstance(row, sqlite3.Row) else {
        key[0]: value for key, value in zip(conn.execute("PRAGMA table_info(items)"), row)
    }


_SECRET_NAMES = frozenset({
    "body", "description", "raw", "rfc822", "token", "tokens",
    "access_token", "refresh_token", "oauth", "authorization",
})


def _table_names(conn: sqlite3.Connection) -> list[str]:
    return [row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]


def export_database(conn: sqlite3.Connection, destination: Path, *,
                    user_id: str = "local") -> dict[str, Any]:
    """Write a sanitized, auditable JSON export of local records."""
    create_privacy_schema(conn)
    tables: dict[str, list[dict[str, Any]]] = {}
    excluded: dict[str, list[str]] = {}
    for table in _table_names(conn):
        if table == "privacy_audit_events":
            continue
        columns = [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')]
        keep = [c for c in columns if c.casefold() not in _SECRET_NAMES and
                not any(secret in c.casefold() for secret in _SECRET_NAMES)]
        excluded[table] = [c for c in columns if c not in keep]
        if not keep:
            continue
        quoted = ", ".join(f'"{c}"' for c in keep)
        rows = conn.execute(f'SELECT {quoted} FROM "{table}"').fetchall()
        tables[table] = [dict(zip(keep, row)) for row in rows]
    payload = {
        "format": "graph-agent-sanitized-export-v1",
        "encrypted_at_rest": encryption_capability(conn).encrypted,
        "tables": tables,
        # Do not echo secret field names into an export either: even schema
        # metadata can disclose that a credential-bearing source was present.
        "excluded_field_counts": {table: len(fields) for table, fields in excluded.items()},
    }
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    _audit(conn, "export", str(destination), user_id,
           {"table_count": len(tables),
            "excluded_field_counts": {table: len(fields) for table, fields in excluded.items()}})
    conn.commit()
    return {"destination": str(destination), "tables": len(tables), "audited": True}


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name = ?", (name,)
    ).fetchone() is not None


def delete_item(conn: sqlite3.Connection, item_id: str, *, user_id: str = "local",
                authenticate: Callable[[], bool] | None = None) -> dict[str, Any]:
    """Delete one item and all searchable/projection rows, with an audit event."""
    row = conn.execute("SELECT typing_state FROM items WHERE item_id = ?", (item_id,)).fetchone()
    if row is None:
        return {"deleted": False, "item_id": item_id, "audited": False}
    state = row[0]
    if state == "held":
        _authenticate(authenticate)
    nested = conn.in_transaction
    if nested:
        conn.execute("SAVEPOINT privacy_delete")
    else:
        conn.execute("BEGIN IMMEDIATE")
    try:
        for table, column in (
            ("relationships", "from_item_id"), ("relationships", "to_item_id"),
            ("relationship_decisions", "relationship_id"),
            ("item_headers", "item_id"), ("item_versions", "item_id"),
            ("item_identity_events", "item_id"), ("item_chunks", "item_id"),
            ("item_chunk_embeddings", "item_id"), ("vector_embeddings", "item_id"),
            ("items", "item_id"),
        ):
            if _has_table(conn, table):
                conn.execute(f'DELETE FROM "{table}" WHERE "{column}" = ?', (item_id,))
        for table in ("item_fts", "item_chunk_fts"):
            if _has_table(conn, table):
                conn.execute(f'DELETE FROM "{table}" WHERE item_id = ?', (item_id,))
        _audit(conn, "delete", item_id, user_id, {"typing_state": state})
        if nested:
            conn.execute("RELEASE SAVEPOINT privacy_delete")
        else:
            conn.commit()
    except Exception:
        if nested:
            conn.execute("ROLLBACK TO SAVEPOINT privacy_delete")
            conn.execute("RELEASE SAVEPOINT privacy_delete")
        else:
            conn.rollback()
        raise
    return {"deleted": True, "item_id": item_id, "audited": True}
