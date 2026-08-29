# src/facts/file_facts.py
"""§3.12's `file_facts` -- the table that "connects one file to one field and one value
while retaining the evidence and reliability state that justify the connection."

There is ONE fact table and one set of six reliability states. §3.5: "A file fact is
not inherently rule-based or LLM-based. It is the common format into which both systems
write their conclusions." So the producer is a COLUMN (`origin`), not a second schema:
there is no rules table and no model table, and this module is the only writer.

THE NEGATIVE CONTRACT, which is this module's reason to exist as a separate file:

    §3.14  "Facts remain separate from the future destination tree. A fact such as
            subject = BUSIB 4300 does not itself dictate one permanent folder path."
    §4.3   a fact records no group membership; §4.1, the graph "does not automatically
            copy those missing facts onto sparse files".

`file_facts` therefore has no path, destination, folder, node or group column, and
`write_fact` has no such keyword either -- a keyword argument is the other way a
destination gets in. `FILE_FACTS_COLUMNS` and `FORBIDDEN_COLUMN_SUBSTRINGS` are
published so a reviewer, `unresolved` (Task 5) and Tasks 16-19 all check the same
contract against the same list rather than three lists that drift.

A fact is never separable from its evidence (§3.1: "Every fact preserves where it came
from"). Every non-`user_confirmed` fact carries at least one `evidence_refs` entry and
every entry is a P4 observation KEY -- content-addressed, `sha256:`-prefixed, and
excluding `extractor_version` by construction, which is what makes a citation recorded
today still resolve after an extractor upgrade (M14, §8.7).

`fact_id` is content-addressed over the whole conclusion, so writing the same fact at
the same cache key twice is one row and one event. §8.2's supersession is unaffected: a
later pass cites `ocr`-tier observations, so §3.4's `analysis_tier` differs, so the
cache key differs, so the id differs and the new fact supersedes rather than collides.

This module does not set `preferred` (Task 18) and appends no event but `fact creation`.
"""
from __future__ import annotations

import sqlite3

from database_agent.db import transaction
from database_agent.events import append_event
from database_agent.supersede import SUPERSEDE_COLUMNS

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import check

from facts.authorship import AUTHORED_EVENT_TYPES, event_defaults
from facts.evidence import resolve_citation
from facts.fields import get_field
from facts.states import USER_CONFIRMED

# Bind authored meanings by name once, as `facts.learning` does. Call sites must not
# select an event by tuple position: a vocabulary reorder must not turn a creation
# into a rejection.
CREATION, _REJECTION = AUTHORED_EVENT_TYPES

# Reached through the module, never bound to a module-level name here. Preamble rule 2
# -- "P6 publishes no second copy and no alias table" -- is enforced by
# `test_no_module_in_facts_publishes_a_second_copy_of_the_six`, which flags any name in
# `facts.*` bound to a collection whose members are the six. `from facts.states import
# STATES` would be such a name even though it is the same object, because a consumer
# could then import the vocabulary from here. `states.py` is its one home.
from facts import states as _states

#: §3.1's five producers, one named constant each. This module owns the literal
#: spelling; every consumer imports the CONSTANT, never an index into the tuple
#: (preamble §3.1: an index couples the consumer to this tuple's order, so a reorder
#: relabels every fact with no test failing).
DETERMINISTIC_EXTRACTOR: str = "deterministic_extractor"
RULE: str = "rule"
LLM_INTERPRETATION: str = "llm_interpretation"
USER_CORRECTION: str = "user_correction"
USER_APPROVED_FOLDER: str = "user_approved_folder"

#: The five in the order the SPEC's `file_facts` shape publishes them:
#: "deterministic extractor | rule | LLM interpretation | user correction |
#: user-approved folder". For iteration and membership; to NAME one origin, import
#: the constant above.
FACT_ORIGINS: tuple[str, ...] = (
    DETERMINISTIC_EXTRACTOR, RULE, LLM_INTERPRETATION,
    USER_CORRECTION, USER_APPROVED_FOLDER,
)

#: What the table is, in declaration order, minus the VIRTUAL `record_id`, which
#: `PRAGMA table_info` does not report. The test asserts this EQUALS the live column
#: set, so this tuple cannot describe a table that does not exist.
FILE_FACTS_COLUMNS: tuple[str, ...] = (
    "fact_id", "file_id", "content_hash", "field_key", "value_id",
    "reliability_state", "origin", "evidence_refs", "cited_quote_refs",
    "cache_key", "model_identifier", "prompt_fingerprint", "internal_score",
    "active", *SUPERSEDE_COLUMNS, "preferred", "rejection_reason", "created_at",
)

