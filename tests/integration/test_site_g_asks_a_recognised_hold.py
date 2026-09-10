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
from model_situation import NONE_OF_THESE
from privacy.vocabulary import (
    LOCAL_MODEL_SITUATION, PRIVACY_CLASS_ORDINARY, PRIVACY_CLASS_PROTECTED,
    PROTECTED_KIND_IDENTITY_DOCUMENT,
)
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

#: What the rules make of the held file: RECOGNISED as one and HELD as the other.
#: Both are `SCHEMA_IDS` members and neither is authored here.
RECOGNISED_AS = "academic"
HELD_DOMAIN = "identity"

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


# --- the file is asked, and the question says what the rules did -----------------


def test_a_recognised_file_the_rules_hold_is_asked_and_its_report_names_both(
        tmp_path_factory, monkeypatch):
    """THE RULING, on the wire. A file the rules recognised AND hold reaches site
    G, and the report in its dossier says BOTH halves of what the rules concluded.

    Before this gap the file was `settled`: no dossier, no call, no line on any
    screen, and a `protected=1` row taken on the word `passport` in a filename
    that also carries a course code. Now the model is shown that the rules read
    this file as `academic` and are holding it as `identity` on the work type
    `passport`, found in the filename -- and it is offered both, plus the decline.

    THE WORDS ARE THE LIBRARY'S AND NOT THE PERSON'S. `academic`, `identity` and
    `passport` are authored names; nothing out of the file's own text reaches the
    prompt through this item, which is the guarantee `matched` already carries.

    SABOTAGE: restore the `settled` branch to `if not isinstance(outcome,
    Abstention)`. There is no dossier at all and this errors on the unpack.
    """
    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)

    (payload,) = conn.execute(
        "SELECT payload FROM llm_dossier WHERE call_site = ? AND subject_ref = ?",
        (cli.G_SITUATION_SENSITIVITY, held)).fetchall()
    dossier = json.loads(payload["payload"])
    (report,) = [item for item in dossier["evidence_items"]
                 if item["kind"] == "recogniser_abstention"]

    # What the rules RECOGNISED -- the half gap 24 had no way to say, because
    # every file it reached had abstained.
    assert f"recognised this file as {RECOGNISED_AS}" in report["location"], (
        report["location"])
    # ...and the hold, in gap 24's own phrase, unchanged.
    assert "held:" in report["location"]
    assert HELD_DOMAIN in report["location"]
    assert "passport" in report["location"]
    assert "filename" in report["location"]
    # AND IT DOES NOT CLAIM AN ABSTENTION THAT NEVER HAPPENED. The item kind is
    # still the one the ratified text describes; the sentence inside it is not.
    assert "recogniser abstention" not in report["location"], report["location"]

    # The shortlist is the ruling read literally: what the rules named, what they
    # are holding it as, and the decline that keeps it a question.
    options = dossier["allowed_vocabulary"]
    assert RECOGNISED_AS in options and HELD_DOMAIN in options
    assert options[-1] == NONE_OF_THESE
    assert len(options) == 3, options


def test_a_recognised_file_with_no_hold_is_still_settled_and_never_asked(
        tmp_path_factory, monkeypatch):
    """`00`:110 STILL STANDS WHERE NO HOLD EXISTS, and this is the file that says
    so. Its twin differs by one word in a filename.

    The ruling is narrow on purpose: a hold makes a recognised file askable, and
    nothing else does. `00`:110 -- "the LLM should not be called for direct,
    unique matches" -- is untouched for every recognised file the rules are not
    holding, which on a real corpus is nearly all of them. Widening this would
    spend a local call per file on the one site that already runs on every file.

    Measured on the wire and on the screen: no dossier was built for it, and the
    `settled` line counts it.

    SABOTAGE: drop the `precaution is None` half of the settled test and ask every
    recognised file. This file gets a dossier and the count reads 0.
    """
    database, said, _stub = _run("released", _naming(RECOGNISED_AS),
                                 tmp_path_factory, monkeypatch)
    conn = _read(database)
    free = _file_id(conn, FREE_NAME)

    assert _report_items(conn, free) == [], (
        "a recognised file the rules are not holding was put to the model")
    assert "1 settled by rule" in " ".join(said.split())
    # And it is not protected, which is what makes it the honest twin: the two
    # files differ in the hold and in nothing else this pass reads.
    assert free not in cli._protected_file_ids(conn)


# --- the verdict decides what becomes of the hold --------------------------------


