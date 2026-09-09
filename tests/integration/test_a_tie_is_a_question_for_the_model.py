# tests/integration/test_a_tie_is_a_question_for_the_model.py
"""R-166: an unresolved tie, over a real run, and exactly what stands between it
and a model.

`00`:39 is the authority and it names this file's subject in its own words: the LLM
receives evidence packets for files that *"remain ambiguous, have multiple plausible
domains, or contain language that requires interpretation"*, and *"must return
unknown where support is insufficient"*. A tie is that file. Today it is not asked,
and 95 of the owner's 199 files are in this state -- for those files no rule, no
model and no person has decided anything.

`tests/integration/test_situation_site_boundary.py` already pins the three walls
against SYNTHETIC abstentions. This file is the same question asked of the product:
one offline `cli.main` run over one résumé, and every step measured on what the real
detector, the real evidence table and the real privacy gate actually do.

**WHAT R-166 CHANGED, and it is the precondition the rest of the route needs.**
`00`:42 requires the model to cite -- *"A model that cannot cite sufficient evidence
must return unknown"* -- and until now an `Abstention` named its readings and not one
observation behind them. `model_situation.question_for` therefore took `evidence_refs`
as an argument the caller had to supply from somewhere, and
`questions.triggers.tied_readings_and_the_files_they_reach` cited the string
`subject:<value>` instead, its own comment saying "an abstention carries no evidence
refs of its own". It carries them now, they are the matches the decision was already
made from, and the tests below resolve every one of them against P4's table.

**THE GATE IS NOT THE BLOCKER, WHICH IS WORTH SAYING BECAUSE IT WAS.** `104` R-121
and R-02 settled §8.4's Open question 5 under one name -- `privacy.denial.
UNCLASSIFIED_PERMITS_LOCAL` -- and it is `True`. Measured below on this file:
`model_route_permitted` answers `True` for a LOCAL target and `False` for a cloud
one, which is `00`:189-193's hybrid rule ("sensitive files remain LOCAL") working
rather than failing. The file the recogniser could not read may already be shown to a
model on the person's own machine.

**WHAT IS ACTUALLY IN THE WAY IS THE CALL SITE, AND IT IS THE OWNER'S ACT.**
`llm_harness.vocabulary.CALL_SITES` is a closed tuple of six whose sixth member
records "ADDED 2026-09-02 WITH THE OWNER'S APPROVAL". `model_situation` names the
seventh, `G_situation_sensitivity`, and refuses to build a request under it. Behind
that stand two more: no prompt is ratified for the site, and
`privacy.vocabulary.CLASSIFICATION_BASES` has four members and none of them names a
model, so a verdict has nowhere lawful to be written. Q-M puts all three together.

No model is configured (`conftest` sets `GRAPH_AGENT_NO_DOTENV=1`) and nothing here
reaches a network.
"""
from __future__ import annotations

import io
import json
import sqlite3

import pytest

import cli
import model_situation
from facts.domains import SCHEMA_IDS
from model_situation import (
    NONE_OF_THESE, SITUATION_SENSITIVITY, question_for,
)
from privacy.classification_store import ClassificationStore
from questions.store import activated_schemas
from recognition.detector import Abstention, Detector
from recognition.rules import load_rules

RESUME = "Jane Doe resume.txt"


def _local_target():
    """The one target this site has. `104` §17.1: nothing leaves the device.

    Read off the product's own routing rather than built here would be better and
    is not available offline -- `conftest` sets `GRAPH_AGENT_NO_DOTENV=1`, so no
    client is configured and `routing.client_for` has nothing to answer with. What
    the request builder reads off a target is its locality, and `local` is the only
    value this site may carry.
    """
    from readers.model_routing import ModelTarget

    return ModelTarget(provider="ollama", model_id="offline", locality=cli.LOCAL)

#: The two readings a résumé honestly has. `00`'s own example of the case: the same
#: document is the thing you send an employer and the thing you send an admissions
#: office, and its own words do not say which.
TIED = ("career", "college_applications")


