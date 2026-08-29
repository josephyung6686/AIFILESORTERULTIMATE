# src/evidence_shape/observation.py
"""Record 1 -- the observation. §2.8's field list, in §2.8's order.

The table name is the design's (§3.12: "**evidence** -- stores raw observations from
extractors, including the source, location, surrounding text, extractor version, and
content hash"). §2.8 says "At minimum, every observation should contain...", which is
what licenses the additions; each traces to a section that requires the information
be preserved.

Two field sets, because a value and a row are different things. `Observation` is what
an extractor emits (eighteen fields). The stored row adds `observation_id` and P1's
three supersede columns, which a later run sets and the emitting extractor does not.

`observation_key` deliberately EXCLUDES `extractor_version`: §8.5 requires the replay
harness to compare a new extractor version against a prior result for the same
content, and identity that included the version would make every row a false diff
(MINOR 8). It is the citation handle every consumer cites -- never `observation_id`,
which is per-row and dies on extractor upgrade while §8.7 requires a negative example
recorded today to still resolve afterwards (M14).
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from database_agent.supersede import SUPERSEDE_COLUMNS

from database_agent.identity import is_content_hash
from evidence_shape.canonical import sha256_of
from evidence_shape.location import Location
from evidence_shape.locator import (
    location_from_mapping, location_to_mapping, serialize_locator,
)
from evidence_shape.vocabulary import (
    EXTRACTOR_RELIABILITY_STATES, SIGNAL_TIERS, SOURCE_TYPES, check,
)

#: §2.8's own eleven lines, verbatim, kept so the counting stays checkable (MINOR 1).
SECTION_2_8_LINES: tuple[str, ...] = (
    "File identifier", "Content hash", "Extractor name and version", "Source type",
    "Raw value", "Normalized candidate value", "Location", "Surrounding context",
    "Occurrence count", "Observation time", "Reliability state",
)

#: Those eleven lines as field names. "Extractor name and version" is two;
#: "Surrounding context" is `context_before` + `context_after` (M5).
SECTION_2_8_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version", "source_type",
    "raw_value", "normalized_value", "location", "context_before", "context_after",
    "occurrence_count", "observed_at", "reliability",
)

#: Required elsewhere in the design, and marked ✚ in the SPEC. `context_truncated` is
#: §8.6's (never truncate silently); `run_id` is D5's; `confidence` is §2.7's;
#: `signal_tier` is §2.6's (M2); the three supersede columns are §8.2's (M1).
ADDED_FIELDS: tuple[str, ...] = (
    "observation_id", "observation_key", "context_truncated", "run_id", "confidence",
    "signal_tier", *SUPERSEDE_COLUMNS,
)

#: What an extractor emits, in the SPEC's display order.
OBSERVATION_FIELDS: tuple[str, ...] = (
    "observation_key",
    "file_id", "content_hash", "extractor_name", "extractor_version", "source_type",
    "raw_value", "normalized_value", "location", "context_before", "context_after",
    "context_truncated", "occurrence_count", "observed_at", "reliability",
    "run_id", "confidence", "signal_tier",
)

#: What the table holds. The store owns the four that are not emitted.
OBSERVATION_ROW_FIELDS: tuple[str, ...] = (
    ("observation_id",) + OBSERVATION_FIELDS + SUPERSEDE_COLUMNS
)

#: Nullable only where the SPEC states it (conformance rule 1).
NULLABLE_FIELDS = frozenset(
    {"normalized_value", "context_before", "context_after", "confidence", "signal_tier"})

#: The fields that carry no meaning empty, and the counterpart to `NULLABLE_FIELDS`.
#: Four of them are `observation_key`'s and rule 8's inputs, so an empty one is a
#: citation handle that addresses nothing; `run_id` is the row's own run.
#:
#: PUBLISHED, with `check_non_empty` below, because the extractor that BUILDS an
#: observation and the record that STORES one must refuse the same values. P5's
#: builder took an empty `raw_value` happily and the refusal then arrived at write
#: time, deep in a scan -- and a rule restated in the consumer to fix that is how one
#: concept ends up with two answers, which is the defect this project has paid for
#: most often. One definition, two callers.
NON_EMPTY_FIELDS: tuple[str, ...] = (
    "file_id", "content_hash", "extractor_name", "extractor_version", "raw_value",
    "observed_at", "run_id",
)


class MalformedObservation(ValueError):
    """A non-conforming observation. P4 fails it rather than coercing it."""


def check_non_empty(value, *, name: str):
    """Presence, or a rejection. No stripping, no defaulting, no coercion.

    Shaped like `vocabulary.check`: it raises on the way through and returns the
    value, so a caller reads as the check it is performing.
    """
    if not isinstance(value, str) or not value:
        raise MalformedObservation(f"{name} is a non-empty string, not {value!r}")
    return value


def observation_key(*, content_hash: str, extractor_name: str, locator: str,
                    raw_value: str) -> str:
    """`sha256(content_hash ‖ extractor_name ‖ locator ‖ raw_value)`, injectively.

    `extractor_version` is absent on purpose: §8.5's replay diff compares a new
    extractor version against a prior result for the same content, and a key that
    carried the version would leave nothing to diff against (MINOR 8). Version
    differences are visible in the rows, not in the key.
    """
    return sha256_of(content_hash, extractor_name, locator, raw_value)


#: The property below needs the function while the class body shadows the name.
_key = observation_key


@dataclass(frozen=True, slots=True)
class Observation:
    """One located reading of one value in one file version."""

    file_id: str
    content_hash: str
    extractor_name: str
    extractor_version: str
    source_type: str
    raw_value: str
    location: Location
    occurrence_count: int
    observed_at: str
    reliability: str
    run_id: str
    normalized_value: str | None = None
    context_before: str | None = None
    context_after: str | None = None
    context_truncated: bool = False
    confidence: float | None = None
    signal_tier: int | None = None

    def __post_init__(self) -> None:
        for name in NON_EMPTY_FIELDS:
            check_non_empty(getattr(self, name), name=name)
        # R1's identity, in P1's spelling and no other. `observation_key` hashes
        # `content_hash` first, so one file under two spellings is two citation
        # handles and §3.4's cache misses on a file it already extracted. The
        # predicate is P1's; P4 does not restate "64 lowercase hex".
        if not is_content_hash(self.content_hash):
            raise MalformedObservation(
                f"content_hash is the digest P1 stored (R1), not {self.content_hash!r}"
            )
        check(self.source_type, SOURCE_TYPES, name="source_type")
        # D11: an extractor writes two of §3.13's six. The other four are fact-layer
        # outcomes (§3.5) and §2.8 forbids treating model output as proof.
        check(self.reliability, EXTRACTOR_RELIABILITY_STATES, name="reliability")
        if not isinstance(self.location, Location):
            raise MalformedObservation(
                "location is the structured record (D1), never a per-format string")
        for name in ("normalized_value", "context_before", "context_after"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise MalformedObservation(f"{name} is a string or None")
        if type(self.context_truncated) is not bool:
            raise MalformedObservation(
                "context_truncated is a bool and is never absent (§8.6)")
        if type(self.occurrence_count) is not int or self.occurrence_count < 1:
            raise MalformedObservation(
                "occurrence_count >= 1 (rule 7): an observation records presence, and "
                "absence lives on the run record or nowhere (§2.6)")
        if self.confidence is not None and type(self.confidence) not in (int, float):
            raise MalformedObservation(
                "confidence is the extractor's own number, or None. §2.7 names no "
                "scale and §3.13 says it is not comparable across extractors, so P4 "
                "stores it and asserts no range")
        if self.signal_tier is not None:
            check(self.signal_tier, SIGNAL_TIERS, name="signal_tier")

    @property
    def locator(self) -> str:
        """The canonical string form of `location`, and one input to the key."""
        return serialize_locator(self.location)

    @property
    def observation_key(self) -> str:
        """M14's citation handle."""
        return _key(content_hash=self.content_hash, extractor_name=self.extractor_name,
                    locator=self.locator, raw_value=self.raw_value)

    @property
    def zone(self) -> str:
        """§2.2's "document zone", which §3.7 weights and D10 collapses on."""
        return self.location.zone

    def to_mapping(self) -> dict[str, object]:
        mapping = {name: getattr(self, name) for name in OBSERVATION_FIELDS
                   if name not in ("location", "observation_key")}
        mapping["location"] = location_to_mapping(self.location)
        mapping["observation_key"] = self.observation_key
        return {name: mapping[name] for name in OBSERVATION_FIELDS}


