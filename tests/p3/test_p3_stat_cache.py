# tests/p3/test_p3_stat_cache.py
import os
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.stat_cache import (
    REASON_FIRST_OBSERVATION, REASON_MODIFICATION_TIME_CHANGED, REASON_SIZE_CHANGED,
    REASON_UNCHANGED, VERDICT_RECOMPUTE, VERDICT_REUSE, cache_verdicts,
)

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


@pytest.fixture()
def selection(ready, corpus: Path):
    return record_selection(ready, sources=[corpus], candidate_roots=[],
                            cross_folder_moves=False, selected_by=None)


def _scan(conn, selection):
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


def _rewrite_keeping_mtime(path: Path, data: bytes):
    before = path.stat()
    path.write_bytes(data)
    os.utime(path, (before.st_atime, before.st_mtime))


def test_the_first_observation_recomputes(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"one")
    run = _scan(ready, selection)
    row = cache_verdicts(ready, run)[0]
    assert row["verdict"] == VERDICT_RECOMPUTE
    assert row["reason"] == REASON_FIRST_OBSERVATION
    assert row["prior_observed_size"] is None
    assert row["prior_observed_modification_time"] is None
    assert row["observed_size"] == 3
    assert row["file_id"]


def test_rescanning_an_unchanged_corpus_reuses_everything(ready, selection, corpus: Path):
    # Done-means 7: "Re-scanning an unchanged corpus yields verdict = reuse for
    # every file and zero recomputes."
    for name in ("a.txt", "b.txt", "c.txt"):
        (corpus / name).write_bytes(b"content")
    _scan(ready, selection)
    second = _scan(ready, selection)

    rows = cache_verdicts(ready, second)
    assert len(rows) == 3
    assert {r["verdict"] for r in rows} == {VERDICT_REUSE}
    assert {r["reason"] for r in rows} == {REASON_UNCHANGED}
    assert not [r for r in rows if r["verdict"] == VERDICT_RECOMPUTE]


def test_reuse_re_reads_nothing(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"content")
    _scan(ready, selection)
    before = ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'hashing'"
    ).fetchone()["c"]
    _scan(ready, selection)
    after = ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'hashing'"
    ).fetchone()["c"]
    assert after == before
    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 1


def test_size_changed_with_mtime_unchanged_recomputes(ready, selection, corpus: Path):
    # Done-means 8. §1.2: "if either changes".
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    _rewrite_keeping_mtime(target, b"one plus more bytes")
    run = _scan(ready, selection)

    row = cache_verdicts(ready, run)[0]
    assert row["verdict"] == VERDICT_RECOMPUTE
    assert row["reason"] == REASON_SIZE_CHANGED
    assert row["prior_observed_size"] == 3
    assert row["observed_size"] == len(b"one plus more bytes")


def test_mtime_moving_backwards_with_size_unchanged_recomputes(ready, selection, corpus: Path):
    # Done-means 9. §1.2: "instead of assuming that time only moves forward" — this
    # is a difference test, and a restore or migration moves mtime backwards.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime - 100_000))
    run = _scan(ready, selection)

    row = cache_verdicts(ready, run)[0]
    assert row["verdict"] == VERDICT_RECOMPUTE
    assert row["reason"] == REASON_MODIFICATION_TIME_CHANGED
    assert row["observed_modification_time"] < row["prior_observed_modification_time"]


def test_mtime_moving_forwards_with_size_unchanged_recomputes(ready, selection, corpus: Path):
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime + 100_000))
    run = _scan(ready, selection)
    assert cache_verdicts(ready, run)[0]["reason"] == REASON_MODIFICATION_TIME_CHANGED


def test_both_changed_reports_one_deterministic_reason(ready, selection, corpus: Path):
    # R4's `reason` is one value and the SPEC supplies no compound one. Both
    # observed and both prior values are on the row regardless.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    target.write_bytes(b"a longer body entirely")
    run = _scan(ready, selection)
    row = cache_verdicts(ready, run)[0]
    assert row["reason"] == REASON_SIZE_CHANGED
    assert row["prior_observed_size"] is not None
    assert row["prior_observed_modification_time"] is not None


def test_there_is_one_verdict_per_file_per_run(ready, selection, corpus: Path):
    for name in ("a.txt", "b.txt"):
        (corpus / name).write_bytes(b"x")
    first = _scan(ready, selection)
    second = _scan(ready, selection)
    assert len(cache_verdicts(ready, first)) == 2
    assert len(cache_verdicts(ready, second)) == 2


