# tests/readers/test_model_deepseek_timeout.py
"""A model call that cannot time out can stop the whole product for ever.

`_send` built `openai.OpenAI(api_key=..., base_url=...)` and passed no timeout and
no retry ceiling. The library's own defaults are ten minutes PER ATTEMPT with
retries on top, so one unanswered request holds a scan open long past any point a
person would still be watching.

Found by running the suite: `tests/integration/test_cli_corpus_selection.py::
test_a_second_source_does_not_send_under_the_first_ones_consent` passes
`--enable-cloud`, the A_fact site is now wired to a real client, and the whole test
run stopped dead. Ten minutes, twice, with no output. The test was right and the
transport was wrong.

It matters far more in production than in the suite. §8.6 bounds model SPEND per
scan and says nothing about a call that never returns, so a hung socket is not a
budget event, not a `budget_deferred`, and not a refusal -- it is a run that never
finishes over a person's ten thousand files.

The NUMBER is not chosen here. `cli.py` is the only file that picks one; this
module refuses to invent a default, the same way it already refuses a missing key,
a missing endpoint and a mislabelled target -- and for the same reason: a default
timeout would be this module authoring a deployment's patience.

**WHAT THE NUMBER MEANS CHANGED WITH `104` R-176, and the second half of this file
is about that.** It used to reach the SDK as four per-operation timers, each of
which bounds one connect, one write or one read and restarts on the next; it is now
ONE budget over the whole call, named by phase. The socket half of that is measured
against a real server in `test_model_deepseek_deadline.py`. What is pinned here is
the half that needs no socket: that every phase has a class, and that a deadline
reaching `deepseek_invoke` -- plainly, or wrapped by the SDK in its own connection
error -- comes back out as the phase's own `ModelRanOutOfTime` rather than as
whatever a library chose to raise.
"""
from __future__ import annotations

import pytest

from privacy.release import ModelTarget
from readers.model_deepseek import (
    CALL_PHASES, CONNECTING, RAN_OUT_OF_TIME_IN, READING_THE_BODY,
    SENDING_THE_REQUEST, TIMER_PHASE, WAITING_FOR_THE_FIRST_BYTE,
    ModelRanOutOfTime, ModelRanOutOfTimeWaitingForTheFirstByte, deepseek_invoke,
)


def _target():
    return ModelTarget(locality="cloud", model_id="deepseek-v4-pro",
                       provider="deepseek")


def test_the_timeout_reaches_the_transport():
    """The whole point: the number arrives where the socket is opened."""
    seen = {}

    def send(**kwargs):
        seen.update(kwargs)
        message = type("M", (), {"content": "ok"})()
        choice = type("C", (), {"message": message, "finish_reason": "stop"})()
        return type("R", (), {"choices": [choice]})()

    deepseek_invoke(api_key="k", base_url="https://example.invalid",
                    model_target=_target(), max_response_tokens=64,
                    timeout_seconds=30, send=send)(b"hello")
    assert seen["timeout_seconds"] == 30


def test_a_client_with_no_timeout_is_refused_when_it_is_built():
    """Refused at BUILD time, like the key and the endpoint already are.

    A deployment that forgot the number learns before the scan, not after ten
    thousand files have been read and one socket has gone quiet.
    """
    with pytest.raises(ValueError):
        deepseek_invoke(api_key="k", base_url="https://example.invalid",
                        model_target=_target(), max_response_tokens=64,
                        timeout_seconds=None, send=lambda **k: None)


@pytest.mark.parametrize("bad", [0, -1, -30])
def test_a_timeout_that_is_not_a_positive_number_of_seconds_is_refused(bad):
    """Zero is not patience, it is a different bug wearing a number."""
    with pytest.raises(ValueError):
        deepseek_invoke(api_key="k", base_url="https://example.invalid",
                        model_target=_target(), max_response_tokens=64,
                        timeout_seconds=bad, send=lambda **k: None)


# --- `104` R-176: one deadline, four phases, and a class for each --------------

class _Expiry(TimeoutError):
    """A deadline that knows which phase it expired in, as a transport raises it.

    Built here rather than imported: what `deepseek_invoke` promises is that it
    reads a `phase` off a `TimeoutError`, and any transport somebody wires -- the
    module's own, or a deployment's replacement -- keeps working by carrying one.
    A test that reached for the private class would be pinning the implementation
    instead of the contract.
    """

    def __init__(self, phase: str) -> None:
        super().__init__(f"expired while {phase}")
        self.phase = phase


