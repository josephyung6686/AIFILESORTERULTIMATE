"""`filesorter view`, `filesorter suggest`, and `search`.

None of these open a socket. Suggest never applies a move. Search is read-only.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

APPLY_REFUSED = (
    "suggest does not move files. A proposal is printed for a person to "
    "approve later. Nothing was moved."
)


def _open(path: Path, *, key_file: Path | None = None):
    from database_agent.db import open_database
    return open_database(path, scan_roots=[], encryption=key_file is not None,
                         encryption_key_file=key_file)


def view_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter view")
    parser.add_argument(
        "name", nargs="?", default="deadlines",
        choices=("deadlines", "folder", "table", "board", "timeline", "graph"),
    )
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, default=None)
    parser.add_argument("--html", type=Path, default=None)
    parser.add_argument("--center", default=None, help="item_id for graph focus")
    parser.add_argument(
        "--expect", action="append", default=[], metavar="EVENT=FILE",
        help="an event item id and a file item id expected on that deadline")
    args = parser.parse_args(argv)
    conn = _open(args.database, key_file=args.key_file)
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
    parser.add_argument("--key-file", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--rebuild-fts", action="store_true")
    args = parser.parse_args(argv)
    from items.hot_index import rebuild_fts
    from items.refresh import refresh_index
    from items.search import meaning_search
    conn = _open(args.database, key_file=args.key_file)
    try:
        try:
            refresh_index(conn, prefer_fsevents=False)
            conn.commit()
        except Exception:
            pass
        if args.rebuild_fts:
            n = rebuild_fts(conn)
            conn.commit()
            print(f"Rebuilt item_fts: {n} rows.", file=out)
        result = meaning_search(conn, args.query, limit=args.limit)
        conn.commit()
    finally:
        conn.close()
    print(
        f"{len(result.hits)} hit(s). Protected present-but-unopened: "
        f"{result.protected_count}. Moved: no. "
        f"latency fts={result.fts_ms:.1f}ms vec={result.vector_ms:.1f}ms "
        f"total={result.total_ms:.1f}ms",
        file=out)
    for hit in result.hits:
        target = "(protected)" if hit.protected else (hit.open_target or "")
        print(
            f"{hit.score:.4f}\t{hit.channel}\t{hit.display_label}\t{target}",
            file=out)
    return 0


def preview_main(argv: list[str] | None = None, *, out=None) -> int:
    """Dry-run a plan (P3). Never moves."""
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter preview-plan")
    parser.add_argument("plan_id")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, default=None)
    parser.add_argument("--full-list-viewed", action="store_true")
    args = parser.parse_args(argv)
    from assistant.place_preview import place_preview, preview_as_dict
    conn = _open(args.database, key_file=args.key_file)
    try:
        prev = place_preview(
            conn, args.plan_id, full_list_viewed=args.full_list_viewed)
        d = preview_as_dict(prev)
    finally:
        conn.close()
    print(f"plan {d['plan_id']} hash={d['plan_hash'][:12]}… "
          f"ops={len(d['ops'])} can_apply={d['can_apply']} moved=no",
          file=out)
    for op in d["ops"]:
        print(f"  {op['item_id']}: {op['src']} -> {op['dst']} "
              f"hash_ok={op['hash_ok']}", file=out)
    if d["blockers"]:
        print("blockers:", file=out)
        for b in d["blockers"]:
            print(f"  - {b}", file=out)
    return 0


def plan_main(argv: list[str] | None = None, *, out=None) -> int:
    """P4 product path: show / approve / apply / undo assistant plans."""
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter plan")
    parser.add_argument(
        "action", choices=("show", "approve", "apply", "undo", "create"))
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, default=None)
    parser.add_argument("--plan-id", default=None)
    parser.add_argument("--full-list-viewed", action="store_true")
    parser.add_argument("--item-id", default=None)
    parser.add_argument("--dst", default=None, help="destination path for create")
    args = parser.parse_args(argv)

    from assistant.apply import apply_enabled, apply_plan
    from assistant.place_preview import place_preview, preview_as_dict
    from assistant.plans import PlanOp, approve_plan, create_draft_plan, plan_hash
    from assistant.undo import undo_plan

    conn = _open(args.database, key_file=args.key_file)
    try:
        if args.action == "create":
            if not args.item_id or not args.dst:
                print("create requires --item-id and --dst", file=out)
                return 2
            row = conn.execute(
                "SELECT item_id, open_target, file_id FROM items "
                "WHERE item_id=?", (args.item_id,),
            ).fetchone()
            if row is None or not row["open_target"]:
                print("item not found or has no open_target", file=out)
                return 2
            # CLI --item-id is an explicit user pick → grounded.
            plan = create_draft_plan(
                conn,
                ops=[PlanOp(
                    item_id=row["item_id"], src=row["open_target"],
                    dst=args.dst, file_id=row["file_id"],
                )],
                require_grounded=True,
                user_picked_ids=[row["item_id"]],
            )
            conn.commit()
            print(f"created draft plan {plan.plan_id}", file=out)
            return 0

        if not args.plan_id:
            print("--plan-id required", file=out)
            return 2

        if args.action == "show":
            prev = place_preview(
                conn, args.plan_id,
                full_list_viewed=args.full_list_viewed)
            d = preview_as_dict(prev)
            print(
                f"plan {d['plan_id']} hash={d['plan_hash'][:16]}… "
                f"ops={len(d['ops'])} can_apply={d['can_apply']} "
                f"apply_env={apply_enabled()} moved=no",
                file=out)
            for op in d["ops"]:
                print(
                    f"  {op['item_id']}: {op['src']} -> {op['dst']}",
                    file=out)
            return 0

        if args.action == "approve":
            result = approve_plan(
                conn, args.plan_id,
                full_list_viewed=args.full_list_viewed)
            conn.commit()
            if not result.ok:
                print(result.error, file=out)
                return 2
            print(
                f"approved plan {args.plan_id} hash={result.plan_hash[:16]}… "
                f"moved=no",
                file=out)
            return 0

        if args.action == "apply":
            result = apply_plan(
                conn, args.plan_id,
                full_list_viewed=args.full_list_viewed)
            conn.commit()
            print(
                f"apply ok={result.ok} moved={result.moved} "
                f"applied={list(result.applied)} error={result.error}",
                file=out)
            return 0 if result.ok else 2

        if args.action == "undo":
            result = undo_plan(conn, args.plan_id)
            conn.commit()
            print(
                f"undo ok={result.ok} moved={result.moved} "
                f"undone={list(result.undone)} error={result.error}",
                file=out)
            return 0 if result.ok else 2
    finally:
        conn.close()
    return 2


def ask_main(argv: list[str] | None = None, *, out=None) -> int:
    """BYOK read-only chat over the local index. Product surface."""
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter ask")
    parser.add_argument("question", nargs="?", default=None)
    parser.add_argument("--database", type=Path, default=None)
    parser.add_argument("--key-file", type=Path, default=None)
    parser.add_argument("--rebuild-fts", action="store_true")
    parser.add_argument(
        "--show-trust", action="store_true",
        help="Print per-provider retention/location facts (Addendum A4).")
    parser.add_argument(
        "--local-only", action="store_true",
        help="No cloud: answer find questions from the hybrid index. "
             "Apple FM generation is used when available (not wired yet).")
    parser.add_argument(
        "--show-local-capability", action="store_true",
        help="Print Apple FM / index-find capability probe and exit.")
    args = parser.parse_args(argv)
    from assistant.chat import ask, format_answer
    from assistant.local_model import capability_lines
    from assistant.trust import onboarding_lines
    from items.hot_index import rebuild_fts
    if args.show_local_capability:
        for line in capability_lines():
            print(line, file=out)
        return 0
    if args.show_trust:
        for line in onboarding_lines("deepseek"):
            print(line, file=out)
        if not args.question:
            return 0
    if not args.question or args.database is None:
        parser.error("question and --database are required "
                     "(unless --show-local-capability / --show-trust alone)")
    conn = _open(args.database, key_file=args.key_file)
    try:
        try:
            from items.refresh import refresh_index
            refresh_index(conn, prefer_fsevents=False)
            conn.commit()
        except Exception:
            pass
        if args.rebuild_fts:
            n = rebuild_fts(conn)
            conn.commit()
            print(f"Rebuilt item_fts: {n} rows.", file=out)
        try:
            answer = ask(conn, args.question, local_only=args.local_only)
        except RuntimeError as problem:
            # Missing BYOK key / provider config — refuse cleanly, move nothing.
            print(str(problem), file=out)
            return 2
        conn.commit()
    finally:
        conn.close()
    print(format_answer(answer), file=out)
    # Local-only refuse is a clean product outcome (exit 0) with moved=no.
    if args.local_only and answer.provider == "local" and not answer.citations:
        return 0
    return 0


def suggest_main(argv: list[str] | None = None, *, out=None) -> int:
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter suggest")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, default=None)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if args.apply:
        print(APPLY_REFUSED, file=out)
        return 2
    from items.nudge import render
    from items.suggest import proposals
    conn = _open(args.database, key_file=args.key_file)
    try:
        rows = proposals(conn)
        text = render(rows)
    finally:
        conn.close()
    print(text, file=out)
    return 0


def watch_main(argv: list[str] | None = None, *, out=None) -> int:
    """Background watcher: FSEvents/polling → reconcile → FTS. Never moves."""
    out = out if out is not None else sys.stdout
    parser = argparse.ArgumentParser(prog="filesorter watch")
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--key-file", type=Path, default=None)
    parser.add_argument(
        "--root", type=Path, action="append", default=None,
        help="Root to watch (repeatable). Default: infer from DB paths.")
    parser.add_argument(
        "--seconds", type=float, default=0.0,
        help="Run this many seconds then exit (0 = until Ctrl-C).")
    parser.add_argument(
        "--interval", type=float, default=1.0,
        help="Polling tick interval seconds.")
    args = parser.parse_args(argv)
    import time
    from items.path_watch import PathWatcher
    from items.refresh import discover_roots

    conn = _open(args.database, key_file=args.key_file)
    roots = list(args.root) if args.root else discover_roots(conn)
    if not roots:
        print("No watch roots found.", file=out)
        conn.close()
        return 2
    watchers = [PathWatcher(r) for r in roots]
    for w in watchers:
        w.ensure_best_backend()
        w.scan_events()
    print(
        f"watching {len(watchers)} root(s) backend={watchers[0].backend} "
        f"moved=no",
        file=out,
    )
    started = time.monotonic()
    try:
        while True:
            for w in watchers:
                result = w.tick(conn)
                if result.reindexed:
                    conn.commit()
                    print(
                        f"tick accepted={result.accepted} "
                        f"renames={result.renames_followed} "
                        f"backend={result.backend}",
                        file=out,
                    )
            if args.seconds and (time.monotonic() - started) >= args.seconds:
                break
            time.sleep(max(0.1, args.interval))
    except KeyboardInterrupt:
        print("watch stopped.", file=out)
    finally:
        for w in watchers:
            w.stop_live()
        conn.close()
    return 0
