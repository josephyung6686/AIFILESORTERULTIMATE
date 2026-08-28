"""Contract out §8 — the §8.6 budget configuration object (S5, G4).

Seventeen keys. Three of §8.6's twelve ceilings are held by two parts on different
graphs and are namespaced accordingly (O10), giving fifteen; the sixteenth is
`evidence.context_window`, ratified 2026-08-20; the seventeenth is `tree.max_depth`,
2026-08-29. P1 holds and publishes values; P1 enforces none of them. Reading a
ceiling is not enforcing it.
"""
from __future__ import annotations

import sqlite3

CEILING_KEYS: tuple[str, ...] = (
    "ocr.max_pages_per_file",
    "ocr.max_time_per_file",
    "ocr.max_time_per_scan",
    "image.max_analysis_ops_per_scan",
    "model.max_llm_calls_per_thousand_files",
    "model.max_cost_per_scan",
    "model.max_dossier_tokens_per_call",
    "grouping.max_retrieved_neighbors",
    "placement.max_retrieved_neighbors",
    "grouping.max_local_graph_neighborhood",
    "placement.max_local_graph_neighborhood",
    "grouping.max_candidate_cluster_size",
    "placement.max_candidate_cluster_size",
    "residual.max_files_per_review_batch",
    #: The seventeenth, and its twin, 2026-08-29. `00`:256 names TWO numbers on
    #: one line -- "Maximum folder proposals and maximum depth" -- and this tuple
    #: carried one key for both, `tree.max_folder_proposals_and_depth`. Every
    #: other line in that list is one quantity; this one is two, and P10 was
    #: reading the single value FOUR times: how many options the picker offers,
    #: how deep a candidate may go, how wide a date level may be, and the sample
    #: size of the printed lists. The first two want opposite values -- `00`:78's
    #: own recommended tree is five levels deep, and a picker offering five
    #: options per branch is not a picker -- so no P10 change could reconcile
    #: them, which `tree_design/config.py` recorded as a standing complaint and
    #: `test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit` failed
    #: over for as long as the key was one. Splitting it publishes what §8.6
    #: already names; it does not add a ceiling the design does not state.
    "tree.max_folder_proposals",
    "tree.max_depth",
    #: The sixteenth, ratified 2026-08-20. §2.8 requires surrounding context be
    #: stored and §8.6 forbids silent truncation, yet none of §8.6's twelve — and
    #: none of the other fifteen — is a context length, so the budget had nowhere
    #: to live and P4 held it caller-supplied with no number. It belongs here AND
    #: in the extraction run's `config` fingerprint: a ceiling outside the
    #: fingerprint makes two runs at different context widths look identical to
    #: §3.4's cache key and §8.5's replay, which is a silent wrong answer.
    "evidence.context_window",
)

BUDGET_DDL = """
CREATE TABLE IF NOT EXISTS budget_ceilings (
    key           TEXT PRIMARY KEY,
    value         INTEGER NOT NULL,
    object_version INTEGER NOT NULL DEFAULT 1
);
"""


def _check(key: str) -> None:
    if key not in CEILING_KEYS:
        raise KeyError(
            f"{key!r} is not one of the seventeen published ceiling keys")


def set_ceiling(conn: sqlite3.Connection, key: str, value: int) -> None:
    _check(key)
    if type(value) is not int:
        raise TypeError(f"ceiling {key!r} must be an int, not {type(value).__name__}")
    conn.execute(
        "INSERT INTO budget_ceilings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
        "object_version = object_version + 1",
        (key, value),
    )


def get_ceiling(conn: sqlite3.Connection, key: str) -> int | None:
    _check(key)
    row = conn.execute("SELECT value FROM budget_ceilings WHERE key = ?", (key,)).fetchone()
    return None if row is None else row["value"]


def all_ceilings(conn: sqlite3.Connection) -> dict[str, int]:
    return {
        r["key"]: r["value"]
        for r in conn.execute("SELECT key, value FROM budget_ceilings")
        if r["key"] in CEILING_KEYS
    }
