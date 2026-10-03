#!/usr/bin/env python3
"""Supervised daily-use pilot (T12) — cloud/memory/apply off by default."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--database", type=Path, required=True)
    p.add_argument("--copy", type=Path, required=True)
    p.add_argument("--cloud", choices=("off", "on"), default="off")
    p.add_argument("--memory-steering", choices=("off", "on"), default="off")
    p.add_argument("--apply", choices=("off", "on"), default="off")
    p.add_argument("--out", type=Path, default=ROOT /
                   "docs/superpowers/measurements/daily-use-pilot.json")
    args = p.parse_args(argv)

    if args.cloud == "off":
        os.environ.pop("DEEPSEEK_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)
    if args.memory_steering == "off":
        os.environ["ASSISTANT_ATOMS_STEER"] = "0"
    if args.apply == "off":
        os.environ.pop("ASSISTANT_ENABLE_APPLY", None)

    from database_agent.db import open_database
    from database_agent.maintenance import check_database, backup_database
    from items.hot_index import find_files, rebuild_fts
    from items.identity import reconcile_tree
    from items.refresh import refresh_index
    from items.schema import create_items_schema

    args.copy.mkdir(parents=True, exist_ok=True)
    sample = args.copy / "pilot-note.txt"
    if not sample.exists():
        sample.write_text("pilot marker Joint PMFs homework", encoding="utf-8")

    conn = open_database(args.database, scan_roots=[])
    create_items_schema(conn)
    reconcile_tree(conn, args.copy)
    rebuild_fts(conn)
    refresh_index(conn, prefer_fsevents=False)
    conn.commit()

    # edit + rename
    sample.write_text("pilot marker edited", encoding="utf-8")
    renamed = args.copy / "pilot-note-renamed.txt"
    sample.rename(renamed)
    refresh_index(conn, prefer_fsevents=False)
    rebuild_fts(conn)
    conn.commit()

    hits = find_files(conn, "pilot", limit=5)
    conn.close()

    check = check_database(args.database)
    bak_dir = Path(tempfile.mkdtemp())
    bak = bak_dir / "pilot.bak.sqlite"
    backup_database(args.database, bak)

    report = {
        "ok": check.ok and any(
            "pilot" in (h.display_label or "").lower() for h in hits.hits
        ),
        "check": check.as_dict(),
        "find_hits": [h.display_label for h in hits.hits],
        "backup": str(bak),
        "cloud": args.cloud,
        "memory_steering": args.memory_steering,
        "apply": args.apply,
        "connectors": "scratched",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
