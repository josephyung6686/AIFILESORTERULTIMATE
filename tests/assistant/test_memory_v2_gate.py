"""P7 memory v2: atoms dark until version-bound release; hard source_ids."""
from __future__ import annotations

import pytest

from assistant.memory_l0 import capture_accept_correction
from assistant.memory_release import (
    create_release,
    enable_release,
    model_fingerprint_of,
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
from items.schema import create_items_schema


def _diff(conn, claim="x"):
    create_items_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "external_key, presence, typing_state, type_schema, profile_id, "
        "created_at, superseded_by, content_hash) VALUES ("
        "?,?,?,?,?,?, 'live','typed',NULL,NULL,datetime('now'),NULL,?)",
        ("ia", "file", "ia", None, "/tmp/ia", None, "ha"),
    )
    return capture_accept_correction(
        conn,
        ai_proposal={"label": claim},
        item_ids=["ia"],
    )


def test_atom_requires_source_ids(conn):
    with pytest.raises(ValueError):
        add_atom(conn, claim="file X is homework", source_ids=[])
    d = _diff(conn)
    aid = add_atom(
        conn, claim="file X is homework", source_ids=[d.diff_id])
    atoms = live_atoms(conn)
    assert any(a["atom_id"] == aid for a in atoms)
    assert atoms_steering_allowed(conn) is False
    pack = retrieve_atoms_for_prompt(conn)
    assert pack["atoms_steering"] is False
    assert pack["atoms"] == []


def test_gate_fails_closed_then_opens_via_release(conn, monkeypatch):
    monkeypatch.delenv("ASSISTANT_ATOMS_STEER", raising=False)
    # Weak proposals — fail
    proposals = [
        {"proposal_id": "a", "willing": True},
        {"proposal_id": "b", "willing": True},
        {"proposal_id": "c", "willing": True},
    ]
    gold = {"a"}
    rules = {"a", "b"}
    bad = evaluate_gate(
        proposals=proposals, gold_accepted=gold, rules_only_accepted=rules)
    assert bad.passed is False
    assert bad.precision < PRECISION_BAR
    record_gate(conn, bad)
    assert atoms_steering_allowed(conn) is False

    # High precision + beats rules — still dark until deliberate release enable
    good_props = [
        {"proposal_id": f"p{i}", "willing": True} for i in range(20)
    ]
    gold2 = {f"p{i}" for i in range(20)}
    rules2 = {f"p{i}" for i in range(15)} | {
        "noise1", "noise2", "noise3", "noise4", "noise5"
    }
    good = evaluate_gate(
        proposals=good_props, gold_accepted=gold2, rules_only_accepted=rules2,
        model_version="m", corpus_version="c",
    )
    assert good.precision >= PRECISION_BAR
    assert good.precision > good.rules_only_precision
    assert good.passed is True
    gate_id = record_gate(conn, good)
    assert atoms_steering_allowed(conn) is False  # dark without release

    d = _diff(conn)
    add_atom(conn, claim="homework", source_ids=[d.diff_id])
    # Re-evaluate after atom (new atom invalidates nothing yet — no release)
    good2 = evaluate_gate(
        proposals=good_props, gold_accepted=gold2, rules_only_accepted=rules2,
        model_version="m", corpus_version="c",
    )
    gate_id = record_gate(conn, good2)
    from assistant.memory_release import collect_atom_source_ids
    release = create_release(
        conn,
        gate=good2,
        gate_id=gate_id,
        corpus_hash="c",
        model_fingerprint=model_fingerprint_of("m"),
        atom_source_ids=collect_atom_source_ids(conn),
    )
    enable_release(conn, release.release_id, deliberate=True)
    assert atoms_steering_allowed(conn) is True
    pack = retrieve_atoms_for_prompt(conn)
    assert pack["atoms_steering"] is True


def test_supersede_keeps_history(conn):
    d = _diff(conn)
    a = add_atom(conn, claim="old", source_ids=[d.diff_id])
    b = add_atom(conn, claim="new", source_ids=[d.diff_id])
    supersede_atom(conn, a, replacement_id=b)
    live = live_atoms(conn)
    assert all(x["atom_id"] != a for x in live)
    assert any(x["atom_id"] == b for x in live)
