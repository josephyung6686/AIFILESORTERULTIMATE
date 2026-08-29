# tests/p10/test_p10_records.py
"""P10 Task 2 — the node record, the plan version, and P10's own tables.

Two shape rules carry the most weight.

`accepts_placement` is DERIVED and then STORED, and the record refuses a stored
value that disagrees with the derivation. P11 needs one flag rather than a case
analysis (resolution B6), but a flag nobody can re-derive is a flag that drifts.

No node holds a composed path. `root_anchor` plus the ancestor `display_label`
chain is what P10 publishes; P12 composes the path and applies §8.3's
case-sensitivity, Unicode and length rules. A plan-versioned tree holding
platform-specific strings would resolve differently on a case-sensitive and a
case-insensitive volume, and the same frozen tree must resolve on both.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from tree_design.records import (
    ExpectedValue,
    MalformedTreeRecord,
    Node,
    PlanVersion,
    SharedMaterialPolicy,
    TemplateContext,
    derive_accepts_placement,
)
from tree_design.schema import P10_TABLES, create_tree_schema
from tree_design.vocabulary import (
    EXISTING,
    IGNORED,
    ORDINARY,
    PHYSICAL_DESTINATION,
    PRIMARY_HOME,
    PROPOSED,
    PROTECTED,
    REFINED,
    RESIDUAL,
    SHALLOW_BY_CHOICE,
    USER_CREATED,
)

BASE = dict(
    node_id="n_1", plan_version_id="plan_1", node_type=PROPOSED,
    display_label="Homework", parent_node_id="n_0", root_anchor="root_documents",
    ordinal=2, associated_group_ids=("g_phys1401",),
    explanation="Six files in the accepted PHYS1401 group carry work type = Homework.",
    node_role=ORDINARY, accepts_placement=True,
    handling_class="personal_non_sensitive", origin_node_id="n_1",
)


def test_a_node_round_trips_through_canonical_json():
    node = Node(
        **BASE,
        template_context=TemplateContext(
            binding_id="btb_1", template_id="academic-coursework",
            template_version=1, dimension_index=3,
            fragment_id="artifact-kind", fragment_version=1,
        ),
        dimension_role="artifact_kind",
        dimension="work_type",
        expected_values=(ExpectedValue(field="work_type", value="Homework"),),
        refinement_disposition=REFINED,
        refinement_reason="The course has enough populated work types to help retrieval.",
    )
    encoded = json.dumps(dataclasses.asdict(node), sort_keys=True)
    restored = json.loads(encoded)
    assert restored["template_context"]["fragment_version"] == 1
    assert restored["expected_values"] == [{"field": "work_type", "value": "Homework"}]
    assert restored["dimension_role"] == "artifact_kind"
    assert restored["dimension"] == "work_type"


def test_accepts_placement_is_derived_from_type_and_policy_only():
    for node_type in (EXISTING, PROPOSED, USER_CREATED):
        assert derive_accepts_placement(node_type, protected_movement_permitted=False)
    # §5.10 lets the user leave an existing folder untouched; an ignored node is
    # visible context, never a destination.
    assert not derive_accepts_placement(IGNORED, protected_movement_permitted=True)
    # §8.4: protected material "should not be moved automatically without a user
    # policy that explicitly permits it".
    assert not derive_accepts_placement(PROTECTED, protected_movement_permitted=False)
    assert derive_accepts_placement(PROTECTED, protected_movement_permitted=True)


def test_a_stored_flag_that_contradicts_the_derivation_is_refused():
    with pytest.raises(MalformedTreeRecord) as excinfo:
        Node(**{**BASE, "node_type": IGNORED, "accepts_placement": True})
    assert "ignored" in str(excinfo.value)


def test_no_node_field_but_existing_path_may_hold_a_separator():
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "display_label": "Academics/Columbia"})
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "display_label": "Academics\\Columbia"})
    observed = Node(**{
        **BASE, "node_type": EXISTING, "display_label": "To Sort",
        "existing_path": "/Users/jy/Documents/To Sort",
    })
    assert observed.existing_path == "/Users/jy/Documents/To Sort"


def test_existing_path_belongs_only_to_an_existing_node():
    with pytest.raises(MalformedTreeRecord) as excinfo:
        Node(**{**BASE, "existing_path": "/Users/jy/Documents/Homework"})
    assert "existing" in str(excinfo.value)


def test_every_node_carries_a_non_empty_prose_explanation():
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "explanation": ""})
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "explanation": "   "})


def test_disposition_is_required_on_a_residual_node_and_refused_elsewhere():
    residual = Node(**{
        **BASE, "node_role": RESIDUAL, "disposition": PHYSICAL_DESTINATION,
    })
    assert residual.disposition == PHYSICAL_DESTINATION
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "node_role": RESIDUAL})
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "disposition": PHYSICAL_DESTINATION})


def test_a_refinement_disposition_always_carries_its_reason():
    """§5.8: an intentionally shallow branch and an unfinished one are different
    states, and only the reason distinguishes them."""
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "refinement_disposition": SHALLOW_BY_CHOICE})
    node = Node(**{
        **BASE, "refinement_disposition": SHALLOW_BY_CHOICE,
        "refinement_reason": "Twelve receipts do not need a per-vendor level.",
    })
    assert node.refinement_disposition == SHALLOW_BY_CHOICE


def test_a_top_level_branch_has_a_null_parent_but_always_a_root_anchor():
    top = Node(**{**BASE, "parent_node_id": None})
    assert top.parent_node_id is None
    with pytest.raises(MalformedTreeRecord):
        Node(**{**BASE, "root_anchor": ""})


def test_unknown_vocabulary_values_are_load_errors_not_fallbacks():
    for field, bad in (
        ("node_type", "suggested"),
        ("node_role", "catch-all"),
        ("handling_class", "Public or low sensitivity"),
    ):
        with pytest.raises(Exception):
            Node(**{**BASE, field: bad})


def test_a_shared_material_policy_records_which_branch_it_covers():
    """SPEC open question 9 is open: §6.9 reads global, its example reads
    branch-local. `policy_scope = None` means tree-global and is a value, not a
    missing one, so the answer can land either way without a migration."""
    policy = SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None,
        reason="One packet is the primary home; the other references it.",
    )
    assert policy.policy_scope is None
    branch_local = dataclasses.replace(policy, policy_scope="n_applications")
    assert branch_local.policy_scope == "n_applications"


def test_the_schema_is_idempotent_and_owns_only_p10_tables(conn):
    create_tree_schema(conn)
    create_tree_schema(conn)
    names = {
        row["name"] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert set(P10_TABLES) <= names
    assert "events" in names  # P1's, untouched


def test_a_plan_version_carries_p3s_cross_folder_permission(conn):
    """§1.1's "whether files may move across high-level folders" is recorded by
    P3 as `cross_folder_moves` and STORED by P10 at freeze under §8.8's placement
    policy settings. P12 enforces it at mutation time."""
    create_tree_schema(conn)
    version = PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at="2026-08-27T00:00:00Z", cross_folder_moves=False,
        selection_id="sel_1",
    )
    conn.execute(
        "INSERT INTO plan_versions (plan_version_id, predecessor_id, state, "
        "created_at, cross_folder_moves, selection_id) VALUES (?, ?, ?, ?, ?, ?)",
        (version.plan_version_id, version.predecessor_id, version.state,
         version.created_at, int(version.cross_folder_moves), version.selection_id),
    )
    row = conn.execute("SELECT * FROM plan_versions").fetchone()
    assert row["cross_folder_moves"] == 0
    assert row["selection_id"] == "sel_1"
