# tests/integration/test_the_situation_is_optional.py
"""The owner's ruling of 11 Sep 2026: `--situation` is not demanded of a person.

`00` Amendments of 2026-09-11 item 2, `104` §18.43, rows R-23 and R-88, the
audit's item 5: "One whole-disk `--situation` and `--label` demanded before a
file is opened." `66`:461 -- §14, "Ask only when needed" -- says the first run
asks for no profession, no household, nothing "before the user has a reason to
provide them", and asks a narrow, evidence-linked question only where a repeated
ambiguity actually prevents a useful answer. The parser contradicted it outright:
two arguments, both required, both about the whole disk, both demanded before a
single byte was read. On the person's 52-file walkthrough that is what filed two
cover letters under `Coursework/Summer2026/cover letter`.

The ruling: the flag is optional; each branch's situation comes from the
evidence; a typed one still overrides for the whole run.

**What this module pins, and what it does not.** The run now starts with nothing
typed, opens the folder, names the default branch's SCHEMA from the corpus's own
evidence -- the anchors first, the recogniser's readings second -- and settles
that branch's situation by the same rule every other branch already has: the
person's own answer at the branch's scope, or the library's single situation for
that schema, or unsettled with its candidates recorded as a question. A typed
`--situation` overrides the lot.

**The gap the ruling leaves open is named in a strict xfail below.** Site G names
a SCHEMA -- `SituationOutcome.recognised` and `.candidates` are `SCHEMA_IDS`, and
`ask_the_situation`'s own shortlist is schemas -- while a branch needs one of the
N SITUATIONS the library carries under that schema, and it carries at least two
under every one of the nineteen. R-88's own words name the settler: "per-branch
situation, MODEL DECIDING FROM VALID OPTIONS", and `104` §11.2 step 4 is the
standing ruling that the person, or a model from valid options, decides -- never
a rule picking the first of twenty-six. So until that model call exists, an
untyped run records one narrow question per branch and stops with them, which is
`66` §14 exactly.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path

import pytest

import cli

#: All one life, and every kind word in it is academic's alone, so the anchors
#: name one schema outright: `syllabus`, `lecture`, `homework` and `exam` are
#: `104` R-37's own examples of terms the compiled release authors for `academic`
#: and for nothing else.
COURSEWORK = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n",
    "PHYS 1401 lecture 08.txt":
        "PHYS 1401 Lecture 08\n\nSpring 2026. Torque and angular momentum.\n",
    "PHYS 1401 homework 3.txt":
        "PHYS 1401 Homework 3\n\nSpring 2026. Due Friday.\n",
    "PHYS 1401 midterm exam.txt":
        "PHYS 1401 Midterm Exam\n\nSpring 2026. Closed book.\n",
}


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in COURSEWORK.items():
        (corpus / name).write_text(body)
    return corpus


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--user", "t", "--database", str(database),
                     *extra], out=out)
    return code, out.getvalue()


def _flat(report: str) -> str:
    return " ".join(report.split())


# --- the run starts, and the question comes after the folder is read ------------


def test_a_run_with_no_situation_starts_and_opens_the_folder(tmp_path):
    """The parser no longer refuses, and the scan happens before anything asks.

    The refusal that ends this run is about the CORPUS -- which situation these
    folders are -- and it is reached only after the folder has been read. That is
    the whole of `66` §14 in one run.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)

    assert "the following arguments are required" not in report, report
    assert code == 2, report
    # THE FILES WERE OPENED, read off the run's own index rather than off a
    # sentence on the screen: every file of the corpus has a row, and rows are
    # written by the scan.
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        indexed = {row[0] for row in conn.execute("SELECT filename FROM files")}
    finally:
        conn.close()
    assert indexed == set(COURSEWORK), indexed
    assert "the folder was read" in _flat(report), report


def test_the_question_names_the_branch_the_files_and_what_to_type(tmp_path):
    """`66` §14: the visible context, the precise consequence, and the gesture."""
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")

    assert code == 2, report
    flat = _flat(report)
    # The branch is named after the kind of life its files turned out to be --
    # the library's own word, and the name every other branch already carries --
    # and it is the QUESTION's own three parts that print: the prompt, the
    # evidence, and one typable line per option.
    assert "Which of these is academic?" in flat, report
    assert f"{len(COURSEWORK)} files sit under academic" in flat, report
    assert "--answer situation:academic=academic.coursework" in flat, report
    # And the whole-folder override is offered beside the per-branch answer.
    assert "--situation" in flat, report


