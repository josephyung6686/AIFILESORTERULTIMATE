import pytest

from database_agent.supersede import (
    SUPERSEDE_COLUMNS, chain, mark_superseded, supersede_ddl,
)


def _make_table(conn):
    conn.executescript(
        "CREATE TABLE extraction_records (record_id TEXT PRIMARY KEY, value TEXT, "
        + supersede_ddl("extraction_records") + ");"
    )


def test_the_three_shared_columns_are_exactly_these():
    assert SUPERSEDE_COLUMNS == ("supersedes", "superseded_by", "supersede_reason")


def test_supersession_reason_is_not_an_alias():
    # M1: the spelling is supersede_reason. supersession_reason is not accepted.
    assert "supersession_reason" not in SUPERSEDE_COLUMNS
    assert "supersession_reason" not in supersede_ddl("t")


def test_preferred_is_not_in_the_shared_set():
    # M1: `preferred` is carried on P6's file_facts only.
    assert "preferred" not in SUPERSEDE_COLUMNS


def test_the_8_2_ocr_case_keeps_both_records_readable(conn):
    # §8.2's worked case is normative: a first OCR pass producing unreadable text
    # and a later engine that recovers a university name must BOTH remain available.
    _make_table(conn)
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r1', 'unreadable')")
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r2', 'recovered')")
    mark_superseded(conn, "extraction_records", old_id="r1", new_id="r2",
                    reason="improved OCR engine")

    old = conn.execute("SELECT * FROM extraction_records WHERE record_id='r1'").fetchone()
    new = conn.execute("SELECT * FROM extraction_records WHERE record_id='r2'").fetchone()
    assert old is not None and old["value"] == "unreadable"
    assert old["superseded_by"] == "r2"
    assert old["supersede_reason"] == "improved OCR engine"
    assert new["supersedes"] == "r1"
    assert [r["record_id"] for r in chain(conn, "extraction_records", "r1")] == ["r1", "r2"]


def test_superseding_never_deletes_or_mutates_the_old_value(conn):
    _make_table(conn)
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r1', 'original')")
    conn.execute("INSERT INTO extraction_records (record_id, value) VALUES ('r2', 'newer')")
    mark_superseded(conn, "extraction_records", old_id="r1", new_id="r2", reason="x")
    assert conn.execute(
        "SELECT value FROM extraction_records WHERE record_id='r1'"
    ).fetchone()["value"] == "original"


def test_the_newest_record_is_not_automatically_preferred(conn):
    # §8.2 says the resolver MAY mark it — preference is an explicit act, and not P1's.
    _make_table(conn)
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(extraction_records)")]
    assert "preferred" not in cols
