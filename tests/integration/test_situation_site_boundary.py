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
    SituationSiteNotRatified,
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


def test_wall_one_is_a_refusal_that_counts_what_is_waiting():
    """A gap with a number on it. The refusal names all three walls, so a reader who
    opens one finds the other two without going looking."""
    question = question_for(
        _abstention("ambiguous", tied=("academic", "career")),
        file_id="f", content_hash="a" * 64)

    with pytest.raises(SituationSiteNotRatified) as raised:
        build_situation_request([question, question])

    message = str(raised.value)
    assert "2 files" in message
    assert SITUATION_SENSITIVITY in message
    assert "CLASSIFICATION_BASES" in message


def test_wall_two_a_verdict_from_a_model_has_no_lawful_basis():
    """MEASURED, not read. This is why no record is written: writing one as
    `detector` would claim a deterministic rule concluded it, which is the untruth
    `96` §19 caught when `detector_no_safety_evidence` was read as "I checked and it
    is fine"."""
    from privacy.classification import ClassificationRecord
    from privacy.vocabulary import CLASSIFICATION_BASES

    assert "local_model" not in CLASSIFICATION_BASES
    assert len(CLASSIFICATION_BASES) == 4
    with pytest.raises(Exception) as raised:
        ClassificationRecord(
            file_id="f", content_hash="a" * 64,
            handling_class="personal_non_sensitive", protected=False,
            basis="local_model", evidence_refs=("sha256:" + "a" * 64,),
            reliability_state="llm_supported",
            observed_at="2026-09-06T00:00:00+00:00")
    assert "local_model" in str(raised.value)


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
