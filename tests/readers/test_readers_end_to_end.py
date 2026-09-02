# tests/readers/test_readers_end_to_end.py
"""The whole Wave-2 path over a real PDF, with real libraries. No fixture readers.

Every other test of `run_wave2` injects a deterministic fake reader, which proves the
JOIN and says nothing about whether a real library can actually fill the shape. This
is the one that opens a file.
"""
import re
from pathlib import Path

import pytest

# All three, and all three BEFORE the `readers.deployment` import below.
# `deployment` imports `ocr_vision`, which imports Vision and Quartz at module scope,
# so guarding only pdfminer would make this module raise during COLLECTION on any
# machine without pyobjc -- and a collection error is fatal to the whole run, not a
# skip. The suite would go from "readers skipped" to "nothing ran".
pytest.importorskip("pdfminer", reason="pdfminer.six is an optional `readers` extra")
pytest.importorskip("Vision", reason="pyobjc-framework-Vision is a `readers` extra")
pytest.importorskip("Quartz", reason="pyobjc-framework-Quartz is a `readers` extra")

from orchestrator import TARGETED_OCR_UNAVAILABLE, run_wave2
from pdf_bytes import build_pdf
from readers.deployment import macos_readers
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.selection import record_selection


@pytest.fixture()
def db(conn):
    """All five parts' tables. A harness that creates four out of five is testing a
    database the product never runs on — that gap once hid the routing table
    entirely. Declared here rather than imported from `tests/wave2/`: pytest only
    puts a test directory on `sys.path` while collecting it, so that import breaks
    whenever this directory is run alone."""
    from database_agent.db import create_schema
    from eval_harness.store import create_eval_schema
    from evidence_shape.schema import create_evidence_schema
    from extractors.schema import create_extraction_schema
    from scan_agent.schema import create_scan_schema
    create_schema(conn)
    create_scan_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    create_eval_schema(conn)
    return conn


#: The test's OWN pattern, not a product default. §2.2 names "identifiers" as a class
#: and P5's SPEC puts the patterns in its Deferred table, so a real deployment must
#: supply these and this file is a deployment.
# `BUSIB` is FIVE letters -- a `{4}` quantifier here matched nothing at all
# and the pipeline looked broken when only the pattern was.
COURSE_CODE = re.compile(r"\b[A-Z]{2,5}\s?\d{3,4}\b")


def find_course_codes(text: str):
    from extractors.reading import StructuredString
    return tuple(StructuredString(kind="identifier", start=m.start(), end=m.end())
                 for m in COURSE_CODE.finditer(text))


@pytest.fixture()
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "Documents"
    root.mkdir()
    build_pdf(root / "syllabus.pdf")
    (root / "notes.md").write_text("BUSIB 4300 lecture notes\n", encoding="utf-8")
    return root


