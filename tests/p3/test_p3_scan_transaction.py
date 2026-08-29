# tests/p3/test_p3_scan_transaction.py
"""Where the scan's transaction boundary is, and what it may not cost.

The scan is the first thing the product does: a person points it at a folder and
waits. Measured on the 3,473-file corpus of `tests/integration/test_scale_stress.py`
it managed 67 files/s -- 14 ms a file, which is 25 minutes for 100,000 files.

The 14 ms was not the hashing and not the queries. `open_database` opens the
connection in autocommit (`isolation_level=None`) with `synchronous = FULL`, and a
file admitted writes about five rows -- the `files` row, its `discovery`, `hashing`
and `stat observation` events, and P3's cache verdict. With no explicit boundary
each of those five is its own transaction and each one fsyncs. On macOS that fsync
is `F_FULLFSYNC`, a flush of the whole device write cache, so it also stalls the
NEXT file's `open()`: a cProfile blamed `_io.open` for 79% of the run, and the same
profile with one transaction held open showed `_io.open` fall by 5x without one
line of the hashing changing.

**Every test here has a twin, because a throughput win can always be faked by
doing less work.** The batching guards below are paired with a census that pins
what one scan of a fixed corpus records, down to the exclusion verdict for a
protected container that must be counted and never opened.
"""
from __future__ import annotations

import builtins
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.exclusion import (
    LABEL_UNTOUCHED_PROTECTED, RULE_LITERAL_DIRECTORY_NAME,
    RULE_PROJECT_ROOT_DESCENDANT, RULE_PROTECTED_CONTAINER, exclusion_verdicts,
)
from scan_agent.inventory import directory_inventory
from scan_agent.scan import SCAN_COMMIT_BATCH, scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.stat_cache import VERDICT_RECOMPUTE, cache_verdicts

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"

#: Two full batches and one file over, derived from the shipped constant rather
#: than fixed: a corpus smaller than one batch commits once whatever the boundary
#: is, and would tell these tests nothing.
MANY = 2 * SCAN_COMMIT_BATCH + 1

#: The tables one walked item writes. `corpus_selections`, `scan_runs` and
#: `scan_resource_usage` are deliberately NOT here: they bracket the run and are
#: written outside its batches, so an interrupted scan still leaves a visible run.
PER_ITEM_TABLES = ("files", "events", "stat_cache_verdicts", "exclusion_verdicts",
                   "directory_inventory")


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def _scan(conn, corpus: Path):
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=lambda path: None, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


def _traced(conn) -> list[str]:
    """Every statement the connection executes, whitespace-collapsed."""
    log: list[str] = []
    conn.set_trace_callback(lambda statement: log.append(" ".join(statement.split())))
    return log


def _boundaries(log: list[str]) -> tuple[int, list[str]]:
    """(number of COMMITs, per-item writes that ran with no transaction open).

    A write with no transaction open is a write SQLite commits by itself, which is
    the fsync this file exists to remove.
    """
    depth = 0
    stray: list[str] = []
    for statement in log:
        head = statement.split()[0].upper() if statement.split() else ""
        if head == "BEGIN":
            depth += 1
        elif head in ("COMMIT", "ROLLBACK", "RELEASE"):
            depth = max(0, depth - 1)
        elif head == "INSERT" and depth == 0:
            table = statement.split()[2].split("(")[0]
            if table in PER_ITEM_TABLES:
                stray.append(statement)
    return sum(1 for s in log if s.split() and s.split()[0].upper() == "COMMIT"), stray


def _flat_corpus(corpus: Path, count: int) -> None:
    for index in range(count):
        (corpus / f"file_{index:05d}.txt").write_bytes(f"contents {index}".encode())


# ---------------------------------------------------------------------------
# 1. The boundary. Both directions: not per statement, and not one per scan.
# ---------------------------------------------------------------------------

def test_no_per_file_row_is_written_with_no_transaction_open(ready, corpus: Path):
    """The defect, stated as the mechanism rather than as a number of seconds.

    A statement executed in autocommit is its own transaction, and at
    `synchronous = FULL` that is an fsync. Five per file admitted is the 14 ms.
    """
    _flat_corpus(corpus, 20)
    log = _traced(ready)
    _scan(ready, corpus)
    _, stray = _boundaries(log)
    assert stray == [], (
        f"{len(stray)} per-file writes ran with no transaction open, so SQLite "
        f"committed each one by itself: e.g. {stray[0][:80]!r}. At "
        "`synchronous = FULL` every one of those is an fsync."
    )