def test_a_prior_verdict_is_not_reused_for_a_different_file_at_that_path(
        ready, selection, corpus: Path):
    # The prior only counts while its file still lives at that path.
    original = corpus / "a.txt"
    original.write_bytes(b"one")
    _scan(ready, selection)
    moved = corpus / "moved.txt"
    original.rename(moved)
    _scan(ready, selection)

    replacement = corpus / "a.txt"
    replacement.write_bytes(b"two")
    run = _scan(ready, selection)
    row = [r for r in cache_verdicts(ready, run)
           if r["observed_path"] == str(replacement)][0]
    assert row["reason"] == REASON_FIRST_OBSERVATION


def test_the_comparison_is_never_a_newer_than_test():
    # §1.2 says so in as many words. A `>` between two modification times would
    # reintroduce exactly the assumption the design rejects.
    import scan_agent.stat_cache as module
    source = Path(module.__file__).read_text()
    # Operators, not prose: the module docstring quotes §1.2's "instead of assuming
    # that time only moves forward", so the words are expected and the code is not.
    for forbidden in ("mtime >", "mtime <", "modification_time >",
                      "modification_time <", "> prior", "< prior", "max(", "min("):
        assert forbidden not in source, forbidden


def test_a_changed_stat_yields_a_p3_authored_external_modification_detection(
        ready, selection, corpus: Path):
    # Done-means 18.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    _rewrite_keeping_mtime(target, b"one plus more bytes")
    run = _scan(ready, selection)

    rows = ready.execute(
        "SELECT * FROM events WHERE event_type = 'external modification detection' "
        "ORDER BY event_id"
    ).fetchall()
    assert rows
    assert {r["subsystem"] for r in rows} == {"P3"}

    # alongside its stat observation and its recompute verdict
    assert cache_verdicts(ready, run)[0]["verdict"] == VERDICT_RECOMPUTE
    assert ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'stat observation'"
    ).fetchone()["c"] == 2


def test_the_detection_carries_the_hash_it_was_recorded_under(ready, selection, corpus: Path):
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    prior_hash = ready.execute("SELECT content_hash FROM files").fetchone()["content_hash"]
    _rewrite_keeping_mtime(target, b"one plus more bytes")
    _scan(ready, selection)

    first = ready.execute(
        "SELECT * FROM events WHERE event_type = 'external modification detection' "
        "ORDER BY event_id"
    ).fetchall()[0]
    assert first["content_hash"] == prior_hash


def test_a_first_observation_yields_no_detection(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"one")
    _scan(ready, selection)
    assert ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'external modification detection'"
    ).fetchone()["c"] == 0


def test_an_unchanged_rescan_yields_no_detection(ready, selection, corpus: Path):
    (corpus / "a.txt").write_bytes(b"one")
    _scan(ready, selection)
    _scan(ready, selection)
    assert ready.execute(
        "SELECT count(*) c FROM events WHERE event_type = 'external modification detection'"
    ).fetchone()["c"] == 0


def test_a_touch_alone_is_a_detection_even_with_identical_bytes(ready, selection, corpus: Path):
    # §1.2's rule is about size and mtime, not about bytes. A restore that resets
    # mtime is exactly the case the design names.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    before = target.stat()
    os.utime(target, (before.st_atime, before.st_mtime - 100_000))
    _scan(ready, selection)
    rows = ready.execute(
        "SELECT subsystem FROM events WHERE event_type = 'external modification detection'"
    ).fetchall()
    assert [r["subsystem"] for r in rows] == ["P3"]


def test_the_earlier_detection_is_never_rewritten(ready, selection, corpus: Path):
    # SPEC, "What P3 never overwrites": a re-scan appends; it does not rewrite.
    target = corpus / "a.txt"
    target.write_bytes(b"one")
    _scan(ready, selection)
    _rewrite_keeping_mtime(target, b"two bytes longer")
    _scan(ready, selection)
    first = ready.execute(
        "SELECT event_id, explanation FROM events "
        "WHERE event_type = 'external modification detection' ORDER BY event_id"
    ).fetchall()[0]
    _rewrite_keeping_mtime(target, b"three bytes longer again")
    _scan(ready, selection)
    still = ready.execute(
        "SELECT event_id, explanation FROM events "
        "WHERE event_type = 'external modification detection' ORDER BY event_id"
    ).fetchall()[0]
    assert (still["event_id"], still["explanation"]) == \
           (first["event_id"], first["explanation"])
