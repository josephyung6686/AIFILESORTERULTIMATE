# tests/p9/test_p9_store.py
"""P9 Task 9a — the writers for the six shared tables.

Everything here is shared across plan versions. A group, its memberships, its
dossier, its edges, its stop-rule outcome and its failure points are facts about a
corpus, not about a plan; `group_acceptance` is the one table that carries a
version, and it has its own module.

A record goes in and the same record comes back. That is the whole contract, and
it is worth a test because the round trip is where a tuple silently becomes a
list, a bool becomes a 1, and a frozen record acquires a shape its own validator
would have refused.

Supersede-never-overwrite: a revision appends and links. The triggers refuse a
DELETE and refuse an UPDATE of anything but the supersession columns, so a writer
that tried to correct a row in place would fail rather than lose the original.
"""
from __future__ import annotations

import sqlite3

import pytest

from grouping.records import (
    AnchorFact,
    Conflict,
    FailurePoint,
    Group,
    Membership,
    StopRuleOutcome,
    Support,
    TypedEdge,
)
from grouping.schema import create_grouping_schema
from grouping.store import (
    RecordAbsent,
    current_group,
    current_membership,
    edges_for_group,
    memberships_for_group,
    record_dossier,
    record_edges,
    record_failure_point,
    record_group,
    record_membership,
    record_stop_rule_outcome,
    stop_rule_outcome_for,
    stored_dossier,
)
from grouping.vocabulary import (
    CANDIDATE,
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    GRAPH,
    INCLUDED,
    LLM,
    NO_GROUP,
    RULES,
    SHARED_VALIDATED_FACT,
    SR1,
    STRONGLY_IDENTIFIED_FILE,
    SUPPORTED,
    VALIDATOR,
)

T0 = "2026-08-27T00:00:00Z"
T1 = "2026-08-27T01:00:00Z"
GROUP = "group-1"
KEY = "sha256:" + "c" * 64


@pytest.fixture()
def store_conn(conn):
    create_grouping_schema(conn)
    return conn


def _group(**overrides) -> Group:
    values = dict(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="subject=PHYS1401",
        anchor_facts=(AnchorFact(
            field="subject", value="PHYS1401", file_ids=("file-1",),
            reliability_state="validated", observation_key=KEY),),
        pre_model_signals={"anchor_count": 1}, anchor_count=1,
        coherence_verdict=None, coherence_citations=(), group_category=None,
        display_label=None, label_source=None,
        conflicts=(Conflict(kind="term", competing_values=("a", "b"),
                            file_ids=("file-1",)),),
        stop_rule_hits=(), state=CANDIDATE, sensitivity_state="none",
        dossier_id=None, llm_response_ref=None, validation_verdict_ref=None,
        created_by=RULES, created_at=T0,
    )
    values.update(overrides)
    return Group(**values)


def _membership(**overrides) -> Membership:
    values = dict(
        membership_id="membership-1", group_id=GROUP, file_id="file-2",
        content_hash="h-2", basis=CONTEXT_SUPPORTED,
        support=(Support(support_kind=SHARED_VALIDATED_FACT, observation_key=KEY,
                         quote_or_field="subject", location="heading",
                         edge_ref=None),),
        decision=INCLUDED, decision_source=LLM, insufficient_evidence=False,
        insufficiency_statement=None, conflicts=(), outlier_flag="none",
        validation_verdict_ref=None, created_at=T0,
    )
    values.update(overrides)
    return Membership(**values)


def _edge(edge_id="edge-1", **overrides) -> TypedEdge:
    values = dict(
        edge_id=edge_id, from_file_id="file-1", to_file_id="file-2",
        edge_type=SHARED_VALIDATED_FACT, evidence_ref=KEY, weight=None,
        bridge_entity_ref="subject=PHYS1401", hub_suppressed=False, created_at=T0,
    )
    values.update(overrides)
    return TypedEdge(**values)


# --- a record goes in and the same record comes back -----------------------------


def test_a_group_round_trips_unchanged(store_conn):
    group = _group()
    assert record_group(store_conn, group) == GROUP
    assert current_group(store_conn, GROUP) == group


def test_a_membership_round_trips_unchanged(store_conn):
    membership = _membership()
    record_membership(store_conn, membership)
    assert current_membership(store_conn, "membership-1") == membership
    assert memberships_for_group(store_conn, GROUP) == (membership,)


def test_a_direct_anchor_membership_round_trips_with_its_anchoring_support(store_conn):
    membership = _membership(
        membership_id="membership-anchor", basis=DIRECT_ANCHOR,
        support=(Support(support_kind=SHARED_VALIDATED_FACT, observation_key=KEY,
                         quote_or_field="subject", location="heading",
                         edge_ref=None),))
    record_membership(store_conn, membership)
    assert current_membership(store_conn, "membership-anchor") == membership


