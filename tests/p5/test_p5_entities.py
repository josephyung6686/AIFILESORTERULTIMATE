# tests/p5/test_p5_entities.py
"""`00` amendment 7(b)'s entity pass: the rows it writes and where they sit.

The reader is a stub throughout. What is under test is the contract at the top of
`extractors/entities.py` -- the names, the masking, the span arithmetic and the run
the readings ride on -- and none of that needs a model.
"""
from __future__ import annotations

import gc
import weakref
from dataclasses import dataclass

import pytest

from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import RunWriter, observations_for_file
from evidence_shape.text_units import check_span_anchor
from extractors.entities import (
    ENTITY_NAMESPACE, VERSION, entity_readings, extractor_name_for,
    is_entity_extractor, label_slug, record_entity_readings,
)
from extractors.shape import location, observation, run, text_unit
from extractors.runs import coverage
from extractors.sink import ExtractionResult

CONTENT_HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
CLOCK = "2026-09-12T12:00:00+00:00"
LATER = "2026-09-12T13:00:00+00:00"

BODY = ("Patient intake summary. Sarah Whitfield, born on 14 March 1987. "
        "Passport number N2938471 is on file.")

#: The deployment's, injected everywhere below exactly as `cli.py` injects them.
ZONES = ("filename", "title", "heading", "header_footer", "body", "table", "ocr")
MASKED = ("passport number", "phone number")
TAIL = 4


@dataclass(frozen=True)
class Found:
    """What the reader returns: `readers.entities_gliner.Entity`'s five fields."""
    label: str
    start: int
    end: int
    score: float
    text: str


def at(text: str, needle: str, label: str, score: float = 0.9) -> Found:
    start = text.index(needle)
    return Found(label=label, start=start, end=start + len(needle), score=score,
                 text=needle)


@pytest.fixture()
def database(conn):
    create_evidence_schema(conn)
    return conn


def a_text_run(*, body: str = BODY, file_id: str = "f1",
               content_hash: str = CONTENT_HASH) -> ExtractionResult:
    """One `text.structured` run in the shape E3 emits for a short document: one
    unit at the empty path and one span-less `body` reading over the whole of it."""
    file_row = {"file_id": file_id, "content_hash": content_hash}
    return ExtractionResult(
        run=run(file_id=file_id, content_hash=content_hash,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", analysis_tier="native",
                config={"reader": "fixture"}, completeness="complete",
                coverage=coverage("files", 1, 1), observation_count=1,
                started_at=CLOCK, finished_at=CLOCK),
        observations=(observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="text.structured", extractor_version="0.4.0",
            source_type="text_document", raw_value=body,
            location=location(zone="body"), observed_at=CLOCK,
            reliability="possible"),),
        text_units=(text_unit(text=body),))


def entity_rows(conn, file_id="f1"):
    return [one for one in observations_for_file(conn, file_id)
            if is_entity_extractor(one.extractor_name)]


# --- the names ----------------------------------------------------------------

def test_every_label_becomes_one_name_in_one_namespace():
    assert extractor_name_for("person") == "entities.person"
    assert extractor_name_for("date of birth") == "entities.date_of_birth"
    assert extractor_name_for("identity document number") == \
        "entities.identity_document_number"
    # The deployment spells the model's own label; the slug is the repo's.
    assert extractor_name_for("organization") == "entities.organization"
    assert all(is_entity_extractor(extractor_name_for(label))
               for label in ("person", "e-mail address", "Phone Number"))
    assert not is_entity_extractor("text.structured")
    assert ENTITY_NAMESPACE == "entities."


def test_a_label_that_slugs_to_nothing_is_refused_rather_than_named_blank():
    with pytest.raises(ValueError):
        label_slug("   ///   ")


# --- the rows -----------------------------------------------------------------

def test_a_person_is_recorded_whole_and_the_span_is_the_person(database):
    RunWriter(database, author="P5").write(a_text_run())
    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)],
        entities=lambda text: [at(text, "Sarah Whitfield", "person")],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)

    rows = entity_rows(database)
    assert len(rows) == 1
    reading = rows[0]
    assert reading.extractor_name == "entities.person"
    assert reading.extractor_version == VERSION
    assert reading.raw_value == "Sarah Whitfield"
    assert BODY[reading.location.text_span.start:
                reading.location.text_span.end] == "Sarah Whitfield"
    assert reading.confidence == pytest.approx(0.9)
    assert reading.reliability == "possible"
    assert reading.observed_at == LATER


def test_a_number_is_recorded_as_a_tail_and_the_rest_is_written_nowhere(database):
    RunWriter(database, author="P5").write(a_text_run())
    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)],
        entities=lambda text: [at(text, "N2938471", "passport number")],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)

    reading, = entity_rows(database)
    assert reading.extractor_name == "entities.passport_number"
    assert reading.raw_value == "8471"
    # THE SPAN IS NARROWED TO WHAT WAS KEPT, which is what lets RAW-1 hold.
    span = reading.location.text_span
    assert BODY[span.start:span.end] == "8471"
    # And the characters this pass declined to record are nowhere on the row.
    assert reading.normalized_value is None
    assert reading.context_before is None and reading.context_after is None
    row = database.execute(
        "SELECT * FROM evidence WHERE observation_key = ?",
        (reading.observation_key,)).fetchone()
    assert "N293" not in "".join(str(value) for value in tuple(row))


