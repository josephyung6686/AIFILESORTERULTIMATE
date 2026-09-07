"""`104` R-87. A folder somebody dropped one file into is not a destination profile.

The walkthrough, in the person's words: they had a folder called `old stuff`
holding a single PHYS1401 problem set. The run read that one file, decided the
folder "expects subject = PHYS1401, work_type = problem set", and the next
problem set they saved was ready to file into `old stuff` -- ahead of the
course folder the run had just proposed for exactly that material.

`upstream.settled_values_by_directory` had ruled on half of this already: "a
set of one is always unanimous", so a folder holding ONE file states nothing.
That floor counts the files in the folder. §5.11 counts a silent file as
silent -- rightly -- so a folder holding two files where only one settles the
field is still unanimous at that field on the strength of one file, and clears
a floor written about folder size.

That is the shape this corpus has and the shape the walkthrough had: `old
stuff` holds a PHYS1401 problem set and one other thing, so the folder-size
floor passes it and the field is claimed by one file.

The ruling: an adopted folder may claim an expected value from its name or from
two or more files that agree, never from one file. Q-D refinement, not removal
-- the folder is still in the tree, still the person's, still reachable by its
name; what it loses is a claim about its contents that its contents made once.

The unit half is in `tests/p10/test_p10_existing_folders.py`. This is the
walkthrough itself, end to end on a corpus small enough to read.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import cli

SITUATION = "academic.coursework"
LABEL = "Coursework"
NEW_FILE = "PHYS1401 Problem Set 4.txt"
ADOPTED = "old stuff"


def _corpus(tmp_path: Path) -> Path:
    """One folder the person made, one problem set in it, and a course around it.

    `old stuff` is the folder somebody drops things into rather than one they
    built for a course: a PHYS1401 problem set and a shopping list. Two files,
    so the folder-size floor passes it, and exactly ONE of them says what kind
    of thing it is -- which is the claim the ruling refuses.

    The three files beside it are what gives the run a real course to propose,
    so that "not `old stuff`" is a choice between two destinations rather than
    the absence of one.
    """
    root = tmp_path / "Documents"
    if root.is_dir():
        return root
    (root / ADOPTED).mkdir(parents=True)
    (root / ADOPTED / "PHYS1401 Problem Set 1.txt").write_text(
        "PHYS 1401 Problem Set 1\nSpring 2026\nProblem 1. A ball is thrown.\n")
    (root / ADOPTED / "scratch.txt").write_text("Remember to buy milk.\n")
    (root / "PHYS1401 Syllabus Spring 2026.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    for index in (2, 3):
        (root / f"PHYS1401 Problem Set {index}.txt").write_text(
            f"PHYS 1401 Problem Set {index}\nSpring 2026\n"
            "Problem 1. A block slides.\n")
    (root / NEW_FILE).write_text(
        "PHYS 1401 Problem Set 4\nSpring 2026\n"
        "Problem 1. A spring oscillates.\n")
    return root


def _run(tmp_path: Path, database: Path) -> str:
    out = io.StringIO()
    code = cli.main([str(_corpus(tmp_path)), "--situation", SITUATION,
                     "--label", LABEL, "--user", "jy",
                     "--database", str(database)], out=out)
    printed = out.getvalue()
    assert code == 0, printed
    return printed


def _open(database: Path):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def _adopted_node(database: Path):
    """The node `old stuff` became, or `None` if the run never adopted it."""
    conn = _open(database)
    try:
        for row in conn.execute(
                "SELECT node_id, display_label, existing_path FROM tree_nodes"):
            if row["existing_path"] and Path(row["existing_path"]).name == ADOPTED:
                return dict(row)
    finally:
        conn.close()
    return None


def _expected_values(database: Path, node_id: str) -> set[tuple[str, str]]:
    conn = _open(database)
    try:
        return {(row["field_key"], row["value"]) for row in conn.execute(
            "SELECT field_key, value FROM node_expected_values "
            "WHERE node_id = ?", (node_id,))}
    finally:
        conn.close()


def _destination_of(database: Path, filename: str) -> str | None:
    conn = _open(database)
    try:
        names = {row["file_id"]: row["filename"]
                 for row in conn.execute("SELECT file_id, filename FROM files")}
        wanted = next((file_id for file_id, name in names.items()
                       if name == filename), None)
        for row in conn.execute("SELECT payload FROM placement_decisions "
                                "WHERE superseded_by IS NULL"):
            decision = json.loads(row["payload"])
            if decision["subject"].get("file_id") != wanted:
                continue
            destination = decision.get("destination")
            return None if destination is None else destination["node_id"]
    finally:
        conn.close()
    return None


def test_the_folder_claims_nothing_from_the_one_file_that_spoke(tmp_path):
    """The defect, stated as the property that fixes it.

    `old stuff` is still in the tree and still the person's folder, carrying its
    real path. What it no longer says is that it expects problem sets, on the
    evidence of the one problem set somebody left in it beside a shopping list.
    """
    database = tmp_path / "plan.sqlite"
    printed = _run(tmp_path, database)

    node = _adopted_node(database)
    assert node is not None, (
        f"this run adopted no folder called {ADOPTED!r}, so the test is "
        f"measuring nothing:\n{printed}")
    claimed = _expected_values(database, node["node_id"])
    assert claimed == set(), (
        f"{ADOPTED!r} claims {sorted(claimed)}, and one file said it")


def test_the_new_problem_set_reaches_the_course_folder(tmp_path):
    """The walkthrough, which is what the claim was costing.

    A claim read off one file scores exactly like a claim read off twenty, so
    `old stuff` and the course folder the same run had just proposed fit the new
    problem set equally well -- and a file with two homes and nothing to
    separate them is a file that does not move. Measured on this corpus before
    the ruling: `old stuff` expected `work_type = problem set`, and problem sets
    2, 3 and 4 all abstained between the two folders.

    So the property is not only "not `old stuff`". It is that the file is
    PLACED, in the folder the course produced.
    """
    database = tmp_path / "plan.sqlite"
    printed = _run(tmp_path, database)

    node = _adopted_node(database)
    assert node is not None, printed
    where = _destination_of(database, NEW_FILE)
    assert where is not None, (
        f"{NEW_FILE} was not placed at all: the person's scratch folder and the "
        f"course folder fit it equally well and nothing separated them:\n"
        f"{printed}")
    assert where != node["node_id"], (
        f"{NEW_FILE} is still ready to file into {ADOPTED!r}, on the strength "
        f"of the one file in it that said anything:\n{printed}")
