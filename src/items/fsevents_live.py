"""Live macOS FSEvents watcher (P1). Falls back to polling PathWatcher.

Uses optional ``watchdog`` with FSEventsEmitter when installed. Never moves
files — only emits FsEvent for PathWatcher/policy to consume.

Each event carries a monotonic ``seq`` so PathWatcher can persist a durable
cursor/watermark and a restart cannot skip observed work.
"""
from __future__ import annotations

import sys
import threading
import time
import weakref
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


def _identity_for(path: str) -> tuple[int | None, int | None]:
    try:
        st = Path(path).stat()
        return int(st.st_dev), int(st.st_ino)
    except OSError:
        return None, None


@dataclass
class LiveFsEventsWatcher:
    """Subscribe to FSEvents for ``root``. Thread-safe event queue."""

    root: Path
    _queue: list[FsEvent] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _observer: object | None = None
    _started: bool = False
    _seq: int = 0
    last_seq: int = 0

    def start(self) -> bool:
        if self._started:
            return True
        if not fsevents_available():
            return False
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers.fsevents import FSEventsObserver

        root = str(self.root.resolve())
        watcher_ref = weakref.ref(self)

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
                st_dev, st_ino = _identity_for(str(path))
                watcher = watcher_ref()
                if watcher is None:
                    return
                with watcher._lock:
                    watcher._seq += 1
                    seq = watcher._seq
                    watcher.last_seq = seq
                    watcher._queue.append(FsEvent(
                        path=str(path),
                        flags=flags,
                        st_dev=st_dev,
                        st_ino=st_ino,
                        seq=seq,
                    ))

        obs = FSEventsObserver()
        try:
            obs.schedule(_Handler(), root, recursive=True)
            obs.start()
        except Exception:
            try:
                obs.stop()
                obs.join()
            except Exception:
                pass
            raise
        self._observer = obs
        self._started = True
        return True

    def stop(self) -> None:
        if self._observer is not None:
            try:
                self._observer.stop()
                # Do not return while the native emitter is still alive. A
                # timeout leaves the C FSEvents callback running into the next
                # database operation and has caused process-level crashes.
                self._observer.join()
            except Exception:
                pass
            self._observer = None
        self._started = False

    def close(self) -> None:
        """Explicit lifecycle alias used by owning services and context managers."""
        self.stop()

    def drain(self) -> list[FsEvent]:
        with self._lock:
            out = list(self._queue)
            self._queue.clear()
        return out

    def peek_seq(self) -> int:
        with self._lock:
            return self.last_seq

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
