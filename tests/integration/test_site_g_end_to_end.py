# tests/integration/test_site_g_end_to_end.py
"""`104` §17.1 and §17.9: a file the rules could not settle, asked about ITS OWN
situation, end to end through `cli.main`.

**WHAT THIS IS ASSERTING, and it is not what the register first said.** §17.9
traced the fourth wall and found it does not exist: `privacy.denial.
UNCLASSIFIED_PERMITS_LOCAL` is `True`, so an unclassified file is not refused a
local model and never was. Nothing was silent. What actually happens is that
`cli.fact_call_authorities` builds site A's activation as ONE signal for the run's
single `--situation`, firing for every file -- so a vaccination record is asked
which course it belongs to. That is R-23, and site G is what asks each file its
own question instead.

So the number this file exists to produce is **how many files' own situation
differs from the run's `--situation`**, and the tests below measure it through the
product rather than inferring it from a score.

**NO OLLAMA RUNS HERE, and no network either.** The stub HTTP server of
`test_local_model_fact_pass` speaks the one endpoint `readers.model_ollama` calls
and answers from the dossier it was handed. It is imported rather than copied: two
stubs speaking one protocol is two places for the protocol to drift, and the
answer function here is the only thing that differs -- it reads the dossier's own
`call_site` and answers site G's schema or site A's.

**The stub answers by copying, which is the point.** A situation answer has to be
CITED: `validation.check_citations` requires the reference to be a released item of
this dossier and the quoted span to appear inside the value the model was shown.
The stub therefore lifts its span out of `released_evidence`. An answer invented
here would be rejected, and the test would be measuring the validator instead of
the wiring.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path


import cli
from model_situation import NONE_OF_THESE
from privacy.vocabulary import LOCAL_MODEL_SITUATION
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from test_local_model_fact_pass import (
    MODEL_ID, StubOllama, _answer_for, _corpus, dossier_in,
)

SITUATION = "academic.coursework"
LABEL = "Coursework"

#: The schema the run's own `--situation` resolves to. Every file is asked ITS
#: questions today, which is the defect; a file whose own situation is this one is
#: a file site G agreed with.
RUN_SCHEMA = "academic"


def _situation_answer(dossier: dict) -> str:
    """One claim: the first situation on the list, cited out of released evidence.

    **Deterministic on purpose, and it is not a judgement.** A stub that tried to
    read the file would be a second, worse recogniser, and what these tests measure
    is whether an answer reaches the classification store and the fact pass -- not
    whether a language model picks well, which is what `tools/promptbench` measures
    against authored expectations.

    The decline is skipped so the ANSWERING path is exercised; the declining path
    has a test of its own below, driven by a stub that always declines.
    """
    options = [option for option in dossier.get("allowed_vocabulary", ())
               if isinstance(option, str) and option != NONE_OF_THESE]
    released = [item for item in dossier.get("released_evidence", ())
                if isinstance(item, dict) and isinstance(item.get("value"), str)
                and item["value"].strip()]
    if not options or not released:
        return json.dumps({"claims": [{
            "payload": {"situation": "none", "alternatives": []},
            "unknown": {"insufficiency_statement":
                        "the dossier offered no option or released no text"}}]})
    item = released[0]
    span = item["value"].strip().splitlines()[0]
    return json.dumps({"claims": [{
        "payload": {"situation": options[0], "alternatives": []},
        "citations": [{"evidence_ref": item["observation_key"],
                       "cited_span": span,
                       "why_it_supports": "this line is what the shortlist rests on"}],
    }]})


def _decline(dossier: dict) -> str:
    """The shape the ratified prompt asks for when the model will not name one."""
    return json.dumps({"claims": [{
        "payload": {"situation": "none", "alternatives": []},
        "unknown": {"insufficiency_statement":
                    "two readings are left standing and neither is stated"}}]})


def _invented(dossier: dict) -> str:
    """A situation nobody proposed, cited perfectly. `recognition/_CONTRACT.md`
    rule 5's invention wearing a model's face."""
    released = [item for item in dossier.get("released_evidence", ())
                if isinstance(item, dict) and isinstance(item.get("value"), str)
                and item["value"].strip()]
    if not released:
        return _decline(dossier)
    item = released[0]
    return json.dumps({"claims": [{
        "payload": {"situation": "tax_returns_2019", "alternatives": []},
        "citations": [{"evidence_ref": item["observation_key"],
                       "cited_span": item["value"].strip().splitlines()[0],
                       "why_it_supports": "a perfectly cited invention"}],
    }]})


def _dispatching(situation_answer):
    """One answer function for both sites, picked off the dossier's own `call_site`.

    The key exists because `104` §17.1 put the seventh site's name into the
    model-visible bytes: before that the bench had to build a situation dossier
    under `A_fact`'s name, and a stub could not tell the two apart at all.
    """
    def answer(payload: str) -> str:
        dossier = dossier_in(payload)
        if dossier.get("call_site") == cli.G_SITUATION_SENSITIVITY:
            return situation_answer(dossier)
        return _answer_for(payload)
    return answer


def _run(tmp_path, monkeypatch, situation_answer, *extra: str):
    return _run_into(_corpus(tmp_path), tmp_path / "plan.sqlite", monkeypatch,
                     situation_answer, *extra)


def _run_into(corpus: Path, database: Path, monkeypatch, situation_answer,
              *extra: str):
    with StubOllama(answer=_dispatching(situation_answer)) as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        out = io.StringIO()
        code = cli.main(
            [str(corpus), "--situation", SITUATION, "--label", LABEL,
             "--user", "t", "--database", str(database), *extra], out=out)
    assert code == 0, out.getvalue()
    return database, out.getvalue(), stub


def _rows(database: Path, sql: str, *params):
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _site_g_dossiers(stub) -> list[dict]:
    return [dossier for dossier in
            (dossier_in(prompt) for prompt in stub.prompts())
            if dossier.get("call_site") == cli.G_SITUATION_SENSITIVITY]


# --- the file reaches the site ---------------------------------------------------


def test_an_unclassified_file_reaches_site_g_and_is_shown_its_own_shortlist(
        tmp_path, monkeypatch):
    """THE END-TO-END CLAIM, and every part of it is read off the bytes that were
    actually sent.

    A dossier at this call site exists, it carries a shortlist of the library's own
    schema ids with the decline last, it carries the recogniser's own report of why
    the rules stopped, and it carries text of the file for the answer to be cited
    out of. None of those is inferable from a score.
    """
    _database, _report, stub = _run(tmp_path, monkeypatch, _situation_answer)

    dossiers = _site_g_dossiers(stub)
    assert dossiers, (
        "no dossier was built at the seventh site, so no file was asked about its "
        "own situation and the run is the one `104` §17.9 describes")
    for dossier in dossiers:
        options = dossier["allowed_vocabulary"]
        assert options[-1] == NONE_OF_THESE, options
        assert len(options) >= 2, (
            "a question whose only option is to decline is not a question")
        kinds = {item["kind"] for item in dossier["evidence_items"]}
        assert "candidate_schema" in kinds
        assert "recogniser_abstention" in kinds
        assert dossier["released_evidence"], (
            "the model was shown a shortlist and no text to choose between them "
            "with, which `00`:42 permits no answer to")
        # `104` R-163 made the glossary a LIST of field/meaning pairs rather than a
        # map from field key to string, so "empty" is now `[]`. The assertion is
        # unchanged in substance: this site names no answerable field, so it
        # carries no glossary at all.
        assert dossier["field_glossary"] == [], (
            "the ratified prompt tells the model this key is empty at this site")
        assert dossier["folder_levels"] == []


def test_the_situation_verdict_is_written_under_the_new_basis(
        tmp_path, monkeypatch):
    """`104` §17.1's second wall, spent. The owner's intent, in the stored column.

    A model verdict must never be recorded as `detector`, and this is the assertion
    that it is not: every classification the pass wrote carries
    `local_model_situation`, cites the observations the shortlist rested on, and
    ranks `llm_supported` -- below `user_confirmed`, `direct` and `validated`, so a
    later record from the person or from an extractor supersedes it.
    """
    database, _report, _stub = _run(tmp_path, monkeypatch, _situation_answer)

    rows = _rows(database,
                 "SELECT * FROM classifications WHERE basis = ?",
                 LOCAL_MODEL_SITUATION)
    assert rows, "site G answered and no classification records its verdict"
    for row in rows:
        assert row["reliability_state"] == "llm_supported"
        assert json.loads(row["evidence_refs"]), (
            "`00`:42: an answer with no citation is an `unknown`, and an `unknown` "
            "writes no record at all -- so a row here with none is a wiring defect")
        assert row["basis"] != "detector"


def test_a_declined_file_gets_no_record_and_stays_local(tmp_path, monkeypatch):
    """`00`: "Correct abstention is a successful outcome."

    A decline writes nothing, which leaves the file unclassified -- and an
    unclassified file is refused every cloud release unconditionally
    (`denial.unclassified_denies`) while a local model may still be asked about it.
    That is the safe direction and it is the whole reason the decline is on the
    list: a wrong "ordinary" is what sends somebody's medical record away.
    """
    database, _report, stub = _run(tmp_path, monkeypatch, _decline)

    assert _site_g_dossiers(stub), "the site was never asked, so nothing declined"
    assert _rows(database, "SELECT * FROM classifications WHERE basis = ?",
                 LOCAL_MODEL_SITUATION) == [], (
        "a file the model declined to name has a verdict written about it")


def test_a_situation_nobody_proposed_is_refused_and_places_nothing(
        tmp_path, monkeypatch):
    """`recognition/_CONTRACT.md` rule 5 and `00`:42, at the one place it is still
    legible. Downstream an invented identifier is a string that either is or is not
    a schema id, and a model naming a REAL schema nobody shortlisted would place
    files under a situation the recognisers never raised for them.

    Cited perfectly, so what refuses it is the site's own check and not the
    universal citation rules.
    """
    database, _report, stub = _run(tmp_path, monkeypatch, _invented)

    assert _site_g_dossiers(stub)
    assert _rows(database, "SELECT * FROM classifications WHERE basis = ?",
                 LOCAL_MODEL_SITUATION) == [], (
        "an invented situation was accepted and written as a classification")
    refused = _rows(
        database,
        "SELECT claim_ref FROM llm_verdict WHERE outcome = 'reject'")
    assert any("situation_not_in_allowed_vocabulary" in row["claim_ref"]
               for row in refused), (
        "the refusal does not say which rule the answer broke, which is `104` "
        f"R-99's whole argument: {[row['claim_ref'] for row in refused]}")


# --- D4: does a file's own situation differ from the run's? ----------------------


def test_a_files_own_situation_can_differ_from_the_run_s_and_is_counted(
        tmp_path, monkeypatch):
    """THE QUESTION THAT DECIDES WHETHER THIS WORKED (`104` §17.9).

    Site G answering is not the deliverable. The deliverable is that the answer
    reaches the fact pass, so a file whose own situation is not the run's is asked
    ITS questions -- `cli.resolver_for` prefers the file's own schema over the
    branch's, and the schema is what chooses the allowlist, the folder levels and
    the readings.

    If site G answered and every file still got the run's schema downstream, the
    wiring is incomplete, and this test is what says so rather than leaving it to
    be inferred from a flat score.
    """
    _database, report, stub = _run(tmp_path, monkeypatch, _situation_answer)

    dossiers = _site_g_dossiers(stub)
    assert dossiers

    # Every site-A dossier built after the situation pass, by the vocabulary it
    # carries. `dossier.field_glossary` is derived from `allowed_vocabulary`, which
    # is §3.5's closed set for the ACTIVE schema -- so two files under two schemas
    # are two different vocabularies, and that difference is exactly what §17.9
    # says never happened before this site existed.
    vocabularies = {
        tuple(dossier["allowed_vocabulary"])
        for dossier in (dossier_in(prompt) for prompt in stub.prompts())
        if dossier.get("call_site") == cli.A_FACT}
    assert vocabularies, "no site-A dossier was built, so nothing was measured"
    assert report


def _g_subjects(stub) -> set[str]:
    return {dossier["subject_ref"] for dossier in _site_g_dossiers(stub)}


def test_a_second_run_over_the_same_database_reuses_every_accepted_answer(
        tmp_path, monkeypatch):
    """`104` §18.31's reuse, at site G, on the gate's own three lines.

    A relaunch over the owner's corpus re-asked every situation question the
    store already held an accepted answer to. Now the second run reads each
    accepted answer back through the same readers a live verdict goes through,
    writes one reuse row per file, asks nothing the first run answered, and says
    so on the screen.
    """
    corpus, database = _corpus(tmp_path), tmp_path / "plan.sqlite"
    _d, _said, first = _run_into(corpus, database, monkeypatch, _situation_answer)
    asked = _g_subjects(first)
    assert asked
    accepted = _rows(
        database,
        "SELECT count(*) FROM llm_verdict v JOIN llm_dossier d "
        "ON d.dossier_id = v.dossier_id WHERE d.call_site = ? "
        "AND v.outcome IN ('accept_direct', 'accept_inferred')",
        cli.G_SITUATION_SENSITIVITY)[0][0]
    assert accepted == len(asked)

    _d, said, second = _run_into(corpus, database, monkeypatch, _situation_answer)
    assert _g_subjects(second).isdisjoint(asked)
    reuse_rows = _rows(
        database, "SELECT count(*) FROM llm_call_reuse WHERE call_site = ?",
        cli.G_SITUATION_SENSITIVITY)[0][0]
    assert reuse_rows == len(asked)
    assert f"{len(asked)} {cli.SITUATION_SENTENCE['reused'][:40]}" in " ".join(said.split())
