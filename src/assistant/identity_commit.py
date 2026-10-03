"""Keep items DB aligned with disk after apply/undo (truth loop)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from items.file_identity import remember_path
from items.hot_index import rebuild_fts


def commit_item_path(
        conn: sqlite3.Connection,
        item_id: str,
        new_path: Path,
) -> None:
    """Update open_target, display_label, bookmark for one item; no-op if missing."""
    has = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='items'"
    ).fetchone()
    if has is None:
        return
    path = new_path.resolve()
    label = path.name
    row = conn.execute(
        "SELECT item_id FROM items WHERE item_id=?", (item_id,)
    ).fetchone()
    if row is None:
        return
    conn.execute(
        "UPDATE items SET open_target=?, display_label=? WHERE item_id=?",
        (str(path), label, item_id),
    )
    if path.is_file():
        remember_path(conn, item_id, path)


def commit_ops_and_reindex(
        conn: sqlite3.Connection,
        ops: list[tuple[str, Path]],
) -> None:
    """ops = [(item_id, new_path), ...]; then rebuild FTS."""
    for item_id, path in ops:
        commit_item_path(conn, item_id, path)
    try:
        rebuild_fts(conn)
    except Exception:
        pass
