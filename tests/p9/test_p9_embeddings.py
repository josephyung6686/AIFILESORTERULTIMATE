# tests/p9/test_p9_embeddings.py
"""P9 Task 5 — P9 computes, P1 stores, and nothing here defaults.

Every input to an embedding is injected: which model, which version, which text
scope, which encoder. P9 defines no default scope and never implicitly
concatenates a whole file — what a vector was computed over is part of what it
means, and a silent default would make two vectors incomparable while looking
identical.

The invalidation rule is the one that matters downstream. A vector belongs to a
FILE VERSION. A new content hash never reuses the prior vector, because a
similarity computed against stale text is a similarity to a document that no
longer exists.

Off means off: no text read, no encoder call, no P1 write.
"""
from __future__ import annotations

import pytest

from database_agent.db import create_schema
from database_agent.vector_versions import current_embedding, embedding_history
from grouping.embeddings import (
    EmbeddingConfig,
    EmbeddingsOff,
    EmbeddingsOn,
    EncodedVector,
    EncoderContractViolation,
    ensure_file_embedding,
    recompute_file_embedding,
)

T0 = "2026-08-26T00:00:00Z"
T1 = "2026-08-26T00:01:00Z"

CONFIG = EmbeddingConfig(
    model_id="fixture-encoder",
    model_version="1",
    scope="extracted_text",
    encoding="fixture-bytes",
    dimension=3,
)
IDENTITY = dict(
    scope=CONFIG.scope,
    embedding_model_id=CONFIG.model_id,
    embedding_version=CONFIG.model_version,
)


@pytest.fixture()
def vector_conn(conn):
    create_schema(conn)
    return conn


class Encoder:
    """Records every call, so "never encoded" is provable rather than assumed."""

    def __init__(self, *, dimension: int | None = None, encoding: str | None = None):
        self.calls: list[tuple[str, EmbeddingConfig]] = []
        self._dimension = dimension
        self._encoding = encoding

    def __call__(self, text: str, config: EmbeddingConfig) -> EncodedVector:
        self.calls.append((text, config))
        return EncodedVector(
            array_bytes=text.encode("utf-8"),
            dimension=self._dimension if self._dimension is not None
            else config.dimension,
            encoding=self._encoding if self._encoding is not None
            else config.encoding,
        )


class TextFor:
    def __init__(self, text: str | None = "the extracted text"):
        self.calls: list[tuple[str, str, str]] = []
        self._text = text

    def __call__(self, conn, file_id: str, content_hash: str, scope: str):
        self.calls.append((file_id, content_hash, scope))
        return self._text


def _ensure(conn, *, encoder=None, text_for=None, enabled=True, config=CONFIG,
            file_id="f1", content_hash="h1", created_at=T0):
    return ensure_file_embedding(
        conn, file_id=file_id, content_hash=content_hash, config=config,
        encoder=encoder, embedding_text_for=text_for,
        embeddings_enabled=enabled, created_at=created_at,
    )


# --- off means off --------------------------------------------------------------


def test_embeddings_off_never_reads_text_calls_encoder_or_writes(vector_conn):
    encoder, text_for = Encoder(), TextFor()
    result = _ensure(vector_conn, encoder=encoder, text_for=text_for, enabled=False)
    assert result is None
    assert encoder.calls == []
    assert text_for.calls == []
    assert vector_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings"
    ).fetchone()["c"] == 0


def test_embeddings_off_needs_no_config_encoder_or_reader_at_all(vector_conn):
    assert _ensure(vector_conn, config=None, enabled=False) is None


def test_the_off_runtime_carries_nothing_to_misconfigure():
    off = EmbeddingsOff()
    assert off.enabled is False
    assert not hasattr(off, "encoder")
    assert not hasattr(off, "config")


# --- enabled mode refuses an incomplete runtime ---------------------------------


@pytest.mark.parametrize("missing", ["config", "encoder", "text_for"])
def test_enabled_mode_refuses_a_missing_injected_input(vector_conn, missing):
    kwargs = dict(config=CONFIG, encoder=Encoder(), text_for=TextFor())
    kwargs[missing] = None
    with pytest.raises(ValueError):
        _ensure(vector_conn, **kwargs)
    assert vector_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings"
    ).fetchone()["c"] == 0


@pytest.mark.parametrize(
    "field", ["model_id", "model_version", "scope", "encoding"],
)
def test_configuration_requires_every_identifying_string(field):
    import dataclasses

    with pytest.raises(ValueError):
        dataclasses.replace(CONFIG, **{field: ""})


@pytest.mark.parametrize("dimension", [0, -1])
def test_configuration_requires_a_positive_dimension(dimension):
    import dataclasses

    with pytest.raises(ValueError):
        dataclasses.replace(CONFIG, dimension=dimension)


def test_an_enabled_runtime_rejects_a_non_callable_dependency():
    """An incomplete enabled runtime must not reach retrieval."""
    with pytest.raises((TypeError, ValueError)):
        EmbeddingsOn(
            config=CONFIG, encoder="not a callable",
            embedding_text_for=TextFor(), eligible_versions_for=lambda *a: (),
        )


def test_a_complete_enabled_runtime_is_accepted():
    runtime = EmbeddingsOn(
        config=CONFIG, encoder=Encoder(), embedding_text_for=TextFor(),
        eligible_versions_for=lambda *a: (),
    )
    assert runtime.enabled is True
    assert runtime.config is CONFIG


