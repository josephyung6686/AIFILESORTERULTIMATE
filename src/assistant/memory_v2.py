"""Memory v2 atoms — dark by default until precision gate passes.

Atoms never steer recognition or filing while ``atoms_steering`` is False.
Gate: precision ≥ 0.95 on willing proposals, coverage floor (T-P4-01),
must beat rules-only baseline. Also requires ASSISTANT_ATOMS_STEER=1.
Dirty (untrusted-session) DiffEvents cannot promote to atoms.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Sequence

ATOMS_DDL = """
CREATE TABLE IF NOT EXISTS memory_atoms (
    atom_id TEXT PRIMARY KEY,
    claim TEXT NOT NULL,
    source_ids_json TEXT NOT NULL,
    created_ts TEXT NOT NULL,
    superseded_by TEXT,
    active INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS memory_atoms_active
    ON memory_atoms(active) WHERE superseded_by IS NULL;
CREATE TABLE IF NOT EXISTS memory_gate_runs (
    run_id TEXT PRIMARY KEY,
    ts TEXT NOT NULL,
    precision REAL NOT NULL,
    abstention REAL NOT NULL,
    rules_only_precision REAL NOT NULL,
    n_proposals INTEGER NOT NULL,
    passed INTEGER NOT NULL,
    notes TEXT
);
"""

PRECISION_BAR = 0.95
COVERAGE_FLOOR = 0.20  # 1 - abstention must be ≥ this


@dataclass(frozen=True)
class GateResult:
    passed: bool
    precision: float
    abstention: float
    rules_only_precision: float
    n_proposals: int
    notes: str


def ensure_atoms_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(ATOMS_DDL)


def atoms_steering_allowed(conn: sqlite3.Connection) -> bool:
    """Dark until a passing gate run is the latest.

    Set ASSISTANT_ATOMS_STEER=0 to force dark even after a passing gate.
    """
    if os.environ.get("ASSISTANT_ATOMS_STEER", "").strip() == "0":
        return False
    ensure_atoms_schema(conn)
    row = conn.execute(
        "SELECT passed FROM memory_gate_runs ORDER BY ts DESC LIMIT 1"
    ).fetchone()
    return bool(row and row["passed"])


# Alias
atoms_steering_enabled = atoms_steering_allowed


def add_atom(
        conn: sqlite3.Connection,
        *,
        claim: str,
        source_ids: Sequence[str],
) -> str:
    ensure_atoms_schema(conn)
    if not (claim or "").strip():
        raise ValueError("claim required")
    if not source_ids:
        raise ValueError("source_ids required — hard link, no orphan atoms")
    atom_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO memory_atoms ("
        "atom_id, claim, source_ids_json, created_ts, superseded_by, active) "
        "VALUES (?,?,?,?,NULL,1)",
        (
            atom_id, claim.strip(),
            json.dumps(list(source_ids)),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    return atom_id


def supersede_atom(
        conn: sqlite3.Connection, atom_id: str, *, replacement_id: str,
) -> None:
    ensure_atoms_schema(conn)
    conn.execute(
        "UPDATE memory_atoms SET superseded_by=?, active=0 WHERE atom_id=?",
        (replacement_id, atom_id),
    )


def live_atoms(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    ensure_atoms_schema(conn)
    rows = conn.execute(
        "SELECT atom_id, claim, source_ids_json, created_ts FROM memory_atoms "
        "WHERE active=1 AND superseded_by IS NULL ORDER BY created_ts DESC"
    ).fetchall()
    out = []
    for r in rows:
        out.append({
            "atom_id": r["atom_id"],
            "claim": r["claim"],
            "rule_text": r["claim"],  # v1 prompt compat
            "kind": "atom",
            "source_ids": json.loads(r["source_ids_json"] or "[]"),
            "created_ts": r["created_ts"],
        })
    return out


def promote_from_diff(
        conn: sqlite3.Connection,
        diff_id: str,
        *,
        claim: str,
) -> str | dict[str, Any]:
    """Human promote L0 → L1. Dirty sessions refuse (stay L0 only)."""
    ensure_atoms_schema(conn)
    from assistant.memory_l0 import ensure_l0_schema
    ensure_l0_schema(conn)
    row = conn.execute(
        "SELECT diff_id, session_flags_json FROM diff_events WHERE diff_id=?",
        (diff_id,),
    ).fetchone()
    if row is None:
        return {"ok": False, "error": "diff not found", "moved": False}
    flags = json.loads(row["session_flags_json"] or "{}")
    if flags.get("session_read_untrusted"):
        return {
            "ok": False,
            "error": "dirty session — L0 only until reviewed; no atom",
            "moved": False,
        }
    return add_atom(conn, claim=claim, source_ids=[diff_id])


def evaluate_gate(
        *,
        proposals: Sequence[dict[str, Any]],
        gold_accepted: set[str],
        rules_only_accepted: set[str],
) -> GateResult:
    """Score willing proposals. Abstention = no proposal id emitted."""
    willing = [p for p in proposals if p.get("willing")]
    n = len(willing)
    if n == 0:
        return GateResult(
            passed=False, precision=0.0, abstention=1.0,
            rules_only_precision=0.0, n_proposals=0,
            notes="no willing proposals — gate fails closed",
        )
    ids = {str(p["proposal_id"]) for p in willing}
    tp = len(ids & gold_accepted)
    precision = tp / n
    abstention = 1.0 - (n / max(len(proposals), 1))
    coverage = 1.0 - abstention
    rules_tp = len(rules_only_accepted & gold_accepted)
    rules_n = max(len(rules_only_accepted), 1)
    rules_prec = rules_tp / rules_n
    beats = precision > rules_prec
    passed = (
        precision >= PRECISION_BAR
        and beats
        and coverage >= COVERAGE_FLOOR
    )
    notes = (
        f"precision={precision:.3f} bar={PRECISION_BAR} "
        f"abstention={abstention:.3f} coverage={coverage:.3f} "
        f"rules_only={rules_prec:.3f} beats_rules={beats}"
    )
    return GateResult(
        passed=passed, precision=precision, abstention=abstention,
        rules_only_precision=rules_prec, n_proposals=n, notes=notes,
    )


def record_gate(conn: sqlite3.Connection, result: GateResult) -> str:
    ensure_atoms_schema(conn)
    run_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO memory_gate_runs ("
        "run_id, ts, precision, abstention, rules_only_precision, "
        "n_proposals, passed, notes) VALUES (?,?,?,?,?,?,?,?)",
        (
            run_id, datetime.now(timezone.utc).isoformat(),
            result.precision, result.abstention, result.rules_only_precision,
            result.n_proposals, 1 if result.passed else 0, result.notes,
        ),
    )
    return run_id


def retrieve_atoms_for_prompt(conn: sqlite3.Connection) -> dict[str, Any]:
    """Never inject atoms while dark."""
    live = live_atoms(conn)
    if not atoms_steering_allowed(conn):
        return {
            "atoms_steering": False,
            "atoms": [],
            "atoms_available": len(live),
            "dark": True,
            "note": "atoms dark — precision gate not passed (or ASSISTANT_ATOMS_STEER=0)",
        }
    return {
        "atoms_steering": True,
        "atoms": live,
        "atoms_available": len(live),
        "dark": False,
    }


# Compat alias for v1 retrieve
def retrieve_atoms_for_proposal(
        conn: sqlite3.Connection,
        *,
        query: str = "",
        limit: int = 5,
) -> dict[str, Any]:
    pack = retrieve_atoms_for_prompt(conn)
    atoms = pack.get("atoms") or []
    if query and atoms:
        q = query.casefold()
        scored = []
        for a in atoms:
            text = (a.get("claim") or a.get("rule_text") or "").casefold()
            score = sum(1 for tok in q.split() if tok and tok in text)
            scored.append((score, a))
        scored.sort(key=lambda x: -x[0])
        atoms = [a for _, a in scored[:limit]]
        pack = {**pack, "atoms": atoms}
    return pack
