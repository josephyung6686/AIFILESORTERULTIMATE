# tests/p5/test_p5_person_fields.py
"""`104` R-161, owner item 15, ruled 8 Sep 2026 (`104` §17.6): a format's own
person-valued fields are signalled BY THE FIELD.

The ruling's words: *"a format's own person-valued fields (PDF `/Author`, OOXML
`dc:creator`, `cp:lastModifiedBy`) are signalled by the field, which is structure
and not a word list."* So every assertion below is about an ADDRESS -- the `field`
segment P4 D7 already carries -- and not one is about a value. No name, no address
pattern and no identifier shape appears in this file, because a detector's
vocabulary is the owner's and it has not been given (`104` §15.4 item 15).

What is NOT covered, stated because the ruling states it: body-text address and
identifier detection. R-161's other half stays open.
"""
from pathlib import Path

import pytest

from extractors.docx import DocxDocument, DocxParagraph, extract_docx
from extractors.dispatch import Dispatched, Readers, extract_initial
from extractors.long_tail import (
    LongTailEntry, LongTailFile, LongTailText, LongTailValue, POTENTIALLY_SENSITIVE,
    PERSON_VALUED_FIELD_BASIS, extract_long_tail,
)
from extractors.pdf import PdfDocument, PdfPage, extract_pdf
from extractors.router import route
from extractors.safety import SafetyPolicy
from extractors import structured_text
from extractors.structured_text import (
    StructuralMarker, TextDocument, extract_structured_text,
)

from conftest import FIXED_CLOCK

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
NO_STRINGS = lambda text: ()


def _row(filename: str) -> dict:
    return {"file_id": "f-person", "content_hash": HASH, "filename": filename}


def _field_of(observation) -> str | None:
    """The observation's own innermost `field` segment label -- the address the
    ruling signals by, read back off the stored locator."""
    fields = [s["label"] for s in observation["location"]["container_path"]
              if s["kind"] == "field"]
    return fields[-1] if fields else None


def _signalled_fields(result, signals) -> set:
    return {_field_of(result.observations[s.observation_index]) for s in signals}


# --------------------------------------------------------------------------- PDF

def a_pdf() -> PdfDocument:
    """A PDF Info dictionary in the shape the owner's corpus actually carries: one
    person-valued slot beside four that name software or the document."""
    return PdfDocument(
        metadata={"Author": "Daniel Lacker", "Creator": "Microsoft Word",
                  "Producer": "Acrobat Distiller", "Title": "Lecture 3",
                  "Subject": "stochastic analysis"},
        pages=(PdfPage(number=1, text="Lecture 3. Martingales."),),
    )


def run_pdf(document=None):
    from extractors.pdf import person_field_signals
    result = extract_pdf(file_row=_row("lecture.pdf"), path=Path("/corpus/l.pdf"),
                         policy=OPEN_POLICY,
                         read_pdf=lambda path: document or a_pdf(),
                         find_structured_strings=NO_STRINGS, now=FIXED_CLOCK,
                         context_window=20)
    return result, person_field_signals(result)


def test_a_pdfs_author_slot_is_signalled_and_the_other_slots_are_not():
    result, signals = run_pdf()
    assert _signalled_fields(result, signals) == {"Author"}
    assert {s.signal for s in signals} == {POTENTIALLY_SENSITIVE}


def test_a_pdfs_creator_slot_is_not_signalled_because_it_names_software():
    """`/Creator` is the application that made the original document, not a person.

    Measured on the owner's 199-file corpus (`gt-w1bn`, 8 Sep 2026): 31 `/Creator`
    values, and all 31 are software -- `Microsoft Word`, `Adobe Scan for iOS
    24.09.17`, `WPS 文字`, `wkhtmltopdf 0.12.5`. Signalling it would be this file
    deciding, by reading the values, that a slot is person-valued -- which is the
    word list the ruling refuses. The owner's ruling names `/Author` and this
    module carries no other PDF slot.
    """
    result, signals = run_pdf()
    assert "Creator" not in _signalled_fields(result, signals)
    assert "Producer" not in _signalled_fields(result, signals)


def test_a_pdf_with_no_author_slot_raises_nothing():
    result, signals = run_pdf(PdfDocument(
        metadata={"Creator": "Microsoft Word"},
        pages=(PdfPage(number=1, text="Lecture 3."),)))
    assert signals == ()


def test_the_signal_indexes_into_the_batch_it_rides_with():
    """The invariant `LongTailResult` and `ImageResult` state in their own
    `__post_init__`: a position that is not a position in THIS batch is the defect
    that filed §2.9's signal against a neighbour."""
    result, signals = run_pdf()
    assert all(0 <= s.observation_index < len(result.observations) for s in signals)
    assert Dispatched((result,), signals, 0)          # constructs; the check is there


# -------------------------------------------------------------------------- DOCX

def a_docx(properties=None) -> DocxDocument:
    return DocxDocument(
        core_properties=properties if properties is not None else {
            "author": "Jessica Hofflich", "last_modified_by": "Joseph Yung",
            "title": "Application Essay", "keywords": "admissions",
            "language": "en-US"},
        paragraphs=(DocxParagraph(index=1, text="Why Wash U", zone="heading",
                                  heading_path=((1, "Why Wash U"),)),),
    )


def run_docx(document=None):
    from extractors.docx import person_field_signals
    result = extract_docx(file_row=_row("essay.docx"), path=Path("/corpus/e.docx"),
                          policy=OPEN_POLICY,
                          read_docx=lambda path: document or a_docx(),
                          find_structured_strings=NO_STRINGS, now=FIXED_CLOCK,
                          context_window=20)
    return result, person_field_signals(result)


