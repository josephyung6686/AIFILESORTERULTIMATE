"""P10 Task 16 — the freeze guarantee, stated as a set membership test.

DM3: "given a frozen tree fixture and an arbitrary destination string, a caller
can decide legality without consulting facts, templates or the filesystem." That
is why `FreezeRecord` carries `legal_destination_ids` as a frozenset of ids and
nothing else: an answer that needed a join could disagree with itself later.

§8.8 makes a frozen version immutable, so the bundle is written ONCE and read
back verbatim. Rebuilding the §6.1 profiles at read time would consult P9, P4 and
P6 as they are THEN, not as they were when the user adopted the plan.
"""
from __future__ import annotations

import dataclasses

import pytest

from tree_design.freeze import (
    FreezeRecord,
    FreezeRefused,
    NotFrozen,
    freeze,
    frozen_tree,
    is_legal_destination,
    legal_destination_ids,
    validate_for_freeze,
)
from tree_design.profiles import build_profiles
from tree_design.records import (
    ExpectedValue,
    Node,
    PlanVersion,
    SharedMaterialPolicy,
    derive_accepts_placement,
)
from tree_design.schema import create_tree_schema
from tree_design.store import set_shared_material_policy, write_node, write_plan_version
from tree_design.upstream import AcceptedGroup, GroupMember
from tree_design.vocabulary import PRIMARY_HOME, RESIDUAL, REVIEW_ONLY

T0 = "2026-08-27T00:00:00Z"
T1 = "2026-08-27T01:00:00Z"

GROUP = AcceptedGroup(
    group_id="g_phys", label="PHYS 1401 course", domain="academic",
    members=(GroupMember("lecture", "h_lecture", "direct-anchor"),),
    anchor_facts=("fact_g_phys",), excluded_members=())


def _node(node_id, label, *, parent=None, node_type="proposed", role="ordinary",
          handling="personal_non_sensitive", groups=(), disposition=None,
          protected_ok=False, refinement="refined", reason="The groups justify it."):
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=groups,
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role=role,
        accepts_placement=derive_accepts_placement(
            node_type, protected_movement_permitted=protected_ok),
        handling_class=handling, origin_node_id=node_id,
        disposition=disposition, protected_movement_permitted=protected_ok,
        refinement_disposition=refinement, refinement_reason=reason)


@pytest.fixture()
def seeded(conn):
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    write_node(conn, _node("n_root", "Academics"))
    write_node(conn, _node("n_course", "PHYS1401", parent="n_root",
                           groups=("g_phys",)))
    write_node(conn, _node("n_app", "Numbers.app", node_type="protected"))
    write_node(conn, _node("n_ignored", "Old Downloads", node_type="ignored"))
    write_node(conn, _node("n_review", "Review Later", role=RESIDUAL,
                           disposition=REVIEW_ONLY))
    set_shared_material_policy(conn, SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None,
        reason="A transcript lives in one packet and is referenced from the other."))
    return conn


def _profiles(conn):
    return build_profiles(
        conn, plan_version_id="plan_1", groups_by_id={"g_phys": GROUP},
        document_types_by_node={}, anchor_excerpts_by_node={},
        user_edits_by_node={}, node_scoped_rejections={})


def _freeze(conn, **over):
    kwargs = dict(
        plan_version_id="plan_1", created_at=T1, user_id="jy",
        component_version="p10-1", residual_configuration={"Review Later": "enabled"},
        approved_branch_ids=("n_root", "n_course"), profiles=_profiles(conn))
    kwargs.update(over)
    return freeze(conn, **kwargs)


def test_a_protected_area_is_in_the_frozen_tree_and_never_a_destination(seeded):
    """The product owner's standing rule, at the seam that matters most: a
    protected container is MARKED AND COUNTED, NEVER OPENED — present in the
    tree, never silently omitted, and never a place files are put.

    The second half is what makes this a test rather than a tautology: an
    ORDINARY node beside it stays legal. Marking everything protected would pass
    "the protected node is not a destination" and would also make the product
    place nothing anywhere.
    """
    tree = _freeze(seeded)
    ids = {node.node_id for node in tree.nodes}
    assert "n_app" in ids, "a protected area must be present, not omitted"

    legal = tree.freeze_record.legal_destination_ids
    assert "n_app" not in legal
    assert "n_ignored" not in legal
    assert "n_course" in legal, "an ordinary node beside it stays placeable"
    assert "n_review" in legal, "00:121 — an approved residual branch is legal"

    app = next(node for node in tree.nodes if node.node_id == "n_app")
    assert app.protected_movement_permitted is False
    assert "Numbers.app" in app.explanation or app.display_label == "Numbers.app"


def test_legality_is_decidable_from_the_record_alone(seeded):
    """DM3. No facts, no templates, no filesystem — one set membership test."""
    record = _freeze(seeded).freeze_record
    assert legal_destination_ids(record) == record.legal_destination_ids
    assert is_legal_destination(record, "n_course") is True
    assert is_legal_destination(record, "n_app") is False
    assert is_legal_destination(record, "a string nobody minted") is False


