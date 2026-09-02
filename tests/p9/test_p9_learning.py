# tests/p9/test_p9_learning.py
"""P9 Task 11 — the P13 back-edge, received structurally and never imported.

P13 is specification only. `src/grouping/` may never import its test fixture, and
no source stub impersonates it: a stub in `src/` would be P9 deciding what a user
action looks like, which is P13's to say. The receiver takes a protocol-shaped
value, and a test proves the package imports nothing from `tests/`.

Two things ride on every action.

**The plan-version decision**, through Task 9's acceptance table. Accepting in
version 2 and rejecting in version 3 leaves one group and two opinions.

**The scoped learning record**, through P1. §8.7 stores a rejection WITH its
evidence, and §4.9 SR6 reads it — which is why a rejection recorded under one plan
version still stops the same attractive-but-incorrect grouping resurfacing under
the next. The scope is carried and never inferred: guessing `corpus` from one file
is the failure the six scopes exist to prevent.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from database_agent.learning import learning_records
from grouping.acceptance import group_state_as_of, membership_review_state_as_of
from grouping.graph import evaluate_stop_rules
from grouping.learning import (
    ReviewActionRefused,
    apply_review_action,
    group_basis_key,
    membership_basis_key,
)
from grouping.records import AnchorFact, Group
from grouping.schema import create_grouping_schema
from grouping.store import record_group
from grouping.vocabulary import (
    ACCEPTED,
    CANDIDATE,
    DEFERRED,
    REJECTED,
    RULES,
    STRONGLY_IDENTIFIED_FILE,
    SUPPORTED,
    USER_ACCEPTED,
    USER_EXCLUDED_FROM_PACKET,
    USER_REJECTED,
)
from p9.p13_fixtures import (
    GROUP_PLAN_SURFACE,
    accept_group,
    defer_group,
    exclude_member,
    reject_group,
)

T0 = "2026-08-27T00:00:00Z"
GROUP = "fixture-course-group"
KEY = "sha256:" + "a" * 64


@pytest.fixture()
def review_conn(conn):
    create_schema(conn)
    create_grouping_schema(conn)
    record_group(conn, _group())
    return conn


def _group(**overrides) -> Group:
    values = dict(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="PHYS1401 course materials",
        anchor_facts=(
            AnchorFact(field="subject", value="PHYS1401", file_ids=("lecture-08",),
                       reliability_state="validated", observation_key=KEY),
            AnchorFact(field="term", value="Spring 2026", file_ids=("midterm",),
                       reliability_state="validated", observation_key=KEY),
        ),
        pre_model_signals={}, anchor_count=2, coherence_verdict=None,
        coherence_citations=(), group_category=None, display_label=None,
        label_source=None, conflicts=(), stop_rule_hits=(), state=SUPPORTED,
        sensitivity_state="none", dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0)
    values.update(overrides)
    return Group(**values)


def _bare(**overrides):
    """A P13-shaped value that carries no validation of its own, so the receiver
    is the thing under test."""
    from dataclasses import dataclass, field, make_dataclass

    values = dict(
        action="accept", plan_version_id="plan-2", group_id=GROUP,
        membership_id=None, basis="the user accepted it",
        user_edited_label=None, decided_at=T0, user_id="user-1",
        correction_scope="group", presented_state_ref="presented-1",
        surface=GROUP_PLAN_SURFACE,
    )
    values.update(overrides)
    return type("BareAction", (), values)()


def _events(conn):
    return list(conn.execute(
        "SELECT * FROM events WHERE event_type = 'user group decision' "
        "ORDER BY event_id"))


# --- the decision lands in the plan version --------------------------------------


def test_accept_records_the_plan_version_decision(review_conn):
    written = apply_review_action(review_conn, accept_group(plan_version_id="plan-2"))
    assert written
    assert group_state_as_of(
        review_conn, group_id=GROUP, plan_version_id="plan-2") == ACCEPTED


def test_accept_in_one_version_and_reject_in_the_next_leaves_one_group(review_conn):
    apply_review_action(review_conn, accept_group(plan_version_id="plan-2"))
    apply_review_action(review_conn, reject_group(plan_version_id="plan-3"))
    assert group_state_as_of(
        review_conn, group_id=GROUP, plan_version_id="plan-2") == ACCEPTED
    assert group_state_as_of(
        review_conn, group_id=GROUP, plan_version_id="plan-3") == REJECTED
    assert review_conn.execute(
        "SELECT count(*) AS c FROM groups").fetchone()["c"] == 1


def test_defer_is_a_plan_opinion_and_not_a_lifecycle_state(review_conn):
    apply_review_action(review_conn, defer_group(plan_version_id="plan-2"))
    assert group_state_as_of(
        review_conn, group_id=GROUP, plan_version_id="plan-2") == SUPPORTED
    assert review_conn.execute(
        "SELECT acceptance FROM group_acceptance").fetchone()["acceptance"] == DEFERRED


def test_an_edit_records_the_user_label_without_touching_the_proposal(review_conn):
    from p9.p13_fixtures import accept_group as base

    apply_review_action(review_conn, base(
        action="rename", user_edited_label="Physics I", plan_version_id="plan-2",
        basis="the user renamed the group"))
    row = review_conn.execute(
        "SELECT user_edited_label, review_state FROM group_acceptance").fetchone()
    assert row["user_edited_label"] == "Physics I"
    assert row["review_state"] == USER_ACCEPTED
    assert review_conn.execute(
        "SELECT display_label FROM groups").fetchone()["display_label"] is None


def test_excluding_one_member_is_scoped_to_that_membership(review_conn):
    apply_review_action(review_conn, exclude_member(plan_version_id="plan-2"))
    assert membership_review_state_as_of(
        review_conn, membership_id="fixture-membership",
        plan_version_id="plan-2") == USER_EXCLUDED_FROM_PACKET
    assert group_state_as_of(
        review_conn, group_id=GROUP, plan_version_id="plan-2") == SUPPORTED


def test_a_rejection_records_the_user_rejected_review_state(review_conn):
    apply_review_action(review_conn, reject_group(plan_version_id="plan-2"))
    assert review_conn.execute(
        "SELECT review_state FROM group_acceptance").fetchone()[
            "review_state"] == USER_REJECTED


# --- the learning record, scoped and evidence-bearing ----------------------------


def test_every_action_appends_one_scoped_user_group_decision(review_conn):
    apply_review_action(review_conn, accept_group(plan_version_id="plan-2"))
    events = _events(review_conn)
    assert len(events) == 1
    event = events[0]
    assert event["subsystem"] == "P9"
    assert event["user_id"] == "user-1"
    assert event["correction_scope"] == "group"
    assert event["correction_subject"] == GROUP
    assert event["polarity"] == "accept"
    assert event["proposal_class"] == "group"
    assert event["basis_key"] == group_basis_key(_group())
    assert "presented-1" in event["explanation"]


def test_a_rejection_is_the_record_sr6_reads(review_conn):
    """The whole point of the learning store: a rejection under one plan version
    stops the same grouping resurfacing under the next."""
    group = _group()
    apply_review_action(review_conn, reject_group(plan_version_id="plan-2"))
    rows = learning_records(review_conn, "group", GROUP)
    assert [row["polarity"] for row in rows] == ["reject"]
    assert rows[0]["basis_key"] == group_basis_key(group)


def test_the_basis_key_sr6_matches_is_the_one_this_module_publishes(review_conn):
    """Two spellings of "the same proposal" would mean a rejection the user made
    and a rejection SR6 looks for that never meet."""
    from grouping.graph import build_graph
    from grouping.retrieval import Neighbor, Neighborhood
    from grouping.seeds import Seed
    from grouping.vocabulary import SHARED_VALIDATED_FACT, SR6

    group = _group()
    apply_review_action(review_conn, reject_group(plan_version_id="plan-2"))
    graph = build_graph(
        group_id=GROUP,
        neighborhood=Neighborhood(
            seed=Seed(seed_kind=STRONGLY_IDENTIFIED_FILE, file_id="lecture-08",
                      content_hash="h", field_key="subject", value="PHYS1401",
                      reliability_state="validated", observation_key=KEY,
                      basis=None),
            neighbors=(Neighbor(
                file_id="midterm", content_hash="h2",
                channel=SHARED_VALIDATED_FACT, anchors=True, evidence_ref=KEY,
                detail="subject=PHYS1401"),)),
        limits=_limits(), duplicate_or_version=None, created_at=T0)
    outcome = evaluate_stop_rules(
        review_conn, graph, limits=_limits(),
        conflicts_for=lambda files: (), basis_key=group_basis_key(group),
        seed_anchors=True)
    assert outcome is not None
    assert SR6 in outcome.rules_fired


def _limits():
    from grouping.config import GroupingLimits

    return GroupingLimits(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)


def test_a_membership_rejection_uses_its_own_equivalence_class(review_conn):
    apply_review_action(review_conn, exclude_member(plan_version_id="plan-2"))
    event = _events(review_conn)[0]
    assert event["proposal_class"] == "membership"
    assert event["basis_key"] == membership_basis_key(
        GROUP, "fixture-membership")
    assert event["basis_key"] != group_basis_key(_group())


def test_the_group_basis_key_is_order_independent():
    """`anchor_facts` is a list and the same two facts can arrive either way
    round. Two orderings producing two keys would be two proposals."""
    import dataclasses

    group = _group()
    flipped = dataclasses.replace(
        group, anchor_facts=tuple(reversed(group.anchor_facts)))
    assert group_basis_key(group) == group_basis_key(flipped)


# --- what P9 refuses -------------------------------------------------------------


def test_an_action_from_another_surface_is_refused(review_conn):
    with pytest.raises(ReviewActionRefused):
        apply_review_action(review_conn, accept_group(surface="node_plan"))
    assert _events(review_conn) == []


@pytest.mark.parametrize(
    "blank", ["user_id", "correction_scope", "presented_state_ref",
              "plan_version_id", "basis", "decided_at"])
def test_a_missing_carried_field_is_refused_and_never_inferred(review_conn, blank):
    """P9 never guesses `corpus`. Teaching the engine from one file that every
    file like it belongs there is the §8.7 failure the six scopes prevent.

    Sent through the structural stand-in, not the fixture: the fixture refuses a
    blank field at construction, so testing through it would prove the fixture
    works and say nothing about the receiver.
    """
    with pytest.raises(ReviewActionRefused) as excinfo:
        apply_review_action(review_conn, _bare(**{blank: ""}))
    assert blank in str(excinfo.value)
    assert _events(review_conn) == []
    assert review_conn.execute(
        "SELECT count(*) AS c FROM group_acceptance").fetchone()["c"] == 0


def test_an_unknown_correction_scope_is_refused_by_p1(review_conn):
    """P1 owns which scopes exist. P9 requires the field and does not keep a
    second copy of the vocabulary, which is how two copies drift."""
    with pytest.raises(Exception):
        apply_review_action(review_conn, _bare(correction_scope="packet"))
    assert _events(review_conn) == []
    assert review_conn.execute(
        "SELECT count(*) AS c FROM group_acceptance").fetchone()["c"] == 0


def test_the_decision_and_the_learning_record_are_one_write(review_conn, monkeypatch):
    """A plan-version acceptance with no learning record is a rejection SR6 will
    never see, and the same grouping resurfaces in the next version."""
    import grouping.learning as module

    def boom(*_a, **_k):
        raise RuntimeError("the event append failed")

    monkeypatch.setattr(module, "append_event", boom)
    with pytest.raises(RuntimeError):
        apply_review_action(review_conn, reject_group(plan_version_id="plan-2"))
    assert review_conn.execute(
        "SELECT count(*) AS c FROM group_acceptance").fetchone()["c"] == 0


def test_a_bulk_decision_arrives_as_one_action_per_subject(review_conn):
    """A collapsed action over a set could not say which subject a later reversal
    applies to."""
    import inspect

    parameters = inspect.signature(apply_review_action).parameters
    assert list(parameters) == ["conn", "action"]
    first = apply_review_action(review_conn, exclude_member(
        membership_id="m-1", plan_version_id="plan-2"))
    second = apply_review_action(review_conn, exclude_member(
        membership_id="m-2", plan_version_id="plan-2"))
    assert first != second
    assert len(_events(review_conn)) == 2


# --- the back edge is a boundary, not an import ----------------------------------


def test_no_source_module_imports_p13_or_its_fixture():
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    offenders = []
    for path in sorted(root.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if "p13" in name.lower() or name.startswith("tests"):
                    offenders.append(f"{path.name}:{node.lineno}:{name}")
    assert offenders == [], offenders


def test_the_receiver_takes_any_shape_with_the_published_fields(review_conn):
    """Structural, not nominal. When P13 ships, only the test factory changes."""
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class NotTheFixture:
        action: str = "accept"
        plan_version_id: str = "plan-2"
        group_id: str = GROUP
        membership_id: str | None = None
        basis: str = "a P13 record P9 has never seen"
        user_edited_label: str | None = None
        decided_at: str = T0
        user_id: str = "user-1"
        correction_scope: str = "group"
        presented_state_ref: str = "presented-1"
        surface: str = GROUP_PLAN_SURFACE

    apply_review_action(review_conn, NotTheFixture())
    assert group_state_as_of(
        review_conn, group_id=GROUP, plan_version_id="plan-2") == ACCEPTED
