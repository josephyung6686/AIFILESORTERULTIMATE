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
"""
from __future__ import annotations

import pytest

from privacy.release import ModelTarget
from readers.model_deepseek import deepseek_invoke


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
