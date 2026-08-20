# tests/p4/test_p4_prohibitions.py
"""Done-means 6. §2.8's four prohibitions and the three the SPEC derives.

Task 13 tests that the validator REPORTS a violation. This file tests that the shape
makes the thing impossible: the constructor refuses it, the table has no column for
it, the trigger aborts it. A validator is a call an author can forget; a schema is not.
"""
import pytest

from evidence_shape.location import Location, Segment
from evidence_shape.observation import (
    MalformedObservation, OBSERVATION_ROW_FIELDS, Observation,
)
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import (
    observations_for_run, record_observation, record_run, record_text_unit,
    runs_for_file,
)
from evidence_shape.text_units import TextUnit
from evidence_shape.vocabulary import NotInVocabulary, ZONES

#: Every name a destination, a domain, a product field, a grouping or a plan would
#: have to be stored under. §2.8, §3.11, §3.12, §3.14, §8.8.
FORBIDDEN_COLUMNS = (
    "proposed_path", "destination", "destination_node", "target_path", "folder",
    "domain", "domain_id", "category", "field_name", "fact", "facet",
    "group_id", "node_id", "template_id", "plan_id", "plan_version_id",
    "handling_class", "preferred", "conflict", "resolution", "absent",
)

P4_TABLES = ("evidence", "extraction_runs", "text_units")


def _run(run_id="r1", file_id="f1", *, completeness="complete", number=1):
    return ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=f"sha256:abc{number}",
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness=completeness, started_at="2026-08-19T14:00:00+00:00")


def _observation(run, **overrides):
    fields = dict(
        file_id=run.file_id, content_hash=run.content_hash,
        extractor_name=run.extractor_name, extractor_version=run.extractor_version,
        source_type=run.source_type, raw_value="Columbia",
        location=Location("body", (Segment("page", 1),)), occurrence_count=1,
        observed_at="2026-08-19T14:03:22+00:00", reliability="possible",
        run_id=run.run_id)
    fields.update(overrides)
    return Observation(**fields)


def _columns(conn, table):
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


# ── §2.8: "does not treat model output as proof" ──────────────────────────────

def test_an_extractor_cannot_write_a_fact_layer_reliability_state():
    # D11, and §3.5: rules produce validated facts, the LLM produces LLM-supported
    # facts, the user produces user-confirmed facts. None of them is an extractor.
    run = _run()
    for fact_state in ("validated", "llm_supported", "user_confirmed", "rejected"):
        with pytest.raises(NotInVocabulary):
            _observation(run, reliability=fact_state)


def test_the_refusal_is_in_the_record_not_only_in_the_validator():
    # An extractor that never calls validate_observation still cannot write one.
    with pytest.raises(NotInVocabulary):
        Observation(
            file_id="f1", content_hash="sha256:abc", extractor_name="llm.dossier",
            extractor_version="1.0.0", source_type="text_document",
            raw_value="Columbia", location=Location("body", (Segment("page", 1),)),
            occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
            reliability="llm_supported", run_id="r1")


# ── §2.8: "does not create a final folder path" / "invent domains" ────────────

def test_no_p4_table_has_a_destination_domain_group_node_or_plan_column(p4_conn):
    for table in P4_TABLES:
        columns = set(_columns(p4_conn, table))
        for forbidden in FORBIDDEN_COLUMNS:
            assert forbidden not in columns, f"{table}.{forbidden}"


def test_the_observation_record_is_a_closed_field_set():
    # There is nowhere to put one even as an extra key: rule 6 rejects an unknown
    # field, and the row field list is the whole surface.
    assert "domain" not in OBSERVATION_ROW_FIELDS
    assert "proposed_path" not in OBSERVATION_ROW_FIELDS
    with pytest.raises(TypeError):
        _observation(_run(), domain="education")


def test_the_path_zone_addresses_where_the_file_is_not_where_it_should_go():
    # One word, two concepts. §2.9's parent-folder context is evidence; a
    # destination is P11's and does not exist here.
    assert "path" in ZONES
    observation = _observation(
        _run(), location=Location("path", (Segment("field", label="parent"),)),
        raw_value="Columbia Applications")
    assert observation.zone == "path"
    assert not hasattr(observation, "proposed_path")


