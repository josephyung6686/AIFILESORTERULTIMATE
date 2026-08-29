# tests/test_vector_versions.py
"""P9 Task 1 — P1's versioned embedding records.

The legacy store is `vector_arrays(subject_key PRIMARY KEY, array_bytes,
producer_version)` with `ON CONFLICT DO UPDATE`. It overwrites, and it carries no
file version, scope, model id or version, dimension, encoding, creation time, or
supersession history — so a recomputed vector destroys the one it replaces and
nothing can say which model produced either. P9 needs a vector it can cite.

This table is additive. Legacy rows are not migrated or reinterpreted: they lack
the metadata required to do that safely.

P1 stays an opaque-byte store. It checks that `dimension > 0` and that the
identifying strings are non-empty; it does not infer a codec or claim that the
byte length matches the dimension. P9's injected encoder owns that.
"""
from __future__ import annotations

import sqlite3

import pytest

from database_agent.db import create_schema
from database_agent.vector_versions import (
    AmbiguousCurrentEmbedding,
    EmbeddingRecord,
    current_embedding,
    embedding_history,
    record_embedding,
)

T0 = "2026-08-25T00:00:00Z"
T1 = "2026-08-25T00:01:00Z"
T2 = "2026-08-25T00:02:00Z"

IDENTITY = dict(
    file_id="f1",
    content_hash="h1",
    scope="extracted_text",
    embedding_model_id="fixture-model",
    embedding_version="1",
)


@pytest.fixture()
def vector_conn(conn):
    create_schema(conn)
    return conn


def _record(conn, **overrides):
    values = dict(
        **IDENTITY,
        dimension=2,
        encoding="fixture-bytes",
        array_bytes=b"first",
        created_at=T0,
    )
    values.update(overrides)
    return record_embedding(conn, **values)


def _current(conn, **overrides):
    values = dict(IDENTITY)
    values.update(overrides)
    return current_embedding(conn, **values)


# --- append and supersede -------------------------------------------------------


def test_recompute_supersedes_without_overwriting(vector_conn):
    first = _record(vector_conn)
    second = _record(
        vector_conn,
        array_bytes=b"second",
        created_at=T1,
        supersede_reason="recomputed after extractor upgrade",
    )
    rows = embedding_history(
        vector_conn, file_id="f1", content_hash="h1", scope="extracted_text",
    )
    assert [row.array_bytes for row in rows] == [b"first", b"second"]
    assert rows[0].superseded_by == second
    assert rows[0].supersede_reason == "recomputed after extractor upgrade"
    assert rows[1].supersedes == first
    assert _current(vector_conn).embedding_id == second


def test_the_superseded_row_stays_readable(vector_conn):
    first = _record(vector_conn)
    _record(vector_conn, array_bytes=b"second", created_at=T1,
            supersede_reason="recomputed")
    rows = embedding_history(
        vector_conn, file_id="f1", content_hash="h1", scope="extracted_text",
    )
    assert rows[0].embedding_id == first
    assert rows[0].array_bytes == b"first"
    assert isinstance(rows[0], EmbeddingRecord)


def test_superseding_an_existing_vector_requires_a_reason(vector_conn):
    _record(vector_conn)
    with pytest.raises(ValueError):
        _record(vector_conn, array_bytes=b"second", created_at=T1)


def test_the_first_write_needs_no_reason(vector_conn):
    embedding_id = _record(vector_conn)
    assert _current(vector_conn).embedding_id == embedding_id
    assert _current(vector_conn).supersedes is None


# --- identity is exact ----------------------------------------------------------


def test_a_new_content_hash_never_returns_the_prior_vector(vector_conn):
    _record(vector_conn)
    assert _current(vector_conn, content_hash="h2") is None
    _record(vector_conn, content_hash="h2", array_bytes=b"other", created_at=T1)
    assert _current(vector_conn, content_hash="h2").array_bytes == b"other"
    assert _current(vector_conn).array_bytes == b"first"


@pytest.mark.parametrize(
    "field", ["scope", "embedding_model_id", "embedding_version"],
)
def test_a_different_model_scope_or_version_is_a_different_vector(vector_conn, field):
    _record(vector_conn)
    assert _current(vector_conn, **{field: "other"}) is None
    _record(vector_conn, **{field: "other"}, array_bytes=b"other", created_at=T1)
    assert _current(vector_conn, **{field: "other"}).array_bytes == b"other"
    assert _current(vector_conn).array_bytes == b"first"


