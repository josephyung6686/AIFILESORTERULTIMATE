# tests/integration/test_the_product_survives_a_real_run.py
"""The product reaches the end of its own PROCESS, and leaves the machine as it was.

**What happened, and what the suite said about it.** On 2026-09-04 the product was
run over the owner's real 199-file corpus and died natively: `exit 133` on one
attempt, `-11` -- SIGSEGV -- on another, at interpreter shutdown, on leaked
multiprocessing semaphores:

    resource_tracker.py:254: UserWarning: resource_tracker: There appear to be 5
        leaked semaphore objects to clean up at shutdown

The crash truncated the output database: a measurement that should have read 176 of
199 files extracted read 19. Earlier the same night the same subsystem left FORTY-SEVEN
orphaned `multiprocessing.spawn` workers on the machine, and a run hung for forty
minutes with no error message. Through all of it the suite was GREEN at 7,985 passing.

**Why nearly eight thousand tests saw none of it.** Every one of them either drives a
part directly or calls `cli.main` IN THIS INTERPRETER. An in-process call cannot
observe an exit code, because it never receives one; and it cannot observe a crash at
interpreter shutdown, because the interpreter it would report in is the one that
crashed. The three failures all live AFTER the last statement any of those tests can
reach. That is not a gap in coverage, it is a gap in the shape of the coverage -- so
the only guard that closes it is one that runs the real command line in a process of
its own and then asks the operating system what became of it.

**Five questions, one run.** The three real failures, the one that stops the other
three being decorative, and the one the exit code cannot see:

    1. the process exited 0, and was not killed by a signal;
    2. its stderr carries no leaked-semaphore warning;
    3. no process of its own outlived it;
    4. it actually read the corpus -- because a run that exits 0 having read nothing
       passes 1, 2 and 3 perfectly, and 19 of 199 is exactly what the crash looked
       like from the outside;
    5. no process of its own CRASHED, even one it recovered from -- because
       `ProcessPool._rebuild` is built to survive exactly that, so a worker segfault
       it retried successfully leaves an exit code of 0, a complete database, and no
       trace anywhere but the operating system's own crash report.

**NO PIPES. `capture_output=True` reproduces the forty-minute hang INSIDE the test.**
`test_extraction_pool_lifecycle.py` records the mechanism: an orphaned worker still
holds the file descriptors it inherited, and descriptors 1 and 2 are the run's stdout
and stderr. When those are pipes the reader waits for an end-of-file that the dead
run's surviving children are still holding open -- observed at forty minutes, released
instantly when the orphans were killed by hand. `subprocess.run(timeout=...)` kills
the direct child and then calls `communicate()`, which blocks on exactly those pipes.
So both streams go to FILES in `tmp_path`. The resource_tracker's warning is written
to the inherited descriptor 2 and lands in the file like anything else.

**THE PROCESS GROUP, and not a count of `multiprocessing` processes on the machine.**
This repository is worked by many agents at once and several of their suites start
pools of their own, so a before-and-after count cannot tell this run's orphans from
somebody else's and would fail on innocent days -- and a guard that is flaky is a
guard the next person deletes. `start_new_session=True` makes the run its own process
group leader; spawned workers and the resource tracker inherit that group, and being
re-parented to PID 1 does NOT change it. So `pgrep -g <the run's pid>` after the run
has been reaped names exactly the processes this run left behind and nothing else.
The same reading taken WHILE it runs is what proves the pool was really used: measured
here, the group peaks at nine -- the run, seven workers and the resource tracker.

**The fixture is sized at `CORPUS_FILES`, and the number has a history.** It used to
be `cli.EXTRACTION_POOL_FLOOR` plus a margin, because `ProcessPool` performed the
first `floor` submissions on the calling thread and started no interpreter at all --
so a corpus of a couple of dozen files exercised none of the worker lifecycle these
failures live in, exited 0 every time and proved nothing. R-138 removed that floor:
a reader on the calling thread cannot be given a deadline, so every run now starts
workers whatever the corpus size. The number is KEPT at the size the crash was
reproduced at, because what this file needs is the pool running beside a pdfium read
for long enough for the cyclic collector to trip, and that is a property of how much
reading happens rather than of how the first submissions are dispatched. Nothing is
cached in a fresh directory with a fresh database, so every file is one submission.

**The formats are the ones with a native library under them**, because that is where a
segfault comes from: PDFs through pdfium, images through Apple's Vision, a spreadsheet
and an archive and plain text through the rest. It is not a large corpus -- the owner's
real one takes about four minutes and would be skipped and rot. This one takes about
three seconds.

**It does NOT read `.groundtruth/`.** Those are the owner's real files, they are
gitignored, and a test that quietly passes because a directory is absent is worse than
no test at all. Every byte of this corpus is written by this file.

**And no particular file was ever the trigger, which is why a written corpus can
stand in for the owner's.** The crash was found and its cause is in
`readers/pdf_pdfium.py`: pypdfium2's page objects are reference CYCLES, so a refcount
never frees one and the CYCLIC collector does -- running `FPDF_ClosePage` on whichever
thread happened to trip the collector's threshold. Once `ProcessPool` starts there are
two more such threads (`_ExecutorManagerThread` and the call queue's `_feed`), pdfium
is not thread-safe and its refcounts are not atomic, so a page got closed on the
feeder thread while the calling thread was inside `FPDF_LoadPage` on another page of
the same document. THE POOL IS THE TRIGGER AND THE CORPUS IS NOT. Verified from the
other side: all 91 PDFs in the owner's real corpus read clean through the same reader
in ONE single-threaded process -- no pool, no second thread, no crash. So what a
fixture has to reproduce is the pool running beside PDFs, which is exactly what
`CORPUS_FILES` files and four PDFs are for.

**And it does not skip.** The deployment is macOS with the `readers` extras; if they
are missing, `cli.py` fails to import, the run exits non-zero and the first question
fails loudly. That is the intended behaviour. A guard that turns itself off when the
thing it guards is missing is the failure mode this file exists to answer.
"""
from __future__ import annotations

