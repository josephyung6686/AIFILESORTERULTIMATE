# src/facts/supersede.py
"""§8.2 supersession, and the `preferred` pointer M1 places on P6 (§8.2, §8.7).

§8.2, and it is the whole task in one paragraph:

    "The product must never overwrite the evidence record merely because a later
     extractor or model produces a different answer. A newer result should supersede
     an earlier result while retaining the old observation and the reason it was
     superseded. ... The resolver may mark the newer value as preferred, but a user
     reviewing a placement should still be able to inspect the origin of the
     conclusion."

**What P1 does and what this module adds.** `mark_superseded` writes three columns
across two rows -- `superseded_by` and `supersede_reason` on the old, `supersedes` on
the new -- and, verified by execution, knows nothing about `preferred`. So the pointer
is this module's whole addition, set in the same call that links the two rows and set
nowhere else in `facts`.

**No event is appended here.** §8.2 gives P6 two event types, `fact creation` and
`fact rejection`, and supersession is neither: §8.7 keeps a `rejected` fact rather
than removing it, so rejection is a STATE a fact carries, while supersession is one
fact replacing another -- and P1 publishes three columns for exactly that, one of
which is the reason §8.2 asks to be retained. M8 also puts `subsystem = "P6"` in one
module, so an `append_event` call here would be a second home for P6's authorship.
Task 4 already appends `fact creation` when the new fact is written; this call links
two rows that both already exist.

**The chain is walked backwards before forwards.** P1's `chain` walks forward only:
with `a -> b -> c` recorded, `chain(a)` is `[a, b, c]` and `chain(c)` is `[c]`. A
history read starting from the newest row would return one row and look correct, so
`fact_history` finds each chain's tail through `supersedes` first. The walk needs no
cycle guard: `mark_superseded` refuses a cycle at write time, so the graph on disk is
acyclic by construction rather than by a second policy here.

**The slot is addressed through Task 4's reader, never through `field_key`.** Which
column `file_facts` uses to reference the catalogue is Task 4's schema decision, and a
second module spelling it would be a second home for one decision. This module reads
`file_id` and `content_hash`, takes the field key off `facts_for_file`'s rows, and
expands each into its history with P1's `chain`.

**`preferred` is a pointer, not a strength.** The SPEC's negative is exact: "It never
enters the §3.6 contradiction check, never breaks a §3.7 margin tie, and never makes a
fact destination-eligible. A reader that wants strength reads `reliability_state`."
Nothing here exports it into those paths, and a test parses those modules for the
column by name.
"""
from __future__ import annotations

import sqlite3

from database_agent.supersede import chain, mark_superseded

from facts.file_facts import facts_for_file
from facts.states import USER_CONFIRMED

#: The table P1's `mark_superseded` and `chain` are addressed by. Task 4 owns the DDL,
#: including the VIRTUAL `record_id` projection of `fact_id` that P1 requires and the
#: `preferred` column this module sets; the name has one home and the test asserts it
#: names a table carrying both.
FACT_TABLE: str = "file_facts"


class PreferredNeverReverses(ValueError):
    """§3.13's ordering, raised rather than documented.

    "A `user_confirmed` fact is always the preferred row for its `(file_id,
    field_key)`; §3.13's ordering is not negotiable and `preferred` never reverses it."
    """


class SupersedeAcrossSlots(ValueError):
    """§8.2 replaces an ANSWER, so both rows answer the same question."""


