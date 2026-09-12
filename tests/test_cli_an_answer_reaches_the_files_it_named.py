# tests/test_cli_an_answer_reaches_the_files_it_named.py
"""`104` R-86. What a person decided when they answered the question on screen.

The screen asks one question per folder nothing could be read out of, and it
says in as many words what the answer does:

    Where should the files in Downloads go?
      2 files in Downloads were opened and nothing readable came out of them,
      so nothing but you can say what they are.
      This decides where those 2 files are filed.

`cli.already_answered` then read that answer off the FOLDER the file sits in,
so `--answer home:.=Coursework` about two unreadable scans re-homed all 33
files in the folder -- and the freeze that followed froze nothing, because a
single group of thirty-three files past the report's naming cap is a group the
freeze may not approve.

The ruling: the answer's scope is the files the question named. A folder-wide
answer needs a folder-wide question, and this screen does not ask one. The
question's sentence and the answer's reach are one fact, and the sentence was
the half that was right.

These tests are that fact from both ends: the two files the sentence names are
the two that move, the other thirty-one are decided exactly as they would have
been had nobody answered, and the freeze can then act on what it was shown.
"""
from __future__ import annotations

import io
import json
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402

#: `104` SF-3. A group is a DRAFT until somebody decides it (see `test_cli.py`'s
#: own docstring for the ruling); every run below reads a structural question or
#: a placement decision, so every one of them has to type the accept, same as a
#: person does, or none of that exists yet.
ACCEPTS_THE_PROPOSAL: tuple[str, ...] = ("--accept-groups",)

#: Thirty-one files the product CAN read, over two courses so the plan has more
#: than one destination to offer -- a question with one option is a placement
#: wearing a question mark, and `question_for_unreadable_folder` refuses it.
READABLE = 31
UNREADABLE = ("scan_0001.png", "scan_0002.png")


def _corpus(tmp_path):
    """Thirty-three files in ONE folder: two nothing opens, thirty-one that read.

    They sit in the scan root itself, which is the shape the row was measured
    on: the question is `home:.`, and `.` is the folder the person typed.
    """
    corpus = tmp_path / "Downloads"
    # WRITTEN ONCE, and every later call finds what the first one built. These
    # tests run the same corpus twice -- once to be asked, once to answer -- and
    # rewriting the files between the two would change every `mtime`, which the
    # scan reads as thirty-three files the person had just edited. The corpus is
    # meant to be the same corpus.
    if corpus.is_dir():
        return corpus
    corpus.mkdir(parents=True)
    for index in range(READABLE):
        course = "PHYS1401" if index % 2 else "ECON2010"
        (corpus / f"{course} problem set {index}.txt").write_text(
            f"{course} Problem Set {index}\n"
            f"Problem set for {course}, due 2026-02-{1 + index % 27:02d}.\n"
            "Student: jy\n")
    # PNG magic and nothing else: opened, recognised as an image, no text. The
    # padding differs per file so the two are two documents rather than one
    # duplicate family, which is a different screen and a different row.
    for index, name in enumerate(UNREADABLE):
        (corpus / name).write_bytes(b"\x89PNG\r\n\x1a\n" + bytes([index]) * 64)
    return corpus


def _argv(corpus, database, *extra):
    return [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy",
            "--database", str(database), *extra]


def _run(argv):
    out = io.StringIO()
    code = cli.main(argv, out=out)
    return code, out.getvalue()


def _open(database):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def _home_question(database):
    conn = _open(database)
    try:
        row = conn.execute(
            "SELECT question_id, unlocks, options FROM structural_questions "
            "WHERE question_id = 'home:.'").fetchone()
    finally:
        conn.close()
    assert row is not None, "the run asked no question about the scanned folder"
    return dict(row)


def _names(database):
    conn = _open(database)
    try:
        return {row["file_id"]: row["filename"]
                for row in conn.execute("SELECT file_id, filename FROM files")}
    finally:
        conn.close()


