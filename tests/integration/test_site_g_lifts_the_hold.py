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
from recognition.detector import Abstention
from model_situation import NONE_OF_THESE, _abstention_item, question_for
from privacy.classification_store import ClassificationStore
from privacy.learning_seam import reclassify
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
from test_local_model_fact_pass import MODEL_ID, StubOllama, dossier_in
from test_site_g_end_to_end import (
    LABEL, SITUATION, _decline, _dispatching, _invented,
)

#: The held file. Its name carries `identity`'s work type and `academic`'s
#: context term, one each -- see the module docstring for why both are needed.
HELD_NAME = "Passport syllabus.txt"
#: The safety domain the precaution reads it as, and the ordinary situation the
#: shortlist also offers. Both are `SCHEMA_IDS` members; neither is authored here.
HELD_DOMAIN = "identity"
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


# --- the file is asked, and the hold is in the question --------------------------


def test_a_file_the_rules_hold_is_asked_and_its_dossier_carries_the_hold(
        tmp_path_factory, monkeypatch):
    """RULING 1. Every file the precaution marked is put to site G, and G's
    dossier carries the precaution's own report as evidence-shaped context.

    The report rides on the `recogniser_abstention` item the ratified text already
    describes as "the reason the rules stopped ... a report, not a verdict" -- so
    the model meets no kind the approved prompt never explains. What it now says
    is which safety domain, which of its work types, and in which P4 zone: on r19
    the model was asked to judge held files and was shown no word of the hold.

    THE TERMS ARE THE LIBRARY'S AND NOT THE PERSON'S. `passport` is an authored
    work type; nothing out of the file's own text reaches the prompt through this
    item, which is the same guarantee `matched` already carries.

    SABOTAGE: drop `precaution=precaution` from the `question_for` call in
    `ask_the_situation`, or `_held_phrase` from `_abstention_item`.
    """
    database, _report, stub = _run("released", _naming(ORDINARY_SITUATION),
                                   tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)

    (payload,) = conn.execute(
        "SELECT payload FROM llm_dossier WHERE call_site = ? AND subject_ref = ?",
        (cli.G_SITUATION_SENSITIVITY, held)).fetchall()
    dossier = json.loads(payload["payload"])
    (report,) = [item for item in dossier["evidence_items"]
                 if item["kind"] == "recogniser_abstention"]

    assert "held:" in report["location"], report["location"]
    assert HELD_DOMAIN in report["location"]
    assert "passport" in report["location"]
    assert "filename" in report["location"]
    # And the shortlist still ends with the decline, which is what keeps the
    # question a question rather than a forced choice about a protected file.
    assert dossier["allowed_vocabulary"][-1] == NONE_OF_THESE


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
        "one authored term and every node row carries a `never_alone` rule")
    question = question_for(abstention, file_id="f-1", content_hash="h-1",
                            matched_terms=((ORDINARY_SITUATION, ("syllabus",)),),
                            evidence_refs=("sha256:one",))

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


def test_a_released_file_is_ordinary_for_the_route_that_comes_after(
        tmp_path_factory, monkeypatch):
    """RULING 2, the consequence the lift exists for: "the file is then ordinary
    for every later pass in the same run (site A's route, placement)".

    The situation pass runs BEFORE the fact pass and before placement -- it has to,
    because the schema it names is what chooses site A's allowlist -- so a hold
    lifted here is lifted in time to change where the file goes. This is the same
    predicate the test above asks of a standing hold, asked of a released one, and
    the two together are what say the lift is a real change of route rather than a
    row nobody reads.

    SABOTAGE: write G's row without letting `assign` supersede the precaution's.
    Two live rows would wedge the store; one live protected row keeps this red.
    """
    database, _report, _stub = _run("released", _naming(ORDINARY_SITUATION),
                                    tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)

    assert cli.model_route_permitted(
        conn, locality=CLOUD,
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.CLOUD_ENABLED_MODE)(held) is True, (
        "the local model released this file and the route still treats it as "
        "protected, so the lift changed nothing a person would notice")


# --- the verdict decides what becomes of the hold --------------------------------


