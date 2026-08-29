# src/facts/direct.py
"""§3.5's direct facts. The slot decides, and the slot is injected.

§3.5: "Deterministic extractors create direct facts when the information comes from a
reliable, explicit source, such as a content hash, EXIF timestamp, a document title,
or a labeled form field." §3.13 repeats it in the reliability vocabulary. Both
sentences name a LOCATION, never a value and never a confidence -- which is P4's own
fixture 6, whose design case reads "direct describes the slot, not the value's
usefulness" over a `raw_value` of `python-docx`.

Three consequences, and each is a test rather than a comment:

* **No test is applied to the observation's own `reliability`.** P4's fixture 12 is
  §3.5's labeled form field and P4 marks it `possible`; a gate here would make one of
  the four named slots unreachable against P4's own fixture for it. An extractor's
  two admissible states are a claim about an OBSERVATION (P4 D11); the fact's six are
  P6's, and Task 1 asserts that boundary from both sides.

* **A `Producer` slot would therefore make `python-docx` a direct fact.** It is
  stopped by §2.2's suppression tier firing first (`facts.discount`), never by
  anything here. This module declares no slot and imports nothing from that one; the
  ordering is the sequencer's.

* **No slot name appears in this file.** P5 spells no EXIF tag name anywhere, on
  purpose (P4 D7: "the source format's own slot name, verbatim"), so a literal here
  would be P6 minting a vocabulary member P5 refused to publish. `DirectSlots`
  arrives at the call with no default. The catalogue behind it does not exist (F8).

The predicate reads P4's `locator` -- `metadata:field=DateTimeOriginal`,
`title:page=1`, `table:sheet=2/row=7/column=3` -- because that is the slot's
published name and reading it needs no rule for which `container_path` segment names
a slot. Such a rule would differ per format, which is what §2.8 exists to prevent.

This producer never abstains. §8.6's order is direct, then rule-validated, then the
model; a field no direct slot filled is a field the next producer has not tried. An
`unresolved` row here would answer §8.5's "Did it abstain when evidence was absent?"
with a claim that had not happened yet. The sequencer writes that row once, at the
end.

`get_file` is read for exactly one thing: P1 owns §1.2's identity, and a `direct`
fact -- the strongest state a deterministic producer writes -- must not be anchored
to a `file_id` the system of record does not hold. No VALUE is taken from the row:
`files.content_hash` and `files.observed_timestamps` are the two columns a careless
implementation would mine for §3.5's first and second slots, and neither is citable
evidence (M14 makes every citation an `observation_key`).
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Callable, Iterable

from database_agent.files_table import get_file as _get_file
from evidence_shape.observation import Observation

from facts.cache import pass_cache_key
from facts.discount import MetadataScreen, field_permitted
from facts.evidence import cite as _cite
from facts.evidence import observations_for_version as _observations_for_version
from facts.file_facts import write_fact as _write_fact
from facts.file_facts import DETERMINISTIC_EXTRACTOR
from facts.states import DIRECT
from facts.values import VALUE_ORIGINS as _VALUE_ORIGINS
from facts.values import ensure_value as _ensure_value

#: Task 1 owns the spelling. Never an index into STATES.
DIRECT_STATE: str = DIRECT

#: Task 4 owns the spelling. Never an index into FACT_ORIGINS.
DIRECT_ORIGIN: str = DETERMINISTIC_EXTRACTOR


class UnknownFile(Exception):
    """P1 holds no `files` row for the `file_id` a direct fact was asked for."""


@dataclass(frozen=True)
class DirectSlot:
    """One of §3.5's explicit slots, named and canonicalised by the caller.

    `names` is a predicate over the slot's published name -- P4's
    `Observation.locator`. `canonical` turns the raw reading into the fact's value;
    §3.2's own example is `2026:07:17 14:03:22` becoming `2026-07-17`, and P6 owns
    neither end of that map (round 4's C-5: `normalize(field, raw_value)` is claimed
    by P8's Contract-in and disowned by P6's Task 17, so no part builds it). A
    canonicaliser that raises propagates: a broken injection must not arrive as a
    silent absence of facts (§8.6).
    """

    slot_id: str
    field_key: str
    names: Callable[[str], bool]
    canonical: Callable[[str], str]
    #: An optional predicate over the RAW READING, beside `names`'s predicate over
    #: the locator. `None` claims every reading `names` matched, which is what
    #: every existing caller gets and what the parameter's absence has always
    #: meant.
    #:
    #: It exists because §3.5 speaks of slots in the PLURAL and `names` alone
    #: cannot make that true. `00`:78's own recommended tree is
    #: `Academics/Columbia/2026-Spring/PHYS1401/Homework`, so at least two of its
    #: dimensions are read out of the same document text -- and a course code and
    #: a term sitting in one body share every locator prefix there is. Two slots
    #: declared over them would each claim the other's readings, and every file
    #: would carry a term called PHYS1401. A deployment could therefore only ever
    #: ship ONE text slot, which is exactly what the shipped one does.
    #:
    #: The predicate is the CALLER'S, like `names` above and `canonical` below.
    #: P6 authors no pattern here and gains no opinion about what a term looks
    #: like; it gains only the ability to be told.
    matches: Callable[[str], bool] | None = None


@dataclass(frozen=True)
class DirectSlots:
    """The injected slot set. No default, so no call can omit it (F8)."""

    slots: tuple[DirectSlot, ...]


def direct_facts(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                 slots: DirectSlots, screen: MetadataScreen) -> tuple[str, ...]:
    """§3.5's direct facts for one version of one file. Returns the fact ids.

    Every reading a slot claims becomes a `direct` fact citing the observation it was
    read from. Readings that agree on a value are ONE fact with several citations
    (§3.1: "Every fact preserves where it came from" -- plural); that is not an answer
    to OQ6, which asks how many values a field may hold.

    `screen` is §2.2/§2.3's injected catalogue and has NO DEFAULT, the same shape
    `DirectSlots` uses and for the same reason (F8). A slot set that claims
    `metadata:field=Producer` is exactly what `FactResolver`'s own docstring warns
    about -- "without this call `python-docx` can become a `direct` fact" -- so the
    screen is consulted before the reading is canonicalised, not after: a
    canonicaliser is the caller's and must not be handed a value §2.2 has refused.
    """
    if _get_file(conn, file_id) is None:
        raise UnknownFile(
            f"P1 holds no files row for {file_id!r}; P6 re-observes no filesystem "
            f"and will not anchor a {DIRECT_STATE!r} fact to a file the system of "
            f"record has never seen"
        )

    grouped: dict[tuple[str, str], list[Observation]] = {}
    for slot in slots.slots:
        for one in _observations_for_version(conn, file_id, content_hash):
            if not slot.names(one.locator):
                continue
            if slot.matches is not None and not slot.matches(one.raw_value):
                continue
            if not field_permitted(
                    one, slot.field_key,
                    tool_producer_strings=screen.tool_producer_strings,
                    metadata_property_names=screen.metadata_property_names):
                continue
            key = (slot.field_key, slot.canonical(one.raw_value))
            grouped.setdefault(key, []).append(one)

    written: list[str] = []
    for (field_key, canonical_value) in sorted(grouped):
        cited = grouped[(field_key, canonical_value)]
        refs = tuple(sorted({_cite(one) for one in cited}))
        value_id = _ensure_value(conn, field_key=field_key,
                                 canonical_value=canonical_value,
                                 first_evidence_ref=refs[0],
                                 origin=_VALUE_ORIGINS[0])
        written.append(_write_fact(
            conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
            value_id=value_id, reliability_state=DIRECT_STATE,
            origin=DIRECT_ORIGIN, evidence_refs=refs,
            cache_key=pass_cache_key(conn, file_id=file_id,
                                     content_hash=content_hash),
            active=True))
    return tuple(written)


