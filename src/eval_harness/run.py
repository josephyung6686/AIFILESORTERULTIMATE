# src/eval_harness/run.py
"""Contract out §5 — the run manifest.

The six version axes are exactly the six things §8.5 says a bundle may be
re-processed by. `analysis_tiers_enabled[]` is a seventh field, added by
10-i4-learning-ops.md so that "native on, OCR off" is expressible; it is recorded
and compared, and this module does not claim it is a §8.5 axis.

`run_settings` is separate from the tuple because a disable changes WHICH stages
ran, not which version produced them.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from database_agent.budget import CEILING_KEYS

from eval_harness.store import canonical_json, content_ref
from eval_harness.vocabulary import RUN_KINDS

#: §8.5: "a new extractor version, graph algorithm, LLM prompt, model, template
#: library, or placement scorer". Six, and Task 12 names which of them differ.
VERSION_AXES: tuple[str, ...] = (
    "extractor_versions",         # {} — one version per extractor (§3.4)
    "graph_algorithm_version",
    "prompt_fingerprint",         # §3.4
    "model_identifier",           # §3.4
    "template_library_version",
    "placement_scorer_version",
)

#: The seventh field. 10-i4-learning-ops.md, binding: a subset of the four tiers.
VERSION_TUPLE_FIELDS: tuple[str, ...] = VERSION_AXES + ("analysis_tiers_enabled",)

#: The four analysis tiers (I4, ratified). P5 owns the vocabulary; P2's Contract
#: out §5 prints all four inside its own record, which is why they appear here.
ANALYSIS_TIERS: tuple[str, ...] = ("filesystem", "native", "ocr", "llm")

#: Contract out §5 — "Two are required." Independent stage disables, not versions.
RUN_SETTING_KEYS: tuple[str, ...] = ("model_enabled", "embeddings_enabled")

RUN_DDL = """
CREATE TABLE IF NOT EXISTS version_tuple (
    version_tuple_ref TEXT PRIMARY KEY,
    fields            TEXT NOT NULL          -- canonical JSON of the seven fields
);
CREATE TABLE IF NOT EXISTS run_manifest (
    run_id              TEXT PRIMARY KEY,
    bundle_id           TEXT NOT NULL,
    run_kind            TEXT NOT NULL,
    version_tuple_ref   TEXT NOT NULL REFERENCES version_tuple (version_tuple_ref),
    budget_ceilings     TEXT NOT NULL,       -- canonical JSON; the set this run was GIVEN
    run_settings        TEXT NOT NULL,       -- canonical JSON; exactly RUN_SETTING_KEYS
    pinned_plan_id      TEXT,
    pinned_plan_version TEXT,
    started_at          TEXT NOT NULL,
    finished_at         TEXT
);
CREATE INDEX IF NOT EXISTS run_manifest_bundle ON run_manifest (bundle_id);
"""


class UnknownAnalysisTier(Exception):
    """A tier outside I4's ratified four."""


class UnknownRunSetting(Exception):
    """A run setting outside Contract out §5's two."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_version_tuple(conn: sqlite3.Connection, **fields) -> str:
    """Store the seven-field tuple and return its stable reference.

    Two runs given structurally identical tuples share a reference. That is an
    identity of the tuple and NOT a claim that a re-run under it reproduces its
    outputs — §3.4's cache key pins model identifier and prompt fingerprint and
    says nothing about sampling parameters. SPEC Open question 11 is open.
    """
    missing = set(VERSION_TUPLE_FIELDS) - set(fields)
    extra = set(fields) - set(VERSION_TUPLE_FIELDS)
    if missing or extra:
        raise ValueError(f"version tuple fields: missing {sorted(missing)}, "
                         f"unexpected {sorted(extra)}")
    tiers = fields["analysis_tiers_enabled"]
    unknown = [t for t in tiers if t not in ANALYSIS_TIERS]
    if unknown:
        raise UnknownAnalysisTier(
            f"{unknown} outside the four analysis tiers {ANALYSIS_TIERS} (I4)")
    payload = canonical_json({k: fields[k] for k in VERSION_TUPLE_FIELDS})
    ref = content_ref(payload)
    conn.execute(
        "INSERT INTO version_tuple (version_tuple_ref, fields) VALUES (?, ?) "
        "ON CONFLICT(version_tuple_ref) DO NOTHING",
        (ref, payload),
    )
    return ref


def get_version_tuple(conn: sqlite3.Connection, version_tuple_ref: str) -> dict:
    import json
    row = conn.execute(
        "SELECT fields FROM version_tuple WHERE version_tuple_ref = ?",
        (version_tuple_ref,),
    ).fetchone()
    return {} if row is None else json.loads(row["fields"])


def start_run(conn: sqlite3.Connection, *, bundle_id: str, run_kind: str,
              version_tuple_ref: str, budget_ceilings: dict,
              run_settings: dict, pinned_plan_id: str | None,
              pinned_plan_version: str | None) -> str:
    """Open a run. Returns its run_id.

    `budget_ceilings` is the set this run was GIVEN — snapshot it from
    `database_agent.budget.all_ceilings(conn)` at the call site. P2 validates the
    keys against P1's fifteen and validates no value: §8.6's ceilings are
    configurable and hand-authored, and P2 holds keys, never numbers.
    """
    if run_kind not in RUN_KINDS:
        raise ValueError(f"run_kind {run_kind!r} is not one of {RUN_KINDS}")
    for key in budget_ceilings:
        if key not in CEILING_KEYS:
            raise KeyError(f"{key!r} is not one of §8.6's fifteen ceiling keys")
    unknown = set(run_settings) - set(RUN_SETTING_KEYS)
    if unknown:
        raise UnknownRunSetting(
            f"{sorted(unknown)} outside Contract out §5's {RUN_SETTING_KEYS}")
    run_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO run_manifest (run_id, bundle_id, run_kind, version_tuple_ref, "
        "budget_ceilings, run_settings, pinned_plan_id, pinned_plan_version, started_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (run_id, bundle_id, run_kind, version_tuple_ref,
         canonical_json(budget_ceilings), canonical_json(run_settings),
         pinned_plan_id, pinned_plan_version, _now()),
    )
    return run_id


def finish_run(conn: sqlite3.Connection, run_id: str) -> None:
    conn.execute("UPDATE run_manifest SET finished_at = ? WHERE run_id = ?",
                 (_now(), run_id))


def get_run(conn: sqlite3.Connection, run_id: str) -> sqlite3.Row:
    return conn.execute("SELECT * FROM run_manifest WHERE run_id = ?",
                        (run_id,)).fetchone()


def run_ceilings(conn: sqlite3.Connection, run_id: str) -> dict:
    """The ceiling set this run was given, as recorded. Never re-read from config."""
    import json
    row = get_run(conn, run_id)
    return {} if row is None else json.loads(row["budget_ceilings"])


def run_settings(conn: sqlite3.Connection, run_id: str) -> dict:
    import json
    row = get_run(conn, run_id)
    return {} if row is None else json.loads(row["run_settings"])