def test_an_accepted_ordinary_verdict_lifts_the_hold_by_supersession(
        tmp_path_factory, monkeypatch):
    """RULING 2, first arm. A VALIDATED, ACCEPTED claim naming an ordinary
    situation, with resolved citations and no restricted kind, releases the hold.

    Three things are asserted and they are three different claims: the precaution
    row is SUPERSEDED (not edited and not deleted -- it is still readable, with
    its reason and its link), the row that supersedes it is G's own
    `local_model_situation` at `protected=0` and `privacy_class='ordinary'`, and
    the file is no longer in the set every later pass reads as protected. The
    third is the one that matters to a person: on r19, 11 ordinary files were
    routed local-only and withheld from placement for no reason.

    SABOTAGE: pass `held=True` unconditionally into `situation_classification`,
    and this file stays protected forever.
    """
    database, _report, _stub = _run("released", _naming(ORDINARY_SITUATION),
                                    tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    rows = _classifications(conn, held)
    hold = _the_hold(rows)

    assert hold["superseded_by"] is not None, (
        "the hold was never retired, so the local model's answer changed nothing")
    assert hold["supersede_reason"], (
        "§8.2 retains the old record AND the reason it was superseded")
    (lifted,) = [row for row in rows if row["fact_id"] == hold["superseded_by"]]
    assert lifted["basis"] == LOCAL_MODEL_SITUATION
    assert lifted["protected"] == 0
    assert lifted["privacy_class"] == PRIVACY_CLASS_ORDINARY
    assert lifted["supersedes"] == hold["fact_id"]
    # The set every later pass reads. `_protected_file_ids` is the one query the
    # report, the route and the review sets share, so this is the lift arriving
    # where it has to arrive.
    assert held not in cli._protected_file_ids(conn)


def test_a_verdict_naming_a_safety_situation_keeps_the_hold(
        tmp_path_factory, monkeypatch):
    """RULING 2, second arm, first half: a protected situation confirms the hold,
    and G's own protected row supersedes the precaution's so the record shows the
    model AGREED rather than showing only that the rules had guessed.

    This is the path r19 already exercised on 2 of the 5 true marks; it is pinned
    here so the release arm cannot be widened over it by accident.

    SABOTAGE: read `protected` off anything but `HANDLING_POLICY` for the named
    situation.
    """
    database, _report, _stub = _run("confirmed", _naming(HELD_DOMAIN),
                                    tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    rows = _classifications(conn, held)
    hold = _the_hold(rows)

    assert hold["superseded_by"] is not None
    (agreed,) = [row for row in rows if row["fact_id"] == hold["superseded_by"]]
    assert agreed["basis"] == LOCAL_MODEL_SITUATION
    assert agreed["protected"] == 1
    assert held in cli._protected_file_ids(conn)


def test_a_named_restricted_kind_keeps_the_hold_under_an_ordinary_situation(
        tmp_path_factory, monkeypatch):
    """RULING 2, second arm, second half -- AND THE ONE THAT WAS BROKEN.

    A passport in a coursework folder is protected whatever its situation, and
    `privacy_class_for`'s precedence already says so. But `HANDLING_POLICY`
    answers for the SITUATION and knows nothing about the kind, so a verdict
    naming an ordinary situation AND a protected restricted kind wrote
    `protected=0` beside `privacy_class='protected'` -- and because
    `llm_supported` outranks `possible`, that row superseded the precaution's.
    The gate still refused the file every model (it reads the class), and
    `_protected_file_ids` -- which the report, the placement route and the review
    sets read -- saw an ordinary file. The hold was lifted by the very answer that
    should have confirmed it.

    SABOTAGE: drop `or (held and restricted_kind is not None)` from
    `situation_classification`. `protected` reads 0 here and the file becomes
    filable.
    """
    database, _report, _stub = _run(
        "kind", _naming(ORDINARY_SITUATION, kind=PROTECTED_KIND_IDENTITY_DOCUMENT),
        tmp_path_factory, monkeypatch)
    conn = _read(database)
    held = _held_file(conn)
    rows = _classifications(conn, held)
    hold = _the_hold(rows)

    assert hold["superseded_by"] is not None
    (agreed,) = [row for row in rows if row["fact_id"] == hold["superseded_by"]]
    assert agreed["basis"] == LOCAL_MODEL_SITUATION
    assert agreed["privacy_class"] == PRIVACY_CLASS_PROTECTED
    assert agreed["protected"] == 1, (
        "the model named a passport and the file was released to placement")
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


def test_the_report_says_what_became_of_the_hold(tmp_path_factory, monkeypatch):
    """RULING 3, on a real run. A person reading the screen is told how many files
    the rules held, how many the model released, how many it confirmed, and how
    many it left held because it could not say.

    On r19 the answer was 16 held, 5 of them rightly, and every one of them read
    as the single word "protected" with nothing saying which.

    SABOTAGE: delete the `_print_the_holds` call from `_print_situation_pass`.
    """
    _database, released, _stub = _run("released", _naming(ORDINARY_SITUATION),
                                      tmp_path_factory, monkeypatch)
    said = " ".join(released.split())

    assert "the rules were holding 1 file on a safety term" in said
    assert "1 released by the model" in said
    assert "0 confirmed by the model" in said
    assert "0 still held because nothing could say" in said

    _database, declined, _stub = _run("declined", _decline, tmp_path_factory,
                                      monkeypatch)
    said = " ".join(declined.split())
    assert "the rules were holding 1 file on a safety term" in said
    assert "0 released by the model" in said
    assert "1 still held because nothing could say" in said


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

    SABOTAGE: drop the `current.basis in SAFETY_DOMAIN_BASES` test in
    `ask_the_situation`. The block reappears and says 1 held, 1 still held.
    """
    database, _report, _stub = _run("declined", _decline, tmp_path_factory,
                                    monkeypatch)
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

    # The same corpus, the same database, scanned again.
    root = Path(database).parent
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

    assert "Protected holds the model looked at" not in said, (
        "a hold the person had already lifted was counted and printed as held")
    # And the dossier does not tell the model the rules are holding it either.
    # THE LAST ONE, because the first run's dossier is still in the table and
    # SHOULD say `held:` -- the rules were holding the file when it was built.
    # Both are asserted: one says the phrase arrives when there is a hold, the
    # other that it stops arriving when the person has lifted it.
    conn = _read(database)
    reports = [
        item["location"]
        for row in conn.execute(
            "SELECT payload FROM llm_dossier WHERE call_site = ? "
            "AND subject_ref = ? ORDER BY rowid",
            (cli.G_SITUATION_SENSITIVITY, held))
        for item in json.loads(row["payload"])["evidence_items"]
        if item["kind"] == "recogniser_abstention"]
    assert len(reports) == 2, reports
    assert "held:" in reports[0]
    assert "held:" not in reports[-1], reports[-1]
