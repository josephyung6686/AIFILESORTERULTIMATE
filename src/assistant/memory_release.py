"""Version-bound memory releases — atoms stay dark until deliberate enable.

A release artifact binds steering to:
  - gate_id (passing evaluation run)
  - corpus_hash
  - evaluator_version
  - model_fingerprint
  - atom source DiffEvent IDs

A new atom or changed model fingerprint invalidates an enabled release.
CLI: ``database-agent memory release`` prints evidence; ``--enable`` is
required to open steering. Default remains dark.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from assistant.memory_l0 import source_ids_resolvable
from assistant.memory_v2 import (
    COVERAGE_FLOOR,
    MIN_SAMPLES,
    PRECISION_BAR,
    GateResult,
    ensure_atoms_schema,
    evaluate_gate,
    find_contradictory_atoms,
    live_atoms,
    record_gate,
)

EVALUATOR_VERSION = "memory-gate-v1"

RELEASE_DDL = """
CREATE TABLE IF NOT EXISTS memory_releases (
    release_id TEXT PRIMARY KEY,
    gate_id TEXT NOT NULL,
    corpus_hash TEXT NOT NULL,
    evaluator_version TEXT NOT NULL,
    model_fingerprint TEXT NOT NULL,
    atom_source_ids_json TEXT NOT NULL,
    evidence_json TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 0,
    created_ts TEXT NOT NULL,
    invalidated_reason TEXT
);
"""


@dataclass(frozen=True)
class ReleaseArtifact:
    release_id: str
    gate_id: str
    corpus_hash: str
    evaluator_version: str
    model_fingerprint: str
    atom_source_ids: tuple[str, ...]
    enabled: bool
    evidence: dict[str, Any]
    invalidated_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["atom_source_ids"] = list(self.atom_source_ids)
        return d


def ensure_release_schema(conn: sqlite3.Connection) -> None:
    ensure_atoms_schema(conn)
    conn.executescript(RELEASE_DDL)


def corpus_hash_of(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def model_fingerprint_of(model_version: str | None) -> str:
    return hashlib.sha256((model_version or "unknown").encode("utf-8")).hexdigest()


def collect_atom_source_ids(conn: sqlite3.Connection) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for atom in live_atoms(conn):
        for sid in atom.get("source_ids") or []:
            if sid not in seen:
                seen.add(sid)
                ids.append(sid)
    return ids


def evaluate_release_gate(
        *,
        proposals: Sequence[dict[str, Any]],
        gold_accepted: set[str] | None = None,
        rules_only_accepted: set[str] | None = None,
        model_version: str,
        corpus_version: str,
        min_samples: int = MIN_SAMPLES,
) -> GateResult:
    """Full gate with recorded predictions / labels / versions."""
    gold = gold_accepted or {
        str(p["proposal_id"]) for p in proposals
        if p.get("gold") or p.get("label") in (True, "accept")
    }
    rules = rules_only_accepted or set()
    return evaluate_gate(
        proposals=proposals,
        gold_accepted=gold,
        rules_only_accepted=rules,
        model_version=model_version,
        corpus_version=corpus_version,
        min_samples=min_samples,
    )


def create_release(
        conn: sqlite3.Connection,
        *,
        gate: GateResult,
        gate_id: str,
        corpus_hash: str,
        model_fingerprint: str,
        atom_source_ids: Sequence[str] | None = None,
        evaluator_version: str = EVALUATOR_VERSION,
) -> ReleaseArtifact:
    """Persist a release artifact. Enabled=False until deliberate enable."""
    ensure_release_schema(conn)
    if not gate.passed:
        raise ValueError("cannot create release from failing gate")
    contradictory = find_contradictory_atoms(conn)
    if contradictory:
        raise ValueError(
            f"contradictory live atoms without supersede: {contradictory}"
        )
    sources = list(atom_source_ids) if atom_source_ids is not None else (
        collect_atom_source_ids(conn)
    )
    ok, err = source_ids_resolvable(conn, sources) if sources else (True, "")
    if sources and not ok:
        raise ValueError(err)
    release_id = str(uuid.uuid4())
    evidence = {
        "gate": {
            "precision": gate.precision,
            "coverage": gate.coverage,
            "abstention": gate.abstention,
            "rules_only_precision": gate.rules_only_precision,
            "n_proposals": gate.n_proposals,
            "beats_rules": gate.beats_rules,
            "safety_hold_regressions": gate.safety_hold_regressions,
            "regression_clean": gate.regression_clean,
            "model_version": gate.model_version,
            "corpus_version": gate.corpus_version,
            "notes": gate.notes,
        },
        "gate_evidence": gate.evidence or {},
        "precision_bar": PRECISION_BAR,
        "coverage_floor": COVERAGE_FLOOR,
        "min_samples": MIN_SAMPLES,
        "evaluator_version": evaluator_version,
    }
    conn.execute(
        "INSERT INTO memory_releases ("
        "release_id, gate_id, corpus_hash, evaluator_version, "
        "model_fingerprint, atom_source_ids_json, evidence_json, "
        "enabled, created_ts, invalidated_reason) "
        "VALUES (?,?,?,?,?,?,?,0,?,NULL)",
        (
            release_id, gate_id, corpus_hash, evaluator_version,
            model_fingerprint, json.dumps(sources),
            json.dumps(evidence), datetime.now(timezone.utc).isoformat(),
        ),
    )
    return ReleaseArtifact(
        release_id=release_id,
        gate_id=gate_id,
        corpus_hash=corpus_hash,
        evaluator_version=evaluator_version,
        model_fingerprint=model_fingerprint,
        atom_source_ids=tuple(sources),
        enabled=False,
        evidence=evidence,
    )


def get_release(
        conn: sqlite3.Connection, release_id: str,
) -> ReleaseArtifact | None:
    ensure_release_schema(conn)
    row = conn.execute(
        "SELECT * FROM memory_releases WHERE release_id = ?", (release_id,),
    ).fetchone()
    if row is None:
        return None
    return _row_to_release(row)


def latest_release(conn: sqlite3.Connection) -> ReleaseArtifact | None:
    ensure_release_schema(conn)
    row = conn.execute(
        "SELECT * FROM memory_releases ORDER BY created_ts DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return _row_to_release(row)


def _row_to_release(row: sqlite3.Row) -> ReleaseArtifact:
    return ReleaseArtifact(
        release_id=row["release_id"],
        gate_id=row["gate_id"],
        corpus_hash=row["corpus_hash"],
        evaluator_version=row["evaluator_version"],
        model_fingerprint=row["model_fingerprint"],
        atom_source_ids=tuple(json.loads(row["atom_source_ids_json"] or "[]")),
        enabled=bool(row["enabled"]) and not row["invalidated_reason"],
        evidence=json.loads(row["evidence_json"] or "{}"),
        invalidated_reason=row["invalidated_reason"],
    )


def invalidate_releases(
        conn: sqlite3.Connection, *, reason: str,
) -> int:
    ensure_release_schema(conn)
    cur = conn.execute(
        "UPDATE memory_releases SET enabled=0, invalidated_reason=? "
        "WHERE enabled=1 AND invalidated_reason IS NULL",
        (reason,),
    )
    return cur.rowcount


def release_still_valid(
        conn: sqlite3.Connection,
        release: ReleaseArtifact,
        *,
        model_fingerprint: str | None = None,
) -> tuple[bool, str]:
    """A new atom or changed model invalidates steering."""
    if release.invalidated_reason:
        return False, f"invalidated: {release.invalidated_reason}"
    if release.evaluator_version != EVALUATOR_VERSION:
        return False, "evaluator version changed"
    current_sources = set(collect_atom_source_ids(conn))
    bound = set(release.atom_source_ids)
    if current_sources != bound:
        return False, "atom source IDs changed since release"
    ok, err = source_ids_resolvable(conn, list(release.atom_source_ids))
    if release.atom_source_ids and not ok:
        return False, err
    if model_fingerprint is not None and (
            model_fingerprint != release.model_fingerprint):
        return False, "model fingerprint changed"
    contradictory = find_contradictory_atoms(conn)
    if contradictory:
        return False, f"contradictory atoms: {contradictory}"
    return True, ""


def enable_release(
        conn: sqlite3.Connection,
        release_id: str,
        *,
        deliberate: bool = False,
        model_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Open steering only with an explicit deliberate enable action."""
    ensure_release_schema(conn)
    if not deliberate:
        return {
            "ok": False,
            "enabled": False,
            "error": (
                "refused — pass deliberate=True / --enable to open atom "
                "steering; default remains dark"
            ),
            "moved": False,
        }
    release = get_release(conn, release_id)
    if release is None:
        return {
            "ok": False, "enabled": False,
            "error": "release not found", "moved": False,
        }
    if release.invalidated_reason:
        return {
            "ok": False, "enabled": False,
            "error": f"release invalidated: {release.invalidated_reason}",
            "moved": False,
        }
    valid, reason = release_still_valid(
        conn, release, model_fingerprint=model_fingerprint)
    if not valid:
        return {
            "ok": False, "enabled": False,
            "error": f"stale release: {reason}", "moved": False,
        }
    # Only one enabled release at a time.
    conn.execute(
        "UPDATE memory_releases SET enabled=0 WHERE enabled=1"
    )
    conn.execute(
        "UPDATE memory_releases SET enabled=1, invalidated_reason=NULL "
        "WHERE release_id=?",
        (release_id,),
    )
    return {
        "ok": True,
        "enabled": True,
        "release_id": release_id,
        "gate_id": release.gate_id,
        "corpus_hash": release.corpus_hash,
        "evaluator_version": release.evaluator_version,
        "model_fingerprint": release.model_fingerprint,
        "atom_source_ids": list(release.atom_source_ids),
        "moved": False,
    }


