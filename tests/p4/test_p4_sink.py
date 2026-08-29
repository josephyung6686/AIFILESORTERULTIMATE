# tests/p4/test_p4_sink.py
"""The batch writer -- P5's `EvidenceSink` Protocol, implemented over P4's tables.

`store.py` had three separate inserts and no transaction, so a crash after
`record_run` left a run with zero observations, which conformance rule 9 makes
indistinguishable from a legitimately empty run. These tests are the ones the three
loose inserts could not pass: one transaction, one event, nothing half-landed.
"""
import inspect
import json
import sqlite3

import pytest

from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.authorship import UnauthoredEvent
from evidence_shape.conformance import NonConforming
from evidence_shape.runs import MalformedRun
from evidence_shape.store import (
    AmbiguousAuthoritativeRun, AmbiguousSupersession, RunWriter,
    authoritative_result, get_run, observation_keys_for_run, result_for_run,
    observation_row, observations_for_run, supersede_chain, text_units_for_run,
)

from extractors.sink import EvidenceSink, ExtractionResult
from extractors import shape

CONTENT_HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
PAGE_ONE = "BUSIB 4300 Syllabus\nSpring 2026. Meetings on Tuesdays."
HEADING = "BUSIB 4300 Syllabus"
STARTED = "2026-08-19T14:00:00+00:00"
FINISHED = "2026-08-19T14:03:22+00:00"

PAGE = (shape.segment("page", index=1),)


def an_observation(*, raw_value=HEADING, start=0, version="0.1.0"):
    """One located value on page one, spanning the stored unit (rule 10, RAW-1)."""
    return shape.observation(
        file_id="f1", content_hash=CONTENT_HASH, extractor_name="pdf.text",
        extractor_version=version, source_type="text_document", raw_value=raw_value,
        location=shape.location(zone="heading", container_path=PAGE,
                                text_span={"start": start,
                                           "end": start + len(raw_value)}),
        observed_at=FINISHED, reliability="direct")


def a_result(*, observations=None, text_units=None, version="0.1.0", **run_overrides):
    """What an extractor hands over: no `run_id` anywhere. P4 assigns it."""
    observations = (an_observation(version=version),) if observations is None \
        else observations
    text_units = (shape.text_unit(text=PAGE_ONE, container_path=PAGE),) \
        if text_units is None else text_units
    run = dict(
        file_id="f1", content_hash=CONTENT_HASH, extractor_name="pdf.text",
        extractor_version=version, source_type="text_document",
        analysis_tier="native", config={}, completeness="complete",
        coverage={"units": "pages", "processed": 1, "total": 1},
        observation_count=len(observations), started_at=STARTED, finished_at=FINISHED)
    run.update(run_overrides)
    return ExtractionResult(run=shape.run(**run), observations=observations,
                            text_units=text_units)


def events_for(conn, run_id):
    """Every event whose §8.2 evidence reference names this run."""
    return [row for row in conn.execute("SELECT * FROM events ORDER BY event_id")
            if json.loads(row["explanation"] or "{}").get("run_id") == run_id]


def only_observation_id(conn, run_id) -> str:
    """The one `evidence` row of a one-observation run, by its stored id."""
    return conn.execute("SELECT observation_id FROM evidence WHERE run_id = ?",
                        (run_id,)).fetchone()["observation_id"]


def counts(conn):
    return {table: conn.execute(f"SELECT count(*) c FROM {table}").fetchone()["c"]
            for table in ("extraction_runs", "evidence", "text_units", "events")}


def test_persisted_result_is_reconstructed_losslessly(p4_conn):
    run_id = RunWriter(p4_conn, author="P5").write(a_result())

    restored = result_for_run(p4_conn, run_id)

    assert restored.run == get_run(p4_conn, run_id).to_mapping()
    assert restored.observations == tuple(
        row.to_mapping() for row in observations_for_run(p4_conn, run_id))
    assert restored.text_units == tuple(
        row.to_mapping() for row in text_units_for_run(p4_conn, run_id))


