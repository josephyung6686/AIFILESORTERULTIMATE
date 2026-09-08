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
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.store import (
    get_observation, observations_by_key, unit_for_observation,
    unit_holds_a_line_break,
)
from evidence_shape.location import Location, TextSpan
from evidence_shape.locator import location_from_mapping
from evidence_shape.observation import Observation
from evidence_shape.text_units import SpanAnchorError, check_span_anchor, raw_value_at

from privacy.redaction import span_address
from privacy.release import (
    released_whole_heading_unit, released_whole_line_unit,
)

#: The one zone a `items.Filename` may resolve through, and the zone
#: `extractors/filesystem.py` writes the person's own name for the file into. Named
#: here rather than in the gate because this module is the only one that reads P4.
FILENAME_ZONE: str = "filename"

#: §2.9's format family for P3's section 1.2 record, and the SECOND half of the
#: address, without which the first half is not unique. Measured on the owner's 199
#: files: `image.metadata` also writes a `filename`-zone observation -- the
#: camera-or-screenshot NAME PATTERN it matched, span-less and shorter than the name
#: -- so one of the 199 carried two live rows in the zone and "the filename" had two
#: candidates. They are not two readings of one value: one is the name, the other is
#: a signal derived from it, and `source_type` is the field that already tells them
#: apart. A vocabulary member, checked against `SOURCE_TYPES` by
#: `test_p7_resolve.py`, never a string this module invented.
FILESYSTEM_SOURCE_TYPE: str = "filesystem"

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


