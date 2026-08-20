# src/scan_agent/scan.py
"""One scan run: §1.1's boundary and §1.2's records, written through P1."""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from pathlib import Path

from scan_agent.access import require_access
from scan_agent.basic_record import (
    append_external_modification_detection, append_stat_observation, record_basic_record,
)
from scan_agent.stat_cache import (
    VERDICT_REUSE, cache_verdict, prior_observation, record_cache_verdict,
)
from scan_agent.corpus_source import CorpusSource
from scan_agent.dataless import record_dataless_detection
from scan_agent.deferrals import record_deferral
from scan_agent.exclusion import APPLIES_TO_SCANNED_SOURCE, ExclusionVerdict, record_exclusion
from scan_agent.run import finish_scan_run, start_scan_run
from scan_agent.selection import selection_candidate_roots, selection_sources
from scan_agent.traversal import Deferred, ObservedDirectory, ObservedFile, walk
from scan_agent.inventory import record_directory


def scan(conn: sqlite3.Connection, selection_id: str, *,
         source: CorpusSource,
         mime_type_for: Callable[[Path], str | None],
         scan_state: str,
         budget_exhausted: Callable[[], bool]) -> str:
    """Run one scan against one R1 selection. Returns P3's local run handle.

    Full Disk Access is checked BEFORE the run row exists: 11-ops-runtime.md §1 says
    "Until it is granted, P3 does not traverse", and a refused scan should leave no
    partial corpus and no run to mistake for one.
    """
    sources = selection_sources(conn, selection_id)
    candidate_roots = selection_candidate_roots(conn, selection_id)
    require_access([*sources, *candidate_roots])

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
            if item.applies_to != APPLIES_TO_SCANNED_SOURCE:
                continue              # §1.1: roots are context, not corpus
            if item.dataless:
                record_dataless_detection(conn, scan_run_id, item.path)
                continue
            prior = prior_observation(conn, item.path)
            verdict = cache_verdict(item, prior)
            if verdict.verdict == VERDICT_REUSE:
                # §1.2: nothing is re-read. No hash, no observe_path, no files write.
                file_id = prior["file_id"]
                append_stat_observation(conn, file_id, item)
            else:
                if prior is not None:
                    # Done-means 18: a recorded file whose size or modification time
                    # differs. Appended BEFORE the recompute, on the identity the
                    # file was recorded under.
                    append_external_modification_detection(
                        conn, prior["file_id"], item, verdict)
                file_id = record_basic_record(conn, item, mime_type_for=mime_type_for,
                                              scan_state=scan_state)
            record_cache_verdict(conn, scan_run_id, item.path, file_id, verdict)
    finish_scan_run(conn, scan_run_id)
    return scan_run_id
