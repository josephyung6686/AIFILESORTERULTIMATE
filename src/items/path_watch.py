"""Path watcher: live macOS FSEvents when available, else polling.

Never moves files. On accepted changes: identity reconcile + FTS rebuild
for the tree. Own-move echoes are filtered by the policy.

Rename-follow: inode tokens in item_bookmarks survive Path.rename; tick
updates open_target when the old path is gone and the inode reappears.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from items.file_identity import remember_path, resolve_renamed
from items.fsevents_feed import ChangeFeedPolicy, FsEvent
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree


@dataclass
class WatchTickResult:
    accepted: int
    reindexed: bool
    moved: bool = False
    renames_followed: int = 0
    backend: str = "polling"


@dataclass
class PathWatcher:
    root: Path
    policy: ChangeFeedPolicy = field(default_factory=ChangeFeedPolicy)
    prefer_fsevents: bool = True
    _mtime_index: dict[str, float] = field(default_factory=dict)
    _primed: bool = False
    _live: object | None = None
    backend: str = "polling"

    def start_live(self) -> bool:
        """Start macOS FSEvents subscription when watchdog is installed."""
        if not self.prefer_fsevents:
            return False
        try:
            from items.fsevents_live import LiveFsEventsWatcher, fsevents_available
        except Exception:
            return False
        if not fsevents_available():
            return False
        live = LiveFsEventsWatcher(root=self.root)
        if not live.start():
            return False
        self._live = live
        self.backend = "fsevents"
        return True

    def stop_live(self) -> None:
        if self._live is not None:
            try:
                self._live.stop()
            except Exception:
                pass
            self._live = None
            self.backend = "polling"

    def _scan_polling(self) -> list[FsEvent]:
        events: list[FsEvent] = []
        root = self.root
        if not root.is_dir():
            return events
        seen: set[str] = set()
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            key = str(path)
            seen.add(key)
            prev = self._mtime_index.get(key)
            if prev is None:
                self._mtime_index[key] = mtime
                if self._primed:
                    events.append(FsEvent(path=key, flags="created"))
            elif mtime > prev:
                self._mtime_index[key] = mtime
                events.append(FsEvent(path=key, flags="modified"))
        for key in list(self._mtime_index):
            if key not in seen:
                del self._mtime_index[key]
                if self._primed:
                    events.append(FsEvent(path=key, flags="renamed"))
        self._primed = True
        return events

    def scan_events(self) -> list[FsEvent]:
        # Live FSEvents can lag; always merge a polling pass so creates/renames
        # are not missed when the observer queue is empty.
        poll = self._scan_polling()
        if self._live is None:
            return poll
        live = list(self._live.drain())
        if not live:
            return poll
        seen = {(e.path, e.flags) for e in live}
        for e in poll:
            if (e.path, e.flags) not in seen:
                live.append(e)
        return live

    def _remember_live(self, conn: sqlite3.Connection) -> None:
        rows = conn.execute(
            "SELECT item_id, open_target FROM items "
            "WHERE presence='live' AND open_target IS NOT NULL"
        ).fetchall()
        for row in rows:
            path = Path(row["open_target"])
            if path.is_file():
                remember_path(conn, row["item_id"], path)

    def _follow_renames(self, conn: sqlite3.Connection) -> int:
        """Update open_target when inode bookmark matches a new path."""
        followed = 0
        rows = conn.execute(
            "SELECT item_id, open_target FROM items "
            "WHERE presence='live' AND open_target IS NOT NULL"
        ).fetchall()
        candidates = [p for p in self.root.rglob("*") if p.is_file()]
        for row in rows:
            path = Path(row["open_target"])
            if path.is_file():
                remember_path(conn, row["item_id"], path)
                continue
            hit = resolve_renamed(conn, row["item_id"], candidates)
            if hit is not None:
                conn.execute(
                    "UPDATE items SET open_target=? WHERE item_id=?",
                    (str(hit), row["item_id"]),
                )
                followed += 1
        return followed

    def ensure_best_backend(self) -> str:
        """Prefer live FSEvents; leave polling if unavailable."""
        if self.backend == "fsevents" and self._live is not None:
            return self.backend
        if self.prefer_fsevents:
            self.start_live()
        return self.backend

    def _tree_drift(self, conn: sqlite3.Connection) -> bool:
        """True when disk has a live file the DB does not know (or vice versa)."""
        if not self.root.is_dir():
            return False
        disk = {
            str(p.resolve())
            for p in self.root.rglob("*")
            if p.is_file()
        }
        rows = conn.execute(
            "SELECT open_target FROM items "
            "WHERE presence='live' AND open_target IS NOT NULL "
            "AND item_type='file'"
        ).fetchall()
        known: set[str] = set()
        for r in rows:
            try:
                known.add(str(Path(r["open_target"]).resolve()))
            except Exception:
                known.add(r["open_target"])
        return disk != known

    def tick(self, conn: sqlite3.Connection) -> WatchTickResult:
        self.ensure_best_backend()
        raw = self.scan_events()
        accepted = self.policy.filter_batch(raw)
        # Bookmarks before reconcile so inode identity survives Path.rename.
        try:
            self._remember_live(conn)
        except Exception:
            pass
        # FSEvents lag / debounce can drop creates; polling merge + drift catch.
        drift = False
        if not accepted:
            try:
                drift = self._tree_drift(conn)
            except Exception:
                drift = False
        if not accepted and not drift:
            # Still attempt rename-follow when feed was quiet (race / debounce).
            try:
                n = self._follow_renames(conn)
            except Exception:
                n = 0
            if n:
                rebuild_fts(conn)
                return WatchTickResult(
                    accepted=0, reindexed=True, renames_followed=n,
                    backend=self.backend)
            return WatchTickResult(
                accepted=0, reindexed=False, backend=self.backend)
        reconcile_tree(conn, self.root)
        try:
            n = self._follow_renames(conn)
        except Exception:
            n = 0
        rebuild_fts(conn)
        return WatchTickResult(
            accepted=len(accepted), reindexed=True, renames_followed=n,
            backend=self.backend)
