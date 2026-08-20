# tests/p4/test_p4_schema.py
import pytest

from database_agent.db import create_schema
from database_agent.supersede import chain, mark_superseded

from evidence_shape.observation import OBSERVATION_ROW_FIELDS
from evidence_shape.runs import RUN_FIELDS
from evidence_shape.schema import SUPERSEDE_ADAPTER_COLUMN, create_evidence_schema
from evidence_shape.text_units import TEXT_UNIT_FIELDS

P1_TABLES = {"files", "events", "learning_resets", "budget_ceilings", "vector_arrays",
             "scan_resource_usage"}


def _columns(conn, table):
    return [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]


def _insert_run(conn, run_id="r1", **overrides):
    values = dict(run_id=run_id, file_id="f1", content_hash="sha256:abc",
                  extractor_name="pdf.text", extractor_version="3.1.0",
                  source_type="text_document", analysis_tier="native", config="{}",
                  config_fingerprint="sha256:cfg", completeness="complete",
                  coverage=None, observation_count=0, started_at="t0",
                  finished_at="t1", failure_reason=None)
    values.update(overrides)
    conn.execute(
        f"INSERT INTO extraction_runs ({','.join(values)}) "
        f"VALUES ({','.join('?' * len(values))})", list(values.values()))


def _insert_observation(conn, observation_id, run_id="r1", **overrides):
    values = dict(observation_id=observation_id, observation_key="sha256:k",
                  file_id="f1", content_hash="sha256:abc", extractor_name="pdf.text",
                  extractor_version="3.1.0", source_type="text_document",
                  raw_value="BUSIB 4300", normalized_value=None,
                  location='{"zone":"heading"}', context_before=None,
                  context_after=None, context_truncated=0, occurrence_count=3,
                  observed_at="t0", reliability="possible", run_id=run_id,
                  confidence=None, signal_tier=None, supersedes=None,
                  superseded_by=None, supersede_reason=None)
    values.update(overrides)
    conn.execute(
        f"INSERT INTO evidence ({','.join(values)}) "
        f"VALUES ({','.join('?' * len(values))})", list(values.values()))


