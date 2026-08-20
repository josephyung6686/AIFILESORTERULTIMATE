# tests/eval/test_bundle.py
import sqlite3

import pytest

from eval_harness.bundle import (
    BUNDLE_CONTENTS, BodyMismatch, BundleSealed, add_file_entry, bundle_files,
    get_bundle, open_bundle, rebuild_bundle, seal_bundle,
)
from eval_harness.store import create_eval_schema


def _policy():
    """§8.5's "policy settings". privacy_mode and placement_policy are P7's and
    P10's vocabularies and are carried opaquely; the ceiling set is P1's keys."""
    return {"privacy_mode": "offline", "placement_policy": "policy-fixture",
            "budget_ceilings": {}}


def _open(conn, **overrides):
    fields = dict(corpus_form="snapshot", source_scan_ref="scan-fixture",
                  pinned_plan_id="plan-fixture", pinned_plan_version="1",
                  policy_settings=_policy())
    fields.update(overrides)
    return open_bundle(conn, **fields)


def test_the_manifest_carries_every_8_5_content_item():
    # §8.5: "a frozen corpus snapshot or a metadata-safe representation of one,
    # content hashes, extraction outputs, expected facts, accepted groups, tree
    # versions, policy settings, and expected placement or abstention outcomes."
    assert BUNDLE_CONTENTS == (
        "corpus", "content_hashes", "extraction_outputs", "expected_facts",
        "accepted_groups", "tree_versions", "policy_settings",
        "expected_placement_or_abstention",
    )
    assert len(BUNDLE_CONTENTS) == 8


def test_a_bundle_records_its_scan_plan_and_policy(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    row = get_bundle(eval_conn, bundle_id)
    assert row["corpus_form"] == "snapshot"
    # `source_scan_ref` IS P3's published `scan_run_id` — P3 OQ16 / P1 OQ19 closed
    # 2026-08-20: P3 owns the scan (§1.1) so P3 publishes the name, and P1's
    # `start_scan(conn, *, scan_run_id)` keys `scan_resource_usage` on it. That
    # join is what lets a bundle name the scan it captured, and lets P13 put
    # §8.6's six counters beside the file counts from the same scan.
    # The fixture below is still a literal, because this test builds no scan: a
    # bundle stores whatever handle it is given. What changed is that the field is
    # now a shared identity rather than an opaque string P2 must never join on.
    assert row["source_scan_ref"] == "scan-fixture"
    assert row["pinned_plan_id"] == "plan-fixture"           # §8.8
    assert row["pinned_plan_version"] == "1"
    assert '"privacy_mode":"offline"' in row["policy_settings"]
    assert row["created_at"] and row["sealed_at"] is None
    assert row["supersedes_bundle_id"] is None


def test_a_corpus_form_outside_the_two_is_rejected(eval_conn):
    create_eval_schema(eval_conn)
    with pytest.raises(ValueError):
        _open(eval_conn, corpus_form="redacted")


def test_a_snapshot_entry_carries_a_payload_ref_and_not_metadata_only(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn, corpus_form="snapshot")
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   payload_ref="blobs/aa")
    entry = bundle_files(eval_conn, bundle_id)[0]
    assert entry["payload_ref"] == "blobs/aa"
    assert entry["metadata_only"] is None
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low",
                       metadata_only='{"size":10}')


def test_a_metadata_safe_entry_carries_metadata_only_and_no_bytes(eval_conn):
    # A metadata_safe bundle acquiring a payload_ref is the failure SPEC OQ5
    # cannot authorize. Refused structurally, not by review.
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn, corpus_form="metadata_safe")
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="sensitive_personal",
                   metadata_only='{"size":10}')
    entry = bundle_files(eval_conn, bundle_id)[0]
    assert entry["metadata_only"] == '{"size":10}'
    assert entry["payload_ref"] is None
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low",
                       payload_ref="blobs/bb")


def test_an_entry_with_both_bodies_or_neither_is_refused(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                       hash_algorithm="sha256", handling_class="public_low",
                       payload_ref="blobs/aa", metadata_only="{}")
    with pytest.raises(BodyMismatch):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low")


def test_a_sealed_bundle_cannot_be_changed(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   payload_ref="blobs/aa")
    seal_bundle(eval_conn, bundle_id)
    with pytest.raises(BundleSealed):
        add_file_entry(eval_conn, bundle_id, file_id="f2", content_hash="sha256:bb",
                       hash_algorithm="sha256", handling_class="public_low",
                       payload_ref="blobs/bb")
    with pytest.raises(sqlite3.IntegrityError):
        eval_conn.execute("UPDATE bundle_manifest SET corpus_form = 'metadata_safe' "
                          "WHERE bundle_id = ?", (bundle_id,))
    with pytest.raises(sqlite3.IntegrityError):
        eval_conn.execute("DELETE FROM bundle_file_entry WHERE bundle_id = ?",
                          (bundle_id,))


def test_a_rebuild_supersedes_and_retains(eval_conn):
    # §8.2 supersede-never-overwrite; §8.8 a new plan never silently reclassifies.
    create_eval_schema(eval_conn)
    first = _open(eval_conn)
    add_file_entry(eval_conn, first, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   payload_ref="blobs/aa")
    seal_bundle(eval_conn, first)
    second = rebuild_bundle(eval_conn, first, pinned_plan_version="2")
    assert second != first
    assert get_bundle(eval_conn, second)["supersedes_bundle_id"] == first
    assert get_bundle(eval_conn, second)["pinned_plan_version"] == "2"
    # the old one is still there, still sealed, still readable
    assert get_bundle(eval_conn, first)["sealed_at"]
    assert bundle_files(eval_conn, first)[0]["content_hash"] == "sha256:aa"


def test_p2_validates_no_p7_vocabulary(eval_conn):
    # P7 owns the five handling classes and the four operation modes. P2 carries
    # what it is handed. A typo is NOT caught here, deliberately: retyping P7's
    # enum would be two vocabularies for one concept. See Known gaps.
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn)
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="anything-p7-says",
                   payload_ref="blobs/aa")
    assert bundle_files(eval_conn, bundle_id)[0]["handling_class"] == "anything-p7-says"


def test_a_bundle_needs_no_live_filesystem(eval_conn, tmp_path):
    # Done-means 1: built, stored, and read back with nothing on disk to consult.
    create_eval_schema(eval_conn)
    bundle_id = _open(eval_conn, corpus_form="metadata_safe")
    add_file_entry(eval_conn, bundle_id, file_id="f1", content_hash="sha256:aa",
                   hash_algorithm="sha256", handling_class="public_low",
                   metadata_only='{"size":10}')
    seal_bundle(eval_conn, bundle_id)
    assert not any(tmp_path.glob("corpus*"))
    assert bundle_files(eval_conn, bundle_id)[0]["content_hash"] == "sha256:aa"