def test_a_number_no_longer_than_the_tail_is_recorded_whole_and_still_says_it_is_there():
    """Dropping it would lose the one thing the gate's rule needs -- that a number of
    that kind is present -- and its tail IS the whole of it."""
    host = a_text_run().observations[0]
    from evidence_shape.observation import observation_from_mapping
    record = observation_from_mapping({**host, "run_id": "r1"})
    minted, = entity_readings(record, [Found("phone number", 0, 3, 0.9, "911")],
                              now=LATER, masked_labels=MASKED, tail_kept=TAIL)
    assert minted.raw_value == "911"
    assert (minted.location.text_span.start, minted.location.text_span.end) == (0, 3)


def test_every_reading_satisfies_rule_10_against_the_unit_it_spans(database):
    """The contract's central claim, asserted with P4's own checker rather than with
    arithmetic that repeats the pass's."""
    from evidence_shape.store import text_units_for_run

    RunWriter(database, author="P5").write(a_text_run())
    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)],
        entities=lambda text: [at(text, "Sarah Whitfield", "person"),
                               at(text, "14 March 1987", "date of birth"),
                               at(text, "N2938471", "passport number")],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)

    rows = entity_rows(database)
    assert len(rows) == 3
    for reading in rows:
        unit, = [one for one in text_units_for_run(database, reading.run_id)
                 if one.unit_locator == ""]
        check_span_anchor(reading, unit)          # raises if RAW-1 or rule 10 fails


def test_the_readings_ride_on_the_hosts_own_run_and_inherit_its_tier(database):
    from facts.evidence import analysis_tier_for_observation

    host_run = RunWriter(database, author="P5").write(a_text_run())
    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)],
        entities=lambda text: [at(text, "Sarah Whitfield", "person")],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)

    reading, = entity_rows(database)
    assert reading.run_id == host_run
    assert reading.source_type == "text_document"
    assert reading.zone == "body"
    # No second run row: the pass mints readings, never runs.
    assert database.execute("SELECT count(*) FROM extraction_runs").fetchone()[0] == 1
    assert analysis_tier_for_observation(database, reading) == "native"


def test_the_pass_writes_nothing_twice_over_an_unchanged_corpus(database):
    RunWriter(database, author="P5").write(a_text_run())
    once = record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)],
        entities=lambda text: [at(text, "Sarah Whitfield", "person")],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)
    twice = record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)],
        entities=lambda text: [at(text, "Sarah Whitfield", "person")],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now="2026-09-13T09:00:00+00:00")
    assert len(once) == 1 and twice == ()
    assert len(entity_rows(database)) == 1


def test_its_own_readings_are_never_read_back_as_text_to_read(database):
    """A `entities.person` row is a reading of a name, not a unit of the document.
    Offering it to the model on the next pass would ask what a name is a name of."""
    RunWriter(database, author="P5").write(a_text_run())
    seen: list[str] = []

    def reader(text):
        seen.append(text)
        return [at(text, "Sarah Whitfield", "person")] if "Patient" in text else []

    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)], entities=reader,
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)
    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)], entities=reader,
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)
    assert seen == [BODY, BODY]


# --- what the model is shown ---------------------------------------------------

def test_the_character_budget_is_spent_and_the_model_sees_no_more(database):
    RunWriter(database, author="P5").write(a_text_run())
    seen: list[str] = []
    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)],
        entities=lambda text: seen.append(text) or [],
        zones=ZONES, char_budget=30, masked_labels=MASKED, tail_kept=TAIL, now=LATER)
    assert seen == [BODY[:30]]


def test_a_reading_with_no_unit_at_its_path_is_not_read(database):
    """A span-less reading with no unit standing at its path -- §2.8's EXIF field,
    E3's `language` marker -- would give a minted span nothing to anchor to. The
    zone here is one the budget spends on, so it is the UNIT rule doing the work."""
    RunWriter(database, author="P5").write(ExtractionResult(
        run=run(file_id="f2", content_hash=CONTENT_HASH,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", analysis_tier="native",
                config={}, completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=1, started_at=CLOCK, finished_at=CLOCK),
        observations=(observation(
            file_id="f2", content_hash=CONTENT_HASH,
            extractor_name="text.structured", extractor_version="0.4.0",
            source_type="text_document", raw_value="Sarah Whitfield wrote this",
            location=location(zone="body",
                              container_path=({"kind": "paragraph", "index": 1},)),
            observed_at=CLOCK, reliability="possible"),),
        text_units=()))
    seen: list[str] = []
    record_entity_readings(
        database, file_versions=[("f2", CONTENT_HASH)],
        entities=lambda text: seen.append(text) or [],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)
    assert seen == []
    assert entity_rows(database, "f2") == []


