"""A chat question gets a few strong answers, not a flood.

Question words never match on their own, results are capped, a weak tail is
dropped, a protected file shows only when its own name was asked for, and a
folder's name brings that folder up first."""
from __future__ import annotations

from pathlib import Path

from database_agent.db import open_database
from items.hot_index import DEFAULT_LIMIT, find_files
from items.indexing import index_folder


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "home"
    (root / "Stroke paper").mkdir(parents=True)
    (root / "Stroke paper" / "covid and stroke.txt").write_text(
        "Stroke outcomes in covid patients, a research paper", encoding="utf-8")
    logs = root / "logs"
    logs.mkdir()
    for n in range(14):
        # Words a question is made of, and nothing else in common.
        (logs / f"run_{n:02d}.log").write_text(
            f"which files are about the folder with a name {n}",
            encoding="utf-8")
    (root / "research").mkdir()
    (root / "research" / "server.pem").write_text("-----BEGIN",
                                                  encoding="utf-8")
    project = root / "lacuna"
    project.mkdir()
    (project / "package.json").write_text("{}", encoding="utf-8")
    (project / "index.js").write_text("x", encoding="utf-8")
    (root / "lacuna notes.txt").write_text("thoughts", encoding="utf-8")
    for n in range(12):
        (root / f"tide chart {n:02d}.txt").write_text("tide", encoding="utf-8")
    return root


def _labels(hits) -> list[str]:
    return [h.display_label for h in hits]


def _conn(tmp_path):
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    return conn


def test_question_words_do_not_flood_the_answer(tmp_path):
    from items.indexing import read_document_text
    conn = _conn(tmp_path)
    read_document_text(conn)
    hits = find_files(conn, "which files are about stroke research",
                      mode="fts").hits
    labels = _labels(hits)
    assert labels[0] == "covid and stroke.txt"
    assert not [n for n in labels if n.startswith("run_")]


def test_results_are_capped_for_chat_and_a_limit_still_widens(tmp_path):
    conn = _conn(tmp_path)
    assert DEFAULT_LIMIT == 8
    assert len(find_files(conn, "tide chart", mode="fts").hits) == 8
    assert len(find_files(conn, "tide chart", limit=12, mode="fts").hits) == 12


def test_a_protected_file_shows_only_when_its_name_is_asked_for(tmp_path):
    conn = _conn(tmp_path)
    # "research" is only in the key's folder, never in its name.
    result = find_files(conn, "stroke research", mode="fts")
    assert not [h for h in result.hits if h.protected]
    # Its folder matched, so it is counted, never silently omitted.
    assert result.protected_count == 1
    unrelated = find_files(conn, "tide chart", mode="fts")
    assert unrelated.protected_count == 0
    named = find_files(conn, "server", mode="fts")
    assert [h.protected for h in named.hits] == [True]
    assert named.protected_count == 1


def test_a_protected_file_matched_by_its_folder_is_counted_not_shown(
        tmp_path):
    root = tmp_path / "home"
    folder = root / "Chinese University Application Materials"
    folder.mkdir(parents=True)
    (folder / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    for n in range(12):
        (root / f"chinese notes {n:02d}.txt").write_text("x", encoding="utf-8")
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, root)

    result = find_files(conn, "the chinese folder", mode="fts")

    # Never silently omitted: counted for this search, the row not returned.
    assert not [h for h in result.hits if h.protected]
    assert result.protected_count == 1


def test_a_folder_name_brings_up_the_project_first(tmp_path):
    conn = _conn(tmp_path)
    hits = find_files(conn, "the lacuna folder", mode="fts").hits
    first = conn.execute("SELECT item_type FROM items WHERE item_id = ?",
                         (hits[0].item_id,)).fetchone()["item_type"]
    assert first == "project"
    assert "lacuna notes.txt" in _labels(hits)


def test_a_folder_name_brings_up_what_is_inside_it(tmp_path):
    conn = _conn(tmp_path)
    hits = find_files(conn, "the stroke paper folder", mode="fts").hits
    assert _labels(hits)[0] == "covid and stroke.txt"


def test_a_weak_tail_is_dropped(tmp_path):
    from items import hot_index

    fused = [("a", 0.0328), ("b", 0.0300), ("c", 0.0100), ("d", 0.0090)]
    kept = hot_index._drop_weak_tail(fused)
    assert [i for i, _ in kept] == ["a", "b"]
