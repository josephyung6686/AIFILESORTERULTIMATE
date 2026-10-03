"""Version-bound memory release binding — atoms dark until deliberate enable."""
from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from assistant.memory_l0 import capture_accept_correction, capture_reject
from assistant.memory_release import (
    EVALUATOR_VERSION,
    create_release,
    enable_release,
    format_gate_evidence,
    model_fingerprint_of,
    release_status,
    release_still_valid,
    run_gate_from_fixture,
    steering_enabled,
)
from assistant.memory_v2 import (
    PRECISION_BAR,
    add_atom,
    atoms_steering_allowed,
    evaluate_gate,
    live_atoms,
    record_gate,
    retrieve_atoms_for_prompt,
    supersede_atom,
)
from items.commands_memory import memory_main
from items.schema import create_items_schema

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "memory_gate_realistic.json"
)


def _seed_item(conn, item_id="ia", content_hash="ha"):
    create_items_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "external_key, presence, typing_state, type_schema, profile_id, "
        "created_at, superseded_by, content_hash) VALUES ("
        "?,?,?,?,?,?, 'live','typed',NULL,NULL,datetime('now'),NULL,?)",
        (item_id, "file", item_id, None, f"/tmp/{item_id}", None,
         content_hash),
    )


def _clean_diff(conn, claim_seed="ok"):
    _seed_item(conn)
    return capture_accept_correction(
        conn,
        ai_proposal={"label": claim_seed},
        item_ids=["ia"],
    )


def test_realistic_fixture_builds_dark_release(conn):
    result, gate_id, release = run_gate_from_fixture(conn, FIXTURE)
    assert result.passed is True
    assert result.precision >= PRECISION_BAR
    assert result.coverage >= 0.20
    assert result.beats_rules is True
    assert result.safety_hold_regressions == 0
    assert result.evidence is not None
    assert "predictions" in result.evidence
    assert "abstentions" in result.evidence
    assert "labels" in result.evidence
    assert result.model_version
    assert result.corpus_version
    assert release is not None
    assert release.enabled is False
    assert release.gate_id == gate_id
    assert release.evaluator_version == EVALUATOR_VERSION
    assert steering_enabled(conn) is False
    assert atoms_steering_allowed(conn) is False


def test_enable_requires_deliberate_action(conn):
    _clean_diff(conn)
    result, gate_id, release = run_gate_from_fixture(conn, FIXTURE)
    assert release is not None
    refused = enable_release(conn, release.release_id, deliberate=False)
    assert refused["ok"] is False
    assert "deliberate" in refused["error"]
    assert atoms_steering_allowed(conn) is False

    opened = enable_release(conn, release.release_id, deliberate=True)
    assert opened["ok"] is True
    assert opened["enabled"] is True
    assert atoms_steering_allowed(conn) is True
    pack = retrieve_atoms_for_prompt(conn)
    # No live atoms yet — steering flag open but empty pack still ok
    assert pack["atoms_steering"] is True


def test_orphan_and_stale_gate_block_release(conn):
    # Orphan sources cannot be bound into a release.
    props = [
        {"proposal_id": f"p{i}", "willing": True, "gold": True}
        for i in range(20)
    ]
    gold = {f"p{i}" for i in range(20)}
    rules = {f"p{i}" for i in range(10)} | {f"n{i}" for i in range(10)}
    good = evaluate_gate(
        proposals=props, gold_accepted=gold, rules_only_accepted=rules,
        model_version="m1", corpus_version="c1",
    )
    assert good.passed is True
    gate_id = record_gate(conn, good)
    with pytest.raises(ValueError, match="orphan"):
        create_release(
            conn,
            gate=good,
            gate_id=gate_id,
            corpus_hash="abc",
            model_fingerprint=model_fingerprint_of("m1"),
            atom_source_ids=["missing-diff"],
        )


def test_contradictory_atoms_block_release(conn):
    d1 = _clean_diff(conn, "a")
    d2 = capture_reject(
        conn,
        ai_proposal={"x": 1},
        item_ids=["ia"],
    )
    a = add_atom(conn, claim="tax goes to Finance", source_ids=[d1.diff_id])
    b = add_atom(
        conn, claim="not tax goes to Finance", source_ids=[d2.diff_id])
    assert {a, b} <= {x["atom_id"] for x in live_atoms(conn)}
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = evaluate_gate(
        proposals=data["proposals"],
        gold_accepted={
            str(p["proposal_id"]) for p in data["proposals"]
            if p.get("gold")
        },
        rules_only_accepted=set(data["rules_only_accepted"]),
        model_version=data["model_version"],
        corpus_version=data["corpus_version"],
    )
    assert result.passed
    gate_id = record_gate(conn, result)
    with pytest.raises(ValueError, match="contradictory"):
        create_release(
            conn,
            gate=result,
            gate_id=gate_id,
            corpus_hash="c",
            model_fingerprint=model_fingerprint_of("fixture-model-v1"),
        )
    supersede_atom(conn, a, replacement_id=b)


