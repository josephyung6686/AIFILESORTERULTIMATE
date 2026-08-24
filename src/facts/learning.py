# src/facts/learning.py
"""§8.7 correction learning -- the query-before-propose guard (I4).

TWO HALVES, AND ONLY ONE OF THEM CAN FIRE TODAY.

READ (binding now).  §8.7's failure mode is literal: without stored negative feedback
the system "will repeatedly resurface the same attractive but incorrect grouping."
I4 states P6's obligation as: before writing a `file_facts` row that would revive a
`rejected` claim, query the learning store; on an unreset reject, leave the `rejected`
row in place and do not propose the same (field, value) again.  `is_suppressed` is
that query.  It ships with the fact tables because a guard that arrives after the
first fact is written has already failed once.  Its call site is Task 20's resolver.

WRITE (built, unreachable).  Corrections arrive through P13's `review_action`, and
P13 does not exist.  `record_correction` is the surface P13 will route a fact-level
gesture into; nothing in this plan calls it, and P6's tests drive it directly.  Owed
to P13's wave: the gesture surface, the inspect/reset UI, the routing decision, and
the call to `database_agent.learning.reset_preferences`.

P6 MINTS NO §8.2 EVENT TYPE HERE.  A user correction is keyed by `proposal_class` and
`basis_key` -- two ordinary columns beside §8.2's eleven -- never by a type of its own.
The two types used are P6's authored pair from `facts.authorship`, both already among
§8.2's reserved nineteen, so nothing is registered.

P1 STORES, P6 INTERPRETS.  P1's own docstring is explicit that it "derives no polarity,
compares no basis_key, interprets no proposal_class".  Suppressing a proposal is the
acting part's rule, applied here.

WHAT THIS MODULE DELIBERATELY DOES NOT DECIDE.  I4 says an `accept` is not itself a
suppression; it does not say a later `accept` *lifts* an earlier `reject`.  Only a
reset does, in I4's text.  The literal rule is implemented -- any unreset reject at
that scope, subject, class and basis suppresses -- and no newest-wins override is
invented.  An accept lifting a reject without a reset would be a decision for Joseph.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable

from database_agent.events import append_event
from database_agent.learning import learning_records
from evidence_shape.canonical import canonical_json
from facts.authorship import AUTHORED_EVENT_TYPES, event_defaults

#: I4's equivalence table. P6 owns proposal class `fact`; its basis is the claim.
#: `group`, `membership`, `branch`, `placement`, `residual` and `privacy` belong to
#: P9, P10, P11 and P7, and a record at one of those classes is not P6's to read.
PROPOSAL_CLASS: str = "fact"

#: I4: "polarity in accept | reject ... supplied by the acting part, never inferred".
#: Every rule below turns on finding an *unreset reject*; a reader that could not
#: separate rejections from approvals would have to parse explanation free text.
POLARITIES: tuple[str, str] = ("accept", "reject")
ACCEPT, REJECT = POLARITIES

#: P6's two §8.2 names, taken from Task 1's tuple rather than respelled here. Both are
#: reserved names, spelled with a space; `fact_creation` would raise at the writer.
CREATION, REJECTION = AUTHORED_EVENT_TYPES


class MalformedCorrection(Exception):
    """Refused at the writer. `events` is append-only, so a bad row cannot be repaired."""


def basis_key(*, file_id: str, field_key: str, value_id: str) -> str:
    """I4's `(file_id, field, value_id)`, serialized once -- here, and nowhere else.

    Canonical JSON rather than a delimiter join (not injective: a `|` inside a part
    would collide two claims and suppress a proposal the user never rejected) and
    rather than a digest (§8.7 requires the user "be able to inspect or reset learned
    preferences", and an opaque basis is not inspectable).  `canonical_json` sorts
    keys, so the argument order at the call site cannot change the stored key.

    This is NOT a §3.4 cache key and is not one of `facts.cache`'s three: it is I4's
    proposal identity, a different rule over a different triple.

    Member set, dossier hash and display label are NOT in the basis (I4).
    """
    return canonical_json(
        {"field_key": field_key, "file_id": file_id, "value_id": value_id}
    )


def is_suppressed(conn: sqlite3.Connection, *, scope: str, subject_id: str,
                  file_id: str, field_key: str, value_id: str) -> bool:
    """True when an unreset rejection of exactly this claim stands at this scope.

    I4's query-before-propose, applied in order: ignore records at the wrong
    `proposal_class`; ignore records whose `basis_key` does not match; honour a later
    reset; and on a `polarity = reject` record that no later reset covers, do not
    emit.  An `accept` at the same basis is not a suppression and is not read as one.

    The reset is honoured by `learning_records` itself -- it applies the cutoff and
    returns nothing below it.  This function does not re-derive it: a second place
    the cutoff rule lives is a second place it can drift.

    Read-only.  It appends no event, writes no fact, and mutates nothing.
    """
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    for row in learning_records(conn, scope, subject_id):
        if row["proposal_class"] != PROPOSAL_CLASS:
            continue
        if row["basis_key"] != key:
            continue
        if row["polarity"] == REJECT:
            return True
    return False


def record_correction(conn: sqlite3.Connection, *, action: str, scope: str, subject: str,
                      polarity: str, file_id: str, field_key: str, value_id: str,
                      evidence_refs: Iterable[str], user_id: str,
                      observed_at: str) -> int:
    """Author the fact-level consequence of one user correction; P1 writes it (M8).

    P13's stand-in until P13 exists.  `action` is P13's gesture name: P6 stores the
    string in the explanation and branches on `polarity`, never on `action` -- the
    action vocabulary is P13's and P6 does not coin a name another part owns.

    `subject` is not derived from `file_id`.  Five of §8.7's six scopes have no file,
    so the correction's subject is always the caller's to supply.

    `scope` is validated by P1's writer against `CORRECTION_SCOPES`, which is the one
    place the six are spelled.  P6 keeps no copy.
    """
    if polarity not in POLARITIES:
        raise MalformedCorrection(
            f"polarity {polarity!r} is not one of {POLARITIES}; I4 requires it be "
            "supplied by the acting part and never inferred"
        )
    if not action:
        raise MalformedCorrection("action is required; it is P13's gesture name")
    if not user_id:
        raise MalformedCorrection(
            "user_id is required: learning_records filters `user_id IS NOT NULL`, so a "
            "correction stored without one is storable and permanently unreadable"
        )
    refs = tuple(evidence_refs)
    if polarity == REJECT and not refs:
        raise MalformedCorrection(
            "§8.7 requires a rejection be stored with the evidence that produced it"
        )
    key = basis_key(file_id=file_id, field_key=field_key, value_id=value_id)
    explanation = canonical_json({
        "action": action,
        "basis_key": key,
        "evidence_refs": list(refs),
        "polarity": polarity,
        "proposal_class": PROPOSAL_CLASS,
    })
    payload = event_defaults(
        event_type=REJECTION if polarity == REJECT else CREATION,
        observed_at=observed_at,
        explanation=explanation,
        file_id=file_id,
        user_id=user_id,
        correction_scope=scope,
        correction_subject=subject,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS,
        basis_key=key,
    )
    return append_event(conn, **payload)
