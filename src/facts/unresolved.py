# src/facts/unresolved.py
"""§3.6's abstention, as a ROW -- B7, Done-means 18 and 19.

§3.6 stops at "no fact": "A model that cannot cite sufficient evidence must return
unknown." §8.5 then asks, under Fact quality, "Did it abstain when evidence was
absent?" -- and an absent row cannot answer a question about absence. P2 cannot tell a
considered refusal from a crash, a skip, or a file that was never reached. So every
refusal P6 makes is recorded here, naming the field it attempted, the reason, the §3.5
routes it tried, and the observation keys it looked at.

Four properties make the row trustworthy, and each is a test rather than a comment:

  1. It is NOT a fact. No `value_id`, no reliability state -- absent from the schema,
     not merely null -- and absent from every fact read including the proposal-eligible
     one. A reader that treats it as a weaker `possible` has broken it.
  2. It obeys `file_facts`' negative contract: no path, destination, folder or group
     column (§3.14, §4.3). The forbidden-substring list is imported from `file_facts`
     rather than copied, so the two tables cannot drift.
  3. A later fact SUPERSEDES it and never deletes it (§8.2, §8.7). This module builds
     the affordance -- P1's three supersede columns and the `record_id` projection --
     and `facts/supersede.py` owns the operation.
  4. `budget_deferred` and `privacy_withheld` are NOT abstentions (§8.6). They are
     rows; they are not answers. `NOT_ABSTENTIONS` is published so a caller can make
     the distinction without a second copy of the rule.

The vocabularies are defined in `facts.vocabulary` -- one home for every closed set P6
owns -- and re-exported here because `facts.unresolved` is the address the rest of the
part imports them from.
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Iterable, Sequence

from evidence_shape.canonical import canonical_json
from evidence_shape.vocabulary import check

from facts.fields import get_field
from facts.vocabulary import (
    ATTEMPTED_PRODUCERS, BELOW_MARGIN, BELOW_SCORE_THRESHOLD, BUDGET_DEFERRED,
    CITATION_ABSENT_FROM_EVIDENCE, CONTEXT_CHECK_FAILED, CONTEXT_TRUNCATED,
    CONTRADICTED_BY_STRONGER_FACT, DIRECT_ROUTE, DISCOUNTED_TOOL_METADATA,
    FIELD_NOT_IN_ACTIVE_SCHEMA, LLM_ROUTE, MODEL_RETURNED_UNKNOWN,
    NO_CANDIDATE_EVIDENCE, NORMALIZATION_FAILED, NOT_ABSTENTIONS, PRIVACY_WITHHELD,
    RULE_ROUTE, UNRESOLVED_REASONS,
)

#: The vocabularies are re-exported here, beside `write_unresolved`, because this is
#: the module preamble §3.4 publishes and a call site should import the reason it
#: passes from the same place as the writer it passes it to.
__all__ = [
    "ATTEMPTED_PRODUCERS",
    "BELOW_MARGIN",
    "BELOW_SCORE_THRESHOLD",
    "BUDGET_DEFERRED",
    "CITATION_ABSENT_FROM_EVIDENCE",
    "CONTEXT_CHECK_FAILED",
    "CONTEXT_TRUNCATED",
    "CONTRADICTED_BY_STRONGER_FACT",
    "DIRECT_ROUTE",
    "DISCOUNTED_TOOL_METADATA",
    "FIELD_NOT_IN_ACTIVE_SCHEMA",
    "LLM_ROUTE",
    "MODEL_RETURNED_UNKNOWN",
    "NOT_ABSTENTIONS",
    "NO_CANDIDATE_EVIDENCE",
    "NORMALIZATION_FAILED",
    "PRIVACY_WITHHELD",
    "RULE_ROUTE",
    "UNRESOLVED_REASONS",
    "unresolved_for_file",
    "write_unresolved",
]

#: An observation key is `sha256:`-prefixed (P4's `sha256_of`); an `observation_id` and
#: a content hash are not. The prefix is the whole difference between citing M14's
#: version-independent key and citing a row id that an extractor upgrade invalidates.
_KEY_PREFIX = "sha256:"


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's identity, resolved through Task 2's published reader.

    Named `_checked_` rather than `_field_key` because after brief §17 it takes a key
    and returns the same key: its whole value is the refusal on the way through.

    `get_field` raises `FieldNotInCatalogue` for a key the catalogue does not carry,
    which is §3.12 -- "it should not invent new fields automatically" -- enforced at
    the abstention row exactly as hard as at the fact row. A refusal naming a field
    that does not exist is not a refusal, it is a typo.
    """
    return get_field(conn, field_key)["field_key"]


