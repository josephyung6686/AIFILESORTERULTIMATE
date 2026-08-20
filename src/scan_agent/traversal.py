# src/scan_agent/traversal.py
"""The corpus boundary: §1.1's exclusion rules applied while walking.

A pure generator over a CorpusSource. It opens no database and writes no row, so
every §1.1 decision is finished before any record exists — which is what lets Task
13's curation signal be provably unable to change an exclusion or a cache verdict.
"""
from __future__ import annotations

from collections import Counter, deque
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from pathlib import PurePath

from scan_agent.corpus_source import KIND_DIRECTORY, KIND_FILE, CorpusSource
from scan_agent.deferrals import (
    DEFERRED_BUDGET, DEFERRED_DIRECTORY_UNREADABLE, DEFERRED_PATH_ABSENT,
    DEFERRED_TRAVERSAL_UNRESOLVED,
)
from scan_agent.exclusion import (
    APPLIES_TO_CANDIDATE_ROOT, APPLIES_TO_SCANNED_SOURCE, exclusion_for,
    project_root_markers_in,
)


@dataclass(frozen=True)
class ObservedFile:
    """A non-excluded file. The writer turns a scanned-source one into an R2 row."""
    path: str
    size: int
    mtime: float
    dataless: bool
    applies_to: str


@dataclass(frozen=True)
class ObservedDirectory:
    """R6's observations for one fully-listed non-excluded directory."""
    directory_path: str
    parent_directory: str | None
    file_count: int
    subdirectory_count: int
    extension_mix: dict[str, int]
    project_root_markers: tuple[str, ...]
    applies_to: str


@dataclass(frozen=True)
class Deferred:
    path: str
    is_directory: bool
    reason: str


def walk(source: CorpusSource, *,
         sources: Iterable,
         candidate_roots: Iterable,
         budget_exhausted: Callable[[], bool]) -> Iterator:
    """Walk both sides of the scan, applying §1.1 before descending.

    `budget_exhausted` is required and has no default: §8.6's configurable-ceiling
    list names none for traversal or hashing (SPEC Q15 is open), so P3 holds no
    ceiling of its own and a caller with none supplies a predicate that never fires.
    """
    for root in sources:
        yield from _walk_root(source, root, APPLIES_TO_SCANNED_SOURCE, budget_exhausted)
    for root in candidate_roots:
        yield from _walk_root(source, root, APPLIES_TO_CANDIDATE_ROOT, budget_exhausted)


def _walk_root(source, root, applies_to, budget_exhausted) -> Iterator:
    root = str(root)
    root_verdict = exclusion_for(root, is_dir=True, applies_to=applies_to)
    if root_verdict is not None:
        # §1.1's exclusion "must apply both to scanned sources and to candidate
        # roots" — including when the root IS one of the eleven names.
        yield root_verdict
        return

    queue: deque[tuple[str, str | None]] = deque([(root, None)])
    while queue:
        directory, parent = queue.popleft()
        try:
            entries = source.entries(directory)
        except (FileNotFoundError, NotADirectoryError):
            yield Deferred(directory, True, DEFERRED_PATH_ABSENT)
            continue
        except PermissionError:
            # One directory this process cannot list does not end the walk, and it
            # is never silent (§8.6). Task 8 cleared the selected ROOTS; anything
            # below one can still refuse. Nothing inside is known — the listing
            # never happened — so this yields the directory and no inventory row.
            yield Deferred(directory, True, DEFERRED_DIRECTORY_UNREADABLE)
            continue

        markers = project_root_markers_in(
            (entry.name, entry.kind == KIND_DIRECTORY) for entry in entries
        )
        file_count = 0
        subdirectory_count = 0
        mix: Counter[str] = Counter()

        for index, entry in enumerate(entries):
            if budget_exhausted():
                # Retain what was already observed (§8.6), record everything not
                # reached, and emit NO inventory row for this directory: R6 has no
                # field for a partial count and P3 does not invent one.
                for remaining in entries[index:]:
                    yield Deferred(remaining.path,
                                   remaining.kind == KIND_DIRECTORY, DEFERRED_BUDGET)
                yield Deferred(directory, True, DEFERRED_BUDGET)
                while queue:
                    pending, _ = queue.popleft()
                    yield Deferred(pending, True, DEFERRED_BUDGET)
                return

            is_dir = entry.kind == KIND_DIRECTORY
            verdict = exclusion_for(entry.path, is_dir=is_dir, applies_to=applies_to,
                                    project_root_markers=markers)
            if verdict is not None:
                yield verdict          # pruned: never enqueued, never listed
                continue
            if is_dir:
                subdirectory_count += 1
                queue.append((entry.path, directory))
            elif entry.kind == KIND_FILE:
                file_count += 1
                mix[PurePath(entry.path).suffix] += 1
                yield ObservedFile(entry.path, entry.size, entry.mtime,
                                   entry.dataless, applies_to)
            else:
                yield Deferred(entry.path, False, DEFERRED_TRAVERSAL_UNRESOLVED)

        yield ObservedDirectory(directory, parent, file_count, subdirectory_count,
                                dict(mix), markers, applies_to)
