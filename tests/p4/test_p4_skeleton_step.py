# tests/p4/test_p4_skeleton_step.py
"""The walking skeleton's P4 step (02-segmentation-map.md):
"P4/P5 extract page-one text; emit ONE observation in the frozen shape."

P5 does the extracting. P4's half is the frozen shape: one observation, the run that
scoped it, and the page-one text it was read out of, all conforming, stored, and read
back as what was emitted -- with no extractor in existence.

This test stays in the repository as the integration test every later part must keep
green. It is deterministic: no model, no cloud, no embeddings, no network.
"""
import json
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.files_table import get_file, observe_path

from evidence_shape.authorship import UnauthoredEvent
from evidence_shape.canonical import canonical_json
from evidence_shape.conformance import validate_run
from evidence_shape.determinism import observation_set_digest
from evidence_shape.fixtures import by_number
from evidence_shape.location import Segment
from evidence_shape.store import (
    get_run, observations_by_key, observations_for_run, record_observation,
    record_run, record_run_event, record_text_unit, text_unit_at,
)
from evidence_shape.text_units import TextUnit

#: The page the skeleton extracts. It carries the value three times, which is what
#: fixture 1's occurrence_count says, and the context §3.5's term lives in.
PAGE_ONE = (
    "BUSIB 4300 Syllabus\n"
    "Course Information\n"
    "Syllabus — BUSIB 4300 — Spring 2026\n"
    "Instructor office hours are by appointment.\n"
    "Questions about BUSIB 4300 go to the teaching assistant.\n"
)

SKELETON_RUN = "skeleton-run"
PAGE_ONE_PATH = (Segment("page", 1),)


def _file_row(conn, tmp_path: Path) -> tuple[str, str]:
    """P3's half of the seam, as a fixture: one `files` row, authored by P3.

    P4 touches `observe_path` here and nowhere else in this plan -- its records are
    testable without a file row, which is what lets P6 be built against the fixtures.
    """
    document = tmp_path / "corpus" / "syllabus-fixture.pdf"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(PAGE_ONE, encoding="utf-8")
    stat = document.stat()
    file_id = observe_path(
        conn, document, author="P3", component_version="p3-skeleton-fixture",
        filename=document.name, normalized_filename=document.name,
        extension=document.suffix, observed_size=stat.st_size,
        observed_timestamps=json.dumps({"modified": stat.st_mtime}),
        parent_folder_context=str(document.parent), mime_type="application/pdf",
        detected_format="pdf", scan_state="fixture-scan-state", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def test_skeleton_p4_step(p4_conn, tmp_path: Path):
    file_id, content_hash = _file_row(p4_conn, tmp_path)

    # ── the frozen shape, rebuilt on the real identity P1 resolved ────────────
    template = by_number(1)
    run = replace(template.run, run_id=SKELETON_RUN, file_id=file_id,
                  content_hash=content_hash)
    observation = replace(template.observations[0], file_id=file_id,
                          content_hash=content_hash, run_id=SKELETON_RUN)
    unit = TextUnit(run_id=SKELETON_RUN, container_path=PAGE_ONE_PATH, text=PAGE_ONE)

    # ── the gate six extractor authors run, before anything is written ────────
    assert validate_run(run, [observation], [unit]) is run

    record_run(p4_conn, run)
    record_text_unit(p4_conn, unit)
    record_observation(p4_conn, observation)
    record_run_event(p4_conn, SKELETON_RUN, author="P5")

    # ── ONE observation, in the frozen shape ──────────────────────────────────
    assert p4_conn.execute("SELECT count(*) FROM evidence").fetchone()[0] == 1
    stored, = observations_for_run(p4_conn, SKELETON_RUN)
    assert stored == observation
    assert stored.locator == "heading:page=1/heading=2"
    assert stored.zone == "heading"
    assert stored.raw_value == "BUSIB 4300"
    assert stored.source_type == "text_document"
    assert stored.reliability == "possible"
    assert stored.occurrence_count == PAGE_ONE.count("BUSIB 4300") == 3
    assert stored.context_before == "Syllabus — "
    assert stored.context_after == " — Spring 2026"
    assert stored.context_truncated is False
    assert stored.signal_tier is None

    # Fixture 1's golden locator carries no span, so rule 10 is vacuous here: the
    # page-one unit exists because §2.2 requires complete text by page, not because a
    # span forced it.
    assert stored.location.text_span is None

    # ── the citation handle resolves, and it is the KEY, never the row id ─────
    assert observations_by_key(p4_conn, stored.observation_key) == [stored]
    assert stored.observation_key.startswith("sha256:")

    # ── the page-one text is stored and readable, and the value is in it ──────
    page = text_unit_at(p4_conn, SKELETON_RUN, PAGE_ONE_PATH)
    assert page.text == PAGE_ONE
    assert page.length == len(PAGE_ONE)
    assert page.truncated is False
    assert stored.raw_value in page.text

    # ── the run says what happened, including the count ───────────────────────
    recorded = get_run(p4_conn, SKELETON_RUN)
    assert recorded.completeness == "complete"
    assert recorded.analysis_tier == "native"
    assert recorded.observation_count == 1
    assert recorded.config_fingerprint == run.config_fingerprint

    # ── rule 8: what was stored is byte-identical to what was emitted ─────────
    assert (observation_set_digest([stored])
            == observation_set_digest([observation]))

    # ── the one §8.2 event, authored by the acting part (M8) ──────────────────
    events = p4_conn.execute(
        "SELECT * FROM events WHERE event_type = 'extraction'").fetchall()
    assert len(events) == 1
    event = events[0]
    assert event["subsystem"] == "P5"
    assert event["component_version"] == run.extractor_version
    assert event["file_id"] == file_id
    assert event["content_hash"] == content_hash
    # §8.2's "structured explanation or evidence reference": run_id plus the KEYS.
    assert event["explanation"] == canonical_json(
        {"run_id": SKELETON_RUN, "observation_keys": [stored.observation_key]})
    assert "observation_id" not in event["explanation"]

    # ── nobody named P4, and nobody named P1 ──────────────────────────────────
    authors = {row["subsystem"] for row in p4_conn.execute(
        "SELECT DISTINCT subsystem FROM events")}
    assert authors == {"P3", "P5"}
    assert "P4" not in authors
    assert "P1" not in authors


def test_the_skeleton_run_event_refuses_p1_as_its_author(p4_conn, tmp_path: Path):
    # M8: "P1 appends no event on its own initiative." A log whose subsystem names
    # the storage substrate cannot reconstruct what happened, which is §8.2's point.
    file_id, content_hash = _file_row(p4_conn, tmp_path)
    template = by_number(1)
    record_run(p4_conn, replace(template.run, run_id=SKELETON_RUN, file_id=file_id,
                                content_hash=content_hash))
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, SKELETON_RUN, author="P1")
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, SKELETON_RUN, author="")
