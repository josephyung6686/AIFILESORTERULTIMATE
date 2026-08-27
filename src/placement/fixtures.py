"""Golden P11 records, published for P12 and P13. Content-free contract witnesses.

These are what a downstream part builds against before P11 runs on a real corpus.
They are not an alternate authority: every one is constructed through
`placement.records`, so a shape change breaks them at import rather than leaving a
consumer building against a record the product no longer has.

Five, and each one is a case a consumer must be able to parse:

* a placement, with the evidence that produced it;
* a correct abstention, which §6.10 makes a SUCCESSFUL outcome and not a failure;
* a §7-origin decision, on the same thirty-field shape, so a consumer parses it
  with no residual branch (SPEC:610-612);
* a budget deferral, which §8.6 requires to render differently from an evidential
  abstention -- it names the stage it was cut short at and nothing else does;
* a decision about protected material, which is never `auto_eligible` and whose
  `model_eligibility` is `local_only`.

Nothing here carries a path, a deletion or an expiry, because no field of
`PlacementDecision` can hold one.
"""
from __future__ import annotations

from placement.records import (
    DecisionDepth, Destination, MatchingFact, PlacementDecision, PrivacyState,
    ResidualContext, Subject, TwoCondition,
)
from placement.vocabulary import (
    ABSTAIN, ABSTAIN_NO_SUPPORTED_DESTINATION, ACCEPT_DIRECT, AUTO_ELIGIBLE,
    BUDGET_DEFERRED, CONTEXT_SUPPORTED, DIRECT, DOSSIER_PERMITTED,
    EXACT_FACT_MATCH, FILE, LEAVE_IN_PLACE, LOCAL_ONLY, MARGIN_TRUE_VACUOUS,
    NO_SUPPORTED_DESTINATION, ORDINARY, PLACE, PLACEMENT, PLACEMENT_SCORING,
    RESIDUAL, REVIEW_REQUIRED, REVIEW_WITH_MODEL, WEAK,
)

T0 = "2026-08-27T00:00:00Z"

_SUBJECT = Subject(kind=FILE, file_id="f-syllabus", content_hash="h-syllabus",
                   group_id=None, member_file_ids=())
_PRIVACY = PrivacyState(handling_class="personal_non_sensitive", protected=False,
                        model_eligibility=DOSSIER_PERMITTED,
                        consent_audit_ref=None)
#: P7's flag travels with the class, because §8.4 Open question 1 leaves their
#: relation unsettled and has neighbouring parts CONSUME the flag.
_PROTECTED = PrivacyState(handling_class="sensitive_personal", protected=True,
                          model_eligibility=LOCAL_ONLY, consent_audit_ref=None)

_FACT = MatchingFact(file_fact_id="ff-1", field="subject", value="PHYS1401",
                     reliability=DIRECT, evidence_ref="obs-syllabus")


def _two_condition(**overrides) -> TwoCondition:
    values = dict(support_score=1.0, support_threshold=0.5, meets_threshold=True,
                  margin_over_next=None, margin_threshold=0.2,
                  meets_margin=MARGIN_TRUE_VACUOUS, verdict=ACCEPT_DIRECT,
                  requires_review=False)
    values.update(overrides)
    return TwoCondition(**values)


def _decision(**overrides) -> PlacementDecision:
    values = dict(
        decision_id="fixture", plan_version="plan-1", supersedes=None,
        superseded_by=None, supersede_reason=None, created_at=T0,
        origin_stage=PLACEMENT, returned_from=None, subject=_SUBJECT,
        group_plan_id=None, outcome=PLACE, destination=None, return_target=None,
        marked_state=None, ask=None,
        decision_depth=DecisionDepth(node_depth=0, supported_depth=0,
                                     unsupported_levels=()),
        evidence_type=CONTEXT_SUPPORTED,
        confidence_class=ABSTAIN_NO_SUPPORTED_DESTINATION, matching_facts=(),
        group_support=None, graph_anchors=(), conflicts_considered=(),
        alternatives=(), two_condition=_two_condition(), abstention_reason=None,
        deferred_stage=None, privacy=_PRIVACY, review_policy=REVIEW_REQUIRED,
        explanation="fixture", residual=None,
    )
    values.update(overrides)
    return PlacementDecision(**values)


