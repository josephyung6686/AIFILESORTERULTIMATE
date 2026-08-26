# src/grouping/learning.py
"""P13's review action, received structurally. Two writes, and never one.

P13 is specification only. Nothing here imports it or a stand-in for it: the
receiver takes any value carrying the published fields, and a test proves
`src/grouping/` imports nothing from `tests/`. A source stub would be P9 deciding
what a user action looks like, which is P13's to say.

Every accepted action produces two records.

**The plan-version decision**, through the acceptance table. Accepting in version
2 and rejecting in version 3 leaves one group and two opinions.

**The scoped learning record**, through P1's event log. §8.7 stores a rejection
WITH its evidence and §4.9 SR6 reads it, which is why a rejection recorded under
one plan version still stops the same attractive-but-incorrect grouping
resurfacing under the next.

The scope is carried and never inferred. Guessing `corpus` from one file would
teach the engine that every file like it belongs there -- the §8.7 failure the six
scopes exist to prevent -- so a missing one is a refusal.
"""
from __future__ import annotations

import sqlite3

from database_agent.db import transaction
from database_agent.events import append_event

from grouping.acceptance import record_acceptance
from grouping.records import Group, GroupAcceptance
from grouping.store import current_group
from grouping.vocabulary import (
    ACCEPTED,
    GROUP_PROPOSAL_CLASS,
    MEMBERSHIP_PROPOSAL_CLASS,
    DEFERRED,
    PENDING_REVIEW,
    REJECTED,
    USER,
    USER_ACCEPTED,
    USER_EXCLUDED_FROM_PACKET,
    USER_REJECTED,
)

#: The surface a group review happens on. An action from a node or template
#: surface reaching this receiver would be P9 recording a decision about
#: something it does not own.
GROUP_PLAN_SURFACE: str = "group_plan"

#: The event P1 reserves for a user's decision about a group.
USER_GROUP_DECISION: str = "user group decision"

#: What each of P13's seven actions means to P9: the plan-version acceptance, the
#: review state that goes with it, and the learning polarity P1 records. Stated
#: one line per action rather than derived, because "reject implies negative" is
#: the kind of derivation that quietly acquires an eighth case.
_ACTIONS: dict[str, tuple[str, str, str]] = {
    "accept": (ACCEPTED, USER_ACCEPTED, "accept"),
    "edit": (ACCEPTED, USER_ACCEPTED, "accept"),
    "reject": (REJECTED, USER_REJECTED, "reject"),
    "defer": (DEFERRED, DEFERRED, "defer"),
    "restore": (ACCEPTED, USER_ACCEPTED, "accept"),
    "reset-suggestion": (PENDING_REVIEW, PENDING_REVIEW, "reset"),
    "exclude-from-packet": (
        REJECTED, USER_EXCLUDED_FROM_PACKET, "reject"),
}


class ReviewActionRefused(ValueError):
    """The action does not belong to P9, or does not carry what P1 requires."""


def group_basis_key(group: Group) -> str:
    """SR6's equivalence class for a whole group: its anchor facts, sorted.

    Sorted because `anchor_facts` is a list and the same two facts can arrive
    either way round; two orderings producing two keys would be two proposals,
    and a rejection of one would not stop the other.
    """
    return "|".join(sorted(
        f"{fact.field}={fact.value}" for fact in group.anchor_facts
    ))


def membership_basis_key(group_id: str, membership_id: str) -> str:
    """SR6's equivalence class for one membership. One file the user pushed out
    of a group is not a rejection of the group."""
    return f"{group_id}:{membership_id}"


def _require(action: object, name: str) -> object:
    value = getattr(action, name, None)
    if value is None or value == "":
        raise ReviewActionRefused(
            f"{name} is required on a review action and P9 supplies no default. "
            "A guessed scope teaches the engine from one file that every file "
            "like it belongs there, which is the failure the six scopes prevent."
        )
    return value


def apply_review_action(conn: sqlite3.Connection, action) -> tuple[str, ...]:
    """Record one user decision about one subject. Returns the ids written.

    One action, one subject. A bulk decision arrives as one call per subject with
    a shared basis: a collapsed action over a set could not say which of them a
    later reversal applies to.
    """
    if getattr(action, "surface", None) != GROUP_PLAN_SURFACE:
        raise ReviewActionRefused(
            f"P9 receives actions from the {GROUP_PLAN_SURFACE!r} surface only; "
            f"{getattr(action, 'surface', None)!r} belongs to another part"
        )
    kind = _require(action, "action")
    if kind not in _ACTIONS:
        raise ReviewActionRefused(f"{kind!r} is not a review action P9 receives")
    # The scope must be present, and P1 owns which ones exist. Re-checking the
    # membership here would be a second copy of P1's vocabulary, which is how the
    # two drift; `append_event` refuses an unknown one and the transaction below
    # takes the acceptance row down with it.
    scope = _require(action, "correction_scope")
    user_id = _require(action, "user_id")
    presented = _require(action, "presented_state_ref")
    plan_version_id = _require(action, "plan_version_id")
    group_id = _require(action, "group_id")
    decided_at = _require(action, "decided_at")
    basis = _require(action, "basis")

    membership_id = getattr(action, "membership_id", None)
    acceptance, review_state, polarity = _ACTIONS[kind]
    if membership_id:
        proposal_class = MEMBERSHIP_PROPOSAL_CLASS
        basis_key = membership_basis_key(group_id, membership_id)
        subject = membership_id
    else:
        proposal_class = GROUP_PROPOSAL_CLASS
        basis_key = group_basis_key(current_group(conn, group_id))
        subject = group_id

    acceptance_id = f"{plan_version_id}:{subject}:{kind}"
    with transaction(conn):
        record_acceptance(conn, GroupAcceptance(
            acceptance_id=acceptance_id,
            plan_version_id=plan_version_id,
            group_id=group_id,
            membership_id=membership_id or None,
            acceptance=acceptance,
            review_state=review_state,
            user_edited_label=getattr(action, "user_edited_label", None),
            aliases=(),
            review_decision_ref=presented,
            decided_by=USER,
            created_at=decided_at,
        ))
        event_id = append_event(
            conn,
            event_type=USER_GROUP_DECISION,
            file_id=None,
            content_hash=None,
            subsystem="P9",
            component_version="p9",
            observed_at=decided_at,
            explanation=f"{basis} (presented state {presented})",
            user_id=user_id,
            correction_scope=scope,
            correction_subject=subject,
            polarity=polarity,
            proposal_class=proposal_class,
            basis_key=basis_key,
        )
    return (acceptance_id, str(event_id))
