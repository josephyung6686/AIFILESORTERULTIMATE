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
    ClassificationRequired, PolicyRequired, automatic_move_permitted_for,
    blocked_policy, may_assemble_dossier, privacy_state_for, review_policy_for,
)
from placement.records import GroupSupport, TwoCondition

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

def test_an_unclassified_file_blocks_and_never_defaults_to_public(p11_conn):
    _policy(p11_conn)
    with pytest.raises(ClassificationRequired):
        _state(p11_conn)


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
    with pytest.raises(ClassificationRequired):
        _state(p11_conn)


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
                             unique_direct_match=True) == v.REVIEW_REQUIRED


def test_an_explicit_permission_restores_automatic_eligibility(p11_conn):
    _classify(p11_conn, handling_class="sensitive_personal", protected=True)
    _policy(p11_conn, permissions={"f1": True})
    assert review_policy_for(privacy_state=_state(p11_conn),
                             two_condition=_two_condition(), group_support=None,
                             unique_direct_match=True,
                             automatic_move_permitted=True) == v.AUTO_ELIGIBLE


def test_local_only_alone_does_not_force_review(p11_conn):
    # Egress eligibility and move permission are different axes. `offline` is one
    # of the two modes that may ship as the install default, so reading it as
    # "review everything" would make §6.6's deterministic path dead on arrival.
    _classify(p11_conn)
    _policy(p11_conn, mode="offline")
    state = _state(p11_conn)
    assert state.model_eligibility == v.LOCAL_ONLY
    assert review_policy_for(privacy_state=state, two_condition=_two_condition(),
                             group_support=None,
                             unique_direct_match=True) == v.AUTO_ELIGIBLE


def test_a_context_supported_verdict_always_requires_review(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn),
        two_condition=_two_condition(verdict="accept_context_supported",
                                     requires_review=True),
        group_support=None, unique_direct_match=False) == v.REVIEW_REQUIRED


def test_a_verdict_requiring_review_is_the_only_thing_that_need_forbid_auto(p11_conn):
    # Every other gate is deliberately left open here. Sharing a test with the
    # non-unique-match case would let either check be deleted with the suite
    # staying green, which is a guard that cannot fail.
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn),
        two_condition=_two_condition(requires_review=True),
        group_support=None, unique_direct_match=True) == v.REVIEW_REQUIRED


def test_a_user_attached_membership_never_reaches_auto_eligible(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=GroupSupport(group_id="g1", membership="user-attached"),
        unique_direct_match=True) == v.REVIEW_REQUIRED


def test_a_decision_that_is_not_a_unique_direct_match_requires_review(p11_conn):
    _classify(p11_conn)
    _policy(p11_conn)
    assert review_policy_for(
        privacy_state=_state(p11_conn), two_condition=_two_condition(),
        group_support=None, unique_direct_match=False) == v.REVIEW_REQUIRED


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
