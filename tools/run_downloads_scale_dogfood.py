#!/usr/bin/env python3
"""Real Downloads-copy scale dogfood: find latency + optional live ask.

Uses GA_PERFECT_DB (/tmp/ga-500.sqlite) and GA_PERFECT_COPY (/tmp/ga-500-copy).
Never moves originals.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--db", type=Path,
        default=Path(os.environ.get("GA_PERFECT_DB", "/tmp/ga-500.sqlite")))
    p.add_argument(
        "--copy", type=Path,
        default=Path(os.environ.get("GA_PERFECT_COPY", "/tmp/ga-500-copy")))
    p.add_argument(
        "--out", type=Path,
        default=ROOT / "docs/superpowers/measurements/"
        "2026-10-02-downloads-scale-dogfood.json")
    p.add_argument("--live-ask", action="store_true")
    args = p.parse_args(argv)

    if not args.db.is_file():
        print(f"FAIL: missing db {args.db}", file=sys.stderr)
        return 2

    from database_agent.db import open_database
    from items.hot_index import find_files, rebuild_fts
    from items.identity import reconcile_tree
    from assistant.local_model import capability_lines

    conn = open_database(args.db, scan_roots=[])
    n_items = conn.execute(
        "SELECT COUNT(*) AS n FROM items WHERE presence='live'"
    ).fetchone()["n"]
    if args.copy.is_dir():
        reconcile_tree(conn, args.copy)
    n_fts = rebuild_fts(conn, evidence_chars=8000)
    chunks = 0
    try:
        chunks = conn.execute("SELECT COUNT(*) FROM item_chunks").fetchone()[0]
    except Exception:
        pass
    conn.commit()

    queries = [
        "Joint PMFs", "resume", "作業", "Conditioning", "Columbia", "稅務",
    ]
    samples = []
    hits_ok = {}
    for q in queries:
        times = []
        last_hits = []
        for _ in range(5):
            r = find_files(conn, q, limit=8)
            times.append(r.total_ms)
            last_hits = [h.display_label for h in r.hits[:3]]
        samples.extend(times)
        hits_ok[q] = {"p50_ms": statistics.median(times), "top": last_hits}

    samples.sort()
    p50 = statistics.median(samples)
    p95 = samples[int(0.95 * (len(samples) - 1))]

    live = None
    if args.live_ask:
        from assistant.chat import ask
        from assistant.provider import load_dotenv
        load_dotenv(ROOT / ".env")
        t0 = time.perf_counter()
        ans = ask(conn, "Where is the Joint PMFs PDF?", session_id="dl-dogfood")
        live = {
            "provider": ans.provider,
            "model": ans.model,
            "citations": list(ans.citations),
            "moved": ans.moved,
            "ms": (time.perf_counter() - t0) * 1000,
            "text_head": (ans.text or "")[:240],
        }

    report = {
        "db": str(args.db),
        "copy": str(args.copy) if args.copy.is_dir() else None,
        "n_live_items": n_items,
        "fts_rows": n_fts,
        "chunks": chunks,
        "find_p50_ms": p50,
        "find_p95_ms": p95,
        "n_samples": len(samples),
        "per_query": hits_ok,
        "capability": capability_lines(),
        "live_ask": live,
        "kind": "downloads_copy_scale",
        "ok": p95 < 500 and n_items >= 100,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        k: report[k] for k in (
            "ok", "n_live_items", "chunks", "find_p50_ms", "find_p95_ms",
        )
    }, indent=2))
    print(f"wrote {args.out}")
    conn.close()
    return 0 if report["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
