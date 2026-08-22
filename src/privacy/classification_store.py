# src/privacy/classification_store.py
"""P7's own classification store (D2, ratified 2026-08-21).

This module used to be `facts_seam.py`: an injected `SensitivityFacts` protocol over
a `sensitivity` fact P6 owned. D2 removed the seam. P7's `ClassificationRecord`,
keyed `(file_id, content_hash)`, is AUTHORITATIVE, so there is no P6 record to read
and nothing to inject. The four methods keep their shape -- `current`, `write`,
`supersede`, `history` -- over a table P7 creates and owns.

Three rules, each a quotation rather than a choice.

**The key is the bytes.** A classification is bound to a file VERSION (§8.2). New
bytes at a path are a new version and inherit nothing, so `current` is keyed on the
pair and returns `None` for a hash nothing has classified.

**Supersede, never overwrite (§8.2).** A revision is a new record linked through P1's
three published columns; both remain inspectable. P7 does not implement supersession,
it calls `mark_superseded` and `chain`. §3.13's ordering is the design's own listed
order, `user confirmed`, `direct`, `validated`, `LLM-supported`, `possible`, with
`rejected` outside it -- taken from P4's published tuple and never re-derived from a
score.

**`Unreadable or unclassified` is a gate OUTCOME, not a file fact (D2).** It lives on
the release decision. It is refused here on both sides of the projection, because a
stored row saying it would claim, as a fact, exactly what the absence of a row
already says -- and the two would then be able to disagree.

This module authors nothing. C4: "a gate that also wrote would be doing two jobs."
`classification_assigned` and `classification_superseded` are appended once, by
Task 16's `assign` and `reclassify`, which are the entry points a detector or a user
correction calls.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Sequence

from database_agent.files_table import set_sensitivity_state
from database_agent.supersede import chain, mark_superseded

from evidence_shape.canonical import canonical_json

from privacy.authorship import SUBSYSTEM
from privacy.classification import UNREADABLE_UNCLASSIFIED, ClassificationRecord
from privacy.schema import CLASSIFICATIONS_TABLE
from privacy.vocabulary import RELIABILITY_STATES

#: The sixth state, and the one outside the ranking. "A rejected fact is a proposal
#: that the user or validator marked as incorrect" -- stored, kept for §8.7's
#: negative examples, never current. This is the one state name spelled in this
#: module, and it is checked against Task 2's published tuple at import so it cannot
#: drift.
REJECTED = "rejected"
if REJECTED not in RELIABILITY_STATES:
    raise ImportError(
        f"{REJECTED!r} is not one of §3.13's six reliability states "
        f"{RELIABILITY_STATES}; the states are P4's and Task 2 re-exports them"
    )

#: §3.13, in the design's own listed order, strongest first: Task 2's re-exported
#: tuple with the unranked state removed, IN PLACE. Derived rather than retyped --
#: five literals here would be a second home for a vocabulary P4 publishes and Task 2
#: re-exports, which is the defect brief §11 exists to prevent. Never sorted, never
#: scored: the order is the design's own line 50 read in sequence and nothing
#: computes it.
RELIABILITY_ORDER: tuple[str, ...] = tuple(
    state for state in RELIABILITY_STATES if state != REJECTED
)

_COLUMNS = (
    "fact_id", "file_id", "content_hash", "handling_class", "protected", "basis",
    "evidence_refs", "reliability_state", "observed_at",
)


class AmbiguousCurrentClassification(Exception):
    """Two live records at one key and one rank. Raised, never resolved by picking."""


class UnrankedReliability(Exception):
    """A reliability state outside §3.13's six. A load error, not a fallback."""


class GateOutcomeNotAFileFact(Exception):
    """`unreadable_unclassified` was offered as a stored fact or as a projection."""


def _rank(record: ClassificationRecord) -> int:
    try:
        return RELIABILITY_ORDER.index(record.reliability_state)
    except ValueError:
        raise UnrankedReliability(
            f"{record.reliability_state!r} is not one of §3.13's ranked states "
            f"{RELIABILITY_ORDER!r}; {REJECTED!r} is stored but never current"
        ) from None


def strongest(records: Sequence[ClassificationRecord]) -> ClassificationRecord:
    """The record §3.13's listed order ranks highest. Ties raise."""
    if not records:
        raise ValueError("strongest() of no records")
    ranked = sorted(records, key=_rank)
    best = _rank(ranked[0])
    tied = [r for r in ranked if _rank(r) == best]
    if len(tied) > 1:
        raise AmbiguousCurrentClassification(
            f"{len(tied)} live classifications at reliability "
            f"{tied[0].reliability_state!r} for {tied[0].file_id!r} at "
            f"{tied[0].content_hash!r}; one must supersede the other (§8.2)"
        )
    return ranked[0]


