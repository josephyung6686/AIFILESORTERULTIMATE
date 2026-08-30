# src/scan_agent/disappearance.py
"""Contract out SPEC Q14's other half — a recorded path that is no longer there.

Q14 asks three things and M8 had settled only the first: `external modification
detection` has two authors, **P3** (§1.2 re-scan) and **P12** (§8.3 staleness).
Still open were "what happens to a `files` row whose path no longer exists" and
"whether a disappearance is that same event or another".

`11-ops-runtime.md` §4 already answers the second for the LIVE watch: while a
session is open P3 authors `external modification detection` for a watched path
"which appears, or which disappears", and `watch.py` implements it. So the event
type is settled and this part registers nothing new (B5). What §4 does not cover is
the ordinary case: a person quits the app, deletes a file, and runs a scan again a
week later. There is no watch across that gap, and until this module existed the
re-scan never asked. The walk only ever visits what is on the disk NOW, so a file
that had been removed was simply not visited, nothing about it changed, and it went
on being part of the corpus every later run planned over. The product offered to
file something that was not there.

**What this does and does not touch.** It retires the row from the corpus and
destroys nothing: `set_path_no_longer_exists` moves one column and leaves the path,
the hash, the stat history and every event exactly where they are, because §8.5's
replay has to be able to reconstruct the run that saw the file. A deleted file's
records are not the product's to delete.

**Absent is not the same as unreachable.** `files_table._lstat_or_none` answers None
for any `OSError` at all, which is the right answer to the question IT asks -- "is
this the same file" -- and the wrong one here. Losing permission to a folder is a
thing that happens to a live disk, and retiring the files inside it would take them
out of the person's plan while they are sitting right there. Only the errors that
mean the name resolves to nothing count, and every other error leaves the row alone.

**A protected container is never opened, here as everywhere.** The check comes
first, before the stat, for the reason `watch.py` gives at its own entry point: the
stat IS the read §4b forbids. A row whose path has since ended up inside one is left
as it is -- still counted, never examined, and never reported as deleted on the
strength of a look this part is not allowed to take.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path, PurePath

from database_agent.files_table import set_path_no_longer_exists

from scan_agent.authorship import COMPONENT_VERSION, SUBSYSTEM, event_defaults
from scan_agent.exclusion import is_protected_container
from scan_agent.watch import CHANGE_DISAPPEARED

from database_agent.events import append_event

#: The errors that mean the path names nothing. `FileNotFoundError` is the deletion;
#: `NotADirectoryError` is a parent that stopped being a folder, which unmakes every
#: name beneath it just as thoroughly. `PermissionError`, `OSError` and everything
#: else mean the answer is unknown, and unknown is not gone.
_MEANS_ABSENT = (FileNotFoundError, NotADirectoryError)


def _is_absent(path: str) -> bool:
    """Does this recorded path name nothing at all?

    `lstat`, not `stat`, and not `Path.exists()`: a symlink whose target is gone is
    still a directory entry the person can see and delete, so it is a file that is
    there. `exists()` would call it absent and retire a row for something still on
    the disk.
    """
    try:
        os.lstat(path)
    except _MEANS_ABSENT:
        return True
    except OSError:
        return False
    return False


def _under(path: str, sources) -> bool:
    """Was this row's path inside a folder THIS scan looked at?

    Scanning one folder must not retire the files of another. Both are the person's;
    only one of them was walked, and the other's absence from this walk is not
    evidence of anything.
    """
    candidate = PurePath(path)
    return any(candidate == source or source in candidate.parents
               for source in (PurePath(s) for s in sources))


def reconcile_disappearances(conn: sqlite3.Connection, scan_run_id: str, *,
                             sources, scan_state: str) -> tuple[str, ...]:
    """Retire every row this scan's folders no longer hold. Returns their file ids.

    Runs after the walk, because the walk is what proves the file was not found:
    asking first would race a scan that had not looked yet.

    `scan_state` is the caller's corpus value, the same one the walk writes, for the
    reason `basic_record` gives -- SPEC Q4 leaves the enumeration to the caller and
    P3 invents none. Rows recorded under any other value are already out of the
    corpus and are not re-examined.
    """
    retired: list[str] = []
    rows = conn.execute(
        "SELECT file_id, current_path, content_hash FROM files "
        "WHERE scan_state = ? ORDER BY file_id", (scan_state,)).fetchall()
    for row in rows:
        path = row["current_path"]
        # FIRST, and before the stat. See the module docstring, and `watch.notify`.
        if is_protected_container(Path(path)):
            continue
        if not _under(path, sources):
            continue
        if not _is_absent(path):
            continue
        append_event(conn, **event_defaults(
            event_type="external modification detection",
            file_id=row["file_id"], content_hash=row["content_hash"],
            old_path=path, new_path=None,
            explanation=json.dumps({
                "change": CHANGE_DISAPPEARED,
                "source": "re-scan (P3 SPEC Q14)",
                "scan_run_id": scan_run_id,
            }),
        ))
        set_path_no_longer_exists(conn, row["file_id"], author=SUBSYSTEM,
                                  component_version=COMPONENT_VERSION)
        retired.append(row["file_id"])
    return tuple(retired)
