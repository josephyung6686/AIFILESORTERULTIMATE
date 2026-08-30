"""One record for every gesture, on every surface. Scope is presented, never inferred.

`74` §6 A4. `review_action` is the ONE record P13 emits; it writes nothing else
on this surface. Every field below is the SPEC's, in the SPEC's spelling, and
P13 adds no value to any closed list it did not print.
"""
from __future__ import annotations

import dataclasses
import inspect
import json
import sqlite3

import pytest

from database_agent.events import CORRECTION_SCOPES

from review_surface.collect import (
    BulkMembersRequired,
    PresentationRequired,
    ProtectedContainerHasNoAction,
    ScopeNotPresented,
    collect,
)
from review_surface.records import ReviewAction
from review_surface.store import actions_for, actions_naming_member, record_action
from review_surface.vocabulary import (
    ACTION_ACCEPT,
    ACTION_ACCEPT_BULK,
    ACTION_CHANGE_DESTINATION,
    ACTION_CREATE_CUSTOM_FOLDER,
    ACTION_DEFER,
    ACTION_LEAVE_UNTOUCHED,
    ACTION_MARK_PRIVATE,
    ACTION_RETURN_TO_ACCEPTED_GROUP,
    ACTIONS,
    EVENT_ACTION_ROUTED,
    SUBSYSTEM,
    SURFACE_PLACEMENT,
    UNTOUCHED_PROTECTED,
)

T0 = "2026-08-29T00:00:00Z"

#: The fourteen fields the SPEC's `review_action` block prints, in its order.
#: The protected-container paragraph sitting between `session_id` and `action`
#: in the SPEC is prose, not a field -- see the note in `collect.py`.
SPEC_FIELDS = (
    "action_id", "surface", "subject_ref", "plan_version", "session_id",
    "action", "bulk_member_refs", "bulk_basis", "correction_scope",
    "routed_to", "presented_state_ref", "payload", "user_id", "acted_at",
)


def _presentation(conn, ref="ps-1", *, surface=SURFACE_PLACEMENT,
                  subject_ref="d1"):
    """One row in `review_presentations`, written with raw SQL on purpose.

    `review_surface.presentation` is Wave B's module and does not exist yet.
    Rather than stand a fake one up in `src/`, the test writes the row this
    package will later write and `collect` reads it through P13's own store --
    the seam that has to hold either way.
    """
    conn.execute(
        "INSERT INTO review_presentations (presented_state_ref, event_id, "
        "surface, subject_ref, plan_version, session_id, redaction_policy, "
        "evidence_refs, user_id, rendered_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (ref, 1, surface, subject_ref, "plan-1", "s-1",
         json.dumps({"names": "shown"}), json.dumps(["obs-1"]), "jy", T0))
    conn.commit()
    return ref


@pytest.fixture()
def shown_ref(p13_conn):
    return _presentation(p13_conn)


def _collect(conn, ref, **overrides):
    values = dict(
        action_id="a-1", surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", action=ACTION_ACCEPT,
        correction_scope="file", presented_state_ref=ref, user_id="jy",
        acted_at=T0, component_version="p13-1")
    values.update(overrides)
    return collect(conn, **values)


# --------------------------------------------------------------------------
# `74` §6 A4's named failing test.
# --------------------------------------------------------------------------

def test_a_review_action_carries_the_specs_fields_and_routes_to_the_owning_part(
        p13_conn, shown_ref):
    """`74` §6 A4's named test. The record's shape AND its routing, together.

    They are one test because they are one claim: the SPEC's sentence is
    "routing is the whole contract", and a record with the right fields that
    reaches nobody has satisfied neither half.
    """
    collected = _collect(p13_conn, shown_ref)
    assert tuple(f.name for f in dataclasses.fields(ReviewAction)) == SPEC_FIELDS
    assert collected.action_id == "a-1"
    assert collected.surface == SURFACE_PLACEMENT
    assert collected.subject_ref == "d1"
    assert collected.plan_version == "plan-1"
    assert collected.session_id == "s-1"
    assert collected.action == ACTION_ACCEPT
    assert collected.bulk_member_refs == ()
    assert collected.bulk_basis is None
    assert collected.correction_scope == "file"
    assert collected.presented_state_ref == shown_ref
    assert collected.user_id == "jy"
    assert collected.acted_at == T0
    # Routing: a placement gesture is P11's, and P13 decided nothing about it.
    assert collected.routed_to == ("P11",)


# --------------------------------------------------------------------------
# Done-means 7 and 9.
# --------------------------------------------------------------------------

