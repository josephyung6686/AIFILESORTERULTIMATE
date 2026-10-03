"""The Mac window's calls into the engine.

One SQLite database. Saving writes the answers file the scan already reads.
A scan refuses to start when answers are unfinished or folder access is
missing. The scan that does start does not move or rename files. Moving or
renaming on disk is a paid action and stays off.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path

from empty_directories import empty_directories
from onboarding.snapshot import ScanRefused, prepare_engine_scan

_STANDARD = {"Documents": "Documents", "Downloads": "Downloads", "Desktop": "Desktop"}
_MOVE_FLAGS = ("--apply", "--apply-everything", "--undo", "--undo-everything")


def empty_briefing() -> dict:
    """No scan has finished. Counts stay empty rather than becoming zeroes."""
    return {
        "complete": False,
        "found": None,
        "held": None,
        "unplaced": None,
        "review": None,
    }


def resolve_granted(snapshot: dict, *, home: Path) -> list[Path]:
    """Folders the person granted, under `home`. This does not read them.

    A name such as Documents is `home / Documents`. It is never the
    machine's own Downloads folder unless `home` is that machine's home
    and she granted Downloads.
    """
    if not isinstance(snapshot, dict):
        return []
    access = snapshot.get("folderAccess")
    if not isinstance(access, dict) or access.get("state") != "granted":
        return []
    folders = access.get("folders")
    if not isinstance(folders, list):
        return []
    found: list[Path] = []
    for raw in folders:
        if not isinstance(raw, str) or not raw.strip():
            continue
        text = raw.strip()
        candidate = Path(text)
        if candidate.is_absolute():
            path = candidate
        else:
            path = home / _STANDARD.get(text, text)
        if not path.is_dir() or path.is_symlink():
            continue
        resolved = path.resolve()
        if resolved not in found:
            found.append(resolved)
    return found


def build_scan_argv(roots: list[Path], *, database: Path, answers: Path,
                    user: str, paid_moves: bool = False) -> list[str]:
    """The one plan scan. It never includes a flag that moves or renames.

    `paid_moves` is the paid path. It is off. Turning it on does not add
    `--apply`; this build refuses instead of moving files.
    """
    if paid_moves:
        raise ScanRefused(
            "Moving or renaming files on disk is a paid action and is not on.")
    if not roots:
        raise ScanRefused("Allow folder access before scanning")
    database = database.expanduser().resolve()
    for root in roots:
        root = root.resolve()
        if database == root or root in database.parents:
            raise ScanRefused(
                "The database cannot sit inside a folder being read.")
    primary, *rest = roots
    argv = [
        str(primary),
        "--user", user,
        "--database", str(database),
        "--answers", str(answers),
        "--accept-groups",
    ]
    for extra in rest:
        argv.extend(["--also-read", str(extra)])
    for token in argv:
        if token in _MOVE_FLAGS or token.startswith("--apply") or token.startswith("--undo"):
            raise ScanRefused("A normal scan does not move or rename files.")
    return argv


def _file_snapshot(roots: list[Path]) -> dict[str, bytes]:
    found: dict[str, bytes] = {}
    for root in roots:
        for path in root.rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue
            found[str(path.resolve())] = path.read_bytes()
    return found


def _tables(conn: sqlite3.Connection) -> set[str]:
    return {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")
    }


def _file_id_from_subject(subject_ref: str) -> str | None:
    if not subject_ref.startswith("file:"):
        return None
    rest = subject_ref[len("file:"):]
    file_id, separator, _content_hash = rest.partition(":")
    if not separator or not file_id:
        return None
    return file_id


def review_files(database: Path) -> list[dict] | None:
    """Files the plan did not place. None when the database has no such rows.

    An empty list means the scan stored decisions and none need review.
    """
    if not database.is_file():
        return None
    conn = sqlite3.connect(database)
    try:
        tables = _tables(conn)
        if "files" not in tables or "placement_decisions" not in tables:
            return None
        try:
            decisions = conn.execute(
                "SELECT subject_ref, outcome FROM placement_decisions "
                "WHERE superseded_by IS NULL"
            ).fetchall()
            paths = {
                row[0]: row[1]
                for row in conn.execute(
                    "SELECT file_id, current_path FROM files")
            }
        except sqlite3.OperationalError:
            return None
    finally:
        conn.close()
    listed: list[dict] = []
    seen: set[str] = set()
    for subject_ref, outcome in decisions:
        if outcome == "place":
            continue
        file_id = _file_id_from_subject(str(subject_ref))
        if file_id is None or file_id in seen:
            continue
        current = paths.get(file_id)
        if not current:
            continue
        seen.add(file_id)
        listed.append({"path": current, "name": Path(current).name})
    return listed


def briefing_from_database(database: Path) -> dict:
    """Counts from the one database after a scan that finished.

    A missing table stays None. It is not reported as zero.
    """
    briefing = empty_briefing()
    if not database.is_file():
        return briefing
    conn = sqlite3.connect(database)
    try:
        tables = _tables(conn)
        if "files" not in tables:
            return briefing
        found = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        held = None
        if "classifications" in tables:
            try:
                held = conn.execute(
                    "SELECT COUNT(DISTINCT file_id) FROM classifications "
                    "WHERE superseded_by IS NULL AND "
                    "(protected = 1 OR privacy_class IN "
                    "('protected', 'always_local'))"
                ).fetchone()[0]
            except sqlite3.OperationalError:
                held = None
    finally:
        conn.close()
    review = review_files(database)
    briefing["complete"] = True
    briefing["found"] = int(found)
    briefing["held"] = None if held is None else int(held)
    if review is None:
        briefing["unplaced"] = None
        briefing["review"] = None
    else:
        briefing["unplaced"] = len(review)
        briefing["review"] = len(review)
    return briefing


def outline_text(database: Path) -> str:
    path = database.parent / "proposed-structure.txt"
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def empty_folder_rows(roots: list[Path]) -> list[dict]:
    """Directories with zero files on disk. The scan root itself is not listed."""
    rows: list[dict] = []
    seen: set[Path] = set()
    for root in roots:
        for path in empty_directories(root):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            rows.append({"path": str(resolved), "name": resolved.name})
    return rows


class CompanionService:
    """Save, scan, and the workspace. One answers file and one database."""

    def __init__(self, *, home: Path, answers: Path, database: Path,
                 user: str = "you") -> None:
        self.home = Path(home)
        self.answers = Path(answers)
        self.database = Path(database)
        self.user = user
        self.last_argv: list[str] = []

    def save_answers(self, snapshot: dict) -> dict:
        try:
            prepare_engine_scan(snapshot, self.answers)
        except ScanRefused as refused:
            return {"ok": False, "error": str(refused)}
        return {"ok": True}

    def scan(self, snapshot: dict, *, paid_moves: bool = False) -> dict:
        """Refuse before any folder is walked when answers or access are missing."""
        try:
            prepare_engine_scan(snapshot, self.answers)
            roots = resolve_granted(snapshot, home=self.home)
            if not roots:
                access = snapshot.get("folderAccess") if isinstance(snapshot, dict) else None
                granted = isinstance(access, dict) and access.get("state") == "granted"
                raise ScanRefused(
                    "The chosen folder is not on this Mac."
                    if granted else "Allow folder access before scanning")
            argv = build_scan_argv(
                roots, database=self.database, answers=self.answers,
                user=self.user, paid_moves=paid_moves)
        except ScanRefused as refused:
            return {"ok": False, "error": str(refused), "briefing": empty_briefing()}
        before = _file_snapshot(roots)
        self.last_argv = list(argv)
        import cli
        out = io.StringIO()
        code = cli.main(argv, out=out)
        after = _file_snapshot(roots)
        if before != after:
            return {
                "ok": False,
                "error": "The scan changed files on disk. That is not allowed.",
                "briefing": empty_briefing(),
            }
        if code != 0:
            lines = [line for line in out.getvalue().splitlines() if line.strip()]
            message = lines[-1] if lines else "The scan did not finish."
            return {"ok": False, "error": message, "briefing": empty_briefing()}
        return {"ok": True, "briefing": briefing_from_database(self.database)}

    def workspace(self, snapshot: dict) -> dict:
        roots = resolve_granted(snapshot, home=self.home)
        review = review_files(self.database)
        return {
            "ok": True,
            "outline": outline_text(self.database),
            "review": review or [],
            "emptyFolders": empty_folder_rows(roots),
        }

    def remove_empty(self, path: str, confirm: str, snapshot: dict) -> dict:
        """Remove one listed folder only when she says yes and it has no files."""
        if (confirm or "").strip().lower() != "yes":
            return {"ok": True, "removed": False}
        roots = resolve_granted(snapshot, home=self.home)
        target = Path(path).expanduser()
        if not target.is_absolute():
            return {"ok": False, "removed": False, "error": "That folder is not in the list."}
        try:
            resolved = target.resolve()
        except OSError:
            return {"ok": False, "removed": False, "error": "That folder is not in the list."}
        inside = None
        for root in roots:
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                continue
            inside = root
            break
        if inside is None:
            return {
                "ok": False, "removed": False,
                "error": "That folder is not in a folder you opened.",
            }
        listed = {item.resolve() for item in empty_directories(inside)}
        if resolved not in listed or resolved.is_symlink() or not resolved.is_dir():
            return {
                "ok": False, "removed": False,
                "error": "That folder has files on disk.",
            }
        if any(resolved.iterdir()):
            return {
                "ok": False, "removed": False,
                "error": "That folder still has something in it.",
            }
        if resolved not in {item.resolve() for item in empty_directories(inside)}:
            return {
                "ok": False, "removed": False,
                "error": "That folder has files on disk.",
            }
        resolved.rmdir()
        return {"ok": True, "removed": True}
