#!/usr/bin/env python3
"""Measure hybrid find latency on a real database. Product SLO, not pytest."""
from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--rebuild-fts", action="store_true")
    parser.add_argument("--rounds", type=int, default=8)
    args = parser.parse_args(argv)

    from database_agent.db import open_database
    from items.hot_index import find_files, rebuild_fts

    queries = [
        "CV Joseph resume",
        "Joint PMFs probability",
        "conditioning random variables",
        "suture retention PVA",
        "Independence lecture",
        "annual report",
        "stroke patient transfer",
        "YUNG HAUHONGJOSEPHMR",
    ]
    conn = open_database(args.database, scan_roots=[])
    try:
        if args.rebuild_fts:
            n = rebuild_fts(conn)
            conn.commit()
            print(f"Rebuilt FTS: {n} rows")
        # Warm once
        find_files(conn, queries[0], limit=10)
        totals = []
        fts = []
        vec = []
        print("query\ttotal_ms\tfts_ms\tvec_ms\thits\tfts\tvec")
        for q in queries:
            samples = []
            for _ in range(args.rounds):
                r = find_files(conn, q, limit=10)
                samples.append(r)
            # last sample for channels; median of totals
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
        cold = find_files(conn, "probability conditioning lecture notes", limit=10)
        print("---")
        print(
            f"overall p50={statistics.median(totals):.1f}ms "
            f"p95={_pct(totals, 95):.1f}ms "
            f"fts_p50={statistics.median(fts):.1f}ms "
            f"vec_p50={statistics.median(vec):.1f}ms "
            f"n={len(totals)}"
        )
        print(
            f"spot_check hits={len(cold.hits)} "
            f"total={cold.total_ms:.1f}ms "
            f"top={[h.display_label for h in cold.hits[:3]]}"
        )
        conn.commit()
    finally:
        conn.close()
    return 0


def _pct(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((p / 100.0) * (len(ordered) - 1)))))
    return ordered[idx]


if __name__ == "__main__":
    raise SystemExit(main())
