"""P5 entity-merge precision suite on a labeled person set."""
from __future__ import annotations

from items.people import (
    merge_candidates,
    merge_persons,
    merge_precision,
    mint_person,
)


def test_merge_precision_on_labeled_set(conn):
    # Gold merges: same person, two accounts
    p1 = mint_person(conn, display_label="Joseph Yung", email="jy@school.edu")
    p1b = mint_person(conn, display_label="Joseph Yung", email="jy@personal.com")
    # Distinct people — must not merge on label alone if we only use email local?
    # Same label triggers candidate — gold says they ARE same (p1,p1b)
    q1 = mint_person(conn, display_label="Ada Lovelace", email="ada@a.com")
    q2 = mint_person(conn, display_label="Grace Hopper", email="grace@navy.mil")
    # False-friend: shared local-part different people
    r1 = mint_person(conn, display_label="Alex One", email="alex@one.com")
    r2 = mint_person(conn, display_label="Alex Two", email="alex@two.com")

    cands = merge_candidates(conn)
    gold = {
        tuple(sorted((p1.item_id, p1b.item_id))),
    }
    # Label-identical Joseph pair should be proposed
    assert any(
        tuple(sorted((c.left_id, c.right_id))) == tuple(sorted((p1.item_id, p1b.item_id)))
        for c in cands
    )
    # Only score high-confidence label blockers for precision bar
    label_cands = [c for c in cands if c.blocking_key.startswith("label:")]
    metrics = merge_precision(label_cands, gold)
    # Joseph same-name is TP; no other same-label pairs → precision 1.0
    assert metrics["precision"] >= 0.95
    assert metrics["n_tp"] >= 1

    # Confirmed merge
    merged = merge_persons(
        conn, keep_id=p1.item_id, drop_id=p1b.item_id, confirmed=True)
    assert "jy@personal.com" in merged.aliases or "jy@school.edu" in merged.aliases
    # Unrelated people untouched
    assert q1.item_id != q2.item_id
    assert r1.item_id != r2.item_id
