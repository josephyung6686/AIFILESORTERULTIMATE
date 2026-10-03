"""Search ranks the file a person means first and junk folders last."""
from __future__ import annotations

from items.hot_index import find_files, rebuild_fts
from items.identity import reconcile_tree


def _corpus(tmp_path):
    root = tmp_path / "lib"
    files = {
        "Applications/Resume.txt": "work experience",
        "site_files/resume.chunk.js": "var resume = 1;",
        "graphify-out/cache/resume.json": '{"resume": true}',
        "_archive/old/FOLDER_TREE.html": "resume " * 20,
        "Notes/essay_draft.txt": "my resume is attached to this long note",
    }
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return root


def _labels(conn, tmp_path, query="resume"):
    reconcile_tree(conn, _corpus(tmp_path))
    rebuild_fts(conn)
    return [h.display_label for h in find_files(conn, query, mode="fts").hits]


def test_the_filename_match_is_first(conn, tmp_path):
    assert _labels(conn, tmp_path)[0] == "Resume.txt"


def test_junk_paths_rank_below_every_other_hit(conn, tmp_path):
    labels = _labels(conn, tmp_path)
    junk = {"resume.chunk.js", "resume.json"}
    first_junk = min(labels.index(n) for n in junk if n in labels)
    assert all(n in junk for n in labels[first_junk:])
    assert "essay_draft.txt" in labels[:first_junk]
    assert "FOLDER_TREE.html" in labels[:first_junk]


def test_a_filename_match_outranks_a_body_only_match(conn, tmp_path):
    labels = _labels(conn, tmp_path)
    assert labels.index("Resume.txt") < labels.index("FOLDER_TREE.html")
    assert labels.index("Resume.txt") < labels.index("essay_draft.txt")


def test_an_archived_copy_ranks_below_the_current_body_match(conn, tmp_path):
    labels = _labels(conn, tmp_path)
    assert labels.index("essay_draft.txt") < labels.index("FOLDER_TREE.html")
