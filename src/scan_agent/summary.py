# src/scan_agent/summary.py
"""Contract out R5 — the §8.6 scan-run summary.

§8.6's example line: "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs
deferred after the OCR limit; 34 files require model review; 18 files remain
unreadable." The `indexed` count is P3's; the extraction, model-review and unreadable
counts are P5's and P8's, and P3 publishes no slot for them.

R5 is a PROJECTION over the records it counts, not a stored row, so a counter cannot
drift from the rows behind it.
"""
from __future__ import annotations

import sqlite3

from scan_agent.deferrals import DEFERRED_BUDGET

#: The SPEC's five, in the SPEC's order. There is no sixth.
R5_COUNTERS: tuple[str, ...] = (
    "files_indexed", "paths_excluded_by_rule", "files_reused_from_stat_cache",
    "files_recomputed", "files_deferred",
)


def scan_run_summary(conn: sqlite3.Connection, scan_run_id: str) -> dict:
    """R5 for one run."""
    indexed = conn.execute(
        "SELECT count(DISTINCT file_id) AS c FROM stat_cache_verdicts "
        "WHERE scan_run_id = ? AND file_id IS NOT NULL", (scan_run_id,)
    ).fetchone()["c"]

    by_rule = {
        row["rule"]: row["c"] for row in conn.execute(
            "SELECT rule, count(*) AS c FROM exclusion_verdicts WHERE scan_run_id = ? "
            "GROUP BY rule", (scan_run_id,)
        )
    }

    verdicts = {
        row["verdict"]: row["c"] for row in conn.execute(
            "SELECT verdict, count(*) AS c FROM stat_cache_verdicts "
            "WHERE scan_run_id = ? GROUP BY verdict", (scan_run_id,)
        )
    }

    # "files deferred (scan budget exhausted)" — the SPEC's spelling, so the counter
    # filters on the budget reason. The other deferral reasons (Q7, Q14, and the
    # directory that could not be read) are readable from `scan_deferrals` without
    # an invented counter.
    deferred = conn.execute(
        "SELECT count(*) AS c FROM scan_deferrals "
        "WHERE scan_run_id = ? AND reason = ? AND is_directory = 0",
        (scan_run_id, DEFERRED_BUDGET),
    ).fetchone()["c"]

    return {
        "files_indexed": indexed,
        "paths_excluded_by_rule": by_rule,
        "files_reused_from_stat_cache": verdicts.get("reuse", 0),
        "files_recomputed": verdicts.get("recompute", 0),
        "files_deferred": deferred,
    }
