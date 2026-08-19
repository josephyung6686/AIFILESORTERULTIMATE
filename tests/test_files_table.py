from pathlib import Path

import pytest

from database_agent.db import create_schema
from p1_contract import p3_basic_record
from database_agent.files_table import FILES_COLUMNS, get_file, record_file


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