# ── §2.8: "does not merge all files that share one string" ────────────────────

def test_an_observation_references_exactly_one_file():
    with pytest.raises(MalformedObservation):
        _observation(_run(), file_id=["f1", "f2"])


def test_two_files_sharing_a_raw_value_share_nothing_structurally(p4_conn):
    first, second = _run("r1", "f1", number=1), _run("r2", "f2", number=2)
    record_run(p4_conn, first)
    record_run(p4_conn, second)
    record_observation(p4_conn, _observation(first))
    record_observation(p4_conn, _observation(second))

    one, = observations_for_run(p4_conn, "r1")
    two, = observations_for_run(p4_conn, "r2")
    assert one.raw_value == two.raw_value == "Columbia"
    assert one.file_id != two.file_id
    # Not even the citation handle merges them: the key is content-addressed, and
    # two files are two contents. Any link between them is P6's or P9's.
    assert one.observation_key != two.observation_key


def test_p4_owns_three_tables_and_no_table_that_links_two_files(p4_conn):
    names = {row[0] for row in p4_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert set(P4_TABLES) <= names
    for suspicious in ("evidence_links", "value_matches", "duplicates", "groups"):
        assert suspicious not in names


# ── §2.6, derived: no absence, no conflict, no resolution of one ──────────────

def test_an_observation_cannot_record_an_absence():
    # A count of zero IS an absence, and absence lives on the run record or nowhere.
    with pytest.raises(MalformedObservation):
        _observation(_run(), occurrence_count=0)


def test_a_complete_run_that_emitted_nothing_is_how_absence_is_recorded(p4_conn):
    # §2.6's "no EXIF" is exactly this case: no field is added for it and no
    # observation is written for it.
    record_run(p4_conn, _run(completeness="complete"))
    assert observations_for_run(p4_conn, "r1") == []
    stored, = runs_for_file(p4_conn, "f1")
    assert stored.completeness == "complete"
    assert stored.observation_count == 0


def test_an_observation_cannot_carry_a_conflict_or_its_resolution():
    # §2.6's conflicting signals are TWO observations with two signal_tier values.
    # There is one raw_value slot, one location slot, and no third "conflict" row.
    with pytest.raises(MalformedObservation):
        _observation(_run(), raw_value=["Canon EOS R6", "1920x1080"])
    with pytest.raises(TypeError):
        _observation(_run(), conflicts_with="obs-2")


# ── §8.2 / §8.7, derived: superseded, never deleted ───────────────────────────

def test_an_observation_is_superseded_never_deleted(p4_conn):
    # §8.7 requires a rejected proposal to be stored WITH the evidence that produced
    # it; deleting evidence decays every negative example that depends on it.
    record_run(p4_conn, _run())
    record_observation(p4_conn, _observation(_run()))
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM evidence")


def test_a_run_and_a_text_unit_are_never_deleted_either(p4_conn):
    record_run(p4_conn, _run())
    record_text_unit(p4_conn, TextUnit(run_id="r1",
                                       container_path=(Segment("page", 1),),
                                       text="Syllabus — BUSIB 4300"))
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM text_units")
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM extraction_runs")


# ── §2.4 / §2.9: three states that must stay distinguishable ──────────────────

def test_the_three_zero_observation_states_are_distinguishable(p4_conn):
    # §2.4: "an empty extraction result is different from an extractor that does not
    # yet exist." §2.9 adds the third: metadata_only is a deliberate policy stop.
    for index, (run_id, completeness) in enumerate((
            ("r-complete", "complete"),
            ("r-unsupported", "unsupported"),
            ("r-metadata-only", "metadata_only"))):
        record_run(p4_conn, _run(run_id, "f1", completeness=completeness,
                                 number=index))

    stored = {run.run_id: run for run in runs_for_file(p4_conn, "f1")}
    assert len(stored) == 3
    assert {run.completeness for run in stored.values()} == {
        "complete", "unsupported", "metadata_only"}
    for run in stored.values():
        assert run.observation_count == 0
        assert observations_for_run(p4_conn, run.run_id) == []
    # The three differ in exactly one field, and it is the field §2.4 requires.
    assert (stored["r-complete"].completeness
            != stored["r-unsupported"].completeness
            != stored["r-metadata-only"].completeness)