def test_the_branch_question_is_recorded_so_the_answer_can_be_given(tmp_path):
    """The refusal is raised AFTER the question is written down.

    `apply_answers` refuses an answer to a question no run has asked, so a
    refusal raised before the question was recorded would print a gesture the
    next invocation would reject.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)
    assert code == 2, report

    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        asked = [row[0] for row in conn.execute(
            "SELECT question_id FROM structural_questions")]
    finally:
        conn.close()
    assert any(question.endswith(":academic") for question in asked), asked


# --- the answer is honoured, and the run then does its work ---------------------


def test_answering_the_branch_lets_the_next_run_through(tmp_path):
    """Two runs, the second carrying the answer the first asked for."""
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    first_code, first = _run(corpus, database)
    assert first_code == 2, first

    code, report = _run(corpus, database,
                        "--answer", "situation:academic=academic.coursework")
    assert code == 0, report
    assert "the folder was read, and these are the folders" not in _flat(report)
    # The folder is called after the life its files belong to, which is what
    # every other branch this run proposes is already called.
    assert "academic" in report, report


def test_a_label_with_no_situation_is_still_the_persons_own_name(tmp_path):
    """The two flags became optional together and neither depends on the other.

    A person who named the folder and not the life gets the folder they named:
    the branch's question is asked under THEIR name, and the answer they are told
    to type is the one the run will look for.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database, "--label", "Coursework")
    assert code == 2, report
    assert "--answer situation:Coursework=academic.coursework" in _flat(report), (
        report)

    code, report = _run(corpus, database, "--label", "Coursework",
                        "--answer", "situation:Coursework=academic.coursework")
    assert code == 0, report
    assert "Coursework" in report, report


# --- a typed situation still governs the whole run ------------------------------


def test_a_typed_situation_still_governs_the_whole_run(tmp_path):
    """Unchanged, byte for byte: the typed answer is read where it always was."""
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite",
                        "--situation", "academic.coursework",
                        "--label", "Coursework")
    assert code == 0, report
    assert "Coursework" in report, report
    assert "the folder was read, and these are the folders" not in _flat(report)


def test_a_typed_situation_with_no_label_names_the_folder_after_the_schema(
        tmp_path):
    """`--label` follows `--situation`: optional, and derived from the library.

    What `--label` supplies is the TOP-LEVEL BRANCH's name. Every other branch a
    run proposes is already called after its schema (`branch_situation.Branch.
    label`), so the answer for the default branch is the same word, and no name
    this file invented reaches somebody's disk.
    """
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite",
                        "--situation", "academic.coursework")
    assert code == 0, report
    assert "academic" in report, report


def test_a_typed_situation_that_names_nothing_still_refuses_before_the_scan(
        tmp_path):
    """The typo refusal is unmoved: it is about the ARGUMENT, not the corpus."""
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite",
                        "--situation", "academic.courswork")
    assert code == 2, report
    assert "names no situation the shipped template library recognises" in _flat(
        report), report
    # And nothing was indexed: the argument is refused before the folder is
    # opened, which is where an argument refusal belongs.
    conn = sqlite3.connect(
        f"file:{tmp_path / 'holder' / 'plan.sqlite'}?mode=ro", uri=True)
    try:
        indexed = conn.execute("SELECT count(*) FROM files").fetchone()[0]
    finally:
        conn.close()
    assert indexed == 0, indexed


# --- the gap the ruling leaves open --------------------------------------------


@pytest.mark.xfail(strict=True, reason=(
    "OWNER-OWED. Site G names a SCHEMA and not a situation: `SituationOutcome."
    "recognised` and `.candidates` are `facts.domains.SCHEMA_IDS`, and "
    "`ask_the_situation`'s shortlist is built from them. A branch needs one of "
    "the N SITUATIONS the library carries under that schema, and it carries at "
    "least two under every one of the nineteen (28 for `creative`, 11 for "
    "`academic`, 3 for `career`), so no branch is ever settled by the library "
    "alone. R-88's own words name the settler -- 'per-branch situation, model "
    "deciding from valid options' -- and `104` §11.2 step 4 is the standing "
    "ruling: the person, or a model from valid options, decides, never a rule "
    "picking the first of twenty-six. Two of the run's OWN sites already pick "
    "the first (`_situation_of` and the by-schema resolver, both "
    "`_situations_of(answered)[0]`) for a file G named a schema for; widening "
    "that to a BRANCH fixes the folder levels, the group-level fields and the "
    "tree for every file under it, which is the decision the ruling reserves. "
    "Unblock: the model call that picks one of a branch's valid options, with "
    "its prompt sentence, or the owner's rule for which of the N a schema "
    "means."))
def test_a_branch_names_one_situation_from_site_gs_evidence(tmp_path):
    """The pin the ruling asks for, red until the settler exists."""
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")
    assert code == 0, report
    assert "academic.coursework" in report, report