def test_every_one_of_section_7_10_s_eight_actions_is_collectable(p13_conn, shown_ref):
    """Done-means 7: accept one, accept a batch, change the destination, create
    a custom folder, return the file to a different accepted group, mark
    private, defer, leave untouched."""
    eight = (ACTION_ACCEPT, ACTION_ACCEPT_BULK, ACTION_CHANGE_DESTINATION,
             ACTION_CREATE_CUSTOM_FOLDER, ACTION_RETURN_TO_ACCEPTED_GROUP,
             ACTION_MARK_PRIVATE, ACTION_DEFER, ACTION_LEAVE_UNTOUCHED)
    for index, action in enumerate(eight):
        extra = {}
        if action == ACTION_ACCEPT_BULK:
            extra = dict(bulk_member_refs=("f-1", "f-2"),
                         bulk_basis="same evidence pattern")
        collected = _collect(p13_conn, shown_ref, action_id=f"a-{index}",
                             action=action, **extra)
        assert collected.action == action


def test_every_published_action_is_collectable_on_some_surface(p13_conn, shown_ref):
    """A published action with no collectable surface is a vocabulary member
    with no consumer, which is this project's most-paid-for defect class."""
    from review_surface.routing import Unroutable, route
    from review_surface.vocabulary import SURFACES

    for action in ACTIONS:
        reachable = [surface for surface in SURFACES
                     if _routable(route, Unroutable, surface, action)]
        assert reachable, f"{action} is collectable on no surface"


def _routable(route, unroutable, surface, action):
    try:
        route(surface, action)
    except unroutable:
        return False
    return True


def test_every_action_carries_an_explicit_scope(p13_conn, shown_ref):
    collected = _collect(p13_conn, shown_ref, correction_scope="group")
    assert collected.correction_scope == "group"


def test_no_code_path_assigns_corpus_scope_without_the_user_selecting_it(p13_conn):
    """Done-means 9, NEGATIVE. §8.7's Columbia transcript is the case: a user
    saying ONE transcript belongs in a packet must not teach the engine that all
    transcripts do.

    Two halves. The signature has no default, so there is no value the function
    can supply on the user's behalf; and the widest scope is not spelled anywhere
    in the collection path, so it cannot be reached by a branch either.
    """
    import review_surface.collect as module

    parameter = inspect.signature(module.collect).parameters["correction_scope"]
    assert parameter.default is inspect.Parameter.empty, (
        "correction_scope must have NO default; a default IS an inference")
    source = inspect.getsource(module)
    widest = CORRECTION_SCOPES[-1]
    assert f'"{widest}"' not in source and f"'{widest}'" not in source, (
        f"the literal {widest!r} appears in the collection path")


def test_a_missing_scope_is_a_refusal_and_not_a_default(p13_conn, shown_ref):
    with pytest.raises(TypeError):
        collect(p13_conn, action_id="a-x", surface=SURFACE_PLACEMENT,
                subject_ref="d1", plan_version="plan-1", session_id="s-1",
                action=ACTION_ACCEPT, presented_state_ref=shown_ref,
                user_id="jy", acted_at=T0, component_version="p13-1")


def test_an_out_of_vocabulary_scope_is_refused(p13_conn, shown_ref):
    with pytest.raises(ScopeNotPresented):
        _collect(p13_conn, shown_ref, correction_scope="everything")


def test_the_six_scopes_are_p1_s_six_and_every_one_is_collectable(p13_conn, shown_ref):
    for index, scope in enumerate(CORRECTION_SCOPES):
        collected = _collect(p13_conn, shown_ref, action_id=f"s-{index}",
                             correction_scope=scope)
        assert collected.correction_scope == scope


def test_an_out_of_vocabulary_surface_or_action_is_refused(p13_conn, shown_ref):
    from review_surface.vocabulary import OutOfVocabulary

    with pytest.raises(OutOfVocabulary):
        _collect(p13_conn, shown_ref, surface="dashboard")
    with pytest.raises(OutOfVocabulary):
        _collect(p13_conn, shown_ref, action="delete_everything")


# --------------------------------------------------------------------------
# The three refusals.
# --------------------------------------------------------------------------

def test_an_action_with_no_presented_state_is_refused(p13_conn):
    """§8.7 requires negative feedback stored WITH the evidence that produced it.
    A file rejected while its OCR text was redacted is a different signal from
    one rejected with the evidence visible, so a gesture with no record of what
    was shown carries no evidence at all."""
    with pytest.raises(PresentationRequired):
        _collect(p13_conn, "ps-never-minted")


def test_a_protected_container_carries_no_action_at_all(p13_conn, shown_ref):
    """`67` §1 and the SPEC's own paragraph: applications and system items are
    never read or moved, so offering the user a choice would imply one exists."""
    with pytest.raises(ProtectedContainerHasNoAction):
        _collect(p13_conn, shown_ref, subject_ref=UNTOUCHED_PROTECTED)
    with pytest.raises(ProtectedContainerHasNoAction):
        _collect(p13_conn, shown_ref,
                 payload={"subject_kind": UNTOUCHED_PROTECTED})


