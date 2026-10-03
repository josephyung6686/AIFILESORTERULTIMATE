"""P6 deferred organize / link tools — dry-run by default.

Loaded only after request_tools(group). apply/undo stay in tools.py behind
ASSISTANT_ENABLE_APPLY. Never invent destinations from file text.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from items.hot_index import rebuild_fts
from items.identity import reconcile_tree


def scan_refresh(conn: sqlite3.Connection, root: str | None) -> dict[str, Any]:
    if not root:
        return {"ok": False, "error": "root path required", "moved": False}
    path = Path(root)
    if not path.is_dir():
        return {"ok": False, "error": f"not a directory: {root}", "moved": False}
    reconcile_tree(conn, path)
    rebuilt = rebuild_fts(conn)
    return {
        "ok": True,
        "reconciled": True,
        "fts_rows": rebuilt,
        "moved": False,
    }


def propose_groups(conn: sqlite3.Connection, *, limit: int = 20) -> dict[str, Any]:
    """Read-only: surface mutual-semantic / duplicate edges as group proposals."""
    groups = []
    if not _table(conn, "group_edges"):
        return {"ok": True, "groups": [], "moved": False, "note": "no group_edges"}
    rows = conn.execute(
        "SELECT edge_type, from_file_id, to_file_id, weight FROM group_edges "
        "WHERE superseded_by IS NULL "
        "ORDER BY weight DESC LIMIT ?",
        (limit,),
    ).fetchall()
    for r in rows:
        groups.append({
            "edge_type": r["edge_type"],
            "from_file_id": r["from_file_id"],
            "to_file_id": r["to_file_id"],
            "weight": r["weight"],
            "state": "proposed",
        })
    return {"ok": True, "groups": groups, "moved": False}


RUN_THE_SORTER = (
    "No folder tree has been proposed yet. Run `database-agent <FOLDER>` to "
    "read the folder and propose one; nothing moves until you freeze and apply.")
PLACE_THE_FILES = (
    "The sorter proposed folders but has not placed files in them yet (it was "
    "run with --stop-after). Run `database-agent <FOLDER>` without --stop-after "
    "to see where each file would go.")


def _sorter_tree(conn: sqlite3.Connection):
    """The sorter's latest plan version: node paths, decisions and move plans."""
    if not (_table(conn, "plan_versions") and _table(conn, "placement_decisions")):
        return None
    from placement.store import decisions_for_plan
    from tree_design.store import latest_plan_version, nodes_for_version
    version = latest_plan_version(conn)
    if version is None:
        return None
    nodes = {n.node_id: n for n in nodes_for_version(conn, version)}

    def path(node_id: str) -> str:
        parts = []
        while node_id in nodes:
            parts.append(nodes[node_id].display_label)
            node_id = nodes[node_id].parent_node_id
        return "/".join(reversed(parts))

    by_file = {}
    for d in decisions_for_plan(conn, plan_version=version):
        for file_id in (d.subject.file_id, *d.subject.member_file_ids):
            if file_id:
                by_file[file_id] = d
    moves = {}
    if _table(conn, "move_plans"):
        moves = {r["file_id"]: r["plan_id"] for r in conn.execute(
            "SELECT file_id, plan_id FROM move_plans WHERE plan_version = ? "
            "AND superseded_by IS NULL", (version,))}
    return {"version": version, "nodes": nodes, "path": path,
            "by_file": by_file, "moves": moves}


def _held(row) -> bool:
    from items.file_identity import path_is_protected
    return row["typing_state"] == "held" or bool(
        row["open_target"] and path_is_protected(row["open_target"]))


def _set_aside_by_rule(conn: sqlite3.Connection) -> dict[str, int]:
    """Paths the latest scan set aside, per rule: marked and counted."""
    if _table(conn, "scan_runs"):
        last = conn.execute(
            "SELECT scan_run_id FROM scan_runs "
            "ORDER BY started_at DESC, rowid DESC LIMIT 1").fetchone()
        if last is not None:
            from scan_agent.summary import scan_run_summary
            return dict(scan_run_summary(
                conn, last["scan_run_id"])["paths_excluded_by_rule"])
    from items.identity import excluded_areas
    by_rule: dict[str, int] = {}
    for area in excluded_areas(conn):
        by_rule[area["rule"]] = by_rule.get(area["rule"], 0) + area["paths"]
    return by_rule


