# src/privacy/resolve.py
"""(observation_key, span) -> text. The only module in the product that does this.

Everything about this module is narrow deliberately:

- **The handle is the key, never the id** (M14). SPEC *Correction learning*: "The key,
  not the id, is what makes that durable" -- a per-row `observation_id` dies when the
  extractor is upgraded, and a citation that stops resolving is a citation that stops
  being evidence.
- **The current row, not the first.** P4's reader is a LIST on purpose: "two extractor
  versions carry one key, which is what MINOR 8 arranged". Resolving to a superseded
  row would release text a later extractor already retracted.
- **Two resolvers and no third.** A `text_span` materialises through P4's
  `raw_value_at` behind P4's own `check_span_anchor`; a container-path-only address
  (§2.3's table/row/cell, §2.8's EXIF field) materialises `Observation.raw_value`,
  because `unit_for_observation` returns None for one and there is nothing to take a
  substring of. Anything else raises. A fallback to the whole unit is how "send the
  cell" becomes "send the sheet". The span-less branch ASKS whether that is the
  shape it has rather than assuming it (CR-07): a whole text document is emitted
  span-less too, at the empty path where its own text unit stands, and the unit
  lookup is the one thing that tells a cell from a document.
- **A failure is a refusal, never a repair.** P4's checker "raises; never returns a
  repair", and P4 does not validate the anchor at write time, so this is the only
  thing between a stale span and released text.

One thing here is not P4's, and it is reported rather than hidden: P4 publishes no
reader that returns the CURRENT row for a key. `observations_by_key` returns records
carrying neither `observation_id` nor `superseded_by`, and `supersede_chain` needs an
id those records do not have. `current_observation` therefore issues one read-only
SELECT for the live id and hands it straight back to P4's published `get_observation`.
The one-function fix belongs in P4 -- `store.current_observation_by_key(conn,
observation_key) -> Observation | None` -- and this module is the caller waiting for it.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.store import (
    get_observation, observations_by_key, unit_for_observation,
)
from evidence_shape.location import Location
from evidence_shape.locator import location_from_mapping
from evidence_shape.observation import Observation
from evidence_shape.text_units import SpanAnchorError, check_span_anchor, raw_value_at

from privacy.redaction import span_address

#: The P4 functions that turn a stored record into a string of document text, by
#: module. Published so Task 21's single-locus guard names them instead of matching
#: on the word "text" -- an AST walk needs a subject, and a guess is how a guard
#: passes vacuously.
MATERIALISERS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "evidence_shape.store": (
        "get_observation", "observation_row", "observations_by_key",
        "observations_for_file", "observations_for_run", "text_unit_at",
        "text_units_for_run", "unit_for_observation",
    ),
    "evidence_shape.text_units": ("raw_value_at",),
})


class UnresolvableSpan(Exception):
    """The address does not resolve, and the gate does not guess.

    Raised for an unknown key, an id passed where a key belongs, a span that does not
    anchor, a span with no unit, and a caller span that disagrees with the record.
    """


class AmbiguousObservationKey(Exception):
    """The key resolves to no live row, or to more than one.

    P4's reader is multi-valued on purpose; the supersession chain is what makes it
    single-valued again. When it does not, picking one would release the wrong text
    silently, so this raises instead.
    """


@dataclass(frozen=True, slots=True)
class CurrentLocation:
    """The owning file and Location of one live observation, with no content."""

    file_id: str
    location: Location


def current_location(conn: sqlite3.Connection,
                     observation_key: str) -> CurrentLocation:
    """Return the sole live location for a key without selecting content.

    Consent needs a canonical address before it may read protected text. Keep this
    query explicit: adding ``raw_value`` or context columns here would move content
    access in front of the consent decision.
    """
    rows = conn.execute(
        "SELECT observation_id, observation_key, file_id, location, superseded_by "
        "FROM evidence WHERE observation_key = ? ORDER BY rowid",
        (observation_key,),
    ).fetchall()
    if not rows:
        raise UnresolvableSpan(
            f"no observation carries key {observation_key!r}. P4's citation handle "
            "is the content-addressed `observation_key`, not a per-row id"
        )
    live = [row for row in rows if row["superseded_by"] is None]
    if len(live) != 1:
        raise AmbiguousObservationKey(
            f"key {observation_key!r} has {len(live)} live rows among {len(rows)} "
            "candidates; no unique current location exists"
        )
    return CurrentLocation(
        file_id=live[0]["file_id"],
        location=location_from_mapping(json.loads(live[0]["location"])),
    )


@dataclass(frozen=True, slots=True)
class Materialised:
    """One resolved item, with M5's three context fields still attached.

    No `file_id`, no path, no `content_hash`: §8.4 puts "Paths" and "file hashes" in
    the always-local set, and the type is where that is cheapest to enforce.

    `unit_length` is the STORED length of the text unit the span points into, or None
    for a container-path address that has no unit. Task 7's whole-document check --
    §8.4's "It should not send full documents where a short heading or OCR excerpt is
    enough to resolve the question" -- needs it, and this module is the only one that
    may ask P4 for it.

    Beside a SPAN-LESS address it is the same measurement and carries one more fact:
    it is the length of the unit standing at the observation's own container path,
    and it is set only when the resolved value covers the whole of that unit. A
    non-None `unit_length` next to a span-less item therefore states "this value is
    a whole text unit", which is how `items.is_whole_document` reads it (CR-07).
    §2.3's cell, §2.8's field and a `title` field have no unit at their own path and
    keep the `None` that has always meant "there is nothing here to be the whole of".
    """

    observation_key: str
    span: str
    value: str
    zone: str
    context_before: str | None
    context_after: str | None
    context_truncated: bool
    unit_length: int | None


def _live_observation_ids(conn: sqlite3.Connection,
                          observation_key: str) -> list[str]:
    """The rows for this key that nothing has superseded.

    The one read P4 does not publish. See the module docstring: `Observation` carries
    neither the id nor the supersession columns, so the current-row rule cannot be
    expressed with the published readers alone.
    """
    return [row["observation_id"] for row in conn.execute(
        "SELECT observation_id FROM evidence "
        "WHERE observation_key = ? AND superseded_by IS NULL ORDER BY rowid",
        (observation_key,))]


def current_observation(conn: sqlite3.Connection,
                        observation_key: str) -> Observation:
    """The one live row for a key, or a refusal."""
    candidates = observations_by_key(conn, observation_key)
    if not candidates:
        raise UnresolvableSpan(
            f"no observation carries key {observation_key!r}. P4's citation handle is "
            "the content-addressed `observation_key`, not the per-row "
            "`observation_id`, which dies on extractor upgrade (M14)")
    live = _live_observation_ids(conn, observation_key)
    if not live:
        raise AmbiguousObservationKey(
            f"key {observation_key!r} has {len(candidates)} rows and every one is "
            "superseded; the chain has no head, so there is no current text to release")
    if len(live) > 1:
        raise AmbiguousObservationKey(
            f"key {observation_key!r} has {len(live)} live rows. P4 returns a list "
            "because two extractor versions carry one key (MINOR 8); the supersession "
            "chain is what makes it single-valued, and picking one of two would "
            "release text an upgrade may already have retracted")
    return get_observation(conn, live[0])


def materialise(conn: sqlite3.Connection, item) -> Materialised:
    """Resolve one requested item against local storage.

    `item` is Task 7's `Excerpt` or `RedactedIdentifier`: it needs an
    `observation_key` and a `span` of `TextSpan | None`, and nothing else is read.
    """
    observation = current_observation(conn, item.observation_key)
    location = observation.location
    address = span_address(location)  # refuses a region (C3) and a time span
    text_span = location.text_span
    if item.span != text_span:
        raise UnresolvableSpan(
            f"the request addresses {item.span!r} and key "
            f"{item.observation_key!r} carries {text_span!r}. SPEC §4 has the gate "
            "resolve the excerpt from local storage, so a caller's coordinates are a "
            "claim; a claim that disagrees with the record is refused, not honoured "
            "and not silently replaced")
    if text_span is None:
        # CR-07. The absence of a span does not make a value a bounded one. §2.3's
        # cell and §2.8's EXIF field have no unit for a span to cover -- but
        # `extractors/structured_text.py` emits a whole text document as a span-less
        # `body` observation at the EMPTY container path, which is precisely where
        # that run's one `text_units` row stands, and its `raw_value` is every
        # character of the document. Which of the two shapes this is cannot be read
        # off the missing span; it is read off the unit at the observation's OWN
        # path, and this module is the only one that may ask P4 for it.
        #
        # `>=` rather than `==`, mirroring `items.is_whole_document`'s span rule: a
        # stored unit may be truncated (`TextUnit.truncated`) while the observation
        # carries the untruncated value, and a value at least as long as its unit is
        # not a short excerpt of that unit under either reading. A SHORTER value is
        # a bounded one and keeps `unit_length = None` -- so a span-less field that
        # happens to sit at a path a unit also occupies is still released.
        value = observation.raw_value
        unit = unit_for_observation(conn, observation)
        unit_length = (unit.length
                       if unit is not None and len(value) >= unit.length else None)
    else:
        unit = unit_for_observation(conn, observation)
        if unit is None:
            raise UnresolvableSpan(
                f"{address} has a text span and no text unit at "
                f"{location.container_path!r} in run {observation.run_id!r}; there is "
                "nothing to take a substring of and the whole file is not a fallback")
        try:
            check_span_anchor(observation, unit)
        except SpanAnchorError as error:
            raise UnresolvableSpan(
                f"{address} does not anchor in run {observation.run_id!r}: {error}. "
                "P4's checker raises and never returns a repair, and a gate that "
                "repaired would release text nobody addressed"
            ) from error
        value, unit_length = raw_value_at(unit, text_span), unit.length
    return Materialised(
        observation_key=item.observation_key, span=address, value=value,
        zone=location.zone, context_before=observation.context_before,
        context_after=observation.context_after,
        context_truncated=observation.context_truncated, unit_length=unit_length)
