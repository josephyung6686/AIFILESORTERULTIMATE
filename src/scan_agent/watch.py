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
from scan_agent.exclusion import is_protected_container

#: The three §4 names. Recorded in the event's structured explanation (§8.2).
CHANGE_MODIFIED = "size or modification time changed"
CHANGE_APPEARED = "appeared"
CHANGE_DISAPPEARED = "disappeared"


class SessionWatch:
    """Open for one session (11 §3). Closing it ends the watch; nothing survives."""

    def __init__(self, conn: sqlite3.Connection, *, is_protected=None):
        self._conn = conn
        # `11-ops-runtime.md` §4b / P3 SPEC:39. `extra` can only ADD members: a
        # predicate that returned False for a `.app` would be the override §4b says
        # does not exist, and `is_protected_container` checks the suffix first.
        self._is_protected = is_protected
        self._roots: tuple[Path, ...] = ()
        self._observed: dict[str, tuple[int, float] | None] = {}
        self._open = False

    def open(self, roots) -> None:
        """Begin watching the selected roots and record their current stat."""
        self._roots = tuple(Path(root) for root in roots)
        self._observed = {}
        for root in self._roots:
            # A root that IS inside a container cannot be reached by pruning
            # `dirnames`: `os.walk` never offers its own top to the prune.
            if self._protected(root):
                continue
            for current, _dirnames, names in self._walk(root):
                for name in names:
                    path = Path(current) / name
                    self._observed[str(path)] = self._stat(path)
        self._open = True

    def _protected(self, path) -> bool:
        return is_protected_container(path, extra=self._is_protected)

    def _walk(self, root: Path):
        """`os.walk`, pruned at every protected container before it is entered.

        The prune is an in-place assignment to `dirnames` because that is the only
        thing `os.walk` reads back. Filtering the result instead would have already
        descended, and descending IS the read §4b forbids — P3 "does not descend
        into one, does not stat its contents" (P3 SPEC:39).
        """
        for current, dirnames, names in os.walk(root):
            dirnames[:] = [name for name in dirnames
                           if not self._protected(Path(current) / name)]
            yield current, dirnames, names

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
            if self._protected(root):
                continue
            for current, _dirnames, names in self._walk(root):
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
        # FIRST, and before the roots test and before the stat below. A platform
        # adapter calls `notify` directly, so `open`'s prune does not protect this
        # entry point. The stat IS the read §4b forbids, and `append_event` would
        # then write an interior path into the append-only `events` log, where it
        # cannot be removed. SPEC:46-47: the record carries "the container's own
        # path and nothing derived from inside it".
        if self._protected(path):
            return
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
