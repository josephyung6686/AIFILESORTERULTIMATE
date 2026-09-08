# tests/integration/test_situation_site_boundary.py
"""`104` R-32 and R-37: the seventh site's question, and the three walls it stops at.

R-32 is that the gate refuses every unclassified file a cloud call; R-37 is that the
per-branch situation question was registered, its trigger never fired and its reader
never read. The lead ruled them one question -- which situation is this file part of,
and under what sensitivity class -- so they share one site, asked LOCALLY first
because `00`:189-193's hybrid mode says "sensitive files remain LOCAL".

MEASURED ON THE OWNER'S CORPUS, offline and read-only over the 4 September
extraction, counts only:

| why the file is unclassified | files |
|---|---|
| `no_evidence` -- carries no term any schema authored | 60 |
| `no_corroboration` -- one term, and one signal never activates a schema | 32 |
| `ambiguous` -- schemas tied on term count | 20 |

All 199 files have stored observations, so "nothing to look at" is not one of the
cases; and the stored run classified 90, leaving 109 unclassified, not the 90 the
scoreboard's refusal count suggests.

**The three walls are pinned below and each fails the day it opens**, which is the
signal to wire the next piece rather than a reminder to.
"""
from __future__ import annotations

import pathlib
import sqlite3
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from facts.domains import SCHEMA_IDS  # noqa: E402
from model_situation import (  # noqa: E402
    NONE_OF_THESE,
    SITUATION_SENSITIVITY,
    NothingToAsk,
    build_situation_request,
    question_for,
    shortlist_for,
)
from recognition.detector import Abstention  # noqa: E402


def _abstention(reason: str, schema_id=None, tied=()) -> Abstention:
    return Abstention(reason, schema_id, f"a {reason} case", tuple(tied))


class _Semantic:
    """The shape `SemanticProposal` and `SemanticAbstention` share: a nearest, and
    something beside it. Read by attribute, never imported as a type -- this module
    must not care which of the two it was handed."""

    def __init__(self, schema_id=None, runner_up=None, tied=()):
        self.schema_id = schema_id
        self.runner_up = runner_up
        self.tied_schema_ids = tuple(tied)


class _Observation:
    """The three things `build_situation_request` reads off a P4 observation.

    A stand-in and not a stub of a decision: the real `Observation` is P4's and the
    request builder reads its key, its locator and its reliability and nothing else.
    `test_a_tie_is_a_question_for_the_model` builds the same request over the real
    ones, so what this file measures is the SHAPE and that file measures the wiring.
    """

    def __init__(self, key: str, zone: str):
        from evidence_shape.location import Location

        self.observation_key = key
        self.location = Location(zone=zone)
        self.reliability = "direct"


def _observation(key: str, zone: str) -> _Observation:
    return _Observation(key, zone)


#: A LOCAL target, because that is the only target this site has. `104` §17.1:
#: nothing leaves the device under the ruling that opened it.
class _LocalTargetShape:
    locality = "local"
    model_id = "test-local"
    provider = "test"


_LOCAL_TARGET = _LocalTargetShape()


def _prompt():
    """The deployment's own site-G prompt, read through the manifest row.

    Not a fixture prompt: `prompt_fingerprint` hashes the template id with the
    three files' bytes, so a request built under a made-up definition would carry a
    fingerprint no record could resolve, and `transport.issue` refuses the release
    when the two disagree.
    """
    import cli

    return cli.situation_prompt()


# --- the shortlist is what the recognisers raised, and nothing else --------------


def test_a_tie_becomes_the_tied_schemas_and_a_way_out():
    """`ambiguous`, 20 files on the owner's corpus. The tie IS the shortlist."""
    options = shortlist_for(_abstention("ambiguous", tied=("career", "academic")))

    assert options == ("academic", "career", NONE_OF_THESE)


def test_a_near_miss_becomes_a_shortlist_of_one_and_a_way_out():
    """`no_corroboration`, 32 files: one term matched, and one signal never
    activates a schema. The model is shown the schema that term belongs to and can
    say it does not fit."""
    assert shortlist_for(_abstention("no_corroboration", schema_id="medical")) == \
        ("medical", NONE_OF_THESE)


