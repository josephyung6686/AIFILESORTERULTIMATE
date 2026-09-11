"""A person renames a level, and the run after that still calls it their word.

`104` R-41, end to end, and the promise is `64` §2's: **the catalogue is a
proposal and the user's edits are facts.** A proposal may be re-derived at any
time; a fact may not be overwritten by re-derivation.

**What was already true, and is the control below.** The overlay has been
readable, appliable and durable since `64` landed: `design_tree` reads
`user_level_edits` off the database, and `route_branch` applies them as its LAST
step, after the C1-C8 gates have judged the recipe. What it had no caller for was
the WRITER -- `record_user_level_edit`, published by its module and called by
nothing -- so the edit was not honoured because it could not be MADE, which is
what `tests/integration/test_composition_root.py`'s strict xfail reported until
this change.

**Why it is asked by running the shipped command.** A test that writes the
overlay itself and then reads it back proves the two halves of a seam agree with
each other and says nothing about whether a person can reach either. That is the
shape of the defect this whole row is: both halves built, joined at neither.

**Three runs and not two.** A gesture that survives one run and not the next is
worse than one that never worked, because by then the person has started trusting
it. Run one is the screen that has to print the key; run two makes the gesture;
run three is the one that proves re-derivation did not take it back.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: Two courses, so `subject` divides and the level the gesture renames is one the
#: tree actually BUILT. The block prints a measured-but-unbuilt level too, on
#: purpose -- the name is a fact about the vocabulary and not about this week's
#: disk -- but a corpus where the renamed level never becomes a folder could not
#: tell a rename that reached the composition from one that reached only the
#: screen. `test_cli_correction_loop`'s corpus carries a second course for the
#: neighbouring reason, recorded there in full.
CORPUS = {
    "week 3 syllabus.pdf.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Ross.\n",
    "notes.txt":
        "PHYS 1401 lecture notes, week 3.\n",
    "COMS 4995 problem set 1.txt":
        "COMS 4995 Problem Set 1\n\nSpring 2026. Instructor: Dr. Okafor.\n",
}

#: `64` §3's triple, in the spelling the shipped library authors it in
#: (`tree_design/library/applicabilities.json`, `ap.academic.coursework`): the
#: schema, the role the recipe binds, and the P6 field it resolves to. It is
#: written out as a literal rather than read off the catalogue on purpose -- this
#: is the string the report tells a person to paste, and a test that computed it
#: the way the product does could not tell a screen that prints a key from a
#: screen that prints a key nothing reads.
LEVEL = "academic:subject_anchor:subject"

#: What the shipped library calls that level, and what the person calls it after.
PROPOSED = "Course"
MINE = "Class"


def _corpus(tmp_path: Path) -> Path:
    """Under `holder/corpus`, for `test_cli_correction_loop`'s reason: pytest
    names `tmp_path` after the test function, and a directory name above the
    corpus root has changed classification before now."""
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path, *extra: str) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"),
              "--accept-groups", *extra], out=out)
    return out.getvalue()


def _level_line(printed: str, key: str) -> str:
    """The line the levels block prints for one triple, or a word saying so.

    Read off the screen rather than out of the database, because half (a) of the
    row is that the person can SEE the key: a level renamed in a table nobody
    prints is a level nobody can name.
    """
    for line in printed.splitlines():
        if line.strip().endswith(key) or f"-- {key}" in line:
            return line.strip()
    return "ABSENT"


def _conn(corpus: Path) -> sqlite3.Connection:
    return cli.open_database(corpus.parent / "plan.sqlite")


def test_a_level_renamed_through_the_cli_is_what_the_next_runs_routing_reads(
        tmp_path):
    """The whole row in one test, because the halves are only worth anything joined.

    Run one prints the key. Run two types it and the two records land -- P13's
    `review_action`, which is the audit trail `81` §13.1 requires every canvas
    edit to travel in, and P10's overlay row, which is the durable fact. Run
    three re-derives the whole composition from the catalogue and comes back
    saying the person's word, with the library's own proposal kept beside it
    (`64` §5b) rather than discarded.
    """
    corpus = _corpus(tmp_path)

    first = _run(corpus)
    assert "What each level of this plan is called:" in first, first
    # The library's word, and the key beside it. Before this change the screen
    # printed the FIELD REF on the nesting chain and nothing else, which is one
    # third of the key and the third that says least.
    assert _level_line(first, LEVEL).startswith(PROPOSED), first

    second = _run(corpus, "--rename-level", f"{LEVEL}={MINE}")
    assert _level_line(second, LEVEL).startswith(MINE), second

    conn = _conn(corpus)
    try:
        stored = conn.execute(
            "SELECT uses_schema, role_ref, field_ref, action, display_label, "
            "basis FROM user_level_edits").fetchall()
        assert [tuple(row) for row in stored] == [
            ("academic", "subject_anchor", "subject", "renamed", MINE, "user")]
        # `81` §13.1's answer, which `review_surface/vocabulary.py` records at the
        # member: a canvas gesture DOES travel as a `review_action`, so one
        # history explains every change. Before this change `review_actions` held
        # only the bulk residual send.
        actions = conn.execute(
            "SELECT surface, action, subject_ref, correction_scope, routed_to "
            "FROM review_actions WHERE action = 'rename'").fetchall()
        assert len(actions) == 1, [tuple(row) for row in actions]
        assert actions[0]["surface"] == "canvas"
        assert actions[0]["subject_ref"] == LEVEL
        # `domain`, argued at `cli.LEVEL_RELABEL_SCOPE`: the sentence is about one
        # schema, and §8.7's whole example is about not inferring a scope.
        assert actions[0]["correction_scope"] == "domain"
        assert "P10" in actions[0]["routed_to"]
    finally:
        conn.close()

    third = _run(corpus)
    line = _level_line(third, LEVEL)
    assert line.startswith(MINE), third
    # `64` §5b: what the library proposed is recorded, not discarded -- which is
    # what lets an upgrade say "it called this Course when you renamed it".
    assert PROPOSED in line, third


def test_a_level_no_run_has_shown_is_refused_in_p13s_own_words(tmp_path):
    """The negative twin, and it guards the refusal rather than the happy path.

    §8.7 requires feedback to be stored with the evidence that produced it, so
    `collect` refuses a gesture naming something no presentation was recorded
    for. A first run that accepted a rename of a level it had never printed would
    store a fact about a screen nobody saw -- and would take the overlay's key on
    trust, so a typo would become a durable edit that silently applies to nothing
    for the rest of the database's life.

    The refusal is asserted as the SENTENCE a person reads, not as an exception
    type: it reaches them through `main`'s own "this run was refused" block, and
    a traceback there would be the product's answer to a mistyped word.
    """
    corpus = _corpus(tmp_path)
    refused = _run(corpus, "--rename-level", "academic:no_such_role:subject=X")
    assert "This run was refused" in refused, refused
    assert "names no recorded presentation" in refused, refused

    conn = _conn(corpus)
    try:
        assert conn.execute(
            "SELECT count(*) AS n FROM user_level_edits").fetchone()["n"] == 0
    finally:
        conn.close()


def test_the_form_of_the_gesture_is_refused_before_anything_is_written(tmp_path):
    """A key that is not a key names no level, and is told so rather than stored.

    Three parts and a name: anything else is a person who believes they have said
    something. `--reject`'s own rule -- a silently dropped gesture is the worst of
    both -- applied one flag over.
    """
    corpus = _corpus(tmp_path)
    for typed in ("subject=Class", "academic:subject_anchor:subject=",
                  "academic::subject=Class"):
        refused = _run(corpus, "--rename-level", typed)
        assert "is not a level" in refused, (typed, refused)

    conn = _conn(corpus)
    try:
        assert conn.execute(
            "SELECT count(*) AS n FROM review_actions").fetchone()["n"] == 0
    finally:
        conn.close()


def test_a_label_that_is_a_path_fragment_leaves_no_record_of_having_been_typed(
        tmp_path):
    """P10's refusal has to land in FRONT of P13's write, not behind it.

    "A renamed level is a display label, never a path fragment" is
    `templates.py`'s rule and `UserLevelEdit` enforces it at construction. If the
    gesture were collected first, a label with a separator in it would leave a
    stored `review_action` saying the person renamed the level, and the screen
    immediately telling them they had not -- the same split record the
    collect-before-the-receiver order exists to prevent, arriving from the other
    side. So the record is BUILT first, collected second and stored third.

    The level is one this run really shows, so the refusal cannot be the
    no-presentation one standing in for the one under test.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    refused = _run(corpus, "--rename-level", f"{LEVEL}=Class/2026")
    assert "This run was refused" in refused, refused
    assert "path separator" in refused, refused

    conn = _conn(corpus)
    try:
        # THE RENAME, not every action. `104` SF-3 put an `accept_bulk` on this
        # run -- the person accepted the groups, which is what makes there be a
        # tree with a level in it to rename -- so a bare count of `review_actions`
        # would now be a count of a gesture this test is not about. What must not
        # be here is a record of the rename they were told did not happen.
        assert conn.execute(
            "SELECT count(*) AS n FROM review_actions WHERE action = 'rename'"
        ).fetchone()["n"] == 0
        assert conn.execute(
            "SELECT count(*) AS n FROM user_level_edits").fetchone()["n"] == 0
    finally:
        conn.close()
