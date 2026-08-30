"""§6.8: one coherent group plan, not several unrelated file moves.

Done-means 4: a group plan reaches a surface as ONE thing, each member stays
individually inspectable, and every excluded outlier arrives with its conflicting
fact and where it was routed. `66` §4's absence notices ride here because the
group plan is the first place the question "why is this member not shown?" can be
asked, and the answer must never be a shrug.
"""
from __future__ import annotations

from placement.groups import ExcludedOutlier, GroupPlan
from placement.records import (
    DecisionDepth,
    Destination,
    PlacementDecision,
    PrivacyState,
    Subject,
    TwoCondition,
)
from placement.vocabulary import (
    ACCEPT_DIRECT,
    EXACT_FACT_MATCH,
    MARGIN_TRUE_VACUOUS,
    PLACE,
    REVIEW_REQUIRED,
    ROUTED_TO_NODE,
    ROUTED_TO_REVIEW_QUEUE,
)
from tree_design.records import Node, PlanVersion
from tree_design.store import write_node, write_plan_version

from review_surface.citations import resolve_matching_facts
from review_surface.items import group_plan_review_item
from review_surface.states import ABSENCE_PROTECTED, AbsenceNotice

T0 = "2026-08-29T00:00:00Z"

#: P11's §6.10 arithmetic, carried whole. P13 shows the figures; it recomputes
#: nothing, so the fixture is P11's shape rather than a plausible one.
TWO_CONDITION = TwoCondition(
    support_score=1.0, support_threshold=1.0, meets_threshold=True,
    margin_over_next=None, margin_threshold=0.0,
    meets_margin=MARGIN_TRUE_VACUOUS, verdict=ACCEPT_DIRECT,
    requires_review=True)


def _tree(conn):
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel-1"))
    for node_id, label, parent in (("n-1", "Applications", None),
                                   ("n-2", "Columbia", "n-1"),
                                   ("n-9", "Review Queue", None)):
        write_node(conn, Node(
            node_id=node_id, plan_version_id="plan-1", node_type="proposed",
            display_label=label, parent_node_id=parent, root_anchor="root",
            ordinal=0, associated_group_ids=(), explanation="fixture",
            node_role="ordinary", accepts_placement=True,
            handling_class="public_low", origin_node_id=node_id,
            template_context=None, dimension_role=None, dimension=None,
            expected_values=(), existing_path=None, disposition=None,
            refinement_disposition=None, refinement_reason=None,
            protected_movement_permitted=False))


def _member(file_id: str) -> PlacementDecision:
    return PlacementDecision(
        decision_id=f"d-{file_id}", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage="placement", returned_from=None,
        subject=Subject(kind="file", file_id=file_id, content_hash="h",
                        group_id="g-1", member_file_ids=()),
        group_plan_id="gp-1", outcome=PLACE,
        destination=Destination(node_id="n-2", node_role="ordinary"),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=2, supported_depth=2,
                                     unsupported_levels=()),
        evidence_type="direct", confidence_class=EXACT_FACT_MATCH,
        matching_facts=(), group_support=None, graph_anchors=(),
        conflicts_considered=(), alternatives=(),
        two_condition=TWO_CONDITION,
        abstention_reason=None, deferred_stage=None,
        privacy=PrivacyState(handling_class="public_low", protected=False,
                             model_eligibility="local_only",
                             consent_audit_ref=None),
        review_policy=REVIEW_REQUIRED, explanation="member", residual=None)


def _plan(members=None, outliers=None) -> GroupPlan:
    """P11's `member_decisions` carries the DECISIONS, not their ids.

    So P13 reads the members off the plan and takes no second member list: P11
    already refuses a plan whose members do not all share its id, and a second
    list would let a surface show members P11 never put in the plan.
    """
    return GroupPlan(
        group_plan_id="gp-1", plan_version="plan-1", group_id="g-1",
        shared_parent_node_id="n-2",
        member_decisions=members or (_member("f1"), _member("f2")),
        excluded_outliers=outliers if outliers is not None else (
            ExcludedOutlier(
                file_id="f-3", conflicting_fact="target_school=NYU",
                evidence_ref="obs-nyu", routed_to=ROUTED_TO_NODE,
                node_id="n-9"),))


def _item(conn, plan, absences=()):
    return group_plan_review_item(
        conn, plan, resolve_citations=resolve_matching_facts,
        absences=absences)


def test_the_plan_presents_as_one_thing_with_its_shared_parent(p13_conn):
    _tree(p13_conn)
    item = _item(p13_conn, _plan())
    assert item.group_plan_id == "gp-1"
    assert item.shared_parent_label_chain == ("Applications", "Columbia")
    assert len(item.member_items) == 2


def test_each_member_is_still_individually_inspectable(p13_conn):
    """§8.2 and §8.7: the group is the framing, never a wrapper that hides it."""
    _tree(p13_conn)
    item = _item(p13_conn, _plan())
    assert {m.subject_ref for m in item.member_items} == {"d-f1", "d-f2"}
    for member in item.member_items:
        assert member.destination_label_chain == ("Applications", "Columbia")


def test_each_outlier_carries_its_conflicting_fact_and_where_it_went(p13_conn):
    """§6.8, Done-means 4."""
    _tree(p13_conn)
    item = _item(p13_conn, _plan())
    assert len(item.excluded_outliers) == 1
    outlier, chain = item.excluded_outliers[0]
    assert outlier.file_id == "f-3"
    assert outlier.conflicting_fact == "target_school=NYU"
    assert outlier.evidence_ref == "obs-nyu"
    assert outlier.routed_to == ROUTED_TO_NODE
    assert chain == ("Review Queue",)


def test_an_outlier_routed_to_the_review_queue_has_no_label_chain(p13_conn):
    """An empty chain, never an invented one: there is no node to name, and a
    placeholder would read as a destination the user could accept."""
    _tree(p13_conn)
    plan = _plan(outliers=(ExcludedOutlier(
        file_id="f-4", conflicting_fact="subject=CHEM1010",
        evidence_ref="obs-chem", routed_to=ROUTED_TO_REVIEW_QUEUE,
        node_id=None),))
    item = _item(p13_conn, plan)
    assert item.excluded_outliers[0][1] == ()


def test_absence_notices_ride_on_the_group_plan_and_stay_distinct(p13_conn):
    """`66` §4 in its first real position: members not shown, said properly."""
    _tree(p13_conn)
    item = _item(p13_conn, _plan(members=(_member("f1"),)),
                 absences=(AbsenceNotice(state=ABSENCE_PROTECTED, count=2,
                                         explanation_ref="help/protected"),))
    assert len(item.absence_notices) == 1
    assert item.absence_notices[0].count == 2
    assert "privacy policy" in item.absence_notices[0].sentence()