def _chosen_by_the_person(database):
    """The files this run placed because the PERSON said where they go.

    Read off `confidence_class`, which is what P13 shows back as the reason a
    file moved, rather than off the destination: several files can land in one
    folder and only some of them because somebody was asked.
    """
    conn = _open(database)
    try:
        decisions = [json.loads(row["payload"]) for row in conn.execute(
            "SELECT payload FROM placement_decisions WHERE superseded_by IS NULL")]
    finally:
        conn.close()
    names = _names(database)
    return {names[decision["subject"]["file_id"]] for decision in decisions
            if decision["confidence_class"] == "user chose the destination"
            and decision["subject"]["file_id"] in names}


def _asked(tmp_path, database):
    """Run once, and read back the question the screen printed.

    The answer has to be given to the database that asked: `--answer` naming a
    question this plan has never raised is refused outright, and rightly.
    """
    code, printed = _run(_argv(_corpus(tmp_path), database, *ACCEPTS_THE_PROPOSAL))
    assert code == 0, printed
    question = _home_question(database)
    return question, json.loads(question["options"])[0]["option_id"], printed


def _outcomes(database, *, excluding=()):
    """What this run concluded about each file, by the name a person reads."""
    conn = _open(database)
    try:
        decisions = [json.loads(row["payload"]) for row in conn.execute(
            "SELECT payload FROM placement_decisions "
            "WHERE superseded_by IS NULL")]
    finally:
        conn.close()
    names = _names(database)
    return {names[d["subject"]["file_id"]]: d["outcome"] for d in decisions
            if d["subject"]["file_id"] in names
            and names[d["subject"]["file_id"]] not in excluding}


def test_the_answer_moves_the_two_files_the_question_named(tmp_path):
    """The defect, stated as the property that fixes it.

    Before this, one `--answer home:.=Coursework` carried every file in the
    folder -- the thirty-one the product had read perfectly well included -- to
    the destination the person had chosen for two scans.
    """
    database = tmp_path / "plan.sqlite"
    _, chosen, _ = _asked(tmp_path, database)

    code, printed = _run(_argv(_corpus(tmp_path), database,
                               "--answer", f"home:.={chosen}",
                               *ACCEPTS_THE_PROPOSAL))
    assert code == 0, printed

    moved = _chosen_by_the_person(database)
    assert moved == set(UNREADABLE), (
        f"the person was asked about {sorted(UNREADABLE)} and the answer "
        f"reached {sorted(moved)}")


def test_the_other_thirty_one_files_are_decided_by_the_run(tmp_path):
    """The twin, and the one that says what "not reached" means.

    A file the question did not name is not held back or refused -- it is
    decided exactly as it would have been had nobody answered anything. So the
    property is an equality against the SECOND run of the same corpus that was
    never answered, not merely "fewer than thirty-three moved". Second against
    second: a first run and a second differ in what they have already accepted,
    and comparing across that would be measuring the wrong thing.
    """
    database = tmp_path / "plan.sqlite"
    _, chosen, _ = _asked(tmp_path, database)
    _run(_argv(_corpus(tmp_path), database, "--answer", f"home:.={chosen}",
              *ACCEPTS_THE_PROPOSAL))

    control = tmp_path / "unanswered.sqlite"
    _asked(tmp_path, control)
    _run(_argv(_corpus(tmp_path), control, *ACCEPTS_THE_PROPOSAL))

    answered = _outcomes(database, excluding=UNREADABLE)
    assert len(answered) == READABLE
    assert answered == _outcomes(control, excluding=UNREADABLE), (
        "answering a question about two scans changed what the run concluded "
        "about the thirty-one files it had read")


