"""Embedding bake-off helpers (T-P1-01). See tools/bakeoff_embeddings_protocol.py."""
from __future__ import annotations

import json
import random
from pathlib import Path


def paired_bootstrap_ci(
        deltas: list[float], *, n_boot: int = 2000, seed: int = 0
) -> tuple[float, float, float]:
    if not deltas:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    n = len(deltas)
    means = []
    for _ in range(n_boot):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(0.025 * (n_boot - 1))]
    hi = means[int(0.975 * (n_boot - 1))]
    return sum(deltas) / n, lo, hi


def validate_golden(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    queries = data.get("queries") or []
    zh = [q for q in queries if q.get("lang") in ("zh", "zh-Hant", "zh-HK")]
    return {
        "n_queries": len(queries),
        "n_zh": len(zh),
        "ok_for_decision": len(zh) >= 100 or len(queries) >= 100,
    }
