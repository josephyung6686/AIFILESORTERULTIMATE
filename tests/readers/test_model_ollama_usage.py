# tests/readers/test_model_ollama_usage.py
"""R-14 on the local transport: what ollama says a call cost reaches the row too.

The cloud half landed first, and left the deployment `104` D1 actually steers toward
recording nothing: `cli.model_route` gives the LOCAL model site A_fact whenever one
is configured, and `readers/model_ollama.py` named no usage field at all. So every
local fact call would have written a usage row carrying its reservation and no
tokens -- the ordinary case, not the exception.

`_answer` already read `prompt_eval_count`, for the truncation receipt, and threw it
away afterwards. This keeps it, adds `eval_count` beside it, and sends both out
through the same `on_usage` sink the cloud transport uses.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from privacy.release import ModelTarget  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    RESPONSE_FORMAT,
    Usage,
    ollama_invoke,
    usage_of,
)

TARGET = ModelTarget(locality="local", model_id="qwen3:8b", provider="ollama",
                     context_tokens=32768)
CEILING = 32768
RESPONSE_TOKENS = 512

#: A payload the size a real A_fact dossier is, and it has to be: the transport
#: refuses a reply claiming more prompt tokens than the bytes it sent could hold
#: (`BYTES_PER_TOKEN_FLOOR`, the truncation receipt), so a nine-byte stand-in beside
#: a 4,970-token count is a payload this module is right to reject. `104` R-58
#: measured the real thing at 8,020 template bytes plus a body under 9,000.
DOSSIER = b"x" * 10_000


def _reply(**overrides) -> dict:
    body = {
        "model": "qwen3:8b",
        "message": {"role": "assistant", "content": "{}"},
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": 4970,
        "eval_count": 120,
    }
    body.update(overrides)
    return body


def _answering(reply: dict):
    def post(url: str, body: bytes, *, timeout: float) -> bytes:
        return json.dumps(reply).encode("utf-8")
    return post


def _built(**overrides):
    arguments = dict(model_target=TARGET, base_url="http://127.0.0.1:11434",
                     max_response_tokens=RESPONSE_TOKENS, context_ceiling=CEILING,
                     timeout_seconds=30, post=_answering(_reply()))
    arguments.update(overrides)
    return ollama_invoke(**arguments)


# --- read ------------------------------------------------------------------------


def test_usage_is_read_off_the_reply():
    usage = usage_of(_reply(), model_id="qwen3:8b")

    assert usage == Usage(
        model_id="qwen3:8b", prompt_tokens=4970, completion_tokens=120,
        prompt_cache_hit_tokens=None, prompt_cache_miss_tokens=None,
        response_format=RESPONSE_FORMAT)


def test_the_cache_counters_are_absent_and_that_is_the_truth():
    """ollama reuses its KV cache across prompts sharing a prefix -- which is what
    `104` R-52 and R-58 both exploit -- and `/api/chat` reports no count for it. A
    zero would claim nothing was served from cache; `None` says nobody counted.
    `prompt_eval_count` does FALL on a hit, so the effect is visible in the total
    even though its size is not reported."""
    usage = usage_of(_reply(prompt_eval_count=490), model_id="qwen3:8b")

    assert usage.prompt_cache_hit_tokens is None
    assert usage.prompt_cache_miss_tokens is None
    assert usage.prompt_tokens == 490


def test_a_reply_with_no_counts_is_an_absence_and_not_a_zero():
    assert usage_of({"message": {"content": "{}"}}, model_id="m") is None
    assert usage_of(_reply(eval_count=None), model_id="m") is None
    assert usage_of("not an object", model_id="m") is None


def test_the_response_format_recorded_is_the_one_actually_sent():
    """The request field and the record read the same constant, so they cannot
    disagree about what the call was made with -- which is the whole reason the
    column exists: `prompt_fingerprint` covers no transport parameter."""
    sent = {}

    def post(url, body, *, timeout):
        sent.update(json.loads(body))
        return json.dumps(_reply()).encode("utf-8")

    seen: list[Usage] = []
    _built(post=post, on_usage=seen.append)(DOSSIER)

    assert sent["format"] == RESPONSE_FORMAT
    assert seen[0].response_format == RESPONSE_FORMAT


# --- and sent ---------------------------------------------------------------------


def test_the_sink_is_handed_the_usage_of_every_answered_call():
    seen: list[Usage | None] = []
    invoke = _built(on_usage=seen.append)

    invoke(DOSSIER)
    invoke(DOSSIER + b"!")

    assert [item.prompt_tokens for item in seen] == [4970, 4970]


def test_no_sink_is_the_default_and_costs_nothing():
    assert _built()(DOSSIER) == b"{}"


def test_a_refusal_is_not_billed():
    """`done_reason='length'` is our ceiling cutting the answer off, and
    `_answer` raises on it. Nothing reaches the sink, because a refusal is not a
    call this run may record a cost for."""
    from readers.model_ollama import NoAnswerFromModel

    seen: list = []
    invoke = _built(post=_answering(_reply(done_reason="length")),
                    on_usage=seen.append)

    with pytest.raises(NoAnswerFromModel):
        invoke(DOSSIER)
    assert seen == []


# --- one shape, two transports ----------------------------------------------------


def test_the_two_usage_records_cannot_drift():
    """`model_ollama` imports nothing from `src/` at run time -- the property
    `model_deepseek`'s own `CLOUD` constant cites when it declines to import P7's
    vocabulary -- so the record is defined twice on purpose. This is what keeps the
    duplication honest: `cli.UsageMailbox` reads both by attribute, so a field added
    to one and not the other would silently produce a row with a missing column.
    """
    from readers.model_deepseek import Usage as CloudUsage

    names = [f.name for f in dataclasses.fields(Usage)]
    assert names == [f.name for f in dataclasses.fields(CloudUsage)]

    from llm_harness.store import USAGE_COLUMNS

    assert sorted(names) == sorted(USAGE_COLUMNS)


def test_the_mailbox_translates_a_local_usage_the_same_way():
    import cli

    box = cli.UsageMailbox()
    box(usage_of(_reply(), model_id="qwen3:8b"))
    taken = box.take()

    assert taken["prompt_tokens"] == 4970
    assert taken["completion_tokens"] == 120
    assert taken["response_format"] == RESPONSE_FORMAT
    assert taken["prompt_cache_hit_tokens"] is None