def _required(value: str, *, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} is required and must be a non-empty string")
    return value


def _evidence_refs(refs: Iterable[str]) -> list[str]:
    """The observation keys considered, "where any were" -- the SPEC allows none.

    An empty list is stored as `[]` in a NOT NULL column, so "looked at nothing" is
    distinguishable from "column never written". Membership in `evidence` is NOT
    checked here: `observations_by_key` returns `[]` rather than raising for an unknown
    key, so a resolution check would need a policy for the empty result and that policy
    is Task 7's.
    """
    out: list[str] = []
    for ref in refs:
        _required(ref, name="evidence_ref")
        if not ref.startswith(_KEY_PREFIX):
            raise ValueError(
                f"evidence_refs entry {ref!r} is not a P4 observation key: every "
                f"citation is an `observation_key` and starts {_KEY_PREFIX!r} (M14). "
                "An `observation_id` or a row id does not survive an extractor "
                "version bump and is not a citation (§8.7)."
            )
        out.append(ref)
    return out


def _attempted(producers: Iterable[str]) -> list[str]:
    """Which §3.5 routes were tried. May be empty.

    An §8.6 ceiling can be reached BEFORE any producer runs, so requiring at least one
    would make `budget_deferred` -- the reason that most needs recording -- unwritable.
    """
    return [check(one, ATTEMPTED_PRODUCERS, name="attempted_producer")
            for one in producers]


def write_unresolved(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                     field_key: str, reason: str,
                     attempted_producers: Sequence[str],
                     evidence_refs: Sequence[str], cache_key: str) -> str:
    """Record one refusal. Returns the `unresolved_id`.

    Always an INSERT, never an update and never de-duplicated: two refusals for the
    same `(file_id, content_hash, field_key)` under two different §3.4 cache keys are
    two different events, and §8.2 keeps both readable.
    """
    _required(file_id, name="file_id")
    _required(content_hash, name="content_hash")
    _required(cache_key, name="cache_key")
    field_key = _checked_field_key(conn, field_key)
    check(reason, UNRESOLVED_REASONS, name="reason")
    producers = _attempted(attempted_producers)
    refs = _evidence_refs(evidence_refs)

    unresolved_id = uuid.uuid4().hex
    conn.execute(
        """
        INSERT INTO unresolved (
            unresolved_id, file_id, content_hash, field_key, reason,
            attempted_producers, evidence_refs, cache_key, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (unresolved_id, file_id, content_hash, field_key, reason,
         canonical_json(producers), canonical_json(refs), cache_key,
         datetime.now(timezone.utc).isoformat()),
    )
    return unresolved_id


def unresolved_for_file(conn: sqlite3.Connection, file_id: str, content_hash: str, *,
                        field_key: str | None = None,
                        reason: str | None = None) -> list[sqlite3.Row]:
    """Every refusal recorded for one file VERSION, superseded rows included.

    Superseded rows are returned deliberately: SPEC rule 3 says a later fact "does not
    delete the row -- it supersedes it, and the row remains readable as the record of
    what was once refused". A reader that wants only live refusals filters on
    `superseded_by IS NULL` itself; hiding them here would delete the history at the
    read instead of at the write, which is the same loss by a quieter route.

    The order is `(created_at, unresolved_id)` -- P6's own total order, never SQLite's
    insertion order. P4's reads are `ORDER BY rowid`, which is stable within one
    database and is not a property of the corpus, so §8.5's replay would compare a run
    against itself and report a difference.
    """
    clauses = ["file_id = ?", "content_hash = ?"]
    params: list[str] = [file_id, content_hash]
    if field_key is not None:
        clauses.append("field_key = ?")
        params.append(_checked_field_key(conn, field_key))
    if reason is not None:
        clauses.append("reason = ?")
        params.append(check(reason, UNRESOLVED_REASONS, name="reason"))
    return list(conn.execute(
        "SELECT * FROM unresolved WHERE " + " AND ".join(clauses)
        + " ORDER BY created_at, unresolved_id",
        params,
    ))
