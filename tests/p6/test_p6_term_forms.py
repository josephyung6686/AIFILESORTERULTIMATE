# tests/p6/test_p6_term_forms.py
"""The term vocabulary the owner ruled on, as the SHIPPED command carries it.

`105` §13.2 put a closed vocabulary of term forms to the owner and §14.2 ruled on it
on 7 Sep 2026: *"Keep the proposed accepted forms and refusals, preserve the
distinction between academic-year and individual-term granularity, and infer no
equivalence between numbered terms, semesters, or seasons without evidence for that
course's calendar."*

**The measurement underneath it is `104` R-101.** On the owner's own corpus, local
model, 114 `term` answers were refused `VALUE_NOT_NORMALIZABLE`, and the refused
shapes were countable: `2023-2024 Term 1` fifteen times, `2023-2024` thirteen,
`S2026` five, and a tail of bare years. The first is a real calendar this product
could not read -- a two-term academic year written the way the university writes it
-- and a person on that calendar got no `Semester` folder at all. The others are
right to refuse and were refused with nothing to say which.

So this file holds two halves of one ruling:

* **five accepted forms, five dedicated pattern ids.** §3.10 requires "dedicated
  patterns rather than generic parsing" and the id is how a test asserts dedication
  rather than coincidence. `facts.dates` authors the ids; `cli` authors the
  expressions and the canonical forms; neither authors the other's half.
* **three refused shapes, each with a name.** They were already refused by matching
  nothing, which is why R-101 could count them but not sort them. `cli.term_refusal`
  is what says WHICH, and the name reaches this deployment and its tests -- not the
  P8 verdict, whose `reasons` are a closed vocabulary this ruling did not open.

And the amendment that is not about spelling at all: GRANULARITY IS IDENTITY.
`AY 2024-25` is not a semester, `2023-2024 Semester 1` is not `Fall 2023`, and
`Term 1` is not `Semester 1`. Identity in this product is the `value_id`, which is
content-addressed over (field, canonical value), so the assertions below are made
against real rows rather than against the strings that produce them.
"""
from __future__ import annotations

import pytest

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation

from facts.dates import (
    ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR, REQUIRED_PATTERN_IDS, SEASON_YEAR,
    YEAR_RANGE_SEMESTER_NUMBER, YEAR_RANGE_TERM_NUMBER, date_matches,
)
from facts.values import VALUE_ORIGINS, ensure_value

import cli

CLOCK = "2026-09-07T00:00:00Z"
EVIDENCE = "sha256:" + "0" * 64


def _observation(text: str) -> Observation:
    """One P4 reading carrying `text`, so the patterns are asked the way the
    producer asks them -- over an observation, not over a bare string."""
    return Observation(
        file_id="file-1", content_hash="a" * 64, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=text,
        location=Location("body", (Segment("page", 1),)), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id="run-1")


#: §13.2's accepted forms, as the ruling lists them, plus §14.2's two additions.
#: Each row is (what a document printed, which pattern must claim it, what identity
#: it becomes). The three spellings of a season and a year are `00`:78's own worked
#: folder `2026-Spring` and the two ways the same semester is otherwise written.
ACCEPTED = [
    ("Spring 2026", SEASON_YEAR, "Spring2026"),
    ("Spring2026", SEASON_YEAR, "Spring2026"),
    ("2026-Spring", SEASON_YEAR, "Spring2026"),
    ("AY 2024-25", ACADEMIC_YEAR_RANGE, "AY2024-25"),
    ("Michaelmas Term 2024", NAMED_TERM_YEAR, "Michaelmas2024"),
    ("2023-2024 Term 1", YEAR_RANGE_TERM_NUMBER, "2023-2024Term1"),
    ("2023-2024 Semester 1", YEAR_RANGE_SEMESTER_NUMBER, "2023-2024Semester1"),
]


# --- the accepted forms: one dedicated pattern each, spelling kept ------------

@pytest.mark.parametrize("printed,pattern_id,identity", ACCEPTED)
def test_each_accepted_form_is_claimed_by_its_own_pattern_and_keeps_its_spelling(
        printed, pattern_id, identity):
    """One span, one pattern id, and the wording the document used still on the
    match.

    `DateMatch` carries `pattern_id`, `raw` and `value` precisely so this can be
    asserted separately: that a dedicated pattern claimed the span (§3.10), that the
    identity is the canonical one, and that §14.2's "the original spelling is
    preserved alongside the normalized identity" is true at the point the value is
    made rather than recovered later from the text.
    """
    matches = date_matches(_observation(f"Coursework {printed} handout"),
                           patterns=cli.DATE_PATTERNS)

    assert len(matches) == 1, [one.pattern_id for one in matches]
    assert matches[0].pattern_id == pattern_id
    assert matches[0].raw == printed
    assert matches[0].value == identity


