"""The §8.2 event types P12 authors and P1 writes. One writer each, one home.

*"Every movement action is visible afterward"* (`66` §19), so nothing in P12
ends without a row. This module exists because the three outcomes a person cares
about -- it moved, it broke, it was stopped -- are three different sentences and
`74` §5.2 makes them three different event types:

* `executed move` -- the file is at its destination.
* `failed move` -- the move was ATTEMPTED and did not complete. The disk filled,
  the destination vanished mid-write, the copy could not be confirmed.
* `refused move` -- nothing was attempted. The cause is a rule, not an error.

Keeping the writers apart is the point rather than an accident of layout: a
single `record_outcome(event_type=...)` would let any caller put a refusal under
`failed move`, and `database_agent/events.py:30-44` records the owner minting the
twentieth name precisely so that *"the plan was stopped from running"* and *"the
run broke"* stop being the same row. Each writer here checks its own vocabulary
and rejects the other's values, so the distinction is enforced at the writer and
not left to the caller's care.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from mutation.vocabulary import (
    EXECUTED_MOVE, FAILED_MOVE, FAILURE_CLASSES, REFUSED_MOVE, SUBSYSTEM,
    check, decline_message,
)


def record_executed_move(conn: sqlite3.Connection, *, file_id: str,
                         content_hash: str, source_path: str,
                         destination_path: str, observed_at: str,
                         component_version: str, user_id: str | None,
                         detail: Mapping[str, object]) -> int:
    """`executed move`: the file is at its destination and the hash confirmed it."""
    return append_event(
        conn, event_type=EXECUTED_MOVE, file_id=file_id,
        content_hash=content_hash, old_path=source_path,
        new_path=destination_path, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=observed_at,
        user_id=user_id, explanation=canonical_json(dict(detail)))


def record_failed_move(conn: sqlite3.Connection, *, failure_class: str,
                       file_id: str, content_hash: str, source_path: str,
                       destination_path: str | None, observed_at: str,
                       component_version: str, user_id: str | None,
                       detail: Mapping[str, object]) -> int:
    """`failed move`: an ATTEMPTED move that did not complete.

    `failure_class` is checked against `FAILURE_CLASSES` and nothing else. A
    refusal class handed here is rejected rather than written: `refused move`
    exists for that, and a refusal filed as a failure would tell the person the
    product broke when in fact it obeyed one of their own rules.
    """
    check(failure_class, FAILURE_CLASSES, name="failure class")
    return append_event(
        conn, event_type=FAILED_MOVE, file_id=file_id,
        content_hash=content_hash, old_path=source_path,
        new_path=destination_path, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=observed_at,
        user_id=user_id,
        explanation=canonical_json({
            "failure_class": failure_class,
            "message": decline_message(f"failed:{failure_class}"),
            **dict(detail)}))


def record_refused_move(conn: sqlite3.Connection, *, outcome: str,
                        file_id: str, content_hash: str,
                        source_path: str, destination_path: str | None,
                        observed_at: str, component_version: str,
                        user_id: str | None,
                        detail: Mapping[str, object]) -> int:
    """`refused move`: nothing was attempted, and a rule is why.

    `outcome` is a member of `DECLINABLE_OUTCOMES` -- one of Contract out §5's
    ten refusal classes, one of §8.3's five staleness triggers spelled
    `stale:<trigger>`, or one of the two pause reasons spelled
    `paused:<reason>`. `74` §3.3 makes all three families refusals of the same
    kind to the person: the move did not run, nothing was touched, and here is
    what you can do. `decline_message` supplies `66` §10's distinct sentence and
    RAISES on anything outside the table, so a refusal with no sentence for the
    person cannot be written at all.

    A FAILURE class handed here is rejected by that same lookup, because the
    failure table is keyed `failed:<class>` and a bare class is not in it. That
    is the guard in the other direction from `record_failed_move`'s: neither
    writer can be talked into the other's event.
    """
    return append_event(
        conn, event_type=REFUSED_MOVE, file_id=file_id,
        content_hash=content_hash, old_path=source_path,
        new_path=destination_path, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=observed_at,
        user_id=user_id,
        explanation=canonical_json({
            "outcome": outcome, "message": decline_message(outcome),
            **dict(detail)}))
