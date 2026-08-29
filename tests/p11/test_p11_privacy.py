"""§8.4 carried, never re-derived; and the review policy that follows from it."""
from __future__ import annotations

import inspect

import pytest

import json

from database_agent.files_table import get_file, record_file
from privacy import moves as p7_moves
from privacy.moves import UNREADABLE_UNCLASSIFIED
from privacy.classification import ClassificationRecord, observation_key
from privacy.classification_store import (
    ClassificationStore, GateOutcomeNotAFileFact,
)
from privacy.denial import mode_forbids
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.vocabulary import DISPLAY_FACETS, OutOfVocabulary

from placement import vocabulary as v
from placement.privacy import (
    PolicyRequired, automatic_move_permitted_for, blocked_policy,
    is_unclassified, may_assemble_dossier, privacy_state_for, review_policy_for,
)
from placement.records import GroupSupport, TwoCondition
from p11.p10_fixtures import FROZEN_TREE as FROZEN_TREE_FOR_LEGALITY

T0 = "2026-08-27T00:00:00Z"

#: A real P4 content-addressed key. `"obs-1"` is rejected by shape: P7 refuses a
#: per-row observation id, so a fixture that used one would prove the classification
#: is evidence-backed against a store that never accepted it (M14).
OBS = observation_key(content_hash="h1", extractor_name="fixture",
                      locator="page-1", raw_value="fixture value")


def _classify(conn, *, file_id="f1", handling_class="personal_non_sensitive",
              protected=False):
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash="h1", handling_class=handling_class,
        protected=protected, basis="detector", evidence_refs=(OBS,),
        reliability_state="direct", observed_at=T0))


def _policy(conn, *, mode="hybrid", permissions=None):
    # `set_policy` takes no `author`: M8 makes the acting part the author. It
    # does take `reason`, because §8.8 requires a meaningful policy diff line.
    # `set_policy` refuses a caller-supplied version: the gate mints it and the
    # caller echoes it back (SPEC §6). `UNSET_POLICY_VERSION` is the sentinel.
    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode, consent_grants=(),
        redaction_settings={}, automatic_move_permissions=permissions or {},
        plan_version="plan-1", set_at=T0,
    ), component_version="P7-test", user_id="u1",
       reason="fixture policy for the P11 privacy tests")


def _two_condition(**overrides):
    values = dict(support_score=0.9, support_threshold=0.5, meets_threshold=True,
                  margin_over_next=0.4, margin_threshold=0.2,
                  meets_margin=v.MARGIN_TRUE, verdict="accept_direct",
                  requires_review=False)
    values.update(overrides)
    return TwoCondition(**values)


def _real_file(conn, directory):
    """A real P1 row. `may_move_automatically` looks the content hash up by
    file id, so a synthesized id would not exercise the predicate at all."""
    directory.mkdir(parents=True, exist_ok=True)
    document = directory / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(directory), mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _state(conn, *, file_id="f1"):
    return privacy_state_for(conn, file_id=file_id, content_hash="h1",
                             plan_version="plan-1")


# --- the carry ------------------------------------------------------------------

def test_an_unclassified_file_reads_p7s_own_answer_instead_of_refusing(p11_conn):
    # P7's detector abstaining is DESIGNED behaviour -- it is what stops it
    # guessing -- and `resolve_class(None)` is P7's published answer for it.
    # Refusing here instead meant one file the detector said nothing about took
    # down the whole corpus run: ten thousand files and one ambiguous scan
    # produced a traceback and no plan at all.
    _policy(p11_conn)
    state = _state(p11_conn)
    assert state.handling_class == UNREADABLE_UNCLASSIFIED
    # §8.6's rule, in the direction that matters: absence resolves to the gate
    # outcome and NEVER down to the least protected class.
    assert state.handling_class != "public_low"
    # And §8.4's precondition holds: classification comes before escalation, so
    # nothing about a file nobody classified is assembled for a model.
    assert state.model_eligibility == v.LOCAL_ONLY
    assert may_assemble_dossier(state) is False


