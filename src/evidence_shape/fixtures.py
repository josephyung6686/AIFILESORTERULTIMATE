# src/evidence_shape/fixtures.py
"""The SPEC's nineteen worked examples, as golden records.

Done-means 9: "a P5 author can write a conforming extractor from this document plus
the fixtures without asking P4 a question", and "P6 resolves `course = BUSIB 4300`
from fixture 1 with no extractor present". P6, P7, P8 and P2 are all built before any
extractor exists; this module is what they build against.

Records, not files. Every consumer imports them, and a JSON file would need a loader
that reconstructs exactly the records this package already constructs -- a second
construction path for one set of data. `canonical_json(observation.to_mapping())`
produces the golden bytes whenever a file is wanted.

The coverage shortfall is computed here and published, not filled: the SPEC's own
table reaches 10 of the 15 zones and 13 of the 14 source types, and inventing the
missing examples would author the very thing six extractor authors would implement
against.

No fixture carries a `signal_tier`. §2.6 makes `DateTimeOriginal` both "camera EXIF"
(tier 1) and a "capture time" (tier 2), so the design does not settle it, and which
field belongs to which tier is P5's catalogue (SPEC, Deferred). Extractor names here
are illustrative for the same reason: P5 owns the routing table and the real names.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field

from evidence_shape.canonical import sha256_of
from evidence_shape.location import Location, Region, Segment, TextSpan, TimeSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.text_units import TextUnit
from evidence_shape.vocabulary import SOURCE_TYPES, ZONES

#: Pinned, so two readings of a fixture are never two readings of the wall clock.
FIXTURE_OBSERVED_AT = "2026-08-19T14:03:22+00:00"
FIXTURE_STARTED_AT = "2026-08-19T14:00:00+00:00"

#: Fixture 3's page: a reference list, elided down to the offsets the SPEC's golden
#: locator names. `body:page=18#12043-12051` is §2.2's page-eighteen reference.
_PAGE_18 = "…" * 12043 + "Columbia" + " University Press, 2019."

#: Fixture 8's OCR region. §7.8's admissions screenshot; the span is 0-24.
_OCR_REGION_4_2 = "Your Columbia University application status"

#: Fixture 11's unit. Rule 10 requires a unit for every span, and this span is into a
#: filename -- see the module tests for the tension that records.
_FILENAME = "Wash U.docx"

#: Fixture 13's speaker note. The golden span is 0-42, so the note is at least that
#: long; the words themselves are fixture text and carry no meaning to any rule.
_SLIDE_6_NOTES = "Application deadlines close on 1 December; mention the fee waiver."


@dataclass(frozen=True, slots=True)
class Fixture:
    """One row of the SPEC's worked-example table, as records."""

    number: int
    design_case: str
    run: ExtractionRun
    observations: tuple[Observation, ...] = ()
    text_units: tuple[TextUnit, ...] = ()


def _content_hash(number: int) -> str:
    return sha256_of(f"fixture-{number}")


def _run(number: int, *, source_type: str, extractor_name: str, analysis_tier: str,
         completeness: str = "complete", config: dict | None = None) -> ExtractionRun:
    return ExtractionRun(
        run_id=f"run-{number:02d}", file_id=f"file-{number:02d}",
        content_hash=_content_hash(number), extractor_name=extractor_name,
        extractor_version="1.0.0", source_type=source_type,
        analysis_tier=analysis_tier, config=config or {},
        completeness=completeness, started_at=FIXTURE_STARTED_AT,
        finished_at=FIXTURE_OBSERVED_AT)


def _observation(number: int, run: ExtractionRun, *, location: Location,
                 raw_value: str, reliability: str, **rest) -> Observation:
    return Observation(
        file_id=run.file_id, content_hash=run.content_hash,
        extractor_name=run.extractor_name, extractor_version=run.extractor_version,
        source_type=run.source_type, raw_value=raw_value, location=location,
        occurrence_count=rest.pop("occurrence_count", 1),
        observed_at=FIXTURE_OBSERVED_AT, reliability=reliability,
        run_id=run.run_id, **rest)


def _one(number: int, design_case: str, *, source_type: str, extractor_name: str,
         analysis_tier: str = "native", completeness: str = "complete",
         config: dict | None = None, units: tuple[TextUnit, ...] = (),
         **observation) -> Fixture:
    run = _run(number, source_type=source_type, extractor_name=extractor_name,
               analysis_tier=analysis_tier, completeness=completeness, config=config)
    return Fixture(number, design_case, run,
                   (_observation(number, run, **observation),),
                   tuple(TextUnit(run_id=run.run_id, container_path=path, text=text)
                         for path, text in units))


