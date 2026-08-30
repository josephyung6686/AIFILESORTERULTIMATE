# src/scan_agent/summary.py
"""Contract out R5 — the §8.6 scan-run summary.

§8.6's example line: "1,842 files indexed; 1,611 fully extracted; 89 scanned PDFs
deferred after the OCR limit; 34 files require model review; 18 files remain
unreadable." The `indexed` count is P3's; the extraction, model-review and unreadable
counts are P5's and P8's, and P3 publishes no slot for them.

R5 is a PROJECTION over the records it counts, not a stored row, so a counter cannot
drift from the rows behind it.

`set_aside_paths` is the other half of the same §8.6 obligation, and it had no reader.
The counters above say HOW MANY paths a rule excluded; they cannot say WHICH, and a
person cannot ask for a folder back that they were never told was left behind.
`tree_design.upstream.protected_areas` reads the same `exclusion_verdicts` table and
filters it to `RULE_PROTECTED_CONTAINER`, so §1.1's other three rules -- the literal
directory names, the categories and the software-project descendants -- were recorded
and never surfaced. That is `Library/` on a real person's machine, which is where
their mail and their app data live.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from scan_agent.deferrals import DEFERRED_BUDGET
from scan_agent.exclusion import RULE_PROTECTED_CONTAINER, exclusion_verdicts

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


@dataclass(frozen=True)
class SetAside:
    """One path §1.1 excluded by rule, and the rule that excluded it.

    **Four fields, and none of them a file inside.** §1.1: "An excluded path yields
    no `files` row and no descendants" -- P3 never listed the folder's contents, so
    there is nothing here that could name one. The absence is the same guarantee
    `ProtectedSummary` makes by having nowhere to put a filename: a field that does
    not exist cannot be populated by a later caller in a hurry.
    """

    path: str
    display_label: str
    rule: str
    rule_subject: str | None


def set_aside_paths(conn: sqlite3.Connection, *,
                    scan_run_id: str) -> tuple[SetAside, ...]:
    """Every path §1.1 set aside by rule, EXCEPT the protected containers.

    Protected containers are left out because they are not un-reported -- they have
    their own block, with their own wording about never having been opened, and a
    second appearance here in a second voice is how a person comes to believe two
    different things happened to one folder.

    Filtered on `rule`, not on `label`, for the reason `protected_areas` gives: the
    rule is the DECISION P3 made and the label is §8.6's display category, so
    selecting on the display string would let a presentation change silently alter
    which folders a person is told about.
    """
    return tuple(
        SetAside(path=row["path"], display_label=_folder_name(row["path"]),
                 rule=row["rule"], rule_subject=row["rule_subject"])
        for row in exclusion_verdicts(conn, scan_run_id)
        if row["rule"] != RULE_PROTECTED_CONTAINER
    )


def _folder_name(path: str) -> str:
    """The last segment, as a display label. Never the path."""
    cleaned = path.rstrip("/\\")
    for separator in ("/", "\\"):
        if separator in cleaned:
            cleaned = cleaned.rsplit(separator, 1)[-1]
    return cleaned
