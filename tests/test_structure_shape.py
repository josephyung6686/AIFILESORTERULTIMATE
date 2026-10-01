"""The proposed outline collapses obvious duplicates before it is written out.

A plain scan keeps CourseWorks and Finder names as top-level peers. These tests
are the cases a person would fix by hand: Finder copies, `_export` titles,
same-subject siblings, same-stem exports that are different courses, and empty
names sitting beside a folder that actually holds files.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import cli
from structure_shape import shape_proposed_tree
from tree_design.records import ExpectedValue, Node


def _node(node_id, label, *, parent=None, expected=(), node_type="existing"):
    return Node(
        node_id=node_id, plan_version_id="plan-1", node_type=node_type,
        display_label=label, parent_node_id=parent, root_anchor="downloads",
        ordinal=0, associated_group_ids=(),
        explanation="Adopted from the scanned folder.",
        node_role="ordinary", accepts_placement=node_type != "protected",
        handling_class="personal_non_sensitive", origin_node_id=node_id,
        expected_values=tuple(ExpectedValue(field, value)
                              for field, value in expected),
        existing_path=f"/downloads/{label}" if node_type == "existing" else None,
        protected_movement_permitted=False)


def _ids(nodes):
    return {node.node_id for node in nodes}


def _by_id(nodes):
    return {node.node_id: node for node in nodes}


def _tops(nodes):
    return [node for node in nodes if node.parent_node_id is None]


def _ancestor_labels(nodes, node_id):
    by_id = _by_id(nodes)
    labels = []
    seen = set()
    current = by_id[node_id].parent_node_id
    while current and current not in seen:
        seen.add(current)
        labels.append(by_id[current].display_label)
        current = by_id[current].parent_node_id
    return labels


def test_finder_copy_suffixes_collapse_and_empty_copies_leave_the_top_level():
    """`Class_notes_export`, `(1)`…`(5)`, and bare `Class notes` are one empty.

    The real notes already live under the course. The copies are not peers of it.
    """
    copies = [
        _node("n_export", "Class_notes_export"),
        *[_node(f"n_copy_{index}", f"Class_notes_export ({index})")
          for index in range(1, 6)],
        _node("n_bare", "Class notes"),
    ]
    course = _node("n_course", "IEOR3658", expected=(("subject", "IEOR3658"),))
    nested = _node("n_real", "Class notes", parent="n_course",
                   expected=(("subject", "IEOR3658"), ("work_type", "notes")))
    shaped = shape_proposed_tree(
        [*copies, course, nested], holds={"n_course": ["a"], "n_real": ["b"]})
    tops = {node.display_label for node in _tops(shaped)}
    assert "IEOR3658" in tops
    assert "Class notes" not in tops
    assert "Class_notes_export" not in tops
    for index in range(1, 6):
        assert f"Class_notes_export ({index})" not in tops
    kept = [node for node in shaped
            if node.display_label in {"Class notes", "Class_notes"}
            and node.node_id != "n_real"]
    assert len(kept) == 1
    assert kept[0].node_id == "n_bare"
    assert kept[0].parent_node_id is not None
    parent = _by_id(shaped)[kept[0].parent_node_id]
    assert parent.display_label == "99 Archive"
    assert _by_id(shaped)["n_real"].parent_node_id == "n_course"
    assert _by_id(shaped)["n_real"].display_label == "Class notes"
    dropped = {f"n_copy_{index}" for index in range(1, 6)} | {"n_export"}
    assert dropped.isdisjoint(_ids(shaped))


def test_the_nonempty_finder_copy_is_the_one_that_survives():
    """`starter` is empty and `starter 2` holds the files. One folder remains."""
    shaped = shape_proposed_tree((
        _node("n_empty", "starter"),
        _node("n_full", "starter 2"),
    ), holds={"n_full": ["notes.txt"]})
    assert _ids(shaped) == {"n_full"}
    survivor = shaped[0]
    assert survivor.display_label == "starter"
    assert survivor.parent_node_id is None
    assert survivor.node_id == "n_full"


def test_export_suffixes_are_stripped_from_display_names_only():
    """`_export` and `__export` are CourseWorks noise, not a second identity."""
    shaped = shape_proposed_tree((
        _node("n_files", "course_files_export"),
        _node("n_readings", "readings__export"),
    ), holds={"n_files": ["a"], "n_readings": ["b"]})
    by_id = _by_id(shaped)
    assert by_id["n_files"].display_label == "course_files"
    assert by_id["n_readings"].display_label == "readings"
    assert by_id["n_files"].node_id == "n_files"
    assert by_id["n_files"].origin_node_id == "n_files"
    assert by_id["n_files"].parent_node_id is None
    assert by_id["n_readings"].parent_node_id is None


def test_same_subject_peers_nest_under_subject_then_term_then_work_type():
    """IEOR3658 split across finder names becomes one course, then term, then kind."""
    lectures = _node(
        "n_lec", "IEOR3658_lectures_export",
        expected=(("subject", "IEOR3658"), ("term", "2025-Spring"),
                  ("work_type", "lecture")))
    homework = _node(
        "n_hw", "problem_sets_export",
        expected=(("subject", "IEOR3658"), ("term", "2025-Spring"),
                  ("work_type", "problem set")))
    notes = _node(
        "n_notes", "week1",
        expected=(("subject", "IEOR3658"), ("term", "2025-Fall"),
                  ("work_type", "notes")))
    taxes = _node("n_tax", "Taxes")
    shaped = shape_proposed_tree(
        (lectures, homework, notes, taxes),
        holds={"n_lec": ["a"], "n_hw": ["b"], "n_notes": ["c"], "n_tax": ["d"]})
    tops = {node.display_label for node in _tops(shaped)}
    assert tops == {"Academic", "Taxes"}
    by_id = _by_id(shaped)
    assert by_id["n_lec"].display_label == "lecture"
    assert by_id["n_hw"].display_label == "problem set"
    assert by_id["n_notes"].display_label == "notes"
    for node_id, term in (("n_lec", "2025-Spring"), ("n_hw", "2025-Spring"),
                          ("n_notes", "2025-Fall")):
        ancestors = _ancestor_labels(shaped, node_id)
        assert ancestors == [term, "IEOR3658", "Academic"]
    assert by_id["n_lec"].node_id == "n_lec"
    assert by_id["n_hw"].origin_node_id == "n_hw"


def test_same_stem_exports_with_different_subjects_stay_separate():
    """`course_files_export (4)` is not `(5)` when the subjects differ.

    Each keeps its own course code under Academic. They are not one
    `course_files` folder.
    """
    ieor = _node(
        "n4", "course_files_export (4)",
        expected=(("subject", "IEOR3658"), ("term", "2025-Spring"),
                  ("work_type", "syllabus")))
    coms = _node(
        "n5", "course_files_export (5)",
        expected=(("subject", "COMS4701"), ("term", "2025-Spring"),
                  ("work_type", "lecture")))
    chen = _node(
        "n3", "course_files_export (3)",
        expected=(("subject", "CHEN E3020"),))
    shaped = shape_proposed_tree(
        (ieor, coms, chen),
        holds={"n4": ["a"], "n5": ["b"], "n3": ["c"]})
    labels = {node.display_label for node in shaped}
    assert "course_files" not in labels
    assert "course_files_export" not in labels
    assert "course_files_export (4)" not in labels
    by_id = _by_id(shaped)
    assert {"n4", "n5", "n3"} <= _ids(shaped)
    assert "IEOR3658" in _ancestor_labels(shaped, "n4")
    assert "COMS4701" not in _ancestor_labels(shaped, "n4")
    assert "COMS4701" in _ancestor_labels(shaped, "n5")
    assert "IEOR3658" not in _ancestor_labels(shaped, "n5")
    assert "Academic" in _ancestor_labels(shaped, "n4")
    assert "Academic" in _ancestor_labels(shaped, "n5")
    assert by_id["n3"].display_label == "CHEN E3020"
    assert by_id["n3"].parent_node_id is not None
    assert by_id[by_id["n3"].parent_node_id].display_label == "Academic"
    assert by_id["n4"].display_label == "syllabus"
    assert by_id["n5"].display_label == "lecture"
    assert by_id["n4"].parent_node_id != by_id["n5"].parent_node_id


def test_empty_noise_is_not_a_top_level_peer_of_a_folder_that_holds_files():
    """`files`, `0718` and `starter` copies are noise. Review and Archive stay."""
    noise = [
        _node("n_files", "files"),
        _node("n_files_1", "files (1)"),
        _node("n_files_2", "files 2"),
        _node("n_0718", "0718"),
        _node("n_0718_1", "0718(1)"),
        _node("n_starter", "starter"),
        _node("n_starter_2", "starter 2"),
    ]
    lectures = _node("n_lec", "Lectures")
    archive = _node("n_arch", "99 Archive")
    review = _node("n_rev", "98 Review and Unsorted")
    shaped = shape_proposed_tree(
        [*noise, lectures, archive, review], holds={"n_lec": ["a.pdf"]})
    tops = {node.display_label for node in _tops(shaped)}
    assert "Lectures" in tops
    assert "99 Archive" in tops
    assert "98 Review and Unsorted" in tops
    for label in ("files", "files (1)", "files 2", "0718", "0718(1)",
                  "starter", "starter 2"):
        assert label not in tops
    by_id = _by_id(shaped)
    assert by_id["n_arch"].parent_node_id is None
    assert by_id["n_rev"].parent_node_id is None
    for node_id in ("n_files", "n_0718", "n_starter"):
        assert by_id[node_id].parent_node_id == "n_arch"
    assert "n_files_1" not in by_id
    assert "n_files_2" not in by_id
    assert "n_0718_1" not in by_id
    assert "n_starter_2" not in by_id


def test_an_empty_named_branch_stays_a_top_level_peer():
    """A real branch can count as empty. That is not the dump names above."""
    society = _node("n_soc", "Debate Society")
    school = _node("n_school", "Academics")
    term = _node("n_term", "2024-Fall", parent="n_school",
                 expected=(("term", "2024-Fall"), ("subject", "ENG101")))
    shaped = shape_proposed_tree(
        (society, school, term), holds={})
    by_id = _by_id(shaped)
    assert by_id["n_soc"].parent_node_id is None
    assert by_id["n_soc"].display_label == "Debate Society"
    assert by_id["n_school"].parent_node_id is None
    assert by_id["n_term"].parent_node_id == "n_school"
    assert "99 Archive" not in {node.display_label for node in shaped}


def test_a_tree_without_those_patterns_keeps_its_folders():
    """Nothing here is a copy, an export, or a shared subject."""
    root = _node("n_tax", "Taxes")
    child = _node("n_year", "2024", parent="n_tax")
    shaped = shape_proposed_tree(
        (root, child), holds={"n_tax": ["a"], "n_year": ["b"]})
    assert [(node.node_id, node.display_label, node.parent_node_id)
            for node in shaped] == [
                ("n_tax", "Taxes", None),
                ("n_year", "2024", "n_tax"),
            ]


def test_the_outline_does_not_list_finder_copies_as_top_level_peers():
    """`--structure-out` walks the shaped tree, not the scan's own names."""
    nodes = (
        _node("n_export", "Class_notes_export"),
        _node("n_copy", "Class_notes_export (1)"),
        _node("n_bare", "Class notes"),
        _node("n_lec", "Lectures"),
    )
    rows = cli.structure_rows(
        SimpleNamespace(
            tree=SimpleNamespace(tree=SimpleNamespace(nodes=nodes)),
            placement=SimpleNamespace(decisions=())),
        situations={}, words_of=lambda _situation: "",
        holds={"n_lec": ["f1"]})
    top = [row.label for row in rows if row.depth == 0]
    assert "Lectures" in top
    assert "Class_notes_export" not in top
    assert "Class_notes_export (1)" not in top
    assert "Class notes" not in top


def test_a_copy_with_a_subject_is_not_merged_into_a_copy_that_has_none():
    """Same stem is not enough when one export has a subject and the other does not."""
    named = _node("n_named", "course_files_export (4)",
                  expected=(("subject", "IEOR3658"),))
    unnamed = _node("n_plain", "course_files_export (5)")
    shaped = shape_proposed_tree(
        (named, unnamed), holds={"n_named": ["a"], "n_plain": ["b"]})
    by_id = _by_id(shaped)
    assert "n_named" in by_id and "n_plain" in by_id
    assert by_id["n_named"].node_id != by_id["n_plain"].parent_node_id
    assert by_id["n_plain"].node_id != by_id["n_named"].parent_node_id
    assert by_id["n_named"].display_label == "IEOR3658"
    assert by_id["n_plain"].display_label == "course_files"
