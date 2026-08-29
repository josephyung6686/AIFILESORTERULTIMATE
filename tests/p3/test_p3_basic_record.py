# tests/p3/test_p3_basic_record.py
from pathlib import Path

import pytest

from database_agent.db import create_schema
from database_agent.files_table import file_path_history, get_file
from database_agent.identity import hash_file

from scan_agent.access import FullDiskAccessRequired
from scan_agent.corpus_source import FilesystemCorpusSource
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import record_selection

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"     # SPEC Q4 is OPEN; the caller supplies this


def fixture_mime(path: Path) -> str | None:
    """Stands in for whoever answers SPEC Q6. P3 holds no determination method."""
    return {".pdf": "application/pdf", ".txt": "text/plain"}.get(path.suffix)


@pytest.fixture()
def ready(conn):
    create_schema(conn)
    create_scan_schema(conn)
    return conn


def _scan(conn, corpus, *, roots=(), sources=None):
    selection = record_selection(
        conn, sources=[corpus] if sources is None else sources,
        candidate_roots=list(roots), cross_folder_moves=False, selected_by=None,
    )
    return scan(conn, selection, source=FilesystemCorpusSource(),
                mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                budget_exhausted=NEVER)


def test_one_row_per_non_excluded_file_with_all_ten_1_2_fields(ready, corpus: Path):
    # Done-means 1.
    document = corpus / "Syllabus.pdf"
    document.write_bytes(b"%PDF-1.4 fixture bytes")
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "ignored.pdf").write_bytes(b"x")

    _scan(ready, corpus)

    rows = ready.execute("SELECT * FROM files").fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert row["current_path"] == str(document)                     # 1  path
    assert row["filename"] == "Syllabus.pdf"                        # 2  filename
    assert row["normalized_filename"] == "Syllabus.pdf"             # 3  normalized
    assert row["extension"] == ".pdf"                               # 4  extension
    assert row["mime_type"] == "application/pdf"                    # 5  MIME type
    assert row["observed_size"] == len(b"%PDF-1.4 fixture bytes")   # 6  size
    assert row["observed_timestamps"]                               # 7  timestamps
    assert row["directory_position"] == str(corpus)                 # 8  parent-folder
    assert row["content_hash"] == hash_file(document, materialized=True)   # 9 hash
    assert row["scan_state"] == FIXTURE_STATE                       # 10 scan state


def test_p3_supplies_no_detected_format(ready, corpus: Path):
    # detected_format is NOT one of R2's ten. It is §8.2's field and §2.9's
    # determination is P5's; P3 invents no value another part owns.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    assert ready.execute("SELECT detected_format FROM files").fetchone()[0] is None


def test_p3_is_the_author_of_every_event_the_scan_produces(ready, corpus: Path):
    # M8, and the other half of P1's test_p1_authors_none_of_the_scan_events.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    rows = ready.execute("SELECT DISTINCT subsystem FROM events").fetchall()
    assert [r["subsystem"] for r in rows] == ["P3"]


def test_discovery_stat_observation_and_hashing_are_all_appended(ready, corpus: Path):
    # Done-means 11, first half.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    types = {r["event_type"] for r in ready.execute("SELECT event_type FROM events")}
    assert {"discovery", "stat observation", "hashing"} <= types


def test_the_hashing_event_is_p3s_even_though_p1_wrote_it(ready, corpus: Path):
    # P1's observe_path appends `hashing` with subsystem = the `author` P3 supplied.
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    row = ready.execute(
        "SELECT subsystem FROM events WHERE event_type = 'hashing'"
    ).fetchone()
    assert row["subsystem"] == "P3"


def test_a_second_scan_adds_a_stat_observation_and_keeps_the_first(ready, corpus: Path):
    # Done-means 11, second half: "a second scan of the same file adds a new stat
    # observation and leaves the earlier one intact and readable."
    (corpus / "a.txt").write_bytes(b"a")
    _scan(ready, corpus)
    first = ready.execute(
        "SELECT event_id, explanation FROM events WHERE event_type = 'stat observation' "
        "ORDER BY event_id"
    ).fetchall()
    _scan(ready, corpus)
    after = ready.execute(
        "SELECT event_id, explanation FROM events WHERE event_type = 'stat observation' "
        "ORDER BY event_id"
    ).fetchall()
    assert len(after) == len(first) + 1
    assert after[0]["event_id"] == first[0]["event_id"]
    assert after[0]["explanation"] == first[0]["explanation"]


