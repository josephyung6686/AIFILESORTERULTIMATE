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
    """A run with NO gesture at all. `104` SF-3 made this a real state.

    Before SF-3 there was no such run: the rules recorded an acceptance on every
    invocation, so "nobody was at the screen" described the screen and not the
    database. A run with no gesture now proposes its groups and stops, and the
    sweep over it is the strongest form of R-28 available -- a database in which
    nothing at all should name the person.
    """
    return [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy",
            "--database", str(database)]


def _argv_accepted(corpus, database):
    """The same run with the one gesture that turns a proposal into a plan.

    `104` SF-3: a tree is built out of ACCEPTED groups, so a plan exists only
    downstream of somebody's accept. Every test below that needs a frozen branch,
    a refinement reason or a structural question runs this argv -- and the
    assertion it carries is not "nothing names the person" but "the ONLY thing
    that names the person is the gesture they made", which is the same shape
    `test_one_answer_writes_exactly_the_records_that_answer_produced` already
    applies to `--answer`.
    """
    return _argv(corpus, database) + ["--accept-groups"]


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


def test_a_run_with_no_gesture_attributes_nothing_at_all_to_the_user(tmp_path):
    """Nobody typed anything: NOTHING on disk says they acted. `104` SF-3.

    This is R-28 at its strongest, and SF-3 is what made it available. The register
    named three sites where the run claimed the person -- `review_and_accept`'s
    merge, `choose_option`'s first pass, the refinement dispositions -- and the
    first of them wrote an `accepted` row on every invocation, so a sweep of a
    gesture-free database was a sweep of something that did not exist. It does now:
    a run nobody decided proposes its groups and stops.

    The columns are discovered from `sqlite_master` rather than listed, so a part
    that adds a table with an actor column is swept the day it lands.
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
    finally:
        conn.close()

    assert claims == {}, (
        "these records name the person as their author on a run where nobody "
        f"was shown anything: {claims}")
    assert gestures == {table: 0 for table in GESTURE_TABLES}, (
        f"a gesture nobody made was recorded: {gestures}")


def test_the_run_that_shapes_a_branch_says_the_rules_shaped_it(tmp_path):
    """The nesting and depth choices, on a run whose ONE gesture was the accept.

    Accepting the groups is the person's act and the only one here; everything the
    tree pass then decides -- which nesting, how deep each branch goes -- is still
    the rules'. It is allowed to be decided. What it may not do is arrive as an
    ANSWER: `66` §12's test is that the QUESTION is on disk and the answer is not,
    and the permanent reason frozen onto a branch has to say who decided it.

    Split off from the sweep above by `104` SF-3, and the split is the point: a
    tree exists only downstream of an acceptance, so these two properties cannot be
    asserted over one database any more. Asserting them over the accepted run and
    calling that run gesture-free would have been the overclaim this file exists to
    catch, written into the file itself.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    code = cli.main(_argv_accepted(corpus, database), out=out)
    assert code == 0, out.getvalue()

    conn = _connect(database)
    try:
        claims = _authorship_claims(conn)
        reasons = [row["refinement_reason"] for row in conn.execute(
            "SELECT refinement_reason FROM tree_nodes "
            "WHERE refinement_disposition IS NOT NULL")]
        questions = conn.execute(
            "SELECT COUNT(*) FROM structural_questions").fetchone()[0]
    finally:
        conn.close()

    # The acceptance is the person's and says so; NOTHING ELSE is.
    assert claims == {"group_acceptance.decided_by": claims.get(
        "group_acceptance.decided_by")}, (
        "the accept gesture is the only act the person performed, and these "
        f"records claim others: {claims}")
    assert claims["group_acceptance.decided_by"] >= 1, claims

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

    **`104` SF-3 ADDED A SECOND THING THEY SUPPLIED, and the last assertion here
    inverts because of it.** It read `decided_by != USER` -- true, and worth
    asserting, while `review_and_accept` wrote an `accepted` row nobody had asked
    for. The row now exists only because this run typed `--accept-groups`, so
    `user` is what it must say; the old assertion would be the same overclaim
    pointing the other way. The half that has NOT changed is which claim is being
    made: they accepted the group the rules assembled, they did not choose its
    files, and the group row's `proposed_basis` still says so in its own words.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(_argv_accepted(corpus, database), out=out) == 0, out.getvalue()

    conn = _connect(database)
    try:
        labelled = [dict(row) for row in conn.execute(
            "SELECT display_label, label_source FROM groups "
            "WHERE display_label = 'Coursework'")]
        merged = [dict(row) for row in conn.execute(
            "SELECT proposed_basis FROM groups "
            "WHERE display_label = 'Coursework'")]
        accepted = [dict(row) for row in conn.execute(
            "SELECT user_edited_label, decided_by FROM group_acceptance")]
    finally:
        conn.close()

    assert labelled, "the label the person typed is on no group"
    assert all(row["label_source"] == "user-edited" for row in labelled), labelled
    assert any(row["user_edited_label"] == "Coursework" for row in accepted), accepted
    # And the acceptance is theirs too, since `104` SF-3: they typed it. The half
    # that is NOT theirs is the FILE SET, and it is asserted where it lives -- on
    # the group row's `proposed_basis`, which still admits nobody was shown it.
    assert all(row["decided_by"] == USER for row in accepted), accepted
    assert all("nobody was shown which files" in (row["proposed_basis"] or "")
               for row in merged), merged


