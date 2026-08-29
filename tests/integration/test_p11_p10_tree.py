"""G-P10: the live frozen-tree read, against P10's own `frozen_tree`.

The gate is not skipped and no source stub satisfies it: a stub would be P11
deciding what a frozen node is, which is the one thing SPEC:102 says P11 does not
own. While `tree_design.freeze` is absent the test reports an explicit `xfail`
naming the missing module -- the gap is in the run report, not hidden -- and the
moment P10 publishes `frozen_tree` the body executes for real and must pass.

`tree_design.records` already ships, and `tests/p11/p10_fixtures.py` imports
`Node`, `ExpectedValue` and `TemplateContext` from it rather than mirroring them,
so the half of the seam that exists is already live-tested by every P11 index test.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from placement.index import build_destination_index, legal_node_ids
from placement.schema import create_placement_schema
from p11.conftest import FIXED_CLOCK


@pytest.fixture()
def p11_conn(conn):
    # `tests/p11/conftest.py` is not on this directory's fixture path, so the
    # database is built here the way every other integration test builds its own
    # (`tests/integration/test_p9_p8_group_seam.py`).
    create_schema(conn)
    create_placement_schema(conn)
    _seed_a_real_frozen_p10_tree(conn)
    return conn


def _seed_a_real_frozen_p10_tree(conn):
    """One plan version, built and frozen with P10's OWN writers.

    Nothing here is hand-assembled: `write_node` stores, `build_profiles` emits
    the §6.1 profiles and `freeze` produces the bundle. A fixture that built the
    bundle itself would prove only that this file and `index.py` agree.

    `n-app` is a protected area and it is here on purpose. The product owner's
    standing rule is that it is MARKED AND COUNTED, NEVER OPENED — so it must be
    IN the frozen tree and OUT of the legal set, and this is the seam where both
    halves are observable at once.
    """
    from tree_design.freeze import freeze, represent_protected_areas
    from tree_design.profiles import build_profiles
    from tree_design.records import (
        Node,
        PlanVersion,
        SharedMaterialPolicy,
        derive_accepts_placement,
    )
    from tree_design.schema import create_tree_schema
    from tree_design.store import (
        set_shared_material_policy,
        write_node,
        write_plan_version,
    )
    from tree_design.upstream import ProtectedArea
    from tree_design.vocabulary import PRIMARY_HOME

    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan-1", predecessor_id=None, state="draft",
        created_at="2026-01-01T00:00:00Z", cross_folder_moves=False,
        selection_id="sel-1"))

    def node(node_id, label, *, parent=None, node_type="proposed"):
        return Node(
            node_id=node_id, plan_version_id="plan-1", node_type=node_type,
            display_label=label, parent_node_id=parent,
            root_anchor="root_documents", ordinal=0, associated_group_ids=(),
            explanation=f"{label} appeared from the accepted groups beneath it.",
            node_role="ordinary",
            accepts_placement=derive_accepts_placement(
                node_type, protected_movement_permitted=False),
            handling_class="personal_non_sensitive", origin_node_id=node_id,
            refinement_disposition="shallow-by-choice",
            refinement_reason="The user kept this branch shallow on purpose.")

    write_node(conn, node("n-academics", "Academics"))
    write_node(conn, node("n-course", "PHYS1401", parent="n-academics"))

    # The protected area goes in through the REAL join, not hand-built: P3 marks
    # it, `upstream.protected_areas` reads it, `candidates.protected_area_nodes`
    # builds the node and `represent_protected_areas` writes it. A fixture that
    # constructed the node itself would prove the tree can hold one, not that the
    # product ever puts one there.
    area = ProtectedArea(
        path="/Users/jy/Applications/Numbers.app", display_label="Numbers.app",
        rule_subject="directory", applies_to="scan",
        label="untouched_protected", observed_at="2026-01-01T00:00:00Z")
    represent_protected_areas(
        conn, plan_version_id="plan-1", areas=(area,),
        root_anchor="root_applications", mint_node_id=lambda: "n-app",
        handling_class_for=lambda a: "personal_non_sensitive")
    set_shared_material_policy(conn, SharedMaterialPolicy(
        policy_id="smp-1", plan_version_id="plan-1", policy=PRIMARY_HOME,
        policy_scope=None,
        reason="A transcript lives in one packet and is referenced from another."))

    freeze(
        conn, plan_version_id="plan-1", created_at="2026-01-01T00:00:00Z",
        user_id="jy", component_version="P10-integration",
        residual_configuration={}, approved_branch_ids=("n-academics", "n-course"),
        protected_areas=(area,),
        profiles=build_profiles(
            conn, plan_version_id="plan-1", groups_by_id={},
            document_types_by_node={}, anchor_excerpts_by_node={},
            user_edits_by_node={}, node_scoped_rejections={}))


def test_p11_indexes_p10s_live_frozen_tree(p11_conn):
    try:
        from tree_design.freeze import frozen_tree
    except ModuleNotFoundError as absent:  # G-P10
        pytest.xfail(f"G-P10 open: {absent}")

    tree = frozen_tree(p11_conn, plan_version="plan-1")
    entries = build_destination_index(
        p11_conn, tree, component_version="P11-integration",
        observed_at=FIXED_CLOCK,
    )
    assert entries
    assert all(entry.plan_version == "plan-1" for entry in entries)
    # ONE legality authority: P10's freeze record decides, P11's index projects.
    assert legal_node_ids(p11_conn, plan_version="plan-1") == frozenset(
        tree.freeze_record.legal_destination_ids)

    # The owner's standing rule, observable at the seam: present in the tree,
    # absent from the legal set, and an ordinary node beside it still placeable.
    assert "n-app" in {node.node_id for node in tree.nodes}
    assert "n-app" not in tree.freeze_record.legal_destination_ids
    assert "n-course" in tree.freeze_record.legal_destination_ids
    assert "n-app" not in {entry.node_id for entry in entries}


def test_no_placement_module_imports_p11s_test_only_tree_fixture():
    # A source stub for P10 would make G-P10 unfalsifiable.
    import pathlib

    source = pathlib.Path(__file__).resolve().parents[2] / "src" / "placement"
    for module in source.glob("*.py"):
        assert "p10_fixtures" not in module.read_text(), module


def test_freeze_and_the_index_refuse_the_same_missing_policy(p11_conn):
    """§6.9's gate, asserted BEHAVIOURALLY rather than by matching P11's source.

    A source-string match breaks on a reformat and passes on a semantic change
    that keeps the words. Two refusals on one input IS the agreement, and it
    survives a rename: what freeze lets through the index accepts, and what the
    index would refuse freeze refuses FIRST — at the stage the user can still act.
    """
    import dataclasses

    import pytest

    from placement.index import FrozenTreeRequired, build_destination_index
    from tree_design.freeze import FreezeRefused, freeze, frozen_tree
    from tree_design.profiles import build_profiles

    # The seeded version already carries a policy, so both stages accept it.
    accepted = frozen_tree(p11_conn, plan_version="plan-1")
    assert accepted.shared_material_policy
    assert build_destination_index(
        p11_conn, accepted, component_version="P11-agreement",
        observed_at=FIXED_CLOCK)

    # The SAME bundle with the policy removed is what the index refuses...
    without = dataclasses.replace(accepted, shared_material_policy=None)
    with pytest.raises(FrozenTreeRequired) as index_refusal:
        build_destination_index(p11_conn, without,
                                component_version="P11-agreement",
                                observed_at=FIXED_CLOCK)
    assert "shared-material policy" in str(index_refusal.value)

    # ...and freeze refuses a version in that state before it can ever get there.
    _seed_second_version_without_a_policy(p11_conn)
    with pytest.raises(FreezeRefused) as freeze_refusal:
        freeze(p11_conn, plan_version_id="plan-2", created_at="2026-01-01T00:00:00Z",
               user_id="jy", component_version="P10-agreement",
               residual_configuration={}, approved_branch_ids=("n2-academics",),
               profiles=build_profiles(
                   p11_conn, plan_version_id="plan-2", groups_by_id={},
                   document_types_by_node={}, anchor_excerpts_by_node={},
                   user_edits_by_node={}, node_scoped_rejections={}))
    assert any("shared-material" in reason
               for reason in freeze_refusal.value.reasons)


def _seed_second_version_without_a_policy(conn):
    from tree_design.records import Node, PlanVersion, derive_accepts_placement
    from tree_design.store import write_node, write_plan_version

    write_plan_version(conn, PlanVersion(
        plan_version_id="plan-2", predecessor_id=None, state="draft",
        created_at="2026-01-01T00:00:00Z", cross_folder_moves=False,
        selection_id="sel-1"))
    write_node(conn, Node(
        node_id="n2-academics", plan_version_id="plan-2", node_type="proposed",
        display_label="Academics", parent_node_id=None,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="A branch the user approved at the top level.",
        node_role="ordinary",
        accepts_placement=derive_accepts_placement(
            "proposed", protected_movement_permitted=False),
        handling_class="personal_non_sensitive", origin_node_id="n2-academics",
        refinement_disposition="shallow-by-choice",
        refinement_reason="The user kept this branch shallow on purpose."))
