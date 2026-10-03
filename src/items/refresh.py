"""Index freshness: tick PathWatcher roots so ask/search see disk truth."""
from __future__ import annotations

import json
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
    """The folders the person chose to scan; inferred from items only if none.

    Recorded selection sources, newest first, are the folders a scan reads, so
    a new file at the top of one is found and its top-level exclusions are
    recorded again. Item parents are a guess, used only before any selection.
    """
    chosen = _selected_sources(conn)
    if chosen:
        # Parents first, so a chosen folder inside another is not walked twice.
        return _collapse(sorted(chosen, key=lambda p: len(p.parts)), limit)
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
    return _collapse([Path(key) for key, _ in ranked], limit)


def _selected_sources(conn: sqlite3.Connection) -> list[Path]:
    """Every recorded selection source that is still a folder, newest first."""
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' "
                    "AND name='corpus_selections'").fetchone() is None:
        return []
    out: list[Path] = []
    for row in conn.execute(
            "SELECT sources FROM corpus_selections ORDER BY selected_at DESC"):
        for source in json.loads(row["sources"]):
            path = Path(source)
            if path.is_dir() and path not in out:
                out.append(path)
    return out


def _collapse(paths: list[Path], limit: int) -> list[Path]:
    """Drop folders already covered by an earlier one, up to `limit`."""
    out: list[Path] = []
    seen: set[str] = set()
    for path in paths:
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
            # Startup reconcile is restart-safe; tick drains the shared queue.
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
