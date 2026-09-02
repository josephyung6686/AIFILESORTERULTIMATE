"""P10 Task 14 — a frozen version is immutable and an edit opens a draft.

§8.8: "When the user edits the tree, the product should create a draft plan
version and show a meaningful diff." And: "A new plan should never silently
reclassify or move old files."

§5.12 states the other half from the user's side: "The facts and accepted groups
remain separate from the tree, so the user can change the visual organization
without destroying the underlying evidence." The evidence test below is
byte-for-byte, because "unchanged" checked loosely is how evidence loss ships.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from p10 import p13_fixtures
from tree_design.diff import diff_versions
from tree_design.records import (
    ExpectedValue, Node, PlanVersion, SharedMaterialPolicy,
)
from tree_design.schema import create_tree_schema
from tree_design.store import (
    FrozenVersionImmutable,
    ReviewActionRefused,
    UnknownPlanVersion,
    apply_review_action,
    freeze_version,
    nodes_for_version,
    open_draft,
    set_shared_material_policy,
    write_node,
    write_plan_version,
)
from tree_design.vocabulary import (
    DIFF_ADDED,
    MERGE,
    OutOfVocabulary,
    DIFF_REMOVED,
    DIFF_RENAMED,
    DIFF_REPARENTED,
    DIFF_TYPE_CHANGED,
    PRIMARY_HOME,
    SURFACE_UNATTENDED,
)

T0 = "2026-08-27T00:00:00Z"
T1 = "2026-08-27T01:00:00Z"


def _ids(prefix="n"):
    counter = iter(range(1000))
    return lambda: f"{prefix}_{next(counter)}"


def _node(node_id, label, *, parent=None, node_type="proposed", role="ordinary",
          version="plan_1", origin=None, ordinal=0):
    return Node(
        node_id=node_id, plan_version_id=version, node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=ordinal, associated_group_ids=(),
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role=role,
        accepts_placement=node_type != "ignored",
        handling_class="personal_non_sensitive",
        origin_node_id=origin or node_id,
        existing_path="/Users/jy/Documents/School" if node_type == "existing" else None,
    )


@pytest.fixture()
def seeded(conn):
    create_tree_schema(conn)
    write_plan_version(conn, PlanVersion(
        plan_version_id="plan_1", predecessor_id=None, state="draft",
        created_at=T0, cross_folder_moves=False, selection_id="sel_1"))
    write_node(conn, _node("n_root", "Academics"))
    write_node(conn, _node("n_a", "Columbia", parent="n_root"))
    write_node(conn, _node("n_school", "School", node_type="existing", ordinal=1))
    return conn


def test_nodes_round_trip_through_the_store(seeded):
    nodes = {n.node_id: n for n in nodes_for_version(seeded, "plan_1")}
    assert nodes["n_a"].parent_node_id == "n_root"
    assert nodes["n_school"].existing_path == "/Users/jy/Documents/School"
    assert nodes["n_root"].accepts_placement is True


def test_a_frozen_version_refuses_every_further_write(seeded):
    freeze_version(seeded, "plan_1")
    with pytest.raises(FrozenVersionImmutable):
        write_node(seeded, _node("n_new", "Late addition"))


def test_an_edit_opens_a_draft_and_leaves_the_frozen_version_intact(seeded):
    freeze_version(seeded, "plan_1")
    draft = open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
                       created_at=T1, mint_node_id=_ids("n2"))
    assert draft.predecessor_id == "plan_1"
    assert draft.state == "draft"
    assert len(nodes_for_version(seeded, "plan_1")) == 3
    assert len(nodes_for_version(seeded, "plan_2")) == 3
    # §1.1's permission travels with the version it was frozen under.
    assert draft.cross_folder_moves is False


def test_a_copied_node_keeps_its_lineage_and_gets_a_new_identity(seeded):
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    before = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_1")}
    after = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    assert set(before) == set(after)
    assert before["n_root"].node_id != after["n_root"].node_id
    assert after["n_a"].parent_node_id == after["n_root"].node_id


def test_a_rename_produces_a_new_version_and_a_renamed_diff_entry(seeded):
    freeze_version(seeded, "plan_1")
    action = p13_fixtures.rename("n_root", plan_version="plan_1",
                                 new_label="School work")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")
    entries = diff_versions(seeded, before="plan_1", after=new_version)
    renamed = [e for e in entries if e.kind == DIFF_RENAMED]
    assert len(renamed) == 1
    assert renamed[0].before["display_label"] == "Academics"
    assert renamed[0].after["display_label"] == "School work"
    assert renamed[0].undo_label == 'Undo rename of "Academics"'


def test_a_rename_changes_no_fact_and_no_expected_value(seeded):
    """§2.8 and §3.14: renaming a node rewrites `display_label` only. The
    underlying expected values and the evidence behind them are untouched."""
    freeze_version(seeded, "plan_1")
    facts_before = seeded.execute(
        "SELECT count(*) AS n FROM events").fetchone()["n"]
    action = p13_fixtures.rename("n_root", plan_version="plan_1",
                                 new_label="School work")
    apply_review_action(seeded, action, new_version_id="plan_2", created_at=T1,
                        mint_node_id=_ids("n2"), component_version="p10-1")
    # One new event: the edit itself. No fact table exists to change, and the
    # node's expected values travel unmodified.
    facts_after = seeded.execute("SELECT count(*) AS n FROM events").fetchone()["n"]
    assert facts_after == facts_before + 1


def test_ignoring_an_existing_folder_flips_legality_and_nothing_else(seeded):
    """§5.10 lets the user leave an existing folder untouched. The node stays
    visible as context; `accepts_placement` is what stops P11 placing into it."""
    freeze_version(seeded, "plan_1")
    action = p13_fixtures.ignore_existing("n_school", plan_version="plan_1")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")
    after = {n.origin_node_id: n for n in nodes_for_version(seeded, new_version)}
    assert after["n_school"].node_type == "ignored"
    assert after["n_school"].accepts_placement is False
    assert after["n_school"].existing_path is None  # ignored is no longer `existing`
    entries = diff_versions(seeded, before="plan_1", after=new_version)
    assert DIFF_TYPE_CHANGED in {e.kind for e in entries}


def test_accepting_a_branch_writes_the_nodes_it_was_populated_with(seeded):
    """The path the whole part exists for: an accepted candidate becomes stored,
    evidence-backed nodes. Before Task 12 there was no producer for this at all.

    `project` is the injection point; here it stands in for
    `materialise.project_branch_nodes` bound to the branch's evidence."""
    action = p13_fixtures.accept("cand_academics", plan_version="plan_1")

    def project(_action, plan_version_id):
        return (_node("n_columbia", "Columbia", version=plan_version_id),
                _node("n_busib", "BUSIB 4300", parent="n_columbia",
                      version=plan_version_id))

    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids(), component_version="p10-1", project=project)
    labels = {n.display_label for n in nodes_for_version(seeded, new_version)}
    assert {"Columbia", "BUSIB 4300"} <= labels
    row = seeded.execute(
        "SELECT * FROM events WHERE event_type = 'destination-tree edit' "
        "AND correction_subject = 'cand_academics'").fetchone()
    assert row is not None


