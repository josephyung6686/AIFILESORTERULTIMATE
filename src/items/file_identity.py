"""Rename-follow helpers: stable file IDs + bookmark blobs (macOS)."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from scan_agent.exclusion import is_protected_container

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
    """Either protection list covers this path: the item layer's private names,
    or the sorter's protected containers (a `.app` and everything inside it).
    A union -- this can only add protection."""
    parts = {part.casefold() for part in path.replace("\\", "/").split("/")}
    if parts & _PROTECTED_PARTS:
        return True
    lower = path.casefold()
    if any(lower.endswith(ext) for ext in _PROTECTED_EXTENSIONS):
        return True
    return bool(path) and is_protected_container(path)


def record_is_held(record) -> bool:
    """The sorter's hold, as `items.typing._map` reads a classification record."""
    return bool(getattr(record, "protected", False)) or (
        getattr(record, "basis", None) == "safety_domain")


def item_is_sensitive(conn: sqlite3.Connection, item_id: str) -> bool:
    """THE one answer to "is this item sensitive?", read live (owner, 3 Oct 2026).

    True when any of these says so -- a union, never weaker than any one alone:
    the copied `items.typing_state == 'held'`; the sorter's CURRENT
    classification record for the file version (so `--file-held` lands at once,
    without a re-run); or either path list. A store that cannot give one clear
    answer fails closed. An item this database does not hold is not sensitive
    (there is nothing of it to send).
    """
    row = conn.execute(
        "SELECT typing_state, open_target, file_id, content_hash FROM items "
        "WHERE item_id = ?", (item_id,)).fetchone()
    if row is None:
        return False
    typing_state, open_target, file_id, content_hash = tuple(row)
    if typing_state == "held":
        return True
    if open_target and path_is_protected(open_target):
        return True
    return _store_holds(conn, file_id, content_hash)


def _has_table(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (name,)).fetchone() is not None


def _store_holds(conn: sqlite3.Connection, file_id: str | None,
                 item_hash: str | None) -> bool:
    if not file_id or not _has_table(conn, "classifications"):
        return False
    # The sorter keys its record on the `files` row's hash (`apply_file_held`,
    # `project_typing`); the item's own hash is asked too, so a stale one in
    # either place cannot hide a hold.
    hashes = []
    if _has_table(conn, "files"):
        found = conn.execute("SELECT content_hash FROM files WHERE file_id = ?",
                             (file_id,)).fetchone()
        if found is not None and found[0]:
            hashes.append(found[0])
    if item_hash and item_hash not in hashes:
        hashes.append(item_hash)
    from privacy.classification_store import ClassificationStore
    store = ClassificationStore(conn)
    for content_hash in hashes:
        try:
            record = store.current(file_id, content_hash)
        except Exception:
            return True  # two live answers, or an unreadable row: fail closed
        if record is not None and record_is_held(record):
            return True
    return False


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
