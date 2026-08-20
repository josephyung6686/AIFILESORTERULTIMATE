# src/scan_agent/replay.py
"""§8.5 — serialize a scan's corpus and re-assert it without a live filesystem.

SPEC Contract in (from P2): "P3 must therefore be runnable against a bundle-backed
corpus source as well as a live filesystem, with identical exclusion and cache
verdicts." SPEC Serialization: "R1–R4 and R6 must serialize into and re-assert from a
P2 replay bundle (§8.5), `curation_signal` included."

P2 owns the bundle ENVELOPE. This module defines the payload P3 can re-assert from,
using P2's spellings where P2 publishes one, and imports no P2 code.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable

from database_agent.identity import HASH_ALGORITHM

from scan_agent.corpus_source import CorpusSource, SnapshotCorpusSource
from scan_agent.deferrals import record_deferral
from scan_agent.exclusion import APPLIES_TO_SCANNED_SOURCE, ExclusionVerdict, record_exclusion
from scan_agent.inventory import record_directory
from scan_agent.run import finish_scan_run, start_scan_run
from scan_agent.selection import (
    record_selection_from_payload, selection_candidate_roots, selection_payload,
    selection_sources,
)
from scan_agent.stat_cache import cache_verdict, prior_observation, record_cache_verdict
from scan_agent.traversal import Deferred, ObservedDirectory, ObservedFile, walk

#: §8.5's two corpus forms, P2's spellings.
CORPUS_FORM_SNAPSHOT = "snapshot"
CORPUS_FORM_METADATA_SAFE = "metadata_safe"


class RecordingCorpusSource:
    """Wraps a CorpusSource and remembers every listing it served.

    The LISTINGS are what a replay needs, not the verdicts: the §1.1 rules have to
    re-fire on replay or the replay proves nothing. The contents of a pruned
    directory were never listed and stay unlisted, which is what reproduces the
    pruning rather than replaying it as a conclusion.
    """

    def __init__(self, inner: CorpusSource):
        self._inner = inner
        self.has_bytes = inner.has_bytes
        self.listings: dict[str, list] = {}

    def entries(self, directory) -> list:
        served = self._inner.entries(directory)
        self.listings[str(directory)] = served
        return served


def snapshot_from(conn: sqlite3.Connection, recording: RecordingCorpusSource, *,
                  selection_id: str, corpus_form: str) -> dict:
    """The re-assertable payload for one recorded scan.

    Carries R1 (SPEC Serialization) so a harness can reproduce the corpus boundary
    from the bundle instead of being told it, and the listings the §1.1 rules re-fire
    over. `content_hash` is carried for §8.5's bundle ("content hashes") and P2's
    `bundle_file_entry`; P3's own replay does not consume it, because P1 publishes no
    entry point that records a file from a supplied hash.
    """
    recorded_hashes = {
        row["current_path"]: row["content_hash"]
        for row in conn.execute("SELECT current_path, content_hash FROM files")
    }
    entries = []
    for directory, served in recording.listings.items():
        for entry in served:
            entries.append({
                "parent": directory,
                "path": entry.path,
                "name": entry.name,
                "kind": entry.kind,
                "size": entry.size,
                "mtime": entry.mtime,
                "dataless": entry.dataless,
                "content_hash": recorded_hashes.get(entry.path),
            })
    return {
        "corpus_form": corpus_form,
        "hash_algorithm": HASH_ALGORITHM,
        # R1 — SPEC Serialization. Written by `selection.py`, which owns the record;
        # this module carries the payload and reads no field of it.
        "selection": selection_payload(conn, selection_id),
        "listed_directories": sorted(recording.listings),
        "entries": entries,
    }


def record_selection_from_snapshot(conn: sqlite3.Connection, snapshot: dict) -> str:
    """Re-assert the bundle's R1 into this database (§8.5). Returns its id.

    The harness's corpus boundary comes from the bundle. Without this, a replay is
    driven by a selection someone re-described by hand, and Serialization's "re-assert
    from a P2 replay bundle" is unmet for R1.
    """
    return record_selection_from_payload(conn, snapshot["selection"])


def replay(conn: sqlite3.Connection, selection_id: str, *,
           snapshot: dict,
           budget_exhausted: Callable[[], bool]) -> str:
    """Re-assert a scan's corpus boundary, cache verdicts and inventory (§8.5).

    Writes NO `files` row and appends NO event: a metadata-safe corpus has no bytes,
    so P1's content-hash identity is unavailable. Done-means 14 asks for identical
    exclusion verdicts, identical cache verdicts and identical curation signals, and
    those are what this reproduces.
    """
    source = SnapshotCorpusSource(snapshot)
    sources = selection_sources(conn, selection_id)
    candidate_roots = selection_candidate_roots(conn, selection_id)
    scan_run_id = start_scan_run(conn, selection_id)

    for item in walk(source, sources=sources, candidate_roots=candidate_roots,
                     budget_exhausted=budget_exhausted):
        if isinstance(item, ExclusionVerdict):
            record_exclusion(conn, scan_run_id, item)
        elif isinstance(item, Deferred):
            record_deferral(conn, scan_run_id, item)
        elif isinstance(item, ObservedDirectory):
            record_directory(conn, scan_run_id, item)
        elif isinstance(item, ObservedFile):
            if item.applies_to != APPLIES_TO_SCANNED_SOURCE or item.dataless:
                continue
            verdict = cache_verdict(item, prior_observation(conn, item.path))
            record_cache_verdict(conn, scan_run_id, item.path, None, verdict)
    finish_scan_run(conn, scan_run_id)
    return scan_run_id


def boundary_fingerprint(conn: sqlite3.Connection, scan_run_id: str) -> dict:
    """The three things Done-means 14 requires to be identical, comparably shaped."""
    return {
        "exclusions": [
            (row["path"], row["rule"], row["rule_subject"], row["applies_to"])
            for row in conn.execute(
                "SELECT path, rule, rule_subject, applies_to FROM exclusion_verdicts "
                "WHERE scan_run_id = ? ORDER BY path, applies_to", (scan_run_id,))
        ],
        "cache": [
            (row["observed_path"], row["verdict"], row["reason"])
            for row in conn.execute(
                "SELECT observed_path, verdict, reason FROM stat_cache_verdicts "
                "WHERE scan_run_id = ? ORDER BY observed_path", (scan_run_id,))
        ],
        "curation": [
            (row["directory_path"], row["curation_signal"])
            for row in conn.execute(
                "SELECT directory_path, curation_signal FROM directory_inventory "
                "WHERE scan_run_id = ? ORDER BY directory_path", (scan_run_id,))
        ],
    }
