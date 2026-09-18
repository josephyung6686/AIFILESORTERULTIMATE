# tests/p6/test_p6_year_rule.py
"""`00` amendment 20: a `year` field, derived by rule from `creation_date`.

Patterned on `capture_date -> capture_year` (`tests/p6/test_p6_capture_year_slot.py`),
with one difference that decides where the producer lives: `capture_year` reads an
OBSERVATION (the EXIF tag), while `creation_date` is a FACT the model writes at site
A, so `year` is a fact derived from a fact and runs after the model has written, not
inside `_rule_stage`, which the resolver runs before its `llm` stage.

`year` is NOT `record_period` (the interval a record COVERS), NOT `tax_year` and NOT
`capture_year`. The catalogue keeps all four apart and this producer writes only one.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.fields import FIELD_ROWS, get_field
from facts.file_facts import LLM_INTERPRETATION, RULE, facts_for_file, write_fact
from facts.states import LLM_SUPPORTED, VALIDATED
from facts.values import VALUE_ORIGINS, ensure_value

import cli

CLOCK = "2026-09-18T00:00:00+00:00"
CACHE_KEY = "test-year-rule:v1"


def _document(conn, tmp_path, name="notes.pdf"):
    path = tmp_path / name
    path.write_bytes(b"\x00document-bytes")
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=15,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Work", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observation(conn, *, file_id, content_hash, raw) -> str:
    """One document-metadata observation; returns its citation key. One run per
    observation, so a file may carry two dates from two runs."""
    run_id = f"run-{file_id}-{abs(hash(raw))}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.metadata", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.metadata",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location("metadata", (Segment("field", label="CreationDate"),)),
        occurrence_count=1, observed_at=CLOCK, reliability="direct",
        run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


def _creation_date(conn, *, file_id, content_hash, value, state=LLM_SUPPORTED) -> str:
    """The model's `creation_date` fact, written the way `llm_seam.apply_verdict`
    writes it: `llm_interpretation` origin, one citation, the site's cache key."""
    ref = _observation(conn, file_id=file_id, content_hash=content_hash, raw=value)
    value_id = ensure_value(conn, field_key="creation_date", canonical_value=value,
                            first_evidence_ref=ref, origin=VALUE_ORIGINS[0])
    return write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key="creation_date",
        value_id=value_id, reliability_state=state, origin=LLM_INTERPRETATION,
        evidence_refs=(ref,), cache_key=CACHE_KEY, active=True,
        model_identifier="test-model", prompt_fingerprint="test-prompt")


def _facts(conn, file_id, content_hash, field_key):
    return [row for row in facts_for_file(conn, file_id, content_hash)
            if row["field_key"] == field_key and row["active"]]


# --- the field row -------------------------------------------------------------

def test_year_is_a_destination_eligible_row_apart_from_its_three_neighbours(p6_conn):
    """SABOTAGE: alias `year` onto `capture_year` or `tax_year` -- four concepts
    become three and the Current work and Taxes templates share a folder."""
    keys = {row.field_key for row in FIELD_ROWS}
    assert {"year", "capture_year", "tax_year", "record_period"} <= keys
    year = get_field(p6_conn, "year")
    assert year["destination_eligible"] == 1
    rows = {row.field_key: row for row in FIELD_ROWS}
    assert rows["year"].reliability_ceiling == rows["capture_year"].reliability_ceiling
    assert rows["year"].scope == "universal"
    for other in ("capture_year", "tax_year", "record_period"):
        row = next(r for r in FIELD_ROWS if r.field_key == other)
        assert "year" not in row.aliases, other


# --- the producer --------------------------------------------------------------

def test_a_file_with_a_creation_date_gets_its_year(p6_conn, tmp_path):
    """SABOTAGE: `year_facts` returns `()` -- the row exists, nothing fills it, and
    `104` §18.109's finding (levels with no producer) is re-created on day one."""
    file_id, content_hash = _document(p6_conn, tmp_path)
    source = _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                            value="2024-07-17T14:03:22")
    written = cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash)
    assert len(written) == 1
    [year] = _facts(p6_conn, file_id, content_hash, cli.YEAR_FIELD)
    assert year["canonical_value"] == "2024"
    assert year["origin"] == RULE
    # A derivation cannot outrank what it derives from: the state and the citations
    # are the source fact's own, so a folder built on `year` rests on exactly the
    # evidence `creation_date` rests on.
    source_row = next(r for r in facts_for_file(p6_conn, file_id, content_hash)
                      if r["fact_id"] == source)
    assert year["reliability_state"] == source_row["reliability_state"] == LLM_SUPPORTED
    assert json.loads(year["evidence_refs"]) == json.loads(source_row["evidence_refs"])


def test_a_validated_creation_date_yields_a_validated_year(p6_conn, tmp_path):
    file_id, content_hash = _document(p6_conn, tmp_path)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                   value="2023-01-05", state=VALIDATED)
    cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash)
    [year] = _facts(p6_conn, file_id, content_hash, cli.YEAR_FIELD)
    assert (year["canonical_value"], year["reliability_state"]) == ("2023", VALIDATED)


