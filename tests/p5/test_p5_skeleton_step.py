# tests/p5/test_p5_skeleton_step.py
"""The walking skeleton's P5 step (02-segmentation-map.md):
P4/P5 extract page-one text; emit ONE observation in the frozen shape.

This test stays in the repository as the integration test every later part must keep
green. It is deterministic: no model, no cloud, no embeddings, no network.

It writes through P4's REAL sink now, not conftest.py's `RecordingSink`. A walking
skeleton that stops at a list of dicts is the gap the 2026-08-21 stress test named:
the suite was comprehensive about SHAPE and never about the JOIN, and P5's own event
writer was what made the stop necessary. Every assertion below is the one that was
here; each reads P4's stored rows instead of the double's lists, and the event is no
longer appended by this test -- the sink appends it, once, at the end of the batch.
"""
import json
from pathlib import Path

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file

from evidence_shape.conformance import validate_run
from evidence_shape.location import Segment
from evidence_shape.runs import Coverage
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import (
    RunWriter, get_run, observations_for_run, text_unit_at, text_units_for_run,
)

from extractors.authorship import SUBSYSTEM
from extractors.events import EXTRACTION
from extractors.pdf import EXTRACTOR_NAME, PdfDocument, PdfPage, extract_pdf
from extractors.reading import Region
from extractors.router import record_routing_decision, route, routing_decisions
from extractors.safety import SafetyPolicy
from extractors.schema import create_extraction_schema
from extractors.shape import EXTRACTOR_RELIABILITY
from extractors.stage_output import STAGE_ID, extraction_stage_output

from conftest import FIXED_CLOCK

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


def test_skeleton_p5_step(conn, tmp_path: Path):
    create_schema(conn)
    create_extraction_schema(conn)
    create_evidence_schema(conn)

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
    # P5 authors; P4 writes. The batch is one transaction: run row, text units,
    # observations, then the one §8.2 event (M8).
    run_id = RunWriter(conn, author=SUBSYSTEM).write(result)

    observations = observations_for_run(conn, run_id)
    # TWO, and the second one is §2.4's prose-as-evidence: E1 now emits the page's
    # own text addressed `body:page=1`, span-less, so the recogniser can read the
    # document. It used to emit the heading alone, and this assertion said `== 1`.
    # The ADDRESSABLE observation is still exactly one -- a locator becomes claimable
    # by carrying a `#`, which it gets from a span, and the prose carries none.
    addressable = [o for o in observations if "#" in o.locator]
    assert len(addressable) == 1, [o.locator for o in observations]
    only = addressable[0]
    assert only.raw_value == HEADING
    assert only.locator == "heading:page=1/heading=1#0-19"
    assert only.reliability in EXTRACTOR_RELIABILITY
    assert only.file_id == file_id
    assert only.content_hash == file_row["content_hash"]

    prose = [o for o in observations if "#" not in o.locator]
    assert [o.locator for o in prose] == ["body:page=1"], [o.locator for o in prose]

    # It validates against P4's frozen shape, through P4's own conformance rules.
    # This was `p4_stub.validate_observation` + `validate_run` over the double's
    # dicts; P4's `validate_run` over the stored records is the same rules and more
    # of them -- rules 5, 9 and 10 need the whole set, which is what a run has.
    stored = get_run(conn, run_id)
    units = text_units_for_run(conn, run_id)
    validate_run(stored, observations, units)     # raises NonConforming, or returns
    # The stub's `validate_run(run, 1)` asserted this and P4's rules do not: the count
    # is DERIVED from the rows by `record_observation`, and a stored count that
    # disagrees with them is a fact nobody downstream can use.
    assert stored.observation_count == 2

    # Page-one text is a `text_units` row AND, since §2.4's prose-as-evidence
    # reached E1, a span-less `body:page=1` observation beside it. The unit is what
    # a citation resolves against; the observation is what the recogniser can read.
    page = text_unit_at(conn, run_id, (Segment("page", 1),))
    assert page is not None and page.text == PAGE_ONE
    # G1, narrowed: the page's text is never an ADDRESSABLE value. It is evidence
    # the recogniser can read, and it is not something a locator can be claimed on.
    assert all(o.raw_value != PAGE_ONE or "#" not in o.locator for o in observations)

    # Deterministic: the native tier, no model, no network.
    assert stored.analysis_tier == "native"
    assert stored.completeness == "complete"
    assert stored.coverage == Coverage("pages", 1, 1)

    # Exactly one §8.2 event, and the sink wrote it -- nothing here appended one.
    events = conn.execute("SELECT * FROM events WHERE event_type = ?",
                          (EXTRACTION,)).fetchall()
    assert len(events) == 1
    assert events[0]["subsystem"] == "P5"
    assert json.loads(events[0]["explanation"])["run_id"] == run_id

    # And the run is measurable (§8.5, B7).
    envelope = extraction_stage_output(run=stored.to_mapping())
    assert envelope["stage_id"] == STAGE_ID
    assert envelope["outcome"] == "produced"
    assert envelope["inputs"] == (file_row["content_hash"],)
