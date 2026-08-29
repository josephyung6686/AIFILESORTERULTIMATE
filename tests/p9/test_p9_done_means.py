# tests/p9/test_p9_done_means.py
"""P9 Task 15 — the two Done-means items nothing else in the suite covers.

**Done-means 3 (§4.6 reproduced exactly).** The design's own worked example, as a
test rather than as prose: two files that state the course directly are `included`
on direct evidence; the sparse homework is `uncertain` and `context-supported`
with a `pending-review` obligation; and NO course fact is written onto it. That
last clause is the one that matters — a group membership is not a fact about a
file, and writing one would make a semantic neighbour into a claim about the
document.

**Provenance: three event types, not two.** §8.2 says P9 appends `graph-edge
creation`, `group membership proposal` and `user group decision`. The first had no
producer, which is this project's named "reserved name with no writer" defect.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from facts.file_facts import facts_for_file
from grouping.acceptance import membership_review_state_as_of
from grouping.graph import build_graph
from grouping.retrieval import Neighbor, Neighborhood
from grouping.schema import create_grouping_schema
from grouping.seeds import Seed
from grouping.store import record_edges
from grouping.vocabulary import (
    CONTEXT_SUPPORTED,
    DIRECT_ANCHOR,
    INCLUDED,
    MUTUAL_SEMANTIC_RETRIEVAL,
    PENDING_REVIEW,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
    UNCERTAIN,
    USER_CREATED_STARTING_POINT,
)

T0 = "2026-08-27T00:00:00Z"
PLAN = "plan-2"


@pytest.fixture()
def p9_conn(conn):
    create_schema(conn)
    create_grouping_schema(conn)
    return conn


# --- Done-means 3: §4.6, exactly -------------------------------------------------


def test_the_course_example_is_reproduced_exactly(p9_conn):
    """`Lecture 08` and `Midterm Practice` are included on direct evidence.
    `HW 3` is uncertain and context-supported, and carries a pending review."""
    from grouping.fixtures import course_dossier_fixture
    from grouping.p8_seam import apply_p8_verdict
    from grouping.store import memberships_for_group, record_group
    from llm_harness.records import P8Verdict
    from llm_harness.vocabulary import (
        ACCEPT_CONTEXT_SUPPORTED,
        ACCEPT_DIRECT,
        CONTEXT_SUPPORTED_MEMBERSHIP,
        DIRECT_MEMBERSHIP,
    )

    from grouping.records import AnchorFact, Group
    from grouping.vocabulary import CANDIDATE, RULES

    dossier = course_dossier_fixture()
    group = Group(
        group_id=dossier.group_id, seed_ref="lecture-08", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis=dossier.proposed_basis, anchor_facts=dossier.key_facts,
        pre_model_signals={}, anchor_count=len(dossier.key_facts),
        coherence_verdict=None, coherence_citations=(), group_category=None,
        display_label=None, label_source=None, conflicts=(), stop_rule_hits=(),
        state=CANDIDATE, sensitivity_state="none", dossier_id=dossier.dossier_id,
        llm_response_ref=None, validation_verdict_ref=None, created_by=RULES,
        created_at=T0)
    record_group(p9_conn, group)

    def _verdict(outcome, disposition, ref):
        return P8Verdict(
            verdict_id=ref, dossier_id=dossier.dossier_id, claim_ref="members",
            outcome=outcome, disposition=disposition, reasons=(), may_propose=True,
            requires_review=outcome == ACCEPT_CONTEXT_SUPPORTED,
            citations_checked=(), scope="group", validator_version="P8/0.1.0",
            policy_version="policy-1", plan_version=None)

    apply_p8_verdict(
        p9_conn, group=group, dossier=dossier,
        result=_verdict(ACCEPT_DIRECT, DIRECT_MEMBERSHIP, "v-direct"),
        plan_version_id=PLAN, created_at=T0)
    apply_p8_verdict(
        p9_conn, group=group, dossier=dossier,
        result=_verdict(ACCEPT_CONTEXT_SUPPORTED, CONTEXT_SUPPORTED_MEMBERSHIP,
                        "v-context"),
        plan_version_id=PLAN, created_at=T0)

    by_file = {
        item.file_id: item
        for item in memberships_for_group(p9_conn, dossier.group_id)
    }
    for anchor in ("lecture-08", "midterm-practice"):
        assert by_file[anchor].basis == DIRECT_ANCHOR
        assert by_file[anchor].decision == INCLUDED

    homework = by_file["hw-3"]
    assert homework.basis == CONTEXT_SUPPORTED
    assert homework.decision == UNCERTAIN
    assert homework.decision != INCLUDED
    assert membership_review_state_as_of(
        p9_conn, membership_id=homework.membership_id,
        plan_version_id=PLAN) == PENDING_REVIEW


def test_no_course_fact_is_written_onto_the_context_member(p9_conn):
    """The clause that matters most in §4.6. A membership says a file belongs with
    others; a FACT says something is true of the file. `HW 3` is in the group on
    inference, and asserting `subject=PHYS1401` about it would turn a semantic
    neighbour into a claim about the document."""
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    offenders = []
    for path in sorted(root.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Name) and node.id in {
                    "write_fact", "ensure_value", "apply_verdict"}:
                offenders.append(f"{path.name}:{node.lineno}:{node.id}")
    assert offenders == [], offenders


# --- provenance: the third event type had no producer ----------------------------


def test_recording_edges_appends_the_graph_edge_creation_event(p9_conn):
    """§8.2 names three P9 event types. `graph-edge creation` had no writer, which
    is a reserved name with nothing behind it -- the defect shape this project
    keeps finding."""
    from grouping.store import GRAPH_EDGE_CREATION

    graph = build_graph(
        group_id="group-1",
        neighborhood=Neighborhood(
            seed=Seed(
                seed_kind=STRONGLY_IDENTIFIED_FILE, file_id="file-seed",
                content_hash="h-seed", field_key="subject", value="PHYS1401",
                reliability_state="validated", observation_key="sha256:" + "a" * 64,
                basis=None),
            neighbors=(Neighbor(
                file_id="file-a", content_hash="h-a",
                channel=SHARED_VALIDATED_FACT, anchors=True,
                evidence_ref="sha256:" + "b" * 64, detail="subject=PHYS1401"),)),
        limits=_limits(), duplicate_or_version=None, created_at=T0)

    record_edges(p9_conn, "group-1", graph.edges, created_at=T0)
    events = list(p9_conn.execute(
        "SELECT * FROM events WHERE event_type = ?", (GRAPH_EDGE_CREATION,)))
    assert len(events) == len(graph.edges)
    assert events[0]["subsystem"] == "P9"
    assert graph.edges[0].edge_id in events[0]["explanation"]
    assert graph.edges[0].edge_type in events[0]["explanation"]


def test_recording_the_same_edges_twice_appends_no_second_event(p9_conn):
    """An edge id is content-derived, so a replay re-derives the same edge. Two
    creation events for one edge would say it was created twice."""
    from grouping.store import GRAPH_EDGE_CREATION

    graph = build_graph(
        group_id="group-1",
        neighborhood=Neighborhood(
            seed=Seed(
                seed_kind=STRONGLY_IDENTIFIED_FILE, file_id="file-seed",
                content_hash="h-seed", field_key="subject", value="PHYS1401",
                reliability_state="validated", observation_key="sha256:" + "a" * 64,
                basis=None),
            neighbors=(Neighbor(
                file_id="file-a", content_hash="h-a",
                channel=MUTUAL_SEMANTIC_RETRIEVAL, anchors=False,
                evidence_ref=None, detail="sem-a"),)),
        limits=_limits(), duplicate_or_version=None, created_at=T0)

    record_edges(p9_conn, "group-1", graph.edges, created_at=T0)
    record_edges(p9_conn, "group-1", graph.edges, created_at=T0)
    assert p9_conn.execute(
        "SELECT count(*) AS c FROM events WHERE event_type = ?",
        (GRAPH_EDGE_CREATION,)).fetchone()["c"] == len(graph.edges)


def test_p9_appends_exactly_the_three_event_types_ss8_2_names():
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    appended = set()
    for path in sorted(root.glob("*.py")):
        source = path.read_text()
        for node in ast.walk(ast.parse(source)):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "append_event"):
                for keyword in node.keywords:
                    if keyword.arg == "event_type":
                        appended.add(ast.unparse(keyword.value))
    assert len(appended) == 3, appended


def _limits():
    from grouping.config import GroupingLimits

    return GroupingLimits(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)


# --- Done-means 5: embeddings never establish a group ----------------------------


def test_every_group_reachable_with_embeddings_on_is_reachable_with_them_off(
    p9_conn,
):
    """§4.2: embeddings never establish a group. So a group that forms with them
    enabled and does NOT form with them disabled is a defect by definition, and
    the replay harness runs both to find one.

    Proved here at the rule rather than the run: a neighbourhood whose only
    surviving edges are semantic fires SR2, whatever the model would have said.
    """
    from grouping.graph import evaluate_stop_rules
    from grouping.vocabulary import SR2

    semantic_only = build_graph(
        group_id="group-1",
        neighborhood=Neighborhood(
            seed=Seed(
                seed_kind=USER_CREATED_STARTING_POINT, file_id="file-seed",
                content_hash="h-seed", field_key=None, value=None,
                reliability_state=None, observation_key=None,
                basis="the user started a group here"),
            neighbors=tuple(
                Neighbor(
                    file_id=f"file-{n}", content_hash=f"h-{n}",
                    channel=MUTUAL_SEMANTIC_RETRIEVAL, anchors=False,
                    evidence_ref=None, detail=f"sem-{n}")
                for n in range(3))),
        limits=_limits(), duplicate_or_version=None, created_at=T0)

    outcome = evaluate_stop_rules(
        p9_conn, semantic_only, limits=_limits(),
        conflicts_for=lambda files: (), basis_key="b", seed_anchors=False)
    assert outcome is not None
    assert SR2 in outcome.rules_fired


def test_a_semantic_neighbour_can_never_be_the_only_support_of_an_anchor():
    """The same rule at the record. A `direct-anchor` membership requires a
    `shared-validated-fact` support, so no amount of semantic proximity produces
    one."""
    from grouping.records import MalformedGroupRecord, Membership, Support
    from grouping.vocabulary import BOUNDED_SESSION, NOT_FLAGGED, RULES

    for kind in (MUTUAL_SEMANTIC_RETRIEVAL, BOUNDED_SESSION):
        with pytest.raises(MalformedGroupRecord):
            Membership(
                membership_id="m-1", group_id="g-1", file_id="f-1",
                content_hash="h-1", basis=DIRECT_ANCHOR,
                support=(Support(
                    support_kind=kind, observation_key=None, quote_or_field=None,
                    location=None, edge_ref="edge-1"),),
                decision=INCLUDED, decision_source=RULES,
                insufficient_evidence=False, insufficiency_statement=None,
                conflicts=(), outlier_flag=NOT_FLAGGED,
                validation_verdict_ref=None, created_at=T0)


# --- Done-means 7: one file, two groups ------------------------------------------


def test_one_file_holds_accepted_memberships_in_two_groups_at_once(p9_conn):
    """§4.9: an abstract belongs to a Research group and an application packet at
    the same time, and P11 reads both. A membership is per (group, file), so the
    two do not compete -- and a store that keyed on the file alone would have made
    the second overwrite the first."""
    from grouping.acceptance import group_state_as_of, record_acceptance
    from grouping.records import (
        AnchorFact,
        Group,
        GroupAcceptance,
        Membership,
        Support,
    )
    from grouping.store import (
        memberships_for_group,
        record_group,
        record_membership,
    )
    from grouping.vocabulary import (
        ACCEPTED,
        CANDIDATE,
        NOT_FLAGGED,
        NOT_REQUIRED,
        RULES,
        USER,
    )

    abstract = ("file-abstract", "h-abstract")
    for group_id, field, value in (
        ("group-research", "project", "photonics"),
        ("group-application", "target_school", "Columbia"),
    ):
        record_group(p9_conn, Group(
            group_id=group_id, seed_ref=abstract[0],
            seed_kind=STRONGLY_IDENTIFIED_FILE,
            proposed_basis=f"{field}={value}",
            anchor_facts=(AnchorFact(
                field=field, value=value, file_ids=(abstract[0],),
                reliability_state="validated",
                observation_key="sha256:" + "c" * 64),),
            pre_model_signals={}, anchor_count=1, coherence_verdict=None,
            coherence_citations=(), group_category=None, display_label=None,
            label_source=None, conflicts=(), stop_rule_hits=(), state=CANDIDATE,
            sensitivity_state="none", dossier_id=None, llm_response_ref=None,
            validation_verdict_ref=None, created_by=RULES, created_at=T0))
        record_membership(p9_conn, Membership(
            membership_id=f"{group_id}:{abstract[0]}", group_id=group_id,
            file_id=abstract[0], content_hash=abstract[1], basis=DIRECT_ANCHOR,
            support=(Support(
                support_kind=SHARED_VALIDATED_FACT,
                observation_key="sha256:" + "c" * 64, quote_or_field=field,
                location=None, edge_ref=None),),
            decision=INCLUDED, decision_source=RULES, insufficient_evidence=False,
            insufficiency_statement=None, conflicts=(), outlier_flag=NOT_FLAGGED,
            validation_verdict_ref=None, created_at=T0))
        record_acceptance(p9_conn, GroupAcceptance(
            acceptance_id=f"{PLAN}:{group_id}", plan_version_id=PLAN,
            group_id=group_id, membership_id=None, acceptance=ACCEPTED,
            review_state=NOT_REQUIRED, user_edited_label=None, aliases=(),
            review_decision_ref=None, decided_by=USER, created_at=T0))

    for group_id in ("group-research", "group-application"):
        members = memberships_for_group(p9_conn, group_id)
        assert [item.file_id for item in members] == [abstract[0]]
        assert members[0].decision == INCLUDED
        assert group_state_as_of(
            p9_conn, group_id=group_id, plan_version_id=PLAN) == ACCEPTED

    both = p9_conn.execute(
        "SELECT group_id FROM memberships WHERE file_id = ? ORDER BY group_id",
        (abstract[0],)).fetchall()
    assert [row["group_id"] for row in both] == [
        "group-application", "group-research"]