def test_an_unclassified_file_is_not_a_protected_one(p11_conn):
    # The two findings must stay apart. `unclassified` is "we could not tell";
    # `protected` is "the user said this is sensitive and we deliberately did not
    # look". §8.4 Open question 1 makes `protected` a FLAG a consumer carries and
    # never infers, and an absent record carries no flag -- so raising one here
    # would describe a passport and an unreadable scan with the same word, which
    # is the collapse `00` forbids in terms: sensitive personal material is not
    # the same thing as `Numbers.app`.
    _policy(p11_conn)
    unclassified = _state(p11_conn)
    _classify(p11_conn, file_id="f2", protected=True,
              handling_class="highly_sensitive_credential_bearing")
    passport = privacy_state_for(p11_conn, file_id="f2", content_hash="h1",
                                 plan_version="plan-1")
    assert unclassified.protected is False
    assert passport.protected is True
    assert unclassified.handling_class != passport.handling_class


def test_a_missing_policy_refuses_rather_than_assuming_a_mode(p11_conn):
    _classify(p11_conn)
    with pytest.raises(PolicyRequired):
        _state(p11_conn)


def test_p11_carries_the_handling_class_and_reclassifies_nothing(p11_conn):
    _classify(p11_conn, handling_class="sensitive_personal", protected=True)
    _policy(p11_conn)
    state = _state(p11_conn)
    assert state.handling_class == "sensitive_personal"
    assert state.model_eligibility == v.LOCAL_ONLY


def test_a_protected_files_flag_survives_the_carry_intact(p11_conn):
    # The standing constraint: a protected container is marked and counted, never
    # opened. §8.4 Open question 1 forbids a consumer inferring the flag from the
    # class, so the flag must BE carried -- there is no other way to consume it.
    _classify(p11_conn, handling_class="personal_non_sensitive", protected=True)
    _policy(p11_conn)
    state = _state(p11_conn)
    assert state.protected is True
    assert state.handling_class == "personal_non_sensitive"


def test_offline_mode_makes_everything_local_only(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn, mode="offline")
    state = _state(p11_conn)
    assert state.model_eligibility == v.LOCAL_ONLY
    assert may_assemble_dossier(state) is False


def test_local_model_mode_is_local_only_on_p7s_own_authority(p11_conn):
    # The mode gate is `privacy.denial.mode_forbids`, not a P11 copy of the list.
    # If P7 ever moved a mode across that line P11 would move with it.
    _classify(p11_conn)
    _policy(p11_conn, mode="local_model")
    assert mode_forbids("local_model", "cloud") is True
    assert _state(p11_conn).model_eligibility == v.LOCAL_ONLY


def test_a_non_sensitive_file_in_hybrid_mode_may_reach_a_dossier(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    state = _state(p11_conn)
    assert state.model_eligibility == v.DOSSIER_PERMITTED
    assert may_assemble_dossier(state) is True


def test_unclassified_arrives_only_as_absence_so_the_carry_has_one_path(p11_conn):
    # P7 REFUSES to store `unreadable_unclassified`: it is a gate outcome, and the
    # absence of a record already says nothing has looked (D2). So a P11 branch
    # reading `record.handling_class == UNREADABLE_UNCLASSIFIED` could never fire,
    # and blocking on absence is not one of two paths -- it is the only one.
    _policy(p11_conn)
    with pytest.raises(GateOutcomeNotAFileFact):
        _classify(p11_conn, handling_class=UNREADABLE_UNCLASSIFIED)
    # So the value can only ever arrive from absence, through `resolve_class`.
    assert _state(p11_conn).handling_class == UNREADABLE_UNCLASSIFIED


def test_a_handling_class_can_never_be_a_redaction_setting_key(p11_conn):
    # Guards a check that could never fire: `redaction_settings` is keyed by
    # §8.4's five DISPLAY facets, and `Policy` raises on anything else. Deriving
    # `redacted` eligibility by looking a handling class up in it would be a
    # branch no corpus could ever take.
    assert "sensitive_personal" not in DISPLAY_FACETS
    with pytest.raises(OutOfVocabulary):
        Policy(policy_version="pol-x", operation_mode="hybrid", consent_grants=(),
               redaction_settings={"sensitive_personal": "redacted"},
               automatic_move_permissions={}, plan_version="plan-1", set_at=T0)


# --- the §8.4 move permission, asked of P7 rather than re-derived -----------------

def test_the_move_permission_is_p7s_live_predicate(p11_conn, tmp_path):
    assert list(inspect.signature(p7_moves.may_move_automatically).parameters) == [
        "conn", "file_id", "plan_version"]
    file_id, content_hash = _real_file(p11_conn, tmp_path / "corpus")
    ClassificationStore(p11_conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="sensitive_personal", protected=True, basis="detector",
        evidence_refs=(OBS,), reliability_state="direct", observed_at=T0))
    _policy(p11_conn)
    assert automatic_move_permitted_for(
        p11_conn, file_id=file_id, plan_version="plan-1") is False