def test_the_legal_set_is_exactly_the_nodes_that_accept_placement(seeded):
    """ONE legality authority. P11's index projects this set and asserts equality,
    so a second rule here would surface as a P8 error on a legal node."""
    tree = _freeze(seeded)
    assert tree.freeze_record.legal_destination_ids == frozenset(
        node.node_id for node in tree.nodes if node.accepts_placement)


def test_the_bundle_round_trips_verbatim_through_the_store(seeded):
    """§8.8 makes a frozen version immutable, so the bundle is written once and
    read back. Rebuilding profiles at read time would consult a P9/P4/P6 state
    that has moved on since the user adopted the plan."""
    written = _freeze(seeded)
    read = frozen_tree(seeded, plan_version="plan_1")
    assert read.plan_version_id == "plan_1"
    assert read.freeze_record == written.freeze_record
    assert read.profiles == written.profiles
    assert read.nodes == written.nodes
    assert read.shared_material_policy == PRIMARY_HOME
    assert read.shared_material_policy_scope is None


def test_reading_a_version_that_was_never_frozen_is_refused(seeded):
    with pytest.raises(NotFrozen):
        frozen_tree(seeded, plan_version="plan_1")


def test_freeze_marks_the_version_frozen_and_records_the_adoption(seeded):
    _freeze(seeded)
    state = seeded.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = 'plan_1'"
    ).fetchone()["state"]
    assert state == "frozen"
    row = seeded.execute(
        "SELECT * FROM events WHERE proposal_class = 'plan_version' "
        "AND correction_subject = 'plan_1'").fetchone()
    assert row is not None


def test_an_approved_branch_with_no_refinement_disposition_refuses_the_freeze(seeded):
    """§5.8 / P10 SPEC:230. `Node.refinement_disposition` is optional on a DRAFT
    node — a branch the user has not approved has not answered yet — and required
    on an approved one. Without it, `shallow-by-choice` and `refine-later` are
    indistinguishable, and P11 cannot tell a deliberate design from unfinished
    work."""
    write_node(seeded, _node("n_bare", "Unanswered", parent="n_root",
                             refinement=None, reason=None))
    reasons = validate_for_freeze(
        seeded, plan_version_id="plan_1",
        residual_configuration={"Review Later": "enabled"},
        approved_branch_ids=("n_root", "n_course", "n_bare"))
    assert any("n_bare" in reason for reason in reasons)
    with pytest.raises(FreezeRefused) as excinfo:
        _freeze(seeded, approved_branch_ids=("n_root", "n_course", "n_bare"))
    assert excinfo.value.reasons


def test_a_draft_node_that_was_never_approved_does_not_block_the_freeze(seeded):
    """The discriminating half: the requirement is on APPROVED branches. A node
    the user has not approved may still carry `None`, and refusing on it would
    make the state the user is actually in while editing unfreezable."""
    write_node(seeded, _node("n_draft", "Still deciding", parent="n_root",
                             refinement=None, reason=None))
    assert validate_for_freeze(
        seeded, plan_version_id="plan_1",
        residual_configuration={"Review Later": "enabled"},
        approved_branch_ids=("n_root", "n_course")) == ()


def test_a_disabled_residual_template_is_unreachable_after_freeze(seeded):
    """DM12. §7.4's enforcement is that a template the user did not enable HAS NO
    NODE, so no model can return it. The freeze record carries the configuration
    so the absence is auditable rather than merely true."""
    tree = _freeze(seeded, residual_configuration={
        "Review Later": "enabled", "Reading Inbox": "disabled"})
    labels = {node.display_label for node in tree.nodes}
    assert "Reading Inbox" not in labels
    assert tree.freeze_record.residual_configuration["Reading Inbox"] == "disabled"
    assert not any(
        is_legal_destination(tree.freeze_record, node_id)
        for node_id in ("Reading Inbox", "reading-inbox"))


def test_no_published_node_carries_a_composed_path(seeded):
    """DM11. P10 publishes `root_anchor` plus the label chain; P12 composes."""
    tree = _freeze(seeded)
    for node in tree.nodes:
        assert "/" not in node.display_label and "\\" not in node.display_label
    for profile in tree.profiles:
        assert "/" not in profile.display_label


def test_the_record_carries_the_placement_policy_the_user_chose(seeded):
    """§1.1's permission travels with the version it was frozen under; P12
    enforces it at mutation time and re-derives nothing."""
    record = _freeze(seeded).freeze_record
    assert record.cross_folder_moves is False
    assert record.selection_id == "sel_1"
    assert record.created_at == T1


