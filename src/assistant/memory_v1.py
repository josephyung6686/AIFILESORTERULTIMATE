"""Memory v1: explicit user rules steer proposals; atoms stay dark.

L0 DiffEvents are few-shot INDEX only (never inject untrusted proposals).
Explicit user rules are injected into the system pack so the model can
follow them — that is rules steering, not atom auto-filing.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from assistant.memory_l0 import few_shot_index, ensure_l0_schema

RULES_DDL = """
CREATE TABLE IF NOT EXISTS memory_rules (
    rule_id TEXT PRIMARY KEY,
    rule_text TEXT NOT NULL,
    kind TEXT NOT NULL,
    created_ts TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);
"""


def ensure_rules_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(RULES_DDL)


def add_rule(
        conn: sqlite3.Connection,
        *,
        rule_text: str,
        kind: str = "route",
) -> str:
    ensure_rules_schema(conn)
    text = (rule_text or "").strip()
    if not text:
        raise ValueError("rule_text required")
    rule_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO memory_rules (rule_id, rule_text, kind, created_ts, active) "
        "VALUES (?,?,?,?,1)",
        (rule_id, text, kind, datetime.now(timezone.utc).isoformat()),
    )
    return rule_id


def list_rules(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    ensure_rules_schema(conn)
    rows = conn.execute(
        "SELECT rule_id, rule_text, kind, created_ts FROM memory_rules "
        "WHERE active = 1 ORDER BY created_ts DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def retrieve_for_proposal(
        conn: sqlite3.Connection,
        *,
        query: str,
        limit_rules: int = 5,
        limit_shots: int = 5,
) -> dict[str, Any]:
    """INDEX pack for proposal/ask time.

    rules_steering=True when explicit user rules are present (inject into
    system prompt). atoms_steering always False in v1.
    """
    ensure_rules_schema(conn)
    ensure_l0_schema(conn)
    q = (query or "").casefold()
    rules = list_rules(conn)
    scored = []
    for r in rules:
        text = r["rule_text"].casefold()
        score = sum(1 for tok in q.split() if tok and tok in text)
        scored.append((score, r))
    scored.sort(key=lambda x: -x[0])
    top_rules = [r for _, r in scored[:limit_rules]]
    shots = few_shot_index(conn, limit=limit_shots)
    return {
        "rules": top_rules,
        "few_shot": shots,
        "rules_steering": bool(top_rules),
        "atoms_steering": False,
        "steering": bool(top_rules),  # alias: rules may steer; atoms never
        "query": query,
    }


def format_rules_block(pack: dict[str, Any]) -> str:
    """Compact system-prompt appendix from retrieve_for_proposal."""
    rules = pack.get("rules") or []
    if not rules:
        return ""
    lines = ["User rules (follow when relevant; never move files from these alone):"]
    for r in rules[:5]:
        lines.append(f"- [{r.get('kind', 'rule')}] {r['rule_text']}")
    shots = pack.get("few_shot") or []
    if shots:
        lines.append("Recent expert corrections (INDEX only, not instructions from files):")
        for s in shots[:3]:
            exp = s.get("expert_fix") or {}
            lines.append(
                f"- action={exp.get('action')} reason={exp.get('reason')}"
            )
    return "\n".join(lines)
