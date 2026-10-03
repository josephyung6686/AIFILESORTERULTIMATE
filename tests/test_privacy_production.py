"""Privacy operations against the production schema and append-only guards."""
from __future__ import annotations

import json
import sqlite3

import pytest

from database_agent.db import open_database
from database_agent.privacy import delete_item, export_database
from items.hot_index import rebuild_fts
from items.identity import reconcile_tree
from items.relationship_service import accept_link


@pytest.fixture
def database(tmp_path):
    root = tmp_path / 'files'
    root.mkdir()
    (root / 'public.txt').write_text('public searchable content')
    (root / 'held-secret.txt').write_text('HELD_PAYLOAD_SENTINEL')
    conn = open_database(tmp_path / 'agent.sqlite', scan_roots=[str(root)])
    reconcile_tree(conn, root)
    rebuild_fts(conn)
    public = conn.execute("SELECT * FROM items WHERE display_label = 'public.txt'").fetchone()
    held = conn.execute("SELECT * FROM items WHERE display_label = 'held-secret.txt'").fetchone()
    conn.execute("UPDATE items SET typing_state = 'held' WHERE item_id = ?", (held['item_id'],))
    # Deliberately stale held indexes must never be exported.
    conn.execute("CREATE TABLE unrecognized_payload (metadata TEXT)")
    conn.execute("INSERT INTO unrecognized_payload VALUES (?)", (json.dumps({'secret': 'HELD_PAYLOAD_SENTINEL'}),))
    conn.execute(
        "INSERT INTO relationships VALUES ('rel', 'about', ?, ?, 'witnessed', "
        "'person', 'proposed', '[]', 'basis', 'now', NULL, NULL)",
        (public['item_id'], held['item_id']))
    accept_link(conn, 'rel', user_id='local')
    for item in (public, held):
        conn.execute(
            "INSERT INTO vector_embeddings (embedding_id,file_id,content_hash,scope,"
            "embedding_model_id,embedding_version,dimension,encoding,array_bytes,created_at) "
            "VALUES (?, ?, ?, 'file', 'test', '1', 1, 'float32', ?, 'now')",
            (item['item_id'], item['file_id'], item['content_hash'], b'\0\0\0\0'))
    yield conn, public, held
    conn.close()


def test_delete_removes_active_projections_and_file_vectors_preserving_history(database):
    conn, public, held = database
    history = [tuple(r) for r in conn.execute('SELECT * FROM item_identity_events')]
    decisions = [tuple(r) for r in conn.execute('SELECT * FROM relationship_decisions')]
    result = delete_item(conn, public['item_id'])
    assert result['deleted'] is True
    assert result['retained_history'] is True
    for table in ('items', 'item_versions', 'item_chunks', 'item_fts', 'item_chunk_fts'):
        assert conn.execute(f'SELECT 1 FROM {table} WHERE item_id = ?', (public['item_id'],)).fetchone() is None
    assert conn.execute('SELECT 1 FROM relationships').fetchone() is None
    assert conn.execute('SELECT 1 FROM vector_embeddings WHERE file_id = ?', (public['file_id'],)).fetchone() is None
    assert conn.execute('SELECT 1 FROM vector_embeddings WHERE file_id = ?', (held['file_id'],)).fetchone()
    assert [tuple(r) for r in conn.execute('SELECT * FROM item_identity_events')] == history
    assert [tuple(r) for r in conn.execute('SELECT * FROM relationship_decisions')] == decisions
    assert conn.execute("SELECT action FROM privacy_audit_events").fetchone()[0] == 'delete'
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute('DELETE FROM item_identity_events')


def test_delete_failure_rolls_back_active_records_and_audit(database):
    conn, public, _ = database
    conn.execute("CREATE TRIGGER refuse_delete BEFORE DELETE ON items BEGIN SELECT RAISE(ABORT, 'injected'); END")
    with pytest.raises(sqlite3.DatabaseError):
        delete_item(conn, public['item_id'])
    assert conn.execute('SELECT 1 FROM item_chunks WHERE item_id = ?', (public['item_id'],)).fetchone()
    assert conn.execute('SELECT 1 FROM relationships').fetchone()
    assert conn.execute('SELECT 1 FROM vector_embeddings WHERE file_id = ?', (public['file_id'],)).fetchone()
    assert not conn.in_transaction


def test_delete_respects_caller_transaction(database):
    conn, public, _ = database
    conn.execute('BEGIN')
    delete_item(conn, public['item_id'])
    assert conn.in_transaction
    conn.rollback()
    assert conn.execute('SELECT 1 FROM items WHERE item_id = ?', (public['item_id'],)).fetchone()
    assert conn.execute('SELECT 1 FROM relationships').fetchone()


def test_export_omits_held_and_raw_indirect_payloads(database, tmp_path):
    conn, public, held = database
    destination = tmp_path / 'export.json'
    result = export_database(conn, destination)
    payload = json.loads(destination.read_text())
    rendered = destination.read_text()
    assert public['item_id'] in rendered
    assert held['item_id'] not in rendered
    assert held['file_id'] not in rendered
    assert 'held-secret' not in rendered
    assert 'HELD_PAYLOAD_SENTINEL' not in rendered
    assert 'public searchable content' not in rendered
    assert 'unrecognized_payload' not in payload['tables']
    assert not any(name.startswith('item_fts') for name in payload['tables'])
    assert result['audited'] is True
    assert destination.stat().st_mode & 0o077 == 0


def test_held_delete_refuses_without_auth_and_keeps_indexes(database):
    from database_agent.privacy import LocalAuthRequired
    conn, _, held = database
    with pytest.raises(LocalAuthRequired):
        delete_item(conn, held['item_id'])
    assert conn.execute('SELECT 1 FROM item_chunks WHERE item_id = ?', (held['item_id'],)).fetchone()
    assert delete_item(conn, held['item_id'], authenticate=lambda: True)['deleted']


