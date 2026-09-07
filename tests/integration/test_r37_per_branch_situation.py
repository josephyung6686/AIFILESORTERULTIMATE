# tests/integration/test_r37_per_branch_situation.py
"""`104` R-37 with R-100: the situation is answered per top-level branch.

A run used to answer ONE situation for every file in the folder, so site A asked
the coursework fields -- `subject`, `term`, `work_type` -- of every file. On the
owner's corpus 60 of 83 model calls went to files that are not coursework, and the
refused answers said so (`application/pdf`, `notebook`, `survey`, `Research
Paper` for `work_type`); on the person's 52-file walkthrough two cover letters
were filed under `Coursework/Summer2026/cover letter` and a résumé under a course.

The ruling (`104` §15.2): each proposed top-level branch carries its own
situation, derived from the files that ANCHOR it. The anchor is a signal the
deterministic pass already writes -- a validated `work_type` whose term the
library authored for exactly one schema (`syllabus`, `lecture`, `homework` are
academic's; `cover letter` and `resume` are career's) -- and site A asks a
branch's fields only of that branch's files. A file no branch reaches is asked
nothing and is held under the review set its own placement reason names.

**No model runs here.** The loopback stub is `test_local_model_fact_pass`'s, and
it answers by copying from the dossier; what is asserted is which fields each
file was OFFERED, read off the call log, which is the whole of R-100 in calls.
"""
from __future__ import annotations

import importlib.util
import io
import re
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)

HERE = Path(__file__).resolve().parent
SITUATION = "academic.coursework"
LABEL = "Coursework"
MODEL_ID = "stub-qwen3:8b"

#: The coursework fields site A may ask of a file under the coursework branch,
#: less the two `104` §11.2 step 2 routes to the group (`school`, `term`).
COURSEWORK_FIELDS = {"subject", "term", "work_type"}
#: `career.recruiting`'s file-level fields, from the shipped library's own row.
RECRUITING_FIELDS = {"target_employer", "job_title", "recruiting_cycle", "work_type"}

COURSEWORK = ("PHYS 1401 syllabus.txt", "Lecture 08.txt", "PHYS 1401 notes.txt")
COVER_LETTERS = ("Cover letter Acme.txt", "Cover letter Beta.txt")
CAREER = COVER_LETTERS + ("Jane Doe resume.txt", "Job posting Acme.txt")
#: `HW 3` is NOT here: its own word `homework` is academic's, the recogniser's
#: near-miss names the coursework branch, and that reaches it (`00`:56's own
#: example of a file that lacks the course code and still belongs).
HELD = ("survey results.txt",)


def _corpus(root: Path) -> Path:
    """A Downloads folder with two lives in it, and two files in neither.

    The syllabus and the lecture state `PHYS1401`, so they share a course with the
    syllabus anchor; the two cover letters and the résumé carry a validated
    `work_type` the library authored for `career` alone; the job posting carries
    no work-type fact and is reached only through the recogniser's own reading of
    it. `HW 3` states no course and `survey results` matches nothing: neither is
    under either branch, and the ruling holds them rather than asking.
    """
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    files = {
        "PHYS 1401 syllabus.txt":
            "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3. "
            "Lecture Mondays.\n",
        "Lecture 08.txt":
            "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular "
            "momentum.\n",
        "HW 3.txt": "Homework 3\n\nProblem 1. A ball is thrown upward...\n",
        # States its course beside a lecture word, so the rule settles `subject`
        # and leaves `work_type` open: the one coursework file here with a
        # question a model is actually asked.
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
    }
    for name, body in files.items():
        (corpus / name).write_text(body)
    return corpus


def _stub_module():
    spec = importlib.util.spec_from_file_location(
        "local_fact_pass", HERE / "test_local_model_fact_pass.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def stub():
    module = _stub_module()
    with module.StubOllama() as running:
        running.dossier_in = module.dossier_in
        yield running


def _run(corpus: Path, database: Path, *extra: str) -> str:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "t", "--database", str(database), *extra], out=out)
    assert code == 0, out.getvalue()
    return out.getvalue()


def _flat(report: str) -> str:
    """The screen with its wrapping undone, so a sentence can be searched for."""
    return " ".join(report.split())


def _call_log(database: Path) -> dict[str, list[frozenset[str]]]:
    """filename -> the `allowed_vocabulary` of every A_fact call MADE about it.

    Read off the product's own record -- a dossier row joined to the response it
    got -- rather than off the stub's prompts, where the subject is a wire handle
    digested under this run's key. A dossier with no response is a call the gate
    refused or the harness abstained from, and is not a question the model saw.
    """
    import json
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        names = {row[0]: row[1] for row in conn.execute(
            "SELECT file_id, filename FROM files")}
        log: dict[str, list[frozenset[str]]] = {}
        for subject, payload in conn.execute(
                "SELECT d.subject_ref, d.payload FROM llm_dossier d "
                "JOIN llm_response r ON r.dossier_id = d.dossier_id "
                "WHERE d.call_site = 'A_fact' ORDER BY r.rowid"):
            log.setdefault(names.get(subject, subject), []).append(
                frozenset(json.loads(payload).get("allowed_vocabulary", ())))
        return log
    finally:
        conn.close()


