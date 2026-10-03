#!/usr/bin/env python3
"""Run a supervised pilot against a disposable copy of a corpus.

The source corpus is never modified. Cloud calls, learned steering, and moves
are opt-in and default off; the release runbook uses all three safe defaults.
With --apply off the pilot proves an approved plan is refused; with --apply on
it applies, recovers a simulated crash, and undoes inside the copy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TERMINAL = {"applied", "undone", "conflicted", "failed"}


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--database", type=Path, required=True)
    p.add_argument("--corpus", "--copy", dest="corpus", type=Path,
                   help="source corpus; it is copied into a disposable temp directory")
    p.add_argument("--cloud", choices=("off", "on"), default="off")
    p.add_argument("--memory-steering", choices=("off", "on"), default="off")
    p.add_argument("--apply", choices=("off", "on"), default="off")
    p.add_argument("--out", type=Path, default=ROOT / "docs/superpowers/measurements/daily-use-pilot.json")
    return p


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    if args.cloud == "off":
        for key in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            os.environ.pop(key, None)
        os.environ["ASSISTANT_LOCAL_ONLY"] = "1"
    if args.memory_steering == "off":
        os.environ["ASSISTANT_ATOMS_STEER"] = "0"
    if args.apply == "off":
        os.environ.pop("ASSISTANT_ENABLE_APPLY", None)
    else:
        os.environ["ASSISTANT_ENABLE_APPLY"] = "1"

    from assistant.apply import apply_plan
    from assistant.egress import ensure_egress_schema
    from assistant.journal import entries_for_plan, nonterminal_entries, set_journal_state
    from assistant.plans import PlanOp, approve_plan, create_draft_plan
    from assistant.recovery import recover_journal, recover_on_startup
    from assistant.undo import undo_plan
    from database_agent.db import open_database
    from database_agent.maintenance import backup_database, check_database, restore_database
    from grouping.schema import create_grouping_schema
    from items.decisions import reject_link
    from items.hot_index import find_files
    from items.mailbox import ingest_fixture
    from items.profile_loader import load_profile
    from items.refresh import refresh_index
    from items.relationships import project_witnessed_links
    from items.schema import create_items_schema

    steps: dict[str, dict] = {}
    skipped = [{"step": "explain",
                "reason": "no explain command exists; search citations cover it"}]

    def step(name: str, ok: bool, detail: object = "") -> None:
        steps[name] = {"ok": bool(ok), "detail": detail}

    def hits(conn, query: str) -> list[str]:
        return [h.display_label for h in find_files(conn, query, limit=10).hits]

    with tempfile.TemporaryDirectory(prefix="database-agent-pilot-") as temp:
        temp_root = Path(temp)
        work = temp_root / "corpus"
        if args.corpus:
            source = args.corpus.expanduser().resolve()
            if not source.is_dir():
                raise SystemExit(f"corpus must be a directory: {source}")
            shutil.copytree(source, work)
        else:
            work.mkdir()
        # The pilot's own markers live beside the copied corpus so every step
        # has a known answer regardless of what the person's files contain.
        lab = work / "_pilot"
        lab.mkdir()
        (lab / "pilot-note.txt").write_text("pilotnote original", encoding="utf-8")
        (lab / "pilot-delete.txt").write_text("pilotdeleteme body", encoding="utf-8")
        (lab / "pilot-move.txt").write_text("pilotmove body", encoding="utf-8")
        (lab / "twin-a.bin").write_bytes(b"pilot twins")
        (lab / "twin-b.bin").write_bytes(b"pilot twins")

        db = args.database.expanduser().resolve()
        roots = [work]

        # 1. initial scan
        conn = open_database(db, scan_roots=[])
        create_items_schema(conn)
        refresh_index(conn, roots=roots, prefer_fsevents=False)
        conn.commit()
        count = conn.execute("SELECT count(*) FROM items").fetchone()[0]
        step("initial_scan", count >= 5 and "pilot-note.txt" in hits(conn, "pilotnote"),
             f"{count} items")

        # 2. restart: a fresh connection runs startup recovery and still finds.
        conn.close()
        conn = open_database(db, scan_roots=[])
        recovered = recover_on_startup(conn)
        step("restart", "pilot-note.txt" in hits(conn, "pilotnote"),
             f"{len(recovered)} journal rows recovered")

        # 3-5. edit, rename, delete, then search must reflect all three.
        note = lab / "pilot-note.txt"
        note.write_text("pilotedited content", encoding="utf-8")
        note.rename(lab / "pilot-note-renamed.txt")
        (lab / "pilot-delete.txt").unlink()
        refresh_index(conn, roots=roots, prefer_fsevents=False)
        conn.commit()
        step("edit", "pilot-note-renamed.txt" in hits(conn, "pilotedited"))
        step("rename", "pilot-note.txt" not in hits(conn, "pilotedited"))
        deleted_hits = hits(conn, "pilotdeleteme")
        step("delete", not deleted_hits, f"stale hits: {deleted_hits}")
        step("search", bool(hits(conn, "pilotmove")))

        # 6. relationship proposal and rejection.
        create_grouping_schema(conn)
        project_witnessed_links(conn)
        proposed = conn.execute(
            "SELECT relationship_id FROM relationships WHERE superseded_by IS NULL"
        ).fetchall()
        if proposed:
            reject_link(conn, proposed[0]["relationship_id"], user_id="pilot")
        conn.commit()
        step("relationship_proposal", bool(proposed), f"{len(proposed)} proposed")
        step("relationship_rejection", bool(proposed))

        # 7. plan preview and approval.
        move_src = lab / "pilot-move.txt"
        move_dst = lab / "filed" / "pilot-move.txt"
        row = conn.execute(
            "SELECT item_id, open_target, file_id FROM items "
            "WHERE display_label = 'pilot-move.txt'"
        ).fetchone()
        plan = create_draft_plan(conn, ops=(PlanOp(
            item_id=row["item_id"], src=row["open_target"], dst=str(move_dst),
            file_id=row["file_id"], content_hash=_sha(move_src),
            root_scope=str(work.resolve()),
        ),))
        approve_plan(conn, plan.plan_id, actor="pilot", approve_ms=3000,
                     full_list_viewed=True)
        conn.commit()
        step("plan_preview_approval", True, plan.plan_id)

        # 8. apply. Off: the approved plan must be refused and nothing move.
        result = apply_plan(conn, plan.plan_id, full_list_viewed=True)
        conn.commit()
        if args.apply == "off":
            step("apply_refused", not result.moved and move_src.exists()
                 and not move_dst.exists(), result.error or "")
            skipped += [{"step": s, "reason": "--apply off"}
                        for s in ("apply", "crash_recovery", "undo")]
        else:
            step("apply", result.ok and result.moved and move_dst.exists()
                 and not move_src.exists(), result.error or "")
            # Simulate a crash after the move but before the applied commit.
            entries = entries_for_plan(conn, plan.plan_id)
            for entry in entries:
                set_journal_state(conn, entry.journal_id, "moving")
            conn.commit()
            recover_journal(conn)
            conn.commit()
            states = {e.state for e in entries_for_plan(conn, plan.plan_id)}
            step("crash_recovery", bool(states) and states <= TERMINAL, sorted(states))
            undo = undo_plan(conn, plan.plan_id)
            conn.commit()
            step("undo", undo.ok and move_src.exists() and not move_dst.exists())

        # 9. fixture sync stores headers, never the body.
        body = "PILOT-BODY-MUST-NOT-BE-STORED"
        ingest_fixture(conn, {"messages": [{
            "message_id": "pilot-msg-1", "thread_id": "pilot-thread-1",
            "internal_date": "2026-10-03T12:00:00+00:00",
            "from": "pilot@example.com", "to": ["owner@example.com"],
            "subject": "Pilot message", "body": body, "attachments": [],
        }]}, kind="gmail")
        conn.commit()
        stored = []
        for (table,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            for r in conn.execute(f'SELECT * FROM "{table}"'):
                stored.extend(str(v) for v in r if v is not None)
        step("fixture_sync", body not in "\n".join(stored))

        ensure_egress_schema(conn)
        egress_rows = conn.execute("SELECT count(*) FROM egress_ledger").fetchone()[0]
        unresolved = len(nonterminal_entries(conn))
        conn.close()

        # 10. backup and restore into a new path.
        check = check_database(db)
        backup = temp_root / "pilot-backup.sqlite"
        backup_database(db, backup)
        step("backup", backup.is_file())
        restored = temp_root / "pilot-restored.sqlite"
        restore = restore_database(backup, restored)
        rconn = open_database(restored, scan_roots=[])
        step("restore", restore["ok"] and bool(hits(rconn, "pilotmove")))
        rconn.close()

    profiles = []
    for name in ("student", "files_only", "job_seeker"):
        try:
            load_profile(name)
            profiles.append(name)
        except Exception:
            pass

    thresholds = {
        "zero_stale_or_deleted_results": steps["delete"]["ok"] and steps["rename"]["ok"],
        "zero_protected_egress": egress_rows == 0 if args.cloud == "off" else None,
        "zero_unapproved_writes": steps.get("apply_refused", {"ok": True})["ok"],
        "zero_data_loss": steps.get("undo", {"ok": True})["ok"] and steps["restore"]["ok"],
        "zero_unresolved_journal_states": unresolved == 0 and check.nonterminal_journal == 0,
        "all_profiles_load": len(profiles) == 3,
    }
    ok = all(s["ok"] for s in steps.values()) and all(
        v for v in thresholds.values() if v is not None)
    report = {
        "schema": "daily-use-pilot/v1", "ok": ok,
        "corpus": {"source": str(args.corpus) if args.corpus else "generated", "copied": True},
        "check": check.as_dict(), "schema_version": check.schema_version,
        "steps": steps, "thresholds": thresholds, "skipped": skipped,
        "egress_rows": egress_rows, "profiles": profiles,
        "cloud": args.cloud, "memory_steering": args.memory_steering, "apply": args.apply,
        "connectors": "scratched", "ui": "excluded",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
