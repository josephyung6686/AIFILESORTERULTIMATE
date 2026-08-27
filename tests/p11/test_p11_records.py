"""Contract out §1 — one record shape, and the fields that make it one."""
from __future__ import annotations

import dataclasses

import pytest

from placement import vocabulary as v
from placement.records import (
    Alternative, Ask, ConflictConsidered, DecisionDepth, Destination, GraphAnchor,
    GroupSupport, MalformedPlacementRecord, MatchingFact, PlacementDecision,
    PrivacyState, ResidualContext, ReturnTarget, Subject, TwoCondition,
)

T0 = "2026-08-27T00:00:00Z"


def _two_condition(**overrides) -> TwoCondition:
    values = dict(
        support_score=0.9, support_threshold=0.5, meets_threshold=True,
        margin_over_next=0.4, margin_threshold=0.2, meets_margin=v.MARGIN_TRUE,
        verdict="accept_direct", requires_review=False,
    )
    values.update(overrides)
    return TwoCondition(**values)


def _decision(**overrides) -> PlacementDecision:
    values = dict(
        decision_id="d1", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage=v.PLACEMENT, returned_from=None,
        subject=Subject(kind=v.FILE, file_id="f1", content_hash="h1",
                        group_id=None, member_file_ids=()),
        group_plan_id=None, outcome=v.PLACE,
        destination=Destination(node_id="n1", node_role=v.ORDINARY),
        return_target=None, marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=3, supported_depth=3,
                                     unsupported_levels=()),
        evidence_type=v.DIRECT, confidence_class=v.EXACT_FACT_MATCH,
        matching_facts=(MatchingFact(file_fact_id="ff1", field="subject",
                                     value="PHYS1401", reliability=v.DIRECT,
                                     evidence_ref="obs-1"),),
        group_support=None, graph_anchors=(), conflicts_considered=(),
        alternatives=(), two_condition=_two_condition(),
        abstention_reason=None, deferred_stage=None,
        privacy=PrivacyState(handling_class="personal_non_sensitive", protected=False,
                             model_eligibility=v.DOSSIER_PERMITTED,
                             consent_audit_ref=None),
        review_policy=v.AUTO_ELIGIBLE,
        explanation="The file's direct subject fact PHYS1401 matches this node's "
                    "expected value.",
        residual=None,
    )
    values.update(overrides)
    return PlacementDecision(**values)


def test_a_residual_decision_parses_with_no_residual_specific_branch():
    # Done-means 1: a consumer built against the shape reads both paths the same.
    placement = _decision()
    residual = _decision(
        decision_id="d2", origin_stage=v.RESIDUAL, outcome=v.LEAVE_IN_PLACE,
        destination=None,
        decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                     unsupported_levels=()),
        confidence_class=v.ABSTAIN_NO_SUPPORTED_DESTINATION,
        # `margin_over_next=None` REQUIRES `true_vacuous`: `TwoCondition`
        # refuses a null margin under any other value, because a measured margin
        # with no number is a comparison nobody made. This residual file had one
        # candidate and no next-best, so vacuous is also the true answer.
        two_condition=_two_condition(meets_threshold=False, verdict="weak",
                                     margin_over_next=None,
                                     meets_margin=v.MARGIN_TRUE_VACUOUS),
        residual=ResidualContext(set_id="s1", set_decision=v.REVIEW_WITH_MODEL,
                                 lifecycle_policy_ref=None),
    )
    for decision in (placement, residual):
        assert decision.outcome in v.OUTCOMES
        assert decision.explanation
        assert isinstance(decision.two_condition, TwoCondition)
    assert {f.name for f in dataclasses.fields(placement)} == {
        f.name for f in dataclasses.fields(residual)}


def test_a_destination_is_present_only_when_the_outcome_is_place():
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, abstention_reason=v.LOW_MARGIN)
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.PLACE, destination=None)


def test_an_abstention_names_a_reason_and_a_reason_needs_an_abstention():
    ok = _decision(outcome=v.ABSTAIN, destination=None,
                   abstention_reason=v.NO_SUPPORTED_DESTINATION)
    assert ok.abstention_reason == v.NO_SUPPORTED_DESTINATION
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, destination=None, abstention_reason=None)
    with pytest.raises(MalformedPlacementRecord):
        _decision(abstention_reason=v.LOW_MARGIN)