def test_the_biggest_bucket_has_nothing_to_ask_without_the_semantic_recogniser():
    """THE MEASUREMENT THAT DECIDES WHETHER `--semantic-model` IS OPTIONAL.

    60 of the owner's 112 abstentions are `no_evidence` -- no term any schema
    authored -- so the lexical side raises no candidate at all and there is no
    question with valid options. Those 60 become askable only when the semantic
    recogniser's nearest and runner-up are passed in, which is what makes the two
    mechanisms partners rather than alternatives.
    """
    empty = _abstention("no_evidence")
    assert shortlist_for(empty) == (NONE_OF_THESE,)
    with pytest.raises(NothingToAsk):
        question_for(empty, file_id="f", content_hash="a" * 64)

    with_semantic = shortlist_for(
        empty, _Semantic(schema_id="research", runner_up="academic"))
    assert with_semantic == ("academic", "research", NONE_OF_THESE)
    assert question_for(empty, file_id="f", content_hash="a" * 64,
                        semantic=_Semantic(schema_id="research")).allowed_situations


def test_both_recognisers_contribute_and_neither_orders_the_list():
    """The order is `SCHEMA_IDS`', so the same file gets the same prompt however the
    candidates arrived. `104` R-58 is the same argument about the dossier's bytes."""
    merged = shortlist_for(
        _abstention("ambiguous", schema_id="career", tied=("career", "photos")),
        _Semantic(schema_id="academic", runner_up="photos"))

    assert merged == ("academic", "career", "photos", NONE_OF_THESE)
    assert list(merged[:-1]) == [s for s in SCHEMA_IDS if s in set(merged[:-1])]


def test_a_shortlist_never_carries_a_name_the_library_does_not(monkeypatch):
    """`recognition/_CONTRACT.md` rule 5 forbids inventing a class to let the
    pipeline continue. A candidate from outside the library would be that invention
    arriving through the back door."""
    with pytest.raises(ValueError):
        shortlist_for(_abstention("ambiguous", tied=("academic",)),
                      _Semantic(schema_id="not_a_schema"))


def test_declining_is_always_available_and_always_last():
    for outcome in (_abstention("ambiguous", tied=("academic", "career")),
                    _abstention("no_corroboration", schema_id="legal")):
        options = shortlist_for(outcome)
        assert options[-1] == NONE_OF_THESE
        assert options.count(NONE_OF_THESE) == 1
        assert NONE_OF_THESE not in SCHEMA_IDS


def test_a_question_whose_only_option_is_to_decline_is_refused():
    """Not a question. A model shown one way out and no way in answers something
    about every file it is given."""
    with pytest.raises(NothingToAsk):
        question_for(_abstention("no_evidence"), file_id="f", content_hash="a" * 64)


# --- the three walls -------------------------------------------------------------


def test_wall_one_is_open_and_the_seventh_site_is_a_call_site():
    """THE WALL OPENED, 8 September 2026, and this test is the record of it.

    It was the assertion that `SITUATION_SENSITIVITY` is NOT in `CALL_SITES` and
    that there are six. `104` §17.1 is the owner's act that made both false: the
    seventh member is granted, on the sixth's own precedent -- "THE SIXTH, ADDED
    2026-09-02 WITH THE OWNER'S APPROVAL, RECORDED HERE".

    Kept as an assertion rather than deleted, and turned around rather than
    weakened into a tautology: what it pins now is that the seventh is a MEMBER,
    that it is spelled in exactly one place, and that opening it did not disturb
    the six that were already there. A file that only said "six became seven"
    would let the next member arrive without an approval beside it.
    """
    from llm_harness.vocabulary import CALL_SITES, G_SITUATION_SENSITIVITY

    assert SITUATION_SENSITIVITY in CALL_SITES
    assert len(CALL_SITES) == 7
    assert CALL_SITES[-1] == SITUATION_SENSITIVITY, (
        "the seventh is appended, so the six that records already point at keep "
        "their positions")
    assert SITUATION_SENSITIVITY is G_SITUATION_SENSITIVITY, (
        "the site is spelled in `llm_harness.vocabulary` and re-exported here; "
        "two spellings of one call site is two vocabularies")


