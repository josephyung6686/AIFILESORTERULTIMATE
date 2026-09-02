# tests/eval/test_bundle_recording.py
"""§8.5's "frozen corpus snapshot", and the name a person calls it by.

§8.5 says a replay bundle contains "a frozen corpus snapshot or a metadata-safe
representation of one". `bundle_manifest.corpus_form` named WHICH of the two and
nothing stored the payload -- `bundle_file_entry.payload_ref` is a content hash --
so `scan_agent.snapshot_from()`'s output had nowhere to go and no bundle in this
repository could build a `SnapshotCorpusSource`. That is what this table is for.

The name is the other half and it is not decoration. A bundle id is a uuid4, and
a gesture whose argument a person can only obtain by reading it off a previous
screen is a gesture nobody uses twice. `--record` takes the name; `--replay`
accepts it.
"""
from __future__ import annotations

import pytest

from scan_agent.corpus_source import SnapshotCorpusSource

from eval_harness.bundle import (
    RecordingNameTaken, bundle_named, name_recording, open_bundle,
    rebuild_bundle, recording_for, seal_bundle,
)
from eval_harness.store import EVAL_SCHEMA_VERSION, create_eval_schema

SNAPSHOT = {
    "corpus_form": "snapshot",
    "hash_algorithm": "sha256",
    "selection": {"sources": ["/corpus"], "candidate_roots": []},
    "listed_directories": ["/corpus"],
    "entries": [
        {"parent": "/corpus", "path": "/corpus/a.txt", "name": "a.txt",
         "kind": "file", "size": 1, "mtime": 0.0, "dataless": False,
         "content_hash": "h1"},
        {"parent": "/corpus", "path": "/corpus/sub", "name": "sub",
         "kind": "directory", "size": 0, "mtime": 0.0, "dataless": False,
         "content_hash": None},
    ],
}


@pytest.fixture()
def conn(eval_conn):
    create_eval_schema(eval_conn)
    return eval_conn


def _open(conn):
    return open_bundle(
        conn, corpus_form="snapshot", source_scan_ref="scan-1",
        pinned_plan_id=None, pinned_plan_version=None, policy_settings={})


def test_the_schema_records_the_version_that_added_the_table(conn):
    """P1's `SCHEMA_VERSION` sets the shape: the bump RECORDS the change and does
    not gate behaviour. Nothing reads this value to decide what to do."""
    assert EVAL_SCHEMA_VERSION == 2
    assert conn.execute(
        "SELECT value FROM eval_schema_meta WHERE key = 'eval_schema_version'"
    ).fetchone()["value"] == "2"


def test_a_recording_carries_the_snapshot_and_the_name(conn):
    bundle_id = _open(conn)
    name_recording(conn, bundle_id, name="before-upgrade", snapshot=SNAPSHOT)
    seal_bundle(conn, bundle_id)

    record = recording_for(conn, bundle_id)

    assert record["name"] == "before-upgrade"
    assert record["snapshot"] == SNAPSHOT
    assert bundle_named(conn, "before-upgrade") == bundle_id


def test_a_bundle_with_no_recording_reads_as_none_rather_than_raising(conn):
    """Every bundle P1--P7 has ever sealed is one of these. An unnamed bundle is
    a real state -- the ordinary run records one on every scan -- and it is not
    an error, so the reader says so rather than raising at every caller."""
    bundle_id = _open(conn)
    seal_bundle(conn, bundle_id)

    assert recording_for(conn, bundle_id) is None
    assert bundle_named(conn, "before-upgrade") is None


def test_a_name_already_taken_is_refused_and_nothing_is_written(conn):
    """Absent means refuse, never guess -- and so does ambiguous. Two bundles
    sharing a name make `--replay before-upgrade` a question with two answers,
    and choosing one would replay a corpus the person did not name.

    Refused at RECORD time rather than at replay time because that is when the
    person can still do something about it: they are told immediately, by a
    message that names the bundle already holding it."""
    first = _open(conn)
    name_recording(conn, first, name="before-upgrade", snapshot=SNAPSHOT)
    seal_bundle(conn, first)
    second = _open(conn)

    with pytest.raises(RecordingNameTaken) as refused:
        name_recording(conn, second, name="before-upgrade", snapshot=SNAPSHOT)

    assert first in str(refused.value)
    assert "before-upgrade" in str(refused.value)
    # Nothing written for the second bundle: a refusal that half-wrote would
    # leave a recording nobody asked for.
    assert recording_for(conn, second) is None
    assert bundle_named(conn, "before-upgrade") == first


def test_a_sealed_recording_cannot_be_written_updated_or_deleted(conn):
    """The three triggers every other child table carries. A table given the
    writer check and not the triggers is mutable after sealing to anything
    holding the connection."""
    import sqlite3

    bundle_id = _open(conn)
    name_recording(conn, bundle_id, name="before-upgrade", snapshot=SNAPSHOT)
    seal_bundle(conn, bundle_id)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE bundle_recording SET name = 'other' "
                     "WHERE bundle_id = ?", (bundle_id,))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM bundle_recording WHERE bundle_id = ?",
                     (bundle_id,))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO bundle_recording (bundle_id, name, snapshot) "
                     "VALUES (?, 'other', '{}')", (bundle_id,))


def test_naming_a_sealed_bundle_is_refused(conn):
    """The writer check, ahead of the trigger. A sealed bundle is immutable, and
    a rebuild is how a person gets a bundle that carries more (§8.2)."""
    from eval_harness.bundle import BundleSealed

    bundle_id = _open(conn)
    seal_bundle(conn, bundle_id)

    with pytest.raises(BundleSealed):
        name_recording(conn, bundle_id, name="before-upgrade", snapshot=SNAPSHOT)


def test_a_rebuild_links_the_bundle_it_supersedes(conn):
    """The link is what stops a reader of `bundle_manifest` mistaking the second
    bundle for a second recording of the same corpus. It is the first plus what
    P9--P11 produced, and the manifest says so."""
    first = _open(conn)
    seal_bundle(conn, first)

    second = rebuild_bundle(conn, first)

    from eval_harness.bundle import get_bundle
    assert get_bundle(conn, second)["supersedes_bundle_id"] == first
    assert get_bundle(conn, first)["supersedes_bundle_id"] is None


def test_the_stored_snapshot_drives_a_corpus_source_with_no_filesystem(conn):
    """The property that makes storing it worth anything. §8.5 asks for
    evaluation "without touching a live filesystem", and a snapshot that cannot
    be handed to P3's `SnapshotCorpusSource` is a blob nobody can replay."""
    bundle_id = _open(conn)
    name_recording(conn, bundle_id, name="before-upgrade", snapshot=SNAPSHOT)
    seal_bundle(conn, bundle_id)

    source = SnapshotCorpusSource(recording_for(conn, bundle_id)["snapshot"])

    assert source.has_bytes is True
    assert [entry.path for entry in source.entries("/corpus")] == [
        "/corpus/a.txt", "/corpus/sub"]
    # A directory nobody listed stays unlisted, which is what reproduces a
    # pruning rather than replaying it as a conclusion.
    assert source.entries("/corpus/sub") == []