def active_release(conn: sqlite3.Connection) -> ReleaseArtifact | None:
    ensure_release_schema(conn)
    row = conn.execute(
        "SELECT * FROM memory_releases "
        "WHERE enabled=1 AND invalidated_reason IS NULL "
        "ORDER BY created_ts DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None
    return _row_to_release(row)


def steering_enabled(conn: sqlite3.Connection) -> bool:
    """True only when an enabled release is still valid."""
    rel = active_release(conn)
    if rel is None:
        return False
    valid, _ = release_still_valid(conn, rel)
    if not valid:
        return False
    return True


def release_status(conn: sqlite3.Connection) -> dict[str, Any]:
    """Human/CLI evidence snapshot — default dark."""
    ensure_release_schema(conn)
    rel = active_release(conn)
    latest = latest_release(conn)
    live = live_atoms(conn)
    status = {
        "atoms_steering": False,
        "dark": True,
        "live_atoms": len(live),
        "active_release": None,
        "latest_release": None,
        "evaluator_version": EVALUATOR_VERSION,
        "precision_bar": PRECISION_BAR,
        "coverage_floor": COVERAGE_FLOOR,
        "min_samples": MIN_SAMPLES,
    }
    if latest is not None:
        status["latest_release"] = latest.as_dict()
    if rel is not None:
        valid, reason = release_still_valid(conn, rel)
        status["active_release"] = rel.as_dict()
        status["active_release"]["still_valid"] = valid
        status["active_release"]["validity_reason"] = reason
        if valid:
            status["atoms_steering"] = True
            status["dark"] = False
    return status


def run_gate_from_fixture(
        conn: sqlite3.Connection,
        fixture_path: Path | str,
) -> tuple[GateResult, str, ReleaseArtifact | None]:
    """Evaluate a fixture, record gate, create (disabled) release if passed."""
    path = Path(fixture_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    proposals = data["proposals"]
    gold = {
        str(p["proposal_id"]) for p in proposals
        if p.get("gold") or p.get("label") in (True, "accept")
    }
    rules = set(data.get("rules_only_accepted") or [])
    model_version = data.get("model_version") or "fixture-model"
    corpus_version = data.get("corpus_version") or path.name
    result = evaluate_release_gate(
        proposals=proposals,
        gold_accepted=gold,
        rules_only_accepted=rules,
        model_version=model_version,
        corpus_version=corpus_version,
        min_samples=int(data.get("min_samples") or MIN_SAMPLES),
    )
    gate_id = record_gate(conn, result)
    release = None
    if result.passed:
        release = create_release(
            conn,
            gate=result,
            gate_id=gate_id,
            corpus_hash=data.get("corpus_hash") or corpus_hash_of(data),
            model_fingerprint=model_fingerprint_of(model_version),
            atom_source_ids=data.get("atom_source_ids"),
        )
    return result, gate_id, release


def format_gate_evidence(status: dict[str, Any]) -> str:
    lines = [
        "Memory release status (default: dark)",
        f"  atoms_steering={status.get('atoms_steering')} dark={status.get('dark')}",
        f"  live_atoms={status.get('live_atoms')}",
        f"  evaluator={status.get('evaluator_version')}",
        f"  bars: precision>={status.get('precision_bar')} "
        f"coverage>={status.get('coverage_floor')} "
        f"min_samples>={status.get('min_samples')}",
    ]
    latest = status.get("latest_release")
    if latest:
        ev = (latest.get("evidence") or {}).get("gate") or {}
        lines.append(f"  latest_release={latest.get('release_id')}")
        lines.append(
            f"    gate_id={latest.get('gate_id')} enabled={latest.get('enabled')}"
        )
        lines.append(
            f"    corpus_hash={latest.get('corpus_hash', '')[:16]}…"
        )
        lines.append(
            f"    model_fp={latest.get('model_fingerprint', '')[:16]}…"
        )
        lines.append(
            f"    precision={ev.get('precision')} coverage={ev.get('coverage')} "
            f"beats_rules={ev.get('beats_rules')} "
            f"safety_regs={ev.get('safety_hold_regressions')}"
        )
        if latest.get("invalidated_reason"):
            lines.append(
                f"    invalidated={latest.get('invalidated_reason')}"
            )
    else:
        lines.append("  latest_release=(none)")
    active = status.get("active_release")
    if active:
        lines.append(
            f"  active_release={active.get('release_id')} "
            f"valid={active.get('still_valid')} "
            f"reason={active.get('validity_reason')}"
        )
    lines.append(
        "  To enable: database-agent memory release --enable "
        "--release-id <id> (deliberate)"
    )
    return "\n".join(lines)
