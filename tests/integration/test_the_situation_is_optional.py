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

**AND THE QUESTION IS PRINTED AT THE END, NOT RAISED BEFORE THE MODEL RAN.**
Amendment item 2's own words are that a situation is not demanded before a file
is opened, and `_partition_branches` used to raise `NotConfigured` the moment the
default branch came back unsettled -- which is one statement ABOVE
`_model_fact_pass`, and site G, the situation judge, runs inside it. So the run
refused before the part of itself that answers this very question had looked at a
single file. It no longer does: the questions are recorded where their evidence
is, the run goes on with an unsettled default branch, the gate and site G run,
the branches site G names are opened by the second partition, and the question is
printed at the END of the run under the blocks that say what the scan found. A
file nothing named a situation for is asked no fields at site A -- there is no
situation whose fields they would be -- and is counted under the fact pass's
`unsettled` reason rather than called settled.

**The gap the ruling leaves open is named in a strict xfail below.** Site G names
a SCHEMA -- `SituationOutcome.recognised` and `.candidates` are `SCHEMA_IDS`, and
`ask_the_situation`'s own shortlist is schemas -- while a branch needs one of the
N SITUATIONS the library carries under that schema, and it carries at least two
under every one of the nineteen. R-88's own words name the settler: "per-branch
situation, MODEL DECIDING FROM VALID OPTIONS", and `104` §11.2 step 4 is the
standing ruling that the person, or a model from valid options, decides -- never
a rule picking the first of twenty-six. So until that model call exists, an
untyped run does everything it can and ends on one narrow question per branch,
which is `66` §14 exactly.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path

import pytest

import cli
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)

from test_local_model_fact_pass import MODEL_ID, StubOllama, dossier_in
from test_site_g_end_to_end import _decline
from test_site_h_gate import _clear

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

    The question that ends this run is about the CORPUS -- which situation these
    folders are -- and it is reached only after the folder has been read. That is
    the whole of `66` §14 in one run.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)

    assert "the following arguments are required" not in report, report
    # NOT A REFUSAL. The run did everything a run with no named situation can
    # do; what it ends on is a question, and `main`'s refusal handler -- which
    # would print "This run was refused" and return 2 -- is not on the path.
    assert code == 0, report
    assert "This run was refused" not in report, report
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

    assert code == 0, report
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
    """The question is written down BEFORE it is printed, and printed at the end.

    `apply_answers` refuses an answer to a question no run has asked, so a
    question printed before it was recorded would be a gesture the next
    invocation rejects. It is recorded in `_partition_branches`, where its
    evidence is, and printed when the run ends.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database)
    assert code == 0, report

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
    assert first_code == 0, first

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

    **THE KEY GAINED A MARKER ON 19 Sep and the NAME did not** (the owner's
    ruling). The default branch's question is keyed `situation:default:<label>` so
    it cannot collide with a sibling branch keyed by the same word -- on an untyped
    run the default's label IS its majority kind, and `record_question` is
    `ON CONFLICT DO NOTHING`, so one of the two questions was silently dropped.
    The PROMPT still reads "Which of these is Coursework?": what changed is the
    string the person types, and this test is exactly the guard that the string
    printed is the string the run then looks for.
    """
    corpus = _corpus(tmp_path)
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(corpus, database, "--label", "Coursework")
    assert code == 0, report
    assert ("--answer situation:default:Coursework=academic.coursework"
            in _flat(report)), report
    # The name is still theirs, on the line they read.
    assert "Which of these is Coursework?" in _flat(report), report

    code, report = _run(corpus, database, "--label", "Coursework",
                        "--answer",
                        "situation:default:Coursework=academic.coursework")
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
    """The pin the ruling asks for, red until the settler exists.

    ASKED AS "THE QUESTION IS GONE" and not as "the run reached the end". The run
    reaches the end today -- it prints the question there instead of refusing
    before the model -- and `academic.coursework` is one of the eleven options
    that question prints, so both of the assertions this test used to make are
    now true of a branch nothing settled. What is still owed is the SETTLER: the
    branch names one of its eleven and there is nothing left to ask.
    """
    corpus = _corpus(tmp_path)
    code, report = _run(corpus, tmp_path / "holder" / "plan.sqlite")
    assert code == 0, report
    assert "Which of these is academic?" not in _flat(report), report
    assert "academic.coursework" in report, report


# --- the run reaches the model, and the question comes after it -----------------

#: Files the ANCHORS cannot name. Not one of them carries a kind-of-file word a
#: single schema owns -- no `syllabus`, no `lecture`, no `cover letter` -- so
#: `_the_corpus_names_a_schema`'s first signal is silent and the default branch's
#: schema comes from the recogniser's readings instead. Whichever schema that is,
#: the library carries more than one situation under it, so the branch is
#: UNSETTLED and this is the corpus the defect lived on.
UNNAMEABLE = {
    "notes one.txt": "Some thoughts jotted down on a Tuesday.\nNothing in "
                     "particular, and nothing due.\n",
    "notes two.txt": "A second page of the same thoughts.\nStill nothing in "
                     "particular.\n",
    "list.txt": "milk\nbread\nbatteries\n",
}


