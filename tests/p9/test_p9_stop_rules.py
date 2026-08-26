# tests/p9/test_p9_stop_rules.py
"""P9 Task 7 — the five stop rules that run before a model is ever called.

SR1, SR2, SR3, SR4 and SR6 are all decidable from the graph, the injected conflict
oracle and P1's learning records. Each of them returns before a dossier is
assembled and before `run_call`, which is the point: a group that cannot be formed
should not cost a model call to find that out.

SR5 is NOT here. It means P8 could not explain the group with valid citations, and
that is only knowable after `run_call` returns. Evaluating it before the call would
be P9 deciding what P8 was going to say.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from database_agent.events import append_event
from grouping.config import GroupingLimits
from grouping.graph import build_graph, evaluate_stop_rules
from grouping.retrieval import Neighbor, Neighborhood
from grouping.records import Conflict
from grouping.seeds import Seed
from grouping.vocabulary import (
    COMPATIBLE_DOCUMENT_TYPE,
    MUTUAL_SEMANTIC_RETRIEVAL,
    NO_GROUP,
    SHARED_VALIDATED_FACT,
    SR1,
    SR2,
    SR3,
    SR4,
    SR5,
    SR6,
    STRONGLY_IDENTIFIED_FILE,
    TENTATIVE_DISCOVERY,
)

T0 = "2026-08-27T00:00:00Z"
SEED_FILE = "file-seed"
GROUP = "group-1"
BASIS = "subject=BUSIB 4300"


@pytest.fixture()
def learning_conn(conn):
    create_schema(conn)
    return conn


def _limits(**overrides) -> GroupingLimits:
    values = dict(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=3,
        minimum_independent_anchors=1,
    )
    values.update(overrides)
    return GroupingLimits(**values)


def _seed() -> Seed:
    return Seed(
        seed_kind=STRONGLY_IDENTIFIED_FILE, file_id=SEED_FILE,
        content_hash="h-seed", field_key="subject", value="BUSIB 4300",
        reliability_state="validated", observation_key="sha256:seed-fact",
        basis=None,
    )


def _neighbor(file_id, channel, *, anchors=False, detail=BASIS) -> Neighbor:
    return Neighbor(
        file_id=file_id, content_hash=f"h-{file_id}", channel=channel,
        anchors=anchors, evidence_ref="sha256:edge-evidence", detail=detail,
    )


def _graph(*neighbors, limits=None):
    return build_graph(
        group_id=GROUP,
        neighborhood=Neighborhood(seed=_seed(), neighbors=tuple(neighbors)),
        limits=limits or _limits(),
        duplicate_or_version=None,
        created_at=T0,
    )


def _evaluate(conn, graph, *, limits=None, conflicts=None, basis_key=BASIS,
              seed_anchors=False):
    return evaluate_stop_rules(
        conn, graph,
        limits=limits or _limits(),
        conflicts_for=conflicts if conflicts is not None else (lambda files: ()),
        basis_key=basis_key,
        seed_anchors=seed_anchors,
    )


def _reject(conn, *, basis_key=BASIS, proposal_class="group"):
    append_event(
        conn,
        event_type="user group decision",
        file_id=None,
        content_hash=None,
        subsystem="P9",
        component_version="p9-fixture",
        observed_at=T0,
        explanation="the user rejected this grouping",
        user_id="user-1",
        correction_scope="group",
        correction_subject=GROUP,
        polarity="reject",
        proposal_class=proposal_class,
        basis_key=basis_key,
    )


# --- nothing fires ---------------------------------------------------------------


def test_a_graph_with_an_anchor_and_a_real_bridge_fires_nothing(learning_conn):
    graph = _graph(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor("file-b", COMPATIBLE_DOCUMENT_TYPE, detail="pdf~pdf"),
    )
    assert _evaluate(learning_conn, graph) is None


# --- SR1: no valid anchor --------------------------------------------------------


def test_sr1_fires_when_no_edge_anchors(learning_conn):
    graph = _graph(_neighbor("file-a", COMPATIBLE_DOCUMENT_TYPE, detail="pdf~pdf"))
    outcome = _evaluate(learning_conn, graph)
    assert outcome.rules_fired == (SR1,)
    assert outcome.group_id == GROUP


def test_a_seed_with_its_own_direct_fact_anchors_itself(learning_conn):
    """A group of one, seeded by a validated fact, has an anchor even though no
    edge points at it. Counting only edge endpoints would say a file cannot
    anchor itself, which is the opposite of what a strongly-identified seed is."""
    graph = _graph(_neighbor("file-a", COMPATIBLE_DOCUMENT_TYPE, detail="pdf~pdf"))
    assert _evaluate(learning_conn, graph, seed_anchors=False).rules_fired == (SR1,)
    assert _evaluate(learning_conn, graph, seed_anchors=True) is None


def test_sr1_is_zero_anchors_and_not_the_support_bar(learning_conn):
    """SR1 stops the group forming at all. `minimum_independent_anchors` decides
    whether a formed group may become `supported`. Conflating them made a
    one-anchor group vanish instead of waiting for confirmation."""
    from grouping.graph import meets_support_bar

    graph = _graph(_neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True))
    strict = _limits(minimum_independent_anchors=2)
    assert _evaluate(learning_conn, graph, limits=strict) is None
    assert meets_support_bar(graph, limits=strict, seed_anchors=False) is False
    assert meets_support_bar(graph, limits=_limits(minimum_independent_anchors=1),
                             seed_anchors=False) is True
    assert meets_support_bar(graph, limits=strict, seed_anchors=True) is True


def test_a_sparse_anchorless_group_is_tentative_discovery_not_no_group(learning_conn):
    """SS4.9 permits an anchorless group to be shown "only as tentative discovery
    candidates, if at all". That is SR1 ALONE; anything else fired alongside it is
    a positive reason not to form the group, and outranks the permission."""
    graph = _graph(_neighbor("file-a", COMPATIBLE_DOCUMENT_TYPE, detail="pdf~pdf"))
    assert _evaluate(learning_conn, graph).outcome == TENTATIVE_DISCOVERY

    with_conflict = _evaluate(
        learning_conn, graph,
        conflicts=lambda files: (Conflict(
            kind="term", competing_values=("Spring", "Fall"), file_ids=("file-a",)),),
    )
    assert set(with_conflict.rules_fired) == {SR1, SR4}
    assert with_conflict.outcome == NO_GROUP


# --- SR2: the graph is connected only by embeddings ------------------------------


def test_sr2_fires_when_every_surviving_edge_is_semantic(learning_conn):
    """An embedding can propose a neighbour and can never establish membership.
    A neighbourhood connected only by mutual semantic retrieval yields no group
    even when a recorded P8 fixture would have called it coherent."""
    graph = _graph(
        _neighbor("file-a", MUTUAL_SEMANTIC_RETRIEVAL, detail="sem-a"),
        _neighbor("file-b", MUTUAL_SEMANTIC_RETRIEVAL, detail="sem-b"),
    )
    outcome = _evaluate(learning_conn, graph)
    assert SR2 in outcome.rules_fired
    assert outcome.outcome == NO_GROUP


def test_sr2_does_not_fire_when_one_non_semantic_edge_survives(learning_conn):
    graph = _graph(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor("file-b", MUTUAL_SEMANTIC_RETRIEVAL, detail="sem-b"),
    )
    assert _evaluate(learning_conn, graph) is None


def test_a_suppressed_hub_edge_does_not_save_the_graph_from_sr2(learning_conn):
    """A hub-suppressed edge is not a connection. Counting it would let a bridge
    the product decided means nothing rescue a graph that is otherwise vectors."""
    graph = _graph(
        *[_neighbor(f"file-{n}", COMPATIBLE_DOCUMENT_TYPE, detail="columbia.edu")
          for n in range(3)],
        _neighbor("file-x", MUTUAL_SEMANTIC_RETRIEVAL, detail="sem-x"),
        limits=_limits(generic_hub_frequency=3),
    )
    outcome = _evaluate(learning_conn, graph, limits=_limits(generic_hub_frequency=3))
    assert SR2 in outcome.rules_fired


# --- SR3: one high-frequency entity is the only bridge ---------------------------


def test_sr3_fires_when_every_bridge_is_a_suppressed_hub(learning_conn):
    graph = _graph(
        *[_neighbor(f"file-{n}", COMPATIBLE_DOCUMENT_TYPE, detail="columbia.edu")
          for n in range(3)],
        limits=_limits(generic_hub_frequency=3),
    )
    outcome = _evaluate(learning_conn, graph, limits=_limits(generic_hub_frequency=3))
    assert SR3 in outcome.rules_fired
    assert outcome.outcome == NO_GROUP


def test_sr3_does_not_fire_when_a_real_bridge_survives(learning_conn):
    graph = _graph(
        *[_neighbor(f"file-{n}", COMPATIBLE_DOCUMENT_TYPE, detail="columbia.edu")
          for n in range(3)],
        _neighbor("file-anchor", SHARED_VALIDATED_FACT, anchors=True),
        limits=_limits(generic_hub_frequency=3),
    )
    outcome = _evaluate(learning_conn, graph, limits=_limits(generic_hub_frequency=3))
    assert outcome is None


# --- SR4: irreconcilable facts ---------------------------------------------------


def test_sr4_fires_from_the_injected_conflict_oracle(learning_conn):
    """P9 does not decide that `Spring 2026` and `Fall 2026` are irreconcilable.
    A course code alone must not merge two semesters, and what makes two terms
    incompatible is domain knowledge P9 receives."""
    graph = _graph(_neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True))
    outcome = _evaluate(
        learning_conn, graph,
        conflicts=lambda files: (Conflict(
            kind="term", competing_values=("Spring 2026", "Fall 2026"),
            file_ids=tuple(files)),),
    )
    assert outcome.rules_fired == (SR4,)
    assert outcome.outcome == NO_GROUP


def test_the_conflict_oracle_sees_every_node_in_the_graph(learning_conn):
    seen = []
    graph = _graph(
        _neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True),
        _neighbor("file-b", COMPATIBLE_DOCUMENT_TYPE, detail="pdf~pdf"),
    )

    def conflicts(files):
        seen.append(tuple(files))
        return ()

    _evaluate(learning_conn, graph, conflicts=conflicts)
    assert seen == [(SEED_FILE, "file-a", "file-b")]


# --- SR6: the user already rejected an equivalent proposal -----------------------


def test_sr6_fires_on_a_standing_reject_for_the_same_basis(learning_conn):
    graph = _graph(_neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True))
    assert _evaluate(learning_conn, graph) is None
    _reject(learning_conn)
    outcome = _evaluate(learning_conn, graph)
    assert outcome.rules_fired == (SR6,)
    assert outcome.outcome == NO_GROUP


def test_sr6_does_not_fire_for_a_different_basis(learning_conn):
    graph = _graph(_neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True))
    _reject(learning_conn, basis_key="subject=ECON 1105")
    assert _evaluate(learning_conn, graph) is None


def test_sr6_does_not_fire_for_a_membership_rejection(learning_conn):
    """`proposal_class` separates a rejected GROUP from a rejected MEMBERSHIP.
    One file the user pushed out of a group does not reject the group."""
    graph = _graph(_neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True))
    _reject(learning_conn, proposal_class="membership")
    assert _evaluate(learning_conn, graph) is None


def test_p9_and_p8_read_the_same_rejection_the_same_way(learning_conn):
    """P1 owns the query and both parts consume it. Two readings of one row that
    disagree would mean a proposal P8 refuses to call about and P9 keeps surfacing.
    """
    from llm_harness.eligibility import suppressed_by_learning

    graph = _graph(_neighbor("file-a", SHARED_VALIDATED_FACT, anchors=True))
    _reject(learning_conn)
    assert suppressed_by_learning(
        learning_conn, scope="group", subject_id=GROUP,
        proposal_class="group", basis_key=BASIS,
    ) is True
    assert SR6 in _evaluate(learning_conn, graph).rules_fired


# --- SR5 is not a pre-model rule -------------------------------------------------


def test_sr5_is_never_returned_before_a_model_call(learning_conn):
    """SR5 means P8 could not explain the group with valid citations. Deciding it
    here would be P9 predicting what P8 was going to say."""
    import ast
    import pathlib

    import grouping.graph as module

    graph = _graph(
        *[_neighbor(f"file-{n}", MUTUAL_SEMANTIC_RETRIEVAL, detail=f"sem-{n}")
          for n in range(3)])
    outcome = _evaluate(
        learning_conn, graph,
        conflicts=lambda files: (Conflict(
            kind="term", competing_values=("a", "b"), file_ids=tuple(files)),),
    )
    assert SR5 not in outcome.rules_fired

    names = {
        node.id for node in ast.walk(ast.parse(pathlib.Path(module.__file__).read_text()))
        if isinstance(node, ast.Name)
    }
    assert SR5 not in {name for name in names}


def test_every_fired_rule_carries_the_evidence_that_fired_it(learning_conn):
    graph = _graph(_neighbor("file-a", COMPATIBLE_DOCUMENT_TYPE, detail="pdf~pdf"))
    outcome = _evaluate(
        learning_conn, graph,
        conflicts=lambda files: (Conflict(
            kind="term", competing_values=("a", "b"), file_ids=("file-a",)),),
    )
    assert outcome.evidence_refs
    assert all(isinstance(ref, str) and ref for ref in outcome.evidence_refs)