def test_edges_round_trip_and_keep_their_suppression_flag(store_conn):
    edges = (_edge("edge-1"), _edge("edge-2", to_file_id="file-3",
                                    hub_suppressed=True, weight=0.5))
    record_edges(store_conn, GROUP, edges)
    stored = edges_for_group(store_conn, GROUP)
    assert stored == edges
    assert [item.hub_suppressed for item in stored] == [False, True]
    assert stored[1].weight == 0.5


def test_a_stop_rule_outcome_round_trips(store_conn):
    outcome = StopRuleOutcome(
        group_id=GROUP, rules_fired=(SR1,), evidence_refs=(KEY,), outcome=NO_GROUP)
    record_stop_rule_outcome(store_conn, outcome, created_at=T0)
    assert stop_rule_outcome_for(store_conn, GROUP) == outcome


def test_a_failure_point_is_recorded_per_stage(store_conn):
    point = FailurePoint(
        group_id=GROUP, dossier_id=None, membership_id=None, stage=GRAPH,
        cause_code="hub_only_bridge", evidence_ref=KEY, detected_by=VALIDATOR)
    record_failure_point(store_conn, point, created_at=T0)
    assert store_conn.execute(
        "SELECT stage FROM group_failure_points").fetchone()["stage"] == GRAPH


def test_a_dossier_round_trips_by_its_fingerprint(store_conn):
    from grouping.fixtures import course_dossier_fixture

    dossier = course_dossier_fixture()
    record_dossier(store_conn, dossier)
    assert stored_dossier(store_conn, dossier.dossier_id) == dossier


def test_a_dossier_recorded_twice_is_one_row(store_conn):
    """The fingerprint is content-derived, so the same references assembled twice
    are the same dossier and not a conflict."""
    from grouping.fixtures import course_dossier_fixture

    dossier = course_dossier_fixture()
    record_dossier(store_conn, dossier)
    record_dossier(store_conn, dossier)
    assert store_conn.execute(
        "SELECT count(*) AS c FROM group_dossiers").fetchone()["c"] == 1


# --- absence is an error, never an empty record ----------------------------------


@pytest.mark.parametrize(
    ("reader", "kwargs"),
    [
        (current_group, {"group_id": "no-such-group"}),
        (current_membership, {"membership_id": "no-such-membership"}),
        (stored_dossier, {"dossier_id": "no-such-dossier"}),
    ],
)
def test_a_missing_record_raises_rather_than_returning_a_blank(
    store_conn, reader, kwargs,
):
    with pytest.raises(RecordAbsent):
        reader(store_conn, *kwargs.values())


def test_a_group_with_no_stop_rule_outcome_returns_none(store_conn):
    """No outcome is not the same as a missing record: most groups never fire a
    rule, and `None` says so without inventing an empty `rules_fired`."""
    record_group(store_conn, _group())
    assert stop_rule_outcome_for(store_conn, GROUP) is None


# --- supersede, never overwrite --------------------------------------------------


def test_a_revised_group_appends_and_links(store_conn):
    record_group(store_conn, _group())
    record_group(store_conn, _group(
        group_id="group-2", state=SUPPORTED, created_at=T1,
        supersedes=GROUP, supersede_reason="the model confirmed coherence"))
    assert current_group(store_conn, "group-2").state == SUPPORTED
    assert store_conn.execute(
        "SELECT superseded_by FROM groups WHERE group_id = ?", (GROUP,),
    ).fetchone()["superseded_by"] == "group-2"


def test_a_revision_naming_no_predecessor_is_refused(store_conn):
    with pytest.raises(RecordAbsent):
        record_group(store_conn, _group(
            group_id="group-2", supersedes="group-that-never-was",
            supersede_reason="none"))


def test_a_supersession_with_no_reason_is_refused(store_conn):
    record_group(store_conn, _group())
    with pytest.raises(ValueError):
        record_group(store_conn, _group(
            group_id="group-2", supersedes=GROUP, supersede_reason=None))


def test_updating_a_stored_group_in_place_is_refused(store_conn):
    record_group(store_conn, _group())
    with pytest.raises(sqlite3.IntegrityError):
        store_conn.execute(
            "UPDATE groups SET state = ? WHERE group_id = ?", (SUPPORTED, GROUP))


def test_deleting_a_stored_group_is_refused(store_conn):
    record_group(store_conn, _group())
    with pytest.raises(sqlite3.IntegrityError):
        store_conn.execute("DELETE FROM groups WHERE group_id = ?", (GROUP,))


# --- no destination, node, path or tree ------------------------------------------


def test_the_store_names_no_destination_concept():
    """P9 says which files belong together. Where they go is P10's and P11's, and
    a P9 writer carrying a path would be P9 deciding it. Checked over identifiers
    and string literals, since the docstrings have to be able to say the word."""
    import ast
    import pathlib

    import grouping.store as module

    banned = {"destination", "node_id", "folder_path", "tree", "template"}
    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    docstrings = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and body:
            first = body[0]
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docstrings.add(id(first.value))
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.lower() in banned:
            offenders.append(f"{node.lineno}:{node.id}")
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in docstrings):
            for word in banned:
                if word in node.value.lower():
                    offenders.append(f"{node.lineno}:{word}")
    assert offenders == [], offenders
