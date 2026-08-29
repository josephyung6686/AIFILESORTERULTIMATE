# src/facts/values.py
"""§3.12's `values` table -- "the changing, user-specific content discovered from
files", as against `fields`, which are "the long-term organization language of the
product".

Three design sentences are load-bearing here, and each is a test rather than a comment:

  * §3.12: "The system may create new values when it sees a new course, project,
    company, university, or event, but it should not invent new fields automatically."
    `ensure_value` creates a VALUE row and never a FIELD row. The field must already be
    in Task 2's closed catalogue; `get_field` raises `FieldNotInCatalogue` if it is not,
    so creating a value is not a back door into creating a field (§3.5).
  * §3.12 again: "a value belongs to exactly one field". The same string under two
    fields is two values. That is §3.8's role separation -- "the same entity type in a
    different role is a different field" -- expressed in this table.
  * §2.8: "If a document says U Chicago, the raw observation remains exactly that
    wording, while a resolver may normalize it to University of Chicago and the user
    may later choose to display it as UChicago." Three renderings, three columns,
    none of them overwriting another.

`value_id` is content-addressed over (field_key, canonical_value). That makes
`ensure_value` idempotent with no read-then-write race, gives two databases that saw
the same corpus the same value ids (§8.5's replay), and turns one-value-one-field into
a property of the identifier rather than a rule to remember.

Ordering is imposed, never inherited. `raw_variants` and `aliases` are stored sorted,
and `values_in_field` sorts, because P4's reads are in insertion order (verified by
execution) and a corpus extracted in a different order must not produce a different
row.

The table name is a SQL keyword and every statement below quotes it.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

from database_agent.db import transaction

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import check

from facts.fields import get_field

__all__ = [
    "VALUE_ORIGINS", "ValueRow", "add_raw_variant", "ensure_value", "merge_values",
    "set_display_label", "values_in_field",
]

#: §3.12's two origins. A closed vocabulary, checked through P4's `check` so a foreign
#: value raises `NotInVocabulary` instead of being stored (Global Constraints).
VALUE_ORIGINS: tuple[str, str] = ("automatic", "user")

#: An observation key is P4's, content-addressed, and `sha256:`-prefixed (M14).
_KEY_PREFIX = "sha256:"


@dataclass(frozen=True)
class ValueRow:
    """The SPEC's `values` shape, with its two JSON arrays already decoded.

    Decoding happens in exactly one place. A reader that calls `json.loads` on
    `raw_variants` itself is a second decoder, and a second decoder is where the two
    representations drift.
    """

    value_id: str
    field_key: str
    canonical_value: str
    raw_variants: tuple[str, ...]
    display_label: str | None
    aliases: tuple[str, ...]
    origin: str
    first_evidence_ref: str | None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "ValueRow":
        return cls(
            value_id=row["value_id"],
            field_key=row["field_key"],
            canonical_value=row["canonical_value"],
            raw_variants=tuple(json.loads(row["raw_variants"])),
            display_label=row["display_label"],
            aliases=tuple(json.loads(row["aliases"])),
            origin=row["origin"],
            first_evidence_ref=row["first_evidence_ref"],
        )


def _checked_field_key(conn: sqlite3.Connection, field_key: str) -> str:
    """The catalogue row's key, and the gate that stops a value inventing a field.

    `get_field` raises `FieldNotInCatalogue` for a key outside Task 2's closed
    catalogue, so this function is also §3.12's "it should not invent new fields
    automatically" enforced on the value path.
    """
    return get_field(conn, field_key)["field_key"]


def _value_identity(*, field_key: str, canonical_value: str) -> str:
    """Content-addressed value identity. `sha256_of` is length-prefixed and injective,
    so ("a", "bc") and ("ab", "c") do not collide."""
    return sha256_of("facts.values", field_key, canonical_value)


def _fetch(conn: sqlite3.Connection, value_id: str) -> sqlite3.Row:
    row = conn.execute(
        'SELECT * FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if row is None:
        raise KeyError(f"unknown value {value_id!r}")
    return row


def _store_list(items) -> str:
    """One sorted, de-duplicated, canonical JSON array. Sorted because P4's reads are
    in insertion order and this row must not inherit it."""
    return canonical_json(sorted(set(items)))


def ensure_value(conn: sqlite3.Connection, *, field_key: str, canonical_value: str,
                 first_evidence_ref: str | None, origin: str) -> str:
    """§3.12's auto-create. Returns the value id, creating the row on first sight.

    Idempotent: the second sighting of the same canonical value under the same field
    returns the first row's id and does not overwrite its `first_evidence_ref`, which
    is the observation that introduced it.
    """
    check(origin, VALUE_ORIGINS, name="value origin")
    if not canonical_value:
        raise ValueError("a value needs a canonical form (§3.12)")
    if origin == VALUE_ORIGINS[0]:
        if not first_evidence_ref or not first_evidence_ref.startswith(_KEY_PREFIX):
            raise ValueError(
                "an automatically created value cites the observation that introduced "
                "it (§3.1); first_evidence_ref must be a P4 observation key"
            )
    field_key = _checked_field_key(conn, field_key)
    value_id = _value_identity(field_key=field_key, canonical_value=canonical_value)
    existing = conn.execute(
        'SELECT value_id FROM "values" WHERE value_id = ?', (value_id,)
    ).fetchone()
    if existing is not None:
        return existing["value_id"]
    conn.execute(
        'INSERT INTO "values" (value_id, field_key, canonical_value, raw_variants, '
        'display_label, aliases, origin, first_evidence_ref, merged_into, '
        'merge_reason) VALUES (?, ?, ?, ?, NULL, ?, ?, ?, NULL, NULL)',
        (value_id, field_key, canonical_value, _store_list(()), _store_list(()),
         origin, first_evidence_ref),
    )
    return value_id


def add_raw_variant(conn: sqlite3.Connection, value_id: str, raw: str) -> None:
    """§2.8: "the raw observation remains exactly that wording". Byte-exact, and
    recorded once however many times it is seen."""
    if not raw:
        raise ValueError(
            "a raw variant is the wording the document used; it is never empty (§2.8)"
        )
    row = _fetch(conn, value_id)
    variants = json.loads(row["raw_variants"])
    if raw in variants:
        return
    conn.execute(
        'UPDATE "values" SET raw_variants = ? WHERE value_id = ?',
        (_store_list([*variants, raw]), value_id),
    )


def set_display_label(conn: sqlite3.Connection, value_id: str,
                      display_label: str) -> None:
    """§2.8's third rendering: "the user may later choose to display it as UChicago".

    Stored unscoped. §8.8 places the display label inside a plan version and Task 22
    owns that scoping; this function invents no `plan_version` keyword, because no
    caller could supply one today and a required keyword nobody can fill is a
    threshold with no injector.
    """
    if not display_label:
        raise ValueError("a display label is a rendering, never empty (§2.8)")
    _fetch(conn, value_id)
    conn.execute(
        'UPDATE "values" SET display_label = ? WHERE value_id = ?',
        (display_label, value_id),
    )


def merge_values(conn: sqlite3.Connection, *, keep: str, merged: str,
                 reason: str) -> None:
    """§0's taxonomy aliases. The merge records an alias and deletes nothing (§8.2).

    The merged row keeps its identity, its canonical wording and its evidence ref, and
    gains a pointer to the surviving value, so every fact that already pointed at it
    still resolves and a reader can see where it went. The surviving row absorbs the
    merged value's canonical wording, its label and its raw variants as aliases.
    """
    if not reason:
        raise ValueError("a merge records why (§8.2)")
    if keep == merged:
        raise ValueError("a value cannot be merged into itself")
    # Authority reads, the cycle walk and both writes share one SQLite boundary. If
    # the reads happened before BEGIN, another connection could change the merge
    # chain before these writes and invalidate the decision. P1's transaction is
    # reentrant, so a caller who already holds a boundary gets a SAVEPOINT.
    with transaction(conn):
        keep_row, merged_row = _fetch(conn, keep), _fetch(conn, merged)
        if keep_row["field_key"] != merged_row["field_key"]:
            raise ValueError(
                "a value belongs to exactly one field (§3.12); merging across two "
                "fields would erase §3.8's role separation"
            )
        if merged_row["merged_into"] is not None:
            raise ValueError(
                f"{merged} is already merged into {merged_row['merged_into']}; "
                "the first merge_reason is never overwritten (§8.2)"
            )
        seen, cursor = {merged}, keep
        while cursor is not None:
            if cursor in seen:
                raise ValueError("merge chain would cycle")
            seen.add(cursor)
            row = conn.execute(
                'SELECT merged_into FROM "values" WHERE value_id = ?', (cursor,)
            ).fetchone()
            cursor = None if row is None else row["merged_into"]

        aliases = set(json.loads(keep_row["aliases"]))
        aliases.add(merged_row["canonical_value"])
        aliases.update(json.loads(merged_row["aliases"]))
        if merged_row["display_label"]:
            aliases.add(merged_row["display_label"])
        variants = set(json.loads(keep_row["raw_variants"]))
        variants.update(json.loads(merged_row["raw_variants"]))
        conn.execute(
            'UPDATE "values" SET aliases = ?, raw_variants = ? WHERE value_id = ?',
            (_store_list(aliases), _store_list(variants), keep),
        )
        conn.execute(
            'UPDATE "values" SET merged_into = ?, merge_reason = ? WHERE value_id = ?',
            (keep, reason, merged),
        )


def values_in_field(conn: sqlite3.Connection, field_key: str) -> list[sqlite3.Row]:
    """Every value in one field, merged ones included -- a merged value is still a
    readable value (§8.2) and a fact that points at it must still resolve.

    Sorted, because P4's reads are in insertion order and this one imposes its own.
    """
    return list(conn.execute(
        'SELECT * FROM "values" WHERE field_key = ? '
        'ORDER BY canonical_value, value_id',
        (_checked_field_key(conn, field_key),),
    ))
