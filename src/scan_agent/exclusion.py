# src/scan_agent/exclusion.py
"""Contract out R3 — §1.1's exclusion rules and the verdict they produce.

§1.1: "Before scanning, the system excludes directories that should not participate
in organization… The exclusion must apply both to scanned sources and to candidate
roots. The engine should ignore `node_modules`, `.git`, `venv`, `build`, `dist`,
`target`, `vendor`, `Pods`, `site-packages`, `Library`, `__pycache__`, build
artifacts, caches, auto-save folders, previews, and generated dependency trees. It
should also reject descendants of software project roots indicated by files such as
`package.json`, `requirements.txt`, `Cargo.toml`, or `go.mod`."

An excluded path yields no `files` row and no descendants.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePath
from types import MappingProxyType

#: §1.1's eleven literal directory names, verbatim and in the design's order.
EXCLUDED_DIRECTORY_NAMES: tuple[str, ...] = (
    "node_modules", ".git", "venv", "build", "dist", "target", "vendor",
    "Pods", "site-packages", "Library", "__pycache__",
)

#: §1.1's five open-ended categories. The design NAMES them and enumerates no member
#: of any of them, so each maps to an empty membership (SPEC Deferred: "the category
#: members are a hand-authored list and are not guessed here"). The rule below is
#: wired against this mapping, so authoring the list is a data change, not a code one.
EXCLUSION_CATEGORIES: tuple[str, ...] = (
    "build artifacts", "caches", "auto-save folders", "previews",
    "generated dependency trees",
)

#: §1.1's four literal software-project-root markers, verbatim and in order.
#: §1.1's "files such as" signals an extensible set and names no other member, so
#: any extension is hand-authored (SPEC Deferred). Four, and no fifth.
PROJECT_ROOT_MARKERS: tuple[str, str, str, str] = (
    "package.json", "requirements.txt", "Cargo.toml", "go.mod",
)
CATEGORY_MEMBERS = MappingProxyType({name: () for name in EXCLUSION_CATEGORIES})

#: R3's `rule` — which §1.1 rule fired. §1.1 states three rule kinds and no fourth.
RULE_LITERAL_DIRECTORY_NAME = "literal directory name"
RULE_CATEGORY = "category"
RULE_PROJECT_ROOT_DESCENDANT = "software project root descendant"

#: R3's `applies_to` — the SPEC's two words, and no third.
APPLIES_TO_SCANNED_SOURCE = "scanned source"
APPLIES_TO_CANDIDATE_ROOT = "candidate root"


@dataclass(frozen=True)
class ExclusionVerdict:
    """R3. One per rejected path, emitted for both sides of the scan."""
    path: str
    rule: str
    rule_subject: str
    applies_to: str


def exclusion_for(path, *, is_dir: bool, applies_to: str,
                  project_root_markers: tuple[str, ...] = ()) -> ExclusionVerdict | None:
    """The §1.1 verdict for one entry, or None when no rule fires.

    `project_root_markers` are the markers observed in the entry's PARENT directory:
    a non-empty tuple means this entry is a descendant of a software project root,
    which §1.1 rejects whether it is a file or a directory.
    """
    name = PurePath(path).name
    if project_root_markers:
        return ExclusionVerdict(str(path), RULE_PROJECT_ROOT_DESCENDANT,
                                project_root_markers[0], applies_to)
    if is_dir and name in EXCLUDED_DIRECTORY_NAMES:
        return ExclusionVerdict(str(path), RULE_LITERAL_DIRECTORY_NAME, name, applies_to)
    if is_dir:
        for category, members in CATEGORY_MEMBERS.items():
            if name in members:
                return ExclusionVerdict(str(path), RULE_CATEGORY, category, applies_to)
    return None

def project_root_markers_in(entry_names) -> tuple[str, ...]:
    """The §1.1 markers observed directly inside one directory, in the design's order.

    A non-empty result makes that directory a software project root, so §1.1 rejects
    its descendants. Whether the marker-bearing directory ITSELF is excluded — and
    whether it may still be a candidate root — is SPEC Q9 and is OPEN: §1.1 says
    only "descendants of software project roots". Nothing here decides it.

    `entry_names` is an iterable of (name, is_dir) pairs: §1.1 says the markers are
    FILES, so a directory called `package.json` is not one.
    """
    files = {name for name, is_dir in entry_names if not is_dir}
    return tuple(marker for marker in PROJECT_ROOT_MARKERS if marker in files)


EXCLUSION_DDL = """
CREATE TABLE IF NOT EXISTS exclusion_verdicts (
    verdict_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id  TEXT NOT NULL REFERENCES scan_runs(scan_run_id),
    path         TEXT NOT NULL,
    rule         TEXT NOT NULL,
    rule_subject TEXT NOT NULL,
    applies_to   TEXT NOT NULL,
    observed_at  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS exclusion_verdicts_no_delete
BEFORE DELETE ON exclusion_verdicts
BEGIN
    SELECT RAISE(ABORT, 'an exclusion verdict survives a later rule-set change');
END;
"""


def record_exclusion(conn: sqlite3.Connection, scan_run_id: str,
                     verdict: ExclusionVerdict) -> int:
    conn.execute(
        "INSERT INTO exclusion_verdicts "
        "(scan_run_id, path, rule, rule_subject, applies_to, observed_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (scan_run_id, verdict.path, verdict.rule, verdict.rule_subject,
         verdict.applies_to, datetime.now(timezone.utc).isoformat()),
    )
    return conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]


def exclusion_verdicts(conn: sqlite3.Connection, scan_run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM exclusion_verdicts WHERE scan_run_id = ? ORDER BY verdict_id",
        (scan_run_id,),
    ).fetchall()
