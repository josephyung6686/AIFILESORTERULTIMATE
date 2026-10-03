"""Keep items DB aligned with disk after apply/undo (truth loop)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from database_agent.files_table import get_file, observe_path
from grouping.vocabulary import P1_INCLUDED_SCAN_STATE
from items.file_identity import remember_path
from items.identity import follow_move
from scan_agent.authorship import COMPONENT_VERSION, SUBSYSTEM
from scan_agent.basic_record import parent_folder_context
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
        "SELECT file_id FROM items WHERE item_id=?", (item_id,)
    ).fetchone()
    if row is None:
        return
    conn.execute(
        "UPDATE items SET open_target=?, display_label=? WHERE item_id=?",
        (str(path), label, item_id),
    )
    if not path.is_file():
        return
    file = get_file(conn, row["file_id"]) if row["file_id"] else None
    if file is not None:
        # The same observation a sorter move makes, so `files.current_path`
        # and the item agree on where the file is.
        file_id = observe_path(
            conn, path, author=SUBSYSTEM, component_version=COMPONENT_VERSION,
            filename=path.name, normalized_filename=path.name,
            extension=file["extension"], observed_size=file["observed_size"],
            observed_timestamps=file["observed_timestamps"],
            parent_folder_context=parent_folder_context(path),
            mime_type=file["mime_type"], detected_format=file["detected_format"],
            scan_state=P1_INCLUDED_SCAN_STATE, materialized=True)
        follow_move(conn, file_id)
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
