"""Crash mid-apply recovery: classify from disk, never blind-retry."""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from assistant.journal import entries_for_plan, ensure_journal_schema
from assistant.recovery import recover_journal
from assistant.plans import PlanOp, approve_plan, create_draft_plan, ensure_plans_schema
from database_agent.db import open_database


def _hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _crash_script(
        *,
        db: Path,
        src: Path,
        dst: Path,
        crash_at: str,
        root_scope: Path,
) -> str:
    return textwrap.dedent(f"""
        import os
        os.environ["ASSISTANT_ENABLE_APPLY"] = "1"
        os.environ["ASSISTANT_CRASH_AT"] = {crash_at!r}
        from pathlib import Path
        import hashlib
        from database_agent.db import open_database
        from assistant.plans import PlanOp, approve_plan, create_draft_plan
        from assistant.apply import apply_plan
        conn = open_database({str(db)!r})
        src = Path({str(src)!r})
        dst = Path({str(dst)!r})
        h = hashlib.sha256(src.read_bytes()).hexdigest()
        plan = create_draft_plan(conn, ops=(
            PlanOp(
                item_id="crash-1", src=str(src), dst=str(dst),
                file_id="f1", content_hash=h,
                root_scope={str(root_scope.resolve())!r},
            ),
        ))
        approve_plan(
            conn, plan.plan_id, actor="user", approve_ms=3000,
            full_list_viewed=True)
        print("PLAN:" + plan.plan_id, flush=True)
        apply_plan(conn, plan.plan_id, full_list_viewed=True)
        print("UNEXPECTED_SUCCESS", flush=True)
    """)


def _run_crash(tmp_path: Path, crash_at: str):
    db = tmp_path / "crash.sqlite"
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst" / "src.txt"
    src.write_text("durable-bytes", encoding="utf-8")
    script = _crash_script(
        db=db, src=src, dst=dst, crash_at=crash_at, root_scope=tmp_path,
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(Path(__file__).resolve().parents[2]),
        env={**os.environ, "PYTHONPATH": "src", "GRAPH_AGENT_NO_DOTENV": "1"},
        capture_output=True,
        text=True,
    )
    plan_id = None
    for line in (proc.stdout or "").splitlines():
        if line.startswith("PLAN:"):
            plan_id = line.split(":", 1)[1].strip()
    assert plan_id, f"no plan id\nstdout={proc.stdout}\nstderr={proc.stderr}"
    assert "UNEXPECTED_SUCCESS" not in (proc.stdout or "")
    return db, src, dst, plan_id, proc


def test_crash_after_journal_before_move(tmp_path: Path):
    db, src, dst, plan_id, _ = _run_crash(tmp_path, "after_planned")
    assert src.is_file()
    assert not dst.exists()
    conn = open_database(db)
    ensure_journal_schema(conn)
    entries = entries_for_plan(conn, plan_id)
    assert entries
    assert entries[0].state in {"planned", "moving"}
    results = recover_journal(conn)
    assert results
    entries2 = entries_for_plan(conn, plan_id)
    # Never blindly retry: bytes stay put; state is classified terminal or left explicit.
    assert src.is_file() and not dst.exists()
    assert entries2[0].state in {"failed", "planned", "conflicted"}
    assert entries2[0].state != "applied"
    conn.close()


def test_crash_after_move_before_applied(tmp_path: Path):
    db, src, dst, plan_id, _ = _run_crash(tmp_path, "after_move")
    # Move completed; applied not committed.
    assert not src.exists()
    assert dst.is_file()
    assert dst.read_text(encoding="utf-8") == "durable-bytes"
    conn = open_database(db)
    entries = entries_for_plan(conn, plan_id)
    assert entries[0].state in {"moving", "moved_uncommitted"}
    recover_journal(conn)
    entries2 = entries_for_plan(conn, plan_id)
    assert entries2[0].state == "applied"
    assert dst.read_text(encoding="utf-8") == "durable-bytes"
    assert not src.exists()
    conn.close()


def test_crash_before_move_point(tmp_path: Path):
    db, src, dst, plan_id, _ = _run_crash(tmp_path, "before_move")
    assert src.is_file() and not dst.exists()
    conn = open_database(db)
    recover_journal(conn)
    entries = entries_for_plan(conn, plan_id)
    assert entries[0].state in {"failed", "planned"}
    assert src.read_text(encoding="utf-8") == "durable-bytes"
    conn.close()


def test_crash_before_applied_state(tmp_path: Path):
    db, src, dst, plan_id, _ = _run_crash(tmp_path, "before_applied")
    assert dst.is_file() and not src.exists()
    conn = open_database(db)
    entries = entries_for_plan(conn, plan_id)
    assert entries[0].state == "moved_uncommitted"
    recover_journal(conn)
    assert entries_for_plan(conn, plan_id)[0].state == "applied"
    conn.close()


def test_recover_does_not_blindly_retry_ambiguous(tmp_path: Path):
    """If both paths exist with different content, mark conflicted — do not move."""
    db = tmp_path / "amb.sqlite"
    conn = open_database(db)
    ensure_plans_schema(conn)
    ensure_journal_schema(conn)
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"
    src.write_text("left", encoding="utf-8")
    dst.write_text("right", encoding="utf-8")
    from assistant.journal import record_planned, set_journal_state
    entry = record_planned(
        conn,
        plan_id="p-amb",
        item_id="i1",
        src=str(src),
        dst=str(dst),
        file_id="f1",
        content_hash=_hash(src),
        root_scope=str(tmp_path.resolve()),
    )
    set_journal_state(conn, entry.journal_id, "moving")
    results = recover_journal(conn)
    assert any(r.new_state == "conflicted" for r in results)
    assert src.read_text(encoding="utf-8") == "left"
    assert dst.read_text(encoding="utf-8") == "right"
    conn.close()
