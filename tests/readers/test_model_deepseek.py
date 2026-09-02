# tests/readers/test_model_deepseek.py
"""`ModelClient.invoke` backed by DeepSeek's OpenAI-compatible API.

The twin of `test_model_anthropic.py`, and it exists for the same reason: this is
a module that can put a byte on the internet, and everything above it has only
ever been proven against a recorded-bytes stand-in.

**The socket is injected.** `_send` is two statements: import the SDK, call
`chat.completions.create`. Everything else -- the credential refusal, the endpoint
refusal, the target check, the decode, the response handling -- is pure and every
line of it is exercised here. What is untested-by-default is exactly the two
statements that cannot run without a key and a bill.

**What is DIFFERENT from the Anthropic twin, and why it is tested here.** The
OpenAI-compatible client defaults its `base_url` to OpenAI's own endpoint. A
DeepSeek transport handed no endpoint would therefore call a DIFFERENT COMPANY
while the release ledger, the audit record and the screen all say `deepseek` --
the same class of falsehood `test_a_local_target_is_refused` exists to prevent,
pointed at the provider field instead of the locality field. So an absent endpoint
is a refusal here, and it is not one in the Anthropic module because there the SDK
has nowhere else to go.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from privacy.release import LOCALITIES, ModelTarget
from readers.model_deepseek import (
    BASE_URL_NAME,
    CLOUD,
    CREDENTIAL_NAME,
    PROVIDER,
    ModelCredentialMissing,
    ModelEndpointMissing,
    ModelVisibleBytesNotText,
    NoAnswerFromModel,
    TargetIsNotThisTransport,
    deepseek_invoke,
    response_text,
)

ENDPOINT = "https://api.deepseek.example"
TARGET = ModelTarget(locality="cloud", model_id="a-model", provider=PROVIDER)
LOCAL_TARGET = ModelTarget(locality="local", model_id="a-model", provider=PROVIDER)
OTHER_PROVIDER = ModelTarget(
    locality="cloud", model_id="a-model", provider="somebody-else")

#: One token of headroom. A literal ceiling inside the module under test would be
#: a number this part authored; here it is a test's own input, which is what it is.
ONE_TOKEN = 1


class _Message:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _Choice:
    def __init__(self, content: str | None, finish_reason: str = "stop") -> None:
        self.message = _Message(content)
        self.finish_reason = finish_reason


class _Response:
    def __init__(self, *choices: _Choice) -> None:
        self.choices = list(choices)


def _answering(text: str, captured: dict | None = None):
    def send(*, api_key, base_url, model_id, max_tokens, prompt):
        if captured is not None:
            captured.update(api_key=api_key, base_url=base_url, model_id=model_id,
                            max_tokens=max_tokens, prompt=prompt)
            captured.setdefault("calls", []).append(prompt)
        return _Response(_Choice(text))
    return send


def _built(**overrides):
    arguments = dict(api_key="k", base_url=ENDPOINT, model_target=TARGET,
                     max_response_tokens=ONE_TOKEN, send=_answering("{}"))
    arguments.update(overrides)
    return deepseek_invoke(**arguments)


# --- absent means refuse, and refuse is not "carry on without a model" ----------

def test_no_api_key_refuses_and_names_what_was_missing():
    with pytest.raises(ModelCredentialMissing) as raised:
        _built(api_key=None)
    message = str(raised.value)
    assert CREDENTIAL_NAME in message
    assert PROVIDER in message


def test_a_blank_api_key_is_absent_too():
    """Whitespace is not a key. Passed through, it fails at the provider one call
    later as an authentication error -- which reads to every layer above as "the
    model was asked and could not answer" rather than "nobody was asked"."""
    for blank in ("", "   ", "\n", "\t"):
        with pytest.raises(ModelCredentialMissing):
            _built(api_key=blank)


def test_no_base_url_refuses_and_names_what_was_missing():
    """THE refusal that is specific to this transport.

    `openai.OpenAI(api_key=...)` with no `base_url` calls OpenAI. A DeepSeek key
    sent there fails, but that is luck, not design: the module would have opened a
    socket to a company the `ModelTarget` does not name, and §8.4's audit record --
    "which model received the data" -- would be false at the one place in the
    product where it is written. `84` §1's rule is absent means refuse, never
    guess, and an SDK default is a guess this module did not make.
    """
    for absent in (None, "", "   "):
        with pytest.raises(ModelEndpointMissing) as raised:
            _built(base_url=absent)
        assert BASE_URL_NAME in str(raised.value)


def test_the_refusal_happens_before_a_run_can_start():
    """`deepseek_invoke` raises rather than returning an `invoke` that fails on
    first use. A deployment with no key stops before the scan, not after it -- and
    it can never return an `invoke` that answers with nothing, which every layer
    above would record as a schema-invalid model answer that no model gave."""
    with pytest.raises(ModelCredentialMissing):
        deepseek_invoke(api_key=None, base_url=ENDPOINT, model_target=TARGET,
                        max_response_tokens=ONE_TOKEN)