def show_tree(conn: sqlite3.Connection) -> dict[str, Any]:
    """The sorter's proposed or frozen tree, read from its tables. Moves nothing."""
    tree = _sorter_tree(conn)
    aside = _set_aside_by_rule(conn)
    if tree is None:
        return {"ok": True, "moved": False, "plan_version": None,
                "set_aside_by_rule": aside, "next_step": RUN_THE_SORTER}
    placed: dict[str, int] = {}
    outcomes: dict[str, int] = {}
    for d in tree["by_file"].values():
        outcomes[d.outcome] = outcomes.get(d.outcome, 0) + 1
        if d.outcome == "place" and d.destination is not None:
            placed[d.destination.node_id] = placed.get(d.destination.node_id, 0) + 1
    held = 0
    if _table(conn, "items"):
        held = conn.execute(
            "SELECT count(DISTINCT file_id) FROM items WHERE presence = 'live' "
            "AND superseded_by IS NULL AND typing_state = 'held'").fetchone()[0]
    # The person's own folders that receive nothing are counted, not listed:
    # a real Desktop mirrors hundreds and would overrun the turn's byte budget.
    quiet = {n.node_id for n in tree["nodes"].values()
             if n.node_type == "existing" and not placed.get(n.node_id)}
    out = {
        "ok": True,
        "moved": False,
        "plan_version": tree["version"],
        "folders": [
            {"node_id": n.node_id, "path": tree["path"](n.node_id),
             "kind": n.node_type, "role": n.node_role,
             "files": placed.get(n.node_id, 0)}
            for n in tree["nodes"].values() if n.node_id not in quiet
        ],
        "your_folders_receiving_nothing": len(quiet),
        "files": {"decided": len(tree["by_file"]), "by_outcome": outcomes,
                  "held": held},
        "frozen_moves": len(tree["moves"]),
        "set_aside_by_rule": aside,
        "note": ("Held files are counted, never named here. Use propose_tree "
                 "with item_ids to see where a file goes and why."),
    }
    if not tree["by_file"]:
        out["next_step"] = PLACE_THE_FILES
    return out


def organise_summary(conn: sqlite3.Connection, root: Path) -> dict[str, Any]:
    """What an organise run left in the database, as counts a person can
    be told: no paths of the database, flags, codes or arithmetic."""
    tree = show_tree(conn)
    sorter = _sorter_tree(conn)
    nodes = sorter["nodes"] if sorter else {}
    placed = {f["node_id"]: f["files"] for f in tree.get("folders") or []}

    def under(node_id: str) -> int:
        return placed.get(node_id, 0) + sum(
            under(n.node_id) for n in nodes.values()
            if n.parent_node_id == node_id)

    top = [n for n in nodes.values() if n.parent_node_id not in nodes]
    proposed = [n for n in nodes.values() if n.node_type != "existing"]
    loose = [r for r in conn.execute(
        "SELECT file_id, open_target FROM items WHERE presence = 'live' "
        "AND superseded_by IS NULL AND open_target IS NOT NULL")
        if str(Path(r["open_target"]).parent) == str(root)]
    by_file = sorter["by_file"] if sorter else {}

    def is_placed(file_id) -> bool:
        d = by_file.get(file_id)
        return bool(d and d.outcome == "place")

    return {
        "folders_proposed": len(proposed),
        "top_folders": [{"name": n.display_label, "files": under(n.node_id),
                         "new": n.node_type != "existing"}
                        for n in sorted(top, key=lambda n: -under(n.node_id))
                        ][:12],
        "files_placed": sum(1 for f in by_file if is_placed(f)),
        "loose_files": len(loose),
        "loose_files_placed": sum(1 for r in loose if is_placed(r["file_id"])),
        "open_questions": len(_open_questions(conn)),
        "held": int((tree.get("files") or {}).get("held") or 0),
        "set_aside": sum(tree.get("set_aside_by_rule", {}).values()),
    }


def _open_questions(conn: sqlite3.Connection) -> tuple:
    try:
        from questions.store import open_questions
        return open_questions(conn)
    except sqlite3.Error:
        return ()


def propose_tree(conn: sqlite3.Connection,
                 item_ids: list[str] | None = None) -> dict[str, Any]:
    """Quick sort for the files the person names. Writes nothing, moves nothing.

    With a sorter tree: each file's destination and reason come from its
    placement row. Without one: its recognised type, and what to run.
    """
    if not item_ids:
        return {"ok": False, "moved": False,
                "error": "name the files to sort (item_ids); "
                         "show_tree covers the whole folder"}
    tree = _sorter_tree(conn)
    names = {} if tree else _type_names()
    files = []
    for item_id in item_ids:
        row = conn.execute(
            "SELECT item_id, display_label, file_id, open_target, typing_state, "
            "type_schema FROM items WHERE item_id = ? AND presence = 'live' "
            "AND superseded_by IS NULL", (item_id,)).fetchone()
        if row is None:
            files.append({"item_id": item_id, "error": "item not found"})
            continue
        held = _held(row)
        entry = {"item_id": item_id, "display_label": row["display_label"],
                 "open_target": None if held else row["open_target"],
                 "held": held, "destination": None}
        if held:
            entry["reason"] = ("held as protected: never filed automatically; "
                               "file it yourself with --file-held")
        elif tree is None:
            schema = row["type_schema"]
            entry["bucket"] = (names.get(schema, schema) if schema
                               else "Not recognised yet")
        else:
            d = tree["by_file"].get(row["file_id"])
            if d is None:
                entry["outcome"] = None
                entry["reason"] = (
                    PLACE_THE_FILES if not tree["by_file"] else
                    "the sorter has no decision for this version of the file; "
                    "run database-agent <FOLDER> again")
            else:
                entry["outcome"] = d.outcome
                entry["decision_id"] = d.decision_id
                entry["why"] = d.explanation
                if d.outcome == "place" and d.destination is not None:
                    entry["destination"] = tree["path"](d.destination.node_id)
                    entry["move_plan_id"] = tree["moves"].get(row["file_id"])
                else:
                    entry["reason"] = d.abstention_reason or d.outcome
                    if d.ask is not None:
                        entry["question"] = d.ask.question
        files.append(entry)
    out = {"ok": True, "moved": False, "files": files}
    if tree is None:
        out.update(source="type_buckets", next_step=RUN_THE_SORTER)
    else:
        out.update(source="sorter_tree", plan_version=tree["version"])
    return out


