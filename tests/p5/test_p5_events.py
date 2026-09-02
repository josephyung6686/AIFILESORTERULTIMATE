# tests/p5/test_p5_events.py
"""§8.2 — the two events P5 authors, written by P4, once per run. MINOR 2: `OCR`.

`append` used to live in `extractors.events` and call P1's `append_event` directly,
so these tests drove P5's own writer. There is one writer now — the batch sink, which
appends the event after the rows it references exist — so they drive that instead.
The two builders below still have tests of their own: they are dicts, and what a dict
says is a different assertion from what the database holds.
"""
import json

import pytest

from database_agent.db import create_schema
from database_agent.events import (
    RESERVED_EVENT_TYPES, UnregisteredEventType, append_event,
)

from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter, get_run, observation_keys_for_run

from extractors.authorship import AUTHORED_EVENT_TYPES, SUBSYSTEM
from extractors.authorship import event_defaults
from extractors.events import EXTRACTION, OCR
from extractors.shape import fingerprint, location, observation, run, segment, text_unit
from extractors.sink import ExtractionResult

from conftest import FIXED_CLOCK

CONFIG = {"recognition": "accurate", "languages": ["en-US"], "dpi": 200}
CONTENT_HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
PAGE_ONE = "BUSIB 4300 Syllabus"
PAGE = (segment("page", index=1),)


@pytest.fixture()
def writer(conn):
    """The real sink. P5 names itself as the author (M8); P4 writes.

    Not called `sink`: conftest.py's `sink` is `RecordingSink`, and one name for two
    objects is the defect tests/p5/test_p5_join.py's agreement test exists to catch.
    """
    create_evidence_schema(conn)
    return RunWriter(conn, author=SUBSYSTEM)


def a_pdf_run(version="0.1.0"):
    """A native run carrying one located value, so the event has a key to reference."""
    return ExtractionResult(
        run=run(file_id="f-1", content_hash=CONTENT_HASH, extractor_name="pdf.text",
                extractor_version=version, source_type="text_document",
                analysis_tier="native", config={}, completeness="complete",
                coverage={"units": "pages", "processed": 1, "total": 1},
                observation_count=1, started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK),
        observations=(observation(
            file_id="f-1", content_hash=CONTENT_HASH, extractor_name="pdf.text",
            extractor_version=version, source_type="text_document",
            raw_value=PAGE_ONE,
            location=location(zone="heading", container_path=PAGE,
                              text_span={"start": 0, "end": len(PAGE_ONE)}),
            observed_at=FIXED_CLOCK, reliability="direct"),),
        text_units=(text_unit(text=PAGE_ONE, container_path=PAGE),))


def an_ocr_run():
    """§2.7's provider, version and configuration, on a run that was capped."""
    return ExtractionResult(
        run=run(file_id="f-1", content_hash=CONTENT_HASH,
                extractor_name="ocr.apple_vision", extractor_version="19.1",
                source_type="ocr", analysis_tier="ocr", config=CONFIG,
                completeness="capped",
                coverage={"units": "pages", "processed": 40, "total": 312},
                observation_count=0, started_at=FIXED_CLOCK, finished_at=FIXED_CLOCK))


def only_event(conn, **where):
    rows = conn.execute("SELECT * FROM events ORDER BY event_id").fetchall()
    for name, value in where.items():
        rows = [row for row in rows if row[name] == value]
    assert len(rows) == 1, f"expected one event, found {len(rows)}"
    return rows[0]


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


def test_an_extraction_event_round_trips_through_p1(conn, writer):
    writer.write(a_pdf_run())
    row = only_event(conn)
    assert row["event_type"] == "extraction"
    assert row["subsystem"] == "P5"
    assert row["file_id"] == "f-1"
    assert row["content_hash"] == CONTENT_HASH
    assert row["observed_at"] == FIXED_CLOCK


def test_section_8_2s_extractor_version_is_p1s_component_version(conn, writer):
    writer.write(a_pdf_run())
    assert only_event(conn)["component_version"] == "0.1.0"


