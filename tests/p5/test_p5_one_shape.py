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


def producers(*, context_window: int = 16):
    """One call per producer, each over a fixture containing the same raw value.

    `context_window` is a parameter because P4 ratification B4 puts §8.6's context
    budget in the run's `config` "so it is fingerprinted": two runs at different
    context widths must not look identical to §3.4's cache key. Proving that needs
    the same producer built twice at two widths.
    """
    common = dict(file_row=FILE_ROW, path=PATH, policy=OPEN_POLICY,
                  now=FIXED_CLOCK, context_window=context_window)

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
        filename_pattern=lambda name: None, **common).extraction

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


#: Every producer, by name, so the two whole-surface invariants below are
#: parametrised rather than looped -- a failure names the producer that broke it.
PRODUCER_NAMES: tuple[str, ...] = tuple(name for name, _ in producers())


def build(name: str, *, context_window: int = 16):
    return dict(producers(context_window=context_window))[name]()


#: The same raw value twice in one zone, which is what D10 collapses. `producers()`
#: above holds no duplicate anywhere, so the count invariant is the identity case
#: there and passes whether or not the collapse corrects the number.
TWICE = f"{RAW} and again {RAW}."


def find_every_raw(text: str):
    found, at = [], text.find(RAW)
    while at != -1:
        found.append(StructuredString(kind="identifier", start=at, end=at + len(RAW)))
        at = text.find(RAW, at + 1)
    return tuple(found)


def duplicating_producers():
    """The same eight producers over a fixture that repeats ONE value in ONE zone.

    Each format repeats it where that format naturally can: two header slots holding
    one address, two EXIF tags holding one camera, a paragraph naming one institution
    twice. `pdf` and `archive` collapse their own candidate lists before counting and
    were already right; the other six counted the submitted list.
    """
    row = dict(FILE_ROW, mime_type=".pdf")     # equal to `extension`, zone `metadata`
    common = dict(file_row=row, path=PATH, policy=OPEN_POLICY, now=FIXED_CLOCK,
                  context_window=16)

    yield "filesystem", lambda: extract_filesystem(**common)

    yield "pdf", lambda: extract_pdf(
        read_pdf=lambda target: PdfDocument(
            metadata={}, pages=(PdfPage(number=1, text=TWICE, regions=()),)),
        find_structured_strings=find_every_raw, **common)

    yield "docx", lambda: extract_docx(
        read_docx=lambda target: DocxDocument(
            core_properties={}, cells=(),
            paragraphs=(DocxParagraph(index=1, text=TWICE, zone="body"),)),
        find_structured_strings=find_every_raw, **common)

    yield "structured_text", lambda: extract_structured_text(
        source_type="text_document",
        read_text_document=lambda target: TextDocument(text=TWICE,
                                                       language="Markdown"),
        find_structured_strings=find_every_raw, **common)

    yield "long_tail", lambda: extract_long_tail(
        source_type="email",
        read_long_tail=lambda target, *, transcribe: LongTailFile(
            entries=(LongTailEntry(kind="entry", label="<m-1@x>"),),
            values=(LongTailValue(name="From", value="a@example.com",
                                  entry_ordinal=1, kind="address"),
                    LongTailValue(name="Reply-To", value="a@example.com",
                                  entry_ordinal=1, kind="address"))),
        find_structured_strings=lambda text: (),
        transcription_authorized=lambda: False, **common).extraction

    yield "archive", lambda: extract_archive(
        read_manifest=lambda target: ArchiveManifest(
            archive_type="ZIP", inspected=2, total=2,
            members=(ArchiveMember(path=f"{RAW}/essay.docx"),
                     ArchiveMember(path=f"{RAW}/notes.docx"))),
        recognize_markers=lambda paths: (), **common)

    yield "image", lambda: extract_image(
        read_image=lambda target: ImageRecord(
            image_format="HEIC", dimensions="4032x3024", width=4032, height=3024,
            perceptual_hash="phash:1",
            exif=(ExifValue(name="Make", value="Apple", kind="camera EXIF"),
                  ExifValue(name="Model", value="Apple", kind="camera EXIF"))),
        dimension_signal=lambda width, height: None,
        filename_pattern=lambda name: None, **common).extraction

    yield "ocr", lambda: extract_ocr(
        ocr_engine=lambda target, *, config: OcrOutput(
            provider="apple-vision", provider_version="19.1",
            regions=(OcrRegion(page=1, region=1, text=TWICE, confidence=0.9),),
            pages_processed=1, pages_total=1),
        config={"recognition": "accurate"},
        find_structured_strings=find_every_raw, **common)


@pytest.mark.parametrize("name", PRODUCER_NAMES)
def test_the_run_counts_what_the_batch_holds(name):
    """`stage_output.py:73` copies `run["observation_count"]` into the P2 §8.5
    payload, and every extractor computes it from the list it SUBMITS -- before
    `ExtractionResult.__post_init__` applies D10 and collapses it. A batch holding
    one repeated value therefore reported a count its own batch cannot support: not
    an `.eml` edge case, but any file mentioning one string twice in one zone.
    """
    for result in (build(name), dict(duplicating_producers())[name]()):
        assert result.run["observation_count"] == len(result.observations)


#: The producers that hand the sink a list still holding the duplicate. `pdf` and
#: `archive` collapse their own candidate lists BEFORE counting -- their
#: `observation_count` was right all along -- so the collapse at the sink is the
#: identity for them and the invariant above is untestable there by construction.
COLLAPSING_AT_THE_SINK: tuple[str, ...] = ("filesystem", "docx", "structured_text",
                                           "long_tail", "image", "ocr")


@pytest.mark.parametrize("name", PRODUCER_NAMES)
def test_a_repeated_value_really_does_collapse_where_it_reaches_the_sink(name):
    """Without this, the count invariant above is the identity case in eight
    disguises: a fixture that happens to hold no duplicate proves nothing about a
    number that is only ever wrong when one is present."""
    repeated = dict(duplicating_producers())[name]()
    submitted, held = len(repeated.collapsed_index), len(repeated.observations)

    if name in COLLAPSING_AT_THE_SINK:
        assert submitted > held, (
            f"{name}'s duplicating fixture holds no duplicate, so the count "
            "invariant above proves nothing for it")
    else:
        assert submitted == held, (
            f"{name} used to collapse its own candidates before counting; if it "
            "stopped, it belongs in COLLAPSING_AT_THE_SINK")


@pytest.mark.parametrize("name", PRODUCER_NAMES)
def test_the_context_budget_is_fingerprinted(name):
    """P4 ratification B4: §8.6's context budget "goes in the run's `config` so it is
    fingerprinted". Without it two runs at different context widths are byte-identical
    to §3.4's cache key -- the cache serves an answer built at the other width and
    §8.5's replay cannot tell the two runs apart. The value is read, never defaulted:
    every producer here is already required to be given one.
    """
    narrow, wide = build(name, context_window=8), build(name, context_window=64)

    assert narrow.run["config"]["context_window"] == 8
    assert wide.run["config"]["context_window"] == 64
    assert narrow.run["config_fingerprint"] != wide.run["config_fingerprint"]
