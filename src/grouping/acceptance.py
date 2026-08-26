# src/grouping/acceptance.py
"""What a plan version has to say about a group. The only versioned P9 record.

M15. A group, its memberships, its dossier and its edges live in the shared
evidence database and survive every plan version. `group_acceptance` records the
opinion one version holds about them, and it is the only table in P9 carrying a
`plan_version_id`.

That is why `accepted` and `rejected` are not members of `GROUP_STATES`. They are
resolved AS OF a version through `group_state_as_of`, published as a call rather
than left to a consumer looking for `rejected` in an enum that does not contain
it -- a consumer that looks and does not find is a consumer about to invent one.

`pending-review` and `deferred` never become shared lifecycle states either. They
are things a plan version is doing, not things a group is.

Absence is not a state. `membership_review_state_as_of` raises rather than
reporting `pending-review` for a membership no writer has recorded: deriving one
from `Membership.basis` would manufacture a review nobody asked for, in a version
that never asked for it.
"""
from __future__ import annotations

import sqlite3

from database_agent.db import transaction

from grouping.records import GroupAcceptance
from grouping.store import RecordAbsent, current_group
from grouping.vocabulary import (
    ACCEPTED,
    PENDING_REVIEW,
    PLAN_VERSIONED_STATES,
    REJECTED,
    VALIDATOR,
)


class AcceptanceStateAbsent(LookupError):
    """No plan-version opinion is recorded. Not a state; the lack of one."""


def _link(conn: sqlite3.Connection, record: GroupAcceptance) -> None:
    if record.supersedes is None:
        return
    conn.execute(
        "UPDATE group_acceptance SET superseded_by = ?, supersede_reason = ? "
        "WHERE acceptance_id = ?",
        (record.acceptance_id, record.supersede_reason, record.supersedes),
    )


def record_acceptance(conn: sqlite3.Connection, record: GroupAcceptance) -> str:
    """Append one plan-version opinion, superseding the one it replaces.

    The unique index is over unsuperseded rows, so a second CURRENT opinion in one
    version about one group is refused by the database rather than by a check that
    could be forgotten -- two current answers to one question is the thing the
    index exists to prevent.
    """
    if record.supersedes is not None:
        if not record.supersede_reason:
            raise ValueError(
                "a supersession carries the reason for the change; without it a "
                "later reader has two rows and no account of why the second exists"
            )
        found = conn.execute(
            "SELECT acceptance_id FROM group_acceptance WHERE acceptance_id = ?",
            (record.supersedes,),
        ).fetchone()
        if found is None:
            raise AcceptanceStateAbsent(
                f"{record.supersedes!r} is not recorded; a revision of an opinion "
                "that does not exist supersedes nothing"
            )
    with transaction(conn):
        # Supersede first. The unique index is over unsuperseded rows, so linking
        # after the insert would mean two current opinions existed for the length
        # of one statement -- and the database would refuse the insert that was
        # about to resolve it.
        _link(conn, record)
        conn.execute(
            "INSERT INTO group_acceptance ("
            "acceptance_id, plan_version_id, group_id, membership_id, acceptance, "
            "review_state, user_edited_label, aliases, review_decision_ref, "
            "decided_by, created_at, supersedes, superseded_by, supersede_reason"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record.acceptance_id, record.plan_version_id, record.group_id,
                record.membership_id, record.acceptance, record.review_state,
                # The user's label lives here and nowhere else. `display_label`
                # keeps what the engine or the model proposed, because an
                # evaluation of the edit needs the thing that was edited.
                record.user_edited_label, _aliases(record.aliases),
                record.review_decision_ref, record.decided_by, record.created_at,
                record.supersedes, record.superseded_by, record.supersede_reason,
            ),
        )
    return record.acceptance_id


def _aliases(aliases: tuple[str, ...]) -> str:
    from evidence_shape.canonical import canonical_json

    return canonical_json(list(aliases))


def record_context_review_pending(
    conn: sqlite3.Connection,
    *,
    plan_version_id: str,
    group_id: str,
    membership_id: str,
    created_at: str,
) -> str:
    """Materialise the row `membership_review_state_as_of` will read.

    Called inside the membership-write transaction. It exists so that the accessor
    never has to infer a pending review: the state a reader sees is one a writer
    put there, in the plan version that introduced the proposal.
    """
    return record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"{plan_version_id}:{membership_id}:pending",
        plan_version_id=plan_version_id,
        group_id=group_id,
        membership_id=membership_id,
        acceptance=PENDING_REVIEW,
        review_state=PENDING_REVIEW,
        user_edited_label=None,
        aliases=(),
        review_decision_ref=None,
        decided_by=VALIDATOR,
        created_at=created_at,
    ))


def _current(
    conn: sqlite3.Connection, *, plan_version_id: str, group_id: str | None,
    membership_id: str | None,
) -> sqlite3.Row | None:
    if membership_id is not None:
        return conn.execute(
            "SELECT * FROM group_acceptance WHERE plan_version_id = ? "
            "AND membership_id = ? AND superseded_by IS NULL",
            (plan_version_id, membership_id),
        ).fetchone()
    return conn.execute(
        "SELECT * FROM group_acceptance WHERE plan_version_id = ? "
        "AND group_id = ? AND membership_id IS NULL AND superseded_by IS NULL",
        (plan_version_id, group_id),
    ).fetchone()


def group_state_as_of(
    conn: sqlite3.Connection, *, group_id: str, plan_version_id: str,
) -> str:
    """`accepted` or `rejected` when this version decided; otherwise the shared state.

    `pending-review` and `deferred` are plan opinions and never surface here: a
    version that is still deciding has not changed what the group IS, and
    returning either would put a value in `Group.state`'s place that
    `GROUP_STATES` does not contain.
    """
    row = _current(
        conn, plan_version_id=plan_version_id, group_id=group_id,
        membership_id=None)
    if row is not None and row["acceptance"] in PLAN_VERSIONED_STATES:
        return row["acceptance"]
    return current_group(conn, group_id).state


def membership_review_state_as_of(
    conn: sqlite3.Connection, *, membership_id: str, plan_version_id: str,
) -> str:
    """The recorded review state, or `AcceptanceStateAbsent`. No fallback.

    There is deliberately no basis-derived default. A `context-supported`
    membership does not imply a pending review, and inventing one would put a
    review in front of the user that no plan version asked for.
    """
    row = _current(
        conn, plan_version_id=plan_version_id, group_id=None,
        membership_id=membership_id)
    if row is None:
        raise AcceptanceStateAbsent(
            f"no acceptance row for membership {membership_id!r} in plan version "
            f"{plan_version_id!r}; a review state is something a writer recorded, "
            "not something a reader derives"
        )
    return row["review_state"]