def go(db, corpus):                                          # noqa: F811
    from evidence_shape.store import RunWriter
    from extractors.safety import SafetyPolicy
    from scan_agent.exclusion import is_protected_container

    selection = record_selection(db, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return run_wave2(
        db, selection,
        source=FilesystemCorpusSource(),
        mime_type_for=lambda p: {".pdf": "application/pdf",
                                 ".md": "text/markdown"}.get(p.suffix),
        scan_state="scanned", budget_exhausted=lambda: False,
        detect_format=lambda p: p.suffix.lstrip(".") or None,
        policy=SafetyPolicy(is_protected_container=is_protected_container,
                            is_dataless=lambda path: False),
        readers=macos_readers(find_structured_strings=find_course_codes),
        sink=RunWriter(db, author="P5"),
        now=lambda: "2026-08-21T12:00:00+00:00", context_window=40,
        no_usable_facts=TARGETED_OCR_UNAVAILABLE,
        transcription_authorized=lambda: False,
        corpus_form="snapshot", policy_settings={},
        file_entry_body=lambda row: {"payload_ref": f"blobs/{row['content_hash']}"})


def test_a_real_pdf_produces_real_observations(db, corpus):
    """`BUSIB 4300` out of an actual PDF, through pdfminer, into P4's evidence table.

    This is the sentence the whole Wave-2 stack exists to make true, and until the
    reader socket had a library in it, nothing in the repository could produce it.
    """
    result = go(db, corpus)
    assert result.run_ids

    values = {row["raw_value"] for row in db.execute(
        "SELECT raw_value FROM evidence WHERE extractor_name = 'pdf.text'")}
    assert "BUSIB 4300" in values


def test_the_observation_carries_the_zone_the_library_reported(db, corpus):
    """§2.2: *"A course code or university name found in a filename, title, or
    page-one heading is more meaningful than the same text appearing once in a
    reference list on page eighteen."* That ranking is P6's to make and it is only
    possible because the reader reported which zone the value sat in."""
    import json

    go(db, corpus)
    zones = set()
    for row in db.execute(
            "SELECT location FROM evidence WHERE extractor_name = 'pdf.text'"):
        zones.add(json.loads(row["location"])["zone"])
    assert "heading" in zones, (
        f"the page-one heading was not reported as one; got {zones}")


def test_the_pdf_title_metadata_reaches_the_evidence_table(db, corpus):
    """§2.2 requires the title preserved, and §3.2 names "the PDF title" as evidence.
    The slot keeps the format's own name (P4 D7)."""
    go(db, corpus)
    values = {row["raw_value"] for row in db.execute("SELECT raw_value FROM evidence")}
    assert "BUSIB 4300 Syllabus" in values


def test_a_format_with_no_library_is_unsupported_not_failed(db, tmp_path):
    """§2.4's first half. No image library ships, so those bytes were never looked
    at; calling that `failed` would report a missing library as a corrupt document.

    This test used to make the same point with a `.docx`, and stopped being able
    to on 2026-08-29 when `python-docx` was wired: the premise "the deployment
    ships no DOCX reader" became false. It moved to a format that genuinely has no
    reader rather than being deleted -- the PROPERTY is the point and it still has
    to hold somewhere. Its twin below now covers what a `.docx` proves instead.
    """
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "scan.heic").write_bytes(b"\x00\x00\x00\x18ftypheic not really an image")

    go(db, root)
    states = {row["extractor_name"]: row["completeness"] for row in db.execute(
        "SELECT extractor_name, completeness FROM extraction_runs")}
    assert states.get("image.metadata") == "unsupported", states


def test_a_reader_that_ran_and_raised_is_failed_not_unsupported(db, tmp_path):
    """§2.4's other half, and the half that could not be reached until a DOCX
    reader existed: `failed` means a reader RAN and raised.

    The two states ask the user for different things -- one says "this product
    cannot open this kind of file", the other says "this file is damaged" -- and a
    deployment with no reader at all can only ever produce the first.
    """
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "letter.docx").write_bytes(b"PK\x03\x04 not really a docx")

    go(db, root)
    states = {row["extractor_name"]: row["completeness"] for row in db.execute(
        "SELECT extractor_name, completeness FROM extraction_runs")}
    assert states.get("docx.structure") == "failed", states


def test_a_real_docx_becomes_evidence_with_the_zone_word_recorded(db, tmp_path):
    """The sentence this reader exists to make true, on bytes Word itself wrote.

    `43`'s R2: the deployment wired `read_docx = _no_reader`, so every `.docx` on
    a person's disk recorded `unsupported` -- "no reader exists and the bytes were
    never looked at" -- and every count downstream agreed those files carried
    nothing. On a real human's disk that is most of the writing they have ever
    done.
    """
    import json

    docx_lib = pytest.importorskip("docx")
    root = tmp_path / "Documents"
    root.mkdir()
    document = docx_lib.Document()
    document.add_heading("BUSIB 4300 Syllabus", level=1)
    document.add_paragraph("Readings for the term.")
    document.save(root / "syllabus.docx")

    go(db, root)
    rows = [dict(row) for row in db.execute(
        "SELECT raw_value, location FROM evidence "
        "WHERE extractor_name = 'docx.structure'")]
    assert rows, "a real .docx produced no evidence at all"
    # Verbatim, not canonicalised: collapsing `BUSIB 4300` to one token is
    # `cli.py`'s DIRECT_SLOTS doing P6's work, and an extractor that did it here
    # would be interpreting what it saw.
    assert any(row["raw_value"] == "BUSIB 4300" for row in rows), (
        f"the course code in the heading never became evidence: "
        f"{[row['raw_value'] for row in rows]}")
    zones = {json.loads(row["location"])["zone"] for row in rows}
    assert "heading" in zones, (
        f"Word's own heading style was not reported as P4's heading zone; {zones}")


