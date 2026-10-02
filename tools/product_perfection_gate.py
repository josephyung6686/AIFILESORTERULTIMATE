#!/usr/bin/env python3
"""Non-UI / non-sorter product perfection gate on a real Downloads copy DB.

Exits 0 only if every in-scope check passes. Does not run the organize engine.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> int:
    db = Path(os.environ.get("GA_PERFECT_DB", "/tmp/ga-500.sqlite"))
    copy = Path(os.environ.get("GA_PERFECT_COPY", "/tmp/ga-500-copy"))
    fails: list[str] = []

    def ok(name: str, cond: bool, detail: str = "") -> None:
        if cond:
            print(f"OK  {name}")
        else:
            fails.append(f"{name}: {detail}")
            print(f"FAIL {name}: {detail}")

    if not db.is_file():
        print(f"FAIL database missing: {db}")
        return 2

    from database_agent.db import open_database
    from items.hot_index import find_files, rebuild_fts
    from items.path_watch import PathWatcher
    from items.fsevents_live import fsevents_available
    from items.people import mint_person
    from assistant.tools import ToolRuntime
    from assistant.memory_v2 import (
        add_atom, atoms_steering_allowed, retrieve_atoms_for_prompt,
    )
    from assistant.plans import PlanOp, create_draft_plan, approve_plan
    from assistant.apply import apply_plan
    from assistant.undo import undo_plan

    conn = open_database(db, scan_roots=[])
    try:
        n = rebuild_fts(conn)
        conn.commit()
        ok("fts_rebuild", n >= 100, f"n={n}")

        r = find_files(conn, "Joint PMFs", limit=5)
        ok("find_en", any("Joint" in h.display_label for h in r.hits),
           str([h.display_label for h in r.hits[:3]]))

        if copy.is_dir():
            from items.identity import reconcile_tree
            demo = copy / "作業講義-gate.txt"
            demo.write_text("作業講義", encoding="utf-8")
            reconcile_tree(conn, copy)
            rebuild_fts(conn)
            conn.commit()
            r2 = find_files(conn, "作業", limit=10)
            ok("find_zh", any("作業" in (h.display_label or "") for h in r2.hits))

        w = PathWatcher(root=copy if copy.is_dir() else db.parent)
        backend = w.ensure_best_backend()
        ok("fsevents_or_polling", backend in ("fsevents", "polling"), backend)
        if fsevents_available():
            ok("fsevents_live", backend == "fsevents", backend)
        w.stop_live()

        rt = ToolRuntime(conn)
        held = conn.execute(
            "SELECT item_id FROM items WHERE typing_state='held' LIMIT 1"
        ).fetchone()
        if held:
            out = rt.execute("read_item", {"item_id": held["item_id"]})
            ok("held_withhold", out.ok is False and out.payload.get("refused"))
        for name in ("apply_moves", "accept_link"):
            out = rt.execute(name, {"plan_id": "x", "relationship_id": "x"})
            ok(f"locked_{name}", out.ok is False and out.payload.get("moved") is False)

        req = rt.execute("request_tools", {"group": "organize_propose"})
        ok("request_tools", req.ok)
        tree = rt.execute("propose_tree", {})
        ok("propose_tree", tree.ok and tree.payload.get("moved") is False)

        # Atoms dark
        ok("atoms_dark", atoms_steering_allowed(conn) is False)
        add_atom(conn, claim="gate check", source_ids=["src-1"])
        ok("atoms_not_in_prompt",
           retrieve_atoms_for_prompt(conn)["atoms_steering"] is False)

        # People
        p = mint_person(conn, display_label="Gate Person", email="gate@example.com")
        ok("person_mint", bool(p.aliases))

        # Apply/undo in isolated temp (never touch Downloads originals)
        with tempfile.TemporaryDirectory() as td:
            tdp = Path(td)
            lib = tdp / "lib"
            lib.mkdir()
            src = lib / "move-me.txt"
            src.write_text("body")
            dst = tdp / "dest" / "move-me.txt"
            from items.schema import create_items_schema
            from items.identity import reconcile_tree
            c2 = open_database(tdp / "x.sqlite", scan_roots=[])
            create_items_schema(c2)
            reconcile_tree(c2, lib)
            item = c2.execute(
                "SELECT item_id, open_target, file_id FROM items "
                "WHERE display_label='move-me.txt'"
            ).fetchone()
            os.environ["ASSISTANT_ENABLE_APPLY"] = "1"
            plan = create_draft_plan(c2, ops=[PlanOp(
                item_id=item["item_id"], src=str(src.resolve()),
                dst=str(dst), file_id=item["file_id"])])
            assert approve_plan(c2, plan.plan_id, full_list_viewed=True).ok
            ap = apply_plan(c2, plan.plan_id, full_list_viewed=True)
            ok("apply", ap.ok and dst.is_file() and not src.exists(), str(ap))
            un = undo_plan(c2, plan.plan_id)
            ok("undo", un.ok and src.is_file(), str(un))
            c2.close()

        conn.commit()
    finally:
        conn.close()

    print("---")
    if fails:
        print(f"{len(fails)} FAIL(S)")
        for f in fails:
            print(f)
        return 1
    print("PRODUCT PERFECTION GATE PASSED (non-UI, non-sorter)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
