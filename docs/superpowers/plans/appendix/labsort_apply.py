"""The only component that writes to the lab folder.

Contract:
  * The journal record is written and fsynced BEFORE the corresponding disk change.
  * A group is atomic: if any member fails, the whole group is rolled back and the
    run stops. Groups already committed stay committed and stay undoable.
  * Nothing is ever overwritten. Exclusive creation is enforced by the filesystem
    (os.link / O_EXCL), not by a stat() check, so there is no TOCTOU window.
  * Undo is written first and tested first. Build it before the mover.
"""

from __future__ import annotations

import errno
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, Sequence

from .model import AUTO_MOVE, Decision, FileRef, Group, Plan

LINK_UNSUPPORTED = {errno.EPERM, errno.EOPNOTSUPP, errno.EMLINK, errno.EACCES}


class CollisionError(OSError):
    """Destination exists with different content. Never resolved by overwriting."""


class Journal:
    """Append-only JSONL, fsynced per record.

    Durability is the whole point: a crash between two moves must leave a file on
    disk that undo can read. Buffered writes would defeat that.
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a", encoding="utf-8")

    def write(self, **record) -> None:
        self._fh.write(json.dumps(record, sort_keys=True) + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())

    def close(self) -> None:
        self._fh.close()

    @staticmethod
    def read(path: Path) -> list[dict]:
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as fh:
            return [json.loads(line) for line in fh if line.strip()]


def _fsync_dir(path: Path) -> None:
    """Renames are only durable once the containing directory is synced."""
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def move_exclusive(src: Path, dst: Path) -> None:
    """Move src to dst, guaranteeing dst did not previously exist.

    Same volume: hardlink then unlink. os.link raises EEXIST if dst is taken, which
    is exactly the guard we want, and the source survives until the link succeeds.

    Cross volume (EXDEV) or a filesystem without hardlinks (FAT32 on a USB stick,
    which this will meet): copy into a temp file in the destination directory,
    fsync it, publish it with os.link, then unlink the source. The source is only
    removed after the destination is durable.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except FileExistsError:
        raise CollisionError(errno.EEXIST, "destination exists", str(dst)) from None
    except OSError as exc:
        if exc.errno != errno.EXDEV and exc.errno not in LINK_UNSUPPORTED:
            raise
        _copy_publish_unlink(src, dst)
        return
    os.unlink(src)
    _fsync_dir(dst.parent)


