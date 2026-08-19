import json
from pathlib import Path

import pytest

from p1_contract import p3_basic_record
from database_agent.db import create_schema
from database_agent.files_table import observe_path
from database_agent.identity import hash_file
from database_agent.verify import (
    VerificationPoint, confirm_cross_volume_copy, verify_content,
)


def _observed(path=None, **overrides):
    fields = dict(author="P3", component_version="p3-fixture",
                  parent_folder_context="corpus", mime_type=None,
                  detected_format=None, scan_state="scanned", materialized=True)
    if path is not None:
        fields.update(p3_basic_record(path))
    fields.update(overrides)
    return fields


def _asked_by_p12(**overrides):
    fields = dict(author="P12", component_version="p12-fixture", materialized=True)
    fields.update(overrides)
    return fields


def test_all_four_points_exist():
    assert [p.name for p in VerificationPoint] == ["V1", "V2", "V3", "V4"]


def test_verify_returns_match_for_unchanged_content(conn, sample_file: Path):
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed(sample_file))
    expected = hash_file(sample_file, materialized=True)
    for point in VerificationPoint:
        if point is VerificationPoint.V4:
            continue
        assert verify_content(conn, file_id, expected, point=point,
                              **_asked_by_p12()) == "match"


def test_verify_returns_mismatch_after_content_changes(conn, sample_file: Path):
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed(sample_file))
    expected = hash_file(sample_file, materialized=True)
    sample_file.write_bytes(b"different bytes entirely")
    assert verify_content(conn, file_id, expected, point=VerificationPoint.V1,
                          **_asked_by_p12()) == "mismatch"


def test_v4_refuses_success_until_destination_hash_is_confirmed(conn, tmp_path: Path):
    create_schema(conn)
    source = tmp_path / "src.bin"
    source.write_bytes(b"payload")
    good = tmp_path / "good.bin"
    good.write_bytes(b"payload")
    bad = tmp_path / "bad.bin"
    bad.write_bytes(b"truncated")
    expected = hash_file(source, materialized=True)

    assert confirm_cross_volume_copy(conn, source=source, destination=good,
                                     expected_hash=expected, **_asked_by_p12()) is True
    assert confirm_cross_volume_copy(conn, source=source, destination=bad,
                                     expected_hash=expected, **_asked_by_p12()) is False


def test_verification_is_recorded_as_a_hashing_event(conn, sample_file: Path):
    # SPEC: the `hashing` event for a verification is authored by the calling part,
    # with `subsystem` naming P1 as the performer.
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed(sample_file))
    before = conn.execute("SELECT count(*) c FROM events").fetchone()["c"]
    verify_content(conn, file_id, hash_file(sample_file, materialized=True),
                   point=VerificationPoint.V2, **_asked_by_p12())
    rows = conn.execute("SELECT * FROM events ORDER BY event_id DESC").fetchall()
    assert conn.execute("SELECT count(*) c FROM events").fetchone()["c"] == before + 1
    assert rows[0]["event_type"] == "hashing"
    assert rows[0]["subsystem"] == "P1"          # performer
    assert json.loads(rows[0]["explanation"])["requested_by"] == "P12"   # author


def test_p1_will_not_verify_without_a_caller(conn, sample_file: Path):
    # The decision that a verification was due is never P1's.
    create_schema(conn)
    file_id = observe_path(conn, sample_file, **_observed(sample_file))
    with pytest.raises(TypeError):
        verify_content(conn, file_id, "abc", point=VerificationPoint.V1)