def _unnameable(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in UNNAMEABLE.items():
        (corpus / name).write_text(body)
    return corpus


def _with_a_local_model(corpus: Path,
                        database: Path) -> tuple[int, str, list[str]]:
    """One `cli.main` with a stub local model, and the sites it was asked at.

    The gate clears every file and site G names no situation for any of them --
    the two shapes `test_site_h_gate` and `test_site_g_end_to_end` already pin,
    reused rather than re-derived. G DECLINING is the case this corpus is for:
    nothing named a situation for these files, so nothing can, and the run has to
    end on the question rather than on a refusal raised before G was asked.

    The call log is returned because "the run reached site G" is the whole claim
    and a printed block is weaker evidence than the call itself.
    """
    asked_at: list[str] = []

    def answer(payload: str) -> str:
        dossier = dossier_in(payload)
        asked_at.append(dossier.get("call_site"))
        if dossier.get("call_site") == cli.H_RESTRICTED_KIND:
            return _clear(dossier)
        return _decline(dossier)

    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch, StubOllama(answer=answer) as stub:
        patch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        patch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        code = cli.main([str(corpus), "--user", "t", "--database", str(database)],
                        out=out)
    return code, out.getvalue(), asked_at


def test_an_unnameable_folder_reaches_the_model_and_then_asks(tmp_path):
    """THE DEFECT, PINNED. `_partition_branches` raised before site G ever ran.

    The situation judge is site G and it runs INSIDE `_model_fact_pass`, one
    statement below the partition. The refusal that used to stand in
    `_partition_branches` therefore ended the run before the only part of it that
    could have answered "which situation is this folder" had opened a file --
    which is the ruling of 11 Sep 2026 broken by the code written to keep it.

    Read off the call log and off the screen: the gate and site G were both
    asked about every file, and the question is printed after them. Nothing was
    refused.
    """
    corpus = _unnameable(tmp_path)
    code, report, asked_at = _with_a_local_model(
        corpus, tmp_path / "holder" / "plan.sqlite")

    assert code == 0, report
    # NOT A REFUSAL, and that sentence is what `main` prints for `NotConfigured`.
    assert "This run was refused" not in report, report
    # THE SITUATION JUDGE WAS ASKED, once per file, which is the whole of what
    # the old refusal made impossible. The gate ran first, as it must.
    assert asked_at.count(cli.G_SITUATION_SENSITIVITY) == len(UNNAMEABLE), asked_at
    assert asked_at.count(cli.H_RESTRICTED_KIND) == len(UNNAMEABLE), asked_at
    assert asked_at.index(cli.H_RESTRICTED_KIND) < asked_at.index(
        cli.G_SITUATION_SENSITIVITY), asked_at
    assert "Situations from a model:" in report, report
    # AND THE QUESTION COMES AFTER IT.
    flat = _flat(report)
    assert "the folder was read, and these are the folders" in flat, report
    assert report.index("Situations from a model:") < report.index(
        "the folder was read, and these are the folders"), report
    assert "--answer situation:" in flat, report


def test_a_file_no_situation_names_is_asked_no_fields_and_the_sum_still_closes(
        tmp_path):
    """`resolver_for`'s `None` arm, measured on the same run.

    A file whose folder nobody has named a situation for is asked nothing at site
    A -- the fields a call would offer are a situation's, and there is no
    situation -- and it lands under NOT ASKED with that reason in its own words,
    not under `settled by rule` and not under `unreadable`. The sum still closes,
    which is `104` §18.2 gap 10's whole point and is what a fact pass that raised
    instead of returning would have broken.

    The BUCKET is the assertion and not just the sum: these three files are
    readable and were read -- a run with no model at all counts the same corpus
    `unreadable`, for a different reason -- so a pin that only closed the sum
    would pass without the `resolver_for` arm this exists for existing.
    """
    corpus = _unnameable(tmp_path)
    code, report, _asked_at = _with_a_local_model(
        corpus, tmp_path / "holder" / "plan.sqlite")

    assert code == 0, report
    flat = _flat(report)
    assert f"Coverage: {len(UNNAMEABLE)} files indexed" in flat, report
    assert f"{len(UNNAMEABLE)} not asked" in flat, report
    assert "0 settled by rule" in flat, report
    assert "0 unreadable" in flat, report
    # `resolver_for`'s `NOT_ASKED_UNSETTLED` reason, in the words the screen
    # gives it, so the bucket cannot be reached by a different route and pass.
    # The sentence names both ways a file reaches it since `branch_situation.
    # the_one_situation`: the folder it SITS under, and the folder a model NAMED
    # it for. These three are the first -- site G named no schema for any of
    # them, so there is no schema to ask their fields under either.
    assert ("a folder they belong to -- the one they sit under, or the one a "
            "model named them for -- has a situation you have not yet said"
            in flat), report
    # The sum's own closing line, printed only when every file is on exactly one
    # bucket line above it.
    assert "and every file is on exactly one line above" in flat, report
