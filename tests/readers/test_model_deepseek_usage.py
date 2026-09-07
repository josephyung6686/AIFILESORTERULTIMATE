# tests/readers/test_model_deepseek_usage.py
"""R-14: the request asks for JSON, and what the provider says it spent is read.

`104` R-14: *"No `response_format` at the API; `actual_cost` is a constant, not
observed usage."* Two halves, and they land differently.

**JSON mode lands whole.** Every DeepSeek call now carries
`response_format={"type": "json_object"}`. `model_deepseek.py`'s own docstring said
nothing here may set one, and that rule is right about what it was written against:
a knob that changes what the model is ASKED is a prompt nobody approved. This is not
that. The ratified A_fact template already tells the model "answer with one JSON
object and nothing else" and "The first character you send is { and the last
character you send is }", so JSON mode is the transport ENFORCING the ratified text
rather than adding to it -- and the failure it removes is the one
`response_text` already has to raise on, a reasoning model that spends the ceiling
on prose and returns something that is not an object.

**Usage stops at a boundary**, the same shape as R-08. `ModelClient.invoke` is
`Callable[[bytes], bytes]` and `ModelResponse` is `llm_harness/transport.py`; the
client is built in `readers/model_routing.py`. Neither is this branch's. So the
usage a provider reports cannot ride the return path, and it leaves through an
injected sink instead: `deepseek_invoke(..., on_usage=...)`. Wiring that sink is one
line in `deepseek_routing`, and it is reported rather than taken.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from privacy.release import ModelTarget  # noqa: E402
from readers.model_deepseek import (  # noqa: E402
    JSON_MODE,
    PROVIDER,
    PromptDoesNotAskForJson,
    Usage,
    deepseek_invoke,
    request_body,
    usage_of,
)

ENDPOINT = "https://api.deepseek.example"
TARGET = ModelTarget(locality="cloud", model_id="a-model", provider=PROVIDER)

#: The ratified A_fact template's own words, which is what makes JSON mode legal
#: here rather than a new instruction.
ASKS_FOR_JSON = "Read it and answer with one JSON object and nothing else."


class _Message:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _Choice:
    def __init__(self, content: str | None, finish_reason: str = "stop") -> None:
        self.message = _Message(content)
        self.finish_reason = finish_reason


class _Usage:
    def __init__(self, **fields) -> None:
        for name, value in fields.items():
            setattr(self, name, value)


class _Response:
    def __init__(self, *choices: _Choice, usage=None) -> None:
        self.choices = list(choices)
        if usage is not None:
            self.usage = usage


def _answering(text: str, usage=None):
    def send(*, api_key, base_url, model_id, max_tokens, prompt,
             timeout_seconds=None):
        return _Response(_Choice(text), usage=usage)
    return send


def _built(**overrides):
    arguments = dict(api_key="k", base_url=ENDPOINT, model_target=TARGET,
                     max_response_tokens=64, send=_answering("{}"))
    arguments.update(overrides)
    return deepseek_invoke(**arguments, timeout_seconds=30)


# --- the request asks for JSON ---------------------------------------------------


def test_the_request_carries_json_mode():
    body = request_body(model_id="a-model", max_tokens=64, prompt=ASKS_FOR_JSON)

    assert body["response_format"] == {"type": "json_object"}
    assert JSON_MODE == {"type": "json_object"}


def test_the_request_is_otherwise_exactly_what_it_was():
    """One knob added and nothing else. No system message, no temperature, no `n`
    -- each of those would be a prompt nobody approved and no record names, which is
    the rule this module states about itself and which still holds."""
    body = request_body(model_id="a-model", max_tokens=64, prompt=ASKS_FOR_JSON)

    assert set(body) == {"model", "max_tokens", "messages", "response_format"}
    assert body["messages"] == [{"role": "user", "content": ASKS_FOR_JSON}]
    assert body["model"] == "a-model"
    assert body["max_tokens"] == 64


def test_a_prompt_that_never_says_json_is_refused_before_the_socket():
    """DeepSeek's JSON mode requires the word in the prompt and returns an empty
    reply without it -- which arrives here as `NoAnswerFromModel` and is recorded
    against the model, for a mistake made on this side. Refused where it is a fact
    instead: a prompt that does not ask for JSON must not be sent under a flag that
    demands it."""
    with pytest.raises(PromptDoesNotAskForJson):
        request_body(model_id="a-model", max_tokens=64,
                     prompt="Describe this file in a sentence.")


def test_the_word_is_looked_for_case_insensitively():
    for prompt in ("answer with json", "one JSON object", "a Json reply"):
        assert request_body(model_id="m", max_tokens=1, prompt=prompt)


def test_the_shipped_a_fact_prompt_already_satisfies_the_precondition():
    """The guard above must never fire in production, and this is why it does not.

    Asked of the SHIPPED bytes rather than of a sentence quoted here: the day
    somebody ratifies a revision that drops the word, this fails at build time
    instead of every call failing at the provider.
    """
    from llm_harness.prompt_library import a_fact_template_folder_levels_bytes

    template = a_fact_template_folder_levels_bytes().decode("utf-8")
    assert request_body(model_id="m", max_tokens=1, prompt=template)
    assert "JSON object" in template


# --- and what it spent is read ---------------------------------------------------


def test_usage_is_read_off_the_response_including_the_cache_counters():
    """`prompt_cache_hit_tokens` is the number `104` R-58 predicts and nothing in
    the product recorded. Without it the prefix work is visible only in a bench."""
    usage = usage_of(_Response(_Choice("{}"), usage=_Usage(
        prompt_tokens=4970, completion_tokens=120, total_tokens=5090,
        prompt_cache_hit_tokens=4480, prompt_cache_miss_tokens=490)),
        model_id="a-model")

    assert usage == Usage(
        model_id="a-model", prompt_tokens=4970, completion_tokens=120,
        prompt_cache_hit_tokens=4480, prompt_cache_miss_tokens=490,
        response_format="json_object")


def test_a_provider_that_reports_no_usage_is_an_absence_and_not_a_zero():
    """A zero would read as "this call cost nothing", which is a claim. `None` is
    what is actually known."""
    assert usage_of(_Response(_Choice("{}")), model_id="a-model") is None


def test_the_cache_counters_are_optional_and_the_token_counts_are_not():
    """Only DeepSeek publishes the two cache fields. A provider without them still
    reports what it charged for, and that half must survive."""
    usage = usage_of(_Response(_Choice("{}"), usage=_Usage(
        prompt_tokens=100, completion_tokens=10)), model_id="a-model")

    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 10
    assert usage.prompt_cache_hit_tokens is None
    assert usage.prompt_cache_miss_tokens is None


def test_the_sink_is_handed_the_usage_of_every_answered_call():
    seen: list[Usage] = []
    invoke = _built(
        send=_answering("{}", usage=_Usage(
            prompt_tokens=10, completion_tokens=2,
            prompt_cache_hit_tokens=8, prompt_cache_miss_tokens=2)),
        on_usage=seen.append)

    invoke(ASKS_FOR_JSON.encode("utf-8"))
    invoke(ASKS_FOR_JSON.encode("utf-8"))

    assert len(seen) == 2
    assert {item.prompt_cache_hit_tokens for item in seen} == {8}


def test_no_sink_is_the_default_and_costs_nothing():
    """A deployment that records no usage is a real deployment -- `model_ollama`'s
    caller does not have this seam -- and it must not have to supply a sink."""
    assert _built()(ASKS_FOR_JSON.encode("utf-8")) == b"{}"


def test_a_provider_with_no_usage_block_calls_the_sink_with_nothing():
    """The sink hears about the call either way, because "the provider told us
    nothing" is itself the audit's answer, and silence is indistinguishable from a
    call that never happened."""
    seen: list[Usage | None] = []
    _built(send=_answering("{}"), on_usage=seen.append)(
        ASKS_FOR_JSON.encode("utf-8"))

    assert seen == [None]


# --- and it is recordable -------------------------------------------------------


OBSERVED = {
    "model_id": "a-model", "prompt_tokens": 4970, "completion_tokens": 120,
    "prompt_cache_hit_tokens": 4480, "prompt_cache_miss_tokens": 490,
    "response_format": "json_object",
}


def test_the_usage_row_carries_the_cache_counters(conn):
    from llm_harness.schema import create_llm_schema
    from llm_harness.store import record_call_usage

    create_llm_schema(conn)
    record_call_usage(
        conn, dossier_id="d-1", release_id="r-1", reserved_cost="1",
        observed=OBSERVED, observed_at="2026-09-06T00:00:00+00:00")

    row = conn.execute("SELECT * FROM llm_call_usage").fetchone()
    assert row["prompt_cache_hit_tokens"] == 4480
    assert row["prompt_tokens"] == 4970
    assert row["dossier_id"] == "d-1"
    assert row["response_format"] == "json_object"
    assert row["reserved_cost"] == "1"


def test_a_call_the_provider_said_nothing_about_is_still_a_row(conn):
    """`{}` is a real answer: the call was made and the budget spent for it. A row
    of nulls says "asked, and it told us nothing"; no row is indistinguishable from
    a call that never happened."""
    from llm_harness.schema import create_llm_schema
    from llm_harness.store import record_call_usage

    create_llm_schema(conn)
    record_call_usage(
        conn, dossier_id="d-1", release_id="r-1", reserved_cost="1",
        observed={}, observed_at="2026-09-06T00:00:00+00:00")

    row = conn.execute("SELECT * FROM llm_call_usage").fetchone()
    assert row["prompt_tokens"] is None
    assert row["model_id"] is None
    assert row["reserved_cost"] == "1"


def test_a_column_the_table_does_not_have_is_refused(conn):
    """A number nobody can read back is worse than a refusal, and dropping it
    silently would lose the one thing the row exists to keep."""
    from llm_harness.records import MalformedRecord
    from llm_harness.schema import create_llm_schema
    from llm_harness.store import record_call_usage

    create_llm_schema(conn)
    with pytest.raises(MalformedRecord):
        record_call_usage(
            conn, dossier_id="d-1", release_id="r-1", reserved_cost="1",
            observed={**OBSERVED, "reasoning_tokens": 40},
            observed_at="2026-09-06T00:00:00+00:00")


def test_the_usage_row_is_append_only_like_every_other_p8_row(conn):
    from llm_harness.schema import create_llm_schema
    from llm_harness.store import record_call_usage

    create_llm_schema(conn)
    record_call_usage(
        conn, dossier_id="d-1", release_id="r-1", reserved_cost="1",
        observed=OBSERVED, observed_at="2026-09-06T00:00:00+00:00")

    import sqlite3

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM llm_call_usage")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE llm_call_usage SET prompt_tokens = 2")


def test_what_a_json_mode_flag_still_does_not_reach():
    """THE GAP, PINNED. `prompt_fingerprint` hashes the template, its id, the
    response schema, the shaping policy and the call site -- and no transport
    parameter. So two runs, one with JSON mode and one without, carry the same
    fingerprint and are indistinguishable in every audit row.

    `response_format` is therefore recorded on the usage row, which is the only
    place in the product that can say which of the two a call was. Widening the
    fingerprint to cover transport parameters is `llm_harness/fingerprint.py` and is
    not this branch's; this test fails the day it happens, which is the signal to
    drop the column.
    """
    from llm_harness.fingerprint import prompt_fingerprint
    from llm_harness.records import PromptDefinition

    definition = PromptDefinition(
        call_site="A_fact", call_site_version="1", template_id="t",
        template_bytes=b"answer in json", response_schema_bytes=b"{}",
        shaping_policy_bytes=b"{}")
    assert "response_format" not in json.dumps(
        {"fingerprint": prompt_fingerprint(definition)})
