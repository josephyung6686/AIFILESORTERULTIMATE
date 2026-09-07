"""A file is offered the groups IT is in, and never the run's whole accepted set.

`104` R-11, and `104` §11.1's `exp1` row measured as a test rather than as a run.

**The defect.** `cli.run.evidence_for` returned `group_ids=tuple(accepted_ids)` --
every group the run had accepted, handed to every file in the corpus. So
`placement.retrieval.retrieve`'s `ACCEPTED_GROUP` channel fired for a file that
belonged to nothing: it reached the branch some OTHER file's group had built, and
scored on membership it did not have. `00`:107 is explicit that "accepted group
membership should retrieve the branch that was created from that group" -- from
THAT group, the file's own.

**What the measurement said, and why the fix is still right.** `exp1` removed the
fabricated credit on the owner's 199 files: not placed went 32 -> 35, `wrong` stayed
0 and spillover stayed 11. So R-11 is not the cause of the regression `104` §11 is
about -- but three files were being placed on evidence that did not exist, and the
direction of the correction is exactly that: the placements it removes are the ones
nothing supported, and it moves NOT PLACED, never WRONG. That direction is what this
file asserts, on a corpus a test can carry.

The corpus is one coherent course plus one document that shares nothing with it.
Before the fix the stranger was offered the course group's id; after it, `()`.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: Three files that agree on one course, and one that has nothing to do with them.
#: The stranger names no course, no term and no instructor, sits in its own folder,
#: and shares no validated fact with the other three.
A_COURSE_AND_A_STRANGER = {
    "Uni/PHYS 1401 syllabus.txt":
        "PHYS 1401 - Introduction to Mechanics\nFall 2024 Syllabus\n\n"
        "Instructor: Professor R. Villanueva\n"
        "Office hours: Wednesday 3:00-5:00 p.m.\nCredits: 3\n\n"
        "COURSE DESCRIPTION\n"
        "Kinematics, Newton's laws, work and energy, momentum.\n\nGRADING\n"
        "Problem sets 30%. Midterm 30%. Final examination 40%.\n"
        "Readings are assigned from the course textbook each week.\n",
    "Uni/PHYS 1401 lecture 08.txt":
        "PHYS 1401 - Lecture 08: Work and Energy\nFall 2024\n"
        "Professor R. Villanueva\n\n"
        "Lecture notes for the eighth meeting of the course.\n"
        "The work-energy theorem relates the net work to the change in kinetic "
        "energy.\n"
        "Worked examples are drawn from the assigned reading for this seminar.\n",
    "Uni/PHYS 1401 problem set 3.txt":
        "PHYS 1401 - Problem Set 3\nFall 2024\n"
        "Due: Thursday October 17, 2024 at the start of lecture\n"
        "Professor R. Villanueva\n\n"
        "1. A block of mass 2.0 kg slides down a frictionless incline.\n"
        "2. Derive the work-energy theorem for a constant force.\n"
        "This assignment is graded coursework for the course.\n",
    "Kitchen/soup.txt":
        "Leek and potato soup\n\n"
        "Sweat three leeks in butter until soft. Add four potatoes, peeled and "
        "diced, and a litre of stock.\n"
        "Simmer for twenty minutes. Blend until smooth, season, and finish with "
        "cream.\n"
        "Serves four. Keeps three days in the refrigerator.\n",
}


def _corpus(tmp_path: Path, files: dict[str, str]) -> Path:
    """Under `holder/corpus`: `84` §4's warning is that a directory name ABOVE the
    corpus root once changed classification, and `tmp_path` carries the test's."""
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in files.items():
        path = corpus / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    return corpus


def _run(corpus: Path, label: str, *extra: str) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", label, "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"), *extra], out=out)
    return out.getvalue()