def test_discovery_is_appended_once_per_file_version(ready, corpus: Path):
    # §8.2's `discovery` is "a file enters the corpus", and §1.2's record is one per
    # FILE VERSION. The check is keyed on `file_id`, so a re-scan of an unchanged
    # file appends nothing, and a file whose bytes changed — which P1 resolves as a
    # new version with a new `file_id` (§8.2) — appends one for that version.
    target = corpus / "a.txt"
    target.write_bytes(b"a")

    def discoveries():
        return ready.execute(
            "SELECT file_id FROM events WHERE event_type = 'discovery' "
            "ORDER BY event_id"
        ).fetchall()

    _scan(ready, corpus)
    _scan(ready, corpus)
    assert len(discoveries()) == 1              # unchanged corpus: nothing entered

    target.write_bytes(b"a, with different bytes")
    _scan(ready, corpus)
    rows = discoveries()
    assert len(rows) == 2
    assert rows[0]["file_id"] != rows[1]["file_id"]     # per version, not per path


def test_a_moved_file_resolves_to_one_identity(ready, corpus: Path):
    # Done-means 10: "A file moved to a new path with byte-identical content resolves
    # to the same file version, and P3 emits no second identity."
    first = corpus / "one.pdf"
    first.write_bytes(b"identical bytes")
    _scan(ready, corpus)
    file_id = ready.execute("SELECT file_id FROM files").fetchone()["file_id"]

    moved = corpus / "moved" / "one.pdf"
    moved.parent.mkdir()
    first.rename(moved)
    _scan(ready, corpus)

    rows = ready.execute("SELECT * FROM files").fetchall()
    assert len(rows) == 1
    assert rows[0]["file_id"] == file_id
    assert rows[0]["current_path"] == str(moved)
    history = [r["path"] for r in file_path_history(ready, file_id)]
    assert history[0] == str(first)          # discovered here
    assert history[-1] == str(moved)         # and observed here afterwards
    assert set(history) == {str(first), str(moved)}     # and nowhere else


def test_a_candidate_root_contributes_no_files_row(ready, corpus: Path, tmp_path: Path):
    # §1.1: "roots are context for the proposal canvas, not permission to move files."
    landscape = tmp_path / "Documents"
    landscape.mkdir()
    (landscape / "elsewhere.txt").write_bytes(b"x")
    (corpus / "in-corpus.txt").write_bytes(b"x")
    _scan(ready, corpus, roots=[landscape])
    paths = [r["current_path"] for r in ready.execute("SELECT current_path FROM files")]
    assert paths == [str(corpus / "in-corpus.txt")]


def test_a_dataless_file_is_detected_and_never_hashed(ready, corpus: Path, monkeypatch):
    # 11 §5. SF_DATALESS is not settable on a fixture, so the source's verdict is
    # what is driven here; the point under test is that P3 skips before hashing.
    import scan_agent.corpus_source as module
    (corpus / "cloud.pdf").write_bytes(b"bytes that must not be read")

    real_entries = module.FilesystemCorpusSource.entries

    def entries(self, directory):
        from dataclasses import replace
        return [replace(e, dataless=e.name == "cloud.pdf")
                for e in real_entries(self, directory)]

    monkeypatch.setattr(module.FilesystemCorpusSource, "entries", entries)
    run = _scan(ready, corpus)

    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    detections = ready.execute(
        "SELECT path FROM dataless_detections WHERE scan_run_id = ?", (run,)
    ).fetchall()
    assert [d["path"] for d in detections] == [str(corpus / "cloud.pdf")]


def test_mime_strategy_and_scan_state_are_required(ready, corpus: Path):
    # SPEC Q6 and Q4 are OPEN. P3 holds neither a determination method nor an
    # enumeration, so the caller must supply both.
    selection = record_selection(ready, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    with pytest.raises(TypeError):
        scan(ready, selection, source=FilesystemCorpusSource(),
             scan_state=FIXTURE_STATE, budget_exhausted=NEVER)
    with pytest.raises(TypeError):
        scan(ready, selection, source=FilesystemCorpusSource(),
             mime_type_for=fixture_mime, budget_exhausted=NEVER)


def test_no_source_set_writes_nothing(ready, corpus: Path):
    # Done-means 2, at the writer.
    run = _scan(ready, corpus, sources=[])
    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    assert ready.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0
    assert ready.execute(
        "SELECT count(*) c FROM exclusion_verdicts WHERE scan_run_id = ?", (run,)
    ).fetchone()["c"] == 0


def test_an_unreadable_root_refuses_the_scan_before_any_row_exists(ready, corpus: Path):
    # 11 §1: "Until it is granted, P3 does not traverse." No run row either.
    import os
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("root can list a 0o000 directory")
    corpus.chmod(0o000)
    try:
        selection = record_selection(ready, sources=[corpus], candidate_roots=[],
                                     cross_folder_moves=False, selected_by=None)
        with pytest.raises(FullDiskAccessRequired):
            scan(ready, selection, source=FilesystemCorpusSource(),
                 mime_type_for=fixture_mime, scan_state=FIXTURE_STATE,
                 budget_exhausted=NEVER)
    finally:
        corpus.chmod(0o700)
    assert ready.execute("SELECT count(*) c FROM scan_runs").fetchone()["c"] == 0
    assert ready.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