def _row(conn: sqlite3.Connection, fact_id: str) -> sqlite3.Row:
    row = conn.execute(
        f"SELECT * FROM {FACT_TABLE} WHERE fact_id = ?", (fact_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown fact {fact_id!r}")
    return row


def _tail(conn: sqlite3.Connection, fact_id: str) -> str:
    """The oldest row of this fact's chain.

    P1's `chain` walks forward only, so a history read has to find the start itself.
    No cycle guard: `mark_superseded` walks the prospective chain and refuses one at
    write time, so this loop terminates on any graph the writer could have produced.
    """
    row = _row(conn, fact_id)
    while row["supersedes"] is not None:
        row = _row(conn, row["supersedes"])
    return row["fact_id"]


def _slot(conn: sqlite3.Connection, *, file_id: str,
          field_key: str) -> list[sqlite3.Row]:
    """Every row for one (file, field) slot, superseded rows included.

    Spans every content hash the file has had, which is what a reader inspecting the
    origin of a conclusion needs: §8.2's user "does not know which version produced
    it". Supersession itself always happens inside one content hash, because §3.4's
    invalidation cases -- a bumped extractor version, a changed prompt fingerprint, a
    new analysis tier -- all leave the bytes alone.
    """
    hashes = sorted(row["content_hash"] for row in conn.execute(
        f"SELECT DISTINCT content_hash FROM {FACT_TABLE} WHERE file_id = ?",
        (file_id,)))
    reachable: dict[str, sqlite3.Row] = {}
    for content_hash in hashes:
        for row in facts_for_file(conn, file_id, content_hash):
            if row["field_key"] != field_key:
                continue
            for member in chain(conn, FACT_TABLE, _tail(conn, row["fact_id"])):
                reachable[member["fact_id"]] = member
    return [reachable[fact_id] for fact_id in sorted(reachable)]


def supersede_fact(conn: sqlite3.Connection, *, old_fact_id: str,
                   new_fact_id: str, reason: str) -> None:
    """Done-means 29. Link two facts, and move the pointer. Nothing is deleted.

    The reason is required by P1 and is the half §8.2 names explicitly -- "retaining
    the old observation AND the reason it was superseded".
    """
    old = _row(conn, old_fact_id)
    new = _row(conn, new_fact_id)
    if (old["file_id"], old["field_key"]) != (new["file_id"], new["field_key"]):
        raise SupersedeAcrossSlots(
            "§8.2 supersedes an answer: both facts must be for one file and one "
            f"field; {old_fact_id!r} and {new_fact_id!r} are not")
    if old["reliability_state"] == USER_CONFIRMED != new["reliability_state"]:
        raise PreferredNeverReverses(
            f"{old_fact_id!r} is {USER_CONFIRMED!r}; §3.13's ordering is not negotiable "
            "and `preferred` never reverses it, so a weaker fact cannot take the "
            "pointer from a user's own answer")
    mark_superseded(conn, FACT_TABLE, old_id=old_fact_id, new_id=new_fact_id,
                    reason=reason)
    conn.execute(f"UPDATE {FACT_TABLE} SET preferred = 0 WHERE fact_id = ?",
                 (old_fact_id,))
    conn.execute(f"UPDATE {FACT_TABLE} SET preferred = 1 WHERE fact_id = ?",
                 (new_fact_id,))


def preferred_fact(conn: sqlite3.Connection, *, file_id: str,
                   field_key: str) -> sqlite3.Row | None:
    """The row a reader should show for this slot, or `None`.

    Three cases are answerable and are answered:

    * a `user_confirmed` live row wins outright -- §3.13's ordering is not
      negotiable and the SPEC names this case;
    * a single live row is the answer even though `preferred` was never set on it,
      because the column is set ONLY on supersession;
    * among several live rows, exactly one carrying `preferred` is the pointer.

    Anything else returns `None`. OQ6 -- multiplicity -- is open and the SPEC carries
    `multiplicity` as an unanswered column, so "which of several simultaneous values
    is preferred" is that question and a reader that picked one would close it by
    accident.

    Live means not superseded. `active` is a different axis and is Task 4's: §8.2's
    mechanism for the pointer is supersession, and reading a second column here would
    make the pointer depend on two rules instead of one.
    """
    live = [row for row in _slot(conn, file_id=file_id, field_key=field_key)
            if row["superseded_by"] is None]
    confirmed = [row for row in live if row["reliability_state"] == USER_CONFIRMED]
    if confirmed:
        live = confirmed
    if len(live) == 1:
        return live[0]
    pointed = [row for row in live if row["preferred"]]
    return pointed[0] if len(pointed) == 1 else None


def fact_history(conn: sqlite3.Connection, *, file_id: str,
                 field_key: str) -> list[sqlite3.Row]:
    """Done-means 15's history half. Every row for the slot, oldest first.

    Superseded rows included, each carrying its own reliability state, its own
    evidence refs and the reason it was superseded -- §8.2's "a user reviewing a
    placement should still be able to inspect the origin of the conclusion".
    """
    rows = _slot(conn, file_id=file_id, field_key=field_key)
    tails = sorted({_tail(conn, row["fact_id"]) for row in rows})
    history: list[sqlite3.Row] = []
    for tail in tails:
        history.extend(chain(conn, FACT_TABLE, tail))
    return history
