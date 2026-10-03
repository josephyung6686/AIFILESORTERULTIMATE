"""What the chat shows of the sorter's tree: folder names without ordering
numbers, and nothing from inside a set-aside coding project.

Judge 2 read "98 Review and Unsorted" as a top folder, and was asked about
files inside set-aside projects.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from assistant import organize_tools
from database_agent.db import open_database
from items.schema import create_items_schema


def _node(node_id, label, parent=None, kind="new"):
    return SimpleNamespace(node_id=node_id, display_label=label,
                           parent_node_id=parent, node_type=kind,
                           node_role="topic")


def _place(file_id, node_id):
    return SimpleNamespace(
        outcome="place", destination=SimpleNamespace(node_id=node_id),
        subject=SimpleNamespace(file_id=file_id, member_file_ids=()))


@pytest.fixture()
def tree(tmp_path, monkeypatch):
    root = tmp_path / "Desktop"
    conn = open_database(tmp_path / "agent.sqlite", scan_roots=[])
    create_items_schema(conn)
    conn.execute("INSERT INTO corpus_selections (selection_id, sources, "
                 "candidate_roots, cross_folder_moves, selected_at) VALUES "
                 "('s', ?, '[]', 0, '2026-10-04')", (json.dumps([str(root)]),))
    nodes = {n.node_id: n for n in (
        _node("r", "98 Review and Unsorted"),
        _node("e", "Education"),
        _node("p", "podcast-code", kind="existing"),
        _node("ps", "storage", parent="p", kind="existing"))}

    def path(node_id):
        parts = []
        while node_id in nodes:
            parts.append(nodes[node_id].display_label)
            node_id = nodes[node_id].parent_node_id
        return "/".join(reversed(parts))
    fake = {"version": "v", "nodes": nodes, "path": path,
            "by_file": {"f1": _place("f1", "r"), "f2": _place("f2", "e"),
                        "f3": _place("f3", "ps")}, "moves": {}}
    monkeypatch.setattr(organize_tools, "_sorter_tree", lambda c: fake)
    monkeypatch.setattr(organize_tools, "_set_aside_folders",
                        lambda c: [root / "podcast-code"])
    yield conn, root
    conn.close()


def test_show_tree_drops_ordering_numbers_and_project_insides(tree):
    conn, _ = tree
    paths = [f["path"] for f in organize_tools.show_tree(conn)["folders"]]
    assert "Review and Unsorted" in paths
    assert not any(p.startswith("98 ") for p in paths)
    assert "podcast-code/storage" not in paths


def test_moving_a_folder_by_its_shown_name_moves_the_real_branch(tree):
    from assistant.engine_tools import apply_branch
    conn, root = tree
    root.mkdir()
    organize_tools._sorter_tree(conn)["moves"]["f1"] = "plan"
    ctx = SimpleNamespace(chosen_folders={root.resolve()})
    result = apply_branch(conn, "Review and Unsorted", str(root), ctx)
    confirm = result["needs_confirmation"]
    assert confirm["ref"].endswith("|98 Review and Unsorted")
    assert "98 " not in confirm["summary"]
    assert "Review and Unsorted" in confirm["summary"]


def test_the_summary_names_top_folders_without_ordering_numbers(tree):
    conn, root = tree
    names = [t["name"] for t in organize_tools.organise_summary(
        conn, root)["top_folders"]]
    assert "Review and Unsorted" in names
    assert not any(n.startswith("98 ") for n in names)
