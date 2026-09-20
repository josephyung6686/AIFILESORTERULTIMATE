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


#: `00` amendment 34, "a question names what it replaced". The rule these three
#: tests state, and it is the whole of it:
#:
#:     abstention_reason is REQUIRED  iff outcome == abstain
#:     abstention_reason is PERMITTED iff outcome == ask_user
#:     abstention_reason is FORBIDDEN otherwise
#:
#: The middle line is the amendment. A file a model was not allowed to look at
#: abstains with `privacy_blocked` and is then overlaid with a question about
#: where its folder should go; before this, the record refused to carry both, so
#: the reason was dropped and an unopenable vault and a classified photo came out
#: of the pipeline indistinguishable. The question is what the person acts on and
#: the reason is why the file stopped, and `66` §4 is satisfied by the THIRD line
#: rather than the second: what keeps a reason from meaning two things is that no
#: outcome but these two may carry one.
def _asked(**overrides):
    values = dict(
        outcome=v.ASK_USER, destination=None,
        ask=Ask(question="Where should the files in Private go?",
                options=("n-private", "n-review")),
        confidence_class=v.ABSTAIN_NO_SUPPORTED_DESTINATION,
    )
    values.update(overrides)
    return _decision(**values)


def test_an_abstention_is_still_required_to_name_why_it_abstained():
    """Clause one, and amendment 34 does not touch it: an unexplained abstention
    is silence, and silence is what `00` says this product may not answer with."""
    ok = _decision(outcome=v.ABSTAIN, destination=None,
                   abstention_reason=v.PRIVACY_BLOCKED)
    assert ok.abstention_reason == v.PRIVACY_BLOCKED
    with pytest.raises(MalformedPlacementRecord):
        _decision(outcome=v.ABSTAIN, destination=None, abstention_reason=None)


def test_a_question_may_name_the_reason_it_replaced_and_may_also_name_none():
    """Clause two, which is the amendment. PERMITTED and not required, because two
    of the three writers of an `ask_user` reach it with no abstention behind them:
    §6.9's two-homes question (`_multi_home_decision`), where the selector chooses
    between asking and abstaining and only one of them happens, and step 9's ask
    over a file nothing was read out of that the graph nevertheless supported.
    Neither replaced a reason, and requiring one there would make the record
    invent the fact it exists to carry."""
    carried = _asked(abstention_reason=v.PRIVACY_BLOCKED)
    assert carried.abstention_reason == v.PRIVACY_BLOCKED
    assert carried.outcome == v.ASK_USER
    replaced_nothing = _asked(abstention_reason=None)
    assert replaced_nothing.abstention_reason is None


def test_no_outcome_but_an_abstention_or_a_question_may_carry_a_reason():
    """Clause three, and it is the one that satisfies `66` §4. A `place` names a
    destination, a `mark_state` names a state and a `leave_in_place` names
    neither; a reason on any of them would be a second, contradicting account of
    a decision that was already made, which is two facts in one record."""
    for outcome, extra in (
            (v.PLACE, {}),
            (v.LEAVE_IN_PLACE, {"destination": None}),
            (v.MARK_STATE, {"destination": None,
                            "marked_state": v.UNSUPPORTED}),
    ):
        with pytest.raises(MalformedPlacementRecord):
            _decision(outcome=outcome, abstention_reason=v.PRIVACY_BLOCKED,
                      **extra)


def test_where_the_widening_stops_and_the_pipeline_takes_over():
    """THE ONE HOLE THE WIDENING OPENS, PINNED RATHER THAN QUIETLY CLOSED.

    §8.6: a run cut short at a ceiling did not look, and a question is the
    strongest possible claim that it did, so a budget deferral is never a
    question. Before the amendment the record enforced that as a side effect --
    an `ask_user` could carry no reason at all, so it could not carry that one.
    It no longer does: the deferral biconditional below still refuses the
    stage-less form, and the form WITH a stage is now a record this class
    accepts. It is built by nothing: `pipeline._abstention` consults the ask hook
    only `if reason != BUDGET_DEFERRED`, and `_asking` is reached from there and
    from step 9, which has no reason at all.

    Closing it here would be a rule the owner did not ratify -- amendment 34
    names three clauses and this is a fourth -- so it is recorded as the boundary
    of what was ratified rather than legislated past.
    """
    with pytest.raises(MalformedPlacementRecord):
        _asked(abstention_reason=v.BUDGET_DEFERRED, deferred_stage=None)
    admitted = _asked(abstention_reason=v.BUDGET_DEFERRED,
                      deferred_stage=v.PLACEMENT_SCORING)
    assert admitted.deferred_stage == v.PLACEMENT_SCORING


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
