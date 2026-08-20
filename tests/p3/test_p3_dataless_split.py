# tests/p3/test_p3_dataless_split.py
"""OQ3, closed as TWO counts -- and the loop that could reach neither.

`scan()` recorded the detection and `continue`d before `prior_observation`, so a
dataless file never reached the stat cache at all. That is right for a file seen for
the first time: hashing it would download it (11-ops-runtime.md §5) and P1 refuses to
mint a `files` row without a hash (R1). It is WRONG for a file the database already
holds -- one scanned while it was local and since evicted by "Optimize Mac Storage".
That file has a `files` row, a content hash and a history, and the unconditional
`continue` dropped it out of the scan entirely: no stat observation, no cache
verdict, nothing saying its bytes had gone.

So the two counts are:

    never hashed          P3's `dataless_detections` only. No `files` row exists and
                          none can be made.
    hashed, then evicted  the existing `files` row stays live, and P5 emits ONE
                          `completeness = dataless` run against it (C4's ninth value).

Neither branch could be reached before this. §8.6 requires unfinished work to stay
visible AS unfinished, and a file that silently stopped being scanned is the opposite.
"""
from dataclasses import replace
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.dataless import dataless_detections
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.stat_cache import cache_verdicts

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return {".pdf": "application/pdf", ".txt": "text/plain"}.get(path.suffix)


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def run_scan(conn, corpus):
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


def evict(monkeypatch, name: str):
    """Present one entry as dataless. SF_DATALESS is outside macOS's SF_SETTABLE
    mask, so it cannot be set on a fixture file; the source's verdict is driven."""
    import scan_agent.corpus_source as module
    real = module.FilesystemCorpusSource.entries

    def entries(self, directory):
        return [replace(e, dataless=e.name == name) for e in real(self, directory)]

    monkeypatch.setattr(module.FilesystemCorpusSource, "entries", entries)


# ------------------------------------------------- branch 1: never hashed
def test_a_file_first_seen_dataless_gets_no_files_row_and_is_still_counted(
        ready, corpus: Path, monkeypatch):
    (corpus / "cloud.pdf").write_bytes(b"bytes that must not be read")
    evict(monkeypatch, "cloud.pdf")
    scan_run = run_scan(ready, corpus)

    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    assert [d["path"] for d in dataless_detections(ready, scan_run)] == [
        str(corpus / "cloud.pdf")]


# --------------------------------------- branch 2: hashed, then evicted
def test_a_known_file_that_has_been_evicted_keeps_its_identity(
        ready, corpus: Path, monkeypatch):
    document = corpus / "cloud.pdf"
    document.write_bytes(b"bytes that were local last week")

    first = run_scan(ready, corpus)                      # scanned while local
    file_id = ready.execute("SELECT file_id FROM files").fetchone()["file_id"]
    assert dataless_detections(ready, first) == []

    evict(monkeypatch, "cloud.pdf")
    second = run_scan(ready, corpus)                     # bytes now in iCloud

    # The detection is recorded, as for any dataless file.
    assert [d["path"] for d in dataless_detections(ready, second)] == [str(document)]
    # And the file did not fall out of the scan: it is still one live row, under the
    # identity it was recorded with, with the hash taken when the bytes WERE local.
    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 1
    assert get_file(ready, file_id)["content_hash"]


def test_an_evicted_known_file_still_gets_its_stat_verdict(
        ready, corpus: Path, monkeypatch):
    """The verdict row is what the orchestrator reads to decide there is work. With
    the unconditional `continue` there was no row, so a dataless run could never be
    emitted for any file and C4's ninth completeness value was unreachable."""
    document = corpus / "cloud.pdf"
    document.write_bytes(b"bytes that were local last week")
    run_scan(ready, corpus)
    file_id = ready.execute("SELECT file_id FROM files").fetchone()["file_id"]

    evict(monkeypatch, "cloud.pdf")
    second = run_scan(ready, corpus)

    verdicts = [v for v in cache_verdicts(ready, second)
                if v["observed_path"] == str(document)]
    assert len(verdicts) == 1
    assert verdicts[0]["file_id"] == file_id


def test_an_evicted_file_is_never_re_hashed(ready, corpus: Path, monkeypatch):
    """11 §5: "Do not materialize, hash, or extract." Keeping the file in the scan
    must not turn into reading it. P1 raises if anything tries."""
    document = corpus / "cloud.pdf"
    document.write_bytes(b"bytes that were local last week")
    run_scan(ready, corpus)
    before = get_file(ready, ready.execute(
        "SELECT file_id FROM files").fetchone()["file_id"])["content_hash"]

    import database_agent.identity as identity
    monkeypatch.setattr(identity, "hash_file", lambda *a, **k: pytest.fail(
        "a dataless file was hashed; 11 §5 forbids it"))
    import scan_agent.basic_record as basic_record
    monkeypatch.setattr(basic_record, "hash_file", lambda *a, **k: pytest.fail(
        "a dataless file was hashed; 11 §5 forbids it"), raising=False)

    evict(monkeypatch, "cloud.pdf")
    run_scan(ready, corpus)
    after = get_file(ready, ready.execute(
        "SELECT file_id FROM files").fetchone()["file_id"])["content_hash"]
    assert after == before