def _open(corpus: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{corpus.parent / 'plan.sqlite'}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _file_id(conn: sqlite3.Connection, name: str) -> str:
    row = conn.execute("SELECT file_id FROM files WHERE filename = ?",
                       (name,)).fetchone()
    assert row is not None, f"{name} was never indexed"
    return row["file_id"]


def _decision(conn: sqlite3.Connection, file_id: str) -> dict:
    row = conn.execute(
        "SELECT payload FROM placement_decisions WHERE subject_ref LIKE ? "
        "AND superseded_by IS NULL ORDER BY rowid DESC LIMIT 1",
        (f"%{file_id}%",)).fetchone()
    assert row is not None, f"no placement decision for {file_id}"
    return json.loads(row["payload"])


def _premise(conn: sqlite3.Connection) -> tuple[set[str], str]:
    """The corpus really did accept a group, and the stranger really is outside it.

    Without this the assertions below would pass on a corpus that simply grouped
    nothing, which is not what is being tested.
    """
    accepted = {row["group_id"] for row in conn.execute(
        "SELECT DISTINCT group_id FROM group_acceptance "
        "WHERE acceptance = 'accepted'")}
    assert accepted, "the corpus produced no accepted group to be credited with"
    stranger = _file_id(conn, "soup.txt")
    mine = {row["group_id"] for row in conn.execute(
        "SELECT group_id FROM memberships WHERE file_id = ? "
        "AND superseded_by IS NULL AND decision = 'included'", (stranger,))}
    assert not mine & accepted, (
        "the stranger joined an accepted group; pick a file that shares less")
    return accepted, stranger


def test_a_file_in_no_accepted_group_reaches_no_node_on_group_credit(tmp_path):
    """The mechanism, read off the record the run wrote.

    `alternatives` is what retrieval reached and what each candidate scored. For a
    file with no facts the tree states and no accepted membership, every channel
    must contribute nothing -- so the shortlist scores zero throughout.

    THIS IS NOT A VACUOUS ASSERTION, and it was checked by putting the defect back:
    with `group_ids=tuple(accepted_ids)` restored, this same corpus scores the
    stranger 0.286 on the course branch and hands it a shortlist of several nodes.
    The fabricated credit was worth two sevenths of the acceptance threshold to a
    recipe for leek and potato soup.
    """
    corpus = _corpus(tmp_path, A_COURSE_AND_A_STRANGER)
    _run(corpus, "PHYS 1401")

    conn = _open(corpus)
    _accepted, stranger = _premise(conn)

    decision = _decision(conn, stranger)
    scores = [one["support_score"] for one in decision["alternatives"]]
    assert scores and not any(scores), (
        f"a file in no accepted group was scored towards a destination on "
        f"{scores} -- which is the whole of R-11: `evidence_for` handed every "
        f"file the run's entire accepted set")
    assert decision["group_support"] is None


def test_the_files_that_are_in_the_group_still_carry_its_credit(tmp_path):
    """The direction that keeps the fix a correction rather than a removal.

    Offering each file its OWN memberships must not stop offering them. A version
    of this that returned `()` for everybody would pass the test above and switch
    off `00`:107's accepted-group retrieval channel entirely.
    """
    corpus = _corpus(tmp_path, A_COURSE_AND_A_STRANGER)
    _run(corpus, "PHYS 1401")

    conn = _open(corpus)
    accepted, _stranger = _premise(conn)
    members = {row["file_id"] for row in conn.execute(
        "SELECT file_id FROM memberships WHERE superseded_by IS NULL "
        "AND decision = 'included' AND group_id IN (%s)"
        % ",".join("?" * len(accepted)), tuple(sorted(accepted)))}
    assert members, "no file is in an accepted group on this corpus"

    scored = [file_id for file_id in sorted(members)
              if any(one["support_score"] > 0
                     for one in _decision(conn, file_id)["alternatives"])]
    assert len(scored) == len(members), (
        "a file in an accepted group reached no destination with any support; the "
        "channel `00`:107 names has been switched off rather than corrected")


def test_removing_fabricated_credit_moves_not_placed_and_never_wrong(tmp_path):
    """`104` §11.1's `exp1` row, as a property rather than as a number.

    The measurement on the owner's corpus was 32 -> 35 not placed, `wrong`
    unchanged at 0 and spillover unchanged at 10 -- reproduced on this branch, and
    the three placements it removed were the three scored "top folder only". What
    makes that the RIGHT direction is structural and holds on any corpus: the credit
    withdrawn is credit for a group the file is not in, so every placement it can
    remove is one that rested on nothing. It moves NOT PLACED, never WRONG.

    Here: the stranger is not filed into the course branch, and the three course
    files still are.
    """
    corpus = _corpus(tmp_path, A_COURSE_AND_A_STRANGER)
    _run(corpus, "PHYS 1401")

    conn = _open(corpus)
    _accepted, stranger = _premise(conn)
    assert _decision(conn, stranger)["outcome"] != "place", (
        "the stranger was filed; on this corpus nothing supports a destination "
        "for it")

    placed = [row["filename"] for row in conn.execute("SELECT filename FROM files")
              if row["filename"] != "soup.txt"
              and _decision(conn, _file_id(conn, row["filename"]))["outcome"]
              == "place"]
    assert len(placed) == 3, (
        f"the course files stopped being placed as well: {placed}. The correction "
        f"removes credit nobody had, and must remove nothing else")
