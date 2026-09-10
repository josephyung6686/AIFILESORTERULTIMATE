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
COURSEWORK_FIELDS = {"subject", "term", "work_type", "school"}  # `school` since R-131: an anchor is asked the holder's school
#: `career.recruiting`'s file-level fields, from the shipped library's own row.
RECRUITING_FIELDS = {"target_employer", "job_title", "recruiting_cycle", "work_type"}

COURSEWORK = ("PHYS 1401 syllabus.txt", "Lecture 08.txt", "PHYS 1401 notes.txt")
COVER_LETTERS = ("Cover letter Acme.txt", "Cover letter Beta.txt")
CAREER = COVER_LETTERS + ("Jane Doe resume.txt", "Job posting Acme.txt")
#: `104` R-140. A file NO branch reaches is the default branch's and is asked
#: its questions: the survey matches nothing of either life. Only a file TWO
#: branches reach is held: `two things` says academic's words and career's
#: words in equal number, the recogniser ties, and no fact decides.
DEFAULTED = ("survey results.txt",)
HELD = ("two things.txt",)


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
        # One academic word (`curriculum`, `cohort`) for one career word
        # (`scope of work`, `retainer`), no course code, no kind word in the
        # name: the recogniser ties `academic`/`career` and no fact decides.
        "two things.txt":
            "Two things\n\nThe curriculum for this cohort, and the scope of work "
            "for the retainer.\n",
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


# --- (b) no branch: the default's questions; two branches: held with its reason --


def test_a_file_no_branch_reaches_is_asked_the_default_branchs_questions(
        tmp_path, stub, monkeypatch):
    """`104` R-140. The person said what this folder is; a file nothing else
    claims is asked that, and the model may still decline every field. Before
    this ruling 147 of the owner's 199 files met no model at all."""
    _corpus_, database, report = _local(tmp_path, stub, monkeypatch)
    log = _call_log(database)

    for name in DEFAULTED:
        offered = frozenset().union(*log.get(name, [frozenset()]))
        assert offered and offered <= COURSEWORK_FIELDS, (name, log, report)
    assert "none of the folders this run proposes reaches them" not in _flat(report)


def test_a_file_two_branches_reach_is_asked_nothing_and_held_with_its_reason(
        tmp_path, stub, monkeypatch):
    _corpus_, database, report = _local(tmp_path, stub, monkeypatch)
    log = _call_log(database)

    for name in HELD:
        assert name not in log, ("a file two branches reach was shown to a model",
                                 name, log[name])
    # Named on the fact-pass line, by its reason, and never quietly.
    assert re.search(r"1 of \d+ files were not asked anything: two of the "
                     r"folders this run proposes reach them equally", _flat(report)), report
    # Held under the review set its OWN placement reason names -- the set the
    # screen already prints, `104` R-115 -- with the file named in it.
    held_blocks = report.split("Waiting for you to say what these are")
    assert any("two things.txt" in block and "Held for review" in block
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
    # `104` §18.2 gap 14 prints the group block between the folder list and
    # "Files:"; the folder list ends at whichever of the two comes first.
    folders = report.split("Folders in this plan:", 1)[1]
    folders = folders.split("Groups put to a model as groups:", 1)[0].split("Files:", 1)[0]
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


# --- the default branch keeps its course and term levels on a multi-branch run ---

#: Two courses with terms, one course whose every file two branches reach, and
#: the career files. Offline; no stub. `MATH 2000` is the reverted merge's case:
#: no kind word in any name, so no anchor; its course code beside `instructor`
#: so P9 groups it on `subject`; three career terms so the recogniser reads it
#: as `career` and both branches reach it. Held, and still coursework's to file.
TWO_LIVES = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n",
    "PHYS 1401 lecture 08.txt":
        "PHYS 1401 Lecture 08\n\nSpring 2026. Torque and angular momentum.\n",
    "PHYS 1401 homework 3.txt": "PHYS 1401 Homework 3\n\nSpring 2026. Due Friday.\n",
    "PHYS 1401 midterm exam.txt": "PHYS 1401 Midterm Exam\n\nSpring 2026. Closed book.\n",
    "ECON 2010 syllabus.txt":
        "ECON 2010 Syllabus\n\nFall 2025. Instructor: Prof. Ng. Credits: 3.\n",
    "ECON 2010 lecture 02.txt": "ECON 2010 Lecture 02\n\nFall 2025. Aggregate demand.\n",
    "ECON 2010 homework 1.txt": "ECON 2010 Homework 1\n\nFall 2025. Elasticity problems.\n",
    "ECON 2010 final exam.txt": "ECON 2010 Final Exam\n\nFall 2025. Two hours.\n",
    "MATH 2000 week 1.txt":
        "Prepared by the TA. Deliverable for MATH 2000. Instructor: Dr. Wu. "
        "Milestone one. Fall 2025.\n",
    "MATH 2000 week 2.txt":
        "Prepared by the TA. Deliverable for MATH 2000. Instructor: Dr. Wu. "
        "Milestone two. Fall 2025.\n",
    "MATH 2000 week 3.txt":
        "Prepared by the TA. Deliverable for MATH 2000. Instructor: Dr. Wu. "
        "Milestone three. Fall 2025.\n",
    "HW 3.txt": "Homework 3\n\nProblem 1. A ball is thrown upward...\n",
    "Cover letter Acme.txt":
        "Cover Letter\n\nDear Hiring Manager,\nI am writing to apply for the "
        "Software Engineer position at Acme Corp. My resume is attached.\n",
    "Cover letter Beta.txt":
        "Cover letter\n\nDear Recruiting Team at Beta Ltd,\nPlease consider my "
        "application for the Data Analyst role. Job title: Data Analyst.\n",
    "Jane Doe resume.txt":
        "Jane Doe\nCurriculum Vitae / Resume\n\nWork experience\n2024-2026 "
        "Software Engineer, Acme Corp.\n",
    "Job posting Acme.txt":
        "Job description: Software Engineer\nAcme Corp is hiring. Job title: "
        "Software Engineer. Approved job description.\n",
    "survey results.txt":
        "Survey results\n\nQuestion 1: 42% agree. Question 2: 58% disagree.\n",
}

