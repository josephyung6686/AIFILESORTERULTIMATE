# src/eval_harness/bundle.py
"""Contract out §3 — the replay bundle.

Contents are exactly §8.5's list. A bundle is immutable once sealed, and a rebuild
is a NEW bundle that supersedes the old and retains it (§8.2, §8.8).

P2 records `handling_class` and `privacy_mode` and validates neither: those are
P7's closed vocabularies and copying them here would be two vocabularies for one
concept. P2 does not decide whether a bundle may leave the device — SPEC Open
question 5 is open and there is no export path in this module.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from eval_harness.store import canonical_json
from eval_harness.vocabulary import CORPUS_FORMS

#: §8.5's contents list, verbatim, as the names of the things a bundle must hold.
#: Each maps to a table created here or in Tasks 6-8.
BUNDLE_CONTENTS: tuple[str, ...] = (
    "corpus",                            # bundle_file_entry.body (both forms)
    "content_hashes",                    # bundle_file_entry.content_hash
    "extraction_outputs",                # bundle_extraction_output/_run/_text_unit (Task 6)
    "expected_facts",                    # bundle_expectation, dimension = fact (Task 8)
    "accepted_groups",                   # bundle_accepted_group (Task 8)
    "tree_versions",                     # bundle_manifest.pinned_plan_id/version
    "policy_settings",                   # bundle_manifest.policy_settings
    "expected_placement_or_abstention",  # bundle_expectation, dimensions 9 and 10 (Task 8)
)

BUNDLE_DDL = """
CREATE TABLE IF NOT EXISTS bundle_manifest (
    bundle_id            TEXT PRIMARY KEY,
    created_at           TEXT NOT NULL,
    corpus_form          TEXT NOT NULL,
    source_scan_ref      TEXT,
    pinned_plan_id       TEXT,
    pinned_plan_version  TEXT,
    policy_settings      TEXT NOT NULL,
    supersedes_bundle_id TEXT REFERENCES bundle_manifest (bundle_id),
    sealed_at            TEXT
);
CREATE TABLE IF NOT EXISTS bundle_file_entry (
    bundle_id      TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    file_id        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    hash_algorithm TEXT NOT NULL,
    handling_class TEXT,                 -- P7's vocabulary, carried opaquely
    payload_ref    TEXT,                 -- corpus_form = snapshot
    metadata_only  TEXT,                 -- corpus_form = metadata_safe
    PRIMARY KEY (bundle_id, file_id)
);

-- A sealed bundle is immutable (Contract out §3). These triggers are on P2's own
-- tables; `events` is P1's and P2 never writes it.
CREATE TRIGGER IF NOT EXISTS bundle_manifest_sealed_no_update
BEFORE UPDATE ON bundle_manifest
WHEN OLD.sealed_at IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_manifest_sealed_no_delete
BEFORE DELETE ON bundle_manifest
WHEN OLD.sealed_at IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'a sealed bundle is retained, never deleted (8.2)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_file_entry_sealed_no_insert
BEFORE INSERT ON bundle_file_entry
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_file_entry_sealed_no_update
BEFORE UPDATE ON bundle_file_entry
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_file_entry_sealed_no_delete
BEFORE DELETE ON bundle_file_entry
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;
CREATE TABLE IF NOT EXISTS bundle_extraction_output (
    bundle_id         TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    content_hash      TEXT NOT NULL,
    extractor_version TEXT NOT NULL,
    observation_key   TEXT NOT NULL,   -- P4's citation handle; EXCLUDES the version
    payload           TEXT,            -- opaque observation payload
    PRIMARY KEY (bundle_id, content_hash, extractor_version, observation_key)
);
CREATE TABLE IF NOT EXISTS bundle_extraction_run (
    bundle_id          TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    run_id             TEXT NOT NULL,
    file_id            TEXT,
    content_hash       TEXT,
    extractor_name     TEXT,
    extractor_version  TEXT,
    source_type        TEXT,
    config_fingerprint TEXT,
    completeness       TEXT,
    coverage           TEXT,           -- P4's {units, processed, total}, canonical JSON
    observation_count  INTEGER,
    row                TEXT NOT NULL,  -- P4's whole row, verbatim; nothing is lost
    PRIMARY KEY (bundle_id, run_id)
);
CREATE TABLE IF NOT EXISTS bundle_text_unit (
    bundle_id     TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    run_id        TEXT NOT NULL,
    unit_locator  TEXT NOT NULL,
    row           TEXT NOT NULL,       -- P4's whole row, verbatim
    PRIMARY KEY (bundle_id, run_id, unit_locator)
);

