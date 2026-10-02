"""`filesorter sync`, `filesorter view`, `filesorter suggest`, and `search`.

None of these open a socket. Sync without a local fixture stores nothing.
Suggest never applies a move. Search is read-only.
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
    parser.add_argument(
        "name", nargs="?", default="deadlines",
        choices=("deadlines", "folder", "table", "board", "timeline", "graph"),
    )
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--html", type=Path, default=None)
    parser.add_argument("--center", default=None, help="item_id for graph focus")
    parser.add_argument(
        "--expect", action="append", default=[], metavar="EVENT=FILE",
        help="an event item id and a file item id expected on that deadline")
    args = parser.parse_args(argv)
    conn = _open(args.database)
    try:
        if args.name == "deadlines":
            expected: dict[str, list[str]] = {}
            for pair in args.expect:
                event, separator, file_id = pair.partition("=")
                if not event or not separator or not file_id:
                    print(f"{pair!r} is not EVENT=FILE.", file=out)
                    return 2
                expected.setdefault(event, []).append(file_id)
            from items.deadline_view import deadline_view, render_html, render_text
            view = deadline_view(conn, expected=expected)
            print(render_text(view), file=out)
            if args.html is not None:
                args.html.parent.mkdir(parents=True, exist_ok=True)
                args.html.write_text(render_html(view), encoding="utf-8")
                print(f"HTML: {args.html}", file=out)
            return 0
        from items import views as item_views
        if args.name == "folder":
            rows = item_views.folder_view(conn)
            for row in rows:
                print(f"{row['parent']}\t{row['display_label']}\t{row['open_target']}",
                      file=out)
        elif args.name == "table":
            for row in item_views.table_view(conn):
                print(
                    f"{row['item_type']}\t{row['display_label']}\t"
                    f"{row['typing_state']}\t{row['approved_links']}",
                    file=out)
        elif args.name == "board":
            board = item_views.board_view(conn)
            for column, cards in board.items():
                print(f"## {column} ({len(cards)})", file=out)
                for card in cards:
                    print(f"  - {card['display_label']}", file=out)
        elif args.name == "timeline":
            for row in item_views.timeline_view(conn):
                print(f"{row['happened_at']}\t{row['display_label']}", file=out)
        else:
            graph = item_views.graph_view(conn, center_item_id=args.center)
            print(
                f"nodes={len(graph.nodes)} edges={len(graph.edges)} "
                f"hidden={graph.hidden_count} cap={graph.cap}",
                file=out)
            for node in graph.nodes:
                print(f"N\t{node['item_id']}\t{node['display_label']}", file=out)
            for edge in graph.edges:
                print(
                    f"E\t{edge['rel_type']}\t{edge['from_item_id']}\t"
                    f"{edge['to_item_id']}\t{edge['state']}",
                    file=out)
    finally:
        conn.close()
    return 0


def search_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter search")
    parser.add_argument("query")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args(argv)
    from items.search import meaning_search
    conn = _open(args.database)
    try:
        result = meaning_search(conn, args.query, limit=args.limit)
    finally:
        conn.close()
    print(
        f"{len(result.hits)} hit(s). Protected present-but-unopened: "
        f"{result.protected_count}. Moved: no.",
        file=out)
    for hit in result.hits:
        target = "(protected)" if hit.protected else (hit.open_target or "")
        print(
            f"{hit.score:.1f}\t{hit.channel}\t{hit.display_label}\t{target}",
            file=out)
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