@pytest.mark.parametrize("printed,pattern_id,identity", ACCEPTED)
def test_a_model_proposing_an_accepted_form_gets_the_same_identity(
        printed, pattern_id, identity):
    """Check 3 and the deterministic path agree, which is `normalize_for_model`'s
    whole promise: "the model's value is canonicalised by the SAME rule the
    deterministic path uses". Without it a model's `2023-2024 Term 1` would be stored
    beside the producer's `2023-2024Term1` -- `65` §4.2's several-spellings failure,
    re-created across the seam instead of inside one stage."""
    assert cli.normalize_for_model(cli.TERM_FIELD, printed) == identity


def test_the_ruled_forms_are_written_in_the_documents_own_separators():
    """A university writes its calendar with the separators it likes, and the
    ruling is about the FORM, not about one printing of it. `2023/2024`, an
    underscore, a lower-case word and a space before the number are the same term.
    The number is read through the term word and not off the end of a year:
    `[0-9](?![0-9])` reads `2023-2024 Term 1` as `Term 3`, because `2023` ends in a
    lone `3`."""
    for printed in ("2023-2024 Term 1", "2023/2024 Term 1", "2023-2024_TERM_1",
                    "2023 - 2024 term-1"):
        assert cli.normalize_for_model(cli.TERM_FIELD, printed) == "2023-2024Term1"


# --- the refused shapes, each with a name ------------------------------------

@pytest.mark.parametrize("printed,named", [
    ("2019", cli.TERM_REFUSAL_BARE_YEAR),
    ("2026", cli.TERM_REFUSAL_BARE_YEAR),
    ("2023-2024", cli.TERM_REFUSAL_BARE_RANGE),
    ("2023/2024", cli.TERM_REFUSAL_BARE_RANGE),
    ("2024-25", cli.TERM_REFUSAL_BARE_RANGE),
    ("S2026", cli.TERM_REFUSAL_SEASON_INITIAL),
    ("S 2026", cli.TERM_REFUSAL_SEASON_INITIAL),
    ("F2026", cli.TERM_REFUSAL_SEASON_INITIAL),
])
def test_each_refused_shape_is_refused_and_the_refusal_says_which(printed, named):
    """§13.2 asks for the three refusals "stated so the validator's reason names
    them", and §14.2 keeps them.

    THE OUTCOME ON THE WIRE IS UNCHANGED and that is deliberate: `P8Verdict.reasons`
    is checked against `llm_harness.vocabulary`'s closed `ALL_REASON_CODES`, so the
    refusal is still `VALUE_NOT_NORMALIZABLE`. What did not exist before is a way to
    tell R-101's 114 refusals apart, and `term_refusal` is it.
    """
    assert cli.term_refusal(printed) == named
    assert cli.normalize_for_model(cli.TERM_FIELD, printed) is None


def test_a_course_number_is_not_named_a_refused_year():
    """`_YEAR` and not `[0-9]{4}`, for the reason `_YEAR` exists at all: `4300` is
    the course number in `BUSIB 4300 Spring 2026`, and it was never a term
    candidate. Naming it a refused bare year would put the wrong defect in front of
    whoever reads the refusals."""
    for printed in ("4300", "1401", "2801"):
        assert cli.term_refusal(printed) is None
        assert cli.normalize_for_model(cli.TERM_FIELD, printed) is None


def test_no_accepted_form_is_caught_by_a_refusal():
    """The refusals run BEFORE the pattern loop, so an accepted form that also
    matched one of them would be refused by ordering alone. None does, and this is
    what says so rather than the ordering comment at the call site."""
    for printed, _, identity in ACCEPTED:
        assert cli.term_refusal(printed) is None
        assert cli.normalize_for_model(cli.TERM_FIELD, printed) == identity


# --- §14.2's amendment: granularity is part of identity ----------------------

def _identity(conn, printed: str) -> str:
    """The `value_id` this term would be stored under -- which is what identity
    MEANS here. `ensure_value` content-addresses over (field, canonical value), so
    two forms are one value exactly when this string repeats."""
    canonical = cli.normalize_for_model(cli.TERM_FIELD, printed)
    assert canonical is not None, printed
    return ensure_value(conn, field_key=cli.TERM_FIELD, canonical_value=canonical,
                        first_evidence_ref=EVIDENCE, origin=VALUE_ORIGINS[0])