import json
import os
import signal
import sqlite3
import struct
import subprocess
import sys
import threading
import time
import zipfile
import zlib
from dataclasses import dataclass
from pathlib import Path

import pytest

from extractors.filesystem import EXTRACTOR_NAME as FILESYSTEM_ONLY

_HERE = Path(__file__).resolve()
#: The real command line, run the way a person runs it. `src/cli.py` guards its own
#: `__main__` with `raise SystemExit(main())`, so this is the composition root and the
#: argument parser and the exit code, not a re-implementation of any of them.
_CLI = _HERE.parents[2] / "src" / "cli.py"

#: The literal `multiprocessing/resource_tracker.py` prints when it finds semaphores
#: nobody unlinked. Matched as a substring because the COUNT is in the middle of the
#: sentence and any count above zero is the failure.
LEAKED_SEMAPHORES = "resource_tracker: There appear to be"

SITUATION = "academic.coursework"
LABEL = "Coursework"

#: HOW MANY FILES THIS CORPUS HOLDS. Forty-two, which is the thirty-two of the pool
#: floor R-138 removed plus the ten-file margin that floor was given, and it is kept
#: rather than recomputed for the reason the module docstring gives: this is the size
#: the pdfium crash was reproduced at, and shrinking it to the smallest corpus that
#: now starts a worker -- which is one file -- would leave the pool running beside a
#: single read, where the cyclic collector never trips.
CORPUS_FILES = 42

#: HOW MANY FILES MUST HAVE HAD THEIR CONTENT READ for the run not to have been
#: truncated. It was `EXTRACTION_POOL_FLOOR`, borrowed because "the pool started" and
#: "the run was not truncated" happened to be the same number under the floor. They
#: are two different questions -- the first is `SMALLEST_GROUP_THAT_USED_THE_POOL`,
#: counted in operating-system processes -- so the number is kept at the value it had
#: and named for the job it actually does. Below `CORPUS_FILES` by the same margin
#: the floor was given, so a handful of formats a machine lacks a library for do not
#: turn a healthy run red.
NOT_TRUNCATED = 32

#: Long enough that a loaded machine is not called a hang, short enough that the
#: forty-minute stall this file exists to catch is reported the same day. Measured
#: run time on an idle machine: 2.8 to 3.7 seconds.
RUN_CEILING_SECONDS = 300.0

#: How long a survivor is given to be a straggler rather than an orphan. The resource
#: tracker exits a beat after the parent it serves, so a reading taken in the same
#: instant the run is reaped can catch it mid-exit; three seconds is far longer than
#: that and far shorter than the forty-minute stall.
SURVIVOR_GRACE_SECONDS = 3.0

#: How often the run's process group is counted while it runs. Frequent enough to see
#: workers that live for part of one phase, sparse enough not to load the machine the
#: run is being timed on.
SAMPLE_SECONDS = 0.1

