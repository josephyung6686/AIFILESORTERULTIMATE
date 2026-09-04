"""Running the real product over the corpus, once per labelled situation.

`--situation` is one answer applied to every file in the folder -- the product
says so itself, in the block of decisions it made because nobody was at the
screen. So one run cannot score a corpus that is deliberately several situations
at once. Each situation gets a run of its own over the WHOLE corpus, and a file
is scored against the run whose situation its label names.

Each run gets a fresh database. Answers, plan versions and consent are all
remembered between runs against one database, so sharing one would let the first
situation's decisions reach the second.
"""
from __future__ import annotations

import concurrent.futures
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


#: How much of a failing run's stderr to keep. Generous on purpose: a frame in
#: this codebase prints the docstring around it, so a traceback runs to
#: thousands of characters and a tight tail keeps the frames and drops the
#: exception line -- which is the one thing the tail exists to preserve.
STDERR_TAIL = 20_000


def _tail(text: str) -> str:
    return text if len(text) <= STDERR_TAIL else "...\n" + text[-STDERR_TAIL:]


class MachineTooBusy(Exception):
    """The machine is already carrying work this run would contend with.

    Not a performance concern. A wall-clock measurement taken beside six of
    these processes is not slow, it is WRONG -- and the person who finds out is
    whoever reads the number, long after the run that spoiled it has finished.

    This exists because the harness was picked up by an agent who had never
    read its brief, started six processes against another agent's seven on
    eight cores, and cost that agent four measurement arms. That is what an
    instrument being useful looks like, and nothing in it said "check first".
    """


def refuse_if_busy(ceiling: float, *, force: bool, out) -> None:
    """Print what the machine is carrying, and stop if it is already loaded.

    `ceiling` is injected, never a literal here: this package holds mechanism
    and the composition root holds the number, which is the same rule `src/`
    follows. A ceiling this function chose for itself would be a policy decided
    in the wrong place and invisible to whoever changed their mind about it.
    """
    one_minute = os.getloadavg()[0]
    cores = os.cpu_count() or 1
    print(f"machine: load average {one_minute:.1f} over {cores} cores "
          f"(ceiling {ceiling:.1f})", file=out, flush=True)
    if one_minute <= ceiling or force:
        if force and one_minute > ceiling:
            print("  --force given: running anyway. Anything else being timed "
                  "on this machine right now is now unreliable.", file=out,
                  flush=True)
        return
    raise MachineTooBusy(
        f"load average is {one_minute:.1f} against a ceiling of {ceiling:.1f}. "
        f"Something else is using this machine, and a run started now both "
        f"takes longer and spoils whatever is being measured beside it. Wait, "
        f"or pass --force if you know what else is running and have decided "
        f"the contention is acceptable.")


@dataclass(frozen=True)
class RunResult:
    situation: str
    label: str
    database: Path
    report: Path
    exit_code: int
    seconds: float
    stderr: str


def label_for(situation: str) -> str:
    """The top-level folder name to give a situation's run.

    Taken from the situation's own last word so it reads like something a person
    would type, and so two situations never collide on one name.
    """
    tail = situation.split(".")[-1]
    return tail.replace("-", " ").title()


def run_situations(corpus: Path, situations, out_dir: Path, *,
                   load_ceiling: float, workers: int = 4, cloud: bool = False,
                   force: bool = False, on_done=None) -> list[RunResult]:
    refuse_if_busy(load_ceiling, force=force, out=sys.stdout)
    out_dir.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[2]
    results: list[RunResult] = []

    def one(situation: str) -> RunResult:
        stem = situation.replace(".", "_")
        database = out_dir / f"{stem}.sqlite"
        report = out_dir / f"{stem}.report.txt"
        for stale in (database, report):
            stale.unlink(missing_ok=True)
        started = time.monotonic()
        command = [sys.executable, "-m", "tools.groundtruth._one_run", str(corpus),
                   situation, label_for(situation), str(database), str(report)]
        if cloud:
            command.append("cloud")
        completed = subprocess.run(command, cwd=root, capture_output=True, text=True)
        return RunResult(situation, label_for(situation), database, report,
                         completed.returncode, time.monotonic() - started,
                         _tail(completed.stderr))

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(one, s): s for s in situations}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            if on_done is not None:
                on_done(result)
    return sorted(results, key=lambda r: r.situation)
