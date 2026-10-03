"""Organise a whole folder, and change protection, from the conversation."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from assistant.events import Confirm, Error, Message, Progress
from assistant.session import Session
from database_agent.db import open_database
from items.file_identity import item_is_sensitive
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema


def calls(*tool_calls, reply="OK."):
    script = [{"role": "assistant", "content": None, "tool_calls": [
        {"id": f"c{i}", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}
        for i, (name, args) in enumerate(tool_calls)]},
        {"role": "assistant", "content": reply}]
    seen = []
    it = iter(script)

    def turn(messages, tools, config=None, **_):
        seen.append(json.dumps(messages))
        return next(it)
    turn.seen = seen
    return turn


def _corpus(tmp_path: Path) -> Path:
    corpus = tmp_path / "corpus"
    corpus.mkdir(exist_ok=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr Lee. Credits: 3.\n")
    (corpus / "PHYS 1401 homework 3.txt").write_text(
        "PHYS 1401 Homework 3\n\nSpring 2026 lecture notes.\n")
    return corpus


@pytest.fixture()
def db(tmp_path):
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    yield conn
    conn.close()


def _files(root: Path) -> set[str]:
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def test_organise_runs_the_sorter_and_moves_nothing(db, tmp_path):
    corpus = _corpus(tmp_path)
    before = _files(corpus)
    out = []
    s = Session(db, provider_turn=calls(("organise_folder",
                                         {"folder": str(corpus)})),
                emit=out.append)
    s.chosen_folders.add(corpus.resolve())
    s.say("organise my corpus folder")
    assert [e for e in out if isinstance(e, Progress)]
    assert _files(corpus) == before
    assert not [e for e in out if isinstance(e, Error)]


def test_a_folder_the_person_did_not_choose_is_asked_about(db, tmp_path):
    corpus = _corpus(tmp_path)
    out = []
    s = Session(db, provider_turn=calls(("organise_folder",
                                         {"folder": str(corpus)})),
                emit=out.append)
    s.say("organise it")
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    assert "Nothing moves" in confirm.summary
    assert not [e for e in out if isinstance(e, Progress)]


def test_a_protected_folder_is_refused_outright(db, tmp_path):
    secret = tmp_path / ".ssh"
    secret.mkdir()
    app = tmp_path / "Tool.app"
    app.mkdir()
    for folder in (secret, app):
        out = []
        turn = calls(("index_folder", {"folder": str(folder)}))
        Session(db, provider_turn=turn, emit=out.append).say("index that")
        assert not [e for e in out if isinstance(e, Confirm)]
        assert "never open" in turn.seen[-1]


def _seeded(db, tmp_path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "medical letter.txt").write_text("my diagnosis", encoding="utf-8")
    (root / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    reconcile_tree(db, root)
    rebuild_fts(db)
    db.commit()
    return root


def _item(db, label):
    return db.execute("SELECT item_id FROM items WHERE display_label = ?",
                      (label,)).fetchone()["item_id"]


def test_already_protected_is_said_and_nothing_is_granted(db, tmp_path):
    _seeded(db, tmp_path)
    out = []
    turn = calls(("mark_sensitive", {"file": "id.pem"}))
    Session(db, provider_turn=turn, emit=out.append).say("protect id.pem")
    assert not [e for e in out if isinstance(e, Confirm)]
    assert "already protected" in turn.seen[-1]


def test_protect_after_yes_is_sensitive_and_never_sent(db, tmp_path):
    import cli
    from evidence_shape.observation import observation_key
    from privacy.classification import ClassificationRecord
    from privacy.classification_store import ClassificationStore
    from privacy.policy import UNSET_POLICY_VERSION, Policy, set_policy
    from privacy.schema import create_privacy_schema
    from privacy.vocabulary import DETECTOR

    clock = "2026-10-03T00:00:00+00:00"
    _seeded(db, tmp_path)
    create_privacy_schema(db)
    item = _item(db, "medical letter.txt")
    file_id = db.execute("SELECT file_id FROM items WHERE item_id = ?",
                         (item,)).fetchone()[0]
    content_hash = db.execute("SELECT content_hash FROM files WHERE file_id=?",
                              (file_id,)).fetchone()[0]
    # The rules cleared it; the person says otherwise.
    ClassificationStore(db).write(ClassificationRecord(
        file_id=file_id, content_hash=content_hash,
        handling_class="personal_non_sensitive", protected=False,
        basis=DETECTOR, evidence_refs=(observation_key(
            content_hash=content_hash, extractor_name="fixture.text",
            locator="body:page=1#0-10", raw_value="fixture"),),
        reliability_state="validated", observed_at=clock))
    set_policy(db, Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode="cloud_assisted",
        consent_grants=(), redaction_settings={},
        automatic_move_permissions={}, plan_version=cli.PLAN_VERSION,
        set_at=clock), component_version="0.1.0", user_id="jy",
        reason="the policy this test starts from")
    db.commit()
    assert item_is_sensitive(db, item) is False

    out = []
    s = Session(db, provider_turn=calls(("mark_sensitive",
                                         {"file": "medical letter.txt"})),
                emit=out.append)
    s.say("keep my medical letter private")
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    assert item_is_sensitive(db, item) is False      # nothing until yes
    s.confirm(confirm.confirm_id, True)
    assert item_is_sensitive(db, item) is True
    assert "protected now" in out[-1].text

    later = calls(("find_files", {"query": "medical letter"}))
    s.provider_turn = later
    s.say("where is my medical letter?")
    sent = "".join(later.seen)
    assert "medical letter.txt" in sent or "medical" in sent
    assert str(tmp_path / "lib" / "medical letter.txt") not in sent


def test_a_branch_apply_asks_even_at_level_3(db, tmp_path, monkeypatch):
    import cli
    import assistant.organize_tools as ot
    corpus = _corpus(tmp_path)
    monkeypatch.setattr(ot, "show_tree", lambda conn: {"frozen_moves": 2})
    ran = []
    monkeypatch.setattr(cli, "main", lambda args, **kw: ran.append(args) or 0)
    monkeypatch.delenv("ASSISTANT_ENABLE_APPLY", raising=False)
    out = []
    s = Session(db, provider_turn=calls(("apply_branch", {
        "branch": "Coursework", "folder": str(corpus)})), emit=out.append)
    s.chosen_folders.add(corpus.resolve())
    s.set_level(3)
    s.say("move the coursework folder")
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    assert not ran
    s.confirm(confirm.confirm_id, True)
    assert ran[-1][-2:] == ["--apply", "Coursework"]


def test_release_always_confirms_and_names_the_cloud(db, tmp_path):
    _seeded(db, tmp_path)
    out = []
    Session(db, provider_turn=calls(("release", {"file": "id.pem"})),
            emit=out.append).say("id.pem is fine")
    confirm = [e for e in out if isinstance(e, Confirm)][-1]
    assert confirm.sensitive and "AI model" in confirm.summary
