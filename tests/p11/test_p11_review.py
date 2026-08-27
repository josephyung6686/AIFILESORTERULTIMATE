"""P13 collects; P11 authors. The back edge is fixture-mediated until P13 ships.

Two properties are tested in pairs throughout, because each half alone passes
against a broken receiver: a guard that always fires and a guard that never does
look identical from the positive case.
"""
from __future__ import annotations

import json

import pytest

from placement import vocabulary as v
from placement.learning import suppressed_nodes
from placement.review import (
    BulkMembersRequired, P11_ACTIONS, P11_SURFACES, ScopeSubjectRequired,
    UnroutedSurface, apply_review_action, correction_scope_of, routes_to_p10,
)
from placement.records import Subject
from placement.store import record_decision
from p11.conftest import FIXED_CLOCK
from p11 import p13_fixtures as p13
from p11.test_p11_records import _decision


def _factory(**_kwargs):
    return _decision


def _apply(conn, action, **overrides):
    values = dict(decision_factory=_factory(), component_version="P11-test",
                  observed_at=FIXED_CLOCK)
    values.update(overrides)
    return apply_review_action(conn, action, **values)


def _record_d1(conn, **overrides):
    """The decision the user is looking at. A gesture revises something."""
    record_decision(conn, _decision(decision_id="d1", **overrides),
                    component_version="P11-test", observed_at=FIXED_CLOCK)


def _last_event(conn):
    return conn.execute(
        "SELECT * FROM events ORDER BY event_id DESC LIMIT 1").fetchone()


# --- what routes here, and what does not ------------------------------------------

def test_the_four_surfaces_are_p13s_four_for_p11():
    assert P11_SURFACES == ("placement", "group_plan", "residual_set",
                            "residual_file")


def test_an_action_on_another_parts_surface_is_refused(p11_conn):
    # `ReviewActionFixture` refuses `canvas` at construction, which is P13's own
    # guard. P11's guard is for a record that reached it wearing a surface P13
    # routes elsewhere, so the test uses a bare object rather than the fixture.
    class Foreign:
        surface = "consent"
        action = "accept"

    with pytest.raises(UnroutedSurface):
        _apply(p11_conn, Foreign())
    with pytest.raises(ValueError):
        p13.accept(surface="canvas")


def test_an_action_p13_routes_elsewhere_is_refused_on_a_p11_surface(p11_conn):
    # The negative twin of the surface guard: the surface is P11's and the ACTION
    # is not. Without this, `adopt_version` on a placement surface would fall
    # through `_POLARITY.get` and be recorded as a placement gesture.
    class Foreign:
        surface = "placement"
        action = "adopt_version"
        payload = {}
        subject_ref = "d1"
        user_id = "u1"
        correction_scope = "file"
        bulk_member_refs = ()

    with pytest.raises(UnroutedSurface):
        _apply(p11_conn, Foreign())
    assert "adopt_version" not in P11_ACTIONS


def test_a_p11_action_on_a_p11_surface_is_not_refused(p11_conn):
    # The twin that keeps both guards honest: a guard that always fires passes
    # every test above.
    _record_d1(p11_conn)
    assert _apply(p11_conn, p13.accept()) == ()


# --- what the receiver authors, and what it does not -------------------------------

def test_an_acceptance_records_a_correction_and_authors_no_new_decision(p11_conn):
    _record_d1(p11_conn)
    ids = _apply(p11_conn, p13.accept())
    assert ids == ()
    row = _last_event(p11_conn)
    assert row["polarity"] == "accept"
    assert row["correction_scope"] == "file"
    assert row["user_id"] == "u1"


def test_a_rejection_is_a_negative_example_at_the_scope_the_user_chose(p11_conn):
    _record_d1(p11_conn)
    _apply(p11_conn, p13.reject())
    row = _last_event(p11_conn)
    assert row["polarity"] == "reject"
    assert row["correction_scope"] == "node"
    assert "n-course" in row["basis_key"]


def test_changing_a_destination_authors_a_new_decision(p11_conn):
    # The decision the user is revising must EXIST before it can be superseded:
    # `mark_superseded` raises `KeyError` on an unknown `old_id`. P13's
    # `subject_ref` on a placement surface is that decision's record id.
    _record_d1(p11_conn)
    ids = _apply(p11_conn, p13.change_destination())
    assert len(ids) == 1
    row = p11_conn.execute(
        "SELECT superseded_by, supersede_reason FROM placement_decisions "
        "WHERE record_id = 'd1'").fetchone()
    assert row["superseded_by"] == ids[0]
    assert "change_destination" in row["supersede_reason"]