def test_wall_one_the_seventh_site_can_carry_a_reason_a_recogniser_produces():
    """A member of `CALL_SITES` that no `DossierRequest` can name is half a wall.

    `records.DossierRequest.__post_init__` checks `eligibility_reason` against
    `ELIGIBILITY_BY_SITE[call_site]`, so a site with no entry raises `KeyError`
    before any of its own checks run. The seventh reuses site A's three -- `00`:39's
    own words, "remain ambiguous, have multiple plausible domains, or contain
    language that requires interpretation" -- because a recogniser tie IS a file
    with multiple plausible domains and a fourth closed list would be a second
    approval taken for one act.
    """
    from llm_harness.vocabulary import (
        ELIGIBILITY_BY_SITE, FACT_ELIGIBILITY, MULTIPLE_PLAUSIBLE_DOMAINS,
        REMAINS_AMBIGUOUS,
    )

    assert ELIGIBILITY_BY_SITE[SITUATION_SENSITIVITY] is FACT_ELIGIBILITY
    assert MULTIPLE_PLAUSIBLE_DOMAINS in ELIGIBILITY_BY_SITE[SITUATION_SENSITIVITY]
    assert REMAINS_AMBIGUOUS in ELIGIBILITY_BY_SITE[SITUATION_SENSITIVITY]


def test_wall_one_a_question_now_becomes_a_request_at_the_seventh_site():
    """WHAT THE REFUSAL BECAME. It counted the files waiting behind three walls and
    named all three; the walls are open and the count is zero, so what is asserted
    now is the request the refusal described.

    Reference-only, and that is the property worth pinning rather than the fact that
    something was returned: `DossierRequest` carries no text, the candidates are the
    library's own ids, and the file's own readings are `Excerpt` items naming
    observation keys. What the model is shown of the file is whatever P7 releases
    for those keys at the door, and nothing here can widen it.
    """
    question = question_for(
        _abstention("ambiguous", tied=("academic", "career")),
        file_id="file-1", content_hash="b" * 64,
        matched_terms=(("academic", ("syllabus",)), ("career", ("resume",))),
        evidence_refs=("sha256:" + "c" * 64,))

    request = build_situation_request(
        question, (_observation("sha256:" + "c" * 64, "heading"),),
        model_target=_LOCAL_TARGET, prompt=_prompt(), max_dossier_tokens=4000)

    assert request.call_site == SITUATION_SENSITIVITY
    assert request.subject_ref == "file-1"
    assert request.eligibility_reason == "multiple_plausible_domains"
    assert request.plan_version is None
    assert request.evidence_snapshot_id is None
    kinds = [item.kind for item in request.evidence_items]
    assert kinds == ["candidate_schema"] * 3 + ["recogniser_abstention", "excerpt"]
    refs = [item.evidence_ref for item in request.evidence_items]
    assert refs[:3] == ["academic", "career", NONE_OF_THESE], (
        "every option the model is offered is described, the way out included; an "
        "option shown in the vocabulary and in no item is the one the prompt most "
        "wants used and the one it says least about")
    assert [item.observation_key
            for item in request.model_call_request.requested_items] == [
        "sha256:" + "c" * 64], "the file's own readings are asked for by key"
    assert request.model_call_request.target.file_ids == ("file-1",), (
        "one file and no neighbour: nothing at this site gathers a neighbour's "
        "readings, and `gate._decisive` reads the first id's handling class as the "
        "one the release is judged under")


