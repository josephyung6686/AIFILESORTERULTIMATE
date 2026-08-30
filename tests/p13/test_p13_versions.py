"""§8.8 + `66` §17: a visible diff, and a draft the user explicitly adopts.

`74` §6 B12's named test is
`test_adopting_a_draft_version_never_reclassifies_or_moves_an_existing_file` and
its negative twin is `test_a_diff_that_omits_a_removed_node_fails`.

`66` §17 is newer than the SPEC and governs: a changed structural answer produces
a DRAFT plan version with a meaningful diff, and "must not silently rename
folders, reclassify files, reveal protected records, or move anything as a
consequence of a changed answer." Three of its six diff dimensions have no
producer anywhere in src/; they are reported as absent rather than invented.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from placement.versions import VersionDiff
from privacy.display import RedactionSettings
from tree_design.diff import DIFF_REMOVED, DIFF_RENAMED
from tree_design.records import Node, PlanVersion
from tree_design.store import write_node, write_plan_version
from tree_design.user_edits import UnappliedUserEdit, UserLevelEdit

from review_surface.presentation import record_presentation
from review_surface.versions_view import (
    THREE_VERSION_ACTIONS,
    NothingIsAdoptedSilently,
    RemovedNodeMissingFromDiff,
    collect_version_action,
    structural_diff_view,
)
from review_surface.vocabulary import (
    ACTION_ADOPT_VERSION,
    ACTION_RESTORE_VERSION,
    SURFACE_PLAN_VERSION,
)

T0 = "2026-08-29T00:00:00Z"
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")


def _node(conn, *, version, node_id, label, origin):
    write_node(conn, Node(
        node_id=node_id, plan_version_id=version, node_type="proposed",
        display_label=label, parent_node_id=None, root_anchor="root",
        ordinal=0, associated_group_ids=(), explanation="fixture",
        node_role="ordinary", accepts_placement=True,
        handling_class="public_low", origin_node_id=origin,
        template_context=None, dimension_role=None, dimension=None,
        expected_values=(), existing_path=None, disposition=None,
        refinement_disposition=None, refinement_reason=None,
        protected_movement_permitted=False))


def _versions(conn, *, with_removed=True):
    for version_id, predecessor in (("plan-1", None), ("plan-2", "plan-1")):
        write_plan_version(conn, PlanVersion(
            plan_version_id=version_id, predecessor_id=predecessor,
            state="draft", created_at=T0, cross_folder_moves=False,
            selection_id="sel-1"))
    # `Applications` renamed to `Admissions` -- §8.8's own first example.
    _node(conn, version="plan-1", node_id="n-a1", label="Applications",
          origin="origin-a")
    _node(conn, version="plan-2", node_id="n-a2", label="Admissions",
          origin="origin-a")
    if with_removed:
        # A node that exists in plan-1 and not in plan-2: the removal that makes
        # twenty-three files need renewed review.
        _node(conn, version="plan-1", node_id="n-gone", label="Reference Clips",
              origin="origin-gone")


TWENTY_THREE = VersionDiff(
    from_plan_version="plan-1", to_plan_version="plan-2",
    requiring_renewed_review=tuple(f"d-{n}" for n in range(23)),
    carried_unchanged=("d-99",), removed_node_ids=("origin-gone",))


def _view(conn, **overrides):
    values = dict(before="plan-1", after="plan-2", version_diff=TWENTY_THREE)
    values.update(overrides)
    return structural_diff_view(conn, **values)


def _ref(conn, subject):
    return record_presentation(
        conn, surface=SURFACE_PLAN_VERSION, subject_ref=subject,
        plan_version="plan-2", session_id="s-1", settings=SHOWN,
        evidence_refs=(), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref


def test_adopting_a_draft_version_never_reclassifies_or_moves_an_existing_file(
        p13_conn):
    """`74` §6 B12's named test, and Done-means 21.

    Four things must hold together, because `66` §17's prohibition is about what
    happens as a CONSEQUENCE of adoption:

    * the view adopts nothing -- `adopted` is False on every view this builds,
      because existing approved structure stays stable unless the user
      explicitly adopts the new plan;
    * adoption is a collected gesture routed to P10, which owns the record;
    * the files that need renewed review are PRESENTED as needing it and are
      never pre-accepted at their old destination, because approvals do not
      carry across versions;
    * and the module imports no writer at all, asserted by parsing rather than
      by promising.
    """
    _versions(p13_conn)
    view = _view(p13_conn)
    assert view.adopted is False
    assert view.renewed_review.count == 23
    assert "23" in view.renewed_review.sentence
    assert "renewed review" in view.renewed_review.sentence
    assert len(view.renewed_review.subject_refs) == 23
    assert "not pre-accepted" in view.renewed_review.sentence

    action = collect_version_action(
        p13_conn, view, ACTION_ADOPT_VERSION, action_id="a-adopt",
        plan_version="plan-2", session_id="s-1", correction_scope="corpus",
        presented_state_ref=_ref(p13_conn, "plan-2"), user_id="jy",
        acted_at=T0, component_version="p13-1")
    assert action.routed_to == ("P10",)
    assert action.subject_ref == "plan-2"

    import review_surface.versions_view as module

    tree = ast.parse(pathlib.Path(inspect.getfile(module)).read_text())
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    names |= {node.attr for node in ast.walk(tree)
              if isinstance(node, ast.Attribute)}
    names |= {alias.name.split(".")[0] for node in ast.walk(tree)
              if isinstance(node, ast.Import) for alias in node.names}
    names |= {alias.name for node in ast.walk(tree)
              if isinstance(node, ast.ImportFrom) for alias in node.names}
    for writer in ("write_node", "write_plan_version", "apply_review_action",
                   "freeze_version", "rename", "replace", "shutil", "os"):
        assert writer not in names, f"{writer} is reachable from the view module"


def test_a_diff_that_omits_a_removed_node_fails(p13_conn):
    """`74` §6 B12's negative twin.

    P11 says twenty-three files need renewed review because a destination no
    longer exists; P10's node diff is what shows the user WHICH destination. If
    P11 names a removed node the node diff does not report, the screen states a
    consequence with no visible cause -- which is §8.8's sentence with its second
    half missing, and is worse than no diff at all because it looks complete.

    Both directions are asserted: the honest pair passes, and a `VersionDiff`
    naming a node the tree diff never removed is refused by name.
    """
    _versions(p13_conn)
    view = _view(p13_conn)
    removed = {entry.origin_node_id for entry in view.node_entries
               if entry.kind == DIFF_REMOVED}
    assert "origin-gone" in removed

    with pytest.raises(RemovedNodeMissingFromDiff) as caught:
        _view(p13_conn, version_diff=VersionDiff(
            from_plan_version="plan-1", to_plan_version="plan-2",
            requiring_renewed_review=("d-1",), carried_unchanged=(),
            removed_node_ids=("origin-gone", "origin-never-existed")))
    assert "origin-never-existed" in str(caught.value)
    assert "origin-gone" not in str(caught.value)

    # And a tree where nothing was removed refuses the same claim, so the check
    # is about agreement rather than about the fixture happening to have a node.
    p13_conn.execute("DELETE FROM tree_nodes WHERE node_id = 'n-gone'")
    with pytest.raises(RemovedNodeMissingFromDiff):
        _view(p13_conn)


def test_the_node_level_diff_shows_the_rename(p13_conn):
    """§8.8's own example: Applications was renamed to Admissions."""
    _versions(p13_conn)
    view = _view(p13_conn)
    renamed = next(e for e in view.node_entries if e.kind == DIFF_RENAMED)
    assert renamed.before["display_label"] == "Applications"
    assert renamed.after["display_label"] == "Admissions"
    assert renamed.undo_label


