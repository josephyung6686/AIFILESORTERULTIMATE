# src/eval_harness/counts.py
"""§8.6's count line, computed from the bundle alone (Done-means 13).

The mappings are P5's, adopted verbatim: fully extracted = files whose EVERY run
is `complete`; deferred = runs at `deferred` or `capped`; unreadable = runs at
`unreadable` or `failed`. P2 recomputes none of them from the observations.

"Files indexed" is reported from BOTH sources, because P2's own Contract out §3
(the bundle_file_entry[] count) and P5's mapping (files with any run) do not agree
and a plan does not resolve a conflict between two specs.
"""
from __future__ import annotations

import sqlite3

#: P5's mapping. §8.6's "89 scanned PDFs deferred after the OCR limit".
DEFERRED_COMPLETENESS: frozenset[str] = frozenset({"deferred", "capped"})

#: P5's mapping. §8.6's "18 files remain unreadable".
UNREADABLE_COMPLETENESS: frozenset[str] = frozenset({"unreadable", "failed"})

#: C4, ratified 2026-08-20 — the ninth `completeness` value gets its own bucket.
#: A source whose bytes are in iCloud is not `deferred` (no budget ran out), not
#: `unreadable` (nothing is damaged) and not `unsupported` (an extractor exists).
#: With no bucket these files either vanished from §8.6's progress line or were
#: counted under a word that lies about why they are missing, which is the exact
#: failure §8.6 exists to prevent: unfinished work must stay visible AS unfinished.
DATALESS_COMPLETENESS: frozenset[str] = frozenset({"dataless"})


def bundle_counts(conn: sqlite3.Connection, bundle_id: str) -> dict:
    """§8.6's legibility counts, with no live filesystem present.

    `files_requiring_model_review` is None, not 0: it is a review-state count that
    P8 owns, and a zero would assert something P2 cannot know. §8.6 asks that
    unmeasured work stay visible as unmeasured.
    """
    entries = conn.execute(
        "SELECT count(*) AS n FROM bundle_file_entry WHERE bundle_id = ?",
        (bundle_id,)).fetchone()["n"]

    by_file: dict[str, list[str]] = {}
    deferred = unreadable = dataless = 0
    for row in conn.execute(
            "SELECT file_id, completeness FROM bundle_extraction_run "
            "WHERE bundle_id = ?", (bundle_id,)):
        by_file.setdefault(row["file_id"], []).append(row["completeness"])
        if row["completeness"] in DEFERRED_COMPLETENESS:
            deferred += 1
        if row["completeness"] in UNREADABLE_COMPLETENESS:
            unreadable += 1
        if row["completeness"] in DATALESS_COMPLETENESS:
            dataless += 1

    return {
        # P2 Contract out §3's reading.
        "files_indexed": entries,
        # P5's mapping, which the same paragraph claims to adopt verbatim. The two
        # differ when a bundle carries a file no extractor ran against.
        "files_with_any_run": len(by_file),
        "files_fully_extracted": sum(
            1 for states in by_file.values()
            if states and all(state == "complete" for state in states)),
        "runs_deferred": deferred,
        "runs_unreadable": unreadable,
        "runs_dataless": dataless,
        # P8's count, not P5's and not P2's.
        "files_requiring_model_review": None,
    }
