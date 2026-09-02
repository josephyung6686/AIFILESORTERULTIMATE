"""P13's `review_action`, received. P13 presents and collects; P11 authors (M8).

Nothing here interprets a gesture into a preference. It records what the user did
at the scope the user chose, and authors the decision the action produces -- which
for most actions is none: accepting a recommendation confirms a decision that
already exists, deferring decides nothing, and creating a folder is P10's edit.

Scope is the safety property and it is never widened. §8.7's governing example is
that one transcript belonging in a Columbia packet must not teach the engine that
all transcripts do, so `correction_scope` comes off the action and P11 adds
nothing to it.

A bulk acceptance enumerates its members. A filter expression cannot be re-read
later to say which files a reversal applies to, which is why P13's own record
forbids one and why this refuses an empty enumeration.

**What is written here is what §8.7 reads back.** `learning.suppressed_nodes` is
this module's consumer, and it queries `(scope, correction_subject)` and matches
`basis_key`. A correction stored under a subject that query never asks for is a
correction that silently does nothing -- the same node is resurfaced on the next
run and no test of either side alone can see it. So the subject a correction is
keyed on is the subject the SCOPE names, resolved through the decision when the
action's own `subject_ref` is a decision id rather than a file id.
"""
from __future__ import annotations

import sqlite3
from types import MappingProxyType

from placement import events as placement_events
from placement.learning import (
    ACCEPT, CORPUS, NODE, REJECT, ScopeSubjectRequired, basis_key_for,
    record_correction,
)
from placement.vocabulary import (
    ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_CHANGE_DESTINATION,
    ACTION_CREATE_CUSTOM_FOLDER, ACTION_DEFER, ACTION_DISABLE_SUGGESTION_TYPE,
    ACTION_EDIT_RECOMMENDATION, ACTION_LEAVE_UNTOUCHED, ACTION_MARK_PRIVATE,
    ACTION_REJECT, ACTION_RETURN_TO_ACCEPTED_GROUP, FILE, GROUP, PLACEMENT,
    RESIDUAL, REVIEW_ACTIONS, REVIEW_SURFACES, SURFACE_GROUP_PLAN,
    SURFACE_PLACEMENT, SURFACE_RESIDUAL_FILE, SURFACE_RESIDUAL_SET,
)

#: P13 SPEC:294 -- the surfaces whose actions route to P11. Imported, not
#: re-spelled, and two copies of one vocabulary is how a surface P13 renames
#: becomes a surface P11 silently refuses.
#:
#: This used to say `placement/vocabulary.py` was "the one home for a value P13
#: owns and **has not yet published**". P13 has published, so that file now
#: carries P13's objects rather than holding a second home for them (`81` §14.3's
#: Q2'); the import here is unchanged and is now one hop from the owner.
P11_SURFACES: tuple[str, ...] = REVIEW_SURFACES
P11_ACTIONS: tuple[str, ...] = REVIEW_ACTIONS

#: Which §8.7 store a correction collected on each surface belongs to. A rejection
#: taken on a residual surface is a residual fact: read back as a placement fact it
#: would suppress a node the user never saw in the §6 pass. `learning` publishes
#: both classes and, until this map existed, nothing produced the second one.
_PROPOSAL_CLASS: MappingProxyType = MappingProxyType({
    SURFACE_PLACEMENT: PLACEMENT, SURFACE_GROUP_PLAN: PLACEMENT,
    SURFACE_RESIDUAL_SET: RESIDUAL, SURFACE_RESIDUAL_FILE: RESIDUAL,
})
assert set(_PROPOSAL_CLASS) == set(P11_SURFACES)

ACCEPT_BULK: str = ACTION_ACCEPT_BULK
CHANGE_DESTINATION: str = ACTION_CHANGE_DESTINATION
CREATE_CUSTOM_FOLDER: str = ACTION_CREATE_CUSTOM_FOLDER

#: Which actions are a negative example and which a positive one. `defer` is
#: neither: it is a decision to decide later, and recording it under either
#: polarity would teach the engine something the user did not say. An action
#: absent from this map is recorded with `polarity` NULL, which is the column
#: saying "the user acted and expressed no preference" rather than "accept".
_POLARITY: MappingProxyType = MappingProxyType({
    ACTION_ACCEPT: ACCEPT, ACTION_ACCEPT_BULK: ACCEPT,
    ACTION_LEAVE_UNTOUCHED: ACCEPT, ACTION_REJECT: REJECT,
    ACTION_CHANGE_DESTINATION: REJECT, ACTION_DISABLE_SUGGESTION_TYPE: REJECT,
})
assert ACTION_DEFER not in _POLARITY

#: Actions that author a new P11 decision. The rest confirm one, record a
#: preference, or belong to another part.
_AUTHORS_A_DECISION: frozenset[str] = frozenset({
    ACTION_CHANGE_DESTINATION, ACTION_RETURN_TO_ACCEPTED_GROUP,
    ACTION_EDIT_RECOMMENDATION, ACTION_MARK_PRIVATE,
})

#: §7.10 and §8.8: a folder the user creates is a tree edit, and P10's.
_ROUTED_TO_P10: frozenset[str] = frozenset({ACTION_CREATE_CUSTOM_FOLDER})

