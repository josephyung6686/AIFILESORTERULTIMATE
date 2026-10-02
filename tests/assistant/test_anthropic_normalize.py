"""Anthropic tool schema / message normalization — no network."""
from __future__ import annotations

from assistant.provider import (
    ProviderConfig,
    _messages_to_anthropic,
    _openai_tools_to_anthropic,
    chat_turn_anthropic,
)


def test_tools_and_messages_normalize():
    tools = _openai_tools_to_anthropic([{
        "type": "function",
        "function": {
            "name": "find_files",
            "description": "find",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
            },
        },
    }])
    assert tools[0]["name"] == "find_files"
    assert "input_schema" in tools[0]

    system, msgs = _messages_to_anthropic([
        {"role": "system", "content": "Be careful."},
        {"role": "user", "content": "where is x?"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "t1",
                "type": "function",
                "function": {
                    "name": "find_files",
                    "arguments": '{"query":"x"}',
                },
            }],
        },
        {
            "role": "tool",
            "tool_call_id": "t1",
            "content": '{"hits":[]}',
        },
    ])
    assert "careful" in system.lower()
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"][0]["type"] == "tool_use"
    assert msgs[2]["content"][0]["type"] == "tool_result"


def test_chat_turn_anthropic_mocked(monkeypatch):
    class Block:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    class FakeMessages:
        def create(self, **kwargs):
            assert "tools" in kwargs
            return type("R", (), {
                "content": [
                    Block(type="tool_use", id="u1", name="find_files",
                          input={"query": "cv"}),
                ],
            })()

    class FakeClient:
        def __init__(self, **kw):
            self.messages = FakeMessages()

    monkeypatch.setitem(
        __import__("sys").modules, "anthropic",
        type("M", (), {"Anthropic": FakeClient})())

    # Re-import path uses anthropic inside function
    import assistant.provider as prov
    cfg = ProviderConfig(
        api_key="k", base_url="https://api.anthropic.com",
        model="claude-test", provider="anthropic")
    out = prov.chat_turn_anthropic(
        messages=[{"role": "user", "content": "hi"}],
        tools=[{
            "type": "function",
            "function": {
                "name": "find_files",
                "description": "d",
                "parameters": {"type": "object"},
            },
        }],
        config=cfg,
    )
    assert out["tool_calls"][0]["function"]["name"] == "find_files"
