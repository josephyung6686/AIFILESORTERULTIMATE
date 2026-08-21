# tests/readers/test_readers_end_to_end.py
"""The whole Wave-2 path over a real PDF, with real libraries. No fixture readers.

Every other test of `run_wave2` injects a deterministic fake reader, which proves the
JOIN and says nothing about whether a real library can actually fill the shape. This
is the one that opens a file.
"""
import re
from pathlib import Path

import pytest

pytest.importorskip("pdfminer", reason="pdfminer.six is an optional `readers` extra")

from evidence_shape.store import observations_for_run
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