def test_wall_one_the_abstention_report_carries_the_recognisers_own_words():
    """The item the ratified prompt calls "a report, not a verdict".

    Everything in it is the recogniser's: its reason, the shortlist it produced,
    and the LIBRARY's authored terms each candidate matched. Nothing about the
    person's file reaches these bytes that the recogniser had not already concluded.
    """
    question = question_for(
        _abstention("no_corroboration", schema_id="medical"),
        file_id="file-2", content_hash="b" * 64,
        matched_terms=(("medical", ("diagnosis",)),))

    request = build_situation_request(
        question, (_observation("sha256:" + "d" * 64, "body"),),
        model_target=_LOCAL_TARGET, prompt=_prompt(), max_dossier_tokens=4000)

    report = next(item for item in request.evidence_items
                  if item.kind == "recogniser_abstention")
    assert "no_corroboration" in report.location
    assert "diagnosis" in report.location
    assert request.eligibility_reason == "remains_ambiguous"

    protected = next(item for item in request.evidence_items
                     if item.evidence_ref == "medical")
    assert "protected" in protected.location, (
        "one of `00`:52's four kinds is marked as one on its own item, so the "
        "prompt's rule about protected material has something to read")


def test_wall_one_a_file_with_no_releasable_reading_is_not_asked():
    """`00`:42, one step earlier than the model.

    A shortlist and nothing to read it against is not a question a model can
    answer: `DossierRequest` would refuse the empty item list and `ModelCallRequest`
    the empty request, both correctly and both from a place that cannot say what
    happened. It is said here instead, and the file stays where the rules left it
    -- which for an unclassified file is local.
    """
    question = question_for(
        _abstention("ambiguous", tied=("academic", "career")),
        file_id="file-3", content_hash="b" * 64)

    with pytest.raises(NothingToAsk):
        build_situation_request(
            question, (), model_target=_LOCAL_TARGET, prompt=_prompt(),
            max_dossier_tokens=4000)


def test_wall_two_is_open_and_a_local_model_verdict_has_a_truthful_basis():
    """THE SECOND WALL OPENED, 8 September 2026, and this is the record of it.

    It was the assertion that a verdict from a model on this device has no lawful
    basis, measured by watching `ClassificationRecord(basis="local_model")` raise.
    `104` §17.1 grants the fifth member, with the owner's intent stated in one
    line: **a model verdict must NEVER be recorded as `detector`.**

    THE SPELLING, AND WHY IT IS NOT `local_model`. `96` §19's lesson governs the
    choice -- a basis word must not overclaim what was checked. What was checked is
    ONE question: which of a SHORTLIST of situations, raised by the recognisers
    themselves, this file is part of. The model was not shown the 23 schemas, was
    not asked what else the file might be, and was not asked to examine it for
    anything outside the list. `local_model` alone reads as "a model looked at this
    file", which is broader than the question that was put; `local_model_situation`
    says which question was answered and by what. That is the same narrowing the
    fourth member made in the other direction, one column along.

    `local` is load-bearing and stays: it says the bytes did not leave the device,
    which is what makes a record about an unclassified file admissible at all
    (`privacy.denial.UNCLASSIFIED_PERMITS_LOCAL`).
    """
    from privacy.classification import ClassificationRecord
    from privacy.vocabulary import CLASSIFICATION_BASES, LOCAL_MODEL_SITUATION

    assert LOCAL_MODEL_SITUATION == "local_model_situation"
    assert LOCAL_MODEL_SITUATION in CLASSIFICATION_BASES
    assert len(CLASSIFICATION_BASES) == 5
    assert CLASSIFICATION_BASES[-1] == LOCAL_MODEL_SITUATION
    assert "detector" not in LOCAL_MODEL_SITUATION, (
        "the owner's stated intent is that a model verdict is never recorded as "
        "`detector`, and a word carrying it would read as one at a glance")

    record = ClassificationRecord(
        file_id="f", content_hash="a" * 64,
        handling_class="personal_non_sensitive", protected=False,
        basis=LOCAL_MODEL_SITUATION, evidence_refs=("sha256:" + "a" * 64,),
        reliability_state="llm_supported",
        observed_at="2026-09-06T00:00:00+00:00")

    assert record.basis == LOCAL_MODEL_SITUATION