def test_authoritative_result_accepts_current_text_run_with_zero_observations(p4_conn):
    writer = RunWriter(p4_conn, author="P5")
    run_id = writer.write(a_result(version="0.1.0", observations=()))

    restored = authoritative_result(
        p4_conn, file_id="f1", content_hash=CONTENT_HASH,
        extractor_name="pdf.text", extractor_version="0.1.0",
        analysis_tier="native")

    assert restored is not None
    assert restored.run["run_id"] == run_id
    assert authoritative_result(
        p4_conn, file_id="f1", content_hash=CONTENT_HASH,
        extractor_name="pdf.text", extractor_version="stale",
        analysis_tier="native") is None


def test_observation_supersession_does_not_invent_run_level_authority(p4_conn):
    writer = RunWriter(p4_conn, author="P5")
    run_id = writer.write(a_result(version="0.1.0"))
    writer.write(
        a_result(version="stale"),
        supersede_reason="a different extractor version reread the observation")

    restored = authoritative_result(
        p4_conn, file_id="f1", content_hash=CONTENT_HASH,
        extractor_name="pdf.text", extractor_version="0.1.0",
        analysis_tier="native")

    assert restored is not None
    assert restored.run["run_id"] == run_id
    assert authoritative_result(
        p4_conn, file_id="another-file", content_hash=CONTENT_HASH,
        extractor_name="pdf.text", extractor_version="0.1.0",
        analysis_tier="native") is None
    assert authoritative_result(
        p4_conn, file_id="f1", content_hash="08da1122759d0a1822140a5d9ac70b8daec5393fbaa23cafd3024817d0c59c3c",
        extractor_name="pdf.text", extractor_version="0.1.0",
        analysis_tier="native") is None


def test_authoritative_result_refuses_ambiguous_current_runs(p4_conn):
    writer = RunWriter(p4_conn, author="P5")
    writer.write(a_result())
    writer.write(a_result(observations=(an_observation(raw_value="Spring 2026", start=20),)))

    with pytest.raises(AmbiguousAuthoritativeRun):
        authoritative_result(
            p4_conn, file_id="f1", content_hash=CONTENT_HASH,
            extractor_name="pdf.text", extractor_version="0.1.0",
            analysis_tier="native")


# ── the Protocol P5 wrote, implemented ────────────────────────────────────────

def test_it_is_the_evidence_sink_p5s_extractors_already_hand_their_batch_to():
    # P5's `sink.py` published `EvidenceSink` with `RecordingSink` as its only
    # implementation. `write` is the whole surface, so the signatures agree or the
    # orchestrator's first call does not type-check against the Protocol it named.
    expected = inspect.signature(EvidenceSink.write).parameters
    actual = inspect.signature(RunWriter.write).parameters
    assert list(actual) == list(expected)
    assert [p.kind for p in actual.values()] == [p.kind for p in expected.values()]
    assert actual["supersede_reason"].default is None


def test_the_sink_mints_the_run_id_the_batch_does_not_carry(p4_conn):
    result = a_result()
    assert "run_id" not in result.run

    run_id = RunWriter(p4_conn, author="P5").write(result)

    assert get_run(p4_conn, run_id).run_id == run_id
    assert [o.run_id for o in observations_for_run(p4_conn, run_id)] == [run_id]
    assert [u.run_id for u in text_units_for_run(p4_conn, run_id)] == [run_id]


def test_the_whole_batch_lands(p4_conn):
    run_id = RunWriter(p4_conn, author="P5").write(a_result())

    stored = get_run(p4_conn, run_id)
    assert stored.extractor_name == "pdf.text"
    assert stored.completeness == "complete"
    assert stored.config_fingerprint == shape.fingerprint({})
    assert [o.raw_value for o in observations_for_run(p4_conn, run_id)] == [HEADING]
    assert [u.text for u in text_units_for_run(p4_conn, run_id)] == [PAGE_ONE]


