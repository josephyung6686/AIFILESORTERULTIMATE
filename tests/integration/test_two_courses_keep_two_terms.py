# tests/integration/test_two_courses_keep_two_terms.py
"""Two courses, two calendars, two `Semester` folders -- through `cli.main`.

`105` §14.2 is three rulings about one field and only the third can be asked here:
*"the result is bound to the relevant course"*, and *"infer no equivalence between
numbered terms, semesters, or seasons without evidence for that course's calendar"*.
A unit test can prove a canonicaliser keeps two strings apart; only a run can prove
that the two strings become two folders and that each course's files are under its
own.

**HALF OF THIS CORPUS WAS UNREADABLE BEFORE 7 SEP 2026.** `104` R-101 counted the
owner's real run: 114 `term` answers refused, and the single commonest refused shape
was `2023-2024 Term 1`, fifteen times, with `2023-2024` thirteen more. That is one
university writing its own two-term calendar, and this product had no pattern for it,
so those files reached no `Semester` level at all. `CHEM2100` below is that course.
The test is therefore not a rearrangement of an existing one: run it against the
previous vocabulary and the second course has no term.

**AND THE MERGE IT RULES OUT IS REAL AND IS STILL SWITCHED OFF.**
`production.GROUP_LEVEL_ROLES` deliberately does not carry `cycle_period`.
`cli._merge_reviewed_groups` writes ONE accepted group per `--label` -- both courses
below are in it -- so "the group's term" would be a disagreement between `Fall2024`
and `2023-2024Semester1`, `group_level_value` would answer `None`, and BOTH folders
would disappear. The term stays the FILE's own value, and a file belongs to one
course. That is the binding §14.2 asks for at the only grain that exists until B is
ratified and groups are per course.

Written through `cli.main` rather than a hand-built fixture, for `85` §6.4 and `84`
§5.5's reason: a part's own suite cannot see this defect class, because every part
builds its own fixture and sets up the state the run never reaches.
`tests/integration/test_production_corpus.py` cannot ask it either -- its `_stage`
splits a filename on spaces and assigns the tokens to fields positionally, so no
term pattern runs there at all.
"""
from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli


#: One syllabus, printing its course and its term the way a syllabus does.
#: `Instructor:` is load-bearing: `cli.SUBJECT_RULE` is §3.5's rule and a course code
#: is a fact only "together with academic context such as 'syllabus,' 'lecture,'
#: 'credits,' 'instructor,' or 'semester'". Without a subject there is no course to
#: bind the term TO, and the test would pass for the wrong reason.
SYLLABUS = """{code} Syllabus -- {term}

Instructor: R. Feynman. Section 001, {term}.
Meets Tuesday and Thursday.
"""

#: THE TWO CALENDARS. `Fall 2024` is a season and a year, which this product has read
#: since it could read a term at all. `2023-2024 Semester 1` is the two-term academic
#: year's own spelling, which `105` §14.2 ruled in.
#:
#: They are very probably the SAME PART of the year at two universities, and that is
#: exactly what the ruling forbids inferring: a two-term year's first semester is
#: autumn in the northern hemisphere and is not in the southern one, and this product
#: has no evidence about either course's calendar. So they stay two.
COURSES = (
    ("phys", "PHYS 1401", "PHYS1401", "Fall 2024", "Fall2024"),
    ("chem", "CHEM 2100", "CHEM2100", "2023-2024 Semester 1", "2023-2024Semester1"),
)


@pytest.fixture()
def run(tmp_path):
    """One corpus, one `--label`, two courses on two calendars, two files each."""
    holder = tmp_path / "holder"
    corpus = holder / "corpus"
    corpus.mkdir(parents=True)
    for stem, code, _, term, _ in COURSES:
        for index in range(2):
            (corpus / f"{stem} syllabus {index}.txt").write_text(
                SYLLABUS.format(code=code, term=term), encoding="utf-8")
    database = holder / "plan.sqlite"
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=out)
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def _values(conn, field_key):
    return {row["canonical_value"]: json.loads(row["raw_variants"])
            for row in conn.execute(
                'SELECT canonical_value, raw_variants FROM "values" '
                "WHERE field_key = ? ORDER BY canonical_value", (field_key,))}