#: Disjoint BY CONSTRUCTION rather than by a second check at the call site. A
#: `not routes_to_p10(...)` guard beside the membership test below would be a
#: condition that can never fire, which is indistinguishable from a guard that
#: works until the day someone adds a routed action to the authoring set.
assert not (_AUTHORS_A_DECISION & _ROUTED_TO_P10)
assert set(_POLARITY) | _AUTHORS_A_DECISION | _ROUTED_TO_P10 <= set(P11_ACTIONS)


class UnroutedSurface(ValueError):
    """An action reached P11 wearing a surface, or a name, P13 routes elsewhere."""


class BulkMembersRequired(ValueError):
    """A bulk acceptance with no enumerated members. A filter is not a list."""


def routes_to_p10(action) -> bool:
    """§7.10 and §8.8: a folder the user creates is a tree edit, and P10's.

    P11 routes it and authors nothing. This is the one place where the answer to
    "who invents a destination?" has to be visible in P11's own code, because the
    prohibition (§6.12) is about the SYSTEM inventing one and this is the user.
    """
    return action.action in _ROUTED_TO_P10


def correction_scope_of(action) -> tuple[str, str]:
    """The scope the user chose, and the subject the ACTION names.

    Never widened and never inferred. A `node`-scoped correction is about the node
    in the action's payload; every other scope is about its `subject_ref`. What a
    correction is finally KEYED on is `_correction_subjects` below, which resolves
    a file- or group-scoped subject through the decision -- because on a placement
    surface `subject_ref` is a decision id, and §8.7's reader asks for a file id.
    """
    payload = getattr(action, "payload", {}) or {}
    if action.correction_scope == NODE and payload.get("node_id"):
        return action.correction_scope, payload["node_id"]
    if action.correction_scope == FILE:
        return action.correction_scope, action.subject_ref
    return action.correction_scope, payload.get("subject_id", action.subject_ref)


def _correction_subjects(action, decision) -> tuple[str, ...]:
    """One subject per subject the SCOPE names. This is the key §8.7 reads back.

    At `file` and `group` scope the subject is the file or the group itself, taken
    from the decision, because `learning._subject_ids` derives exactly that from
    the subject ref and would find nothing under a decision id. A bulk at those
    scopes is one correction per member: the user made one statement per file.

    At every other scope the scope names ONE subject and a bulk stays one
    correction -- three rows under one corpus subject would be three copies of one
    fact, and a reversal reading them would count the preference three times.
    """
    scope, named = correction_scope_of(action)
    members = tuple(getattr(action, "bulk_member_refs", ()) or ())
    if scope in (FILE, GROUP):
        if members:
            return members
        subject = decision.subject
        own = subject.file_id if scope == FILE else subject.group_id
        if subject.kind != scope or not own:
            raise ScopeSubjectRequired(
                f"the {scope!r} scope was asked about a {subject.kind!r} subject; "
                "reading one id as the other would store this user's decision "
                "under another's name and read it back for the wrong subject"
            )
        return (own,)
    return (named,)


def _predecessor_row(conn: sqlite3.Connection, action):
    """The LIVE decision this action revises, or None.

    P13's `subject_ref` on a placement surface is the id of the decision the user
    was looking at (`presented_state_ref` names the event; `subject_ref` names the
    record). It is passed to `mark_superseded` as `old_id`, which raises for a
    record that is not in the table -- so a first decision about a subject, or one
    whose predecessor was already superseded, must resolve to None rather than to
    a plausible-looking string. Inventing a predecessor is how a user gesture
    becomes an unwritable decision.
    """
    return conn.execute(
        "SELECT record_id, node_id FROM placement_decisions WHERE record_id = ? "
        "AND superseded_by IS NULL", (action.subject_ref,),
    ).fetchone()


def _node_in_question(conn: sqlite3.Connection, action, payload) -> str | None:
    """The node the correction is ABOUT, or None when P11 cannot name one.

    For `change_destination` the payload names where the user moved the file TO,
    so the negative example is the node they moved AWAY from -- the live
    decision's own node. Keying the rejection on the payload instead would
    suppress the destination the user had just chosen, and the mistake would only
    surface on a later run.

    None is a marker here and never a key: an action P11 cannot resolve to a node
    is recorded with its scope and polarity and no `basis_key`, rather than under
    a key like `f1->` that matches nothing and looks like a stored preference.
    """
    if action.action == CHANGE_DESTINATION:
        row = _predecessor_row(conn, action)
        return None if row is None else row["node_id"]
    named = payload.get("node_id")
    if named:
        return named
    row = _predecessor_row(conn, action)
    return None if row is None else row["node_id"]


def _explanation(action, members: tuple[str, ...]) -> str:
    """The action, its stated basis, and -- for a bulk -- every member by name.

    P13 SPEC:271-272 requires the enumeration and forbids a filter expression,
    because a filter cannot be re-read later to say which files a reversal applies
    to. P13's record is its durable home; the log carries it so §8.2 can
    reconstruct what the user did without P13's table.
    """
    basis = getattr(action, "bulk_basis", None)
    text = f"{action.action}: {basis}" if basis else action.action
    if members:
        text = f"{text} [members: {' '.join(members)}]"
    return text


