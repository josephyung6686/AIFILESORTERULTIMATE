"""The placement review item. §6.11's four labels, rendered distinguishably.

    "The user should see these distinctions in the review interface, because a
    direct placement and a context-supported placement should not demand the
    same level of trust."

Three rendering obligations are contractual, and each is a function here rather
than a comment:

* **Trust is not uniform.** `affordance_for` gives a context-supported match a
  different acceptance affordance from an exact fact match. This module does not
  decide WHICH files those are -- P11 already did -- it decides that the two do
  not present the same one-click control. A label alone would satisfy
  "distinguishable" and would not satisfy "should not demand the same level of
  trust": two cards that read differently and accept identically demand
  identical trust.
* **A budget deferral is not an abstention.** `render_state_for` separates them,
  and a deferral is offered no acceptance affordance at all: §8.6's rule that
  cost exhaustion never turns into lower-quality classification is inverted here
  into a rule about PRESENTATION.
* **The explanation is shown with its citations**, which is why `cited_facts`
  pairs each `MatchingFact` with its resolution and the item never carries the
  explanation alone.

There is no score and no arithmetic anywhere in this module. `two_condition` is
carried whole, because §6.11's own requirement is that the FIGURES AND BOTH
THRESHOLDS are presentable -- P13 shows P11's arithmetic, it does not repeat it.

The citation resolver is INJECTED with no default. Resolving an `observation_key`
to a displayable excerpt is `review_surface.citations`' job (M14), and it has not
shipped; a default here would be P13 guessing what a citation says. Absent means
refuse.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from placement.groups import ExcludedOutlier, GroupPlan
from placement.records import (
    Alternative,
    Ask,
    ConflictConsidered,
    DecisionDepth,
    GraphAnchor,
    GroupSupport,
    MatchingFact,
    PlacementDecision,
    PrivacyState,
    TwoCondition,
)
from placement.vocabulary import (
    ABSTAIN,
    ASK_USER,
    EXACT_FACT_MATCH,
    MARK_STATE,
    PLACE,
    ROUTED_TO_NODE,
    SHARED_MATERIAL_DECISION,
)

from review_surface.labels import label_chain_for_version
from review_surface.states import AbsenceNotice

AFFORDANCE_ONE_STEP: str = "one_step_accept"
AFFORDANCE_REVIEW_REQUIRED: str = "review_each_before_accepting"
AFFORDANCE_NONE: str = "no_acceptance_offered"
ACCEPTANCE_AFFORDANCES: tuple[str, ...] = (
    AFFORDANCE_ONE_STEP, AFFORDANCE_REVIEW_REQUIRED, AFFORDANCE_NONE)

RENDER_PLACEMENT: str = "placement_state"
RENDER_SHARED_MATERIAL: str = "shared_material_state"
RENDER_ABSTENTION: str = "abstention_state"
RENDER_BUDGET_DEFERRAL: str = "budget_deferral_state"
RENDER_ASK: str = "ask_user_state"
RENDER_MARKED: str = "marked_state"
RENDER_STATES: tuple[str, ...] = (
    RENDER_PLACEMENT, RENDER_SHARED_MATERIAL, RENDER_ABSTENTION,
    RENDER_BUDGET_DEFERRAL, RENDER_ASK, RENDER_MARKED)

#: What the composition root injects for citation resolution: it is handed the
#: connection and P11's `matching_facts[]` and returns one pair per fact.
CitationResolver = Callable[
    [sqlite3.Connection, Sequence[MatchingFact]],
    "tuple[tuple[MatchingFact, object], ...]"]


class UnrenderableDecision(RuntimeError):
    """A decision whose own fields contradict each other. Refused, not blanked."""


@dataclass(frozen=True)
class PlacementReviewItem:
    """A rendering projection over one decision. It adds no field of its own."""

    subject_ref: str
    plan_version: str
    subject_kind: str
    render_state: str
    acceptance_affordance: str
    destination_label_chain: tuple[str, ...]
    destination_node_role: str | None
    confidence_class: str | None
    evidence_type: str | None
    decision_depth: DecisionDepth | None
    levels_deliberately_unfilled: tuple[str, ...]
    cited_facts: tuple[tuple[MatchingFact, object], ...]
    group_support: GroupSupport | None
    graph_anchors: tuple[GraphAnchor, ...]
    conflicts_considered: tuple[ConflictConsidered, ...]
    alternatives: tuple[Alternative, ...]
    two_condition: TwoCondition | None
    abstention_reason: str | None
    deferred_stage: str | None
    ask: Ask | None
    privacy: PrivacyState | None
    review_policy: str | None
    explanation: str


def render_state_for(decision: PlacementDecision) -> str:
    """Which of the six visibly different states this decision is in.

    `deferred_stage` is read BEFORE `abstention_reason`, because P11 carries both
    on a budget deferral and the deferral is the more specific claim. Reading the
    reason first would render every deferral as an ordinary abstention, which is
    exactly the conflation Done-means 2 forbids.
    """
    if decision.deferred_stage:
        return RENDER_BUDGET_DEFERRAL
    if decision.outcome == ASK_USER:
        return RENDER_ASK
    if decision.outcome == ABSTAIN:
        return RENDER_ABSTENTION
    if decision.outcome == MARK_STATE:
        return RENDER_MARKED
    if decision.confidence_class == SHARED_MATERIAL_DECISION:
        return RENDER_SHARED_MATERIAL
    if decision.outcome == PLACE:
        return RENDER_PLACEMENT
    # Every remaining outcome -- a return to placement, a review-later mark, a
    # leave-in-place -- proposes no destination on this surface. Rendering one
    # as a placement would be P13 claiming a decision P11 did not make.
    return RENDER_ABSTENTION


def affordance_for(decision: PlacementDecision) -> str:
    """§6.11's trust distinction, expressed as a CONTROL rather than as a label."""
    state = render_state_for(decision)
    if state in (RENDER_BUDGET_DEFERRAL, RENDER_ASK, RENDER_ABSTENTION,
                 RENDER_MARKED):
        # No "accept anyway" over a deferred subject, and an abstention has
        # nothing to accept.
        return AFFORDANCE_NONE
    if decision.confidence_class == EXACT_FACT_MATCH:
        return AFFORDANCE_ONE_STEP
    return AFFORDANCE_REVIEW_REQUIRED