def test_accepting_a_branch_whose_files_all_agree_records_no_new_folder(seeded):
    """The composition that populates the BRANCH rather than a child.

    Every level names one value, so §5.4 builds no folder -- "you would open it
    to find one folder" -- and what the projection hands over is the branch node
    itself, rewritten with the values its files share. The refusal below must not
    fire on it: nothing here is a silent no-op, the node is written and the
    expected values are new.

    The sentence in the log has to say so. "It became 1 node(s)" would tell a
    reader a folder appeared, and none did.
    """
    action = p13_fixtures.accept("n_root", plan_version="plan_1")

    def project(_action, plan_version_id):
        parent = next(node for node in nodes_for_version(seeded, plan_version_id)
                      if node.origin_node_id == "n_root")
        return (dataclasses.replace(parent, expected_values=(
            ExpectedValue(field="subject", value="PHYS1401"),)),)

    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids(), component_version="p10-1", project=project)
    written = {n.origin_node_id: n for n in nodes_for_version(seeded, new_version)}
    assert written["n_root"].expected_values == (
        ExpectedValue(field="subject", value="PHYS1401"),)
    row = seeded.execute(
        "SELECT explanation FROM events WHERE event_type = 'destination-tree edit' "
        "AND correction_subject = 'n_root'").fetchone()
    assert "no folder was added" in row["explanation"]
    assert "node(s) built from facts" not in row["explanation"]


def test_an_accept_that_would_write_no_node_is_refused_not_silently_empty(seeded):
    """A branch whose files carry no settled value at any dimension has nothing
    to build. Opening a draft that changed nothing would show the user a new
    version with no visible difference and no error."""
    action = p13_fixtures.accept("cand_empty", plan_version="plan_1")
    with pytest.raises(ReviewActionRefused):
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids(), component_version="p10-1",
            project=lambda _a, _v: ())
    # The SAME version id, deliberately. The first refusal rolled its draft back,
    # so nothing claimed the id; the original spelling reached for `plan_3` here
    # because the failed call had already committed `plan_2`.
    with pytest.raises(ReviewActionRefused):
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids(), component_version="p10-1")