def test_no_action_over_a_protected_container_is_constructible_for_any_action(
        p13_conn, shown_ref):
    """Not one action, and not one surface: NO action at all. A refusal that
    covered `accept` and let `leave_untouched` through would still be offering
    the user a choice that does not exist."""
    for index, action in enumerate(ACTIONS):
        with pytest.raises(ProtectedContainerHasNoAction):
            _collect(p13_conn, shown_ref, action_id=f"p-{index}",
                     action=action, subject_ref=UNTOUCHED_PROTECTED,
                     bulk_member_refs=("f-1",), bulk_basis="b")


def test_a_bulk_acceptance_with_no_enumerated_members_is_refused(p13_conn, shown_ref):
    """A filter expression cannot be re-read later to say which files a reversal
    applies to."""
    with pytest.raises(BulkMembersRequired):
        _collect(p13_conn, shown_ref, action=ACTION_ACCEPT_BULK)


# --------------------------------------------------------------------------
# Routing recorded on the record, and the event.
# --------------------------------------------------------------------------

def test_the_action_is_routed_and_the_parts_are_recorded_on_it(p13_conn, shown_ref):
    collected = _collect(p13_conn, shown_ref, action=ACTION_MARK_PRIVATE)
    assert "P7" in collected.routed_to and "P6" in collected.routed_to


def test_collecting_appends_the_registered_event_with_the_scope_and_the_parts(
        p13_conn, shown_ref):
    collected = _collect(p13_conn, shown_ref, correction_scope="node",
                         action=ACTION_CHANGE_DESTINATION,
                         payload={"node_id": "n-9"})
    row = p13_conn.execute(
        "SELECT event_type, subsystem, correction_scope, explanation FROM "
        "events WHERE event_type = ? ORDER BY event_id DESC LIMIT 1",
        (EVENT_ACTION_ROUTED,)).fetchone()
    assert row["event_type"] == EVENT_ACTION_ROUTED
    assert row["subsystem"] == SUBSYSTEM
    assert row["correction_scope"] == "node"
    assert "P11" in row["explanation"]
    assert collected.routed_to == ("P11",)


def test_p13_authors_only_the_fact_that_one_gesture_was_collected(p13_conn, shown_ref):
    """M8: the acting part authors; P1 writes. P13 never authors P11's placement
    event, P10's tree edit, P7's consent events or P12's move events."""
    _collect(p13_conn, shown_ref, action=ACTION_MARK_PRIVATE)
    types = {row["event_type"] for row in
             p13_conn.execute("SELECT DISTINCT event_type FROM events")}
    assert types == {EVENT_ACTION_ROUTED}


# --------------------------------------------------------------------------
# The store.
# --------------------------------------------------------------------------

def test_a_collected_action_stores_and_reads_back_whole(p13_conn, shown_ref):
    collected = _collect(p13_conn, shown_ref)
    record_action(p13_conn, collected)
    assert actions_for(p13_conn, subject_ref="d1") == (collected,)


def test_a_bulk_member_is_findable_from_the_member_s_side(p13_conn, shown_ref):
    """§8.2 and §8.7: a bulk acceptance is not a single opaque decision over an
    unnamed population, so each member stays individually inspectable."""
    collected = _collect(p13_conn, shown_ref, action=ACTION_ACCEPT_BULK,
                         bulk_member_refs=("f-1", "f-2"),
                         bulk_basis="same evidence pattern")
    record_action(p13_conn, collected)
    assert actions_naming_member(p13_conn, member_ref="f-2") == (collected,)
    assert actions_naming_member(p13_conn, member_ref="f-9") == ()


def test_a_stored_action_cannot_be_updated_or_deleted(p13_conn, shown_ref):
    record_action(p13_conn, _collect(p13_conn, shown_ref))
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute("UPDATE review_actions SET action = 'reject'")
    with pytest.raises(sqlite3.IntegrityError):
        p13_conn.execute("DELETE FROM review_actions")


def test_the_store_has_no_update_path_at_all(p13_conn):
    """P13 owns no supersedable record, so there is no `supersede`, no
    `mark_superseded` and no `current_*`. A later gesture is a later row."""
    import review_surface.store as module

    for name in dir(module):
        assert "supersede" not in name
        assert not name.startswith("update_")


def test_p13_writes_no_record_other_than_its_own(p13_conn, shown_ref):
    """Done-means 22's writing clause, in its first position."""
    watched = ("placement_decisions", "classifications", "files", "tree_nodes")
    present = [name for name in watched if p13_conn.execute(
        "SELECT count(*) AS c FROM sqlite_master WHERE type='table' AND name = ?",
        (name,)).fetchone()["c"]]
    assert present, "the fixture creates none of the watched tables"
    before = {name: p13_conn.execute(
        f"SELECT count(*) AS c FROM {name}").fetchone()["c"] for name in present}
    record_action(p13_conn, _collect(p13_conn, shown_ref))
    after = {name: p13_conn.execute(
        f"SELECT count(*) AS c FROM {name}").fetchone()["c"] for name in present}
    assert after == before
