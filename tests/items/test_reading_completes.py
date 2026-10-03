"""Reading document text finishes: one file never stops the rest, each file
has a short ceiling, and a later session picks up where the last one stopped."""
from __future__ import annotations

import dataclasses
from pathlib import Path

from database_agent.db import open_database
from items import indexing
from items.indexing import counts, index_folder, read_document_text
from test_indexing_sensitivity import text_pdf


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "home"
    root.mkdir()
    for name in ("alpha", "bravo", "charlie", "delta"):
        (root / f"{name}.txt").write_text(f"notes about {name} things",
                                          encoding="utf-8")
    return root


def _file_id(conn, name: str) -> str:
    return conn.execute("SELECT file_id FROM files WHERE filename = ?",
                        (name,)).fetchone()["file_id"]


def test_one_file_that_raises_does_not_stop_the_rest(tmp_path, monkeypatch):
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    bad = _file_id(conn, "bravo.txt")
    real = indexing._authorities

    def authorities(c):
        made = real(c)

        def classify(conn_, file_id, content_hash):
            if file_id == bad:
                raise RuntimeError("the classifier broke on this one")
            return made.classify(conn_, file_id, content_hash)
        return dataclasses.replace(made, classify=classify)

    monkeypatch.setattr(indexing, "_authorities", authorities)
    seen = []
    read = read_document_text(conn, on_progress=lambda s, d, t: seen.append(d))

    assert read == 4
    assert read.unreadable == 1
    assert seen[-1] == 4 and seen == sorted(seen)
    after = counts(conn)
    # Counted, with a reason, and not owed again every session.
    assert after.unread_documents == 0
    assert after.unreadable_documents == 1
    reason = conn.execute("SELECT reason FROM unreadable_documents").fetchone()
    assert "classifier broke" in reason["reason"]


def test_reading_resumes_in_a_later_session(tmp_path):
    db = tmp_path / "a.sqlite"
    conn = open_database(db, scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    assert read_document_text(conn, limit=1) == 1
    conn.close()

    again = open_database(db, scan_roots=[])
    assert counts(again).unread_documents == 3
    assert read_document_text(again) == 3
    assert counts(again).unread_documents == 0


def test_each_file_has_a_short_ceiling(tmp_path, monkeypatch):
    import extraction_pool

    built = []
    real = extraction_pool.ProcessPool

    def recording(**kwargs):
        built.append(kwargs["seconds_per_extraction"])
        return real(**kwargs)

    monkeypatch.setattr(extraction_pool, "ProcessPool", recording)
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    read_document_text(conn)
    assert built == [indexing.READ_SECONDS_PER_FILE]
    assert indexing.READ_SECONDS_PER_FILE <= 60


def test_a_reading_that_protects_a_file_is_reported(tmp_path):
    root = _corpus(tmp_path)
    (root / "scan_0042.pdf").write_bytes(
        text_pdf("Hong Kong Identity Card HKID A123456(3)"))
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, root)
    before = counts(conn).protected

    read = read_document_text(conn)

    assert read.protected_newly_found == 1
    assert counts(conn).protected == before + 1


def test_a_file_whose_reading_failed_is_still_found_by_name_only(tmp_path):
    from items.hot_index import _text_was_read

    root = _corpus(tmp_path)
    (root / "take_01.wav").write_bytes(b"not really a wave file")
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, root)

    read = read_document_text(conn)

    content_hash = conn.execute(
        "SELECT content_hash FROM files WHERE filename = 'take_01.wav'"
    ).fetchone()[0]
    assert not _text_was_read(conn, content_hash)
    assert read.unreadable == 1
    assert counts(conn).unreadable_documents == 1