def test_the_explanation_is_the_run_and_the_keys_of_its_observations(conn, writer):
    # It was P5's dict — extractor_name, completeness — built before any row existed.
    # SPEC, Provenance: the evidence reference is "`run_id` plus the
    # `observation_key`s", and P4 reads those out of the stored rows so the event and
    # the database cannot disagree. What the run was is on the run record (B1).
    run_id = writer.write(a_pdf_run())
    explanation = json.loads(only_event(conn)["explanation"])
    assert explanation["run_id"] == run_id
    assert explanation["observation_keys"] == observation_keys_for_run(conn, run_id)
    assert get_run(conn, run_id).extractor_name == "pdf.text"
    assert get_run(conn, run_id).completeness == "complete"


def test_an_ocr_run_appends_8_2s_OCR_event(conn, writer):
    writer.write(a_pdf_run())
    writer.write(an_ocr_run())
    assert only_event(conn, event_type=OCR)["component_version"] == "19.1"


def test_the_stored_ocr_event_carries_no_prompt_fingerprint(conn, writer):
    """P4's SPEC, Provenance: "`prompt fingerprint` does not apply (P4 is
    model-free)", and P4's own store test asserts the column is null on every run
    event. `ocr_event()` below fills it; the writer does not.

    Nothing is lost, and this records WHERE it went: §2.7's languages and recognition
    settings reach the database as the run's `config`, and their identity as its
    `config_fingerprint` — which is the same digest, on the record that owns it.
    """
    run_id = writer.write(an_ocr_run())
    row = only_event(conn, event_type=OCR)
    assert row["prompt_fingerprint"] is None
    stored = get_run(conn, run_id)
    assert stored.config == CONFIG
    assert stored.config_fingerprint == fingerprint(CONFIG)


# `an_ocr_event()`'s two builder-only cases are DELETED with `extractors.events.ocr_event`
# itself, 2026-09-02. They asserted that a dict the product never builds carries §8.2's
# model positions -- and the module header already recorded that `record_run_event`
# leaves `prompt_fingerprint` NULL, so the shape they described was not the shape the
# database produces. `test_the_stored_ocr_event_carries_no_prompt_fingerprint` above
# keeps the half that is true of a real row.


def test_every_event_names_p5(conn, writer):
    writer.write(a_pdf_run())
    writer.write(an_ocr_run())
    authors = conn.execute("SELECT DISTINCT subsystem FROM events").fetchall()
    assert [r["subsystem"] for r in authors] == ["P5"]


def test_p5_authors_none_of_p3s_events():
    # M8: `discovery`, `stat observation` and `hashing` are P3's. Asserted against
    # `event_defaults`, which is where the refusal has always lived and which the live
    # writer path reaches; `extraction_event` was a deleted wrapper around it.
    for event_type in ("discovery", "stat observation", "hashing", "planned move"):
        with pytest.raises(ValueError):
            event_defaults(event_type=event_type, file_id="f", content_hash="h",
                           component_version="0.1.0", observed_at=FIXED_CLOCK,
                           explanation='{"run_id": "r"}')


def test_exactly_one_event_per_run(conn, writer):
    # Done-means, and the reason `append` is gone: two writers meant two `extraction`
    # events for one run, or one whose explanation was P5's payload and not P4's keys.
    first = writer.write(a_pdf_run())
    second = writer.write(a_pdf_run(version="0.2.0"),
                        supersede_reason="pdf.text 0.2.0 re-read the heading")

    rows = conn.execute("SELECT * FROM events ORDER BY event_id").fetchall()
    assert [json.loads(r["explanation"])["run_id"] for r in rows] == [first, second]
    assert [r["component_version"] for r in rows] == ["0.1.0", "0.2.0"]


def test_a_second_run_appends_a_second_event_and_the_first_remains(conn, writer):
    # §8.2: P5 overwrites nothing. Supersession leaves both records readable.
    first = writer.write(a_pdf_run())
    second = writer.write(a_pdf_run(version="0.2.0"),
                        supersede_reason="a later pass")
    assert get_run(conn, first).extractor_version == "0.1.0"
    assert get_run(conn, second).extractor_version == "0.2.0"
    assert conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == 2
