"""Append and read P13's own three tables. No update path exists anywhere here.

P13 owns no supersedable record: it never edits a decision, plan, verdict, fact
or observation. So there is no `supersede`, no `mark_superseded` and no
`current_*`. A later gesture is a later row, and the prior one stays inspectable
-- which is what makes §8.2's "a superseded record is shown AS superseded,
alongside the record that replaced it" possible for the parts that DO own
supersedable records.
"""
from __future__ import annotations

import json
import sqlite3

from review_surface.records import ReviewAction, ReviewApproval


def presentation_exists(conn: sqlite3.Connection, presented_state_ref: str) -> bool:
    """Whether a `review presentation` was recorded under this reference.

    A read of P13's own table. The WRITER is `review_surface.presentation`, which
    is a later task; this is the half `collect` needs, and it is here rather than
    there so that the refusal does not wait on a module it only reads from.
    """
    row = conn.execute(
        "SELECT presented_state_ref FROM review_presentations "
        "WHERE presented_state_ref = ?", (presented_state_ref,)).fetchone()
    return row is not None


def record_action(conn: sqlite3.Connection, action: ReviewAction) -> None:
    conn.execute(
        "INSERT INTO review_actions "
        "(action_id, surface, subject_ref, plan_version, session_id, action, "
        " bulk_member_refs, bulk_basis, correction_scope, routed_to, "
        " presented_state_ref, payload, user_id, acted_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (action.action_id, action.surface, action.subject_ref,
         action.plan_version, action.session_id, action.action,
         json.dumps(list(action.bulk_member_refs)), action.bulk_basis,
         action.correction_scope, json.dumps(list(action.routed_to)),
         action.presented_state_ref,
         json.dumps(dict(action.payload), sort_keys=True),
         action.user_id, action.acted_at))
    conn.commit()


def _from_row(row: sqlite3.Row) -> ReviewAction:
    return ReviewAction(
        action_id=row["action_id"], surface=row["surface"],
        subject_ref=row["subject_ref"], plan_version=row["plan_version"],
        session_id=row["session_id"], action=row["action"],
        bulk_member_refs=tuple(json.loads(row["bulk_member_refs"])),
        bulk_basis=row["bulk_basis"],
        correction_scope=row["correction_scope"],
        routed_to=tuple(json.loads(row["routed_to"])),
        presented_state_ref=row["presented_state_ref"],
        payload=json.loads(row["payload"]), user_id=row["user_id"],
        acted_at=row["acted_at"])


def actions_for(conn: sqlite3.Connection, *, subject_ref: str,
                plan_version: str | None = None) -> tuple[ReviewAction, ...]:
    """Every action on one subject, oldest first. Deterministic order."""
    if plan_version is None:
        rows = conn.execute(
            "SELECT * FROM review_actions WHERE subject_ref = ? "
            "ORDER BY acted_at, action_id", (subject_ref,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM review_actions WHERE subject_ref = ? AND "
            "plan_version = ? ORDER BY acted_at, action_id",
            (subject_ref, plan_version)).fetchall()
    return tuple(_from_row(row) for row in rows)


def actions_naming_member(conn: sqlite3.Connection, *, member_ref: str,
                          ) -> tuple[ReviewAction, ...]:
    """Every action whose `bulk_member_refs` enumerates this member.

    §8.2 and §8.7: a bulk acceptance is not a single opaque decision over an
    unnamed population, so a member must be findable from the member's side.
    """
    rows = conn.execute(
        "SELECT * FROM review_actions ORDER BY acted_at, action_id").fetchall()
    return tuple(record for record in map(_from_row, rows)
                 if member_ref in record.bulk_member_refs)


def record_approval(conn: sqlite3.Connection, approval: ReviewApproval) -> None:
    """Store one §8.3 approval. No update path exists here either.

    A person who changes their mind gives a LATER approval; the earlier one stays
    inspectable, which is what makes "you approved this on Tuesday and withdrew it
    on Thursday" a thing the product can say rather than a thing it has forgotten.
    """
    conn.execute(
        "INSERT INTO review_approvals "
        "(approval_id, plan_id, placement_decision_ref, plan_version, "
        " required_review_policy, verdict, presented_state_ref, user_id, "
        " decided_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (approval.approval_id, approval.plan_id,
         approval.placement_decision_ref, approval.plan_version,
         approval.required_review_policy, approval.verdict,
         approval.presented_state_ref, approval.user_id, approval.decided_at))
    conn.commit()


def approvals_for(conn: sqlite3.Connection, *, plan_id: str,
                  plan_version: str | None = None,
                  ) -> tuple[ReviewApproval, ...]:
    """Every approval on one plan, oldest first. Deterministic order.

    `plan_version` is OPTIONAL and defaults to every version on purpose. The
    composition root hands P12 an unfiltered lookup, because P12's gate is what
    decides whether an approval authorizes this plan: a reader that quietly
    dropped an approval stamped with another version would leave that gate
    untested, and would leave the person told "this is waiting for your approval"
    about a plan they have already answered under a version that has since moved.
    """
    if plan_version is None:
        rows = conn.execute(
            "SELECT * FROM review_approvals WHERE plan_id = ? "
            "ORDER BY decided_at, approval_id", (plan_id,)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM review_approvals WHERE plan_id = ? AND "
            "plan_version = ? ORDER BY decided_at, approval_id",
            (plan_id, plan_version)).fetchall()
    return tuple(
        ReviewApproval(
            approval_id=row["approval_id"], plan_id=row["plan_id"],
            placement_decision_ref=row["placement_decision_ref"],
            plan_version=row["plan_version"],
            required_review_policy=row["required_review_policy"],
            verdict=row["verdict"],
            presented_state_ref=row["presented_state_ref"],
            user_id=row["user_id"], decided_at=row["decided_at"])
        for row in rows)