# --- the encoder contract -------------------------------------------------------


@pytest.mark.parametrize(
    ("kwargs", "why"),
    [
        ({"dimension": 5}, "dimension"),
        ({"encoding": "other-bytes"}, "encoding"),
    ],
)
def test_an_encoder_that_contradicts_configuration_writes_nothing(
    vector_conn, kwargs, why,
):
    """P1 stores opaque bytes and cannot catch this. P9 is the boundary."""
    encoder = Encoder(**kwargs)
    with pytest.raises(EncoderContractViolation) as excinfo:
        _ensure(vector_conn, encoder=encoder, text_for=TextFor())
    assert why in str(excinfo.value)
    assert vector_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings"
    ).fetchone()["c"] == 0


def test_the_encoder_sees_the_configured_scope_and_nothing_else(vector_conn):
    encoder, text_for = Encoder(), TextFor()
    _ensure(vector_conn, encoder=encoder, text_for=text_for)
    assert text_for.calls == [("f1", "h1", "extracted_text")]
    assert encoder.calls[0][0] == "the extracted text"
    assert encoder.calls[0][1] is CONFIG


# --- an empty scope is an omission, not a vector --------------------------------


@pytest.mark.parametrize("empty", [None, "", "   "])
def test_an_empty_text_scope_records_no_vector(vector_conn, empty):
    encoder = Encoder()
    result = _ensure(vector_conn, encoder=encoder, text_for=TextFor(empty))
    assert result is None
    assert encoder.calls == []
    assert vector_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings"
    ).fetchone()["c"] == 0


# --- one vector per file version ------------------------------------------------


def test_content_version_change_never_reuses_the_prior_vector(vector_conn):
    encoder, text_for = Encoder(), TextFor()
    old = _ensure(vector_conn, encoder=encoder, text_for=text_for,
                  content_hash="h1", created_at=T0)
    new = _ensure(vector_conn, encoder=encoder, text_for=text_for,
                  content_hash="h2", created_at=T1)
    assert old.embedding_id != new.embedding_id
    assert old.content_hash == "h1"
    assert new.content_hash == "h2"
    assert current_embedding(
        vector_conn, file_id="f1", content_hash="h1", **IDENTITY) == old
    assert current_embedding(
        vector_conn, file_id="f1", content_hash="h2", **IDENTITY) == new


def test_an_existing_exact_record_is_returned_without_re_encoding(vector_conn):
    encoder, text_for = Encoder(), TextFor()
    first = _ensure(vector_conn, encoder=encoder, text_for=text_for)
    again = _ensure(vector_conn, encoder=encoder, text_for=text_for, created_at=T1)
    assert again == first
    assert len(encoder.calls) == 1
    assert len(embedding_history(
        vector_conn, file_id="f1", content_hash="h1", scope=CONFIG.scope)) == 1


def test_a_different_model_version_is_a_different_vector(vector_conn):
    import dataclasses

    encoder, text_for = Encoder(), TextFor()
    _ensure(vector_conn, encoder=encoder, text_for=text_for)
    _ensure(vector_conn, encoder=encoder, text_for=text_for,
            config=dataclasses.replace(CONFIG, model_version="2"), created_at=T1)
    assert len(encoder.calls) == 2
    assert len(embedding_history(
        vector_conn, file_id="f1", content_hash="h1", scope=CONFIG.scope)) == 2


# --- recompute is explicit and carries a reason ---------------------------------


def test_recompute_supersedes_and_requires_a_reason(vector_conn):
    encoder, text_for = Encoder(), TextFor()
    first = _ensure(vector_conn, encoder=encoder, text_for=text_for)
    second = recompute_file_embedding(
        vector_conn, file_id="f1", content_hash="h1", config=CONFIG,
        encoder=encoder, embedding_text_for=TextFor("new extracted text"),
        created_at=T1, supersede_reason="extractor upgraded",
    )
    assert second.embedding_id != first.embedding_id
    history = embedding_history(
        vector_conn, file_id="f1", content_hash="h1", scope=CONFIG.scope)
    assert [row.embedding_id for row in history] == [
        first.embedding_id, second.embedding_id,
    ]
    assert history[0].superseded_by == second.embedding_id


def test_recompute_without_a_reason_is_refused(vector_conn):
    encoder, text_for = Encoder(), TextFor()
    _ensure(vector_conn, encoder=encoder, text_for=text_for)
    with pytest.raises(ValueError):
        recompute_file_embedding(
            vector_conn, file_id="f1", content_hash="h1", config=CONFIG,
            encoder=encoder, embedding_text_for=text_for, created_at=T1,
            supersede_reason="",
        )


# --- P9 never touches the legacy overwrite store --------------------------------


def test_p9_never_calls_the_legacy_put_embedding():
    import ast
    import pathlib

    import grouping

    root = pathlib.Path(grouping.__file__).resolve().parent
    offenders = []
    for path in sorted(root.glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Name) and node.id in {
                "put_embedding", "get_embedding",
            }:
                offenders.append(f"{path.name}:{node.lineno}:{node.id}")
    assert offenders == [], offenders


def test_p9_publishes_no_similarity_query():
    import grouping.embeddings as module

    names = [name.lower() for name in dir(module) if not name.startswith("_")]
    for banned in ("similar", "nearest", "cosine", "knn"):
        assert not any(banned in name for name in names), banned
