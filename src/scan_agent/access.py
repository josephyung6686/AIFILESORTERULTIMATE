# src/scan_agent/access.py
"""11-ops-runtime.md §1 — Full Disk Access before traversing a protected folder.

"Full Disk Access is required before P3 may scan Desktop, Downloads, Documents, or
any user-selected root that TCC protects. Until it is granted, P3 does not traverse;
P13 shows why."

P3 holds NO list of protected paths and does not decide which folders TCC covers.
It attempts to list each selected root; a TCC refusal arrives as PermissionError,
and that is the whole test. A root that is simply absent is not a permission problem
and is left to the traversal (SPEC Q14 is open on disappearance).
"""
from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path


class FullDiskAccessRequired(Exception):
    """11-ops-runtime.md §1 — until access is granted, P3 does not traverse."""


def unreadable_roots(roots: Iterable[Path]) -> tuple[Path, ...]:
    """The selected roots this process cannot list."""
    denied: list[Path] = []
    for root in roots:
        try:
            with os.scandir(root) as listing:
                next(iter(listing), None)
        except PermissionError:
            denied.append(Path(root))
        except (FileNotFoundError, NotADirectoryError):
            continue
    return tuple(denied)


def require_access(roots: Iterable[Path]) -> None:
    """Run once, before the first directory is listed.

    A scan with one unreadable root performs zero traversal rather than a partial
    one: §8.6 requires the difference between completed and deferred work to be
    visible, and a corpus quietly missing a whole root is not.
    """
    denied = unreadable_roots(roots)
    if denied:
        raise FullDiskAccessRequired(
            "Full Disk Access is required before traversing "
            + ", ".join(str(root) for root in denied)
            + " (11-ops-runtime.md §1)"
        )
