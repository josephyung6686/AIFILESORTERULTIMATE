"""Darwin kqueue directory watch — live change feed without third-party deps.

Uses NOTE_WRITE / NOTE_RENAME / NOTE_DELETE on the root directory vnode.
Falls back to PathWatcher.tick polling when not Darwin or kqueue fails.
"""
from __future__ import annotations

import select
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from items.fsevents_feed import ChangeFeedPolicy, FsEvent
from items.path_watch import PathWatcher, WatchTickResult


@dataclass
class KqueueWatch:
    root: Path
    policy: ChangeFeedPolicy = field(default_factory=ChangeFeedPolicy)
    _kq: object | None = None
    _fd: int | None = None
    _poller: PathWatcher | None = None

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self._poller = PathWatcher(self.root, policy=self.policy)
        if sys.platform != "darwin":
            return
        try:
            import os
            self._fd = os.open(str(self.root), os.O_RDONLY)
            self._kq = select.kqueue()
            kev = select.kevent(
                self._fd,
                filter=select.KQ_FILTER_VNODE,
                flags=select.KQ_EV_ADD | select.KQ_EV_CLEAR,
                fflags=(
                    select.KQ_NOTE_WRITE
                    | select.KQ_NOTE_RENAME
                    | select.KQ_NOTE_DELETE
                    | select.KQ_NOTE_ATTRIB
                    | select.KQ_NOTE_EXTEND
                ),
            )
            self._kq.control([kev], 0, 0)
        except Exception:
            self.close()
            self._kq = None

    @property
    def live(self) -> bool:
        return self._kq is not None

    def wait(self, timeout_s: float = 0.5) -> list[FsEvent]:
        """Block up to timeout; return coarse dir-level events."""
        if self._kq is None:
            return []
        try:
            events = self._kq.control(None, 4, timeout_s)
        except Exception:
            return []
        out = []
        for ev in events:
            out.append(FsEvent(
                path=str(self.root),
                flags="modified",
            ))
        return out

    def tick(self, conn) -> WatchTickResult:
        """Wait briefly for kqueue, then reconcile via PathWatcher logic."""
        if self.live:
            self.wait(0.05)
        assert self._poller is not None
        return self._poller.tick(conn)

    def close(self) -> None:
        if self._kq is not None:
            try:
                self._kq.close()
            except Exception:
                pass
            self._kq = None
        if self._fd is not None:
            try:
                import os
                os.close(self._fd)
            except Exception:
                pass
            self._fd = None
