# tests/p5/test_p5_one_shape.py
"""§2.8's whole claim. Done-means 2, 3 and 11.

"Every extractor must emit the same evidence shape ... so downstream logic can work
consistently across formats."
"""
from pathlib import Path

import pytest

from extractors.archive import ArchiveManifest, ArchiveMember, extract_archive
from extractors.docx import DocxCell, DocxDocument, DocxParagraph, extract_docx
from extractors.filesystem import extract_filesystem
from extractors.image import ExifValue, ImageRecord, extract_image
from extractors.long_tail import (
    LongTailEntry, LongTailFile, LongTailText, LongTailValue, extract_long_tail,
)
from extractors.ocr import OcrOutput, OcrRegion, extract_ocr
from extractors.pdf import PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region, StructuredString
from extractors.safety import SafetyPolicy
from extractors.shape import LOCATION_FIELDS, OBSERVATION_FIELDS
from extractors.structured_text import TextDocument, extract_structured_text

from conftest import FIXED_CLOCK
from p4_stub import locator_for, observation_key

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)
FILE_ROW = {"file_id": "f-1", "content_hash": "273433e673d6b366684561c0fa5d9bbb72c96174be4c68f0dde483c278aa5d97",
            "filename": "U Chicago admission.pdf",
            "normalized_filename": "u chicago admission.pdf", "extension": ".pdf",
            "mime_type": "application/pdf", "directory_position": "/corpus/apps"}
PATH = Path("/corpus/apps/U Chicago admission.pdf")

#: §2.8's own example of a value that must survive verbatim.
RAW = "U Chicago"

#: P4 scopes exactly two observation fields to a source type: conformance rule 11
#: scopes `signal_tier` to §2.6's images, and §2.7 puts OCR confidence on the
#: observation. Both are read through the DECLARED source type, which is what §2.8
#: publishes it for. A third entry here would be a new per-format branch.
SOURCE_TYPE_SCOPED = {"signal_tier": {"image"}, "confidence": {"ocr"}}

NULLABLE = ("normalized_value", "confidence", "signal_tier")


def find_raw(text: str):
    at = text.find(RAW)
    return (StructuredString(kind="identifier", start=at, end=at + len(RAW)),) if at != -1 else ()


def producers():
    """One call per producer, each over a fixture containing the same raw value."""
    common = dict(file_row=FILE_ROW, path=PATH, policy=OPEN_POLICY,
                  now=FIXED_CLOCK, context_window=16)

    yield "filesystem", lambda: extract_filesystem(**common)

    yield "pdf", lambda: extract_pdf(
        read_pdf=lambda target: PdfDocument(
            metadata={"Title": f"{RAW} supplement"},
            pages=(PdfPage(number=1, text=f"Applying to {RAW} this year.",
                           regions=(Region(zone="heading", start=0, end=11,
                                           ordinal=1, label="Applying to"),)),)),
        find_structured_strings=find_raw, **common)

    yield "docx", lambda: extract_docx(
        read_docx=lambda target: DocxDocument(
            core_properties={"creator": "python-docx"},
            paragraphs=(DocxParagraph(index=1, text=f"Why {RAW}?", zone="heading",
                                      heading_path=((1, "Why"),)),),
            cells=(DocxCell(table=1, row=1, column=1, text=RAW),)),
        find_structured_strings=find_raw, **common)

    yield "structured_text", lambda: extract_structured_text(
        source_type="text_document",
        read_text_document=lambda target: TextDocument(
            text=f"Notes on {RAW}.", language="Markdown"),
        find_structured_strings=find_raw, **common)

    yield "long_tail", lambda: extract_long_tail(
        source_type="email",
        read_long_tail=lambda target, *, transcribe: LongTailFile(
            entries=(LongTailEntry(kind="entry", label="<m-1@x>"),),
            values=(LongTailValue(name="Subject", value=RAW, entry_ordinal=1),),
            texts=(LongTailText(zone="body", text=f"About {RAW}.", entry_ordinal=1,
                                region=1),)),
        find_structured_strings=find_raw, transcription_authorized=lambda: False,
        **common).extraction

    yield "archive", lambda: extract_archive(
        read_manifest=lambda target: ArchiveManifest(
            archive_type="ZIP", members=(ArchiveMember(path=f"{RAW}/essay.docx"),),
            inspected=1, total=1),
        recognize_markers=lambda paths: (), **common)

    yield "image", lambda: extract_image(
        read_image=lambda target: ImageRecord(
            image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
            perceptual_hash="phash:1",
            exif=(ExifValue(name="Make", value="Apple", kind="camera EXIF"),)),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None, **common)

    yield "ocr", lambda: extract_ocr(
        ocr_engine=lambda target, *, config: OcrOutput(
            provider="apple-vision", provider_version="19.1",
            regions=(OcrRegion(page=1, region=1, text=f"Admitted to {RAW}.",
                               confidence=0.9),),
            pages_processed=1, pages_total=1),
        config={"recognition": "accurate"}, find_structured_strings=find_raw,
        **common)


