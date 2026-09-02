# tests/readers/test_model_anthropic.py
"""`ModelClient.invoke` backed by Anthropic's cloud API.

This is the first thing in the product that can put a byte on the internet.
Everything above it -- `harness.run_call`, `transport.issue`, `Gate.release` --
has been proven for months against a recorded-bytes stand-in, and a stand-in
cannot be wrong about the one thing this module can be wrong about.

**The socket is injected.** `_send` is two statements: import the SDK, call
`messages.create`. Everything else the module does -- the credential refusal, the
target check, the decode, the response handling -- is pure and every line of it is
here. So what is untested-by-default is exactly those two statements, and they are
the two that cannot be exercised without a key and a bill.

The same reasoning `test_model_ollama.py` gives for not starting ollama: a test
that needed a live provider would be skipped on the machine that most needs to run
it.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from privacy.release import LOCALITIES, ModelTarget
from readers.model_anthropic import (
    CLOUD,
    CREDENTIAL_NAME,
    PROVIDER,
    ModelCredentialMissing,
    ModelVisibleBytesNotText,
    NoAnswerFromModel,
    TargetIsNotThisTransport,
    anthropic_invoke,
    response_text,
)

TARGET = ModelTarget(locality="cloud", model_id="a-model", provider=PROVIDER)
LOCAL_TARGET = ModelTarget(locality="local", model_id="a-model", provider=PROVIDER)
OTHER_PROVIDER = ModelTarget(
    locality="cloud", model_id="a-model", provider="somebody-else")

#: One token of headroom. A literal ceiling inside the module under test would be
#: a number this part authored; here it is a test's own input, which is what it is.
ONE_TOKEN = 1


class _Block:
    def __init__(self, type_: str, text: str = "") -> None:
        self.type = type_
        self.text = text


class _Response:
    def __init__(self, content, stop_reason="end_turn", stop_details=None) -> None:
        self.content = content
        self.stop_reason = stop_reason
        self.stop_details = stop_details


def _answering(text: str, captured: dict | None = None):
    def send(*, api_key, model_id, max_tokens, prompt):
        if captured is not None:
            captured.update(api_key=api_key, model_id=model_id,
                            max_tokens=max_tokens, prompt=prompt)
            captured.setdefault("calls", []).append(prompt)
        return _Response([_Block("text", text)])
    return send


# --- absent means refuse, and refuse is not "carry on without a model" ----------

def test_no_api_key_refuses_and_names_what_was_missing():
    with pytest.raises(ModelCredentialMissing) as raised:
        anthropic_invoke(api_key=None, model_target=TARGET,
                         max_response_tokens=ONE_TOKEN, send=_answering("{}"))
    message = str(raised.value)
    assert CREDENTIAL_NAME in message
    assert PROVIDER in message


def test_a_blank_api_key_is_absent_too():
    """Whitespace is not a key. Passed through, it fails at the provider one call
    later as an authentication error -- which reads to every layer above as "the
    model was asked and could not answer" rather than "nobody was asked"."""
    for blank in ("", "   ", "\n", "\t"):
        with pytest.raises(ModelCredentialMissing):
            anthropic_invoke(api_key=blank, model_target=TARGET,
                             max_response_tokens=ONE_TOKEN, send=_answering("{}"))


def test_the_refusal_happens_before_a_run_can_start():
    """`anthropic_invoke` raises rather than returning an `invoke` that fails on
    first use. A deployment with no key stops before the scan, not after it -- and
    it can never return an `invoke` that answers with nothing, which every layer
    above would record as a schema-invalid model answer that no model gave."""
    with pytest.raises(ModelCredentialMissing):
        anthropic_invoke(api_key=None, model_target=TARGET,
                         max_response_tokens=ONE_TOKEN)


def test_a_ceiling_below_one_is_not_a_ceiling():
    for bad in (0, -1, None, "many"):
        with pytest.raises(ValueError, match="max_response_tokens"):
            anthropic_invoke(api_key="k", model_target=TARGET,
                             max_response_tokens=bad, send=_answering("{}"))


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
        anthropic_invoke(api_key="k", model_target=LOCAL_TARGET,
                         max_response_tokens=ONE_TOKEN, send=_answering("{}"))


def test_another_providers_target_is_refused():
    """§8.4 audits "which model received the data". A target naming a provider
    this module does not call makes that record false where it is written."""
    with pytest.raises(TargetIsNotThisTransport, match="somebody-else"):
        anthropic_invoke(api_key="k", model_target=OTHER_PROVIDER,
                         max_response_tokens=ONE_TOKEN, send=_answering("{}"))


def test_the_cloud_constant_is_p7s_own_value():
    """Spelled here so the module imports nothing from `src/` at run time, and
    checked here so the spelling cannot drift from P7's closed pair."""
    assert CLOUD == LOCALITIES[1]


# --- bytes in, bytes out, and nothing invented in between ----------------------

