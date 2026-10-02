"""P4 undo_moves — reverse applied journal ops. Same env gate as apply."""
from __future__ import annotations

import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from assistant.apply import apply_enabled
from assistant.journal import ensure_journal_schema, entries_for_plan


@dataclass(frozen=True)
class UndoResult:
    ok: bool
    moved: bool
    undone: tuple[str, ...]
    error: str | None = None


def undo_plan(conn: sqlite3.Connection, plan_id: str) -> UndoResult:
    ensure_journal_schema(conn)
    if not apply_enabled():
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
        src = Path(e.dst)  # current location
        dst = Path(e.src)  # original
        if not src.is_file():
            return UndoResult(
                ok=False, moved=bool(undone), undone=tuple(undone),
                error=f"missing current file {e.dst}")
        if dst.exists():
            return UndoResult(
                ok=False, moved=bool(undone), undone=tuple(undone),
                error=f"original path occupied {e.src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        ts = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "UPDATE assistant_journal SET state='undone', updated_ts=? "
            "WHERE journal_id=?",
            (ts, e.journal_id),
        )
        undone.append(e.item_id)
    conn.execute(
        "UPDATE assistant_plans SET state='undone' WHERE plan_id=?",
        (plan_id,),
    )
    return UndoResult(ok=True, moved=True, undone=tuple(undone))
