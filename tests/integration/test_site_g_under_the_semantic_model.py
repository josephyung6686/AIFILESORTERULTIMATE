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

**THE HELD FILE IS NO LONGER ASKED (13 Sep 2026, the owner's word: a protected
record is filed by the person).** The defect above is about the two files the
recognisers do not hold, and they are still asked -- turning the weights on may
neither narrow what a model is offered nor widen who is put to it. The third file
is held by the rules, and `cli.ask_the_situation` now counts it `held` and goes on
before it reads what any recogniser proposed, so the composition is measured on
the two files it can still be measured on and the hold is measured as a hold.

**NO OLLAMA AND NO NETWORK.** The stubs are gap 24's own, imported rather than
copied so a run here and a run there are runs of the same shape.
"""
from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path

import cli
from facts.domains import SCHEMA_IDS
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

#: The safety domain the RULES hold the third file as -- `identity` -- and the
#: ordinary reading they also raise for it need no names of their own since
#: 13 Sep 2026: the file is not asked, so no shortlist of its readings is built
#: and no test reads one.

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
    # THE WHOLE LIBRARY SINCE `00` amendment 7(c), where this read `== 3`. What the
    # vector raised is still the thing this test is about and it is still measured
    # -- on the candidate items and in the report, two assertions down -- but it is
    # no longer the boundary of what the model may answer. `104` §18.56: the
    # boundary held the right answer for 35 of 87 files.
    assert len(options) == len(SCHEMA_IDS) + 1, options
    raised = {item["evidence_ref"]: item["location"]
              for item in dossier["evidence_items"]
              if item["kind"] == "candidate_schema"}
    for near in (NEAR_ONE, NEAR_TWO):
        assert "raised this for this file, on no term" in raised[near], raised[near]
    report = _report(dossier)
    assert "reason: no_evidence" in report, report
    assert f"{NEAR_ONE}: no term" in report and f"{NEAR_TWO}: no term" in report, (
        "a candidate the file matched nothing for is a candidate the vector "
        "raised, and saying so is what keeps 'near in vector space' from "
        "reading as 'said this word'")


def test_a_semantic_proposal_with_no_hold_is_asked_too(tmp_path_factory,
                                                       monkeypatch):
    """`00`:110 NO LONGER STANDS WHERE THE VECTOR SETTLED THE FILE EITHER.

    **WHAT THIS ASSERTED, and it was the lexical rule applied to the vector.** "A
    proposal clear of the release floor and clear of its runner-up is a
    recognition: the composed recogniser writes the classification for it, so the
    situation pass has nothing to ask and spending a local call would be asking
    about a file this run had already filed." No dossier, and the `settled` line
    counted it.

    `00` amendment 7(c) ends it on both paths at once, and the vector is the one
    where it matters more: a nearest neighbour clear of a floor is a weaker
    conclusion than a term the library authored, and the file it settles is
    cloud-eligible the moment the row is written. Measured on the second corpus,
    the rules' own top-1 accuracy on the files they named was 32.2%.

    The vector's record is still what it was -- basis `detector`, written by the
    composed recogniser -- and it is still checked below, because what changed is
    who else looks, not who wrote the row. Its twin above still differs only in
    what the vector said about it.

    SABOTAGE: restore the `outcome.recognised is not None` continue and this file
    goes back to being filed on a nearest neighbour nobody re-read.
    """
    database, said, _stub = _run("named", _situation_answer, tmp_path_factory,
                                 monkeypatch)
    conn = _read(database)
    settled = _file_id(conn, SETTLED_NAME)

    assert _dossiers(conn, settled) != [], (
        "a file the vector proposed a situation for was not put to the model, "
        "which is the state `00` amendment 7(c) ended")
    assert "the rules had already recognised" in " ".join(said.split()), (
        "what the recognisers settled is still counted, as a fact about them")
    records = _classifications(conn, settled)
    assert "detector" in {record["basis"] for record in records}, (
        "the vector's own record, written by the composed recogniser, still "
        "stands in the store; the model's answer supersedes it rather than "
        "replacing the history of it")


def test_a_semantic_proposal_the_rules_hold_is_not_asked(tmp_path_factory,
                                                         monkeypatch):
    """GAP 24b ON THE SEMANTIC PATH, WITHDRAWN by the owner's word of 13 Sep 2026:
    a protected record is filed by the person, and that is true however the file
    came to be recognised.

    The vector proposed an ordinary situation for this file and the RULES are
    holding it as one of `00`'s four. Gap 24b put exactly that disagreement to the
    model; the ruling says the hold ends the question rather than starting it, so
    no dossier is built, no shortlist is assembled and nothing about the file is
    sent. The two unheld files are asked on the same run, which is what keeps this
    an assertion about the hold and not about the weights.

    SABOTAGE: drop the `current.protected` skip from `ask_the_situation`. A
    protected record is assembled for a model on the strength of a vector.
    """
    database, _said, _stub = _run("named", _situation_answer, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)

    assert _dossiers(conn, _file_id(conn, HELD_NAME)) == [], (
        "a protected record was assembled for a model, which is what the "
        "owner's word of 13 Sep 2026 ended")
    for filename in (ASKED_NAME, SETTLED_NAME):
        assert len(_dossiers(conn, _file_id(conn, filename))) == 1, (
            "the composed recogniser reached nothing this run, so the line "
            "above says nothing about the hold")
    # And the hold stands where the rules wrote it, unasked and unretired.
    hold = _the_hold(_classifications(conn, _file_id(conn, HELD_NAME)))
    assert hold["protected"] == 1 and hold["superseded_by"] is None


def test_the_similarity_path_never_raises_one_of_the_four_as_a_candidate(
        tmp_path_factory, monkeypatch):
    """`104` §18.11 AND THE CONSTITUTION, on the wire. A safety domain is RAISED
    for a file by the TERM detector or not at all.

    **THE ASSERTION MOVED FROM THE MENU TO THE CANDIDATES, and the rule is
    untouched.** Under `00` amendment 7(c) every menu holds all four safety
    domains, on every file, because the menu is the whole library -- so "not on
    the shortlist" is no longer a thing that can be measured about a file, and it
    was never what this rule was about. What the rule forbids is the SIMILARITY
    PATH concluding something about one of `00`'s four, and that is exactly what a
    raised candidate is: the recogniser saying it read this file as plausibly
    that. An item reading "in the library; not raised for this file" is the vector
    saying nothing, which is what the veto requires of it.

    The measurement behind the rule is `SemanticFloors`': this path can neither
    protect nor release one of `00`'s four -- a Red Cross certificate outscores an
    HKID -- so it names none of them and offers none of them as a near miss.

    `VETOED` is scored level with the two ordinary readings on the asked file,
    which is UNDER the caution line: the veto does not fire, the recogniser
    abstains `inside_margin`, and the domain is named among the tied readings
    precisely because it is refusing to judge it. Offering a model a domain the
    recogniser has just said it cannot judge would be the guess the whole veto
    exists to refuse. The file carries no authored medical term at all.

    **THE HELD FILE IS NO LONGER PART OF THIS MEASUREMENT** (13 Sep 2026, the
    owner's word: a protected record is filed by the person). This test used to
    finish by reading the held file's own dossier and checking that the safety
    domain on it had been raised by the TERM detector rather than by the vector.
    There is no such dossier: a held file is not asked. Nothing of the rule is
    lost -- the rule is about what the SIMILARITY path may conclude, and the two
    files it is measured on below are the two it ever proposed for. What the term
    detector raises for a file nobody asks about is not a question this site
    answers any more.

    SABOTAGE: drop the `not in self._safety` filter from the composed recogniser's
    merge. `medical` appears on the shortlist of a file with no authored term in
    it at all.
    """
    database, _said, _stub = _run("named", _situation_answer, tmp_path_factory,
                                  monkeypatch)
    conn = _read(database)

    for filename in (ASKED_NAME, SETTLED_NAME):
        for dossier in _dossiers(conn, _file_id(conn, filename)):
            for domain in cli.SAFETY_DOMAIN_HANDLING:
                (item,) = [i for i in dossier["evidence_items"]
                           if i["kind"] == "candidate_schema"
                           and i["evidence_ref"] == domain]
                assert "not raised for this file" in item["location"], (
                    f"the similarity path raised {domain}, which the veto "
                    f"forbids it: {item['location']}")


# --- the counts a person reads still close ---------------------------------------


def test_the_hold_counts_close_under_the_semantic_model_too(
        tmp_path_factory, monkeypatch):
    """`PrecautionHolds`' three arms still partition `held` under the owner's word
    of 13 Sep 2026, on a run where the vector is what recognised two of the three
    files -- and now all of `held` sits in one of them.

    The block used to have two live arms on this corpus: the answering run
    released the hold and the declining run left it standing. Neither happens now;
    a protected record is filed by the person, so `released` and `confirmed` are
    zero on every run and `held and not asked` carries the whole count. Both runs
    are read for exactly that reason -- the block must say the same thing whatever
    the model would have answered, because the model was not asked.

    **THE ROSTER PARTITION IS NOT ASSERTED HERE, and it is open rather than
    moved.** The held file lands in none of the five counters that partition the
    roster, so on this corpus they account for two files of three. What still
    closes is this block, and this block is what is pinned.

    SABOTAGE: count the skipped file as `declined`, or drop `_print_the_holds`
    from `_print_situation_pass` -- the first says a model was asked about a
    protected record, the second leaves the only line that mentions it off the
    screen entirely.
    """
    for key, answer in (("named", _situation_answer), ("declined", _decline)):
        _database, report, _stub = _run(key, answer, tmp_path_factory,
                                        monkeypatch)
        said = " ".join(report.split())
        # `00` amendment 7(c): this read `1 settled by rule`, a file nobody asked.
        # The count survives as a fact about the recognisers, and since 13 Sep it
        # counts the ASKED files the rules recognised -- the held one is not one.
        assert "the rules had already recognised" in said
        assert ("were holding 1 file, and a protected record is filed by "
                "the person" in said), said
        assert "0 released by the model" in said
        assert "0 confirmed by the model" in said
        assert "1 held and not asked" in said


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
