# tests/p5/test_p5_pdf.py
"""E1 - §2.2. Done-means 4: "PDF is complete, not previewed, and location survives:
the page-1 and page-18 occurrences of one string are two distinguishable
observations.\""""
from pathlib import Path

import pytest

from extractors.pdf import EXTRACTOR_NAME, PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region, StructuredString
from extractors.safety import ProtectedContainerRefused, SafetyPolicy

from conftest import FIXED_CLOCK
from p4_stub import locator_for

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)

FILE_ROW = {"file_id": "f1", "content_hash": "sha256:abc",
            "filename": "syllabus-busib4300.pdf"}

PAGE_1 = ("BUSIB 4300 Course Information\n"
          "Syllabus — Spring 2026. Contact prof@wustl.edu.")
PAGE_18 = ("References\n"
           "Ng, A. (2024). BUSIB 4300 readings. doi:10.1000/xyz. "
           "See also BUSIB 4300 supplement.")


def a_syllabus() -> PdfDocument:
    """The SPEC's `syllabus-busib4300.pdf`: the course code in the title and in a
    page-18 reference list."""
    return PdfDocument(
        metadata={"Title": "BUSIB 4300 Syllabus", "Author": "J. Yung",
                  "Producer": "python-docx", "CreationDate": "D:20260717140322Z"},
        iso_dates={"CreationDate": "2026-07-17T14:03:22+00:00"},
        pages=(
            PdfPage(number=1, text=PAGE_1,
                    regions=(Region(zone="heading", start=0, end=29, ordinal=1,
                                    label="Course Information"),
                             Region(zone="body", start=30, end=len(PAGE_1)))),
            PdfPage(number=18, text=PAGE_18,
                    regions=(Region(zone="heading", start=0, end=10, ordinal=1,
                                    label="References"),
                             Region(zone="reference_list", start=11,
                                    end=len(PAGE_18)))),
        ),
    )


def find_the_course_code(text: str):
    """The fixture finder. §2.2's pattern sets are DEFERRED (SPEC Deferred: "Citation
    and identifier pattern sets ... The patterns"), so no pattern lives in
    src/extractors/ and the test supplies this one."""
    found = []
    start = text.find("BUSIB 4300")
    while start != -1:
        found.append(StructuredString(kind="identifier", start=start,
                                      end=start + len("BUSIB 4300")))
        start = text.find("BUSIB 4300", start + 1)
    for token, kind in (("prof@wustl.edu", "email"), ("doi:10.1000/xyz", "doi")):
        at = text.find(token)
        if at != -1:
            found.append(StructuredString(kind=kind, start=at, end=at + len(token)))
    return tuple(sorted(found, key=lambda s: s.start))


def run_it(document=None, finder=find_the_course_code, **kwargs):
    return extract_pdf(file_row=FILE_ROW, path=Path("/corpus/syllabus.pdf"),
                       policy=OPEN_POLICY, read_pdf=lambda path: document or a_syllabus(),
                       find_structured_strings=finder, now=FIXED_CLOCK,
                       context_window=40, **kwargs)


def test_every_observation_conforms_to_p4s_shape(sink):
    sink.write(run_it())
    sink.conforms()


def test_the_complete_text_is_stored_by_page(sink):
    # §2.2: "extract the complete document rather than only a first-page preview";
    # G1: page text is a text_units row, not an observation.
    run_id = sink.write(run_it())
    pages = {u["container_path"][0]["index"]: u["text"]
             for u in sink.units_for(run_id) if len(u["container_path"]) == 1}
    assert pages == {1: PAGE_1, 18: PAGE_18}
    assert not [o for o in sink.observations if o["raw_value"] == PAGE_1]


def test_the_page_count_is_the_runs_coverage(sink):
    run_id = sink.write(run_it())
    assert sink.run_for(run_id)["coverage"] == {"units": "pages", "processed": 2,
                                                "total": 2}


def test_the_course_code_in_the_title_and_in_the_reference_list_are_two_rows(sink):
    # SPEC fixture: "two observations, distinct locations, distinct occurrence counts."
    # §2.2: a code in a title "is more meaningful than the same text appearing once in
    # a reference list on page eighteen."
    sink.write(run_it())
    rows = {o["location"]["zone"]: o for o in sink.observations
            if o["raw_value"] == "BUSIB 4300"}
    assert set(rows) == {"heading", "reference_list"}
    assert locator_for(rows["heading"]["location"]) == "heading:page=1/heading=1#0-10"
    assert rows["heading"]["occurrence_count"] == 1
    assert rows["reference_list"]["location"]["container_path"][0]["index"] == 18
    assert rows["reference_list"]["occurrence_count"] == 2


def test_the_title_slot_is_its_own_zone_and_is_direct(sink):
    # P4's zone table: `title` is "the document title", named at §2.2 and §3.2.
    sink.write(run_it())
    titles = [o for o in sink.observations if o["location"]["zone"] == "title"]
    assert len(titles) == 1
    assert titles[0]["raw_value"] == "BUSIB 4300 Syllabus"
    assert titles[0]["reliability"] == "direct"
    assert locator_for(titles[0]["location"]) == "title:field=Title"


