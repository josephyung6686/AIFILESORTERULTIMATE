"""`104` §18.55: the pass cache key is derived by one indexed join, and it is the
same key the row-by-row derivation gave.

`pass_cache_key` used to read EVERY observation of the version (JSON, one row at a
time) and ask P4 for each one's tier. It is asked once per fact and once per refusal
a pass writes, so a four-megabyte data export with 7,578 observations -- thousands of
them matching a rule whose context check fails -- read its own evidence thousands of
times over: the P6 pass sat at full CPU for forty minutes on one file. The key is
made of two sets, the (extractor, version) pairs and the tiers present, and SQLite's
DISTINCT over the version's rows joined to their runs is those two sets.
"""
from __future__ import annotations

import json

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from evidence_shape.vocabulary import ANALYSIS_TIERS
from facts.cache import fact_cache_key, pass_cache_key
from facts.evidence import analysis_tier_for_observation, observations_for_version
from evidence_shape.canonical import canonical_json

CLOCK = "2026-09-11T00:00:00Z"


def _version(conn, tmp_path, *, observations_per_run: int = 40):
    """One file version with a native run and an OCR run, two extractor versions,
    and many observations -- the shape of the data export that spun."""
    create_schema(conn)
    create_evidence_schema(conn)
    body = b"research_focus\tclinical_trial\n" * 200
    path = tmp_path / "export.txt"
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename="export.txt", normalized_filename="export.txt",
        extension=".txt", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="text/plain",
        detected_format="txt", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    for run_id, extractor, version, tier in (
            ("run-native", "text.structured", "0.3.0", "native"),
            ("run-ocr", "ocr.apple_vision", "0.1.0", "ocr")):
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name=extractor, extractor_version=version,
            source_type="text_document", analysis_tier=tier, config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
        for k in range(observations_per_run):
            record_observation(conn, Observation(
                file_id=file_id, content_hash=content_hash,
                extractor_name=extractor, extractor_version=version,
                source_type="text_document", raw_value=f"SDY{1000 + k}",
                location=Location("body", (Segment("page", 1),), text_span=None),
                occurrence_count=1, observed_at=CLOCK, reliability="possible",
                run_id=run_id))
    return file_id, content_hash


def _row_by_row(conn, file_id, content_hash) -> str:
    """The derivation this replaces, kept here as the oracle."""
    observations = observations_for_version(conn, file_id, content_hash)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {analysis_tier_for_observation(conn, one) for one in observations}
    present = [tier for tier in ANALYSIS_TIERS if tier in tiers]
    return fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([list(pair) for pair in pairs]),
        analysis_tier=present[-1] if present else ANALYSIS_TIERS[0],
        model_identifier=None, prompt_fingerprint=None)


def test_the_joined_key_is_the_row_by_row_key(p6_conn, tmp_path):
    file_id, content_hash = _version(p6_conn, tmp_path)
    assert pass_cache_key(p6_conn, file_id=file_id, content_hash=content_hash) == \
        _row_by_row(p6_conn, file_id, content_hash)


def test_the_key_names_the_last_tier_present(p6_conn, tmp_path):
    file_id, content_hash = _version(p6_conn, tmp_path)
    key = pass_cache_key(p6_conn, file_id=file_id, content_hash=content_hash)
    # An OCR run beside the native one: the key stands in the `ocr` slot, and a
    # version with only the native run stands in `native`.
    assert key != fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([["ocr.apple_vision", "0.1.0"],
                                          ["text.structured", "0.3.0"]]),
        analysis_tier="native", model_identifier=None, prompt_fingerprint=None)
    assert key == fact_cache_key(
        content_hash=content_hash,
        extractor_version=canonical_json([["ocr.apple_vision", "0.1.0"],
                                          ["text.structured", "0.3.0"]]),
        analysis_tier="ocr", model_identifier=None, prompt_fingerprint=None)


def test_one_key_costs_a_handful_of_statements_however_many_observations(
        p6_conn, tmp_path):
    """The cost is the join, not the observation count: 80 observations or 8,000,
    the same three statements."""
    file_id, content_hash = _version(p6_conn, tmp_path, observations_per_run=200)
    statements: list[str] = []
    p6_conn.set_trace_callback(statements.append)
    try:
        pass_cache_key(p6_conn, file_id=file_id, content_hash=content_hash)
    finally:
        p6_conn.set_trace_callback(None)
    assert len(statements) <= 3, statements
