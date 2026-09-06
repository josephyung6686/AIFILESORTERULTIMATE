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
from readers.model_ollama import (
    CONTEXT_GRANULARITY, LOCAL, PROVIDER, DEFAULT_BASE_URL,
    ModelVisibleBytesNotText, NoAnswerFromModel, OllamaContextExceeded,
    OllamaUnavailable, TargetIsNotThisTransport, ollama_invoke,
)

TARGET = ModelTarget(locality="local", model_id="qwen3:8b", provider="ollama")

#: Big enough that every test here fits under it without thinking about it. The
#: NUMBER is the deployment's and `cli.py` picks it; these tests only care that
#: what is sent is derived from the payload and bounded by this.
CEILING = 32768
RESPONSE_TOKENS = 512


def fake_post(captured):
    def post(url: str, body: bytes, *, timeout: float) -> bytes:
        captured["url"] = url
        captured["body"] = json.loads(body)
        captured["timeout"] = timeout
        answer = {"message": {"role": "assistant",
                              "content": captured.get("reply", '{"claims":[]}')},
                  "done": True,
                  "done_reason": captured.get("done_reason", "stop"),
                  "prompt_eval_count": captured.get("prompt_eval_count", 12)}
        if "thinking" in captured:
            answer["message"]["thinking"] = captured["thinking"]
        return json.dumps(answer).encode("utf-8")
    return post


def _invoke(captured, **overrides):
    settings = dict(model_target=TARGET, base_url=DEFAULT_BASE_URL,
                    max_response_tokens=RESPONSE_TOKENS,
                    context_ceiling=CEILING, post=fake_post(captured),
                    timeout_seconds=5.0)
    settings.update(overrides)
    return ollama_invoke(**settings)


# --- the bytes, unchanged -----------------------------------------------------

def test_the_dossier_bytes_are_what_the_model_is_asked():
    """P8 hands `invoke` the exact model-visible bytes it assembled -- prompt,
    schema and released evidence together -- and the transport's whole job is to
    put those bytes in front of the model unchanged.

    Rewriting them here would mean the release ledger recorded one thing and the
    model saw another, which is the failure P7's whole audit trail exists to make
    impossible. The message shape is `model_deepseek`'s: one user message carrying
    the payload and nothing beside it.
    """
    captured = {}
    _invoke(captured)(b"DOSSIER BYTES")

    assert captured["body"]["messages"] == [
        {"role": "user", "content": "DOSSIER BYTES"}]
    assert captured["body"]["model"] == "qwen3:8b"
    assert captured["url"].endswith("/api/chat")


def test_the_models_own_answer_comes_back_as_bytes():
    """`invoke` returns the model's answer and nothing of its own. P8 validates
    those bytes; a transport that repaired them would be validating them first,
    in the one place with no evidence to validate against."""
    captured = {"reply": '{"claims":[{"claim_ref":"c1"}]}'}

    assert _invoke(captured)(b"x") == b'{"claims":[{"claim_ref":"c1"}]}'


def test_the_call_is_deterministic():
    """A run must be replayable. §8.5's replay compares two runs of one corpus, so
    a sampling temperature would make the product's own evaluation harness
    meaningless -- and `00` asks for deterministic scores everywhere else."""
    captured = {}
    _invoke(captured)(b"x")

    assert captured["body"]["options"]["temperature"] == 0
    assert captured["body"]["stream"] is False
    # JSON mode: P8 parses the reply against `response_schema_bytes`, and a model
    # free to answer in prose fails that check for a reason that is not about the
    # evidence.
    assert captured["body"]["format"] == "json"


# --- thinking is off, and it is off at the API --------------------------------

def test_thinking_is_turned_off_in_the_request():
    """`104` R-18 and `103` §28: a thinking model spends the shared budget
    thinking and never begins writing. MEASURED on the cloud tier -- four real
    dossiers, `finish_reason == "length"`, `completion_tokens == 8192`, zero
    answer characters -- and `qwen3:8b` is a thinking model by default.

    Measured here too, on 2026-09-05 against ollama 0.31.1: the same prompt with
    `think` absent came back carrying a full `thinking` block, and with
    `think: false` came back with none. So it is sent on every request rather
    than trusted to a default.
    """
    captured = {}
    _invoke(captured)(b"x")

    assert captured["body"]["think"] is False


def test_a_thinking_block_that_came_back_anyway_is_a_refusal():
    """`think: false` is a REQUEST, and a version that ignores it is a version
    whose budget went to thinking. The answer that arrives beside it may be
    complete or may be what was left; the transport cannot tell, and validating
    it would record the model's reading of evidence it may never have finished
    reading. So it refuses and names the parameter that was not honoured, which
    is the one thing a person can act on."""
    captured = {"thinking": "Okay, let me consider every field in turn..."}

    with pytest.raises(NoAnswerFromModel, match="think"):
        _invoke(captured)(b"x")


