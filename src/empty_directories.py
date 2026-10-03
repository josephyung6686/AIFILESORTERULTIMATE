"""Empty directories are listed, and removed only when the answer is yes.

A directory is empty when it contains no files. Zero placements are not
that fact. The scan root is never removed. Nothing here deletes a file.
"""
from __future__ import annotations

import os
from pathlib import Path

__all__ = ["apply_empty_removal", "empty_directories"]


def empty_directories(root: Path) -> tuple[Path, ...]:
    """Directories under `root` that contain no files. The root itself stays.

    Symlinks are not walked and are not listed. A directory of empty
    directories is empty. Order is deepest first so a later removal can
    remove a parent after its children.
    """
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        return ()
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        kept: list[str] = []
        for name in dirnames:
            child = current / name
            if not child.is_symlink():
                kept.append(name)
        dirnames[:] = kept
        if current.resolve() == root.resolve():
            continue
        if current.is_symlink():
            continue
        if not _contains_file(current):
            found.append(current)
    found.sort(key=lambda path: len(path.parts), reverse=True)
    return tuple(found)


def apply_empty_removal(root: Path, *, confirm: str) -> tuple[str, tuple[Path, ...]]:
    """List the empty directories. Remove them only when `confirm` is yes.

    Any other value, including the default ``no``, removes nothing. The
    message names the listed set and the flag that confirms it.
    """
    listed = empty_directories(root)
    if not listed:
        return "", ()
    lines = [
        "Empty folders (no files on disk). Nothing is removed unless you confirm:",
    ]
    lines.extend(f"  {path}" for path in listed)
    lines.append(
        "Confirm with --remove-empty yes to remove this listed set. "
        "Any other answer leaves them.")
    message = "\n".join(lines)
    if (confirm or "").strip().lower() != "yes":
        return message, ()
    removed: list[Path] = []
    for path in listed:
        if path.is_symlink() or not path.is_dir():
            continue
        if _contains_file(path) or any(path.iterdir()):
            continue
        path.rmdir()
        removed.append(path)
    return message, tuple(removed)


def _contains_file(path: Path) -> bool:
    if path.is_symlink() or not path.is_dir():
        return False
    for dirpath, dirnames, filenames in os.walk(path, followlinks=False):
        current = Path(dirpath)
        dirnames[:] = [
            name for name in dirnames
            if not (current / name).is_symlink()]
        if filenames:
            return True
    return False