def test_the_permission_is_keyed_on_the_file_id_p7_keys_it_on(p11_conn, tmp_path):
    # `automatic_move_permissions` is keyed by file id (`moves.py`), not by
    # handling class. A P11 that keyed it by class would permit nothing, ever.
    file_id, content_hash = _real_file(p11_conn, tmp_path / "corpus")
    ClassificationStore(p11_conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="sensitive_personal", protected=True, basis="detector",
        evidence_refs=(OBS,), reliability_state="direct", observed_at=T0))
    _policy(p11_conn, permissions={"sensitive_personal": True})
    assert automatic_move_permitted_for(
        p11_conn, file_id=file_id, plan_version="plan-1") is False
    _policy(p11_conn, permissions={file_id: True})
    assert automatic_move_permitted_for(
        p11_conn, file_id=file_id, plan_version="plan-1") is True


# --- the review policy ------------------------------------------------------------

def test_a_protected_file_is_never_auto_eligible_without_an_explicit_permission(p11_conn):
    # Design:185: protected material "should not be moved automatically without a
    # user policy that explicitly permits it". The gate is the FLAG, not the mode:
    # under `offline` every file is local_only and most of them are ordinary.
    _classify(p11_conn, handling_class="sensitive_personal", protected=True)
    _policy(p11_conn)
    assert review_policy_for(privacy_state=_state(p11_conn),
                             two_condition=_two_condition(), group_support=None,
                             unique_direct_match=True,
                             destination_disposition=None) == v.REVIEW_REQUIRED


def test_an_explicit_permission_restores_automatic_eligibility(p11_conn):
    _classify(p11_conn, handling_class="sensitive_personal", protected=True)
    _policy(p11_conn, permissions={"f1": True})
    assert review_policy_for(privacy_state=_state(p11_conn),
                             two_condition=_two_condition(), group_support=None,
                             unique_direct_match=True,
                             automatic_move_permitted=True,
                             destination_disposition=None) == v.AUTO_ELIGIBLE


def test_local_only_alone_does_not_force_review(p11_conn):
    # Egress eligibility and move permission are different axes. `offline` is one
    # of the two modes that may ship as the install default, so reading it as
    # "review everything" would make §6.6's deterministic path dead on arrival.
    _classify(p11_conn)
    _policy(p11_conn, mode="offline")
    state = _state(p11_conn)
    assert state.model_eligibility == v.LOCAL_ONLY
    assert review_policy_for(privacy_state=state, two_condition=_two_condition(),
                             group_support=None, unique_direct_match=True,
                             destination_disposition=None) == v.AUTO_ELIGIBLE


def test_a_context_supported_verdict_always_requires_review(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn),
        two_condition=_two_condition(verdict="accept_context_supported",
                                     requires_review=True),
        group_support=None, unique_direct_match=False,
        destination_disposition=None) == v.REVIEW_REQUIRED


def test_a_verdict_requiring_review_is_the_only_thing_that_need_forbid_auto(p11_conn):
    # Every other gate is deliberately left open here. Sharing a test with the
    # non-unique-match case would let either check be deleted with the suite
    # staying green, which is a guard that cannot fail.
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn),
        two_condition=_two_condition(requires_review=True),
        group_support=None, unique_direct_match=True,
        destination_disposition=None) == v.REVIEW_REQUIRED


def test_a_user_attached_membership_never_reaches_auto_eligible(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=GroupSupport(group_id="g1", membership="user-attached"),
        unique_direct_match=True,
        destination_disposition=None) == v.REVIEW_REQUIRED


def test_a_decision_that_is_not_a_unique_direct_match_requires_review(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=None, unique_direct_match=False,
        destination_disposition=None) == v.REVIEW_REQUIRED


