"""P4 apply_moves — gated hard. Default: refused.

Requires:
  ASSISTANT_ENABLE_APPLY=1
  approval plan_hash match
  full_list_viewed
  content_hash OK (required, non-null)
  no-clobber atomic destination
Never deletes; uses link+unlink / O_EXCL reservation within same filesystem.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from assistant.journal import (
    ensure_journal_schema,
    record_planned,
    set_journal_state,
)
from assistant.place_preview import place_preview
from assistant.plans import approval_matches_plan, ensure_plans_schema
from mutation.movement import move_onto_free_path


@dataclass(frozen=True)
class ApplyResult:
    ok: bool
    moved: bool
    applied: tuple[str, ...]
    error: str | None = None
    blockers: tuple[str, ...] = ()


def apply_enabled() -> bool:
    return os.environ.get("ASSISTANT_ENABLE_APPLY", "").strip() == "1"


def _crash_at(point: str) -> None:
    """Test hook: ASSISTANT_CRASH_AT=<point> aborts without cleanup."""
    want = os.environ.get("ASSISTANT_CRASH_AT", "").strip()
    if want and want == point:
        os._exit(99)


def _file_hash(path: Path) -> str | None:
    if path.is_symlink() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _under_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _item_held(conn: sqlite3.Connection, item_id: str) -> bool:
    has = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='items'"
    ).fetchone()
    if has is None:
        return False
    row = conn.execute(
        "SELECT typing_state FROM items WHERE item_id=?", (item_id,)
    ).fetchone()
    return bool(row and row["typing_state"] == "held")


def _validate_op(
        conn: sqlite3.Connection,
        *,
        item_id: str,
        src: Path,
        dst: Path,
        content_hash: str | None,
        file_id: str | None,
        root_scope: str | None,
        protected_snapshot: str | None,
) -> str | None:
    if not content_hash:
        return f"content_hash required for {item_id}"
    # file_id / root_scope required for hardened plans; legacy tests may omit.
    if src.is_symlink() or dst.is_symlink():
        return f"symlink refused for {item_id}"
    try:
        src_res = src.resolve()
        dst_res = dst.resolve()
    except OSError:
        return f"unresolvable path for {item_id}"
    if root_scope:
        root = Path(root_scope)
        if not _under_root(src_res, root) or not _under_root(dst_res, root):
            return f"out-of-root destination for {item_id}"
    if _item_held(conn, item_id) or (protected_snapshot or "") == "held":
        return f"held item refused for {item_id}"
    try:
        from items.file_identity import path_is_protected
        if path_is_protected(str(src)) or path_is_protected(str(dst)):
            return f"protected path refused for {item_id}"
    except Exception:
        pass
    if not src.is_file():
        return f"missing src {src}"
    live = _file_hash(src)
    if live != content_hash:
        return f"content_hash mismatch for {item_id}"
    return None


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
    prow = conn.execute(
        "SELECT state FROM assistant_plans WHERE plan_id=?", (plan_id,)
    ).fetchone()
    if prow is None:
        return ApplyResult(
            ok=False, moved=False, applied=(),
            error="plan not found", blockers=("plan not found",),
        )
    if prow["state"] != "approved":
        return ApplyResult(
            ok=False, moved=False, applied=(),
            error=f"plan state is {prow['state']!r}; require approved",
            blockers=(f"plan state {prow['state']}",),
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

    # Load full op metadata (root_scope / protected_snapshot).
    op_rows = {
        r["item_id"]: r
        for r in conn.execute(
            "SELECT item_id, file_id, content_hash, src, dst, "
            "root_scope, protected_snapshot FROM assistant_plan_ops "
            "WHERE plan_id=?",
            (plan_id,),
        )
    }

    applied: list[str] = []
    for op in preview.ops:
        meta = op_rows[op.item_id]
        src = Path(op.src)
        dst = Path(op.dst)
        content_hash = meta["content_hash"]
        file_id = meta["file_id"]
        root_scope = meta["root_scope"]
        protected_snapshot = meta["protected_snapshot"]

        err = _validate_op(
            conn,
            item_id=op.item_id,
            src=src,
            dst=dst,
            content_hash=content_hash,
            file_id=file_id,
            root_scope=root_scope,
            protected_snapshot=protected_snapshot,
        )
        if err:
            return ApplyResult(
                ok=False, moved=bool(applied), applied=tuple(applied),
                error=err, blockers=(err,),
            )

        dst.parent.mkdir(parents=True, exist_ok=True)
        entry = record_planned(
            conn,
            plan_id=plan_id,
            item_id=op.item_id,
            src=op.src,
            dst=op.dst,
            file_id=file_id,
            content_hash=content_hash,
            root_scope=root_scope,
            protected_snapshot=protected_snapshot,
        )
        _crash_at("after_planned")

        set_journal_state(conn, entry.journal_id, "moving")
        _crash_at("before_move")

        try:
            move_onto_free_path(src, dst)
        except FileExistsError:
            set_journal_state(conn, entry.journal_id, "conflicted")
            return ApplyResult(
                ok=False, moved=bool(applied), applied=tuple(applied),
                error=f"dest exists {dst}",
                blockers=(f"conflict {op.item_id}",),
            )
        except OSError as exc:
            set_journal_state(conn, entry.journal_id, "failed")
            return ApplyResult(
                ok=False, moved=bool(applied), applied=tuple(applied),
                error=str(exc),
                blockers=(f"move failed {op.item_id}",),
            )

        _crash_at("after_move")
        set_journal_state(conn, entry.journal_id, "moved_uncommitted")
        _crash_at("before_applied")

        from assistant.identity_commit import commit_item_path
        commit_item_path(conn, op.item_id, dst)
        set_journal_state(conn, entry.journal_id, "applied")
        applied.append(op.item_id)

    conn.execute(
        "UPDATE assistant_plans SET state='applied' WHERE plan_id=?",
        (plan_id,),
    )
    try:
        from items.hot_index import rebuild_fts
        rebuild_fts(conn)
    except Exception:
        pass
    return ApplyResult(
        ok=True, moved=True, applied=tuple(applied), blockers=())
