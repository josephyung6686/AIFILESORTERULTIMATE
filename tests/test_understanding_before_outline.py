"""Understanding seats files before the outline is written.

A plan-only scan used to place what the rules could, write the outline, and
only then ask the model. The names that came back stayed in the cache. These
tests are the outline this path writes once those answers exist, and the
folder rules that go with it: a directory is empty only when it has no files
on disk, one course is one home, and review is not zero while files abstained.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli
from empty_directories import apply_empty_removal
from structure_shape import course_key, shape_proposed_tree
from tree_design.records import ExpectedValue, Node
from understanding.answer import Understanding
from understanding.into_placement import seat_unplaced


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


def _understood(file_id, *, life_area="Academic", course="COMS4701",
                term="2025-Spring", confidence=0.91, needs_review=False):
    return Understanding(
        file_id=file_id, kind="homework", life_area=life_area, course=course,
        term=term, company=None, project=None, concerns="user",
        confidence=confidence, evidence_quote="COMS 4701 homework 3",
        needs_review=needs_review,
        reason="" if not needs_review else "needs review")


def _abstained(file_id):
    return SimpleNamespace(
        outcome="abstain", destination=None,
        subject=SimpleNamespace(file_id=file_id, member_file_ids=()))


def _rows(nodes, *, holds, on_disk=None, declared=(), review_ids=(),
          extra_nodes=()):
    return cli.structure_rows(
        SimpleNamespace(
            tree=SimpleNamespace(tree=SimpleNamespace(nodes=tuple(nodes))),
            placement=SimpleNamespace(decisions=())),
        situations={}, words_of=lambda _situation: "",
        holds=holds, on_disk=on_disk, declared_courses=declared,
        review_ids=review_ids, extra_nodes=extra_nodes)


def _row(rows, label):
    found = [row for row in rows if row.label == label]
    assert found, labels_of(rows)
    return found[0]


def labels_of(rows):
    return [(row.depth, row.label, row.words) for row in rows]


def test_outline_file_counts_files_the_rules_left_unplaced(tmp_path):
    """Rules placed nothing. Understanding names a course and a review file.

    The outline file this path writes counts both. The course line is not the
    zero the pre-understand placement would have printed.
    """
    course = _node("course", "COMS4701",
                   expected=(("subject", "COMS4701"),))
    review = _node("review", "98 Review and Unsorted")
    nodes = (course, review)
    before = _rows(nodes, holds={})
    assert "0 files" in _row(before, "COMS4701").words

    seating = seat_unplaced(
        nodes, placement_holds={},
        decisions=(_abstained("f-placed"), _abstained("f-review")),
        understandings={
            "f-placed": _understood("f-placed"),
            "f-review": _understood(
                "f-review", life_area="needs_review", course=None,
                needs_review=True, confidence=0.2),
        })
    after = _rows(
        nodes, holds=seating.holds, review_ids=seating.review_ids,
        extra_nodes=seating.extra_nodes)
    placed_before = sum(len(ids) for ids in {}.values())
    placed_after = sum(len(ids) for ids in seating.holds.values())
    placed_after += len(seating.review_ids)
    assert placed_after > placed_before
    assert "1 file" in _row(after, "COMS4701").words
    assert "0 files" not in _row(after, "98 Review and Unsorted").words
    assert "1 file" in _row(after, "98 Review and Unsorted").words

    path = tmp_path / "proposed-structure.txt"
    path.write_text(
        cli.structure_render(
            after, path=str(path), plan="plan-1"),
        encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    assert "COMS4701" in text
    assert "1 file" in text
    assert "98 Review and Unsorted" in text


def test_proposal_outline_uses_understanding_before_the_file_is_the_picture(tmp_path):
    """The helper the scan uses to build the outline seats understanding first."""
    course = _node("course", "COMS4701",
                   expected=(("subject", "COMS4701"),))
    review = _node("review", "98 Review and Unsorted")
    nodes = (course, review)
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE files (file_id TEXT, current_path TEXT)")
    result = SimpleNamespace(
        placement=SimpleNamespace(decisions=(
            _abstained("f-placed"), _abstained("f-held"))),
        tree=SimpleNamespace(tree=SimpleNamespace(nodes=nodes)))
    rows = cli._proposal_outline(
        result, conn, situations={},
        understandings={
            "f-placed": _understood("f-placed"),
            "f-held": _understood(
                "f-held", needs_review=True, life_area="needs_review",
                course=None, confidence=0.1),
        })
    path = tmp_path / "proposed-structure.txt"
    path.write_text(cli.structure_render(rows, path=str(path), plan="plan-1"),
                    encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    assert "1 file" in _row(rows, "COMS4701").words
    review_words = _row(rows, "98 Review and Unsorted").words
    assert "0 files" not in review_words
    assert "1 file" in text


def test_review_line_is_not_zero_when_files_abstained():
    """1712 abstentions printed as 0 because only placements were counted."""
    review = _node("review", "98 Review and Unsorted")
    lectures = _node("lec", "Lectures")
    seating = seat_unplaced(
        (lectures, review), placement_holds={"lec": ["placed.pdf"]},
        decisions=tuple(_abstained(f"a{index}") for index in range(4)),
        understandings={})
    rows = _rows(
        (lectures, review), holds=seating.holds,
        review_ids=seating.review_ids)
    words = _row(rows, "98 Review and Unsorted").words
    assert "0 files" not in words
    assert words.startswith("4 files")


def test_a_directory_with_files_and_zero_placements_is_kept(tmp_path):
    """Week-4 export, 0 placed, 5 files on disk: not Archive, not a removal."""
    week = _node("week", "week4_export")
    lectures = _node("lec", "Lectures")
    on_disk = {"week": ["a", "b", "c", "d", "e"]}
    shaped = shape_proposed_tree(
        (week, lectures), holds={"lec": ["placed.pdf"]}, on_disk=on_disk)
    by_id = _by_id(shaped)
    assert by_id["week"].parent_node_id is None
    assert by_id["week"].display_label == "week4"
    archive = [node for node in shaped if node.display_label == "99 Archive"]
    if archive:
        assert by_id["week"].parent_node_id != archive[0].node_id
    rows = _rows(
        (week, lectures), holds={"lec": ["placed.pdf"]}, on_disk=on_disk)
    week_row = _row(rows, "week4")
    assert week_row.depth == 0
    assert "0 files" not in week_row.words
    assert "5 files in this folder" in week_row.words

    root = tmp_path / "corpus"
    (root / "week4_export").mkdir(parents=True)
    (root / "week4_export" / "notes.pdf").write_bytes(b"x")
    (root / "vacant").mkdir()
    message, removed = apply_empty_removal(root, confirm="yes")
    assert "week4_export" not in message
    assert (root / "week4_export" / "notes.pdf").exists()
    assert removed == () or all("week4_export" not in str(path) for path in removed)


def test_empty_directory_is_listed_and_removed_only_when_confirmed(tmp_path):
    root = tmp_path / "corpus"
    vacant = root / "vacant"
    nested = vacant / "also-empty"
    nested.mkdir(parents=True)
    kept = root / "week4_export"
    kept.mkdir()
    (kept / "notes.pdf").write_bytes(b"x")

    message, removed = apply_empty_removal(root, confirm="no")
    assert str(vacant) in message
    assert "week4_export" not in message
    assert removed == ()
    assert vacant.exists()
    assert nested.exists()
    assert (kept / "notes.pdf").exists()

    message, removed = apply_empty_removal(root, confirm="yes")
    assert vacant.resolve() in {path.resolve() for path in removed} or not vacant.exists()
    assert not vacant.exists()
    assert not nested.exists()
    assert (kept / "notes.pdf").exists()
    assert "week4_export" not in message


def test_remove_empty_is_an_explicit_cli_flag(capsys):
    with pytest.raises(SystemExit) as caught:
        cli.main(["--help"])
    assert caught.value.code == 0
    assert "--remove-empty" in capsys.readouterr().out


def test_the_same_course_is_not_several_peer_homes():
    """COMS4701 was a top-level homework folder, a recitation, and Academic/COMS4701."""
    academic = _node("ac", "Academic")
    course = _node("course", "COMS4701", parent="ac",
                   expected=(("subject", "COMS4701"),))
    homework = _node(
        "hw", "conceptual homework",
        expected=(("subject", "COMS 4701"), ("work_type", "homework")))
    recitation = _node(
        "rec", "recitation",
        expected=(("subject", "COMS4701"), ("work_type", "recitation")))
    shaped = shape_proposed_tree(
        (academic, course, homework, recitation),
        holds={"hw": ["a"], "rec": ["b"], "course": ["c"]})
    by_id = _by_id(shaped)
    assert by_id["hw"].parent_node_id is not None
    assert by_id["rec"].parent_node_id is not None
    assert "COMS4701" in _ancestor_labels(shaped, "hw")
    assert "COMS4701" in _ancestor_labels(shaped, "rec")
    homes = [
        node for node in shaped
        if course_key(node.display_label) == course_key("COMS4701")
        and (node.parent_node_id is None
             or by_id[node.parent_node_id].display_label == "Academic")]
    assert len(homes) == 1
    top_labels = {node.display_label for node in _tops(shaped)}
    assert "conceptual homework" not in top_labels
    assert "recitation" not in top_labels


def test_course_codes_that_differ_only_by_spacing_are_one_home():
    spaced = _node("spaced", "CHEN 2100",
                   expected=(("subject", "CHEN 2100"),))
    tight = _node("tight", "CHEN2100",
                  expected=(("subject", "CHEN2100"),))
    shaped = shape_proposed_tree(
        (spaced, tight),
        holds={"spaced": ["a"], "tight": ["b"]},
        on_disk={"spaced": ["a"], "tight": ["b"]},
        declared_courses=("CHEN 2100",))
    by_id = _by_id(shaped)
    homes = [
        node for node in shaped
        if course_key(node.display_label) == course_key("CHEN2100")
        and (node.parent_node_id is None
             or by_id[node.parent_node_id].display_label == "Academic")]
    assert len(homes) == 1
    peer_tops = [
        node for node in _tops(shaped)
        if course_key(node.display_label) == course_key("CHEN2100")]
    assert len(peer_tops) <= 1


def test_a_declared_course_leaf_is_not_parked_as_empty_noise():
    """An export leaf whose name is the course stays, even with nothing placed."""
    leaf = _node("leaf", "COMS4701_export")
    shaped = shape_proposed_tree(
        (leaf,), holds={}, on_disk={}, declared_courses=("COMS 4701",))
    by_id = _by_id(shaped)
    assert "leaf" in by_id
    assert by_id["leaf"].parent_node_id is None
    assert "99 Archive" not in {node.display_label for node in shaped}


def test_finder_suffixes_still_collapse_without_splitting_two_courses():
    ieor = _node(
        "ieor", "course_files_export (4)",
        expected=(("subject", "IEOR3658"), ("work_type", "syllabus")))
    coms = _node(
        "coms", "course_files_export (5)",
        expected=(("subject", "COMS4701"), ("work_type", "lecture")))
    shaped = shape_proposed_tree(
        (ieor, coms), holds={"ieor": ["a"], "coms": ["b"]})
    by_id = _by_id(shaped)
    assert course_key("IEOR3658") != course_key("COMS4701")
    assert "IEOR3658" in _ancestor_labels(shaped, "ieor")
    assert "COMS4701" in _ancestor_labels(shaped, "coms")
    assert by_id["ieor"].parent_node_id != by_id["coms"].parent_node_id
    assert "course_files_export (4)" not in {node.display_label for node in shaped}
