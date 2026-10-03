"""Site G's cloud judge calls are on the wire together, as site A's are.

Measured 3 Oct 2026: an 800-file organise made 863 `deepseek-v4-flash` judge
calls one at a time, about 25 minutes before the fact pass began. Site G now
drives its files through `harness.in_walk_order`, so its cloud calls share the
lane `cli.cloud_calls_at_once()` sizes. This runs `test_the_judge_names_the_
situation`'s own cloud-only corpus with a provider that takes 0.2 s per answer
and counts how many site-G calls were in flight at once.
"""
from __future__ import annotations

import threading
import time

import cli
import test_the_judge_names_the_situation as judge


class _SlowCloud(judge._Cloud):
    in_flight = 0
    widest = 0
    lock = threading.Lock()

    def factory(self, **unused):
        answer = super().factory(**unused)

        def invoke(payload: bytes) -> bytes:
            if self._body(payload)["call_site"] != cli.G_SITUATION_SENSITIVITY:
                return answer(payload)
            with _SlowCloud.lock:
                _SlowCloud.in_flight += 1
                _SlowCloud.widest = max(_SlowCloud.widest, _SlowCloud.in_flight)
            try:
                time.sleep(0.2)
                with _SlowCloud.lock:
                    return answer(payload)
            finally:
                with _SlowCloud.lock:
                    _SlowCloud.in_flight -= 1
        return invoke


def test_site_gs_cloud_calls_are_in_flight_together(tmp_path, monkeypatch):
    monkeypatch.setattr(judge, "_Cloud", _SlowCloud)
    _SlowCloud.widest = 0
    state = judge._run(tmp_path, ratify=True)
    asked = state["cloud"].dossiers_at(cli.G_SITUATION_SENSITIVITY)
    assert len(asked) > 1
    assert _SlowCloud.widest > 1, _SlowCloud.widest


def test_a_lane_of_one_is_the_serial_loop(tmp_path, monkeypatch):
    monkeypatch.setattr(judge, "_Cloud", _SlowCloud)
    monkeypatch.setenv(cli.CLOUD_CALLS_AT_ONCE_NAME, "1")
    _SlowCloud.widest = 0
    judge._run(tmp_path, ratify=True)
    assert _SlowCloud.widest == 1
