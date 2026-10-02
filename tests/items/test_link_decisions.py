"""Link approve/reject/undo is exact on basis_key and never changes recognition."""
from __future__ import annotations

from pathlib import Path

from grouping.schema import create_grouping_schema
from items.decisions import accept_link, reject_link, undo_link
from items.identity import reconcile_tree
from items.relationships import project_witnessed_links


def _dup_pair(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    (root / "a.bin").write_bytes(b"twins")
    (root / "b.bin").write_bytes(b"twins")
    (root / "c.bin").write_bytes(b"other-pair-1")
    (root / "d.bin").write_bytes(b"other-pair-1")
    reconcile_tree(conn, root)
    create_grouping_schema(conn)
    project_witnessed_links(conn)
    return conn.execute(
        "SELECT * FROM relationships WHERE superseded_by IS NULL "
        "ORDER BY basis_key"
    ).fetchall()


def test_reject_suppresses_rebuild_of_same_basis_only(conn, tmp_path: Path):
    rows = _dup_pair(conn, tmp_path)
    assert len(rows) == 2
    first, second = rows[0], rows[1]
    reject_link(conn, first["relationship_id"], user_id="ada")
    # Drop live rows and rebuild — rejected basis stays gone; other pair returns.
    conn.execute("DELETE FROM relationships")
    project_witnessed_links(conn)
    live = conn.execute(
        "SELECT basis_key FROM relationships WHERE superseded_by IS NULL"
    ).fetchall()
    keys = {r["basis_key"] for r in live}
    assert first["basis_key"] not in keys
    assert second["basis_key"] in keys


def test_accept_then_undo_returns_to_proposed_and_keeps_history(conn, tmp_path: Path):
    rows = _dup_pair(conn, tmp_path)
    rel_id = rows[0]["relationship_id"]
    accept_link(conn, rel_id, user_id="ada")
    state = conn.execute(
        "SELECT state FROM relationships WHERE relationship_id = ?", (rel_id,)
    ).fetchone()["state"]
    assert state == "approved"
    undo_link(conn, rel_id, user_id="ada")
    state = conn.execute(
        "SELECT state FROM relationships WHERE relationship_id = ?", (rel_id,)
    ).fetchone()["state"]
    assert state == "proposed"
    history = conn.execute(
        "SELECT polarity FROM relationship_decisions WHERE relationship_id = ? "
        "ORDER BY created_at, rowid",
        (rel_id,),
    ).fetchall()
    assert [r["polarity"] for r in history] == ["accept", "undo"]


def test_reject_does_not_change_file_item_typing(conn, tmp_path: Path):
    """A link reject must not rewrite item typing or file rows.

    `Detector.explain` reads evidence tables, not relationships. This test
    locks the contract decisions actually own: typing_state and file_id stay.
    """
    rows = _dup_pair(conn, tmp_path)
    before = conn.execute(
        "SELECT item_id, file_id, typing_state, type_schema FROM items "
        "WHERE item_type = 'file' ORDER BY item_id"
    ).fetchall()
    reject_link(conn, rows[0]["relationship_id"], user_id="ada")
    after = conn.execute(
        "SELECT item_id, file_id, typing_state, type_schema FROM items "
        "WHERE item_type = 'file' ORDER BY item_id"
    ).fetchall()
    assert [tuple(r) for r in after] == [tuple(r) for r in before]
    # decisions.py must not import recognition (reject is not a reclassify).
    import ast
    import items.decisions as decisions
    from pathlib import Path as _Path
    tree = ast.parse(_Path(decisions.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(not a.name.startswith("recognition") for a in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("recognition")