def test_every_run_is_complete_and_the_status_column_agrees(db, corpus):
    """The join that four separate defects hid this week: a real extraction must
    leave `files.extraction_status_by_tier` describing what actually happened."""
    import json

    from database_agent.files_table import get_file

    go(db, corpus)
    for row in db.execute("SELECT file_id, current_path FROM files"):
        status = json.loads(get_file(db, row["file_id"])["extraction_status_by_tier"])
        assert status.get("filesystem") == "complete", row["current_path"]
        assert "native" in status, f"{row['current_path']} never reached a native tier"


def test_the_bundle_carries_what_was_extracted(db, corpus):
    """§8.5's envelope, filled from a real run rather than a fixture."""
    from eval_harness.counts import bundle_counts

    result = go(db, corpus)
    counts = bundle_counts(db, result.bundle_id)
    assert counts["files_indexed"] == 2
    assert counts["files_with_any_run"] == 2
    payloads = db.execute(
        "SELECT count(*) AS n FROM bundle_extraction_output WHERE bundle_id = ?",
        (result.bundle_id,)).fetchone()["n"]
    assert payloads > 0


# `test_extractors_never_import_the_deployment_layer` used to live here. It globbed a
# RELATIVE `src/extractors` and sat behind the three `importorskip`s above, so it
# passed vacuously from any other cwd and on any machine without pdfminer or pyobjc --
# an `import readers.deployment` inside `src/extractors/` did not fail it. It now
# lives in `tests/p5/test_p5_one_definition.py`, which nothing skips, over a path
# derived from the imported package.


# ------------------------------------------------- the scanned PDF, end to end
def build_scanned_pdf(path: Path, text: str = "BUSIB 4300") -> Path:
    """A PDF whose page is an IMAGE of text — no text layer at all.

    Drawn with Quartz rather than hand-assembled, because a genuine scanned page is
    a raster embedded in a PDF and that is not something you can write by hand in a
    content stream. This is the file §2.2 means by *"a PDF with no extractable text
    and evidence of being created from a photographed page"*.
    """
    import Quartz
    from Foundation import NSURL

    width, height = 600, 200
    space = Quartz.CGColorSpaceCreateDeviceRGB()
    bitmap = Quartz.CGBitmapContextCreate(
        None, width, height, 8, 0, space, Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(bitmap, 1, 1, 1, 1)
    Quartz.CGContextFillRect(bitmap, Quartz.CGRectMake(0, 0, width, height))
    Quartz.CGContextSetRGBFillColor(bitmap, 0, 0, 0, 1)
    Quartz.CGContextSelectFont(bitmap, b"Helvetica", 64.0, Quartz.kCGEncodingMacRoman)
    raw = text.encode("mac-roman")
    Quartz.CGContextShowTextAtPoint(bitmap, 40.0, 80.0, raw, len(raw))
    image = Quartz.CGBitmapContextCreateImage(bitmap)

    media = Quartz.CGRectMake(0, 0, width, height)
    pdf = Quartz.CGPDFContextCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), media, None)
    Quartz.CGPDFContextBeginPage(pdf, {Quartz.kCGPDFContextMediaBox: media})
    Quartz.CGContextDrawImage(pdf, media, image)
    Quartz.CGPDFContextEndPage(pdf)
    Quartz.CGPDFContextClose(pdf)
    return path


def test_a_scanned_pdf_reaches_ocr_with_no_p6_in_the_loop(db, tmp_path):
    """§2.2: *"A file with no text should route directly to OCR."*

    That clause is a `should` and it needs no verdict from P6 — `text_layer_state`
    asks P6 only about a NON-EMPTY text layer, because a document with no text has
    no stored evidence P6 could have failed to make facts from. So the moment an
    engine is wired, scanned PDFs are read. This is the half of §2.2 that does not
    wait for the fact layer, and it is why D5 could cut the four-pass restructure
    without stranding scanned documents.
    """
    pytest.importorskip("Quartz")
    root = tmp_path / "Documents"
    root.mkdir()
    build_scanned_pdf(root / "scan.pdf")

    go(db, root)

    runs = {row["extractor_name"]: row["completeness"] for row in db.execute(
        "SELECT extractor_name, completeness FROM extraction_runs")}
    assert "ocr.apple_vision" in runs, (
        f"a PDF with no text layer never reached OCR; runs were {runs}")

    recognised = " ".join(row["raw_value"] for row in db.execute(
        "SELECT raw_value FROM evidence WHERE extractor_name = 'ocr.apple_vision'"))
    assert "BUSIB" in recognised, f"OCR ran but recognised {recognised!r}"


