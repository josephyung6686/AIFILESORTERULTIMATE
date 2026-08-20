# tests/p3/test_p3_watch.py
import os
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.watch import (
    CHANGE_APPEARED, CHANGE_DISAPPEARED, CHANGE_MODIFIED, SessionWatch,
)

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


@pytest.fixture()
def scanned(conn, corpus: Path):
    create_schema(conn)
    create_scan_schema(conn)
    (corpus / "a.txt").write_bytes(b"one")
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    scan(conn, selection, source=FilesystemCorpusSource(), mime_type_for=fixture_mime,
         scan_state=FIXTURE_STATE, budget_exhausted=NEVER)
    return conn


def _detections(conn):
    return conn.execute(
        "SELECT * FROM events WHERE event_type = 'external modification detection' "
        "ORDER BY event_id"
    ).fetchall()


def test_a_change_while_a_session_is_open_is_detected(scanned, corpus: Path):
    watch = SessionWatch(scanned)
    watch.open([corpus])
    target = corpus / "a.txt"
    target.write_bytes(b"one plus more")
    watch.notify(target)

    rows = _detections(scanned)
    assert len(rows) == 1
    assert rows[0]["subsystem"] == "P3"
    assert CHANGE_MODIFIED in rows[0]["explanation"]
    watch.close()


def test_an_appearance_is_detected(scanned, corpus: Path):
    watch = SessionWatch(scanned)
    watch.open([corpus])
    fresh = corpus / "brand-new.txt"
    fresh.write_bytes(b"new")
    watch.notify(fresh)
    rows = _detections(scanned)
    assert len(rows) == 1
    assert CHANGE_APPEARED in rows[0]["explanation"]
    assert rows[0]["file_id"] is None      # no record for it yet; §8.2 allows empty
    watch.close()


def test_a_disappearance_is_detected_and_the_record_is_untouched(scanned, corpus: Path):
    # 11 §4 names disappearance. SPEC Q14 still marks it unsettled and asks what
    # happens to a `files` row whose path no longer exists — that half is NOT
    # answered here: the row is not modified, moved, or removed.
    before = scanned.execute("SELECT * FROM files").fetchone()
    watch = SessionWatch(scanned)
    watch.open([corpus])
    (corpus / "a.txt").unlink()
    watch.notify(corpus / "a.txt")

    rows = _detections(scanned)
    assert len(rows) == 1
    assert CHANGE_DISAPPEARED in rows[0]["explanation"]
    after = scanned.execute("SELECT * FROM files").fetchone()
    assert tuple(after) == tuple(before)
    watch.close()


def test_nothing_is_watched_before_open_or_after_close(scanned, corpus: Path):
    # 11 §4: "There is no background daemon in v1. Closing the app ends the watch."
    watch = SessionWatch(scanned)
    target = corpus / "a.txt"
    target.write_bytes(b"changed before open")
    watch.notify(target)
    assert _detections(scanned) == []

    watch.open([corpus])
    watch.close()
    target.write_bytes(b"changed after close")
    watch.notify(target)
    assert _detections(scanned) == []


def test_a_path_outside_the_watched_roots_is_ignored(scanned, corpus: Path, tmp_path: Path):
    outside = tmp_path / "elsewhere.txt"
    outside.write_bytes(b"x")
    watch = SessionWatch(scanned)
    watch.open([corpus])
    watch.notify(outside)
    assert _detections(scanned) == []
    watch.close()


def test_an_unchanged_path_produces_no_detection(scanned, corpus: Path):
    watch = SessionWatch(scanned)
    watch.open([corpus])
    watch.notify(corpus / "a.txt")
    assert _detections(scanned) == []
    watch.close()


def test_a_detection_is_not_a_rescan(scanned, corpus: Path):
    # 11 §4: "A detection is not a rescan by itself… it does not restart the corpus
    # scan unless the user asks."
    def counts():
        return tuple(
            scanned.execute(f"SELECT count(*) c FROM {table}").fetchone()["c"]
            for table in ("scan_runs", "files", "exclusion_verdicts",
                          "directory_inventory", "stat_cache_verdicts")
        )

    before = counts()
    watch = SessionWatch(scanned)
    watch.open([corpus])
    (corpus / "a.txt").write_bytes(b"one plus more")
    watch.notify(corpus / "a.txt")

    assert counts() == before                  # nothing rescanned, nothing re-indexed
    assert len(_detections(scanned)) == 1      # only the detection
    watch.close()


def test_the_watch_observes_a_path_the_scan_would_have_excluded(scanned, corpus: Path):
    # The reading, asserted so it cannot drift silently. `11` §4 says P3 "watches the
    # selected roots" and narrows nothing; §1.1's exclusion is a rule for scanning.
    # So a change under a directory the scan prunes still authors a detection — with
    # an empty `file_id`, because no `files` row exists for it or ever will. P13's §4
    # rule must therefore tolerate a detection that marks no review item stale.
    watch = SessionWatch(scanned)
    watch.open([corpus])
    (corpus / "node_modules").mkdir()          # a new directory appears mid-session
    (corpus / "node_modules" / "pkg.js").write_bytes(b"x")
    watch.notify(corpus / "node_modules" / "pkg.js")

    rows = _detections(scanned)
    assert len(rows) == 1
    assert CHANGE_APPEARED in rows[0]["explanation"]
    assert rows[0]["file_id"] is None
    assert rows[0]["subsystem"] == "P3"
    # and it is still not a rescan: no `files` row was added for it
    assert scanned.execute("SELECT count(*) c FROM files").fetchone()["c"] == 1
    watch.close()


def test_poll_drives_the_watch_without_a_platform_binding(scanned, corpus: Path):
    # FSEvents / DispatchSource need a macOS API binding the standard library does
    # not supply. `poll` is the stdlib driver; the platform adapter calls `notify`.
    watch = SessionWatch(scanned)
    watch.open([corpus])
    target = corpus / "a.txt"
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime - 100_000))
    watch.poll()
    rows = _detections(scanned)
    assert len(rows) == 1
    assert rows[0]["subsystem"] == "P3"
    watch.close()


def test_the_module_starts_no_thread_and_no_timer():
    # "There is no background daemon in v1."
    import scan_agent.watch as module
    source = Path(module.__file__).read_text()
    # `daemon` is deliberately absent from this list: the module docstring quotes
    # §4's "There is no background daemon in v1".
    for forbidden in ("threading", "Thread", "Timer", "asyncio", "multiprocessing",
                      "signal.", "atexit"):
        assert forbidden not in source, forbidden
