"""`74` §5.3 / §6 B9: the moment a person grants automatic movement.

`74` §5.3 narrowed P12's F15 by finding that the PREDICATE is live and complete --
`privacy.moves.may_move_automatically` reads the flag, checks absence first, reads
the policy at the asked-for plan version, and treats no policy as no permission --
and that what genuinely has no producer is the SURFACE that writes
`Policy.automatic_move_permissions`. That surface is P13's, it was not in P13's
twenty tasks, and it is this one. Until it exists `may_move_automatically` refuses
every protected file, which is the correct posture and not a bug.

B9's named test is
`test_granting_automatic_movement_writes_the_permission_at_the_named_plan_version`
and its twin is
`test_a_grant_collected_under_one_plan_version_does_not_permit_a_move_under_another`.
Both are asserted through P7's own predicate rather than through P13's return
value, because the thing that matters is whether a MOVE becomes permitted.

**P13 writes no P7 record.** The policy write is injected: P13 presents the named
files, collects the gesture, routes it to P7, and hands the grant to a writer the
composition root supplies. Absent means refuse -- there is no default writer, so
there is no path by which P13 quietly becomes the author of a privacy policy.
"""
from __future__ import annotations

import json

import pytest

from database_agent.files_table import get_file, record_file

from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.display import RedactionSettings
from privacy.moves import (
    POLICY_PERMITS,
    PROTECTED_WITHOUT_PERMITTING_POLICY,
    may_move_automatically,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy, current_policy, set_policy
from privacy.vocabulary import USER, USER_CONFIRMED

from review_surface.move_permission import (
    MovePermissionWriterRequired,
    ProtectedFilesRequired,
    grant_automatic_movement,
    move_permission_item,
)
from review_surface.presentation import record_presentation
from review_surface.vocabulary import ACTION_MARK_PRIVATE, SURFACE_PRIVACY_SETTINGS

T0 = "2026-08-29T00:00:00Z"
PLAN_ONE = "plan-1"
PLAN_TWO = "plan-2"
COMPONENT = "p13-1"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")


def _policy_writer(conn, *, plan_version, permissions, user_id,
                   component_version, reason):
    """P7's writer, as the composition root would compose it.

    It reads the policy in force at this plan version, replaces only
    `automatic_move_permissions`, and lets P7 mint the version. P13 does none of
    this; it hands the grant over and P7 authors the record.
    """
    existing = current_policy(conn, plan_version=plan_version)
    base = dict(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={}, plan_version=plan_version, set_at=T0)
    if existing is not None:
        base.update(
            operation_mode=existing.operation_mode,
            consent_grants=existing.consent_grants,
            redaction_settings=dict(existing.redaction_settings),
            automatic_move_permissions=dict(existing.automatic_move_permissions))
    merged = dict(base["automatic_move_permissions"])
    merged.update(permissions)
    base["automatic_move_permissions"] = merged
    return set_policy(conn, Policy(**base), component_version=component_version,
                      user_id=user_id, reason=reason)


@pytest.fixture()
def protected_file(p13_conn, tmp_path):
    directory = tmp_path / "corpus"
    directory.mkdir(exist_ok=True)
    document = directory / "passport-scan.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    file_id = record_file(
        p13_conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(directory), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state",
        materialized=True)
    content_hash = get_file(p13_conn, file_id)["content_hash"]
    ClassificationStore(p13_conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="highly_sensitive_credential_bearing", protected=True,
        basis=USER, evidence_refs=(), reliability_state=USER_CONFIRMED,
        observed_at=T0))
    return file_id


@pytest.fixture()
def ref(p13_conn):
    return record_presentation(
        p13_conn, surface=SURFACE_PRIVACY_SETTINGS, subject_ref="policy",
        plan_version=PLAN_ONE, session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version=COMPONENT,
        rendered_at=T0).presented_state_ref


def _grant(conn, ref, file_ids, *, permitted=True, plan_version=PLAN_ONE,
           writer=_policy_writer, action_id="a-grant"):
    return grant_automatic_movement(
        conn, file_ids=file_ids, permitted=permitted,
        plan_version=plan_version, action_id=action_id,
        session_id="s-1", correction_scope="file", presented_state_ref=ref,
        user_id="jy", acted_at=T0, component_version=COMPONENT,
        write_policy=writer)