def test_the_scan_commits_as_it_goes_and_is_not_one_long_transaction(ready,
                                                                    corpus: Path):
    """The twin of the test above, and the reason the fix is a BATCH.

    One transaction around the whole scan would remove the same fsyncs and be the
    wrong answer twice over: the WAL cannot checkpoint while a write transaction is
    open, so it grows to hold every page of a 500,000-file scan, and a power cut
    then loses the entire scan rather than the last few files. Committing as it
    goes is what bounds both.
    """
    _flat_corpus(corpus, MANY)
    log = _traced(ready)
    _scan(ready, corpus)
    commits, _ = _boundaries(log)
    assert 1 < commits < MANY, (
        f"{MANY} files were scanned in {commits} commits. One commit is the whole "
        "scan in a single transaction -- an unbounded WAL and an all-or-nothing "
        f"scan; {MANY} or more is a commit per file, which is the fsync per file "
        "this change exists to remove."
    )


def test_speed_was_not_bought_by_relaxing_durability(ready, corpus: Path):
    """The trade that was NOT made, pinned so it cannot be made quietly later.

    `synchronous = NORMAL` or `OFF` would also make the scan fast, and would mean a
    power cut could leave the database itself damaged rather than merely short of
    the last few files. Batching costs no durability at all: what a crash loses is
    files that were never recorded, which the next scan simply records.
    """
    _flat_corpus(corpus, 20)
    _scan(ready, corpus)
    assert ready.execute("PRAGMA synchronous").fetchone()[0] == 2, (
        "PRAGMA synchronous is no longer FULL. Throughput bought by relaxing it is "
        "durability spent, not work saved."
    )
    assert ready.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"