def test_a_null_protected_flag_is_refused_rather_than_read_as_false(p11_conn):
    # The whole reason the flag is carried is that consumers must not infer it.
    # A `None` reaching a consumer that tests it truthily reads as "not protected",
    # which is the silent downgrade this record exists to prevent.
    from placement.records import MalformedPlacementRecord, PrivacyState

    with pytest.raises(MalformedPlacementRecord):
        PrivacyState(handling_class="sensitive_personal", protected=None,
                     model_eligibility=v.LOCAL_ONLY, consent_audit_ref=None)


def test_the_unclassified_answer_is_blocked_and_not_a_quiet_review(p11_conn):
    assert blocked_policy() == v.BLOCKED_PENDING_USER


def test_an_unclassified_file_is_never_auto_eligible_however_strong_the_match(
        p11_conn):
    """The negative half of "one unclassified file no longer refuses the run".

    A fix that merely stopped raising would leave every file nobody classified
    ORDINARY -- and a unique direct match at an ordinary node with a permissive
    policy is precisely the shape that reaches `auto_eligible`. An unattended move
    of a file nothing has ever looked at is the outcome §8.4's gate exists to
    prevent, so every other input here is as permissive as it can be made.
    """
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn),
        two_condition=_two_condition(support_score=1.0, margin_over_next=0.99,
                                     meets_threshold=True, requires_review=False),
        group_support=None, unique_direct_match=True,
        automatic_move_permitted=True,
        destination_disposition=None) == v.BLOCKED_PENDING_USER


def test_blocked_is_a_different_obligation_from_the_ordinary_review_queue(p11_conn):
    """`blocked_pending_user` and `review_required` ask the person for two things.

    A reviewer can confirm a decision that merely needs confirming; they cannot
    confirm one whose subject nothing has classified, because there is nothing to
    confirm it against. A protected file with no move permission gets the second
    -- it is a decision about SENSITIVITY, and it is actionable. An unclassified
    file gets the first. Collapsing them would put a file nobody looked at into
    the ordinary approve queue, and would also describe a passport as an evidence
    failure on the way past.
    """
    _policy(p11_conn)
    _classify(p11_conn, file_id="f2", handling_class="sensitive_personal",
              protected=True)
    protected = privacy_state_for(p11_conn, file_id="f2", content_hash="h1",
                                  plan_version="plan-1")
    ordinary = dict(two_condition=_two_condition(), group_support=None,
                    unique_direct_match=True, destination_disposition=None)
    assert review_policy_for(privacy_state=protected, **ordinary) == v.REVIEW_REQUIRED
    assert review_policy_for(privacy_state=_state(p11_conn),
                             **ordinary) == v.BLOCKED_PENDING_USER


def test_the_unclassified_gate_is_asked_before_the_destinations(p11_conn):
    # Ordering, and it is load-bearing. A review-only destination answers
    # `review_required` on its own, so an unclassified file sent to one would come
    # back describable as "just needs a look" if the class were checked second.
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=None, unique_direct_match=True,
        destination_disposition=v.REVIEW_ONLY) == v.BLOCKED_PENDING_USER


# --- §7.4's residual disposition: what happens when a node IS chosen -------------
#
# `IndexEntry.disposition` was written and validated by `placement/index.py` and
# read by nothing -- P10 escalated that as an open cross-part question and left two
# xfail tests standing on it. It holds the only thing that stops an automatic file
# move, so a field with no reader is the whole defect.
#
# 00:121 settles the shape: the three dispositions all become "legal nodes in the
# frozen destination tree" and "the LLM may choose among them later". So the
# disposition does not govern WHETHER a node may be chosen -- `accepts_placement`
# stays the one legality authority -- it governs WHAT HAPPENS when it is.

def test_a_review_only_destination_never_auto_applies_however_strong_the_match(p11_conn):
    # 00:121's adverb is the whole rule: a review-only category "never moves files
    # automatically". Every other input here is as permissive as it can be -- a
    # top score, a huge margin, a unique direct match, an unprotected file -- so
    # if this returns auto_eligible the policy is reading confidence where it
    # should be reading disposition.
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn),
        two_condition=_two_condition(support_score=1.0, margin_over_next=0.99,
                                     meets_threshold=True, requires_review=False),
        group_support=None, unique_direct_match=True,
        automatic_move_permitted=True,
        destination_disposition=v.REVIEW_ONLY) == v.REVIEW_REQUIRED


