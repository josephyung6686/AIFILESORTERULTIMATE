"""The check that stops this harness spoiling somebody else's measurement.

It exists because the tool was picked up by an agent who had never read its
brief and started six processes against another agent's seven on eight cores.
That is what an instrument being useful looks like; nothing in it said "check
first", and four measurement arms were voided.
"""
from __future__ import annotations

# `tools/` is a sibling of `src/`, and `pyproject.toml` puts only `src` on the
# path. Done HERE rather than in a `conftest.py`: with no `__init__.py` in the
# tests tree every conftest is imported under the bare name `conftest`, and the
# last one collected wins -- which once took that name from `tests/p5/conftest.py`.
import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.groundtruth.run import MachineTooBusy, refuse_if_busy  # noqa: E402


def _at(monkeypatch, load: float) -> None:
    monkeypatch.setattr("tools.groundtruth.run.os.getloadavg",
                        lambda: (load, load, load))


def test_a_quiet_machine_is_allowed(monkeypatch):
    _at(monkeypatch, 1.5)
    out = io.StringIO()
    refuse_if_busy(8.0, force=False, out=out)     # does not raise
    assert "load average 1.5" in out.getvalue()


def test_a_busy_machine_is_refused_and_the_message_says_what_to_do(monkeypatch):
    _at(monkeypatch, 47.0)
    with pytest.raises(MachineTooBusy) as raised:
        refuse_if_busy(8.0, force=False, out=io.StringIO())
    message = str(raised.value)
    assert "47.0" in message and "8.0" in message
    # A refusal that does not say how to proceed is an obstacle, not a guard.
    assert "--force" in message


def test_force_runs_anyway_and_says_what_it_just_cost(monkeypatch):
    _at(monkeypatch, 47.0)
    out = io.StringIO()
    refuse_if_busy(8.0, force=True, out=out)      # does not raise
    assert "running anyway" in out.getvalue()
    assert "unreliable" in out.getvalue()


def test_the_load_is_printed_even_when_the_machine_is_fine(monkeypatch):
    # The number goes on screen every run, not only when it refuses: a run
    # whose timing looks odd afterwards should carry the reason in its own log.
    _at(monkeypatch, 0.2)
    out = io.StringIO()
    refuse_if_busy(8.0, force=False, out=out)
    assert "machine: load average 0.2" in out.getvalue()
    assert "cores" in out.getvalue()


def test_the_ceiling_is_injected_and_not_chosen_here(monkeypatch):
    # The number is the composition root's, the same rule `src/` follows. A
    # ceiling this function picked for itself would be a policy decided in the
    # wrong place, and invisible to whoever wanted to change it.
    import inspect

    from tools.groundtruth.run import refuse_if_busy as checked

    ceiling = inspect.signature(checked).parameters["ceiling"]
    assert ceiling.default is inspect.Parameter.empty

    _at(monkeypatch, 5.0)
    refuse_if_busy(6.0, force=False, out=io.StringIO())          # under: allowed
    with pytest.raises(MachineTooBusy):
        refuse_if_busy(4.0, force=False, out=io.StringIO())      # over: refused


def test_run_situations_will_not_start_without_a_ceiling():
    # Absent means refuse, never guess: a caller that forgot the ceiling must
    # fail loudly rather than inherit a default nobody chose.
    import inspect

    from tools.groundtruth.run import run_situations

    assert (inspect.signature(run_situations).parameters["load_ceiling"].default
            is inspect.Parameter.empty)
