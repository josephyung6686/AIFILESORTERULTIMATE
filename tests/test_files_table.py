import json
from pathlib import Path

import pytest

from database_agent.db import create_schema
from p1_contract import p3_basic_record
from database_agent.files_table import (
    FILES_COLUMNS, get_file, invalidate_extraction_state, record_file)


def _p3_fields(path=None, **overrides):
    """The §1.2 fields P3 hands P1 (SPEC Contract in). A test stands in for P3;
    P1 never derives any of these itself."""
    fields = dict(parent_folder_context="corpus", mime_type="application/pdf",
                  detected_format="pdf", scan_state="scanned", materialized=True)
    if path is not None:
        fields.update(p3_basic_record(path))
    fields.update(overrides)
    return fields


def test_record_file_writes_every_column(conn, sample_file: Path):
    create_schema(conn)
    file_id = record_file(conn, sample_file, **_p3_fields(sample_file))
    row = get_file(conn, file_id)
    for column in FILES_COLUMNS:
        assert column in row.keys(), f"missing column {column}"
    assert row["content_hash"]
    assert row["hash_algorithm"]
    assert row["volume_id"]
    assert row["current_path"] == str(sample_file)
    assert row["filename"] == "Syllabus.pdf"
    assert row["extension"] == ".pdf"
    assert row["directory_position"] == "corpus"
    # stored exactly as handed over — P1 derives none of these
    assert row["mime_type"] == "application/pdf"
    assert row["detected_format"] == "pdf"
    assert row["scan_state"] == "scanned"


def test_p3_supplied_fields_have_no_defaults(conn, sample_file: Path):
    # Contract in: P3 supplies MIME type, detected format and scan state. P1 stores
    # them; it does not guess them. Omitting one is a TypeError, not a silent guess.
    create_schema(conn)
    with pytest.raises(TypeError):
        record_file(conn, sample_file, parent_folder_context="corpus")


def test_volume_id_is_nullable(conn, sample_file: Path):
    # P1 OQ9 is open; a caller with no usable volume identifier stores NULL rather
    # than a value a later session could compare against.
    create_schema(conn)
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, normalized_filename, "
        "extension, volume_id, content_hash, hash_algorithm, observed_size, "
        "observed_timestamps, scan_state) "
        "VALUES ('f-null', '/x', 'x', 'x', '', NULL, 'h', 'sha256', 1, '{}', 'scanned')"
    )
    assert get_file(conn, "f-null")["volume_id"] is None


def test_files_table_holds_no_vectors(conn):
    create_schema(conn)
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(files)")]
    for forbidden in ("embedding", "vector", "array"):
        assert not any(forbidden in c.lower() for c in cols)


def test_no_preferred_column_on_p1_tables(conn):
    # M1: `preferred` is carried on P6's file_facts only. P1 creates no such column.
    create_schema(conn)
    for table in ("files", "events"):
        cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
        assert "preferred" not in cols


def test_p1_publishes_a_writer_for_extraction_status_by_tier(conn, sample_file):
    """The column existed with a reset and no setter: P5 could compute the map and
    P1 had nowhere to put it, so `files` stayed `{}` after a real extraction."""
    from database_agent.files_table import set_extraction_status
    file_id = record_file(conn, sample_file, **_p3_fields(sample_file))
    set_extraction_status(conn, file_id, status_by_tier={"native": "complete"},
                          author="P5", component_version="1.0")
    assert json.loads(get_file(conn, file_id)["extraction_status_by_tier"]) == {
        "native": "complete"}


def test_p1_holds_no_tier_vocabulary_and_stores_what_it_is_given(conn, sample_file):
    """I4's four tiers are P4's vocabulary, not P1's. P1 stores an opaque map for the
    same reason it stores an opaque `sensitivity_state`: interpreting it here would be
    a second home for a vocabulary another part owns."""
    from database_agent.files_table import set_extraction_status
    file_id = record_file(conn, sample_file, **_p3_fields(sample_file))
    set_extraction_status(conn, file_id, status_by_tier={"a-tier-p1-never-heard-of": "x"},
                          author="P5", component_version="1.0")
    assert json.loads(get_file(conn, file_id)["extraction_status_by_tier"]) == {
        "a-tier-p1-never-heard-of": "x"}


def test_invalidation_clears_a_status_a_caller_had_set(conn, sample_file):
    """R3: new bytes invalidate the extraction state, whatever it had reached."""
    from database_agent.files_table import set_extraction_status
    file_id = record_file(conn, sample_file, **_p3_fields(sample_file))
    set_extraction_status(conn, file_id, status_by_tier={"native": "complete"},
                          author="P5", component_version="1.0")
    invalidate_extraction_state(conn, file_id, author="P5", component_version="1.0")
    assert get_file(conn, file_id)["extraction_status_by_tier"] == "{}"


# ------------------------------------------------- D2: `sensitivity_state` (§8.4)
def test_p1_publishes_a_writer_for_sensitivity_state(conn, sample_file):
    """The twin of `set_extraction_status`, and for the identical reason.

    `sensitivity_state` has been a column on `files` since the first schema with
    NOTHING able to write it -- a column with no writer, which is this project's
    recurring defect class. Every reader therefore saw NULL and could not tell
    "not yet classified" from "classified as carrying nothing", and the Wave-2
    caller passed the NULL on to a bundle field that means something else.

    D2, ratified 2026-08-21: P7's `ClassificationRecord` keyed `(file_id,
    content_hash)` is authoritative and P1's column is its projection -- the same
    shape as `extraction_status_by_tier`, where P5 computes and P1 stores.
    """
    from database_agent.files_table import set_sensitivity_state
    file_id = record_file(conn, sample_file, **_p3_fields(sample_file))
    assert get_file(conn, file_id)["sensitivity_state"] is None
    set_sensitivity_state(conn, file_id, state={"handling_class": "local_only"},
                          author="P7", component_version="1.0")
    assert json.loads(get_file(conn, file_id)["sensitivity_state"]) == {
        "handling_class": "local_only"}


def test_p1_holds_no_handling_class_vocabulary(conn, sample_file):
    """§8.4's handling classes are P7's. P1 stores the state opaquely for the same
    reason it stores the tier map opaquely: validating the values here would put one
    vocabulary in two homes."""
    from database_agent.files_table import set_sensitivity_state
    file_id = record_file(conn, sample_file, **_p3_fields(sample_file))
    set_sensitivity_state(conn, file_id,
                          state={"a-class-p1-never-heard-of": ["why"]},
                          author="P7", component_version="1.0")
    assert json.loads(get_file(conn, file_id)["sensitivity_state"]) == {
        "a-class-p1-never-heard-of": ["why"]}


def test_p1_appends_no_event_of_its_own_for_a_classification(conn, sample_file):
    """M8: the acting part authors, P1 stores. P7 appends its own §8.4 audit record;
    P1 minting one here would name the storage substrate as the classifier."""
    from database_agent.files_table import set_sensitivity_state
    file_id = record_file(conn, sample_file, **_p3_fields(sample_file))
    before = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    set_sensitivity_state(conn, file_id, state={"handling_class": "local_only"},
                          author="P7", component_version="1.0")
    assert conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before