def test_an_academic_year_is_never_the_same_value_as_a_term(p6_conn):
    """§14.2: "`AY 2024-25` does not identify a semester."

    An academic year names TWO semesters and a term names one, so a product that
    treated them as one value would put a year's worth of work into a folder called
    after one semester -- or, filing the other way, split one semester's files
    between `Fall2024` and `AY2024-25` and show the person two folders for material
    they think of as one.
    """
    assert _identity(p6_conn, "AY 2024-25") != _identity(p6_conn, "Fall 2024")
    assert _identity(p6_conn, "AY 2024-25") != _identity(p6_conn, "Spring 2025")


def test_a_numbered_semester_is_never_the_same_value_as_a_season(p6_conn):
    """§14.2: "`2023-2024 Semester 1` does not establish `Fall 2023`."

    It is the obvious-looking inference and it is wrong for a real reason: a
    two-term year's first semester is autumn in the northern hemisphere, and is not
    in the southern one, and plenty of calendars start their first semester in
    January. The ruling forbids inferring it "without evidence for that course's
    calendar", and this product has no such evidence.
    """
    assert (_identity(p6_conn, "2023-2024 Semester 1")
            != _identity(p6_conn, "Fall 2023"))


def test_a_numbered_term_is_never_the_same_value_as_a_numbered_semester(p6_conn):
    """§14.2: "`Term 1` and `Semester 1` are not automatically one value."

    This is what makes the word part of the canonical form rather than a noise word
    dropped like the `Term` in `Michaelmas Term 2024`. A university on three terms
    and one on two semesters both write `1`, and the ordinal alone would merge two
    calendars into one folder.
    """
    assert (_identity(p6_conn, "2023-2024 Term 1")
            != _identity(p6_conn, "2023-2024 Semester 1"))


def test_the_ruled_forms_are_four_identities_and_not_one(p6_conn):
    """The whole collision matrix in one place, because the three tests above each
    check one edge and a canonicaliser can fail on a pair none of them names."""
    printed = ("2023-2024 Term 1", "2023-2024 Semester 1", "Fall 2023",
               "AY 2023-24")

    assert len({_identity(p6_conn, one) for one in printed}) == len(printed)


def test_two_numbered_terms_of_one_year_stay_two(p6_conn):
    """The negative twin of the whole ruling: keeping granularity must not collapse
    into keeping only the year. A canonicaliser that dropped the number would file
    a whole year's work into one folder, which is the failure `AY 2024-25` and
    `AY 2025-26` are already guarded against one pattern over."""
    assert (_identity(p6_conn, "2023-2024 Term 1")
            != _identity(p6_conn, "2023-2024 Term 2"))


# --- the catalogue: five ids, and which three the SPEC required --------------

def test_the_deployment_ships_all_five_ruled_patterns():
    """§3.10 requires three; `105` §14.2 adds two. `DatePatterns` enforces the
    three by refusing a catalogue without them, and nothing enforces the two --
    they are a deployment's ruled vocabulary and a test fixture that omits them is
    testing something else. This assertion is what holds THIS deployment to them."""
    assert cli.DATE_PATTERNS.pattern_ids == (
        SEASON_YEAR, ACADEMIC_YEAR_RANGE, NAMED_TERM_YEAR,
        YEAR_RANGE_TERM_NUMBER, YEAR_RANGE_SEMESTER_NUMBER)
    assert YEAR_RANGE_TERM_NUMBER not in REQUIRED_PATTERN_IDS
    assert YEAR_RANGE_SEMESTER_NUMBER not in REQUIRED_PATTERN_IDS


def test_the_ruled_forms_are_read_as_terms_and_not_as_course_codes():
    """`_TERM` is the one definition of a term this file authors and THREE things
    read it: `find_structured_strings` claims its spans first so `SPRING2026` cannot
    become a course code, `_is_term` keeps the `subject` slot off a term, and
    `_SUBJECT_IDENTIFIER`'s lookahead refuses one as an identifier. Adding two forms
    to `DATE_PATTERNS` and not to `_TERM` would leave the new spellings readable as
    terms and still claimable as something else."""
    for printed in ("2023-2024 Term 1", "2023-2024 Semester 1"):
        assert cli._is_term(printed)
        assert cli.normalize_for_model(cli.SUBJECT_FIELD, printed) is None


def test_a_numbered_term_beside_a_course_code_leaves_the_code_alone():
    """The span the term claims is the term's, and what is left is still the
    course. `find_structured_strings` runs `_TERM` first and takes its spans, so a
    filename carrying both must yield two readings and not one swallowing the
    other."""
    found = cli.find_structured_strings("2023-2024 Semester 1 PHYS2801 Syllabus")
    text = "2023-2024 Semester 1 PHYS2801 Syllabus"

    assert [text[one.start:one.end] for one in found] == [
        "2023-2024 Semester 1", "PHYS2801"]