def test_a_reading_that_is_only_part_of_its_unit_is_not_read(database):
    """A span-less reading shorter than the unit at its own path is not the whole of
    it, so an offset into its value is an offset into something else."""
    RunWriter(database, author="P5").write(ExtractionResult(
        run=run(file_id="f3", content_hash=CONTENT_HASH,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", analysis_tier="native",
                config={}, completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=1, started_at=CLOCK, finished_at=CLOCK),
        observations=(observation(
            file_id="f3", content_hash=CONTENT_HASH,
            extractor_name="text.structured", extractor_version="0.4.0",
            source_type="text_document", raw_value="Sarah Whitfield",
            location=location(zone="body"), observed_at=CLOCK,
            reliability="possible"),),
        text_units=(text_unit(text="Signed: Sarah Whitfield, 1987"),)))
    seen: list[str] = []
    record_entity_readings(
        database, file_versions=[("f3", CONTENT_HASH)],
        entities=lambda text: seen.append(text) or [],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)
    assert seen == []
    assert entity_rows(database, "f3") == []


def test_the_budget_is_spent_across_units_in_the_zones_own_order(database):
    """Zone order is spend order, so a truncation keeps the half of a document that
    says what it is -- `recognition.semantic.evidence_text`'s rule, applied here."""
    heading, body = "Riverside Community Health Center", "Sarah Whitfield, 1987."
    RunWriter(database, author="P5").write(ExtractionResult(
        run=run(file_id="f4", content_hash=CONTENT_HASH,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", analysis_tier="native",
                config={}, completeness="complete", coverage=coverage("files", 1, 2),
                observation_count=2, started_at=CLOCK, finished_at=CLOCK),
        observations=(
            observation(
                file_id="f4", content_hash=CONTENT_HASH,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", raw_value=body,
                location=location(zone="body",
                                  container_path=({"kind": "paragraph", "index": 1},)),
                observed_at=CLOCK, reliability="possible"),
            observation(
                file_id="f4", content_hash=CONTENT_HASH,
                extractor_name="text.structured", extractor_version="0.4.0",
                source_type="text_document", raw_value=heading,
                location=location(zone="heading",
                                  container_path=({"kind": "heading", "index": 1},)),
                observed_at=CLOCK, reliability="possible"),
        ),
        text_units=(
            text_unit(text=body, container_path=({"kind": "paragraph", "index": 1},)),
            text_unit(text=heading, container_path=({"kind": "heading", "index": 1},)),
        )))
    seen: list[str] = []
    record_entity_readings(
        database, file_versions=[("f4", CONTENT_HASH)],
        entities=lambda text: seen.append(text) or [],
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)
    # `heading` outranks `body` in the deployment's list, whatever order P4 wrote them.
    assert seen == [heading, body]

    spent: list[str] = []
    record_entity_readings(
        database, file_versions=[("f4", CONTENT_HASH)],
        entities=lambda text: spent.append(text) or [],
        zones=ZONES, char_budget=len(heading) + 5, masked_labels=MASKED,
        tail_kept=TAIL, now=LATER)
    assert spent == [heading, body[:5]]


# --- the session is a phase ----------------------------------------------------

def test_the_pass_keeps_no_reference_to_the_reader_it_was_handed(database):
    """`104` §18.56: the fp32 session holds 2.36 GB and the local language model
    wants the machine. The pass may not be the reason it stays resident."""
    RunWriter(database, author="P5").write(a_text_run())

    class Reader:
        def entities(self, text):
            return [at(text, "Sarah Whitfield", "person")]

    reader = Reader()
    watch = weakref.ref(reader)
    record_entity_readings(
        database, file_versions=[("f1", CONTENT_HASH)], entities=reader.entities,
        zones=ZONES, char_budget=1_000, masked_labels=MASKED, tail_kept=TAIL,
        now=LATER)
    assert len(entity_rows(database)) == 1
    del reader
    gc.collect()
    assert watch() is None, "something in the pass is still holding the session"


# --- registration ---------------------------------------------------------------

def test_the_pass_is_not_a_routed_family_and_says_so_where_that_is_read():
    """`current_versions()` is what a caller reads to call a run stale. The entity
    pass mints no run, so an entry there would be a second and staler home for a
    version the readings already carry -- and the absence is DOCUMENTED, the way
    OCR's is, rather than left for someone to fix by adding one."""
    import inspect

    from extractors.dispatch import current_versions

    assert not any(is_entity_extractor(name) for name in current_versions())
    reason = inspect.getdoc(current_versions)
    assert "entities." in reason and "DELIBERATELY ABSENT" in reason


def test_an_entity_reading_is_evidence_and_not_a_derived_copy():
    """`derived.` is for an addressable COPY of text an earlier pass stored, which
    "says nothing new about what the file it was cut from IS". A reading that says a
    span is a person says something new, and the rule that reads these must see it."""
    from evidence_shape.store import is_derived_extractor

    assert not is_derived_extractor(extractor_name_for("person"))