def test_the_scanned_pdf_keeps_both_runs_and_both_tiers(db, tmp_path):
    """§2.2 requires "no text layer" and "broken text layer" to stay
    distinguishable, and §8.5 requires evaluation decomposed by stage — so the
    native attempt and the OCR run are two rows, not one merged outcome."""
    import json

    from database_agent.files_table import get_file

    root = tmp_path / "Documents"
    root.mkdir()
    build_scanned_pdf(root / "scan.pdf")
    go(db, root)

    row = db.execute("SELECT file_id FROM files").fetchone()
    status = json.loads(get_file(db, row["file_id"])["extraction_status_by_tier"])
    assert set(status) >= {"filesystem", "native", "ocr"}, status


def test_a_real_vision_box_survives_to_a_parsed_p4_region(db, tmp_path):
    """§2.7's bounding box, engine to `Region`, with nothing stubbed.

    This is the round trip that had no test anywhere. The OCR extractor once emitted
    `width`/`height` against a P4 `Region` of `(x, y, w, h, unit)`; `location()` did
    not validate, `location_from_mapping` raised a bare `KeyError('w')` three layers
    later during a write, and `tests/p5/p4_stub.py` dropped the field entirely — so
    the one field §8.4 redacts against was the one field nothing round-tripped.
    """
    import json

    from evidence_shape.location import Region
    from evidence_shape.locator import location_from_mapping

    root = tmp_path / "Documents"
    root.mkdir()
    build_scanned_pdf(root / "scan.pdf")
    go(db, root)

    located = [json.loads(r["location"]) for r in db.execute(
        "SELECT location FROM evidence WHERE extractor_name = 'ocr.apple_vision'")]
    assert located, "OCR produced no observations to carry a box"

    boxed = [m for m in located if m["region"] is not None]
    assert boxed, "Vision reported bounding boxes and none reached the evidence row"

    for mapping in boxed:
        region = location_from_mapping(mapping).region
        assert isinstance(region, Region)
        assert region.unit == "norm"
        assert all(0.0 <= v <= 1.0 for v in (region.x, region.y, region.w, region.h))



# --------------------------------------------------------------------------- #
# §2.9's long tail, and §2.9's own sensitivity rule, over the same live path
# --------------------------------------------------------------------------- #

def test_a_real_csv_becomes_cell_evidence_addressed_by_row_and_column(db, tmp_path):
    """`read_long_tail` was `_no_reader`, so a spreadsheet recorded `unsupported` --
    "no reader exists and the bytes were never looked at" -- and every count
    downstream agreed the file carried nothing. §2.9 asks a spreadsheet for "column
    headers, visible cell values", and each value has to be ADDRESSED: P4's locator
    is what lets a fact cite the cell it came from rather than the file.
    """
    import json

    root = tmp_path / "Documents"
    root.mkdir()
    (root / "grades.csv").write_text("student_id,course,grade\nS1001,BUSIB 4300,A\n")

    go(db, root)
    rows = [dict(row) for row in db.execute(
        "SELECT raw_value, location FROM evidence "
        "WHERE source_type = 'spreadsheet' ORDER BY observation_key")]
    assert rows, "a real .csv produced no evidence at all"

    located = {row["raw_value"]: json.loads(row["location"]) for row in rows}
    assert "BUSIB 4300" in located, sorted(located)
    address = located["BUSIB 4300"]["container_path"]
    # `.get`, because the stored locator omits a null rather than spelling it: the
    # round trip through `evidence_shape.locator` is part of what is asserted here.
    assert [(segment["kind"], segment.get("index"), segment.get("label"))
            for segment in address] == [
        ("sheet", 1, None), ("row", 2, None), ("column", 2, "course")]


