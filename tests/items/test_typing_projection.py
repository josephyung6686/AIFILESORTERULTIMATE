"""Recognition and classification project onto file items."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from database_agent.db import open_database
from items.identity import reconcile_tree
from items.schema import create_items_schema
from items.typing import project_typing
from recognition.detector import Abstention, Recognition


def _conn(tmp_path: Path, body: bytes = b"x") -> sqlite3.Connection:
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.pdf").write_bytes(body)
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[str(root)])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    return conn


def test_recognition_types_the_item(tmp_path: Path):
    conn = _conn(tmp_path)

    def explain(c, file_id, content_hash):
        return Recognition(
            schema_id="academic", matches=(), evidence_refs=("e1",))

    def classify(c, file_id, content_hash):
        return None

    n = project_typing(conn, explain=explain, classify=classify)
    assert n == 1
    row = conn.execute(
        "SELECT typing_state, type_schema FROM items WHERE item_type = 'file'"
    ).fetchone()
    assert row["typing_state"] == "typed"
    assert row["type_schema"] == "academic"


def test_abstention_leaves_unplaced(tmp_path: Path):
    conn = _conn(tmp_path)

    def explain(c, file_id, content_hash):
        return Abstention(
            reason="outside_declared_lives", schema_id=None,
            detail="would-be business",
            matched_terms=(("business_operations", ()),))

    n = project_typing(conn, explain=explain, classify=lambda *a: None)
    assert n == 1
    row = conn.execute(
        "SELECT typing_state, type_schema FROM items WHERE item_type = 'file'"
    ).fetchone()
    assert row["typing_state"] == "unplaced"
    assert row["type_schema"] is None


def test_protected_classification_holds_even_when_recognised(tmp_path: Path):
    conn = _conn(tmp_path)

    class _Rec:
        protected = True
        basis = "safety_domain"

    def explain(c, file_id, content_hash):
        return Recognition(
            schema_id="identity", matches=(), evidence_refs=("e1",))

    n = project_typing(conn, explain=explain, classify=lambda *a: _Rec())
    row = conn.execute(
        "SELECT typing_state, type_schema FROM items WHERE item_type = 'file'"
    ).fetchone()
    assert row["typing_state"] == "held"
    assert row["type_schema"] == "identity"
    assert n == 1