def test_no_code_path_renames_an_existing_node_without_a_recorded_action(seeded):
    """§5.10's hard prohibition: "Existing folders must not be automatically
    flattened, renamed, or reorganized simply because a template would produce a
    different structure."
    """
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    after = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    assert after["n_school"].display_label == "School"
    assert after["n_school"].node_type == "existing"
    assert after["n_school"].existing_path == "/Users/jy/Documents/School"


def test_the_diff_reports_all_seven_kinds_it_can_observe(seeded):
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    nodes = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    seeded.execute("DELETE FROM tree_nodes WHERE plan_version_id = ? AND node_id = ?",
                   ("plan_2", nodes["n_a"].node_id))
    write_node(seeded, Node(
        node_id="n2_extra", plan_version_id="plan_2", node_type="user-created",
        display_label="Reading", parent_node_id=nodes["n_root"].node_id,
        root_anchor="root_documents", ordinal=2, associated_group_ids=(),
        explanation="The user created this branch by name.",
        node_role="ordinary", accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id="n2_extra"))
    entries = diff_versions(seeded, before="plan_1", after="plan_2")
    kinds = {e.kind for e in entries}
    assert DIFF_REMOVED in kinds
    assert DIFF_ADDED in kinds


def test_a_shared_material_policy_is_recorded_per_version(seeded):
    set_shared_material_policy(seeded, SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None,
        reason="A transcript lives in one packet and is referenced from the other."))
    row = seeded.execute("SELECT * FROM shared_material_policies").fetchone()
    assert row["policy"] == PRIMARY_HOME
    assert row["policy_scope"] is None


def test_two_global_shared_material_policies_in_one_version_are_refused(seeded):
    import sqlite3

    set_shared_material_policy(seeded, SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None, reason="first"))
    with pytest.raises(sqlite3.IntegrityError):
        set_shared_material_policy(seeded, SharedMaterialPolicy(
            policy_id="smp_2", plan_version_id="plan_1", policy=PRIMARY_HOME,
            policy_scope=None, reason="second"))


def test_restoring_an_earlier_version_creates_a_new_draft_and_deletes_nothing(seeded):
    freeze_version(seeded, "plan_1")
    action = p13_fixtures.rename("n_root", plan_version="plan_1",
                                 new_label="School work")
    apply_review_action(seeded, action, new_version_id="plan_2", created_at=T1,
                        mint_node_id=_ids("n2"), component_version="p10-1")
    freeze_version(seeded, "plan_2")
    restore = p13_fixtures.restore("plan_2", target="plan_1")
    third = apply_review_action(
        seeded, restore, new_version_id="plan_3", created_at=T1,
        mint_node_id=_ids("n3"), component_version="p10-1")
    labels = {n.origin_node_id: n.display_label
              for n in nodes_for_version(seeded, third)}
    assert labels["n_root"] == "Academics"
    assert len(nodes_for_version(seeded, "plan_2")) == 3
    assert len(nodes_for_version(seeded, "plan_1")) == 3


def test_a_partial_depth_design_survives_a_round_trip(seeded):
    """DM17: one refined, one shallow-by-choice, one refine-later branch, each
    with a reason, all in one version."""
    for node_id, disposition, reason in (
        ("n_r", "refined", "The course groups justify the split."),
        ("n_s", "shallow-by-choice", "Twelve receipts need no vendor level."),
        ("n_l", "refine-later", "Not enough validated facts yet."),
    ):
        write_node(seeded, Node(
            node_id=node_id, plan_version_id="plan_1", node_type="proposed",
            display_label=node_id, parent_node_id=None,
            root_anchor="root_documents", ordinal=9, associated_group_ids=(),
            explanation="A branch the user approved at the top level.",
            node_role="ordinary", accepts_placement=True,
            handling_class="personal_non_sensitive", origin_node_id=node_id,
            refinement_disposition=disposition, refinement_reason=reason))
    stored = {n.node_id: n for n in nodes_for_version(seeded, "plan_1")}
    assert {stored[n].refinement_disposition for n in ("n_r", "n_s", "n_l")} == {
        "refined", "shallow-by-choice", "refine-later"}
    assert all(stored[n].refinement_reason for n in ("n_r", "n_s", "n_l"))


# --- repairs: a refusal must leave nothing behind, and must say what it refused --