@pytest.fixture(scope="module")
def measured(tmp_path_factory):
    root = tmp_path_factory.mktemp("tie")
    corpus = root / "corpus"
    corpus.mkdir()
    (corpus / RESUME).write_text(
        "Jane Doe\nCurriculum Vitae / Resume\n\n"
        "Work experience\n"
        "2024-2026  Software Engineer, Acme Corp. Job title: Software Engineer.\n"
        "2022-2024  Intern, Beta Ltd.\n\n"
        "Education\nBSc Computer Science, Columbia University, 2022\n\n"
        "Cover letter enclosed. Applying for the Senior Engineer role.\n"
        "References available on request.\n")

    database = root / "plan.sqlite"
    out = io.StringIO()
    assert cli.main(
        [str(corpus), "--situation", "academic.coursework", "--label", "Coursework",
         "--user", "t", "--database", str(database)], out=out) == 0, out.getvalue()

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def _version(conn) -> tuple[str, str]:
    row = conn.execute(
        "SELECT file_id, content_hash FROM files WHERE filename = ?",
        (RESUME,)).fetchone()
    assert row is not None, f"{RESUME!r} is not in the run"
    return row["file_id"], row["content_hash"]


def _verdict(conn) -> Abstention:
    """Composed as `cli.run` composes it, which is the only way to read it back.

    `test_step4_recognition_as_a_gate::test_the_schema_the_detector_settled_on_is_
    not_written_down_anywhere` is why: the verdict reaches no column, so a second
    detector is the only reader there is.
    """
    detector = Detector(
        load_rules(cli._RECOGNITION_MANIFEST.read_text),
        handling_for=cli.HANDLING_POLICY,
        now=lambda: "2026-09-08T00:00:00+00:00",
        is_protected=cli.is_protected_container,
        corroborating_observations=cli._identifier_observations,
        settled_by_user=lambda: activated_schemas(conn))
    outcome = detector.explain(conn, *_version(conn))
    assert isinstance(outcome, Abstention), repr(outcome)
    return outcome


# --- the tie, and what it now rests on -------------------------------------------


def test_the_run_leaves_the_resume_tied_between_two_readings(measured):
    outcome = _verdict(measured)

    assert outcome.reason == "ambiguous", outcome.detail
    assert set(outcome.tied_schema_ids) == set(TIED), outcome.tied_schema_ids
    assert outcome.deferred_readings, (
        "no authored `needs_llm` reading came with the tie, so there is nothing "
        "that says in prose what a model would have to decide")


def test_the_tie_names_the_terms_each_reading_matched(measured):
    """R-166. Not "these two schemas tied" on trust -- what each one matched.

    `career` and `college_applications` both match `resume`, and each has one word
    the other does not: a curriculum vitae is the admissions reading's, a cover
    letter is the employment reading's. That is why nothing breaks the tie and why
    the question is worth putting.
    """
    outcome = _verdict(measured)

    per_schema = dict(outcome.matched_terms)
    assert set(per_schema) == set(TIED), outcome.matched_terms
    assert all(terms for terms in per_schema.values()), outcome.matched_terms
    assert "resume" in per_schema["career"], per_schema
    assert "resume" in per_schema["college_applications"], per_schema
    assert [schema_id for schema_id, _ in outcome.matched_terms] == [
        schema_id for schema_id in SCHEMA_IDS if schema_id in set(TIED)], (
        "the order is the library's, so the same file puts the same question "
        "however the matches arrived: " + repr(outcome.matched_terms))


def test_every_citation_the_tie_carries_resolves_in_the_evidence_table(measured):
    """`00`:42's precondition, measured against P4 rather than asserted.

    A citation the validator cannot resolve is worse than none: it would let a
    model's answer be accepted against a reference to nothing. These are the
    observation keys the matches were found in, so each must be a live row of this
    file version's own evidence -- not a neighbour's, not superseded.
    """
    outcome = _verdict(measured)
    file_id, content_hash = _version(measured)

    assert outcome.evidence_refs, (
        "the tie cites nothing, so the question cannot be put under `00`:42")
    for ref in outcome.evidence_refs:
        row = measured.execute(
            "SELECT file_id, content_hash FROM evidence WHERE observation_key = ? "
            "AND superseded_by IS NULL", (ref,)).fetchone()
        assert row is not None, f"{ref} resolves to no live observation"
        assert (row["file_id"], row["content_hash"]) == (file_id, content_hash), (
            f"{ref} is another file's observation, so the citation would put one "
            "file's words behind another file's answer")
    assert len(set(outcome.evidence_refs)) == len(outcome.evidence_refs), (
        "one observation cited twice is one signal counted twice")


