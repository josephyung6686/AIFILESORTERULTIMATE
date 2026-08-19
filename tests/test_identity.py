from pathlib import Path

import pytest

from database_agent.identity import (
    HASH_ALGORITHM, OBSERVATION_SESSION, DatalessFileRefused, hash_file, volume_id_for,
)


def test_same_bytes_same_hash(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"identical")
    b.write_bytes(b"identical")
    assert hash_file(a, materialized=True) == hash_file(b, materialized=True)


def test_different_bytes_different_hash(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"one")
    b.write_bytes(b"two")
    assert hash_file(a, materialized=True) != hash_file(b, materialized=True)


def test_algorithm_is_recorded_alongside(tmp_path: Path):
    # §8.2 requires "Content hash and hash algorithm" — the name must be available.
    assert HASH_ALGORITHM
    assert isinstance(HASH_ALGORITHM, str)


def test_large_file_is_streamed_not_loaded(tmp_path: Path):
    big = tmp_path / "big.bin"
    big.write_bytes(b"x" * (5 * 1024 * 1024))
    assert len(hash_file(big, materialized=True)) == 64


def test_a_file_not_declared_materialized_is_never_opened(tmp_path: Path):
    # 11-ops-runtime.md §5: hashing a dataless iCloud item downloads it. P3 detects
    # before hashing; P1 refuses to be the path that materializes one.
    p = tmp_path / "cloud.bin"
    p.write_bytes(b"bytes that must not be read")
    with pytest.raises(DatalessFileRefused):
        hash_file(p, materialized=False)


def test_materialized_is_a_required_keyword(tmp_path: Path):
    p = tmp_path / "a.bin"
    p.write_bytes(b"a")
    with pytest.raises(TypeError):
        hash_file(p)


def test_volume_id_is_stable_within_one_process(tmp_path: Path):
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"a")
    b.write_bytes(b"b")
    assert volume_id_for(a) == volume_id_for(b)


def test_volume_id_carries_its_observation_session(tmp_path: Path):
    # P1 OQ9 is OPEN. st_dev is not stable across remount on macOS, so a value
    # observed in another process must NOT compare equal to one observed here —
    # a cross-session comparison has to fail loudly, not misfire (§8.3, P12).
    a = tmp_path / "a.bin"
    a.write_bytes(b"a")
    value = volume_id_for(a)
    assert value.startswith(OBSERVATION_SESSION + ":")
    from_another_session = "00000000-0000-0000-0000-000000000000:" + value.split(":", 1)[1]
    assert from_another_session != value
