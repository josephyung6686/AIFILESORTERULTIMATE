"""A person leaves one LEVEL out, and the run after that still leaves it out.

`110` §2.2, and `107`'s *change depth* read as `110` reads it: not the
`TREE_LIMITS.max_depth` ceiling, which is one number for every tree, but *"keep
all receipts directly under 2026, or split by purpose"* -- omitting ONE level of
ONE branch. `64` §6 said the overlay "should be designed to hold them rather than
retrofitted per action", and it was: the record takes any of `DIMENSION_ACTIONS`
and the WRITER took one. This is the second.

**The same key `--rename-level` takes**, which is the whole of `64` §3: a level is
named by the vocabulary -- schema, role, field -- and never by a node id §8.8
re-mints or a template version an upgrade replaces. One key for both gestures,
printed once by the report, and the line a person pastes is the line that works.

**`84` §1 is the rule this gesture is most likely to break.** The folders under
the omitted level are not built; the FILES that were in them are still read,
still counted and still on the screen. The run's own coverage arithmetic is what
this asserts, rather than a sum computed here, because that block is what the
person checks.

**Three runs and not two**, for `test_cli_level_relabel`'s reason: run one prints
the key, run two makes the gesture, run three proves re-derivation did not take
it back.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: `test_cli_level_relabel`'s corpus and its reason: two courses, so the level
#: this gesture omits is one the tree actually BUILT. A corpus where the omitted
#: level never became a folder could not tell an omission that reached the
#: composition from one that reached only the overlay.
CORPUS = {
    "week 3 syllabus.pdf.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Ross.\n",
    "notes.txt":
        "PHYS 1401 lecture notes, week 3.\n",
    "COMS 4995 problem set 1.txt":
        "COMS 4995 Problem Set 1\n\nSpring 2026. Instructor: Dr. Okafor.\n",
}

#: `64` §3's triple, in the spelling the shipped library authors it in, written
#: out as a literal for `test_cli_level_relabel`'s stated reason: this is the
#: string the report tells a person to paste, and a test that computed it the way
#: the product does could not tell a screen that prints a key from a screen that
#: prints a key nothing reads. The guard in the first test is what stops it
#: passing vacuously if the library ever stops building this level.
LEVEL = "academic:subject_anchor:subject"

LABEL = "Coursework"


def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in CORPUS.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path, *extra: str) -> str:
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", LABEL, "--user", "jy",
              "--database", str(corpus.parent / "plan.sqlite"),
              "--accept-groups", *extra], out=out)
    return out.getvalue()


def _conn(corpus: Path) -> sqlite3.Connection:
    return cli.open_database(corpus.parent / "plan.sqlite")


def _folders(printed: str) -> list[str]:
    """The folder list, as labels, read off the screen and not out of the run."""
    lines = printed.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if line.startswith("Folders in this plan:"))
    found: list[str] = []
    for line in lines[start + 1:]:
        if not line.strip():
            break
        found.append(line.split("   [")[0].strip())
    return found


def test_a_level_omitted_through_the_cli_is_one_the_next_runs_tree_does_not_build(
        tmp_path):
    """The whole gesture in one test, because its halves are worth nothing apart.

    Run one prints the key and builds folders for it. Run two omits it: those
    folders are gone, the level is still NAMED on the screen -- `84` §1, marked
    and counted rather than silently dropped -- and two records land, P13's
    `review_action` and P10's overlay row. Run three re-derives the whole
    composition from the catalogue and still builds no folder for it, which is
    what makes this a durable fact rather than a one-run flag.
    """
    corpus = _corpus(tmp_path)

    first = _run(corpus)
    # THE GUARD. If the library ever stops building this level, this test must
    # fail loudly rather than assert that omitting it changed nothing.
    assert LEVEL in first, first
    built_first = _folders(first)
    assert len(built_first) > 2, (
        "this corpus has to build folders for the level being omitted, or the "
        f"test proves nothing: {built_first}")
    # `84` §6: a control the screen does not name is a control nobody has.
    assert "--omit-level" in first, first

    second = _run(corpus, "--omit-level", LEVEL)
    built_second = _folders(second)
    assert len(built_second) < len(built_first), (built_first, built_second)
    # The level is still on the screen, named, with what the library would have
    # done recorded beside it. `64` §5b, one action over, and `84` §1: a level
    # that vanished from the list would be one the person could no longer see
    # they had left out.
    assert LEVEL in second, second
    assert "you left this level out; this release would have built it" in second, \
        second

    conn = _conn(corpus)
    try:
        stored = conn.execute(
            "SELECT uses_schema, role_ref, field_ref, action, basis "
            "FROM user_level_edits").fetchall()
        assert [tuple(row) for row in stored] == [
            ("academic", "subject_anchor", "subject", "omitted", "user")]
        # `81` §13.1: a canvas gesture travels as a `review_action`, so one
        # history explains every change -- the same trail `--rename-level` leaves.
        actions = conn.execute(
            "SELECT surface, action, subject_ref, correction_scope "
            "FROM review_actions WHERE subject_ref = ?", (LEVEL,)).fetchall()
        assert len(actions) == 1, [tuple(row) for row in actions]
        assert actions[0]["surface"] == "canvas"
        # `domain`, the scope `--rename-level` argues for at `LEVEL_RELABEL_SCOPE`
        # and for its reason: the sentence is about one SCHEMA.
        assert actions[0]["correction_scope"] == "domain"
    finally:
        conn.close()

    third = _run(corpus)
    assert _folders(third) == built_second, (built_second, _folders(third))


def test_no_file_is_lost_when_a_level_is_not_built(tmp_path):
    """`84` §1, off the run's own arithmetic.

    SABOTAGE: drop the omitted level's members instead of routing them to the
    folder above. The coverage sum still prints and no longer closes.
    """
    corpus = _corpus(tmp_path)
    _run(corpus)
    second = _run(corpus, "--omit-level", LEVEL)
    total = len(CORPUS)

    assert f"Coverage: {total} files indexed." in second, second
    assert f"= {total}, and every file is on exactly one line above." in second, \
        second
    for name in CORPUS:
        assert name in second, (name, second)


def test_a_level_no_run_has_shown_is_refused_in_p13s_own_words(tmp_path):
    """The negative twin, and it guards the refusal rather than the happy path.

    §8.7 requires feedback stored with the evidence that produced it, so `collect`
    refuses a gesture naming something no presentation was recorded for -- and a
    first run that accepted an omission of a level it had never printed would
    take the overlay's key on trust, so a typo would become a durable edit that
    silently applies to nothing for the rest of the database's life.
    """
    corpus = _corpus(tmp_path)
    refused = _run(corpus, "--omit-level", "academic:no_such_role:subject")
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

    Three parts: anything else is a person who believes they have said something.
    `--rename-level`'s own refusal, one flag over and without the `=NAME` half,
    because an omission names no new word.
    """
    corpus = _corpus(tmp_path)
    for typed in ("subject", "academic::subject", "academic:subject_anchor"):
        refused = _run(corpus, "--omit-level", typed)
        assert "is not a level" in refused, (typed, refused)

    conn = _conn(corpus)
    try:
        assert conn.execute(
            "SELECT count(*) AS n FROM user_level_edits").fetchone()["n"] == 0
    finally:
        conn.close()
