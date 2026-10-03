"""The cloud lane's width is one knob, and a lane that wide finishes in batches.

N cloud round trips of 0.2 s each, driven through `harness.in_walk_order` at the
width `cli.cloud_calls_at_once()` reads, take ceil(N / width) * 0.2 s -- not
N * 0.2 s -- and still come back in walk order.
"""
from __future__ import annotations

import math
import time

import pytest

import cli
from llm_harness.harness import CallLane, in_walk_order
from privacy.vocabulary import CLOUD_LOCALITY

LATENCY = 0.2


class _Send:
    locality = CLOUD_LOCALITY

    def __init__(self, n: int) -> None:
        self.n = n

    def perform(self):
        time.sleep(LATENCY)
        return f"answer {self.n}"


def _call(n: int):
    answer = yield _Send(n)
    return answer


def test_the_width_is_read_from_the_environment(monkeypatch):
    monkeypatch.delenv(cli.CLOUD_CALLS_AT_ONCE_NAME, raising=False)
    assert cli.cloud_calls_at_once() == cli.CLOUD_CALLS_AT_ONCE
    monkeypatch.setenv(cli.CLOUD_CALLS_AT_ONCE_NAME, "8")
    assert cli.cloud_calls_at_once() == 8
    for bad in ("0", "-2", "eight", "1.5"):
        monkeypatch.setenv(cli.CLOUD_CALLS_AT_ONCE_NAME, bad)
        with pytest.raises(SystemExit):
            cli.cloud_calls_at_once()


@pytest.mark.parametrize("n", [20, 8, 1])
def test_n_slow_calls_finish_in_ceil_n_over_the_width_round_trips(monkeypatch, n):
    monkeypatch.setenv(cli.CLOUD_CALLS_AT_ONCE_NAME, "8")
    lane = CallLane(width=cli.cloud_calls_at_once())
    started = time.monotonic()
    results = list(in_walk_order(((i, _call(i)) for i in range(n)), lane=lane))
    took = time.monotonic() - started
    expected = math.ceil(n / 8) * LATENCY
    assert results == [(i, f"answer {i}") for i in range(n)]
    assert lane.at_once == min(n, 8)
    assert expected <= took < expected + 0.3, (n, took, expected)
