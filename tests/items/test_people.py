"""P5 person items, aliases, merge precision."""
from __future__ import annotations

import pytest

from items.people import (
    add_alias,
    merge_candidates,
    merge_persons,
    merge_precision,
    mint_person,
)


def test_mint_person_and_alias(conn):
    p = mint_person(conn, display_label="Ada Lovelace", email="ada@example.com")
    assert p.item_id
    assert "ada@example.com" in p.aliases
    # same email returns same person
    p2 = mint_person(conn, display_label="Ada L", email="ada@example.com")
    assert p2.item_id == p.item_id


def test_merge_requires_confirm_and_precision(conn):
    a = mint_person(conn, display_label="Same Name", email="a@x.com")
    b = mint_person(conn, display_label="Same Name", email="b@x.com")
    cands = merge_candidates(conn)
    assert any(
        {c.left_id, c.right_id} == {a.item_id, b.item_id} for c in cands)
    with pytest.raises(PermissionError):
        merge_persons(conn, keep_id=a.item_id, drop_id=b.item_id, confirmed=False)
    merged = merge_persons(
        conn, keep_id=a.item_id, drop_id=b.item_id, confirmed=True)
    assert merged.item_id == a.item_id
    assert "b@x.com" in merged.aliases or "a@x.com" in merged.aliases
    gold = {(a.item_id, b.item_id)}
    metrics = merge_precision(cands, gold)
    assert metrics["precision"] >= 0.5