# --- the question the model would be asked ---------------------------------------


def test_the_tie_becomes_a_question_with_valid_options_and_a_way_out(measured):
    """`00`:39 and constitution 3. The options are the recogniser's own candidates.

    The model chooses among the readings the file raised; it does not pick from the
    23 schemas, and it cannot name one nobody proposed -- `00`:42 forbids the LLM
    inventing a fact schema and `recognition/_CONTRACT.md` rule 5 forbids the
    recogniser inventing a class to let the pipeline continue.

    `none_of_these` is the shape `00`'s "must return unknown where support is
    insufficient" lands in: a real answer, always available, always last. Correct
    abstention is a successful outcome, and a closed list without it would be a
    forced choice.
    """
    outcome = _verdict(measured)
    file_id, content_hash = _version(measured)

    question = question_for(
        outcome, file_id=file_id, content_hash=content_hash,
        matched_terms=outcome.matched_terms, evidence_refs=outcome.evidence_refs)

    assert question.allowed_situations[-1] == NONE_OF_THESE
    assert set(question.allowed_situations[:-1]) == set(TIED)
    assert NONE_OF_THESE not in SCHEMA_IDS
    assert question.reason == outcome.reason
    assert question.evidence_refs == outcome.evidence_refs, (
        "the question cites something other than what the recogniser matched")
    assert question.matched_terms == outcome.matched_terms


def test_nothing_in_the_question_is_authored_by_the_code_that_builds_it(measured):
    """Every string in it came from the library, the file, or the recogniser.

    The failure this guards is the one `00` names outright: a rule that decides what
    the model should decide, arriving as a helpful default in the prompt.
    """
    outcome = _verdict(measured)
    file_id, content_hash = _version(measured)
    question = question_for(
        outcome, file_id=file_id, content_hash=content_hash,
        matched_terms=outcome.matched_terms, evidence_refs=outcome.evidence_refs)

    for option in question.allowed_situations:
        assert option in SCHEMA_IDS or option == NONE_OF_THESE, option
    for schema_id, terms in question.matched_terms:
        for term in terms:
            assert term in json.dumps(
                json.loads(cli._RECOGNITION_MANIFEST.read_text(encoding="utf-8"))
                ["schemas"][schema_id]), (
                f"{term!r} is not one of {schema_id}'s authored terms")


# --- the gate is not what is in the way ------------------------------------------


def test_the_unclassified_file_has_no_classification_record_at_all(measured):
    """The premise of the two tests below, and the reason the gate is asked twice.

    An abstention returns `None` from `Detector.__call__` unless a safety domain
    raised precaution, so this file has no record -- which is `resolve_class(None)`,
    `unreadable_unclassified`, the name `104` R-02 measured as a sentence about the
    detector rather than about the bytes.
    """
    file_id, content_hash = _version(measured)

    assert ClassificationStore(measured).current(file_id, content_hash) is None


def test_a_local_model_may_already_be_asked_about_this_file(measured):
    """R-121 AND R-02, MEASURED: the gate blocker is closed for a local target.

    §8.4's Open question 5 -- may an unclassified file reach a LOCAL model -- had
    two answers in two places, and the second was blocking the owner's unclassified
    files before the gate was ever asked. It is one answer now, under one name, and
    it is yes. So "the gate refuses the file the recogniser could not read" is no
    longer true of the route, and nothing here has to widen it.
    """
    file_id, _ = _version(measured)

    permitted = cli.model_route_permitted(
        measured, locality="local",
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.OPERATION_MODE)

    assert cli.UNCLASSIFIED_PERMITS_LOCAL is True
    assert permitted(file_id) is True, (
        "the route refuses a local model the very file that needs one; the tie "
        "cannot become a question while this is False")


