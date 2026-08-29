# tests/p3/test_p3_corpus_source.py
from pathlib import Path

import pytest

from scan_agent.corpus_source import (
    KIND_DIRECTORY, KIND_FILE, KIND_OTHER, FilesystemCorpusSource, SnapshotCorpusSource,
)


def test_a_directory_listing_reports_kind_size_and_mtime(tmp_path: Path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.txt").write_bytes(b"abc")
    entries = {e.name: e for e in FilesystemCorpusSource().entries(tmp_path)}
    assert entries["sub"].kind == KIND_DIRECTORY
    assert entries["a.txt"].kind == KIND_FILE
    assert entries["a.txt"].size == 3
    assert entries["a.txt"].mtime > 0
    assert entries["a.txt"].dataless is False
    assert entries["a.txt"].path == str(tmp_path / "a.txt")


def test_a_listing_is_ordered_so_two_runs_agree(tmp_path: Path):
    for name in ("c.txt", "a.txt", "b.txt"):
        (tmp_path / name).write_bytes(b"x")
    first = [e.path for e in FilesystemCorpusSource().entries(tmp_path)]
    second = [e.path for e in FilesystemCorpusSource().entries(tmp_path)]
    assert first == second == sorted(first)


def test_a_symlink_is_neither_a_directory_nor_a_file(tmp_path: Path):
    # SPEC Q7 is OPEN. `follow_symlinks=False` means a symlink is never silently
    # descended and never handed to hash_file. What the traversal does with it is
    # Task 9's, and Task 9 records it as unresolved rather than deciding.
    (tmp_path / "real").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "real")
    entries = {e.name: e for e in FilesystemCorpusSource().entries(tmp_path)}
    assert entries["link"].kind == KIND_OTHER


def test_a_dataless_entry_is_reported_as_dataless_and_never_opened(tmp_path: Path):
    # 11 §5: the source's job is to REPORT the observation; refusing to hash is
    # P1's, through the `materialized` flag P3 derives from this field (Task 10).
    p = tmp_path / "cloud.bin"
    p.write_bytes(b"bytes")
    entry = FilesystemCorpusSource().entries(tmp_path)[0]
    assert entry.dataless is False
    import scan_agent.corpus_source as module
    assert "hash_file" not in Path(module.__file__).read_text()


def test_the_filesystem_source_has_bytes():
    assert FilesystemCorpusSource().has_bytes is True


def test_a_snapshot_source_lists_without_touching_a_filesystem(tmp_path: Path):
    # §8.5: evaluation "without touching a live filesystem".
    snapshot = {
        "corpus_form": "metadata_safe",
        "entries": [
            {"path": "/c/sub", "name": "sub", "kind": KIND_DIRECTORY, "size": 0,
             "mtime": 0.0, "dataless": False, "content_hash": None, "parent": "/c"},
            {"path": "/c/a.txt", "name": "a.txt", "kind": KIND_FILE, "size": 3,
             "mtime": 1.5, "dataless": False, "content_hash": "aaa", "parent": "/c"},
        ],
    }
    source = SnapshotCorpusSource(snapshot)
    entries = {e.name: e for e in source.entries("/c")}
    assert entries["a.txt"].size == 3
    assert entries["a.txt"].mtime == 1.5
    assert source.entries("/c/sub") == []


def test_a_metadata_safe_snapshot_has_no_bytes():
    # §8.5's metadata-safe form carries no file bytes, so P1's content-hash identity
    # cannot be recomputed from it. Recorded, not papered over.
    assert SnapshotCorpusSource({"corpus_form": "metadata_safe", "entries": []}).has_bytes is False
    assert SnapshotCorpusSource({"corpus_form": "snapshot", "entries": []}).has_bytes is True


def test_the_module_imports_nothing_from_p2():
    # P3 is buildable against P1 alone; P2 owns the bundle envelope.
    import scan_agent.corpus_source as module
    source = Path(module.__file__).read_text()
    assert "eval_agent" not in source and "bundle_manifest" not in source
