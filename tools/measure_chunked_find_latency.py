#!/usr/bin/env python3
"""Latency on REAL files with long bodies → item_chunks (not padded empty rows).

Default: 500 files × ~4KB body. Use --body-kb 40 for PDF-like chunk blowup
(×10–50 vs label-only). Optional --files 2000.
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


def _body(kb: int) -> str:
    unit = "probability lecture notes conditioning joint pmf pdf page. "
    # ~50 chars/unit → ~20 units/KB
    n = max(1, kb * 20)
    return unit * n


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--files", type=int, default=500)
    p.add_argument("--body-kb", type=int, default=4,
                   help="Approx body size in KB (PDF-like: try 20–40)")
    p.add_argument("--rounds", type=int, default=6)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)
    BODY = _body(args.body_kb)

    from database_agent.db import open_database
    from items.hot_index import find_files, rebuild_fts
    from items.identity import reconcile_tree
    from items.schema import create_items_schema

    with tempfile.TemporaryDirectory(prefix="ga-chunk-") as td:
        root = Path(td) / "lib"
        root.mkdir()
        for i in range(args.files):
            name = f"doc_{i:04d}.txt"
            if i % 25 == 0:
                name = f"作業_{i:04d}.txt"
            (root / name).write_text(BODY + f" id={i}", encoding="utf-8")
        db = Path(td) / "t.sqlite"
        conn = open_database(db, scan_roots=[])
        create_items_schema(conn)
        # Put bodies into evidence so rebuild_fts chunks them
        conn.execute(
            "CREATE TABLE IF NOT EXISTS evidence ("
            "evidence_id TEXT PRIMARY KEY, file_id TEXT, raw_value TEXT, "
            "superseded_by TEXT)"
        )
        reconcile_tree(conn, root)
        for row in conn.execute(
            "SELECT item_id, file_id, display_label FROM items "
            "WHERE presence='live'"
        ):
            if not row["file_id"]:
                continue
            text = (root / row["display_label"]).read_text(encoding="utf-8")
            conn.execute(
                "INSERT INTO evidence VALUES (?,?,?,NULL)",
                (f"ev-{row['item_id']}", row["file_id"], text),
            )
        # Cap must cover full body or PDF-scale chunking is fake (default 4k).
        evidence_chars = max(args.body_kb * 1024, 4000)
        n_fts = rebuild_fts(conn, evidence_chars=evidence_chars)
        chunks = conn.execute("SELECT COUNT(*) FROM item_chunks").fetchone()[0]
        conn.commit()
        print(f"files={args.files} fts_rows={n_fts} chunks={chunks}", flush=True)

        queries = ["probability lecture", "joint pmf", "作業", "conditioning"]
        totals = []
        for q in queries:
            for _ in range(args.rounds):
                totals.append(find_files(conn, q, limit=10).total_ms)
        totals.sort()
        p50 = statistics.median(totals)
        p95 = totals[int(0.95 * (len(totals) - 1))]
        report = {
            "files": args.files,
            "body_kb": args.body_kb,
            "chunks": chunks,
            "chunks_per_file": round(chunks / max(args.files, 1), 2),
            "p50_ms": p50,
            "p95_ms": p95,
            "n_samples": len(totals),
            "kind": "real_files_with_evidence_chunks",
        }
        print(json.dumps(report, indent=2))
        if args.out:
            args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        conn.close()
        # Soft gate: 500 files with chunks should stay < 200ms p95 on M-series
        if p95 >= 500:
            print("FAIL: chunked p95 >= 500ms", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
