# tests/integration/test_the_level_answer_is_written_down.py
"""`106` Phase 2(b): the judge's SECOND answer is computed, counted, and thrown away.

**THE DEFECT, FOUND WHILE GRADING (`104` §18.103).** `record_the_situation` has
exactly one call site, `cli.py:9564`, and it runs on the KIND path -- before
`_ask_which_situation_of_the_kind` is even called. So the `situation` fact holds
`nonprofit`, the schema id, and the finer answer the level stage went and got,
`nonprofit.member-association`, is recorded as *no fact at all*. The product asks
the judge a second, sharper question, spends a call on it, counts the answer in
`SituationPass.situations` -- and then lets it die with the pass object.

**WHY THE FINER VALUE, AND NOT A SECOND FIELD.** `106` Phase 2 left this open:
*"add a `situation_level` field or reuse `situation` with the finer value --
decide by asking which the sort needs, not by which is easier."* The sort needs
the finer one. `cli.signals_for_branch` emits `recognition:{situation}` and the
template router matches applicability rows keyed on SITUATION ids, not schema
ids; `production.schema_for_situation` recovers `nonprofit` from
`nonprofit.member-association` whenever the kind is what a reader wants, and
nothing recovers the situation from the schema. One field, one meaning -- "the
situation this file is part of" -- answered as finely as the run managed.

**IT SUPERSEDES, IT DOES NOT OVERWRITE.** `record_the_situation` already retires
the standing row through `supersede_fact`, so the kind row stays readable with a
pointer to what replaced it, and a run written under the old meaning still reads.
`00` amendment 9 is untouched: neither field is destination-eligible, so nothing
written here can become a folder name.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from facts.llm_seam import SITUATION_FIELD  # noqa: E402
from facts.supersede import preferred_fact  # noqa: E402

from test_the_judge_names_the_situation import (  # noqa: E402
    CHOSEN, CLUB, CLUB_FILES, SCHEMA, _run,
)


@pytest.fixture(scope="module")
def deciding(tmp_path_factory):
    """The ratified run: the judge names the kind, then names which of its
    situations, and the person is asked about that branch at all."""
    return _run(tmp_path_factory.mktemp("written-down"), ratify=True)


def _situations_of_the_clubs_files(database: Path) -> dict[str, str | None]:
    """Each society file's situation AS A READER OF THE STORE SEES IT.

    Through `preferred_fact`, which is the same call `cli._situations_of` makes
    for the branch signals -- not a raw row read. A test that queried
    `file_facts` directly would pass on a store whose slot is unresolvable, which
    is precisely the state the supersession exists to prevent. `preferred_fact`
    hands back a row carrying `value_id`, and the canonical value is read through
    the `values` table exactly as `cli.py:16111` reads it.
    """
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        value_of = {row["value_id"]: row["canonical_value"] for row in conn.execute(
            'select value_id, canonical_value from "values" where field_key = ?',
            (SITUATION_FIELD,))}
        seen = {}
        for row in conn.execute("select file_id, filename from files"):
            if row["filename"] in CLUB_FILES:
                fact = preferred_fact(conn, file_id=row["file_id"],
                                      field_key=SITUATION_FIELD)
                seen[row["filename"]] = (
                    None if fact is None else value_of.get(fact["value_id"]))
        return seen
    finally:
        conn.close()


def test_the_society_files_carry_the_situation_and_not_only_the_kind(deciding):
    """The defect, stated as an assertion.

    SABOTAGE: delete the `record_the_situation` call on the level path. Red here,
    and the store goes back to answering `nonprofit` for a file the judge was
    asked, and answered, `nonprofit.member-association` about -- which is the
    branch signal `106` Phase 2(a) just taught the router to read.
    """
    seen = _situations_of_the_clubs_files(deciding["database"])

    assert seen, f"no society file was found in the run's store ({CLUB})"
    for filename, situation in sorted(seen.items()):
        assert situation == CHOSEN, (
            f"{filename} reads {situation!r}, not the situation the judge named")


def test_the_kind_row_is_superseded_and_points_at_the_situation(deciding):
    """A run written under the old meaning stays readable.

    `106` Phase 2's own risk line: *"(b) changes what an existing field means.
    Supersede, never overwrite; a run written under the old meaning must stay
    readable."* The kind row is still there, retired, and its pointer names the
    row that replaced it -- which is the claim, not merely that some pointer is
    set. Scoped to the society's own files: another file whose kind is the same
    and whose level stage was never asked has a kind row still standing, and that
    is correct for it.

    SABOTAGE: have the level path delete or update the kind row in place. Green
    above, and the audit trail that says WHY this file's situation changed is
    gone -- `104` §17.2's rule one field over.
    """
    conn = sqlite3.connect(deciding["database"])
    conn.row_factory = sqlite3.Row
    try:
        rows = list(conn.execute(
            'select f.filename, old.superseded_by, '
            '       ov.canonical_value as was, nv.canonical_value as now '
            'from file_facts old '
            'join "values" ov on ov.value_id = old.value_id '
            'join files f on f.file_id = old.file_id '
            'left join file_facts new on new.fact_id = old.superseded_by '
            'left join "values" nv on nv.value_id = new.value_id '
            "where old.field_key = ? and ov.canonical_value = ?",
            (SITUATION_FIELD, SCHEMA)))
    finally:
        conn.close()

    mine = [row for row in rows if row["filename"] in CLUB_FILES]
    assert mine, f"the kind row for {SCHEMA} was deleted, not superseded"
    for row in mine:
        assert row["superseded_by"], (
            f"{row['filename']}: a kind row is still standing beside the "
            "situation that replaced it, which makes the situation unresolvable")
        assert row["now"] == CHOSEN, (
            f"{row['filename']}: the kind row was retired by {row['now']!r}, "
            f"not by the situation the judge named")


def test_the_run_still_does_not_ask_the_person_about_that_branch(deciding):
    """The fact is written AND the branch is still settled by the judge.

    This is `test_the_judges_situation_resolves_the_file_and_the_question_is_not_
    asked` restated against this run, because writing a fact on the level path is
    exactly the kind of change that could re-open a question by giving
    `partition_by_branch` a different answer to read.

    SABOTAGE: write the finer value somewhere the branch partition does not read,
    and this stays green while the first test goes red -- which is why both are
    here.
    """
    said = deciding["said"]

    assert f"Which of these is {SCHEMA}?" not in said, said
    assert f"--answer situation:{SCHEMA}=" not in said, said


@pytest.fixture(scope="module")
def again(tmp_path_factory):
    """The ratified run, then the same command again over the same database."""
    return _run(tmp_path_factory.mktemp("written-twice"), ratify=True, twice=True)


def test_a_second_run_does_not_make_the_situation_unreadable(again):
    """THE FAILURE A SECOND PASS OVER ONE FIELD INVITES, asserted before it ships.

    Two writers now touch one slot in one run -- the kind pass, then the level
    pass -- and `record_the_situation` retires whatever is standing when it
    writes. Trace the second run of the same command:

      run 1   kind writes `nonprofit` (K); level writes the situation (F);
              standing was [K], so K is retired by F. Correct.
      run 2   kind writes `nonprofit` again. `write_fact` is idempotent at one
              identity, so it hands back K -- WHICH IS ALREADY RETIRED. Standing
              is now [F], F does not name `nonprofit`, and F is not the person's
              answer, so the loop would retire F by K. Both rows are then
              superseded, no live row names the slot, and `preferred_fact`
              answers `None`.

    A file whose situation the judge answered TWICE would end with no readable
    situation at all -- the exact failure `record_the_situation`'s own docstring
    says its retirement exists to prevent, arrived at from the other direction.

    SABOTAGE: this test is the sabotage. Ship 2(b) without it and the product
    passes every other assertion in this file while a re-run silently unreads the
    answer it just paid a model to give.
    """
    seen = _situations_of_the_clubs_files(again["database"])

    assert seen, "no society file was found in the run's store"
    for filename, situation in sorted(seen.items()):
        assert situation == CHOSEN, (
            f"after a second run {filename} reads {situation!r} -- the slot is "
            "unresolvable or the kind has taken it back")
