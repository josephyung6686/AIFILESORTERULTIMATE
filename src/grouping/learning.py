# src/grouping/learning.py
"""P13's review action, received structurally. Two writes, and never one.

The receiver takes any value carrying the published fields, and a test proves
`src/grouping/` imports nothing from `tests/`. A source stub would be P9 deciding
what a user action looks like, which is P13's to say.

This docstring used to open *"P13 is specification only. Nothing here imports it
or a stand-in for it."* P13 shipped, and `81` §14 ruled that **the part which
COLLECTS a gesture owns its name**, so the NAMES below are now imported from
`review_surface.vocabulary` and respelled nowhere. The record's SHAPE is still
read structurally and still not imported -- that is Option G (`81` §12) and it is
unchanged: the receiver declares what it requires, the producer produces the
SPEC's record, and an integration test running the real chain holds them together.

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
from review_surface.vocabulary import (
    ACTION_ACCEPT, ACTION_DEFER, ACTION_REJECT, SURFACE_GROUP_PLAN,
)

#: The surface a group review happens on. An action from a node or template
#: surface reaching this receiver would be P9 recording a decision about
#: something it does not own.
#:
#: P13's, carried verbatim (`81` §14, MINOR 6). It was `"group_plan"` spelled
#: here, and a surface P13 renamed would have become a surface P9 silently
#: refused.
GROUP_PLAN_SURFACE: str = SURFACE_GROUP_PLAN

#: The event P1 reserves for a user's decision about a group.
USER_GROUP_DECISION: str = "user group decision"

#: What each action P9 receives means to it: the plan-version acceptance, the
#: review state that goes with it, and the learning polarity P1 records. Stated
#: one line per action rather than derived, because "reject implies negative" is
#: the kind of derivation that quietly acquires an eighth case.
#:
#: **The keys are P13's, where P13 has a name.** `81` §14 ruled the collector owns
#: the name, so `accept`, `reject` and `defer` are imported and respelled nowhere.
#:
#: **The other four are the ruling's unfinished half, and they are left standing
#: deliberately.** `edit` and `exclude-from-packet` name gestures §8.7 names in
#: its own words -- renaming, and *"excluding one member from a packet"* -- that
#: P13 has no member for; adding those members needs the owner's approval
#: recorded at the member, which is owed and not given
#: (`review_surface/vocabulary.py`, the block above `ACTIONS`;
#: `tests/p13/test_p13_unhomed_gestures.py` reports it). `restore` and
#: `reset-suggestion` are worse than unhomed: `81` §8 Q5 answered **no** under
#: both readings, because no sentence in P9's SPEC or the design names either.
#: They are removals, not renames, and removing them is P9's own contract
#: revision rather than this ruling's consequence. Nothing here is a second home
#: for a P13 name; each is a name P13 does not have.
#:
#: The third element of each tuple is §8.7's POLARITY, which is P1's axis and not
#: an action -- `defer` is an action with no polarity in P11's vocabulary, and the
#: two spellings colliding is the reason these are not bound to the keys.
_ACTIONS: dict[str, tuple[str, str, str]] = {
    ACTION_ACCEPT: (ACCEPTED, USER_ACCEPTED, "accept"),
    "edit": (ACCEPTED, USER_ACCEPTED, "accept"),
    ACTION_REJECT: (REJECTED, USER_REJECTED, "reject"),
    ACTION_DEFER: (DEFERRED, DEFERRED, "defer"),
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
