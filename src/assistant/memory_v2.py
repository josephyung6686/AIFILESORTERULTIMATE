"""Memory v2 atoms — dark by default until a version-bound release passes.

Atoms never steer recognition or filing while ``atoms_steering`` is False.
Gate: precision ≥ 0.95 on willing proposals, coverage floor (T-P4-01),
must beat rules-only baseline, min samples, no safety-hold regressions.
Also requires an enabled memory release artifact (see memory_release).
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

from assistant.memory_l0 import source_ids_resolvable

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
    notes TEXT,
    model_version TEXT,
    corpus_version TEXT,
    evidence_json TEXT
);
"""

PRECISION_BAR = 0.95
COVERAGE_FLOOR = 0.20  # 1 - abstention must be ≥ this
MIN_SAMPLES = 20


@dataclass(frozen=True)
class GateResult:
    passed: bool
    precision: float
    abstention: float
    rules_only_precision: float
    n_proposals: int
    notes: str
    model_version: str | None = None
    corpus_version: str | None = None
    coverage: float = 0.0
    safety_hold_regressions: int = 0
    regression_clean: bool = True
    beats_rules: bool = False
    evidence: dict[str, Any] | None = None


def ensure_atoms_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(ATOMS_DDL)
    cols = {
        row[1] for row in conn.execute("PRAGMA table_info(memory_gate_runs)")
    }
    for name, decl in (
        ("model_version", "TEXT"),
        ("corpus_version", "TEXT"),
        ("evidence_json", "TEXT"),
    ):
        if name not in cols:
            conn.execute(
                f"ALTER TABLE memory_gate_runs ADD COLUMN {name} {decl}"
            )


def atoms_steering_allowed(conn: sqlite3.Connection) -> bool:
    """Dark until a version-bound release is enabled and still valid.

    Set ASSISTANT_ATOMS_STEER=0 to force dark even after a passing release.
    """
    if os.environ.get("ASSISTANT_ATOMS_STEER", "").strip() == "0":
        return False
    try:
        from assistant.memory_release import steering_enabled
        return steering_enabled(conn)
    except Exception:
        return False


# Alias
atoms_steering_enabled = atoms_steering_allowed


def add_atom(
        conn: sqlite3.Connection,
        *,
        claim: str,
        source_ids: Sequence[str],
        require_diff_events: bool = True,
) -> str:
    ensure_atoms_schema(conn)
    if not (claim or "").strip():
        raise ValueError("claim required")
    if not source_ids:
        raise ValueError("source_ids required — hard link, no orphan atoms")
    if require_diff_events:
        ok, err = source_ids_resolvable(conn, source_ids)
        if not ok:
            raise ValueError(err)
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
    # New atom invalidates any previously enabled release.
    try:
        from assistant.memory_release import invalidate_releases
        invalidate_releases(conn, reason="new_atom_added")
    except Exception:
        pass
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


