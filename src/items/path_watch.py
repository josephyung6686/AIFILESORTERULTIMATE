"""Polling path watcher using ChangeFeedPolicy (P1 until live FSEvents).

Never moves files. On accepted changes: identity reconcile + FTS rebuild
for the tree. Own-move echoes are filtered by the policy.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from items.fsevents_feed import ChangeFeedPolicy, FsEvent
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree


@dataclass
class WatchTickResult:
    accepted: int
    reindexed: bool
    moved: bool = False


@dataclass
class PathWatcher:
    root: Path
    policy: ChangeFeedPolicy = field(default_factory=ChangeFeedPolicy)
    _mtime_index: dict[str, float] = field(default_factory=dict)
    _primed: bool = False

    def scan_events(self) -> list[FsEvent]:
        events: list[FsEvent] = []
        root = self.root
        if not root.is_dir():
            return events
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            key = str(path)
            prev = self._mtime_index.get(key)
            if prev is None:
                self._mtime_index[key] = mtime
                if self._primed:
                    events.append(FsEvent(path=key, flags="created"))
            elif mtime > prev:
                self._mtime_index[key] = mtime
                events.append(FsEvent(path=key, flags="modified"))
        self._primed = True
        return events

    def tick(self, conn: sqlite3.Connection) -> WatchTickResult:
        raw = self.scan_events()
        accepted = self.policy.filter_batch(raw)
        if not accepted:
            return WatchTickResult(accepted=0, reindexed=False)
        reconcile_tree(conn, self.root)
        rebuild_fts(conn)
        return WatchTickResult(accepted=len(accepted), reindexed=True)