def test_a_batch_that_names_its_own_run_id_is_refused(p4_conn):
    # `extractors.shape`'s own header: "Not computed here, because they are
    # P4-assigned: `observation_id`, `observation_key`, `run_id` ...". Merging the
    # caller's id over P4's lets a batch name a row it does not own; merging P4's over
    # the caller's discards a value the caller believed was honoured. Neither is a
    # thing to do silently.
    with pytest.raises(MalformedRun):
        RunWriter(p4_conn, author="P5").write(
            ExtractionResult(run={"run_id": "r1", **a_result().run}))

    assert counts(p4_conn) == {"extraction_runs": 0, "evidence": 0,
                               "text_units": 0, "events": 0}


# ── the order store.py's docstring states ─────────────────────────────────────

def test_the_write_order_is_run_then_units_and_observations_then_the_event(p4_conn):
    """"run row, then text units and observations, then the one §8.2 event".

    Not cosmetic. `evidence.run_id` and `text_units.run_id` are foreign keys into
    `extraction_runs`, and `record_run_event` reads the run's `observation_key`s out
    of the STORED rows -- which is why P5 could not append its own event before a
    sink existed to write the rows first.
    """
    statements = []
    p4_conn.set_trace_callback(statements.append)
    try:
        RunWriter(p4_conn, author="P5").write(a_result())
    finally:
        p4_conn.set_trace_callback(None)

    # Order of FIRST insert into each table. `events`' append-only BEFORE INSERT
    # trigger is traced alongside the statement it guards, so that one INSERT is
    # traced twice; `test_exactly_one_event_per_run` is what proves it wrote once.
    tables = []
    for line in statements:
        if line.upper().startswith("INSERT INTO") and line.split()[2] not in tables:
            tables.append(line.split()[2])
    assert tables == ["extraction_runs", "text_units", "evidence", "events"]


def test_the_whole_batch_is_one_transaction(p4_conn):
    statements = []
    p4_conn.set_trace_callback(statements.append)
    try:
        RunWriter(p4_conn, author="P5").write(a_result())
    finally:
        p4_conn.set_trace_callback(None)

    boundaries = [line.split()[0].upper() for line in statements
                  if line.split()[0].upper() in ("BEGIN", "COMMIT", "ROLLBACK")]
    assert boundaries == ["BEGIN", "COMMIT"]


# ── nothing half-lands ────────────────────────────────────────────────────────

def test_a_failure_partway_leaves_no_run_no_unit_no_observation_and_no_event(p4_conn):
    """The defect the three loose inserts had: a crash after `record_run` left a run
    with zero observations, which rule 9 makes a MEANINGFUL state -- an unsupported
    or failed run legitimately carries none. A half-written batch is indistinguishable
    from a run that genuinely read nothing.

    The failure here is real, not injected: two units at one `container_path` collide
    on `text_units`' `(run_id, unit_locator)` primary key, and the run row is already
    in by then.
    """
    unit = shape.text_unit(text=PAGE_ONE, container_path=PAGE)
    statements = []
    p4_conn.set_trace_callback(statements.append)
    try:
        with pytest.raises(sqlite3.IntegrityError):
            RunWriter(p4_conn, author="P5").write(a_result(text_units=(unit, unit)))
    finally:
        p4_conn.set_trace_callback(None)

    # The run row really was in when it broke -- otherwise this proves nothing.
    assert "INSERT INTO extraction_runs" in " ".join(statements)
    assert statements[-1].upper().startswith("ROLLBACK")
    assert counts(p4_conn) == {"extraction_runs": 0, "evidence": 0,
                               "text_units": 0, "events": 0}


def test_a_failure_at_the_last_step_rolls_back_everything_before_it(p4_conn,
                                                                   monkeypatch):
    # The event is written last, so it is the step with the most already committed
    # behind it. Rolling back from there is the strongest statement of atomicity.
    from evidence_shape import store

    def boom(*args, **kwargs):
        raise RuntimeError("the event writer failed")

    monkeypatch.setattr(store, "record_run_event", boom)
    with pytest.raises(RuntimeError):
        store.RunWriter(p4_conn, author="P5").write(a_result())

    assert counts(p4_conn) == {"extraction_runs": 0, "evidence": 0,
                               "text_units": 0, "events": 0}


