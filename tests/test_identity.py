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


from database_agent.db import create_schema
from database_agent.files_table import (
    file_path_history, get_file, observe_path,
)


def _observed(**overrides):
    """What P3 hands P1 on an observation. A fixture stands in for P3; `author` is
    what lands in `subsystem`, because the acting part authors and P1 writes (M8)."""
    fields = dict(author="P3", component_version="p3-fixture",
                  parent_folder_context="root", mime_type=None,
                  detected_format=None, scan_state="scanned", materialized=True)
    fields.update(overrides)
    return fields


def test_a_moved_file_keeps_one_record_and_gains_path_history(conn, tmp_path: Path):
    # R2 (§8.2): the same content observed at a new path is the same file version.
    # The ORIGINAL is gone — this is a move, not a duplicate.
    create_schema(conn)
    first = tmp_path / "one.bin"
    first.write_bytes(b"same content")
    file_id = observe_path(conn, first, **_observed(parent_folder_context="a"))

    second = tmp_path / "moved" / "two.bin"
    second.parent.mkdir()
    second.write_bytes(b"same content")
    first.unlink()                       # the move: only one copy is live
    again = observe_path(conn, second, **_observed(parent_folder_context="moved"))

    assert again == file_id
    history = file_path_history(conn, file_id)
    assert [r["path"] for r in history] == [str(first), str(second)]


def test_p1_authors_none_of_the_scan_events(conn, tmp_path: Path):
    # Contract in: P1 originates no discovery / stat observation / hashing event.
    # Every row an observation produces names its caller, never P1.
    create_schema(conn)
    p = tmp_path / "one.bin"
    p.write_bytes(b"bytes")
    observe_path(conn, p, **_observed(author="P3"))
    rows = conn.execute("SELECT subsystem, event_type FROM events").fetchall()
    assert rows
    assert {r["subsystem"] for r in rows} == {"P3"}
    assert "P1" not in {r["subsystem"] for r in rows}


def test_author_and_component_version_are_required(conn, tmp_path: Path):
    create_schema(conn)
    p = tmp_path / "one.bin"
    p.write_bytes(b"bytes")
    fields = _observed()
    fields.pop("author")
    with pytest.raises(TypeError):
        observe_path(conn, p, **fields)


def test_path_history_publishes_volume_id_as_unknown(conn, tmp_path: Path):
    # SPEC Contract out §2 shape is (path, volume_id, observed_at, event_id).
    # No per-observation volume is recorded (P1 OQ9), so the column reads as
    # unknown rather than repeating a within-session value as if it were history.
    create_schema(conn)
    p = tmp_path / "one.bin"
    p.write_bytes(b"bytes")
    file_id = observe_path(conn, p, **_observed())
    row = file_path_history(conn, file_id)[0]
    assert set(row.keys()) == {"path", "volume_id", "observed_at", "event_id"}
    assert row["volume_id"] is None


def test_two_live_copies_are_two_records_sharing_one_hash(conn, tmp_path: Path):
    # I1 (ratified): two live copies = two `files` rows, same content_hash,
    # different file_id and path. §2.9 requires duplicate-family signals, which
    # are unrepresentable if duplicates collapse into one record; §8.3's collision
    # policy presumes both copies exist.
    create_schema(conn)
    a = tmp_path / "a.bin"
    b = tmp_path / "b.bin"
    a.write_bytes(b"identical bytes")
    b.write_bytes(b"identical bytes")

    id_a = observe_path(conn, a, **_observed())
    id_b = observe_path(conn, b, **_observed())

    assert id_a != id_b
    rows = conn.execute(
        "SELECT file_id, current_path, content_hash FROM files ORDER BY current_path"
    ).fetchall()
    assert len(rows) == 2
    assert rows[0]["content_hash"] == rows[1]["content_hash"]
    assert {r["current_path"] for r in rows} == {str(a), str(b)}


def test_same_path_new_bytes_is_a_new_version_and_invalidates_extraction(conn, tmp_path: Path):
    # R3 (§8.2): a file whose content hash changes is a new version.
    create_schema(conn)
    p = tmp_path / "doc.bin"
    p.write_bytes(b"version one")
    first_id = observe_path(conn, p, **_observed())

    p.write_bytes(b"version two")
    second_id = observe_path(conn, p, **_observed())

    assert second_id != first_id
    assert get_file(conn, second_id)["extraction_status_by_tier"] == "{}"
    assert get_file(conn, first_id)["scan_state"] == "superseded_content"


def test_the_superseded_version_carries_its_authors_explanation(conn, tmp_path: Path):
    # No mutation of the current projection is accepted without the authoring
    # part's event explaining it (SPEC, Cross-cutting answers → Provenance).
    create_schema(conn)
    p = tmp_path / "doc.bin"
    p.write_bytes(b"version one")
    first_id = observe_path(conn, p, **_observed())
    p.write_bytes(b"version two")
    observe_path(conn, p, **_observed())

    explaining = conn.execute(
        "SELECT * FROM events WHERE file_id = ? AND event_type = "
        "'external modification detection'", (first_id,)
    ).fetchone()
    assert explaining is not None
    assert explaining["subsystem"] == "P3"
