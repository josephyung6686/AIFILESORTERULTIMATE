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
    """The deployment ships no DOCX reader. §2.4 says that file is `unsupported`;
    calling it `failed` would report a missing library as a corrupt document."""
    root = tmp_path / "Documents"
    root.mkdir()
    (root / "letter.docx").write_bytes(b"PK\x03\x04 not really a docx")

    go(db, root)
    states = {row["extractor_name"]: row["completeness"] for row in db.execute(
        "SELECT extractor_name, completeness FROM extraction_runs")}
    assert states.get("docx.structure") == "unsupported", states


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


def test_extractors_never_import_the_deployment_layer():
    """The direction that keeps P5 stdlib-only.

    `src/readers/` depends on `src/extractors/` for the shapes it fills; the reverse
    would put pdfminer and pyobjc inside a part whose SPEC says it *"adds no
    third-party runtime dependency"*, and every P5 test would start needing a PDF
    library installed.
    """
    import ast

    offenders = []
    for module in sorted(Path("src/extractors").glob("*.py")):
        tree = ast.parse(module.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                    ("readers", "pdfminer", "Vision", "Quartz")):
                offenders.append(f"{module.name}: from {node.module}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in {
                            "readers", "pdfminer", "Vision", "Quartz", "objc"}:
                        offenders.append(f"{module.name}: import {alias.name}")
    assert not offenders, offenders


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