def test_a_non_conforming_batch_is_refused_before_anything_is_written(p4_conn):
    # Rule 9: an `unsupported` run carries zero observations. Validating the whole
    # batch first is what makes "never half-lands" true for a batch that is wrong
    # rather than for a database that failed.
    with pytest.raises(NonConforming):
        RunWriter(p4_conn, author="P5").write(a_result(completeness="unsupported"))

    assert counts(p4_conn) == {"extraction_runs": 0, "evidence": 0,
                               "text_units": 0, "events": 0}


def test_an_observation_whose_span_has_no_unit_is_refused(p4_conn):
    # Rule 10 needs the run's whole batch to be checkable at once, which is exactly
    # what a batch writer has and three separate inserts did not.
    with pytest.raises(NonConforming):
        RunWriter(p4_conn, author="P5").write(a_result(text_units=()))

    assert counts(p4_conn) == {"extraction_runs": 0, "evidence": 0,
                               "text_units": 0, "events": 0}


# ── exactly one event per run (break 5) ───────────────────────────────────────

def test_exactly_one_event_per_run(p4_conn):
    """P5's `extractors.events.append` wrote a second one. Done-means "exactly one
    event per run" could not hold while two writers existed."""
    writer = RunWriter(p4_conn, author="P5")
    first = writer.write(a_result())
    second = writer.write(a_result(version="0.2.0",
                                   observations=(an_observation(version="0.2.0"),)))

    assert len(events_for(p4_conn, first)) == 1
    assert len(events_for(p4_conn, second)) == 1
    assert p4_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == 2


def test_the_event_carries_the_observation_keys_built_from_the_stored_rows(p4_conn):
    # SPEC, Provenance: the evidence reference is "`run_id` plus the
    # `observation_key`s", and it is the KEY, never `observation_id` (M14). Read from
    # the rows rather than handed in, so the event and the database cannot disagree.
    run_id = RunWriter(p4_conn, author="P5").write(a_result(
        observations=(an_observation(), an_observation(raw_value="Spring 2026",
                                                       start=20))))

    explanation = json.loads(events_for(p4_conn, run_id)[0]["explanation"])
    assert explanation["run_id"] == run_id
    assert explanation["observation_keys"] == observation_keys_for_run(p4_conn, run_id)
    assert set(explanation["observation_keys"]) == {
        o.observation_key for o in observations_for_run(p4_conn, run_id)}


def test_an_ocr_run_appends_8_2s_OCR_event_and_a_native_run_an_extraction_event(
        p4_conn):
    writer = RunWriter(p4_conn, author="P5")
    native = writer.write(a_result())
    ocr = writer.write(a_result(extractor_name="ocr.apple_vision", source_type="ocr",
                                analysis_tier="ocr", observations=(), text_units=(),
                                config={"dpi": 200}, completeness="complete",
                                observation_count=0))

    assert events_for(p4_conn, native)[0]["event_type"] == "extraction"
    assert events_for(p4_conn, ocr)[0]["event_type"] == "OCR"


def test_the_acting_part_authors_and_p1_is_refused(p4_conn):
    # M8: "The acting part authors; P1 writes." P5 constructs the sink with `P5`;
    # P8 constructs it with `P8` for an `llm`-tier run. P4 supplies no default.
    assert events_for(p4_conn, RunWriter(p4_conn, author="P5").write(
        a_result()))[0]["subsystem"] == "P5"
    with pytest.raises(UnauthoredEvent):
        RunWriter(p4_conn, author="P1")
    with pytest.raises(UnauthoredEvent):
        RunWriter(p4_conn, author="")
    with pytest.raises(TypeError):
        RunWriter(p4_conn)


# ── §8.2 supersession ─────────────────────────────────────────────────────────