def test_the_producer_is_emitted_verbatim_with_no_marker_of_any_kind(sink):
    # SPEC fixture: "`python-docx-producer.pdf` | §2.2, §8.5 | producer emitted
    # verbatim at `zone = metadata`, `reliability: direct`, NO MARKER OF ANY KIND on
    # the observation; P6 discounts it (M4)."
    from extractors.shape import OBSERVATION_FIELDS
    sink.write(run_it())
    producer = [o for o in sink.observations
                if locator_for(o["location"]) == "metadata:field=Producer"][0]
    assert producer["raw_value"] == "python-docx"
    assert producer["reliability"] == "direct"
    assert tuple(k for k in producer if k != "run_id") == OBSERVATION_FIELDS
    for marker in ("tool_generated", "suppressed", "discount", "trustworthy",
                   "generic", "stale"):
        assert marker not in producer


def test_a_structured_date_slot_is_normalized_to_iso_8601_by_the_reader(sink):
    # P4 D8's fourth transform. The PDF date syntax is a format detail, so the reader
    # renders it and P5 carries it; §3.10 forbids parsing a date out of free text.
    sink.write(run_it())
    created = [o for o in sink.observations
               if locator_for(o["location"]) == "metadata:field=CreationDate"][0]
    assert created["raw_value"] == "D:20260717140322Z"
    assert created["normalized_value"] == "2026-07-17T14:03:22+00:00"


def test_headings_are_observations_and_have_their_own_addressable_unit(sink):
    # §2.2 requires headings; P4's fixture 1 addresses a value INSIDE one, which
    # conformance rule 10 says needs a unit at exactly that container path.
    run_id = sink.write(run_it())
    heading = [o for o in sink.observations
               if o["location"]["zone"] == "heading"
               and o["raw_value"].startswith("BUSIB 4300 Course")][0]
    path = heading["location"]["container_path"]
    assert [s["kind"] for s in path] == ["page", "heading"]
    assert path[1]["label"] == "Course Information"
    unit = [u for u in sink.units_for(run_id) if u["container_path"] == path][0]
    assert unit["text"] == "BUSIB 4300 Course Information"


def test_a_url_email_or_doi_lands_in_the_link_zone(sink):
    # P4's zone table: "`link` - a URL, email address, DOI or hyperlink".
    sink.write(run_it())
    links = {o["raw_value"] for o in sink.observations
             if o["location"]["zone"] == "link"}
    assert links == {"prof@wustl.edu", "doi:10.1000/xyz"}


def test_surrounding_context_is_carried_as_p4s_three_fields(sink):
    # §2.2 requires surrounding context; M5 makes it three fields.
    sink.write(run_it())
    code = [o for o in sink.observations
            if o["raw_value"] == "BUSIB 4300"
            and o["location"]["zone"] == "reference_list"][0]
    assert "BUSIB 4300 readings" not in code["context_before"]
    assert code["context_after"].startswith(" readings")
    assert code["context_truncated"] in (True, False)


def test_raw_survives_exactly_and_normalization_is_mechanical(sink):
    # Done-means 3: "A document saying `U Chicago` keeps that exact wording as the raw
    # value regardless of what any resolver later does with it."
    document = PdfDocument(
        metadata={}, pages=(PdfPage(number=1, text="Applying to U  Chicago this fall.",
                                    regions=(Region(zone="body", start=0, end=33),)),))

    def finder(text):
        at = text.find("U  Chicago")
        return (StructuredString(kind="identifier", start=at, end=at + 10),)

    sink.write(run_it(document, finder))
    row = [o for o in sink.observations if o["raw_value"] == "U  Chicago"][0]
    assert row["raw_value"] == "U  Chicago"
    assert row["normalized_value"] == "U Chicago"     # whitespace collapse only


def test_a_pdf_with_no_structured_strings_is_complete_with_zero_of_them(sink):
    # §2.4's rule, applied here: an empty result is `complete`, never `unsupported`.
    document = PdfDocument(metadata={},
                           pages=(PdfPage(number=1, text="   ",
                                          regions=()),))
    run_id = sink.write(run_it(document, lambda text: ()))
    assert sink.run_for(run_id)["completeness"] == "complete"
    assert sink.observations_for(run_id) == []
    sink.conforms()


def test_the_run_is_native_and_names_the_pdf_extractor(sink):
    run_id = sink.write(run_it())
    row = sink.run_for(run_id)
    assert row["extractor_name"] == EXTRACTOR_NAME == "pdf.text"
    assert row["source_type"] == "text_document"
    assert row["analysis_tier"] == "native"


def test_e1_refuses_a_protected_path_before_it_calls_its_reader():
    calls = []
    policy = SafetyPolicy(is_protected_container=lambda path: True,
                          is_dataless=lambda path: False)
    with pytest.raises(ProtectedContainerRefused):
        extract_pdf(file_row=FILE_ROW,
                    path=Path("/Applications/Thing.app/Resources/help.pdf"),
                    policy=policy,
                    read_pdf=lambda path: calls.append(path) or a_syllabus(),
                    find_structured_strings=find_the_course_code, now=FIXED_CLOCK,
                    context_window=40)
    assert calls == []


def test_there_is_no_language_quality_check_anywhere_in_e1():
    # §2.2: "The system should not use unreliable global language-quality checks that
    # incorrectly punish multilingual or mathematics-heavy documents." Done-means 5.
    import inspect

    import extractors.pdf as module
    names = {name.lower() for name in vars(module)}
    for forbidden in ("language_quality", "gibberish", "readability", "is_garbled",
                      "text_quality", "looks_like_text", "detect_language"):
        assert forbidden not in names
    assert "language" not in inspect.signature(extract_pdf).parameters
