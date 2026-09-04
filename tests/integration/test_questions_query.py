# tests/integration/test_questions_query.py
"""The question pass must ask about exactly the files it used to ask about.

`cli.files_with_observations` replaced `SELECT DISTINCT file_id, content_hash FROM
evidence` -- a full pass over 365,690 rows to produce 200 -- with the same question
asked of `extraction_runs`, which holds 425. That is a 900-fold difference on a real
corpus and it was the single largest cost in a 200-file run, but it is only allowed
if the two formulations name the SAME FILES. A faster question pass that quietly
stops asking about one file is worse than a slow one.

So this file does not test the speed. It runs the real pipeline over a real folder
and holds the two queries against each other on the database that run produced.
"""
from pathlib import Path

import pytest

import cli
from database_agent.db import open_database

pytest.importorskip("pdfminer", reason="the real pipeline needs its readers")


def _corpus(tmp_path: Path) -> Path:
    """Several formats, because the equivalence has to hold for every extractor.

    A run that only ever wrote `pdf.text` rows could not show that an OCR run, an
    archive manifest or a filesystem record keeps its `(file_id, content_hash)` pair
    in both tables.
    """
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "notes.txt").write_text(
        "PHYS 1401 lecture notes. Contact eric@example.edu about the midterm.")
    (root / "grades.csv").write_text("student,course,grade\nA,PHYS1401,91\n")
    (root / "readme.md").write_text("# Syllabus\n\nWeek one covers kinematics.\n")
    (root / "empty-ish.txt").write_text("x")
    # A file that produces a run and NO observations, which is the case the
    # `observation_count > 0` predicate exists for. §2.4 calls this `failed`: a
    # reader ran and raised, which is a true statement about the file and not a
    # reason to ask its owner a question about it.
    (root / "truncated.pdf").write_bytes(b"%PDF-1.4\nnot actually a pdf\n")
    return root


def _run(tmp_path: Path, root: Path):
    database = tmp_path / "plan.sqlite"
    with open(tmp_path / "out.txt", "w") as sink:
        code = cli.main([str(root), "--situation", "academic.coursework",
                         "--label", "Coursework", "--database", str(database)],
                        out=sink)
    assert code == 0, (tmp_path / "out.txt").read_text()[-2000:]
    return open_database(database)


def test_the_fast_query_names_exactly_the_files_the_slow_one_named(tmp_path):
    """The whole claim, on a database a real run wrote.

    Sets and not counts: two queries can agree on how many files there are and
    disagree about which, and the second failure is the one that silently drops a
    person's file out of the questions they are asked.
    """
    conn = _run(tmp_path, _corpus(tmp_path))
    try:
        slow = {(row[0], row[1]) for row in conn.execute(
            "SELECT DISTINCT file_id, content_hash FROM evidence")}
        fast = set(cli.files_with_observations(conn))
        assert slow, "the run produced no evidence at all; this proves nothing"
        assert fast == slow, (
            "the question pass would ask about a different set of files: "
            f"missing {slow - fast}, extra {fast - slow}")
    finally:
        conn.close()


def test_a_run_with_no_observations_is_not_counted_as_a_file_with_some(tmp_path):
    """The half a bare `SELECT DISTINCT ... FROM extraction_runs` gets wrong.

    §2.4 gives a run three ways to produce nothing: `unsupported` (no reader
    exists), `failed` (a reader raised) and `dataless` (the file was never opened).
    None of them writes an observation, and a pair whose only run is one of those is
    NOT in `evidence` -- so without the predicate the question pass starts asking
    about files that have nothing to answer with.

    The row is written directly rather than fished out of a corpus, and that is
    deliberate. The first version of this test looked for such a run among real
    files and found none: every scanned file also gets a `filesystem.record` run,
    which always writes observations, so the pair is in `evidence` anyway and
    dropping the predicate changed nothing. The test passed with the predicate
    removed, which made it worthless. This writes the case the predicate exists for.
    """
    conn = _run(tmp_path, _corpus(tmp_path))
    try:
        template = conn.execute(
            "SELECT * FROM extraction_runs LIMIT 1").fetchone()
        row = dict(template)
        row["run_id"] = "run-with-nothing-in-it"
        row["file_id"] = "a-file-whose-bytes-were-never-read"
        row["content_hash"] = "0" * 64
        row["observation_count"] = 0
        row["completeness"] = "unsupported"
        conn.execute(
            f"INSERT INTO extraction_runs ({','.join(row)}) "
            f"VALUES ({','.join('?' * len(row))})", tuple(row.values()))

        with_evidence = {(r[0], r[1]) for r in conn.execute(
            "SELECT DISTINCT file_id, content_hash FROM evidence")}
        assert ("a-file-whose-bytes-were-never-read", "0" * 64) not in with_evidence
        assert set(cli.files_with_observations(conn)) == with_evidence, (
            "a run that produced no observations was counted as a file with some")
    finally:
        conn.close()