def test_the_freeze_path_actually_calls_the_protected_area_producer():
    """The reachability guard, so this cannot go inert the way four other
    concepts already did.

    `protected_areas` reads P3's verdicts and `protected_area_nodes` turns them
    into nodes, and for a while nothing in `src/` joined the two — so on a real
    scan a protected container was pruned and then absent from the tree, which is
    the silent omission the owner's rule names. Correct code, wired to nothing,
    is the shape that has cost this project the most.

    Asserted by AST rather than by grep: the import AND an actual call, because
    "imported but never invoked" is the same defect with better paperwork.
    """
    import ast
    from pathlib import Path

    source = (Path(__file__).resolve().parents[2]
              / "src" / "tree_design" / "freeze.py").read_text()
    tree = ast.parse(source)
    imported = {
        alias.name for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "tree_design.candidates"
        for alias in node.names
    }
    assert "protected_area_nodes" in imported

    called = {
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "protected_area_nodes" in called, "imported but never invoked"


def test_a_marked_area_with_no_node_refuses_the_freeze(seeded):
    """"Never silently omitted" enforced at the last moment it still can be. A
    frozen tree is permanent: an area missing here is invisible for good, and
    every later part inherits the omission."""
    from tree_design.upstream import ProtectedArea

    area = ProtectedArea(
        path="/Users/jy/Applications/Mail.app", display_label="Mail.app",
        rule_subject="directory", applies_to="scan",
        label="untouched_protected", observed_at=T0)
    reasons = validate_for_freeze(
        seeded, plan_version_id="plan_1", residual_configuration={},
        approved_branch_ids=("n_root", "n_course"), protected_areas=(area,))
    assert any("Mail.app" in reason for reason in reasons)


def test_representing_the_areas_first_lets_the_freeze_through(seeded):
    """The discriminating half: once the areas ARE represented, the same freeze
    succeeds and the nodes are in the bundle and out of the legal set."""
    from tree_design.freeze import represent_protected_areas
    from tree_design.upstream import ProtectedArea

    area = ProtectedArea(
        path="/Users/jy/Applications/Mail.app", display_label="Mail.app",
        rule_subject="directory", applies_to="scan",
        label="untouched_protected", observed_at=T0)
    counter = iter(range(50))
    written = represent_protected_areas(
        seeded, plan_version_id="plan_1", areas=(area,),
        root_anchor="root_applications",
        mint_node_id=lambda: f"n_prot_{next(counter)}",
        handling_class_for=lambda a: "personal_non_sensitive")
    assert [node.display_label for node in written] == ["Mail.app"]

    assert validate_for_freeze(
        seeded, plan_version_id="plan_1", residual_configuration={},
        approved_branch_ids=("n_root", "n_course"),
        protected_areas=(area,)) == ()
    tree = _freeze(seeded, profiles=_profiles(seeded))
    assert "Mail.app" in {node.display_label for node in tree.nodes}
    mail = next(n for n in tree.nodes if n.display_label == "Mail.app")
    assert mail.node_id not in tree.freeze_record.legal_destination_ids
    assert "n_course" in tree.freeze_record.legal_destination_ids


# --- §6.9's gate, at the stage the user can still act -----------------------------


def test_a_version_with_no_shared_material_policy_refuses_at_freeze(conn):
    """The user designs a tree, reviews it, approves it, presses freeze — and it
    FROZE. The refusal arrived at the next stage, from
    `build_destination_index`, phrased as a contract violation about a policy
    nobody had ever been asked to choose. Failing at the stage the user can still
    act on is the whole point; §5.9's warnings exist for the same reason.

    The gate is UNCONDITIONAL, and that is not the obvious-but-wrong version —
    it is what "refuse exactly when placement would refuse" actually means here.
    `placement/index.py:143` refuses ANY frozen tree with no policy, not only one
    carrying multi-home material, and it is right to: `resolve_multi_home` is
    handed `candidate_node_ids` computed during PLACEMENT from retrieval, so
    whether a file will turn out to belong in two homes is not knowable at freeze
    by anyone. The question is never contentless — it is "what should happen IF",
    and it is always answerable.
    """
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_x", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    conn.execute(
        "INSERT INTO tree_nodes SELECT * FROM tree_nodes WHERE 0")  # no-op, shape only
    write_node(conn, dataclasses.replace(
        _node("n_only", "Academics"), plan_version_id="plan_x"))

    reasons = validate_for_freeze(
        conn, plan_version_id="plan_x", residual_configuration={},
        approved_branch_ids=("n_only",))
    assert any("6.9" in reason or "shared" in reason for reason in reasons)
    with pytest.raises(FreezeRefused):
        freeze(conn, plan_version_id="plan_x", created_at=T1, user_id="jy",
               component_version="p10-1", residual_configuration={},
               approved_branch_ids=("n_only",), profiles=())


def test_the_seeded_version_with_a_policy_freezes_cleanly(seeded):
    """The discriminating half. A version that HAS the policy passes the same
    gate — the check refuses an absence, not every version."""
    assert validate_for_freeze(
        seeded, plan_version_id="plan_1", residual_configuration={},
        approved_branch_ids=("n_root", "n_course")) == ()
    assert _freeze(seeded).freeze_record.plan_version_id == "plan_1"


def test_the_freeze_gate_is_not_a_blanket_refusal(seeded):
    """The source-level half of the agreement lives at the seam in
    `tests/integration/test_p11_p10_tree.py`, where importing P11 is legitimate.
    Here: the gate refuses an ABSENCE, not every version."""
    assert _freeze(seeded).shared_material_policy == PRIMARY_HOME
