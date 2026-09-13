# tests/p7/test_p7_file_held.py
"""THE RULING (owner, 13 Sep 2026): a protected record is filed by the person,
not by a model. `--file-held FILE_ID` is that one gesture, and `cli.apply_file_held`
is what it calls.

Three facts pin it, and none of them is a new rule -- each is an existing one this
gesture must not disturb:

* `privacy.moves.may_move_automatically` already refuses a protected file with no
  permitting policy (§8.4) and already permits one a policy names. This gesture's
  whole job is to make that second branch reachable for a file the person files
  themselves, and nothing else.
* `basis="user"` on a classification row is a `CLOUD_CLEARING_BASES` member
  (`cli.py`): it is what opens the cloud door. This gesture writes no
  classification row at all, so the file's classification -- basis, handling
  class, protected flag, fact id -- is byte-for-byte the same before and after.
* A file id `--file-held` names that this database has never recorded is refused
  by a sentence, the way `cli.apply_answers` refuses a `question_id` it has never
  asked about, rather than silently doing nothing.
"""
from __future__ import annotations

import json

import pytest

import cli
from database_agent.files_table import get_file, record_file
from evidence_shape.observation import observation_key

from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.moves import POLICY_PERMITS, PROTECTED_WITHOUT_PERMITTING_POLICY, \
    may_move_automatically
from privacy.policy import UNSET_POLICY_VERSION, Policy, current_policy, set_policy
from privacy.vocabulary import DETECTOR, USER_CONFIRMED

FIXED_CLOCK = "2026-09-13T00:00:00+00:00"
COMPONENT = "0.1.0"
PLAN_VERSION = cli.PLAN_VERSION


def _write_document(conn, directory, name, body):
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
    return _write_document(p7_conn, tmp_path / "corpus", "passport-scan.pdf",
                           b"%PDF-1.4 fixture bytes")


@pytest.fixture()
def content_hash(p7_conn, file_id):
    return get_file(p7_conn, file_id)["content_hash"]


@pytest.fixture()
def protected_classification(p7_conn, file_id, content_hash):
    """Protected by a DETECTOR-basis row -- deliberately not a `CLOUD_CLEARING_BASES`
    member, so a test that finds the basis unchanged is finding it still absent."""
    store = ClassificationStore(p7_conn)
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="highly_sensitive_credential_bearing", protected=True,
        basis=DETECTOR, evidence_refs=(observation_key(
            content_hash=content_hash, extractor_name="fixture.text",
            locator="body:page=1#0-10", raw_value="passport number 123"),),
        reliability_state=USER_CONFIRMED, observed_at=FIXED_CLOCK)
    store.write(record)
    return record


@pytest.fixture()
def standing_policy(p7_conn):
    """The policy already in force at `cli.PLAN_VERSION` -- what `--file-held`
    reads and adds one permission to. `apply_file_held` does not invent one."""
    return set_policy(
        p7_conn, Policy(
            policy_version=UNSET_POLICY_VERSION, operation_mode="offline",
            consent_grants=(), redaction_settings={},
            automatic_move_permissions={}, plan_version=PLAN_VERSION,
            set_at=FIXED_CLOCK),
        component_version=COMPONENT, user_id="joseph",
        reason="the policy this test starts from")


def test_the_gesture_permits_the_move_and_leaves_the_classification_and_the_route(
        p7_conn, file_id, content_hash, protected_classification, standing_policy):
    store = ClassificationStore(p7_conn)
    before_record = store.current(file_id, content_hash)
    before_verdict = may_move_automatically(p7_conn, file_id, PLAN_VERSION)
    assert before_verdict.allowed is False
    assert before_verdict.reason == PROTECTED_WITHOUT_PERMITTING_POLICY

    settled = cli.apply_file_held(
        p7_conn, [file_id], plan_version=PLAN_VERSION, user_id="joseph",
        recorded_at=FIXED_CLOCK)
    assert settled == (file_id,)

    # The move verdict: POLICY_PERMITS, and only for the reason this gesture gives.
    after_verdict = may_move_automatically(p7_conn, file_id, PLAN_VERSION)
    assert after_verdict.allowed is True
    assert after_verdict.reason == POLICY_PERMITS

    # The classification row: untouched, field for field, including its basis --
    # so no cloud door was opened by this gesture. `basis` is still not a
    # `CLOUD_CLEARING_BASES` member, exactly as before.
    after_record = store.current(file_id, content_hash)
    assert after_record == before_record
    assert after_record.basis not in cli.CLOUD_CLEARING_BASES
    assert after_record.basis == DETECTOR
    assert after_record.protected is True

    # The policy carries forward everything it already held, plus the one grant.
    after_policy = current_policy(p7_conn, plan_version=PLAN_VERSION)
    assert after_policy.automatic_move_permissions == {file_id: True}
    assert after_policy.operation_mode == "offline"


def test_an_unrecorded_file_id_is_refused_by_name(p7_conn, standing_policy):
    with pytest.raises(cli.FileHeldRefused):
        cli.apply_file_held(
            p7_conn, ["no-such-file"], plan_version=PLAN_VERSION,
            user_id="joseph", recorded_at=FIXED_CLOCK)


def test_with_no_policy_in_force_yet_the_gesture_is_refused_rather_than_inventing_one(
        p7_conn, file_id, protected_classification):
    with pytest.raises(cli.FileHeldRefused):
        cli.apply_file_held(
            p7_conn, [file_id], plan_version=PLAN_VERSION, user_id="joseph",
            recorded_at=FIXED_CLOCK)
