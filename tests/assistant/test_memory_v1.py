"""Memory v1: user rules + few-shot DiffEvents; never auto-atoms."""
from __future__ import annotations

from assistant.memory_l0 import capture_diff_event
from assistant.memory_v1 import (
    add_rule,
    list_rules,
    retrieve_for_proposal,
)


def test_rules_and_few_shot_index(conn):
    add_rule(conn, rule_text="PDFs from Georgetown go to Coursework", kind="route")
    capture_diff_event(
        conn,
        ai_proposal={"dst": "/tmp"},
        expert_fix={"action": "reject", "reason": "unsafe"},
        item_ids=["i1"],
        session_read_untrusted=True,
    )
    pack = retrieve_for_proposal(conn, query="where should Georgetown PDF go")
    assert any("Georgetown" in r["rule_text"] for r in pack["rules"])
    assert pack["few_shot"]
    assert all(f["ai_proposal_injected"] is False for f in pack["few_shot"])
    assert pack["rules_steering"] is True  # explicit user rules may steer
    assert pack["atoms_steering"] is False  # atoms stay dark in v1
    assert pack["steering"] is True
    assert list_rules(conn)