def test_granting_automatic_movement_writes_the_permission_at_the_named_plan_version(
        p13_conn, protected_file, ref):
    """`74` §6 B9's named test, asserted through P7's own predicate.

    Before the grant, §8.4's default answer stands: protected and no permitting
    policy. After it, the same file is permitted at the same plan version, and the
    verdict names the policy version P7 minted -- so P11 and P12 can record a
    permission that actually exists rather than one they assumed.
    """
    before = may_move_automatically(p13_conn, protected_file, PLAN_ONE)
    assert before.allowed is False
    assert before.reason == PROTECTED_WITHOUT_PERMITTING_POLICY

    result = _grant(p13_conn, ref, (protected_file,))
    assert result.action.action == ACTION_MARK_PRIVATE
    assert "P7" in result.action.routed_to
    assert result.policy_version

    after = may_move_automatically(p13_conn, protected_file, PLAN_ONE)
    assert after.allowed is True
    assert after.reason == POLICY_PERMITS
    assert after.permitting_policy == result.policy_version


def test_a_grant_collected_under_one_plan_version_does_not_permit_a_move_under_another(
        p13_conn, protected_file, ref):
    """`74` §6 B9's negative twin. §8.8: a new plan never silently moves old files.

    The grant is real at plan-1 and absent at plan-2. A permission that carried
    across versions would let a tree the user has not yet adopted move a passport
    scan on the strength of a decision taken about a different tree.
    """
    _grant(p13_conn, ref, (protected_file,))
    assert may_move_automatically(p13_conn, protected_file, PLAN_ONE).allowed
    other = may_move_automatically(p13_conn, protected_file, PLAN_TWO)
    assert other.allowed is False
    assert other.reason == PROTECTED_WITHOUT_PERMITTING_POLICY
    assert other.permitting_policy is None


def test_the_grant_is_revocable_and_the_revocation_takes_effect(
        p13_conn, protected_file, ref):
    """`74` §5.3: "a person grants automatic movement ... and can revoke it"."""
    _grant(p13_conn, ref, (protected_file,))
    assert may_move_automatically(p13_conn, protected_file, PLAN_ONE).allowed
    _grant(p13_conn, ref, (protected_file,), permitted=False,
           action_id="a-revoke")
    after = may_move_automatically(p13_conn, protected_file, PLAN_ONE)
    assert after.allowed is False
    assert after.reason == PROTECTED_WITHOUT_PERMITTING_POLICY


def test_the_permission_names_the_files_and_is_never_a_blanket(p13_conn, ref):
    """§8.4 permits named material, not a category.

    A grant over no file is refused rather than stored as an empty permission: an
    empty grant is a gesture that looks like consent and permits nothing, and the
    next reader cannot tell it from a grant that was meant to be wide.
    """
    with pytest.raises(ProtectedFilesRequired):
        _grant(p13_conn, ref, ())


def test_the_item_presents_the_files_by_id_and_the_state_they_are_in(
        p13_conn, protected_file, ref):
    """The surface says which files, and what is true of them right now."""
    item = move_permission_item(
        p13_conn, file_ids=(protected_file,), plan_version=PLAN_ONE)
    assert item.plan_version == PLAN_ONE
    assert item.file_ids == (protected_file,)
    assert item.currently_permitted == {protected_file: False}
    _grant(p13_conn, ref, (protected_file,))
    again = move_permission_item(
        p13_conn, file_ids=(protected_file,), plan_version=PLAN_ONE)
    assert again.currently_permitted == {protected_file: True}


def test_there_is_no_default_policy_writer_so_p13_never_authors_the_policy(
        p13_conn, protected_file, ref):
    """P13 writes no record P7 owns. Absent means refuse.

    A default writer would make P13 the author of a privacy policy the first time
    somebody forgot to inject one -- and that author would be invisible, because
    the call would simply succeed.
    """
    import inspect

    signature = inspect.signature(grant_automatic_movement)
    assert signature.parameters["write_policy"].default is (
        inspect.Parameter.empty)
    with pytest.raises(MovePermissionWriterRequired):
        _grant(p13_conn, ref, (protected_file,), writer=None)


def test_the_module_writes_no_privacy_table_itself(p13_conn):
    """Parsed, not promised: P13 issues no INSERT or UPDATE against P7's tables."""
    import ast
    import pathlib

    import review_surface.move_permission as module

    source = pathlib.Path(module.__file__).read_text()
    tree = ast.parse(source)
    called = {node.func.attr for node in ast.walk(tree)
              if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute)}
    assert "execute" not in called
    assert "executescript" not in called
    assert "set_policy" not in called
