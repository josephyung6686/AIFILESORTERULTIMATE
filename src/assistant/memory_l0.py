"""L0 DiffEvent capture with per-field provenance (Addendum A6).

v1 steering / atoms are dark. Dirty sessions write L0 only.
Captures reject, edit, accept-correction, relationship decision, and
plan correction with item versions + session trust flags.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

L0_DDL = """
CREATE TABLE IF NOT EXISTS diff_events (
    diff_id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    ai_proposal_json TEXT NOT NULL,
    expert_fix_json TEXT NOT NULL,
    item_ids_json TEXT NOT NULL,
    basis TEXT,
    session_flags_json TEXT NOT NULL,
    field_trust_json TEXT NOT NULL,
    item_versions_json TEXT NOT NULL DEFAULT '{}',
    kind TEXT
);
"""

# User-decision kinds that feed correction memory.
KIND_REJECT = "reject"
KIND_EDIT = "edit"
KIND_ACCEPT_CORRECTION = "accept_correction"
KIND_RELATIONSHIP = "relationship_decision"
KIND_PLAN_CORRECTION = "plan_correction"
CAPTURE_KINDS = frozenset({
    KIND_REJECT, KIND_EDIT, KIND_ACCEPT_CORRECTION,
    KIND_RELATIONSHIP, KIND_PLAN_CORRECTION,
})


@dataclass(frozen=True)
class DiffEvent:
    diff_id: str
    ai_proposal: dict[str, Any]
    expert_fix: dict[str, Any]
    item_ids: tuple[str, ...]
    basis: str | None
    session_dirty: bool
    field_trust: dict[str, str]
    item_versions: dict[str, str]
    kind: str | None = None


def ensure_l0_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(L0_DDL)
    cols = {
        row[1] for row in conn.execute("PRAGMA table_info(diff_events)")
    }
    if "item_versions_json" not in cols:
        conn.execute(
            "ALTER TABLE diff_events ADD COLUMN item_versions_json "
            "TEXT NOT NULL DEFAULT '{}'"
        )
    if "kind" not in cols:
        conn.execute("ALTER TABLE diff_events ADD COLUMN kind TEXT")


def resolve_item_versions(
        conn: sqlite3.Connection,
        item_ids: Sequence[str],
) -> dict[str, str]:
    """Best-effort content versions for item_ids at capture time."""
    out: dict[str, str] = {}
    for item_id in item_ids:
        if not item_id:
            continue
        try:
            row = conn.execute(
                "SELECT content_hash, file_id FROM items WHERE item_id = ?",
                (item_id,),
            ).fetchone()
        except sqlite3.OperationalError:
            continue
        if row is None:
            continue
        digest = row["content_hash"] if "content_hash" in row.keys() else None
        if not digest and row["file_id"]:
            try:
                frow = conn.execute(
                    "SELECT content_hash FROM files WHERE file_id = ?",
                    (row["file_id"],),
                ).fetchone()
            except sqlite3.OperationalError:
                frow = None
            digest = None if frow is None else frow["content_hash"]
        if digest:
            out[str(item_id)] = str(digest)
    return out


def get_diff_event(
        conn: sqlite3.Connection, diff_id: str,
) -> DiffEvent | None:
    ensure_l0_schema(conn)
    row = conn.execute(
        "SELECT * FROM diff_events WHERE diff_id = ?", (diff_id,),
    ).fetchone()
    if row is None:
        return None
    flags = json.loads(row["session_flags_json"] or "{}")
    versions_raw = row["item_versions_json"] if "item_versions_json" in row.keys() else "{}"
    return DiffEvent(
        diff_id=row["diff_id"],
        ai_proposal=json.loads(row["ai_proposal_json"]),
        expert_fix=json.loads(row["expert_fix_json"]),
        item_ids=tuple(json.loads(row["item_ids_json"] or "[]")),
        basis=row["basis"],
        session_dirty=bool(flags.get("session_read_untrusted")),
        field_trust=json.loads(row["field_trust_json"] or "{}"),
        item_versions=json.loads(versions_raw or "{}"),
        kind=row["kind"] if "kind" in row.keys() else None,
    )


def source_ids_resolvable(
        conn: sqlite3.Connection,
        source_ids: Sequence[str],
) -> tuple[bool, str]:
    """True when every source_id is a live DiffEvent with matching versions."""
    ensure_l0_schema(conn)
    if not source_ids:
        return False, "source_ids required"
    for sid in source_ids:
        ev = get_diff_event(conn, sid)
        if ev is None:
            return False, f"orphan source_id {sid!r} — no DiffEvent"
        if ev.session_dirty:
            return False, f"dirty session DiffEvent {sid!r} cannot back an atom"
        if ev.item_versions:
            current = resolve_item_versions(conn, list(ev.item_versions))
            for item_id, captured in ev.item_versions.items():
                now = current.get(item_id)
                if now is not None and now != captured:
                    return (
                        False,
                        f"item {item_id!r} version changed "
                        f"(captured={captured[:12]}… now={now[:12]}…)",
                    )
    return True, ""


def capture_diff_event(
        conn: sqlite3.Connection,
        *,
        ai_proposal: dict[str, Any],
        expert_fix: dict[str, Any],
        item_ids: Sequence[str],
        basis: str | None = None,
        session_read_untrusted: bool = False,
        item_versions: Mapping[str, str] | None = None,
        kind: str | None = None,
) -> DiffEvent:
    """Store L0. ai_proposal fields tagged untrusted when session was dirty."""
    ensure_l0_schema(conn)
    if kind is not None and kind not in CAPTURE_KINDS:
        raise ValueError(f"unknown capture kind {kind!r}")
    versions = dict(item_versions) if item_versions is not None else (
        resolve_item_versions(conn, item_ids)
    )
    field_trust = {
        "expert_fix": "trusted",
        "item_ids": "structural",
        "basis": "trusted" if basis else "absent",
        "ai_proposal": (
            "untrusted" if session_read_untrusted else "model_clean"
        ),
        "item_versions": "structural" if versions else "absent",
    }
    diff_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    flags = {
        "session_read_untrusted": bool(session_read_untrusted),
        "l1_allowed": False,  # atoms dark until gate + release
    }
    conn.execute(
        "INSERT INTO diff_events ("
        "diff_id, ts, ai_proposal_json, expert_fix_json, item_ids_json, "
        "basis, session_flags_json, field_trust_json, item_versions_json, kind) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            diff_id, ts,
            json.dumps(ai_proposal, ensure_ascii=False),
            json.dumps(expert_fix, ensure_ascii=False),
            json.dumps(list(item_ids)),
            basis,
            json.dumps(flags),
            json.dumps(field_trust),
            json.dumps(versions, sort_keys=True),
            kind,
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
        item_versions=versions,
        kind=kind,
    )


def capture_relationship_decision(
        conn: sqlite3.Connection,
        *,
        relationship_id: str,
        polarity: str,
        item_ids: Sequence[str],
        item_versions: Mapping[str, str] | None = None,
        user_id: str = "local-user",
        session_read_untrusted: bool = False,
        ai_proposal: dict[str, Any] | None = None,
) -> DiffEvent:
    """DiffEvent for accept/reject link decisions."""
    return capture_diff_event(
        conn,
        ai_proposal=ai_proposal or {
            "action": "propose_link",
            "relationship_id": relationship_id,
        },
        expert_fix={
            "action": f"{polarity}_link",
            "relationship_id": relationship_id,
            "user_id": user_id,
            "polarity": polarity,
        },
        item_ids=list(item_ids),
        basis=f"relationship:{polarity}",
        session_read_untrusted=session_read_untrusted,
        item_versions=item_versions,
        kind=KIND_RELATIONSHIP,
    )


def capture_plan_correction(
        conn: sqlite3.Connection,
        *,
        plan_id: str,
        ai_proposal: dict[str, Any],
        expert_fix: dict[str, Any],
        item_ids: Sequence[str],
        item_versions: Mapping[str, str] | None = None,
        session_read_untrusted: bool = False,
        basis: str = "plan_correction",
) -> DiffEvent:
    return capture_diff_event(
        conn,
        ai_proposal=ai_proposal,
        expert_fix={**expert_fix, "plan_id": plan_id},
        item_ids=list(item_ids),
        basis=basis,
        session_read_untrusted=session_read_untrusted,
        item_versions=item_versions,
        kind=KIND_PLAN_CORRECTION,
    )


def capture_reject(
        conn: sqlite3.Connection,
        *,
        ai_proposal: dict[str, Any],
        expert_fix: dict[str, Any] | None = None,
        item_ids: Sequence[str],
        item_versions: Mapping[str, str] | None = None,
        session_read_untrusted: bool = False,
        reason: str | None = None,
) -> DiffEvent:
    return capture_diff_event(
        conn,
        ai_proposal=ai_proposal,
        expert_fix=expert_fix or {
            "action": "reject",
            "reason": reason or "user_reject",
        },
        item_ids=list(item_ids),
        basis="user_reject",
        session_read_untrusted=session_read_untrusted,
        item_versions=item_versions,
        kind=KIND_REJECT,
    )


def capture_edit(
        conn: sqlite3.Connection,
        *,
        ai_proposal: dict[str, Any],
        expert_fix: dict[str, Any],
        item_ids: Sequence[str],
        item_versions: Mapping[str, str] | None = None,
        session_read_untrusted: bool = False,
) -> DiffEvent:
    return capture_diff_event(
        conn,
        ai_proposal=ai_proposal,
        expert_fix=expert_fix,
        item_ids=list(item_ids),
        basis="user_edit",
        session_read_untrusted=session_read_untrusted,
        item_versions=item_versions,
        kind=KIND_EDIT,
    )


def capture_accept_correction(
        conn: sqlite3.Connection,
        *,
        ai_proposal: dict[str, Any],
        expert_fix: dict[str, Any] | None = None,
        item_ids: Sequence[str],
        item_versions: Mapping[str, str] | None = None,
        session_read_untrusted: bool = False,
) -> DiffEvent:
    return capture_diff_event(
        conn,
        ai_proposal=ai_proposal,
        expert_fix=expert_fix or {
            "action": "accept_correction",
            "accepted": True,
        },
        item_ids=list(item_ids),
        basis="accept_correction",
        session_read_untrusted=session_read_untrusted,
        item_versions=item_versions,
        kind=KIND_ACCEPT_CORRECTION,
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
