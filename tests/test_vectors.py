from database_agent.db import create_schema
from database_agent.vectors import get_embedding, put_embedding
import database_agent.vectors as vectors_module


def test_array_round_trips_byte_identically(conn):
    create_schema(conn)
    payload = bytes(range(256)) * 4
    put_embedding(conn, "file:abc", payload, producer_version="p9-v1")
    assert get_embedding(conn, "file:abc") == payload


def test_arrays_live_outside_files_and_events(conn):
    create_schema(conn)
    put_embedding(conn, "file:abc", b"\x00\x01", producer_version="p9-v1")
    for table in ("files", "events"):
        cols = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
        assert not any(c.lower() in ("embedding", "vector", "array") for c in cols)


def test_p1_exposes_no_similarity_or_nearest_neighbour_call():
    # §0: never a vector database. Retrieval belongs to P9 (§4.2) and P11 (§6.3).
    exported = dir(vectors_module)
    for forbidden in ("similarity", "cosine", "nearest", "knn", "search", "index"):
        assert not any(forbidden in name.lower() for name in exported)


def test_missing_key_returns_none(conn):
    create_schema(conn)
    assert get_embedding(conn, "file:absent") is None
