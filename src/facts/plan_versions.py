"""§8.8 — what belongs to a plan version, and what does not.

> **CUT 3 is UNRATIFIED (D13).** Round 5 recommended cutting this module. Its
> argument in one sentence: §8.8's guarantee is a negative, and a negative is
> enforced by the absence of a column rather than by a new table. It is **not
> ruled** — written in full so a reader deciding the cut has it in front of them,
> and flagged rather than silently complied with or silently ignored.

§8.8's guarantee is one sentence: "A new plan should never silently reclassify or move
old files. It creates a new set of placement recommendations subject to review. The
evidence database remains shared across plan versions, but the destination tree and
user policy define which projections are valid in each version."

THE NEGATIVE, which is the half that matters.  Nothing P6 stores as a record is
plan-versioned: `fields`, value identity, `file_facts`, `unresolved`, every evidence
ref, every reliability state and all supersession history are shared.  Enforced by
ABSENCE -- no record table carries a plan-version column, so there is nowhere a
version could be written even by a later mistake.  A new plan version therefore
re-resolves nothing, invalidates nothing and reclassifies nothing; §3.4's cache key has
five parts and a plan version is none of them.

THE POSITIVE.  §8.8's plan version captures "User labels and aliases", so the RENDERING
of a value is the plan's.  `UChicago` and `University of Chicago` are two labels for
one value, and choosing between them must leave the value and every fact pointing at
it untouched.  That is why the rendering lives here, in a plan-version-keyed side
table, and not on the `values` row: writing it there would rewrite a row every other
plan version shares, which is the silent cross-version mutation §8.8 forbids.

`facts.values.set_display_label` remains what it is -- the version-INDEPENDENT default
§2.8 describes, stored unscoped, and its own docstring already says the §8.8 scoping is
owed elsewhere.  This module is that elsewhere.  It does not modify, wrap or deprecate
it, and it never writes the `values` row.

`aliases` is declared in PLAN_VERSIONED and has no writer here on purpose.  §8.8
versions "labels and aliases", so the boundary names both; but `values.aliases` is
already §0's taxonomy aliases, which are identity rather than rendering, and no
Done-means asks for a per-version alias override.  Declaring the boundary is this
module's job; building a column with no writer is not (D3).  The per-version alias
override is OWED, not stubbed.

P6 MINTS NO §8.2 EVENT TYPE HERE and appends none.  §8.8's plan diff ("Applications was
renamed to Admissions") belongs to the plan-version object, and that object is P10's
and P12's.  `destination-tree edit` is a reserved name and is not P6's to write.
"""
from __future__ import annotations

import sqlite3

from facts.schema import VALUE_RENDERINGS_DDL, VALUE_RENDERINGS_TABLE

#: §8.8: "User labels and aliases" are captured BY a plan version. A declaration of the
#: boundary, not a column list -- only `display_label` has a writer today.
PLAN_VERSIONED: tuple[str, ...] = ("display_label", "aliases")

#: Everything a plan version must NOT be able to change. The four record tables, plus
#: the three fact properties §8.8's guarantee turns on.
SHARED_ACROSS_PLAN_VERSIONS: tuple[str, ...] = (
    "fields",
    "values",
    "file_facts",
    "unresolved",
    "evidence_refs",
    "reliability_state",
    "supersession_history",
)

#: The one plan-version-keyed table P6 owns. Not a fifth RECORD table: it holds no
#: claim, no evidence and no reliability state, and nothing reads it to decide a fact.
VALUE_RENDERINGS_COLUMNS: tuple[str, ...] = (
    "value_id", "plan_version", "display_label",
)



def _value_row(conn: sqlite3.Connection, value_id: str) -> sqlite3.Row:
    # `values` is a SQLite keyword; the identifier must be quoted or the statement is
    # a syntax error rather than a missing table.
    row = conn.execute(
        'SELECT canonical_value, display_label FROM "values" WHERE value_id = ?',
        (value_id,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"no value {value_id!r}: a rendering with no value to render would be a "
            "label the user can never trace back to a fact"
        )
    return row


def set_display_label(conn: sqlite3.Connection, *, value_id: str, plan_version: str,
                      label: str) -> None:
    """Record the label THIS plan version shows for one value. Touches no record.

    Writes only `value_renderings`: no fact, no value, no field, no event. A repeat
    for the same version replaces that version's choice rather than accumulating a
    second one -- a value renders one way per version or the display is ambiguous.
    """
    if not plan_version:
        raise ValueError("plan_version is required: a rendering belongs to a version")
    if not label:
        raise ValueError(
            "label is required: an empty rendering is not a choice, and clearing one "
            "is a different operation than making one"
        )
    _value_row(conn, value_id)
    conn.execute(
        "INSERT INTO value_renderings (value_id, plan_version, display_label) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT (value_id, plan_version) DO UPDATE SET "
        "display_label = excluded.display_label",
        (value_id, plan_version, label),
    )


def display_label(conn: sqlite3.Connection, *, value_id: str,
                  plan_version: str) -> str:
    """This version's rendering, else the value's own label, else its canonical string.

    Total by construction: §5.5 previews "three schools, five terms, and twelve course
    branches" before the user commits, and a renderer that can return None shows
    nothing for a value whose version made no choice.

    The chain never borrows another version's label. A rendering is scoped to the
    version that chose it, exactly as §8.8 scopes everything else a plan captures.
    """
    chosen = conn.execute(
        "SELECT display_label FROM value_renderings "
        "WHERE value_id = ? AND plan_version = ?",
        (value_id, plan_version),
    ).fetchone()
    if chosen is not None:
        return chosen["display_label"]
    value = _value_row(conn, value_id)
    return value["display_label"] or value["canonical_value"]
