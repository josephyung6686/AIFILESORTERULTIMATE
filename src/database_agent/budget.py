"""Contract out §8 — the §8.6 budget configuration object (S5, G4).

Fifteen keys, because three of §8.6's twelve ceilings are held by two parts on
different graphs and are namespaced accordingly (O10). P1 holds and publishes
values; P1 enforces none of them. Reading a ceiling is not enforcing it.
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
    "tree.max_folder_proposals_and_depth",
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
        raise KeyError(f"{key!r} is not one of §8.6's fifteen ceiling keys")


def set_ceiling(conn: sqlite3.Connection, key: str, value: int) -> None:
    _check(key)
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
    return {r["key"]: r["value"] for r in conn.execute("SELECT key, value FROM budget_ceilings")}
