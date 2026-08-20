# src/evidence_shape/store.py
"""The writers and readers over P4's three tables.

P4 AUTHORS NO EVENT. `record_run_event` takes a required `author`, passes it into
`events.subsystem`, and refuses `P1` -- M8: "The acting part authors; P1 writes. P1
appends no event on its own initiative." P5 is the acting part for filesystem, native
and OCR runs; P8 for an `analysis_tier = llm` run.

The write order is: run row, then text units and observations, then the one §8.2
event. The event's evidence reference is "`run_id` plus the `observation_key`s", and
those keys do not exist until the observations are written -- so `record_run_event`
reads them from the rows rather than being handed them, and the event and the
database cannot disagree.
"""
from __future__ import annotations

import json
import sqlite3
import uuid

from database_agent.events import append_event

from evidence_shape.authorship import event_defaults, run_event_type
from evidence_shape.canonical import canonical_json
from evidence_shape.runs import RUN_FIELDS, ExtractionRun, run_from_mapping
from evidence_shape.location import Segment
from evidence_shape.locator import serialize_container_path
from evidence_shape.observation import OBSERVATION_FIELDS, OBSERVATION_ROW_FIELDS, Observation, observation_from_mapping
from evidence_shape.text_units import TEXT_UNIT_FIELDS, TextUnit, text_unit_from_mapping
from database_agent.supersede import chain, mark_superseded


def new_id() -> str:
    """A row identifier. Not the citation handle -- that is `observation_key` (M14)."""
    return str(uuid.uuid4())


def record_run(conn: sqlite3.Connection, run: ExtractionRun) -> str:
    """Insert one `extraction_runs` row. Appends no event; see `record_run_event`."""
    mapping = run.to_mapping()
    mapping["config"] = canonical_json(mapping["config"])
    mapping["coverage"] = (None if mapping["coverage"] is None
                           else canonical_json(mapping["coverage"]))
    conn.execute(
        f"INSERT INTO extraction_runs ({','.join(RUN_FIELDS)}) "
        f"VALUES ({','.join('?' * len(RUN_FIELDS))})",
        [mapping[name] for name in RUN_FIELDS],
    )
    return run.run_id


def _run_from_row(row: sqlite3.Row) -> ExtractionRun:
    mapping = {name: row[name] for name in RUN_FIELDS}
    mapping["config"] = json.loads(mapping["config"])
    mapping["coverage"] = (None if mapping["coverage"] is None
                           else json.loads(mapping["coverage"]))
    return run_from_mapping(mapping)


