# src/facts/discount.py
"""§2.2/§2.3's producer, creator and author discount, and §3.8's role bound (M4).

**Two tiers, and they are not interchangeable.** Getting them the other way round is
the mistake this module is written against.

* **Suppression (§2.2).** A generic TOOL string produces **no fact in any field**,
  `authored_by` included, and one `unresolved` row with
  `reason = discounted_tool_metadata`. §2.2: "a value such as python-docx,
  Mozilla/5.0, or a browser-generated producer string should not be mistaken for
  meaningful content." Not-meaningful is not weak: a tool name is a true fact about
  the software and no evidence about the document, so there is nothing for a
  `possible` fact to be weak about, and letting one into §3.7's ranking starts a
  contest §2.2 says should never start.

* **Demotion (§2.3, §3.8).** Any other producer/creator/author value is KEPT. §2.3:
  such metadata "should remain supporting information only, because it may identify a
  prior editor, a document template, or a script rather than the meaningful subject or
  purpose of the file." It may populate `authored_by` and no other field, it is never
  destination-eligible (§3.8), and it gets NO `unresolved` row -- an abstention that
  did not happen must not be recorded as one (B7).

**Why the discount is P6's (M4).** There is no marker on the observation. P4 emits
fixture 6 with `reliability = "direct"` because "direct describes the slot, not the
value's usefulness"; P5 emits the value verbatim with no flag. Nobody upstream owned
this and both sections require it, so it is here, keyed on exactly what P4 publishes:
`location.zone == metadata` plus the `field`-kind segment's label -- catalogue 01's
`match_field` clause word for word.

**Everything catalogue-shaped is injected.** `tool_producer_strings` is a collection
of compiled predicates, one per catalogue entry, because the catalogue declares three
`match_kind`s whose semantics (the boundary-character set, the version-tail rule) live
in its `boundary_rule` field as prose with no machine-readable form; compiling belongs
with the loader, so a catalogue v2.0 needs no change here. `metadata_property_names`
arrives FLAT: the catalogue groups the names by format family, and consuming that
mapping here would be a lookup keyed by format -- the branching §2.8 exists to prevent.

The one piece of matching that IS P6's, because the catalogue assigns it here in
writing: "Compare against the raw value with Unicode NFC applied and leading/trailing
whitespace stripped, for comparison only ... this normalization exists inside P6's
matcher and never writes back."

**Ordering.** `screen_metadata` returns survivors, and the survivors are what any
ranking sees. §3.7 decides by score and margin, so a suppressed value that reaches it
can win outright, and one that loses still moves the margin and can push a good
candidate under it -- an empty field that looks like §3.7 working and is in fact
§2.2's own example beating it.
"""
from __future__ import annotations

import sqlite3
import unicodedata
from typing import Callable, Collection, Iterable

from evidence_shape.canonical import canonical_json as _canonical_json
from evidence_shape.observation import Observation
from evidence_shape.vocabulary import ANALYSIS_TIERS as _ANALYSIS_TIERS
from evidence_shape.vocabulary import ZONES as _ZONES
from evidence_shape.vocabulary import check as _check

from facts.cache import fact_cache_key as _fact_cache_key
from facts.evidence import analysis_tier_for_observation as _tier_of
from facts.evidence import cite as _cite
from facts.unresolved import ATTEMPTED_PRODUCERS as _ATTEMPTED_PRODUCERS
from facts.unresolved import write_unresolved as _write_unresolved

#: The three outcomes, published once. `suppress` and `demote` are §2.2's and §2.3's
#: two tiers; `not_metadata` is "this observation is not in the slots the discount
#: reads", which is neither a refusal nor a permission.
DISCOUNT_OUTCOMES: tuple[str, str, str] = ("suppress", "demote", "not_metadata")

#: The fields a DEMOTED metadata value may fill. Done-means 22 is literal: "a human
#: author name in the same slot may populate `authored_by` and no other field". §3.8
#: names four role fields and Task 2 carries all four with
#: `destination_eligible = FALSE`; this is the narrower set, because `target_school`
#: and `client` are targets rather than authorship and no Done-means reaches
#: `our_firm`. Naming §3.8's `target_school` here would also pre-empt Task 2's
#: decision about whether that concept's key is `target_school` or §3.11's
#: `target_university` -- one concept, one key, and it is not this module's to pick.
AUTHORSHIP_FIELDS: tuple[str, ...] = ("authored_by",)

#: P4's zone the discount reads. Validated against P4's published vocabulary at
#: import, so a rename upstream is a load error rather than a rule that silently
#: stops firing.
_METADATA_ZONE: str = _check("metadata", _ZONES, name="zone")

_SUPPRESS, _DEMOTE, _NOT_METADATA = DISCOUNT_OUTCOMES


def is_discount_target(observation: Observation, *,
                       metadata_property_names: Collection[str]) -> bool:
    """Catalogue 01's `match_field`: zone `metadata` plus a listed property name.

    "A slot not on this list is not a discount target." An observation with no
    `field`-kind segment has no slot name and is therefore not one either -- P4's
    `container_path` is a tuple and is routinely empty.
    """
    if observation.zone != _METADATA_ZONE:
        return False
    return _slot_name(observation) in metadata_property_names