#: How long `ReportCrash` is given to write a crash report before its absence is
#: believed. Measured on this machine by segfaulting a process and polling for the
#: report that named its pid: 0.33 seconds. Three is an order of magnitude over that,
#: and the run itself gives far more -- a worker dies during extraction and the run
#: then does P8 through P11 and prints its whole report before exiting -- so this
#: window is the margin on a worker that dies in the very last moment of the pool.
#:
#: It is the only wait a CLEAN run pays for in full, because absence cannot be
#: concluded early. That is about three seconds on a run of three, and it is the price
#: of the one crash the exit code cannot see.
CRASH_REPORT_GRACE_SECONDS = 3.0

#: Where macOS writes them. Every process the run started is a `Python` process and
#: lands here under the user's own account.
CRASH_REPORTS = Path.home() / "Library" / "Logs" / "DiagnosticReports"

#: The smallest process group that proves a worker really started: the run itself, the
#: resource tracker, and at least one worker. Measured here it peaks at nine -- seven
#: workers, because `EXTRACTION_WORKERS` is seven -- but the assertion is deliberately
#: not that number: what has to be true is that the pool was used, and pinning the
#: worker count here would make this guard fail the day somebody tunes it.
SMALLEST_GROUP_THAT_USED_THE_POOL = 3


def _png(path: Path, *, width: int = 64, height: int = 32) -> Path:
    """A real PNG, stdlib only, so Apple's Vision has something to actually open.

    What matters is that the file goes THROUGH the OCR reader, not what comes back
    from it: the failures this file guards are in worker lifecycle, and a worker
    crashes on a page it cannot parse just as readily as on one it can.
    """
    rows = b"".join(b"\x00" + bytes((x * 4 + y) % 256 for x in range(width * 3))
                    for y in range(height))

    def chunk(kind: bytes, body: bytes) -> bytes:
        return (struct.pack(">I", len(body)) + kind + body
                + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF))

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b""))
    return path


