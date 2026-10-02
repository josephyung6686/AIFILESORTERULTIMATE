#!/usr/bin/env python3
"""Build synthetic corpus and print p50/p95 at N in {2000, 50000}.

Does not require a pre-existing DB. Writes a short JSON report.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def build(conn, root: Path, n: int) -> None:
    """Seed a small real tree, then pad items+FTS in-DB (fast path for 50k/250k)."""
    import uuid
    from items.identity import reconcile_tree
    from items.hot_index import ensure_fts, rebuild_fts
    from items.schema import create_items_schema

    root.mkdir(parents=True, exist_ok=True)
    seed_n = min(n, 200)
    for i in range(seed_n):
        name = f"doc_{i:06d}.txt"
        if i % 20 == 0:
            name = f"作業_{i:06d}.txt"
        (root / name).write_text(
            f"document {i} probability lecture", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    live = conn.execute(
        "SELECT COUNT(*) FROM items WHERE presence='live'"
    ).fetchone()[0]
    # Pad remaining rows without creating 250k files on disk.
    while live < n:
        item_id = str(uuid.uuid4())
        label = f"pad_doc_{live:06d}.txt"
        if live % 20 == 0:
            label = f"作業_pad_{live:06d}.txt"
        conn.execute(
            "INSERT INTO items ("
            "item_id, item_type, display_label, file_id, open_target, "
            "external_key, presence, typing_state, type_schema, profile_id, "
            "created_at, superseded_by) VALUES ("
            "?,?,?,NULL,NULL,NULL,'live','unplaced',NULL,NULL,"
            "datetime('now'),NULL)",
            (item_id, "file", label),
        )
        live += 1
    rebuild_fts(conn)
    ensure_fts(conn)
    conn.commit()


def measure(conn, rounds: int = 6) -> dict:
    from items.hot_index import find_files
    queries = ["probability lecture", "document 12", "作業", "missingzzz"]
    totals = []
    for q in queries:
        for _ in range(rounds):
            totals.append(find_files(conn, q, limit=10).total_ms)
    totals.sort()
    p50 = statistics.median(totals)
    p95 = totals[int(0.95 * (len(totals) - 1))]
    return {"p50_ms": p50, "p95_ms": p95, "n_samples": len(totals)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="2000", help="comma sizes e.g. 2000,50000")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)
    from database_agent.db import open_database

    report = {}
    for size_s in args.sizes.split(","):
        n = int(size_s.strip())
        with tempfile.TemporaryDirectory(prefix="ga-scale-") as td:
            root = Path(td) / "lib"
            db = Path(td) / "t.sqlite"
            conn = open_database(db, scan_roots=[])
            print(f"building n={n} …", flush=True)
            build(conn, root, n)
            live = conn.execute(
                "SELECT COUNT(*) FROM items WHERE presence='live'"
            ).fetchone()[0]
            stats = measure(conn)
            stats["live_items"] = live
            report[str(n)] = stats
            print(json.dumps({n: stats}), flush=True)
            conn.close()
    if args.out:
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    # Soft gate: 2k p95 under 800ms
    if "2000" in report and report["2000"]["p95_ms"] >= 800:
        print("FAIL: 2k p95 >= 800ms", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
