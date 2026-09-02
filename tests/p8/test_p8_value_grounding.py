# tests/p8/test_p8_value_grounding.py
"""The comparison itself, before any verdict depends on it.

`llm_harness.value_grounding` is one text comparison and this file is the whole of
what it promises. It is separated from `test_p8_glossary_as_value_source.py` on
purpose: that file measures what the DISPATCHER does with a lifted value, and this
one measures the rule, in both directions, so that a change to the rule shows up as
a named failure rather than as a stress case quietly changing colour.

Every false-reject class the rule has is asserted here as a failure, not omitted.
A guard whose limits are not written down is a guard nobody can reason about.
"""
from __future__ import annotations

import pytest

from llm_harness.records import Citation, ReleasedEvidence
from llm_harness.value_grounding import (
    cited_released_values,
    grounding_tokens,
    occurs_in,
    value_is_grounded,
)


# --- the fold ---------------------------------------------------------------------


def test_tokens_are_alphanumeric_runs_casefolded():
    assert grounding_tokens("PHYS 1401 Problem Set 4") == (
        "phys", "1401", "problem", "set", "4")
    assert grounding_tokens("AY2024-25") == ("ay2024", "25")
    assert grounding_tokens("Prepared by the office.") == (
        "prepared", "by", "the", "office")


def test_text_with_no_alphanumeric_character_has_no_tokens():
    """Nothing to compare is not the same as comparing equal."""
    assert grounding_tokens("") == ()
    assert grounding_tokens("--- / ---") == ()
    assert grounding_tokens(None) == ()
    assert grounding_tokens(2026) == ()


# --- the rule, in both directions -------------------------------------------------


@pytest.mark.parametrize(("value", "text"), [
    # The separator variance `cli.normalize_for_model` exists for, both ways round.
    ("PHYS 1401", "PHYS1401 Problem Set 4"),
    ("PHYS1401", "The course PHYS 1401 meets on Tuesdays"),
    ("PHYS-1401", "PHYS1401 Problem Set 4"),
    ("AY 2024-25", "Fees for AY2024-25 are due"),
    ("AY2024-25", "Fees for AY 2024-25 are due"),
    # Case, and punctuation hard against the value.
    ("dr smith", "Taught by Dr Smith."),
    ("Dr Smith", "taught by dr smith"),
    ("committee", "Prepared for the committee in the autumn, with notes."),
    # A multi-word value spanning a run of tokens.
    ("Shipping Line", "Carried by Ocean Shipping Line Ltd"),
    # The whole released line, which is S1: over-quotation is grounded and stays a
    # question for the prompt, not for this rule.
    ("PHYS1401 Problem Set 4", "PHYS1401 Problem Set 4"),
])
def test_a_value_whose_characters_are_in_the_text_is_grounded(value, text):
    assert occurs_in(value, text) is True


@pytest.mark.parametrize(("value", "text"), [
    # The reason this is a token RUN and not a substring. Every one of these is a
    # glossary-enumerated word sitting inside a longer word, and a folded-substring
    # test accepts all four.
    ("form", "Filed under the information the office prepared"),
    ("field", "Recorded across three fields of the return"),
    ("scan", "The scanner was serviced in the autumn"),
    ("store", "Restored from the archive"),
    # A run must be contiguous: these tokens are all present and out of order.
    ("office autumn", "Prepared by the office in the autumn"),
    # A run must start on a token boundary.
    ("1401", "PHYS1401 Problem Set 4"),
    # Nothing to compare.
    ("", "Prepared by the office"),
    ("---", "Prepared by the office"),
    ("office", ""),
])
def test_a_value_whose_characters_are_not_a_token_run_is_not_grounded(value, text):
    assert occurs_in(value, text) is False


def test_a_run_must_end_on_a_token_boundary():
    """`phys140` is a prefix of a token and is not a reading of the text.

    Prefix matching is the tempting loosening -- it would let `scan` match
    `scanned` -- and it is refused, because it would equally let `photo` match
    `photocopy` and `form` match `formal`. See the false-reject test below, which
    records what that refusal costs.
    """
    assert occurs_in("PHYS 140", "PHYS1401 Problem Set 4") is False


