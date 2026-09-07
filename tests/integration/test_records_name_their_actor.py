# tests/integration/test_records_name_their_actor.py
"""R-28, over a whole run: does anything on disk claim an act nobody performed?

`00`:136 requires every provenance record to carry "the responsible subsystem,
extractor or model version ... user identity when there is an explicit user
action". The failure this file exists to catch is the second clause read
backwards: a record that names the user when there was no user action. A frozen
tree is permanent, P13 shows its reasons back to the person as their own words,
and §8.5's replay reads the same rows to say what a run was allowed to do -- so
an overclaim here is not a cosmetic one.

The sweep is deliberately over the ACTOR columns rather than over every mention
of the person. `decided_by`, `created_by` and `detected_by` each carry `user` in
their own closed vocabulary (`grouping.vocabulary.DECIDED_BY`, `CREATED_BY`,
`DETECTED_BY`), which is what makes `!= 'user'` a statement about authorship and
not a keyword search. Two things are asserted PRESENT for the same reason:
`--label` and `--answer` are real gestures, and a run scrubbed of the person
would have replaced one false record with another.

Written by discovering the columns from `sqlite_master` rather than listing
them, so a part that adds a table with an actor column is swept the day it
lands. A hard-coded table list would pass forever while the thing it checks
moved somewhere else.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from grouping.vocabulary import USER  # noqa: E402
from tree_design.provenance import actor_phrase  # noqa: E402
from tree_design.vocabulary import SURFACE_UNATTENDED  # noqa: E402

#: The columns that say WHO. Each is a closed vocabulary that includes `user`,
#: so a value of `user` in one of them is an authorship claim and not a label.
ACTOR_COLUMNS: tuple[str, ...] = ("decided_by", "created_by", "detected_by")

#: The tables that exist only because somebody made a gesture. A row in any of
#: them on a run with no gesture is the same overclaim one level up: not a field
#: that names the wrong actor, but a record of an act that did not happen.
GESTURE_TABLES: tuple[str, ...] = (
    "structural_answers", "review_actions", "residual_set_decisions")


def _corpus(tmp_path):
    """Three courses over two terms, one of them holding a single file.

    Uneven on purpose: the freeze has to answer §5.8's depth question both ways
    in one run, so both of `refinement_for`'s sentences are on disk to be read.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    bodies = (("PHYS1401", "Spring 2026"), ("PHYS1401", "Spring 2026"),
              ("CHEM1500", "Fall 2025"), ("CHEM1500", "Fall 2025"),
              ("MATH2010", "Fall 2025"))
    for index, (course, term) in enumerate(bodies):
        (corpus / f"f{index}.txt").write_text(
            f"{course} Syllabus\nInstructor: Dr. Ramirez\n{term}\n")
    return corpus


def _argv(corpus, database):
    return [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy",
            "--database", str(database)]


def _connect(database):
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def _authorship_claims(conn) -> dict[str, int]:
    """Every `<table>.<column> = 'user'` in the database, with its row count."""
    claims = {}
    tables = [row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")]
    for table in sorted(tables):
        columns = [row[1] for row in conn.execute(
            'PRAGMA table_info("%s")' % table)]
        for column in columns:
            if column not in ACTOR_COLUMNS:
                continue
            count = conn.execute(
                'SELECT COUNT(*) FROM "%s" WHERE "%s" = ?' % (table, column),
                (USER,)).fetchone()[0]
            if count:
                claims["%s.%s" % (table, column)] = count
    return claims


def _gesture_rows(conn) -> dict[str, int]:
    rows = {}
    for table in GESTURE_TABLES:
        exists = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,)).fetchone()[0]
        assert exists, (
            f"{table!r} is not in the schema, so this sweep silently checks "
            "nothing. A renamed gesture table has to be renamed here too")
        rows[table] = conn.execute('SELECT COUNT(*) FROM "%s"' % table).fetchone()[0]
    return rows


