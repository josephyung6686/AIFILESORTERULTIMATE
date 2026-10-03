"""Held reads require both local egress and actual local authentication."""
import pytest

from assistant.tools import ToolRuntime
from items.schema import create_items_schema


@pytest.fixture
def held(conn):
    create_items_schema(conn)
    conn.execute("INSERT INTO items(item_id,item_type,display_label,open_target,presence,typing_state,created_at) VALUES ('held','file','secret','/tmp/secret','live','held','now')")
    return conn


@pytest.mark.parametrize('allow,egress', [(False, 'cloud'), (True, 'cloud'), (False, 'local')])
def test_loopback_environment_cannot_override_explicit_policy(held, monkeypatch, allow, egress):
    monkeypatch.setenv('ASSISTANT_LOCAL_BASE_URL', 'http://127.0.0.1:11434/v1')
    result = ToolRuntime(held, allow_held_body=allow, egress_class=egress).execute('read_item', {'item_id': 'held'})
    assert not result.ok
    assert '/tmp/secret' not in str(result.payload)


def test_local_transport_alone_does_not_authenticate(held):
    result = ToolRuntime(held, allow_held_body=True, egress_class='local').execute('read_item', {'item_id': 'held'})
    assert not result.ok
    assert 'authentication' in result.payload['reason']


@pytest.mark.parametrize('authenticated', [False, True])
def test_explicit_local_read_obeys_authentication(held, authenticated):
    runtime = ToolRuntime(held, allow_held_body=True, egress_class='local',
                          authenticate_held=lambda: authenticated)
    result = runtime.execute('read_item', {'item_id': 'held'})
    assert result.ok is authenticated
    assert bool(result.payload.get('open_target')) is authenticated


def test_cloud_never_invokes_local_authentication(held):
    calls = []
    def unexpected():
        calls.append(True)
        return True
    result = ToolRuntime(held, allow_held_body=True, egress_class='cloud',
                         authenticate_held=unexpected).execute('read_item', {'item_id': 'held'})
    assert not result.ok
    assert calls == []