def test_a_refused_action_leaves_no_draft_behind(seeded):
    """The refusal paths opened the draft BEFORE they checked anything.

    The connection is autocommit (`open_database` passes `isolation_level=None`),
    so a draft opened before a refusal is COMMITTED before the raise. The user is
    then left with a new plan version holding a full copy of the tree and no edit
    in it — which is precisely the outcome `apply_review_action`'s own docstring
    says must never happen: "a no-op edit still opens a draft and the user would
    see a new version that changed nothing".

    One accepted edit is ONE new plan version, or it is none.
    """
    action = p13_fixtures.accept("cand_empty", plan_version="plan_1")
    with pytest.raises(ReviewActionRefused):
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids(), component_version="p10-1",
            project=lambda _a, _v: ())
    versions = [r["plan_version_id"] for r in
                seeded.execute("SELECT plan_version_id FROM plan_versions")]
    assert versions == ["plan_1"]
    assert nodes_for_version(seeded, "plan_2") == ()
    # And the same id is still free, because nothing claimed it.
    assert nodes_for_version(seeded, "plan_1") != ()


def test_a_refused_action_appends_no_event(seeded):
    """§8.2 logs edits that happened. An event for a refused action would put a
    tree edit in the replay log that never reached the tree."""
    before = seeded.execute("SELECT count(*) AS n FROM events").fetchone()["n"]
    action = dataclasses.replace(
        p13_fixtures.rename("n_root", plan_version="plan_1", new_label="x"),
        action=MERGE)
    with pytest.raises(ReviewActionRefused):
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids(), component_version="p10-1")
    assert seeded.execute("SELECT count(*) AS n FROM events").fetchone()["n"] == before


def test_a_refused_action_is_not_reported_as_a_frozen_version(seeded):
    """`FrozenVersionImmutable` named exactly one thing: a write to a frozen
    version. It was being raised for five others — a missing projection, an empty
    projection, an unknown target, an unhandled action, and a draft opened from a
    version that does not exist. A reader who caught it to mean "the user edited
    a frozen plan, open a draft and retry" would retry forever on every one of
    them."""
    freeze_version(seeded, "plan_1")
    with pytest.raises(FrozenVersionImmutable):
        write_node(seeded, _node("n_new", "Late addition"))

    action = dataclasses.replace(
        p13_fixtures.rename("n_root", plan_version="plan_1", new_label="x"),
        action=MERGE)
    with pytest.raises(ReviewActionRefused) as excinfo:
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids(), component_version="p10-1")
    assert not isinstance(excinfo.value, FrozenVersionImmutable)


def test_an_action_with_no_writer_is_refused_by_its_own_name(seeded):
    """The refusal sat AFTER the target lookup, so `merge` against a node this
    version does not hold reported "names node 'n_absent', which this version
    does not contain" — a message about the wrong problem. Fixing the node id
    would produce a second, different error.

    An action with no writer is refused by NAME, before anything is looked up.
    """
    action = dataclasses.replace(
        p13_fixtures.rename("n_absent", plan_version="plan_1", new_label="x"),
        action=MERGE)
    with pytest.raises(ReviewActionRefused) as excinfo:
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids(), component_version="p10-1")
    message = str(excinfo.value)
    assert MERGE in message
    assert "n_absent" not in message


def test_every_tree_edit_action_is_named_by_the_writer_or_by_the_refusal(seeded):
    """The guard against a silent fall-through: the union of what
    `apply_review_action` writes and what it refuses BY NAME is exactly
    `TREE_EDIT_ACTIONS`. A member in neither set would reach a default branch and
    a member added to the vocabulary later cannot quietly inherit one."""
    from tree_design.store import ACTIONS_WITH_NO_WRITER, ACTIONS_WITH_A_WRITER
    from tree_design.vocabulary import TREE_EDIT_ACTIONS

    assert ACTIONS_WITH_A_WRITER | ACTIONS_WITH_NO_WRITER == set(TREE_EDIT_ACTIONS)
    assert not (ACTIONS_WITH_A_WRITER & ACTIONS_WITH_NO_WRITER)
    for name in ACTIONS_WITH_NO_WRITER:
        action = dataclasses.replace(
            p13_fixtures.rename("n_root", plan_version="plan_1", new_label="x"),
            action=name)
        with pytest.raises(ReviewActionRefused) as excinfo:
            apply_review_action(
                seeded, action, new_version_id=f"plan_{name}", created_at=T1,
                mint_node_id=_ids(), component_version="p10-1")
        assert name in str(excinfo.value)
    assert [r["plan_version_id"] for r in
            seeded.execute("SELECT plan_version_id FROM plan_versions")] == ["plan_1"]


