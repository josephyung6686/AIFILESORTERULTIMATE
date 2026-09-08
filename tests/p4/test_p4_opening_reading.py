# tests/p4/test_p4_opening_reading.py
"""`104` R-164 -- the OPENING of a text unit, as a reading with a span of its own.

`104` §16 traced why a cloud dossier carries no words of the document it is about.
Every text extractor writes one span-less `body` observation over each page or
paragraph, and `model_facts.may_be_released` refuses "a span-less observation whose
value is at least as long as the unit standing at its own path" -- the rule that
stops SF-1's whole DOCX body (45,843 bytes, span-less) from travelling. A PDF page
arrives in exactly that shape, so the rule refuses every page of every PDF, and the
model is shown `extension`, `mime_type`, `Producer` and a heading fragment.

`00`:186 says what to send instead: "selected excerpts ... It should not send full
documents where a short heading or OCR excerpt is enough to resolve the question."
This is the cut that makes one. It is HERE, beside `line_reading_for`, for the same
reason that one is: `tests/p7/test_p7_no_invention.py`'s L2 guard names the three
top-level packages that may bind a P4 text materialiser and `model_facts` is not one
of them, so the read happens where the text already lives and the caller receives a
RECORD it may then decide to store.
"""
from __future__ import annotations

from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    opening_reading_for, record_run, record_text_unit, unit_for_observation,
)
from evidence_shape.text_units import TextUnit, check_span_anchor

CLOCK = "2026-09-08T00:00:00+00:00"
HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"

#: A page in the shape `extractors/pdf.py` writes one: several lines, no blank line
#: between them. Measured on the owner's own corpus at `gt-w1bn`: of the 714 stored
#: text units longer than 333 characters, 671 hold no blank line at all, so a
#: paragraph boundary is not available to cut on and the last LINE BREAK before the
#: bound is the only structure a page reliably has.
PAGE = ("PHYS 1401 Homework 3, Spring 2026\n"
        "Answer all five questions and show your working.\n"
        "Question 1. A block of mass m slides down a frictionless incline.\n"
        "Question 2. Two carts collide elastically on a level track.\n")


def _page(p4_conn, *, text=PAGE, unit=True, span=None):
    """One page unit and the span-less body reading over the whole of it."""
    record_run(p4_conn, ExtractionRun(
        run_id="r1", file_id="f1", content_hash=HASH,
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    at = (Segment("page", 1),)
    if unit:
        record_text_unit(p4_conn, TextUnit(run_id="r1", container_path=at, text=text))
    return Observation(
        file_id="f1", content_hash=HASH, extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document", raw_value=text,
        location=Location("body", at, text_span=span), occurrence_count=1,
        observed_at=CLOCK, reliability="possible", run_id="r1",
        normalized_value=None, context_before=None, context_after=None,
        context_truncated=False)


def test_the_opening_reading_is_the_units_first_characters_with_a_span(p4_conn):
    """The whole point: a reading of the page that is NOT the whole of the page, so
    the whole-unit refusal keeps doing its job and the model still gets sentences."""
    whole = _page(p4_conn)

    opening = opening_reading_for(p4_conn, whole, extractor_name="release.opening",
                                  extractor_version="1.0.0", bound=120)

    assert opening.location.text_span.start == 0
    assert opening.location.text_span.end < len(PAGE)
    assert opening.raw_value == PAGE[:opening.location.text_span.end]
    assert opening.location.zone == whole.location.zone
    assert opening.location.container_path == whole.location.container_path
    assert opening.run_id == whole.run_id
    # Its own provenance, so nothing reads it as a second reading of the bytes.
    assert opening.extractor_name == "release.opening"
    # And it anchors against the same unit, which is what makes it releasable
    # rather than an `UnresolvableSpan` at the door.
    check_span_anchor(opening, unit_for_observation(p4_conn, opening))


def test_the_cut_is_the_documents_own_line_break_and_not_the_bound(p4_conn):
    """The BOUND says how much may travel; the DOCUMENT says where the text stops.

    A cut at the bound itself would end mid-word, so the reading ends at the last
    line break at or before it -- the only structure a page of extracted text has.
    """
    whole = _page(p4_conn)

    opening = opening_reading_for(p4_conn, whole, extractor_name="release.opening",
                                  extractor_version="1.0.0", bound=120)

    assert opening.raw_value.endswith("\n")
    assert opening.raw_value == (
        "PHYS 1401 Homework 3, Spring 2026\n"
        "Answer all five questions and show your working.\n")


def test_a_unit_with_no_line_break_before_the_bound_is_cut_at_the_bound(p4_conn):
    """671 of the owner's 714 long units hold no blank line and some hold no newline
    at all -- one 27,510-character paragraph of extracted text among them (`104`
    R-145). Refusing to cut there would leave exactly those files showing nothing."""
    run_on = "x" * 500
    whole = _page(p4_conn, text=run_on)

    opening = opening_reading_for(p4_conn, whole, extractor_name="release.opening",
                                  extractor_version="1.0.0", bound=120)

    assert opening.location.text_span == TextSpan(0, 120)
    assert opening.raw_value == run_on[:120]


def test_a_unit_no_longer_than_the_bound_has_no_opening(p4_conn):
    """The opening would BE the unit, and a reading whose span covers the whole of
    its unit is the thing the whole-unit rule refuses. Nothing is minted to walk
    around a refusal; a short unit is already `104` R-152's line or heading and is
    released, or it is not, and that stays P7's answer."""
    whole = _page(p4_conn, text="Homework 3\n")

    assert opening_reading_for(p4_conn, whole, extractor_name="release.opening",
                               extractor_version="1.0.0", bound=120) is None


def test_a_reading_that_already_carries_a_span_has_no_opening(p4_conn):
    """This cuts the shape that has no span. A reading WITH one is already addressed
    inside its unit, and re-cutting it would move a citation the model may be about
    to make."""
    heading = _page(p4_conn, span=TextSpan(0, 9))

    assert opening_reading_for(p4_conn, heading, extractor_name="release.opening",
                               extractor_version="1.0.0", bound=120) is None


def test_a_reading_with_no_stored_unit_has_no_opening(p4_conn):
    """§2.3's spreadsheet cell and §2.8's EXIF field: span-less with no unit at their
    path, so there is nothing to take a substring of. `line_reading_for` refuses the
    same state for the same reason."""
    whole = _page(p4_conn, unit=False)

    assert opening_reading_for(p4_conn, whole, extractor_name="release.opening",
                               extractor_version="1.0.0", bound=120) is None


def test_the_opening_reading_is_built_and_not_recorded(p4_conn):
    """Whether the reading may exist at all is the caller's rule, exactly as it is
    for `104` R-135's minted line: P4 hands back a record and writes nothing."""
    whole = _page(p4_conn)
    before = p4_conn.execute("SELECT count(*) c FROM evidence").fetchone()["c"]

    opening_reading_for(p4_conn, whole, extractor_name="release.opening",
                        extractor_version="1.0.0", bound=120)

    assert p4_conn.execute(
        "SELECT count(*) c FROM evidence").fetchone()["c"] == before


def test_a_bound_of_nothing_mints_nothing_rather_than_an_empty_reading(p4_conn):
    """The state a deployment that stores no dossier ceiling reaches. No bound means
    no excerpt -- never a bound chosen here, which is `104` R-159's whole ruling
    about invented lengths."""
    whole = _page(p4_conn)

    assert opening_reading_for(p4_conn, whole, extractor_name="release.opening",
                               extractor_version="1.0.0", bound=0) is None
