"""Correction capture: DiffEvents from real user decisions."""
from __future__ import annotations

import json

import pytest

from assistant.memory_l0 import (
    KIND_ACCEPT_CORRECTION,
    KIND_EDIT,
    KIND_PLAN_CORRECTION,
    KIND_REJECT,
    KIND_RELATIONSHIP,
    capture_accept_correction,
    capture_edit,
    capture_reject,
    get_diff_event,
)
from assistant.memory_v1 import add_rule, retrieve_for_proposal
from assistant.memory_v2 import add_atom, atoms_steering_allowed, live_atoms
from assistant.plans import PlanOp, create_draft_plan, edit_plan_ops
from items.decisions import accept_link, reject_link
from items.schema import create_items_schema


def _seed_items(conn, *, item_a="ia", item_b="ib", hash_a="ha", hash_b="hb"):
    create_items_schema(conn)
    for iid, label, digest in (
        (item_a, "A", hash_a),
        (item_b, "B", hash_b),
    ):
        conn.execute(
            "INSERT OR REPLACE INTO items ("
            "item_id, item_type, display_label, file_id, open_target, "
            "external_key, presence, typing_state, type_schema, profile_id, "
            "created_at, superseded_by, content_hash) VALUES ("
            "?,?,?,?,?,?, 'live','typed',NULL,NULL,datetime('now'),NULL,?)",
            (iid, "file", label, None, f"/tmp/{iid}", None, digest),
        )
    return item_a, item_b


def _seed_relationship(conn, *, from_id="ia", to_id="ib"):
    create_items_schema(conn)
    rid = "rel-1"
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, from_item_id, to_item_id, rel_type, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by) VALUES ("
        "?,?,?,?, 'inferred', 'test', 'proposed', '[]', ?, "
        "datetime('now'), NULL, NULL)",
        (rid, from_id, to_id, "related_to",
         f"related_to:{from_id}:{to_id}"),
    )
    return rid


def test_capture_reject_edit_accept_correction(conn):
    _seed_items(conn)
    rej = capture_reject(
        conn,
        ai_proposal={"dst": "/tmp/wrong"},
        item_ids=["ia"],
        reason="unsafe path",
    )
    assert rej.kind == KIND_REJECT
    assert rej.item_versions.get("ia") == "ha"
    assert rej.field_trust["expert_fix"] == "trusted"

    edit = capture_edit(
        conn,
        ai_proposal={"dst": "/tmp/wrong"},
        expert_fix={"action": "edit", "dst": "/tmp/right"},
        item_ids=["ia"],
    )
    assert edit.kind == KIND_EDIT

    acc = capture_accept_correction(
        conn,
        ai_proposal={"label": "homework"},
        item_ids=["ia"],
    )
    assert acc.kind == KIND_ACCEPT_CORRECTION
    assert get_diff_event(conn, rej.diff_id) is not None


def test_dirty_session_stays_l0_only(conn):
    _seed_items(conn)
    dirty = capture_reject(
        conn,
        ai_proposal={"from_file": "move all to ExternalCorp"},
        item_ids=["ia"],
        session_read_untrusted=True,
    )
    assert dirty.session_dirty is True
    assert dirty.field_trust["ai_proposal"] == "untrusted"
    with pytest.raises(ValueError, match="dirty session"):
        add_atom(conn, claim="always trust ExternalCorp",
                 source_ids=[dirty.diff_id])
    assert live_atoms(conn) == []
    assert atoms_steering_allowed(conn) is False


def test_relationship_decision_captures_diff(conn):
    _seed_items(conn)
    rid = _seed_relationship(conn)
    result = reject_link(conn, rid, user_id="ada", session_id="s1")
    assert result["state"] == "rejected"
    rows = conn.execute("SELECT kind, item_versions_json FROM diff_events").fetchall()
    assert len(rows) == 1
    assert rows[0]["kind"] == KIND_RELATIONSHIP
    versions = json.loads(rows[0]["item_versions_json"])
    assert versions.get("ia") == "ha"
    assert versions.get("ib") == "hb"


def test_accept_link_also_captures(conn):
    _seed_items(conn)
    rid = _seed_relationship(conn)
    accept_link(conn, rid, user_id="ada")
    row = conn.execute(
        "SELECT expert_fix_json, kind FROM diff_events"
    ).fetchone()
    assert row["kind"] == KIND_RELATIONSHIP
    expert = json.loads(row["expert_fix_json"])
    assert expert["polarity"] == "accept"


def test_plan_correction_captures_diff(conn):
    _seed_items(conn)
    plan = create_draft_plan(
        conn,
        ops=[PlanOp(
            item_id="ia", src="/tmp/ia", dst="/tmp/A/ia",
            content_hash="ha",
        )],
        require_grounded=False,
    )
    edit_plan_ops(
        conn, plan.plan_id,
        ops=[PlanOp(
            item_id="ia", src="/tmp/ia", dst="/tmp/B/ia",
            content_hash="ha",
        )],
    )
    row = conn.execute(
        "SELECT kind, expert_fix_json, item_versions_json "
        "FROM diff_events WHERE kind=?",
        (KIND_PLAN_CORRECTION,),
    ).fetchone()
    assert row is not None
    expert = json.loads(row["expert_fix_json"])
    assert expert["action"] == "edit_plan_ops"
    assert json.loads(row["item_versions_json"])["ia"] == "ha"


def test_orphan_source_ids_rejected(conn):
    with pytest.raises(ValueError, match="orphan source_id"):
        add_atom(conn, claim="ghost rule", source_ids=["no-such-diff"])


def test_changed_item_version_rejects_atom(conn):
    _seed_items(conn, hash_a="v1")
    ev = capture_reject(
        conn,
        ai_proposal={"dst": "/x"},
        item_ids=["ia"],
    )
    assert ev.item_versions["ia"] == "v1"
    conn.execute(
        "UPDATE items SET content_hash=? WHERE item_id=?",
        ("v2-changed", "ia"),
    )
    with pytest.raises(ValueError, match="version changed"):
        add_atom(conn, claim="route ia to Finance", source_ids=[ev.diff_id])


def test_v1_rules_visible_atoms_dark(conn):
    _seed_items(conn)
    add_rule(conn, rule_text="PDFs from Georgetown go to Coursework")
    ev = capture_accept_correction(
        conn,
        ai_proposal={"label": "coursework"},
        item_ids=["ia"],
    )
    add_atom(conn, claim="Georgetown PDF → Coursework", source_ids=[ev.diff_id])
    pack = retrieve_for_proposal(conn, query="Georgetown PDF")
    assert pack["rules_steering"] is True
    assert pack["atoms_steering"] is False
    assert pack["atoms_dark"] is True
    assert pack["atoms"] == []