def test_a_file_without_a_creation_date_gets_no_year(p6_conn, tmp_path):
    file_id, content_hash = _document(p6_conn, tmp_path)
    assert cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash) == ()
    assert _facts(p6_conn, file_id, content_hash, cli.YEAR_FIELD) == []


def test_the_producer_writes_year_and_none_of_its_three_neighbours(p6_conn, tmp_path):
    """SABOTAGE: spell `field_key="capture_year"` in the producer -- every document
    with a creation date becomes a photo of that year."""
    file_id, content_hash = _document(p6_conn, tmp_path)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                   value="2022-11-30")
    cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash)
    for other in ("capture_year", "tax_year", "record_period"):
        assert _facts(p6_conn, file_id, content_hash, other) == [], other


@pytest.mark.parametrize("value, expected", [
    ("2024-07-17T14:03:22", "2024"),   # ISO with time
    ("2024-07-17", "2024"),            # ISO date
    ("2024:07:17 14:03:22", "2024"),   # EXIF spelling
    ("17 March 2024", "2024"),         # a written date
    ("03/15/2024", "2024"),            # a slashed date, year last
    ("2024", "2024"),                  # a bare year
])
def test_the_value_is_the_calendar_year_and_nothing_else(p6_conn, tmp_path, value,
                                                          expected):
    """SABOTAGE: store the source value verbatim -- `2024-07-17` becomes a folder
    and two files of one year land in two."""
    file_id, content_hash = _document(p6_conn, tmp_path)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash, value=value)
    cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash)
    assert [r["canonical_value"] for r in
            _facts(p6_conn, file_id, content_hash, cli.YEAR_FIELD)] == [expected]


@pytest.mark.parametrize("value", [
    "0000-00-00",              # an unset clock, `capture_year`'s own refusal
    "unknown",                 # no year at all
    "2023-12-31 to 2024-01-02", # two years: a period, which is `record_period`'s
    "12345",                   # five digits are not a year
])
def test_no_single_calendar_year_means_no_year_fact(p6_conn, tmp_path, value):
    """SABOTAGE: take the first four digits -- `0000` and `1234` become folders, and
    a two-year span is silently filed under its first year."""
    file_id, content_hash = _document(p6_conn, tmp_path)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash, value=value)
    assert cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash) == ()
    assert _facts(p6_conn, file_id, content_hash, cli.YEAR_FIELD) == []


def test_running_the_producer_twice_writes_one_fact(p6_conn, tmp_path):
    """The fact pass may visit a file more than once; the second visit returns the
    existing row, as `write_fact`'s identity promises, and appends no second event."""
    file_id, content_hash = _document(p6_conn, tmp_path)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                   value="2021-06-01")
    first = cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash)
    second = cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash)
    assert first == second
    assert len(_facts(p6_conn, file_id, content_hash, cli.YEAR_FIELD)) == 1


def test_two_agreeing_creation_dates_write_one_year_from_the_strongest(p6_conn,
                                                                       tmp_path):
    """`file_facts` has no uniqueness constraint over (file, version, field), so a
    producer that wrote once per source would put two live `year` rows with one
    value on a file -- `104` §18.108's "second answer unreads the field",
    manufactured by the producer meant to fill it. SABOTAGE: loop over sources."""
    file_id, content_hash = _document(p6_conn, tmp_path)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                   value="2024-02-02", state=LLM_SUPPORTED)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                   value="2024-03-03", state=VALIDATED)
    written = cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash)
    assert len(written) == 1
    [year] = _facts(p6_conn, file_id, content_hash, cli.YEAR_FIELD)
    assert (year["canonical_value"], year["reliability_state"]) == ("2024", VALIDATED)


def test_two_disagreeing_creation_dates_write_no_year(p6_conn, tmp_path):
    file_id, content_hash = _document(p6_conn, tmp_path)
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                   value="2023-12-31")
    _creation_date(p6_conn, file_id=file_id, content_hash=content_hash,
                   value="2024-01-01")
    assert cli.year_facts(p6_conn, file_id=file_id, content_hash=content_hash) == ()


def test_a_models_year_is_canonicalised_by_the_same_rule():
    """`year` is universal, so it is in site A's allowlist and a model may be asked
    it. `normalize_for_model` must run the answer through `year_of`, or `July 2024`
    would be stored beside the rule's `2024` -- the several-spellings failure
    (`65` §4.2) re-created across the seam. SABOTAGE: no `YEAR_FIELD` branch."""
    assert cli.normalize_for_model(cli.YEAR_FIELD, "2024") == "2024"
    assert cli.normalize_for_model(cli.YEAR_FIELD, "July 2024") == "2024"
    assert cli.normalize_for_model(cli.YEAR_FIELD, "2024-07-17") == "2024"
    assert cli.normalize_for_model(cli.YEAR_FIELD, "unknown") is None
    assert cli.normalize_for_model(cli.YEAR_FIELD, "2023 to 2024") is None
