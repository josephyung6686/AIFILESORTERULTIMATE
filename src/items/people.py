"""Person items + address aliases + merge precision (P5).

People are first-class items. Aliases (email addresses) never auto-become
folder destinations. Merge requires human confirm; precision helpers score
blocking-key proposals only.
"""
from __future__ import annotations

import re
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from items.schema import create_items_schema

PEOPLE_DDL = """
CREATE TABLE IF NOT EXISTS person_aliases (
    alias_id TEXT PRIMARY KEY,
    person_item_id TEXT NOT NULL,
    alias_type TEXT NOT NULL,
    alias_value TEXT NOT NULL,
    created_at TEXT NOT NULL,
    superseded_by TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS person_aliases_live_value
    ON person_aliases(alias_type, alias_value)
    WHERE superseded_by IS NULL;
CREATE INDEX IF NOT EXISTS person_aliases_by_person
    ON person_aliases(person_item_id);
"""

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class PersonItem:
    item_id: str
    display_label: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class MergeCandidate:
    left_id: str
    right_id: str
    blocking_key: str
    score: float
    reason: str


def ensure_people_schema(conn: sqlite3.Connection) -> None:
    create_items_schema(conn)
    conn.executescript(PEOPLE_DDL)


def mint_person(
        conn: sqlite3.Connection,
        *,
        display_label: str,
        email: str | None = None,
) -> PersonItem:
    """Create a person item; optional email alias (opt-in)."""
    ensure_people_schema(conn)
    label = (display_label or "").strip()
    if not label:
        raise ValueError("display_label required")
    if email is not None:
        email = email.strip().casefold()
        if not _EMAIL.match(email):
            raise ValueError(f"invalid email alias: {email!r}")
        existing = conn.execute(
            "SELECT person_item_id FROM person_aliases "
            "WHERE alias_type='email' AND alias_value=? "
            "AND superseded_by IS NULL",
            (email,),
        ).fetchone()
        if existing:
            return get_person(conn, existing["person_item_id"])

    item_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "external_key, presence, typing_state, type_schema, profile_id, "
        "created_at, superseded_by) VALUES ("
        "?,?,?,?,NULL,?,?, 'unplaced', NULL, NULL, ?, NULL)",
        (
            item_id, "person", label, None,
            f"person:{label.casefold()}", "live", ts,
        ),
    )
    aliases: list[str] = []
    if email:
        conn.execute(
            "INSERT INTO person_aliases ("
            "alias_id, person_item_id, alias_type, alias_value, created_at, "
            "superseded_by) VALUES (?,?,?,?,?,NULL)",
            (str(uuid.uuid4()), item_id, "email", email, ts),
        )
        aliases.append(email)
    return PersonItem(item_id=item_id, display_label=label, aliases=tuple(aliases))


def get_person(conn: sqlite3.Connection, item_id: str) -> PersonItem:
    ensure_people_schema(conn)
    row = conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE item_id=? AND item_type='person' AND presence='live' "
        "AND superseded_by IS NULL",
        (item_id,),
    ).fetchone()
    if row is None:
        raise KeyError(item_id)
    aliases = tuple(
        r["alias_value"] for r in conn.execute(
            "SELECT alias_value FROM person_aliases "
            "WHERE person_item_id=? AND superseded_by IS NULL "
            "ORDER BY alias_value",
            (item_id,),
        )
    )
    return PersonItem(
        item_id=row["item_id"], display_label=row["display_label"],
        aliases=aliases)


def add_alias(conn: sqlite3.Connection, person_item_id: str, email: str) -> None:
    ensure_people_schema(conn)
    email = email.strip().casefold()
    if not _EMAIL.match(email):
        raise ValueError(f"invalid email: {email!r}")
    ts = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO person_aliases ("
        "alias_id, person_item_id, alias_type, alias_value, created_at, "
        "superseded_by) VALUES (?,?,?,?,?,NULL)",
        (str(uuid.uuid4()), person_item_id, "email", email, ts),
    )


