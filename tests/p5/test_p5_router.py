# tests/p5/test_p5_router.py
"""R - §2.9's routing. Done-means 10: "Routing follows signature over extension on
the disagreeing fixture, and each §2.9 family either has its handler or an explicit
`unsupported` status.\""""
from pathlib import Path

import pytest

from database_agent.db import create_schema

from evidence_shape.vocabulary import COMPLETENESS, SOURCE_TYPES, check

from extractors.router import (
    HANDLER_BY_FORMAT, HANDLER_BY_SOURCE_TYPE, SOURCE_TYPE_BY_FORMAT,
    UNROUTED_COMPLETENESS, record_routing_decision, route, routing_decisions,
)
from extractors.schema import create_extraction_schema


def detector(mapping):
    return lambda path: mapping.get(path.name)


def test_a_txt_that_is_a_zip_by_signature_routes_to_the_archive_extractor():
    # SPEC fixture: "`report.txt` that is a ZIP by signature | §2.9 | routes by
    # signature, not extension."
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/report.txt"), extension=".txt",
                     detect_format=detector({"report.txt": "zip"}))
    assert decision.detected_format == "zip"
    assert decision.declared_extension == ".txt"
    assert decision.disagree is True
    assert decision.source_type == "archive"
    assert decision.extractor_name == "archive.manifest"


def test_agreement_is_recorded_as_agreement():
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/Syllabus.pdf"), extension=".pdf",
                     detect_format=detector({"Syllabus.pdf": "pdf"}))
    assert decision.disagree is False
    assert decision.extractor_name == "pdf.text"


def test_the_extension_is_used_when_the_detector_cannot_identify_the_file():
    # §2.9: "inspect the real MIME type or file signature WHERE POSSIBLE".
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/notes.md"), extension=".md",
                     detect_format=lambda path: None)
    assert decision.detected_format is None
    assert decision.disagree is False
    assert decision.source_type == "text_document"
    assert decision.extractor_name == "text.structured"


def test_pdf_and_csv_carry_both_of_the_families_2_9_lists_them_under():
    # SPEC Open question 2: "Routing precedence for formats §2.9 lists twice. CSV
    # appears under both Spreadsheets and Code/structured data; PDF appears under
    # both Text documents and Presentations. The design specifies different field
    # lists for each and no tiebreak." Not answered here.
    assert SOURCE_TYPE_BY_FORMAT["pdf"] == ("text_document", "presentation")
    assert SOURCE_TYPE_BY_FORMAT["csv"] == ("spreadsheet", "code_structured")
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/grades.csv"), extension=".csv",
                     detect_format=detector({"grades.csv": "csv"}))
    assert decision.source_type_candidates == ("spreadsheet", "code_structured")
    assert decision.source_type == "spreadsheet"      # §2.9's document order, not a preference


def test_every_format_in_the_table_is_one_2_9_or_2_6_names():
    # No invented membership: each key is a format the design spells.
    named_by_2_9 = {
        "pdf", "docx", "rtf", "txt", "md", "html", "epub", "odt",          # text documents
        "xlsx", "xls", "csv", "tsv", "ods", "numbers",                     # spreadsheets
        "pptx", "ppt", "odp",                                              # presentations
        "eml", "mbox", "msg",                                              # email
        "ics", "vcf",                                                      # calendar, contacts
        "py", "js", "sql", "ipynb", "json", "yaml", "yml", "toml", "xml",  # code/structured
        "psd", "ai", "svg",                                                # design/creative
        "zip",                                                             # archives
        "dmg", "bin",                                                      # opaque binary
    }
    named_by_2_6_or_the_spec_fixtures = {"heic", "png", "jpg", "jpeg"}
    # The only keys neither § spells. They are here on ratification B6 and each is
    # declared HERE as well as in the table, so a later format cannot be added
    # silently: adding a key without adding it to one of these three sets fails.
    added_by_b6_and_not_by_a_design_sentence = {
        "webp", "gif", "tiff", "tif", "bmp", "heif", "avif",   # §2.6 names only HEIC and PNG
        "mp3", "m4a", "wav", "mp4", "mov",                     # §2.9 names the family and no format
    }
    assert set(SOURCE_TYPE_BY_FORMAT) == (named_by_2_9
                                          | named_by_2_6_or_the_spec_fixtures
                                          | added_by_b6_and_not_by_a_design_sentence)


