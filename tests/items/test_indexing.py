from pathlib import Path

from database_agent.db import open_database
from items.indexing import counts, index_folder


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "home"
    (root / "notes").mkdir(parents=True)
    (root / "notes" / "essay.txt").write_text("my essay", encoding="utf-8")
    (root / "proj").mkdir()
    (root / "proj" / "package.json").write_text("{}", encoding="utf-8")
    (root / "proj" / "index.js").write_text("x", encoding="utf-8")
    app = root / "Tool.app" / "Contents"
    app.mkdir(parents=True)
    (app / "Info.plist").write_text("<plist/>", encoding="utf-8")
    (root / "id.pem").write_text("-----BEGIN", encoding="utf-8")
    return root


def test_index_folder_reports_every_file_class(tmp_path):
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    seen = []
    c = index_folder(conn, _corpus(tmp_path),
                     on_progress=lambda s, d, t: seen.append(s))
    assert c.indexed >= 1
    assert c.set_aside_folders >= 1          # proj/
    assert c.protected >= 2                  # Tool.app + id.pem
    assert seen and seen[-1] == "done"
    assert counts(conn) == c


def test_search_finds_the_essay_right_after_indexing(tmp_path):
    from items.hot_index import find_files
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, _corpus(tmp_path))
    assert any(h.display_label == "essay.txt"
               for h in find_files(conn, "essay", limit=5).hits)