def merge_candidates(conn: sqlite3.Connection) -> list[MergeCandidate]:
    """Blocking-key proposals: same email alias domain+local OR same casefold label."""
    ensure_people_schema(conn)
    out: list[MergeCandidate] = []
    # Same normalized label
    rows = conn.execute(
        "SELECT item_id, display_label FROM items "
        "WHERE item_type='person' AND presence='live' AND superseded_by IS NULL"
    ).fetchall()
    by_label: dict[str, list[str]] = {}
    for r in rows:
        key = (r["display_label"] or "").casefold().strip()
        by_label.setdefault(key, []).append(r["item_id"])
    for key, ids in by_label.items():
        if len(ids) < 2 or not key:
            continue
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                out.append(MergeCandidate(
                    left_id=ids[i], right_id=ids[j],
                    blocking_key=f"label:{key}",
                    score=1.0,
                    reason="identical display_label casefold",
                ))
    # Same email local-part across different persons (weak)
    aliases = conn.execute(
        "SELECT person_item_id, alias_value FROM person_aliases "
        "WHERE alias_type='email' AND superseded_by IS NULL"
    ).fetchall()
    by_local: dict[str, list[tuple[str, str]]] = {}
    for a in aliases:
        local = a["alias_value"].split("@", 1)[0]
        by_local.setdefault(local, []).append(
            (a["person_item_id"], a["alias_value"]))
    for local, pairs in by_local.items():
        persons = {p for p, _ in pairs}
        if len(persons) < 2:
            continue
        ids = sorted(persons)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                out.append(MergeCandidate(
                    left_id=ids[i], right_id=ids[j],
                    blocking_key=f"email_local:{local}",
                    score=0.7,
                    reason="shared email local-part",
                ))
    # de-dupe pairs
    seen = set()
    uniq = []
    for c in out:
        key = tuple(sorted((c.left_id, c.right_id))) + (c.blocking_key,)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(c)
    return uniq


def merge_persons(
        conn: sqlite3.Connection,
        *,
        keep_id: str,
        drop_id: str,
        confirmed: bool = False,
        user_id: str = "local-user",
        session_id: str | None = None,
) -> PersonItem:
    """Merge drop into keep. Requires confirmed=True. Never auto.

    Relationships and decision provenance migrate transactionally via
    `relationship_service.migrate_person_relationships`.
    """
    if not confirmed:
        raise PermissionError("merge requires confirmed=True — nothing changed")
    if keep_id == drop_id:
        raise ValueError("cannot merge person with itself")
    ensure_people_schema(conn)
    keep = get_person(conn, keep_id)
    drop = get_person(conn, drop_id)
    # One transaction: aliases, relationship migration, person supersession.
    try:
        conn.execute("BEGIN")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute(
            "UPDATE person_aliases SET person_item_id=? "
            "WHERE person_item_id=? AND superseded_by IS NULL",
            (keep_id, drop_id),
        )
        from items.relationship_service import migrate_person_relationships
        migrate_person_relationships(
            conn, keep_id=keep_id, drop_id=drop_id,
            user_id=user_id, session_id=session_id or user_id,
        )
        conn.execute(
            "UPDATE items SET presence='missing', superseded_by=? WHERE item_id=?",
            (keep_id, drop_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    return get_person(conn, keep_id)


def merge_precision(
        candidates: list[MergeCandidate],
        gold_pairs: set[tuple[str, str]],
) -> dict[str, float]:
    """Precision of merge proposals against labeled pairs (unordered)."""
    if not candidates:
        return {"precision": 1.0, "n_pred": 0, "n_tp": 0}
    gold = {tuple(sorted(p)) for p in gold_pairs}
    pred = {tuple(sorted((c.left_id, c.right_id))) for c in candidates}
    tp = len(pred & gold)
    return {
        "precision": tp / len(pred) if pred else 1.0,
        "n_pred": float(len(pred)),
        "n_tp": float(tp),
    }