def _row_to_record(row: sqlite3.Row) -> ClassificationRecord:
    return ClassificationRecord(
        file_id=row["file_id"],
        content_hash=row["content_hash"],
        handling_class=row["handling_class"],
        protected=bool(row["protected"]),
        basis=row["basis"],
        evidence_refs=tuple(json.loads(row["evidence_refs"])),
        reliability_state=row["reliability_state"],
        observed_at=row["observed_at"],
    )


class ClassificationStore:
    """P7's authoritative classification record (D2). Concrete; no injection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def write(self, record: ClassificationRecord) -> str:
        """Insert one record and return its `fact_id`. Appends no event (C4)."""
        if record.handling_class == UNREADABLE_UNCLASSIFIED:
            raise GateOutcomeNotAFileFact(
                f"{UNREADABLE_UNCLASSIFIED!r} is a gate outcome, not a file fact "
                "(D2): the absence of a record already says nothing has looked"
            )
        fact_id = str(uuid.uuid4())
        self._conn.execute(
            f"INSERT INTO {CLASSIFICATIONS_TABLE} ({','.join(_COLUMNS)}) "
            f"VALUES ({','.join('?' * len(_COLUMNS))})",
            (fact_id, record.file_id, record.content_hash, record.handling_class,
             int(record.protected), record.basis,
             canonical_json(list(record.evidence_refs)), record.reliability_state,
             record.observed_at),
        )
        return fact_id

    def _live_rows(self, file_id: str, content_hash: str) -> list[sqlite3.Row]:
        return list(self._conn.execute(
            f"SELECT * FROM {CLASSIFICATIONS_TABLE} "
            "WHERE file_id = ? AND content_hash = ? AND superseded_by IS NULL "
            "  AND reliability_state <> ? "
            "ORDER BY observed_at, rowid",
            (file_id, content_hash, REJECTED),
        ))

    def current(self, file_id: str, content_hash: str) -> ClassificationRecord | None:
        """The one current classification for this file VERSION, or None."""
        rows = self._live_rows(file_id, content_hash)
        if not rows:
            return None
        return strongest([_row_to_record(row) for row in rows])

    def current_fact_id(self, file_id: str, content_hash: str) -> str | None:
        """The row id `mark_superseded` needs. `ClassificationRecord` carries none."""
        rows = self._live_rows(file_id, content_hash)
        if not rows:
            return None
        pairs = [(row["fact_id"], _row_to_record(row)) for row in rows]
        best = strongest([record for _, record in pairs])
        # `strongest` returns one of the objects it was given, so identity is the
        # match. Equality would collapse two byte-identical live rows into one and
        # hide the ambiguity `current` raises on.
        return next(fact_id for fact_id, record in pairs if record is best)

    def supersede(self, old_fact_id: str, new_fact_id: str, reason: str) -> None:
        """P1's three columns. P7 does not copy P1's supersede implementation."""
        mark_superseded(self._conn, CLASSIFICATIONS_TABLE,
                        old_id=old_fact_id, new_id=new_fact_id, reason=reason)

    def history(self, file_id: str) -> list[ClassificationRecord]:
        """Every classification ever written for this file, oldest first."""
        return [_row_to_record(row) for row in self._conn.execute(
            f"SELECT * FROM {CLASSIFICATIONS_TABLE} WHERE file_id = ? "
            "ORDER BY observed_at, rowid", (file_id,))]

    def chain_for(self, fact_id: str) -> list[sqlite3.Row]:
        """P1's `chain`, exposed so a caller does not name P7's table itself."""
        return chain(self._conn, CLASSIFICATIONS_TABLE, fact_id)


def mirror_state(record: ClassificationRecord) -> dict:
    """The opaque dict P1 stores in `files.sensitivity_state` (D2's projection).

    P1 holds no handling-class vocabulary and validates nothing here; §8.4's classes
    are P7's. `file_id` is absent because it is the row's key, and `fact_id` is
    absent because it is not one of SPEC §2's eight fields -- a reader needing the
    classification's provenance reads the record, not the column.
    """
    if record.handling_class == UNREADABLE_UNCLASSIFIED:
        raise GateOutcomeNotAFileFact(
            f"{UNREADABLE_UNCLASSIFIED!r} never reaches files.sensitivity_state "
            "(D2): 'nothing has looked' must not be readable as 'this file carries "
            "nothing'"
        )
    return {
        "handling_class": record.handling_class,
        "protected": record.protected,
        "basis": record.basis,
        "reliability_state": record.reliability_state,
        "content_hash": record.content_hash,
        "evidence_refs": list(record.evidence_refs),
        "observed_at": record.observed_at,
    }


def mirror(conn: sqlite3.Connection, record: ClassificationRecord, *,
           component_version: str) -> None:
    """Project the authoritative record onto P1's column, through P1's setter.

    The single `UPDATE files` in the product's privacy path is P1's, inside
    `set_sensitivity_state`. `author` is not a parameter: M8 makes the acting part
    the author, and a log where the author is a caller-supplied value cannot answer
    §8.2's reconstruction question.
    """
    set_sensitivity_state(conn, record.file_id, state=mirror_state(record),
                          author=SUBSYSTEM, component_version=component_version)
