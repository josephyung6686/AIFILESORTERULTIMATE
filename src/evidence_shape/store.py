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

`RunWriter` is that order, made atomic and made callable once. The four writers below
stay published -- P4's own tests drive them individually -- but a caller that runs
them by hand can crash between two of them and leave a run with zero observations,
which conformance rule 9 makes a MEANINGFUL state rather than an obvious defect: an
`unsupported`, `deferred` or `failed` run legitimately carries none. One transaction
is what makes a half-written batch impossible to mistake for a run that read nothing.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Mapping
from dataclasses import dataclass

from database_agent.db import transaction
from database_agent.events import append_event

from evidence_shape.authorship import check_author, event_defaults, run_event_type
from evidence_shape.canonical import canonical_json
from evidence_shape.conformance import validate_run
from evidence_shape.runs import (
    RUN_FIELDS, ExtractionRun, MalformedRun, run_from_mapping,
)
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

    The keys are read in `rowid` order, which is the batch's own order, so two
    identical batches produce one explanation rather than two shufflings of it.
    `observation_id` is a uuid4 and ordering by it was ordering by nothing.
    """
    run = get_run(conn, run_id)
    keys = [row["observation_key"] for row in conn.execute(
        "SELECT observation_key FROM evidence WHERE run_id = ? ORDER BY rowid",
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
        "SELECT * FROM evidence WHERE run_id = ? ORDER BY rowid", (run_id,))]


def observation_keys_for_run(conn: sqlite3.Connection, run_id: str) -> list[str]:
    """The keys P4 assigned to one batch, in the order the batch was written.

    Published because a caller that emits a per-located-value record alongside a batch
    has no handle otherwise: `record_observation` returns an `observation_id`, and a
    caller that derived its own key would need a second locator implementation --
    the drift §2.8 exists to prevent. P5's §2.9 sensitivity signal is the first such
    caller, and keyed on batch position until this existed.

    Ordered by `rowid`, which IS insertion order. It was ordered by `observation_id`,
    which is not: `record_observation` mints `uuid.uuid4()`, so that was lexicographic
    order over random ids. Executed 2026-08-21, a batch emitted 00,01,02,…,11 came back
    07,10,02,04,09,05,06,01,03,08,11,00 -- and `long_tail.record_sensitivity_signals`
    indexes into this list by the observation's position in its batch, so §2.9's
    "treating addresses and message content as potentially sensitive" attached the
    signal to the WRONG value. The row it writes is keyed on `observation_key`, which
    is what P7 later redacts against.

    A published order has to be a real one. Conformance rule 8 is unaffected and
    deliberately so -- `determinism._lines` sorts, because a set has no order -- but
    this is the ordered handle, not the set.
    """
    return [row["observation_key"] for row in conn.execute(
        "SELECT observation_key FROM evidence WHERE run_id = ? ORDER BY rowid",
        (run_id,))]


def observations_for_file(conn: sqlite3.Connection, file_id: str) -> list[Observation]:
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE file_id = ? ORDER BY rowid", (file_id,))]


def observations_by_key(conn: sqlite3.Connection,
                        observation_key: str) -> list[Observation]:
    """M14's citation resolver. A LIST: two extractor versions carry one key, which
    is what MINOR 8 arranged and what §8.5's cross-version diff reads."""
    return [_observation_from_row(row) for row in conn.execute(
        "SELECT * FROM evidence WHERE observation_key = ? ORDER BY rowid",
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


@dataclass(frozen=True)
class PersistedExtractionResult:
    """The exact three public P4 records belonging to one persisted run.

    This deliberately matches P5's ``ExtractionResult`` structurally without making
    P4 depend on P5.  Unlike a batch presented to :class:`RunWriter`, its mappings
    retain the P4-assigned ``run_id`` because this is a read model, not a new write.
    """

    run: Mapping[str, object]
    observations: tuple[Mapping[str, object], ...]
    text_units: tuple[Mapping[str, object], ...]


class AmbiguousAuthoritativeRun(Exception):
    """More than one persisted run satisfies the caller's exact authority key."""


def result_for_run(conn: sqlite3.Connection, run_id: str) -> PersistedExtractionResult:
    """Losslessly reconstruct one persisted extraction batch by its P4 run id."""
    return PersistedExtractionResult(
        run=get_run(conn, run_id).to_mapping(),
        observations=tuple(
            observation.to_mapping()
            for observation in observations_for_run(conn, run_id)),
        text_units=tuple(
            unit.to_mapping() for unit in text_units_for_run(conn, run_id)),
    )


def authoritative_result(
        conn: sqlite3.Connection, *, file_id: str, content_hash: str,
        extractor_name: str, extractor_version: str,
        analysis_tier: str) -> PersistedExtractionResult | None:
    """Return the sole current, successful, evidence/text-bearing exact run.

    P4 has no chronology-based authority rule for runs, so this never chooses the
    newest row.  A candidate must match the complete caller-supplied identity, have
    finished without failure and carry non-blank stored text. Observations do not
    participate: a native PDF can preserve page text while finding zero structured
    values, and observation supersession publishes no run-level authority rule.
    Zero candidates is absence; multiple candidates is an explicit ambiguity.
    """
    candidates: list[str] = []
    for run in runs_for_file(conn, file_id):
        if (run.content_hash != content_hash
                or run.extractor_name != extractor_name
                or run.extractor_version != extractor_version
                or run.analysis_tier != analysis_tier
                or run.finished_at is None
                or run.failure_reason is not None):
            continue
        if not any(unit.text.strip() for unit in text_units_for_run(conn, run.run_id)):
            continue
        candidates.append(run.run_id)
    if len(candidates) > 1:
        raise AmbiguousAuthoritativeRun(
            f"{len(candidates)} persisted runs satisfy the exact authority key for "
            f"{(file_id, content_hash, extractor_name, extractor_version, analysis_tier)!r}; "
            "P4 publishes no rule for choosing one")
    return None if not candidates else result_for_run(conn, candidates[0])


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


class AmbiguousSupersession(Exception):
    """A superseding batch matches more than one unsuperseded prior observation."""


def _container_path(container_path) -> tuple[Segment, ...]:
    """An emitted container path as P4's records hold it.

    P5's `extractors.shape.text_unit` freezes its path into a TUPLE of mappings, and
    `text_unit_from_mapping` reads a tuple as already being `Segment`s -- so the
    emitted unit raises `MalformedTextUnit` on its own contents. This is the one
    adaptation the batch writer performs, and it converts rather than re-deciding
    anything: `kind`, `index` and `label` are copied across and D3's 1-based index
    rule is still `Segment`'s to enforce.
    """
    return tuple(part if isinstance(part, Segment)
                 else Segment(part["kind"], part.get("index"), part.get("label"))
                 for part in container_path)


class RunWriter:
    """One extraction batch, written in one transaction. P5's `EvidenceSink`.

    An extractor returns ONE result -- the run, its observations and its text units,
    none of them carrying a `run_id` -- and this writes all of it or none of it. The
    batch is validated through the twelve conformance rules FIRST, so a non-conforming
    run is refused before the run row exists rather than discovered halfway through;
    rules 5, 9 and 10 need the whole set at once, which is precisely what a batch has
    and what three separate inserts did not.

    `author` is fixed at construction because it is a property of the part doing the
    extracting, not of one run: M8 -- "the acting part authors; P1 writes". P5
    constructs this with `author="P5"`, P8 with `author="P8"` for an `llm`-tier run,
    and `P1` is refused here rather than at the first write.

    This takes P5's `ExtractionResult` structurally -- `.run`, `.observations`,
    `.text_units` -- and imports nothing from `extractors`. P5 depends on P4; the
    reverse would make the evidence layer unbuildable without a sorter, which is the
    independence P4's Done-means 9 is about.
    """

    def __init__(self, conn: sqlite3.Connection, *, author: str) -> None:
        self.conn = conn
        self.author = check_author(author)

    def write(self, result, *, supersede_reason: str | None = None) -> str:
        """Write the batch and return the `run_id` P4 minted for it."""
        if "run_id" in result.run:
            # P5's own header: "Not computed here, because they are P4-assigned:
            # `observation_id`, `observation_key`, `run_id` ...". Merging a caller's
            # id over the minted one lets a batch name a row it does not own -- and
            # the run then lands under that id while the event, the observations and
            # the returned handle all use the minted one.
            raise MalformedRun(
                f"the batch carries run_id {result.run['run_id']!r}; the run_id is "
                "P4's to assign (D5) and this writer mints it")
        run_id = new_id()
        run = run_from_mapping({"run_id": run_id, **result.run})
        text_units = tuple(
            text_unit_from_mapping({
                **unit, "run_id": run_id,
                "container_path": _container_path(unit["container_path"])})
            for unit in result.text_units)
        observations = tuple(
            observation_from_mapping({**observation, "run_id": run_id})
            for observation in result.observations)
        validate_run(run, observations, text_units)

        with transaction(self.conn) as conn:
            record_run(conn, run)
            for unit in text_units:
                record_text_unit(conn, unit)
            written = [record_observation(conn, observation)
                       for observation in observations]
            if supersede_reason is not None:
                self._supersede(conn, run_id, observations, written,
                                supersede_reason)
            # Last, because its evidence reference is the keys of the rows above.
            record_run_event(conn, run_id, author=self.author)
        return run_id

    def _supersede(self, conn: sqlite3.Connection, run_id: str, observations,
                   written: list[str], reason: str) -> None:
        """§8.2's link, over the only pairing the design publishes.

        Which earlier row a new one supersedes is not settled anywhere: §8.2 gives an
        example (a garbled OCR pass, then a recovered name) and states only that both
        must remain available, and `extraction_runs` carries no supersede columns at
        all, so there is no run-level link to fall back on. The narrowest defensible
        rule is therefore identity: a new observation supersedes the prior one that
        carries the SAME `observation_key`. That handle is `content_hash`,
        `extractor_name`, `locator` and `raw_value` -- and MINOR 8 leaves
        `extractor_version` out of it exactly so a re-extraction's row and the row it
        improves on share one key.

        Two consequences, both deliberate and neither invented here. A pass that reads
        a DIFFERENT value -- §8.2's own example -- pairs nothing, because two readings
        are two handles and P4 publishes no rule for pairing them; P6's `file_facts`
        decides which wins. And more than one unsuperseded prior row under one handle
        means "the prior row" names two: `mark_superseded` would let the second link
        silently overwrite the first's `supersedes` pointer, so this refuses rather
        than picking a winner and losing a link.
        """
        for observation, new_observation_id in zip(observations, written):
            candidates = [row["observation_id"] for row in conn.execute(
                "SELECT observation_id FROM evidence WHERE observation_key = ? "
                # `rowid`, chronological. Nothing here depends on it -- more than
                # one candidate raises rather than picking -- but ordering by a uuid4
                # is ordering by nothing, and the next reader should not have to work
                # that out.
                "AND run_id != ? AND superseded_by IS NULL ORDER BY rowid",
                (observation.observation_key, run_id))]
            if not candidates:
                continue
            if len(candidates) > 1:
                raise AmbiguousSupersession(
                    f"{len(candidates)} unsuperseded observations carry "
                    f"{observation.observation_key}; §8.2 links one earlier record to "
                    "one later one and the design does not say which of these is the "
                    "one this batch supersedes"
                )
            supersede_observation(conn, old_observation_id=candidates[0],
                                  new_observation_id=new_observation_id,
                                  reason=reason)