-- Three seal triggers per content table, the same set bundle_file_entry carries.
-- Written out rather than generated: SQLite has no parameterized trigger, and a
-- table given the writer check but not the triggers is mutable after sealing to
-- anything holding the connection. `_require_open` in the Python writer is the
-- first line and this is the second; the guarantee in Task 5's prose is "every
-- INSERT, UPDATE or DELETE on a child row raises", which is only true if every
-- child table has all three.
CREATE TRIGGER IF NOT EXISTS bundle_extraction_output_sealed_no_insert
BEFORE INSERT ON bundle_extraction_output
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_extraction_output_sealed_no_update
BEFORE UPDATE ON bundle_extraction_output
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_extraction_output_sealed_no_delete
BEFORE DELETE ON bundle_extraction_output
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_extraction_run_sealed_no_insert
BEFORE INSERT ON bundle_extraction_run
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_extraction_run_sealed_no_update
BEFORE UPDATE ON bundle_extraction_run
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_extraction_run_sealed_no_delete
BEFORE DELETE ON bundle_extraction_run
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_text_unit_sealed_no_insert
BEFORE INSERT ON bundle_text_unit
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_text_unit_sealed_no_update
BEFORE UPDATE ON bundle_text_unit
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_text_unit_sealed_no_delete
BEFORE DELETE ON bundle_text_unit
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;
CREATE TABLE IF NOT EXISTS bundle_learning_record (
    bundle_id      TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    event_id       INTEGER NOT NULL,
    scope          TEXT NOT NULL,
    subject_id     TEXT NOT NULL,
    polarity       TEXT,          -- opaque; accept | reject, supplied by the acting part
    proposal_class TEXT,          -- opaque
    basis_key      TEXT,          -- opaque
    row            TEXT NOT NULL, -- P1's whole row, verbatim, incl. §8.2's explanation
    PRIMARY KEY (bundle_id, event_id)
);

CREATE TRIGGER IF NOT EXISTS bundle_learning_record_sealed_no_insert
BEFORE INSERT ON bundle_learning_record
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_learning_record_sealed_no_update
BEFORE UPDATE ON bundle_learning_record
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_learning_record_sealed_no_delete
BEFORE DELETE ON bundle_learning_record
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;
CREATE TABLE IF NOT EXISTS bundle_accepted_group (
    bundle_id TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    group_id  TEXT NOT NULL,
    row       TEXT NOT NULL,   -- P9's group_acceptance row, resolved by P9, verbatim
    PRIMARY KEY (bundle_id, group_id)
);
CREATE TABLE IF NOT EXISTS bundle_expectation (
    bundle_id             TEXT NOT NULL REFERENCES bundle_manifest (bundle_id),
    dimension             TEXT NOT NULL,
    subject_ref           TEXT NOT NULL,
    expected_value        TEXT,           -- canonical JSON; opaque, another part's vocabulary
    expected_outcome_kind TEXT NOT NULL,
    source                TEXT NOT NULL,
    PRIMARY KEY (bundle_id, dimension, subject_ref)
);

