#!/usr/bin/env python3
"""Measure hybrid find latency on a real database. Product SLO, not pytest.

Also supports --scale N to clone labels into a temp DB for 2k-style stress.
"""
from __future__ import annotations

import argparse
import shutil
import statistics
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--rebuild-fts", action="store_true")
    parser.add_argument("--rounds", type=int, default=8)
    parser.add_argument(
        "--scale", type=int, default=0,
        help="If >0, copy DB and pad items to this many live rows (synthetic)",
    )
    args = parser.parse_args(argv)

    from database_agent.db import open_database
    from items.hot_index import find_files, rebuild_fts

    db_path = args.database
    tmp_dir = None
    if args.scale and args.scale > 0:
        tmp_dir = Path(tempfile.mkdtemp(prefix="ga-scale-"))
        scaled = tmp_dir / "scaled.sqlite"
        shutil.copy2(db_path, scaled)
        db_path = scaled
        _pad_items(db_path, args.scale)

    queries = [
        "CV Joseph resume",
        "Joint PMFs probability",
        "conditioning random variables",
        "suture retention PVA",
        "Independence lecture",
        "annual report",
        "stroke patient transfer",
        "YUNG HAUHONGJOSEPHMR",
        "作業",  # CJK probe when present
    ]
    conn = open_database(db_path, scan_roots=[])
    try:
        live = conn.execute(
            "SELECT COUNT(*) FROM items WHERE presence='live'"
        ).fetchone()[0]
        print(f"live_items={live} db={db_path}")
        if args.rebuild_fts or args.scale:
            n = rebuild_fts(conn)
            conn.commit()
            print(f"Rebuilt FTS: {n} rows")
        find_files(conn, queries[0], limit=10)
        totals = []
        fts = []
        vec = []
        print("query\ttotal_ms\tfts_ms\tvec_ms\thits\tfts\tvec")
        for q in queries:
            samples = [find_files(conn, q, limit=10) for _ in range(args.rounds)]
            tot = [s.total_ms for s in samples]
            ft = [s.fts_ms for s in samples]
            vt = [s.vector_ms for s in samples]
            totals.extend(tot)
            fts.extend(ft)
            vec.extend(vt)
            last = samples[-1]
            print(
                f"{q}\t{statistics.median(tot):.1f}\t"
                f"{statistics.median(ft):.1f}\t"
                f"{statistics.median(vt):.1f}\t"
                f"{len(last.hits)}\t{last.fts_used}\t{last.vector_used}"
            )
        print("---")
        print(
            f"overall p50={statistics.median(totals):.1f}ms "
            f"p95={_pct(totals, 95):.1f}ms "
            f"fts_p50={statistics.median(fts):.1f}ms "
            f"vec_p50={statistics.median(vec):.1f}ms "
            f"n={len(totals)} live={live}"
        )
        conn.commit()
    finally:
        conn.close()
        if tmp_dir is not None:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    return 0


def _pad_items(db_path: Path, target: int) -> None:
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    n = conn.execute(
        "SELECT COUNT(*) FROM items WHERE presence='live'"
    ).fetchone()[0]
    if n >= target:
        conn.close()
        return
    template = conn.execute(
        "SELECT display_label, open_target, typing_state, item_type, "
        "file_id, type_schema, profile_id FROM items "
        "WHERE presence='live' LIMIT 50"
    ).fetchall()
    if not template:
        conn.close()
        return
    i = 0
    while n < target:
        row = template[i % len(template)]
        item_id = str(uuid.uuid4())
        label = f"{row['display_label']} __pad_{n}"
        conn.execute(
            "INSERT INTO items ("
            "item_id, item_type, display_label, file_id, open_target, "
            "external_key, presence, typing_state, type_schema, profile_id, "
            "created_at, superseded_by) VALUES ("
            "?,?,?,?,?,NULL,'live',?,?,?,datetime('now'),NULL)",
            (
                item_id, row["item_type"] or "file", label, None,
                row["open_target"], row["typing_state"] or "unplaced",
                row["type_schema"], row["profile_id"],
            ),
        )
        n += 1
        i += 1
    conn.commit()
    conn.close()


def _pct(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((p / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]


if __name__ == "__main__":
    raise SystemExit(main())