def test_compare_restore_and_adopt_are_all_collectable(p13_conn):
    """Done-means 21, second clause. §8.8's three named user actions."""
    _versions(p13_conn)
    assert THREE_VERSION_ACTIONS == ("compare", "restore_version",
                                     "adopt_version")
    assert _view(p13_conn).available_actions == THREE_VERSION_ACTIONS


def test_restoring_names_the_version_being_restored_to(p13_conn):
    """Naming the same version for both gestures would make them
    indistinguishable in the store, and P10 branches on the difference."""
    _versions(p13_conn)
    action = collect_version_action(
        p13_conn, _view(p13_conn), ACTION_RESTORE_VERSION,
        action_id="a-restore", plan_version="plan-2", session_id="s-1",
        correction_scope="corpus", presented_state_ref=_ref(p13_conn, "plan-1"),
        user_id="jy", acted_at=T0, component_version="p13-1")
    assert action.routed_to == ("P10",)
    assert action.subject_ref == "plan-1"


def test_an_unapplied_user_edit_is_surfaced_rather_than_resolved(p13_conn):
    """`64` §5c and the shipped `UnappliedUserEdit`: "that is a question for the
    user, not a decision for the product"."""
    _versions(p13_conn)
    edit = UserLevelEdit(
        uses_schema="academic", role_ref="level", field_ref="subject",
        action="renamed", display_label="Class", proposed_label="Course",
        user_id="jy", recorded_at=T0, basis="user")
    view = _view(p13_conn, unapplied=(UnappliedUserEdit(
        edit, "re-templated",
        "you renamed 'level' to 'Class'; this release resolves it to another "
        "field"),))
    assert len(view.unapplied_user_edits) == 1
    assert view.unapplied_user_edits[0].kind == "re-templated"
    assert view.unapplied_user_edits[0].edit.display_label == "Class"


def test_the_three_missing_diff_dimensions_are_reported_not_faked(p13_conn):
    """`66` §17 asks for six. Three have no producer anywhere in src/."""
    _versions(p13_conn)
    view = _view(p13_conn)
    assert view.schemas_activated_or_deactivated is None
    assert view.protected_area_changes is None
    assert view.filing_policies_paused is None
    assert len(view.producer_gap_notes) == 3
    joined = " ".join(view.producer_gap_notes)
    assert "schema" in joined
    assert "protected area" in joined
    assert "filing policy" in joined


def test_a_gesture_outside_the_three_named_actions_is_refused(p13_conn):
    _versions(p13_conn)
    with pytest.raises(NothingIsAdoptedSilently):
        collect_version_action(
            p13_conn, _view(p13_conn), "accept", action_id="a-x",
            plan_version="plan-2", session_id="s-1", correction_scope="corpus",
            presented_state_ref=_ref(p13_conn, "plan-2"), user_id="jy",
            acted_at=T0, component_version="p13-1")