def _local(tmp_path, stub, monkeypatch, *extra: str):
    monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
    monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    report = _run(corpus, database, *extra)
    return corpus, database, report


# --- (a) coursework fields reach coursework files and never a cover letter ------


def test_site_a_asks_coursework_fields_only_of_the_coursework_branch(
        tmp_path, stub, monkeypatch):
    _corpus_, database, report = _local(tmp_path, stub, monkeypatch)
    log = _call_log(database)

    asked_of_coursework = frozenset().union(
        *(offered for name in COURSEWORK for offered in log.get(name, ())))
    assert asked_of_coursework & COURSEWORK_FIELDS, (log, report)
    for name in COVER_LETTERS:
        assert all(not (offered & COURSEWORK_FIELDS) for offered in log.get(name, ())), (
            "a cover letter was asked which course it is", name, log[name])
    assert not any(field in offered for name in CAREER
                   for offered in log.get(name, ()) for field in ("subject",)), log


# --- (b) a file no branch reaches makes no call and is held with its reason -------


def test_a_file_no_branch_reaches_is_asked_nothing_and_held_with_its_reason(
        tmp_path, stub, monkeypatch):
    _corpus_, database, report = _local(tmp_path, stub, monkeypatch)
    log = _call_log(database)

    for name in HELD:
        assert name not in log, ("a file no branch reaches was shown to a model",
                                 name, log[name])
    # Named on the fact-pass line, by its reason, and never quietly.
    assert re.search(r"\d+ of \d+ files were not asked anything: none of the "
                     r"folders this run proposes reaches them", _flat(report)), report
    # Held under the review set its OWN placement reason names -- the set the
    # screen already prints, `104` R-115 -- with the survey named in it.
    held_blocks = report.split("Waiting for you to say what these are")
    assert any("survey results.txt" in block and "Held for review" in block
               for block in held_blocks[1:]), report


# --- the branch question, and the files it reaches ------------------------------


def test_an_unsettled_branch_is_proposed_asked_about_and_asked_nothing(
        tmp_path, stub, monkeypatch):
    """`career` has three shipped situations, so the branch's situation is the
    person's to say: the trigger R-37 says never fired, fires, under the heading
    for questions that block, with one `--answer` line per situation."""
    _corpus_, database, report = _local(tmp_path, stub, monkeypatch)
    log = _call_log(database)

    assert "Which of these is career?" in report, report
    blocking = report.split("Questions only you can answer:", 1)[1]
    blocking = blocking.split("You can change how this is organised", 1)[0]
    assert "--answer situation:career=career.recruiting" in blocking, report
    assert "--answer situation:career=career.employment-records" in blocking
    for name in CAREER:
        assert name not in log, ("a file under an unsettled branch was asked", name)
    assert re.search(r"\d+ of \d+ files were not asked anything: they sit under "
                     r"a folder you have not yet said the situation of", _flat(report))
    # The branch is proposed beside the typed one, so the cover letters are no
    # longer under Coursework and the résumé is under no course.
    folders = report.split("Folders in this plan:", 1)[1].split("Files:", 1)[0]
    roots = [line.strip() for line in folders.splitlines()
             if line.startswith("  ") and not line.startswith("    ")]
    assert roots == ["career", "Coursework"], roots
    assert "Coursework/cover letter" not in report
    # And the held group under that branch is told which answers reach it.
    held = [block for block in report.split("Waiting for you to say what these are")
            if "Cover letter Beta.txt" in block]
    assert held and "--answer situation:career=career.recruiting" in held[0], report


# --- (d) the answer is honoured, and reaches that branch's files only ------------


def test_the_per_branch_answer_is_honoured_and_scoped_to_that_branch(
        tmp_path, stub, monkeypatch):
    """R-86's scoping rule: an answer reaches the files its question named.

    Two runs, because `apply_answers` refuses an answer to a question no run
    has asked yet. The second run's career files are asked `career.recruiting`'s
    own fields; the coursework files are still asked coursework's; no career
    field reaches a coursework file and no coursework field reaches a career one.
    """
    corpus, database, first = _local(tmp_path, stub, monkeypatch)
    assert "Which of these is career?" in first
    before = {name: calls for name, calls in _call_log(database).items()}

    report = _run(corpus, database, "--answer", "situation:career=career.recruiting")
    log = _call_log(database)

    assert "Which of these is career?" not in report, report
    asked_of_career = {name: [offered - frozenset().union(*before.get(name, [frozenset()]))
                              for offered in log.get(name, ())]
                       for name in CAREER}
    career_fields = frozenset().union(
        *(offered for name in CAREER for offered in log.get(name, ())))
    assert career_fields and career_fields <= RECRUITING_FIELDS, (career_fields, log)
    assert not (career_fields & {"subject", "term"}), career_fields
    for name in CAREER:
        for offered in log.get(name, ()):
            assert not (offered & {"subject", "term"}), (name, offered)
    for name in COURSEWORK:
        for offered in log.get(name, ()):
            assert offered <= COURSEWORK_FIELDS, (name, offered)
            assert not (offered & (RECRUITING_FIELDS - {"work_type"})), (name, offered)
    # The typed situation still governs the coursework branch: its folders are
    # the coursework levels, and the career branch's are recruiting's.
    assert "Coursework" in report and "career" in report
    del asked_of_career
