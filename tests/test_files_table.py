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


# ---------------------------------------------------------------------------
# The `files` row grew `st_dev`/`st_ino` so identity resolution could stop reading
# the whole duplicate family. `create_schema` is `CREATE TABLE IF NOT EXISTS`, so a
# column added to the DDL reaches a NEW database and no other.
# ---------------------------------------------------------------------------

#: `files` exactly as it stood before the identity columns were added. Written out
#: rather than derived, because a migration test that builds the old table from the
#: new DDL tests nothing.
_FILES_DDL_BEFORE_THE_IDENTITY_COLUMNS = """
CREATE TABLE files (
    file_id                   TEXT PRIMARY KEY,
    current_path              TEXT NOT NULL,
    filename                  TEXT NOT NULL,
    normalized_filename       TEXT NOT NULL,
    extension                 TEXT NOT NULL,
    directory_position        TEXT,
    volume_id                 TEXT,
    content_hash              TEXT NOT NULL,
    hash_algorithm            TEXT NOT NULL,
    observed_size             INTEGER NOT NULL,
    observed_timestamps       TEXT NOT NULL,
    mime_type                 TEXT,
    detected_format           TEXT,
    scan_state                TEXT NOT NULL,
    extraction_status_by_tier TEXT NOT NULL DEFAULT '{}',
    sensitivity_state         TEXT
);
CREATE INDEX files_content_hash ON files (content_hash);
CREATE INDEX files_current_path ON files (current_path);
"""


def _database_written_before_the_identity_columns(tmp_path: Path, recorded: Path):
    import sqlite3

    from database_agent.identity import HASH_ALGORITHM, hash_file

    path = tmp_path / "before.sqlite"
    raw = sqlite3.connect(path)
    raw.executescript(_FILES_DDL_BEFORE_THE_IDENTITY_COLUMNS)
    raw.execute(
        "INSERT INTO files (file_id, current_path, filename, normalized_filename, "
        "extension, content_hash, hash_algorithm, observed_size, "
        "observed_timestamps, scan_state) VALUES (?,?,?,?,?,?,?,?,'{}','scanned')",
        ("legacy-1", str(recorded), recorded.name, recorded.name, recorded.suffix,
         hash_file(recorded, materialized=True), HASH_ALGORITHM,
         recorded.stat().st_size),
    )
    raw.commit()
    raw.close()
    return path


def test_a_database_written_before_the_identity_columns_gains_them(tmp_path: Path):
    from database_agent.db import FILES_ADDED_COLUMNS, open_database

    recorded = tmp_path / "recorded.bin"
    recorded.write_bytes(b"identical bytes")
    conn = open_database(_database_written_before_the_identity_columns(
        tmp_path, recorded))
    try:
        columns = tuple(r["name"] for r in conn.execute("PRAGMA table_info(files)"))
        # Same order as a database created today: P7 pins that equality, and
        # ALTER TABLE ADD COLUMN appends, so the two agree only if the DDL declares
        # the added columns last and in this order.
        assert columns == FILES_COLUMNS
        assert columns[-len(FILES_ADDED_COLUMNS):] == tuple(
            name for name, _ in FILES_ADDED_COLUMNS)
        legacy = get_file(conn, "legacy-1")
        assert legacy["st_dev"] is None and legacy["st_ino"] is None
        assert legacy["current_path"] == str(recorded)
    finally:
        conn.close()


def test_a_row_migrated_without_an_inode_claims_no_other_file(tmp_path: Path):
    """A migrated row remembers no inode, and SQL equality never matches NULL — so
    it can never be handed another file's identity by the index. It still answers
    for its own path, and it is still the row a move relocates."""
    from database_agent.db import open_database
    from database_agent.files_table import observe_path
    from p1_contract import p3_basic_record

    recorded = tmp_path / "recorded.bin"
    recorded.write_bytes(b"identical bytes")
    conn = open_database(_database_written_before_the_identity_columns(
        tmp_path, recorded))
    try:
        def observe(target):
            return observe_path(conn, target, author="P3",
                                component_version="p3-fixture",
                                parent_folder_context=None, mime_type=None,
                                detected_format=None, scan_state="scanned",
                                materialized=True, **p3_basic_record(target))

        assert observe(recorded) == "legacy-1"          # its own path, unchanged

        twin = tmp_path / "twin.bin"
        twin.write_bytes(b"identical bytes")
        twin_id = observe(twin)
        assert twin_id != "legacy-1", "a NULL inode matched another file"

        moved = tmp_path / "moved.bin"
        moved.write_bytes(b"identical bytes")
        recorded.unlink()
        assert observe(moved) == "legacy-1", (
            "the migrated row stopped answering for its own bytes once its recorded "
            "path was gone")
    finally:
        conn.close()


def test_identity_resolution_reaches_its_rows_by_index_and_never_by_scan(
        tmp_path: Path):
    """The two questions `observe_path` asks when the exact path misses. Both must
    SEARCH, and the oldest-home probe must reach the first row in rowid order without
    sorting — a temp b-tree there would materialise the whole duplicate family to
    return one row, which is the cost the family walk was removed to avoid.
    """
    from database_agent.db import open_database

    conn = open_database(tmp_path / "agent.sqlite")
    try:
        for sql, arguments in (
            ("SELECT file_id, current_path FROM files WHERE st_dev = ? AND "
             "st_ino = ? AND content_hash = ? AND scan_state != ? ORDER BY rowid",
             (1, 2, "h", "superseded_content")),
            ("SELECT file_id, current_path FROM files WHERE content_hash = ? AND "
             "scan_state != ? ORDER BY rowid LIMIT 1", ("h", "superseded_content")),
        ):
            steps = [r["detail"] for r in
                     conn.execute("EXPLAIN QUERY PLAN " + sql, arguments)]
            assert any(s.startswith("SEARCH files") for s in steps), (sql, steps)
            assert not any("SCAN files" in s for s in steps), (sql, steps)
            assert not any("TEMP B-TREE" in s.upper() for s in steps), (sql, steps)
    finally:
        conn.close()
