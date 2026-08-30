"""E3 -- the two gates that stand between a decision and someone's disk.

**The approval gate.** *"Absence is a refusal, never a default. No approval
record means `review_policy_unsatisfied`. There is no timeout that ripens into
consent and no configuration that skips the check for a plan whose Required
review policy demands one."* (P12 SPEC, Contract in -> From P13.) P13 is
unbuilt, so the record arrives through an injected lookup; what the lookup
returns when nobody has answered is `None`, and `None` is the refusal.

**The protected gate.** §8.4: protected material *"should not be moved
automatically without a user policy that explicitly permits it"*, and
`privacy.moves.may_move_automatically` already decides it -- absence first, the
flag not the class, the policy at the asked-for plan version, no policy at all
is no permission. P12 calls it and picks no winner (`74` §5.3, §5.4).

**And the twin: an approval lifts ONE refusal and no other.** SPEC rule 3:
*"a plan that is also stale, protected without policy, or bound for a node that
refuses placement stays refused with that class."* An approved plan is not a
blessed plan.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from placement.vocabulary import BLOCKED_PENDING_USER, REVIEW_REQUIRED

from mutation import vocabulary as v
from mutation.approval import ReviewApproval, approval_verdict
from mutation.execute import apply_plan

from .conftest import CONSTRAINTS, plan_a_move

FIXED = "2026-08-29T00:00:00Z"


def _approval(plan, *, verdict=v.APPROVED, **overrides):
    fields = dict(
        approval_id="approval-1", plan_id=plan.plan_id,
        placement_decision_ref=plan.placement_decision_reference,
        plan_version=plan.organization_plan_version,
        required_review_policy=plan.required_review_policy, verdict=verdict,
        presented_state_ref="presented-1", user_id="jy", decided_at=FIXED)
    fields.update(overrides)
    return ReviewApproval(**fields)


def _apply(conn, plan, fixture_root, clock, ids, *, approval=None, **overrides):
    kwargs = dict(
        legal_destination_ids=frozenset({plan.requested_destination_node}),
        source_root=fixture_root, destination_root=fixture_root,
        constraints=CONSTRAINTS,
        suffix_for=lambda stem, attempt: f"{stem} ({attempt})",
        max_suffix_attempts=8, extra_protected=None,
        conflict_copies=lambda path: (), dataless_of=lambda path: False,
        normalize_filename=lambda name: name, scan_state="included",
        unverified_copy_disposition=None, materialized=True,
        component_version="p12-test", user_id="jy",
        approval_for=lambda plan_id: approval, now=clock, mint_id=ids)
    kwargs.update(overrides)
    return apply_plan(conn, plan, **kwargs)


@pytest.fixture()
def needs_review(p12_conn, landscape, ids):
    return plan_a_move(p12_conn, landscape, ids,
                       volume_of=lambda path: "vol-main",
                       review_policy=REVIEW_REQUIRED)


@pytest.fixture()
def protected_plan(p12_conn, landscape, ids):
    return plan_a_move(p12_conn, landscape, ids,
                       volume_of=lambda path: "vol-main", name="Passport.pdf",
                       handling_class="sensitive_personal", protected=True)


# --- E3's named test --------------------------------------------------------


def test_absence_of_an_approval_is_a_refusal_and_never_a_default(
        p12_conn, needs_review, fixture_root, clock, ids):
    plan, source = needs_review
    assert plan.required_review_policy == REVIEW_REQUIRED

    record = _apply(p12_conn, plan, fixture_root, clock, ids, approval=None)

    assert record.result == f"{v.REFUSED}:{v.REVIEW_POLICY_UNSATISFIED}"
    assert source.exists()
    assert not Path(plan.resolved_destination_path).exists()
    assert record.directories_created_by_this_action == ()

    refusals = p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.REFUSED_MOVE,)).fetchall()
    assert len(refusals) == 1
    assert v.decline_message(v.REVIEW_POLICY_UNSATISFIED) in refusals[0][0]

    # Nothing ripens. A second run with nothing answered refuses again.
    again = _apply(p12_conn, plan, fixture_root, clock, ids, approval=None)
    assert again.result == record.result


def test_an_approval_never_lifts_a_second_refusal(
        p12_conn, needs_review, protected_plan, fixture_root, clock, ids):
    """The negative twin. An approved plan is not a blessed plan."""
    plan, source = needs_review

    # (a) approved AND stale -> refused with the STALENESS class, not applied
    #     and not reported as a review problem.
    source.write_bytes(b"somebody else edited this")
    stale = _apply(p12_conn, plan, fixture_root, clock, ids,
                   approval=_approval(plan))
    assert stale.result == f"{v.STALE}:{v.CONTENT_HASH_DIFFERS}"
    assert stale.result != v.APPLIED
    assert source.read_bytes() == b"somebody else edited this"

    # (b) approved AND protected with no permitting policy -> refused with the
    #     PROTECTION class. §8.4 is a policy question, not an approval question.
    other, other_source = protected_plan
    approved = _apply(p12_conn, other, fixture_root, clock, ids,
                      approval=_approval(other))
    assert approved.result == f"{v.REFUSED}:{v.PROTECTED_WITHOUT_POLICY}"
    assert other_source.exists()


# --- the approval record's three identifiers --------------------------------


def test_an_approval_collected_under_another_plan_version_authorizes_nothing(
        needs_review):
    plan, _ = needs_review
    for drift in ({"plan_version": "plan-2"},
                  {"plan_id": "some-other-plan"},
                  {"placement_decision_ref": "some-other-decision"}):
        verdict = approval_verdict(plan, _approval(plan, **drift))
        assert not verdict.satisfied
        assert verdict.refusal_class == v.REVIEW_POLICY_UNSATISFIED
        assert verdict.detail["mismatched"] == (next(iter(drift)),)


def test_only_approved_satisfies_the_policy(needs_review):
    plan, _ = needs_review
    assert approval_verdict(plan, _approval(plan)).satisfied
    for verdict in (v.REJECTED, v.DEFERRED, v.REFRESH_REQUIRED):
        answered = approval_verdict(plan, _approval(plan, verdict=verdict))
        assert not answered.satisfied
        assert answered.refusal_class == v.REVIEW_POLICY_UNSATISFIED
        assert answered.detail["verdict"] == verdict


def test_refresh_required_asks_for_revalidation_and_still_does_not_authorize(
        needs_review):
    plan, _ = needs_review
    answered = approval_verdict(plan, _approval(plan, verdict=v.REFRESH_REQUIRED))
    assert not answered.satisfied
    assert answered.revalidate is True
    assert approval_verdict(plan, _approval(plan, verdict=v.REJECTED)).revalidate \
        is False


def test_a_plan_that_demands_no_review_needs_no_approval(
        p12_conn, planned, fixture_root, clock, ids):
    plan, _ = planned
    assert plan.required_review_policy not in (REVIEW_REQUIRED,
                                               BLOCKED_PENDING_USER)
    assert approval_verdict(plan, None).satisfied
    record = _apply(p12_conn, plan, fixture_root, clock, ids, approval=None)
    assert record.result == v.APPLIED


def test_a_blocked_pending_user_plan_demands_one_too(p12_conn, landscape, ids):
    plan, _ = plan_a_move(p12_conn, landscape, ids,
                          volume_of=lambda path: "vol-main",
                          review_policy=BLOCKED_PENDING_USER)
    assert not approval_verdict(plan, None).satisfied


# --- the protected gate -----------------------------------------------------


def test_a_file_nothing_has_classified_is_refused_and_not_read_as_unprotected(
        p12_conn, landscape, fixture_root, clock, ids):
    """`privacy.moves` checks ABSENCE first and P12 does not second-guess it."""
    plan, source = plan_a_move(p12_conn, landscape, ids,
                               volume_of=lambda path: "vol-main",
                               classified=False)

    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    assert record.result == f"{v.REFUSED}:{v.PROTECTED_WITHOUT_POLICY}"
    assert source.exists()
    refusal = p12_conn.execute(
        "SELECT explanation FROM events WHERE event_type = ?",
        (v.REFUSED_MOVE,)).fetchone()[0]
    assert "unreadable_unclassified" in refusal, (
        "the person is told WHICH of P7's four answers refused this, and "
        "'nothing has looked at this file' is not 'this file is protected'")


def test_a_policy_that_explicitly_permits_this_file_lets_it_move(
        p12_conn, protected_plan, fixture_root, clock, ids):
    from privacy.policy import Policy, set_policy

    plan, _ = protected_plan
    set_policy(p12_conn, Policy(
        policy_version="", operation_mode="offline", consent_grants=(),
        redaction_settings={}, automatic_move_permissions={plan.file_id: True},
        plan_version=plan.organization_plan_version, set_at=FIXED),
        component_version="p12-test", user_id="jy",
        reason="jy permitted this one file to be filed automatically")

    record = _apply(p12_conn, plan, fixture_root, clock, ids)
    assert record.result == v.APPLIED