def _invoke(send):
    return deepseek_invoke(api_key="k", base_url="https://example.invalid",
                           model_target=_target(), max_response_tokens=64,
                           timeout_seconds=30, send=send)


def test_every_phase_of_a_call_has_a_class_because_the_class_is_what_is_kept():
    """The deadline covers all four phases, and each is a NAME in the record.

    `llm_harness.transport._client_exception_explanation` reduces a client
    exception to `type(exc).__qualname__` and a status code and drops the message
    (§8.4 property 4: there is no way to enumerate every string an SDK may put in
    one). So a phase that lived only in a sentence would be a phase the
    `llm_call_failure` row cannot say -- which is exactly the unattributable
    failure `104` R-176 exists to end, and §18.28's outage produced no row at all.

    SABOTAGE: add a fifth phase and no class for it, or point a timer at a phase
    that does not exist. `model_deepseek` fails to IMPORT, rather than recording a
    timeout that names nothing.
    """
    assert CALL_PHASES == (CONNECTING, SENDING_THE_REQUEST,
                           WAITING_FOR_THE_FIRST_BYTE, READING_THE_BODY)
    assert tuple(RAN_OUT_OF_TIME_IN) == CALL_PHASES
    assert set(TIMER_PHASE.values()) <= set(CALL_PHASES)
    for phase, kind in RAN_OUT_OF_TIME_IN.items():
        assert issubclass(kind, ModelRanOutOfTime), phase
        # The name alone has to be readable as the phase, because the name alone
        # is what the durable record keeps.
        assert kind.__qualname__ != ModelRanOutOfTime.__qualname__
        assert kind.__qualname__.startswith(ModelRanOutOfTime.__qualname__)


def test_a_deadline_reaching_invoke_is_recorded_as_the_phase_it_died_in():
    """The branch that did not exist before `104` R-176.

    `ollama_invoke` turned a `TimeoutError` into its own refusal and this one did
    not, so a cloud call that ran out of time arrived upstream as whatever the
    library happened to raise -- a shape §8.4's audit column cannot read as a
    timeout at all.
    """
    def send(**_):
        raise _Expiry(WAITING_FOR_THE_FIRST_BYTE)

    with pytest.raises(ModelRanOutOfTimeWaitingForTheFirstByte) as raised:
        _invoke(send)(b"x")
    assert WAITING_FOR_THE_FIRST_BYTE in str(raised.value)


def test_the_same_deadline_arriving_wrapped_by_the_sdk_still_names_its_phase():
    """The shape it ACTUALLY arrives in.

    The SDK catches anything its transport raises and re-raises its own connection
    error `from` the original, so the deadline reaches `invoke` one wrapper down.
    What a timeout MEANS does not change with the wrapper it arrived in, and a run
    whose failure rows said "connection error" would have lost the phase that
    R-176 exists to record.
    """
    def send(**_):
        try:
            raise _Expiry(READING_THE_BODY)
        except TimeoutError as expiry:
            raise RuntimeError("connection error") from expiry

    with pytest.raises(ModelRanOutOfTime) as raised:
        _invoke(send)(b"x")
    assert type(raised.value) is RAN_OUT_OF_TIME_IN[READING_THE_BODY]


def test_a_timeout_that_cannot_say_its_phase_says_so_rather_than_guessing():
    """An injected `send` raises the PLAIN `TimeoutError`, and that is honest.

    The base class and "waiting on the call" is the whole of what is known about
    one of those. Guessing the likeliest phase would put a fact in the record that
    nothing measured, which is the same failure as no record at all wearing better
    clothes.
    """
    def send(**_):
        raise TimeoutError("no phase here")

    with pytest.raises(ModelRanOutOfTime) as raised:
        _invoke(send)(b"x")
    assert type(raised.value) is ModelRanOutOfTime


def test_a_failure_that_is_not_a_deadline_is_re_raised_exactly_as_it_was():
    """The new branch adds a READING, not a handler.

    Everything that is not a timeout still leaves `invoke` untouched for
    `transport.issue` to record as `client_raised`. A branch that swallowed an
    authentication failure into a timeout would tell a person to wait for a call
    that is never going to be allowed.
    """
    def send(**_):
        raise RuntimeError("the provider refused the key")

    with pytest.raises(RuntimeError) as raised:
        _invoke(send)(b"x")
    assert type(raised.value) is RuntimeError
    assert not isinstance(raised.value, ModelRanOutOfTime)
