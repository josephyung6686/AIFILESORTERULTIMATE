#!/usr/bin/env python3
"""Run a supervised pilot against a disposable copy of a corpus.

The source corpus is never modified. Cloud calls, learned steering, and moves
are opt-in and default off; the release runbook uses all three safe defaults.
"""
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


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--database", type=Path, required=True)
    p.add_argument("--corpus", "--copy", dest="corpus", type=Path,
                   help="source corpus; it is copied into a disposable temp directory")
    p.add_argument("--cloud", choices=("off", "on"), default="off")
    p.add_argument("--memory-steering", choices=("off", "on"), default="off")
    p.add_argument("--apply", choices=("off", "on"), default="off")
    p.add_argument("--out", type=Path, default=ROOT / "docs/superpowers/measurements/daily-use-pilot.json")
    return p


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    if args.cloud == "off":
        for key in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            os.environ.pop(key, None)
        os.environ["ASSISTANT_LOCAL_ONLY"] = "1"
    if args.memory_steering == "off":
        os.environ["ASSISTANT_ATOMS_STEER"] = "0"
    if args.apply == "off":
        os.environ.pop("ASSISTANT_ENABLE_APPLY", None)

    with tempfile.TemporaryDirectory(prefix="database-agent-pilot-") as temp:
        temp_root = Path(temp)
        work = temp_root / "corpus"
        if args.corpus:
            source = args.corpus.expanduser().resolve()
            if not source.is_dir():
                raise SystemExit(f"corpus must be a directory: {source}")
            shutil.copytree(source, work)
        else:
            work.mkdir()
            (work / "pilot-note.txt").write_text("pilot marker Joint PMFs homework", encoding="utf-8")
        db = args.database.expanduser().resolve()
        from database_agent.db import open_database
        from database_agent.maintenance import backup_database, check_database
        from items.hot_index import find_files, rebuild_fts
        from items.identity import reconcile_tree
        from items.refresh import refresh_index
        from items.schema import create_items_schema

        conn = open_database(db, scan_roots=[])
        create_items_schema(conn)
        reconcile_tree(conn, work)
        rebuild_fts(conn)
        refresh_index(conn, prefer_fsevents=False)
        conn.commit()
        marker = work / "pilot-note.txt"
        if marker.exists():
            marker.write_text("pilot marker edited", encoding="utf-8")
            marker.rename(work / "pilot-note-renamed.txt")
        refresh_index(conn, prefer_fsevents=False)
        rebuild_fts(conn)
        conn.commit()
        hits = find_files(conn, "pilot", limit=5)
        conn.close()
        check = check_database(db)
        backup = temp_root / "pilot-backup.sqlite"
        backup_database(db, backup)
        report = {
            "schema": "daily-use-pilot/v1", "ok": check.ok and bool(hits.hits),
            "corpus": {"source": str(args.corpus) if args.corpus else "generated", "copied": True, "workdir": str(work)},
            "check": check.as_dict(), "find_hits": [h.display_label for h in hits.hits],
            "backup_created": backup.is_file(), "cloud": args.cloud,
            "memory_steering": args.memory_steering, "apply": args.apply,
            "connectors": "scratched", "ui": "excluded",
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
