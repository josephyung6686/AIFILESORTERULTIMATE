# src/database_agent/vector_versions.py
"""P1's versioned embedding records. Append and supersede; never overwrite (§8.2).

The legacy `vector_arrays` table is `subject_key PRIMARY KEY` with
`ON CONFLICT DO UPDATE`. A recompute destroys the vector it replaces, and the row
records no file version, scope, model identity, dimension, encoding or creation
time -- so nothing can say which model produced a stored vector, and nothing can
read the one it replaced. P9 cites vectors as evidence, which neither property
survives.

This table is ADDITIVE. Legacy rows are not migrated or reinterpreted: they carry
none of the metadata a safe migration would need.

P1 remains an opaque-byte store. `dimension > 0` and the identifying strings must
be non-empty, but this module infers no codec and does not claim that a byte
length matches a dimension -- P9's injected encoder owns serialization. P1 still
publishes no similarity query.
"""
from __future__ import annotations

import sqlite3
import uuid
from dataclasses import dataclass

from database_agent.db import transaction

#: The identity a "current" vector is unique on.
VECTOR_IDENTITY: tuple[str, ...] = (
    "file_id", "content_hash", "scope", "embedding_model_id", "embedding_version",
)

VECTOR_VERSIONS_DDL = """
CREATE TABLE IF NOT EXISTS vector_embeddings (
    embedding_id      TEXT PRIMARY KEY,
    file_id           TEXT NOT NULL,
    content_hash      TEXT NOT NULL,
    scope             TEXT NOT NULL,
    embedding_model_id TEXT NOT NULL,
    embedding_version TEXT NOT NULL,
    dimension         INTEGER NOT NULL CHECK (dimension > 0),
    encoding          TEXT NOT NULL,
    array_bytes       BLOB NOT NULL,
    created_at        TEXT NOT NULL,
    supersedes        TEXT,
    superseded_by     TEXT,
    supersede_reason  TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS one_current_vector_embedding
    ON vector_embeddings (
        file_id, content_hash, scope, embedding_model_id, embedding_version
    ) WHERE superseded_by IS NULL;
CREATE INDEX IF NOT EXISTS vector_embedding_version
    ON vector_embeddings (file_id, content_hash, scope);
"""


class AmbiguousCurrentEmbedding(RuntimeError):
    """More than one current row for one vector identity.

    Only reachable in a store written before the partial unique index existed.
    Repairing it is a deliberate act; a writer that picked one row to supersede
    would be choosing which recorded vector to hide.
    """


@dataclass(frozen=True)
class EmbeddingRecord:
    embedding_id: str
    file_id: str
    content_hash: str
    scope: str
    embedding_model_id: str
    embedding_version: str
    dimension: int
    encoding: str
    array_bytes: bytes
    created_at: str
    supersedes: str | None
    superseded_by: str | None
    supersede_reason: str | None


def _row(row: sqlite3.Row) -> EmbeddingRecord:
    return EmbeddingRecord(
        embedding_id=row["embedding_id"],
        file_id=row["file_id"],
        content_hash=row["content_hash"],
        scope=row["scope"],
        embedding_model_id=row["embedding_model_id"],
        embedding_version=row["embedding_version"],
        dimension=row["dimension"],
        encoding=row["encoding"],
        array_bytes=bytes(row["array_bytes"]),
        created_at=row["created_at"],
        supersedes=row["supersedes"],
        superseded_by=row["superseded_by"],
        supersede_reason=row["supersede_reason"],
    )


def _require_identity(**values: object) -> None:
    for name, value in values.items():
        if not isinstance(value, str) or not value:
            raise ValueError(
                f"{name} is part of a vector's identity and must be a non-empty "
                "string; a vector nothing can be identified by cannot be cited"
            )