#: §3.14 and §4.3 as a checkable list. A SUBSTRING list, not a name list: a future
#: `destination_node_id` must fail on the day it is added, not on the day someone
#: reads the schema. Task 5's `unresolved` imports this and obeys the same contract.
FORBIDDEN_COLUMN_SUBSTRINGS: tuple[str, ...] = (
    "path", "destination", "folder", "node", "group",
)

#: A P4 observation key is `sha256:` + 64 hex (M14, verified by execution).
_KEY_PREFIX = "sha256:"
_KEY_LENGTH = len(_KEY_PREFIX) + 64


class EvidenceRequired(Exception):
    """§3.1: a fact is never separable from its evidence.

    Raised when a non-`user_confirmed` fact carries no citation, or when a citation is
    not a P4 observation key. Both are refusals to store, never warnings: a fact whose
    provenance cannot be resolved is the invisible permanent label §3.1 exists to
    prevent.
    """


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """`get_field` raises `FieldNotInCatalogue` for a key outside Task 2's closed
    catalogue, so writing a fact is not a back door into creating a field (§3.5)."""
    return get_field(conn, field_key)["field_key"]


def _checked_refs(refs, reliability_state: str) -> tuple[str, ...]:
    """The M14 citation rule. Sorted, because P4's reads are in insertion order and
    this column must not inherit it (§8.5's replay compares runs)."""
    ordered = tuple(sorted(set(refs)))
    if reliability_state != USER_CONFIRMED and not ordered:
        raise EvidenceRequired(
            f"a {reliability_state} fact cites at least one observation (§3.1); "
            "only a user_confirmed fact may stand without one"
        )
    for ref in ordered:
        if not ref.startswith(_KEY_PREFIX) or len(ref) != _KEY_LENGTH:
            raise EvidenceRequired(
                f"{ref!r} is not a P4 observation key; a citation is the "
                "content-addressed key, never an observation_id or a row id (M14)"
            )
    return ordered


def _checked_quote_refs(conn: sqlite3.Connection, refs) -> tuple[str, ...]:
    """Validate today's quote-citation handle without inventing its future span shape.

    The current public API carries strings, so the enforceable part of §3.6 is that
    every string is an M14 observation key and resolves through P6's citation read.
    P8 still owns validation of the exact text span inside that observation.
    """
    ordered = tuple(sorted(set(refs)))
    for ref in ordered:
        if (not isinstance(ref, str) or not ref.startswith(_KEY_PREFIX)
                or len(ref) != _KEY_LENGTH):
            raise EvidenceRequired(
                f"{ref!r} is not a P4 observation key; a cited quote names stored "
                "evidence by its content-addressed key (M14)"
            )
        if not resolve_citation(conn, ref):
            raise EvidenceRequired(
                f"cited quote {ref!r} resolves to no stored observation; §3.6 "
                "requires the cited quote to be present in the evidence"
            )
    return ordered


def _fact_identity(*, file_id: str, content_hash: str, field_key: str, value_id: str,
                   reliability_state: str, origin: str, cache_key: str,
                   evidence_refs: tuple[str, ...]) -> str:
    """The same conclusion, from the same evidence, at the same cache key, is the same
    fact -- not a second one. `sha256_of` is length-prefixed and injective."""
    return sha256_of("facts.file_facts", file_id, content_hash, field_key, value_id,
                     reliability_state, origin, cache_key,
                     canonical_json(list(evidence_refs)))


def _refuse_divergent(existing: sqlite3.Row, *, active: bool, cited_quote_refs,
                      model_identifier: str | None, prompt_fingerprint: str | None,
                      internal_score: float | None,
                      rejection_reason: str | None) -> None:
    """A second write at the same identity must not silently drop non-identity
    columns. Changing `active` is Task 16's supersession path, not a re-write."""
    wanted = {
        "active": int(bool(active)),
        "cited_quote_refs": canonical_json(list(cited_quote_refs)),
        "model_identifier": model_identifier,
        "prompt_fingerprint": prompt_fingerprint,
        "internal_score": internal_score,
        "rejection_reason": rejection_reason,
    }
    for column, value in wanted.items():
        if existing[column] != value:
            raise ValueError(
                f"a second write at the same identity diverges on {column}; "
                "changing active is Task 16's supersession path, not a re-write"
            )


