"""FSEvents change feed design (P1) — coalesce + ignore own plan ops.

Real FSEvents subscription is macOS-specific; this module owns the policy
used by any watcher backend (Addendum T-P4-05).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class FsEvent:
    path: str
    flags: str = "modified"  # created|modified|renamed|removed
    is_icloud_placeholder: bool = False


@dataclass
class ChangeFeedPolicy:
    """Debounce + filter before reindex."""
    debounce_ms: float = 300.0
    in_flight_paths: set[str] = field(default_factory=set)
    _last_emit: dict[str, float] = field(default_factory=dict)

    def note_own_move(self, src: str, dst: str) -> None:
        self.in_flight_paths.add(str(Path(src).resolve()) if src else src)
        self.in_flight_paths.add(str(Path(dst).resolve()) if dst else dst)

    def clear_own_move(self, src: str, dst: str) -> None:
        self.in_flight_paths.discard(str(Path(src).resolve()) if src else src)
        self.in_flight_paths.discard(str(Path(dst).resolve()) if dst else dst)

    def accept(self, event: FsEvent, *, now: float | None = None) -> bool:
        """Return True if this event should trigger reindex."""
        if event.is_icloud_placeholder:
            return False
        path = event.path
        try:
            resolved = str(Path(path).resolve())
        except Exception:
            resolved = path
        if resolved in self.in_flight_paths or path in self.in_flight_paths:
            return False
        t = now if now is not None else time.monotonic()
        last = self._last_emit.get(resolved, 0.0)
        if (t - last) * 1000.0 < self.debounce_ms:
            return False
        self._last_emit[resolved] = t
        return True

    def filter_batch(self, events: Iterable[FsEvent]) -> list[FsEvent]:
        out = []
        t = time.monotonic()
        for ev in events:
            if self.accept(ev, now=t):
                out.append(ev)
                t += 0.001  # slight advance so same-path batch collapses
        return out
