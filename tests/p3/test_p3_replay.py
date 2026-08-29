# tests/p3/test_p3_replay.py
from pathlib import Path

import pytest

from database_agent.db import create_schema, open_database

from scan_agent.corpus_source import FilesystemCorpusSource, SnapshotCorpusSource
from scan_agent.inventory import CURATION_UNDETERMINED
from scan_agent.replay import (
    CORPUS_FORM_METADATA_SAFE, CORPUS_FORM_SNAPSHOT, RecordingCorpusSource,
    boundary_fingerprint, record_selection_from_snapshot, replay, snapshot_from,
)
from scan_agent.scan import scan
from scan_agent.schema import create_scan_schema
from scan_agent.selection import (
    record_selection, selection_candidate_roots, selection_sources,
)

NEVER = lambda: False
FIXTURE_STATE = "fixture-scan-state"


def fixture_mime(path: Path) -> str | None:
    return None


def _fresh(tmp_path: Path, name: str):
    conn = open_database(tmp_path / name)
    create_schema(conn)
    create_scan_schema(conn)
    return conn


@pytest.fixture()
def populated(corpus: Path):
    (corpus / "Coursework").mkdir()
    (corpus / "Coursework" / "syllabus.pdf").write_bytes(b"%PDF fixture")
    (corpus / "Coursework" / "notes.md").write_bytes(b"notes")
    (corpus / "node_modules").mkdir()
    (corpus / "node_modules" / "buried.js").write_bytes(b"x")
    (corpus / "app").mkdir()
    (corpus / "app" / "package.json").write_bytes(b"{}")
    (corpus / "app" / "index.js").write_bytes(b"x")
    (corpus / "loose.txt").write_bytes(b"loose")
    return corpus


def _live_scan(conn, corpus):
    selection = record_selection(conn, sources=[corpus], candidate_roots=[],
                                 cross_folder_moves=False, selected_by=None)
    recording = RecordingCorpusSource(FilesystemCorpusSource())
    run = scan(conn, selection, source=recording, mime_type_for=fixture_mime,
               scan_state=FIXTURE_STATE, budget_exhausted=NEVER)
    return selection, run, recording


def test_a_replay_reproduces_exclusion_cache_and_curation_verdicts(
        tmp_path: Path, populated: Path):
    # Done-means 14.
    live = _fresh(tmp_path, "live.sqlite")
    selection, live_run, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, selection_id=selection,
                             corpus_form=CORPUS_FORM_METADATA_SAFE)

    harness = _fresh(tmp_path, "harness.sqlite")
    # the boundary comes from the bundle, not from the harness's own knowledge
    replayed_selection = record_selection_from_snapshot(harness, snapshot)
    replay_run = replay(harness, replayed_selection, snapshot=snapshot,
                        budget_exhausted=NEVER)

    assert boundary_fingerprint(live, live_run) == \
           boundary_fingerprint(harness, replay_run)
    live.close()
    harness.close()


def test_a_replay_touches_no_filesystem(tmp_path: Path, populated: Path):
    # §8.5: evaluation "without touching a live filesystem".
    live = _fresh(tmp_path, "live.sqlite")
    selection, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, selection_id=selection,
                             corpus_form=CORPUS_FORM_METADATA_SAFE)
    live.close()

    import shutil
    shutil.rmtree(populated)          # the corpus is gone

    harness = _fresh(tmp_path, "harness.sqlite")
    run = replay(harness, record_selection_from_snapshot(harness, snapshot),
                 snapshot=snapshot, budget_exhausted=NEVER)
    assert boundary_fingerprint(harness, run)["exclusions"]
    harness.close()


def test_the_snapshot_carries_the_listings_not_the_conclusions(
        tmp_path: Path, populated: Path):
    # The rules must re-fire on replay. The excluded directory is in the listing of
    # its parent; the contents it pruned were never listed and stay unlisted.
    live = _fresh(tmp_path, "live.sqlite")
    selection, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, selection_id=selection,
                             corpus_form=CORPUS_FORM_METADATA_SAFE)
    paths = {entry["path"] for entry in snapshot["entries"]}
    assert str(populated / "node_modules") in paths
    assert str(populated / "node_modules" / "buried.js") not in paths
    assert "rule" not in str(snapshot["entries"][0])
    live.close()