@pytest.mark.parametrize(("value", "text"), [
    # Morphology. The rule compares characters and knows no grammar.
    ("screenshot", "Saved as screenshots on the phone"),
    ("photo", "Two photographs of the meter"),
    # A canonical form whose characters are not the ones on the page. The wired
    # check tries the RAW value too, which is what makes this survivable in
    # practice; the rule on its own does not.
    ("2024-09-15", "Dated 15 September 2024"),
    # A script with no separator to split on: the whole run is one token.
    ("報告", "これは報告書です"),
])
def test_the_false_rejects_this_rule_has_are_written_down(value, text):
    """These are correct readings that the rule refuses. Recorded, not hidden.

    A guard that claimed no false rejects would be claiming something nobody
    measured. Each of these is a value a person would call right and the rule calls
    ungrounded, and each is here so that a later loosening has to argue with a named
    case rather than with a feeling.
    """
    assert occurs_in(value, text) is False


# --- the bound: the items the claim cites, and only those -------------------------


def _cite(ref: str) -> Citation:
    return Citation(evidence_ref=ref, cited_span="the office",
                    metadata_field_name=None, why_it_supports="it says so")


def _released(key: str, value: str) -> ReleasedEvidence:
    return ReleasedEvidence(
        observation_key=key, address="heading#0-10", value=value, zone="body")


RELEASED = (
    _released("obs-cited", "Prepared by the office in the autumn."),
    _released("obs-uncited", "Saved as a screenshot on the phone."),
)


def test_only_the_cited_items_released_text_is_compared_against():
    """A value grounded in an item the model did not cite is not grounded.

    The citation is the only place a model says where a value came from. Comparing
    against the whole dossier would accept a claim that pointed at one line and read
    its value off another, which is the thing the check is for.
    """
    assert cited_released_values((_cite("obs-cited"),), RELEASED) == (
        "Prepared by the office in the autumn.",)
    assert value_is_grounded(
        "screenshot", "screenshot",
        citations=(_cite("obs-cited"),), released_evidence=RELEASED) is False
    assert value_is_grounded(
        "screenshot", "screenshot",
        citations=(_cite("obs-uncited"),), released_evidence=RELEASED) is True


def test_a_claim_citing_nothing_released_is_not_grounded():
    """Absent means refuse. There is no released text, so there is no comparison."""
    assert value_is_grounded(
        "the office", "the office",
        citations=(), released_evidence=RELEASED) is False
    assert value_is_grounded(
        "the office", "the office",
        citations=(_cite("obs-absent"),), released_evidence=RELEASED) is False
    assert value_is_grounded(
        "the office", "the office",
        citations=(_cite("obs-cited"),), released_evidence=()) is False


def test_either_spelling_grounds_the_value():
    """Raw or normalized. Neither alone is enough and the reason differs.

    `Spring 2026` is what a model reads off the page and `Spring2026` is what this
    deployment stores; a rule that demanded the canonical form would reject the
    reading, and one that demanded the raw form would reject a model that proposed
    the canonical spelling directly.
    """
    released = (_released("obs-1", "PHYS 1401 Problem Set 4"),)
    cite = (Citation(evidence_ref="obs-1", cited_span="PHYS 1401",
                     metadata_field_name=None, why_it_supports="the heading"),)
    assert value_is_grounded(
        "PHYS 1401", "PHYS1401",
        citations=cite, released_evidence=released) is True
    assert value_is_grounded(
        "Spring 2026", "Spring2026",
        citations=cite, released_evidence=released) is False


def test_a_non_string_value_is_not_grounded():
    """`2026` as a JSON number reaches check 3 first, and this refuses it too."""
    released = (_released("obs-1", "Dated 2026"),)
    cite = (Citation(evidence_ref="obs-1", cited_span="Dated",
                     metadata_field_name=None, why_it_supports="the heading"),)
    assert value_is_grounded(
        2026, None, citations=cite, released_evidence=released) is False
    assert value_is_grounded(
        "2026", "2026", citations=cite, released_evidence=released) is True
