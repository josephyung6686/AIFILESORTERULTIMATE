"""Organising asks once per folder whether the AI may read ordinary files.

The judge's organise ran offline because nothing ever asked: the rules-only
path filed a stroke paper under construction. The owner: the AI may be used,
never on sensitive files. Consent is the sorter's own per-folder record.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant import events as ev
from assistant.engine_tools import execute_confirmed
from assistant.session import Session
from database_agent.cloud_consent import ENABLED, record_cloud_consent
from database_agent.db import open_database


def _tool(name, args):
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": "c0", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


def _turns(*replies):
    it = iter(replies)
    return lambda messages, tools, config=None, **_: next(it)


@pytest.fixture()
def setup(tmp_path, monkeypatch):
    import cli
    from items.schema import create_items_schema
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-not-real")
    ran: list[list[str]] = []
    monkeypatch.setattr(cli, "main", lambda args, **kw: ran.append(args) or 0)
    corpus = tmp_path / "Desktop"
    corpus.mkdir()
    (corpus / "essay.txt").write_text("words")
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    out: list = []
    s = Session(conn, provider_turn=_turns(
        _tool("organise_folder", {"folder": str(corpus)}),
        {"role": "assistant", "content": "OK."}), emit=out.append)
    s.chosen_folders.add(corpus.resolve())
    yield conn, corpus.resolve(), s, out, ran
    conn.close()


def test_the_first_organise_asks_before_using_the_ai(setup):
    conn, corpus, s, out, ran = setup
    s.say("organise my whole desktop")
    confirm = [e for e in out if isinstance(e, ev.Confirm)][-1]
    assert "AI" in confirm.summary and "never protected" in confirm.summary
    assert not confirm.moves
    assert ran == []                                   # nothing ran yet
    proposal = s.pending[confirm.confirm_id]
    assert proposal["kind"] == "cloud"
    assert proposal["on_no"]["kind"] == "organise_offline"


def test_yes_runs_the_sorter_with_its_own_consent_flag(setup):
    conn, corpus, s, out, ran = setup
    s.say("organise my whole desktop")
    confirm = [e for e in out if isinstance(e, ev.Confirm)][-1]
    s.confirm(confirm.confirm_id, True)
    assert ran and "--enable-cloud" in ran[-1]
    assert ran[-1][0] == str(corpus)


def test_no_runs_offline_and_says_it_will_be_rough(setup):
    conn, corpus, s, out, ran = setup
    result = execute_confirmed(conn, "organise_offline", str(corpus),
                               context=s)
    assert ran and "--enable-cloud" not in ran[-1]
    assert "rough" in result["text"]


def test_a_folder_already_decided_is_not_asked_again(setup):
    conn, corpus, s, out, ran = setup
    record_cloud_consent(conn, corpus_root=str(corpus), decision=ENABLED,
                         user_id="jy", decided_at="2026-10-04T00:00:00+00:00")
    conn.commit()
    s.say("organise my whole desktop")
    assert not [e for e in out if isinstance(e, ev.Confirm)]
    assert ran and "--enable-cloud" not in ran[-1]


def test_without_a_key_nothing_is_asked(setup, monkeypatch):
    conn, corpus, s, out, ran = setup
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    monkeypatch.setenv("GRAPH_AGENT_NO_DOTENV", "1")
    s.say("organise my whole desktop")
    assert not [e for e in out if isinstance(e, ev.Confirm)]
    assert ran


def test_the_folder_question_chains_into_the_ai_question(setup):
    conn, corpus, s, out, ran = setup
    result = execute_confirmed(conn, "folder", f"organise:{corpus}",
                               context=s)
    assert result["needs_confirmation"]["kind"] == "cloud"
    assert ran == []