def _copy_publish_unlink(src: Path, dst: Path) -> None:
    fd, tmp_name = tempfile.mkstemp(dir=dst.parent, prefix=".labsort-", suffix=".partial")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as out, open(src, "rb") as inp:
            shutil.copyfileobj(inp, out, length=1024 * 1024)
            out.flush()
            os.fsync(out.fileno())
        shutil.copystat(src, tmp)
        try:
            os.link(tmp, dst)
        except FileExistsError:
            raise CollisionError(errno.EEXIST, "destination exists", str(dst)) from None
        except OSError as exc:
            if exc.errno not in LINK_UNSUPPORTED:
                raise
            try:
                fd2 = os.open(dst, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            except FileExistsError:
                raise CollisionError(errno.EEXIST, "destination exists", str(dst)) from None
            with os.fdopen(fd2, "wb") as out2, open(tmp, "rb") as inp2:
                shutil.copyfileobj(inp2, out2, length=1024 * 1024)
                out2.flush()
                os.fsync(out2.fileno())
        _fsync_dir(dst.parent)
        if FileRef.stat(dst).digest() != FileRef.stat(src).digest():
            os.unlink(dst)
            raise OSError(errno.EIO, "verification failed after copy", str(dst))
        os.unlink(src)
    finally:
        tmp.unlink(missing_ok=True)


@dataclass(frozen=True, slots=True)
class ApplyResult:
    moved_groups: int
    moved_files: int
    skipped_already_filed: int
    collisions: list[str]
    failed_group: Optional[str]
    journal: Path


class Applier:
    def __init__(self, root: Path, journal_dir: Path) -> None:
        self.root = root
        self.journal_dir = journal_dir

    def journal_path(self, run_id: str) -> Path:
        return self.journal_dir / f"{run_id}.jsonl"

    def apply(self, plan: Plan, *, dry_run: bool = True) -> ApplyResult:
        """`dry_run` defaults True. The caller must opt in to touching disk, and the
        UI must default to showing the plan on the first run against a given root."""
        collisions: list[str] = []
        moved_files = moved_groups = skipped = 0
        failed: Optional[str] = None

        if dry_run:
            for dec in plan.auto():
                moved_groups += 1
                moved_files += len(plan.groups[dec.group_id].members)
            return ApplyResult(moved_groups, moved_files, 0, [], None, self.journal_path(plan.run_id))

        jr = Journal(self.journal_path(plan.run_id))
        jr.write(op="run_begin", run_id=plan.run_id, root=str(self.root))
        try:
            for dec in plan.auto():
                group = plan.groups[dec.group_id]
                planned = list(self._plan_moves(group, dec))

                pending, already = self._partition_existing(planned)
                skipped += already
                if pending is None:
                    collisions.append(dec.group_id)
                    jr.write(op="collision", group_id=dec.group_id)
                    continue
                if not pending:
                    continue

                jr.write(op="group_begin", group_id=dec.group_id, files=len(pending))
                done: list[tuple[Path, Path]] = []
                try:
                    for ref, dst in pending:
                        jr.write(
                            op="move", group_id=dec.group_id, src=str(ref.path), dst=str(dst),
                            size=ref.size, mtime_ns=ref.mtime_ns, digest=ref.digest(),
                        )
                        move_exclusive(ref.path, dst)
                        done.append((ref.path, dst))
                except Exception:
                    self._rollback(done, jr, dec.group_id)
                    failed = dec.group_id
                    break
                jr.write(op="group_commit", group_id=dec.group_id)
                moved_groups += 1
                moved_files += len(done)
                self._prune_empty(group, jr)
            jr.write(op="run_end", status="failed" if failed else "ok")
        finally:
            jr.close()

        return ApplyResult(moved_groups, moved_files, skipped, collisions, failed,
                           self.journal_path(plan.run_id))

    def _plan_moves(self, group: Group, dec: Decision) -> Iterator[tuple[FileRef, Path]]:
        dest_dir = self.root / Path(str(dec.destination))
        for ref in group.members:
            yield ref, dest_dir / ref.path.name

    def _partition_existing(self, planned):
        """Destination exists with identical content -> already filed, skip silently.
        Destination exists with different content -> collision, whole group deferred.

        Identity is size plus head/tail digest. Name alone is never enough: the audit
        found `Exp_20260806_1` and `_2` sharing all nine filenames at 3-6 MB and 13 KB.
        """
        pending, already = [], 0
        for ref, dst in planned:
            if not dst.exists():
                pending.append((ref, dst))
                continue
            existing = FileRef.stat(dst)
            if existing.size == ref.size and existing.digest() == ref.digest():
                already += 1
            else:
                return None, already
        return pending, already

    def _rollback(self, done: Sequence[tuple[Path, Path]], jr: Journal, group_id: str) -> None:
        for src, dst in reversed(done):
            try:
                move_exclusive(dst, src)
            except OSError:
                jr.write(op="rollback_failed", group_id=group_id, dst=str(dst), src=str(src))
        jr.write(op="group_rollback", group_id=group_id)

    def _prune_empty(self, group: Group, jr: Journal) -> None:
        """Record every removed directory so undo can recreate it.

        `New Folder-copy-copy` is the only carrier of a capture date for the files
        inside it. Deleting it without journalling would make undo lossy even though
        every file came back.
        """
        seen: set[Path] = set()
        for ref in group.members:
            d = ref.path.parent
            while d != self.root and d not in seen and self.root in d.parents:
                seen.add(d)
                try:
                    next(d.iterdir())
                    break
                except StopIteration:
                    jr.write(op="rmdir", path=str(d))
                    d.rmdir()
                    d = d.parent
                except FileNotFoundError:
                    break


def undo(journal_path: Path) -> tuple[int, list[str]]:
    """Reverse a run. Only moves inside committed groups are reversed.

    Identity is checked before each restore; a mismatch is skipped and reported.
    A destination file that someone edited after the run is never silently clobbered
    back, and the original is never deleted to make undo appear to succeed.
    """
    records = Journal.read(journal_path)
    committed = {r["group_id"] for r in records if r["op"] == "group_commit"}
    moves = [r for r in records if r["op"] == "move" and r["group_id"] in committed]
    rmdirs = [r for r in records if r["op"] == "rmdir"]

    for rec in rmdirs:
        Path(rec["path"]).mkdir(parents=True, exist_ok=True)

    restored, problems = 0, []
    for rec in reversed(moves):
        dst, src = Path(rec["dst"]), Path(rec["src"])
        if not dst.exists():
            problems.append(f"missing: {dst}")
            continue
        cur = FileRef.stat(dst)
        if cur.size != rec["size"] or cur.digest() != rec["digest"]:
            problems.append(f"changed since run, left in place: {dst}")
            continue
        try:
            move_exclusive(dst, src)
            restored += 1
        except CollisionError:
            problems.append(f"original path reoccupied: {src}")
    return restored, problems