#: What the coursework branch filed BEFORE the per-branch change (measured at
#: ac712bb on this corpus): every placed coursework file under its term and its
#: course. The ruling adds a branch beside this; it takes nothing from it.
COURSEWORK_CHAINS_BEFORE = {
    "Coursework/Spring2026/PHYS1401/syllabus": 1,
    "Coursework/Spring2026/PHYS1401/lecture": 1,
    "Coursework/Spring2026/PHYS1401/homework": 1,
    "Coursework/Spring2026/PHYS1401/exam": 1,
    "Coursework/Fall2025/ECON2010/syllabus": 1,
    "Coursework/Fall2025/ECON2010/lecture": 1,
    "Coursework/Fall2025/ECON2010/homework": 1,
    "Coursework/Fall2025/ECON2010/exam": 1,
    "Coursework/Fall2025/MATH2000": 3,
}


def _chains(database: Path) -> dict[str, int]:
    """Place decisions of the last plan version, by destination chain."""
    from collections import Counter

    from placement.store import decisions_for_plan
    from tree_design.store import nodes_for_version
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        plan_version = conn.execute(
            "SELECT plan_version FROM placement_decisions "
            "ORDER BY rowid DESC LIMIT 1").fetchone()[0]
        nodes = {node.node_id: node for node in nodes_for_version(conn, plan_version)}

        def chain(node_id: str) -> str:
            parts: list[str] = []
            while node_id in nodes:
                parts.append(nodes[node_id].display_label)
                node_id = nodes[node_id].parent_node_id
            return "/".join(reversed(parts))

        return dict(Counter(
            chain(decision.destination.node_id)
            for decision in decisions_for_plan(conn, plan_version=plan_version)
            if decision.outcome == "place"))
    finally:
        conn.close()


def test_the_default_branch_keeps_its_course_and_term_levels_beside_a_second_branch(
        tmp_path):
    """The pin the reverted merge lacked (`104` R-37, merge 8b9280d reverted).

    On the owner's corpus the coursework branch came out flat by kind --
    `Coursework/exam` 7, `Coursework/homework` 3 -- because the groups of the
    held files were not accepted and the course and term levels went with them.
    Here the same shape: `MATH 2000`'s three files are held (two branches reach
    them), and the branch must still file them under `Fall2025/MATH2000`, with
    every other coursework file exactly where it went before, and `career`
    standing beside `Coursework` rather than inside it.
    """
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in TWO_LIVES.items():
        (corpus / name).write_text(body)
    database = tmp_path / "holder" / "plan.sqlite"
    report = _run(corpus, database)

    chains = _chains(database)
    coursework = {chain: count for chain, count in chains.items()
                  if chain.startswith("Coursework")}
    assert coursework == COURSEWORK_CHAINS_BEFORE, (chains, report)
    # `104` §18.2 gap 14 prints the group block between the folder list and
    # "Files:"; the folder list ends at whichever of the two comes first.
    folders = report.split("Folders in this plan:", 1)[1]
    folders = folders.split("Groups put to a model as groups:", 1)[0].split("Files:", 1)[0]
    roots = [line.strip() for line in folders.splitlines()
             if line.startswith("  ") and not line.startswith("    ")]
    assert roots == ["Coursework", "career"] or roots == ["career", "Coursework"], roots
    assert not any(chain.startswith("Coursework") and
                   ("cover letter" in chain or "resume" in chain)
                   for chain in chains), chains
