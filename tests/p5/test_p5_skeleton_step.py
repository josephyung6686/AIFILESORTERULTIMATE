# tests/p5/test_p5_skeleton_step.py
"""The walking skeleton's P5 step (02-segmentation-map.md):
P4/P5 extract page-one text; emit ONE observation in the frozen shape.

This test stays in the repository as the integration test every later part must keep
green. It is deterministic: no model, no cloud, no embeddings, no network.
"""
import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from extractors.events import EXTRACTION, append, extraction_event
from extractors.pdf import EXTRACTOR_NAME, PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region
from extractors.router import record_routing_decision, route, routing_decisions
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.shape import EXTRACTOR_RELIABILITY
from extractors.stage_output import STAGE_ID, extraction_stage_output

from conftest import FIXED_CLOCK
from p4_stub import locator_for, validate_observation, validate_run

PAGE_ONE = "BUSIB 4300 Syllabus\nSpring 2026. Meetings on Tuesdays."
HEADING = "BUSIB 4300 Syllabus"

OPEN_POLICY = SafetyPolicy(is_protected_container=lambda path: False,
                           is_dataless=lambda path: False)


def a_one_page_pdf(path: Path) -> PdfDocument:
    """No metadata slots and no structured strings, so the page yields exactly one
    located value: its heading."""
    return PdfDocument(
        metadata={},
        pages=(PdfPage(number=1, text=PAGE_ONE,
                       regions=(Region(zone="heading", start=0, end=len(HEADING),
                                       ordinal=1, label=HEADING),)),))


def test_skeleton_p5_step(conn, tmp_path: Path, sink):
    create_schema(conn)
    create_extraction_schema(conn)

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    document = corpus / "Syllabus BUSIB 4300 Spring 2026.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")

    # P1's real row, as P3 would have handed it over. `parent_folder_context` is
    # §2.9's name for the value P1 stores in `directory_position` (MINOR 11).
    file_id = record_file(
        conn, document, filename=document.name,
        normalized_filename=document.name.lower(), extension=".pdf",
        observed_size=document.stat().st_size,
        observed_timestamps=json.dumps({"mtime": 1.0}),
        parent_folder_context=str(corpus), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)
    file_row = dict(get_file(conn, file_id))
    assert file_row["directory_position"] == str(corpus)

    # R — §2.9 routes by signature, and the decision is recorded.
    decision = route(file_id=file_id, content_hash=file_row["content_hash"],
                     path=document, extension=".pdf",
                     detect_format=lambda target: "pdf")
    assert decision.extractor_name == EXTRACTOR_NAME
    assert decision.disagree is False
    record_routing_decision(conn, decision)
    assert len(routing_decisions(conn, file_id, file_row["content_hash"])) == 1

    # E1 — page-one text, and ONE observation in the frozen shape.
    result = extract_pdf(file_row=file_row, path=document, policy=OPEN_POLICY,
                         read_pdf=a_one_page_pdf,
                         find_structured_strings=lambda text: (), now=FIXED_CLOCK,
                         context_window=24)
    run_id = sink.write(result)

    observations = sink.observations_for(run_id)
    assert len(observations) == 1
    only = observations[0]
    assert only["raw_value"] == HEADING
    assert locator_for(only["location"]) == "heading:page=1/heading=1#0-19"
    assert only["reliability"] in EXTRACTOR_RELIABILITY
    assert only["file_id"] == file_id
    assert only["content_hash"] == file_row["content_hash"]

    # It validates against P4's frozen shape, through P4's own conformance rules.
    units = [{k: v for k, v in u.items() if k != "run_id"}
             for u in sink.units_for(run_id)]
    validate_observation({k: v for k, v in only.items() if k != "run_id"},
                         text_units=units)
    validate_run(sink.run_for(run_id), 1)

    # Page-one text is a `text_units` row, not an observation (G1).
    page = [u for u in units if u["container_path"]
            == ({"kind": "page", "index": 1, "label": None},)]
    assert page and page[0]["text"] == PAGE_ONE
    assert all(o["raw_value"] != PAGE_ONE for o in observations)

    # Deterministic: the native tier, no model, no network.
    row = sink.run_for(run_id)
    assert row["analysis_tier"] == "native"
    assert row["completeness"] == "complete"
    assert row["coverage"] == {"units": "pages", "processed": 1, "total": 1}

    # P5 authors the extraction event; P1 writes it (M8).
    append(conn, extraction_event(
        run_id=run_id, file_id=file_id, content_hash=file_row["content_hash"],
        extractor_name=row["extractor_name"],
        extractor_version=row["extractor_version"],
        completeness=row["completeness"], observed_at=FIXED_CLOCK))
    event = conn.execute("SELECT * FROM events WHERE event_type = ?",
                         (EXTRACTION,)).fetchone()
    assert event["subsystem"] == "P5"
    assert json.loads(event["explanation"])["run_id"] == run_id

    # And the run is measurable (§8.5, B7).
    envelope = extraction_stage_output(run=row)
    assert envelope["stage_id"] == STAGE_ID
    assert envelope["outcome"] == "produced"
    assert envelope["inputs"] == (file_row["content_hash"],)
