"""FSEvents change feed design (P1) — coalesce + ignore own plan ops.

Real FSEvents subscription is macOS-specific; this module owns the policy
used by any watcher backend (Addendum T-P4-05).

Debounce keys prefer stable file identity (``st_dev``/``st_ino``) when present,
falling back to resolved path. Batch filtering retains the latest event per
identity so rapid edits collapse without dropping the final state.
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
    st_dev: int | None = None
    st_ino: int | None = None
    seq: int | None = None

    def identity_key(self) -> str:
        """Stable debounce key: inode identity when known, else path."""
        if self.st_dev is not None and self.st_ino is not None:
            return f"ino:{int(self.st_dev)}:{int(self.st_ino)}"
        try:
            return f"path:{Path(self.path).resolve()}"
        except Exception:
            return f"path:{self.path}"


@dataclass
class ChangeFeedPolicy:
    """Debounce + filter before reindex."""
    debounce_ms: float = 300.0
    in_flight_paths: set[str] = field(default_factory=set)
    _last_emit: dict[str, float] = field(default_factory=dict)
    # Latest retained event per identity (for coalesce-then-read).
    _latest: dict[str, FsEvent] = field(default_factory=dict)

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
        key = event.identity_key()
        # Always retain the latest observation for this identity.
        self._latest[key] = event
        # Creates/renames/removes are structural — never drop on debounce.
        if event.flags in ("created", "renamed", "removed"):
            self._last_emit[key] = now if now is not None else time.monotonic()
            return True
        t = now if now is not None else time.monotonic()
        last = self._last_emit.get(key, 0.0)
        if (t - last) * 1000.0 < self.debounce_ms:
            return False
        self._last_emit[key] = t
        return True

    def filter_batch(self, events: Iterable[FsEvent]) -> list[FsEvent]:
        """Coalesce by identity; emit at most one accepted event per key.

        Retains the latest event for each identity and re-reads identity fields
        from that event (callers re-stat/hash immediately before indexing).
        """
        # First pass: collapse to latest per identity, preserving order of first
        # appearance for stable output.
        latest: dict[str, FsEvent] = {}
        order: list[str] = []
        for ev in events:
            key = ev.identity_key()
            if key not in latest:
                order.append(key)
            latest[key] = ev
        out: list[FsEvent] = []
        t = time.monotonic()
        for key in order:
            ev = latest[key]
            if self.accept(ev, now=t):
                # Prefer the retained latest (may have been updated in accept).
                out.append(self._latest.get(key, ev))
                t += 0.001  # slight advance so same-batch multi-path still works
        return out

    def take_latest(self, identity_key: str) -> FsEvent | None:
        return self._latest.get(identity_key)
