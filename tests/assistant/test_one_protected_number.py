"""Every protected number the person sees is the index's number at that
moment: the greeting, `status`, and anything the model cites."""
from __future__ import annotations

from types import SimpleNamespace

from assistant import events as ev
from assistant import session as session_mod
from assistant.session import Session, agree_protected_count


def _counts(protected):
    return SimpleNamespace(indexed=40, set_aside=0, protected=protected,
                           held=0, open_questions=0, unread_documents=0)


def test_model_cited_protected_numbers_follow_the_index(conn, monkeypatch):
    state = {"c": _counts(3)}
    monkeypatch.setattr(session_mod, "_counts", lambda _c: state["c"])
    out = []
    reply = ("You have 8 protected files. Of 40 files, 11 are protected "
             "and 5 look personal. Protected files (9) stay here. "
             "Protected: 10. I found 8–11 protected files.")
    s = Session(conn, provider_turn=lambda **k: {"role": "assistant",
                                                 "content": reply},
                emit=out.append)
    s._open_rest()
    greeting = [e.text for e in out if isinstance(e, ev.Message)][0]
    assert "3 files look personal" in greeting
    state["c"] = _counts(8)  # the reader protected five more
    s.say("how many are protected?")
    said = [e.text for e in out if isinstance(e, ev.Message)][-1]
    for wrong in ("11", "9", "10", "8–"):
        assert wrong not in said
    assert said.count("8") >= 4 and "5 look personal" in said


def test_a_protected_free_sentence_is_untouched():
    c = _counts(8)
    line = "Your 12 essays are in Documents; 3 are drafts."
    assert agree_protected_count(line, c) == line
