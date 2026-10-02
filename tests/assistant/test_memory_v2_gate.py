"""P7 memory v2: atoms dark until precision gate; hard source_ids."""
from __future__ import annotations

import pytest

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


def test_atom_requires_source_ids(conn):
    with pytest.raises(ValueError):
        add_atom(conn, claim="file X is homework", source_ids=[])
    aid = add_atom(
        conn, claim="file X is homework", source_ids=["obs-1", "obs-2"])
    atoms = live_atoms(conn)
    assert any(a["atom_id"] == aid for a in atoms)
    assert atoms_steering_allowed(conn) is False
    pack = retrieve_atoms_for_prompt(conn)
    assert pack["atoms_steering"] is False
    assert pack["atoms"] == []


def test_gate_fails_closed_then_opens(conn):
    # Weak proposals — fail
    proposals = [
        {"proposal_id": "a", "willing": True},
        {"proposal_id": "b", "willing": True},
        {"proposal_id": "c", "willing": True},
    ]
    gold = {"a"}
    rules = {"a", "b"}  # rules-only worse or equal
    bad = evaluate_gate(
        proposals=proposals, gold_accepted=gold, rules_only_accepted=rules)
    assert bad.passed is False
    assert bad.precision < PRECISION_BAR
    record_gate(conn, bad)
    assert atoms_steering_allowed(conn) is False

    # High precision + beats rules
    good_props = [
        {"proposal_id": f"p{i}", "willing": True} for i in range(20)
    ]
    gold2 = {f"p{i}" for i in range(20)}
    rules2 = {f"p{i}" for i in range(10)}  # 10/10=1.0 if only those — make worse
    # rules proposes 15 including 5 wrong
    rules2 = {f"p{i}" for i in range(15)} | {"noise1", "noise2", "noise3", "noise4", "noise5"}
    good = evaluate_gate(
        proposals=good_props, gold_accepted=gold2, rules_only_accepted=rules2)
    assert good.precision >= PRECISION_BAR
    assert good.precision > good.rules_only_precision
    assert good.passed is True
    record_gate(conn, good)
    assert atoms_steering_allowed(conn) is True
    pack = retrieve_atoms_for_prompt(conn)
    assert pack["atoms_steering"] is True


def test_supersede_keeps_history(conn):
    a = add_atom(conn, claim="old", source_ids=["s1"])
    b = add_atom(conn, claim="new", source_ids=["s1", "s2"])
    supersede_atom(conn, a, replacement_id=b)
    live = live_atoms(conn)
    assert all(x["atom_id"] != a for x in live)
    assert any(x["atom_id"] == b for x in live)