def test_an_interrupted_scan_keeps_every_batch_it_committed(ready, corpus: Path,
                                                            monkeypatch):
    """What the batch boundary actually costs, stated as the failure it allows.

    A crash loses the files observed since the last commit and nothing else. That
    is not corruption and not silence: those files were never recorded, exactly as
    if the scan had been stopped before reaching them, and a later scan finds no
    prior cache verdict for them and records them.
    """
    _flat_corpus(corpus, MANY)
    real = builtins.open
    seen = {"count": 0}

    def failing_open(path, *args, **kwargs):
        if str(path).endswith(".txt"):
            seen["count"] += 1
            if seen["count"] > MANY // 2:
                raise OSError("simulated power cut")
        return real(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", failing_open)
    with pytest.raises(OSError):
        _scan(ready, corpus)
    monkeypatch.undo()

    recorded = ready.execute("SELECT COUNT(*) c FROM files").fetchone()["c"]
    assert 0 < recorded < MANY, (
        f"{recorded} of {MANY} files survived the interruption. Zero means the "
        "whole scan was one transaction; all of them means nothing was in flight."
    )
    # Resumable: the run row was committed before the first batch, so the
    # interrupted scan is visible rather than absent.
    assert ready.execute("SELECT COUNT(*) c FROM scan_runs").fetchone()["c"] == 1
    # And a second scan finishes the corpus off, because the files lost with the
    # in-flight batch have no prior cache verdict.
    _scan(ready, corpus)
    assert ready.execute("SELECT COUNT(*) c FROM files").fetchone()["c"] == MANY


# ---------------------------------------------------------------------------
# 2. The census twin. A fast scan that misses files is not a scan.
# ---------------------------------------------------------------------------

def _census_corpus(corpus: Path) -> None:
    """One fixed corpus exercising every branch the writer has.

    Four ordinary files, two of them byte-identical (a duplicate family, which is
    two `files` rows under I1), one protected container, one literal-name
    exclusion, and one software project root whose descendants are rejected.
    """
    (corpus / "essay.txt").write_bytes(b"an essay")
    (corpus / "notes.txt").write_bytes(b"some notes")
    (corpus / "Papers").mkdir()
    (corpus / "Papers" / "copy_a.txt").write_bytes(b"identical bytes")
    (corpus / "Papers" / "copy_b.txt").write_bytes(b"identical bytes")

    bundle = corpus / "Numbers.app" / "Contents" / "MacOS"
    bundle.mkdir(parents=True)
    (bundle / "Numbers").write_bytes(b"a binary that is never opened")
    (corpus / "Numbers.app" / "Contents" / "sheet.numbers").write_bytes(b"never read")

    (corpus / "site" / "node_modules" / "left-pad").mkdir(parents=True)
    (corpus / "site" / "node_modules" / "left-pad" / "index.js").write_bytes(b"x")

    (corpus / "tool").mkdir()
    (corpus / "tool" / "package.json").write_bytes(b"{}")
    (corpus / "tool" / "main.js").write_bytes(b"y")


#: What one scan of `_census_corpus` records. Written out rather than computed so
#: that a change which quietly stops recording something has to edit this list and
#: say so.
EXPECTED = {
    "files": 4,                      # essay, notes, and BOTH duplicate copies (I1)
    "cache_verdicts": 4,             # one per admitted file
    "directories": 4,                # corpus, Papers, site, tool
    "exclusions": {
        RULE_PROTECTED_CONTAINER: 1,        # Numbers.app, named and not descended
        RULE_LITERAL_DIRECTORY_NAME: 1,     # node_modules
        RULE_PROJECT_ROOT_DESCENDANT: 2,    # package.json and main.js under `tool`
    },
    "events": {"discovery": 4, "hashing": 4, "stat observation": 4},
}


def test_one_scan_of_a_fixed_corpus_records_exactly_this(ready, corpus: Path):
    """The twin every throughput assertion needs.

    A scan can always be made faster by recording less, so the speed guards above
    are worth nothing without this: the same corpus, the same census, every row
    the slow scan wrote still written.
    """
    _census_corpus(corpus)
    run = _scan(ready, corpus)

    files = ready.execute("SELECT current_path, content_hash FROM files").fetchall()
    assert len(files) == EXPECTED["files"]
    assert {Path(row["current_path"]).name for row in files} == {
        "essay.txt", "notes.txt", "copy_a.txt", "copy_b.txt"}
    # I1: two live copies of identical bytes are two records sharing one hash.
    hashes = [row["content_hash"] for row in files]
    assert len(set(hashes)) == 3 and len(hashes) == 4

    assert len(cache_verdicts(ready, run)) == EXPECTED["cache_verdicts"]
    assert all(row["verdict"] == VERDICT_RECOMPUTE for row in cache_verdicts(ready, run))
    assert len(directory_inventory(ready, run)) == EXPECTED["directories"]

    by_rule: dict[str, int] = {}
    for row in exclusion_verdicts(ready, run):
        by_rule[row["rule"]] = by_rule.get(row["rule"], 0) + 1
    assert by_rule == EXPECTED["exclusions"]

    by_type: dict[str, int] = {}
    for row in ready.execute("SELECT event_type FROM events"):
        by_type[row["event_type"]] = by_type.get(row["event_type"], 0) + 1
    assert by_type == EXPECTED["events"]


def test_the_protected_container_is_counted_and_never_opened(ready, corpus: Path,
                                                             monkeypatch):
    """The fastest possible scan is one that skips protected areas entirely, and
    that is a safety failure wearing a performance win.

    MARKED AND COUNTED, NEVER OPENED: the verdict row is present with §8.6's
    `untouched_protected` label and a reachable path, no `files` row exists under
    the bundle, and no byte inside it was read.
    """
    _census_corpus(corpus)
    opened: list[str] = []
    real = builtins.open
    monkeypatch.setattr(builtins, "open",
                        lambda path, *a, **k: (opened.append(str(path)),
                                               real(path, *a, **k))[1])
    run = _scan(ready, corpus)
    monkeypatch.undo()

    protected = [row for row in exclusion_verdicts(ready, run)
                 if row["rule"] == RULE_PROTECTED_CONTAINER]
    assert len(protected) == 1, "the protected container was silently omitted"
    assert protected[0]["label"] == LABEL_UNTOUCHED_PROTECTED
    assert Path(protected[0]["path"]).name == "Numbers.app"

    assert not [row for row in ready.execute("SELECT current_path FROM files")
                if ".app" in row["current_path"]]
    assert not [path for path in opened if ".app" in path], (
        f"bytes inside a protected container were opened: {opened}")
