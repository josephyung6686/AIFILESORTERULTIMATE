# tests/p7/test_p7_moves.py
"""Done-means 9's first clause: §8.4's automatic-move predicate.

Three sentences decide every assertion here and none of them is P7's. §8.4: protected
material "should not be moved automatically without a user policy that explicitly
permits it." §7.11: the system "must not delete files, mark them disposable, or move
them out of a protected area without explicit user action." §8.8: "A new plan should
never silently reclassify or move old files."

The fourth fact is D2's, and it is why so much of this file is about absence: no
detector exists, so on a real corpus `store.current(...)` returns None for every file
and the verdict is `unreadable_unclassified` every time. That is the honest posture
rather than a gap, and one test says so by name.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from database_agent.files_table import get_file, record_file

from privacy.classification import ClassificationRecord, resolve_class
from privacy.classification_store import ClassificationStore
from privacy.moves import (
    MOVE_REASONS, NOT_PROTECTED, POLICY_PERMITS,
    PROTECTED_WITHOUT_PERMITTING_POLICY, UNREADABLE_UNCLASSIFIED, MoveVerdict,
    may_move_automatically,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, current_policy, set_policy
from privacy.vocabulary import USER, USER_CONFIRMED

FIXED_CLOCK = "2026-08-22T12:00:00+00:00"
COMPONENT = "0.1.0"
PLAN_ONE = "plan-1"
PLAN_TWO = "plan-2"


def _write_document(conn, directory, name, body):
    """A real P1 row. `record_file` stats the path, so the bytes land first."""
    directory.mkdir(exist_ok=True)
    document = directory / name
    document.write_bytes(body)
    return record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(directory), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)


@pytest.fixture()
def file_id(p7_conn, tmp_path):
    """The classification is keyed on (file_id, content_hash) and a synthesized id
    would not exercise the hash lookup the predicate performs."""
    return _write_document(p7_conn, tmp_path / "corpus", "passport-scan.pdf",
                           b"%PDF-1.4 fixture bytes")


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


@pytest.fixture()
def store(p7_conn):
    return ClassificationStore(p7_conn)


def a_policy(**over) -> Policy:
    base = dict(policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
                consent_grants=(("Academics", "cloud_model"),),
                redaction_settings={"names": "redacted", "previews": "redacted",
                                    "thumbnails": "redacted", "ocr_text": "redacted",
                                    "location_data": "redacted"},
                automatic_move_permissions={}, plan_version=PLAN_ONE,
                set_at=FIXED_CLOCK)
    base.update(over)
    return Policy(**base)


def stored(conn, **over) -> str:
    """Store a policy; return the version the gate minted for it.

    SPEC §6: "the gate owns the policy, so the caller does not supply this value, it
    echoes it." The tests below compare the verdict against the RETURNED version, not
    against the placeholder `a_policy` carries in, which is what makes
    `permitting_policy` a fact P11 and P12 can record rather than a value the caller
    already had.
    """
    return set_policy(conn, a_policy(**over), component_version=COMPONENT,
                      user_id="joseph", reason="the policy this test starts from")


def classify(store, file_id, content_hash, *, handling_class, protected):
    """Stand in for the detector that does not exist (D2).

    `basis = USER` rather than `DETECTOR`, because Task 3 refuses a detector record
    with no `evidence_refs` and this test has no detector to have fired.

    A second call supersedes the first through Task 4's `current_fact_id` and
    `supersede`: §8.2 forbids overwriting, and two unsuperseded records would leave
    `current(...)` ambiguous and this file testing the wrong thing.
    """
    prior_fact_id = store.current_fact_id(file_id, content_hash)
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis=USER, evidence_refs=(),
        reliability_state=USER_CONFIRMED, observed_at=FIXED_CLOCK)
    fact_id = store.write(record)
    if prior_fact_id is not None:
        store.supersede(prior_fact_id, fact_id, "the fixture revises its own record")
    return record


# --- the shape SPEC §9 published ---------------------------------------------

def test_the_verdict_carries_specs_three_fields_and_no_fourth(p7_conn):
    # SPEC §9: `Gate.may_move_automatically(file_id, plan_version) -> { allowed,
    # reason, permitting_policy? }`. Read off the dataclass, never off the class body.
    assert [f.name for f in dataclasses.fields(MoveVerdict)] == [
        "allowed", "reason", "permitting_policy"]


def test_the_verdict_is_frozen_so_a_caller_cannot_edit_a_refusal_into_a_permission():
    verdict = MoveVerdict(allowed=False,
                          reason=PROTECTED_WITHOUT_PERMITTING_POLICY,
                          permitting_policy=None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        verdict.allowed = True


def test_the_four_reasons_are_the_only_ones_the_predicate_can_return(
        p7_conn, file_id, content_hash, store):
    assert len(MOVE_REASONS) == 4
    assert set(MOVE_REASONS) == {
        NOT_PROTECTED, POLICY_PERMITS, PROTECTED_WITHOUT_PERMITTING_POLICY,
        UNREADABLE_UNCLASSIFIED}
    seen = set()
    stored(p7_conn)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    stored(p7_conn, plan_version=PLAN_TWO,
           automatic_move_permissions={file_id: True})
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_TWO).reason)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    seen.add(may_move_automatically(p7_conn, file_id, PLAN_ONE).reason)
    assert seen == set(MOVE_REASONS)


def test_move_reasons_is_published_in_the_order_the_predicate_decides():
    # The preamble fixes the read order -- "absence, then the flag, then the policy"
    # -- and `MOVE_REASONS` is that order written down. Absence FIRST is the whole
    # point: a predicate that read the flag first would answer `not_protected` for
    # every file in a corpus with no detector.
    assert MOVE_REASONS == (UNREADABLE_UNCLASSIFIED, NOT_PROTECTED, POLICY_PERMITS,
                            PROTECTED_WITHOUT_PERMITTING_POLICY)


def test_no_move_reason_is_prose(p7_conn):
    # §3.1: "A reason that is an English sentence tested by substring containment is
    # a second home for a vocabulary and it puts UX copy into a value P11/P12 will
    # store verbatim." Every reason is a snake_case identifier.
    for reason in MOVE_REASONS:
        assert reason == reason.lower()
        assert " " not in reason
        assert reason.replace("_", "").isalnum()


# --- absence, which is every file until a detector exists ---------------------

def test_absence_of_a_classification_refuses_and_never_reads_as_public(
        p7_conn, file_id):
    # D2: "Unreadable or unclassified is a GATE OUTCOME, not a file fact." §8.6: cost
    # exhaustion "must never turn into lower-quality automatic classification" -- the
    # forbidden move is exactly resolving absence to a low class so work can continue.
    stored(p7_conn)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == UNREADABLE_UNCLASSIFIED
    assert verdict.reason == "unreadable_unclassified"
    assert verdict.reason != "public_low"
    assert verdict.permitting_policy is None


def test_absence_refuses_even_when_a_policy_names_this_very_file(
        p7_conn, file_id):
    # Absence is checked BEFORE the policy as well as before the flag. A permission
    # cannot stand in for a classification: §8.4 permits moving PROTECTED material,
    # and nothing here knows whether this file is protected.
    stored(p7_conn, automatic_move_permissions={file_id: True})
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == UNREADABLE_UNCLASSIFIED
    assert verdict.permitting_policy is None


def test_the_unclassified_reason_is_task_3s_value_and_not_a_second_spelling():
    # One string, one owner. A second literal here is a second place for the two to
    # disagree, and Task 3 owns the rule that absence resolves to this class.
    assert UNREADABLE_UNCLASSIFIED == resolve_class(None)


def test_with_no_detector_every_file_gets_that_verdict(p7_conn, tmp_path):
    # The honest v1 posture, stated in the suite rather than in a report. No task in
    # any plan produces a detector rule set (D2), so this is what a real corpus looks
    # like on the day P7 ships: a correct, locked door with nobody holding a key.
    stored(p7_conn)
    for index in range(3):
        new_id = _write_document(p7_conn, tmp_path / "many", f"file-{index}.pdf",
                                 f"%PDF-1.4 body {index}".encode())
        verdict = may_move_automatically(p7_conn, new_id, PLAN_ONE)
        assert verdict == MoveVerdict(allowed=False,
                                      reason=UNREADABLE_UNCLASSIFIED,
                                      permitting_policy=None)


# --- protected material, with and without a permitting policy -----------------

def test_protected_material_without_a_permitting_policy_cannot_move(
        p7_conn, file_id, content_hash, store):
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it." §7.11: the system must not "move them out of
    # a protected area without explicit user action."
    stored(p7_conn)
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY


def test_protected_material_refuses_when_no_policy_has_ever_been_set(
        p7_conn, file_id, content_hash, store):
    # `current_policy` returns None when nothing has been set, and that is the
    # ORDINARY state on a fresh install -- policy.py: "None is a fact, not a gap."
    # §7.11 makes refusal the default branch, so the absence of a policy is the
    # absence of a permission and never an unhandled crash.
    assert current_policy(p7_conn, plan_version=PLAN_ONE) is None
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY
    assert verdict.permitting_policy is None


def test_an_unprotected_file_needs_no_policy_at_all(
        p7_conn, file_id, content_hash, store):
    # The flag is read before the policy, so an unclassified-policy database still
    # answers for a file nothing protects.
    assert current_policy(p7_conn, plan_version=PLAN_ONE) is None
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE) == MoveVerdict(
        allowed=True, reason=NOT_PROTECTED, permitting_policy=None)


def test_a_policy_that_explicitly_permits_this_file_allows_the_move(
        p7_conn, file_id, content_hash, store):
    stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is True
    assert verdict.reason == POLICY_PERMITS


def test_the_permitting_policy_is_named_in_the_verdict(
        p7_conn, file_id, content_hash, store):
    # Done-means 9's second clause depends on this field existing: P11 records the
    # answer in the placement decision (§6.11 "required review policy") and P12 in the
    # plan precondition (§8.3 "Sensitivity and consent state"), and neither re-derives
    # it. The version asserted is the one the GATE minted, not the placeholder in.
    version = stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.permitting_policy == version
    assert verdict.permitting_policy != UNSET_POLICY_VERSION


def test_the_named_policy_is_the_one_in_force_and_not_a_superseded_one(
        p7_conn, file_id, content_hash, store):
    # A permission granted, then re-granted, mints two versions. Naming the older one
    # would let P11 record a permission that is no longer in force.
    superseded = stored(p7_conn, automatic_move_permissions={file_id: True})
    live = stored(p7_conn, automatic_move_permissions={file_id: True})
    assert live != superseded
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy == live


def test_a_refusal_names_no_permitting_policy(
        p7_conn, file_id, content_hash, store):
    # There is no policy to name, and naming one would let a caller record a
    # permission that never existed.
    stored(p7_conn)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy is None
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy is None


def test_a_permitted_file_does_not_permit_its_neighbour(
        p7_conn, file_id, content_hash, store, tmp_path):
    # The permission is keyed on the file id, so it covers one file and not the
    # directory it sits in.
    stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    neighbour = _write_document(p7_conn, tmp_path / "corpus", "sibling.pdf",
                                b"%PDF-1.4 sibling bytes")
    classify(store, neighbour, get_file(p7_conn, neighbour)["content_hash"],
             handling_class="sensitive_personal", protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True
    assert may_move_automatically(p7_conn, neighbour, PLAN_ONE).allowed is False


def test_a_withdrawn_permission_does_not_permit(
        p7_conn, file_id, content_hash, store):
    # §8.7's recorded action is "granting or withdrawing an automatic-move permission
    # for protected material". A withdrawal is a stored `False`, not an absent key,
    # and both refuse -- but only the stored `False` proves the branch reads the value
    # rather than the presence of the key.
    stored(p7_conn, automatic_move_permissions={file_id: False})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY
    assert verdict.permitting_policy is None


def test_a_grant_at_a_scope_p7_cannot_resolve_does_not_permit(
        p7_conn, file_id, content_hash, store):
    # Open question 3: "What is a 'corpus area'? ... Consent grants cannot be scoped
    # until this is named." P7 defines no area, so the only key it can resolve to a
    # file is the file's own id. A grant at "Academics" is not read as covering this
    # file, and the alternative -- guessing that it does -- would widen egress policy
    # on an unanswered question.
    stored(p7_conn, automatic_move_permissions={"Academics": True, "/Users/jy": True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False


def test_a_consent_grant_is_not_a_move_permission(
        p7_conn, file_id, content_hash, store):
    # §8.4 keeps the two apart: a consent grant authorizes a MODEL CALL and a move
    # permission authorizes a MOVE. `a_policy` carries a `cloud_model` grant in every
    # test here, and it permits no move anywhere in this file.
    version = stored(p7_conn, consent_grants=((file_id, "cloud_model"),))
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert current_policy(p7_conn, plan_version=PLAN_ONE).policy_version == version
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is False
    assert verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY


# --- the flag, not the class (SPEC §2, Open question 1) -----------------------

def test_a_file_that_is_not_protected_may_move(
        p7_conn, file_id, content_hash, store):
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    verdict = may_move_automatically(p7_conn, file_id, PLAN_ONE)
    assert verdict.allowed is True
    assert verdict.reason == NOT_PROTECTED
    assert verdict.permitting_policy is None


def test_the_verdict_keys_on_the_flag_and_not_the_handling_class(
        p7_conn, file_id, content_hash, store):
    # SPEC §2: "Neighbouring parts should consume the `protected` flag, not infer it
    # from the class." Open question 1 -- whether `protected` is exactly the top two
    # classes -- is unsettled, so both records below are legal and the flag wins in
    # both directions.
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False
    classify(store, file_id, content_hash,
             handling_class="highly_sensitive_credential_bearing", protected=False)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True


# --- §8.8: the plan version is not decoration ---------------------------------

def test_a_later_plan_version_does_not_retroactively_permit(
        p7_conn, file_id, content_hash, store):
    # §8.8: "A new plan should never silently reclassify or move old files." The
    # permission is adopted at plan-2; asking under plan-1 must not see it.
    stored(p7_conn, plan_version=PLAN_ONE, automatic_move_permissions={})
    stored(p7_conn, plan_version=PLAN_TWO,
           automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is True


def test_a_permission_does_not_leak_forward_into_a_later_plan_either(
        p7_conn, file_id, content_hash, store):
    # The symmetric half. §8.8 makes the user policy one of the two things that
    # "define which projections are valid in each version", so a permission granted
    # under plan-1 is not in force under plan-2 unless plan-2 carries it too.
    stored(p7_conn, plan_version=PLAN_ONE,
           automatic_move_permissions={file_id: True})
    stored(p7_conn, plan_version=PLAN_TWO, automatic_move_permissions={})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is False


def test_the_named_policy_is_the_one_at_the_asked_for_plan_version(
        p7_conn, file_id, content_hash, store):
    # Two plan versions, each permitting the file, mint two different versions. The
    # verdict names the one belonging to the plan version asked about -- otherwise
    # P11 would record a permission from a plan it is not executing.
    one = stored(p7_conn, plan_version=PLAN_ONE,
                 automatic_move_permissions={file_id: True})
    two = stored(p7_conn, plan_version=PLAN_TWO,
                 automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(
        p7_conn, file_id, PLAN_ONE).permitting_policy == one
    assert may_move_automatically(
        p7_conn, file_id, PLAN_TWO).permitting_policy == two


def test_the_classification_is_shared_across_plan_versions(
        p7_conn, file_id, content_hash, store):
    # §8.8: "The evidence database remains shared across plan versions." The
    # classification is looked up with no plan version at all; only the policy is
    # plan-scoped, and that asymmetry is §8.8's and not this task's.
    stored(p7_conn, plan_version=PLAN_ONE, automatic_move_permissions={})
    stored(p7_conn, plan_version=PLAN_TWO, automatic_move_permissions={})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    for plan_version in (PLAN_ONE, PLAN_TWO):
        assert may_move_automatically(
            p7_conn, file_id, plan_version).reason == (
                PROTECTED_WITHOUT_PERMITTING_POLICY)


def test_a_reclassification_changes_the_verdict_without_the_policy_moving(
        p7_conn, file_id, content_hash, store):
    # The other half of the asymmetry: the classification is the thing that is
    # shared, so superseding it changes every plan version's answer at once.
    stored(p7_conn, plan_version=PLAN_ONE, automatic_move_permissions={})
    stored(p7_conn, plan_version=PLAN_TWO, automatic_move_permissions={})
    classify(store, file_id, content_hash, handling_class="public_low",
             protected=False)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is True
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is True
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    assert may_move_automatically(p7_conn, file_id, PLAN_ONE).allowed is False
    assert may_move_automatically(p7_conn, file_id, PLAN_TWO).allowed is False


# --- C4: a predicate writes nothing -------------------------------------------

def test_the_predicate_writes_nothing(p7_conn, file_id, content_hash, store):
    # C4: "a gate that also wrote would be doing two jobs." This one does not even
    # release; it answers a question P11 and P12 ask before they plan a move.
    stored(p7_conn)
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    before = p7_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    mirror = get_file(p7_conn, file_id)["sensitivity_state"]
    for plan_version in (PLAN_ONE, PLAN_TWO, PLAN_ONE):
        may_move_automatically(p7_conn, file_id, plan_version)
    assert p7_conn.execute(
        "SELECT count(*) c FROM events").fetchone()["c"] == before
    assert get_file(p7_conn, file_id)["sensitivity_state"] == mirror


def test_the_predicate_issues_no_write_statement_at_all(
        p7_conn, file_id, content_hash, store):
    # §3.12's device: `set_trace_callback` observes the SQL at run time, which is how
    # this project proves a no-write claim without grepping source text. A predicate
    # that minted a policy version or appended an event would show up here.
    stored(p7_conn, automatic_move_permissions={file_id: True})
    classify(store, file_id, content_hash, handling_class="sensitive_personal",
             protected=True)
    statements: list[str] = []
    p7_conn.set_trace_callback(statements.append)
    try:
        may_move_automatically(p7_conn, file_id, PLAN_ONE)
    finally:
        p7_conn.set_trace_callback(None)
    assert statements, "the trace callback saw nothing, so it proves nothing"
    for statement in statements:
        first = statement.strip().split(None, 1)[0].upper()
        assert first == "SELECT", statement


# --- the half of Done-means 9 that cannot be proved here ----------------------

def test_p11_and_p12_consuming_the_answer_is_not_provable_inside_p7(p7_conn):
    """Done-means 9's second clause is a property of two parts that do not exist.

    The coverage table states it: "**Partly.** First clause yes. The second is a
    property of P11 and P12, which do not exist; P7 makes it *possible* by naming the
    permitting policy in the verdict." §6.11's "required review policy" and §8.3's
    "Sensitivity and consent state" are where the answer lands, and neither field has
    a schema in this repository yet.

    What P7 can assert is that the verdict is complete enough to be recorded without
    re-derivation: three fields, and the permitting policy named whenever one
    permitted. That is asserted above. The rest is P11's and P12's, and this test
    exists so the limitation is in the suite rather than in a report nobody rereads.
    """
    assert [f.name for f in dataclasses.fields(MoveVerdict)] == [
        "allowed", "reason", "permitting_policy"]
