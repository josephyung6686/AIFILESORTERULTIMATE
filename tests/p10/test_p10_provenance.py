"""P10 Task 5 — the two events P10 appends, and the rejections it must honour.

`template application` and `destination-tree edit` are §8.2 reserved names that
have had no producer since P1 shipped. A reserved name with no writer is this
project's named defect class: the column exists, the audit reads it, and it is
always empty. This task is the writer.

The §8.7 read is the other half. §8.7: "Rejected groups, rejected destination
matches, rejected labels, and rejected residual recommendations must be stored
with the evidence that produced them. Otherwise the system will repeatedly
resurface the same attractive but incorrect grouping."
"""
from __future__ import annotations

import json

import pytest

from database_agent.events import MalformedEvent, UnregisteredEventType
from database_agent.learning import reset_preferences
from tree_design.provenance import (
    PROPOSAL_CLASS_BRANCH,
    SUBSYSTEM,
    branch_basis_key,
    record_plan_version_adoption,
    record_template_application,
    record_tree_edit,
    suppressed_branch_basis_keys,
)
from tree_design.vocabulary import (
    DESTINATION_TREE_EDIT,
    RENAME,
    TEMPLATE_APPLICATION,
)

T0 = "2026-08-27T00:00:00Z"
COMMON = dict(observed_at=T0, user_id="jy", component_version="p10-1")


def _events(conn, event_type):
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? ORDER BY event_id",
        (event_type,)).fetchall()


def test_a_tree_edit_appends_82s_reserved_name_with_before_and_after(conn):
    record_tree_edit(
        conn, action=RENAME, node_id="n_1", plan_version_id="plan_1",
        before={"display_label": "Uni"}, after={"display_label": "Academics"},
        explanation="User renamed the branch to their own vocabulary.",
        correction_scope="node", correction_subject="n_1", polarity="accept",
        **COMMON)
    row = _events(conn, DESTINATION_TREE_EDIT)[0]
    assert row["subsystem"] == SUBSYSTEM == "P10"
    payload = json.loads(row["explanation"].split("\n", 1)[1])
    assert payload["action"] == RENAME
    assert payload["before"] == {"display_label": "Uni"}
    assert payload["after"] == {"display_label": "Academics"}
    assert row["correction_scope"] == "node"
    assert row["correction_subject"] == "n_1"


def test_an_edit_with_no_explanation_is_refused_by_p1(conn):
    with pytest.raises(MalformedEvent):
        record_tree_edit(
            conn, action=RENAME, node_id="n_1", plan_version_id="plan_1",
            before={}, after={}, explanation="",
            correction_scope="node", correction_subject="n_1", polarity="accept",
            **COMMON)


def test_an_action_outside_the_tree_edit_set_never_reaches_p1(conn):
    with pytest.raises(Exception):
        record_tree_edit(
            conn, action="reticulate", node_id="n_1", plan_version_id="plan_1",
            before={}, after={}, explanation="x",
            correction_scope="node", correction_subject="n_1", polarity="accept",
            **COMMON)
    assert _events(conn, DESTINATION_TREE_EDIT) == []


def test_a_template_application_carries_template_id_and_exact_version(conn):
    record_template_application(
        conn, node_id="n_1", plan_version_id="plan_1",
        template_id="academic-coursework", template_version=1,
        binding_id="btb_1",
        explanation="Applied the academic coursework recipe to this branch.",
        **COMMON)
    row = _events(conn, TEMPLATE_APPLICATION)[0]
    payload = json.loads(row["explanation"].split("\n", 1)[1])
    assert payload["template_id"] == "academic-coursework"
    assert payload["template_version"] == 1
    assert payload["binding_id"] == "btb_1"
    assert row["prompt_fingerprint"] is None


