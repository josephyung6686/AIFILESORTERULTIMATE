# tests/integration/test_site_g_lifts_the_hold.py
"""`104` §18 gap 24: the local model decides what becomes of a precaution's hold.

**THE DEFECT, measured on r19 against the owner's hand labels.** The term
detector's precaution marks a file `sensitive_personal, protected=1,
basis='safety_domain'` when a safety domain stands among an abstention's tied
leaders and one of its WORK TYPES is anywhere in the file's evidence. It made 16
marks: 5 on truly protected files and 11 on ordinary ones -- `will` (8 of the 11,
the modal verb), `statement`, `receipt`, `consent form`, `medical record`,
`visa`, `credit card`, `endorsement`, in body prose on pages 1-4 of long
documents that discuss such things without being them. Zone does not separate
them: applying `_names_the_file` to this path drops 7 of the 11 false marks AND 2
of the 5 true ones.

**THE OWNER'S RULING (10 Sep):** the hold must be "a little more sure than now",
and under the product constitution the LLM decides. Site G is the product's kind
recogniser (§18.11), it runs on this device, and `cli.model_route_permitted`
already refuses a protected file every cloud target -- so every held file is put
to it, on the local route, with the precaution's own report in its dossier, and
its verdict supersedes the hold or leaves it standing:

* an ACCEPTED, cited, on-the-list ordinary situation with NO restricted kind
  releases the hold -- a new row supersedes the precaution's through
  `supersedes`/`superseded_by`/`supersede_reason`, and the file is ordinary for
  every later pass of the run.
* a safety-domain situation, or ANY of `105` §13.3's ten restricted kinds,
  confirms it -- G's own protected row supersedes the precaution's, so the record
  shows the model agreed rather than showing only that the rules had guessed.
* a decline, a refused claim, a failed call or a file with nothing releasable
  leaves the precaution row exactly as the detector wrote it. **Silence never
  lifts a hold.**

**RETIRED IN PART BY THE OWNER'S WORD OF 13 SEP 2026: a protected record is
filed by the person.** A held file -- rules, identifier, entity reading or gate
-- is no longer put to site G at all: `cli.ask_the_situation` counts it `held`
and goes on, the holds block says "held and not asked", and no model's answer
lifts a hold or opens the cloud. Measured on the second corpus, the local judge
was right 17 times, wrong 42 and silent 10 at 92 seconds a file, and it lifted
the holds on two key-protected files -- so the call bought a name nobody reads
until the person files the record. The first two arms above are gone with it and
the third is now the whole rule, reached without asking: the precaution's row
stands exactly as the detector wrote it, whatever any model would have said.
What the tests below measure is that nothing is asked, nothing is sent and
nothing is lifted, and that the person's own lift is still a lift.

**NO OLLAMA AND NO NETWORK.** `test_site_g_end_to_end`'s stub server is imported
rather than copied, and its answers are cited out of the dossier's own released
evidence -- an invented span is refused by the validator and the test would be
measuring the validator instead of the wiring.

**THE CORPUS IS TWO FILES AND ONE OF THEM IS HELD.** `Passport syllabus.txt`
matches `identity`'s work type `passport` and `academic`'s `syllabus`, one term
each: `never_alone` abstains, the precaution holds it, and the shortlist it is
asked from carries one ordinary option and one protected one -- which is what
makes both directions of the ruling reachable on one file.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import cli
from recognition.detector import Abstention, situation_outcome_of
from model_situation import _abstention_item, question_for
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import reclassify
from readers.model_deepseek import CLOUD
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    LOCAL,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from test_local_model_fact_pass import MODEL_ID, StubOllama, dossier_in
from test_site_g_end_to_end import (
    LABEL, SITUATION, _decline, _dispatching, _invented,
)

#: The held file. Its name carries `identity`'s work type and `academic`'s
#: context term, one each -- see the module docstring for why both are needed.
HELD_NAME = "Passport syllabus.txt"
#: The ordinary situation the file's other term names, and the one the stub
#: answers with. A `SCHEMA_IDS` member; not authored here. The safety domain the
#: precaution reads the file as -- `identity` -- no longer needs a name of its
#: own: since 13 Sep 2026 no answer is given about a held file, so no test picks
#: the hold's own domain as one.
ORDINARY_SITUATION = "academic"


def _corpus(root: Path) -> Path:
    """Two files: one the rules hold, one they do not.

    The companion is `test_local_model_fact_pass`'s own syllabus, unchanged, so a
    run here and a run there are runs of the same shape. It is here because a
    corpus of one held file proves nothing about a mixed folder, which is the only
    kind a person has.
    """
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    (corpus / HELD_NAME).write_text(
        "Passport\nHong Kong Special Administrative Region\n"
        "Date of birth: 1 January 1990\n")
    return corpus


def _naming(situation: str, *, kind: str | None = None):
    """An answer that names ONE situation, cited out of released evidence.

    `test_site_g_end_to_end._situation_answer` names whichever option comes first,
    which is right for the wiring it measures and cannot say anything here: the
    whole question in this file is what happens for THIS situation and THIS kind,
    and picking them is the experiment.

    A situation the shortlist does not carry is not answered at all -- the file
    declines instead -- because a test that quietly asked an off-list question
    would be measuring the validator's refusal and calling it a hold.
    """
    def answer(dossier: dict) -> str:
        options = tuple(dossier.get("allowed_vocabulary", ()))
        released = [item for item in dossier.get("released_evidence", ())
                    if isinstance(item, dict) and isinstance(item.get("value"), str)
                    and item["value"].strip()]
        if situation not in options or not released:
            return _decline(dossier)
        item = released[0]
        payload = {"situation": situation, "alternatives": []}
        if kind is not None:
            payload["restricted_kind"] = kind
        return json.dumps({"claims": [{
            "payload": payload,
            "citations": [{
                "evidence_ref": item["observation_key"],
                "cited_span": item["value"].strip().splitlines()[0],
                "why_it_supports": "this line is what the shortlist rests on"}],
        }]})
    return answer


#: ONE RUN PER ANSWER, SHARED BY THE TESTS THAT READ IT. A `cli.main` run over a
#: real corpus is the most expensive thing in this suite and five of them would be
#: five minutes for five facts about the same five databases. Keyed by the answer's
#: own name, so two tests wanting different answers cannot silently share a run.
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


def _read(database: Path):
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _held_file(conn) -> str:
    (row,) = conn.execute("SELECT file_id FROM files WHERE filename = ?",
                          (HELD_NAME,)).fetchall()
    return row["file_id"]


def _classifications(conn, file_id: str) -> list[sqlite3.Row]:
    """Every row ever written about this file, oldest first -- superseded ones
    included, because "superseded, never deleted" is half of what is asserted."""
    return list(conn.execute(
        "SELECT * FROM classifications WHERE file_id = ? ORDER BY rowid",
        (file_id,)))


def _the_hold(rows) -> sqlite3.Row:
    (hold,) = [row for row in rows if row["basis"] == "safety_domain"]
    return hold


# --- the file is not asked, and nothing about it is assembled --------------------


def _g_dossiers(conn, file_id: str) -> int:
    """How many dossiers site G built for this file."""
    return conn.execute(
        "SELECT COUNT(*) FROM llm_dossier WHERE call_site = ? AND subject_ref = ?",
        (cli.G_SITUATION_SENSITIVITY, file_id)).fetchone()[0]


def test_a_file_the_rules_hold_is_not_asked_and_no_dossier_is_built(
        tmp_path_factory, monkeypatch):
    """THE OWNER'S WORD OF 13 SEP 2026 -- a protected record is filed by the
    person -- so a held file is not put to site G at all.

    This test is the inverse of the one it replaces. Gap 24 put every held file to
    the local model with the precaution's own report in its dossier; the ruling
    withdrew the call, so the thing to measure is that NOTHING was assembled: no
    dossier row, which is the record of what a model was shown, and therefore no
    prompt, no call and nothing off this file at all.

    THE COMPANION IS THE CONTROL, and it is what makes this an assertion about the
    hold rather than about a pass that did not run. The syllabus beside the held
    file is asked and has its dossier; the two differ in the hold and in nothing
    else this site reads.

    SABOTAGE: drop the `current.protected` skip from `ask_the_situation`. A
    dossier appears for a file the person has not filed yet.
    """
    database, _report, _stub = _run("released", _naming(ORDINARY_SITUATION),
                                    tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    (companion,) = conn.execute(
        "SELECT file_id FROM files WHERE filename != ?", (HELD_NAME,)).fetchall()
    free = companion["file_id"]

    assert _g_dossiers(conn, held) == 0, (
        "a protected record was assembled for a model, which is what the "
        "owner's word of 13 Sep 2026 ended")
    assert _g_dossiers(conn, free) == 1, (
        "the pass did not run at all, so the line above says nothing about "
        "the hold")
    # And the hold is still there, unasked and unretired -- marked and counted,
    # never silently dropped.
    hold = _the_hold(_classifications(conn, held))
    assert hold["protected"] == 1 and hold["superseded_by"] is None


def test_a_file_the_rules_do_not_hold_carries_no_hold_in_its_dossier():
    """The negative twin. A phrase printed on every abstention item would say
    nothing, and would spend the shared dossier prefix `104` R-58 protects on the
    absence of a fact.

    ASKED OF THE ITEM AND NOT OF A RUN, and that is deliberate rather than
    cheaper. Whether an ordinary file reaches site G at all depends on what the
    rules made of it, and MEASURED IN THIS HARNESS the syllabus beside the held
    file is not asked -- the rules settle it without a model, which is `00`:110
    working. A twin that asserted on that file's dossier would be asserting on a
    dossier the product may be right not to build, and would go red for a reason
    that has nothing to do with the hold. The positive half above is measured on
    the wire, where it belongs; this half is measured where the phrase is written.

    SABOTAGE: make `_held_phrase` return its sentence unconditionally.
    """
    abstention = Abstention(
        "no_corroboration", ORDINARY_SITUATION,
        "one authored term and every node row carries a `never_alone` rule",
        matched_terms=((ORDINARY_SITUATION, ("syllabus",)),),
        evidence_refs=("sha256:one",))
    question = question_for(situation_outcome_of(abstention),
                            file_id="f-1", content_hash="h-1")

    assert question.precaution is None
    item = _abstention_item(question)
    assert "held:" not in item.location, item.location
    # And the rest of the report is untouched -- this gap ADDS a phrase to an item
    # the ratified text already describes; it does not rewrite one.
    assert "recogniser abstention" in item.location
    assert "syllabus" in item.location


def test_a_held_file_is_never_offered_a_cloud_target(
        tmp_path_factory, monkeypatch):
    """RULING 1, the half that must never move. A protected file reaches the LOCAL
    model only, opened on this machine for it and never sent to the cloud
    (`104` §18.7).

    Asked on the run where the hold STANDS -- the model declined -- because on the
    run where it was released the file is deliberately no longer protected, and
    asking there would measure the lift instead of the bar.

    Asked of `model_route_permitted`, the predicate `target_for` is built from,
    which calls the gate's own `protected_cloud_denies` rather than respelling it.
    Under `CLOUD_ENABLED_MODE`, because under `offline` every file answers the same
    and the assertion would be about the mode. `ask_the_situation` raises
    `ProtectedFileOfferedACloudTarget` if the record and the route ever disagree.

    SABOTAGE: make `model_route_permitted` return `True` for a protected record on
    a cloud locality. This goes red, and so does `test_per_file_model_route`.
    """
    database, _report, _stub = _run("declined", _decline, tmp_path_factory,
                                    monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    hold = _the_hold(_classifications(conn, held))
    assert hold["protected"] == 1 and hold["superseded_by"] is None

    def permitted(locality: str) -> bool:
        return cli.model_route_permitted(
            conn, locality=locality,
            unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
            operation_mode=cli.CLOUD_ENABLED_MODE)(held)

    assert permitted(CLOUD) is False
    assert permitted(LOCAL) is True


def test_no_model_answer_makes_a_held_file_ordinary_for_the_route_after(
        tmp_path_factory, monkeypatch):
    """THE CONSEQUENCE THE LIFT USED TO HAVE, measured now that the 13 Sep 2026
    word has taken the lift away: the route that comes after still refuses the
    file the cloud.

    Asked on the run where the model is answering ORDINARY, which is the dangerous
    direction and the reason the ruling exists: on the second corpus that answer
    lifted the holds on two key-protected files, and under the tuple ratified on
    12 Sep a lifted hold was a cloud clearance, so both would have crossed at the
    fact pass. The file is not asked, so the answer is never given about it, and
    site A's route reads exactly what the rules wrote.

    Asked of `model_route_permitted`, the predicate `target_for` is built from,
    under `CLOUD_ENABLED_MODE` -- under `offline` every file answers the same and
    the assertion would be about the mode.

    SABOTAGE: drop the `current.protected` skip from `ask_the_situation`. The
    ordinary verdict supersedes the hold and the cloud opens for a passport.
    """
    database, _report, _stub = _run("released", _naming(ORDINARY_SITUATION),
                                    tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)

    assert cli.model_route_permitted(
        conn, locality=CLOUD,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.CLOUD_ENABLED_MODE)(held) is False, (
        "a model's ordinary answer opened the cloud for a held file, which is "
        "the crossing the owner's word of 13 Sep 2026 stopped")
    assert held in cli._protected_file_ids(conn)


# --- no verdict is given, so none decides what becomes of the hold ---------------


def test_no_verdict_exists_to_lift_the_hold_because_the_file_is_not_asked(
        tmp_path_factory, monkeypatch):
    """WHAT REPLACES THE LIFT under the owner's word of 13 Sep 2026: a held file is
    not asked, so there is no accepted verdict for it and nothing supersedes the
    precaution's row.

    Read on the run whose stub names an ACCEPTED, cited, on-the-list ordinary
    situation with no restricted kind -- the answer that used to release the hold,
    and the one the second corpus showed the local judge giving about two
    key-protected files. The row a person opens is still the one the detector
    wrote: unsuperseded, protected, with no second row beside it.

    THE TWO OTHER ARMS ARE GONE WITH THE CALL, and this is why they are not tested
    beside this one: with no verdict, "the model agreed" and "the model named a
    restricted kind" are answers about a question nobody put, and the row they
    would have written cannot be reached from any run.

    SABOTAGE: drop the `current.protected` skip from `ask_the_situation`. The
    ordinary verdict supersedes the hold and every assertion here goes red.
    """
    database, _report, _stub = _run("released", _naming(ORDINARY_SITUATION),
                                    tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    rows = _classifications(conn, held)

    assert [row["basis"] for row in rows] == ["safety_domain"], (
        "a model wrote a row about a file it was never asked about")
    assert rows[0]["superseded_by"] is None
    assert rows[0]["supersede_reason"] is None
    assert rows[0]["protected"] == 1
    assert held in cli._protected_file_ids(conn)


# --- silence never lifts a hold --------------------------------------------------


def test_a_decline_leaves_the_hold_exactly_as_the_rules_wrote_it(
        tmp_path_factory, monkeypatch):
    """RULING 2, third arm. "none" is a successful outcome and it is not an
    answer about the hold: the precaution row stands, unsuperseded, and no row is
    written beside it.

    SABOTAGE: write a classification on the decline path. The hold is retired by
    a model that said it could not tell.
    """
    database, _report, stub = _run("declined", _decline, tmp_path_factory,
                                   monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    rows = _classifications(conn, held)

    assert [row["basis"] for row in rows] == ["safety_domain"]
    assert rows[0]["superseded_by"] is None
    assert rows[0]["protected"] == 1
    assert held in cli._protected_file_ids(conn)


def test_a_rejected_claim_leaves_the_hold(tmp_path_factory, monkeypatch):
    """RULING 2, third arm again, by the other road: the model answered, the
    answer was perfectly cited, and P8 REFUSED it because the situation was not on
    the list it was shown. A refused claim is not an answer either.

    SABOTAGE: read the situation off the payload instead of through
    `situation_named_by_verdict`, and an invention retires a hold.
    """
    database, _report, _stub = _run("rejected", _invented, tmp_path_factory,
                                    monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    rows = _classifications(conn, held)

    assert [row["basis"] for row in rows] == ["safety_domain"]
    assert rows[0]["superseded_by"] is None
    assert held in cli._protected_file_ids(conn)


# --- the person is told ----------------------------------------------------------


def test_the_report_says_the_hold_was_not_asked_about(tmp_path_factory,
                                                     monkeypatch):
    """RULING 3, re-argued on the owner's word of 13 Sep 2026: the holds block no
    longer says what a model made of the hold, because no model was asked.

    What a person is owed here changed with the rule. It was four numbers -- held,
    released, confirmed, still held -- and the last of them meant "the model could
    not say". It is now one sentence: the file is protected, a protected record is
    filed by the person, and nothing about it was sent anywhere. `released` and
    `confirmed` stay on the screen as zeros because the block's three lines still
    divide `held`, and a line that vanishes makes the arithmetic unreadable.

    BOTH RUNS ARE ASSERTED AND THEY SAY THE SAME THING, which is the pin. One
    stub names an accepted ordinary situation and the other declines; the block
    is identical, because what the model would have answered is not a fact about
    a file it was never shown.

    SABOTAGE: delete the `_print_the_holds` call from `_print_situation_pass`, or
    let the skip in `ask_the_situation` count anything but `held`.
    """
    _database, released, _stub = _run("released", _naming(ORDINARY_SITUATION),
                                      tmp_path_factory, monkeypatch)
    _database, declined, _stub = _run("declined", _decline, tmp_path_factory,
                                      monkeypatch)

    for said in (" ".join(released.split()), " ".join(declined.split())):
        assert ("were holding 1 file, and a protected record is filed by "
                "the person" in said), said
        assert "no model is asked about one" in said
        assert "0 released by the model" in said
        assert "0 confirmed by the model" in said
        assert "1 held and not asked" in said
        assert "still held because nothing could say" not in said, (
            "the retired sentence blamed the model's silence for a hold no "
            "model was asked about")


def test_a_hold_the_person_has_already_lifted_is_not_a_hold_on_the_next_run(
        tmp_path_factory, monkeypatch):
    """THE MARK IS THE ROW, and the row is what this pass asks about.

    `Detector.precaution_report` answers "would the rules hold this file", which
    is the same answer as "is the precaution's row live" only until something
    stronger supersedes it. §8.4 says a classification "can be revised by the
    user", and `privacy.learning_seam.reclassify` is that revision: it writes a
    `user_confirmed` row over the precaution's. The file's TERMS do not change, so
    on the next run the detector reads exactly what it read before.

    A pass that took the detector's word alone would then tell the local model
    "the rules are holding this file" about a file the person had already
    released, count it among the held, and -- because `assign` is outranked by
    `user_confirmed` and writes nothing -- print it as STILL HELD on the one
    screen that exists to say what became of somebody's protected files. Three
    untruths from one missing lookup, on the safety block.

    TWO RUNS OVER ONE DATABASE, which is what makes this reachable at all: the
    correction has to survive into a later scan, and it does, because `files` and
    `classifications` are the same rows the second run reads.

    THE OWNER'S WORD OF 13 SEP 2026 -- a protected record is filed by the person --
    is what this test now measures from both sides: the person's lift is the only
    thing that lifts a hold, and it also decides whether the file is ASKED. On the
    first run the hold stands and no dossier is built; on the second the person has
    filed the record, so the file is ordinary, it is asked like any other, and the
    report in its dossier carries no hold.

    SABOTAGE: take the hold off `Detector.precaution_report` instead of the store's
    live row in `ask_the_situation`. The block reappears over a file the person
    already released, and the file is skipped instead of asked.
    """
    shared, _report, _stub = _run("declined", _decline, tmp_path_factory,
                                  monkeypatch)
    # ITS OWN COPY, AND THIS IS THE ONLY TEST HERE THAT NEEDS ONE. `_RUNS` hands
    # the same database to four tests because a `cli.main` run is the most
    # expensive thing in this suite -- and every other one of them opens it
    # `mode=ro`. This one WRITES: the person's lift, and then a second scan over
    # the same rows, which is the whole point of it ("TWO RUNS OVER ONE
    # DATABASE" above).
    #
    # Sharing a MUTATED database is what made this module's result a property of
    # the order it ran in. Measured 21 Sep 2026: under the suite's random
    # ordering, four seeds in five put this test before
    # `test_a_decline_leaves_the_hold_exactly_as_the_rules_wrote_it` and
    # `test_a_held_file_is_never_offered_a_cloud_target`, and both went red on
    # `superseded_by is None` -- reading the `user_confirmed` row THIS test
    # wrote. In definition order it runs last and they pass, so the suite was
    # green by arrangement rather than by isolation.
    #
    # A COPY RATHER THAN A SECOND RUN: the run is what costs, and this needs the
    # run's rows and not its process. `Connection.backup` rather than a file copy
    # because a WAL database is more than one file on disk.
    database = tmp_path_factory.mktemp("lifted") / "plan.sqlite"
    _source = sqlite3.connect(f"file:{shared}?mode=ro", uri=True)
    _copy = sqlite3.connect(str(database))
    with _copy:
        _source.backup(_copy)
    _copy.close()
    _source.close()
    conn = sqlite3.connect(str(database))
    conn.row_factory = sqlite3.Row
    held = _held_file(conn)
    hold = _the_hold(_classifications(conn, held))
    assert hold["superseded_by"] is None, "the run under test did not hold it"
    content_hash = conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?", (held,)
    ).fetchone()["content_hash"]

    # THE PERSON'S OWN ANSWER: this is not a passport, it is coursework.
    reclassify(
        conn, held, cli.ORDINARY_CLASS,
        "the person said this is not a protected document",
        store=ClassificationStore(conn), content_hash=content_hash,
        protected=False, evidence_refs=json.loads(hold["evidence_refs"]),
        user_id="t", component_version=cli.COMPONENT_VERSION,
        observed_at="2026-09-10T12:00:00+00:00")
    conn.commit()
    conn.close()

    # The same corpus, the same database, scanned again. The corpus is the
    # shared run's -- nothing writes to it -- and the database is this test's own.
    root = Path(shared).parent
    with StubOllama(answer=_dispatching(_decline)) as stub:
        monkeypatch.setenv(LOCAL_MODEL_NAME, MODEL_ID)
        monkeypatch.setenv(LOCAL_BASE_URL_NAME, stub.base_url)
        out = io.StringIO()
        code = cli.main(
            [str(root / "holder" / "corpus"), "--situation", SITUATION,
             "--label", LABEL, "--user", "t", "--database", str(database)],
            out=out)
    assert code == 0, out.getvalue()
    said = " ".join(out.getvalue().split())

    assert "Protected holds" not in said, (
        "a hold the person had already lifted was counted and printed as held")
    # AND THE FILE IS ASKED, which is the other half of the person's lift. The
    # first run built no dossier -- the hold stood, and a held file is not asked
    # -- so the ONE report in the table is the second run's, and it carries no
    # hold because by then there was none.
    conn = _read(database)
    reports = [
        item["location"]
        for row in conn.execute(
            "SELECT payload FROM llm_dossier WHERE call_site = ? "
            "AND subject_ref = ? ORDER BY rowid",
            (cli.G_SITUATION_SENSITIVITY, held))
        for item in json.loads(row["payload"])["evidence_items"]
        if item["kind"] == "recogniser_abstention"]
    assert len(reports) == 1, reports
    assert "held:" not in reports[0], reports[0]