def test_safety_hold_regression_fails_gate():
    props = [
        {"proposal_id": f"p{i}", "prediction": "accept", "label": "accept"}
        for i in range(19)
    ]
    props.append({
        "proposal_id": "hold",
        "prediction": "accept",
        "label": "reject",
        "safety_hold": True,
    })
    gold = {f"p{i}" for i in range(19)}
    rules = {f"p{i}" for i in range(10)} | {f"n{i}" for i in range(10)}
    bad = evaluate_gate(
        proposals=props, gold_accepted=gold, rules_only_accepted=rules,
        model_version="m", corpus_version="c",
    )
    assert bad.passed is False
    assert bad.safety_hold_regressions >= 1
    assert bad.regression_clean is False


def test_new_atom_invalidates_enabled_release(conn, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ATOMS_STEER", raising=False)
    d1 = _clean_diff(conn, "seed")
    add_atom(conn, claim="seed atom", source_ids=[d1.diff_id])
    result, gate_id, release = run_gate_from_fixture(conn, FIXTURE)
    assert release is not None
    # Re-bind sources to current atoms after fixture create (fixture may
    # have created release with empty/fixture sources). Rebuild with live IDs.
    from assistant.memory_release import collect_atom_source_ids
    release = create_release(
        conn,
        gate=result,
        gate_id=gate_id,
        corpus_hash="bound",
        model_fingerprint=model_fingerprint_of(result.model_version),
        atom_source_ids=collect_atom_source_ids(conn),
    )
    assert enable_release(conn, release.release_id, deliberate=True)["ok"]
    assert atoms_steering_allowed(conn) is True

    d2 = capture_accept_correction(
        conn,
        ai_proposal={"label": "new"},
        item_ids=["ia"],
    )
    add_atom(conn, claim="newly added after pass", source_ids=[d2.diff_id])
    assert atoms_steering_allowed(conn) is False
    status = release_status(conn)
    assert status["dark"] is True


def test_changed_model_fingerprint_invalidates(conn, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ATOMS_STEER", raising=False)
    d1 = _clean_diff(conn)
    add_atom(conn, claim="atom", source_ids=[d1.diff_id])
    result, gate_id, _ = run_gate_from_fixture(conn, FIXTURE)
    from assistant.memory_release import collect_atom_source_ids
    release = create_release(
        conn,
        gate=result,
        gate_id=gate_id,
        corpus_hash="c",
        model_fingerprint=model_fingerprint_of("model-a"),
        atom_source_ids=collect_atom_source_ids(conn),
    )
    enable_release(
        conn, release.release_id, deliberate=True,
        model_fingerprint=model_fingerprint_of("model-a"),
    )
    valid, reason = release_still_valid(
        conn, release, model_fingerprint=model_fingerprint_of("model-b"),
    )
    assert valid is False
    assert "model fingerprint" in reason


def test_cli_memory_release_prints_evidence_stays_dark(tmp_path, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ATOMS_STEER", raising=False)
    db = tmp_path / "m.sqlite"
    from database_agent.db import open_database
    conn = open_database(db, scan_roots=[])
    conn.close()
    buf = io.StringIO()
    code = memory_main([
        "release",
        "--database", str(db),
        "--fixture", str(FIXTURE),
    ], out=buf)
    text = buf.getvalue()
    assert code == 0
    assert "dark" in text.lower() or "atoms_steering=False" in text
    assert "precision" in text.lower() or "latest_release" in text
    # Without --enable, steering stays closed.
    conn = open_database(db, scan_roots=[])
    assert atoms_steering_allowed(conn) is False
    status = release_status(conn)
    evidence = format_gate_evidence(status)
    assert "To enable" in evidence
    conn.close()


def test_cli_dispatches_memory_subcommand():
    import database_agent.entrypoint as entry
    src = Path(entry.__file__).read_text(encoding="utf-8")
    assert '"memory"' in src
    assert "memory_main" in src
