"""CLI: database-agent db check|backup|restore|rebuild-index."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def db_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="database-agent db")
    sub = parser.add_subparsers(dest="action", required=True)

    p_check = sub.add_parser("check")
    p_check.add_argument("--database", type=Path, required=True)

    p_bak = sub.add_parser("backup")
    p_bak.add_argument("--database", type=Path, required=True)
    p_bak.add_argument("dest", type=Path)

    p_res = sub.add_parser("restore")
    p_res.add_argument("backup", type=Path)
    p_res.add_argument("--database", type=Path, required=True,
                       help="restore target path")
    p_res.add_argument("--replace", action="store_true")

    p_reb = sub.add_parser("rebuild-index")
    p_reb.add_argument("--database", type=Path, required=True)

    args = parser.parse_args(argv)
    from database_agent import maintenance as m

    if args.action == "check":
        report = m.check_database(args.database)
        print(json.dumps(report.as_dict(), indent=2), file=out)
        return 0 if report.ok else 2
    if args.action == "backup":
        manifest = m.backup_database(args.database, args.dest)
        print(json.dumps(manifest, indent=2), file=out)
        return 0
    if args.action == "restore":
        result = m.restore_database(
            args.backup, args.database, replace=args.replace)
        print(json.dumps(result, indent=2), file=out)
        return 0 if result.get("ok") else 2
    if args.action == "rebuild-index":
        result = m.rebuild_index(args.database)
        print(json.dumps(result, indent=2), file=out)
        return 0
    return 2
