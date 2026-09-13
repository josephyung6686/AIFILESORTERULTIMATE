# tests/integration/test_site_g_asks_a_recognised_hold.py
"""`104` §18.26 gap 24b: a hold outranks `00`:110, and the file is asked.

**THE OWNER'S RULING (10 Sep, 13:10).** Gap 24 put every held file to the local
model and let a cited ordinary answer lift the hold -- but only for holds taken on
an ABSTENTION. `basis='safety_domain'` has three writers, and the other two sit on
files `Detector.explain` returns a `Recognition` for: the winning-schema branch
(another schema won and a safety domain still NAMED the file) and a safety domain
winning outright. `cli.ask_the_situation` counted those files `settled` and never
asked, on `00`:110's own sentence -- *"The LLM should not be called for direct,
unique matches"*. On r19, **8 of the 11 ordinary files wrongly held were exactly
those**, routed local-only and withheld from placement for no reason.

The owner rules that `00`:110 YIELDS to a protected hold. A hold is not a direct
unique match: it is a word-list guess about what the file IS -- "will" the modal
verb, "statement" in a college personal statement, "passport" in a filename beside
a course code -- and the local model reads the whole text. So a file the rules both
RECOGNISED and HOLD is asked, on the local route, with a shortlist carrying the
schema the rules recognised AND the safety domain the hold names, so the model can
answer the ordinary situation, or the protected one, or neither.

**WHAT IS UNCHANGED, and each has a test here.** The lift rule is gap 24's in
every arm: an ACCEPTED ordinary situation with citations and no restricted kind
supersedes the hold; a restricted kind or a protected situation keeps it on the
model's word; "none" keeps it, and silence never lifts a hold. Site A's route
after a lift behaves exactly as gap 24 pins it. And `00`:110 still stands
everywhere a hold does not: a recognised file the rules are NOT holding is still
`settled` and is still never asked, which is the companion file in this corpus.

**RETIRED IN PART BY THE OWNER'S WORD OF 13 SEP 2026: a protected record is filed
by the person.** The ruling above made a recognised-and-held file askable; this
one makes it unaskable again, and for the opposite reason. It is not `00`:110
reserving a direct unique match from the model -- that reading is gone for good,
and the free twin below is still asked -- it is that a held file is nobody's to
ask about. `cli.ask_the_situation` counts it `held` and goes on before it reads
what the rules recognised, so a held file has no dossier, no verdict, no lift and
no confirmation, and it is not counted among the files the rules recognised
either. The lift arms below are retired with the call; what survives is the hold
itself, the row it is filed on, and the person's own word over it.

**NO OLLAMA AND NO NETWORK**, and the stubs are gap 24's own, imported rather than
copied so a run here and a run there are runs of the same shape.

**THE CORPUS IS TWO RECOGNISED FILES AND ONE OF THEM IS HELD.** Both carry four of
`academic`'s own words, so `academic` reaches `never_alone`'s arity and WINS on
both -- which is what makes these `Recognition`s and not the abstentions gap 24
already measured. `Passport syllabus.txt` also carries `identity`'s work type
`passport` in its FILENAME, a naming zone, so the winning-schema branch protects
it: recognised `academic`, held `identity`. Its twin differs by that one word.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import cli
from readers.model_deepseek import CLOUD
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    LOCAL,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from test_local_model_fact_pass import MODEL_ID, StubOllama
from test_site_g_end_to_end import LABEL, SITUATION, _decline, _dispatching
from test_site_g_lifts_the_hold import _classifications, _naming, _read, _the_hold

#: The recognised-and-held file, and the recognised-and-free one beside it. They
#: differ by the single word `passport` in a filename.
HELD_NAME = "Passport syllabus.txt"
FREE_NAME = "PHYS 1401 syllabus.txt"

#: What the rules RECOGNISE the held file as -- they hold it as `identity`, which
#: since 13 Sep 2026 no test names, because no answer is given about a held file.
#: A `SCHEMA_IDS` member and not authored here.
RECOGNISED_AS = "academic"

#: Four of `academic`'s own authored words -- `syllabus` in the filename, then
#: `grading policy`, `attendance`, `office hours` and `final exam` in the body.
#: Arity is the point: one term each would tie, abstain, and measure gap 24.
BODY = ("PHYS 1401 Syllabus\n\nGrading policy: attendance is required.\n"
        "Office hours Tuesday. Final exam in May.\n")


def _corpus(root: Path) -> Path:
    """Two files the rules RECOGNISE, one of which they also hold."""
    corpus = root / "recognised" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / FREE_NAME).write_text(BODY)
    (corpus / HELD_NAME).write_text(BODY)
    return corpus


#: ONE RUN PER ANSWER, SHARED BY THE TESTS THAT READ IT -- gap 24's own rule, for
#: its own reason: a `cli.main` run over a real corpus is the most expensive thing
#: in this suite. Keyed by the answer's name so two tests wanting different
#: answers cannot silently share a run.
_RUNS: dict[str, tuple] = {}


def _run(key: str, answer, tmp_path_factory, monkeypatch):
    if key in _RUNS:
        return _RUNS[key]
    root = tmp_path_factory.mktemp(key)
    corpus = _corpus(root)
    database = root / "plan.sqlite"
    with StubOllama(answer=_dispatching(answer)) as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        out = io.StringIO()
        code = cli.main(
            [str(corpus), "--situation", SITUATION, "--label", LABEL,
             "--user", "t", "--database", str(database)], out=out)
    assert code == 0, out.getvalue()
    _RUNS[key] = (database, out.getvalue(), stub)
    return _RUNS[key]


def _file_id(conn, filename: str) -> str:
    (row,) = conn.execute("SELECT file_id FROM files WHERE filename = ?",
                          (filename,)).fetchall()
    return row["file_id"]


def _report_items(conn, file_id: str) -> list[str]:
    """The `recogniser_abstention` item of every G dossier built for this file."""
    return [item["location"]
            for row in conn.execute(
                "SELECT payload FROM llm_dossier WHERE call_site = ? "
                "AND subject_ref = ? ORDER BY rowid",
                (cli.G_SITUATION_SENSITIVITY, file_id))
            for item in json.loads(row["payload"])["evidence_items"]
            if item["kind"] == "recogniser_abstention"]


# --- the held twin is not asked, and its free twin is ----------------------------


def test_a_recognised_file_the_rules_hold_is_not_asked_and_its_free_twin_is(
        tmp_path_factory, monkeypatch):
    """THE OWNER'S WORD OF 13 SEP 2026 -- a protected record is filed by the
    person -- on the corpus that separates the two reasons a file goes unasked.

    Gap 24b made this file askable and amendment 7(c) made its twin askable; the
    ruling takes the first back and leaves the second, so the two files now part
    company for the opposite reason to the one they used to. The twin the rules
    recognised and are NOT holding is asked, which is what says `00`:110 is still
    retired. The twin they recognised and ARE holding is not, and no dossier is
    built for it: no prompt, no call, nothing off the file.

    THAT IS THE WHOLE MEASUREMENT, and the two counts have to be read together --
    a run where the site asked nothing at all would satisfy the first line alone
    and would mean the opposite.

    SABOTAGE: drop the `current.protected` skip from `ask_the_situation` and the
    held twin is assembled for a model again.
    """
    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    conn = _read(database)

    assert _report_items(conn, _file_id(conn, HELD_NAME)) == [], (
        "a protected record was assembled for a model, which is what the "
        "owner's word of 13 Sep 2026 ended")
    assert len(_report_items(conn, _file_id(conn, FREE_NAME))) == 1, (
        "the site asked nothing at all, so the line above says nothing about "
        "the hold")


def test_a_recognised_file_with_no_hold_is_asked_too_and_the_count_says_so(
        tmp_path_factory, monkeypatch):
    """`00`:110 NO LONGER RESERVES THIS FILE, and this test is the record of the
    day it stopped. Its twin differs by one word in a filename.

    **WHAT IT USED TO ASSERT, and why it was right until it was measured.** Gap
    24b's ruling was narrow on purpose: a hold makes a recognised file askable and
    nothing else does. This test held the other side of it -- "no dossier was built
    for it, and the `settled` line counts it" -- on the argument that `00`:110
    ("the LLM should not be called for direct, unique matches") is untouched for
    every recognised file the rules are not holding, "which on a real corpus is
    nearly all of them", and that widening it "would spend a local call per file on
    the one site that already runs on every file".

    **THE MEASUREMENT THAT TURNED IT AROUND (`00` amendment 7(c), from `104`
    §18.56).** Nearly all of them was right and was the problem: 218 of the second
    corpus's files carried a rule classification, and the rules' top-1 accuracy on
    the files they named was 32.2%. So this branch was reserving two files in three
    from the only reader that could correct them -- and, because a classified
    ordinary file is cloud-eligible, sending them. The owner ruled that a file the
    rules settle is still asked. The cost the old docstring names is real and was
    accepted: one local call per file is what the site now spends, which is why
    amendment 7(c) also split the protection question onto a shorter, cheaper
    dossier.

    What the rules concluded is not thrown away. It reaches the model on its own
    `candidate_schema` item, and the screen still says how many files the rules had
    recognised -- as a fact about the rules rather than as a fate for the file.

    SABOTAGE: restore `if precaution is None and outcome.recognised is not None:
    settled += 1; continue` and this file goes back to never being read.
    """
    database, said, _stub = _run("released", _naming(RECOGNISED_AS),
                                 tmp_path_factory, monkeypatch)
    conn = _read(database)
    free = _file_id(conn, FREE_NAME)

    assert _report_items(conn, free) != [], (
        "a file the rules recognised was not put to the model, which is the state "
        "`00` amendment 7(c) ended")
    said_flat = " ".join(said.split())
    # THE RETIRED SENTENCE, by its own first words. "settled by rule" alone is not
    # enough to test on: the FACT pass prints a line of its own with that phrase
    # about P6 fields, and it is untouched by this amendment.
    assert "settled by rule: the recognisers named" not in said_flat, (
        "the situation pass's `settled` counter is retired; a file the rules named "
        "is asked like any other and lands in one of the five that partition the "
        "roster")
    assert "the rules had already recognised" in said_flat, (
        "what the rules recognised is still counted and still printed, outside "
        "the partition, because those files were also asked")
    # And it is not protected, which is what makes it the honest twin: the two
    # files differ in the hold and in nothing else this pass reads.
    assert free not in cli._protected_file_ids(conn)


# --- no verdict is given, so the hold stays as the rules wrote it ----------------


def test_no_verdict_lifts_a_recognised_hold_because_none_is_asked_for(
        tmp_path_factory, monkeypatch):
    """THE LIFT, WITHDRAWN by the owner's word of 13 Sep 2026: a held file is not
    asked, so there is no accepted verdict for it and nothing supersedes the
    precaution's row.

    Read on the run whose stub names exactly the ordinary situation the rules
    themselves recognised -- the answer with the best claim of any to be right
    about this file, and the one that used to retire the hold. It never reaches
    the file. The hold is the only row, unsuperseded, and the file is protected
    for every later pass of the run.

    SABOTAGE: drop the `current.protected` skip from `ask_the_situation`. The
    ordinary verdict supersedes the hold and every assertion here goes red.
    """
    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    rows = _classifications(conn, held)

    assert [row["basis"] for row in rows] == ["safety_domain"], (
        "a model wrote a row about a file it was never asked about")
    assert rows[0]["superseded_by"] is None
    assert rows[0]["supersede_reason"] is None
    assert rows[0]["protected"] == 1
    assert held in cli._protected_file_ids(conn)


def test_no_model_answer_makes_a_recognised_hold_ordinary_for_the_route_after(
        tmp_path_factory, monkeypatch):
    """SITE A'S ROUTE WITH THE LIFT GONE (13 Sep 2026, the owner's word): the file
    is refused the cloud on the run where the model answered ordinary.

    Asked on the RELEASED run and not the declining one, because this is the
    dangerous direction: on the second corpus the local judge's ordinary answer
    lifted the holds on two key-protected files, and under the tuple ratified on
    12 Sep a lifted hold was a cloud clearance, so both would have crossed at the
    fact pass. Asked of `model_route_permitted`, the predicate `target_for` is
    built from, under `CLOUD_ENABLED_MODE` -- under `offline` every file answers
    the same and the assertion would be about the mode.

    SABOTAGE: drop the `current.protected` skip from `ask_the_situation`, or put
    `local_model_situation` back into `CLOUD_CLEARING_BASES`.
    """
    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)

    assert cli.model_route_permitted(
        conn, locality=CLOUD,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.CLOUD_ENABLED_MODE)(held) is False, (
        "a model's ordinary answer opened the cloud for a held file, which is "
        "the crossing the owner's word of 13 Sep 2026 stopped")
    assert held in cli._protected_file_ids(conn)


def test_the_hold_is_filed_on_the_observations_its_work_type_was_found_in(
        tmp_path_factory, monkeypatch):
    """`104` §18.27's owed row -- A RECORD CITES WHAT RAISED IT -- on the one row
    that survives the owner's word of 13 Sep 2026.

    The gap was written about the CONFIRMED row site G used to write when the
    model agreed with a hold, and there is no such row now: the file is not asked,
    so the only record saying this file is protected is the precaution's own. The
    claim is unchanged and lands on it instead. What raised this hold is the word
    `passport` in the FILENAME, and that is what a person opening the row to ask
    why their file is protected has to be shown -- not the syllabus body that made
    it look like coursework, which is exactly what this corpus offers instead and
    what the row would cite if it cited the recognition's keys.

    THE COURSEWORK READINGS ARE STILL THERE, and the last assertion says so: they
    were not deleted to make this true, they are simply not what the protection
    rests on.

    SABOTAGE: return `evidence_refs=()` from the detector's `_reported`, or file
    the precaution on the recognition's own keys.
    """
    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    hold = _the_hold(_classifications(conn, held))

    said_by = {row["observation_key"]: (row["raw_value"] or "").casefold()
               for row in conn.execute(
                   "SELECT observation_key, raw_value FROM evidence "
                   "WHERE file_id = ? AND superseded_by IS NULL", (held,))}
    cited = json.loads(hold["evidence_refs"])

    assert hold["protected"] == 1, "this is the hold or it measures nothing"
    assert cited, "§8.4: the classification is itself evidence-backed"
    assert all("passport" in said_by[ref] for ref in cited), (
        "the observations the hold's own work type was found in, and no other")
    assert [ref for ref, value in said_by.items()
            if "grading policy" in value and ref not in cited], (
        "the readings that made this file look like coursework are still in the "
        "file and are not what its protection is filed on")


def test_a_decline_leaves_a_recognised_hold_because_it_is_not_asked_at_all(
        tmp_path_factory, monkeypatch):
    """SILENCE NEVER LIFTS A HOLD, and since the owner's word of 13 Sep 2026 the
    silence is not even the model's: a held file is not asked, so "none" is an
    answer about the twin beside it and about nothing else.

    The outcome is the one gap 24 wrote and the road to it is shorter. The
    precaution row stands, unsuperseded, no row is written beside it, and the file
    stays protected and stays on this device -- reached without a dossier, without
    a call and without a question, which is the line that changed.

    SABOTAGE: write a classification on the decline path, or drop the
    `current.protected` skip -- the first retires a hold on a model that said it
    could not tell, the second builds the dossier the first assertion forbids.
    """
    database, _said, _stub = _run("declined", _decline, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    rows = _classifications(conn, held)

    # It was not asked: no dossier at all, where this used to require exactly one.
    assert _report_items(conn, held) == []
    assert [row["basis"] for row in rows] == ["safety_domain"]
    assert rows[0]["superseded_by"] is None
    assert rows[0]["protected"] == 1
    assert held in cli._protected_file_ids(conn)


def test_a_held_recognised_file_is_never_offered_a_cloud_target(
        tmp_path_factory, monkeypatch):
    """THE HALF THAT MUST NEVER MOVE. A protected file reaches the LOCAL model
    only, opened on this machine for it and never sent to the cloud (`104` §18.7).

    Asked on the run where the hold STANDS, because on the run where it was
    released the file is deliberately no longer protected and asking there would
    measure the lift instead of the bar. `ask_the_situation` raises
    `ProtectedFileOfferedACloudTarget` if the record and the route ever disagree,
    and making a recognised file askable is exactly the change that could have
    opened a new door to that disagreement.

    SABOTAGE: make `model_route_permitted` return `True` for a protected record on
    a cloud locality.
    """
    database, _said, _stub = _run("declined", _decline, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)

    def permitted(locality: str) -> bool:
        return cli.model_route_permitted(
            conn, locality=locality,
            unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
            operation_mode=cli.CLOUD_ENABLED_MODE)(held)

    assert permitted(CLOUD) is False
    assert permitted(LOCAL) is True


# --- the person is told, and the counts still add up -----------------------------


def test_the_counts_move_a_recognised_hold_out_of_the_asking_altogether(
        tmp_path_factory, monkeypatch):
    """RULING 4 under the owner's word of 13 Sep 2026: the held twin leaves every
    count that is about asking, and the hold block is where a person finds it.

    **WHAT THIS TEST MEASURED BEFORE.** Gap 24b moved the held twin out of
    `settled` and into the asked; amendment 7(c) moved its free twin after it, so
    the screen read 2 recognised and 2 asked. The ruling takes the held one back
    out. It is skipped before `recognised_by_rules` is counted, so the recognised
    line reads 1 for a corpus of two files the rules both recognised -- the count
    keeps its own promise, that every file in it was also asked, at the price of
    no longer being every file the rules recognised.

    **WHAT IS NOT ASSERTED HERE, and it is missing rather than moved.** The five
    counters that partition the roster no longer close over it: the held file
    lands in none of them, so on the declining run one file of two is accounted
    for. The hold block's own arithmetic is what still closes, and it is what is
    pinned below -- `released` and `confirmed` are zero and `held and not asked`
    carries the whole of `held`.

    SABOTAGE: count the skipped file as `declined` or `no_route`; either would
    tell a person a model was asked about their protected record.
    """
    for key, answer in (("released", _naming(RECOGNISED_AS)),
                        ("declined", _decline)):
        _database, report, _stub = _run(key, answer, tmp_path_factory,
                                        monkeypatch)
        said = " ".join(report.split())
        assert "1 of them the rules had already recognised" in said, (
            "the rules recognised both twins and only the free one was asked, "
            "so only the free one is counted here")
        assert ("were holding 1 file, and a protected record is filed by "
                "the person" in said), said
        assert "0 released by the model" in said
        assert "0 confirmed by the model" in said
        assert "1 held and not asked" in said
