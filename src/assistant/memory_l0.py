"""L0 DiffEvent capture with per-field provenance (Addendum A6).

v1 steering / atoms are dark. Dirty sessions write L0 only.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

L0_DDL = """
CREATE TABLE IF NOT EXISTS diff_events (
    diff_id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    ai_proposal_json TEXT NOT NULL,
    expert_fix_json TEXT NOT NULL,
    item_ids_json TEXT NOT NULL,
    basis TEXT,
    session_flags_json TEXT NOT NULL,
    field_trust_json TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class DiffEvent:
    diff_id: str
    ai_proposal: dict[str, Any]
    expert_fix: dict[str, Any]
    item_ids: tuple[str, ...]
    basis: str | None
    session_dirty: bool
    field_trust: dict[str, str]


def ensure_l0_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(L0_DDL)


def capture_diff_event(
        conn: sqlite3.Connection,
        *,
        ai_proposal: dict[str, Any],
        expert_fix: dict[str, Any],
        item_ids: Sequence[str],
        basis: str | None = None,
        session_read_untrusted: bool = False,
) -> DiffEvent:
    """Store L0. ai_proposal fields tagged untrusted when session was dirty."""
    ensure_l0_schema(conn)
    field_trust = {
        "expert_fix": "trusted",
        "item_ids": "structural",
        "basis": "trusted" if basis else "absent",
        "ai_proposal": (
            "untrusted" if session_read_untrusted else "model_clean"
        ),
    }
    diff_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    flags = {
        "session_read_untrusted": bool(session_read_untrusted),
        "l1_allowed": False,  # atoms dark until gate + promote
    }
    conn.execute(
        "INSERT INTO diff_events ("
        "diff_id, ts, ai_proposal_json, expert_fix_json, item_ids_json, "
        "basis, session_flags_json, field_trust_json) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            diff_id, ts,
            json.dumps(ai_proposal, ensure_ascii=False),
            json.dumps(expert_fix, ensure_ascii=False),
            json.dumps(list(item_ids)),
            basis,
            json.dumps(flags),
            json.dumps(field_trust),
        ),
    )
    return DiffEvent(
        diff_id=diff_id,
        ai_proposal=ai_proposal,
        expert_fix=expert_fix,
        item_ids=tuple(item_ids),
        basis=basis,
        session_dirty=bool(session_read_untrusted),
        field_trust=field_trust,
    )


def few_shot_index(conn: sqlite3.Connection, *, limit: int = 5) -> list[dict]:
    """INDEX cards for few-shot — trusted expert_fix only, never raw proposal."""
    ensure_l0_schema(conn)
    out = []
    for row in conn.execute(
        "SELECT diff_id, expert_fix_json, item_ids_json, field_trust_json "
        "FROM diff_events ORDER BY ts DESC LIMIT ?",
        (limit,),
    ):
        trust = json.loads(row["field_trust_json"] or "{}")
        out.append({
            "diff_id": row["diff_id"],
            "expert_fix_summary": json.loads(row["expert_fix_json"]),
            "item_ids": json.loads(row["item_ids_json"] or "[]"),
            "ai_proposal_injected": False,
            "field_trust": trust,
        })
    return out