def placement_review_item(conn: sqlite3.Connection, decision: PlacementDecision,
                          *, resolve_citations: CitationResolver,
                          ) -> PlacementReviewItem:
    """Project one P11 decision into what must be presentable. Adds no field."""
    if decision.outcome == PLACE and decision.destination is None:
        raise UnrenderableDecision(
            f"decision {decision.decision_id!r} has outcome {PLACE!r} and no "
            "destination. Rendering it with a blank destination would present a "
            "placement to nowhere as a placement")
    chain: tuple[str, ...] = ()
    role: str | None = None
    if decision.destination is not None:
        chain = label_chain_for_version(
            conn, plan_version=decision.plan_version,
            node_id=decision.destination.node_id)
        role = decision.destination.node_role
    depth = decision.decision_depth
    return PlacementReviewItem(
        subject_ref=decision.decision_id,
        plan_version=decision.plan_version,
        subject_kind=decision.subject.kind,
        render_state=render_state_for(decision),
        acceptance_affordance=affordance_for(decision),
        destination_label_chain=chain,
        destination_node_role=role,
        confidence_class=decision.confidence_class,
        evidence_type=decision.evidence_type,
        decision_depth=depth,
        levels_deliberately_unfilled=(
            tuple(depth.unsupported_levels) if depth is not None else ()),
        cited_facts=resolve_citations(conn, decision.matching_facts),
        group_support=decision.group_support,
        graph_anchors=tuple(decision.graph_anchors),
        conflicts_considered=tuple(decision.conflicts_considered),
        alternatives=tuple(decision.alternatives),
        two_condition=decision.two_condition,
        abstention_reason=decision.abstention_reason,
        deferred_stage=decision.deferred_stage,
        ask=decision.ask,
        privacy=decision.privacy,
        review_policy=decision.review_policy,
        explanation=decision.explanation)


@dataclass(frozen=True)
class GroupPlanReviewItem:
    """§6.8: ONE coherent group plan, not several unrelated file moves.

    The member items are the same `PlacementReviewItem`s any single-file surface
    would show, so a member accepted inside a group is still individually
    inspectable and individually correctable (§8.2, §8.7). The group is the
    framing, never a wrapper that hides its members.

    `absence_notices` is `66` §4 in its first real position. The group plan is
    where "why is this member not on the list?" first gets asked, and the answer
    must name the state that actually applies rather than say "could not find".
    """

    group_plan_id: str
    plan_version: str
    group_id: str
    shared_parent_label_chain: tuple[str, ...]
    member_items: tuple[PlacementReviewItem, ...]
    excluded_outliers: tuple[tuple[ExcludedOutlier, tuple[str, ...]], ...]
    absence_notices: tuple[AbsenceNotice, ...]


def group_plan_review_item(conn: sqlite3.Connection, plan: GroupPlan, *,
                           resolve_citations: CitationResolver,
                           absences: Sequence[AbsenceNotice] = (),
                           ) -> GroupPlanReviewItem:
    """Project a §6.8 group plan and each of its excluded outliers.

    The members are read off `plan.member_decisions`, which carries the decisions
    themselves. P11 already refuses a plan whose members do not all share its id;
    taking a second member list as an argument would let a caller present members
    P11 never put in the plan, which is the one thing §6.8's "one coherent group
    plan" rules out.

    An outlier routed anywhere but to a node gets an EMPTY label chain rather
    than an invented one. There is no node to name, and a placeholder chain would
    read as a destination the user could accept.
    """
    outliers: list[tuple[ExcludedOutlier, tuple[str, ...]]] = []
    for outlier in plan.excluded_outliers:
        chain: tuple[str, ...] = ()
        if outlier.routed_to == ROUTED_TO_NODE and outlier.node_id:
            chain = label_chain_for_version(
                conn, plan_version=plan.plan_version, node_id=outlier.node_id)
        outliers.append((outlier, chain))
    return GroupPlanReviewItem(
        group_plan_id=plan.group_plan_id,
        plan_version=plan.plan_version,
        group_id=plan.group_id,
        shared_parent_label_chain=label_chain_for_version(
            conn, plan_version=plan.plan_version,
            node_id=plan.shared_parent_node_id),
        member_items=tuple(
            placement_review_item(conn, decision,
                                  resolve_citations=resolve_citations)
            for decision in plan.member_decisions),
        excluded_outliers=tuple(outliers),
        absence_notices=tuple(absences))
