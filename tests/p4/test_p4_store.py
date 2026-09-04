# tests/p4/test_p4_store.py
import json

import pytest

from database_agent.events import RESERVED_EVENT_TYPES

from evidence_shape.authorship import UnauthoredEvent
from evidence_shape.runs import Coverage, ExtractionRun
from evidence_shape.store import (
    get_run, new_id, record_run, record_run_event, runs_for_content, runs_for_file,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.store import get_observation, observation_row, observations_by_key, observations_for_file, observations_for_run, record_observation, record_text_unit, text_unit_at, text_units_for_run, unit_for_observation, unit_length_for_observation
from evidence_shape.text_units import TextUnit


def _run(**overrides):
    payload = dict(
        run_id="r1", file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at="2026-08-19T14:00:00+00:00",
        finished_at="2026-08-19T14:03:22+00:00",
    )
    payload.update(overrides)
    return ExtractionRun(**payload)


def _ocr_run(**overrides):
    return _run(run_id="r2", extractor_name="ocr.apple_vision",
                extractor_version="2.4.1", source_type="ocr", analysis_tier="ocr",
                config={"dpi": 200, "languages": ["en", "zh-Hans"],
                        "recognition": "accurate"},
                completeness="capped",
                coverage=Coverage("pages", 40, 312), **overrides)


def test_ids_are_unique(p4_conn):
    assert new_id() != new_id()


def test_a_run_round_trips_through_the_database(p4_conn):
    record_run(p4_conn, _ocr_run())
    stored = get_run(p4_conn, "r2")
    assert stored == _ocr_run()
    assert stored.config["languages"] == ["en", "zh-Hans"]
    assert stored.coverage == Coverage("pages", 40, 312)
    assert stored.config_fingerprint == _ocr_run().config_fingerprint


def test_the_config_is_stored_as_canonical_json(p4_conn):
    record_run(p4_conn, _ocr_run())
    raw = p4_conn.execute(
        "SELECT config FROM extraction_runs WHERE run_id = 'r2'").fetchone()["config"]
    assert raw == '{"dpi":200,"languages":["en","zh-Hans"],"recognition":"accurate"}'


def test_a_run_with_no_coverage_stores_null(p4_conn):
    record_run(p4_conn, _run())
    assert p4_conn.execute(
        "SELECT coverage FROM extraction_runs WHERE run_id = 'r1'"
    ).fetchone()["coverage"] is None
    assert get_run(p4_conn, "r1").coverage is None


def test_two_runs_over_one_file_are_two_rows(p4_conn):
    # B1: "An opaque image runs the image extractor and OCR, which is two rows -- one
    # may be `complete` while the other is `capped`."
    record_run(p4_conn, _run())
    record_run(p4_conn, _ocr_run())
    rows = runs_for_file(p4_conn, "f1")
    assert [row.run_id for row in rows] == ["r1", "r2"]
    assert {row.completeness for row in rows} == {"complete", "capped"}


def test_runs_are_findable_by_content_hash(p4_conn):
    # §2.1: "read each file once per content version"; §3.4 keys on the content hash.
    record_run(p4_conn, _run())
    record_run(p4_conn, _ocr_run())
    assert len(runs_for_content(p4_conn, "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124")) == 2
    assert runs_for_content(p4_conn, "08da1122759d0a1822140a5d9ac70b8daec5393fbaa23cafd3024817d0c59c3c") == []


def test_an_unknown_run_is_a_key_error(p4_conn):
    with pytest.raises(KeyError):
        get_run(p4_conn, "nope")


def test_a_native_run_appends_8_2s_extraction_event(p4_conn):
    record_run(p4_conn, _run())
    event_id = record_run_event(p4_conn, "r1", author="P5")

    row = p4_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (event_id,)).fetchone()
    assert row["event_type"] == "extraction"
    assert row["event_type"] in RESERVED_EVENT_TYPES
    assert row["subsystem"] == "P5"
    assert row["component_version"] == "3.1.0"
    assert row["file_id"] == "f1"
    assert row["content_hash"] == "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
    assert row["observed_at"] == "2026-08-19T14:03:22+00:00"


