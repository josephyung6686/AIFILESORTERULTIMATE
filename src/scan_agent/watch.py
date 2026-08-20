# src/scan_agent/watch.py
"""11-ops-runtime.md §4 — the live observation P3 does while a session is open.

"P3 remains scan-plus-stat-cache. While a session is open, P3 also watches the
selected roots (FSEvents / DispatchSource) and authors `external modification
detection` for any watched path whose size or mtime changes, which appears, or which
disappears. There is no background daemon in v1. Closing the app ends the watch. …
A detection is not a rescan by itself."

The PLATFORM event source is not built here: FSEvents / DispatchSource need a macOS
API binding the standard library does not supply, and this part adds no third-party
dependency. `notify` is the entry point such an adapter calls, and `poll` is a
stdlib driver for it. Everything §4 specifies about WHAT a detection means lives
here and is tested; only the platform callback is missing, and it is not faked.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from database_agent.events import append_event

from scan_agent.authorship import event_defaults

#: The three §4 names. Recorded in the event's structured explanation (§8.2).
CHANGE_MODIFIED = "size or modification time changed"
CHANGE_APPEARED = "appeared"
CHANGE_DISAPPEARED = "disappeared"


class SessionWatch:
    """Open for one session (11 §3). Closing it ends the watch; nothing survives."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._roots: tuple[Path, ...] = ()
        self._observed: dict[str, tuple[int, float] | None] = {}
        self._open = False

    def open(self, roots) -> None:
        """Begin watching the selected roots and record their current stat."""
        self._roots = tuple(Path(root) for root in roots)
        self._observed = {}
        for root in self._roots:
            for current, _, names in os.walk(root):
                for name in names:
                    path = Path(current) / name
                    self._observed[str(path)] = self._stat(path)
        self._open = True

    def close(self) -> None:
        """11 §4: "Closing the app ends the watch." No daemon, no thread, no timer."""
        self._open = False
        self._roots = ()
        self._observed = {}

    def poll(self) -> None:
        """Re-stat the watched paths and notify each difference.

        The stdlib driver. A platform adapter (FSEvents / DispatchSource) calls
        `notify` directly instead, and is not built here.
        """
        if not self._open:
            return
        known = set(self._observed)
        live: set[str] = set()
        for root in self._roots:
            for current, _, names in os.walk(root):
                for name in names:
                    live.add(str(Path(current) / name))
        for path in sorted(known | live):
            self.notify(Path(path))

    def notify(self, path) -> None:
        """One watched path may have changed. Authors the detection when it did.

        A detection is NOT a rescan (11 §4): this re-stats the one path, writes no
        `files` row, and starts no scan run.
        """
        if not self._open:
            return
        path = Path(path)
        if not any(path == root or root in path.parents for root in self._roots):
            return

        before = self._observed.get(str(path))
        after = self._stat(path)
        if before == after:
            return

        if before is None:
            change = CHANGE_APPEARED
        elif after is None:
            change = CHANGE_DISAPPEARED
        else:
            change = CHANGE_MODIFIED
        self._observed[str(path)] = after

        row = self._conn.execute(
            "SELECT file_id, content_hash FROM files WHERE current_path = ? "
            "ORDER BY rowid DESC LIMIT 1", (str(path),)
        ).fetchone()

        # SPEC Q14's other half stays OPEN: what happens to a `files` row whose path
        # no longer exists is not decided here, so no row is modified or removed.
        append_event(self._conn, **event_defaults(
            event_type="external modification detection",
            file_id=row["file_id"] if row else None,
            content_hash=row["content_hash"] if row else None,
            old_path=str(path), new_path=str(path),
            explanation=json.dumps({
                "change": change,
                "prior_observed": list(before) if before else None,
                "observed": list(after) if after else None,
                "source": "session watch (11-ops-runtime.md §4)",
            }),
        ))

    @staticmethod
    def _stat(path: Path) -> tuple[int, float] | None:
        try:
            result = os.stat(path, follow_symlinks=False)
        except (FileNotFoundError, NotADirectoryError, PermissionError):
            return None
        return (result.st_size, result.st_mtime)