def test_the_snapshot_carries_content_hashes_for_p2s_envelope(
        tmp_path: Path, populated: Path):
    # §8.5's bundle contains "content hashes". P2 wraps this payload; P3's own
    # replay does not consume them, because P1 publishes no entry point that records
    # a file from a supplied hash.
    live = _fresh(tmp_path, "live.sqlite")
    selection, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, selection_id=selection,
                             corpus_form=CORPUS_FORM_SNAPSHOT)
    hashed = {e["path"]: e["content_hash"] for e in snapshot["entries"]
              if e["content_hash"] is not None}
    assert str(populated / "loose.txt") in hashed
    assert len(hashed[str(populated / "loose.txt")]) == 64
    assert snapshot["hash_algorithm"]
    live.close()


def test_a_metadata_safe_replay_writes_no_files_row(tmp_path: Path, populated: Path):
    # §8.5's own cost: no bytes, so no content-hash identity. Recorded, not hidden.
    live = _fresh(tmp_path, "live.sqlite")
    selection, _, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, selection_id=selection,
                             corpus_form=CORPUS_FORM_METADATA_SAFE)
    harness = _fresh(tmp_path, "harness.sqlite")
    run = replay(harness, record_selection_from_snapshot(harness, snapshot),
                 snapshot=snapshot, budget_exhausted=NEVER)
    assert harness.execute("SELECT count(*) c FROM files").fetchone()["c"] == 0
    assert harness.execute("SELECT count(*) c FROM events").fetchone()["c"] == 0
    verdicts = harness.execute(
        "SELECT file_id FROM stat_cache_verdicts WHERE scan_run_id = ?", (run,)
    ).fetchall()
    assert verdicts and all(v["file_id"] is None for v in verdicts)
    live.close()
    harness.close()


def test_the_replay_reproduces_the_curation_reading(tmp_path: Path, populated: Path):
    # SPEC Serialization: "a replay that reproduces the corpus but not its curation
    # reading would not reproduce P10's canvas."
    live = _fresh(tmp_path, "live.sqlite")
    selection, live_run, recording = _live_scan(live, populated)
    snapshot = snapshot_from(live, recording, selection_id=selection,
                             corpus_form=CORPUS_FORM_METADATA_SAFE)
    harness = _fresh(tmp_path, "harness.sqlite")
    run = replay(harness, record_selection_from_snapshot(harness, snapshot),
                 snapshot=snapshot, budget_exhausted=NEVER)

    live_signals = boundary_fingerprint(live, live_run)["curation"]
    replay_signals = boundary_fingerprint(harness, run)["curation"]
    assert live_signals == replay_signals
    assert set(dict(replay_signals).values()) == {CURATION_UNDETERMINED}
    live.close()
    harness.close()


def test_the_bundle_carries_r1_and_the_harness_re_asserts_it_from_it(
        tmp_path: Path, populated: Path):
    # SPEC Serialization: "R1–R4 and R6 must serialize into and re-assert from a P2
    # replay bundle." Without R1 in the payload, the harness would have to already
    # know the corpus boundary the bundle was supposed to carry.
    live = _fresh(tmp_path, "live.sqlite")
    landscape = populated.parent / "Documents"
    landscape.mkdir()
    selection = record_selection(live, sources=[populated], candidate_roots=[landscape],
                                 cross_folder_moves=True, selected_by="user-1")
    recording = RecordingCorpusSource(FilesystemCorpusSource())
    scan(live, selection, source=recording, mime_type_for=fixture_mime,
         scan_state=FIXTURE_STATE, budget_exhausted=NEVER)
    snapshot = snapshot_from(live, recording, selection_id=selection,
                             corpus_form=CORPUS_FORM_METADATA_SAFE)

    carried = snapshot["selection"]
    assert carried["sources"] == [str(populated)]
    assert carried["candidate_roots"] == [str(landscape)]
    assert carried["selected_by"] == "user-1"
    assert carried["selected_at"]                       # the original, preserved
    assert "selection_id" not in carried                # P3's local key is not R1

    harness = _fresh(tmp_path, "harness.sqlite")
    replayed = record_selection_from_snapshot(harness, snapshot)
    assert selection_sources(harness, replayed) == [populated]
    assert selection_candidate_roots(harness, replayed) == [landscape]
    row = harness.execute("SELECT * FROM corpus_selections").fetchone()
    assert row["cross_folder_moves"] == 1
    assert row["selected_by"] == "user-1"
    # a replay is a harness run (11 §3), not a second user action: the new row is
    # stamped when the harness wrote it, and the original time stays in the payload.
    assert row["selected_at"] != carried["selected_at"]
    live.close()
    harness.close()


def test_replay_imports_no_p2_code():
    import scan_agent.replay as module
    source = Path(module.__file__).read_text()
    assert "eval_agent" not in source and "bundle_manifest" not in source