def test_an_accepted_ordinary_verdict_lifts_a_recognised_hold(
        tmp_path_factory, monkeypatch):
    """THE LIFT, unchanged from gap 24 and now reachable on a recognised file.

    The model named the ordinary situation the rules themselves recognised, cited
    it out of released evidence, P8 accepted the claim and no restricted kind was
    named. `assign` writes G's `llm_supported` row over the precaution's
    `possible` one -- superseded, not deleted -- and the file is ordinary for
    every later pass of this run.

    THE RETIRED ROW SAYS WHAT RETIRED IT, and on this arm that sentence has to
    carry both halves: the verdict, the situation it named, the domain the rules
    held the file as, and the authored term they held it on.

    SABOTAGE: pass `held=True` and a kind unconditionally into
    `situation_classification`, and this file stays protected forever.
    """
    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    rows = _classifications(conn, held)
    hold = _the_hold(rows)

    assert hold["superseded_by"] is not None, (
        "the hold was never retired, so the local model's answer changed nothing")
    (lifted,) = [row for row in rows if row["fact_id"] == hold["superseded_by"]]
    assert lifted["basis"] == LOCAL_MODEL_SITUATION
    assert lifted["protected"] == 0
    assert lifted["privacy_class"] == PRIVACY_CLASS_ORDINARY
    assert lifted["supersedes"] == hold["fact_id"]
    reason = hold["supersede_reason"]
    assert RECOGNISED_AS in reason and HELD_DOMAIN in reason, reason
    assert "passport" in reason, reason
    # The set every later pass reads -- the report, the route and the review sets
    # share this one query, so this is the lift arriving where it has to arrive.
    assert held not in cli._protected_file_ids(conn)


def test_a_released_file_is_ordinary_for_the_route_that_comes_after(
        tmp_path_factory, monkeypatch):
    """SITE A'S ROUTE AFTER THE LIFT, exactly as gap 24 pins it for an abstention.

    The situation pass runs before the fact pass and before placement, so a hold
    lifted here is lifted in time to change where the file goes. Asked of
    `model_route_permitted`, the predicate `target_for` is built from, under
    `CLOUD_ENABLED_MODE` -- under `offline` every file answers the same and the
    assertion would be about the mode.

    SABOTAGE: write G's row without letting `assign` supersede the precaution's.
    One live protected row keeps this red.
    """
    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)

    assert cli.model_route_permitted(
        conn, locality=CLOUD,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.CLOUD_ENABLED_MODE)(held) is True, (
        "the local model released this file and the route still treats it as "
        "protected, so the lift changed nothing a person would notice")


