"""Live macOS FSEvents watcher (P1). Falls back to polling PathWatcher.

Uses optional ``watchdog`` with FSEventsEmitter when installed. Never moves
files — only emits FsEvent for PathWatcher/policy to consume.
"""
from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from items.fsevents_feed import FsEvent


def fsevents_available() -> bool:
    if sys.platform != "darwin":
        return False
    try:
        from watchdog.observers.fsevents import FSEventsObserver  # noqa: F401
        return True
    except Exception:
        return False


@dataclass
class LiveFsEventsWatcher:
    """Subscribe to FSEvents for ``root``. Thread-safe event queue."""

    root: Path
    _queue: list[FsEvent] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _observer: object | None = None
    _started: bool = False

    def start(self) -> bool:
        if self._started:
            return True
        if not fsevents_available():
            return False
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers.fsevents import FSEventsObserver

        root = str(self.root.resolve())
        watcher = self

        class _Handler(FileSystemEventHandler):
            def on_any_event(self, event):  # noqa: N802
                if event.is_directory:
                    return
                path = getattr(event, "dest_path", None) or event.src_path
                flags = "modified"
                et = event.event_type
                if et == "created":
                    flags = "created"
                elif et == "deleted":
                    flags = "removed"
                elif et == "moved":
                    flags = "renamed"
                with watcher._lock:
                    watcher._queue.append(FsEvent(path=str(path), flags=flags))

        obs = FSEventsObserver()
        obs.schedule(_Handler(), root, recursive=True)
        obs.start()
        self._observer = obs
        self._started = True
        return True

    def stop(self) -> None:
        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join(timeout=2)
            except Exception:
                pass
            self._observer = None
        self._started = False

    def drain(self) -> list[FsEvent]:
        with self._lock:
            out = list(self._queue)
            self._queue.clear()
        return out

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()
        return False


def watch_until(
        root: Path,
        *,
        seconds: float = 1.0,
        on_events: Callable[[list[FsEvent]], None] | None = None,
) -> list[FsEvent]:
    """Convenience: live watch for a short window (tests / CLI)."""
    w = LiveFsEventsWatcher(root=root)
    if not w.start():
        return []
    try:
        time.sleep(seconds)
        events = w.drain()
        if on_events:
            on_events(events)
        return events
    finally:
        w.stop()
