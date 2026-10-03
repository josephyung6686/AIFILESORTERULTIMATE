"""Person merge migrates relationships via relationship_service (T6)."""
from __future__ import annotations

from items.people import merge_persons, mint_person
from items.relationship_service import accept_link
from items.schema import create_items_schema


def test_merge_moves_relationship_endpoints(conn):
    create_items_schema(conn)
    keep = mint_person(conn, display_label="Ada", email="ada@a.com")
    drop = mint_person(conn, display_label="Ada L", email="ada@b.com")
    # File item + proposed about edge to drop
    conn.execute(
        "INSERT INTO items ("
        "item_id, item_type, display_label, file_id, open_target, "
        "external_key, presence, typing_state, type_schema, profile_id, "
        "created_at, superseded_by) VALUES ("
        "'f1','file','note',NULL,NULL,NULL,'live','typed',NULL,NULL,"
        "datetime('now'),NULL)"
    )
    conn.execute(
        "INSERT INTO relationships ("
        "relationship_id, from_item_id, to_item_id, rel_type, confidence, "
        "source, state, evidence_refs, basis_key, created_at, supersedes, "
        "superseded_by) VALUES ("
        "'r1','f1',?, 'about', 'witnessed', 'test', 'proposed', '[]', "
        "'bk1', datetime('now'), NULL, NULL)",
        (drop.item_id,),
    )
    accept_link(conn, "r1", user_id="u")
    merge_persons(
        conn, keep_id=keep.item_id, drop_id=drop.item_id, confirmed=True)
    row = conn.execute(
        "SELECT from_item_id, to_item_id, state FROM relationships "
        "WHERE relationship_id='r1'"
    ).fetchone()
    assert row["to_item_id"] == keep.item_id
    assert row["state"] == "approved"