def _type_names() -> dict[str, str]:
    """The recognition library's own name for each type, keyed by schema id."""
    from recognition.rules import load_rules
    manifest = (Path(__file__).resolve().parents[1] / "recognition" / "library"
                / "recognition.json")
    rules = load_rules(manifest.read_text)
    return {k: getattr(s, "name", None) or k for k, s in rules.schemas.items()}


def propose_links(conn: sqlite3.Connection, *, limit: int = 20) -> dict[str, Any]:
    if not _table(conn, "relationships"):
        return {"ok": True, "links": [], "moved": False, "note": "no relationships"}
    from items.connector import propose_inferred_links
    before = conn.execute(
        "SELECT COUNT(*) FROM relationships WHERE state='proposed'"
    ).fetchone()[0]
    try:
        n = propose_inferred_links(conn)
    except Exception as e:
        return {"ok": False, "error": str(e), "moved": False}
    rows = conn.execute(
        "SELECT relationship_id, rel_type, from_item_id, to_item_id, state "
        "FROM relationships WHERE state='proposed' AND superseded_by IS NULL "
        "ORDER BY rowid DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return {
        "ok": True,
        "new_or_seen": n if isinstance(n, int) else True,
        "proposed_before": before,
        "links": [dict(r) for r in rows],
        "moved": False,
    }


def accept_link(
        conn: sqlite3.Connection, relationship_id: str,
        *, user_id: str = "local-user") -> dict[str, Any]:
    from items.decisions import accept_link as _accept
    try:
        # DiffEvent captured inside decisions.accept_link.
        result = _accept(conn, relationship_id, user_id=user_id)
        return {"ok": True, "relationship_id": relationship_id,
                "state": result.get("state") or "approved",
                "decision_id": result.get("decision_id"),
                "moved": False}
    except Exception as e:
        return {"ok": False, "error": str(e), "moved": False}


def reject_link(
        conn: sqlite3.Connection, relationship_id: str,
        *, user_id: str = "local-user") -> dict[str, Any]:
    from items.decisions import reject_link as _reject
    try:
        # DiffEvent captured inside decisions.reject_link (atoms stay dark).
        result = _reject(conn, relationship_id, user_id=user_id)
        return {"ok": True, "relationship_id": relationship_id,
                "state": result.get("state") or "rejected",
                "decision_id": result.get("decision_id"),
                "moved": False}
    except Exception as e:
        return {"ok": False, "error": str(e), "moved": False}


def freeze_plan(conn: sqlite3.Connection, plan_id: str) -> dict[str, Any]:
    """Mark draft plan frozen for approval — does not move files."""
    try:
        row = conn.execute(
            "SELECT state FROM assistant_plans WHERE plan_id=?", (plan_id,)
        ).fetchone()
    except sqlite3.OperationalError:
        return {"ok": False, "error": "plan not found", "moved": False}
    if row is None:
        return {"ok": False, "error": "plan not found", "moved": False}
    if row["state"] not in ("draft", "approved"):
        return {
            "ok": False,
            "error": f"cannot freeze from state {row['state']!r}",
            "moved": False,
        }
    # Freeze = ready for full-list view / approve; stay draft until approve.
    return {
        "ok": True,
        "plan_id": plan_id,
        "frozen": True,
        "state": row["state"],
        "moved": False,
        "note": "View full list then approve_plan before apply_moves",
    }


def extract_one(
        conn: sqlite3.Connection, item_id: str, *,
        allow_held: bool = False,
) -> dict[str, Any]:
    from items.file_identity import path_is_protected

    row = conn.execute(
        "SELECT item_id, display_label, file_id, open_target, typing_state "
        "FROM items WHERE item_id=? AND presence='live'",
        (item_id,),
    ).fetchone()
    if row is None:
        return {"ok": False, "error": "item not found", "moved": False}
    protected = bool(
        row["open_target"] and path_is_protected(row["open_target"]))
    held = row["typing_state"] == "held" or protected
    if held and not allow_held:
        return {
            "ok": False,
            "item_id": item_id,
            "refused": True,
            "error": "extract_one refused for held/protected item",
            "moved": False,
        }
    return {
        "ok": True,
        "item_id": item_id,
        "display_label": row["display_label"],
        "typing_state": row["typing_state"],
        "open_target": (
            None if (held and not allow_held) else row["open_target"]
        ),
        "moved": False,
        "trust": "UNTRUSTED_LABEL",
        "note": "metadata only — use read_item for untrusted snippet",
    }


def _table(conn, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone() is not None