def test_an_llm_generated_template_additionally_carries_model_and_fingerprint(conn):
    """§8.2 and §3.4. Without both, two runs at different model versions look
    identical to replay, which is a silent wrong answer."""
    record_template_application(
        conn, node_id="n_1", plan_version_id="plan_1",
        template_id="custom-1", template_version=1, binding_id="btb_2",
        explanation="Applied a model-proposed recipe after user approval.",
        model_identifier="fixture-model", prompt_fingerprint="fp-canonical",
        **COMMON)
    row = _events(conn, TEMPLATE_APPLICATION)[0]
    assert row["prompt_fingerprint"] == "fp-canonical"
    payload = json.loads(row["explanation"].split("\n", 1)[1])
    assert payload["model_identifier"] == "fixture-model"


def test_a_model_generated_template_without_a_fingerprint_is_refused(conn):
    with pytest.raises(ValueError):
        record_template_application(
            conn, node_id="n_1", plan_version_id="plan_1",
            template_id="custom-1", template_version=1, binding_id="btb_2",
            explanation="x", model_identifier="fixture-model", **COMMON)


def test_freeze_appends_a_plan_version_adoption_record(conn):
    event_id = record_plan_version_adoption(
        conn, plan_version_id="plan_1", action="adopt_version",
        explanation="User froze the tree.", **COMMON)
    row = conn.execute(
        "SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()
    assert row["event_type"] == DESTINATION_TREE_EDIT
    assert row["correction_scope"] == "corpus"
    assert row["correction_subject"] == "plan_1"


def test_a_rejected_branch_is_suppressed_by_parent_and_label(conn):
    """§8.7 and 10-i4-learning-ops: before proposing a branch candidate, P10
    queries `learning_records` for `proposal_class = branch` and
    `basis_key = (parent_node_id, dimension_or_label)`."""
    key = branch_basis_key(parent_node_id=None, dimension_or_label="Math Stuff")
    record_tree_edit(
        conn, action="delete", node_id="n_math",
        plan_version_id="plan_1", before={"display_label": "Math Stuff"},
        after={}, explanation="User deleted the suggested Math Stuff area.",
        correction_scope="node", correction_subject="__root__",
        polarity="reject", basis_key=key,
        **{**COMMON, "component_version": "p10-1"})
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset({key})
    other = branch_basis_key(parent_node_id="n_academics",
                             dimension_or_label="Math Stuff")
    assert suppressed_branch_basis_keys(conn, parent_node_id="n_academics") == frozenset()
    assert other != key


def test_an_accepted_branch_is_not_suppressed(conn):
    key = branch_basis_key(parent_node_id=None, dimension_or_label="Academics")
    record_tree_edit(
        conn, action="accept", node_id="n_academics", plan_version_id="plan_1",
        before={}, after={"display_label": "Academics"},
        explanation="User accepted the Academics branch.",
        correction_scope="node", correction_subject="__root__",
        polarity="accept", basis_key=key, **COMMON)
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset()


def test_a_reset_lifts_the_suppression_without_deleting_the_record(conn):
    """§8.7: learned preferences are inspectable and resettable, and R6 keeps
    every record. A reset is a cutoff, not a delete."""
    key = branch_basis_key(parent_node_id=None, dimension_or_label="Math Stuff")
    record_tree_edit(
        conn, action="delete", node_id="n_math",
        plan_version_id="plan_1", before={"display_label": "Math Stuff"},
        after={}, explanation="User deleted the suggested Math Stuff area.",
        correction_scope="node", correction_subject="__root__",
        polarity="reject", basis_key=key, **COMMON)
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset({key})
    reset_preferences(conn, "node", "__root__", author="P13",
                      component_version="p13-1", user_id="jy")
    assert suppressed_branch_basis_keys(conn, parent_node_id=None) == frozenset()
    surviving = conn.execute(
        "SELECT count(*) AS n FROM events WHERE basis_key = ?", (key,)).fetchone()
    assert surviving["n"] == 1


def test_p10_appends_no_event_type_it_does_not_own(conn):
    with pytest.raises(UnregisteredEventType):
        from database_agent.events import append_event
        append_event(conn, event_type="tree freeze", subsystem=SUBSYSTEM,
                     component_version="p10-1", observed_at=T0,
                     explanation="not a reserved name")