def test_the_sentence_on_the_screen_and_the_answer_reach_the_same_files(
        tmp_path):
    """`00`'s standing rule for this row: the promise and the act are one fact.

    The question's `unlocks` sentence is a COUNT the person reads before they
    type, so it is the number that has to match what moves. Asserted as the
    same integer twice rather than as two hard-coded 2s, so a fixture that grew
    a third unreadable file would still be testing the property.
    """
    database = tmp_path / "plan.sqlite"
    question, chosen, first = _asked(tmp_path, database)

    said = re.search(r"decides where (?:that|those) (\d+) files? (?:is|are) "
                     r"filed", question["unlocks"])
    assert said, question["unlocks"]

    _run(_argv(_corpus(tmp_path), database, "--answer", f"home:.={chosen}",
              *ACCEPTS_THE_PROPOSAL))
    moved = _chosen_by_the_person(database)
    assert int(said.group(1)) == len(moved), (
        f"the screen said {said.group(0)!r} and the answer reached "
        f"{sorted(moved)}")
    # And the sentence a person actually reads carried that same count.
    assert said.group(1) in " ".join(first.split()), first


def test_the_freeze_plans_the_other_files_into_the_folders_the_run_chose(
        tmp_path):
    """What `--answer` then `--freeze` turns into a plan, measured on this corpus.

    Before the ruling, `--answer home:.=Coursework` gave all thirty-three files
    one destination, so the freeze offered a single `Coursework` branch holding
    thirty-one files the run had read and sorted into two courses. The person
    had answered a question about two scans and been handed a plan that undid
    every other decision in the run -- and on the corpus the row was measured
    on, where the group ran past the report's naming cap, the freeze could
    approve nothing at all.

    After it, the freeze plans exactly the tree the run built, and the two scans
    go where the person put them and nowhere else. Thirty-one files keep the two
    courses the run sorted them into; the two the question named join
    `Coursework`, which is the whole of what was answered.

    **`104` R-40 CHANGED THE SECOND HALF OF THIS TEST AND NOT THE FIRST.** Until
    it landed, this asserted thirty-one and named the two scans as HELD:
    `review_policy_for` returned `blocked_pending_user` for a subject nothing had
    classified before it asked anything else, so a destination the person had
    typed was carried onto the record and then refused by the freeze. That is the
    question failing to deliver, not scope working -- R-86's ruling is about WHICH
    files an answer reaches, and it is measured by the thirty-one that keep their
    own folders, which is unchanged here. The two scans are now planned, and
    `review_required` rather than `auto_eligible` is what keeps naming a home
    apart from authorising the move.
    """
    database = tmp_path / "plan.sqlite"
    _, chosen, _ = _asked(tmp_path, database)

    code, printed = _run(_argv(_corpus(tmp_path), database,
                               "--answer", f"home:.={chosen}", "--freeze",
                               *ACCEPTS_THE_PROPOSAL))
    assert code == 0, printed

    conn = _open(database)
    try:
        nodes = {row["node_id"]: (row["display_label"], row["parent_node_id"])
                 for row in conn.execute(
                     "SELECT node_id, display_label, parent_node_id "
                     "FROM tree_nodes")}
        planned = [(row["file_id"], row["node_id"])
                   for row in conn.execute(
                       "SELECT file_id, node_id FROM move_plans")]
    finally:
        conn.close()

    def chain_of(node_id):
        parts, walk = [], node_id
        while walk is not None and walk in nodes:
            label, walk = nodes[walk]
            parts.append(label)
        return "/".join(reversed(parts))

    names = _names(database)
    where = {names[file_id]: chain_of(node_id) for file_id, node_id in planned}
    assert len(where) == READABLE + len(UNREADABLE), (
        f"the freeze planned {sorted(where)}:\n{printed}")
    # THE THIRTY-ONE ARE THE MEASUREMENT, and they are read separately from the
    # two so that the count above cannot be satisfied by the answer spreading.
    # `home:.=Coursework` said Coursework about two scans; a run that filed the
    # other thirty-one there too would have the same total and the wrong plan.
    assert {chain for name, chain in where.items()
            if name not in UNREADABLE} == {"Coursework/ECON2010",
                                           "Coursework/PHYS1401"}, (
        "the answer about two scans was applied to the whole folder and the "
        f"freeze planned {sorted(set(where.values()))}:\n{printed}")
    # And the two the answer DID reach went where it said, which is `104` R-40:
    # the one question the product asks about an unreadable file now delivers.
    for name in UNREADABLE:
        assert where.get(name) == chosen, (name, where, printed)
        assert name in printed, printed