def test_a_spreadsheet_run_reports_the_sheets_it_processed(db, tmp_path):
    """§8.6 needs the difference between completed and deferred work legible, and
    `coverage` is where a run says it. This one used to read `{"processed": 0,
    "total": 1}` on every spreadsheet in every corpus."""
    import json

    root = tmp_path / "Documents"
    root.mkdir()
    (root / "grades.csv").write_text("course\nBUSIB 4300\n")

    go(db, root)
    row = db.execute("SELECT completeness, coverage FROM extraction_runs "
                     "WHERE source_type = 'spreadsheet'").fetchone()
    assert row["completeness"] == "complete"
    assert json.loads(row["coverage"]) == {"units": "entries", "processed": 1,
                                           "total": 1}


def test_every_value_of_a_contact_card_is_marked_potentially_sensitive(db, tmp_path):
    """§2.9, Contacts: address-book output "should normally be privacy-protected
    rather than used to create folder proposals."

    Reading `.vcf` files is new, and a new reader that made a person's address book
    readable WITHOUT its values arriving marked would be a privacy regression bought
    with an extraction win. The marking is `extract_long_tail`'s, the recording is
    the orchestrator's, and this asserts the whole chain over real bytes.
    """
    from extractors.long_tail import POTENTIALLY_SENSITIVE

    root = tmp_path / "Documents"
    root.mkdir()
    (root / "adviser.vcf").write_text(
        "BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Amara Chen\r\n"
        "ORG:Example University\r\nEMAIL:achen@example.edu\r\n"
        "TEL:+1-555-0142\r\nEND:VCARD\r\n")

    go(db, root)
    marked = {row["observation_key"] for row in db.execute(
        "SELECT observation_key FROM extraction_sensitivity_signal "
        "WHERE signal = ?", (POTENTIALLY_SENSITIVE,))}
    contact_keys = {row["observation_key"]: row["raw_value"] for row in db.execute(
        "SELECT observation_key, raw_value FROM evidence "
        "WHERE source_type = 'contacts'")}

    assert contact_keys, "a real .vcf produced no evidence at all"
    assert set(contact_keys) == marked, (
        "these contact values reached the evidence table unmarked: "
        f"{sorted(contact_keys[k] for k in set(contact_keys) - marked)}")


def test_a_contact_value_cannot_leave_as_an_excerpt(db, tmp_path):
    """The other end of the same chain: P7 refuses to release what P5 marked.

    `privacy.items.check_item` is the release-time gate, and this asserts the
    refusal on a key that a REAL `.vcf` produced through the shipped path -- not on
    a fixture key chosen to make the point.
    """
    from privacy.items import (
        AlwaysLocalRequested, Excerpt, check_item, sensitive_observation_keys,
    )

    root = tmp_path / "Documents"
    root.mkdir()
    (root / "adviser.vcf").write_text(
        "BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Amara Chen\r\n"
        "TEL:+1-555-0142\r\nEND:VCARD\r\n")

    go(db, root)
    row = db.execute("SELECT file_id, observation_key FROM evidence "
                     "WHERE raw_value = '+1-555-0142'").fetchone()
    assert row is not None, "the telephone number did not reach the evidence table"

    sensitive = sensitive_observation_keys(db, row["file_id"])
    with pytest.raises(AlwaysLocalRequested):
        check_item(
            Excerpt(observation_key=row["observation_key"], span=None,
                    reason="a folder proposal"),
            unit_length=None, zone="metadata", protected=False,
            sensitive_keys=sensitive, allow_unratified=False,
            suspension_permits_self_description=False)


def test_an_html_pages_script_body_never_reaches_the_evidence_table(db, tmp_path):
    """`read_text_document` decoded any text format as UTF-8 and returned the bytes,
    so a page's `<script>` contents were stored as the document's prose and read by
    the recogniser as if the author had written them. This is that defect, asserted
    where it would actually have shown: in the database, after a live run.
    """
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "registration.html").write_text(
        "<html><head><style>body { font-family: BUSIB; }</style>"
        '<script>var tracking = "BUSIB 9999";</script></head>'
        "<body><h1>BUSIB 4300</h1><p>You are enrolled.</p></body></html>")

    go(db, root)
    stored = "\n".join(row["text"] for row in db.execute("SELECT text FROM text_units"))
    values = {row["raw_value"] for row in db.execute("SELECT raw_value FROM evidence")}

    assert "tracking" not in stored
    assert "font-family" not in stored
    assert "BUSIB 9999" not in values, "a script literal was read as a course code"
    assert "BUSIB 4300" in values
