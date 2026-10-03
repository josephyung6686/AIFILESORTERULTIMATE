"""Startup / interrupt recovery for assistant_journal nonterminal states.

Never blindly retries a move. Classifies from source/destination existence,
inode relationship, and content hash, then advances only when unambiguous.
"""
from __future__ import annotations

import hashlib
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from assistant.journal import (
    JournalEntry,
    ensure_journal_schema,
    nonterminal_entries,
    set_journal_state,
)


@dataclass(frozen=True)
class RecoveryResult:
    journal_id: str
    plan_id: str
    prior_state: str
    new_state: str
    action: str
    detail: str


def _file_hash(path: Path) -> str | None:
    if not path.exists() or path.is_symlink() or not path.is_file():
        return None
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _same_inode(a: Path, b: Path) -> bool:
    try:
        sa, sb = a.stat(), b.stat()
    except OSError:
        return False
    return sa.st_dev == sb.st_dev and sa.st_ino == sb.st_ino


def _hash_matches(path: Path, expected: str | None) -> bool:
    if not expected:
        return False
    live = _file_hash(path)
    return live is not None and live == expected


def classify_entry(entry: JournalEntry) -> tuple[str, str, str]:
    """Return (new_state, action, detail) without mutating DB or disk."""
    src = Path(entry.src)
    dst = Path(entry.dst)
    src_exists = src.exists()
    dst_exists = dst.exists()
    state = entry.state

    if state == "planned":
        if src_exists and not dst_exists:
            return "failed", "abort_unstarted", "planned but never moved"
        if (not src_exists) and dst_exists and _hash_matches(dst, entry.content_hash):
            return "moved_uncommitted", "observed_move", "dst present after planned"
        if src_exists and dst_exists:
            return "conflicted", "ambiguous", "both paths exist in planned"
        return "failed", "missing_both", "neither path usable"

    if state == "moving":
        if src_exists and not dst_exists:
            return "failed", "abort_before_move", "moving interrupted before dest"
        if (not src_exists) and dst_exists and _hash_matches(dst, entry.content_hash):
            return "moved_uncommitted", "observed_move", "move landed; commit pending"
        if src_exists and dst_exists:
            if _same_inode(src, dst) and _hash_matches(dst, entry.content_hash):
                return (
                    "moved_uncommitted",
                    "finish_hardlink",
                    "same inode at src+dst; drop src name",
                )
            return "conflicted", "ambiguous", "both paths exist with distinct identity"
        return "failed", "missing_both", "moving with neither path"

    if state == "moved_uncommitted":
        if (not src_exists) and dst_exists and _hash_matches(dst, entry.content_hash):
            return "applied", "commit_identity", "complete applied state"
        if src_exists and dst_exists and _same_inode(src, dst):
            return "applied", "finish_hardlink", "complete after unlink src"
        if (not src_exists) and dst_exists:
            return "conflicted", "hash_mismatch", "dst hash != journal"
        if src_exists and not dst_exists:
            return "failed", "move_lost", "moved_uncommitted but dest missing"
        return "conflicted", "ambiguous", "moved_uncommitted unreadable"

    if state == "undo_planned":
        # Undo interrupted: current file should still be at dst (applied location).
        if dst_exists and _hash_matches(dst, entry.content_hash) and not src_exists:
            return "applied", "abort_undo", "undo never started; remain applied"
        if src_exists and not dst_exists and _hash_matches(src, entry.content_hash):
            return "undone", "observed_undo", "undo landed"
        if src_exists and dst_exists:
            return "conflicted", "ambiguous", "undo_planned both paths exist"
        return "conflicted", "undo_unclear", "undo_planned cannot classify"

    return state, "leave", f"terminal or unknown state {state}"


def _finish_hardlink_if_needed(entry: JournalEntry, action: str) -> None:
    if action != "finish_hardlink":
        return
    src = Path(entry.src)
    dst = Path(entry.dst)
    if src.exists() and dst.exists() and _same_inode(src, dst):
        try:
            os.unlink(src)
        except OSError:
            pass