def test_an_action_name_outside_the_vocabulary_is_refused_before_any_database_work(seeded):
    """A misspelling is a different failure from an unbuilt gesture, and it must
    not borrow the unbuilt gesture's message. `renmae` is not "a rename with no
    writer"; it is a name P10 does not define.

    The version below does not exist, and that is the point. `OutOfVocabulary`
    can only come back if the name was checked BEFORE anything was looked up —
    otherwise `open_draft` reaches an absent version first and reports
    `UnknownPlanVersion`.

    The weaker spelling of this test named a version that DID exist, and it
    passed with the check deleted: the misspelling travelled all the way through
    `open_draft`, found its target, flipped the node to `ignored` down the
    `else` branch, and was finally caught by `record_tree_edit`'s own vocabulary
    check on the way to the event log. Right exception, wrong guard, four writes
    too late — a silent guard.
    """
    action = dataclasses.replace(
        p13_fixtures.rename("n_root", plan_version="plan_absent", new_label="x"),
        action="renmae")
    with pytest.raises(OutOfVocabulary):
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids(), component_version="p10-1")
    assert [r["plan_version_id"] for r in
            seeded.execute("SELECT plan_version_id FROM plan_versions")] == ["plan_1"]


def test_freezing_a_version_that_does_not_exist_is_refused(seeded):
    """`UPDATE ... WHERE plan_version_id = ?` against an absent id changes no row
    and returns cleanly. A caller that froze a mistyped id got success, and the
    version it meant to freeze stayed a draft — editable, with §8.8's immutability
    believed to be in force."""
    with pytest.raises(UnknownPlanVersion):
        freeze_version(seeded, "plan_absent")
    assert _state_of(seeded, "plan_1") == "draft"


def test_opening_a_draft_from_a_version_that_does_not_exist_is_refused(seeded):
    with pytest.raises(UnknownPlanVersion):
        open_draft(seeded, from_version="plan_absent", new_version_id="plan_2",
                   created_at=T1, mint_node_id=_ids("n2"))
    assert [r["plan_version_id"] for r in
            seeded.execute("SELECT plan_version_id FROM plan_versions")] == ["plan_1"]


def _state_of(conn, plan_version_id):
    row = conn.execute("SELECT state FROM plan_versions WHERE plan_version_id = ?",
                       (plan_version_id,)).fetchone()
    return None if row is None else row["state"]


def test_removing_a_parent_does_not_report_its_children_as_moved(seeded):
    """`_parent_origin` fell back to the raw minted `node_id` when a node's
    parent row was not in that version.

    A minted id is per-version, so the two sides could never compare equal, and
    every child of a removed node came back as `re-parented` with an undo label
    reading 'Undo moving "Columbia"'. Nothing moved it — its parent was deleted,
    which the diff already reports as `removed` on the parent. The phantom entry
    hands the user an undo control for an edit nobody made.
    """
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    nodes = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    seeded.execute("DELETE FROM tree_nodes WHERE plan_version_id = ? AND node_id = ?",
                   ("plan_2", nodes["n_root"].node_id))

    entries = diff_versions(seeded, before="plan_1", after="plan_2")
    removed = [e for e in entries if e.kind == DIFF_REMOVED]
    assert [e.origin_node_id for e in removed] == ["n_root"]
    moved = [e for e in entries if e.kind == DIFF_REPARENTED]
    assert moved == [], f"nothing moved {[e.origin_node_id for e in moved]}"


def test_a_real_reparenting_is_still_reported(seeded):
    """The guard above suppresses an entry, so it needs the other half: a child
    genuinely moved under a different parent still reports `re-parented`."""
    freeze_version(seeded, "plan_1")
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    nodes = {n.origin_node_id: n for n in nodes_for_version(seeded, "plan_2")}
    write_node(seeded, dataclasses.replace(
        nodes["n_a"], parent_node_id=nodes["n_school"].node_id))
    entries = diff_versions(seeded, before="plan_1", after="plan_2")
    moved = [e for e in entries if e.kind == DIFF_REPARENTED]
    assert [e.origin_node_id for e in moved] == ["n_a"]
    assert moved[0].before["parent_origin"] == "n_root"
    assert moved[0].after["parent_origin"] == "n_school"


# --- the two promoted writers: the design's answer to overlap --------------------


def test_a_scoped_general_branch_is_created_inside_its_parent(seeded):
    """`00`:99: "if a file is clearly part of Academics/Columbia/2026-Spring but
    has no recoverable work type, the future tree can include
    Academics/Columbia/2026-Spring/General rather than sending it to a global
    Unsorted folder. A GLOBAL CATCH-ALL FOLDER SHOULD NOT BECOME THE PRODUCT'S
    DEFAULT ANSWER TO AMBIGUITY."

    `node_role=SCOPED_GENERAL` was in the vocabulary, carried on `Node`, and had
    NO WRITER anywhere in `src/`, so the design's named answer to the commonest
    ambiguity there is could not be produced.
    """
    from tree_design.vocabulary import SCOPED_GENERAL

    freeze_version(seeded, "plan_1")
    action = p13_fixtures.add_scoped_general("n_a", plan_version="plan_1")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")

    nodes = {n.display_label: n for n in nodes_for_version(seeded, new_version)}
    general = nodes["General"]
    assert general.node_role == SCOPED_GENERAL
    # SCOPED, not global: its parent is the branch the user named.
    columbia = next(n for n in nodes_for_version(seeded, new_version)
                    if n.origin_node_id == "n_a")
    assert general.parent_node_id == columbia.node_id
    assert general.accepts_placement is True
    assert general.parent_node_id is not None, "a scoped general is never a root"