def test_changing_a_destination_with_no_prior_decision_supersedes_nothing(p11_conn):
    # A first decision about a subject has no predecessor. Passing the action's
    # `subject_ref` through as `supersedes` regardless would hand
    # `mark_superseded` an id that is not in the table.
    ids = _apply(p11_conn, p13.change_destination())
    assert len(ids) == 1
    row = p11_conn.execute(
        "SELECT supersedes FROM placement_decisions WHERE record_id = ?",
        (ids[0],)).fetchone()
    assert row["supersedes"] is None


def test_deferring_records_the_action_and_decides_nothing(p11_conn):
    ids = _apply(p11_conn, p13.defer())
    assert ids == ()
    assert "defer" in _last_event(p11_conn)["explanation"]


def test_a_deferral_is_recorded_but_is_never_an_acceptance(p11_conn):
    # "Not yet" is not "yes". A deferral written with `polarity = accept` is a
    # value meaning the opposite of what it says: `suppressed_nodes` would read
    # it as a positive example and §8.7's store would hold a preference the user
    # never expressed. The accept case beside it is what proves the column is
    # written at all, so the null below is a decision rather than an omission.
    _record_d1(p11_conn)
    _apply(p11_conn, p13.defer())
    assert _last_event(p11_conn)["polarity"] is None
    _apply(p11_conn, p13.accept())
    assert _last_event(p11_conn)["polarity"] == "accept"


def test_creating_a_custom_folder_routes_to_p10_and_mints_nothing(p11_conn):
    # §7.10, §8.8: a folder the USER adds is a tree edit that opens a draft plan
    # version. It is not the model inventing a destination, and it is not P11's.
    action = p13.create_custom_folder()
    assert routes_to_p10(action) is True
    ids = _apply(p11_conn, action)
    assert ids == ()
    nodes = p11_conn.execute(
        "SELECT count(*) AS c FROM placement_index_entries").fetchone()
    assert nodes["c"] == 0
    # The routing has to be READABLE, or "routed to P10" is a claim with no
    # trace: a receiver that silently swallowed the gesture would pass both
    # assertions above, because both are about things that did NOT happen.
    assert "P10" in _last_event(p11_conn)["explanation"]


def test_an_action_p11_does_own_is_not_routed_to_p10(p11_conn):
    # The negative twin: `routes_to_p10` returning True for everything would send
    # every gesture away and still pass the test above.
    for build in (p13.accept, p13.reject, p13.change_destination, p13.defer):
        assert routes_to_p10(build()) is False


# --- bulk ---------------------------------------------------------------------------

def test_a_bulk_acceptance_enumerates_every_member(p11_conn):
    # P13 SPEC:271-272: "every member enumerated, never a filter expression".
    # A filter cannot be re-read later to say which files a reversal applies to,
    # so the enumeration reaches the log and an empty one is refused.
    _apply(p11_conn, p13.accept_bulk())
    explanation = _last_event(p11_conn)["explanation"]
    for member in ("f-a", "f-b", "f-c"):
        assert member in explanation
    with pytest.raises(BulkMembersRequired):
        _apply(p11_conn, p13.accept_bulk(bulk_member_refs=()))


def test_a_bulk_at_file_scope_is_one_correction_per_file(p11_conn):
    # The scope decides how many corrections a bulk becomes, because the scope
    # decides what was learned. At `file` scope the user made one statement per
    # file; at `corpus` scope they made one statement about the corpus, and
    # writing it three times would be three copies of one fact.
    _apply(p11_conn, p13.accept_bulk(correction_scope="file"))
    subjects = [row["correction_subject"] for row in p11_conn.execute(
        "SELECT correction_subject FROM events WHERE correction_scope = 'file'")]
    assert sorted(subjects) == ["f-a", "f-b", "f-c"]
    _apply(p11_conn, p13.accept_bulk())
    corpus = p11_conn.execute(
        "SELECT correction_subject FROM events WHERE correction_scope = 'corpus'"
    ).fetchall()
    assert [row["correction_subject"] for row in corpus] == ["set-1"]