def _commit_identity_if_needed(
        conn: sqlite3.Connection,
        entry: JournalEntry,
        new_state: str,
) -> None:
    if new_state != "applied":
        return
    from assistant.identity_commit import commit_item_path
    commit_item_path(conn, entry.item_id, Path(entry.dst))
    try:
        conn.execute(
            "UPDATE assistant_plans SET state='applied' WHERE plan_id=?",
            (entry.plan_id,),
        )
    except sqlite3.OperationalError:
        pass


def recover_entry(
        conn: sqlite3.Connection,
        entry: JournalEntry,
) -> RecoveryResult:
    ensure_journal_schema(conn)
    new_state, action, detail = classify_entry(entry)
    if new_state == entry.state and action == "leave":
        return RecoveryResult(
            journal_id=entry.journal_id,
            plan_id=entry.plan_id,
            prior_state=entry.state,
            new_state=entry.state,
            action=action,
            detail=detail,
        )

    _finish_hardlink_if_needed(entry, action)

    # Two-step: moving → moved_uncommitted → applied when commit needed.
    if entry.state == "moving" and new_state == "moved_uncommitted":
        set_journal_state(conn, entry.journal_id, "moved_uncommitted")
        # Immediately complete when unambiguous.
        mid = JournalEntry(
            journal_id=entry.journal_id,
            plan_id=entry.plan_id,
            item_id=entry.item_id,
            src=entry.src,
            dst=entry.dst,
            state="moved_uncommitted",
            file_id=entry.file_id,
            content_hash=entry.content_hash,
            root_scope=entry.root_scope,
            protected_snapshot=entry.protected_snapshot,
        )
        final, action2, detail2 = classify_entry(mid)
        if final == "applied":
            _finish_hardlink_if_needed(mid, action2)
            _commit_identity_if_needed(conn, mid, final)
            set_journal_state(conn, entry.journal_id, "applied")
            return RecoveryResult(
                journal_id=entry.journal_id,
                plan_id=entry.plan_id,
                prior_state=entry.state,
                new_state="applied",
                action=action2,
                detail=detail2,
            )
        return RecoveryResult(
            journal_id=entry.journal_id,
            plan_id=entry.plan_id,
            prior_state=entry.state,
            new_state="moved_uncommitted",
            action=action,
            detail=detail,
        )

    if entry.state == "planned" and new_state == "moved_uncommitted":
        set_journal_state(conn, entry.journal_id, "moved_uncommitted")
        _commit_identity_if_needed(conn, entry, "applied")
        set_journal_state(conn, entry.journal_id, "applied")
        return RecoveryResult(
            journal_id=entry.journal_id,
            plan_id=entry.plan_id,
            prior_state=entry.state,
            new_state="applied",
            action="commit_identity",
            detail=detail,
        )

    if new_state == "applied":
        _commit_identity_if_needed(conn, entry, new_state)

    if new_state == "undone":
        from assistant.identity_commit import commit_item_path
        commit_item_path(conn, entry.item_id, Path(entry.src))
        try:
            conn.execute(
                "UPDATE assistant_plans SET state='undone' WHERE plan_id=?",
                (entry.plan_id,),
            )
        except sqlite3.OperationalError:
            pass

    set_journal_state(conn, entry.journal_id, new_state)
    return RecoveryResult(
        journal_id=entry.journal_id,
        plan_id=entry.plan_id,
        prior_state=entry.state,
        new_state=new_state,
        action=action,
        detail=detail,
    )


def recover_journal(conn: sqlite3.Connection) -> list[RecoveryResult]:
    """Scan nonterminal journal rows and classify/repair each one."""
    ensure_journal_schema(conn)
    results: list[RecoveryResult] = []
    for entry in nonterminal_entries(conn):
        results.append(recover_entry(conn, entry))
    return results


def recover_on_startup(conn: sqlite3.Connection) -> list[RecoveryResult]:
    """Alias for process-start recovery."""
    return recover_journal(conn)