def current_location(conn: sqlite3.Connection, observation_key: str, *,
                     within_file_ids: Sequence[str] | None = None,
                     ) -> CurrentLocation:
    """Return the sole live location for a key without selecting content.

    Consent needs a canonical address before it may read protected text. Keep this
    query explicit: adding ``raw_value`` or context columns here would move content
    access in front of the consent decision.

    **`within_file_ids` is which FILE is being acted for, and without it a duplicate
    has no answer.** `observation_key` is CONTENT-addressed, so two byte-identical
    files carry the same key at the same location and both rows are live -- neither
    supersedes the other, because neither is a newer reading of the other. Asked
    "where does this key live?" across a corpus, a duplicated document has two
    honest answers and this function refused. Measured on 34 of the owner's real
    files: three duplicate pairs poisoned 28 of 1,428 keys and `--enable-cloud`
    exited with a traceback and no plan, while `report.pdf` beside `report (1).pdf`
    is the ordinary contents of a downloads folder rather than a corner case.

    The caller always knew. `gate._consent_reference` takes `target_file_ids` and
    checks membership on the line after this call, so the question it needed
    answered was never "where does this key live?" but "where does it live in THIS
    file?" -- and only the unscoped spelling of that question is unanswerable.

    **This is a narrowing, not a relaxation, and the distinction is the whole
    safety argument.** The scope can only remove candidate rows. One live row still
    means one canonical address; two live rows still refuse, whether they are two
    files the caller named together or P4's retraction shape inside a single file --
    and releasing the wrong one of THOSE is the silent release of retracted text
    that the refusal exists to prevent. Nothing is picked, guessed or preferred.
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
    if within_file_ids is not None:
        wanted = frozenset(within_file_ids)
        scoped = [row for row in live if row["file_id"] in wanted]
        # An empty scope is NOT this function's refusal to make. `_consent_reference`
        # answers "belongs to a file outside the request" with `UnresolvableSpan` and
        # names the owning file in it; narrowing to nothing here would replace that
        # sentence with a less informative one.
        live = scoped if scoped else live
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
    #: `104` R-135. Whether this resolution IS that row's exemption: a span covering
    #: the whole of a unit that is a heading. Decided HERE because this is the last
    #: place P4's `Location` exists -- `span` is its serialisation and `ReleasedItem`
    #: keeps only that -- and a consumer that parsed the string back would be
    #: re-deriving a structural fact from its own printing. Defaulted so a caller
    #: building a `Materialised` by hand states what it means rather than being
    #: required to compute it.
    whole_heading_unit: bool = False
    #: `104` R-152, decided here for the reason above and carried the same way: a span
    #: covering the whole of a unit that holds no line break. Kept apart from the
    #: heading answer because the two are counted apart -- the counts are what both
    #: rulings report INSTEAD of a length bound, and one flag would report a heading
    #: and a line as one exposure.
    whole_line_unit: bool = False


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


def current_observation(conn: sqlite3.Connection, observation_key: str, *,
                        within_file_ids: Sequence[str] | None = None,
                        ) -> Observation:
    """The one live row for a key, or a refusal.

    `within_file_ids` narrows to the files the caller is acting for, for the reason
    `current_location` gives above: a document a person owns twice carries one
    content-addressed key in two live rows, and neither supersedes the other.

    **Scoping is safe HERE, where text is released, and the key itself is why.**
    `observation_key` is `sha256(content_hash | extractor_name | locator |
    raw_value)`, so two rows sharing a key hold a byte-identical `raw_value`, read by
    the same extractor at the same locator out of identical content. There is no
    wrong one to pick: either releases the same characters. The refusal below argues
    the RETRACTION case -- "picking one of two would release text an upgrade may
    already have retracted" -- and that case is supersession, a DIFFERENT reading of
    the same place, which `_live_observation_ids` has already excluded. Two live rows
    left inside one file still refuse, and the test says so.
    """
    candidates = observations_by_key(conn, observation_key)
    if not candidates:
        raise UnresolvableSpan(
            f"no observation carries key {observation_key!r}. P4's citation handle is "
            "the content-addressed `observation_key`, not the per-row "
            "`observation_id`, which dies on extractor upgrade (M14)")
    live = _live_observation_ids(conn, observation_key)
    if within_file_ids is not None and live:
        wanted = frozenset(within_file_ids)
        scoped = [oid for oid in live
                  if get_observation(conn, oid).file_id in wanted]
        live = scoped if scoped else live
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


@dataclass(frozen=True, slots=True)
class _NameAddress:
    """The two fields `materialise` reads, derived from a `file_id`.

    `items.Filename` carries a `file_id` and no address, because SPEC §6 says a
    request carries references and the gate is what resolves one. `materialise`
    reads `observation_key` and `span` and its docstring says it reads nothing
    else, so the derivation ends in this shape rather than in a second resolver.
    """

    observation_key: str
    span: TextSpan | None


def filename_address(conn: sqlite3.Connection, file_id: str) -> _NameAddress:
    """Where this file's own name lives, or a refusal. NO CONTENT IS SELECTED.

    `extractors/filesystem.py` emits exactly one `zone="filename"` observation per
    indexed file version -- P3's section 1.2 record made citable -- and that
    observation is the only place a released filename may come from. `files.filename`
    is the same characters and is deliberately NOT read here: that module's opening
    paragraph refuses a second computation of a P3 value because "the two would
    drift", and a released value the model cites has to resolve back through P4 for
    `00`:62's validator to check the citation at all.

    **THE ZONE IS NOT THE WHOLE ADDRESS**, and one real file is why. `image.py` also
    writes into `zone="filename"`: the camera or screenshot name PATTERN it matched,
    which is a signal derived from the name and not the name. Filtering on the zone
    alone made that file ambiguous and unreleasable, and picking the longer of the
    two would have been the guess this module does not make. The filter is the zone
    AND §2.9's `filesystem` source family, which is what "P3's section 1.2 record,
    re-emitted" means in P4's own vocabulary.

    **Scoped to the file and not to its version, and the reason is the key.** An
    `observation_key` is `sha256(content_hash | extractor | locator | raw_value)`, so
    a file whose bytes changed carries a DIFFERENT key for the same name -- and P4's
    supersession chain is what retires the old row. Filtering on `content_hash` here
    would look stricter and buy nothing the liveness filter does not already buy,
    while adding a way for the gate's own reading of "which version" to disagree with
    P4's.

    **Zero refuses and two refuses**, on this module's standing rule: absent means
    refuse, never guess. Zero is a file the filesystem extractor never ran over, and
    the whole name is not something to reconstruct from a column. Two live rows is
    the retraction case `current_observation` argues at length -- picking one of two
    would release a name a later reading may already have replaced.
    """
    keys: list[str] = []
    spans: dict[str, TextSpan | None] = {}
    for row in conn.execute(
            "SELECT observation_key, location FROM evidence "
            "WHERE file_id = ? AND superseded_by IS NULL AND source_type = ? "
            "AND json_extract(location, '$.zone') = ? ORDER BY rowid",
            (file_id, FILESYSTEM_SOURCE_TYPE, FILENAME_ZONE)):
        key = row["observation_key"]
        if key in spans:
            # The same content-addressed key twice is one reading recorded twice,
            # not two readings: identical bytes at an identical locator. It is the
            # DISTINCT key that has to be single-valued.
            continue
        keys.append(key)
        spans[key] = location_from_mapping(json.loads(row["location"])).text_span
    if not keys:
        raise UnresolvableSpan(
            f"file {file_id!r} carries no live {FILENAME_ZONE!r}-zone "
            f"{FILESYSTEM_SOURCE_TYPE!r} observation, so there is no address for its "
            f"name. `extractors/filesystem.py` writes one for every indexed file; a "
            f"file that has none was never indexed by it, and `files.filename` is "
            f"not a fallback -- releasing a value the model could not then cite is "
            f"what §7.7's flagged kind exists to avoid")
    if len(keys) > 1:
        raise AmbiguousObservationKey(
            f"file {file_id!r} has {len(keys)} live {FILENAME_ZONE!r}-zone "
            f"{FILESYSTEM_SOURCE_TYPE!r} observations; no unique current name "
            f"exists, and picking one of two would release a name a later reading "
            f"may already have retracted")
    return _NameAddress(observation_key=keys[0], span=spans[keys[0]])


def materialise_filename(conn: sqlite3.Connection, file_id: str) -> Materialised:
    """`items.Filename` -> the person's own name for the file, through P4.

    Two steps and no third: find the address, then take the ordinary materialiser
    down it. The value, the span, the zone and the unit length are all P4's, so a
    released filename is the same kind of citable thing an excerpt is.
    """
    return materialise(conn, filename_address(conn, file_id),
                       within_file_ids=(file_id,))


def materialise(conn: sqlite3.Connection, item, *,
                within_file_ids: Sequence[str] | None = None) -> Materialised:
    """Resolve one requested item against local storage.

    `item` is Task 7's `Excerpt` or `RedactedIdentifier`: it needs an
    `observation_key` and a `span` of `TextSpan | None`, and nothing else is read.
    `_NameAddress` above is the third shape, and it is that pair and not a fourth
    reader: `materialise_filename` derives it from a `file_id` and comes back here.
    """
    observation = current_observation(conn, item.observation_key,
                                      within_file_ids=within_file_ids)
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
        context_truncated=observation.context_truncated, unit_length=unit_length,
        # `104` R-135, asked of the LOCATION and not of its printing. This is the same
        # predicate `model_facts.releasable_observations` and
        # `model_placement.releasable_excerpts` admit by, so what the gate releases
        # under the exemption and what `GroundingReport` reports as exposure are one
        # condition evaluated on one object.
        whole_heading_unit=released_whole_heading_unit(location, unit_length),
        # `104` R-152's twin of the line above, and the reason the newline is read in
        # SQL: `unit_holds_a_line_break` asks P4 whether the unit has a second line
        # without bringing its text back, so the document does not cross into `privacy`
        # in order to be declined. The gate cannot ask this itself -- by the time it
        # decides, the `Location` is a serialised address -- which is why the answer is
        # settled here and travels on `ReleasedItem`.
        whole_line_unit=released_whole_line_unit(
            location, unit_length,
            unit_holds_line_break=unit_holds_a_line_break(conn, observation)))