def test_a_named_restricted_kind_keeps_a_recognised_hold(
        tmp_path_factory, monkeypatch):
    """THE ARM THAT MUST NOT WIDEN. A passport in a coursework folder is protected
    whatever its situation.

    The model named the ordinary situation the rules recognised AND one of `105`
    §13.3's ten restricted kinds -- which is precisely what this corpus invites,
    because the file really does read as coursework and really is named for a
    passport. `HANDLING_POLICY` answers for the SITUATION and knows nothing about
    the kind, so without gap 24's `held and restricted_kind is not None` the row
    would carry `protected=0` beside `privacy_class='protected'` and, being
    `llm_supported`, would supersede the hold and release the file to placement.

    SABOTAGE: drop `or (held and restricted_kind is not None)` from
    `situation_classification`. `protected` reads 0 here and the file becomes
    filable.
    """
    database, _said, _stub = _run(
        "kind", _naming(RECOGNISED_AS, kind=PROTECTED_KIND_IDENTITY_DOCUMENT),
        tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    rows = _classifications(conn, held)
    hold = _the_hold(rows)

    assert hold["superseded_by"] is not None
    (agreed,) = [row for row in rows if row["fact_id"] == hold["superseded_by"]]
    assert agreed["basis"] == LOCAL_MODEL_SITUATION
    assert agreed["privacy_class"] == PRIVACY_CLASS_PROTECTED
    assert agreed["protected"] == 1, (
        "the model named a passport and the file was released to placement")
    assert held in cli._protected_file_ids(conn)


def test_a_confirmed_hold_is_filed_on_the_holds_own_observations(
        tmp_path_factory, monkeypatch):
    """`104` §18.27's owed row: A RECORD CITES WHAT RAISED IT.

    The model agreed with the hold -- it named a passport -- so what this row
    records is the rules' hold, confirmed. What raised that hold is the word
    `passport` in the FILENAME. What the row was citing instead was
    `question.evidence_refs`, which on a recognised file are the `Recognition`'s
    own keys: the syllabus body that made the file look like coursework. A person
    opening the row to ask why their file is protected was shown the evidence for
    the opposite claim, and every later reader -- the review sets, the report --
    reads the same column.

    `Precaution` carried no refs at all before this, which is why the row had
    nothing truer to cite. It carries the observations its work types were found
    in now, projected from the same matches its terms and zones already come from.

    SABOTAGE: return `evidence_refs=()` from `_reported`, or cite
    `question.evidence_refs` unconditionally. The confirmed row is filed on the
    body prose and the last two assertions go red.
    """
    database, _said, _stub = _run(
        "kind", _naming(RECOGNISED_AS, kind=PROTECTED_KIND_IDENTITY_DOCUMENT),
        tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    rows = _classifications(conn, held)
    hold = _the_hold(rows)
    (agreed,) = [row for row in rows if row["fact_id"] == hold["superseded_by"]]

    said_by = {row["observation_key"]: (row["raw_value"] or "").casefold()
               for row in conn.execute(
                   "SELECT observation_key, raw_value FROM evidence "
                   "WHERE file_id = ? AND superseded_by IS NULL", (held,))}
    cited = json.loads(agreed["evidence_refs"])

    assert agreed["protected"] == 1, "this is the confirmed arm or it measures nothing"
    assert cited, "§8.4: the classification is itself evidence-backed"
    assert set(cited) == set(json.loads(hold["evidence_refs"])), (
        "the confirmed row rests on what the hold rested on")
    assert all("passport" in said_by[ref] for ref in cited), (
        "the observations the hold's own work type was found in, and no other")
    assert [ref for ref, value in said_by.items()
            if "grading policy" in value and ref not in cited], (
        "the readings that made this file look like coursework are still in the "
        "file and are no longer what its protection is filed on")


def test_a_confirmed_holds_retired_row_says_the_model_agreed(
        tmp_path_factory, monkeypatch):
    """WHICH WAY THE HOLD WENT, in the one column that says why it was retired.

    §8.2 keeps the old row and the reason it was superseded, and that reason is
    where a person reads what happened. "named academic" reads exactly the same on
    the file the model RELEASED and on the passport it CONFIRMED -- two opposite
    outcomes wearing one sentence. The verb is read off the record that is about
    to supersede, so the sentence and the row's own flag cannot disagree.

    SABOTAGE: drop the `record.protected` branch from the reason. Both runs write
    "named", and the retired row of a confirmed hold is indistinguishable from the
    retired row of a lifted one.
    """
    database, _said, _stub = _run(
        "kind", _naming(RECOGNISED_AS, kind=PROTECTED_KIND_IDENTITY_DOCUMENT),
        tmp_path_factory, monkeypatch)
    confirmed = _the_hold(_classifications(_read(database),
                                           _file_id(_read(database), HELD_NAME)))

    database, _said, _stub = _run("released", _naming(RECOGNISED_AS),
                                  tmp_path_factory, monkeypatch)
    lifted = _the_hold(_classifications(_read(database),
                                        _file_id(_read(database), HELD_NAME)))

    assert "confirmed the rules' hold" in confirmed["supersede_reason"], (
        confirmed["supersede_reason"])
    assert "confirmed the rules' hold" not in lifted["supersede_reason"], (
        lifted["supersede_reason"])
    # And both still say what the rules had held the file as, and on which
    # authored term -- the half `104` §18 gap 24 put there, unchanged.
    for reason in (confirmed["supersede_reason"], lifted["supersede_reason"]):
        assert HELD_DOMAIN in reason and "passport" in reason, reason


def test_none_leaves_a_recognised_hold_exactly_as_the_rules_wrote_it(
        tmp_path_factory, monkeypatch):
    """SILENCE NEVER LIFTS A HOLD, on this arm too.

    "none" is a successful outcome and it is not an answer about the hold: the
    precaution row stands, unsuperseded, no row is written beside it, and the file
    stays protected and stays on this device. The file was ASKED -- which is the
    change -- and the asking changed nothing, which is the rule.

    SABOTAGE: write a classification on the decline path. The hold is retired by a
    model that said it could not tell.
    """
    database, _said, _stub = _run("declined", _decline, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    rows = _classifications(conn, held)

    # It was asked: the dossier exists, which is what separates this from the
    # `settled` twin above, where nothing was built at all.
    assert len(_report_items(conn, held)) == 1
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


def test_the_counts_move_a_recognised_hold_out_of_settled_and_into_the_block(
        tmp_path_factory, monkeypatch):
    """RULING 4. A file recognised AND held is not `settled`; it is asked, and its
    hold is counted in `PrecautionHolds` like any other.

    Two files walked. On the released run one is `settled` -- the free twin -- and
    the held one is NAMED, so it is in neither of the six; the hold block says 1
    held, 1 released. On the declined run the same file is `asked and left alone`
    and the block says 1 still held. Both runs keep the arithmetic a person can
    check: the six counters plus the named files are the roster, and the three
    hold sentences add up to `held`.

    On r19 the answer for these files was silence: they were `settled`, they were
    `protected`, and no line on any screen said either thing about them.

    SABOTAGE: count a recognised hold as `settled` as well as asking it. The
    partition over-counts and the `1 settled by rule` assertion goes red.
    """
    _database, released, _stub = _run("released", _naming(RECOGNISED_AS),
                                      tmp_path_factory, monkeypatch)
    said = " ".join(released.split())
    assert "1 settled by rule" in said
    assert "the rules were holding 1 file on a safety term" in said
    assert "1 released by the model" in said
    assert "0 confirmed by the model" in said
    assert "0 still held because nothing could say" in said

    _database, declined, _stub = _run("declined", _decline, tmp_path_factory,
                                      monkeypatch)
    said = " ".join(declined.split())
    assert "1 settled by rule" in said
    assert "1 asked and left alone" in said
    assert "the rules were holding 1 file on a safety term" in said
    assert "0 released by the model" in said
    assert "1 still held because nothing could say" in said
