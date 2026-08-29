"""Contract out §9 — the vector array store (S2, G2).

§0's exact posture: "store vectors separately as compact local arrays if embeddings
are used", never a vector database. P9 computes; P1 stores and returns bytes.
P1 exposes no similarity function, no index, and no nearest-neighbour query.
"""
from __future__ import annotations

import sqlite3

VECTORS_DDL = """
CREATE TABLE IF NOT EXISTS vector_arrays (
    subject_key      TEXT PRIMARY KEY,
    array_bytes      BLOB NOT NULL,
    producer_version TEXT NOT NULL
);
"""


def put_embedding(conn: sqlite3.Connection, subject_key: str, array: bytes, *,
                  producer_version: str) -> None:
    """Store an opaque compact local array. P1 does not interpret its contents."""
    if not isinstance(array, (bytes, bytearray, memoryview)):
        raise TypeError("embeddings are opaque bytes; P1 stores them unchanged")
    conn.execute(
        "INSERT INTO vector_arrays (subject_key, array_bytes, producer_version) "
        "VALUES (?, ?, ?) ON CONFLICT(subject_key) DO UPDATE SET "
        "array_bytes = excluded.array_bytes, producer_version = excluded.producer_version",
        (subject_key, array, producer_version),
    )


def get_embedding(conn: sqlite3.Connection, subject_key: str) -> bytes | None:
    """Return it unchanged."""
    row = conn.execute(
        "SELECT array_bytes FROM vector_arrays WHERE subject_key = ?", (subject_key,)
    ).fetchone()
    return None if row is None else bytes(row["array_bytes"])