CREATE TRIGGER IF NOT EXISTS bundle_accepted_group_sealed_no_insert
BEFORE INSERT ON bundle_accepted_group
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_accepted_group_sealed_no_update
BEFORE UPDATE ON bundle_accepted_group
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_accepted_group_sealed_no_delete
BEFORE DELETE ON bundle_accepted_group
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_expectation_sealed_no_insert
BEFORE INSERT ON bundle_expectation
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = NEW.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_expectation_sealed_no_update
BEFORE UPDATE ON bundle_expectation
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;

CREATE TRIGGER IF NOT EXISTS bundle_expectation_sealed_no_delete
BEFORE DELETE ON bundle_expectation
WHEN (SELECT sealed_at FROM bundle_manifest WHERE bundle_id = OLD.bundle_id) IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'bundle is immutable once sealed (P2 Contract out 3)'); END;
"""


class BundleSealed(Exception):
    """A sealed bundle was written to. Rebuild instead — it supersedes (§8.2)."""


class BodyMismatch(Exception):
    """An entry's body does not match its bundle's declared corpus_form."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def open_bundle(conn: sqlite3.Connection, *, corpus_form: str,
                source_scan_ref: str | None, pinned_plan_id: str | None,
                pinned_plan_version: str | None, policy_settings: dict,
                supersedes_bundle_id: str | None = None) -> str:
    """Open a draft bundle. Fill it, then `seal_bundle` to make it immutable."""
    if corpus_form not in CORPUS_FORMS:
        raise ValueError(f"corpus_form {corpus_form!r} is not one of {CORPUS_FORMS}")
    bundle_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO bundle_manifest (bundle_id, created_at, corpus_form, "
        "source_scan_ref, pinned_plan_id, pinned_plan_version, policy_settings, "
        "supersedes_bundle_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (bundle_id, _now(), corpus_form, source_scan_ref, pinned_plan_id,
         pinned_plan_version, canonical_json(policy_settings), supersedes_bundle_id),
    )
    return bundle_id


def _require_open(conn: sqlite3.Connection, bundle_id: str) -> sqlite3.Row:
    row = get_bundle(conn, bundle_id)
    if row is None:
        raise KeyError(f"no bundle {bundle_id!r}")
    if row["sealed_at"] is not None:
        raise BundleSealed(
            f"bundle {bundle_id} was sealed at {row['sealed_at']}; a rebuild "
            "creates a new bundle that supersedes it (§8.2)"
        )
    return row


def add_file_entry(conn: sqlite3.Connection, bundle_id: str, *, file_id: str,
                   content_hash: str, hash_algorithm: str,
                   handling_class: str | None,
                   payload_ref: str | None = None,
                   metadata_only: str | None = None) -> None:
    """One `bundle_file_entry`. Exactly one body, fixed by the bundle's corpus_form."""
    row = _require_open(conn, bundle_id)
    if (payload_ref is None) == (metadata_only is None):
        raise BodyMismatch("an entry carries exactly one body: payload_ref "
                           "(snapshot) or metadata_only (metadata_safe)")
    if row["corpus_form"] == "snapshot" and payload_ref is None:
        raise BodyMismatch("a snapshot bundle's entries carry payload_ref")
    if row["corpus_form"] == "metadata_safe" and metadata_only is None:
        raise BodyMismatch(
            "a metadata_safe bundle's entries carry metadata_only; whether such a "
            "bundle may carry anything more is SPEC Open question 5, not P2's call"
        )
    conn.execute(
        "INSERT INTO bundle_file_entry (bundle_id, file_id, content_hash, "
        "hash_algorithm, handling_class, payload_ref, metadata_only) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (bundle_id, file_id, content_hash, hash_algorithm, handling_class,
         payload_ref, metadata_only),
    )


def seal_bundle(conn: sqlite3.Connection, bundle_id: str) -> None:
    _require_open(conn, bundle_id)
    conn.execute("UPDATE bundle_manifest SET sealed_at = ? WHERE bundle_id = ?",
                 (_now(), bundle_id))


