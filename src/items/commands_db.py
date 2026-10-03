"""CLI: database-agent db check|backup|restore|rebuild-index."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def db_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="database-agent db")
    sub = parser.add_subparsers(dest="action", required=True)

    p_check = sub.add_parser("check")
    p_check.add_argument("--database", type=Path, default=None)
    p_check.add_argument("--key-file", type=Path, help="owner-only SQLCipher key file")

    p_bak = sub.add_parser("backup")
    p_bak.add_argument("--database", type=Path, default=None)
    p_bak.add_argument("--key-file", type=Path, help="owner-only SQLCipher key file")
    p_bak.add_argument("dest", type=Path)

    p_res = sub.add_parser("restore")
    p_res.add_argument("backup", type=Path)
    p_res.add_argument("--database", type=Path, default=None,
                       help="restore target path")
    p_res.add_argument("--replace", action="store_true")
    p_res.add_argument("--key-file", type=Path, help="owner-only SQLCipher key file")

    p_reb = sub.add_parser("rebuild-index")
    p_reb.add_argument("--database", type=Path, default=None)
    p_reb.add_argument("--key-file", type=Path, help="owner-only SQLCipher key file")

    p_enc = sub.add_parser("encrypt", help="copy plaintext DB to a new encrypted destination")
    p_enc.add_argument("source", type=Path)
    p_enc.add_argument("--database", type=Path, required=True,
                       help="new encrypted destination; source is preserved")
    p_enc.add_argument("--key-file", type=Path, required=True)

    args = parser.parse_args(argv)
    if args.key_file is None and os.environ.get("DATABASE_AGENT_KEY_FILE"):
        args.key_file = Path(os.environ["DATABASE_AGENT_KEY_FILE"])
    from database_agent import maintenance as m
    from database_agent.db import shared_database_path
    from database_agent.encryption import read_key_file
    if args.action != "encrypt" and args.database is None:
        args.database = shared_database_path()
    if args.action in ("check", "backup", "rebuild-index"):
        from items.commands import NOTHING_INDEXED
        if not args.database.is_file():
            print(NOTHING_INDEXED, file=out)
            return 2

    if args.action == "check":
        report = m.check_database(
            args.database,
            encryption_key=read_key_file(args.key_file) if args.key_file else None)
        payload = report.as_dict()
        if report.ok:
            from items.commands import _open, counts_line
            conn = _open(args.database, key_file=args.key_file)
            try:
                payload["summary"] = counts_line(conn)
            finally:
                conn.close()
        print(json.dumps(payload, indent=2), file=out)
        return 0 if report.ok else 2
    if args.action == "backup":
        manifest = m.backup_database(
            args.database, args.dest,
            encryption_key=read_key_file(args.key_file) if args.key_file else None)
        print(json.dumps(manifest, indent=2), file=out)
        return 0
    if args.action == "restore":
        try:
            result = m.restore_database(
                args.backup, args.database, replace=args.replace,
                encryption_key=read_key_file(args.key_file) if args.key_file else None)
        except FileExistsError:
            print(f"{args.database} already exists; nothing was changed. "
                  "Pass --replace to restore over it.", file=out)
            return 2
        except FileNotFoundError:
            print(f"backup not found: {args.backup}; nothing was changed.", file=out)
            return 2
        print(json.dumps(result, indent=2), file=out)
        return 0 if result.get("ok") else 2
    if args.action == "rebuild-index":
        result = m.rebuild_index(
            args.database,
            encryption_key=read_key_file(args.key_file) if args.key_file else None)
        print(json.dumps(result, indent=2), file=out)
        return 0
    if args.action == "encrypt":
        from database_agent.encryption import key_from_file, migrate_plaintext
        source = args.source.expanduser().resolve()
        destination = args.database.expanduser().resolve()
        if source == destination:
            print("encrypt requires a new destination; source was preserved", file=out)
            return 2
        if not source.is_file():
            print(f"source database does not exist: {source}", file=out)
            return 2
        if destination.exists():
            print(f"destination already exists: {destination}; nothing was overwritten", file=out)
            return 2
        key = key_from_file(args.key_file)
        migrate_plaintext(source, destination, key)
        print(json.dumps({"source": str(source), "destination": str(destination),
                          "encrypted": True, "source_preserved": True}, indent=2), file=out)
        return 0
    return 2
