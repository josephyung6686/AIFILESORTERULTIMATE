# tests/p5/test_p5_events.py
"""§8.2 — the two events P5 authors, written by P1. MINOR 2: `OCR`, not `ocr`."""
import json

import pytest

from database_agent.db import create_schema
from database_agent.events import (
    RESERVED_EVENT_TYPES, UnregisteredEventType, append_event,
)

from extractors.authorship import AUTHORED_EVENT_TYPES, SUBSYSTEM
from extractors.events import EXTRACTION, OCR, append, extraction_event, ocr_event
from extractors.shape import fingerprint

from conftest import FIXED_CLOCK

CONFIG = {"recognition": "accurate", "languages": ["en-US"], "dpi": 200}


def an_extraction_event():
    return extraction_event(run_id="run-7", file_id="f-1",
                            content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name="pdf.text",
                            extractor_version="0.1.0", completeness="complete",
                            observed_at=FIXED_CLOCK)


def an_ocr_event():
    return ocr_event(run_id="run-8", file_id="f-1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
                     provider="apple-vision", provider_version="19.1",
                     config=CONFIG, completeness="capped",
                     observed_at=FIXED_CLOCK)


def test_both_types_are_reserved_section_8_2_names_and_p5_registers_nothing():
    assert EXTRACTION in RESERVED_EVENT_TYPES
    assert OCR in RESERVED_EVENT_TYPES
    assert AUTHORED_EVENT_TYPES == (EXTRACTION, OCR)


def test_minor_2_p1_accepts_OCR_and_rejects_ocr(conn):
    create_schema(conn)
    assert OCR == "OCR"
    append_event(conn, event_type=OCR, subsystem=SUBSYSTEM,
                 component_version="19.1", observed_at=FIXED_CLOCK,
                 explanation="{}")
    with pytest.raises(UnregisteredEventType):
        append_event(conn, event_type="ocr", subsystem=SUBSYSTEM,
                     component_version="19.1", observed_at=FIXED_CLOCK,
                     explanation="{}")


def test_an_extraction_event_round_trips_through_p1(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row["event_type"] == "extraction"
    assert row["subsystem"] == "P5"
    assert row["file_id"] == "f-1"
    assert row["content_hash"] == "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
    assert row["observed_at"] == FIXED_CLOCK


def test_section_8_2s_extractor_version_is_p1s_component_version(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    row = conn.execute("SELECT * FROM events").fetchone()
    assert row["component_version"] == "0.1.0"


def test_the_explanation_is_structured_and_names_the_run(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    row = conn.execute("SELECT * FROM events").fetchone()
    explanation = json.loads(row["explanation"])
    assert explanation["run_id"] == "run-7"
    assert explanation["extractor_name"] == "pdf.text"
    assert explanation["completeness"] == "complete"


def test_an_ocr_event_puts_version_and_configuration_in_section_8_2s_model_slots(conn):
    create_schema(conn)
    append(conn, an_ocr_event())
    row = conn.execute("SELECT * FROM events WHERE event_type = ?", (OCR,)).fetchone()
    assert row["component_version"] == "19.1"
    assert row["prompt_fingerprint"] == fingerprint(CONFIG)
    explanation = json.loads(row["explanation"])
    assert explanation["provider"] == "apple-vision"
    assert explanation["run_id"] == "run-8"
    assert explanation["completeness"] == "capped"


def test_one_configuration_has_one_identity_in_both_places():
    # The event's `prompt_fingerprint` and P4's `config_fingerprint` are the same
    # function of the same mapping, so an audit can join them.
    assert an_ocr_event()["prompt_fingerprint"] == fingerprint(CONFIG)


def test_every_event_names_p5(conn):
    create_schema(conn)
    append(conn, an_extraction_event())
    append(conn, an_ocr_event())
    authors = conn.execute("SELECT DISTINCT subsystem FROM events").fetchall()
    assert [r["subsystem"] for r in authors] == ["P5"]


def test_p5_authors_none_of_p3s_events():
    # M8: `discovery`, `stat observation` and `hashing` are P3's.
    for event_type in ("discovery", "stat observation", "hashing", "planned move"):
        with pytest.raises(ValueError):
            extraction_event(run_id="r", file_id="f", content_hash="h",
                             extractor_name="pdf.text", extractor_version="0.1.0",
                             completeness="complete", observed_at=FIXED_CLOCK,
                             event_type=event_type)


def test_a_second_run_appends_a_second_event_and_the_first_remains(conn):
    # §8.2: P5 overwrites nothing. Supersession leaves both records readable.
    create_schema(conn)
    append(conn, an_extraction_event())
    append(conn, extraction_event(
        run_id="run-9", file_id="f-1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
        extractor_name="pdf.text", extractor_version="0.2.0",
        completeness="complete", observed_at=FIXED_CLOCK))
    rows = conn.execute("SELECT * FROM events ORDER BY event_id").fetchall()
    assert [json.loads(r["explanation"])["run_id"] for r in rows] == ["run-7", "run-9"]
    assert [r["component_version"] for r in rows] == ["0.1.0", "0.2.0"]