def test_an_ocr_run_appends_8_2s_OCR_event_spelled_the_way_8_2_spells_it(p4_conn):
    # MINOR 2: "§8.2 spells it `OCR`." P1's writer validates against that
    # vocabulary, so a lowercase name would fail at runtime.
    record_run(p4_conn, _ocr_run())
    event_id = record_run_event(p4_conn, "r2", author="P5")
    assert p4_conn.execute("SELECT event_type FROM events WHERE event_id = ?",
                           (event_id,)).fetchone()["event_type"] == "OCR"


def test_an_llm_tier_run_appends_an_extraction_event_and_p4_forbids_p8_nothing_else(
        p4_conn):
    # I4: "P8 is the only writer of `llm` runs." P4 accepts the value and appends the
    # one event a run appends; P8's own five registered events are its business.
    record_run(p4_conn, _run(run_id="r3", analysis_tier="llm"))
    event_id = record_run_event(p4_conn, "r3", author="P8")
    row = p4_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (event_id,)).fetchone()
    assert row["event_type"] == "extraction"
    assert row["subsystem"] == "P8"


def test_the_event_carries_the_run_id_and_the_keys_of_that_runs_observations(p4_conn):
    # SPEC, Provenance: the reference is "`run_id` plus the `observation_key`s".
    record_run(p4_conn, _run())
    event_id = record_run_event(p4_conn, "r1", author="P5")
    explanation = json.loads(p4_conn.execute(
        "SELECT explanation FROM events WHERE event_id = ?",
        (event_id,)).fetchone()["explanation"])
    assert explanation["run_id"] == "r1"
    assert explanation["observation_keys"] == []      # none written yet


def test_the_caller_names_itself_and_p1_may_never_be_named(p4_conn):
    # M8: the acting part authors; P1 writes. P4 supplies no default author.
    record_run(p4_conn, _run())
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, "r1", author="P1")
    with pytest.raises(UnauthoredEvent):
        record_run_event(p4_conn, "r1", author="")
    with pytest.raises(TypeError):
        record_run_event(p4_conn, "r1")


def test_the_event_carries_no_prompt_fingerprint_no_paths_and_no_user(p4_conn):
    # SPEC, Provenance: "Old and new paths do not apply; `prompt fingerprint` does
    # not apply (P4 is model-free); `user identity` does not apply." MINOR 10 keeps
    # user_id for explicit user actions, and a run is not one.
    record_run(p4_conn, _run())
    row = p4_conn.execute("SELECT * FROM events WHERE event_id = ?",
                          (record_run_event(p4_conn, "r1", author="P5"),)).fetchone()
    for absent in ("prompt_fingerprint", "old_path", "new_path", "user_id",
                   "correction_scope", "polarity"):
        assert row[absent] is None


def test_recording_a_run_appends_nothing_by_itself(p4_conn):
    # The event is the second call, because the keys it references do not exist yet.
    before = p4_conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    record_run(p4_conn, _run())
    assert p4_conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before


PAGE_ONE = "Syllabus — BUSIB 4300 — Spring 2026"


def _observation(**overrides):
    payload = dict(
        file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document",
        raw_value="BUSIB 4300",
        location=Location("heading", (Segment("page", 1),), text_span=TextSpan(11, 21)),
        occurrence_count=3, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id="r1", normalized_value="BUSIB 4300",
        context_before="Syllabus — ", context_after=" — Spring 2026",
        context_truncated=False,
    )
    payload.update(overrides)
    return Observation(**payload)


def test_an_observation_round_trips_through_the_database(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn, _observation())
    assert get_observation(p4_conn, observation_id) == _observation()


