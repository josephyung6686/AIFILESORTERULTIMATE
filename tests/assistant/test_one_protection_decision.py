"""One protection decision, read live from the database (owner, 3 Oct 2026).

"let it go to the API but not sensitive files -- isn't it supposed to be using
the database?" and "union of both" protection lists. A file the sorter's
classification store holds, or that either path list covers, is never sent,
read in detail, exported or shown with its path -- and the person's
`--file-held` reaches the assistant without a re-run.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import cli
from assistant.chat import ask
from assistant.provider import ProviderConfig
from assistant.tools import ToolRuntime
from database_agent.db import open_database
from database_agent.privacy import LocalAuthRequired, delete_item, export_database
from items.file_identity import item_is_sensitive, path_is_protected
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema
from items.typing import project_typing
from items.views import table_view
from evidence_shape.observation import observation_key
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore
from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
from privacy.schema import create_privacy_schema
from privacy.vocabulary import DETECTOR, USER_CONFIRMED

VALIDATED = "validated"

CLOCK = "2026-10-03T00:00:00+00:00"
KEPT_BODY = "KEPT_BODY_SENTINEL passport 123"
OPEN_BODY = "OPEN_BODY_SENTINEL lecture notes"


def _item(conn, label):
    return conn.execute(
        "SELECT item_id, file_id, open_target FROM items WHERE display_label=?",
        (label,)).fetchone()


def _seed(tmp_path: Path, *, privacy_tables: bool = True):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "notes.txt").write_text("lecture notes", encoding="utf-8")
    (root / "boarding-pass.txt").write_text("boarding pass", encoding="utf-8")
    conn = open_database(tmp_path / "t.sqlite", scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, root)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS evidence ("
        "evidence_id TEXT PRIMARY KEY, file_id TEXT, raw_value TEXT, "
        "superseded_by TEXT)")
    for label, body in (("notes.txt", OPEN_BODY),
                        ("boarding-pass.txt", KEPT_BODY)):
        conn.execute("INSERT INTO evidence VALUES (?,?,?,NULL)",
                     (f"e-{label}", _item(conn, label)["file_id"], body))
    if privacy_tables:
        create_privacy_schema(conn)
    rebuild_fts(conn)
    conn.commit()
    return conn


def _classify(conn, file_id, *, protected, reliability=VALIDATED,
              basis=DETECTOR):
    content_hash = conn.execute(
        "SELECT content_hash FROM files WHERE file_id=?", (file_id,)
    ).fetchone()[0]
    ClassificationStore(conn).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class=("sensitive_personal" if protected else "personal_non_sensitive"),
        protected=protected, basis=basis, evidence_refs=(observation_key(
            content_hash=content_hash, extractor_name="fixture.text",
            locator="body:page=1#0-10", raw_value="fixture"),),
        reliability_state=reliability, observed_at=CLOCK))


def _policy(conn):
    set_policy(conn, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={}, plan_version=cli.PLAN_VERSION,
        set_at=CLOCK), component_version="0.1.0", user_id="joseph",
        reason="the policy this test starts from")


def _fake_cloud(conn, item_ids, captured):
    calls = {"n": 0}

    def fake_turn(*, messages, tools, config, temperature=0.2):
        captured.append(json.dumps(messages, ensure_ascii=False, default=str))
        calls["n"] += 1
        if calls["n"] == 1:
            tool_calls = [{
                "id": "f", "type": "function",
                "function": {"name": "find_files",
                             "arguments": json.dumps({"query": "boarding notes"})},
            }]
            for n, item_id in enumerate(item_ids):
                for tool in ("read_item", "explain_file"):
                    tool_calls.append({
                        "id": f"{tool}{n}", "type": "function",
                        "function": {"name": tool, "arguments": json.dumps(
                            {"item_id": item_id})}})
            return {"role": "assistant", "content": None,
                    "tool_calls": tool_calls}
        return {"role": "assistant", "content": "done"}

    cfg = ProviderConfig(api_key="t", base_url="https://api.deepseek.com",
                         model="m", provider="deepseek")
    with patch("assistant.chat.resolve_provider", return_value=cfg), \
            patch("assistant.chat.chat_turn", side_effect=fake_turn):
        ask(conn, "boarding notes", session_id="s")


def test_file_held_on_a_rules_cleared_file_is_refused_without_a_rerun(tmp_path):
    conn = _seed(tmp_path)
    kept = _item(conn, "boarding-pass.txt")
    ordinary = _item(conn, "notes.txt")
    _classify(conn, kept["file_id"], protected=False)    # the rules cleared it
    _classify(conn, ordinary["file_id"], protected=False)
    _policy(conn)
    assert item_is_sensitive(conn, kept["item_id"]) is False

    cli.apply_file_held(conn, [kept["file_id"]], plan_version=cli.PLAN_VERSION,
                        user_id="joseph", recorded_at=CLOCK)
    conn.commit()
    # No sorter re-run: the copied column still says what it said.
    assert conn.execute("SELECT typing_state FROM items WHERE item_id=?",
                        (kept["item_id"],)).fetchone()[0] != "held"

    assert item_is_sensitive(conn, kept["item_id"]) is True
    assert item_is_sensitive(conn, ordinary["item_id"]) is False
    rt = ToolRuntime(conn)
    assert rt.execute("read_item", {"item_id": kept["item_id"]}).ok is False
    assert rt.execute("read_item", {"item_id": ordinary["item_id"]}).ok is True

    destination = tmp_path / "export.json"
    export_database(conn, destination)
    rendered = destination.read_text()
    assert kept["item_id"] not in rendered
    assert kept["open_target"] not in rendered
    assert ordinary["item_id"] in rendered

    with pytest.raises(LocalAuthRequired):
        delete_item(conn, kept["item_id"])

    captured: list[str] = []
    _fake_cloud(conn, [kept["item_id"], ordinary["item_id"]], captured)
    envelope = "\n".join(captured)
    assert KEPT_BODY not in envelope
    assert kept["open_target"] not in envelope
    # The ordinary file still goes to the API, path and snippet.
    assert OPEN_BODY in envelope
    assert ordinary["open_target"] in envelope
    conn.close()


def test_app_child_and_pem_are_protected_on_an_assistant_only_database(tmp_path):
    conn = _seed(tmp_path, privacy_tables=False)
    assert conn.execute("SELECT 1 FROM sqlite_master "
                        "WHERE name='classifications'").fetchone() is None
    app_child = str(tmp_path / "Numbers.app" / "Contents" / "sheet.txt")
    pem = str(tmp_path / "lib" / "server.pem")
    for item_id, label, target in (("app-child", "sheet.txt", app_child),
                                   ("pem", "server.pem", pem)):
        conn.execute(
            "INSERT INTO items (item_id, item_type, display_label, open_target, "
            "presence, typing_state, created_at) "
            "VALUES (?, 'file', ?, ?, 'live', 'unplaced', ?)",
            (item_id, label, target, CLOCK))
    conn.commit()
    assert path_is_protected(app_child) and path_is_protected(pem)
    assert item_is_sensitive(conn, "app-child") and item_is_sensitive(conn, "pem")
    assert not item_is_sensitive(conn, _item(conn, "notes.txt")["item_id"])

    rt = ToolRuntime(conn)
    assert rt.execute("read_item", {"item_id": "app-child"}).ok is False
    assert rt.execute("read_item", {"item_id": "pem"}).ok is False
    rows = {r["item_id"]: r for r in table_view(conn)}
    assert rows["app-child"]["open_target"] is None
    assert rows["pem"]["open_target"] is None

    destination = tmp_path / "export.json"
    export_database(conn, destination)
    rendered = destination.read_text()
    assert app_child not in rendered and pem not in rendered
    conn.close()


def test_release_is_honoured_when_the_sorter_reprojects_not_before(tmp_path):
    conn = _seed(tmp_path)
    held = _item(conn, "boarding-pass.txt")
    # The rules held it, under a basis `--release` may lift.
    _classify(conn, held["file_id"], protected=True, basis="local_model_gate")
    store = ClassificationStore(conn)
    assert project_typing(conn, explain=lambda *_: None,
                          classify=lambda c, f, h: store.current(f, h)) == 2
    assert item_is_sensitive(conn, held["item_id"]) is True

    cli.apply_release(conn, [held["file_id"]], user_id="joseph",
                      recorded_at=CLOCK)
    # Union: the copied `held` still stands until the sorter's own projection
    # reads the person's release -- the sorter's rule, not a new one.
    assert item_is_sensitive(conn, held["item_id"]) is True
    project_typing(conn, explain=lambda *_: None,
                   classify=lambda c, f, h: store.current(f, h))
    assert item_is_sensitive(conn, held["item_id"]) is False
    assert ToolRuntime(conn).execute(
        "read_item", {"item_id": held["item_id"]}).ok is True
    conn.close()


def test_an_ambiguous_store_answer_fails_closed(tmp_path):
    conn = _seed(tmp_path)
    item = _item(conn, "notes.txt")
    _classify(conn, item["file_id"], protected=False, reliability=USER_CONFIRMED)
    _classify(conn, item["file_id"], protected=False, reliability=USER_CONFIRMED)
    assert item_is_sensitive(conn, item["item_id"]) is True
    conn.close()