def test_a_ceiling_below_one_is_not_a_ceiling():
    for bad in (0, -1, None, "many"):
        with pytest.raises(ValueError, match="max_response_tokens"):
            _built(max_response_tokens=bad)


# --- the target claim, measured where it is a fact -----------------------------

def test_a_local_target_is_refused():
    """The most dangerous construction in this file.

    `Gate.release` decides by `model_target.locality`. §8.4's `offline` mode is
    "No content leaves the device" and `local_model` is "a user-installed local
    LLM". A call over the internet wearing `locality="local"` is authorized by
    both, and every released dossier would leave the device under a policy whose
    whole text says it does not. The gate is told the locality; it cannot measure
    it. This module can, because it is the one that opens the socket.
    """
    with pytest.raises(TargetIsNotThisTransport, match="local"):
        _built(model_target=LOCAL_TARGET)


def test_another_providers_target_is_refused():
    """§8.4 audits "which model received the data". A target naming a provider
    this module does not call makes that record false where it is written."""
    with pytest.raises(TargetIsNotThisTransport, match="somebody-else"):
        _built(model_target=OTHER_PROVIDER)


def test_the_cloud_constant_is_p7s_own_value():
    """Spelled here so the module imports nothing from `src/` at run time, and
    checked here so the spelling cannot drift from P7's closed pair."""
    assert CLOUD == LOCALITIES[1]


# --- bytes in, bytes out, and nothing invented in between ----------------------

def test_the_released_bytes_are_sent_verbatim():
    captured: dict = {}
    invoke = _built(api_key="secret", send=_answering('{"claims": []}', captured))
    invoke(b'{"dossier": "released"}')
    assert captured["prompt"] == '{"dossier": "released"}'
    assert captured["model_id"] == "a-model"
    assert captured["max_tokens"] == ONE_TOKEN
    assert captured["api_key"] == "secret"
    assert captured["base_url"] == ENDPOINT


def test_the_answer_comes_back_as_bytes():
    assert _built(send=_answering('{"claims": []}'))(b"x") == b'{"claims": []}'


def test_bytes_that_are_not_text_are_refused_and_never_repaired():
    """`transport.issue` catches whatever `invoke` raises and records a
    `client_raised` failure. A lossy decode would instead send the model something
    the stored prompt fingerprint no longer describes."""
    with pytest.raises(ModelVisibleBytesNotText):
        _built()(b"\xff\xfe not utf-8")


def test_one_invoke_is_exactly_one_request():
    """`harness.run_call` reserves one budget call and `transport.issue` consumes
    one release per `invoke`. A retry loop here over an ANSWER would make one
    reservation pay for several requests, and §8.6's ceiling -- the only thing
    between a wired model and unbounded spend -- would be counting the wrong
    thing. (The SDK retries 429s and 5xx below this line; those are neither billed
    nor answers.)"""
    captured: dict = {}
    _built(send=_answering("{}", captured))(b"x")
    assert captured["calls"] == ["x"]


# --- what comes back, judged without calling anything --------------------------

def test_a_finished_answer_is_returned():
    assert response_text(_Response(_Choice('{"claims": []}'))) == '{"claims": []}'


def test_a_truncated_answer_is_raised_and_never_returned():
    """`finish_reason == "length"` arrives over HTTP 200 with a body that looks
    like an answer and is half a JSON document. Parsed it is schema-invalid, and
    P8 would record the rejection against the model rather than against our
    ceiling -- a person shown "the model could not read your file" about a file
    the model read fine."""
    with pytest.raises(NoAnswerFromModel, match="ceiling"):
        response_text(_Response(_Choice('{"claims": [{', finish_reason="length")))


def test_a_provider_refusal_is_raised_and_never_returned_as_an_answer():
    """`finish_reason == "content_filter"` is the provider declining. That is not
    the same as the model answering that the evidence is insufficient -- `00` §3.6
    demands the model be able to say `unknown`, and only the model can say it."""
    with pytest.raises(NoAnswerFromModel, match="declined"):
        response_text(
            _Response(_Choice("", finish_reason="content_filter")))


def test_a_finish_reason_this_module_does_not_know_is_not_an_answer_either():
    """DeepSeek publishes `insufficient_system_resource`, and a provider may add
    another tomorrow. The closed set of ANSWERS has one member; everything else is
    a refusal, because a reason this module cannot read is a reason it cannot
    certify as complete."""
    for unknown in ("insufficient_system_resource", "tool_calls", None):
        with pytest.raises(NoAnswerFromModel):
            response_text(_Response(_Choice("{}", finish_reason=unknown)))


