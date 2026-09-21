# tests/integration/test_a_silent_file_is_asked_and_filed_under_one_situation.py
"""`cli._the_situation_this_file_is_under` driven end to end through `cli.main`.

A file site G leaves silent used to get THREE answers to one question: the fact
pass asked it its branch's VOTED fields (`branch_votes`, the owner's ruling of
11 Sep), P11 chose its folders under the branch's OWN situation, and site E
offered it the run's `--situation`. Measured on the owner's corpus today, 59 of
371 files are in that state -- asked one situation's fields and then refused that
situation's folders. One function now answers for all three.

**THE CORPUS IS BUILT SO THE THREE ANSWERS DIFFER.** The run is typed
`--situation academic.coursework`; the `career` branch is opened by three
anchored files and settled to `career.recruiting` by the person's own `--answer`;
and site G names `research` for those same three, so the branch votes `research`
3-0. `Cover letter Gamma.txt` is the fourth file of that branch and site G
declines it. Its voted situation is `research.conference-presentation`, which is
neither its branch's nor the run's -- so every reader that disagrees is visible.

**WHY SITE G CAN TELL THESE FILES APART, and only this way.** A site-G dossier
for a short text file releases the folder path, the mime type and the extension;
`filename` is never released to any model. So the three named files sit in one
subfolder, the stub reads the path, and the fourth cover letter sits in the
corpus root and is declined. This is `test_each_file_is_filed_under_its_own_
situation`'s own reason, and its stub answers -- the gate clears, site A copies,
site C takes the top of the shortlist -- are imported rather than rewritten.

**MEASURED BEFORE THE CHANGE, everything else equal:** the same file was asked
`artifact_type`/`project`/`venue` -- research's fields, from the vote -- and then
filed into the person's own `Applications` folder, because its folders were
chosen under `career.recruiting` and no career folder was supported by facts
nobody had asked for. With one decision both halves move together.

**AND SINCE `branch_situation.the_one_situation` THE ONE DECISION IS "NOT YET"
(13 Sep 2026).** The vote names the SCHEMA `research`; the shipped library
carries eight situations under it and the recognisers raised none of them for
this file, so `_situations_of(voted)[0]` was choosing
`research.conference-presentation` out of eight on alphabetical order and every
reader below spent that pick. The file's situation is now unresolved: P11
abstains `situation_unanswered` for it and the person is asked "Which of these is
research?" at the branch site G opened. What this file still pins is the property
it was written for -- one decision, and the fields and the folders never disagree
about it.

**THE FIELDS ARE THE SCHEMA'S AND ARE STILL ASKED.** An unresolved SITUATION
withholds the folder levels and the template; it does not withhold the question.
The first cut of this change withheld both and the facts column came out empty
for every file the judge had read correctly, so a file whose schema is known is
asked that schema's own fields with no levels shown -- `model_facts.
open_question`'s `None` arm, the shape the unsettled default branch's authorities
were already built in.

**TWO RUNS, for `test_r37_per_branch_situation`'s reason:** `apply_answers`
refuses an answer to a question no run has asked yet, so the first run asks
"Which of these is career?" and the second answers it.

**OBSERVED AND DELIBERATELY NOT ASSERTED.** `Jane Doe resume.txt` abstains
`budget_deferred`: six files over two runs sit against this run's call ceiling.
Nothing below reads it, and the three files this pin is about are asked and
placed on both runs.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import cli  # noqa: E402
from facts.domains import DOMAIN_FIELDS  # noqa: E402
from placement.vocabulary import SITUATION_UNANSWERED  # noqa: E402
from privacy.vocabulary import LOCAL_MODEL_SITUATION  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)

from test_each_file_is_filed_under_its_own_situation import (  # noqa: E402
    _abstentions, _names, _placed, _released, _the_deterministic_winner,
)
from test_local_model_fact_pass import (  # noqa: E402
    MODEL_ID, StubOllama, _answer_for, dossier_in,
)
from test_r37_per_branch_situation import (  # noqa: E402
    COURSEWORK_FIELDS, RECRUITING_FIELDS, _call_log,
)
from test_site_g_end_to_end import _decline  # noqa: E402
from test_site_h_gate import _clear  # noqa: E402

SITUATION = "academic.coursework"
LABEL = "Coursework"
RESEARCH_SCHEMA = "research"
CAREER_SITUATION = "career.recruiting"
CAREER_ANSWER = f"situation:career={CAREER_SITUATION}"

#: `research.conference-presentation`'s own file-level fields, from the shipped
#: library's row: the three `_situations_of(voted)[0]` used to narrow the silent
#: file's question to. They are a SUBSET of what it is offered now -- the schema's
#: six -- because with no situation there is no level list to narrow by.
RESEARCH_FIELDS = {"venue", "project", "artifact_type"}

#: The person's subfolder, and the only thing site G can tell these files apart
#: by -- the folder path is the one released item that differs per file.
APPLICATIONS = "Applications"

#: THE FILE THIS PIN IS ABOUT: a fourth cover letter, in the corpus root, that
#: site G declines. Its branch is `career`, and its branch's vote is `research`.
SILENT = "Cover letter Gamma.txt"

ROOT_FILES = {
    "PHYS 1401 syllabus.txt":
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3. "
        "Lecture Mondays.\n",
    "Lecture 08.txt":
        "Lecture 08 - Rotational Dynamics\nPHYS 1401\nTorque and angular "
        "momentum.\n",
    SILENT:
        "Cover letter\n\nDear Recruiting Team at Gamma Inc,\nPlease consider "
        "my application for the Data Analyst role. Job title: Data Analyst. "
        "References available.\n",
}

#: Three files carrying a validated `work_type` the library authored for `career`
#: alone, so they anchor that branch -- and all three in one folder, so site G can
#: name them and only them.
APPLICATION_FILES = {
    "Cover letter Acme.txt":
        "Cover Letter\n\nDear Hiring Manager,\nI am writing to apply for the "
        "Software Engineer position at Acme Corp. My resume is attached. I "
        "look forward to an interview.\n",
    "Cover letter Beta.txt":
        "Cover letter\n\nDear Recruiting Team at Beta Ltd,\nPlease consider my "
        "application for the Data Analyst role. Job title: Data Analyst. "
        "References available.\n",
    "Jane Doe resume.txt":
        "Jane Doe\nCurriculum Vitae / Resume\n\nWork experience\n2024-2026 "
        "Software Engineer, Acme Corp.\nEducation\nBSc Computer Science, "
        "Columbia University, 2022\n",
}


def _situation_answer(dossier: dict) -> str:
    """`research` for the application folder, a decline everywhere else."""
    where = " ".join(item["value"] for item in _released(dossier))
    if APPLICATIONS in where:
        return _names(RESEARCH_SCHEMA, dossier)
    return _decline(dossier)


def _answer(payload: str) -> str:
    dossier = dossier_in(payload)
    site = dossier.get("call_site")
    if site == cli.H_RESTRICTED_KIND:
        return _clear(dossier)
    if site == cli.G_SITUATION_SENSITIVITY:
        return _situation_answer(dossier)
    if site == cli.C_PLACEMENT:
        return _the_deterministic_winner(dossier)
    return _answer_for(payload)


def _corpus(root: Path) -> Path:
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    for name, body in ROOT_FILES.items():
        (corpus / name).write_text(body)
    (corpus / APPLICATIONS).mkdir()
    for name, body in APPLICATION_FILES.items():
        (corpus / APPLICATIONS / name).write_text(body)
    return corpus


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    """Two `cli.main` runs: the branch's question, then the person's answer."""
    root = tmp_path_factory.mktemp("one_situation")
    corpus = _corpus(root)
    database = root / "holder" / "plan.sqlite"

    def _once(*extra: str) -> str:
        out = io.StringIO()
        code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                         "--user", "t", "--database", str(database),
                         "--accept-groups", *extra], out=out)
        assert code == 0, out.getvalue()
        return out.getvalue()

    with pytest.MonkeyPatch.context() as patch, StubOllama(answer=_answer) as stub:
        patch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        patch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        first = _once()
        assert "Which of these is career?" in first, first
        report = _once("--answer", CAREER_ANSWER)
    return corpus, database, report


def test_the_branch_votes_a_situation_that_is_neither_its_own_nor_the_runs(run):
    """The premise, off the store and the screen: three names and one answer.

    A model verdict about a file's situation writes a `local_model_situation`
    row and a decline writes nothing, so these three rows ARE the vote -- three
    `research` against nothing else over the branch's four files. The fourth is
    not among them, and the branch's own situation is the person's, because the
    second run no longer asks what `career` is.
    """
    corpus, database, report = run
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        named = {str(Path(row["current_path"]).relative_to(corpus))
                 for row in conn.execute(
                     "SELECT f.current_path FROM classifications c "
                     "JOIN files f ON f.file_id = c.file_id WHERE c.basis = ?",
                     (LOCAL_MODEL_SITUATION,))}
    finally:
        conn.close()
    assert named == {f"{APPLICATIONS}/{name}" for name in APPLICATION_FILES}
    assert SILENT not in named
    assert "Which of these is career?" not in report, report


def test_every_file_the_judge_named_carries_that_situation_as_a_fact(run):
    """`104` §18.95: the answer the product ACTS on is written where facts are.

    Until 16 Sep 2026 site G's situation was stored nowhere. It reached
    `privacy.ClassificationRecord`, which records the HANDLING CLASS the situation
    implies and not its name, and the name survived only inside
    `llm_response.response_bytes` -- so the review sheets and the design stage
    re-parsed raw model JSON to read a decision the run had already made, and
    `situation_verdict_before` read it back for one purpose only, not re-asking.

    The vote in the test above is three `local_model_situation` rows. This asserts
    the other half of each of them: a `situation` fact on the same file, carrying
    the identifier, at `llm_supported` -- P8 checked its citations span by span --
    and never destination-eligible, because `00` amendment 9 makes the situation an
    INPUT to the sort and never a level of it.

    SABOTAGE: delete the `record_the_situation` call from `ask_the_situation`. This
    goes red and nothing else in the suite does, which is the hole it was in.
    """
    corpus, database, _report = run
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        judged = [row["file_id"] for row in conn.execute(
            "SELECT file_id FROM classifications WHERE basis = ? "
            "AND superseded_by IS NULL", (LOCAL_MODEL_SITUATION,))]
        assert judged, "the run is supposed to name a situation for some file"
        for file_id in judged:
            held = {(row["field_key"], row["canonical_value"], row["reliability_state"])
                    for row in conn.execute(
                        'SELECT ff.field_key, v.canonical_value, ff.reliability_state '
                        'FROM file_facts ff JOIN "values" v USING(value_id) '
                        "WHERE ff.file_id = ? AND ff.active = 1 "
                        "AND ff.superseded_by IS NULL", (file_id,))}
            situations = {(value, state) for field, value, state in held
                          if field == "situation"}
            assert len(situations) == 1, (file_id, sorted(held))
            (value, state), = situations
            assert "." in value or value.isalpha(), value
            assert state == "llm_supported", (value, state)
    finally:
        conn.close()


def test_the_silent_file_is_asked_its_voted_schemas_fields_and_no_situations(run):
    """Site A's `allowed_vocabulary` for it, read off the run's own call log.

    **THE VOTE NAMES A SCHEMA AND A SCHEMA IS NOT A SITUATION -- BUT THE FIELDS
    ARE THE SCHEMA'S.** This used to assert `research.conference-presentation`'s
    three fields, the alphabetically first of the eight the shipped library
    carries under `research`, taken by `_situations_of(voted)[0]`.
    `branch_situation.the_one_situation` retired that pick: the library carries
    eight, the recognisers raised none of them for this file, so which one this
    is has not been answered by anybody and the file's SITUATION is unresolved.

    Its SCHEMA is not. The situation decides the folder levels and the template;
    the fields are `research`'s own, and withholding them cost a whole facts
    column on the first cut of this change. So the file is asked the schema's
    question with no levels shown (`model_facts.open_question`'s `None` arm), and
    every field of the two lives this corpus is otherwise made of is absent.
    """
    _corpus_, database, _report = run
    offered = frozenset().union(*_call_log(database).get(SILENT, [frozenset()]))
    # EVERY FIELD THE VOTED SCHEMA DECLARES, not the three one of its eight
    # situations happens to bind a level for. `stage` is the witness: no
    # `research.conference-presentation` level names it, and the narrowed question
    # never offered it.
    assert offered >= set(DOMAIN_FIELDS["research"]), (offered,
                                                       _call_log(database))
    assert offered >= RESEARCH_FIELDS and "stage" in offered, offered
    # AND NOT THE RUN'S OWN. `academic` is what `--situation academic.coursework`
    # would have asked this file, and not one of its fields is here.
    assert not offered & (COURSEWORK_FIELDS - RESEARCH_FIELDS), offered
    # `career`'s fields ARE here, and that is `active_field_allowlist`'s standing
    # behaviour rather than anything the vote did: this file is a cover letter and
    # its own evidence activates `career`. The allowlist is the union of the
    # ACTIVE schemas, and it always was -- what the missing situation removes is
    # the level narrowing, not the activation.
    assert offered & RECRUITING_FIELDS, offered


def test_and_the_person_is_asked_which_of_the_eight_research_situations_it_is(run):
    """The way out of the unresolved state, and it is the EXISTING question.

    `questions.triggers.question_for_situation` at the branch site G opened. The
    branch exists only in the second partition -- G names a schema per file
    INSIDE the fact pass -- so the question is recorded there, at the same call
    that builds the branch, and it offers the library's own eight names.
    """
    _corpus_, _database, report = run
    assert f"Which of these is {RESEARCH_SCHEMA}?" in report, report


def test_and_its_folders_are_not_chosen_at_all_while_the_situation_is_open(run):
    """The destination, which is the other half of the same answer.

    **THE TWO HALVES ARE ONE DECISION AND THEY SPLIT WHERE THE ANSWER DOES.** The
    fact pass asked this file its SCHEMA's fields, because the schema is known;
    P11 files it nowhere, because a FOLDER needs the situation and nobody has
    named one. That is not the two readers disagreeing -- it is both of them
    reading the same answer, which is "the schema, and not yet the situation".
    The reason word says so: `situation_unanswered`: the judge named a kind and nobody said which situation, which left
    this file unjudged. The two named cover letters are in the same state, which
    is the control: the file G named and the file G left silent are treated
    alike.

    Filing it anyway is what this test used to assert, and the folder it was
    filed into came from `_situations_of("research")[0]` -- the first of eight in
    alphabetical order. A destination chosen that way is the defect, not the fix.

    SABOTAGE: give `the_one_situation` a `raised` set holding exactly one of
    `research`'s eight, and this file is asked that situation's fields and filed
    under it -- the corpus and every stub answer unchanged. That is the second
    arm, pinned without a corpus in
    `test_a_situation_is_never_the_first_of_twenty_six`.
    """
    placed = _placed(run)
    abstained = _abstentions(run)
    assert SILENT not in placed, placed[SILENT]
    assert abstained[SILENT] == SITUATION_UNANSWERED, abstained[SILENT]
    acme = f"{APPLICATIONS}/Cover letter Acme.txt"
    assert acme not in placed, placed[acme]
    assert abstained[acme] == SITUATION_UNANSWERED, abstained[acme]
    # And the run still files its coursework, which is the branch no vote
    # reaches: the default branch's situation is the run's own, the person typed
    # it, and nothing about this change touches a file with an answer.
    assert placed["PHYS 1401 syllabus.txt"].startswith(LABEL), placed


# --- the way out: the question this run recorded has an answer ------------------
#
# DEFINED LAST AND DEPENDING ON `run`, because the third run continues the same
# database: `apply_answers` refuses an answer to a question no run has asked, so
# the question has to have been recorded by one of the two runs above. The tests
# above read that database and therefore have to run first, which they do --
# pytest keeps definition order and this suite is run with `-p no:randomly`.

#: One of the eight situations the shipped library carries under `research`, and
#: deliberately NOT the alphabetically first one this change retired: an answer
#: that happened to agree with the old pick would prove nothing about the pick
#: being gone.
RESEARCH_ANSWER = "research.thesis-dissertation"


@pytest.fixture(scope="module")
def answered(run, tmp_path_factory):
    """A third `cli.main`, answering the question the second run printed.

    **ON ITS OWN COPY OF THE DATABASE, and that is not a detail.** This run
    ANSWERS the open situation, so it places files that `run`'s own tests assert
    are not placed -- `test_and_its_folders_are_not_chosen_at_all_while_the
    _situation_is_open` is the whole point of the state this fixture leaves
    behind. `run` is module-scoped and hands the same database to both sets, so
    writing into it makes this module's result a property of the order it ran in.

    Measured 21 Sep 2026 at `29b85d8c`, before any change of this session's: the
    module passes sorted and on seed 1, and fails on seeds 2 and 3 with
    `Cover letter Gamma.txt` placed under `Applications` -- placed by THIS
    fixture, read by a test that runs before it only because the ordering said
    so. The failing test passes alone on the same seed, which is what tells order
    from seed.

    `Connection.backup` rather than a file copy, because a WAL database is more
    than one file on disk; a copy rather than a fourth run, because the runs are
    what cost and this needs their rows, not their processes. The corpus is
    shared unchanged -- nothing writes to it.
    """
    corpus, shared, _report = run
    database = tmp_path_factory.mktemp("answered") / "plan.sqlite"
    source = sqlite3.connect(f"file:{shared}?mode=ro", uri=True)
    copy = sqlite3.connect(str(database))
    with copy:
        source.backup(copy)
    copy.close()
    source.close()
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch, StubOllama(answer=_answer) as stub:
        patch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        patch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                         "--user", "t", "--database", str(database),
                         "--accept-groups", "--answer", CAREER_ANSWER,
                         "--answer",
                         f"situation:{RESEARCH_SCHEMA}={RESEARCH_ANSWER}"],
                        out=out)
    assert code == 0, out.getvalue()
    return corpus, database, out.getvalue()


def test_the_answer_resolves_the_files_site_g_named(answered):
    """The person said which of the eight `research` is, and the files move.

    `_the_situation_the_person_chose` reads that answer at the branch's own scope,
    ahead of both library arms, so the files G named `research` are asked that
    situation's fields on this run instead of nothing. Without it the answer
    settles a branch on the second partition and every file that branch was
    opened FOR stays unresolved for ever -- a question with no answer path, which
    is worse than the silent pick it replaced.
    """
    _corpus, database, report = answered
    assert f"Which of these is {RESEARCH_SCHEMA}?" not in report, report
    log = _call_log(database)
    for name in ("Cover letter Acme.txt", "Cover letter Beta.txt"):
        offered = frozenset().union(*log.get(name, [frozenset()]))
        assert offered, (name, log)
        assert not offered & COURSEWORK_FIELDS, (name, offered)


def test_and_the_vote_carries_that_answer_to_the_file_g_left_silent(answered):
    """THE NON-OBVIOUS HALF: this file is not under the branch that answers it.

    `Cover letter Gamma.txt` sits under `career`, whose situation the person
    answered `career.recruiting` two runs ago. Its situation comes from its
    branch's VOTE -- the schema G named most often over that branch's files,
    which is `research` -- so the answer that resolves it is the one given at
    `branch:research`, a branch this file is not in. That is the vote arm reading
    the same answer as the name arm, and it is why
    `_the_situation_the_person_chose` takes a SCHEMA and not a branch.
    """
    _corpus, database, _report = answered
    offered = frozenset().union(*_call_log(database).get(SILENT, [frozenset()]))
    assert offered, _call_log(database)
    assert not offered & COURSEWORK_FIELDS, offered
    assert _abstentions(answered).get(SILENT) != SITUATION_UNANSWERED, (
        _abstentions(answered))