def every_observation():
    for name, call in producers():
        for observation in call().observations:
            yield name, observation


def test_every_producer_emits_at_least_one_observation():
    produced = {name for name, _ in every_observation()}
    assert produced == {"filesystem", "pdf", "docx", "structured_text", "long_tail",
                        "archive", "image", "ocr"}


def test_there_is_exactly_one_observation_shape():
    shapes = {tuple(observation) for _, observation in every_observation()}
    assert shapes == {OBSERVATION_FIELDS}


def test_no_extractor_has_a_field_of_its_own():
    keys = set()
    for _, observation in every_observation():
        keys |= set(observation)
    assert keys == set(OBSERVATION_FIELDS)


def test_there_is_exactly_one_location_shape():
    shapes = {tuple(observation["location"])
              for _, observation in every_observation()}
    assert shapes == {LOCATION_FIELDS}


def test_one_consumer_reads_every_observation_with_no_per_format_branch():
    # Done-means 2. This function is the consumer: it names no extractor, no format
    # and no source type, and it works on all eight.
    def cite(observation):
        return (f"{observation['raw_value']} at "
                f"{locator_for(observation['location'])} "
                f"({observation['reliability']}, x{observation['occurrence_count']})")

    citations = [cite(observation) for _, observation in every_observation()]
    assert len(citations) == len(list(every_observation()))
    assert all(citation.strip() for citation in citations)
    assert len(set(citations)) > 20      # they are distinct, not a constant


def test_blinding_the_three_declared_fields_hides_the_producer():
    # The claim: with `extractor_name`, `extractor_version` and `source_type`
    # removed, no remaining field identifies which extractor wrote the row.
    by_field: dict[str, set[str]] = {}
    for name, observation in every_observation():
        for field in NULLABLE:
            if observation[field] is not None:
                by_field.setdefault(field, set()).add(name)

    for field, producers_setting in by_field.items():
        if len(producers_setting) > 1:
            continue
        assert field in SOURCE_TYPE_SCOPED, (
            f"{field} is set by {producers_setting} alone and P4 does not scope it "
            "to a source type — that is a per-format branch"
        )


def test_the_two_scoped_fields_are_read_through_the_declared_source_type():
    for _, observation in every_observation():
        for field, allowed in SOURCE_TYPE_SCOPED.items():
            if observation[field] is not None:
                assert observation["source_type"] in allowed, field


def test_raw_survives_verbatim_in_every_producer_that_saw_it():
    # Done-means 3: "`U Chicago` keeps that exact wording as the raw value".
    carriers = {name for name, observation in every_observation()
                if observation["raw_value"] == RAW}
    assert {"pdf", "docx", "structured_text", "long_tail", "ocr"} <= carriers
    for name, observation in every_observation():
        if observation["raw_value"] == RAW:
            assert observation["normalized_value"] in (None, RAW), name


def test_every_producer_is_deterministic():
    # Done-means 11 / P4 conformance rule 8: a property of TWO runs, which is why it
    # is here and not in the per-observation validator.
    for name, call in producers():
        first, second = call(), call()
        assert first.observations == second.observations, name
        assert first.text_units == second.text_units, name
        assert first.run == second.run, name


def test_the_observation_key_is_stable_across_runs():
    for name, call in producers():
        keys = [tuple(observation_key(o) for o in call().observations)
                for _ in range(2)]
        assert keys[0] == keys[1], name


def test_every_producer_conforms_to_p4s_shape(sink):
    for _, call in producers():
        sink.write(call())
    sink.conforms()


def test_the_shared_fields_carry_the_per_format_difference():
    # The other half of §2.8: one shape does not mean one kind of content. The
    # difference lives in `zone` and `container_path`, which every consumer reads.
    zones = {observation["location"]["zone"]
             for _, observation in every_observation()}
    assert {"filename", "path", "metadata", "title", "heading", "table", "body",
            "manifest", "ocr"} <= zones
    kinds = {segment["kind"] for _, observation in every_observation()
             for segment in observation["location"]["container_path"]}
    assert {"field", "page", "heading", "table", "row", "column", "entry"} <= kinds
