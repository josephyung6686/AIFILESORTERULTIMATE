"""Collecting §8.3's approval. The one record P12 cannot move a reviewed file without.

Before this module, P12's side of the gate was complete and had no producer:
`mutation.approval.approval_verdict` implements the SPEC's four rules in full and
reads the record through an injected `approval_for` lookup, and nothing in the
product ever returned anything but `None` from one. A gate that can refuse and
can never be satisfied is not a gate; it is a wall with a lock drawn on it. This
module is the key, and it is the whole of P13's half.

**P13 produces the record and decides nothing with it.** Enforcement stays with
P12 (S4). Nothing here consults a plan, a hash, a path, a classification or a
disk. It validates that the person's decision is well-formed and says what was on
the screen when they made it, and then it is P12 that refuses or applies.

**Three refusals, and each is about interpretability rather than tidiness.**

* **The presentation must exist.** §8.4 makes what was displayed a
  privacy-relevant fact and §8.7 requires feedback stored WITH the evidence that
  produced it. An approval given while the evidence was redacted is a different
  decision from one given with it visible, and an approval naming no recorded
  presentation records neither.
* **The presentation must be of THIS plan, on the apply surface.** A glance at a
  placement card is not a review of a move plan. Accepting any ref at all would
  make the first refusal a formality: a caller could satisfy it with whatever ref
  it had to hand, and the stored answer to *what was this person looking at?*
  would be wrong rather than missing.
* **The presentation must be of the SAME plan version.** §8.8 is the reason. An
  approval and the display it came from describe one moment or neither does, and
  a record stitched from two versions could not be replayed as either.

**What is deliberately absent: a scope, and a default.** `review_approval` has no
`correction_scope` -- an approval is a decision about one plan, not a lesson about
a class of files -- and no argument here has a default, so there is no value this
module can supply on a person's behalf.
"""
from __future__ import annotations

import json
import sqlite3

from database_agent.events import append_event
# P11's tuple, imported rather than respelled -- the same rule `collect` follows
# for P1's `CORRECTION_SCOPES`. `required_review_policy` is the value P11 put on
# the decision's `review_policy`, so a policy P11 adds later must be storable
# here the day P11 adds it, and a policy P11 never had must not be.
from placement.vocabulary import REVIEW_POLICIES

from review_surface.presentation import presented_state
from review_surface.records import ReviewApproval
from review_surface.vocabulary import (
    EVENT_APPROVAL,
    SUBSYSTEM,
    SURFACE_APPLY,
    VERDICTS,
    check,
)


class ApprovalPresentationRequired(ValueError):
    """An approval with no recorded, matching record of what the person was shown."""


def approve(conn: sqlite3.Connection, *, approval_id: str, plan_id: str,
            placement_decision_ref: str, plan_version: str,
            required_review_policy: str, verdict: str,
            presented_state_ref: str, user_id: str, decided_at: str,
            component_version: str) -> ReviewApproval:
    """Validate the decision, append `apply review approval`, return the record.

    Storing is `store.record_approval`, kept separate for the reason `collect`
    and `record_action` are kept separate: the §8.2 event is the historical fact
    and the row is P13's own index over it, and a writer that did both would make
    the event conditional on the table.

    Every verdict is recorded, not only `approved`. A rejection and a deferral are
    answers a person gave and §8.2 wants them visible afterwards; discarding them
    would make "nobody has looked at this yet" and "somebody looked and said no"
    the same state, which is exactly the conflation `66` §4 forbids one section
    over.
    """
    check(verdict, VERDICTS, name="approval verdict")
    if required_review_policy not in REVIEW_POLICIES:
        raise ValueError(
            f"{required_review_policy!r} is not one of P11's review policies "
            f"{list(REVIEW_POLICIES)}. `required_review_policy` is the value on "
            "the plan that demanded review, so it is P11's word and not a new one")
    shown = presented_state(conn, presented_state_ref)
    if shown is None:
        raise ApprovalPresentationRequired(
            f"{presented_state_ref!r} names no recorded presentation. §8.4 makes "
            "what was displayed a privacy-relevant fact and §8.7 requires a "
            "decision to be stored with the evidence that produced it; an "
            "approval with no record of what was on the screen carries neither")
    # Written as a pair of dict literals rather than a tuple of triples so that
    # the field NAMES are dict keys: `plan_version` is both a P13 surface and a
    # column on all three tables, and A1's guard judges a bare vocabulary member
    # by its syntactic role. A key naming a column is a column reference; the
    # same string loose in a tuple would be a second home for the surface name.
    expected = {"surface": SURFACE_APPLY, "subject_ref": plan_id,
                "plan_version": plan_version}
    given = {"surface": shown.surface, "subject_ref": shown.subject_ref,
             "plan_version": shown.plan_version}
    mismatched = tuple(name for name in expected
                       if expected[name] != given[name])
    if mismatched:
        raise ApprovalPresentationRequired(
            f"{presented_state_ref!r} records a presentation that differs from "
            f"this approval on {list(mismatched)}. An approval and the display "
            "it came from describe one moment or neither does: a ref borrowed "
            "from another screen, another plan or another plan version would "
            "answer 'what was this person looking at?' wrongly rather than "
            "leaving it unanswered")
    record = ReviewApproval(
        approval_id=approval_id, plan_id=plan_id,
        placement_decision_ref=placement_decision_ref,
        plan_version=plan_version,
        required_review_policy=required_review_policy, verdict=verdict,
        presented_state_ref=presented_state_ref, user_id=user_id,
        decided_at=decided_at)
    append_event(
        conn, event_type=EVENT_APPROVAL, subsystem=SUBSYSTEM,
        component_version=component_version, observed_at=decided_at,
        user_id=user_id,
        explanation=json.dumps(
            {"approval_id": approval_id, "plan_id": plan_id,
             "placement_decision_ref": placement_decision_ref,
             "plan_version": plan_version,
             "required_review_policy": required_review_policy,
             "verdict": verdict,
             "presented_state_ref": presented_state_ref},
            sort_keys=True))
    return record