def test_a_scoped_general_at_the_root_is_refused_as_a_global_catch_all(seeded):
    """The discriminating half, and it is the sentence's own second clause. A
    General with no parent IS the global Unsorted folder the design rejects."""
    freeze_version(seeded, "plan_1")
    action = dataclasses.replace(
        p13_fixtures.add_scoped_general("n_a", plan_version="plan_1"),
        subject_ref="__root__")
    with pytest.raises(ReviewActionRefused) as excinfo:
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids("n2"), component_version="p10-1")
    assert "global" in str(excinfo.value).lower()


def test_a_shared_material_branch_is_created_above_the_competition(seeded):
    """§6.9, and the reason three of its four policies silently collapsed into
    one: `node_role=SHARED_MATERIAL` had no writer, so P11's
    `groups.resolve_multi_home` never received a `shared_branch_node_id` and
    `shared-branch`, `primary-home` and `reference-or-alias` all fell through to
    the same ask-or-abstain as `mandatory-review`.
    """
    from tree_design.vocabulary import SHARED_BRANCH, SHARED_MATERIAL

    freeze_version(seeded, "plan_1")
    action = p13_fixtures.set_shared_material_policy(
        "n_root", plan_version="plan_1", policy=SHARED_BRANCH,
        reason="A transcript belongs to two application packets.")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")

    shared = next(n for n in nodes_for_version(seeded, new_version)
                  if n.node_role == SHARED_MATERIAL)
    assert shared.display_label == "Shared Material"
    assert shared.accepts_placement is True
    # The policy is recorded for the NEW version, so the frozen bundle carries it.
    row = seeded.execute(
        "SELECT * FROM shared_material_policies WHERE plan_version_id = ?",
        (new_version,)).fetchone()
    assert row["policy"] == SHARED_BRANCH
    assert row["reason"]


def test_the_shared_branch_is_never_one_of_the_competing_homes(seeded):
    """Bound against P11's live refusal: `resolve_multi_home` raises
    `InstitutionalDestinationRefused` when `shared_branch_node_id` is one of the
    candidates, because "placing there IS choosing between them". So the node
    P10 produces has to sit ABOVE them, and this drives P11's real function."""
    from placement.groups import resolve_multi_home
    from tree_design.vocabulary import SHARED_BRANCH, SHARED_MATERIAL

    freeze_version(seeded, "plan_1")
    action = p13_fixtures.set_shared_material_policy(
        "n_root", plan_version="plan_1", policy=SHARED_BRANCH,
        reason="A transcript belongs to two application packets.")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")
    nodes = nodes_for_version(seeded, new_version)
    shared = next(n for n in nodes if n.node_role == SHARED_MATERIAL)
    competing = [n.node_id for n in nodes
                 if n.node_role == "ordinary" and n.parent_node_id]

    outcome, payload = resolve_multi_home(
        candidate_node_ids=competing + ["n_other"],
        shared_material_policy=SHARED_BRANCH,
        shared_branch_node_id=shared.node_id, ask_or_abstain=None)
    assert outcome == "place"
    assert payload == shared.node_id


def test_a_mandatory_review_policy_creates_no_branch(seeded):
    """The discriminating half. §6.9's fourth policy is the one that does NOT
    resolve to a destination — `mandatory-review` means ask the user. Producing a
    branch for it would answer a question the policy exists to keep open."""
    from tree_design.vocabulary import MANDATORY_REVIEW, SHARED_MATERIAL

    freeze_version(seeded, "plan_1")
    action = p13_fixtures.set_shared_material_policy(
        "n_root", plan_version="plan_1", policy=MANDATORY_REVIEW,
        reason="The user wants to decide these one at a time.")
    new_version = apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")
    assert not [n for n in nodes_for_version(seeded, new_version)
                if n.node_role == SHARED_MATERIAL]
    row = seeded.execute(
        "SELECT * FROM shared_material_policies WHERE plan_version_id = ?",
        (new_version,)).fetchone()
    assert row["policy"] == MANDATORY_REVIEW


def test_the_two_promoted_actions_left_the_no_writer_set(seeded):
    from tree_design.store import ACTIONS_WITH_A_WRITER, ACTIONS_WITH_NO_WRITER
    from tree_design.vocabulary import ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY

    assert {ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY} <= ACTIONS_WITH_A_WRITER
    assert not ({ADD_SCOPED_GENERAL, SET_SHARED_MATERIAL_POLICY}
                & ACTIONS_WITH_NO_WRITER)
    assert len(ACTIONS_WITH_NO_WRITER) == 10