def _final_tree(conn):
    """The nodes of the LAST plan version this run wrote.

    A run writes a plan version per refinement pass and every pass keeps its own
    nodes, so reading `tree_nodes` whole would count one folder several times. The
    last version is the tree the person is shown.
    """
    latest = conn.execute(
        "SELECT plan_version_id FROM tree_nodes ORDER BY rowid DESC LIMIT 1"
    ).fetchone()["plan_version_id"]
    return list(conn.execute(
        "SELECT * FROM tree_nodes WHERE plan_version_id = ? ORDER BY rowid",
        (latest,)))


def test_both_courses_settle_a_term_and_the_new_form_is_one_of_them(run):
    """The premise. If this fails the corpus has stopped exercising the ruling and
    everything below is measuring nothing -- the failure mode `84` §5.3 names."""
    assert set(_values(run, "term")) == {"Fall2024", "2023-2024Semester1"}
    assert set(_values(run, "subject")) == {"PHYS1401", "CHEM2100"}


def test_each_terms_own_spelling_survives_the_run(run):
    """§14.2: "The original spelling is preserved alongside the normalized
    identity." Asserted on a real run because `facts.date_facts` is the only writer
    and nothing between it and the database was hand-assembled here.

    The canonical form is what a folder is called and the raw is what the document
    printed; a person asked to confirm `2023-2024Semester1` is being asked about a
    word their syllabus never used, and this column is the only place the word they
    did use still exists.
    """
    assert _values(run, "term") == {
        "Fall2024": ["Fall 2024"],
        "2023-2024Semester1": ["2023-2024 Semester 1"],
    }


def test_the_two_calendars_do_not_merge_into_one_semester_level(run):
    """TWO `Semester` folders, and the level is the one the library binds
    `cycle_period` to.

    Read off `dimension_role` rather than off the labels, so a run that happened to
    put those two strings somewhere else in the tree cannot satisfy it.
    """
    semester = [node for node in _final_tree(run)
                if node["dimension_role"] == "cycle_period"]

    assert [node["dimension"] for node in semester] == ["term", "term"]
    assert sorted(node["display_label"] for node in semester) == [
        "2023-2024Semester1", "Fall2024"]


def test_each_course_sits_under_its_own_term(run):
    """The binding itself: the Semester level over each course is the term THAT
    COURSE's files carry.

    This is the assertion that would fail if the term were read off the group. Both
    courses are in one accepted group -- one per `--label` -- so a group-grain term
    is a disagreement, and the person loses both folders rather than getting the
    wrong one. Either way `CHEM2100` would not be under `2023-2024Semester1`.
    """
    nodes = _final_tree(run)
    by_id = {node["node_id"]: node for node in nodes}

    for _, _, course, _, term in COURSES:
        node = next(one for one in nodes if one["display_label"] == course)
        parent = by_id[node["parent_node_id"]]
        assert parent["display_label"] == term, (
            f"{course} was filed under {parent['display_label']!r} "
            f"rather than {term!r}")
        assert parent["dimension"] == "term"


def test_no_file_reaches_the_other_courses_term(run):
    """The discriminating twin. Keeping two folders is worth nothing if the files
    are split across them: a person would open `Fall2024` and find the chemistry
    course inside it, which is worse than one merged folder because it looks
    right."""
    nodes = _final_tree(run)
    by_id = {node["node_id"]: node for node in nodes}
    course_nodes = [one for one in nodes if one["dimension"] == "subject"]

    parents = {one["display_label"]: by_id[one["parent_node_id"]]["display_label"]
               for one in course_nodes}
    assert parents == {"PHYS1401": "Fall2024",
                       "CHEM2100": "2023-2024Semester1"}
