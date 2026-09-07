# tests/p10/test_p10_folder_expectations_read_the_corpus_once.py
"""A folder's expectations were read one folder at a time, and each read the corpus.

`settled_values_in_directory` asks, for each destination-eligible field its files
mention, whether the value they agree on DIVIDES the corpus -- and
`_divides_the_corpus` answered by walking every file in `files` and asking P6 for
that file's settled value one at a time. So a corpus of N files with F such fields
and D adopted folders asked D x F x N times, and each ask re-read the asking file's
whole slot: `preferred_fact` reads the file's content hashes, then its facts, then
walks the supersession chain of every row in the slot.

Measured, P8--P11 over a 1,000-file synthetic corpus under cProfile (`104` R-79):
588 invocations of `_divides_the_corpus` making 175,892 `preferred_value_for` calls,
7.8 of 34.5 profiled seconds after R-72's fixes -- and the term that grows fastest,
because D grows with the corpus as well as N.

The answer each folder needs is a property of the CORPUS and not of the folder:
"what does every file settle at this field". That is one read per field, so
`facts.read_surface.preferred_in_field` publishes it and
`settled_values_by_directory` asks it once for every folder in the question.

**What must not change is every answer.** The rule is untouched -- unanimity,
immediate children, destination-eligibility, and the division test -- and
`test_p10_existing_folders.py` is what holds each of those. This file asserts the
growth rate, because a fix that only made each read faster would leave the shape
intact and still pass any wall-clock test on a small corpus; and it pins the
many-folder read to the one-folder read it is built out of, so the two cannot drift.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from evidence_shape.schema import create_evidence_schema
from facts.fields import create_fields

from tree_design.upstream import (
    settled_values_by_directory, settled_values_in_directory,
    settled_values_stated_by_every_file,
)

from p9.test_p9_retrieval import _fact, _file

#: Two corpus sizes, three times apart, each with a folder per five files -- so
#: BOTH the file count and the folder count triple, which is the shape that was
#: quadratic. A quadratic reader does nine times the work between them.
SMALL, LARGE = 20, 60

#: The bar. Generous on purpose: the per-call constant (the roster read, one read
#: per field, the per-file fact reads) is not identical at the two sizes, so the
#: ratio never lands exactly on 3.0.
#:
#: Measured on this corpus, before the fix and after: 968 statements at twenty
#: files and 7,704 at sixty, a ratio of 8.0; then 39 and 103, a ratio of 2.6. The
#: ratio is what this asserts and the absolute counts are why it matters.
LINEAR_ENOUGH = 4.0

#: Five files to a folder. Enough that no folder is refused by the floor ("a set of
#: one is always unanimous") and small enough that the folder count grows with the
#: corpus, which is what makes the old shape quadratic.
PER_FOLDER = 5


@pytest.fixture()
def corpus(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    return conn


def _build(conn, tmp_path, files: int) -> list[str]:
    """A corpus of folders that each agree about something the corpus divides on.

    Every folder's files share one `subject` and one `work_type`, and different
    folders hold different subjects -- so every folder settles a value, and the
    division test says yes rather than short-circuiting on the first file it looks
    at. A corpus where every folder expected nothing would let a reader that gives
    up early pass this file while still being quadratic on a real one.

    `school` is stated by every file identically, so it is the corpus-wide value
    the division test refuses, and it is here to keep the field count honest: the
    reads happen for it too.
    """
    folders: list[str] = []
    for index in range(files):
        group = index // PER_FOLDER
        folder = f"Coursework/course-{group:03d}"
        _file(conn, tmp_path, f"{index:03d}-notes.pdf", folder=folder)
        file_id = _last_file(conn)
        _fact(conn, file_id, field_key="subject", value=f"COURSE{group:03d}",
              run_id=f"run-subject-{index}")
        _fact(conn, file_id, field_key="work_type", value="Notes",
              run_id=f"run-work-{index}")
        _fact(conn, file_id, field_key="school", value="Columbia",
              run_id=f"run-school-{index}")
        if str(tmp_path / folder) not in folders:
            folders.append(str(tmp_path / folder))
    return folders


def _last_file(conn) -> str:
    return conn.execute(
        "SELECT file_id FROM files ORDER BY rowid DESC LIMIT 1").fetchone()[0]


def _statements_for_every_folder(conn, tmp_path, files: int) -> int:
    """Every statement the expectations pass issues, for a whole corpus of folders.

    Counted rather than timed, for the reason the P9 sibling gives: a stopwatch on
    a small corpus cannot tell a faster constant from a better shape. Statements
    rather than calls, because the shape is what the database is asked, and the
    fix moves the same question from many statements into few.
    """
    folders = _build(conn, tmp_path, files)
    counted = 0

    def count(_statement: str) -> None:
        nonlocal counted
        counted += 1

    conn.set_trace_callback(count)
    try:
        settled_values_by_directory(conn, directory_paths=folders)
    finally:
        conn.set_trace_callback(None)
    return counted


def test_a_whole_pass_costs_statements_in_proportion_to_the_corpus(corpus,
                                                                  tmp_path):
    """The item, as a growth rate rather than a stopwatch.

    Two databases, because the two corpora have to be measured separately: sixty
    files in the database that already holds twenty would measure eighty against
    twenty and the ratio would mean nothing.
    """
    from database_agent.db import open_database

    small = _statements_for_every_folder(corpus, tmp_path / "small", SMALL)
    other = open_database(tmp_path / "large.sqlite")
    try:
        create_schema(other)
        create_evidence_schema(other)
        create_fields(other)
        large = _statements_for_every_folder(other, tmp_path / "large", LARGE)
    finally:
        other.close()

    growth = large / small
    assert growth < LINEAR_ENOUGH, (
        f"{SMALL} files in {SMALL // PER_FOLDER} folders cost {small} statements "
        f"and {LARGE} files in {LARGE // PER_FOLDER} folders cost {large}: "
        f"{growth:.1f}x for 3x the corpus. The folder expectations are reading "
        "one file's settled value at a time, so five times the files is "
        "twenty-five times the work and a 5,000-file plan does not finish")


def test_the_corpus_is_read_once_per_field_and_not_once_per_folder(corpus,
                                                                  tmp_path):
    """The claim in its own terms, and the one a growth rate cannot make.

    Three destination-eligible fields and four folders: the reading is fetched
    three times, not twelve, and not three per folder.
    """
    from facts import read_surface

    folders = _build(corpus, tmp_path, SMALL)
    assert len(folders) == SMALL // PER_FOLDER
    asked: list[str] = []
    original = read_surface.preferred_in_field

    def counting(conn, *, field_key):
        asked.append(field_key)
        return original(conn, field_key=field_key)

    import tree_design.upstream as upstream

    upstream.preferred_in_field = counting
    try:
        settled_values_by_directory(corpus, directory_paths=folders)
    finally:
        upstream.preferred_in_field = original

    assert sorted(asked) == sorted(set(asked)), (
        f"a field was read more than once: {asked}")
    assert set(asked) == {"school", "subject", "work_type"}, asked


def test_the_many_folder_read_answers_what_the_one_folder_read_answers(corpus,
                                                                      tmp_path):
    """The fork, pinned. `settled_values_in_directory` is now built out of the
    many-folder read, and every test in `test_p10_existing_folders.py` goes through
    it -- but a caller could later give the bulk form its own rule, so the two are
    compared here over a corpus with folders that agree, a folder of one, and a
    folder whose files disagree.
    """
    folders = _build(corpus, tmp_path, SMALL)
    alone = str(tmp_path / "Coursework" / "solo")
    _file(corpus, tmp_path, "solo-notes.pdf", folder="Coursework/solo")
    _fact(corpus, _last_file(corpus), field_key="subject", value="SOLO001",
          run_id="run-solo")
    mixed = str(tmp_path / "Coursework" / "mixed")
    for index, subject in enumerate(("MIX001", "MIX002")):
        _file(corpus, tmp_path, f"mixed-{index}.pdf", folder="Coursework/mixed")
        _fact(corpus, _last_file(corpus), field_key="subject", value=subject,
              run_id=f"run-mixed-{index}")
    asked = [*folders, alone, mixed, str(tmp_path / "never-scanned")]

    for stated_by_every_file in (False, True):
        together = settled_values_by_directory(
            corpus, directory_paths=asked,
            stated_by_every_file=stated_by_every_file)
        for path in asked:
            one = settled_values_in_directory(
                corpus, directory_path=path,
                stated_by_every_file=stated_by_every_file)
            assert together[path] == one, (path, stated_by_every_file)

    assert settled_values_by_directory(corpus, directory_paths=()) == {}


def test_the_comparison_above_rests_on_folders_that_answer_differently(corpus,
                                                                      tmp_path):
    """The teeth. If every folder in that corpus expected nothing, or all expected
    the same thing, the comparison would pass for the wrong reason."""
    folders = _build(corpus, tmp_path, SMALL)
    answers = settled_values_by_directory(corpus, directory_paths=folders)
    subjects = {path: [value.canonical_value for value in values
                       if value.field_ref == "subject"]
                for path, values in answers.items()}
    assert all(len(found) == 1 for found in subjects.values()), subjects
    assert len({found[0] for found in subjects.values()}) == len(folders)
    schools = {value.field_ref for values in answers.values() for value in values}
    assert "school" not in schools, (
        "every file in this corpus is Columbia's, so expecting Columbia "
        "distinguishes a folder from none of them and the division test refuses it")


def test_the_coverage_question_still_reaches_the_same_answer(corpus, tmp_path):
    """`settled_values_stated_by_every_file` is a different question and it must
    keep coming out different: a folder where one file names a kind and the other
    is silent EXPECTS that kind but was not MADE for it."""
    folders = _build(corpus, tmp_path, SMALL)
    leading = str(tmp_path / "Coursework" / "desk")
    for index in range(2):
        _file(corpus, tmp_path, f"desk-{index}.pdf", folder="Coursework/desk")
        _fact(corpus, _last_file(corpus), field_key="subject", value="DESK001",
              run_id=f"run-desk-{index}")
    _fact(corpus, _last_file(corpus), field_key="work_type", value="Resume",
          run_id="run-desk-kind")

    expects = settled_values_in_directory(corpus, directory_path=leading)
    made_for = settled_values_stated_by_every_file(corpus, directory_path=leading)
    assert "Resume" in [value.canonical_value for value in expects]
    assert "Resume" not in [value.canonical_value for value in made_for]
    assert folders