def get_bundle(conn: sqlite3.Connection, bundle_id: str) -> sqlite3.Row:
    return conn.execute("SELECT * FROM bundle_manifest WHERE bundle_id = ?",
                        (bundle_id,)).fetchone()


def bundle_files(conn: sqlite3.Connection, bundle_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM bundle_file_entry WHERE bundle_id = ? ORDER BY file_id",
        (bundle_id,)).fetchall()


def rebuild_bundle(conn: sqlite3.Connection, bundle_id: str, **overrides) -> str:
    """Open a NEW bundle that supersedes `bundle_id`. The old one is retained.

    §8.2's supersede-never-overwrite, applied to bundles. The caller re-adds the
    contents it wants; nothing is copied silently, because a rebuild that quietly
    carried the old contents forward would make the two indistinguishable.
    """
    old = get_bundle(conn, bundle_id)
    if old is None:
        raise KeyError(f"no bundle {bundle_id!r}")
    import json
    fields = dict(
        corpus_form=old["corpus_form"], source_scan_ref=old["source_scan_ref"],
        pinned_plan_id=old["pinned_plan_id"],
        pinned_plan_version=old["pinned_plan_version"],
        policy_settings=json.loads(old["policy_settings"]),
    )
    fields.update(overrides)
    return open_bundle(conn, supersedes_bundle_id=bundle_id, **fields)


#: P4 SPEC Record 2 (D5), the subset SPEC Contract out §3 enumerates and P2 queries.
#: Every other field P4 publishes is retained verbatim in the `row` column.
P4_RUN_FIELDS: tuple[str, ...] = (
    "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "config_fingerprint", "completeness", "coverage",
    "observation_count",
)

#: P4 SPEC Record 3 (D12, G1). P2 defines none of it.
P4_TEXT_UNIT_FIELDS: tuple[str, ...] = (
    "run_id", "container_path", "unit_locator", "text", "length", "truncated",
)


def add_extraction_output(conn: sqlite3.Connection, bundle_id: str, *,
                          content_hash: str, extractor_version: str,
                          observation_key: str, payload: str | None) -> None:
    """One opaque observation payload, keyed by content hash PLUS extractor version.

    The key deliberately diverges from P4's `observation_key`, which excludes the
    version so a citation survives an upgrade (§8.7). Both are stored: the key
    holds two versions apart for a diff, `observation_key` holds them together for
    a citation.
    """
    _require_open(conn, bundle_id)
    conn.execute(
        "INSERT INTO bundle_extraction_output (bundle_id, content_hash, "
        "extractor_version, observation_key, payload) VALUES (?, ?, ?, ?, ?)",
        (bundle_id, content_hash, extractor_version, observation_key, payload),
    )


def add_extraction_run(conn: sqlite3.Connection, bundle_id: str, *, row: dict) -> None:
    """One P4 `extraction_runs` row, read exactly as P4 publishes it."""
    _require_open(conn, bundle_id)
    promoted = [row.get(f) for f in P4_RUN_FIELDS]
    promoted[P4_RUN_FIELDS.index("coverage")] = canonical_json(row.get("coverage"))
    conn.execute(
        "INSERT INTO bundle_extraction_run (bundle_id, "
        + ", ".join(P4_RUN_FIELDS) + ", row) VALUES ("
        + ", ".join("?" * (len(P4_RUN_FIELDS) + 2)) + ")",
        (bundle_id, *promoted, canonical_json(row)),
    )


def add_text_unit(conn: sqlite3.Connection, bundle_id: str, *, row: dict) -> None:
    """One P4 `text_units` row (D12, G1), read exactly as P4 publishes it."""
    manifest = _require_open(conn, bundle_id)
    if manifest["corpus_form"] == "metadata_safe":
        raise NotImplementedError(
            "whether a metadata_safe bundle may carry text_units is SPEC Open "
            "question 5 (§8.4 requires full extracted text to remain local; §8.5 "
            "offers a metadata-safe representation and defines neither). P2 does "
            "not decide it."
        )
    conn.execute(
        "INSERT INTO bundle_text_unit (bundle_id, run_id, unit_locator, row) "
        "VALUES (?, ?, ?, ?)",
        (bundle_id, row["run_id"], row["unit_locator"], canonical_json(row)),
    )