def test_and_a_cloud_target_is_still_refused_for_it(measured):
    """The half that must NOT move. `00`:189-193: sensitive files remain LOCAL, and
    an unclassified file is one nothing has classified -- asking a provider about it
    is exactly the wrong direction. `104` R-159's locality rules say the same thing
    about what may be released: a `path` or `ocr` observation releases to a LOCAL
    target and a whole unit is cloud-forbidden."""
    file_id, _ = _version(measured)

    permitted = cli.model_route_permitted(
        measured, locality="cloud",
        unclassified_permits_local=cli.UNCLASSIFIED_PERMITS_LOCAL,
        operation_mode=cli.CLOUD_ENABLED_MODE)

    assert permitted(file_id) is False


# --- what is in the way ----------------------------------------------------------


def test_the_question_is_asked_now_and_the_request_is_built_from_the_real_run(
        measured):
    """THE WALL, OPENED, and reached from a real run rather than from a fixture.

    This test used to assert the refusal: `build_situation_request` counted the
    files waiting and named all three reasons -- the site, the prompt, and the basis
    a verdict would be written under -- and said that none of them was an
    engineering step. `104` §17.1 is the owner's act that made all three false on
    8 September 2026, and what it asserts now is the request that refusal described,
    built over the résumé this module has been measuring since the top.

    Everything above still holds and is what makes the request legal: the tie is
    real, it cites observations that resolve against P4's own table, and the route
    permits a local model this file.
    """
    outcome = _verdict(measured)
    file_id, content_hash = _version(measured)
    question = question_for(
        outcome, file_id=file_id, content_hash=content_hash,
        matched_terms=outcome.matched_terms, evidence_refs=outcome.evidence_refs)

    from llm_harness.vocabulary import CALL_SITES
    assert SITUATION_SENSITIVITY in CALL_SITES
    assert len(CALL_SITES) == 7

    observations = cli.releasable_observations(
        measured, file_id=file_id, content_hash=content_hash,
        limit=cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS, locality=cli.LOCAL,
        ceiling=cli.GROUPING_LIMITS.max_dossier_tokens)
    assert observations, (
        "the résumé has readings the recogniser matched on and none of them is "
        "releasable to a local model; the tie could then never be put to one")

    request = model_situation.build_situation_request(
        question, observations,
        model_target=_local_target(), prompt=cli.situation_prompt(),
        max_dossier_tokens=cli.GROUPING_LIMITS.max_dossier_tokens)

    assert request.call_site == SITUATION_SENSITIVITY
    assert request.subject_ref == file_id
    assert request.eligibility_reason == "multiple_plausible_domains", (
        "`ambiguous` IS `00`:39's multiple plausible domains, and the request says "
        "so in P8's vocabulary rather than in the recogniser's")
    offered = {item.evidence_ref
               for item in request.evidence_items if item.kind == "candidate_schema"}
    assert offered == set(TIED) | {NONE_OF_THESE}
    assert offered <= set(SCHEMA_IDS) | {NONE_OF_THESE}, (
        "an option outside the library is `recognition/_CONTRACT.md` rule 5's "
        "invention arriving through the prompt")


def test_every_reading_the_request_asks_for_is_this_files_own(measured):
    """`gate._resolve` refuses an item whose observation lives outside the target's
    file ids, AFTER the release has been minted. One file and no neighbour is what
    this site asks for, so the two can never disagree."""
    outcome = _verdict(measured)
    file_id, content_hash = _version(measured)
    question = question_for(
        outcome, file_id=file_id, content_hash=content_hash,
        matched_terms=outcome.matched_terms, evidence_refs=outcome.evidence_refs)
    observations = cli.releasable_observations(
        measured, file_id=file_id, content_hash=content_hash,
        limit=cli.FACT_CALL_MAX_RELEASED_OBSERVATIONS, locality=cli.LOCAL,
        ceiling=cli.GROUPING_LIMITS.max_dossier_tokens)

    request = model_situation.build_situation_request(
        question, observations,
        model_target=_local_target(), prompt=cli.situation_prompt(),
        max_dossier_tokens=cli.GROUPING_LIMITS.max_dossier_tokens)

    assert request.model_call_request.target.file_ids == (file_id,)
    for item in request.model_call_request.requested_items:
        row = measured.execute(
            "SELECT file_id, content_hash FROM evidence WHERE observation_key = ? "
            "AND superseded_by IS NULL", (item.observation_key,)).fetchone()
        assert row is not None, f"{item.observation_key} resolves to nothing"
        assert (row["file_id"], row["content_hash"]) == (file_id, content_hash)