def _current_rows(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                  scope: str, embedding_model_id: str,
                  embedding_version: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM vector_embeddings "
        "WHERE file_id = ? AND content_hash = ? AND scope = ? "
        "AND embedding_model_id = ? AND embedding_version = ? "
        "AND superseded_by IS NULL ORDER BY rowid",
        (file_id, content_hash, scope, embedding_model_id, embedding_version),
    ).fetchall()


def record_embedding(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    content_hash: str,
    scope: str,
    embedding_model_id: str,
    embedding_version: str,
    dimension: int,
    encoding: str,
    array_bytes: bytes,
    created_at: str,
    supersede_reason: str | None = None,
) -> str:
    """Append one vector for one exact identity, superseding the current row.

    Zero current rows insert normally. Exactly one requires a non-empty
    `supersede_reason`; the predecessor is marked superseded by the minted id and
    the successor is inserted in the same transaction, so a failed insert rolls the
    predecessor back. More than one current row raises before any write.

    The caller cannot choose which predecessor to supersede: it is whichever row is
    current for this identity, or none.
    """
    _require_identity(
        file_id=file_id, content_hash=content_hash, scope=scope,
        embedding_model_id=embedding_model_id,
        embedding_version=embedding_version, encoding=encoding,
        created_at=created_at,
    )
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0:
        raise ValueError("dimension must be a positive integer")
    if not isinstance(array_bytes, (bytes, bytearray, memoryview)):
        raise TypeError(
            "array_bytes must be bytes; SQLite stores str as TEXT, not BLOB"
        )

    identity = dict(
        file_id=file_id, content_hash=content_hash, scope=scope,
        embedding_model_id=embedding_model_id,
        embedding_version=embedding_version,
    )
    successor = str(uuid.uuid4())
    with transaction(conn):
        current = _current_rows(conn, **identity)
        if len(current) > 1:
            raise AmbiguousCurrentEmbedding(
                f"{len(current)} current rows for {identity!r}; a writer that chose "
                "one of them to supersede would be choosing which recorded vector "
                "to hide. Repair the store deliberately."
            )
        predecessor = current[0]["embedding_id"] if current else None
        if predecessor is not None:
            if not supersede_reason:
                raise ValueError(
                    "supersede_reason is required to replace a current vector "
                    "(§8.2: supersede, never overwrite)"
                )
            conn.execute(
                "UPDATE vector_embeddings SET superseded_by = ?, supersede_reason = ? "
                "WHERE embedding_id = ?",
                (successor, supersede_reason, predecessor),
            )
        conn.execute(
            "INSERT INTO vector_embeddings ("
            "embedding_id, file_id, content_hash, scope, embedding_model_id, "
            "embedding_version, dimension, encoding, array_bytes, created_at, "
            "supersedes"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                successor, file_id, content_hash, scope, embedding_model_id,
                embedding_version, dimension, encoding, bytes(array_bytes),
                created_at, predecessor,
            ),
        )
    return successor


def current_embedding(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    content_hash: str,
    scope: str,
    embedding_model_id: str,
    embedding_version: str,
) -> EmbeddingRecord | None:
    """The one live vector for an exact identity, or None. Never a near match."""
    rows = _current_rows(
        conn, file_id=file_id, content_hash=content_hash, scope=scope,
        embedding_model_id=embedding_model_id,
        embedding_version=embedding_version,
    )
    if len(rows) > 1:
        raise AmbiguousCurrentEmbedding(
            f"{len(rows)} current rows for this vector identity"
        )
    return _row(rows[0]) if rows else None


def embedding_history(
    conn: sqlite3.Connection, *, file_id: str, content_hash: str, scope: str,
) -> tuple[EmbeddingRecord, ...]:
    """Every recorded vector for one file version and scope, oldest first.

    Spans every model and version: which model produced a vector is part of what a
    reader needs, so history is not filtered to one of them.
    """
    rows = conn.execute(
        "SELECT * FROM vector_embeddings "
        "WHERE file_id = ? AND content_hash = ? AND scope = ? ORDER BY rowid",
        (file_id, content_hash, scope),
    ).fetchall()
    return tuple(_row(row) for row in rows)
