"""Deterministic find→explain trajectories (pass^k harness, no live LLM)."""
from __future__ import annotations

from pathlib import Path

from assistant.tools import ToolRuntime
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _lib(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "03-09-Joint PMFs.pdf").write_text(
        "Class 13 Joint distributions PMF", encoding="utf-8")
    (root / "Joseph Yung resume updated.pdf").write_text(
        "Resume Georgetown Prep", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    # Store fake evidence rows if table exists after bootstrap — optional.
    rebuild_fts(conn)
    return root


def _trajectory_find_explain(rt: ToolRuntime, query: str, label_substr: str):
    """Canonical read-only trajectory. Returns (ok, citations, moved)."""
    found = rt.execute("find_files", {"query": query, "limit": 5})
    assert found.payload.get("moved") is False
    hits = found.payload.get("hits") or []
    target = next(
        (h for h in hits if label_substr in h["display_label"]
         and not h.get("note")),
        None,
    )
    if target is None:
        return False, (), False
    explained = rt.execute("explain_file", {"item_id": target["item_id"]})
    moved = bool(found.payload.get("moved") or explained.payload.get("moved"))
    ok = explained.ok and target["item_id"] in explained.citations
    return ok, explained.citations, moved


def test_find_explain_trajectories_pass_k(conn, tmp_path: Path):
    _lib(conn, tmp_path)
    rt = ToolRuntime(conn)
    cases = [
        ("Joint PMFs", "Joint PMFs"),
        ("Joseph resume", "resume"),
    ]
    # pass^3: each case succeeds 3 independent runs
    for query, needle in cases:
        passes = 0
        for _ in range(3):
            ok, cites, moved = _trajectory_find_explain(rt, query, needle)
            assert moved is False
            if ok and cites:
                passes += 1
        assert passes == 3, f"{query}: pass^3 failed ({passes}/3)"


def test_ask_user_and_request_tools_in_trajectory(conn, tmp_path: Path):
    _lib(conn, tmp_path)
    answers = []

    def handler(q, choices):
        answers.append(q)
        return "Joint PMFs lecture"

    rt = ToolRuntime(conn, ask_user_handler=handler)
    asked = rt.execute("ask_user", {"question": "Which course?"})
    assert asked.ok is True
    assert answers == ["Which course?"]
    req = rt.execute("request_tools", {"group": "organize_propose"})
    assert req.ok is True
    assert req.payload["write_enabled"] is False
    # Continue find after clarify
    ok, cites, moved = _trajectory_find_explain(rt, "Joint PMFs", "Joint")
    assert ok and cites and moved is False
