# src/scan_agent/corpus_source.py
"""§8.5 — one interface over a live filesystem and a frozen corpus snapshot.

SPEC Contract in (from P2): §8.5 requires evaluation "without touching a live
filesystem", and the bundle contains "a frozen corpus snapshot or a metadata-safe
representation of one". P3 must therefore be runnable against a bundle-backed corpus
source as well as a live filesystem, with identical exclusion and cache verdicts.

P2 owns the bundle ENVELOPE. This module imports no P2 code and defines none of it.
"""
from __future__ import annotations

import os
import stat as stat_module
from dataclasses import dataclass
from typing import Protocol

from scan_agent.dataless import is_dataless

KIND_DIRECTORY = "directory"
KIND_FILE = "file"
#: Anything that is neither: symlinks, aliases, sockets, fifos, devices. SPEC Q7 is
#: OPEN on scan-time traversal of these, and this module decides nothing — it reports
#: the kind and lets the traversal record the unresolved case.
KIND_OTHER = "other"


@dataclass(frozen=True)
class Entry:
    path: str
    name: str
    kind: str
    size: int
    mtime: float
    dataless: bool


class CorpusSource(Protocol):
    has_bytes: bool

    def entries(self, directory) -> list[Entry]: ...


def _kind(mode: int) -> str:
    if stat_module.S_ISDIR(mode):
        return KIND_DIRECTORY
    if stat_module.S_ISREG(mode):
        return KIND_FILE
    return KIND_OTHER


class FilesystemCorpusSource:
    """The live filesystem."""

    has_bytes = True

    def entries(self, directory) -> list[Entry]:
        """One directory's entries, ordered by path so two runs agree.

        `follow_symlinks=False` throughout: a symlink is reported as KIND_OTHER, so
        it is never descended (a loop would make traversal non-terminating) and never
        handed to P1's hasher. SPEC Q7 stays open; this is termination, not policy.

        The phrasing is deliberate. Task 7's guard asserts the name of P1's hashing
        entry point appears nowhere in this module, and a prose mention would trip
        it — the guard is blunt on purpose, because a narrower one that matched only
        a call would stop catching an aliased import.
        """
        found: list[Entry] = []
        with os.scandir(directory) as scan:
            for item in scan:
                st = item.stat(follow_symlinks=False)
                found.append(Entry(
                    path=item.path,
                    name=item.name,
                    kind=_kind(st.st_mode),
                    size=st.st_size,
                    mtime=st.st_mtime,
                    dataless=is_dataless(st),
                ))
        return sorted(found, key=lambda entry: entry.path)


class SnapshotCorpusSource:
    """A frozen corpus snapshot (§8.5). Touches no filesystem at all.

    `has_bytes` is False for §8.5's `metadata_safe` form: there are no bytes, so no
    content hash can be recomputed and P1's content-hash identity is unavailable.
    Exclusion, cache and inventory verdicts are all still reproducible, which is what
    Done-means 14 asks to be identical.
    """

    def __init__(self, snapshot: dict):
        self.has_bytes = snapshot["corpus_form"] == "snapshot"
        self._by_parent: dict[str, list[Entry]] = {}
        for record in snapshot["entries"]:
            entry = Entry(
                path=record["path"], name=record["name"], kind=record["kind"],
                size=record["size"], mtime=record["mtime"],
                dataless=record["dataless"],
            )
            self._by_parent.setdefault(record["parent"], []).append(entry)
        for children in self._by_parent.values():
            children.sort(key=lambda entry: entry.path)

    def entries(self, directory) -> list[Entry]:
        return list(self._by_parent.get(str(directory), []))