def test_wall_two_the_new_basis_still_has_to_cite():
    """The weaker word must not become the way to skip the citation.

    `00`:42 -- "A model that cannot cite sufficient evidence must return unknown"
    -- is stricter here than it is for a detector, not looser: an uncited situation
    answer is not a record written without evidence, it is an `unknown`, and an
    `unknown` writes no record at all. So the fifth basis joins the two detector
    bases in `_EVIDENCE_REQUIRED_BASES` rather than sitting beside `user`, whose
    own act is its evidence.
    """
    from privacy.classification import ClassificationRecord, UnbackedClassification
    from privacy.vocabulary import LOCAL_MODEL_SITUATION

    with pytest.raises(UnbackedClassification):
        ClassificationRecord(
            file_id="f", content_hash="a" * 64,
            handling_class="personal_non_sensitive", protected=False,
            basis=LOCAL_MODEL_SITUATION, evidence_refs=(),
            reliability_state="llm_supported",
            observed_at="2026-09-06T00:00:00+00:00")


def test_wall_two_did_not_widen_what_a_detector_may_claim():
    """The four that were there are unchanged, in their order.

    A fifth member is an addition and not a re-reading of the four: `96` §19's
    split of `detector` still means what it meant, and nothing here lets a
    deterministic rule borrow the model's word or the model borrow a rule's.
    """
    from privacy.vocabulary import CLASSIFICATION_BASES

    assert CLASSIFICATION_BASES[:4] == (
        "detector", "detector_no_safety_evidence", "safety_domain", "user")


def test_wall_three_no_prompt_is_ratified_for_this_site():
    """The shipped A_fact template names fifteen dossier keys "and no others", and
    none of them carries a shortlist. The packet holds the request."""
    from llm_harness.prompt_library import a_fact_template_folder_levels_bytes

    template = a_fact_template_folder_levels_bytes().decode("utf-8")
    assert "allowed_situations" not in template
    assert SITUATION_SENSITIVITY not in template


# --- and the one pass test that is honest today ----------------------------------


def test_with_no_local_model_nothing_changes(tmp_path):
    """The third of the three pass tests, and the only one that can be written
    without the basis wall coming down.

    The other two -- an unclassified file classified ordinary and then admitted to
    the cloud, and one classified sensitive never being sent -- both need a
    classification record on a `local_model` basis, which `CLASSIFICATION_BASES`
    refuses. They are named gaps, not silent ones, and testing them against a record
    written under a false basis would prove the gate works while lying about who
    concluded it.

    What IS true today and worth holding: with no local model configured, an
    unclassified file is refused a cloud call and permitted a local one, and this
    site changes neither.
    """
    from privacy.denial import unclassified_denies

    assert unclassified_denies(locality="cloud",
                               local_calls_on_unclassified=True) is True
    assert unclassified_denies(locality="local",
                               local_calls_on_unclassified=True) is False


def test_the_question_carries_the_recognisers_own_reason_and_evidence():
    """Nothing here is authored: the reason is the recogniser's word, the ids are the
    library's, and the refs are the observations the candidates rest on."""
    question = question_for(
        _abstention("ambiguous", tied=("academic", "career")),
        file_id="file-1", content_hash="b" * 64,
        matched_terms=(("academic", ("syllabus",)), ("career", ("resume",))),
        evidence_refs=("sha256:" + "c" * 64,))

    assert question.reason == "ambiguous"
    assert question.file_id == "file-1"
    assert question.matched_terms == (
        ("academic", ("syllabus",)), ("career", ("resume",)))
    assert question.evidence_refs == ("sha256:" + "c" * 64,)


# --- over the real detector, on synthetic evidence --------------------------------


def test_the_three_reasons_the_real_detector_produces_all_make_a_question(conn):
    """The shapes come from the real `Abstention`, so a change to its fields fails
    here rather than at the seam. Every reason the owner's corpus produces is
    covered, and each is a question the moment a candidate exists."""
    from recognition.vocabulary import ABSTENTION_REASONS

    for reason in ("no_evidence", "no_corroboration", "ambiguous"):
        assert reason in ABSTENTION_REASONS
        outcome = _abstention(reason, schema_id="academic", tied=("academic",))
        question = question_for(outcome, file_id="f", content_hash="a" * 64)
        assert question.allowed_situations == ("academic", NONE_OF_THESE)
        assert question.reason == reason