#: The degenerate case B8(b) gives the walking skeleton: one legal candidate, a
#: vacuous margin, and a placement that still had to clear the support threshold.
EXACT_PLACEMENT = _decision(
    decision_id="fixture-place-1", outcome=PLACE,
    destination=Destination(node_id="n-course", node_role=ORDINARY),
    decision_depth=DecisionDepth(node_depth=1, supported_depth=1,
                                 unsupported_levels=()),
    evidence_type=DIRECT, confidence_class=EXACT_FACT_MATCH,
    matching_facts=(_FACT,), review_policy=AUTO_ELIGIBLE,
    explanation="PHYS1401 expects subject = PHYS1401; support 1.00 against a "
                "threshold of 0.50.",
)

#: The other half of B8(b): the same tree, and support that fell short. Only this
#: one proves the threshold stayed binding.
CORRECT_ABSTENTION = _decision(
    decision_id="fixture-abstain-1", outcome=ABSTAIN,
    two_condition=_two_condition(support_score=0.2, meets_threshold=False,
                                 verdict=WEAK, requires_review=True),
    abstention_reason=NO_SUPPORTED_DESTINATION,
    explanation="No legal destination cleared §6.10's conditions "
                "(no_supported_destination). Abstaining is the correct outcome; "
                "the evidence is retained and the file has not moved.",
)

#: A §7-origin decision, to prove a consumer parses it with no residual branch.
RESIDUAL_LEAVE_IN_PLACE = _decision(
    decision_id="fixture-residual-1", origin_stage=RESIDUAL,
    outcome=LEAVE_IN_PLACE,
    two_condition=_two_condition(support_score=0.3, meets_threshold=False,
                                 verdict=WEAK, requires_review=True),
    explanation="The user chose to review this set with a model; the model left "
                "the file in its current location and nothing was proposed.",
    residual=ResidualContext(set_id="plan-1:Screenshots",
                             set_decision=REVIEW_WITH_MODEL,
                             lifecycle_policy_ref=None),
)

#: §8.6: deferred work renders differently from "I looked and could not tell".
#: `deferred_stage` is the field SPEC:734 gives that job, and `PlacementDecision`
#: enforces the pairing both ways, so this fixture cannot drift into the one above.
BUDGET_DEFERRAL = _decision(
    decision_id="fixture-deferred-1", outcome=ABSTAIN,
    two_condition=_two_condition(support_score=0.0, meets_threshold=False,
                                 verdict=WEAK, requires_review=True),
    abstention_reason=BUDGET_DEFERRED, deferred_stage=PLACEMENT_SCORING,
    explanation="An §8.6 ceiling stopped the scoring stage before this file was "
                "judged. No conclusion about its evidence was reached.",
)

#: Design:185, §8.4: protected material is never moved automatically without a
#: policy that explicitly permits it, and it never leaves the device by default.
PROTECTED_PLACEMENT = _decision(
    decision_id="fixture-protected-1", outcome=PLACE,
    destination=Destination(node_id="n-course", node_role=ORDINARY),
    decision_depth=DecisionDepth(node_depth=1, supported_depth=1,
                                 unsupported_levels=()),
    evidence_type=DIRECT, confidence_class=EXACT_FACT_MATCH,
    matching_facts=(_FACT,), privacy=_PROTECTED, review_policy=REVIEW_REQUIRED,
    explanation="PHYS1401 expects subject = PHYS1401; the file is marked "
                "protected and no policy permits moving it automatically, so it "
                "is proposed for review rather than moved.",
)

GOLDEN_DECISIONS: tuple[PlacementDecision, ...] = (
    EXACT_PLACEMENT, CORRECT_ABSTENTION, RESIDUAL_LEAVE_IN_PLACE,
    BUDGET_DEFERRAL, PROTECTED_PLACEMENT,
)


def golden_decisions() -> tuple[PlacementDecision, ...]:
    return GOLDEN_DECISIONS