def test_a_leave_in_place_destination_never_auto_applies_either(p11_conn):
    # 00:120's "represent without moving" is a first-class outcome, and a policy
    # that tells the system to leave files in place cannot be acted on unattended.
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn),
        two_condition=_two_condition(support_score=1.0, margin_over_next=0.99),
        group_support=None, unique_direct_match=True,
        automatic_move_permitted=True,
        destination_disposition=v.LEAVE_IN_PLACE_DISPOSITION) == v.REVIEW_REQUIRED


def test_a_physical_destination_is_still_reachable_automatically(p11_conn):
    # The gate is not a blanket refusal. A residual node the user made a real
    # physical destination behaves like any other node, or enabling the residual
    # library would quietly turn every one of its branches into review work.
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=None, unique_direct_match=True,
        destination_disposition=v.PHYSICAL_DESTINATION) == v.AUTO_ELIGIBLE


def test_an_ordinary_node_carries_no_disposition_and_is_unaffected(p11_conn):
    # §7.4 makes the disposition required on a residual node and meaningless on
    # every other role, which `placement/index.py` already enforces.
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=None, unique_direct_match=True,
        destination_disposition=None) == v.AUTO_ELIGIBLE


def test_an_unknown_disposition_refuses_rather_than_permitting_a_move(p11_conn):
    # The defect shape this whole gate exists to avoid: a value outside the closed
    # set falling through to the permissive branch. A typo must be a load error.
    _classify(p11_conn)
    _policy(p11_conn)
    with pytest.raises(v.OutOfVocabulary):
        review_policy_for(
            privacy_state=_state(p11_conn), two_condition=_two_condition(),
            group_support=None, unique_direct_match=True,
            destination_disposition="physical_destination")


def test_the_disposition_the_index_carries_is_the_one_the_policy_reads(p11_conn):
    # The binding that closes P10's escalation: the value travels from the frozen
    # tree, through `build_destination_index`, out of `entry_for`, and into the
    # policy. Asserting the two agree by inspection would leave the field exactly
    # as unread as it was.
    from placement.index import build_destination_index, entry_for
    from p11.p10_fixtures import FROZEN_TREE

    _classify(p11_conn)
    _policy(p11_conn)
    build_destination_index(p11_conn, FROZEN_TREE, component_version="P11-test",
                            observed_at=T0)
    entry = entry_for(p11_conn, plan_version="plan-1", node_id="n-review-later")
    assert entry.disposition == v.REVIEW_ONLY
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=None, unique_direct_match=True,
        destination_disposition=entry.disposition) == v.REVIEW_REQUIRED


def test_a_review_only_node_is_still_a_legal_destination(p11_conn):
    # 00:121: all three dispositions "become legal nodes in the frozen destination
    # tree" and "the LLM may choose among them later". A second legality gate here
    # would contradict `index.py`'s own warning that two callables answering one
    # question differently is the defect.
    from placement.index import build_destination_index, legal_node_ids

    build_destination_index(p11_conn, FROZEN_TREE_FOR_LEGALITY,
                            component_version="P11-test", observed_at=T0)
    assert "n-review-later" in legal_node_ids(p11_conn, plan_version="plan-1")


def test_the_disposition_has_no_default_so_it_cannot_be_silently_skipped():
    # A default would let a caller omit the argument and get the ordinary-node
    # answer -- which is the exact state this field was already in: written,
    # validated, and read by nothing. The absence of the default IS the guard, so
    # something has to hold it.
    parameter = inspect.signature(review_policy_for).parameters[
        "destination_disposition"]
    assert parameter.default is inspect.Parameter.empty
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_which_dispositions_move_files_at_all(p11_conn):
    from placement.privacy import moves_files

    assert moves_files(v.PHYSICAL_DESTINATION) is True
    assert moves_files(None) is True
    assert moves_files(v.REVIEW_ONLY) is False
    assert moves_files(v.LEAVE_IN_PLACE_DISPOSITION) is False


def test_moves_files_refuses_a_value_outside_the_closed_set(p11_conn):
    # `.get(value, True)` would answer "yes, move it" for a misspelling. That is
    # the one answer this predicate must never give by accident.
    from placement.privacy import moves_files

    with pytest.raises(v.OutOfVocabulary):
        moves_files("review_only")
