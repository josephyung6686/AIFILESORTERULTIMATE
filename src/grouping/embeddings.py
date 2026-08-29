# src/grouping/embeddings.py
"""P9 computes the vector, P1 stores it. Every input is injected.

The design consumes embeddings in two places and no section assigned the
computation; this module is that assignment. It authors nothing: which model,
which version, which text scope and which encoder all arrive from the caller.

Two rules do the work.

**P9 defines no default scope and never implicitly concatenates a whole file.**
What a vector was computed over is part of what it means, so a silent default
would make two vectors incomparable while looking identical. Text arrives only
through `embedding_text_for(conn, file_id, content_hash, scope)`.

**A vector belongs to a file version.** A new content hash gets a new vector, and
the old one stays readable rather than being overwritten — a similarity computed
against stale text is a similarity to a document that no longer exists.

Embeddings can propose a neighbour and can never establish membership. That rule
lives in the retrieval and graph tasks; this module only makes the vector.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal

from database_agent.vector_versions import (
    EmbeddingRecord,
    current_embedding,
    record_embedding,
)


class EncoderContractViolation(RuntimeError):
    """An encoder returned something its configuration did not describe.

    P1 stores opaque bytes and cannot catch this: a 5-dimension vector filed under
    a 3-dimension identity is a type-correct lie, and the first thing that would
    notice is a similarity computation months later. P9 is the boundary.
    """


@dataclass(frozen=True)
class EmbeddingConfig:
    model_id: str
    model_version: str
    scope: str
    encoding: str
    dimension: int

    def __post_init__(self) -> None:
        for name in ("model_id", "model_version", "scope", "encoding"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"{name} identifies the vector; P9 supplies no default for it"
                )
        if (not isinstance(self.dimension, int) or isinstance(self.dimension, bool)
                or self.dimension <= 0):
            raise ValueError("dimension must be a positive integer")


@dataclass(frozen=True)
class EncodedVector:
    array_bytes: bytes
    dimension: int
    encoding: str


@dataclass(frozen=True)
class FileVersionRef:
    file_id: str
    content_hash: str


Encoder = Callable[[str, EmbeddingConfig], EncodedVector]
EmbeddingTextFor = Callable[[sqlite3.Connection, str, str, str], "str | None"]
EligibleEmbeddingVersions = Callable[
    [sqlite3.Connection, object, int], Sequence[FileVersionRef]
]


@dataclass(frozen=True)
class EmbeddingsOff:
    """Nothing to misconfigure. It carries no encoder and no configuration."""

    enabled: Literal[False] = False


@dataclass(frozen=True)
class EmbeddingsOn:
    config: EmbeddingConfig
    encoder: Encoder
    embedding_text_for: EmbeddingTextFor
    eligible_versions_for: EligibleEmbeddingVersions
    enabled: Literal[True] = True

    def __post_init__(self) -> None:
        if not isinstance(self.config, EmbeddingConfig):
            raise ValueError("config must be an EmbeddingConfig")
        for name in ("encoder", "embedding_text_for", "eligible_versions_for"):
            if not callable(getattr(self, name)):
                raise TypeError(
                    f"{name} must be callable; an incomplete enabled runtime "
                    "cannot be allowed to reach retrieval"
                )


EmbeddingRuntime = EmbeddingsOff | EmbeddingsOn


def _require_enabled_inputs(
    config: EmbeddingConfig | None,
    encoder: Encoder | None,
    embedding_text_for: EmbeddingTextFor | None,
) -> None:
    missing = [
        name
        for name, value in (
            ("config", config),
            ("encoder", encoder),
            ("embedding_text_for", embedding_text_for),
        )
        if value is None
    ]
    if missing:
        raise ValueError(
            f"embeddings are enabled and {missing} were not supplied; P9 authors "
            "no encoder, no scope and no model identity"
        )


def _encode(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    content_hash: str,
    config: EmbeddingConfig,
    encoder: Encoder,
    embedding_text_for: EmbeddingTextFor,
) -> EncodedVector | None:
    """Read the configured scope, encode it, and check the encoder kept its word.

    An empty scope returns None: there is nothing to embed, and a vector over no
    text would be a similarity anchor with no content behind it.
    """
    text = embedding_text_for(conn, file_id, content_hash, config.scope)
    if not isinstance(text, str) or not text.strip():
        return None
    vector = encoder(text, config)
    if not isinstance(vector, EncodedVector):
        raise EncoderContractViolation(
            "the encoder must return an EncodedVector declaring its dimension "
            "and encoding"
        )
    if vector.dimension != config.dimension:
        raise EncoderContractViolation(
            f"the encoder returned dimension {vector.dimension} under a "
            f"configuration declaring {config.dimension}"
        )
    if vector.encoding != config.encoding:
        raise EncoderContractViolation(
            f"the encoder returned encoding {vector.encoding!r} under a "
            f"configuration declaring {config.encoding!r}"
        )
    return vector


def ensure_file_embedding(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    content_hash: str,
    config: EmbeddingConfig | None,
    encoder: Encoder | None,
    embedding_text_for: EmbeddingTextFor | None,
    embeddings_enabled: bool,
    created_at: str,
) -> EmbeddingRecord | None:
    """The vector for one file version, computing it only if it does not exist.

    Disabled returns before touching text, encoder or P1. An exact existing record
    is returned without re-encoding: recomputing the same identity is what
    `recompute_file_embedding` is for, and it needs a reason.
    """
    if not embeddings_enabled:
        return None
    _require_enabled_inputs(config, encoder, embedding_text_for)
    assert config is not None and encoder is not None  # narrowed above
    assert embedding_text_for is not None

    existing = current_embedding(
        conn, file_id=file_id, content_hash=content_hash, scope=config.scope,
        embedding_model_id=config.model_id,
        embedding_version=config.model_version,
    )
    if existing is not None:
        return existing

    vector = _encode(
        conn, file_id=file_id, content_hash=content_hash, config=config,
        encoder=encoder, embedding_text_for=embedding_text_for,
    )
    if vector is None:
        return None
    record_embedding(
        conn, file_id=file_id, content_hash=content_hash, scope=config.scope,
        embedding_model_id=config.model_id,
        embedding_version=config.model_version,
        dimension=vector.dimension, encoding=vector.encoding,
        array_bytes=vector.array_bytes, created_at=created_at,
    )
    return current_embedding(
        conn, file_id=file_id, content_hash=content_hash, scope=config.scope,
        embedding_model_id=config.model_id,
        embedding_version=config.model_version,
    )


def recompute_file_embedding(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    content_hash: str,
    config: EmbeddingConfig,
    encoder: Encoder,
    embedding_text_for: EmbeddingTextFor,
    created_at: str,
    supersede_reason: str,
) -> EmbeddingRecord | None:
    """Re-encode an identity that already has a vector. Explicit, and reasoned.

    P1 finds and transactionally supersedes the exact predecessor; the caller
    chooses neither which row is replaced nor whether history is kept.
    """
    if not supersede_reason:
        raise ValueError(
            "recomputing a stored vector replaces the current one; the reason is "
            "what a later reader has to explain the change with"
        )
    _require_enabled_inputs(config, encoder, embedding_text_for)
    vector = _encode(
        conn, file_id=file_id, content_hash=content_hash, config=config,
        encoder=encoder, embedding_text_for=embedding_text_for,
    )
    if vector is None:
        return None
    record_embedding(
        conn, file_id=file_id, content_hash=content_hash, scope=config.scope,
        embedding_model_id=config.model_id,
        embedding_version=config.model_version,
        dimension=vector.dimension, encoding=vector.encoding,
        array_bytes=vector.array_bytes, created_at=created_at,
        supersede_reason=supersede_reason,
    )
    return current_embedding(
        conn, file_id=file_id, content_hash=content_hash, scope=config.scope,
        embedding_model_id=config.model_id,
        embedding_version=config.model_version,
    )
