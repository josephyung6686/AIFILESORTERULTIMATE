"""Every base + deferred tool passes through one policy boundary."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant.policy import (
    PolicyResult,
    clear_gate_log,
    gate_log,
    gate_tool_call,
    strip_protected_paths,
    validate_citations,
    validate_tool_arguments,
)
from assistant.registry import ALWAYS_TOOLS, DEFERRED_GROUPS
from assistant.tools import ToolRuntime
from items.identity import reconcile_tree
from items.file_identity import path_is_protected
from items.schema import create_items_schema


def _seed(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "notes.txt").write_text("hello notes", encoding="utf-8")
    (root / "secret.pem").write_bytes(b"KEYMATERIAL")
    (root / "tax.pdf").write_text("SSN 000-00-0000", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    conn.execute(
        "UPDATE items SET typing_state='held' "
        "WHERE display_label='tax.pdf'"
    )
    return root


def test_policy_result_fields():
    r = PolicyResult(
        allowed=False,
        reason="nope",
        protected=True,
        untrusted=True,
        bytes_in=3,
        bytes_out=4,
        citations=("a",),
        egress_class="cloud",
    )
    assert r.allowed is False
    assert r.protected is True
    assert r.egress_class == "cloud"


def test_every_tool_hits_gate(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    clear_gate_log()
    rt = ToolRuntime(conn)
    # Base tools
    for name, args in (
        ("find_files", {"query": "notes", "limit": 3}),
        ("list_deadlines", {"limit": 5}),
        ("list_gaps", {"limit": 5}),
        ("ask_user", {"question": "which?"}),
        ("request_tools", {"group": "organize_propose"}),
    ):
        rt.execute(name, args)
    item = conn.execute(
        "SELECT item_id FROM items WHERE display_label='notes.txt'"
    ).fetchone()["item_id"]
    rt.execute("read_item", {"item_id": item})
    rt.execute("explain_file", {"item_id": item})
    rt.execute("list_related", {"item_id": item})
    # Deferred after unlock
    for group, tools in DEFERRED_GROUPS.items():
        rt.execute("request_tools", {"group": group})
        for tool in tools:
            if tool in ("apply_moves", "undo_moves", "place_preview", "freeze"):
                rt.execute(tool, {"plan_id": "none"})
            elif tool == "extract_one":
                rt.execute(tool, {"item_id": item})
            elif tool == "scan_refresh":
                rt.execute(tool, {"root": str(tmp_path / "lib")})
            elif tool in ("accept_link", "reject_link"):
                rt.execute(tool, {"relationship_id": "x"})
            else:
                rt.execute(tool, {})
    names = {e["name"] for e in gate_log()}
    for t in ALWAYS_TOOLS:
        assert t in names, t
    for tools in DEFERRED_GROUPS.values():
        for t in tools:
            assert t in names, t


def test_schema_rejects_non_integer_limit_and_unknown_fields(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    rt = ToolRuntime(conn)
    bad_limit = rt.execute("find_files", {"query": "x", "limit": "8"})
    assert bad_limit.ok is False
    assert "integer" in bad_limit.payload["error"]

    unknown = rt.execute("find_files", {"query": "x", "evil": 1})
    assert unknown.ok is False
    assert "unknown field" in unknown.payload["error"]

    dest = validate_tool_arguments(
        "apply_moves", {"plan_id": "p", "dst": "/tmp"})
    # apply may not be unlocked; direct schema check:
    # apply_moves schema has no dst — unknown field
    ok, reason, _ = dest
    assert ok is False
    assert "unknown" in reason or "destination" in reason or "free-form" in reason


def test_extract_one_refuses_held_and_protected(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    rt = ToolRuntime(conn)
    rt.execute("request_tools", {"group": "organize_propose"})
    held = conn.execute(
        "SELECT item_id, open_target FROM items WHERE display_label='tax.pdf'"
    ).fetchone()
    pem = conn.execute(
        "SELECT item_id, open_target FROM items WHERE display_label='secret.pem'"
    ).fetchone()
    assert path_is_protected(pem["open_target"])

    out_held = rt.execute("extract_one", {"item_id": held["item_id"]})
    assert out_held.ok is False
    assert out_held.payload.get("refused") is True
    blob = json.dumps(out_held.payload)
    assert held["open_target"] not in blob

    out_pem = rt.execute("extract_one", {"item_id": pem["item_id"]})
    assert out_pem.ok is False
    assert pem["open_target"] not in json.dumps(out_pem.payload)


def test_protected_paths_stripped_from_payloads():
    payload = {
        "hits": [
            {"item_id": "a", "open_target": "/Users/x/.ssh/id_rsa"},
            {"item_id": "b", "open_target": "/tmp/ok.txt"},
        ],
        "nested": {"path": "/secret/key.pem"},
    }
    cleaned = strip_protected_paths(payload)
    assert cleaned["hits"][0]["open_target"] is None
    assert cleaned["hits"][1]["open_target"] == "/tmp/ok.txt"
    assert cleaned["nested"]["path"] is None


def test_citations_refuse_invented_ids():
    valid, _, reason = validate_citations(
        ["real-1", "fake-9"],
        returned_item_ids=["real-1"],
    )
    assert valid == ("real-1",)
    assert reason is not None

    none, _, reason2 = validate_citations(
        ["invented"],
        returned_item_ids=["real-1"],
    )
    assert none == ()
    assert reason2 == "invented citations refused"


def test_gate_tool_call_is_the_boundary(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    clear_gate_log()
    r = gate_tool_call(
        name="find_files",
        arguments={"query": "notes", "limit": 2},
        conn=conn,
    )
    assert r.allowed is True
    assert isinstance(r, PolicyResult)
    assert gate_log()[-1]["name"] == "find_files"
