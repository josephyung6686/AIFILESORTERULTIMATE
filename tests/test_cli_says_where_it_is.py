"""A run says where it is when asked, and goes on.

`cli.say_where_you_are_when_asked` registers `SIGUSR1` so that `kill -USR1 <pid>`
prints every thread's Python stack. The first shape chained to the handler it
replaced, and the handler it replaced was the default one, whose action for that
signal is to end the process: a nine-hour parsing run was asked where it was and died
of the question (12 Sep 2026, exit 128 + the signal's number). This sends the real
signal to a real child and reads the answer and the survival off it.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"

CHILD = """
import os, signal, sys, time
import cli
cli.say_where_you_are_when_asked()
os.kill(os.getpid(), signal.SIGUSR1)
time.sleep(0.5)
print("STILL RUNNING")
"""


@pytest.mark.skipif(not hasattr(os, "kill") or sys.platform == "win32",
                    reason="POSIX signals")
def test_the_signal_prints_the_stacks_and_the_run_survives():
    env = dict(os.environ, PYTHONPATH=str(SRC), GRAPH_AGENT_NO_DOTENV="1")
    done = subprocess.run([sys.executable, "-c", CHILD], capture_output=True,
                          text=True, env=env, timeout=120)
    assert done.returncode == 0, (done.returncode, done.stderr[-2000:])
    assert "STILL RUNNING" in done.stdout
    assert "Current thread" in done.stderr
    assert "<module>" in done.stderr
