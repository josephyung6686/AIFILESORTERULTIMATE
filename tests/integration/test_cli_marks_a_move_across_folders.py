"""`104` R-N: the proposal screen applies the rule freeze enforces.

A file on the person's Desktop was offered a home under their Downloads with
`--may-cross-folders` off. Nothing unsafe happened -- `mutation/resolution.py`
refuses the move with `cross_root_refused` when the freeze reaches it -- but the
screen showed a move the plan will not make, beside moves it will, with nothing
telling the two apart. `00`:20 makes crossing a high-level folder the person's
own third choice, and a proposal that quietly ignores their answer is a proposal
they cannot act on.

The predicate is P12's own, imported rather than re-derived: two answers to "does
this move cross a high-level folder" is one too many, and the screen's copy would
be the one that drifts.
"""
from __future__ import annotations

import io
from pathlib import Path

import cli

SITUATION = "academic.coursework"
LABEL = "Coursework"


def _corpus(root: Path) -> tuple[Path, Path]:
    """A Downloads with a course in it, and a Desktop with one more of its files."""
    downloads = root / "holder" / "Downloads"
    desktop = root / "holder" / "Desktop"
    downloads.mkdir(parents=True)
    desktop.mkdir(parents=True)
    (downloads / "PHYS1401 Syllabus Spring 2026.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (downloads / "PHYS1401 Problem Set 1.txt").write_text(
        "PHYS 1401 Problem Set 1\nSpring 2026\nProblem 1. A ball is thrown.\n")
    (downloads / "PHYS1401 Problem Set 2.txt").write_text(
        "PHYS 1401 Problem Set 2\nSpring 2026\nProblem 1. A block slides.\n")
    (desktop / "PHYS1401 Problem Set 4.txt").write_text(
        "PHYS 1401 Problem Set 4\nSpring 2026\nProblem 1. A spring oscillates.\n")
    return downloads, desktop


def _run(downloads: Path, desktop: Path, database: Path,
         *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(downloads), "--situation", SITUATION, "--label", LABEL,
                     "--user", "jy", "--also-read", str(desktop),
                     "--database", str(database), *extra], out=out)
    return code, out.getvalue()


def test_a_move_across_folders_is_marked_as_needing_the_permission(tmp_path):
    downloads, desktop = _corpus(tmp_path)
    code, report = _run(downloads, desktop, tmp_path / "holder" / "plan.sqlite")

    assert code == 0, report
    assert "PHYS1401 Problem Set 4.txt" in report, report
    flat = " ".join(report.split())
    assert "--may-cross-folders" in flat, report
    # And it says WHICH folder the file is in now, because "across folders" is
    # not a fact a person can check without both ends of the move.
    assert "Desktop" in flat, report


def test_the_permission_the_person_gave_is_not_asked_for_twice(tmp_path):
    """With `--may-cross-folders` typed, the mark is gone: the move is legal."""
    downloads, desktop = _corpus(tmp_path)
    _, report = _run(downloads, desktop, tmp_path / "holder" / "plan.sqlite",
                     "--may-cross-folders")

    assert "PHYS1401 Problem Set 4.txt" in report, report
    assert "--may-cross-folders" not in report, report


def test_a_file_inside_the_scanned_folder_is_never_marked(tmp_path):
    """The negative twin: the mark fires on crossing and on nothing else."""
    downloads, desktop = _corpus(tmp_path)
    _, report = _run(downloads, desktop, tmp_path / "holder" / "plan.sqlite")

    # `Problem Set 1` is in the scanned folder and, before this fix, shared a
    # group and a heading with the Desktop file. A mark keyed on the DESTINATION
    # rather than on the file would still catch it.
    body = report.split("\nFiles:", 1)[1]
    groups = body.split("\n\n")
    inside = [group for group in groups if "PHYS1401 Problem Set 1.txt" in group]
    assert inside, report
    for group in inside:
        assert "--may-cross-folders" not in group, report
        assert "PHYS1401 Problem Set 4.txt" not in group, (
            "the Desktop file and the Downloads file are still one offer")
