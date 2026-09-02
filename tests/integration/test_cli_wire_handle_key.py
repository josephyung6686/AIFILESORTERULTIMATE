"""The wire handle key: minted once, stable after, and never spoken.

`llm_harness.wire_handles` refuses without a key and ships no unkeyed fallback,
so until something produced one, every model call ended in
`WireHandleKeyRequired`. The producer is the composition root's because all three
of its facts are deployment facts: the LENGTH is a number, the LIFETIME is a
policy, and the LOCATION is a path.

The property that costs the most to get wrong is STABILITY. `dossier_id` is the
content address of the model-visible bytes and those bytes carry keyed handles,
so a key that changed between runs would give two calls over identical content
two different addresses and `record_dossier` would stop recognising the second as
the first. A per-run key would pass a "is it 32 bytes" test and destroy every
cross-run replay, which is why the second test here is the load-bearing one.
"""
import pytest

from cli import (WIRE_HANDLE_KEY_BYTES, WIRE_HANDLE_KEY_FILENAME,
                 wire_handle_key_for)


def test_a_key_is_minted_at_the_declared_length_and_nowhere_but_beside_the_database(
        tmp_path):
    key = wire_handle_key_for(tmp_path / "agent.sqlite")

    # THIRTY-TWO, spelled out, and not `WIRE_HANDLE_KEY_BYTES`. Asserting the key
    # against the constant that produced it is a tautology: halving the constant
    # moves the assertion with it and the test stays green while the key becomes
    # the weakest part of the digest. Found by sabotage, which is the only way a
    # tautology announces itself. 32 is HMAC-SHA256's output size and is the
    # length below which an attacker goes after the key rather than the guess
    # space -- so it is a security property and belongs in the test as a number.
    assert len(key) == 32
    assert WIRE_HANDLE_KEY_BYTES == 32
    assert isinstance(key, bytes)
    # Beside the database, not inside it: a database is the thing that gets
    # copied, and a key that travels with every copy protects nothing.
    assert [p.name for p in tmp_path.iterdir()] == [WIRE_HANDLE_KEY_FILENAME]


def test_the_same_database_gets_the_same_key_forever_because_replay_addresses_it(
        tmp_path):
    """The load-bearing one. A per-run key passes every other test in this file."""
    first = wire_handle_key_for(tmp_path / "agent.sqlite")
    second = wire_handle_key_for(tmp_path / "agent.sqlite")
    third = wire_handle_key_for(tmp_path / "agent.sqlite")

    assert first == second == third


def test_two_databases_do_not_share_a_key(tmp_path):
    # The directories exist because `open_database` makes them before anything
    # asks for a key; this mirrors that order rather than inventing a kinder one.
    for name in ("one", "two"):
        (tmp_path / name).mkdir()
    one = wire_handle_key_for(tmp_path / "one" / "agent.sqlite")
    two = wire_handle_key_for(tmp_path / "two" / "agent.sqlite")
    assert one != two


def test_the_key_file_is_readable_by_this_user_and_by_nobody_else(tmp_path):
    wire_handle_key_for(tmp_path / "agent.sqlite")
    mode = (tmp_path / WIRE_HANDLE_KEY_FILENAME).stat().st_mode & 0o777
    assert mode == 0o600


def test_a_file_that_is_not_a_key_is_refused_rather_than_digested_under(tmp_path):
    """Truncation is the realistic corruption, and half a key is not a short key."""
    (tmp_path / WIRE_HANDLE_KEY_FILENAME).write_bytes(b"\x01" * 8)

    with pytest.raises(SystemExit) as refusal:
        wire_handle_key_for(tmp_path / "agent.sqlite")

    assert "8 bytes" in str(refusal.value)
    assert str(WIRE_HANDLE_KEY_BYTES) in str(refusal.value)


def test_the_refusal_names_the_file_and_never_its_contents(tmp_path):
    """A credential does not appear in an exception message.

    The WHOLE message is asserted rather than a containment, which is the only
    form that catches an addition -- a later `f"got {key!r}"` appended to this
    string would satisfy any "does not contain" check written against the key's
    hex spelling while printing the key in its raw one.
    """
    secret = bytes(range(9)) * 2
    path = tmp_path / WIRE_HANDLE_KEY_FILENAME
    path.write_bytes(secret)

    with pytest.raises(SystemExit) as refusal:
        wire_handle_key_for(tmp_path / "agent.sqlite")

    assert str(refusal.value) == (
        f"{path} is {len(secret)} bytes; a wire handle key is "
        f"{WIRE_HANDLE_KEY_BYTES}. Refusing rather than digesting "
        "identifiers under something that is not a key.")
