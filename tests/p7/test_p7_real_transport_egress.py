"""Done-means 3's instrument, run over the transport P8 actually shipped.

P7's Done-means 3 is a static property *of the transport*: "the model/connector
transport has exactly one entry point and its only content parameter is a
`Released`." P7 could prove only the instrument -- there was no transport to point
it at, and `test_p7_transport.py`'s last test says so by name.

P8 shipped `llm_harness/transport.py`. The property is now checkable, and nothing
was checking it: `tests/p7/test_p7_skeleton_step.py` finds the transport by scanning
`src/` for `IS_MODEL_TRANSPORT is True`, `transport.py` never set the flag, so the
scan returned `[]` and the `for module in transports: assert_single_egress(module)`
loop below it iterated an empty list. The guard asserted against nothing.

This file is the check, and the fixtures below are the *scope* of the check proven
in both directions -- a sink the transport calls is not content the caller supplies,
and a container of content still is.
"""
from collections.abc import Callable, Sequence
from pathlib import Path
from types import ModuleType

import pytest

import llm_harness.transport as transport
from privacy.release import Released
from privacy.transport_guard import (
    MultipleEgressPoints,
    UnreleasedContentParameter,
    assert_single_egress,
    egress_functions,
)

from p7.transport_fixtures import _module


# --- the property, over the module that has it ----------------------------------

def test_the_real_transport_is_found_by_the_flag_scan():
    """Without this the skeleton step's egress loop iterates an empty list."""
    assert transport.IS_MODEL_TRANSPORT is True


def test_the_guard_reaches_a_verdict_on_the_real_transport():
    assert assert_single_egress(transport) is None


def test_the_real_transport_has_exactly_one_entry_point_and_it_is_issue():
    assert [fn.__name__ for fn in egress_functions(transport)] == ["issue"]


def test_the_entry_point_takes_a_released():
    import inspect
    annotations = {
        name: parameter.annotation
        for name, parameter in inspect.signature(
            transport.issue, eval_str=True).parameters.items()
    }
    assert annotations["released"] is Released


# --- the scope, proven in both directions ---------------------------------------

def test_a_callable_sink_is_not_a_content_parameter():
    """The question `ModelClient.invoke` forced, and the answer §8.4 gives.

    A parameter annotated `Callable[[bytes], bytes]` accepts a FUNCTION. The caller
    hands over no bytes at all; the bytes that later cross it are the ones the
    transport itself computed downstream of `Gate.release`. §8.4 orders privacy
    "before content reaches any model" -- the sink is where released content is
    SUPPOSED to go, so reading the sink's own argument type as if the caller had
    supplied it inverts the direction the rule is about.
    """
    def send(released: Released, sink: Callable[[bytes], bytes]) -> None:
        sink(b"")

    assert assert_single_egress(_module("transport_with_a_sink", send)) is None


def test_a_container_of_content_is_still_a_content_parameter():
    """The other direction, so the callable rule is a distinction and not a hole."""
    def send(released: Released, extra: Sequence[bytes]) -> None:
        pass

    with pytest.raises(UnreleasedContentParameter, match="extra"):
        assert_single_egress(_module("transport_taking_a_sequence_of_bytes", send))


def test_a_callable_taking_a_path_is_still_only_a_callable():
    """Not special-cased to `bytes`: the rule is about who supplies the value."""
    def send(released: Released, sink: Callable[[Path], None]) -> None:
        pass

    assert assert_single_egress(_module("transport_with_a_path_sink", send)) is None


def test_a_record_the_entry_point_only_returns_is_not_an_egress_surface():
    """`ModelResponse` in miniature: a caller can construct one and hand it nowhere.

    The entry point does not accept it, so it is not a way to put content into a
    model call -- which is the only thing §8.4 sequences.
    """
    import dataclasses

    @dataclasses.dataclass(frozen=True)
    class Response:
        response_bytes: bytes
        model_id: str

    def send(released: Released) -> Response:
        return Response(b"", "m")

    assert assert_single_egress(_module("transport_returning_a_record",
                                        Response, send)) is None


def test_a_record_the_entry_point_accepts_is_an_egress_surface():
    """The same shape on the inbound side still fails. One word of difference."""
    import dataclasses

    @dataclasses.dataclass(frozen=True)
    class Envelope:
        text: str

    def send(released: Released, envelope: Envelope) -> None:
        pass

    with pytest.raises(UnreleasedContentParameter, match="Envelope.__init__"):
        assert_single_egress(_module("transport_accepting_a_record",
                                     Envelope, send))