def test_one_answer_writes_exactly_the_records_that_answer_produced(tmp_path):
    """A second run with one `--answer`, diffed against the first.

    The point is not that an answer is recorded -- it is that the answer is the
    ONLY thing the person is recorded as having done BEYOND what they had already
    done. A run that produced a genuine user record and three invented ones beside
    it would look identical from the answer's own row.

    **The baseline is the accepted run, not the bare one (`104` SF-3).** The
    question this answers is a BRANCH question, and a branch exists only once the
    groups are accepted -- so the run that raises it is a run that has already been
    told something. The diff is therefore against a database that already carries
    exactly one user claim, the acceptance; what the answer must add is its own
    row and nothing else.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(_argv_accepted(corpus, database), out=out) == 0, out.getvalue()

    conn = _connect(database)
    try:
        before_claims = _authorship_claims(conn)
        before_gestures = _gesture_rows(conn)
        question_ids = [row[0] for row in conn.execute(
            "SELECT question_id FROM structural_questions")]
    finally:
        conn.close()

    # The acceptance, and only the acceptance. `104` SF-3.
    assert set(before_claims) == {"group_acceptance.decided_by"}, before_claims
    assert "branch:Coursework" in question_ids, question_ids

    answered = io.StringIO()
    assert cli.main(
        _argv_accepted(corpus, database)
        + ["--answer", "branch:Coursework=keep-as-it-is"],
        out=answered) == 0, answered.getvalue()

    conn = _connect(database)
    try:
        after_claims = _authorship_claims(conn)
        after_gestures = _gesture_rows(conn)
        answers = [dict(row) for row in conn.execute(
            "SELECT question_id, option_id, state, scope, user_id, inferred "
            "FROM structural_answers")]
        collected = [dict(row) for row in conn.execute(
            "SELECT surface, action FROM review_actions")]
    finally:
        conn.close()

    # ONE structural answer, and it is the one that was typed.
    assert after_gestures["structural_answers"] == 1, after_gestures
    assert before_gestures["structural_answers"] == 0, before_gestures
    assert after_gestures["residual_set_decisions"] == 0, after_gestures
    # AND THE ANSWER ADDED NO REVIEW ACTION OF ITS OWN (`104` SF-3). The count is
    # deliberately not pinned to a number: the second run collects a second accept
    # exactly when the answer moved which groups P9 forms, because a merged draft's
    # id is a digest over the ids it merges, and it collects none when the draft is
    # the one already accepted (`cli.accept_drafted_groups` skips it). Both are
    # correct and which one happens is a fact about the corpus, so what is asserted
    # is the property: every gesture on this surface is the accept, and answering a
    # question is not recorded as one.
    assert before_gestures["review_actions"] >= 1, before_gestures
    assert after_gestures["review_actions"] >= before_gestures[
        "review_actions"], (before_gestures, after_gestures)
    assert {(row["surface"], row["action"]) for row in collected} == {
        ("group_plan", "accept_bulk")}, collected

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
    # rules', and the acceptance is the one that was already theirs.
    # Compared by COLUMN and not by count: the accept on the second run wrote a
    # second acceptance row, legitimately, so the count moves. What must not move
    # is WHICH records name the person -- a new key here is a new overclaim.
    assert set(after_claims) == set(before_claims) == {
        "group_acceptance.decided_by"}, (
        "answering one question made these records claim the person authored "
        f"them too: {after_claims} (was {before_claims})")
