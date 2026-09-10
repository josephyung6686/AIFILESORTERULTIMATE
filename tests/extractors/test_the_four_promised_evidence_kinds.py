"""`104` §18.2 gap 20 -- §2.2's four other structured-string classes exist.

The design sentence, `00`:28: the extractor *"should preserve the title, author,
subject, creator and producer metadata, creation and modification dates, page
count, complete text by page, headings, URLs, email addresses, DOI values,
citations, identifiers, and other structured strings that may later support file
facts."*

What was measured before this patch: `find_structured_strings` produced ONE kind,
`identifier`, from two regexes, so `extractors/reading.ZONE_BY_STRUCTURED_KIND` --
the design's own kind-to-zone table -- was consumed by five extractors and never
handed a kind it maps. A paper's DOI, a syllabus's URL, an instructor's address
and a reference could not be cited by a model or matched by a rule, because no
observation carrying one was ever written.

The shapes are NOT authored here or in `src/`. They are
`planning/deferred-catalogues/06-citation-identifier-patterns.json`, the P5
Deferred column written 2026-08-20, whose `consumer` field names
`find_structured_strings` by name. Every case below is one of that file's own
`example_true` / `example_false` values, and each test says which entry it pins.

Two levels are measured, because the gap has two halves:

  * the KIND, asserted against `find_structured_strings` directly;
  * the ZONE, asserted on an observation that came out of a real extractor --
    because "reaching the store with the zone the design's map gives them" is a
    claim about the extractor, not about the regex.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from extractors.reading import ZONE_BY_STRUCTURED_KIND, Region
from extractors.safety import SafetyPolicy
from extractors.structured_text import TextDocument, extract_structured_text

from cli import find_structured_strings

FIXED_CLOCK = "2026-09-10T00:00:00Z"

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)

HEADING = "Course information"

FILE_ROW = {
    "file_id": "f-syllabus",
    "content_hash":
        "c4b68614329771504e26f782d73842637dfa7ece1ad2bc377faae5c296806a0b",
    "filename": "Syllabus.md",
}


def kinds(text: str) -> list[tuple[str, str]]:
    """Every reading of one text unit, as `(kind, the exact source substring)`.

    RAW-1 makes the substring the offsets name what `raw_value` will be, so
    reading it back out of the text here is the same check P4 performs at write
    time -- a span that drifted would show up as a different string.
    """
    return [(one.kind, text[one.start:one.end])
            for one in find_structured_strings(text)]


def observations_from(text: str) -> list[dict]:
    """One real E3 extraction over a synthetic text unit, through the deployment's
    own finder.

    `tests/p5/test_p5_long_tail.py`'s email case is the template: a fixture
    reader, the real extractor, and the stored observation read back. What is
    different here is that the finder is `cli.find_structured_strings` itself
    rather than a stub, because the thing under test IS what the deployment
    produces.
    """
    body = HEADING + "\n" + text
    document = TextDocument(
        text=body, language="Markdown",
        headings=(Region(zone="heading", start=0, end=len(HEADING), ordinal=1,
                         label=HEADING),),
        markers=())
    result = extract_structured_text(
        file_row=FILE_ROW, path=Path("/corpus/Syllabus.md"), policy=OPEN_POLICY,
        source_type="text_document", read_text_document=lambda path: document,
        find_structured_strings=find_structured_strings, now=FIXED_CLOCK,
        context_window=20)
    return list(result.observations)


def zone_of(text: str, raw: str) -> str:
    """The P4 zone the stored observation for `raw` carries."""
    matching = [o for o in observations_from(text) if o["raw_value"] == raw]
    assert len(matching) == 1, f"{raw!r} produced {len(matching)} observations"
    return matching[0]["location"]["zone"]


# --------------------------------------------------------------------------- #
# The four kinds, one test each: the kind, and the zone the design's map gives it
# --------------------------------------------------------------------------- #

def test_a_doi_is_read_as_a_doi_in_the_link_zone():
    """Catalogue entry `cid-doi`; `00`:28 "DOI values".

    Measured: Crossref's own `example_true` is read with `kind="doi"` and the
    span is the registered prefix form -- `10.` plus the registrant's digits,
    then the suffix. The stored observation carries `link`, which is the zone
    `ZONE_BY_STRUCTURED_KIND` gives the kind and not a zone this test chose:
    P4's table says "`link` - a URL, email address, DOI or hyperlink".
    """
    text = "Published as 10.1038/s41586-021-03819-2 in Nature."
    assert kinds(text) == [("doi", "10.1038/s41586-021-03819-2")]
    assert zone_of(text, "10.1038/s41586-021-03819-2") == "link"
    assert ZONE_BY_STRUCTURED_KIND["doi"] == "link"


def test_a_url_is_read_as_a_url_in_the_link_zone():
    """Catalogue entry `cid-url-http`; `00`:28 "URLs". Scheme and host.

    Measured: the catalogue's `example_true` reads with `kind="url"` and lands
    in `link`. `104` §18.2 gap 20 names the shape as "its scheme and host", and
    that is what the pattern requires -- the catalogue's schemeless `www.` row is
    deliberately not shipped, so a bare host in prose stays invisible.
    """
    text = "Deadlines: https://admissions.uchicago.edu/apply/deadlines"
    assert kinds(text) == [
        ("url", "https://admissions.uchicago.edu/apply/deadlines")]
    assert zone_of(text, "https://admissions.uchicago.edu/apply/deadlines") == "link"
    assert ZONE_BY_STRUCTURED_KIND["url"] == "link"


def test_a_shouted_scheme_is_still_a_url():
    """The `cid-url-http` row's `case_sensitive: false`, which is RFC 3986 §3.1.

    A scheme is case-insensitive by the standard, and documents really do print
    one in capitals -- a heading, a slide, a scanned letterhead. Measured on both
    the shouted and the title-cased form, because a pattern that read only
    `https://` would drop the URL out of exactly the zones §2.2 weighs highest.
    """
    assert kinds("See HTTPS://EXAMPLE.EDU/APPLY") == [
        ("url", "HTTPS://EXAMPLE.EDU/APPLY")]
    assert kinds("See Https://example.edu/apply") == [
        ("url", "Https://example.edu/apply")]


def test_an_email_address_is_read_as_an_email_in_the_link_zone():
    """Catalogue entry `cid-email`; `00`:28 "email addresses".

    Measured: the local-part-at-domain form reads with `kind="email"` and lands
    in `link`.
    """
    text = "Office hours by appointment: j.chen@uchicago.edu"
    assert kinds(text) == [("email", "j.chen@uchicago.edu")]
    assert zone_of(text, "j.chen@uchicago.edu") == "link"
    assert ZONE_BY_STRUCTURED_KIND["email"] == "link"


def test_a_citation_marker_is_read_as_a_citation_in_the_reference_list_zone():
    """Catalogue entries `cid-citation-numeric` and `cid-citation-authoryear`;
    `00`:28 "citations".

    Measured: both of §2.2's in-text marker forms read with `kind="citation"`
    and land in `reference_list` -- the zone P4's table describes as "a citation
    / reference list", citing `00`:28's own "a reference list on page eighteen".

    The zone is the kind's and not the position's, which the catalogue flags in
    its own `unc-citation-zone-mapping` row: a marker in a page-one introduction
    still carries `reference_list`. That is P4's mapping and this test pins it as
    it is rather than working around it.
    """
    numeric = "as shown previously [12, 15-17]"
    assert kinds(numeric) == [("citation", "[12, 15-17]")]
    assert zone_of(numeric, "[12, 15-17]") == "reference_list"

    author_year = "prior work (Okonkwo et al., 2021) suggests otherwise"
    assert kinds(author_year) == [("citation", "(Okonkwo et al., 2021)")]
    assert zone_of(author_year, "(Okonkwo et al., 2021)") == "reference_list"

    assert ZONE_BY_STRUCTURED_KIND["citation"] == "reference_list"


# --------------------------------------------------------------------------- #
# A citation the design does not count is not produced
# --------------------------------------------------------------------------- #

def test_a_citation_the_design_does_not_count_is_not_produced():
    """The catalogue's Coverage note, and its `unc-full-references` row.

    *"It stops short of parsing full bibliographic citations: an APA, MLA,
    Chicago or IEEE reference is not a regular language, and a regex that tried
    would produce mostly-wrong spans that P4 RAW-1 would then faithfully
    preserve. What this file does instead is match in-text citation markers --
    the bracketed and parenthetical forms -- which are regular."*

    A full reference is `unc-full-references`, which sits in the catalogue's
    **Uncertain -- needs Joseph** table with three options laid out and none
    chosen. So it is not a citation this product counts, and the measurement is
    that the reference line below yields no `citation` reading at all.

    The two narrower negatives are the catalogue's own `example_false` values:
    `see Appendix [A]` (a bracket with no digits is not a numeric marker) and
    `(Chicago, 2021 edition)` (a parenthesis that keeps talking after the year is
    not an author-year marker -- which is what keeps a place name and a date from
    becoming a reference).
    """
    reference = ("Okonkwo, A., & Chen, J. (2021). Reading rooms and their "
                 "readers. Journal of Library Science, 44(2), 113-140.")
    assert [kind for kind, _raw in kinds(reference) if kind == "citation"] == []

    assert kinds("see Appendix [A]") == []
    assert kinds("the meeting (Chicago, 2021 edition)") == []


def test_a_dose_and_a_retina_asset_are_not_a_doi_and_not_an_email():
    """The catalogue's `example_false` for `cid-doi` and `cid-email`.

    `10.5 mg twice daily` has no registered-prefix form -- a DOI's prefix is four
    to nine digits after `10.` and then a `/` -- so no DOI is read out of a
    dose. `logo@2x.png` is the standard retina asset convention and is the guard
    `cid-email` carries in its own pattern: without it, a design or app archive
    would manufacture a PII finding out of a filename.
    """
    assert kinds("Take 10.5 mg twice daily") == []
    assert kinds("the file logo@2x.png is an asset") == []


# --------------------------------------------------------------------------- #
# The identifier kind stays, and stays exactly as it was
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("text, expected", [
    ("PHYS 1401 Fall 2023", [("identifier", "PHYS 1401"),
                             ("identifier", "Fall 2023")]),
    ("AY 2024-25", [("identifier", "AY 2024-25")]),
    ("Homework PHYS1401 and COMS W3134", [("identifier", "PHYS1401"),
                                          ("identifier", "COMS W3134")]),
])
def test_the_identifier_kind_stays(text, expected):
    """`104` §18.2 gap 20: "The `identifier` kind stays."

    Measured: the three readings `find_structured_strings`' own docstring records
    as the ones its ordering exists to protect are unchanged. `PHYS 1401 Fall
    2023` still yields exactly two, and `AY 2024-25` still yields the one term
    rather than `65` §2.1's recorded `AY 2024`.
    """
    assert kinds(text) == expected


def test_a_course_code_inside_a_url_is_still_read_as_an_identifier():
    """The regression the two-span-set design exists to prevent.

    One shared span set with the URL pattern ahead of `_STRUCTURED` would make
    the URL claim these characters and the course code inside it would stop being
    read -- a lost anchor on the one reading this product's placement turns on
    (`104` R-146 is the row about that class of loss).

    Measured: the same characters yield TWO readings of two kinds. That is not a
    contradiction; they are two true statements in two zones answering two
    different questions, and P6 reads them through different slots.
    """
    text = "Submit at https://courseworks.columbia.edu/PHYS1401/assignments"
    assert kinds(text) == [
        ("url", "https://courseworks.columbia.edu/PHYS1401/assignments"),
        ("identifier", "PHYS1401"),
    ]


# --------------------------------------------------------------------------- #
# The catalogue's settled trailing-punctuation rule
# --------------------------------------------------------------------------- #

def test_a_doi_at_the_end_of_a_sentence_does_not_absorb_the_full_stop():
    """The `cid-doi` row's settled trim, and RAW-1 is why it matters.

    *"A DOI at the end of a sentence absorbs the full stop, because `.` is legal
    in a DOI suffix; the finder must trim a single trailing `.`, `,`, `;` or `)`
    that has no opening mate, and that trim adjusts the offsets so RAW-1 still
    holds."*

    The span IS `raw_value`, so an untrimmed span stores a broken DOI verbatim
    and calls it the document's own words. Measured on both a DOI and a URL.
    """
    assert kinds("See 10.1038/s41586-021-03819-2.") == [
        ("doi", "10.1038/s41586-021-03819-2")]
    assert kinds("See https://example.edu/apply, then wait.") == [
        ("url", "https://example.edu/apply")]


def test_a_balanced_parenthesis_inside_a_doi_suffix_is_kept():
    """The other half of the same rule: "that has no opening mate".

    Crossref's own documented example is an early Wiley DOI whose suffix carries
    balanced parentheses. Trimming the closing one would break the identifier,
    so the trim counts mates inside the span rather than looking at the last
    character alone.
    """
    text = "cited as 10.1002/(SICI)1097-0258 here"
    assert kinds(text) == [("doi", "10.1002/(SICI)1097-0258")]


# --------------------------------------------------------------------------- #
# The map is live
# --------------------------------------------------------------------------- #

def test_every_kind_the_design_maps_is_now_produced():
    """`104` §18.2 gap 20: "the kind-to-zone map ... is dead."

    Measured as a closed sum rather than four separate observations: every key of
    `ZONE_BY_STRUCTURED_KIND` is a kind this deployment now emits, and no kind it
    emits is outside that map plus `identifier` (which the map deliberately omits
    so that a found string keeps the zone of the region it sits in).
    """
    text = ("Read https://example.edu/course, cite 10.1038/s41586-021-03819-2, "
            "mail j.chen@uchicago.edu, see [12], (Okonkwo et al., 2021), "
            "for PHYS 1401.")
    produced = {kind for kind, _raw in kinds(text)}
    assert set(ZONE_BY_STRUCTURED_KIND) <= produced
    assert produced - set(ZONE_BY_STRUCTURED_KIND) == {"identifier"}