def _load_pdf_builder():
    """`tests/readers/pdf_bytes.py` is a rootless module: pytest only puts its
    directory on `sys.path` when it collects something from `tests/readers/`, which
    under a randomised order may be after this file or not at all. Load it by path so
    the PDFs are the real ones -- `test_live_path.py` does the same, for the same
    reason."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "survival_pdf_bytes", _HERE.parents[1] / "readers" / "pdf_bytes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_pdf


build_pdf = _load_pdf_builder()


def _corpus(root: Path) -> int:
    """Write the corpus and say how many files it has.

    Five shapes with a native library under them and one without: PDFs read by
    pdfium, images by Apple's Vision, a spreadsheet and an archive by the stdlib
    readers, and plain text to carry the count over the floor. The names are the
    owner's own shape -- a course code, a term, a work type -- so the run has facts
    to resolve rather than forty files of lorem ipsum, which is a different corpus
    from the one that crashes.
    """
    root.mkdir(parents=True, exist_ok=True)
    shaped = 0
    for i in range(1, 5):
        build_pdf(root / f"PHYS 1401 syllabus {i}.pdf", title=f"PHYS 1401 Syllabus {i}")
        shaped += 1
    for i in range(1, 3):
        _png(root / f"PHYS 1401 whiteboard {i}.png")
        shaped += 1
    for i in range(1, 3):
        with zipfile.ZipFile(root / f"PHYS 1401 submission {i}.zip", "w") as archive:
            archive.writestr("readme.txt", "PHYS 1401 submission bundle\n")
            archive.writestr("answers.txt", "1. 42\n2. 7\n")
        shaped += 1
    for i in range(1, 4):
        (root / f"PHYS 1401 grades {i}.csv").write_text(
            "student,assignment,score\nA,hw1,91\nB,hw1,84\nC,hw1,77\n",
            encoding="utf-8")
        shaped += 1
    for i in range(1, 4):
        (root / f"PHYS 1401 course {i}.json").write_text(
            '{"course": "PHYS 1401", "term": "Fall2024", "credits": 4}\n',
            encoding="utf-8")
        shaped += 1
    for i in range(1, 5):
        (root / f"BUSIB 4300 notes {i}.md").write_text(
            f"# BUSIB 4300 lecture {i}\n\nNYU, Spring 2025. Notes for week {i}.\n",
            encoding="utf-8")
        shaped += 1

    # `max`, and not a plain subtraction: the shaped files alone are eighteen, so a
    # `CORPUS_FILES` lowered below that would ask for a negative number of notes,
    # write none, and leave this function reporting a count it did not write -- which
    # the run would then fail on as a truncated scan. The corpus is never smaller
    # than the formats it exists to exercise.
    wanted = max(CORPUS_FILES, shaped)
    for i in range(1, wanted - shaped + 1):
        (root / f"PHYS 1401 homework {i}.txt").write_text(
            f"PHYS 1401 homework {i}\nColumbia University, Fall 2024.\n"
            f"Problem {i}: compute the work done by a constant force.\n",
            encoding="utf-8")
    written = sum(1 for _ in root.iterdir())
    assert written == wanted, f"the corpus builder wrote {written} of {wanted} files"
    return written


def _group_members(pid: int) -> tuple[str, ...]:
    """Every process in the run's process group, the run itself included.

    `pgrep` and not a walk of parent pids, because an orphan has already been
    re-parented to PID 1 by the time anybody asks -- which is precisely why the
    process GROUP is the thing being read.
    """
    found = subprocess.run(["pgrep", "-g", str(pid)], capture_output=True, text=True)
    return tuple(found.stdout.split())


def _kill_the_group(pid: int) -> None:
    """Leave nothing behind, including on the way out of a failure.

    Called only when survivors were actually found or the run had to be killed, so
    that a group whose leader has been reaped is never signalled on the off-chance:
    a pid nothing holds is a pid the kernel may hand to somebody else.
    """
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):        # pragma: no cover -- gone
        pass


def _crash_reports_of(pid: int, *, since: float) -> tuple[str, ...]:
    """The crash reports THIS RUN's processes wrote, and nobody else's.

    **Attributed by pid, never by "a new file appeared".** This machine is worked by
    many agents and that folder is shared: it holds two hundred reports and gains one
    every few minutes, several of them written by the very agents hunting this crash.
    A guard that failed whenever the folder grew would be red most of the day and
    deleted by the end of it.

    `parentPid` is the key that does the work. A worker that segfaults is still a
    child of the run when it dies, so its report names the run's pid as its parent --
    which is true of every worker crash, including one the sampler never happened to
    see. `pid` itself is matched too, for the run's own death.

    `st_mtime` is a PRE-FILTER and not the decision, deliberately: an old report's
    mtime is bumped by whatever collects them -- observed here on a file named for
    the fourth and touched on the fifth -- so the timestamp only says which handful
    of files are worth opening, and the pid says which of them are ours.
    """
    deadline = time.monotonic() + CRASH_REPORT_GRACE_SECONDS
    while True:
        found: list[str] = []
        for report in CRASH_REPORTS.glob("*.ips"):
            try:
                if report.stat().st_mtime < since - 60:
                    continue
                body = json.loads(report.read_text(errors="replace").split("\n", 1)[1])
            except (OSError, ValueError, IndexError):    # pragma: no cover -- theirs
                continue
            if pid in (body.get("pid"), body.get("parentPid")):
                found.append(report.name)
        if found or time.monotonic() >= deadline:
            return tuple(sorted(found))
        time.sleep(0.1)


def _survivors_of(pid: int) -> tuple[str, ...]:
    members = _group_members(pid)
    deadline = time.monotonic() + SURVIVOR_GRACE_SECONDS
    while members and time.monotonic() < deadline:
        time.sleep(0.1)
        members = _group_members(pid)
    return members


@dataclass(frozen=True)
class TheRun:
    """What one real run left behind, on disk and in the process table."""
    code: int
    stderr: str
    database: Path
    survivors: tuple[str, ...]
    crash_reports: tuple[str, ...]
    peak_group: int
    seconds: float
    files: int


@pytest.fixture(scope="module")
def the_run(tmp_path_factory) -> TheRun:
    """One run of the real command line, in a process of its own, watched throughout.

    Module-scoped because the run costs about three seconds and the four questions
    below are four readings of ONE run, not four runs: they have to agree about the
    same process, and asking them separately would make three of them measure a
    different one.
    """
    tmp = tmp_path_factory.mktemp("survives-a-real-run")
    corpus, work = tmp / "corpus", tmp / "work"
    work.mkdir()
    files = _corpus(corpus)
    database = work / "plan.sqlite"

    # `cwd=work` and `--database` inside it, deliberately: the run writes its
    # `.wire-handle-key` beside the database it was given, and a default database
    # lands in the working directory. Both stay in `tmp_path` and neither reaches
    # the repository -- which `tests/conftest.py` polices on its own account.
    command = [sys.executable, str(_CLI), str(corpus),
               "--situation", SITUATION, "--label", LABEL,
               "--user", "survival-guard", "--database", str(database)]
    # Inherited already from `tests/conftest.py`, and stated here anyway: no run
    # started by this suite may read a credential or spend the owner's money.
    environment = dict(os.environ, GRAPH_AGENT_NO_DOTENV="1")

    seen: list[int] = []
    started = time.monotonic()
    # Wall clock and not `monotonic`: it is compared against file mtimes.
    before = time.time()
    with open(work / "stdout.txt", "wb") as out, open(work / "stderr.txt", "wb") as err:
        child = subprocess.Popen(
            command, cwd=str(work), stdin=subprocess.DEVNULL, stdout=out, stderr=err,
            env=environment, start_new_session=True)
        stop = threading.Event()

        def count_the_group() -> None:
            while not stop.wait(SAMPLE_SECONDS):
                seen.append(len(_group_members(child.pid)))

        watcher = threading.Thread(target=count_the_group, daemon=True)
        watcher.start()
        try:
            code = child.wait(timeout=RUN_CEILING_SECONDS)
        except subprocess.TimeoutExpired:
            _kill_the_group(child.pid)
            child.wait()
            raise AssertionError(
                f"the run did not finish within {RUN_CEILING_SECONDS:.0f} seconds. "
                "A pool that leaves its workers running is a HANG and not a slow "
                "run: the parent sits at 0.0 % CPU while a worker nobody told to "
                "stop blocks in `sem_wait` on the call queue. Observed at forty "
                "minutes on the owner's machine, released instantly when the "
                "orphans were killed by hand.") from None
        finally:
            stop.set()
            watcher.join()
    seconds = time.monotonic() - started

    survivors = _survivors_of(child.pid)
    crashes = _crash_reports_of(child.pid, since=before)
    if survivors:
        # Killed HERE and not left for the assertion to report, because a test that
        # proves the product orphans processes must not orphan them itself.
        _kill_the_group(child.pid)
    return TheRun(
        code=code, stderr=(work / "stderr.txt").read_text(errors="replace"),
        database=database, survivors=survivors, crash_reports=crashes,
        peak_group=max(seen, default=0),
        seconds=seconds, files=files)


def _counted(database: Path, sql: str) -> int:
    connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    try:
        return connection.execute(sql).fetchone()[0]
    finally:
        connection.close()


def test_the_run_exits_zero_rather_than_dying_natively(the_run: TheRun) -> None:
    """`exit 133`, and `-11` on the next attempt, on the owner's own corpus.

    A negative code from `Popen` IS the signal that killed it, which is the only way
    this failure is ever visible: the run prints its whole report, says "Nothing was
    moved", and then dies on the way out. Nothing before the last line of output is
    wrong, so nothing an in-process test can assert about the output catches it.
    """
    assert the_run.code == 0, (
        f"the product exited {the_run.code}"
        + (f" -- killed by signal {-the_run.code} "
           f"({signal.Signals(-the_run.code).name})" if the_run.code < 0 else "")
        + f". Its stderr:\n{the_run.stderr[-4000:]}")


def test_the_run_leaks_no_semaphores_at_shutdown(the_run: TheRun) -> None:
    """The warning that came with the segfault, and the reason it is worth its own name.

    Five leaked semaphores were printed by `resource_tracker` at interpreter shutdown
    on the run that died. The warning is not the crash, but it is the crash's own
    account of itself, and it appears on runs that still exit 0 -- so a guard that
    only reads the exit code would let the same defect through on the day it happened
    not to be fatal.
    """
    assert LEAKED_SEMAPHORES not in the_run.stderr, (
        "the run left multiprocessing semaphores for the resource tracker to clean "
        "up at interpreter shutdown -- the warning that came with `exit 133` and "
        f"with SIGSEGV on the owner's 199-file corpus. Its stderr:\n"
        f"{the_run.stderr[-4000:]}")


def test_the_run_leaves_no_worker_process_behind(the_run: TheRun) -> None:
    """Forty-seven of them had accumulated on the machine, and the cost is a deadlock.

    The precondition is half of this test and is asserted first: no orphans is a
    trivially true statement about a run that never started a worker. Since R-138
    every run starts one -- there is no floor left to fall below -- so what this
    reading now catches is a scan that read nothing at all. If the group never held
    more than the run itself, the rest of this file is measuring a serial run and
    every question in it is decorative.
    """
    assert the_run.peak_group >= SMALLEST_GROUP_THAT_USED_THE_POOL, (
        f"the run's process group never held more than {the_run.peak_group} "
        f"process(es), so no extraction worker was ever started and this file is "
        f"guarding nothing. The corpus is {the_run.files} files; every one of them "
        "is a submission and every submission goes to a worker, so either the scan "
        "declined to read these formats or the pool is no longer being built.")
    assert not the_run.survivors, (
        f"{len(the_run.survivors)} process(es) of this run outlived it: "
        f"{', '.join(the_run.survivors)}. A worker nobody stopped blocks in "
        "`sem_wait` for ever while still holding the descriptors it inherited, so "
        "whoever reads this run's output waits for an end-of-file that a dead run's "
        "children are holding open. Forty-seven were found on the owner's machine "
        "and a run stalled forty minutes behind them.")


def test_the_run_actually_read_the_corpus(the_run: TheRun) -> None:
    """The question that stops the other three being decorative.

    A truncated database is what the crash looked like from the outside: 19 of 199
    files extracted where 176 were expected. A run that exits 0, leaks nothing and
    orphans nothing, having read nineteen files, is the exact failure this whole file
    was written for -- and it passes every other question here perfectly.

    Two readings, because they fail differently. `files` is P3's scan and says the
    corpus was WALKED; `extraction_runs` under a content extractor says it was READ,
    and `text_units` says something came back. The content count used to be the
    second proof that the pool engaged -- more submissions than the floor meant
    submissions crossed it -- and R-138 took the floor away, so it is now only what
    it always mainly was: the guard against a truncated run.
    """
    assert the_run.database.exists(), (
        "the run wrote no database at all, having exited "
        f"{the_run.code} in {the_run.seconds:.1f}s")

    walked = _counted(the_run.database, "select count(*) from files")
    assert walked == the_run.files, (
        f"the scan indexed {walked} of {the_run.files} files")

    read = _counted(the_run.database,
                    "select count(distinct file_id) from extraction_runs "
                    f"where extractor_name != '{FILESYSTEM_ONLY}'")
    assert read > NOT_TRUNCATED, (
        f"only {read} of {the_run.files} files had their content read, which is at "
        f"or below `NOT_TRUNCATED` ({NOT_TRUNCATED}). The run was truncated -- 19 of "
        "199 is what the crash looked like -- or the scan is declining to read most "
        "of these formats on this machine.")

    recovered = _counted(the_run.database, "select count(*) from text_units")
    assert recovered >= the_run.files, (
        f"{recovered} text units were recovered from {the_run.files} files. A run "
        "that walks a corpus and reads nothing out of it exits 0 and is still the "
        "failure this file exists to catch.")


def test_the_run_absorbed_no_worker_crash(the_run: TheRun) -> None:
    """A worker segfault the pool RECOVERED from, which the exit code cannot see.

    `ProcessPool` is built to survive this on purpose. A worker that dies raises
    `BrokenProcessPool`, `_rebuild` puts the suspect into a pool of its own, and a
    retry that succeeds returns the outcome the caller was waiting for. The file is
    read, its rows are written, the run exits 0 and its database is complete -- and
    nothing in this product records that a process died. Every other question in this
    file passes such a run perfectly.

    That recovery is deliberate and `test_extraction_pool_recovery.py` exercises it
    on purpose; this test does not contradict it. What it says is that a segfault
    SURVIVED is still a segfault, and the day the reader stops being thread-safe
    again this is the only reading that goes red before the corpus grows big enough
    for the crash to become fatal.

    **A native crash reaches this file by two different doors, and only one is
    quiet.** The crash that started all this killed the PARENT -- on the calling
    thread, on a file read below the pool floor -- and a parent that dies takes the
    run down with it: the exit code says `-11` and the database is truncated, so
    questions 1 and 4 answer it and answer it loudly. This question is the other
    door. A WORKER that dies is caught by design, retried, and recovered from, and
    nothing above notices. Both doors are real; this is the one nothing else watches.

    The signal is the operating system's, because there is no other. Attribution is
    by pid and never by "the folder grew" -- see `_crash_reports_of`.
    """
    assert not the_run.crash_reports, (
        f"{len(the_run.crash_reports)} of this run's own processes crashed and the "
        f"run recovered and exited {the_run.code} anyway: "
        f"{', '.join(the_run.crash_reports)} in {CRASH_REPORTS}. Read the report's "
        "`exception` and `threads` -- a native crash inside a reader is the failure "
        "this whole file exists for, and `_rebuild` retrying it successfully is what "
        "makes it invisible to every other question here.")