def test_a_re_run_supersedes_the_prior_row_that_carries_the_same_citation_handle(
        p4_conn):
    """MINOR 8 leaves `extractor_version` out of `observation_key` precisely so a new
    version's row and the old version's row share one handle. That shared handle is
    the only pairing the design publishes, so it is the one the sink uses."""
    writer = RunWriter(p4_conn, author="P5")
    first = writer.write(a_result(version="0.1.0"))
    second = writer.write(
        a_result(version="0.2.0", observations=(an_observation(version="0.2.0"),)),
        supersede_reason="pdf.text 0.2.0 re-read the same heading")

    assert observations_for_run(p4_conn, first)[0].observation_key == \
        observations_for_run(p4_conn, second)[0].observation_key

    old_id = only_observation_id(p4_conn, first)
    new_id = only_observation_id(p4_conn, second)
    assert observation_row(p4_conn, old_id)["superseded_by"] == new_id
    assert observation_row(p4_conn, old_id)["supersede_reason"] == \
        "pdf.text 0.2.0 re-read the same heading"
    assert observation_row(p4_conn, new_id)["supersedes"] == old_id


def test_both_extraction_records_remain_available(p4_conn):
    # §8.2's own words. Superseding links; it never deletes and never rewrites.
    writer = RunWriter(p4_conn, author="P5")
    first = writer.write(a_result(version="0.1.0"))
    second = writer.write(
        a_result(version="0.2.0", observations=(an_observation(version="0.2.0"),)),
        supersede_reason="a later pass")

    links = supersede_chain(p4_conn, only_observation_id(p4_conn, first))
    assert [row["extractor_version"] for row in links] == ["0.1.0", "0.2.0"]
    assert [u.text for u in text_units_for_run(p4_conn, first)] == [PAGE_ONE]
    assert [u.text for u in text_units_for_run(p4_conn, second)] == [PAGE_ONE]


def test_without_a_reason_nothing_is_superseded(p4_conn):
    # P5 supplies the reason and P4 sets the columns; no reason means no supersession
    # to record, and §8.2 requires the reason on every link.
    writer = RunWriter(p4_conn, author="P5")
    writer.write(a_result(version="0.1.0"))
    writer.write(a_result(version="0.2.0",
                          observations=(an_observation(version="0.2.0"),)))

    for row in p4_conn.execute("SELECT * FROM evidence"):
        for column in SUPERSEDE_COLUMNS:
            assert row[column] is None


def test_a_reason_supersedes_nothing_when_no_prior_row_carries_the_handle(p4_conn):
    """§8.2's OWN example -- a garbled first OCR pass and a later engine recovering
    the name -- pairs nothing here, and that is honest rather than broken: the two
    readings are different `raw_value`s, so they are two citation handles, and P4
    publishes no rule for pairing them. §8.2 asks only that both remain available."""
    writer = RunWriter(p4_conn, author="P5")
    first = writer.write(a_result(observations=(), observation_count=0))
    second = writer.write(a_result(), supersede_reason="a later engine recovered it")

    assert observations_for_run(p4_conn, first) == []
    assert len(observations_for_run(p4_conn, second)) == 1
    assert observation_row(
        p4_conn, only_observation_id(p4_conn, second))["supersedes"] is None


def test_an_ambiguous_pairing_is_refused_and_the_batch_does_not_land(p4_conn):
    """Two prior unsuperseded rows carry one handle, so "the prior row" names two.
    P1's `mark_superseded` would let the second link silently overwrite the first
    row's `supersedes` pointer. The design does not rule on the collision, so the
    sink refuses rather than picking a winner and losing the other link."""
    writer = RunWriter(p4_conn, author="P5")
    writer.write(a_result(version="0.1.0"))
    writer.write(a_result(version="0.2.0",
                          observations=(an_observation(version="0.2.0"),)))
    before = counts(p4_conn)

    with pytest.raises(AmbiguousSupersession):
        writer.write(a_result(version="0.3.0",
                              observations=(an_observation(version="0.3.0"),)),
                     supersede_reason="a third pass")

    assert counts(p4_conn) == before