FIXTURES: tuple[Fixture, ...] = (
    # 1 -- §2.8 "page 1, heading 2"; §3.2's syllabus. The walking-skeleton fixture:
    # its context carries §3.5's "syllabus" term, which is what lets P6 resolve it
    # rather than refuse it (B8a).
    _one(1, '§2.8 "page 1, heading 2"; §3.2\'s syllabus',
         source_type="text_document", extractor_name="pdf.text",
         location=Location("heading", (Segment("page", 1),
                                       Segment("heading", 2,
                                               label="Course Information"))),
         raw_value="BUSIB 4300", normalized_value="BUSIB 4300",
         reliability="possible", occurrence_count=3,
         context_before="Syllabus — ", context_after=" — Spring 2026"),
    # 2 -- §3.2 "the PDF title".
    _one(2, '§3.2 "the PDF title"', source_type="text_document",
         extractor_name="pdf.text",
         location=Location("title", (Segment("page", 1),)),
         raw_value="BUSIB 4300 Syllabus", reliability="direct"),
    # 3 -- §2.2's page-eighteen reference list. Its zone is `body`: the SPEC's own
    # reference-list example is not filed under `reference_list`.
    _one(3, "§2.2's page-eighteen reference list", source_type="text_document",
         extractor_name="pdf.text",
         location=Location("body", (Segment("page", 18),),
                           text_span=TextSpan(12043, 12051)),
         raw_value="Columbia", reliability="possible",
         units=((( Segment("page", 18),), _PAGE_18),)),
    # 4 -- §2.8's DOCX example; §2.3 tables.
    _one(4, "§2.8's DOCX example; §2.3 tables", source_type="text_document",
         extractor_name="docx.text",
         location=Location("table", (Segment("table", 3), Segment("row", 2),
                                     Segment("column", 1))),
         raw_value="Wash U", reliability="possible"),
    # 5 -- §2.3's `Wash U.docx` heading.
    _one(5, "§2.3's Wash U heading", source_type="text_document",
         extractor_name="docx.text",
         location=Location("heading", (Segment("page", 1), Segment("heading", 1))),
         raw_value="Please tell us what you are interested in studying at college "
                   "and why.",
         reliability="possible"),
    # 6 -- §2.2: `direct` describes the SLOT, not the value's usefulness. P6
    # discounts it (§2.2, §2.3); P4 does not pre-discount it.
    _one(6, "§2.2 — direct describes the slot, not the value's usefulness",
         source_type="text_document", extractor_name="docx.metadata",
         location=Location("metadata", (Segment("field", label="Producer"),)),
         raw_value="python-docx", reliability="direct"),
    # 7 -- §2.8's EXIF example; §3.2's capture-date derivation. `signal_tier` is
    # null: §2.6 makes this both camera EXIF and a capture time, and the
    # field-to-tier catalogue is P5's.
    _one(7, "§2.8's EXIF example; §3.2's capture-date derivation",
         source_type="image", extractor_name="image.exif",
         location=Location("metadata",
                           (Segment("field", label="DateTimeOriginal"),)),
         raw_value="2026:07:17 14:03:22", reliability="direct"),
    # 8 -- §2.8's "OCR region"; §7.8's admissions screenshot. §2.7's bounding box
    # and confidence both have their worked example here; the geometry is fixture
    # geometry and the confidence is the SPEC's own 0.92.
    _one(8, '§2.8\'s "OCR region"; §7.8\'s admissions screenshot',
         source_type="ocr", extractor_name="ocr.apple_vision", analysis_tier="ocr",
         config={"dpi": 200, "languages": ["en"], "recognition": "accurate"},
         location=Location("ocr", (Segment("page", 4), Segment("region", 2)),
                           text_span=TextSpan(0, 24),
                           region=Region(0.08, 0.21, 0.55, 0.06, "norm")),
         raw_value="Your Columbia University", reliability="possible",
         confidence=0.92,
         units=(((Segment("page", 4), Segment("region", 2)), _OCR_REGION_4_2),)),
    # 9 -- §2.8's "manifest path"; §2.5's submission.zip. The label needs escaping.
    _one(9, "§2.8's manifest path; §2.5's submission.zip", source_type="archive",
         extractor_name="zip.manifest",
         location=Location("manifest",
                           (Segment("entry", label="docs/transcript.pdf"),)),
         raw_value="docs/transcript.pdf", reliability="direct"),
    # 10 -- §2.5 "file count" — D7's `field` segment on an archive property.
    _one(10, '§2.5 "file count"', source_type="archive",
         extractor_name="zip.manifest",
         location=Location("manifest", (Segment("field", label="file_count"),)),
         raw_value="37", reliability="direct"),
    # 11 -- §2.2, §2.9 filename as evidence. Rule 10 requires a unit for this span,
    # and the unit that satisfies it holds the filename.
    _one(11, "§2.2, §2.9 filename as evidence", source_type="filesystem",
         extractor_name="fs.basic", analysis_tier="filesystem",
         location=Location("filename", (), text_span=TextSpan(0, 6)),
         raw_value="Wash U", reliability="possible",
         units=(((), _FILENAME),)),
    # 12 -- §2.9 "dates or identifiers from labeled cells". Segment-kind rule 3: the
    # native address `C7` is the column segment's label, not a separate kind.
    _one(12, '§2.9 "dates or identifiers from labeled cells"',
         source_type="spreadsheet", extractor_name="xlsx.cells",
         location=Location("table", (Segment("sheet", 2, label="Applications"),
                                     Segment("row", 7),
                                     Segment("column", 3, label="C7"))),
         raw_value="2025", reliability="possible"),
    # 13 -- §2.9 presentations.
    _one(13, "§2.9 presentations", source_type="presentation",
         extractor_name="pptx.notes",
         location=Location("notes", (Segment("slide", 6, label="Deadlines"),),
                           text_span=TextSpan(0, 42)),
         raw_value=_SLIDE_6_NOTES[:42], reliability="possible",
         units=(((Segment("slide", 6),), _SLIDE_6_NOTES),)),
    # 14 -- §2.9 email.
    _one(14, "§2.9 email", source_type="email", extractor_name="email.headers",
         location=Location("metadata", (Segment("field", label="Subject"),)),
         raw_value="Columbia Application — Next Steps", reliability="direct"),
    # 15 -- §2.9 calendar.
    _one(15, "§2.9 calendar", source_type="calendar", extractor_name="ics.fields",
         location=Location("metadata", (Segment("field", label="DTSTART"),)),
         raw_value="20260717T140000Z", reliability="direct"),
    # 16 -- §2.4, §2.9 package manifests. D7: `key` carries the structured-data key
    # path and `field` the format's own slot name, outermost first.
    _one(16, "§2.4, §2.9 package manifests", source_type="code_structured",
         extractor_name="pkg.manifest",
         location=Location("metadata", (Segment("key", label="dependencies"),
                                        Segment("field", label="name"))),
         raw_value="react", reliability="direct"),
    # 17 -- §2.9 audio/video. A caption at 04:12.5-04:15.2: no page and no
    # document-text offset, which is what `time_span` exists for.
    _one(17, "§2.9 audio/video", source_type="audio_video",
         extractor_name="av.transcript",
         location=Location("transcript", (), time_span=TimeSpan(252500, 255200)),
         raw_value="and the Columbia application is due in December",
         reliability="possible"),
    # 18 -- §2.9 design/creative. The run is `unreadable` and STILL carries this
    # metadata-level row: §2.9's "indexed-but-unreadable" (M3).
    _one(18, "§2.9 design/creative, indexed-but-unreadable (M3)",
         source_type="design_creative", extractor_name="psd.metadata",
         completeness="unreadable",
         location=Location("metadata", (Segment("layer", 3),)),
         raw_value="Background", reliability="direct"),
    # 19 -- §2.9's safe default for disk images, executables, databases, encrypted
    # containers, damaged files and unknown binary. No observation from THIS
    # extractor; the file is still indexed through fixture 11's pattern.
    Fixture(19, "§2.9's metadata_only safe default",
            _run(19, source_type="opaque_binary", extractor_name="binary.none",
                 analysis_tier="native", completeness="metadata_only")),
)

_BY_NUMBER = {fixture.number: fixture for fixture in FIXTURES}

#: Computed, never hand-listed, so the shortfall cannot drift from the fixtures.
_COVERED_ZONES = {observation.zone for fixture in FIXTURES
                  for observation in fixture.observations}

ZONES_WITH_A_WORKED_EXAMPLE: tuple[str, ...] = tuple(
    zone for zone in ZONES if zone in _COVERED_ZONES)

#: Done-means 5 asks for all of them; the SPEC's table supplies these none.
ZONES_WITHOUT_A_WORKED_EXAMPLE: tuple[str, ...] = tuple(
    zone for zone in ZONES if zone not in _COVERED_ZONES)

SOURCE_TYPES_WITHOUT_A_WORKED_EXAMPLE: tuple[str, ...] = tuple(
    source_type for source_type in SOURCE_TYPES
    if source_type not in {fixture.run.source_type for fixture in FIXTURES})


def by_number(number: int) -> Fixture:
    """The SPEC's own numbering, so a reviewer can check one row against one table."""
    return _BY_NUMBER[number]