def test_history_spans_every_model_and_version_for_one_file_version(vector_conn):
    _record(vector_conn)
    _record(vector_conn, embedding_model_id="other", array_bytes=b"other",
            created_at=T1)
    rows = embedding_history(
        vector_conn, file_id="f1", content_hash="h1", scope="extracted_text",
    )
    assert {row.embedding_model_id for row in rows} == {"fixture-model", "other"}


# --- required metadata ----------------------------------------------------------


@pytest.mark.parametrize(
    "field",
    ["content_hash", "scope", "embedding_model_id", "embedding_version", "encoding",
     "created_at", "file_id"],
)
def test_identifying_strings_are_required(vector_conn, field):
    with pytest.raises(ValueError):
        _record(vector_conn, **{field: ""})


@pytest.mark.parametrize("dimension", [0, -1])
def test_dimension_must_be_positive(vector_conn, dimension):
    with pytest.raises(ValueError):
        _record(vector_conn, dimension=dimension)


def test_array_bytes_must_be_bytes(vector_conn):
    with pytest.raises(TypeError):
        _record(vector_conn, array_bytes="not bytes")


def test_p1_does_not_check_byte_length_against_dimension(vector_conn):
    """P1 is an opaque-byte store. The encoder owns serialization (P9 Task 5)."""
    embedding_id = _record(vector_conn, dimension=768, array_bytes=b"two")
    assert _current(vector_conn).embedding_id == embedding_id
    assert _current(vector_conn).dimension == 768


# --- the current-row invariant --------------------------------------------------


def test_exact_vector_identity_has_at_most_one_current_row(vector_conn):
    _record(vector_conn, array_bytes=b"one")
    with pytest.raises(sqlite3.IntegrityError):
        vector_conn.execute(
            "INSERT INTO vector_embeddings "
            "(embedding_id,file_id,content_hash,scope,embedding_model_id,"
            "embedding_version,dimension,encoding,array_bytes,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            ("illegal-second-current", "f1", "h1", "extracted_text",
             "fixture-model", "1", 2, "fixture-bytes", b"two", T1),
        )


def test_ambiguous_legacy_current_state_is_rejected_before_write(vector_conn):
    """A malformed store is repaired deliberately, not written through."""
    vector_conn.execute("DROP INDEX one_current_vector_embedding")
    for embedding_id, payload in (("bad-1", b"one"), ("bad-2", b"two")):
        vector_conn.execute(
            "INSERT INTO vector_embeddings "
            "(embedding_id,file_id,content_hash,scope,embedding_model_id,"
            "embedding_version,dimension,encoding,array_bytes,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (embedding_id, "f1", "h1", "extracted_text", "fixture-model", "1", 2,
             "fixture-bytes", payload, T0),
        )
    with pytest.raises(AmbiguousCurrentEmbedding):
        _record(vector_conn, array_bytes=b"three", created_at=T2,
                supersede_reason="repair attempt")
    rows = vector_conn.execute(
        "SELECT embedding_id FROM vector_embeddings ORDER BY rowid"
    ).fetchall()
    assert [row["embedding_id"] for row in rows] == ["bad-1", "bad-2"]


def test_a_failed_successor_insert_leaves_the_predecessor_current(vector_conn):
    """The predecessor is marked superseded before the successor exists.

    If that update survived a failed insert, the identity would have no current
    row at all: the old vector hidden and the new one never written.
    """
    first = _record(vector_conn)
    # Test-only, in this isolated temporary database: make the successor insert
    # fail after the predecessor has already been marked.
    vector_conn.execute(
        "CREATE TRIGGER refuse_insert BEFORE INSERT ON vector_embeddings "
        "BEGIN SELECT RAISE(ABORT, 'fixture refuses this insert'); END"
    )
    with pytest.raises(sqlite3.IntegrityError):
        _record(vector_conn, array_bytes=b"second", created_at=T1,
                supersede_reason="recomputed")
    vector_conn.execute("DROP TRIGGER refuse_insert")
    assert _current(vector_conn).embedding_id == first
    assert _current(vector_conn).superseded_by is None
    assert _current(vector_conn).supersede_reason is None


# --- the legacy store is untouched ----------------------------------------------


def test_the_legacy_overwrite_table_still_exists_and_is_separate(vector_conn):
    tables = {
        row["name"]
        for row in vector_conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert "vector_arrays" in tables
    assert "vector_embeddings" in tables
    _record(vector_conn)
    assert vector_conn.execute(
        "SELECT count(*) AS c FROM vector_arrays"
    ).fetchone()["c"] == 0


def test_p1_still_exposes_no_similarity_query():
    import database_agent.vector_versions as module

    names = [name.lower() for name in dir(module) if not name.startswith("_")]
    for banned in ("similar", "nearest", "cosine", "knn", "search"):
        assert not any(banned in name for name in names), banned
