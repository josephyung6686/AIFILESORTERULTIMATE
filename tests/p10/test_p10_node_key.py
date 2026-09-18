"""SPEC open question 5, answered: a node's `origin_node_id` is its KEY.

`store.py`'s docstring offered the reversible move -- "if node ids turn out to be
stable across versions, `origin_node_id` becomes `node_id` and nothing else
changes". This is the other half: `node_id` stays minted per version and
`origin_node_id` stops being the fresh mint's own id and becomes what the node IS,
spelled from what it already carries. Every reader that compares versions by
origin (`diff.diff_versions`, `placement.versions.reproject`,
`learned_preferences_still_applicable`, `store.apply_review_action`) then works
across RUNS with no change of its own -- which is the whole of why this is the
smallest change and not a new column.

`106` Phase 5's gate: an edit survives a re-run. It cannot while two runs over
one corpus disagree about which node is which. And the hazard the lead met on
18 Sep -- a display string and a primary key are not the same thing even when
they are spelled the same -- is why the key is spelled from the node's CLAIM
(`field=value`, the observed path) and not from what a screen prints.
"""
from __future__ import annotations

import sqlite3

import pytest

from p10.test_p10_materialise import (  # noqa: F401  (`seeded` is a fixture)
    ACCEPTED, ALWAYS_ORDINARY, NO_CONTEXT, ONE_CLASS, PROTECTED_CLASSES,
    _candidate, _ids, _parent, seeded,
)
from tree_design.fixtures import CREATED_AT, SELECTION_ID, _node
from tree_design.materialise import materialise_branch, project_branch_nodes
from tree_design.node_key import (
    branch_key, general_key, level_key, protected_key, residual_key,
)
from tree_design.records import PlanVersion
from tree_design.schema import create_tree_schema
from tree_design.store import DuplicateNodeKey, write_node, write_plan_version


def test_two_runs_over_one_branch_mint_different_ids_and_the_same_origins(seeded):
    """THE GATE. SABOTAGE: put `origin_node_id=node_id` back in
    `materialise._project` -- every origin below differs between the two runs,
    and `diff_versions` reads a re-run as everything removed and everything
    added."""
    conn = seeded.conn
    _, evidence = materialise_branch(
        conn, _candidate(("subject", "subject"), ("work_type", "work_type")),
        branch_node_id="n_academics",
        members=seeded.members("syllabus", "hw3", "lab"),
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    first = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_1",
        mint_node_id=_ids(), handling_class_for=ALWAYS_ORDINARY,
        template_context_for=NO_CONTEXT)
    counter = iter(range(5000, 9000))
    second = project_branch_nodes(
        evidence, ACCEPTED, parent=_parent(), plan_version_id="plan_2",
        mint_node_id=lambda: f"other_{next(counter)}",
        handling_class_for=ALWAYS_ORDINARY, template_context_for=NO_CONTEXT)
    assert first, "no node was built, so nothing below is about a node"
    assert [n.node_id for n in first] != [n.node_id for n in second]
    assert [n.origin_node_id for n in first] == [n.origin_node_id for n in second]
    assert all(n.origin_node_id != n.node_id for n in first)
    # The key is the CHAIN: the parent's key, then what each folder is named by.
    assert all(n.origin_node_id.startswith("n_academics/") for n in first)


def test_a_level_key_is_the_parents_key_and_the_value_the_folder_is_named_by():
    """The same pair `cli._node_claim` reads: a folder named by `subject =
    PHYS1401` under the coursework branch has one spelling wherever it appears."""
    root = branch_key(display_label="Coursework", existing_path=None)
    assert root == "branch:Coursework"
    assert level_key(root, field="subject", value="PHYS1401", role="subject_anchor") \
        == "branch:Coursework/subject=PHYS1401"
    # A template-local level has no P6 field, so its role names it -- and the
    # two cannot collide, because a role is never a field of the same name in
    # one recipe.
    assert level_key(root, field=None, value="Matter 12", role="matter_number") \
        == "branch:Coursework/matter_number=Matter 12"


def test_an_adopted_folder_is_keyed_by_the_path_that_was_observed():
    """An adopted card's `subject_id` IS the directory. Two runs that adopt the
    same folder must agree, and two folders with one name in two places must
    not."""
    assert branch_key(display_label="PHYS1401", existing_path="Uni/PHYS1401") \
        == "existing:Uni/PHYS1401"
    assert branch_key(display_label="PHYS1401", existing_path="Old/PHYS1401") \
        != branch_key(display_label="PHYS1401", existing_path="Uni/PHYS1401")


def test_the_other_three_kinds_of_node_have_their_own_prefix():
    assert residual_key("Reading Inbox") == "residual:Reading Inbox"
    assert protected_key("/a/Keychain") == "protected:/a/Keychain"
    assert general_key("branch:Coursework") == "branch:Coursework/general"


def test_two_nodes_with_one_key_in_one_version_are_refused_at_the_write():
    """C4's shape: one question with two answers has none. SABOTAGE: drop the
    guard -- `reproject` then matches a pending move to whichever of the two
    rows sorts first, silently."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=CREATED_AT, cross_folder_moves=False,
        selection_id=SELECTION_ID))
    write_node(conn, _node("n_1", "Coursework", origin="branch:Coursework"))
    # The SAME row again is a rewrite, not a clash: `apply_review_action` writes
    # an edited node back under its own id.
    write_node(conn, _node("n_1", "Course work", origin="branch:Coursework"))
    with pytest.raises(DuplicateNodeKey):
        write_node(conn, _node("n_2", "Coursework", ordinal=1,
                               origin="branch:Coursework"))
    # Another version may carry the same key: that is the whole point.
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_2", predecessor_id="plan_1", state="draft",
        created_at=CREATED_AT, cross_folder_moves=False,
        selection_id=SELECTION_ID))
    write_node(conn, _node("n_3", "Coursework", version="plan_2",
                           origin="branch:Coursework"))
