# tests/p5/test_p5_router.py
"""R - §2.9's routing. Done-means 10: "Routing follows signature over extension on
the disagreeing fixture, and each §2.9 family either has its handler or an explicit
`unsupported` status.\""""
from pathlib import Path

import pytest

from database_agent.db import create_schema

from extractors.router import (
    HANDLER_BY_FORMAT, HANDLER_BY_SOURCE_TYPE, SOURCE_TYPE_BY_FORMAT,
    record_routing_decision, route, routing_decisions,
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
    assert set(SOURCE_TYPE_BY_FORMAT) == named_by_2_9 | named_by_2_6_or_the_spec_fixtures


def test_no_audio_or_video_format_is_enumerated():
    # §2.9's audio-and-video bullet names a family and NO format. There is nothing to
    # key routing on, so the table has no entry and P5 invents none. The handler is
    # built and tested (Task 11); the routing entry is a NEEDS JOSEPH item.
    assert not [fmt for fmt, families in SOURCE_TYPE_BY_FORMAT.items()
                if "audio_video" in families]


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