def test_the_stored_row_carries_the_key_and_a_separate_row_id(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn, _observation())
    row = observation_row(p4_conn, observation_id)
    assert row["observation_id"] == observation_id
    assert row["observation_key"] == _observation().observation_key
    assert row["observation_id"] != row["observation_key"]


def test_context_truncated_comes_back_as_a_bool_not_an_integer(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn,
                                        _observation(context_truncated=True))
    assert get_observation(p4_conn, observation_id).context_truncated is True


def test_a_null_normalized_value_survives_the_round_trip(p4_conn):
    record_run(p4_conn, _run())
    observation_id = record_observation(p4_conn, _observation(normalized_value=None))
    assert get_observation(p4_conn, observation_id).normalized_value is None


def test_the_run_observation_count_becomes_the_truth_as_rows_land(p4_conn):
    record_run(p4_conn, _run())
    assert get_run(p4_conn, "r1").observation_count == 0
    record_observation(p4_conn, _observation())
    record_observation(p4_conn, _observation(raw_value="Spring 2026"))
    assert get_run(p4_conn, "r1").observation_count == 2
    assert len(observations_for_run(p4_conn, "r1")) == 2


def test_one_key_resolves_to_every_row_that_carries_it(p4_conn):
    # §8.7: "a negative example recorded today still resolves after an extractor
    # upgrade." MINOR 8 makes the key survive the upgrade; this makes both rows
    # reachable through it.
    record_run(p4_conn, _run())
    record_run(p4_conn, _run(run_id="r9", extractor_version="4.0.0"))
    record_observation(p4_conn, _observation())
    record_observation(p4_conn, _observation(run_id="r9", extractor_version="4.0.0"))

    key = _observation().observation_key
    found = observations_by_key(p4_conn, key)
    assert len(found) == 2
    assert {row.extractor_version for row in found} == {"3.1.0", "4.0.0"}
    assert {row.observation_key for row in found} == {key}


def test_an_unknown_key_resolves_to_nothing_rather_than_raising(p4_conn):
    assert observations_by_key(p4_conn, "f6c040e7678e9b8d8f7b29d0d9503b0428cc43a15e45b4258204def0a3aab59a") == []


def test_observations_are_findable_by_file(p4_conn):
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation())
    assert len(observations_for_file(p4_conn, "f1")) == 1
    assert observations_for_file(p4_conn, "f-other") == []


def test_a_text_unit_round_trips_and_is_addressed_by_its_container_path(p4_conn):
    record_run(p4_conn, _run())
    unit = TextUnit(run_id="r1", container_path=(Segment("page", 1),), text=PAGE_ONE)
    record_text_unit(p4_conn, unit)

    assert text_units_for_run(p4_conn, "r1") == [unit]
    assert text_unit_at(p4_conn, "r1", (Segment("page", 1),)) == unit
    assert text_unit_at(p4_conn, "r1", (Segment("page", 9),)) is None
    assert text_unit_at(p4_conn, "r-other", (Segment("page", 1),)) is None


def test_a_whole_file_unit_is_addressed_by_the_empty_path(p4_conn):
    # §2.4: the full text of a text-bearing file is one row, container_path: [].
    record_run(p4_conn, _run())
    unit = TextUnit(run_id="r1", container_path=(), text=PAGE_ONE)
    record_text_unit(p4_conn, unit)
    assert text_unit_at(p4_conn, "r1", ()) == unit


def test_truncated_comes_back_as_a_bool(p4_conn):
    record_run(p4_conn, _run())
    record_text_unit(p4_conn, TextUnit(run_id="r1", container_path=(),
                                       text=PAGE_ONE[:12], truncated=True))
    assert text_unit_at(p4_conn, "r1", ()).truncated is True


