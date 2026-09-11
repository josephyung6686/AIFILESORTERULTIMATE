"""`104` R-113. A placement that cannot happen is still a file waiting on you.

R-115 divided the residual screen by the reason each file stopped, and pinned
the rule that makes the screen honest: every unplaced file is in exactly one
review set, because a file in none is never shown and `--send-set` is the only
gesture the screen offers.

It left a hole the shape of a decision that named a destination and could not
act on it. Two of them:

  * a file NOTHING has classified, whose placement carries
    `blocked_pending_user` -- the screen says "Would go into lecture, once you
    say what these are";
  * a move that would cross one of the person's own top-level folders with
    `--may-cross-folders` off, which `mutation/resolution.py` refuses when the
    freeze reaches it.

Both are `place` decisions. Neither reached `unplaced`, so neither was in any
review set, so `--send-set` could not address them -- and the residual review
did not reach the files the screen was naming. The ruling extends R-115's
invariant to every non-`place` decision AND every placement a policy is
holding: it joins the set of its blocking reason.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import cli
from placement import vocabulary as pv
from placement.store import decisions_for_plan

SITUATION = "academic.coursework"
LABEL = "Coursework"
AREA = "Review Later"

NO_MODEL = "A model was not allowed to look"
NOT_CLASSIFIED = "Not yet said what kind of material"
NO_CROSSING = "Not allowed to move across folders"


# ======================================================================================
# Two corpora, each of which produces one of the two blocked placements.
# ======================================================================================

def _crossing_corpus(root: Path) -> tuple[Path, Path]:
    """`104` R-N's corpus: a course in Downloads and one more of its files on
    the Desktop, so the plan has a home for the Desktop file under a top-level
    folder it is not in."""
    downloads = root / "holder" / "Downloads"
    desktop = root / "holder" / "Desktop"
    if downloads.is_dir():
        return downloads, desktop
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


def _unclassified_corpus(tmp_path: Path) -> Path:
    """`104` R-92's corpus, which places a file nothing has classified.

    The two transcripts and the starter script share one course code and
    nothing in the run says what kind of material any of them is, so the
    placements name a destination under `blocked_pending_user`.
    """
    corpus = tmp_path / "corpus"
    if corpus.is_dir():
        return corpus
    corpus.mkdir()
    (corpus / "Deposition.txt").write_text(
        "BUSIB 4300 Deposition Transcript\n\n"
        "Transcript of the witness in the seminar. Instructor: Dr. Ramirez. "
        "Credits: 3.\n")
    (corpus / "Second Deposition.txt").write_text(
        "BUSIB 4300 Deposition Transcript\n\n"
        "Second transcript of a witness. Instructor: Dr. Ramirez. Credits: 3.\n")
    (corpus / "starter.py").write_text(
        '"""BUSIB 4300 Homework 2 starter: implement a stack using two '
        'queues."""\n\nfrom collections import deque\n\n\nclass Stack:\n'
        "    def __init__(self):\n        self._in = deque()\n")
    return corpus


def _run(argv) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main(argv, out=out)
    return code, out.getvalue()


def _crossing_run(root: Path, database: Path, *extra):
    downloads, desktop = _crossing_corpus(root)
    code, printed = _run([str(downloads), "--situation", SITUATION,
                          "--label", LABEL, "--user", "jy",
                          "--accept-groups",
                          "--also-read", str(desktop),
                          "--database", str(database),
                          "--residual", AREA, *extra])
    assert code == 0, printed
    return printed


def _unclassified_run(tmp_path: Path, database: Path, *extra):
    code, printed = _run([str(_unclassified_corpus(tmp_path)),
                          "--situation", SITUATION, "--label", LABEL,
                          "--accept-groups",
                          "--user", "jy", "--database", str(database),
                          "--residual", AREA, *extra])
    assert code == 0, printed
    return printed


# ======================================================================================
# Reading the run back
# ======================================================================================

def _open(database: Path):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def _sets(database: Path) -> dict[str, tuple[str, ...]]:
    """`label -> the file ids in it`, over every set this run surfaced."""
    conn = _open(database)
    try:
        return {row["label"]: tuple(json.loads(row["payload"])["member_file_ids"])
                for row in conn.execute(
                    "SELECT label, payload FROM residual_sets ORDER BY rowid")}
    finally:
        conn.close()


def _names(database: Path) -> dict[str, str]:
    conn = _open(database)
    try:
        return {row["file_id"]: row["filename"]
                for row in conn.execute("SELECT file_id, filename FROM files")}
    finally:
        conn.close()


def _decisions(database: Path):
    conn = _open(database)
    try:
        version = conn.execute(
            "SELECT plan_version FROM residual_sets LIMIT 1").fetchone()
        assert version is not None, "this run surfaced no review set at all"
        return decisions_for_plan(conn, plan_version=version[0])
    finally:
        conn.close()


def _sets_holding(database: Path, filename: str) -> list[str]:
    names = _names(database)
    wanted = next(file_id for file_id, name in names.items()
                  if name == filename)
    return [label for label, members in _sets(database).items()
            if wanted in members]


# ======================================================================================
# The two halves of the ruling
# ======================================================================================

