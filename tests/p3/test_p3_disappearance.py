# tests/p3/test_p3_disappearance.py
"""SPEC Q14's other half: what a re-scan does about a `files` row whose path is gone.

The person's disk changes between runs -- that is the normal case, not the edge one.
A file they deleted must stop being part of the corpus the next run plans over, and
its records must all still be there, because §8.5 has to be able to reconstruct the
run that saw it.

The twin these tests exist for is the second one: a fix that filtered too widely
would drop files that are still on the disk out of the person's plan, which is far
worse than naming one file too many.
"""
import os
import stat as stat_module
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import PATH_NO_LONGER_EXISTS, get_file

from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection
from scan_agent.watch import CHANGE_DISAPPEARED

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


def _row(conn, name: str):
    return conn.execute(
        "SELECT * FROM files WHERE filename = ?", (name,)).fetchone()


@pytest.fixture()
def three_files(corpus: Path):
    for name in ("syllabus.txt", "homework.txt", "lab.txt"):
        (corpus / name).write_text(f"{name} contents\n")
    return corpus


def test_a_file_the_person_deleted_leaves_the_corpus(ready, selection, three_files):
    _scan(ready, selection)
    (three_files / "lab.txt").unlink()
    _scan(ready, selection)

    assert _row(ready, "lab.txt")["scan_state"] == PATH_NO_LONGER_EXISTS


def test_the_files_that_are_still_there_keep_their_place(ready, selection, three_files):
    """The twin. An over-broad sweep would pass the test above and lose these two."""
    _scan(ready, selection)
    (three_files / "lab.txt").unlink()
    _scan(ready, selection)

    survivors = {row["filename"] for row in ready.execute(
        "SELECT filename FROM files WHERE scan_state = ?", (FIXTURE_STATE,))}
    assert survivors == {"syllabus.txt", "homework.txt"}


def test_nothing_the_deleted_file_left_behind_is_destroyed(ready, selection, three_files):
    """§8.5 has to reconstruct the run that saw it, so the row and every event stay."""
    _scan(ready, selection)
    before = _row(ready, "lab.txt")
    events_before = ready.execute(
        "SELECT event_id FROM events WHERE file_id = ?", (before["file_id"],)
    ).fetchall()
    assert events_before

    (three_files / "lab.txt").unlink()
    _scan(ready, selection)

    after = get_file(ready, before["file_id"])
    assert after is not None
    for column in ("file_id", "current_path", "filename", "content_hash",
                   "observed_size", "observed_timestamps"):
        assert after[column] == before[column], column
    kept = {row["event_id"] for row in ready.execute(
        "SELECT event_id FROM events WHERE file_id = ?", (before["file_id"],))}
    assert kept >= {row["event_id"] for row in events_before}


def test_the_disappearance_is_on_the_record_as_p3_observing_it(
        ready, selection, three_files):
    _scan(ready, selection)
    file_id = _row(ready, "lab.txt")["file_id"]
    (three_files / "lab.txt").unlink()
    _scan(ready, selection)

    rows = ready.execute(
        "SELECT * FROM events WHERE file_id = ? "
        "AND event_type = 'external modification detection'", (file_id,)).fetchall()
    disappearances = [row for row in rows if CHANGE_DISAPPEARED in row["explanation"]]
    assert len(disappearances) == 1
    assert disappearances[0]["subsystem"] == "P3"


def test_it_is_said_once_and_not_again_on_every_later_run(
        ready, selection, three_files):
    """A row already retired is not re-observed: a scan a week later must not add a
    disappearance a week late for a file nobody touched."""
    _scan(ready, selection)
    file_id = _row(ready, "lab.txt")["file_id"]
    (three_files / "lab.txt").unlink()
    _scan(ready, selection)
    _scan(ready, selection)
    _scan(ready, selection)

    rows = ready.execute(
        "SELECT explanation FROM events WHERE file_id = ? "
        "AND event_type = 'external modification detection'", (file_id,)).fetchall()
    assert sum(CHANGE_DISAPPEARED in row["explanation"] for row in rows) == 1


def test_a_folder_this_scan_did_not_look_at_is_not_reported_on(
        ready, corpus: Path, tmp_path: Path):
    """The unplugged-drive case, which is why the sweep is scoped to this scan's
    own folders. A run over one folder has looked at one folder; the files of
    another are absent from THIS walk for a reason it has no evidence about, and
    an external disk that is merely unplugged would otherwise have every file on
    it retired the next time the person scanned their Documents."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "tax return.txt").write_text("tax return\n")
    (corpus / "syllabus.txt").write_text("syllabus\n")

    both = record_selection(ready, sources=[corpus, elsewhere], candidate_roots=[],
                            cross_folder_moves=False, selected_by=None)
    _scan(ready, both)

    # The whole folder goes away, exactly as an unmounted volume does.
    (elsewhere / "tax return.txt").unlink()
    elsewhere.rmdir()

    only_corpus = record_selection(ready, sources=[corpus], candidate_roots=[],
                                   cross_folder_moves=False, selected_by=None)
    _scan(ready, only_corpus)

    assert _row(ready, "tax return.txt")["scan_state"] == FIXTURE_STATE

    # And a scan that DOES look there says so, so the guard is a scope and not a
    # blind spot.
    elsewhere.mkdir()
    _scan(ready, both)
    assert _row(ready, "tax return.txt")["scan_state"] == PATH_NO_LONGER_EXISTS


@pytest.mark.skipif(os.geteuid() == 0, reason="root can stat through mode 000")
def test_a_file_that_is_there_but_unreadable_is_not_called_deleted(
        ready, selection, corpus: Path):
    """Unreachable is not gone. Losing permission to a folder is a thing that
    happens to a live disk, and retiring its files would delete them from the
    person's plan while they are sitting right there."""
    holder = corpus / "locked"
    holder.mkdir()
    (holder / "notes.txt").write_text("notes\n")
    _scan(ready, selection)

    holder.chmod(0o000)
    try:
        _scan(ready, selection)
    finally:
        holder.chmod(stat_module.S_IRWXU)

    assert _row(ready, "notes.txt")["scan_state"] == FIXTURE_STATE


def test_a_path_that_is_now_inside_a_protected_container_is_never_opened(
        ready, selection, corpus: Path, monkeypatch):
    """The standing rule. A protected container is marked and counted, never opened
    -- so the sweep does not stat inside one, and a file it cannot look at is not
    reported as deleted either."""
    holder = corpus / "Vault"
    holder.mkdir()
    (holder / "passport.txt").write_text("passport\n")
    _scan(ready, selection)

    holder.rename(corpus / "Vault.app")
    ready.execute("UPDATE files SET current_path = ? WHERE filename = ?",
                  (str(corpus / "Vault.app" / "passport.txt"), "passport.txt"))

    import scan_agent.disappearance as disappearance
    opened: list[str] = []
    real_lstat = os.lstat

    def watched(path, *args, **kwargs):
        opened.append(str(path))
        return real_lstat(path, *args, **kwargs)

    monkeypatch.setattr(disappearance.os, "lstat", watched)
    _scan(ready, selection)

    assert not any("Vault.app" in path for path in opened)
    assert _row(ready, "passport.txt")["scan_state"] == FIXTURE_STATE
