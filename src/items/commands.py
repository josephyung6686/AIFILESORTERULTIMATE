"""`filesorter sync`, `filesorter view`, and `filesorter suggest`.

None of these open a socket. Sync without a local fixture stores nothing.
Suggest never applies a move.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

NO_CREDENTIALS = (
    "No Gmail or Calendar credentials are configured. Live accounts are not "
    "connected in this build. Nothing was read and nothing was stored. "
    "Pass --fixture FILE to import a local JSON export. "
    "No network call was made."
)

APPLY_REFUSED = (
    "suggest does not move files. A proposal is printed for a person to "
    "approve later. Nothing was moved."
)


def _open(path: Path):
    from database_agent.db import open_database
    return open_database(path, scan_roots=[])


def sync_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter sync")
    parser.add_argument("kind", choices=("gmail", "calendar"))
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--fixture", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.fixture is None:
        print(NO_CREDENTIALS, file=out)
        return 0 if args.dry_run else 2
    from items.mailbox import MailboxRefused, dry_run_plan, ingest_fixture, load_fixture
    try:
        data = load_fixture(args.fixture)
        plan = dry_run_plan(data, kind=args.kind)
    except MailboxRefused as refusal:
        print(str(refusal), file=out)
        return 2
    if args.dry_run:
        print(f"Dry-run {args.kind}. Nothing was stored. No network call was made.",
              file=out)
        print(f"Would store: {plan['count']}.", file=out)
        print("Fields: " + ", ".join(plan["fields"]) + ".", file=out)
        print("Not stored: " + ", ".join(plan["not_stored"]) + ".", file=out)
        return 0
    if args.database is None:
        print("sync needs --database. Nothing was stored.", file=out)
        return 2
    conn = _open(args.database)
    try:
        result = ingest_fixture(conn, data, kind=args.kind)
    except MailboxRefused as refusal:
        print(str(refusal), file=out)
        return 2
    finally:
        conn.close()
    print(
        f"Stored {result['stored']} {args.kind} item"
        f"{'' if result['stored'] == 1 else 's'}. "
        f"Held: {result['held']}. Unplaced: {result['unplaced']}. "
        "Approved links: 0. Nothing was sent.",
        file=out)
    return 0


def view_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter view")
    parser.add_argument("name", nargs="?", default="deadlines")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--html", type=Path, default=None)
    parser.add_argument(
        "--expect", action="append", default=[], metavar="EVENT=FILE",
        help="an event item id and a file item id expected on that deadline")
    args = parser.parse_args(argv)
    if args.name != "deadlines":
        print(f"{args.name!r} is not a view. The view is deadlines.", file=out)
        return 2
    expected: dict[str, list[str]] = {}
    for pair in args.expect:
        event, separator, file_id = pair.partition("=")
        if not event or not separator or not file_id:
            print(f"{pair!r} is not EVENT=FILE.", file=out)
            return 2
        expected.setdefault(event, []).append(file_id)
    from items.deadline_view import deadline_view, render_html, render_text
    conn = _open(args.database)
    try:
        view = deadline_view(conn, expected=expected)
    finally:
        conn.close()
    print(render_text(view), file=out)
    if args.html is not None:
        args.html.parent.mkdir(parents=True, exist_ok=True)
        args.html.write_text(render_html(view), encoding="utf-8")
        print(f"HTML: {args.html}", file=out)
    return 0


def suggest_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter suggest")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.apply:
        print(APPLY_REFUSED, file=out)
        return 2
    from items.suggest import proposals, render
    conn = _open(args.database)
    try:
        rows = proposals(conn)
        text = render(rows)
    finally:
        conn.close()
    print(text, file=out)
    return 0