def test_a_bulk_with_no_members_is_refused_before_anything_is_written(p11_conn):
    with pytest.raises(BulkMembersRequired):
        _apply(p11_conn, p13.accept_bulk(bulk_member_refs=()))
    assert p11_conn.execute(
        "SELECT count(*) AS c FROM events").fetchone()["c"] == 0


# --- scope ---------------------------------------------------------------------------

def test_the_scope_is_the_users_and_p11_widens_none():
    scope, subject = correction_scope_of(p13.reject())
    assert (scope, subject) == ("node", "n-course")
    scope, subject = correction_scope_of(p13.accept())
    assert scope == "file"


def test_a_file_scoped_correction_about_a_group_subject_refuses(p11_conn):
    # §8.7's subject must be the thing the scope names. Reading a group id as a
    # file id would store one user's decision under another's name, and the
    # suppression query would read it back for the wrong file.
    action = p13.reject(correction_scope="file")
    group = _decision(decision_id="dg", subject=Subject(
        kind=v.GROUP, file_id=None, content_hash=None, group_id="g1",
        member_file_ids=("f1",)))
    with pytest.raises(ScopeSubjectRequired):
        _apply(p11_conn, action, decision_factory=lambda **kw: group)


def test_every_action_carries_the_state_the_user_was_actually_shown(p11_conn):
    # §8.2, §8.4, §8.7: `presented_state_ref` is what makes a correction
    # interpretable later, because it says what was on screen under the
    # redaction policy then in force.
    for build in p13.RECORDED_ACTIONS:
        assert build().presented_state_ref


# --- the round trip: what is written here is what §8.7 reads back --------------------

def test_a_rejection_recorded_here_is_read_back_by_the_suppression_query(p11_conn):
    # The defect this exists to catch: a correction written under a key the
    # reader never queries. §8.7's whole promise -- "the same attractive-but-wrong
    # destination is not resurfaced" -- is false if the write and the read
    # disagree about the subject, and both sides pass their own unit tests.
    _record_d1(p11_conn)
    _apply(p11_conn, p13.reject())
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course", "n-course-shared"),
                            scopes=("node",))
    assert [hit.node_id for hit in hits] == ["n-course"]


def test_an_acceptance_suppresses_nothing(p11_conn):
    # The negative twin. A suppression query that returned every recorded action
    # would pass the test above and block every destination the user approved.
    _record_d1(p11_conn)
    _apply(p11_conn, p13.accept())
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n1", "n-course"), scopes=("file",)) == ()


def test_changing_a_destination_rejects_the_node_left_behind(p11_conn):
    # A `change_destination` is a rejection OF THE NODE THE USER MOVED AWAY FROM.
    # Keying the negative example on the payload's node instead would suppress
    # the destination the user just chose -- a value meaning the opposite of
    # what it says, and one that only shows up on the next run.
    _record_d1(p11_conn)
    _apply(p11_conn, p13.change_destination())
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n1", "n-course-alt"), scopes=("file",))
    assert [hit.node_id for hit in hits] == ["n1"]


def test_a_residual_rejection_does_not_suppress_a_placement_candidate(p11_conn):
    # `proposal_class` separates the two stores. A rejection collected on a
    # residual surface is a residual fact; read as a placement fact it would
    # suppress a node the user never saw in the placement pass.
    _record_d1(p11_conn)
    _apply(p11_conn, p13.reject(surface="residual_file"))
    assert suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("node",)) == ()
    hits = suppressed_nodes(p11_conn, subject_ref="file:f1:h1",
                            node_ids=("n-course",), scopes=("node",),
                            proposal_class=v.RESIDUAL)
    assert [hit.node_id for hit in hits] == ["n-course"]


# --- the boundary --------------------------------------------------------------------

def test_placement_never_imports_the_p13_fixture():
    import ast
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "src" / "placement"
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and "p13" in (node.module or ""):
                raise AssertionError(f"{path.name}:{node.lineno} imports P13's fixture")


def test_the_receiver_is_reachable_from_the_review_path():
    # Every event this module writes goes through P11's own append helpers, so a
    # second writer of `placement_review_decision` would be a second §8.2 voice.
    from p11.test_p11_groups import _placement_sources_calling

    assert _placement_sources_calling("review_decision") <= {
        "review.py", "learning.py"}
    assert json.dumps(sorted(P11_ACTIONS))