def test_an_offline_run_attributes_no_record_to_the_user(tmp_path):
    """The whole run, with nobody at the screen: nothing on disk says they acted.

    This is R-28 as a property of the database rather than of one writer. It
    covers the three sites the register names -- `review_and_accept`'s merge,
    `choose_option`'s first pass, and the refinement dispositions -- and it also
    covers the writers nobody has looked at yet, because the columns are
    discovered rather than listed.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main(_argv(corpus, database), out=out)
    assert code == 0, out.getvalue()

    conn = _connect(database)
    try:
        claims = _authorship_claims(conn)
        gestures = _gesture_rows(conn)
        reasons = [row["refinement_reason"] for row in conn.execute(
            "SELECT refinement_reason FROM tree_nodes "
            "WHERE refinement_disposition IS NOT NULL")]
        questions = conn.execute(
            "SELECT COUNT(*) FROM structural_questions").fetchone()[0]
    finally:
        conn.close()

    assert claims == {}, (
        "these records name the person as their author on a run where nobody "
        f"was shown anything: {claims}")
    assert gestures == {table: 0 for table in GESTURE_TABLES}, (
        f"a gesture nobody made was recorded: {gestures}")

    # The nesting choice is the one this run really does make for them. It is
    # allowed to be made -- what it may not do is arrive as an answer. `66` §12's
    # test is that the QUESTION is on disk and the answer is not.
    assert questions >= 1, (
        "the branch this run shaped by rule left no question behind, so the "
        "person has nothing to overrule")

    actor = actor_phrase(SURFACE_UNATTENDED)
    assert reasons, "no branch carried a refinement answer at all"
    for reason in reasons:
        assert reason.startswith(actor), (
            "a frozen branch carries a permanent reason that does not say who "
            f"decided it: {reason!r}")


def test_the_gestures_the_person_did_make_are_still_theirs(tmp_path):
    """The negative twin. Scrubbing the person out would be the opposite error.

    `--label` is required and refused rather than guessed, so the name on the
    top-level branch really is the person's word and `label_source = user-edited`
    really is its author. A sweep that drove every user-shaped field to nothing
    would pass the test above and lose the only thing they actually supplied.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(_argv(corpus, database), out=out) == 0, out.getvalue()

    conn = _connect(database)
    try:
        labelled = [dict(row) for row in conn.execute(
            "SELECT display_label, label_source FROM groups "
            "WHERE display_label = 'Coursework'")]
        accepted = [dict(row) for row in conn.execute(
            "SELECT user_edited_label, decided_by FROM group_acceptance")]
    finally:
        conn.close()

    assert labelled, "the label the person typed is on no group"
    assert all(row["label_source"] == "user-edited" for row in labelled), labelled
    assert any(row["user_edited_label"] == "Coursework" for row in accepted), accepted
    # And the half that is NOT theirs, in the same breath: they named the branch,
    # they did not confirm which files went into it.
    assert all(row["decided_by"] != USER for row in accepted), accepted


def test_one_answer_writes_exactly_the_records_that_answer_produced(tmp_path):
    """A second run with one `--answer`, diffed against the first.

    The point is not that an answer is recorded -- it is that the answer is the
    ONLY thing the person is recorded as having done. A run that produced a
    genuine user record and three invented ones beside it would look identical
    from the answer's own row.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(_argv(corpus, database), out=out) == 0, out.getvalue()

    conn = _connect(database)
    try:
        before_claims = _authorship_claims(conn)
        before_gestures = _gesture_rows(conn)
        question_ids = [row[0] for row in conn.execute(
            "SELECT question_id FROM structural_questions")]
    finally:
        conn.close()

    assert before_claims == {}, before_claims
    assert "branch:Coursework" in question_ids, question_ids

    answered = io.StringIO()
    assert cli.main(
        _argv(corpus, database)
        + ["--answer", "branch:Coursework=keep-as-it-is"],
        out=answered) == 0, answered.getvalue()

    conn = _connect(database)
    try:
        after_claims = _authorship_claims(conn)
        after_gestures = _gesture_rows(conn)
        answers = [dict(row) for row in conn.execute(
            "SELECT question_id, option_id, state, scope, user_id, inferred "
            "FROM structural_answers")]
    finally:
        conn.close()

    # Exactly one gesture, and it is the one that was typed.
    assert after_gestures["structural_answers"] == 1, after_gestures
    assert after_gestures["review_actions"] == 0, after_gestures
    assert after_gestures["residual_set_decisions"] == 0, after_gestures
    assert before_gestures["structural_answers"] == 0, before_gestures

    (answer,) = answers
    assert answer["question_id"] == "branch:Coursework", answer
    assert answer["option_id"] == "keep-as-it-is", answer
    assert answer["scope"] == "branch:Coursework", answer
    assert answer["user_id"] == "jy", answer
    assert answer["state"] == "confirmed", answer
    # `inferred` is the field that would let a run manufacture an answer without
    # one being typed. The person typed this one.
    assert not answer["inferred"], answer

    # And answering did not turn anything ELSE into the person's act. The second
    # run re-derives the whole plan; every one of those records is still the
    # rules'.
    assert after_claims == {}, (
        "answering one question made these records claim the person authored "
        f"them too: {after_claims}")