# --- the context window, which is the one that silently loses evidence --------

def test_the_context_window_is_sized_from_the_payload_and_sent():
    """THE FINDING THAT MADE THIS PARAMETER MANDATORY, measured on ollama 0.31.1
    on 2026-09-05: a ~96,000-character prompt was silently truncated to 2,050
    tokens and the model answered CONFIDENTLY with a value that was not in the
    text -- the marker sentence at the very start had been cut away and it
    invented one. Nothing in the response says a truncation happened.

    That is the worst failure this product can have: not a refusal, not an
    abstention, but a fabricated fact about someone's file with a citation the
    evidence no longer contains. `num_ctx` defaults to a small window and is not
    negotiated, so it is computed from the bytes actually being sent and sent
    with them."""
    captured = {}
    _invoke(captured)(b"x" * 8000)

    options = captured["body"]["options"]
    assert options["num_predict"] == RESPONSE_TOKENS
    # Room for the prompt AND the answer: a window that fits only the prompt
    # truncates the prompt to make room for the reply.
    assert options["num_ctx"] >= 8000 // 2 + RESPONSE_TOKENS
    assert options["num_ctx"] <= CEILING
    assert options["num_ctx"] % CONTEXT_GRANULARITY == 0


def test_a_small_dossier_does_not_pay_for_a_large_window():
    """Sized from the payload rather than pinned at the ceiling, because the
    window is memory: the KV cache is allocated for `num_ctx`, and a run over
    thousands of small files would hold the largest window any of them might have
    needed. The ceiling is the bound, not the value."""
    captured = {}
    _invoke(captured)(b"x" * 40)

    assert captured["body"]["options"]["num_ctx"] < CEILING


def test_a_payload_that_cannot_fit_the_ceiling_is_refused_before_the_socket():
    """IMPOSSIBLE BY CONSTRUCTION, not caught afterwards. A payload too large for
    the window this deployment allows is not sent at all: sending it would
    truncate it, and a truncated dossier is answered rather than refused.

    The refusal is the honest outcome -- P8 records `client_raised` and the file
    keeps its open fields -- and the alternative is a fact invented from evidence
    the model was never shown."""
    captured = {}
    invoke = _invoke(captured, context_ceiling=2048)

    with pytest.raises(OllamaContextExceeded, match="2048"):
        invoke(b"x" * 60_000)
    assert "body" not in captured, "nothing may be sent when the window cannot hold it"


def test_a_payload_that_beat_the_bytes_per_token_floor_is_a_refusal():
    """The receipt behind the construction, checking the ONE assumption it rests
    on. The window is sized above `bytes / BYTES_PER_TOKEN_FLOOR`, which is an
    upper bound on the prompt's true token count -- so the prompt fits and
    truncation cannot happen, UNLESS a payload tokenises worse than that floor.

    `prompt_eval_count` is the only way to find that out, and above the bound the
    answer is refused rather than validated. A cache hit reports FEWER tokens and
    never more, so this cannot fire on a prompt that fitted."""
    captured = {"prompt_eval_count": 100_000}

    with pytest.raises(NoAnswerFromModel, match="truncat"):
        _invoke(captured)(b"x" * 4000)


def test_a_prompt_that_fitted_is_not_refused_by_the_receipt():
    """The negative twin, so the receipt cannot become a refusal of ordinary
    calls. 4,000 bytes at the floor is 2,000 tokens plus the template's headroom;
    a real tokeniser does much better than that, and the number it reports back
    must not be read as a truncation."""
    captured = {"prompt_eval_count": 1100, "reply": '{"claims":[]}'}

    assert _invoke(captured)(b"x" * 4000) == b'{"claims":[]}'


def test_a_bigger_window_is_not_a_fix_and_the_refusal_is():
    """MEASURED AT THREE WINDOW SIZES, 2026-09-05, ollama 0.31.1, qwen3:8b, on a
    103,013-byte prompt whose answer sat in its first sentence:

      * `num_ctx` unset: 2,050 prompt tokens read, answered `"The 3776."`
      * `num_ctx` 8,192: 4,098 read, answered `"The8"`
      * `num_ctx` 16,384: 8,194 read, answered `"The93"`

    The server kept `num_ctx / 2` every time, invented a different wrong value
    each time, and never once said a word had been dropped. Raising the number
    only moves where the evidence is cut, so the product does not raise it: a
    payload that will not fit under the deployment's ceiling is refused before
    the socket. This is that case, at the real byte count."""
    captured = {}
    invoke = _invoke(captured, context_ceiling=16384, max_response_tokens=2048)

    with pytest.raises(OllamaContextExceeded):
        invoke(b"x" * 103_013)
    assert "body" not in captured


