"""P3 place_preview / dry-run — never moves files.

Verifies content_hash when present; requires hash/file_id/root for apply;
surfaces held/symlink/out-of-root blockers; full op list for approval UI.
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from assistant.plans import (
    approval_matches_plan,
    plan_hash,
    require_full_list_viewed,
)


@dataclass(frozen=True)
class PreviewOp:
    item_id: str
    src: str
    dst: str
    content_hash: str | None
    hash_ok: bool | None  # None if no hash recorded
    exists_src: bool
    dest_exists: bool


@dataclass(frozen=True)
class PlacePreview:
    plan_id: str
    plan_hash: str
    ops: tuple[PreviewOp, ...]
    approval_matches: bool
    full_list_viewed_required: bool
    can_apply: bool
    blockers: tuple[str, ...]
    moved: bool = False


def _file_hash(path: Path) -> str | None:
    if not path.is_file() or path.is_symlink():
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


def place_preview(
        conn: sqlite3.Connection,
        plan_id: str,
        *,
        full_list_viewed: bool = False,
) -> PlacePreview:
    """Dry-run a plan. Nothing is moved."""
    from assistant.plans import ensure_plans_schema
    ensure_plans_schema(conn)
    row = conn.execute(
        "SELECT state FROM assistant_plans WHERE plan_id = ?", (plan_id,)
    ).fetchone()
    blockers: list[str] = []
    if row is None:
        return PlacePreview(
            plan_id=plan_id, plan_hash="", ops=(),
            approval_matches=False,
            full_list_viewed_required=True,
            can_apply=False,
            blockers=("plan not found",),
        )
    if row["state"] not in ("approved", "draft"):
        # Still previewable, but apply will refuse non-approved.
        pass
    h = plan_hash(conn, plan_id)
    matches = approval_matches_plan(conn, plan_id)
    if not matches:
        blockers.append("approval missing or plan_hash mismatch")
    if not require_full_list_viewed(full_list_viewed):
        blockers.append("full list not viewed")
    ops_out: list[PreviewOp] = []
    for r in conn.execute(
        "SELECT item_id, src, dst, content_hash, file_id, "
        "root_scope, protected_snapshot "
        "FROM assistant_plan_ops WHERE plan_id = ? ORDER BY item_id",
        (plan_id,),
    ):
        src_p = Path(r["src"])
        dst_p = Path(r["dst"])
        exists_src = src_p.is_file() and not src_p.is_symlink()
        dest_exists = dst_p.exists()
        recorded = r["content_hash"]
        hash_ok: bool | None = None
        if not recorded:
            blockers.append(f"content_hash required for {r['item_id']}")
        else:
            live = _file_hash(src_p) if exists_src else None
            hash_ok = live == recorded
            if hash_ok is False:
                blockers.append(
                    f"content_hash mismatch for {r['item_id']}")
        # file_id / root_scope optional for legacy plans; enforce scope when set.
        root_scope = r["root_scope"]
        if root_scope:
            root = Path(root_scope)
            try:
                if not _under_root(src_p, root) or not _under_root(dst_p, root):
                    blockers.append(
                        f"out-of-root destination for {r['item_id']}")
            except OSError:
                blockers.append(f"unresolvable path for {r['item_id']}")
        if src_p.is_symlink() or dst_p.is_symlink():
            blockers.append(f"symlink refused for {r['item_id']}")
        if _item_held(conn, r["item_id"]) or (
                r["protected_snapshot"] or "") == "held":
            blockers.append(f"held item refused for {r['item_id']}")
        if not exists_src:
            blockers.append(f"missing src {r['src']}")
        if dest_exists:
            blockers.append(f"dest exists {r['dst']}")
        ops_out.append(PreviewOp(
            item_id=r["item_id"], src=r["src"], dst=r["dst"],
            content_hash=recorded, hash_ok=hash_ok,
            exists_src=exists_src, dest_exists=dest_exists,
        ))
    from assistant.apply import apply_enabled
    if not apply_enabled():
        blockers.append(
            "ASSISTANT_ENABLE_APPLY not set — apply refused")
    clean = [b for b in blockers if "ASSISTANT_ENABLE_APPLY" not in b]
    can = (
        apply_enabled()
        and matches
        and full_list_viewed
        and not clean
    )
    return PlacePreview(
        plan_id=plan_id,
        plan_hash=h,
        ops=tuple(ops_out),
        approval_matches=matches,
        full_list_viewed_required=True,
        can_apply=can,
        blockers=tuple(dict.fromkeys(blockers)),
        moved=False,
    )


def preview_as_dict(preview: PlacePreview) -> dict[str, Any]:
    return {
        "plan_id": preview.plan_id,
        "plan_hash": preview.plan_hash,
        "ops": [
            {
                "item_id": o.item_id,
                "src": o.src,
                "dst": o.dst,
                "content_hash": o.content_hash,
                "hash_ok": o.hash_ok,
                "exists_src": o.exists_src,
                "dest_exists": o.dest_exists,
            }
            for o in preview.ops
        ],
        "approval_matches": preview.approval_matches,
        "full_list_viewed_required": preview.full_list_viewed_required,
        "can_apply": preview.can_apply,
        "blockers": list(preview.blockers),
        "moved": False,
    }
