"""Embedding bake-off + search quality metrics (T-P1-01 / Task 4)."""
from __future__ import annotations

import json
import math
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


def bootstrap_ci(
        values: list[float], *, n_boot: int = 2000, seed: int = 0
) -> tuple[float, float, float]:
    return paired_bootstrap_ci(values, n_boot=n_boot, seed=seed)


def validate_golden(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    queries = data.get("queries") or []
    zh = [q for q in queries if str(q.get("lang") or "").startswith("zh")]
    return {
        "n_queries": len(queries),
        "n_zh": len(zh),
        "ok_for_decision": len(zh) >= 100 or len(queries) >= 100,
    }


def recall_at_k(ranked_ids: list[str], relevant: set[str], k: int = 10) -> float:
    if not relevant:
        return 0.0
    top = set(ranked_ids[:k])
    return 1.0 if top & relevant else 0.0


def mrr(ranked_ids: list[str], relevant: set[str]) -> float:
    for i, item_id in enumerate(ranked_ids, start=1):
        if item_id in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(ranked_ids: list[str], relevant: set[str], k: int = 10) -> float:
    if not relevant:
        return 0.0
    dcg = 0.0
    for i, item_id in enumerate(ranked_ids[:k], start=1):
        if item_id in relevant:
            dcg += 1.0 / math.log2(i + 1)
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(k, len(relevant)) + 1))
    return (dcg / ideal) if ideal else 0.0


def abstention_correct(
        ranked_ids: list[str], *, negative: bool, k: int = 10,
) -> float:
    """1.0 when a negative query returns no hits in top-k (honest abstention)."""
    if not negative:
        return float("nan")
    return 1.0 if not ranked_ids[:k] else 0.0


def citation_correct(
        hit,
        *,
        require_chunk: bool = False,
        marker: str | None = None,
        conn=None,
) -> float:
    """1.0 when body claims are backed by a chunk citation (and optional marker)."""
    if hit is None:
        return 0.0
    claims_body = bool(getattr(hit, "claims_body_match", False))
    match_fields = tuple(getattr(hit, "match_fields", ()) or ())
    chunk_id = getattr(hit, "best_chunk_id", None)
    if "filename" in match_fields and not claims_body:
        # Filename-only is honest when it does not claim body.
        return 0.0 if require_chunk else 1.0
    if claims_body or require_chunk:
        if not chunk_id:
            return 0.0
        if marker and conn is not None:
            row = conn.execute(
                "SELECT text, char_start FROM item_chunks WHERE chunk_id = ?",
                (chunk_id,),
            ).fetchone()
            if row is None or marker not in (row["text"] or ""):
                return 0.0
        return 1.0
    return 1.0


def mean(xs: list[float]) -> float:
    vals = [x for x in xs if x == x]  # drop NaN
    return sum(vals) / len(vals) if vals else 0.0


def quality_gate(conn, *, probe: str | None = None) -> list[str]:
    """Fail if any returned hit is deleted, missing, stale, or dishonestly cited."""
    from items.hot_index import find_files

    query = probe or "the a of 作業 講義 notes report"
    result = find_files(conn, query, limit=50, mode="fts")
    failures: list[str] = []
    for hit in result.hits:
        row = conn.execute(
            "SELECT presence, freshness_state, content_hash, last_indexed_hash "
            "FROM items WHERE item_id = ?",
            (hit.item_id,),
        ).fetchone()
        if row is None:
            failures.append(f"missing row for hit {hit.item_id}")
            continue
        if row["presence"] != "live":
            failures.append(f"deleted/non-live hit {hit.item_id}")
        if row["freshness_state"] in ("missing", "conflicted"):
            failures.append(
                f"missing/conflicted hit {hit.item_id} "
                f"state={row['freshness_state']}"
            )
        ch, ih = row["content_hash"], row["last_indexed_hash"]
        if ch and ih and ch != ih:
            failures.append(f"stale hit {hit.item_id} hash mismatch")
        if hit.claims_body_match and not hit.best_chunk_id:
            failures.append(f"body claim without chunk on {hit.item_id}")
        if hit.claims_body_match and hit.best_chunk_id:
            crow = conn.execute(
                "SELECT item_id FROM item_chunks WHERE chunk_id = ?",
                (hit.best_chunk_id,),
            ).fetchone()
            if crow is None or crow["item_id"] != hit.item_id:
                failures.append(
                    f"stale/wrong chunk citation {hit.best_chunk_id}"
                )
    return failures