def observation_from_mapping(mapping: Mapping[str, object]) -> Observation:
    """Build from a stored row or a fixture. Rejects; never fills a gap in."""
    missing = [name for name in OBSERVATION_FIELDS
               if name != "observation_key" and name not in mapping]
    if missing:
        raise MalformedObservation(
            f"missing fields: {missing}. §2.8's "
            '"Surrounding context" is three fields here -- context_before, '
            "context_after and context_truncated -- not one (M5)")
    unknown = sorted(set(mapping) - set(OBSERVATION_ROW_FIELDS))
    if unknown:
        raise MalformedObservation(
            f"{unknown} are not fields of the observation record. §2.8: extraction "
            "does not create a final folder path, invent domains, merge all files "
            "that share one string, or treat model output as proof")
    location = mapping["location"]
    observation = Observation(
        file_id=mapping["file_id"],
        content_hash=mapping["content_hash"],
        extractor_name=mapping["extractor_name"],
        extractor_version=mapping["extractor_version"],
        source_type=mapping["source_type"],
        raw_value=mapping["raw_value"],
        location=location if isinstance(location, Location)
        else location_from_mapping(location),
        occurrence_count=mapping["occurrence_count"],
        observed_at=mapping["observed_at"],
        reliability=mapping["reliability"],
        run_id=mapping["run_id"],
        normalized_value=mapping["normalized_value"],
        context_before=mapping["context_before"],
        context_after=mapping["context_after"],
        context_truncated=mapping["context_truncated"],
        confidence=mapping["confidence"],
        signal_tier=mapping["signal_tier"],
    )
    stated = mapping.get("observation_key")
    if stated is not None and stated != observation.observation_key:
        raise MalformedObservation(
            f"observation_key {stated!r} is not the key of this observation; the "
            "handle §8.7 depends on must be derivable from the row it names")
    return observation


def collapse_key(observation: Observation) -> tuple[str, str, str]:
    """D10's three: (run, exact raw value, zone).

    Published so six extractors collapse the same way. P4 enforces no uniqueness on
    it -- the SPEC's twelve conformance rules do not include one, and adding a
    thirteenth would be P4 legislating P5's traversal.
    """
    return (observation.run_id, observation.raw_value, observation.location.zone)
