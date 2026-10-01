"""Fact and situation calls post chat completions without an SDK.

The understanding pass already does this with `urllib`. A `readers` install
has no `openai` package. A missing import must not become the failure a
person sees, and a failure that does happen must not contain the key.
"""
from __future__ import annotations

import json

import pytest

from privacy.release import ModelTarget
from readers.model_deepseek import (
    JUDGE_SAMPLING, NoAnswerFromModel, ProviderDidNotAnswer, deepseek_invoke,
    request_body, usage_of,
)

SECRET = "sk-test-do-not-print"
TARGET = ModelTarget(locality="cloud", model_id="a-model", provider="deepseek")
DOSSIER = b'{"dossier": "x", "answer_with": "one json object"}'
ANSWER = '{"claims": []}'


def _completion(text: str) -> bytes:
    return json.dumps({
        "id": "chatcmpl-test",
        "choices": [{"finish_reason": "stop",
                     "message": {"role": "assistant", "content": text}}],
        "usage": {"prompt_tokens": 11, "completion_tokens": 3,
                  "prompt_cache_hit_tokens": 2},
    }).encode("utf-8")


class _Response:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self._body = body
        self._done = False

    def isclosed(self) -> bool:
        return self._done

    def read1(self, _n: int) -> bytes:
        if self._done:
            return b""
        self._done = True
        return self._body


class _Socket:
    def settimeout(self, _timeout: float) -> None:
        return None


class _Connection:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = _Socket()
        self.sent = None
        self.closed = False

    def connect(self) -> None:
        return None

    def request(self, method, path, body=None, headers=None) -> None:
        self.sent = (method, path, body, dict(headers or {}))
        _Connection.last = self

    def getresponse(self) -> _Response:
        return _Response(200, _completion(ANSWER))

    def close(self) -> None:
        self.closed = True


def _install(monkeypatch, connection):
    import http.client

    monkeypatch.setattr(http.client, "HTTPConnection", connection)
    real_import = __import__

    def guarded(name, *args, **kwargs):
        if name == "openai" or name.startswith("openai.") or name == "httpx":
            raise AssertionError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", guarded)


def test_a_fact_call_posts_chat_completions_without_importing_openai(monkeypatch):
    _install(monkeypatch, _Connection)
    seen = []
    invoke = deepseek_invoke(
        api_key=SECRET, base_url="http://127.0.0.1:9", model_target=TARGET,
        max_response_tokens=64, timeout_seconds=30, on_usage=seen.append)
    assert invoke(DOSSIER) == ANSWER.encode("utf-8")
    sent = _Connection.last.sent
    assert sent[0] == "POST"
    assert sent[1] == "/chat/completions"
    assert sent[3]["Authorization"] == "Bearer " + SECRET
    body = json.loads(sent[2].decode("utf-8"))
    assert body == request_body(
        model_id=TARGET.model_id, max_tokens=64,
        prompt=DOSSIER.decode("utf-8"), temperature=JUDGE_SAMPLING)
    assert SECRET not in sent[2].decode("utf-8")
    assert seen[0].prompt_tokens == 11
    assert seen[0].prompt_cache_hit_tokens == 2
    assert _Connection.last.closed


def test_an_http_failure_names_the_status_and_not_the_key(monkeypatch):
    class Refused(_Connection):
        def getresponse(self):
            return _Response(401, SECRET.encode("utf-8"))

    _install(monkeypatch, Refused)
    invoke = deepseek_invoke(
        api_key=SECRET, base_url="http://127.0.0.1:9", model_target=TARGET,
        max_response_tokens=64, timeout_seconds=30)
    with pytest.raises(ProviderDidNotAnswer) as raised:
        invoke(DOSSIER)
    text = str(raised.value)
    assert "HTTP 401" in text
    assert SECRET not in text


def test_a_transport_error_that_contains_the_key_is_replaced(monkeypatch):
    class Leaks(_Connection):
        def connect(self):
            raise OSError(f"dial failed {SECRET}")

    _install(monkeypatch, Leaks)
    invoke = deepseek_invoke(
        api_key=SECRET, base_url="http://127.0.0.1:9", model_target=TARGET,
        max_response_tokens=64, timeout_seconds=30)
    with pytest.raises(ProviderDidNotAnswer) as raised:
        invoke(DOSSIER)
    assert SECRET not in str(raised.value)
    assert SECRET not in repr(raised.value)


def test_a_body_that_is_not_json_is_not_an_answer(monkeypatch):
    class Garbage(_Connection):
        def getresponse(self):
            return _Response(200, b"not-json")

    _install(monkeypatch, Garbage)
    invoke = deepseek_invoke(
        api_key=SECRET, base_url="http://127.0.0.1:9", model_target=TARGET,
        max_response_tokens=64, timeout_seconds=30)
    with pytest.raises(NoAnswerFromModel) as raised:
        invoke(DOSSIER)
    assert SECRET not in str(raised.value)