def extraction_outputs(conn: sqlite3.Connection, bundle_id: str, *,
                       content_hash: str | None = None,
                       extractor_version: str | None = None) -> list[sqlite3.Row]:
    sql = "SELECT * FROM bundle_extraction_output WHERE bundle_id = ?"
    args: list = [bundle_id]
    if content_hash is not None:
        sql += " AND content_hash = ?"
        args.append(content_hash)
    if extractor_version is not None:
        sql += " AND extractor_version = ?"
        args.append(extractor_version)
    return conn.execute(sql + " ORDER BY content_hash, extractor_version",
                        args).fetchall()


def extraction_runs(conn: sqlite3.Connection, bundle_id: str) -> list[dict]:
    """P4's rows, as P4 wrote them."""
    import json
    return [json.loads(r["row"]) for r in conn.execute(
        "SELECT row FROM bundle_extraction_run WHERE bundle_id = ? ORDER BY run_id",
        (bundle_id,))]


def text_units(conn: sqlite3.Connection, bundle_id: str, *,
               run_id: str | None = None) -> list[dict]:
    import json
    if run_id is None:
        rows = conn.execute(
            "SELECT row FROM bundle_text_unit WHERE bundle_id = ? "
            "ORDER BY run_id, unit_locator", (bundle_id,))
    else:
        rows = conn.execute(
            "SELECT row FROM bundle_text_unit WHERE bundle_id = ? AND run_id = ? "
            "ORDER BY unit_locator", (bundle_id, run_id))
    return [json.loads(r["row"]) for r in rows]


#: SPEC Contract out §3's named fields. "evidence refs" is §8.2's "structured
#: explanation or evidence reference", which P1 spells `explanation` and which
#: survives in the verbatim `row`. P2 mints no second name for it.
LEARNING_RECORD_FIELDS: tuple[str, ...] = (
    "scope", "subject_id", "polarity", "proposal_class", "basis_key",
)


def capture_learning_records(conn: sqlite3.Connection, bundle_id: str, *,
                             scope: str, subject_id: str) -> int:
    """Snapshot P1's §8.7 records at one scope and subject into the bundle.

    Required by 10-i4-learning-ops.md: a bundle exercising SR6 or
    USER_REJECTED_EQUIVALENT must carry these, or a store-populated run and a
    store-empty run compare as a grouping regression when the cause is a missing
    negative example.

    P2 copies `polarity`, `proposal_class` and `basis_key` and interprets none of
    them. Suppression is the acting part's rule, applied in that part.
    """
    from database_agent.learning import SCOPES, learning_records

    _require_open(conn, bundle_id)
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope!r}; §8.7 defines exactly {SCOPES}")
    captured = 0
    for row in learning_records(conn, scope, subject_id):
        record = {k: row[k] for k in row.keys()}
        conn.execute(
            "INSERT INTO bundle_learning_record (bundle_id, event_id, scope, "
            "subject_id, polarity, proposal_class, basis_key, row) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(bundle_id, event_id) DO NOTHING",
            (bundle_id, row["event_id"], scope, subject_id, row["polarity"],
             row["proposal_class"], row["basis_key"], canonical_json(record)),
        )
        captured += 1
    return captured


def bundle_learning_records(conn: sqlite3.Connection, bundle_id: str, *,
                            scope: str | None = None,
                            subject_id: str | None = None) -> list[dict]:
    import json
    sql = "SELECT * FROM bundle_learning_record WHERE bundle_id = ?"
    args: list = [bundle_id]
    if scope is not None:
        sql += " AND scope = ?"
        args.append(scope)
    if subject_id is not None:
        sql += " AND subject_id = ?"
        args.append(subject_id)
    out = []
    for r in conn.execute(sql + " ORDER BY event_id", args):
        record = {k: r[k] for k in r.keys()}
        record["row"] = json.loads(r["row"])
        out.append(record)
    return out


