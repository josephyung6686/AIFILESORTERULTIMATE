"""P1 latency smoke — absolute p95 caps on tiny synthetic corpus.

Full 50k/250k measurement is nightly; this guards catastrophic regressions.
"""
from __future__ import annotations

import statistics
from pathlib import Path

from items.hot_index import find_files, rebuild_fts
from items.identity import reconcile_tree
from items.schema import create_items_schema

# Absolute caps for ≤2k items (T-P1-02 starting proposal). Soft on CI machines
# that are heavily loaded — fail only if p95 is wildly over.
P95_CAP_MS_2K = 80.0
P95_HARD_FAIL_MS = 500.0  # anything above this on tiny corpus is broken


def test_find_latency_tiny_corpus(conn, tmp_path: Path):
    root = tmp_path / "lib"
    root.mkdir()
    for i in range(200):
        (root / f"file_{i:04d}.txt").write_text(
            f"document number {i} probability lecture notes", encoding="utf-8")
    create_items_schema(conn)
    reconcile_tree(conn, root)
    rebuild_fts(conn)

    samples = []
    for _ in range(20):
        result = find_files(conn, "probability lecture", limit=10)
        assert result.moved is False
        samples.append(result.total_ms)
    samples.sort()
    p95 = samples[int(0.95 * (len(samples) - 1))]
    assert p95 < P95_HARD_FAIL_MS, f"p95={p95:.1f}ms broken on 200 files"
    # Record soft target for logs; do not fail CI on load spikes under hard cap.
    _ = P95_CAP_MS_2K
    assert statistics.median(samples) < P95_HARD_FAIL_MS