def test_the_window_that_was_used_is_readable_but_nothing_reads_it_yet():
    """§8.4 audits what the model was given, and the window is part of that: two
    runs over one file under different windows are two different questions.

    THIS IS A HOOK AND NOT YET A RECORD, and the name says so rather than
    implying otherwise. Nothing persists this number today. The two rows that
    could carry it are `privacy.release_ledger.model_target`, which is P7's
    three-field `ModelTarget` and describes a DEPLOYMENT rather than a call, and
    `llm_harness.llm_response`, which is P8's schema -- neither belongs to the
    readers layer, and inventing a third table here would be a second place
    claiming to say what one call was given.

    So the value is exposed where a P8 or P7 owner can reach it, and the gap is
    reported rather than papered over."""
    captured = {}
    invoke = _invoke(captured)
    invoke(b"x" * 8000)

    assert invoke.context_tokens == captured["body"]["options"]["num_ctx"]


# --- the locality claim, checked where it is a fact ---------------------------

def test_a_host_that_is_not_loopback_is_refused_when_the_client_is_built():
    """`model_deepseek` makes this argument the other way round: the socket is the
    fact, so the socket's module is where the claim is measured. A `ModelTarget`
    claiming `locality="local"` while the request leaves the machine would be
    authorized by `offline` -- whose whole text is "No content leaves the device"
    -- and every released dossier would leave under a policy saying it does not.

    The endpoint is configurable so a test can point at a stub on another port.
    It is not configurable to another HOST, because that is the claim."""
    with pytest.raises(TargetIsNotThisTransport, match="loopback"):
        _invoke({}, base_url="http://ollama.example.com:11434")


def test_a_loopback_endpoint_on_another_port_is_accepted():
    """Which is what makes the stub-server test possible at all, and what a person
    running ollama on a second port needs."""
    captured = {}
    _invoke(captured, base_url="http://127.0.0.1:54321")(b"x")

    assert captured["url"] == "http://127.0.0.1:54321/api/chat"


def test_localhost_and_the_v6_loopback_are_the_same_claim():
    for endpoint in ("http://localhost:11434", "http://[::1]:11434"):
        captured = {}
        _invoke(captured, base_url=endpoint)(b"x")
        assert captured["url"].startswith(endpoint)


def test_a_target_that_is_not_local_is_refused():
    """The mirror of `model_deepseek._require_target`. A cloud target pointed at
    this transport would have the gate deciding about one destination while the
    bytes went to another."""
    cloud = ModelTarget(locality="cloud", model_id="qwen3:8b", provider="ollama")

    with pytest.raises(TargetIsNotThisTransport, match=LOCAL):
        _invoke({}, model_target=cloud)


def test_a_target_naming_another_provider_is_refused():
    other = ModelTarget(locality="local", model_id="qwen3:8b", provider="deepseek")

    with pytest.raises(TargetIsNotThisTransport, match=PROVIDER):
        _invoke({}, model_target=other)


# --- refusals, and never an empty answer --------------------------------------

def test_a_model_that_is_not_running_is_refused_not_guessed():
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

    with pytest.raises(OllamaUnavailable, match="ollama"):
        _invoke({}, post=refuse)(b"x")


def test_an_answer_cut_off_at_the_ceiling_is_a_refusal_not_an_answer():
    """`model_deepseek` refuses `finish_reason == "length"` in these words: what
    came back is part of a document, and validated it would be schema-invalid with
    the rejection recorded against the model rather than against our ceiling.
    ollama spells the same thing `done_reason`."""
    captured = {"done_reason": "length", "reply": '{"claims":[{"payl'}

    with pytest.raises(NoAnswerFromModel, match="length"):
        _invoke(captured)(b"x")


def test_an_empty_answer_is_a_refusal():
    """Empty bytes parse as no claims and would be recorded as a rejected model
    answer; there is no model answer here to reject."""
    captured = {"reply": "   "}

    with pytest.raises(NoAnswerFromModel):
        _invoke(captured)(b"x")


def test_a_deployment_with_no_response_ceiling_refuses_to_be_built():
    """Every number this module needs is injected and none is invented, which is
    `model_deepseek`'s rule and `84` §1's: `src/` picks no numbers."""
    with pytest.raises(ValueError, match="max_response_tokens"):
        _invoke({}, max_response_tokens=0)
    with pytest.raises(ValueError, match="context_ceiling"):
        _invoke({}, context_ceiling=0)
    with pytest.raises(ValueError, match="timeout"):
        _invoke({}, timeout_seconds=0)


def test_bytes_that_are_not_text_are_refused_rather_than_repaired():
    with pytest.raises(ModelVisibleBytesNotText):
        _invoke({})(b"\xff\xfe not utf-8")
