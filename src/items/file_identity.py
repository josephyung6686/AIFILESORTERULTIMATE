"""Rename-follow helpers: stable file IDs + bookmark blobs (macOS)."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

#: Path parts that are private even when nobody typed them. A name-only walk
#: can see these without opening the file. Kept here so the item layer does not
#: depend on the understanding package (which is not on every branch).
_PROTECTED_PARTS: frozenset[str] = frozenset({
    ".ssh", ".gnupg", "keychains", "cookies", "passwords",
})
_PROTECTED_EXTENSIONS: frozenset[str] = frozenset({
    ".pem", ".key", ".p12", ".kdbx", ".keystore",
})


def path_is_protected(path: str) -> bool:
    parts = {part.casefold() for part in path.replace("\\", "/").split("/")}
    if parts & _PROTECTED_PARTS:
        return True
    lower = path.casefold()
    return any(lower.endswith(ext) for ext in _PROTECTED_EXTENSIONS)


BOOKMARK_DDL = """
CREATE TABLE IF NOT EXISTS item_bookmarks (
    item_id TEXT PRIMARY KEY,
    file_id_token TEXT,
    bookmark_blob BLOB,
    last_path TEXT
);
"""


@dataclass(frozen=True)
class FileIdentityMeta:
    """Durable on-disk identity fields used by freshness reconcile."""

    size: int
    mtime_ns: int
    st_dev: int
    st_ino: int


def ensure_bookmark_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(BOOKMARK_DDL)


def read_file_identity(path: Path) -> FileIdentityMeta | None:
    """lstat-shaped identity for a path, or None if absent / unreadable."""
    try:
        st = path.lstat()
    except OSError:
        return None
    if not path.is_file():
        return None
    mtime_ns = getattr(st, "st_mtime_ns", int(st.st_mtime * 1_000_000_000))
    return FileIdentityMeta(
        size=int(st.st_size),
        mtime_ns=int(mtime_ns),
        st_dev=int(st.st_dev),
        st_ino=int(st.st_ino),
    )


def file_id_token(path: Path) -> str | None:
    """Stable-ish identity: st_dev + st_ino (POSIX)."""
    meta = read_file_identity(path)
    if meta is None:
        return None
    return f"{meta.st_dev}:{meta.st_ino}"


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
