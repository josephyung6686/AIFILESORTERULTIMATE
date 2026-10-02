"""P4 apply_moves — gated hard. Default: refused.

Requires:
  ASSISTANT_ENABLE_APPLY=1
  approval plan_hash match
  full_list_viewed
  content_hash OK when recorded
  dest does not exist
Never deletes; uses rename/replace only within same filesystem when possible.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from assistant.journal import ensure_journal_schema, record_planned
from assistant.place_preview import place_preview
from assistant.plans import approval_matches_plan, ensure_plans_schema


@dataclass(frozen=True)
class ApplyResult:
    ok: bool
    moved: bool
    applied: tuple[str, ...]
    error: str | None = None
    blockers: tuple[str, ...] = ()


def apply_enabled() -> bool:
    return os.environ.get("ASSISTANT_ENABLE_APPLY", "").strip() == "1"


def apply_plan(
        conn: sqlite3.Connection,
        plan_id: str,
        *,
        full_list_viewed: bool = False,
) -> ApplyResult:
    ensure_plans_schema(conn)
    ensure_journal_schema(conn)
    if not apply_enabled():
        return ApplyResult(
            ok=False, moved=False, applied=(),
            error="ASSISTANT_ENABLE_APPLY not set — apply refused",
            blockers=("apply disabled",),
        )
    if not full_list_viewed:
        return ApplyResult(
            ok=False, moved=False, applied=(),
            error="full list must be viewed before apply",
            blockers=("full list not viewed",),
        )
    if not approval_matches_plan(conn, plan_id):
        return ApplyResult(
            ok=False, moved=False, applied=(),
            error="approval plan_hash mismatch or missing",
            blockers=("plan_hash mismatch",),
        )
    preview = place_preview(
        conn, plan_id, full_list_viewed=True)
    # Drop env-gate wording from preview when we already passed apply_enabled().
    real_blockers = [
        b for b in preview.blockers
        if "not enabled in this build" not in b
        and "ASSISTANT_ENABLE_APPLY" not in b
    ]
    if real_blockers:
        return ApplyResult(
            ok=False, moved=False, applied=(),
            error="preview blockers remain",
            blockers=tuple(real_blockers),
        )
    applied: list[str] = []
    for op in preview.ops:
        src = Path(op.src)
        dst = Path(op.dst)
        if not src.is_file() or dst.exists():
            return ApplyResult(
                ok=False, moved=bool(applied), applied=tuple(applied),
                error=f"conflict at {op.item_id}",
                blockers=(f"conflict {op.item_id}",),
            )
        dst.parent.mkdir(parents=True, exist_ok=True)
        record_planned(
            conn, plan_id=plan_id, item_id=op.item_id,
            src=op.src, dst=op.dst, content_hash=op.content_hash)
        shutil.move(str(src), str(dst))
        applied.append(op.item_id)
        ts = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "UPDATE assistant_journal SET state='applied', updated_ts=? "
            "WHERE plan_id=? AND item_id=?",
            (ts, plan_id, op.item_id),
        )
    conn.execute(
        "UPDATE assistant_plans SET state='applied' WHERE plan_id=?",
        (plan_id,),
    )
    return ApplyResult(
        ok=True, moved=True, applied=tuple(applied), blockers=())