def get_run(conn: sqlite3.Connection, run_id: str) -> ExtractionRun:
    row = conn.execute("SELECT * FROM extraction_runs WHERE run_id = ?",
                       (run_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown run {run_id!r}")
    return _run_from_row(row)


def runs_for_file(conn: sqlite3.Connection, file_id: str) -> list[ExtractionRun]:
    return [_run_from_row(row) for row in conn.execute(
        "SELECT * FROM extraction_runs WHERE file_id = ? ORDER BY started_at, run_id",
        (file_id,))]


def runs_for_content(conn: sqlite3.Connection,
                     content_hash: str) -> list[ExtractionRun]:
    """§2.1: the engine reads each file once per content version; §3.4 keys on it."""
    return [_run_from_row(row) for row in conn.execute(
        "SELECT * FROM extraction_runs WHERE content_hash = ? "
        "ORDER BY started_at, run_id", (content_hash,))]


def record_run_event(conn: sqlite3.Connection, run_id: str, *, author: str) -> int:
    """The one §8.2 event a run appends: `extraction`, or `OCR` for an OCR run.

    `author` is the acting part and P4 supplies no default (M8). `component_version`
    is the run's own extractor version -- §8.2's "extractor or model version".
    """
    run = get_run(conn, run_id)
    keys = [row["observation_key"] for row in conn.execute(
        "SELECT observation_key FROM evidence WHERE run_id = ? ORDER BY observation_id",
        (run_id,))]
    return append_event(conn, **event_defaults(
        author=author,
        component_version=run.extractor_version,
        event_type=run_event_type(run.analysis_tier),
        file_id=run.file_id,
        content_hash=run.content_hash,
        observed_at=run.finished_at or run.started_at,
        explanation=canonical_json({"run_id": run_id, "observation_keys": keys}),
    ))


def record_observation(conn: sqlite3.Connection, observation: Observation) -> str:
    """Insert one `evidence` row and mint its `observation_id`.

    The run's `observation_count` becomes the count of rows on that run: it is a
    derived number, and a stored count that disagrees with the rows is a fact nobody
    downstream can use -- §8.6's progress line least of all.
    """
    mapping = observation.to_mapping()
    row = dict(mapping)
    row["observation_id"] = new_id()
    row["location"] = canonical_json(mapping["location"])
    row["context_truncated"] = int(observation.context_truncated)
    row["supersedes"] = None
    row["superseded_by"] = None
    row["supersede_reason"] = None
    conn.execute(
        f"INSERT INTO evidence ({','.join(OBSERVATION_ROW_FIELDS)}) "
        f"VALUES ({','.join('?' * len(OBSERVATION_ROW_FIELDS))})",
        [row[name] for name in OBSERVATION_ROW_FIELDS],
    )
    conn.execute(
        "UPDATE extraction_runs SET observation_count = "
        "(SELECT count(*) FROM evidence WHERE run_id = ?) WHERE run_id = ?",
        (observation.run_id, observation.run_id),
    )
    return row["observation_id"]


def _observation_from_row(row: sqlite3.Row) -> Observation:
    mapping = {name: row[name] for name in OBSERVATION_FIELDS}
    mapping["location"] = json.loads(mapping["location"])
    mapping["context_truncated"] = bool(mapping["context_truncated"])
    return observation_from_mapping(mapping)


def observation_row(conn: sqlite3.Connection, observation_id: str) -> sqlite3.Row:
    """The stored row, including the supersede state the emitted record has no
    field for."""
    row = conn.execute("SELECT * FROM evidence WHERE observation_id = ?",
                       (observation_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown observation {observation_id!r}")
    return row


def get_observation(conn: sqlite3.Connection, observation_id: str) -> Observation:
    return _observation_from_row(observation_row(conn, observation_id))


def observations_for_run(conn: sqlite3.Connection, run_id: str) -> list[Observation]:
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE run_id = ? ORDER BY observation_id", (run_id,))]


def observation_keys_for_run(conn: sqlite3.Connection, run_id: str) -> list[str]:
    """The keys P4 assigned to one batch, in the order the batch was written.

    Published because a caller that emits a per-located-value record alongside a batch
    has no handle otherwise: `record_observation` returns an `observation_id`, and a
    caller that derived its own key would need a second locator implementation --
    the drift §2.8 exists to prevent. P5's §2.9 sensitivity signal is the first such
    caller, and keyed on batch position until this existed.

    Ordered by `observation_id`, which is insertion order, so position N in the emitted
    batch is position N here.
    """
    return [row["observation_key"] for row in conn.execute(
        "SELECT observation_key FROM evidence WHERE run_id = ? ORDER BY observation_id",
        (run_id,))]


def observations_for_file(conn: sqlite3.Connection, file_id: str) -> list[Observation]:
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE file_id = ? ORDER BY observation_id", (file_id,))]


def observations_by_key(conn: sqlite3.Connection,
                        observation_key: str) -> list[Observation]:
    """M14's citation resolver. A LIST: two extractor versions carry one key, which
    is what MINOR 8 arranged and what §8.5's cross-version diff reads."""
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE observation_key = ? ORDER BY observation_id",
        (observation_key,))]


def record_text_unit(conn: sqlite3.Connection, unit: TextUnit) -> None:
    mapping = unit.to_mapping()
    conn.execute(
        f"INSERT INTO text_units ({','.join(TEXT_UNIT_FIELDS)}) "
        f"VALUES ({','.join('?' * len(TEXT_UNIT_FIELDS))})",
        [mapping["run_id"], canonical_json(mapping["container_path"]),
         mapping["unit_locator"], mapping["text"], mapping["length"],
         int(mapping["truncated"])],
    )


def _text_unit_from_row(row: sqlite3.Row) -> TextUnit:
    return text_unit_from_mapping({
        "run_id": row["run_id"],
        "container_path": json.loads(row["container_path"]),
        "unit_locator": row["unit_locator"],
        "text": row["text"],
        "length": row["length"],
        "truncated": bool(row["truncated"]),
    })


def text_units_for_run(conn: sqlite3.Connection, run_id: str) -> list[TextUnit]:
    return [_text_unit_from_row(row) for row in conn.execute(
        "SELECT * FROM text_units WHERE run_id = ? ORDER BY unit_locator", (run_id,))]


def text_unit_at(conn: sqlite3.Connection, run_id: str,
                 container_path: tuple[Segment, ...]) -> TextUnit | None:
    """D12's key, `(run_id, container_path)`, through that path's canonical form."""
    row = conn.execute(
        "SELECT * FROM text_units WHERE run_id = ? AND unit_locator = ?",
        (run_id, serialize_container_path(container_path)),
    ).fetchone()
    return None if row is None else _text_unit_from_row(row)


def unit_for_observation(conn: sqlite3.Connection,
                         observation: Observation) -> TextUnit | None:
    """Conformance rule 10's lookup: the unit an observation's span points into."""
    return text_unit_at(conn, observation.run_id,
                        observation.location.container_path)


def supersede_observation(conn: sqlite3.Connection, *, old_observation_id: str,
                          new_observation_id: str, reason: str) -> None:
    """§8.2: a newer result supersedes an earlier one, retaining the old observation
    and the reason it was superseded.

    P1 owns the mechanism -- the cycle check, the first-reason-sticks rule and the
    chain walk are all tested there. P4 supplies the table name and nothing else; a
    second implementation would put one concept under two names.
    """
    mark_superseded(conn, "evidence", old_id=old_observation_id,
                    new_id=new_observation_id, reason=reason)


def supersede_chain(conn: sqlite3.Connection,
                    observation_id: str) -> list[sqlite3.Row]:
    """Every link, oldest first. §8.2: both extraction records remain available."""
    return chain(conn, "evidence", observation_id)
