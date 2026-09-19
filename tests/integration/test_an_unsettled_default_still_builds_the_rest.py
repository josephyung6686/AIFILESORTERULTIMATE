# tests/integration/test_an_unsettled_default_still_builds_the_rest.py
"""`00` amendment 25, read to the end of its consequence.

The owner ratified that the unjudged default has no folders beneath IT. What the
code does is end the whole run: `downstream` returns `None` whenever no situation
is settled (`cli.py`'s `if not of_the_run:`), and `of_the_run` is filled only when
`partition.default.settled`. So a corpus where the person has answered for ONE
branch and not for the default yields the question screen and NO TREE AT ALL --
the branch they DID answer for loses its folders too.

**Measured on this corpus before the fix, with the same flags in both runs:**

```
--situation academic.coursework --accept-groups   18 nodes,  4 acceptances, 20 placements
--answer situation:career=...   --accept-groups    0 nodes,  0 acceptances,  0 placements
```

The second run has a SETTLED career branch -- its question is gone from the screen,
which is how the run says it settled -- and still builds nothing.

**What must stay true after the fix, and each is a test below:** the settled branch
gets its tree; the unsettled default's files are still there and are not filed into
folders invented for them (that is the ratified half of amendment 25); and the
question is still printed, because the fix must not buy a tree by swallowing it.

**No model runs here.** Every branch settles or fails to settle on the person's own
`--answer` and the deterministic pass, which is why this corpus can pin the seam
without a stub: site G is never reached under `offline`.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: `test_r37_per_branch_situation`'s two-life corpus. The cover letters and the
#: résumé carry a validated `work_type` the library authored for `career` alone,
#: so a career branch is proposed; the syllabus and the lecture state a course, so
#: an academic branch is. `academic` is the majority kind, so it is the DEFAULT --
#: and amendment 25 says the default is settled by the person's answer at its own
#: scope and by nothing else.
TWO_LIVES = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3. "
        "Lecture Mondays.\n",
    "Lecture 08.txt":
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular "
        "momentum.\n",
    "HW 3.txt": "Homework 3\n\nProblem 1. A ball is thrown upward...\n",
    "PHYS 1401 notes.txt":
        "PHYS 1401\nNotes from the lecture on torque. Reading for next week.\n",
    "Cover letter Acme.txt":
        "Cover Letter\n\nDear Hiring Manager,\nI am writing to apply for the "
        "Software Engineer position at Acme Corp. My resume is attached. I "
        "look forward to an interview.\n",
    "Cover letter Beta.txt":
        "Cover letter\n\nDear Recruiting Team at Beta Ltd,\nPlease consider my "
        "application for the Data Analyst role. Job title: Data Analyst. "
        "References available.\n",
    "Job posting Acme.txt":
        "Job description: Software Engineer\nAcme Corp is hiring. Job title: "
        "Software Engineer. Salary range. Apply by 1 June 2026. Approved job "
        "description.\n",
    "Jane Doe resume.txt":
        "Jane Doe\nCurriculum Vitae / Resume\n\nWork experience\n2024-2026 "
        "Software Engineer, Acme Corp.\nEducation\nBSc Computer Science, "
        "Columbia University, 2022\n",
    "survey results.txt":
        "Survey results\n\nQuestion 1: 42% agree. Question 2: 58% disagree.\n",
    "two things.txt":
        "Two things\n\nThe curriculum for this cohort, and the scope of work "
        "for the retainer.\n",
}

#: The person's answer at ONE branch's own scope. The default is left alone: that
#: is the whole point of the fixture.
ANSWER_CAREER = ("--answer", "situation:career=career.recruiting")


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in TWO_LIVES.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "t", "--database", str(database),
                     *extra], out=out)
    return code, out.getvalue()


def _counts(database: Path) -> dict[str, int]:
    """The three tables that say whether a run built anything."""
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return {table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                for table in ("tree_nodes", "group_acceptance",
                              "placement_decisions")}
    finally:
        conn.close()


def _flat(report: str) -> str:
    return " ".join(report.split())


@pytest.fixture
def answered_one_branch(tmp_path):
    """Run once so the questions exist, then answer the career branch only.

    `--answer` refuses an answer to a question no run has asked, so the first run
    is what makes the second one legal -- the same two-step every other test of
    this gesture uses.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    _run(corpus, database)
    code, report = _run(corpus, database, *ANSWER_CAREER, "--accept-groups")
    return code, report, database


def test_a_settled_branch_is_still_built_when_the_default_is_unsettled(
        answered_one_branch):
    """THE DEFECT. The career branch is settled and gets nothing.

    SABOTAGE: restore `return None` under `if not of_the_run:` for a partition that
    has a settled branch. Red here, and the product cannot be demonstrated on any
    corpus whose owner has not answered for the whole folder.
    """
    code, report, database = answered_one_branch
    counts = _counts(database)

    assert code == 0, report
    assert counts["tree_nodes"] > 0, (
        "a settled branch has folders, and this run built none: " f"{counts}")
    assert counts["placement_decisions"] > 0, (
        "a settled branch's files reach a destination: " f"{counts}")


def test_the_question_for_the_unsettled_default_is_still_printed(
        answered_one_branch):
    """GREEN BEFORE THE FIX, and it is here so the fix cannot buy a tree by
    swallowing the question. The default is `academic`; nobody has answered for it.
    """
    _code, report, _database = answered_one_branch
    flat = _flat(report)

    assert "Which of these is academic?" in flat, report
    assert "--answer situation:academic=" in flat, report


def test_no_file_is_dropped_when_the_default_is_unsettled(answered_one_branch):
    """COVERAGE IS SACRED. Ten files went in; the coverage block accounts for ten.

    Read off the run's own arithmetic line rather than a count this test computes,
    because that line is what the person is shown and is the thing that must be
    true.
    """
    _code, report, _database = answered_one_branch

    assert "Coverage: 10 files indexed." in report, report
    assert "= 10, and every file is on exactly one line above." in report, report