def test_a_move_across_folders_is_in_a_review_set_of_its_own(tmp_path):
    """The defect, stated as the property that fixes it.

    The Desktop file has a home in this plan and the plan may not carry it
    there. Before the ruling the screen said so -- `104` R-N put the mark
    beside it -- and offered a gesture that could not reach it: `--send-set`
    addresses review sets, and this file was in none.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    printed = _crossing_run(tmp_path, database)

    holding = _sets_holding(database, "PHYS1401 Problem Set 4.txt")
    assert holding == [NO_CROSSING], (
        "the file the plan cannot move is held in "
        f"{holding or 'no review set at all'}:\n{printed}")
    # Named on the screen by the label a person types after `--send-set`.
    assert f'Held for review as "{NO_CROSSING}"' in printed, printed


def test_a_placement_nothing_has_classified_is_in_a_review_set(tmp_path):
    """The other half. A destination and a policy that will not let it happen.

    `review_policy_for`'s first rule puts an unclassified subject's placement
    into `blocked_pending_user`, and `_abstention_explanation` already tells the
    two halves of a privacy block apart -- "nothing has said what this is yet"
    from "a model was not allowed to look". The same switch decides the set, so
    one state has one name on the screen rather than two.
    """
    database = tmp_path / "plan.sqlite"
    printed = _unclassified_run(tmp_path, database)

    blocked = [d for d in _decisions(database)
               if d.outcome == pv.PLACE
               and d.review_policy == pv.BLOCKED_PENDING_USER]
    assert blocked, (
        "this corpus no longer produces a blocked placement, so the test is "
        f"measuring nothing:\n{printed}")

    names = _names(database)
    held = {file_id for members in _sets(database).values()
            for file_id in members}
    missing = sorted(names[d.subject.file_id] for d in blocked
                     if d.subject.file_id not in held)
    assert not missing, (
        f"{missing} have a destination this run cannot act on and are in no "
        f"review set:\n{printed}")
    assert set(_sets(database)) & {NOT_CLASSIFIED, NO_MODEL}, (
        f"the blocked placements landed under {sorted(_sets(database))}")


def test_every_non_place_decision_and_every_blocked_placement_is_in_one_set(
        tmp_path):
    """R-115's invariant, extended, and its negative half kept.

    R-115 pinned "every unplaced file in exactly one set" and said in as many
    words that R-113's case was NOT solved: a placement with a destination and a
    blocked policy was in no set. This is that sentence rewritten by the ruling.

    The negative half is what stops the fix from becoming "hold everything": a
    placement nothing is blocking is in no review set, because a file the run
    can act on is not one the person is being asked to review.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    printed = _crossing_run(tmp_path, database)

    members = [file_id for files in _sets(database).values()
               for file_id in files]
    assert len(members) == len(set(members)), (
        f"a file is in two review sets: {sorted(members)}")

    decisions = _decisions(database)
    names = _names(database)
    crossing = {names[file_id] for file_id in _sets(database)[NO_CROSSING]}
    owed = {d.subject.file_id for d in decisions
            if d.subject.file_id and (
                d.outcome != pv.PLACE
                or d.review_policy == pv.BLOCKED_PENDING_USER
                or names[d.subject.file_id] in crossing)}
    assert set(members) == owed, (
        f"the sets cover {sorted(names[f] for f in set(members))} and the "
        f"decisions owed a set are {sorted(names[f] for f in owed)}:\n{printed}")

    free = {d.subject.file_id for d in decisions
            if d.outcome == pv.PLACE and d.subject.file_id
            and d.review_policy != pv.BLOCKED_PENDING_USER
            and names[d.subject.file_id] not in crossing}
    assert free and not (free & set(members)), (
        "a placement nothing is holding is being shown as held for review")


def test_send_set_reaches_a_blocked_placement(tmp_path):
    """The gesture the ruling exists for.

    A set that cannot be sent is a name on a screen. `--send-set` names the set
    by the label printed beside it, and the point is that it moves the file the
    plan could not: the placement is superseded by a residual decision into the
    area the person enabled.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    _crossing_run(tmp_path, database)

    sent = tmp_path / "holder" / "sent.sqlite"
    printed = _crossing_run(tmp_path, sent, "--send-set", f"{NO_CROSSING}={AREA}")

    names = _names(sent)
    moved = {names[d.subject.file_id] for d in _decisions(sent)
             if d.residual is not None and d.subject.file_id}
    assert moved == {names[file_id]
                     for file_id in _sets(sent)[NO_CROSSING]}, (
        f"sending {NO_CROSSING!r} acted on {sorted(moved)}:\n{printed}")
    assert "PHYS1401 Problem Set 4.txt" in moved, printed


def test_the_permission_the_person_gave_empties_the_set(tmp_path):
    """The negative twin, from the person's side.

    With `--may-cross-folders` typed, nothing is being held: the move is one the
    plan will carry out, so the file is on the "ready to file" side of the
    screen and in no review set. A set that survived the permission would be
    asking a second time for an answer already given.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    printed = _crossing_run(tmp_path, database, "--may-cross-folders")

    assert NO_CROSSING not in _sets(database), printed
    assert _sets_holding(database, "PHYS1401 Problem Set 4.txt") == [], printed