def test_every_source_type_the_table_names_is_in_p4s_closed_vocabulary():
    # P4 D2: "Closed means an extractor may not add a value... Adding a zone or a kind
    # is a P4 contract revision plus a shape-version bump, never a local decision
    # inside an extractor." The router is the one place in P5 that maps a format onto
    # a `source_type`, so it is where an invented family would enter the system. The
    # formats added under B6 are the reason this walk exists rather than a reviewer's
    # eye: the next format someone adds is checked by a test.
    for fmt, families in SOURCE_TYPE_BY_FORMAT.items():
        assert families, f"{fmt!r} is a key with no family; route() would find no handler"
        for family in families:
            check(family, SOURCE_TYPES, name=f"SOURCE_TYPE_BY_FORMAT[{fmt!r}]")
    for family in HANDLER_BY_SOURCE_TYPE:
        check(family, SOURCE_TYPES, name="HANDLER_BY_SOURCE_TYPE key")
    for family, completeness in UNROUTED_COMPLETENESS.items():
        check(family, SOURCE_TYPES, name="UNROUTED_COMPLETENESS key")
        check(completeness, COMPLETENESS, name=f"UNROUTED_COMPLETENESS[{family!r}]")


def test_the_audio_and_video_routing_entry_is_answered_rather_than_open():
    # This assertion used to be its own opposite: §2.9's audio-and-video bullet names
    # a family and NO format, so there was nothing to key routing on and the entry was
    # a NEEDS JOSEPH item. B6 (ratified 2026-08-20) answered it - "Every file type is
    # extracted, and extracted correctly for its own type - except audio and video,
    # which stop at container metadata for v1" - and NEEDS JOSEPH 7 was answered the
    # same day: "Speech-to-text is OUT OF SCOPE for v1... Audio and video stop at
    # container metadata." The five tokens are inference from that, not design text.
    assert {fmt for fmt, families in SOURCE_TYPE_BY_FORMAT.items()
            if "audio_video" in families} == {"mp3", "m4a", "wav", "mp4", "mov"}


def test_an_unknown_format_is_unsupported_and_never_an_empty_document():
    # §2.4: "an empty extraction result is different from an extractor that does not
    # yet exist."
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/thing.qqq"), extension=".qqq",
                     detect_format=lambda path: None)
    assert decision.extractor_name is None
    assert decision.unrouted_completeness == "unsupported"


def test_a_disk_image_and_an_executable_stop_at_metadata_only():
    # SPEC fixture: "`archive.dmg`, `tool.bin` | §2.9 | `metadata_only`."
    for name, extension, fmt in (("archive.dmg", ".dmg", "dmg"),
                                 ("tool.bin", ".bin", "bin")):
        decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                         path=Path("/corpus") / name, extension=extension,
                         detect_format=detector({name: fmt}))
        assert decision.source_type == "opaque_binary"
        assert decision.extractor_name is None
        assert decision.unrouted_completeness == "metadata_only"


def test_a_proprietary_design_format_is_unreadable_not_unsupported():
    # SPEC fixture: "`design.psd` | §2.9 | `unreadable` carrying metadata-level
    # observations (M3) - indexed-but-unreadable, never zero rows."
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/design.psd"), extension=".psd",
                     detect_format=detector({"design.psd": "psd"}))
    assert decision.source_type == "design_creative"
    assert decision.extractor_name is None
    assert decision.unrouted_completeness == "unreadable"


def test_svg_routes_to_the_image_extractor():
    # SPEC routing table: design and creative -> "E5 (raster/SVG), else `unreadable`".
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/logo.svg"), extension=".svg",
                     detect_format=detector({"logo.svg": "svg"}))
    assert decision.extractor_name == "image.metadata"


def test_the_rest_of_a_mac_corpus_reaches_e5_rather_than_the_unsupported_stop():
    # 19-p4-p5-stress.md, "Routing: images and media": "Screenshots on this Mac are
    # usually PNG (routed). iPhone photos are HEIC (routed). WhatsApp / browser saves
    # are often WebP or GIF. Those files get a filesystem filename and nothing else -
    # no dimensions, no EXIF, no OCR trigger via E5. OCR policy keys off an
    # image/native result that never ran." Neither §2.6 nor §2.9 names these tokens;
    # B6 is what puts them in the table, and the table's comment says so.
    png = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                path=Path("/corpus/Screenshot.png"), extension=".png",
                detect_format=detector({"Screenshot.png": "png"}))
    for name, extension, fmt in (("saved.webp", ".webp", "webp"),
                                 ("meme.gif", ".gif", "gif"),
                                 ("scan.tiff", ".tiff", "tiff"),
                                 ("old.bmp", ".bmp", "bmp"),
                                 ("burst.heif", ".heif", "heif"),
                                 ("shared.avif", ".avif", "avif")):
        decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                         path=Path("/corpus") / name, extension=extension,
                         detect_format=detector({name: fmt}))
        assert decision.source_type == "image"
        # The handler PNG and HEIC already reach. §2.7's OCR policy keys off an
        # image/native result, and a family that never routes has none to key off.
        assert decision.extractor_name == png.extractor_name == "image.metadata"
        assert decision.unrouted_completeness is None


def test_both_customary_spellings_of_tiff_are_keys():
    # §2.9 routes on the detected format "where possible" and on the declared
    # extension otherwise, so a scan the detector cannot identify is keyed by ".tif".
    # One format under two extensions, as `jpg`/`jpeg` and `yaml`/`yml` already are.
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/scan.tif"), extension=".tif",
                     detect_format=lambda path: None)
    assert decision.detected_format is None
    assert decision.source_type == "image"
    assert decision.extractor_name == "image.metadata"


