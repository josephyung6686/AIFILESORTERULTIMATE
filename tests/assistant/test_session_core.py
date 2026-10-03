# tests/assistant/test_session_core.py
from assistant.session import Session
from assistant.events import Message, Counts, Error, to_json
import json


def scripted(*replies):
    it = iter(replies)
    def turn(messages, tools, config=None, **_):
        return next(it)
    return turn


def test_open_on_empty_db_asks_for_a_folder(conn):
    out = []
    Session(conn, provider_turn=scripted(), emit=out.append).open()
    assert isinstance(out[-1], Message)
    assert "which folder" in out[-1].text.lower()


def test_two_turns_share_history(conn, tmp_path):
    seen = []
    def turn(messages, tools, config=None, **_):
        seen.append([m["content"] for m in messages if m["role"] == "user"])
        return {"role": "assistant", "content": "noted"}
    s = Session(conn, provider_turn=turn, emit=lambda e: None)
    s.say("my name is Ada")
    s.say("what is my name?")
    assert seen[-1] == ["my name is Ada", "what is my name?"]


def test_history_over_budget_drops_tool_payloads_first(conn):
    s = Session(conn, provider_turn=scripted(*[{"role": "assistant", "content": "ok"}] * 40), emit=lambda e: None)
    for i in range(40):
        s.history.append({"role": "tool", "tool_call_id": str(i), "content": "x" * 5000})
        s.say(f"question {i}")
    users = [m for m in s.history if m["role"] == "user"]
    assert len(users) == 40
    assert sum(len(m["content"]) for m in s.history if m["role"] == "tool") < 60000


def test_provider_failure_is_one_plain_line(conn):
    def boom(*a, **k): raise RuntimeError("402 Insufficient Balance")
    out = []
    Session(conn, provider_turn=boom, emit=out.append).say("hi")
    text = out[-1].text
    assert "Traceback" not in text and "nothing changed" in text.lower()


def test_to_json_adds_type():
    data = json.loads(to_json(Counts(indexed=3, set_aside=1, protected=2,
                                     held=0, open_questions=0)))
    assert data["type"] == "counts" and data["indexed"] == 3
    err = json.loads(to_json(Error(text="x", changed=False)))
    assert err["type"] == "error"
