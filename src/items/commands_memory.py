"""CLI: database-agent memory release|status."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def memory_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="database-agent memory")
    sub = parser.add_subparsers(dest="action", required=True)

    p_rel = sub.add_parser(
        "release",
        help="Print gate evidence; --enable deliberately opens atom steering",
    )
    p_rel.add_argument("--database", type=Path, default=None)
    p_rel.add_argument("--key-file", type=Path, default=None)
    p_rel.add_argument(
        "--fixture", type=Path, default=None,
        help="Optional gate fixture to evaluate and record",
    )
    p_rel.add_argument(
        "--enable", action="store_true",
        help="Deliberate enable of a release (default remains dark)",
    )
    p_rel.add_argument("--release-id", default=None)
    p_rel.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Print machine-readable status",
    )

    p_status = sub.add_parser("status")
    p_status.add_argument("--database", type=Path, default=None)
    p_status.add_argument("--key-file", type=Path, default=None)
    p_status.add_argument("--json", action="store_true", dest="as_json")

    args = parser.parse_args(argv)
    from assistant.memory_release import (
        enable_release,
        format_gate_evidence,
        latest_release,
        release_status,
        run_gate_from_fixture,
    )

    from database_agent.db import open_database, shared_database_path
    from items.commands import NOTHING_INDEXED

    path = args.database or shared_database_path()
    if not path.expanduser().exists():
        print(NOTHING_INDEXED, file=out)
        return 2
    conn = open_database(path, scan_roots=[],
                         encryption_key_file=args.key_file,
                         encryption=args.key_file is not None)
    try:
        if args.action == "status":
            status = release_status(conn)
            if args.as_json:
                print(json.dumps(status, indent=2), file=out)
            else:
                print(format_gate_evidence(status), file=out)
            return 0

        if args.action == "release":
            if args.fixture is not None:
                result, gate_id, release = run_gate_from_fixture(
                    conn, args.fixture)
                conn.commit()
                print(
                    f"gate recorded id={gate_id} passed={result.passed} "
                    f"precision={result.precision:.3f} "
                    f"coverage={result.coverage:.3f}",
                    file=out,
                )
                if release is not None:
                    print(
                        f"release created (dark) id={release.release_id} "
                        f"corpus={release.corpus_hash[:16]}…",
                        file=out,
                    )
                else:
                    print("no release created — gate did not pass", file=out)

            status = release_status(conn)
            if args.as_json and not args.enable:
                print(json.dumps(status, indent=2), file=out)
            else:
                print(format_gate_evidence(status), file=out)

            if args.enable:
                rid = args.release_id
                if not rid:
                    latest = latest_release(conn)
                    if latest is None:
                        print(
                            "no release to enable — run with --fixture first "
                            "or pass --release-id",
                            file=out,
                        )
                        return 2
                    rid = latest.release_id
                result = enable_release(conn, rid, deliberate=True)
                conn.commit()
                print(json.dumps(result, indent=2), file=out)
                return 0 if result.get("ok") else 2

            # Default: print evidence, stay dark.
            return 0 if not args.fixture else (
                0 if status.get("latest_release") else 2
            )
    finally:
        conn.close()
    return 2
