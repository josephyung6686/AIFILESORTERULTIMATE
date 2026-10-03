"""A software project is findable as one item; nothing inside it is an item."""
from __future__ import annotations

from database_agent.db import open_database
from items.hot_index import find_files
from items.indexing import index_folder


def test_a_project_is_one_findable_item(tmp_path):
    root = tmp_path / "home"
    project = root / "Hoyahacks" / "frontend"
    (project / "src").mkdir(parents=True)
    (project / "package.json").write_text("{}", encoding="utf-8")
    (project / "README.md").write_text("# Hackathon dashboard\n",
                                       encoding="utf-8")
    (project / "src" / "app.js").write_text("x", encoding="utf-8")
    (root / "essay.txt").write_text("an essay", encoding="utf-8")
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])

    index_folder(conn, root)

    for query in ("hoyahacks", "hackathon dashboard"):
        hits = find_files(conn, query, limit=5).hits
        assert len(hits) == 1, query
        assert hits[0].display_label in ("frontend", "Hoyahacks/frontend")
        row = conn.execute("SELECT item_type FROM items WHERE item_id = ?",
                           (hits[0].item_id,)).fetchone()
        assert row["item_type"] == "project"
    inside = conn.execute(
        "SELECT COUNT(*) FROM items WHERE open_target LIKE ?",
        (f"{project}/%",)).fetchone()[0]
    assert inside == 0
    # Indexing again does not mint a second item for the same project.
    index_folder(conn, root)
    assert conn.execute("SELECT COUNT(*) FROM items WHERE item_type = 'project'"
                        ).fetchone()[0] == 1


def _project_corpus(tmp_path):
    root = tmp_path / "home"
    project = root / "Hoyahacks" / "frontend"
    (project / "src").mkdir(parents=True)
    (project / "package.json").write_text("{}", encoding="utf-8")
    (project / "README.md").write_text("# Hackathon dashboard\n",
                                       encoding="utf-8")
    (project / "src" / "app.js").write_text("x", encoding="utf-8")
    (root / "essay.txt").write_text("an essay", encoding="utf-8")
    return root, project


def test_a_deleted_project_folder_is_no_longer_found(tmp_path):
    import shutil

    from items.refresh import refresh_index

    root, project = _project_corpus(tmp_path)
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, root)
    assert find_files(conn, "hackathon dashboard", limit=5).hits

    shutil.rmtree(project)
    refresh_index(conn, roots=[root])

    assert not find_files(conn, "hackathon dashboard", limit=5).hits
    assert conn.execute(
        "SELECT presence FROM items WHERE item_type = 'project'"
    ).fetchone()["presence"] == "missing"


def test_a_maintenance_rebuild_keeps_the_project_text(tmp_path):
    from items.hot_index import rebuild_fts

    root, _project = _project_corpus(tmp_path)
    conn = open_database(tmp_path / "a.sqlite", scan_roots=[])
    index_folder(conn, root)

    rebuild_fts(conn)

    for query in ("hackathon dashboard", "package.json"):
        hits = find_files(conn, query, limit=5).hits
        assert len(hits) == 1, query