def find_contradictory_atoms(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """Pairs of live atoms with reverse-polarity claims (simple heuristic)."""
    live = live_atoms(conn)
    pairs: list[tuple[str, str]] = []
    neg_markers = (" not ", " never ", "≠", "!=")
    for i, a in enumerate(live):
        ca = (a["claim"] or "").casefold().strip()
        for b in live[i + 1:]:
            cb = (b["claim"] or "").casefold().strip()
            if not ca or not cb:
                continue
            # Explicit contradiction markers or A == "not " + B style
            if ca == f"not {cb}" or cb == f"not {ca}":
                pairs.append((a["atom_id"], b["atom_id"]))
                continue
            for m in neg_markers:
                if m in ca and ca.replace(m, " ", 1).split() == cb.split():
                    pairs.append((a["atom_id"], b["atom_id"]))
                    break
                if m in cb and cb.replace(m, " ", 1).split() == ca.split():
                    pairs.append((a["atom_id"], b["atom_id"]))
                    break
    return pairs


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
    try:
        return add_atom(conn, claim=claim, source_ids=[diff_id])
    except ValueError as e:
        return {"ok": False, "error": str(e), "moved": False}


def evaluate_gate(
        *,
        proposals: Sequence[dict[str, Any]],
        gold_accepted: set[str],
        rules_only_accepted: set[str],
        model_version: str | None = None,
        corpus_version: str | None = None,
        min_samples: int = MIN_SAMPLES,
) -> GateResult:
    """Score recorded predictions. Prefer explicit prediction/label fields.

    Each proposal may carry:
      - proposal_id
      - willing / prediction ("accept"|"abstain"|True|False)
      - label / gold (bool or "accept"|"reject")
      - safety_hold (bool) — predicting accept here is a regression
    """
    recorded = []
    for p in proposals:
        pid = str(p["proposal_id"])
        willing = p.get("willing")
        prediction = p.get("prediction")
        if prediction is None:
            if willing is True:
                prediction = "accept"
            elif willing is False:
                prediction = "abstain"
            else:
                prediction = "abstain"
        label = p.get("label")
        if label is None and "gold" in p:
            label = "accept" if p.get("gold") else "reject"
        if label is True:
            label = "accept"
        elif label is False:
            label = "reject"
        recorded.append({
            "proposal_id": pid,
            "prediction": prediction,
            "label": label,
            "safety_hold": bool(p.get("safety_hold")),
        })

    n_total = len(recorded)
    willing = [r for r in recorded if r["prediction"] == "accept"]
    abstaining = [r for r in recorded if r["prediction"] != "accept"]
    n = len(willing)
    if n_total < min_samples:
        return GateResult(
            passed=False, precision=0.0, abstention=1.0,
            rules_only_precision=0.0, n_proposals=n,
            notes=f"insufficient samples n={n_total} min={min_samples}",
            model_version=model_version, corpus_version=corpus_version,
            coverage=0.0, safety_hold_regressions=0,
            regression_clean=False, beats_rules=False,
            evidence={"predictions": recorded, "n_total": n_total},
        )
    if n == 0:
        return GateResult(
            passed=False, precision=0.0, abstention=1.0,
            rules_only_precision=0.0, n_proposals=0,
            notes="no willing proposals — gate fails closed",
            model_version=model_version, corpus_version=corpus_version,
            coverage=0.0,
            evidence={"predictions": recorded, "n_total": n_total},
        )

    # Prefer explicit labels on recorded rows; fall back to gold_accepted set.
    tp = 0
    for r in willing:
        if r["label"] == "accept":
            tp += 1
        elif r["label"] is None and r["proposal_id"] in gold_accepted:
            tp += 1
    precision = tp / n
    abstention = len(abstaining) / max(n_total, 1)
    coverage = 1.0 - abstention

    rules_tp = len(rules_only_accepted & gold_accepted)
    if not gold_accepted:
        # Derive gold from labels when set not provided.
        gold_accepted = {
            r["proposal_id"] for r in recorded if r["label"] == "accept"
        }
        rules_tp = len(rules_only_accepted & gold_accepted)
    rules_n = max(len(rules_only_accepted), 1)
    rules_prec = rules_tp / rules_n
    beats = precision > rules_prec

    safety_regs = sum(
        1 for r in willing if r["safety_hold"]
    )
    regression_clean = safety_regs == 0

    passed = (
        precision >= PRECISION_BAR
        and beats
        and coverage >= COVERAGE_FLOOR
        and n_total >= min_samples
        and regression_clean
    )
    notes = (
        f"precision={precision:.3f} bar={PRECISION_BAR} "
        f"abstention={abstention:.3f} coverage={coverage:.3f} "
        f"rules_only={rules_prec:.3f} beats_rules={beats} "
        f"n={n_total} safety_hold_regressions={safety_regs} "
        f"model={model_version} corpus={corpus_version}"
    )
    evidence = {
        "predictions": [r for r in recorded if r["prediction"] == "accept"],
        "abstentions": [r for r in recorded if r["prediction"] != "accept"],
        "labels": {
            r["proposal_id"]: r["label"] for r in recorded if r["label"]
        },
        "model_version": model_version,
        "corpus_version": corpus_version,
        "rules_only_accepted": sorted(rules_only_accepted),
        "gold_accepted": sorted(gold_accepted),
        "n_total": n_total,
        "safety_hold_regressions": safety_regs,
    }
    return GateResult(
        passed=passed, precision=precision, abstention=abstention,
        rules_only_precision=rules_prec, n_proposals=n, notes=notes,
        model_version=model_version, corpus_version=corpus_version,
        coverage=coverage, safety_hold_regressions=safety_regs,
        regression_clean=regression_clean, beats_rules=beats,
        evidence=evidence,
    )


def record_gate(conn: sqlite3.Connection, result: GateResult) -> str:
    ensure_atoms_schema(conn)
    run_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO memory_gate_runs ("
        "run_id, ts, precision, abstention, rules_only_precision, "
        "n_proposals, passed, notes, model_version, corpus_version, "
        "evidence_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            run_id, datetime.now(timezone.utc).isoformat(),
            result.precision, result.abstention, result.rules_only_precision,
            result.n_proposals, 1 if result.passed else 0, result.notes,
            result.model_version, result.corpus_version,
            json.dumps(result.evidence or {}),
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
            "note": (
                "atoms dark — version-bound release not enabled "
                "(or ASSISTANT_ATOMS_STEER=0)"
            ),
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
