"""Index freshness: tick PathWatcher roots so ask/search see disk truth."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RefreshResult:
    roots: tuple[str, ...]
    ticks: int
    reindexed: bool
    backend: str


def discover_roots(conn: sqlite3.Connection, *, limit: int = 8) -> list[Path]:
    """Infer watch roots from live file open_targets (parent dirs)."""
    rows = conn.execute(
        "SELECT open_target FROM items "
        "WHERE presence='live' AND open_target IS NOT NULL "
        "AND item_type='file' LIMIT 500"
    ).fetchall()
    parents: dict[str, int] = {}
    for r in rows:
        try:
            p = Path(r["open_target"]).resolve().parent
        except Exception:
            continue
        if not p.is_dir():
            continue
        # Prefer shallow roots: walk up until Downloads/home-ish or stop at 3 levels
        key = str(p)
        parents[key] = parents.get(key, 0) + 1
    # Collapse to unique top-level parents by frequency
    ranked = sorted(parents.items(), key=lambda kv: -kv[1])
    out: list[Path] = []
    seen: set[str] = set()
    for key, _ in ranked:
        path = Path(key)
        # Skip if already covered by a parent we chose
        if any(str(path).startswith(s + "/") or str(path) == s for s in seen):
            continue
        out.append(path)
        seen.add(str(path))
        if len(out) >= limit:
            break
    return out


def refresh_index(
        conn: sqlite3.Connection,
        *,
        roots: list[Path] | None = None,
        prefer_fsevents: bool = True,
) -> RefreshResult:
    """One-shot reconcile+FTS for discovered or provided roots."""
    from items.path_watch import PathWatcher

    use = roots if roots is not None else discover_roots(conn)
    ticks = 0
    reindexed = False
    backend = "none"
    for root in use:
        if not root.is_dir():
            continue
        w = PathWatcher(root, prefer_fsevents=prefer_fsevents)
        try:
            w.scan_events()  # prime
            result = w.tick(conn)
            ticks += 1
            reindexed = reindexed or bool(result.reindexed)
            backend = result.backend
        finally:
            w.stop_live()
    return RefreshResult(
        roots=tuple(str(r) for r in use),
        ticks=ticks,
        reindexed=reindexed,
        backend=backend,
    )
