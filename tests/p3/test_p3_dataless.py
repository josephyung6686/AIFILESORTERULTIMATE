# tests/p3/test_p3_dataless.py
import os
from pathlib import Path

import pytest

from database_agent.db import create_schema

from scan_agent.dataless import (
    SF_DATALESS, dataless_detections, is_dataless, record_dataless_detection,
)
from scan_agent.run import start_scan_run
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection


class FakeStat:
    """Stands in for os.stat_result. SF_DATALESS is not user-settable (it is outside
    macOS's SF_SETTABLE mask), so a real dataless file cannot be built in a fixture."""
    def __init__(self, st_flags: int):
        self.st_flags = st_flags


@pytest.fixture()
def run(conn, tmp_path: Path):
    create_schema(conn)
    create_scan_schema(conn)
    selection = record_selection(conn, sources=[tmp_path], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    return start_scan_run(conn, selection)


def test_the_constant_is_macos_sf_dataless():
    # macOS sys/stat.h. Python's `stat` module does not publish it.
    assert SF_DATALESS == 0x40000000


def test_a_file_carrying_sf_dataless_is_detected():
    assert is_dataless(FakeStat(SF_DATALESS)) is True
    assert is_dataless(FakeStat(SF_DATALESS | 0x00010000)) is True


def test_an_ordinary_file_is_not_dataless(tmp_path: Path):
    p = tmp_path / "local.bin"
    p.write_bytes(b"bytes that are really here")
    assert is_dataless(os.stat(p)) is False


def test_a_platform_without_st_flags_reads_as_not_dataless():
    class NoFlags:
        pass
    assert is_dataless(NoFlags()) is False


def test_detection_never_opens_the_file():
    # 11 §5: "Hashing or opening them downloads the file." Detection is a stat
    # observation, so this module reads no bytes at all.
    import scan_agent.dataless as module
    source = Path(module.__file__).read_text()
    assert "open(" not in source
    assert "read_bytes" not in source
    assert "hash_file" not in source


def test_a_detection_is_recorded_and_is_readable(conn, run, tmp_path: Path):
    # 11 §5: "§8.6's progress line must be able to name these files rather than
    # folding them into OCR-capped or unreadable."
    record_dataless_detection(conn, run, tmp_path / "Thesis.pdf")
    rows = dataless_detections(conn, run)
    assert [r["path"] for r in rows] == [str(tmp_path / "Thesis.pdf")]
    assert rows[0]["observed_at"]


def test_a_detection_writes_no_extraction_run_and_no_completeness(conn, run, tmp_path: Path):
    # 11 §5 / SPEC: that record is P4's and P5 is its writer. Which `completeness`
    # value a dataless file eventually carries is P4 Open question 6 and is NOT
    # resolved here — none of P4's eight values means "the bytes are not on this
    # machine", and P3 does not choose one or add a ninth.
    record_dataless_detection(conn, run, tmp_path / "Thesis.pdf")
    tables = [r["name"] for r in
              conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    assert "extraction_runs" not in tables
    columns = [r["name"] for r in conn.execute("PRAGMA table_info(dataless_detections)")]
    assert "completeness" not in columns

    import scan_agent.dataless as module
    assert "completeness" not in Path(module.__file__).read_text()
