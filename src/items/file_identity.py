"""Rename-follow helpers: stable file IDs + bookmark blobs (macOS)."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

BOOKMARK_DDL = """
CREATE TABLE IF NOT EXISTS item_bookmarks (
    item_id TEXT PRIMARY KEY,
    file_id_token TEXT,
    bookmark_blob BLOB,
    last_path TEXT
);
"""


def ensure_bookmark_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(BOOKMARK_DDL)


def file_id_token(path: Path) -> str | None:
    """Stable-ish identity: st_dev + st_ino (POSIX)."""
    try:
        st = path.stat()
    except OSError:
        return None
    return f"{st.st_dev}:{st.st_ino}"


def remember_path(conn: sqlite3.Connection, item_id: str, path: Path) -> None:
    ensure_bookmark_schema(conn)
    token = file_id_token(path)
    conn.execute(
        "INSERT INTO item_bookmarks (item_id, file_id_token, bookmark_blob, "
        "last_path) VALUES (?,?,NULL,?) "
        "ON CONFLICT(item_id) DO UPDATE SET "
        "file_id_token=excluded.file_id_token, last_path=excluded.last_path",
        (item_id, token, str(path)),
    )


def resolve_renamed(
        conn: sqlite3.Connection,
        item_id: str,
        candidates: list[Path],
) -> Path | None:
    """If a candidate shares file_id_token, treat as rename-follow hit."""
    ensure_bookmark_schema(conn)
    row = conn.execute(
        "SELECT file_id_token FROM item_bookmarks WHERE item_id = ?",
        (item_id,),
    ).fetchone()
    if row is None or not row["file_id_token"]:
        return None
    want = row["file_id_token"]
    for path in candidates:
        if file_id_token(path) == want:
            remember_path(conn, item_id, path)
            return path
    return None


def scan_for_token(root: Path, token: str) -> Path | None:
    if not root.is_dir():
        return None
    for path in root.rglob("*"):
        if path.is_file() and file_id_token(path) == token:
            return path
    return None
