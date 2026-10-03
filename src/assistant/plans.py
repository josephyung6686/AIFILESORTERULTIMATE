"""Plan objects + risk tiers. No apply in this build.

Addendum A2–A5: T0 template rename, plan_hash, full-list before approve.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

# Prefixed assistant_* — sorter uses move_plans / move_journal separately.
PLANS_DDL = """
CREATE TABLE IF NOT EXISTS assistant_plans (
    plan_id TEXT PRIMARY KEY,
    risk_tier TEXT NOT NULL,
    created_ts TEXT NOT NULL,
    state TEXT NOT NULL,
    summary_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS assistant_plan_ops (
    plan_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    file_id TEXT,
    content_hash TEXT,
    src TEXT NOT NULL,
    dst TEXT NOT NULL,
    op_state TEXT NOT NULL,
    PRIMARY KEY (plan_id, item_id)
);
CREATE TABLE IF NOT EXISTS assistant_approvals (
    plan_id TEXT PRIMARY KEY,
    plan_hash TEXT NOT NULL,
    decided_ts TEXT NOT NULL,
    decision TEXT NOT NULL,
    approve_ms REAL,
    actor TEXT NOT NULL,
    full_list_viewed INTEGER NOT NULL DEFAULT 0
);
"""

RISK_TIERS = frozenset({"T0", "T1", "T2", "T3"})
PLAN_STATES = frozenset({
    "draft", "approved", "applied", "undone", "rejected",
})


@dataclass(frozen=True)
class PlanOp:
    item_id: str
    src: str
    dst: str
    file_id: str | None = None
    content_hash: str | None = None


@dataclass(frozen=True)
class Plan:
    plan_id: str
    risk_tier: str
    state: str
    ops: tuple[PlanOp, ...]
    reversible: bool
    summary: dict[str, Any]


@dataclass(frozen=True)
class ApproveResult:
    ok: bool
    plan_hash: str | None = None
    error: str | None = None


def ensure_plans_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(PLANS_DDL)
    # Migrate older approvals rows missing plan_hash / full_list_viewed.
    cols = {
        r[1] for r in conn.execute("PRAGMA table_info(assistant_approvals)")
    }
    if "plan_hash" not in cols:
        try:
            conn.execute(
                "ALTER TABLE assistant_approvals ADD COLUMN plan_hash TEXT "
                "NOT NULL DEFAULT ''"
            )
        except sqlite3.OperationalError:
            pass
    if "full_list_viewed" not in cols:
        try:
            conn.execute(
                "ALTER TABLE assistant_approvals ADD COLUMN "
                "full_list_viewed INTEGER NOT NULL DEFAULT 0"
            )
        except sqlite3.OperationalError:
            pass


def _ops_canonical(ops: Sequence[PlanOp] | Sequence[dict]) -> str:
    rows = []
    for op in ops:
        if isinstance(op, PlanOp):
            rows.append({
                "item_id": op.item_id,
                "file_id": op.file_id or "",
                "content_hash": op.content_hash or "",
                "src": op.src,
                "dst": op.dst,
            })
        else:
            rows.append({
                "item_id": op["item_id"],
                "file_id": op.get("file_id") or "",
                "content_hash": op.get("content_hash") or "",
                "src": op["src"],
                "dst": op["dst"],
            })
    rows.sort(key=lambda r: r["item_id"])
    return json.dumps(rows, separators=(",", ":"), ensure_ascii=False)


def plan_hash(conn: sqlite3.Connection, plan_id: str) -> str:
    """sha256 of canonical full op list (Addendum A3)."""
    ensure_plans_schema(conn)
    rows = conn.execute(
        "SELECT item_id, file_id, content_hash, src, dst "
        "FROM assistant_plan_ops WHERE plan_id = ? ORDER BY item_id",
        (plan_id,),
    ).fetchall()
    ops = [
        {
            "item_id": r["item_id"],
            "file_id": r["file_id"],
            "content_hash": r["content_hash"],
            "src": r["src"],
            "dst": r["dst"],
        }
        for r in rows
    ]
    return hashlib.sha256(_ops_canonical(ops).encode("utf-8")).hexdigest()


def create_draft_plan(
        conn: sqlite3.Connection,
        *,
        ops: Sequence[PlanOp],
        risk_tier: str = "T1",
        reversible: bool = True,
        require_grounded: bool = False,
        session_key: str = "default",
        user_picked_ids: Sequence[str] | None = None,
) -> Plan:
    """Create a draft plan from code-built ops. Never from free-form file text.

    When require_grounded=True, every op.item_id must be session-surfaced
    (find_files) or in user_picked_ids (explicit CLI/user pick).
    """
    ensure_plans_schema(conn)
    if risk_tier not in RISK_TIERS:
        raise ValueError(f"unknown risk_tier: {risk_tier}")
    if not ops:
        raise ValueError("plan requires at least one op")
    if require_grounded:
        from assistant.session_surface import assert_ops_grounded
        bad = assert_ops_grounded(
            conn, [op.item_id for op in ops],
            session_key=session_key,
            extra_allowed=set(user_picked_ids or ()),
        )
        if bad:
            raise PermissionError(
                f"ungrounded_item: {bad} — find or user-pick first"
            )
    plan_id = str(uuid.uuid4())
    summary = {
        "count": len(ops),
        "reversible": reversible,
        "sample_src": ops[0].src,
        "sample_dst": ops[0].dst,
        "full_list_required": True,
        "ops": [
            {
                "item_id": op.item_id,
                "src": op.src,
                "dst": op.dst,
                "file_id": op.file_id,
                "content_hash": op.content_hash,
            }
            for op in ops
        ],
    }
    ts = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO assistant_plans ("
        "plan_id, risk_tier, created_ts, state, summary_json) "
        "VALUES (?,?,?,?,?)",
        (plan_id, risk_tier, ts, "draft", json.dumps(summary)),
    )
    for op in ops:
        conn.execute(
            "INSERT INTO assistant_plan_ops ("
            "plan_id, item_id, file_id, content_hash, src, dst, op_state) "
            "VALUES (?,?,?,?,?,?,?)",
            (plan_id, op.item_id, op.file_id, op.content_hash,
             op.src, op.dst, "pending"),
        )
    return Plan(
        plan_id=plan_id,
        risk_tier=risk_tier,
        state="draft",
        ops=tuple(ops),
        reversible=reversible,
        summary=summary,
    )


def edit_plan_ops(
        conn: sqlite3.Connection,
        plan_id: str,
        ops: Sequence[PlanOp],
) -> None:
    """Replace ops; invalidates any prior approval (hash changes)."""
    ensure_plans_schema(conn)
    if not ops:
        raise ValueError("plan requires at least one op")
    conn.execute("DELETE FROM assistant_plan_ops WHERE plan_id = ?", (plan_id,))
    conn.execute(
        "DELETE FROM assistant_approvals WHERE plan_id = ?", (plan_id,))
    summary = {
        "count": len(ops),
        "reversible": True,
        "sample_src": ops[0].src,
        "sample_dst": ops[0].dst,
        "full_list_required": True,
        "ops": [
            {
                "item_id": op.item_id,
                "src": op.src,
                "dst": op.dst,
                "file_id": op.file_id,
                "content_hash": op.content_hash,
            }
            for op in ops
        ],
    }
    conn.execute(
        "UPDATE assistant_plans SET state='draft', summary_json=? "
        "WHERE plan_id=?",
        (json.dumps(summary), plan_id),
    )
    for op in ops:
        conn.execute(
            "INSERT INTO assistant_plan_ops ("
            "plan_id, item_id, file_id, content_hash, src, dst, op_state) "
            "VALUES (?,?,?,?,?,?,?)",
            (plan_id, op.item_id, op.file_id, op.content_hash,
             op.src, op.dst, "pending"),
        )


def require_full_list_viewed(full_list_viewed: bool) -> bool:
    """Approve stays disabled until full op list was viewed (A5)."""
    return bool(full_list_viewed)


def approve_plan(
        conn: sqlite3.Connection,
        plan_id: str,
        *,
        actor: str = "user",
        approve_ms: float | None = None,
        full_list_viewed: bool = False,
) -> ApproveResult:
    ensure_plans_schema(conn)
    row = conn.execute(
        "SELECT state, risk_tier FROM assistant_plans WHERE plan_id = ?",
        (plan_id,),
    ).fetchone()
    if row is None:
        return ApproveResult(ok=False, error="plan not found")
    if not require_full_list_viewed(full_list_viewed):
        return ApproveResult(
            ok=False,
            error="full list must be viewed before Approve (Addendum A5)",
        )
    # T2/T3: <2s requires re-confirm — caller must pass actor=user-reconfirm
    tier = row["risk_tier"]
    if tier in ("T2", "T3") and approve_ms is not None and approve_ms < 2000:
        if actor != "user-reconfirm":
            return ApproveResult(
                ok=False,
                error=(
                    f"{tier} approval under 2s requires re-confirm "
                    f"(Addendum T-P4-07)"
                ),
            )
    h = plan_hash(conn, plan_id)
    ts = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO assistant_approvals ("
        "plan_id, plan_hash, decided_ts, decision, approve_ms, actor, "
        "full_list_viewed) VALUES (?,?,?,?,?,?,1)",
        (plan_id, h, ts, "approved", approve_ms, actor),
    )
    conn.execute(
        "UPDATE assistant_plans SET state='approved' WHERE plan_id=?",
        (plan_id,),
    )
    return ApproveResult(ok=True, plan_hash=h)


def approval_matches_plan(conn: sqlite3.Connection, plan_id: str) -> bool:
    ensure_plans_schema(conn)
    row = conn.execute(
        "SELECT plan_hash FROM assistant_approvals WHERE plan_id = ? "
        "AND decision = 'approved'",
        (plan_id,),
    ).fetchone()
    if row is None:
        return False
    return row["plan_hash"] == plan_hash(conn, plan_id)


def render_t0_rename(
        *,
        template: str,
        stem: str,
        type_: str,
        date: str,
        source: str = "",
) -> str:
    """Template-only rename (A2). No model free text."""
    return (
        template
        .replace("{date}", date)
        .replace("{type}", type_)
        .replace("{stem}", stem)
        .replace("{source}", source)
    )


def validate_t0_dst(basename: str, *, template_rendered: bool) -> bool:
    """T0 auto-allow only when dst name was template-rendered."""
    if not template_rendered:
        return False
    if not basename or "/" in basename or "\\" in basename:
        return False
    return True


def refuse_apply_without_approval(conn: sqlite3.Connection, plan_id: str) -> str:
    """Structural guarantee: apply without approval always fails."""
    ensure_plans_schema(conn)
    row = conn.execute(
        "SELECT state FROM assistant_plans WHERE plan_id = ?", (plan_id,)
    ).fetchone()
    if row is None:
        return "plan not found — nothing applied"
    if row["state"] != "approved":
        return (
            f"plan {plan_id} is {row['state']!r}; apply requires state "
            f"'approved'. Nothing moved."
        )
    if not approval_matches_plan(conn, plan_id):
        return (
            f"plan {plan_id} approval plan_hash mismatch — re-approve after "
            f"edit. Nothing moved."
        )
    from assistant.apply import apply_enabled
    if not apply_enabled():
        return (
            f"plan {plan_id} is approved but ASSISTANT_ENABLE_APPLY is not set. "
            f"Nothing moved."
        )
    return (
        f"plan {plan_id} is approved and apply is enabled — call apply_plan "
        f"/ CLI plan apply with --full-list-viewed. Nothing moved yet."
    )