def discount(observation: Observation, *,
             tool_producer_strings: Collection[Callable[[str], bool]],
             metadata_property_names: Collection[str]) -> str:
    """§2.2/§2.3's two tiers. One of `DISCOUNT_OUTCOMES`."""
    if not is_discount_target(observation,
                              metadata_property_names=metadata_property_names):
        return _NOT_METADATA
    candidate = _for_comparison(observation.raw_value)
    if any(matches(candidate) for matches in tool_producer_strings):
        return _SUPPRESS
    return _DEMOTE


def field_permitted(observation: Observation, field_key: str, *,
                    tool_producer_strings: Collection[Callable[[str], bool]],
                    metadata_property_names: Collection[str]) -> bool:
    """May this observation support a fact in this field?

    §3.8, in one predicate: a suppressed value supports nothing, a demoted value
    supports an authorship role and "no other field" (Done-means 22), and an
    observation the discount does not read is not this module's to restrict.
    """
    outcome = discount(observation, tool_producer_strings=tool_producer_strings,
                       metadata_property_names=metadata_property_names)
    if outcome == _SUPPRESS:
        return False
    if outcome == _DEMOTE:
        return field_key in AUTHORSHIP_FIELDS
    return True


def screen_metadata(conn: sqlite3.Connection, *, file_id: str, content_hash: str,
                    observations: Iterable[Observation],
                    tool_producer_strings: Collection[Callable[[str], bool]],
                    metadata_property_names: Collection[str],
                    ) -> tuple[Observation, ...]:
    """Drop the suppressed observations, record the refusal, keep everything else.

    Returns the survivors in the order they were given -- Task 7's read is already a
    total order keyed on `observation_key`, and reordering here would change every
    downstream tie for a reason that has nothing to do with the corpus (§8.5).

    ONE `unresolved` row is written for the whole version, citing every suppressed
    observation: a DOCX commonly writes the same generator into `creator` and
    `lastModifiedBy`, and two rows would double-count one refusal. The row names
    `AUTHORSHIP_FIELDS[0]`, which is the field the value would otherwise have filled
    -- Done-means 22's "no fact in any field, including `authored_by`" recorded as the
    one field there was to refuse.
    """
    observations = tuple(observations)
    suppressed = [one for one in observations
                  if discount(one, tool_producer_strings=tool_producer_strings,
                              metadata_property_names=metadata_property_names)
                  == _SUPPRESS]
    if suppressed:
        _write_unresolved(
            conn, file_id=file_id, content_hash=content_hash,
            field_key=AUTHORSHIP_FIELDS[0], reason="discounted_tool_metadata",
            attempted_producers=(_ATTEMPTED_PRODUCERS[0],),
            evidence_refs=tuple(sorted({_cite(one) for one in suppressed})),
            cache_key=_cache_key(conn, content_hash=content_hash,
                                 observations=suppressed))
    dropped = {id(one) for one in suppressed}
    return tuple(one for one in observations if id(one) not in dropped)


def _slot_name(observation: Observation) -> str:
    """The `field`-kind segment's label, or the empty string.

    Catalogue 01 names this read: "the `field`-kind segment's label is one of the
    property names below". Task 8 reads the whole `locator` instead, because its
    predicates are the caller's and a locator needs no extraction rule; the two reads
    differ because their sources ask for different things.
    """
    for segment in observation.location.container_path:
        if segment.kind == "field" and segment.label:
            return segment.label
    return ""


def _for_comparison(raw_value: str) -> str:
    """Catalogue 01's `normalization_for_matching`, and nothing else.

    "Compare against the raw value with Unicode NFC applied and leading/trailing
    whitespace stripped, for comparison only." Never written back: P4's
    `evidence_never_overwritten` trigger would refuse it, and §3.2 requires the
    original evidence to survive the conclusion built from it.
    """
    return unicodedata.normalize("NFC", raw_value).strip()


def _cache_key(conn: sqlite3.Connection, *, content_hash: str,
               observations: Iterable[Observation]) -> str:
    """§3.4's five parts for a record built from several observations.

    Identical to `facts.direct._cache_key`, `facts.families` and `facts.session`: the
    versions are the canonical JSON of the sorted distinct (name, version) pairs, and
    the tier is the last present in `ANALYSIS_TIERS` order, so a record that cited an
    OCR reading lands outside the slot the native pass computed under. See Contract
    ambiguities -- the reconciliation belongs in `facts.cache`, which is Task 6's.
    """
    observations = tuple(observations)
    pairs = sorted({(one.extractor_name, one.extractor_version)
                    for one in observations})
    tiers = {_tier_of(conn, one) for one in observations}
    tier = max(tiers, key=_ANALYSIS_TIERS.index) if tiers else _ANALYSIS_TIERS[0]
    return _fact_cache_key(
        content_hash=content_hash,
        extractor_version=_canonical_json([list(pair) for pair in pairs]),
        analysis_tier=tier, model_identifier=None, prompt_fingerprint=None)
