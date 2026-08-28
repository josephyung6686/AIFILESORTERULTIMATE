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

**"As of a version" is a question about LINEAGE, not about one id.** §8.8 makes a
plan version a versioned object with a predecessor, and P10 opens a NEW draft
version for every recorded edit -- a rename, a reorder, a moved branch. Resolved
by exact `plan_version_id` alone, the acceptance the user gave would name an
ancestor of the version being asked about and every later version would see none
of it: §5.12's "the user can change the visual organization without destroying
the underlying evidence" inverted, and §8.9's "organization to evolve without
destabilizing accepted structure" with it. So the accessors resolve the NEAREST
opinion along the version's own ancestry, and the shared `Group.state` is the
answer only when no version in that ancestry has spoken at all.

Nearest wins, and a version that HAS spoken ends the walk whatever it said. A
version holding `deferred` is a version still deciding; answering it with an
ancestor's `accepted` would overrule the live decision with the one it replaced.
And a version outside the ancestry inherits nothing -- an opinion does not leak
sideways into a plan it was never given in.
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


def _versions_are_recorded(conn: sqlite3.Connection) -> bool:
    """Is there a plan-version record in this database at all?

    A P9-only database is a real state, not a broken one: P9 runs before any tree
    is designed, and its own tests create P9's tables and no others. There, the
    ancestry of a version id is genuinely unknown, and the honest answer is that
    it has none -- which resolves to exactly the behaviour that held before this
    walk existed. Asked as a question rather than caught as an error, because
    catching `OperationalError` would also swallow a real one.
    """
    return conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' "
        "AND name = 'plan_versions'").fetchone() is not None


def _ancestry(conn: sqlite3.Connection, plan_version_id: str) -> tuple[str, ...]:
    """The versions this one descends from, nearest first.

    The one cross-part read P9 makes, and it is one column: `predecessor_id`, the
    plan version's own account of where it came from. P9 was handed the
    `plan_version_id` by whoever recorded the acceptance and stores it opaquely;
    resolving what "as of" means for that id requires the id's own definition, and
    §8.8 puts that definition -- and only that -- in `plan_versions`. Nothing here
    reads a node, a label or a shape.

    An ancestor is collected from the `predecessor_id` that named it, before its
    own row is looked up. `predecessor_id`'s foreign key normally makes that
    distinction invisible -- every ancestor has a row -- but it means a chain whose
    root is referenced and unrecorded still contributes its opinion instead of
    being dropped one link short of it.

    `seen` is not defensive. `predecessor_id` is a self-reference on one table with
    no cycle constraint, and a cycle would otherwise be an unkillable loop inside a
    read.
    """
    if not _versions_are_recorded(conn):
        return ()
    chain: list[str] = []
    seen = {plan_version_id}
    current = plan_version_id
    while True:
        row = conn.execute(
            "SELECT predecessor_id FROM plan_versions WHERE plan_version_id = ?",
            (current,)).fetchone()
        if row is None or row["predecessor_id"] is None:
            return tuple(chain)
        current = row["predecessor_id"]
        if current in seen:
            return tuple(chain)
        seen.add(current)
        chain.append(current)


def _nearest(
    conn: sqlite3.Connection, *, plan_version_id: str, group_id: str | None,
    membership_id: str | None,
) -> sqlite3.Row | None:
    """This version's own opinion, or the closest ancestor's, or none.

    The version's own row is checked first and ends the search whatever it holds.
    An ancestor's opinion is what the user decided about this group before the
    edit; it is inherited, never preferred.
    """
    row = _current(
        conn, plan_version_id=plan_version_id, group_id=group_id,
        membership_id=membership_id)
    if row is not None:
        return row
    for ancestor in _ancestry(conn, plan_version_id):
        row = _current(
            conn, plan_version_id=ancestor, group_id=group_id,
            membership_id=membership_id)
        if row is not None:
            return row
    return None


def group_state_as_of(
    conn: sqlite3.Connection, *, group_id: str, plan_version_id: str,
) -> str:
    """`accepted` or `rejected` when this version decided; otherwise the shared state.

    "This version decided" includes deciding in the version this one was drafted
    from, and the one before that. The user accepts a packet, then renames one
    folder; §8.8 mints a version for the rename and §5.12 says the rename must not
    destroy what they accepted. Resolved on the exact id alone, §6.8's group pass
    could not run against any tree the user had ever touched.

    `pending-review` and `deferred` are plan opinions and never surface here: a
    version that is still deciding has not changed what the group IS, and
    returning either would put a value in `Group.state`'s place that
    `GROUP_STATES` does not contain. They still END the search -- a version that
    deferred has an opinion, and it is not its predecessor's.
    """
    row = _nearest(
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

    It inherits along the ancestry for the same reason `group_state_as_of` does,
    and the cost of not doing so is larger here in both directions: an unanswered
    `pending-review` -- the obligation that keeps an uncertain member from being a
    silent decision -- would vanish at the first rename, and a review the user
    HAD answered would come back at every rename after it.

    Inheriting is still not deriving. The row returned is one a writer recorded,
    in a version this one descends from; a membership no version ever spoke about
    still raises.
    """
    row = _nearest(
        conn, plan_version_id=plan_version_id, group_id=None,
        membership_id=membership_id)
    if row is None:
        raise AcceptanceStateAbsent(
            f"no acceptance row for membership {membership_id!r} in plan version "
            f"{plan_version_id!r}; a review state is something a writer recorded, "
            "not something a reader derives"
        )
    return row["review_state"]