# --- sabotage: a second egress must not pass ------------------------------------

def _sabotaged(source_edit) -> ModuleType:
    """A scratch copy of the real transport, edited, imported, and handed to the guard."""
    import importlib.util
    import pathlib
    import sys
    import tempfile

    source = pathlib.Path(transport.__file__).read_text()
    edited = source_edit(source)
    assert edited != source, "the sabotage did not change the source"
    scratch = pathlib.Path(tempfile.mkdtemp()) / "sabotaged_transport.py"
    scratch.write_text(edited)
    spec = importlib.util.spec_from_file_location("sabotaged_transport", scratch)
    module = importlib.util.module_from_spec(spec)
    # Registered before exec: the module's dataclasses resolve their own
    # `__module__` through `sys.modules` while their constructors are generated.
    sys.modules["sabotaged_transport"] = module
    try:
        spec.loader.exec_module(module)
    finally:
        del sys.modules["sabotaged_transport"]
    return module


def test_a_second_public_egress_function_is_caught():
    """P10 adds a model call site. If it lands as a second door, this is what fails."""
    def add_a_second_door(source: str) -> str:
        return source + (
            "\n\n"
            "def issue_batch(conn: sqlite3.Connection, released: Released,\n"
            "                payload: CallPayload, *,\n"
            "                model_client: ModelClient) -> ModelResponse | CallFailed:\n"
            "    return issue(conn, released, payload, model_client=model_client)\n"
        )

    with pytest.raises(MultipleEgressPoints, match="issue_batch"):
        assert_single_egress(_sabotaged(add_a_second_door))


def test_a_second_egress_that_takes_a_string_is_caught_as_content_too():
    def add_a_string_door(source: str) -> str:
        return source + (
            "\n\n"
            "def issue_prompt(prompt: str) -> bytes:\n"
            "    return prompt.encode()\n"
        )

    with pytest.raises((MultipleEgressPoints, UnreleasedContentParameter)):
        assert_single_egress(_sabotaged(add_a_string_door))


# --- the hole a signature guard cannot see --------------------------------------

def test_the_real_transport_invokes_its_sink_exactly_once():
    """`assert_single_egress` is SILENT on a second call to the same sink.

    It is an existence proof over a namespace: it reads signatures and never a
    function body, so a second `model_client.invoke(...)` INSIDE `issue` -- one
    handing over `canonical_dossier_bytes` before the released `model_visible_bytes`
    -- changes no signature and is not seen. P8's Done-means 1 is about a call, not
    only a door: "Exactly one function in the codebase constructs a model request."
    """
    from privacy.transport_guard import assert_single_call_site
    assert assert_single_call_site(transport) is None


def test_a_second_call_to_the_sink_is_caught():
    from privacy.transport_guard import MultipleEgressPoints, assert_single_call_site

    def add_a_second_call(source: str) -> str:
        return source.replace(
            "        raw = model_client.invoke(payload.model_visible_bytes)",
            "        model_client.invoke(payload.canonical_dossier_bytes)\n"
            "        raw = model_client.invoke(payload.model_visible_bytes)")

    with pytest.raises(MultipleEgressPoints, match="invoke"):
        assert_single_call_site(_sabotaged(add_a_second_call))


def test_the_sink_is_found_by_its_annotation_and_not_by_its_name():
    """`invoke` is not hardcoded. Rename the field and the guard follows it."""
    from privacy.transport_guard import MultipleEgressPoints, assert_single_call_site

    def rename_and_double(source: str) -> str:
        renamed = source.replace("invoke: Callable[[bytes], bytes]",
                                 "dispatch: Callable[[bytes], bytes]")
        renamed = renamed.replace("model_client.invoke(", "model_client.dispatch(")
        return renamed.replace(
            "        raw = model_client.dispatch(payload.model_visible_bytes)",
            "        model_client.dispatch(payload.canonical_dossier_bytes)\n"
            "        raw = model_client.dispatch(payload.model_visible_bytes)")

    with pytest.raises(MultipleEgressPoints, match="dispatch"):
        assert_single_call_site(_sabotaged(rename_and_double))