def test_ooxml_creator_and_last_modified_by_are_signalled_by_their_fields():
    result, signals = run_docx()
    assert _signalled_fields(result, signals) == {"author", "last_modified_by"}


def test_the_other_core_properties_are_not_signalled():
    result, signals = run_docx()
    assert not {"title", "keywords", "language"} & _signalled_fields(result, signals)


def test_both_spellings_of_one_ooxml_field_are_the_same_field():
    """`dc:creator` reaches P5 as `author` through `readers/docx_python_docx.py`
    (python-docx's attribute name) and as `creator` through
    `readers/long_tail_stdlib._package_properties` (the XML element's own local
    name). Two spellings of ONE field, and the extractor takes whichever its reader
    supplies -- P5 names no reader (§2.9)."""
    result, signals = run_docx(a_docx({"creator": "Jessica Hofflich",
                                       "lastModifiedBy": "Joseph Yung",
                                       "title": "Application Essay"}))
    assert _signalled_fields(result, signals) == {"creator", "lastModifiedBy"}


def test_two_person_fields_holding_one_value_are_one_signal():
    """D10 collapses on (zone, exact raw value), and the sensitivity table is
    UNIQUE on (run_id, observation_key). A document whose author never changed
    hands writes the same name into both slots and that is ONE located value."""
    result, signals = run_docx(a_docx({"author": "Joseph Yung",
                                       "last_modified_by": "Joseph Yung"}))
    assert len(signals) == 1
    assert len({s.observation_index for s in signals}) == 1


def test_an_empty_person_field_is_no_row_and_so_no_signal():
    result, signals = run_docx(a_docx({"author": "", "title": "Essay"}))
    assert signals == ()


# --------------------------------------------------------------- text.structured

def test_an_ooxml_packages_core_properties_are_signalled_by_their_fields():
    """The long-tail half of `text.structured`: a spreadsheet or a deck carries
    `docProps/core.xml`, and `_package_properties` emits each element at its own
    local name."""
    workbook = LongTailFile(
        entries=(LongTailEntry(kind="sheet", index=1, label="Applications"),),
        values=(LongTailValue(name="creator", value="Giuseppina Cambareri"),
                LongTailValue(name="lastModifiedBy", value="Joseph"),
                LongTailValue(name="title", value="Applications")),
        texts=(LongTailText(zone="table", text="Wash U", entry_ordinal=1, row=2,
                            column=1, column_header="Institution"),),
    )
    result = extract_long_tail(
        file_row=_row("apps.xlsx"), path=Path("/corpus/a.xlsx"), policy=OPEN_POLICY,
        source_type="spreadsheet", read_long_tail=lambda p, *, transcribe: workbook,
        find_structured_strings=NO_STRINGS, transcription_authorized=lambda: False,
        now=FIXED_CLOCK, context_window=20)
    assert _signalled_fields(result.extraction, result.sensitivity) == {
        "creator", "lastModifiedBy"}
    assert {s.basis for s in result.sensitivity} == {PERSON_VALUED_FIELD_BASIS}


def test_a_plain_text_document_carries_no_person_valued_field():
    """The OTHER half of `text.structured` emits two metadata fields -- §2.4's
    `language` and its four structural-indicator classes -- and neither names a
    person. Nothing is signalled here, and adding something would need a word list.
    """
    document = TextDocument(
        text="# Syllabus\nPHYS 1401.\n", language="en",
        markers=(StructuralMarker(kind="README file", value="README.md"),))
    result = extract_structured_text(
        file_row=_row("readme.md"), path=Path("/corpus/r.md"), policy=OPEN_POLICY,
        source_type="text_document",
        read_text_document=lambda path: document,
        find_structured_strings=NO_STRINGS, now=FIXED_CLOCK, context_window=20)
    fields = {_field_of(o) for o in result.observations} - {None}
    assert fields == {"language", "README file"}
    # There is no `structured_text.person_field_signals`, and the absence is the
    # statement: neither field names a person, and a third would need a word list.
    assert not hasattr(structured_text, "person_field_signals")


# ---------------------------------------------------------------------- the seam

def _readers(**overrides) -> Readers:
    base = dict(
        read_pdf=lambda path: a_pdf(), read_docx=lambda path: a_docx(),
        read_text_document=lambda path: None,
        read_long_tail=lambda path, *, transcribe: None,
        read_manifest=lambda path: None, read_image=lambda path: None,
        find_structured_strings=NO_STRINGS,
        recognize_markers=lambda document: (), dimension_signal=lambda w, h: None,
        filename_pattern=lambda name: None)
    base.update(overrides)
    return Readers(**base)


@pytest.mark.parametrize("filename,field", [("lecture.pdf", "Author"),
                                            ("essay.docx", "author")])
def test_the_dispatcher_carries_the_signal_and_names_its_batch(filename, field):
    """A signal that does not reach `Dispatched` never reaches the database:
    `orchestrator` writes `dispatched.sensitivity` against `sensitivity_target`,
    and the caller that kept only the runs is why r15's signal table was empty over
    199 files (`104` R-161)."""
    row = _row(filename)
    path = Path("/corpus") / filename
    decision = route(file_id=row["file_id"], content_hash=HASH, path=path,
                     extension=path.suffix,
                     detect_format=lambda p: p.suffix.lstrip("."))
    dispatched = extract_initial(
        file_row=row, decision=decision, path=path,
        policy=OPEN_POLICY, readers=_readers(), now=FIXED_CLOCK,
        context_window=20, transcription_authorized=lambda: False)
    batch = dispatched.results[dispatched.sensitivity_target]
    assert field in _signalled_fields(batch, dispatched.sensitivity)