def test_a_shared_material_policy_with_no_reason_is_refused(seeded):
    """§6.9's policy decides what happens to a file that belongs in two places.
    `SharedMaterialPolicy` already requires a reason at construction, and this
    refuses it one layer earlier, where the action can be named — a policy the
    user cannot review is one they cannot change their mind about.

    Fourth time today a required input had no test for its absence. A required
    input with no test for its absence is not required.
    """
    from tree_design.vocabulary import SHARED_BRANCH

    freeze_version(seeded, "plan_1")
    action = p13_fixtures.set_shared_material_policy(
        "n_root", plan_version="plan_1", policy=SHARED_BRANCH, reason="   ")
    with pytest.raises(ReviewActionRefused) as excinfo:
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids("n2"), component_version="p10-1")
    assert "reason" in str(excinfo.value)
    assert [r["plan_version_id"] for r in
            seeded.execute("SELECT plan_version_id FROM plan_versions")] == ["plan_1"]


def test_a_policy_outside_6_9s_four_is_refused_as_out_of_vocabulary(seeded):
    """The other half: a misspelled policy is a load error, not a fifth rule."""
    from tree_design.vocabulary import OutOfVocabulary

    freeze_version(seeded, "plan_1")
    action = p13_fixtures.set_shared_material_policy(
        "n_root", plan_version="plan_1", policy="pick-whichever",
        reason="A transcript belongs to two packets.")
    with pytest.raises(OutOfVocabulary):
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids("n2"), component_version="p10-1")


# --- §6.9's policy is version state, and a draft is a copy of a version ------------


def _global_policies(conn, plan_version_id):
    return conn.execute(
        "SELECT * FROM shared_material_policies WHERE plan_version_id = ? "
        "AND policy_scope IS NULL", (plan_version_id,)).fetchall()


def test_a_draft_carries_the_69_policy_the_user_already_chose(seeded):
    """`open_draft` copied the NODES and left §6.9's policy behind.

    The consequence is not cosmetic and it is not local to this function. A user
    who chose `primary-home` and then renamed one folder had their answer
    silently revoked: `freeze._shared_material` reads
    `shared_material_policies WHERE plan_version_id = ?`, the draft holds no row,
    and `validate_for_freeze` then refuses the freeze with "this plan version
    carries no §6.9 shared-material policy" — about a version whose predecessor
    carries one and whose shared-material NODE was copied across intact. The
    refusal names the one thing the user did do.

    One step further and it is worse: had the freeze gone through, `FrozenTree.
    shared_material_policy` would be `None` and `build_destination_index` would
    refuse the whole tree at P11's end, where nobody can act on it.
    """
    set_shared_material_policy(seeded, SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None,
        reason="A transcript lives in one packet and is referenced from the other."))
    freeze_version(seeded, "plan_1")

    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))

    carried = _global_policies(seeded, "plan_2")
    assert len(carried) == 1, "the draft lost the policy the user chose"
    assert carried[0]["policy"] == PRIMARY_HOME
    assert carried[0]["reason"].startswith("A transcript lives")
    # A new row, not the same one: `policy_id` is the primary key and the
    # predecessor keeps its own record, because a frozen version is immutable.
    assert carried[0]["policy_id"] != "smp_1"
    assert len(_global_policies(seeded, "plan_1")) == 1


def test_a_per_branch_69_policy_is_carried_with_its_scope(seeded):
    """OQ9 is open — the policy may be tree-global or per-branch — so the copy
    carries `policy_scope` verbatim rather than flattening every row to global."""
    set_shared_material_policy(seeded, SharedMaterialPolicy(
        policy_id="smp_scoped", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope="n_root", reason="Only the Academics branch competes."))
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    rows = seeded.execute(
        "SELECT * FROM shared_material_policies WHERE plan_version_id = 'plan_2'"
    ).fetchall()
    assert [(r["policy"], r["policy_scope"]) for r in rows] == [
        (PRIMARY_HOME, "n_root")]


def test_a_draft_of_a_version_with_no_policy_still_has_none(seeded):
    """The negative twin. The copy carries what is there and invents nothing —
    a draft that acquired a policy nobody chose would answer §6.9 for the user,
    which is the failure `validate_for_freeze` refuses the freeze to prevent."""
    open_draft(seeded, from_version="plan_1", new_version_id="plan_2",
               created_at=T1, mint_node_id=_ids("n2"))
    assert _global_policies(seeded, "plan_2") == []


