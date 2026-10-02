#!/usr/bin/env python3
"""Live BYOK dogfood: real DeepSeek API turns over a temp bilingual corpus.

Writes trajectory evidence (txt + json). Does NOT enable apply by default.
Also exercises --local-only index path (no cloud) in the same run.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


CORPUS = {
    "03-09-Joint PMFs.pdf": (
        "joint probability mass function lecture notes conditioning"
    ),
    "Joseph Yung resume updated.pdf": "resume georgetown prep joseph yung",
    "作業講義_統計.pdf": "homework 作業 講義 probability course",
    "稅務報表_2024.pdf": "tax filing 稅務 報表 annual",
    "保險保單.pdf": "insurance policy 保險 保單",
    "Conditioning RV.pdf": "conditioning random variables notes",
}


QUESTIONS = [
    "Where is the Joint PMFs lecture PDF?",
    "Find my resume",
    "找作業講義",
    "稅務報表在哪",
]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--out", type=Path,
        default=ROOT / "docs/superpowers/measurements/"
        "2026-10-02-live-byok-dogfood.txt")
    p.add_argument(
        "--out-json", type=Path,
        default=ROOT / "docs/superpowers/measurements/"
        "2026-10-02-live-byok-dogfood.json")
    p.add_argument("--max-questions", type=int, default=4)
    p.add_argument(
        "--with-apply", action="store_true",
        help="Also dogfood gated apply/undo on a temp file (sets env).")
    args = p.parse_args(argv)

    from assistant.provider import load_dotenv, resolve_provider
    from assistant.chat import ask, format_answer
    from assistant.memory_v1 import add_rule
    from assistant.local_model import capability_lines
    from database_agent.db import open_database
    from items.hot_index import rebuild_fts
    from items.identity import reconcile_tree
    from items.schema import create_items_schema

    load_dotenv(ROOT / ".env")
    try:
        cfg = resolve_provider()
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 2

    traj = {
        "provider": cfg.provider,
        "model": cfg.model,
        "base_url": cfg.base_url,
        "capability": capability_lines(),
        "turns": [],
        "local_only": None,
        "api_calls": True,
    }

    lines: list[str] = [
        f"# Live BYOK dogfood {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"provider={cfg.provider} model={cfg.model}",
        f"capability: {'; '.join(capability_lines())}",
        "",
    ]

    with tempfile.TemporaryDirectory(prefix="ga-dogfood-") as td:
        root = Path(td) / "lib"
        root.mkdir()
        for name, body in CORPUS.items():
            (root / name).write_text(body, encoding="utf-8")
        db = Path(td) / "t.sqlite"
        conn = open_database(db, scan_roots=[])
        create_items_schema(conn)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS evidence ("
            "evidence_id TEXT PRIMARY KEY, file_id TEXT, raw_value TEXT, "
            "superseded_by TEXT)"
        )
        reconcile_tree(conn, root)
        for row in conn.execute(
            "SELECT item_id, file_id, display_label FROM items"
        ):
            body = CORPUS.get(row["display_label"], "")
            if row["file_id"] and body:
                conn.execute(
                    "INSERT INTO evidence VALUES (?,?,?,NULL)",
                    (f"e-{row['item_id']}", row["file_id"], body),
                )
        rebuild_fts(conn)
        add_rule(
            conn,
            rule_text="Georgetown PDFs go under Coursework/Georgetown",
            kind="route",
        )
        conn.commit()

        # Local-only (no cloud) first
        local = ask(conn, "Where is Joint PMFs?", local_only=True)
        traj["local_only"] = {
            "provider": local.provider,
            "model": local.model,
            "citations": list(local.citations),
            "moved": local.moved,
            "text_head": local.text[:240],
        }
        lines.append("## local-only (no cloud)")
        lines.append(format_answer(local))
        lines.append("")

        for i, q in enumerate(QUESTIONS[: args.max_questions]):
            print(f"API turn {i+1}: {q!r} …", flush=True)
            t0 = time.perf_counter()
            answer = ask(
                conn, q,
                session_id=f"dogfood-{int(time.time())}-{i}",
                local_only=False,
            )
            ms = (time.perf_counter() - t0) * 1000.0
            entry = {
                "question": q,
                "provider": answer.provider,
                "model": answer.model,
                "total_ms": answer.total_ms,
                "wall_ms": ms,
                "citations": list(answer.citations),
                "tools": [
                    {"tool": t.tool, "ok": t.ok, "ms": t.ms}
                    for t in answer.turns
                ],
                "moved": answer.moved,
                "egress_bytes": answer.egress_bytes,
                "text_head": (answer.text or "")[:400],
            }
            traj["turns"].append(entry)
            lines.append(f"## turn {i+1}: {q}")
            lines.append(format_answer(answer))
            lines.append("")
            # Hard fail if somehow no API path was used
            if answer.provider == "local":
                print("FAIL: expected cloud provider", file=sys.stderr)
                return 3

        # Gated write dogfood (tools path — not model inventing moves)
        if args.with_apply:
            import hashlib
            from assistant.plans import PlanOp, approve_plan, create_draft_plan
            from assistant.tools import ToolRuntime
            os.environ["ASSISTANT_ENABLE_APPLY"] = "1"
            src = root / "to_file.pdf"
            src.write_text("apply-dogfood", encoding="utf-8")
            dst = root / "filed" / "to_file.pdf"
            h = hashlib.sha256(src.read_bytes()).hexdigest()
            plan = create_draft_plan(conn, ops=(
                PlanOp(item_id="dog-1", src=str(src), dst=str(dst),
                       content_hash=h),
            ))
            approve_plan(
                conn, plan.plan_id, actor="user", approve_ms=3000,
                full_list_viewed=True)
            rt = ToolRuntime(conn)
            rt.execute("request_tools", {"group": "organize_apply"})
            applied = rt.execute("apply_moves", {
                "plan_id": plan.plan_id, "full_list_viewed": True,
            })
            undid = rt.execute("undo_moves", {"plan_id": plan.plan_id})
            traj["apply_undo"] = {
                "apply_ok": applied.ok,
                "apply_moved": applied.payload.get("moved"),
                "undo_ok": undid.ok,
                "undo_moved": undid.payload.get("moved"),
                "src_restored": src.exists() and src.read_text() == "apply-dogfood",
            }
            lines.append("## apply/undo (gated tool path)")
            lines.append(json.dumps(traj["apply_undo"], indent=2))
            lines.append("")

        conn.close()

    # Require at least one citation across live turns
    cited = any(t["citations"] for t in traj["turns"])
    apply_ok = (
        not args.with_apply
        or (traj.get("apply_undo") or {}).get("src_restored") is True
    )
    traj["ok"] = bool(cited and traj["local_only"]["citations"] and apply_ok)
    lines.append(
        f"## summary ok={traj['ok']} live_turns={len(traj['turns'])} "
        f"apply={args.with_apply}"
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    args.out_json.write_text(
        json.dumps(traj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"wrote {args.out_json}")
    print(json.dumps({
        "ok": traj["ok"],
        "live_turns": len(traj["turns"]),
        "provider": traj["provider"],
        "model": traj["model"],
    }, indent=2))
    return 0 if traj["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