def test_the_three_tables_exist_and_p1s_are_untouched(p4_conn):
    tables = {row["name"] for row in p4_conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert {"evidence", "extraction_runs", "text_units"} <= tables
    assert P1_TABLES <= tables


def test_creating_the_schema_twice_is_idempotent(p4_conn):
    create_evidence_schema(p4_conn)
    create_evidence_schema(p4_conn)
    assert len(_columns(p4_conn, "evidence")) == len(OBSERVATION_ROW_FIELDS)


def test_p1s_schema_function_still_runs_beside_it(p4_conn):
    create_schema(p4_conn)
    assert _columns(p4_conn, "files")


def test_the_evidence_columns_are_exactly_the_published_row_fields_in_order(p4_conn):
    assert _columns(p4_conn, "evidence") == list(OBSERVATION_ROW_FIELDS)


def test_the_run_and_unit_columns_are_exactly_their_published_fields_in_order(p4_conn):
    assert _columns(p4_conn, "extraction_runs") == list(RUN_FIELDS)
    assert _columns(p4_conn, "text_units") == list(TEXT_UNIT_FIELDS)


def test_the_one_adapter_column_is_hidden_generated_and_named(p4_conn):
    # It exists so P1's mark_superseded/chain, which key on `record_id`, work against
    # a table whose published primary key is `observation_id`. It stores nothing.
    assert SUPERSEDE_ADAPTER_COLUMN == "record_id"
    assert SUPERSEDE_ADAPTER_COLUMN not in _columns(p4_conn, "evidence")
    extended = {row["name"]: row["hidden"]
                for row in p4_conn.execute("PRAGMA table_xinfo(evidence)")}
    assert extended[SUPERSEDE_ADAPTER_COLUMN] == 2          # virtual generated
    assert set(extended) - set(OBSERVATION_ROW_FIELDS) == {SUPERSEDE_ADAPTER_COLUMN}


def test_p1s_supersede_functions_work_unchanged_against_the_evidence_table(p4_conn):
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    _insert_observation(p4_conn, "o2", extractor_version="4.0.0")
    mark_superseded(p4_conn, "evidence", old_id="o1", new_id="o2",
                    reason="a later improved OCR engine recovered the name")

    links = chain(p4_conn, "evidence", "o1")
    assert [row["observation_id"] for row in links] == ["o1", "o2"]
    assert links[0]["superseded_by"] == "o2"
    assert links[0]["supersede_reason"].startswith("a later improved")
    assert links[1]["supersedes"] == "o1"
    assert links[0]["raw_value"] == "BUSIB 4300"           # RAW-2: untouched


def test_an_observation_can_never_be_deleted(p4_conn):
    # §8.7: rejected proposals "must be stored with the evidence that produced them".
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM evidence WHERE observation_id = 'o1'")
    assert p4_conn.execute("SELECT count(*) c FROM evidence").fetchone()["c"] == 1


def test_the_seven_never_overwritten_fields_cannot_be_updated(p4_conn):
    # SPEC, Cross-cutting answers -> Provenance, "Never overwritten": raw_value,
    # location, occurrence_count, observed_at, extractor_name, extractor_version,
    # run_id. Improvement is insert + supersede, never update.
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    for column, value in (("raw_value", "BUSIB 4301"), ("location", "{}"),
                          ("occurrence_count", 9), ("observed_at", "t9"),
                          ("extractor_name", "ocr.apple_vision"),
                          ("extractor_version", "4.0.0"), ("run_id", "r2")):
        with pytest.raises(Exception):
            p4_conn.execute(
                f"UPDATE evidence SET {column} = ? WHERE observation_id = 'o1'",
                (value,))


def test_the_supersede_columns_are_outside_that_trigger_on_purpose(p4_conn):
    # Supersession is the one legal write to an existing row (§8.2).
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1")
    p4_conn.execute("UPDATE evidence SET superseded_by = 'o2', supersede_reason = 'x' "
                    "WHERE observation_id = 'o1'")
    assert p4_conn.execute(
        "SELECT superseded_by s FROM evidence").fetchone()["s"] == "o2"


def test_a_text_unit_is_never_rewritten_or_deleted(p4_conn):
    # Rule 4: "Superseding a run never rewrites or deletes the earlier run's units."
    _insert_run(p4_conn)
    p4_conn.execute("INSERT INTO text_units (run_id, container_path, unit_locator, "
                    "text, length, truncated) VALUES ('r1', '[]', '', 'hello', 5, 0)")
    with pytest.raises(Exception):
        p4_conn.execute("UPDATE text_units SET text = 'goodbye'")
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM text_units")


def test_a_run_is_never_deleted(p4_conn):
    _insert_run(p4_conn)
    with pytest.raises(Exception):
        p4_conn.execute("DELETE FROM extraction_runs WHERE run_id = 'r1'")


def test_an_observation_cannot_reference_a_run_that_does_not_exist(p4_conn):
    _insert_run(p4_conn)
    with pytest.raises(Exception):
        _insert_observation(p4_conn, "o9", run_id="missing")


def test_no_foreign_key_points_at_p1s_files_table(p4_conn):
    # Open question 2 -- whether an observation is owned by the content hash or by
    # the file record -- is unsettled, and a foreign key would answer it in DDL. P4
    # also has to be buildable with no `files` row, which is what lets P6 be built
    # entirely against P4's fixtures.
    for table in ("evidence", "extraction_runs", "text_units"):
        targets = {row["table"] for row in
                   p4_conn.execute(f"PRAGMA foreign_key_list({table})")}
        assert "files" not in targets
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1", file_id="a-file-that-was-never-scanned")


def test_both_file_id_and_content_hash_are_required_on_both_records(p4_conn):
    # §2.8's field list contains both, and P4 carries both, which is what makes the
    # contract buildable either way once Open question 2 closes.
    for table in ("evidence", "extraction_runs"):
        required = {row["name"] for row in p4_conn.execute(f"PRAGMA table_info({table})")
                    if row["notnull"]}
        assert {"file_id", "content_hash"} <= required


def test_the_cache_key_index_is_3_4s_tuple_and_is_not_unique(p4_conn):
    # §3.4: content hash + the exact process that produced it. Not unique, because a
    # re-run at the same key is legal and supersedes rather than replaces (§8.2).
    indexes = {row["name"]: row["unique"]
               for row in p4_conn.execute("PRAGMA index_list(extraction_runs)")}
    cache = [name for name in indexes if "cache_key" in name]
    assert cache, indexes
    assert indexes[cache[0]] == 0
    columns = [row["name"] for row in
               p4_conn.execute(f"PRAGMA index_info({cache[0]})")]
    assert columns == ["content_hash", "extractor_name", "extractor_version",
                       "config_fingerprint"]


def test_two_extractor_versions_may_share_one_observation_key(p4_conn):
    # MINOR 8's mechanism, at the storage layer: a unique index on observation_key
    # would make §8.5's cross-version diff impossible.
    _insert_run(p4_conn)
    _insert_observation(p4_conn, "o1", observation_key="sha256:same")
    _insert_observation(p4_conn, "o2", observation_key="sha256:same",
                        extractor_version="4.0.0")
    assert p4_conn.execute(
        "SELECT count(*) c FROM evidence WHERE observation_key = 'sha256:same'"
    ).fetchone()["c"] == 2