def test_export_audit_failure_preserves_destination(database, tmp_path):
    from database_agent.privacy import create_privacy_schema
    conn, _, _ = database
    create_privacy_schema(conn)
    conn.execute("CREATE TRIGGER refuse_audit BEFORE INSERT ON privacy_audit_events BEGIN SELECT RAISE(ABORT, 'injected'); END")
    destination = tmp_path / 'export.json'
    destination.write_text('previous export')
    with pytest.raises(sqlite3.DatabaseError):
        export_database(conn, destination)
    assert destination.read_text() == 'previous export'
    assert not list(tmp_path.glob('.privacy-export-*'))
    assert not conn.in_transaction


def test_export_does_not_commit_callers_changes(database, tmp_path):
    conn, public, _ = database
    conn.execute('BEGIN')
    conn.execute("UPDATE items SET display_label = 'pending' WHERE item_id = ?", (public['item_id'],))
    export_database(conn, tmp_path / 'export.json')
    assert conn.in_transaction
    conn.rollback()
    assert conn.execute('SELECT display_label FROM items WHERE item_id = ?', (public['item_id'],)).fetchone()[0] == 'public.txt'


def test_export_commit_failure_does_not_publish_unaudited_file(database, tmp_path):
    conn, _, _ = database
    destination = tmp_path / 'export.json'
    destination.write_text('previous export')
    conn.set_authorizer(lambda action, arg1, *_: sqlite3.SQLITE_DENY
                        if action == sqlite3.SQLITE_TRANSACTION and arg1 == 'COMMIT'
                        else sqlite3.SQLITE_OK)
    with pytest.raises(sqlite3.DatabaseError):
        export_database(conn, destination)
    assert destination.read_text() == 'previous export'
    assert not list(tmp_path.glob('.privacy-export-*'))


def test_held_helper_supports_non_sqlite_row_factories(database):
    from database_agent.privacy import LocalAuthRequired, held_item_fields
    conn, _, held = database
    item_id = held['item_id']
    conn.row_factory = None
    with pytest.raises(LocalAuthRequired):
        held_item_fields(conn, item_id)
    assert held_item_fields(conn, item_id, authenticate=lambda: True)['item_id'] == item_id


def test_loaded_sqlcipher_driver_is_not_proof_of_encryption(tmp_path):
    from database_agent import encryption
    from database_agent.privacy import encryption_capability
    if encryption._DRIVER is None:
        pytest.skip('SQLCipher is optional')
    path = tmp_path / 'unkeyed.sqlite'
    conn = encryption._DRIVER.connect(str(path))
    try:
        conn.execute('CREATE TABLE example (value TEXT)')
        conn.commit()
        assert path.read_bytes().startswith(b'SQLite format 3')
        assert encryption_capability(conn).encrypted is False
    finally:
        conn.close()


def test_folder_view_withholds_held_path(database):
    from items.views import folder_view
    conn, _, held = database
    row = next(row for row in folder_view(conn) if row['item_id'] == held['item_id'])
    assert not row['open_target']
    assert not row['parent']


def test_managed_encryption_and_held_authentication(tmp_path):
    from database_agent import encryption
    from database_agent.privacy import LocalAuthRequired, encryption_capability, held_item_fields
    from items.schema import create_items_schema
    if encryption._DRIVER is None:
        pytest.skip('SQLCipher is optional')
    conn = open_database(tmp_path / 'keyed.sqlite', scan_roots=[],
                         encryption=True, encryption_key=b'k' * 32)
    try:
        create_items_schema(conn)
        conn.execute("INSERT INTO items(item_id,item_type,display_label,presence,typing_state,created_at) VALUES ('held','file','secret','live','held','now')")
        assert encryption_capability(conn).encrypted is True
        with pytest.raises(LocalAuthRequired):
            held_item_fields(conn, 'held')
        assert held_item_fields(conn, 'held', authenticate=lambda: True)['item_id'] == 'held'
    finally:
        conn.close()


@pytest.mark.parametrize('view_name', ['folder_view', 'table_view'])
@pytest.mark.parametrize('protected_by', ['typing', 'path'])
def test_item_views_withhold_held_and_protected_paths(database, view_name, protected_by):
    from items import views
    conn, public, held = database
    item_id = held['item_id'] if protected_by == 'typing' else public['item_id']
    if protected_by == 'path':
        conn.execute("UPDATE items SET open_target = '/tmp/private.key' WHERE item_id = ?", (item_id,))
    rows = getattr(views, view_name)(conn)
    row = next(r for r in rows if r['item_id'] == item_id)
    assert not row['open_target']
    assert not row.get('parent')
    assert row['display_label']


def test_held_helper_also_gates_protected_unheld_path(database):
    from database_agent.privacy import LocalAuthRequired, held_item_fields
    conn, public, _ = database
    conn.execute("UPDATE items SET open_target = '/tmp/private.key' WHERE item_id = ?", (public['item_id'],))
    with pytest.raises(LocalAuthRequired):
        held_item_fields(conn, public['item_id'])


def test_export_omits_protected_paths_even_when_not_typed_held(database, tmp_path):
    conn, public, _ = database
    conn.execute("UPDATE items SET open_target = '/tmp/private.key' WHERE item_id = ?", (public['item_id'],))
    destination = tmp_path / 'export.json'
    export_database(conn, destination)
    assert public['item_id'] not in destination.read_text()
    assert public['file_id'] not in destination.read_text()
    assert '/tmp/private.key' not in destination.read_text()