def add_accepted_group(conn: sqlite3.Connection, bundle_id: str, *, group_id: str,
                       acceptance_row: dict) -> None:
    """One accepted group, AS OF the bundle's pinned plan version.

    The per-version resolution is P9's `group_acceptance` (§8.8) and the caller
    hands over the already-resolved row. P2 does not re-derive acceptance from
    membership records: that projection is P9's published surface.
    """
    _require_open(conn, bundle_id)
    conn.execute(
        "INSERT INTO bundle_accepted_group (bundle_id, group_id, row) VALUES (?, ?, ?)",
        (bundle_id, group_id, canonical_json(acceptance_row)),
    )


def accepted_groups(conn: sqlite3.Connection, bundle_id: str) -> list[dict]:
    import json
    return [json.loads(r["row"]) for r in conn.execute(
        "SELECT row FROM bundle_accepted_group WHERE bundle_id = ? ORDER BY group_id",
        (bundle_id,))]


def add_expectation(conn: sqlite3.Connection, bundle_id: str, *, dimension: str,
                    subject_ref: str, expected_value, expected_outcome_kind: str,
                    source: str) -> None:
    """The expected side of one assertion, for one subject.

    `expected_value` is opaque: for `fact` it is P6's field/value/reliability
    state, for `placement` and `residual` it is P11's published vocabulary. P2
    validates no member of it — see the module docstring.

    One subject per call, with no bulk path: §8.7's scope discipline means a
    file-scoped correction is an expectation for that file and no other.
    """
    from eval_harness.vocabulary import (
        EXPECTATION_SOURCES, EXPECTED_OUTCOME_KINDS, check_dimension,
    )
    _require_open(conn, bundle_id)
    check_dimension(dimension)
    if expected_outcome_kind not in EXPECTED_OUTCOME_KINDS:
        raise ValueError(f"expected_outcome_kind {expected_outcome_kind!r} is not "
                         f"one of {EXPECTED_OUTCOME_KINDS}")
    if source not in EXPECTATION_SOURCES:
        raise ValueError(f"source {source!r} is not one of {EXPECTATION_SOURCES}")
    conn.execute(
        "INSERT INTO bundle_expectation (bundle_id, dimension, subject_ref, "
        "expected_value, expected_outcome_kind, source) VALUES (?, ?, ?, ?, ?, ?)",
        (bundle_id, dimension, subject_ref,
         None if expected_value is None else canonical_json(expected_value),
         expected_outcome_kind, source),
    )


def _expectation_row(row: sqlite3.Row) -> dict:
    import json
    record = {k: row[k] for k in row.keys()}
    record["expected_value"] = (None if row["expected_value"] is None
                                else json.loads(row["expected_value"]))
    return record


def expectations(conn: sqlite3.Connection, bundle_id: str, *,
                 dimension: str | None = None) -> list[dict]:
    if dimension is None:
        rows = conn.execute(
            "SELECT * FROM bundle_expectation WHERE bundle_id = ? "
            "ORDER BY dimension, subject_ref", (bundle_id,))
    else:
        rows = conn.execute(
            "SELECT * FROM bundle_expectation WHERE bundle_id = ? AND dimension = ? "
            "ORDER BY subject_ref", (bundle_id, dimension))
    return [_expectation_row(r) for r in rows]


def expectation_for(conn: sqlite3.Connection, bundle_id: str, dimension: str,
                    subject_ref: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM bundle_expectation WHERE bundle_id = ? AND dimension = ? "
        "AND subject_ref = ?", (bundle_id, dimension, subject_ref)).fetchone()
    return None if row is None else _expectation_row(row)
