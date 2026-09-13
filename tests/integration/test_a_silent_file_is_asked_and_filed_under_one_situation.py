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
nobody had asked for. With one decision it is filed at the root of `research`,
which is the situation its fields came from.

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
#: library's row: the three the silent file is offered because of the vote.
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


def test_the_silent_file_is_asked_the_voted_situations_fields(run):
    """Site A's `allowed_vocabulary` for it, read off the run's own call log.

    `research.conference-presentation`'s three fields, and not one field of the
    situation its branch carries or of the one the person typed for the run.
    """
    _corpus_, database, _report = run
    offered = frozenset().union(*_call_log(database).get(SILENT, [frozenset()]))
    assert offered == RESEARCH_FIELDS, (offered, _call_log(database))
    assert not offered & RECRUITING_FIELDS
    assert not offered & COURSEWORK_FIELDS


def test_and_its_folders_are_chosen_under_the_same_situation(run):
    """The destination, which is the other half of the same answer.

    `_only_this_files_own_branch` drops every candidate under a root whose branch
    carries another situation, so this file can only be here if P11 was told the
    situation the fact pass asked under. The two named cover letters land beside
    it, which is the control: the file G named and the file G left silent are
    filed together, and that is what the vote is for.

    SABOTAGE: give the decision the branch arm first -- return `branch.situation`
    before the vote -- and this file is filed into the person's own
    `Applications` folder instead, on the same corpus and the same answers. The
    test above fails with it, which is the property: both halves move together
    now, and the file is then asked `target_employer`/`job_title`/
    `recruiting_cycle`/`work_type` as well.
    """
    placed = _placed(run)
    assert placed.get(SILENT) == RESEARCH_SCHEMA, (placed, _abstentions(run))
    assert placed[f"{APPLICATIONS}/Cover letter Acme.txt"] == RESEARCH_SCHEMA
    # And the run still files its coursework, which is the branch no vote
    # reaches: the default branch's situation is the run's own.
    assert placed["PHYS 1401 syllabus.txt"].startswith(LABEL), placed
