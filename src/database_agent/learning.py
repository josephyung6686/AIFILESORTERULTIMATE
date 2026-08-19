"""Contract out §7 — the §8.7 learning-record store.

A scoped projection over `events`, not a new authority and not a second log.
P1 does not learn: no weighting, no generalization, no ranking, no application.
What a record means is decided by the part that authored the correction.

The three opaque fields — polarity, proposal_class, basis_key — are stored and
returned unchanged. P1 derives none of them from the event type or the
explanation, and filters on none of them. Suppressing a proposal is the acting
part's rule, applied in that part.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from database_agent.events import append_event

#: §8.7's six scopes, in the spelling `events.correction_scope` and P13's
#: `review_action.correction_scope` both use. "destination node" is the same scope
#: written out in prose; it is not a second value.
SCOPES: tuple[str, ...] = ("file", "group", "node", "template", "domain", "corpus")

#: The event P13 authors when it routes a collected gesture (P13 SPEC, Provenance).
#: A reset arrives as review_action with surface = learning, action = reset_learning.
_ROUTED = "review action routed"


def _check(scope: str) -> None:
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope!r}; §8.7 defines exactly {SCOPES}")


def reset_cutoff(conn: sqlite3.Connection, scope: str, subject_id: str) -> int | None:
    """The newest reset at this scope and subject, as an event_id, or None."""
    _check(scope)
    row = conn.execute(
        "SELECT MAX(event_id) AS cutoff FROM learning_resets "
        "WHERE scope = ? AND subject_id = ?",
        (scope, subject_id),
    ).fetchone()
    return None if row is None else row["cutoff"]


def learning_records(conn: sqlite3.Connection, scope: str,
                     subject_id: str) -> list[sqlite3.Row]:
    """User-action events at that scope for that subject, newest first, each with
    its §8.2 explanation, polarity, proposal_class and basis_key.

    Scope is the filter and it is exact. The subject is `correction_subject`, not
    `file_id`: five of §8.7's six scopes have no file. A reset at this scope and
    subject is honoured as a cutoff — records before it are not returned, and none
    of them is deleted (R6).
    """
    _check(scope)
    cutoff = reset_cutoff(conn, scope, subject_id) or 0
    return conn.execute(
        "SELECT * FROM events WHERE correction_scope = ? AND correction_subject = ? "
        "AND user_id IS NOT NULL AND event_id > ? ORDER BY event_id DESC",
        (scope, subject_id, cutoff),
    ).fetchall()


def reset_preferences(conn: sqlite3.Connection, scope: str, subject_id: str, *,
                      author: str, component_version: str, user_id: str) -> int:
    """Append a scoped reset and record the cutoff it establishes. Deletes nothing (R6).

    P1 mints no event type for this. P13 collects the gesture as `review_action`
    with surface = learning and action = reset_learning and routes it here; the
    event it authors is its registered `review action routed`, so `author` is the
    routing part and lands in `subsystem` (M8).
    """
    _check(scope)
    now = datetime.now(timezone.utc).isoformat()
    event_id = append_event(
        conn, event_type=_ROUTED, subsystem=author,
        component_version=component_version, observed_at=now,
        explanation=f"learning preferences reset at scope {scope}",
        correction_scope=scope, correction_subject=subject_id, user_id=user_id,
    )
    conn.execute(
        "INSERT INTO learning_resets (scope, subject_id, event_id, reset_at) "
        "VALUES (?, ?, ?, ?)",
        (scope, subject_id, event_id, now),
    )
    return event_id