def test_rule_10s_lookup_finds_the_unit_an_observations_span_points_into(p4_conn):
    record_run(p4_conn, _run())
    record_text_unit(p4_conn, TextUnit(run_id="r1",
                                       container_path=(Segment("page", 1),),
                                       text=PAGE_ONE))
    observation = _observation()
    unit = unit_for_observation(p4_conn, observation)
    assert unit is not None
    assert unit.text[observation.location.text_span.start:
                     observation.location.text_span.end] == observation.raw_value


def test_rule_10s_lookup_returns_nothing_when_no_unit_was_written(p4_conn):
    record_run(p4_conn, _run())
    assert unit_for_observation(p4_conn, _observation()) is None


def test_two_runs_over_one_pdf_leave_two_independent_unit_sets(p4_conn):
    # Rule 4, and §8.2: "if a first OCR pass produces unreadable text and a later
    # improved OCR engine recovers a university name, both extraction records should
    # remain available."
    record_run(p4_conn, _run())
    record_run(p4_conn, _ocr_run())
    record_text_unit(p4_conn, TextUnit(run_id="r1",
                                       container_path=(Segment("page", 1),),
                                       text=PAGE_ONE))
    record_text_unit(p4_conn, TextUnit(run_id="r2",
                                       container_path=(Segment("page", 1),),
                                       text="SyIIabus BUS1B 43OO"))
    assert text_unit_at(p4_conn, "r1", (Segment("page", 1),)).text == PAGE_ONE
    assert text_unit_at(p4_conn, "r2", (Segment("page", 1),)).text != PAGE_ONE
    assert len(text_units_for_run(p4_conn, "r1")) == 1
    assert len(text_units_for_run(p4_conn, "r2")) == 1


def test_the_event_carries_the_keys_once_the_observations_exist(p4_conn):
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation())
    record_observation(p4_conn, _observation(raw_value="Spring 2026"))
    explanation = json.loads(p4_conn.execute(
        "SELECT explanation FROM events WHERE event_id = ?",
        (record_run_event(p4_conn, "r1", author="P5"),)).fetchone()["explanation"])
    assert explanation["run_id"] == "r1"
    assert len(explanation["observation_keys"]) == 2
    assert all(key.startswith("sha256:") for key in explanation["observation_keys"])


# --- rule 10's lookup, without the text -------------------------------------

def test_the_length_only_lookup_answers_rule_10_without_handing_over_the_text(
        p4_conn):
    """A caller that only needs to know how long a unit is never holds the unit.

    `unit_for_observation` returns a `TextUnit`, and a `TextUnit` carries `.text` --
    the whole extracted document. Two callers want rule 10's lookup only to compare
    a length: P8's dossier builder asks "is this observation the whole of its unit?"
    so it can REFUSE to send it. Handing that caller the document in order to let it
    decline to send the document is the wrong shape, and `p7`'s repo-wide binder
    guard is what says so out loud -- it names the three modules that may bind a P4
    materialiser, and a module that builds cloud requests is not going to be a
    fourth.

    So P4 answers the question that was actually asked. The length is a number; a
    number cannot be leaked.
    """
    record_run(p4_conn, _run())
    record_text_unit(p4_conn, TextUnit(run_id="r1",
                                       container_path=(Segment("page", 1),),
                                       text=PAGE_ONE))
    assert unit_length_for_observation(p4_conn, _observation()) == len(PAGE_ONE)


def test_the_length_only_lookup_says_nothing_rather_than_zero_when_no_unit_exists(
        p4_conn):
    """`None` and `0` are different answers and the caller branches on the difference.

    A span-less observation with NO unit at its path is P8's §2.3 cell and §2.8 EXIF
    field -- the shape where the address IS the whole citation -- and it may be
    offered. A span-less observation standing at a unit of length 0 is a different
    thing entirely. Returning `0` for the first would silently reclassify every
    EXIF field as a whole document and drop it from every dossier.
    """
    record_run(p4_conn, _run())
    assert unit_length_for_observation(p4_conn, _observation()) is None
