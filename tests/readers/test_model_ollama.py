# tests/readers/test_model_ollama.py
"""`ModelClient.invoke` backed by a user-installed local model (ollama).

P7 §8.4 names four operation modes and this is the second of them verbatim:
"Local extraction plus a USER-INSTALLED LOCAL LLM for eligible dossiers." Nothing
here reaches the network beyond loopback, and the `ModelTarget` says so -- its
`locality` is `local`, which is what `00`'s audit record and P7's release ledger
both store about where the data went.

**The transport is injected.** These tests never start a model. A test that needed
ollama running would be a test that gets skipped on the machine that most needs to
run it, and `invoke` is a byte-in/byte-out function whose whole contract is
observable without one.
"""
from __future__ import annotations

import json

import pytest

from privacy.release import ModelTarget
from readers.model_ollama import OllamaUnavailable, ollama_invoke


LOCAL = ModelTarget(locality="local", model_id="qwen2.5:3b", provider="ollama")


def fake_post(captured):
    def post(url: str, body: bytes, *, timeout: float) -> bytes:
        captured["url"] = url
        captured["body"] = json.loads(body)
        captured["timeout"] = timeout
        return json.dumps({"response": captured["reply"]}).encode("utf-8")
    return post


def test_the_dossier_bytes_are_what_the_model_is_asked(tmp_path):
    """P8 hands `invoke` the exact model-visible bytes it assembled -- prompt,
    schema and released evidence together -- and the transport's whole job is to
    put those bytes in front of the model unchanged.

    Rewriting them here would mean the release ledger recorded one thing and the
    model saw another, which is the failure P7's whole audit trail exists to make
    impossible.
    """
    captured = {"reply": '{"claims":[]}'}
    invoke = ollama_invoke(model_id="qwen2.5:3b", post=fake_post(captured))

    invoke(b"DOSSIER BYTES")

    assert captured["body"]["prompt"] == "DOSSIER BYTES"
    assert captured["body"]["model"] == "qwen2.5:3b"


def test_the_call_is_deterministic_and_local(tmp_path):
    """A run must be replayable. §8.5's replay compares two runs of one corpus, so
    a sampling temperature would make the product's own evaluation harness
    meaningless -- and `00` asks for deterministic scores everywhere else.

    The host is loopback and is not configurable to anything else by this
    function: the `ModelTarget` says `locality=local`, and a transport that could
    be pointed elsewhere would make that claim unverifiable.
    """
    captured = {"reply": '{"claims":[]}'}
    invoke = ollama_invoke(model_id="qwen2.5:3b", post=fake_post(captured))

    invoke(b"x")

    assert captured["url"].startswith("http://127.0.0.1:")
    assert captured["body"]["options"]["temperature"] == 0
    assert captured["body"]["stream"] is False
    # JSON mode: P8 parses the reply against `response_schema_bytes`, and a model
    # free to answer in prose fails that check for a reason that is not about the
    # evidence.
    assert captured["body"]["format"] == "json"


def test_the_models_own_answer_comes_back_as_bytes(tmp_path):
    """`invoke` returns the model's answer and nothing of its own. P8 validates
    those bytes; a transport that repaired them would be validating them first,
    in the one place with no evidence to validate against."""
    captured = {"reply": '{"claims":[{"claim_ref":"c1"}]}'}
    invoke = ollama_invoke(model_id="qwen2.5:3b", post=fake_post(captured))

    assert invoke(b"x") == b'{"claims":[{"claim_ref":"c1"}]}'


def test_a_model_that_is_not_running_is_refused_not_guessed(tmp_path):
    """The negative twin, and the one that matters for a local model: ollama is a
    process the person may simply not have started.

    `OllamaUnavailable` is raised so P8's `CallFailed` path records that the call
    did not happen. Returning empty bytes would be indistinguishable from a model
    that answered with nothing, and §6.10's abstention reasons have no member for
    "the call did not happen" -- so inventing an empty answer would file a file on
    the strength of a model that was never asked.
    """
    def refuse(url, body, *, timeout):
        raise ConnectionRefusedError("nothing listening")

    invoke = ollama_invoke(model_id="qwen2.5:3b", post=refuse)

    with pytest.raises(OllamaUnavailable, match="ollama"):
        invoke(b"x")
