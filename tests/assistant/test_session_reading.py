"""Reading resumes in every session; counts are not double-counted; the end
of reading says what it found."""
from __future__ import annotations

import assistant.session as session_mod
from assistant import events as ev
from assistant.session import Session
from items.indexing import IndexCounts, ReadOutcome


def _counts(unread):
    return IndexCounts(indexed=10, set_aside=4, set_aside_folders=1,
                       protected=3, held=2, open_questions=0,
                       unread_documents=unread)


def test_a_later_session_resumes_reading(conn, monkeypatch):
    started = []
    monkeypatch.setattr(session_mod, "_counts", lambda c: _counts(5))
    monkeypatch.setattr(session_mod, "start_reading",
                        lambda conn, emit: started.append(1) or "reader")
    out = []
    s = Session(conn, provider_turn=lambda **k: None, emit=out.append)
    s.open()
    assert started == [1] and s.reader == "reader"
    greeting = [e.text for e in out if isinstance(e, ev.Message)][0]
    assert "Protected files (3)" in greeting and "3 files look personal" \
        in greeting


def test_nothing_unread_starts_no_reader(conn, monkeypatch):
    monkeypatch.setattr(session_mod, "_counts", lambda c: _counts(0))
    monkeypatch.setattr(session_mod, "start_reading",
                        lambda conn, emit: (_ for _ in ()).throw(
                            AssertionError("started")))
    Session(conn, provider_turn=lambda **k: None, emit=lambda e: None).open()


def test_the_end_of_reading_reports_its_own_outcome(tmp_path, monkeypatch):
    import threading
    from database_agent.db import open_database
    from items import indexing
    open_database(tmp_path / "db.sqlite", scan_roots=[]).close()
    monkeypatch.setattr(indexing, "read_document_text", lambda conn, **k:
                        ReadOutcome(7, unreadable=2, protected_newly_found=1))
    out = []
    lock = threading.Lock()
    lock.acquire()
    session_mod._read_all(str(tmp_path / "db.sqlite"), out.append, lock)
    text = out[-1].text
    assert "(7 files)" in text and "2 files couldn't be read" in text
    assert "1 more file looks personal" in text