def write_fact(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
               field_key: str, value_id: str, reliability_state: str, origin: str,
               evidence_refs, cache_key: str, active: bool,
               cited_quote_refs=(), model_identifier: str | None = None,
               prompt_fingerprint: str | None = None,
               internal_score: float | None = None,
               rejection_reason: str | None = None) -> str:
    """Write one fact and author its `fact creation` event. Returns the fact id.

    No path, no destination, no folder, no group -- not as a column and not as a
    keyword (§3.14, §4.3).

    Idempotent: the same conclusion at the same cache key, with the same
    non-identity columns, returns the existing row and appends no second event,
    or the provenance log would count one fact twice. A second write at the
    same identity that changes active, cited_quote_refs, model_identifier,
    prompt_fingerprint, internal_score or rejection_reason is refused -- those
    columns are not part of the identity, and changing `active` is Task 16's
    supersession path, not a re-write.
    """
    check(reliability_state, _states.STATES, name="reliability state")
    check(origin, FACT_ORIGINS, name="fact origin")
    if not cache_key:
        raise ValueError("a fact records the cache key it was computed under (§3.4)")
    refs = _checked_refs(evidence_refs, reliability_state)
    quotes = _checked_quote_refs(conn, cited_quote_refs)
    field_key = _checked_field_key(conn, field_key)

    value = conn.execute(
        'SELECT field_key FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if value is None:
        raise KeyError(f"unknown value {value_id!r}")
    if value["field_key"] != field_key:
        raise ValueError(
            f"value {value_id!r} belongs to field {value['field_key']!r}, not "
            f"{field_key!r}; a value belongs to exactly one field (§3.12), which is "
            "§3.8's role separation"
        )

    fact_id = _fact_identity(
        file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=reliability_state, origin=origin,
        cache_key=cache_key, evidence_refs=refs)
    existing = conn.execute(
        "SELECT * FROM file_facts WHERE fact_id = ?", (fact_id,)
    ).fetchone()
    if existing is not None:
        _refuse_divergent(
            existing, active=active, cited_quote_refs=quotes,
            model_identifier=model_identifier,
            prompt_fingerprint=prompt_fingerprint,
            internal_score=internal_score, rejection_reason=rejection_reason,
        )
        return existing["fact_id"]

    # One call, so the fact row's timestamp and its creation event's timestamp are the
    # same instant from the same clock. `authorship` owns that clock; this module has
    # none of its own.
    event = event_defaults(
        event_type=CREATION,
        file_id=file_id,
        content_hash=content_hash,
        explanation=canonical_json({
            "fact_id": fact_id,
            "field": field_key,
            "value_id": value_id,
            "reliability_state": reliability_state,
            "origin": origin,
            "cache_key": cache_key,
            "evidence_refs": list(refs),
        }),
    )
    # The handle is `isolation_level=None`, so unwrapped the fact INSERT and
    # `append_event` autocommit independently and a failure between them leaves
    # a fact with no `fact creation` event — the §8.2 provenance hole this
    # module's docstring is written against. P1's `transaction` is reentrant,
    # so a caller who already holds a boundary gets a SAVEPOINT.
    with transaction(conn):
        conn.execute(
            "INSERT INTO file_facts (fact_id, file_id, content_hash, field_key, value_id, "
            "reliability_state, origin, evidence_refs, cited_quote_refs, cache_key, "
            "model_identifier, prompt_fingerprint, internal_score, active, "
            "supersedes, superseded_by, supersede_reason, preferred, rejection_reason, "
            "created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "NULL, NULL, NULL, NULL, ?, ?)",
            (fact_id, file_id, content_hash, field_key, value_id, reliability_state,
             origin, canonical_json(list(refs)), canonical_json(list(quotes)), cache_key,
             model_identifier, prompt_fingerprint, internal_score, int(bool(active)),
             rejection_reason, event["observed_at"]),
        )
        append_event(conn, **event)
    return fact_id


def facts_for_file(conn: sqlite3.Connection, file_id: str,
                   content_hash: str) -> list[sqlite3.Row]:
    """Every fact for one file VERSION, with its field key and canonical value joined
    on so no caller reassembles them.

    Per content hash, because the cache key and the abstention row both are (§3.4,
    §8.2). Sorted, because P4's reads are in insertion order and this one imposes its
    own. Unfiltered: selecting by `active`, by `preferred` or by reliability state is
    the proposal-eligible read, which Task 24 owns.
    """
    return list(conn.execute(
        'SELECT f.*, '
        '       v.canonical_value AS canonical_value, '
        '       v.display_label AS display_label '
        'FROM file_facts AS f '
        'JOIN fields AS fl ON fl.field_key = f.field_key '
        'JOIN "values" AS v ON v.value_id = f.value_id '
        'WHERE f.file_id = ? AND f.content_hash = ? '
        'ORDER BY fl.field_key, v.canonical_value, f.fact_id',
        (file_id, content_hash),
    ))
