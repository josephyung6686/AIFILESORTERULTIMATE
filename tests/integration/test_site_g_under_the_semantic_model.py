# tests/integration/test_site_g_under_the_semantic_model.py
"""`104` §18.26's owed row, on the wire: site G asks under `--semantic-model` too.

**THE DEFECT, AND IT WAS TOTAL.** `cli.ask_the_situation` read the recogniser's
answer by asking `isinstance` whether it was a `Recognition` or an `Abstention`.
Those are the TERM detector's two record classes. With the weights named, the
object the run classifies with is `SemanticRecogniser`, whose `explain` returns a
`SemanticProposal` or a `SemanticAbstention` -- neither of which is either -- so
every file failed both tests, every file took the `settled` branch, and the site
that decides which situation a file is asked under, and whether it may leave the
device at all, asked NOTHING. The screen reported the rules had settled the whole
corpus. The comment at the call site claimed the opposite: that the composed
recogniser "is what raises a candidate for the 60 `no_evidence` files".

**HOW THIS IS MEASURED WITHOUT THE WEIGHTS.** The 90.4 MB `all-MiniLM-L6-v2` ONNX
model is fetched by hand and lives outside this repository, so `--semantic-model`
cannot be given here. It does not have to be: the design's own seam is that the
similarity is INJECTED -- *"the deployment owns the model, and this package
computes no vector and names no encoder"* -- so what a deployment with weights
supplies is a `SchemaSimilarity`, and that is what is supplied below. The
composition under test is the real `SemanticRecogniser` around the real `Detector`,
reached through the real `cli.main`, over a real corpus, with a real local model
stub. Only the vector arithmetic is the test's.

**NO OLLAMA AND NO NETWORK.** The stubs are gap 24's own, imported rather than
copied so a run here and a run there are runs of the same shape.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import cli
from model_situation import NONE_OF_THESE
from recognition.semantic import SemanticRecogniser, SimilarityReading
from readers.model_ollama import (
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from test_local_model_fact_pass import MODEL_ID, StubOllama
from test_site_g_end_to_end import (
    LABEL, SITUATION, _decline, _dispatching, _situation_answer,
)
from test_site_g_lifts_the_hold import _classifications, _read, _the_hold

#: THE CORPUS: three files, one per arm of the ruling.
#:
#: `IMG_4021.txt` carries no term any schema authored -- it is one of the 60
#: `no_evidence` files, the bucket the semantic path exists for.
#: `notes to self.txt` is its twin and differs only in what the vector says.
#: `Passport syllabus.txt` is `test_site_g_lifts_the_hold`'s own held file,
#: unchanged, so the hold measured here is the hold measured there.
ASKED_NAME = "IMG_4021.txt"
SETTLED_NAME = "notes to self.txt"
HELD_NAME = "Passport syllabus.txt"

#: What the vector says about each file. All three are ordinary schemas: the
#: similarity path may name none of `00`'s four and this corpus never asks it to.
NEAR_ONE = "career"
NEAR_TWO = "photos"
PROPOSED = "creative"

#: The safety domain the RULES hold the third file as, and the ordinary reading
#: they also raise for it. Both are `SCHEMA_IDS` members; neither is authored here.
HELD_DOMAIN = "identity"
RULES_READING = "academic"

#: Prose with no authored term in it, used for the two `no_evidence` files.
NOTHING_AUTHORED = ("A photograph of a bicycle in the rain, taken while waiting "
                    "for the bus that never came.\n")


def _corpus(root: Path) -> Path:
    corpus = root / "semantic" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / ASKED_NAME).write_text(NOTHING_AUTHORED)
    (corpus / SETTLED_NAME).write_text(NOTHING_AUTHORED)
    (corpus / HELD_NAME).write_text(
        "Passport\nHong Kong Special Administrative Region\n"
        "Date of birth: 1 January 1990\n")
    return corpus


def _similarity(scores_by_filename):
    """The `SchemaSimilarity` a deployment's weights would supply.

    **THE CITATIONS ARE REAL AND HAVE TO BE.** `SimilarityReading.evidence_refs`
    are "the P4 observation keys whose text went into the vector", and a
    `local_model_situation` record that carries none is refused at the
    constructor -- so a stub that invented a key would measure a crash rather than
    the question. These are read back out of the file's own evidence rows.

    `chars` is the caller's own floor rather than a number: what this stub is
    saying is "enough of the file's own text to be worth a vector", and
    `SEMANTIC_MIN_CHARS` is where the deployment put that line.
    """
    def similarity(conn, file_id, content_hash):
        (filename,) = conn.execute(
            "SELECT filename FROM files WHERE file_id = ?", (file_id,)).fetchone()
        scores = scores_by_filename.get(filename)
        refs = tuple(row[0] for row in conn.execute(
            "SELECT observation_key FROM evidence WHERE file_id = ? "
            "AND content_hash = ? AND superseded_by IS NULL ORDER BY rowid",
            (file_id, content_hash)))
        if scores is None or not refs:
            return None
        return SimilarityReading(scores=dict(scores), evidence_refs=refs,
                                 scope=cli.scope_for(cli.SEMANTIC_ZONES,
                                                     cli.SEMANTIC_CHAR_BUDGET),
                                 chars=cli.SEMANTIC_MIN_CHARS)
    return similarity


#: The two readings the vector leaves INSIDE the margin on the asked file, and the
#: one it is clear about on its twin. Read against `cli.SEMANTIC_FLOORS`, which is
#: the deployment's own measured table and is not restated here.
#:
#: **`VETOED` IS THE DISCRIMINATING CASE.** It scores level with the two ordinary
#: readings, which puts it UNDER the caution line -- so the safety veto does not
#: fire, the abstention is an ordinary `inside_margin`, and the domain lands in
#: `tied_schema_ids` because the recogniser is refusing to judge it. That is the
#: exact shape in which one of `00`'s four could reach a shortlist with nothing
#: but a vector behind it.
VETOED = "medical"
_INSIDE_THE_MARGIN = {
    NEAR_ONE: cli.SEMANTIC_FLOORS.release,
    NEAR_TWO: cli.SEMANTIC_FLOORS.release,
    VETOED: cli.SEMANTIC_FLOORS.release,
}
_CLEAR_OF_IT = {
    PROPOSED: cli.SEMANTIC_FLOORS.release + cli.SEMANTIC_FLOORS.margin,
    NEAR_ONE: cli.SEMANTIC_FLOORS.release - cli.SEMANTIC_FLOORS.margin,
}

SCORES = {
    ASKED_NAME: _INSIDE_THE_MARGIN,
    SETTLED_NAME: _CLEAR_OF_IT,
    HELD_NAME: _CLEAR_OF_IT,
}


def _with_the_weights(monkeypatch):
    """`--semantic-model`, with the deployment's encoder replaced by the stub.

    `_semantic_classifier` is the composition root's own off switch: it hands the
    term detector straight back when no weights are named, and builds the composed
    recogniser when they are. Patched here so the run takes the SECOND branch
    without a 90 MB download -- everything else about the object, including that
    the term detector is what it is composed around, is the shipped construction.
    """
    def composed(rules, detector, semantic_model, now):
        return SemanticRecogniser(
            lexical=detector, schema_similarity=_similarity(SCORES),
            floors=cli.SEMANTIC_FLOORS, handling_for=cli.HANDLING_POLICY,
            now=now, min_chars=cli.SEMANTIC_MIN_CHARS,
            is_protected=cli.is_protected_container)

    monkeypatch.setattr(cli, "_semantic_classifier", composed)


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
    _with_the_weights(monkeypatch)
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


def _dossiers(conn, file_id: str) -> list[dict]:
    return [json.loads(row["payload"]) for row in conn.execute(
        "SELECT payload FROM llm_dossier WHERE call_site = ? AND subject_ref = ? "
        "ORDER BY rowid", (cli.G_SITUATION_SENSITIVITY, file_id))]


def _report(dossier: dict) -> str:
    (item,) = [item for item in dossier["evidence_items"]
               if item["kind"] == "recogniser_abstention"]
    return item["location"]


# --- the 60 files become askable -------------------------------------------------


def test_a_no_evidence_file_is_asked_with_the_candidates_the_vector_raised(
        tmp_path_factory, monkeypatch):
    """**THE OWED ROW, MEASURED.** A file carrying no term any schema authored is
    put to the local model, with the vector's own near readings on its shortlist.

    Before this it was not asked under `--semantic-model` and it was not asked
    without it either: the lexical side raises nothing for a `no_evidence` file --
    60 of the owner's 112 abstentions -- and the composed recogniser's candidates
    could not reach the pass at all. So this file had no dossier, no call, and no
    line on any screen beyond a `settled by rule` that was false.

    THE REASON IS STILL THE RULES'. What stopped the file is that no authored term
    is in it; the vector did not stop it, it failed to settle it. And each
    candidate is reported with NO term, which is where the model reads that a
    vector raised it rather than a word in the file.

    SABOTAGE: bind `explain=classify_producer.explain` at the composition root
    again. No dossier is built for any file in this corpus and the unpack below
    raises.
    """
    database, _said, _stub = _run("named", _situation_answer, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)

    (dossier,) = _dossiers(conn, _file_id(conn, ASKED_NAME))
    options = dossier["allowed_vocabulary"]

    assert NEAR_ONE in options and NEAR_TWO in options
    assert options[-1] == NONE_OF_THESE
    assert len(options) == 3, options
    report = _report(dossier)
    assert "reason: no_evidence" in report, report
    assert f"{NEAR_ONE}: no term" in report and f"{NEAR_TWO}: no term" in report, (
        "a candidate the file matched nothing for is a candidate the vector "
        "raised, and saying so is what keeps 'near in vector space' from "
        "reading as 'said this word'")


def test_a_semantic_proposal_with_no_hold_is_settled_and_never_asked(
        tmp_path_factory, monkeypatch):
    """`00`:110 STANDS WHERE THE VECTOR SETTLED THE FILE. A proposal clear of the
    release floor and clear of its runner-up is a recognition: the composed
    recogniser writes the classification for it, so the situation pass has nothing
    to ask and spending a local call would be asking about a file this run had
    already filed.

    Its twin above differs only in what the vector said about it -- same bytes,
    same rules, same absence of any authored term.

    SABOTAGE: return the proposal as an abstention carrying the leader as a
    candidate. This file gets a dossier and the `settled` count drops.
    """
    database, said, _stub = _run("named", _situation_answer, tmp_path_factory,
                                 monkeypatch)
    conn = _read(database)
    settled = _file_id(conn, SETTLED_NAME)

    assert _dossiers(conn, settled) == [], (
        "a file the recogniser settled without a model was put to the model")
    assert "1 settled by rule" in " ".join(said.split())
    (record,) = _classifications(conn, settled)
    assert record["basis"] == "detector", (
        "the vector's own record, written by the composed recogniser, is what "
        "makes this file settled -- so the pass counting it settled agrees with "
        "the store rather than contradicting it")


def test_a_semantic_proposal_the_rules_hold_is_asked(tmp_path_factory,
                                                     monkeypatch):
    """GAP 24b ON THE SEMANTIC PATH. A hold outranks `00`:110 however the file came
    to be recognised: the vector proposed a situation for it, the RULES are holding
    it as one of `00`'s four, and the model is asked which of the readings is
    right.

    THE SHORTLIST CARRIES ALL THREE READINGS AND THE HOLD IS ONE OF THEM. Turning
    the weights on may never narrow what a model is offered, so the rules' own
    reading of this file survives beside the vector's proposal -- and the safety
    domain is on the list because the TERM detector put it there. The similarity
    path proposes none of `00`'s four and offers none of them as a near miss.

    SABOTAGE: drop the `precaution is None` half of the `settled` test. This file
    is settled on the vector's word while a `protected=1` row taken on the word
    `passport` in a filename stands over it, unasked and unexamined.
    """
    database, _said, _stub = _run("named", _situation_answer, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)

    (dossier,) = _dossiers(conn, _file_id(conn, HELD_NAME))
    options = dossier["allowed_vocabulary"]

    assert HELD_DOMAIN in options, "the hold is an option or it is not a question"
    assert RULES_READING in options, (
        "the rules' own reading of this file survived the vector's proposal")
    assert PROPOSED in options
    report = _report(dossier)
    assert f"recognised this file as {PROPOSED}" in report, report
    assert "held:" in report and HELD_DOMAIN in report and "passport" in report


def test_the_similarity_path_never_puts_one_of_the_four_on_a_shortlist(
        tmp_path_factory, monkeypatch):
    """`104` §18.11 AND THE CONSTITUTION, on the wire. A safety domain reaches a
    site G shortlist through the TERM detector or not at all.

    The measurement behind the rule is `SemanticFloors`': this path can neither
    protect nor release one of `00`'s four -- a Red Cross certificate outscores an
    HKID -- so it names none of them and offers none of them as a near miss.

    `VETOED` is scored level with the two ordinary readings on the asked file,
    which is UNDER the caution line: the veto does not fire, the recogniser
    abstains `inside_margin`, and the domain is named among the tied readings
    precisely because it is refusing to judge it. Offering a model a domain the
    recogniser has just said it cannot judge would be the guess the whole veto
    exists to refuse. The file carries no authored medical term at all.

    The held file's shortlist is not asserted set-for-set here: an abstention's
    tied readings are the term detector's own and may include a safety domain the
    file's words really did name, which is that recogniser's business and this
    ruling's business only through the hold.

    SABOTAGE: drop the `not in self._safety` filter from the composed recogniser's
    merge. `medical` appears on the shortlist of a file with no authored term in
    it at all.
    """
    database, _said, _stub = _run("named", _situation_answer, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)

    for filename in (ASKED_NAME, SETTLED_NAME):
        for dossier in _dossiers(conn, _file_id(conn, filename)):
            assert not set(dossier["allowed_vocabulary"]) & set(
                cli.SAFETY_DOMAIN_HANDLING), dossier["allowed_vocabulary"]

    (held,) = _dossiers(conn, _file_id(conn, HELD_NAME))
    assert HELD_DOMAIN in held["allowed_vocabulary"], (
        "the hold is an option, and it is the term detector that put it there")


# --- the counts a person reads still close ---------------------------------------


def test_the_four_hold_counts_close_under_the_semantic_model_too(
        tmp_path_factory, monkeypatch):
    """`PrecautionHolds`' three arms partition `held`, on a run where the vector is
    what recognised two of the three files.

    On the answering run the held file is released by the model; on the declining
    run its hold stands. Both print the block, and in both the three sentences add
    up to the one above them -- which is what makes the numbers a person can check
    rather than four tallies drifting apart.

    SABOTAGE: count a semantically-proposed hold as `settled` as well as asking
    it. The partition over-counts and the `settled by rule` assertion goes red.
    """
    _database, named, _stub = _run("named", _situation_answer, tmp_path_factory,
                                   monkeypatch)
    said = " ".join(named.split())
    assert "1 settled by rule" in said
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


def test_a_held_file_the_vector_proposed_for_is_never_routed_off_this_device(
        tmp_path_factory, monkeypatch):
    """THE HALF THAT MUST NEVER MOVE (`104` §18.7). Making a semantically-proposed
    file askable is exactly the change that could open a new door to a protected
    file being offered a cloud target, and `ask_the_situation` raises
    `ProtectedFileOfferedACloudTarget` if the record and the route ever disagree.

    Asked on the run where the hold STANDS: on the answering run the file is
    deliberately no longer protected, and asking there would measure the lift
    instead of the bar.

    SABOTAGE: make `model_route_permitted` return `True` for a protected record on
    a cloud locality.
    """
    from readers.model_deepseek import CLOUD
    from readers.model_ollama import LOCAL

    database, _said, _stub = _run("declined", _decline, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)
    held = _file_id(conn, HELD_NAME)
    hold = _the_hold(_classifications(conn, held))

    assert hold["superseded_by"] is None, "the run under test did not hold it"

    def permitted(locality: str) -> bool:
        return cli.model_route_permitted(
            conn, locality=locality,
            unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
            operation_mode=cli.CLOUD_ENABLED_MODE)(held)

    assert permitted(CLOUD) is False
    assert permitted(LOCAL) is True
