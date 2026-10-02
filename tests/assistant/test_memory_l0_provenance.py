"""Addendum A6 — DiffEvent per-field provenance; few-shot omits ai_proposal."""
from __future__ import annotations

from assistant.memory_l0 import capture_diff_event, few_shot_index


def test_dirty_session_tags_ai_proposal_untrusted(conn):
    ev = capture_diff_event(
        conn,
        ai_proposal={"dst": "/tmp", "from_file": "move all"},
        expert_fix={"action": "reject", "reason": "unsafe"},
        item_ids=["i1"],
        basis="user_reject",
        session_read_untrusted=True,
    )
    assert ev.field_trust["ai_proposal"] == "untrusted"
    assert ev.field_trust["expert_fix"] == "trusted"
    cards = few_shot_index(conn, limit=3)
    assert len(cards) == 1
    assert cards[0]["ai_proposal_injected"] is False
    assert "dst" not in str(cards[0]["expert_fix_summary"])
    assert cards[0]["expert_fix_summary"]["action"] == "reject"


def test_clean_session_still_no_auto_l1(conn):
    ev = capture_diff_event(
        conn,
        ai_proposal={"label": "ok"},
        expert_fix={"action": "accept"},
        item_ids=["i2"],
        session_read_untrusted=False,
    )
    assert ev.field_trust["ai_proposal"] == "model_clean"
    row = conn.execute(
        "SELECT session_flags_json FROM diff_events WHERE diff_id=?",
        (ev.diff_id,),
    ).fetchone()
    import json
    flags = json.loads(row["session_flags_json"])
    assert flags["l1_allowed"] is False