def test_the_released_bytes_are_sent_verbatim():
    captured: dict = {}
    invoke = anthropic_invoke(
        api_key="secret", model_target=TARGET, max_response_tokens=ONE_TOKEN,
        send=_answering('{"claims": []}', captured))
    invoke(b'{"dossier": "released"}')
    assert captured["prompt"] == '{"dossier": "released"}'
    assert captured["model_id"] == "a-model"
    assert captured["max_tokens"] == ONE_TOKEN
    assert captured["api_key"] == "secret"


def test_the_answer_comes_back_as_bytes():
    invoke = anthropic_invoke(api_key="k", model_target=TARGET,
                              max_response_tokens=ONE_TOKEN,
                              send=_answering('{"claims": []}'))
    assert invoke(b"x") == b'{"claims": []}'


def test_bytes_that_are_not_text_are_refused_and_never_repaired():
    """`transport.issue` catches whatever `invoke` raises and records a
    `client_raised` failure. A lossy decode would instead send the model something
    the stored prompt fingerprint no longer describes."""
    invoke = anthropic_invoke(api_key="k", model_target=TARGET,
                              max_response_tokens=ONE_TOKEN,
                              send=_answering("{}"))
    with pytest.raises(ModelVisibleBytesNotText):
        invoke(b"\xff\xfe not utf-8")


def test_one_invoke_is_exactly_one_request():
    """`harness.run_call` reserves one budget call and `transport.issue` consumes
    one release per `invoke`. A retry loop here over an ANSWER would make one
    reservation pay for several requests, and §8.6's ceiling -- the only thing
    between a wired model and unbounded spend -- would be counting the wrong
    thing. (The SDK retries 429s and 5xx below this line; those are neither billed
    nor answers.)"""
    captured: dict = {}
    invoke = anthropic_invoke(api_key="k", model_target=TARGET,
                              max_response_tokens=ONE_TOKEN,
                              send=_answering("{}", captured))
    invoke(b"x")
    assert captured["calls"] == ["x"]


# --- what comes back, judged without calling anything --------------------------

def test_only_text_blocks_are_returned():
    assert response_text(
        _Response([_Block("thinking"), _Block("text", '{"claims": []}')])
    ) == '{"claims": []}'


def test_a_provider_refusal_is_raised_and_never_returned_as_an_answer():
    """`stop_reason == "refusal"` arrives over HTTP 200. Returned as bytes it
    would be validated as if it were the model's reading of the evidence."""
    with pytest.raises(NoAnswerFromModel, match="declined"):
        response_text(_Response([], stop_reason="refusal"))


def test_a_truncated_answer_is_raised_and_never_returned():
    """A response cut off at our ceiling is half a JSON document. Parsed it is
    schema-invalid, and the rejection would be recorded against the model."""
    with pytest.raises(NoAnswerFromModel, match="ceiling"):
        response_text(_Response([_Block("text", '{"claims": [{')],
                                stop_reason="max_tokens"))


def test_an_empty_response_is_a_failure_and_not_an_empty_claim_set():
    with pytest.raises(NoAnswerFromModel):
        response_text(_Response([]))
    with pytest.raises(NoAnswerFromModel):
        response_text(_Response([_Block("text", "")]))


def test_a_refusal_reaching_invoke_raises_rather_than_returning_bytes():
    """The whole path, not just the helper: nothing turns a refusal into bytes."""
    invoke = anthropic_invoke(
        api_key="k", model_target=TARGET, max_response_tokens=ONE_TOKEN,
        send=lambda **_: _Response([], stop_reason="refusal"))
    with pytest.raises(NoAnswerFromModel):
        invoke(b"x")


# --- the shape of the module itself --------------------------------------------

def _module_source() -> str:
    import readers.model_anthropic as module

    return inspect.getsource(module)


def test_the_module_opens_exactly_one_request_to_the_provider():
    """`privacy.transport_guard.assert_single_call_site` asks this of the
    transport's sink. It has to be asked one layer down too, now that the sink
    really does talk to a network: a second `messages.create` here is a second
    thing leaving the device with no second release spent, no second budget call
    reserved and no second audit record written."""
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
    assert "anthropic" not in module_level
    sites = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        and any(alias.name == "anthropic" for alias in node.names)
    ]
    assert len(sites) == 1, [node.lineno for node in sites]


def test_the_module_does_not_declare_itself_the_transport():
    """It is not one. `llm_harness/transport.py` constructs the model request from
    a `Released` and is the single egress point in §8.4's sense; this is the sink
    that request is handed to. `tests/p7/test_p7_skeleton_step.py` asserts the
    src-wide scan finds exactly one module setting the flag."""
    import readers.model_anthropic as module

    assert getattr(module, "IS_MODEL_TRANSPORT", False) is False


def test_nothing_here_can_reach_the_corpus():
    """The types §8.4 puts in the always-local set, absent by import.

    `privacy.transport_guard.CORPUS_ONLY_TYPES` names them: a `Path`, an
    `Observation`, a `TextUnit`. This module cannot hold one, because at run time
    it imports nothing from `src/` at all -- the same property `model_ollama.py`
    has. `ModelTarget` is annotation-only, under `TYPE_CHECKING`.
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
