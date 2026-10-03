"""Deferred tool schemas only after request_tools; local transport rules."""
from __future__ import annotations

from pathlib import Path

from assistant.local_model import probe_local_generation, require_local_or_refuse
from assistant.registry import deferred_schemas_for, deferred_tools
from assistant.tools import ToolRuntime
from items.identity import reconcile_tree
from items.schema import create_items_schema


def _seed(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.txt").write_text("x", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    return root


def test_deferred_schemas_absent_until_request(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    rt = ToolRuntime(conn)
    names = {s["function"]["name"] for s in rt.schemas()}
    assert "propose_tree" not in names
    assert "extract_one" not in names
    assert "find_files" in names

    req = rt.execute("request_tools", {"group": "organize_propose"})
    assert req.ok is True
    schemas = req.payload["schemas"]
    schema_names = {s["function"]["name"] for s in schemas}
    assert schema_names == set(deferred_tools("organize_propose"))
    # Model-facing runtime schemas now include exact deferred set.
    after = {s["function"]["name"] for s in rt.schemas()}
    assert "propose_tree" in after
    assert "extract_one" in after
    # Other deferred groups still dark
    assert "apply_moves" not in after
    assert "sync_mail" not in after


def test_model_receives_exact_deferred_schema(conn, tmp_path: Path):
    _seed(conn, tmp_path)
    rt = ToolRuntime(conn)
    rt.execute("request_tools", {"group": "graph_links"})
    expected = deferred_schemas_for("graph_links")
    got = [
        s for s in rt.schemas()
        if s["function"]["name"] in deferred_tools("graph_links")
    ]
    assert got == expected


def test_remote_local_compat_is_cloud_egress(monkeypatch):
    monkeypatch.setenv(
        "ASSISTANT_LOCAL_BASE_URL", "https://api.together.xyz/v1")
    status = probe_local_generation()
    assert status.available is True
    assert status.egress_class == "cloud"
    refused = require_local_or_refuse(local_only=True)
    assert refused.available is False
    assert refused.index_find is True
    assert "cloud" in refused.reason.lower() or "remote" in refused.reason.lower()


def test_without_explicit_local_url_no_ambient_ollama(monkeypatch):
    monkeypatch.delenv("ASSISTANT_LOCAL_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    status = probe_local_generation()
    # May still find Apple FM; must not claim ollama_compat without explicit URL.
    if status.backend == "ollama_compat":
        raise AssertionError("ambient ollama must not count as local without URL")