def test_an_empty_answer_is_a_failure_and_not_an_empty_claim_set():
    """Empty bytes parse as no claims, `llm_harness.sites._claims` returns `None`,
    and Site A records a REJECT about a judgement no model made. R1's
    `reasoning_content` is a real way to get here: a reasoning model can spend the
    whole ceiling thinking and return `content=""` with `finish_reason` unset."""
    for empty in ("", "   ", None):
        with pytest.raises(NoAnswerFromModel):
            response_text(_Response(_Choice(empty)))


def test_no_choices_at_all_is_a_failure():
    with pytest.raises(NoAnswerFromModel):
        response_text(_Response())


def test_a_second_choice_is_refused_rather_than_silently_dropped():
    """One call, one answer. `n` is never set by this module, so more than one
    choice means the request that came back is not the request that went out, and
    picking the first would be choosing between two answers on no evidence."""
    with pytest.raises(NoAnswerFromModel):
        response_text(_Response(_Choice("{}"), _Choice("{}")))


def test_a_refusal_reaching_invoke_raises_rather_than_returning_bytes():
    """The whole path, not just the helper: nothing turns a refusal into bytes."""
    invoke = _built(send=lambda **_: _Response(
        _Choice("", finish_reason="content_filter")))
    with pytest.raises(NoAnswerFromModel):
        invoke(b"x")


# --- the shape of the module itself --------------------------------------------

def _module_source() -> str:
    import readers.model_deepseek as module

    return inspect.getsource(module)


def test_the_module_opens_exactly_one_request_to_the_provider():
    """`privacy.transport_guard.assert_single_call_site` asks this of the
    transport's sink. It has to be asked one layer down too: a second
    `completions.create` here is a second thing leaving the device with no second
    release spent, no second budget call reserved and no second audit record."""
    calls = [
        node for node in ast.walk(ast.parse(_module_source()))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "create"
    ]
    assert len(calls) == 1, [node.lineno for node in calls]


def test_the_sdk_is_imported_in_exactly_one_function_and_not_at_module_level():
    """`pyproject.toml`'s `dependencies` is empty on purpose -- P5's SPEC says a
    part "adds no third-party runtime dependency" and the libraries belong to the
    deployment that chose them. Importing this module must therefore not require
    the SDK, or the pure half stops being testable on a machine that has neither
    the package nor a key."""
    tree = ast.parse(_module_source())
    module_level = {
        alias.name for node in tree.body
        if isinstance(node, ast.Import) for alias in node.names
    }
    assert "openai" not in module_level
    sites = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        and any(alias.name == "openai" for alias in node.names)
    ]
    assert len(sites) == 1, [node.lineno for node in sites]


def test_no_prompt_text_and_no_model_behaviour_is_chosen_here():
    """`84` §1: an agent may not author or adopt prompt text, and every knob that
    changes what the model does is a prompt nobody approved and no record names.
    The keywords are checked on the ONE outbound call, by AST, because the failure
    this prevents is a convenience somebody adds later."""
    create = next(
        node for node in ast.walk(ast.parse(_module_source()))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "create"
    )
    assert {keyword.arg for keyword in create.keywords} == {
        "model", "max_tokens", "messages"}
    roles = {
        node.value for node in ast.walk(create)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert "system" not in roles, roles


def test_the_module_does_not_declare_itself_the_transport():
    """It is not one. `llm_harness/transport.py` constructs the model request from
    a `Released` and is the single egress point in §8.4's sense; this is the sink
    that request is handed to. `tests/p7/test_p7_skeleton_step.py` asserts the
    src-wide scan finds exactly one module setting the flag."""
    import readers.model_deepseek as module

    assert getattr(module, "IS_MODEL_TRANSPORT", False) is False


def test_nothing_here_can_reach_the_corpus():
    """The types §8.4 puts in the always-local set, absent by import.

    `privacy.transport_guard.CORPUS_ONLY_TYPES` names them: a `Path`, an
    `Observation`, a `TextUnit`. This module cannot hold one, because at run time
    it imports nothing from `src/` at all -- the same property `model_ollama.py`
    and `model_anthropic.py` have. `ModelTarget` is annotation-only, under
    `TYPE_CHECKING`.
    """
    tree = ast.parse(_module_source())
    type_checking_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and ast.unparse(node.test) == "TYPE_CHECKING":
            for child in ast.walk(node):
                type_checking_lines.add(getattr(child, "lineno", -1))
    runtime: set[str] = set()
    for node in ast.walk(tree):
        if getattr(node, "lineno", -1) in type_checking_lines:
            continue
        if isinstance(node, ast.Import):
            runtime.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            runtime.add(node.module)
    src = {path.stem if path.is_file() else path.name
           for path in pathlib.Path("src").iterdir()}
    assert {name for name in runtime if name.split(".")[0] in src} == set()