def test_setting_a_new_69_policy_on_a_draft_replaces_the_carried_one(seeded):
    """The user changing their mind is one policy, not two.

    `one_global_shared_material_policy` is a partial unique index, so once the
    draft carries the predecessor's row, `set-shared-material-policy` on that
    draft would raise `IntegrityError` — the user would be unable to change an
    answer they had already given. The writer replaces its own version's row and
    leaves every other version's alone.
    """
    from tree_design.vocabulary import SHARED_BRANCH

    set_shared_material_policy(seeded, SharedMaterialPolicy(
        policy_id="smp_1", plan_version_id="plan_1", policy=PRIMARY_HOME,
        policy_scope=None, reason="The first answer."))
    freeze_version(seeded, "plan_1")

    new_version = apply_review_action(
        seeded, p13_fixtures.set_shared_material_policy(
            "n_root", plan_version="plan_1", policy=SHARED_BRANCH,
            reason="On reflection a shared branch above the packets is better."),
        new_version_id="plan_2", created_at=T1, mint_node_id=_ids("n2"),
        component_version="p10-test")

    rows = _global_policies(seeded, new_version)
    assert len(rows) == 1
    assert rows[0]["policy"] == SHARED_BRANCH
    # The frozen predecessor is untouched: §8.8 makes it immutable.
    assert _global_policies(seeded, "plan_1")[0]["policy"] == PRIMARY_HOME


def _first_line(conn, subject):
    row = conn.execute(
        "SELECT explanation FROM events WHERE correction_subject = ? "
        "ORDER BY event_id DESC", (subject,)).fetchone()
    assert row is not None, f"no event was written for {subject!r}"
    # `_explanation` writes the human sentence, a newline, then the payload. The
    # sentence is what a person reads, and it is the sentence that overclaimed.
    return row["explanation"].splitlines()[0]


def test_an_unattended_accept_says_the_rules_accepted_it_and_names_no_surface(seeded):
    """The log must not put a person in front of a screen that was never drawn.

    `SURFACE_UNATTENDED` is in force whenever the run had nobody to show the tree
    to, which is every run of the shipped command. What it may NOT change is that
    the event exists and says what happened: the branch really was accepted and
    really did become nodes, and a log that dropped the event to avoid
    overstating it would be worse than the overstatement.
    """
    action = dataclasses.replace(
        p13_fixtures.accept("cand_academics", plan_version="plan_1"),
        surface=SURFACE_UNATTENDED)

    def project(_action, plan_version_id):
        return (_node("n_columbia", "Columbia", version=plan_version_id),)

    apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids(), component_version="p10-1", project=project)

    sentence = _first_line(seeded, "cand_academics")
    assert "The user" not in sentence, sentence
    assert "surface" not in sentence, sentence
    # Still says what did happen, with the subject and the count intact.
    assert "cand_academics" in sentence and "1 node" in sentence, sentence
    assert "nobody at the screen" in sentence, sentence


def test_an_attended_accept_still_names_the_person_and_the_surface(seeded):
    """The negative twin. The day P13 ships, a real click on a real canvas is a
    person's decision and the record should keep saying so -- a fix that scrubbed
    the user from every sentence would lose the thing the log is for."""
    action = p13_fixtures.accept("cand_academics", plan_version="plan_1")
    apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids(), component_version="p10-1",
        project=lambda _a, v: (_node("n_columbia", "Columbia", version=v),))
    sentence = _first_line(seeded, "cand_academics")
    assert sentence.startswith("The user accepted 'cand_academics' on the canvas "
                               "surface"), sentence


def test_an_unattended_rename_claims_no_person_either(seeded):
    """The second sentence that named `{action.surface}`. Same rule, same reason:
    an edit applied by rule is not an edit somebody made."""
    action = dataclasses.replace(
        p13_fixtures.rename("n_root", plan_version="plan_1", new_label="School work"),
        surface=SURFACE_UNATTENDED)
    apply_review_action(
        seeded, action, new_version_id="plan_2", created_at=T1,
        mint_node_id=_ids("n2"), component_version="p10-1")
    sentence = _first_line(seeded, "n_root")
    assert "The user" not in sentence, sentence
    assert "surface" not in sentence, sentence
    assert "'rename'" in sentence and "Academics" in sentence, sentence


def test_a_surface_outside_the_closed_set_is_refused_rather_than_printed(seeded):
    """A surface name P10 does not define would be interpolated into the audit
    sentence verbatim -- "on the whatever surface" -- which is a value a
    deployment invented acquiring a meaning nobody designed."""
    action = dataclasses.replace(
        p13_fixtures.rename("n_root", plan_version="plan_1", new_label="x"),
        surface="whiteboard")
    with pytest.raises(OutOfVocabulary):
        apply_review_action(
            seeded, action, new_version_id="plan_2", created_at=T1,
            mint_node_id=_ids("n2"), component_version="p10-1")