def apply_review_action(conn: sqlite3.Connection, action, *, decision_factory,
                        component_version: str,
                        observed_at: str) -> tuple[str, ...]:
    """Record the action; author the decision it produces, if it produces one.

    Returns the ids of decisions written. An empty tuple is a real answer: most
    gestures confirm or defer rather than decide, and returning a fabricated id
    would put a decision in the store that the user never asked for.
    """
    surface = getattr(action, "surface", None)
    if surface not in P11_SURFACES:
        raise UnroutedSurface(
            f"surface {surface!r} is not one of P11's {P11_SURFACES}; P13 routes "
            "canvas and plan_version to P10, consent to P7, apply to P12"
        )
    if action.action not in P11_ACTIONS:
        raise UnroutedSurface(
            f"action {action.action!r} is not one P13 routes to a placement or "
            f"residual surface; P11 handles {P11_ACTIONS}"
        )

    payload = getattr(action, "payload", {}) or {}
    members = tuple(getattr(action, "bulk_member_refs", ()) or ())
    if action.action == ACCEPT_BULK and not members:
        raise BulkMembersRequired(
            "§7.10's bulk decision enumerates every member; P13's own record "
            "forbids a filter expression, because a filter cannot say later "
            "which files a reversal applies to"
        )

    proposal_class = _PROPOSAL_CLASS[surface]
    scope, _ = correction_scope_of(action)
    probe = _decision_for(conn, decision_factory, action, action.subject_ref)

    if routes_to_p10(action):
        # Routed, and the routing is READABLE. §6.12 prohibits P11 minting a node,
        # so the only trace this gesture can leave in P11 is the log line saying
        # where it went; a receiver that swallowed it silently would look
        # identical from every assertion about what did NOT happen.
        placement_events.review_decision(
            conn, subject_ref=action.subject_ref, action=action.action,
            component_version=component_version, observed_at=observed_at,
            user_id=action.user_id, correction_scope=scope,
            correction_subject=_correction_subjects(action, probe)[0],
            polarity=None, proposal_class=proposal_class, basis_key=None,
            explanation="routed to P10: §7.10 makes a user-created folder a tree "
                        "edit opening a new plan version, and §6.12 forbids P11 "
                        "minting a node",
        )
        return ()

    subjects = _correction_subjects(action, probe)
    polarity = _POLARITY.get(action.action)
    node_id = _node_in_question(conn, action, payload)
    explanation = _explanation(action, members)

    for subject_id in subjects:
        decision = _decision_for(conn, decision_factory, action, subject_id)
        if polarity is not None and node_id:
            record_correction(
                conn, decision=decision, action=action.action, polarity=polarity,
                scope=scope, subject_id=subject_id,
                basis_key=basis_key_for(subject_id=subject_id, node_id=node_id),
                user_id=action.user_id, component_version=component_version,
                observed_at=observed_at, explanation=explanation,
                proposal_class=proposal_class,
            )
            continue
        # §8.2 still records the action: a deferral the log cannot show is a gap
        # in the reconstruction §8.2 exists to make possible. It carries no
        # `basis_key`, because there is no node this is a preference about.
        from placement.store import subject_ref_of

        placement_events.review_decision(
            conn, subject_ref=subject_ref_of(decision.subject),
            action=action.action, component_version=component_version,
            observed_at=observed_at, user_id=action.user_id,
            correction_scope=scope, correction_subject=subject_id,
            polarity=polarity, proposal_class=proposal_class, basis_key=None,
            explanation=explanation, file_id=decision.subject.file_id,
            content_hash=decision.subject.content_hash,
        )

    written: list[str] = []
    if action.action in _AUTHORS_A_DECISION:
        from placement.store import record_decision

        decision = _decision_for(conn, decision_factory, action,
                                 action.subject_ref)
        record_decision(conn, decision, component_version=component_version,
                        observed_at=observed_at,
                        supersede_reason=(f"user {action.action} on "
                                          f"{action.subject_ref}")
                        if decision.supersedes else None)
        written.append(decision.decision_id)
    return tuple(written)


def _decision_for(conn: sqlite3.Connection, decision_factory, action,
                  subject_id: str):
    """The decision this action produces, built by the caller's factory.

    The factory is the pipeline's, because authoring a decision needs the whole
    of Tasks 6-15 -- the index, the retrieval, the scoring, the privacy state.
    P11's receiver decides WHETHER a decision is authored; the pipeline decides
    what it says.

    Every authoring action supersedes its predecessor when one is live, not only
    `change_destination`. `one_current_placement_decision` is a partial unique
    index over unsuperseded rows, so a second live decision about one subject is
    refused by SQLite -- an authoring action that skipped the link would raise on
    the insert rather than quietly writing two current opinions.
    """
    row = (_predecessor_row(conn, action)
           if action.action in _AUTHORS_A_DECISION else None)
    return decision_factory(
        decision_id=f"{action.action_id}:{subject_id}",
        supersedes=None if row is None else row["record_id"],
    )
