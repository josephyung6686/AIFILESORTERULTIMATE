"""P4 undo_moves — reverse applied journal ops. Same env gate as apply.

Undo only when the destination content hash still matches the journal.
Uses no-clobber atomic move back to the original path.
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from assistant.apply import apply_enabled, _crash_at
from assistant.journal import (
    ensure_journal_schema,
    entries_for_plan,
    set_journal_state,
)
from mutation.movement import move_onto_free_path


@dataclass(frozen=True)
class UndoResult:
    ok: bool
    moved: bool
    undone: tuple[str, ...]
    error: str | None = None


def _file_hash(path: Path) -> str | None:
    if path.is_symlink() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def undo_plan(conn: sqlite3.Connection, plan_id: str, *,
              confirmed_by_person: bool = False) -> UndoResult:
    ensure_journal_schema(conn)
    if not apply_enabled(confirmed_by_person=confirmed_by_person):
        return UndoResult(
            ok=False, moved=False, undone=(),
            error="ASSISTANT_ENABLE_APPLY not set — undo refused")
    entries = [
        e for e in entries_for_plan(conn, plan_id) if e.state == "applied"
    ]
    if not entries:
        return UndoResult(
            ok=False, moved=False, undone=(),
            error="no applied journal entries")
    undone: list[str] = []
    for e in reversed(entries):
        cur = Path(e.dst)  # current location
        orig = Path(e.src)  # original
        if not cur.is_file() or cur.is_symlink():
            set_journal_state(conn, e.journal_id, "conflicted")
            return UndoResult(
                ok=False, moved=bool(undone), undone=tuple(undone),
                error=f"missing current file {e.dst}")
        live = _file_hash(cur)
        if not e.content_hash or live != e.content_hash:
            set_journal_state(conn, e.journal_id, "conflicted")
            return UndoResult(
                ok=False, moved=bool(undone), undone=tuple(undone),
                error=f"content hash mismatch at undo for {e.item_id}")
        if orig.exists():
            set_journal_state(conn, e.journal_id, "conflicted")
            return UndoResult(
                ok=False, moved=bool(undone), undone=tuple(undone),
                error=f"original path occupied {e.src}")

        set_journal_state(conn, e.journal_id, "undo_planned")
        _crash_at("undo_before_move")
        orig.parent.mkdir(parents=True, exist_ok=True)
        try:
            move_onto_free_path(cur, orig)
        except FileExistsError:
            set_journal_state(conn, e.journal_id, "conflicted")
            return UndoResult(
                ok=False, moved=bool(undone), undone=tuple(undone),
                error=f"original path occupied {e.src}")
        except OSError as exc:
            set_journal_state(conn, e.journal_id, "failed")
            return UndoResult(
                ok=False, moved=bool(undone), undone=tuple(undone),
                error=str(exc))

        from assistant.identity_commit import commit_item_path
        commit_item_path(conn, e.item_id, orig)
        set_journal_state(conn, e.journal_id, "undone")
        undone.append(e.item_id)

    conn.execute(
        "UPDATE assistant_plans SET state='undone' WHERE plan_id=?",
        (plan_id,),
    )
    # Invalidate approval so re-apply needs a new plan_hash approval.
    conn.execute(
        "DELETE FROM assistant_approvals WHERE plan_id=?", (plan_id,)
    )
    try:
        from items.hot_index import rebuild_fts
        rebuild_fts(conn)
    except Exception:
        pass
    return UndoResult(ok=True, moved=True, undone=tuple(undone))
