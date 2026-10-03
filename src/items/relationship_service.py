"""Canonical relationship approval, supersession, and surface projections.

State machine (only transitions allowed through this module):

  proposed  → approved | rejected
  approved  → superseded
  approved|rejected → proposed   (undo; history stays append-only)

Decision rows are immutable and bind relationship_id, evidence IDs, item
content versions, actor/session, timestamp, and approval_hash. Direct SQL
state changes are prohibited — callers must use the functions here.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Iterable, Sequence

from items.schema import create_items_schema

POLARITY_ACCEPT = "accept"
POLARITY_REJECT = "reject"
POLARITY_UNDO = "undo"
POLARITY_SUPERSEDE = "supersede"
POLARITY_MIGRATE = "migrate"

STATE_PROPOSED = "proposed"
STATE_APPROVED = "approved"
STATE_REJECTED = "rejected"
STATE_SUPERSEDED = "superseded"

SURFACES = frozenset({
    "graph", "board", "deadline", "nudge", "list_related",
})

DRAWABLE_WITNESSED = frozenset({"duplicate-of", "attached-to", "version-of"})
BOARD_CONFIDENCE = frozenset({"witnessed", "declared", "corroborated"})
CANCELLED_STATUSES = frozenset({"cancelled", "canceled", "declined"})

SYSTEM_ACTOR = "system"
SYSTEM_SESSION = "system"


class UnknownRelationship(LookupError):
    """No live relationship row for that id."""


class InvalidTransition(ValueError):
    """Requested state change is not allowed by the machine."""


def accept_link(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        user_id: str,
        session_id: str | None = None,
) -> dict:
    """proposed → approved. Records an immutable decision with approval_hash."""
    return _decide(
        conn, relationship_id,
        polarity=POLARITY_ACCEPT,
        new_state=STATE_APPROVED,
        user_id=user_id,
        session_id=session_id,
        allowed_from={STATE_PROPOSED},
    )


def reject_link(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        user_id: str,
        session_id: str | None = None,
) -> dict:
    """proposed → rejected."""
    return _decide(
        conn, relationship_id,
        polarity=POLARITY_REJECT,
        new_state=STATE_REJECTED,
        user_id=user_id,
        session_id=session_id,
        allowed_from={STATE_PROPOSED},
    )


def undo_link(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        user_id: str,
        session_id: str | None = None,
) -> dict:
    """approved|rejected → proposed. Prior decision rows remain."""
    create_items_schema(conn)
    if not user_id:
        raise ValueError("user_id is required for a link decision")
    row = _live(conn, relationship_id)
    latest = _latest_polarity(conn, row["basis_key"])
    if latest is None:
        raise UnknownRelationship(
            f"nothing to undo for relationship {relationship_id!r}")
    if row["state"] not in (STATE_APPROVED, STATE_REJECTED):
        raise InvalidTransition(
            f"cannot undo from state {row['state']!r}")
    return _record_and_set(
        conn, row,
        polarity=POLARITY_UNDO,
        new_state=STATE_PROPOSED,
        user_id=user_id,
        session_id=session_id or user_id,
    )


def accept_links(
        conn: sqlite3.Connection,
        relationship_ids: Sequence[str],
        *,
        user_id: str,
        session_id: str | None = None,
) -> list[dict]:
    """Bulk accept. Enumerates every id; empty list is refused."""
    if not relationship_ids:
        raise ValueError("bulk accept enumerates every member; empty refused")
    return [
        accept_link(conn, rid, user_id=user_id, session_id=session_id)
        for rid in relationship_ids
    ]


def reject_links(
        conn: sqlite3.Connection,
        relationship_ids: Sequence[str],
        *,
        user_id: str,
        session_id: str | None = None,
) -> list[dict]:
    """Bulk reject. Enumerates every id; empty list is refused."""
    if not relationship_ids:
        raise ValueError("bulk reject enumerates every member; empty refused")
    return [
        reject_link(conn, rid, user_id=user_id, session_id=session_id)
        for rid in relationship_ids
    ]


def supersede_relationship(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        reason: str,
        user_id: str = SYSTEM_ACTOR,
        session_id: str = SYSTEM_SESSION,
) -> dict | None:
    """approved (or proposed) → superseded. No-op if already superseded."""
    create_items_schema(conn)
    row = conn.execute(
        "SELECT * FROM relationships WHERE relationship_id = ?",
        (relationship_id,),
    ).fetchone()
    if row is None:
        raise UnknownRelationship(relationship_id)
    if row["superseded_by"] is not None or row["state"] == STATE_SUPERSEDED:
        return None
    if row["state"] == STATE_REJECTED:
        # Keep rejection as the live polarity for basis_is_rejected.
        return None
    marker = f"supersede:{reason}:{uuid.uuid4()}"
    return _record_and_set(
        conn, row,
        polarity=POLARITY_SUPERSEDE,
        new_state=STATE_SUPERSEDED,
        user_id=user_id,
        session_id=session_id,
        superseded_by=marker,
        extra_evidence=[f"reason:{reason}"],
    )


def revalidate_for_item_version(
        conn: sqlite3.Connection,
        item_id: str,
        *,
        content_hash: str | None = None,
) -> list[str]:
    """Supersede live relationships whose evidence depended on a prior version.

    Approved links whose bound content versions no longer match are superseded.
    Proposed links involving the item are superseded so projectors can rebuild.
    Rejected links stay (basis suppression).
    """
    create_items_schema(conn)
    live = conn.execute(
        "SELECT * FROM relationships WHERE superseded_by IS NULL "
        "AND (from_item_id = ? OR to_item_id = ?)",
        (item_id, item_id),
    ).fetchall()
    superseded: list[str] = []
    current = _item_content_versions(conn, [
        r["from_item_id"] for r in live
    ] + [r["to_item_id"] for r in live] + [item_id])
    if content_hash is not None:
        current[item_id] = content_hash
    for row in live:
        if row["state"] == STATE_REJECTED:
            continue
        if row["state"] == STATE_APPROVED:
            bound = _bound_versions(conn, row["relationship_id"])
            if bound and _versions_still_match(bound, current, row):
                continue
            reason = "item_version_change"
        else:
            reason = "item_version_revalidate"
        result = supersede_relationship(
            conn, row["relationship_id"], reason=reason)
        if result is not None:
            superseded.append(row["relationship_id"])
    return superseded


def migrate_person_relationships(
        conn: sqlite3.Connection,
        *,
        keep_id: str,
        drop_id: str,
        user_id: str = SYSTEM_ACTOR,
        session_id: str = SYSTEM_SESSION,
) -> dict:
    """Rewrite live relationships and append migration decision provenance.

    Runs inside the caller's transaction. Does not commit.
    """
    create_items_schema(conn)
    if keep_id == drop_id:
        raise ValueError("cannot migrate person to itself")
    touched = conn.execute(
        "SELECT * FROM relationships WHERE superseded_by IS NULL "
        "AND (from_item_id = ? OR to_item_id = ?)",
        (drop_id, drop_id),
    ).fetchall()
    migrated: list[str] = []
    for row in touched:
        new_from = keep_id if row["from_item_id"] == drop_id else row["from_item_id"]
        new_to = keep_id if row["to_item_id"] == drop_id else row["to_item_id"]
        if new_from == new_to:
            supersede_relationship(
                conn, row["relationship_id"],
                reason="person_merge_self_loop",
                user_id=user_id, session_id=session_id,
            )
            continue
        conn.execute(
            "UPDATE relationships SET from_item_id = ?, to_item_id = ? "
            "WHERE relationship_id = ?",
            (new_from, new_to, row["relationship_id"]),
        )
        # Append-only provenance that the endpoints moved keep←drop.
        _record_decision(
            conn,
            basis_key=row["basis_key"],
            polarity=POLARITY_MIGRATE,
            relationship_id=row["relationship_id"],
            user_id=user_id,
            session_id=session_id,
            evidence_ids=_parse_json_list(row["evidence_refs"]) + [
                f"merge:{drop_id}->{keep_id}",
            ],
            item_content_versions=_item_content_versions(
                conn, [new_from, new_to]),
        )
        migrated.append(row["relationship_id"])
    # Decision rows themselves stay; relationship_id is stable. Record a
    # person-level migration marker for audit.
    return {
        "keep_id": keep_id,
        "drop_id": drop_id,
        "migrated_relationship_ids": migrated,
        "count": len(migrated),
    }


def basis_is_rejected(conn: sqlite3.Connection, basis_key: str) -> bool:
    """True when the newest polarity for this basis is reject."""
    return _latest_polarity(conn, basis_key) == POLARITY_REJECT


def live_relationships(
        conn: sqlite3.Connection,
        *,
        item_id: str | None = None,
) -> list[dict]:
    """All non-superseded relationship rows (raw canonical inventory)."""
    create_items_schema(conn)
    if item_id is None:
        rows = conn.execute(
            "SELECT * FROM relationships WHERE superseded_by IS NULL "
            "AND state != ? ORDER BY created_at, rowid",
            (STATE_SUPERSEDED,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM relationships WHERE superseded_by IS NULL "
            "AND state != ? AND (from_item_id = ? OR to_item_id = ?) "
            "ORDER BY created_at, rowid",
            (STATE_SUPERSEDED, item_id, item_id),
        ).fetchall()
    return [_as_dict(r) for r in rows]


def project_relationships(
        conn: sqlite3.Connection,
        *,
        surface: str,
        item_id: str | None = None,
        rel_type: str | None = None,
) -> list[dict]:
    """One projection helper for Graph, Board, deadlines, nudges, list_related.

    Surfaces share the same live inventory and apply surface-specific filters:
    inferred stay hidden until approved; rejected/superseded never drawn.
    """
    if surface not in SURFACES:
        raise ValueError(f"unknown surface {surface!r}")
    edges = live_relationships(conn, item_id=item_id)
    out: list[dict] = []
    for edge in edges:
        if rel_type is not None and edge["rel_type"] != rel_type:
            continue
        if _visible_on_surface(edge, surface):
            out.append(edge)
    return out


def projection_hidden_count(
        conn: sqlite3.Connection,
        *,
        surface: str = "graph",
        item_id: str | None = None,
        among: Iterable[str] | None = None,
) -> int:
    """Count live edges that exist but are not drawn on `surface`."""
    edges = live_relationships(conn, item_id=item_id)
    allowed = None if among is None else set(among)
    hidden = 0
    for edge in edges:
        if allowed is not None:
            if (edge["from_item_id"] not in allowed
                    or edge["to_item_id"] not in allowed):
                continue
        if not _visible_on_surface(edge, surface):
            hidden += 1
    return hidden


def _visible_on_surface(edge: dict, surface: str) -> bool:
    state = edge["state"]
    confidence = edge["confidence"]
    rel_type = edge["rel_type"]
    if state in (STATE_REJECTED, STATE_SUPERSEDED):
        return False
    if surface == "list_related":
        if state == STATE_APPROVED:
            return True
        return confidence == "witnessed" and state == STATE_PROPOSED
    if surface == "graph":
        if confidence == "inferred" and state != STATE_APPROVED:
            return False
        if state == STATE_APPROVED:
            return True
        return (
            confidence == "witnessed"
            and rel_type in DRAWABLE_WITNESSED
            and state == STATE_PROPOSED
        )
    if surface == "board":
        if rel_type != "member-of":
            return False
        if state not in (STATE_APPROVED, STATE_PROPOSED):
            return False
        return confidence in BOARD_CONFIDENCE
    if surface == "deadline":
        if confidence == "inferred" or state == "inferred":
            return False
        return confidence == "witnessed" or state in (
            "witnessed", STATE_APPROVED)
    if surface == "nudge":
        if confidence == "inferred" and state != STATE_APPROVED:
            return False
        return confidence == "witnessed" or state == STATE_APPROVED
    return False


def _decide(
        conn: sqlite3.Connection,
        relationship_id: str,
        *,
        polarity: str,
        new_state: str,
        user_id: str,
        session_id: str | None,
        allowed_from: set[str],
) -> dict:
    create_items_schema(conn)
    if not user_id:
        raise ValueError("user_id is required for a link decision")
    row = _live(conn, relationship_id)
    if row["state"] not in allowed_from:
        raise InvalidTransition(
            f"cannot {polarity} from state {row['state']!r}; "
            f"allowed {sorted(allowed_from)}")
    return _record_and_set(
        conn, row,
        polarity=polarity,
        new_state=new_state,
        user_id=user_id,
        session_id=session_id or user_id,
    )


def _record_and_set(
        conn: sqlite3.Connection,
        row: sqlite3.Row,
        *,
        polarity: str,
        new_state: str,
        user_id: str,
        session_id: str,
        superseded_by: str | None = None,
        extra_evidence: list[str] | None = None,
) -> dict:
    evidence = _parse_json_list(row["evidence_refs"])
    if extra_evidence:
        evidence = list(evidence) + list(extra_evidence)
    versions = _item_content_versions(
        conn, [row["from_item_id"], row["to_item_id"]])
    now = _now()
    decision = _record_decision(
        conn,
        basis_key=row["basis_key"],
        polarity=polarity,
        relationship_id=row["relationship_id"],
        user_id=user_id,
        session_id=session_id,
        evidence_ids=evidence,
        item_content_versions=versions,
        created_at=now,
    )
    if superseded_by is not None:
        conn.execute(
            "UPDATE relationships SET state = ?, superseded_by = ? "
            "WHERE relationship_id = ?",
            (new_state, superseded_by, row["relationship_id"]),
        )
    else:
        conn.execute(
            "UPDATE relationships SET state = ? WHERE relationship_id = ?",
            (new_state, row["relationship_id"]),
        )
    return {
        "relationship_id": row["relationship_id"],
        "state": new_state,
        "decision_id": decision["decision_id"],
        "approval_hash": decision["approval_hash"],
        "evidence_ids": decision["evidence_ids"],
        "item_content_versions": decision["item_content_versions"],
        "session_id": session_id,
        "user_id": user_id,
        "created_at": now,
        "polarity": polarity,
    }


def _record_decision(
        conn: sqlite3.Connection,
        *,
        basis_key: str,
        polarity: str,
        relationship_id: str,
        user_id: str,
        session_id: str,
        evidence_ids: list[str],
        item_content_versions: dict[str, str],
        created_at: str | None = None,
) -> dict:
    now = created_at or _now()
    approval_hash = compute_approval_hash(
        relationship_id=relationship_id,
        evidence_ids=evidence_ids,
        item_content_versions=item_content_versions,
        user_id=user_id,
        session_id=session_id,
        created_at=now,
        polarity=polarity,
    )
    decision_id = str(uuid.uuid4())
    evidence_json = json.dumps(list(evidence_ids), sort_keys=True)
    versions_json = json.dumps(item_content_versions, sort_keys=True)
    conn.execute(
        "INSERT INTO relationship_decisions ("
        "decision_id, basis_key, polarity, relationship_id, user_id, "
        "created_at, evidence_ids, item_content_versions, session_id, "
        "approval_hash"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            decision_id, basis_key, polarity, relationship_id, user_id, now,
            evidence_json, versions_json, session_id, approval_hash,
        ),
    )
    return {
        "decision_id": decision_id,
        "approval_hash": approval_hash,
        "evidence_ids": list(evidence_ids),
        "item_content_versions": dict(item_content_versions),
        "created_at": now,
    }


def compute_approval_hash(
        *,
        relationship_id: str,
        evidence_ids: Sequence[str],
        item_content_versions: dict[str, str],
        user_id: str,
        session_id: str,
        created_at: str,
        polarity: str,
) -> str:
    payload = json.dumps(
        {
            "relationship_id": relationship_id,
            "evidence_ids": list(evidence_ids),
            "item_content_versions": item_content_versions,
            "user_id": user_id,
            "session_id": session_id,
            "created_at": created_at,
            "polarity": polarity,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _live(conn: sqlite3.Connection, relationship_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM relationships WHERE relationship_id = ? "
        "AND superseded_by IS NULL AND state != ?",
        (relationship_id, STATE_SUPERSEDED),
    ).fetchone()
    if row is None:
        raise UnknownRelationship(relationship_id)
    return row


def _latest_polarity(conn: sqlite3.Connection, basis_key: str) -> str | None:
    if not _decisions_installed(conn):
        return None
    row = conn.execute(
        "SELECT polarity FROM relationship_decisions WHERE basis_key = ? "
        "ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (basis_key,),
    ).fetchone()
    return None if row is None else row["polarity"]


def _decisions_installed(conn: sqlite3.Connection) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' "
        "AND name = 'relationship_decisions'"
    ).fetchone() is not None


def _item_content_versions(
        conn: sqlite3.Connection, item_ids: Sequence[str],
) -> dict[str, str]:
    out: dict[str, str] = {}
    for item_id in sorted({i for i in item_ids if i}):
        row = conn.execute(
            "SELECT content_hash, file_id FROM items WHERE item_id = ?",
            (item_id,),
        ).fetchone()
        if row is None:
            out[item_id] = ""
            continue
        digest = row["content_hash"]
        if not digest and row["file_id"]:
            try:
                file_row = conn.execute(
                    "SELECT content_hash FROM files WHERE file_id = ?",
                    (row["file_id"],),
                ).fetchone()
            except sqlite3.OperationalError:
                file_row = None
            digest = None if file_row is None else file_row["content_hash"]
        out[item_id] = digest or ""
    return out


def _bound_versions(
        conn: sqlite3.Connection, relationship_id: str,
) -> dict[str, str] | None:
    row = conn.execute(
        "SELECT item_content_versions FROM relationship_decisions "
        "WHERE relationship_id = ? AND polarity = ? "
        "ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (relationship_id, POLARITY_ACCEPT),
    ).fetchone()
    if row is None or not row["item_content_versions"]:
        return None
    try:
        data = json.loads(row["item_content_versions"])
    except (TypeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _versions_still_match(
        bound: dict[str, str], current: dict[str, str], row: sqlite3.Row,
) -> bool:
    for item_id in (row["from_item_id"], row["to_item_id"]):
        if bound.get(item_id, "") != current.get(item_id, ""):
            return False
    return True


def _parse_json_list(raw) -> list[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return [str(raw)]
    if isinstance(data, list):
        return [str(x) for x in data]
    return [str(data)]


def _as_dict(row: sqlite3.Row) -> dict:
    return {key: row[key] for key in row.keys()}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
