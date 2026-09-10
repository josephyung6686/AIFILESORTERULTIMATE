"""`104` §18.2 gap 23 -- the two predicates that were empty are real checks.

The design sentence, `00`:174: *"Cloud folders such as iCloud Drive, Dropbox,
Google Drive, and OneDrive introduce additional race conditions because a sync
agent can rename, replace, or create conflict copies while a plan is active. The
system should treat cloud-synced paths as externally mutable, verify them
immediately before and after action, and pause when sync conflicts appear."*

What was measured before this patch: `cli.py` handed `apply_selected`
`conflict_copies=lambda path: ()` and `dataless_of=lambda path: False`, so
`mutation.special.inspect_objects` -- which has always known how to pause on a
conflict and refuse a dataless source -- was asked two questions that could only
ever answer "no". Every one of `tests/p12/test_p12_special.py`'s conflict tests
passed a hand-written tuple in, so the pause was proven and the DETECTION was
not built. These tests drive the deployment's own predicates.

The measurement each test makes is named in its own docstring.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import observe_path

from mutation import vocabulary as v
from mutation.special import inspect_objects

from cli import _conflict_copies, _dataless

FIXED_TIMESTAMPS = '{"modified": "2026-09-10T00:00:00Z"}'


def _record(conn: sqlite3.Connection, path: Path) -> str:
    """One real `files` row for a real file, through P1's own writer.

    `observe_path` hashes the bytes itself, so two byte-identical files produce
    one `content_hash` across two live rows -- P1's I1, "§2.9's duplicate family
    and §8.3's identical-file collision both require the two copies to remain
    distinguishable". That is the shape a sync conflict actually has on disk and
    it is not simulated here.
    """
    return observe_path(
        conn, path,
        author="P3", component_version="test",
        filename=path.name, normalized_filename=path.name,
        extension=path.suffix, observed_size=path.stat().st_size,
        observed_timestamps=FIXED_TIMESTAMPS,
        parent_folder_context=str(path.parent),
        mime_type=None, detected_format=None,
        scan_state="included", materialized=True)


@pytest.fixture()
def corpus(conn, tmp_path):
    create_schema(conn)
    folder = tmp_path / "Dropbox" / "Coursework"
    folder.mkdir(parents=True)
    return conn, folder


# --------------------------------------------------------------------------- #
# The conflicted copy
# --------------------------------------------------------------------------- #

def test_a_conflicted_copy_beside_the_file_pauses_the_move(corpus, tmp_path):
    """`00`:174 "pause when sync conflicts appear" -- and it is a PAUSE.

    Measured: a byte-identical sibling in the same directory named with the
    marker a sync client leaves makes `inspect_objects` return
    `pause_reason=cloud_sync_conflict` with the sibling's name recorded on the
    verdict, and `permits_mutation` is False. `refusal_class` stays None --
    `special.py`'s own distinction: the plan is still good, a sync agent is
    mid-flight, so the person is told to wait rather than told no.
    """
    conn, folder = corpus
    source = folder / "Syllabus.pdf"
    source.write_bytes(b"the same bytes")
    copy = folder / "Syllabus (conflicted copy 2026-09-10).pdf"
    copy.write_bytes(b"the same bytes")
    _record(conn, source)
    _record(conn, copy)

    verdict = inspect_objects(
        source=source, destination_directory=folder,
        source_root=folder, destination_root=folder,
        extra_protected=None, conflict_copies=_conflict_copies(conn),
        dataless_of=lambda path: False)

    assert verdict.permits_mutation is False
    assert verdict.pause_reason == v.CLOUD_SYNC_CONFLICT
    assert verdict.refusal_class is None
    assert verdict.detail["conflict_copies"] == (
        "Syllabus (conflicted copy 2026-09-10).pdf",)
    # THE REASON IS RECORDED, in the words a person reads. `104` §18.2 gap 23
    # asks for the block "with its reason recorded", and `decline_message` is
    # where P12 keeps the sentence.
    assert verdict.detail["message"] == v.decline_message(
        f"paused:{v.CLOUD_SYNC_CONFLICT}")


def test_an_ordinary_duplicate_is_not_a_conflicted_copy(corpus):
    """Both conditions, never either -- the false-pause this test exists to stop.

    Measured: a byte-identical sibling whose NAME carries no conflict marker
    leaves the move permitted. A person keeps two copies of one PDF in one
    folder all the time; pausing their move to wait for a sync that is not
    running would be a worse product than the gap this closes.
    """
    conn, folder = corpus
    source = folder / "Syllabus.pdf"
    source.write_bytes(b"the same bytes")
    twin = folder / "Syllabus final.pdf"
    twin.write_bytes(b"the same bytes")
    _record(conn, source)
    _record(conn, twin)

    assert _conflict_copies(conn)(source) == ()


def test_a_conflict_marked_name_with_other_bytes_is_not_a_conflicted_copy(corpus):
    """The other half of the conjunction, measured from the other side.

    A file whose name carries the marker but whose bytes differ is not a copy of
    the file being moved -- it is some other file -- and `00`:172's own rule
    says so in the neighbouring paragraph: "A content-hash match supports
    deduplication review; a filename match alone does not."
    """
    conn, folder = corpus
    source = folder / "Syllabus.pdf"
    source.write_bytes(b"the original bytes")
    other = folder / "Notes (conflicted copy 2026-09-10).pdf"
    other.write_bytes(b"entirely different bytes")
    _record(conn, source)
    _record(conn, other)

    assert _conflict_copies(conn)(source) == ()


def test_a_conflicted_copy_in_another_folder_is_not_this_file_s_conflict(corpus):
    """Same directory, because a sync agent writes the copy BESIDE the original.

    Measured: the identical, conflict-marked file one folder over does not pause
    this move. Without the directory condition every duplicate anywhere on the
    disk would pause every move of its twin.
    """
    conn, folder = corpus
    source = folder / "Syllabus.pdf"
    source.write_bytes(b"the same bytes")
    elsewhere = folder.parent / "Archive"
    elsewhere.mkdir()
    away = elsewhere / "Syllabus (conflicted copy 2026-09-10).pdf"
    away.write_bytes(b"the same bytes")
    _record(conn, source)
    _record(conn, away)

    assert _conflict_copies(conn)(source) == ()


def test_a_file_this_scan_never_recorded_answers_none_rather_than_raising(corpus):
    """An answer, not a crash, and it is the honest one.

    A path with no `files` row is a path this product has observed nothing
    about, so it has no hash to compare a sibling against. The predicate says
    "none was found" -- which is now a check that ran, where before the patch it
    was a lambda that could not run.
    """
    conn, folder = corpus
    assert _conflict_copies(conn)(folder / "NeverScanned.pdf") == ()


# --------------------------------------------------------------------------- #
# The dataless source
# --------------------------------------------------------------------------- #

def test_an_ordinary_local_file_is_not_dataless(corpus):
    """The negative that keeps the refusal off every ordinary move.

    `SF_DATALESS` is outside macOS's `SF_SETTABLE` mask, so no test can set it
    and the positive case cannot be manufactured on this machine -- which is
    exactly why `scan_agent.dataless` says so in its own comment. What IS
    testable is that a real, present file reads as materialised, and that a path
    that cannot be stat'd answers False rather than raising.
    """
    conn, folder = corpus
    source = folder / "Syllabus.pdf"
    source.write_bytes(b"bytes")
    assert _dataless(source) is False


def test_a_path_that_cannot_be_stat_d_reads_as_not_dataless(corpus):
    """Not a fail-open, and the distinction is what a person would be told.

    `inspect_objects` refuses a missing source one line later with
    `source_or_destination_unavailable`. Answering True here would put
    `dataless=True` on that refusal -- telling a person their file is in iCloud
    when what happened is that it is gone.
    """
    conn, folder = corpus
    assert _dataless(folder / "NotThere.pdf") is False