def test_audio_and_video_reach_e3_and_stop_at_container_metadata():
    # B6, ratified 2026-08-20: "Every file type is extracted, and extracted correctly
    # for its own type - except audio and video, which stop at container metadata for
    # v1." The handler is not new and is not invented here: the P5 SPEC's own routing
    # table already reads "| Audio and video | - | duration, container and codec
    # metadata, creation time, embedded tags, subtitles or captions where present;
    # speech-to-text transcripts only under an explicit privacy and compute policy |
    # E3 |", and E3 is `text.structured` (long_tail.py). What was missing was a format
    # token to key routing on - the literal "-" in that row's format column.
    for name, extension, fmt in (("lecture.mp3", ".mp3", "mp3"),
                                 ("voice memo.m4a", ".m4a", "m4a"),
                                 ("interview.wav", ".wav", "wav"),
                                 ("demo.mp4", ".mp4", "mp4"),
                                 ("clip.mov", ".mov", "mov")):
        decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                         path=Path("/corpus") / name, extension=extension,
                         detect_format=detector({name: fmt}))
        assert decision.source_type == "audio_video"
        assert decision.extractor_name == HANDLER_BY_SOURCE_TYPE["audio_video"]
        assert decision.extractor_name == "text.structured"
        # NOT `metadata_only`. That value is zero observations - §2.9's safe stop for
        # disk images and unknown binaries - and zero observations cannot carry the
        # duration, codec and tag fields §2.9's audio/video bullet asks for. "Stops at
        # container metadata" is E3 running with transcription unauthorized.
        assert decision.unrouted_completeness is None


def test_an_mp3_is_no_longer_indistinguishable_from_an_unknown_binary():
    # 19-p4-p5-stress.md: "An `.mp3` is not an unknown format. It is a format the
    # product chose not to transcribe. Today it is indistinguishable from
    # `thing.qqq`." B6 is what makes the two different.
    unknown = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                    path=Path("/corpus/thing.qqq"), extension=".qqq",
                    detect_format=lambda path: None)
    mp3 = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", path=Path("/corpus/lecture.mp3"),
                extension=".mp3", detect_format=detector({"lecture.mp3": "mp3"}))
    assert (unknown.source_type, unknown.extractor_name) == (None, None)
    assert unknown.unrouted_completeness == "unsupported"
    assert mp3.source_type == "audio_video"
    assert mp3.extractor_name is not None
    assert mp3.unrouted_completeness is None


def test_the_four_core_families_reach_their_named_handlers():
    assert HANDLER_BY_FORMAT["pdf"] == "pdf.text"
    assert HANDLER_BY_FORMAT["docx"] == "docx.structure"
    assert HANDLER_BY_SOURCE_TYPE["archive"] == "archive.manifest"
    assert HANDLER_BY_SOURCE_TYPE["image"] == "image.metadata"
    for family in ("text_document", "spreadsheet", "presentation", "email",
                   "calendar", "contacts", "code_structured", "audio_video"):
        assert HANDLER_BY_SOURCE_TYPE[family] == "text.structured"


def test_pdf_slide_decks_route_to_e1_and_the_question_stays_open():
    # SPEC routing table: "Presentations | ... PDF slide decks | ... | E3 (PDF decks:
    # E1)". There is no deck detection anywhere: distinguishing a slide deck from a
    # document is OQ2's other half and is not answered in code.
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/deck.pdf"), extension=".pdf",
                     detect_format=detector({"deck.pdf": "pdf"}))
    assert decision.extractor_name == "pdf.text"
    assert "presentation" in decision.source_type_candidates


def test_the_decision_is_recorded_and_readable(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    decision = route(file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     path=Path("/corpus/report.txt"), extension=".txt",
                     detect_format=detector({"report.txt": "zip"}))
    record_routing_decision(conn, decision)
    rows = routing_decisions(conn, "f1", "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124")
    assert len(rows) == 1
    assert rows[0]["detected_format"] == "zip"
    assert rows[0]["declared_extension"] == ".txt"
    assert rows[0]["disagree"] == 1
    assert rows[0]["source_type"] == "archive"
    assert rows[0]["extractor_name"] == "archive.manifest"


def test_p5_creates_no_p4_table(conn):
    # `evidence`, `extraction_runs` and `text_units` are P4's. P5 writes them through
    # the sink and creates none of them.
    create_schema(conn)
    create_extraction_schema(conn)
    tables = {r["name"] for r in
              conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "extraction_routing" in tables
    for p4_table in ("evidence", "extraction_runs", "text_units"):
        assert p4_table not in tables


def test_the_schema_is_idempotent(conn):
    create_schema(conn)
    create_extraction_schema(conn)
    create_extraction_schema(conn)