def test_return_to_placement_is_residual_only_and_ask_user_is_placement_only():
    # SPEC:437-445. The two paths differ by exactly these two outcomes.
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.RETURN_TO_PLACEMENT, destination=None,
                  return_target=ReturnTarget(kind=v.CONFIRMED_DOMAIN_GROUP, id="g1"))
    ok = _decision(origin_stage=v.RESIDUAL, outcome=v.RETURN_TO_PLACEMENT,
                   destination=None,
                   return_target=ReturnTarget(kind=v.CONFIRMED_DOMAIN_GROUP, id="g1"),
                   residual=ResidualContext(set_id="s1",
                                            set_decision=v.REVIEW_WITH_MODEL,
                                            lifecycle_policy_ref=None))
    assert ok.return_target.id == "g1"
    with pytest.raises(MalformedPlacementRecord):
        _decision(origin_stage=v.RESIDUAL, outcome=v.ASK_USER, destination=None,
                  ask=Ask(question="Which packet is this transcript's home?",
                          options=("n-columbia", "n-duke")),
                  residual=ResidualContext(set_id="s1",
                                           set_decision=v.REVIEW_WITH_MODEL,
                                           lifecycle_policy_ref=None))


def test_a_vacuous_margin_records_no_number_and_a_measured_one_does():
    # B8(b): the two must be distinguishable, so a reviewer and a P2 replay can
    # tell an unopposed candidate from a genuine margin.
    vacuous = _decision(two_condition=_two_condition(
        margin_over_next=None, meets_margin=v.MARGIN_TRUE_VACUOUS))
    assert vacuous.two_condition.margin_over_next is None
    with pytest.raises(MalformedPlacementRecord):
        _two_condition(margin_over_next=0.3, meets_margin=v.MARGIN_TRUE_VACUOUS)
    with pytest.raises(MalformedPlacementRecord):
        _two_condition(margin_over_next=None, meets_margin=v.MARGIN_TRUE)


def test_a_context_supported_verdict_is_never_auto_eligible():
    with pytest.raises(MalformedPlacementRecord):
        _decision(two_condition=_two_condition(verdict="accept_context_supported",
                                               requires_review=True),
                  review_policy=v.AUTO_ELIGIBLE)


def test_a_user_attached_membership_is_never_validated_or_auto_eligible():
    # M12, SPEC:176-178. Nothing was read from the file, so nothing validated it.
    support = GroupSupport(group_id="g1", membership="user-attached")
    with pytest.raises(MalformedPlacementRecord):
        _decision(group_support=support, evidence_type=v.VALIDATED)
    with pytest.raises(MalformedPlacementRecord):
        _decision(group_support=support, evidence_type=v.POSSIBLE,
                  review_policy=v.AUTO_ELIGIBLE)


def test_unsupported_levels_distinguish_a_child_from_a_broad_parent():
    # SPEC:414-417: this is what replaced `destination.kind`.
    child = _decision()
    parent = _decision(decision_depth=DecisionDepth(
        node_depth=2, supported_depth=2, unsupported_levels=("term",)))
    assert child.decision_depth.unsupported_levels == ()
    assert parent.decision_depth.unsupported_levels == ("term",)
    with pytest.raises(MalformedPlacementRecord):
        DecisionDepth(node_depth=1, supported_depth=3, unsupported_levels=())


def test_the_record_cannot_express_deletion_expiry_or_a_path():
    # Done-means 15, and B3. A field name is the whole surface here.
    names = {f.name for f in dataclasses.fields(PlacementDecision)}
    for banned in ("path", "resolved_path", "destination_path", "delete",
                   "deleted", "expiry", "expires_at", "disposable", "ttl"):
        assert banned not in names
    assert "node_id" in {f.name for f in dataclasses.fields(Destination)}
    assert "path" not in {f.name for f in dataclasses.fields(Destination)}


def test_every_citation_is_an_observation_key_and_never_an_observation_id():
    # M14, SPEC:193-200. §8.7 needs a rejected match recorded today to still
    # resolve to its evidence after an extractor upgrade; only the key does.
    for record in (MatchingFact, ConflictConsidered):
        names = {f.name for f in dataclasses.fields(record)}
        assert "evidence_ref" in names
        assert "observation_id" not in names


def test_a_budget_deferral_names_the_stage_it_was_cut_short_at():
    ok = _decision(outcome=v.ABSTAIN, destination=None,
                   abstention_reason=v.BUDGET_DEFERRED,
                   deferred_stage=v.PLACEMENT_SCORING)
    assert ok.deferred_stage == v.PLACEMENT_SCORING
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, destination=None,
                  abstention_reason=v.BUDGET_DEFERRED, deferred_stage=None)
    with pytest.raises(MalformedPlacementRecord):
        _decision(deferred_stage=v.PLACEMENT_SCORING)
