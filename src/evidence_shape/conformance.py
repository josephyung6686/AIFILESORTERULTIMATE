# src/evidence_shape/conformance.py
"""The conformance validator. Twelve rules; it FAILS, it does not coerce.

SPEC, Conformance: "A validator, shipped with P4, rejects a non-conforming
observation. Six extractor authors run it as their gate; P6, P7 and P8 may assume it
passed."

It reports every violation before raising, because a gate that stops at the first
problem makes an extractor author fix one thing per run.

Rule 11 is checked in the half that is structural. §2.6's hierarchy is entirely about
images, so a non-null `signal_tier` implies `source_type = "image"` and that is
checkable here. WHICH field inside an image belongs to which tier is P5's catalogue
(SPEC, Deferred: "P4 fixes the shape, not the catalogue"), and P4 authors no list of
EXIF names -- enumerating one would be inventing a gazetteer.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.location import Location, MalformedLocation
from evidence_shape.locator import (
    MalformedLocator, addressing, location_from_mapping, parse_locator,
    serialize_locator,
)
from evidence_shape.observation import (
    MalformedObservation, NULLABLE_FIELDS, OBSERVATION_FIELDS, OBSERVATION_ROW_FIELDS,
    Observation, observation_from_mapping,
)
from evidence_shape.vocabulary import (
    EXTRACTOR_RELIABILITY_STATES, SEGMENT_KINDS, SIGNAL_TIERS, SOURCE_TYPES, ZONES,
)
from evidence_shape.locator import serialize_container_path
from evidence_shape.runs import ExtractionRun, MalformedRun, run_from_mapping
from evidence_shape.text_units import SpanAnchorError, TextUnit, check_span_anchor
from evidence_shape.vocabulary import NotInVocabulary, ZERO_OBSERVATION_COMPLETENESS

#: The SPEC's twelve, numbered as the SPEC numbers them. Rules 5, 9 and 10 are
#: cross-record and are checked by `conformance.check_run`; rule 8 needs two runs and
#: is checked by `determinism.assert_identical_observation_sets`.
CONFORMANCE_RULES: Mapping[int, str] = MappingProxyType({
    1: "Every §2.8 field present -- with context_before, context_after and "
       "context_truncated as three fields, not one (M5); nullable only where stated.",
    2: "zone, all kinds, source_type, reliability, completeness drawn from the "
       "closed vocabularies.",
    3: "reliability in {direct, possible} on any row written by an extractor.",
    4: "locator round-trips: serialize -> parse -> structurally equal.",
    5: "RAW-1 holds wherever text_span is non-null. Checked by check_run.",
    6: "Exactly one file_id; no destination, domain, field-name, group, node, "
       "template or plan reference.",
    7: "occurrence_count >= 1.",
    8: "Same content hash + same extractor version + same config fingerprint => "
       "byte-identical observation set. Checked by evidence_shape.determinism.",
    9: "run.completeness present; unsupported, deferred and failed runs carry zero "
       "observations. Checked by check_run.",
    10: "Every observation with a non-null text_span has a text_units row on the "
        "same run_id whose container_path equals the observation's, and RAW-1 holds "
        "against that row's text. Checked by check_run.",
    11: "signal_tier is null unless the observation is one of §2.6's image-hierarchy "
        "signals; where present it is 1, 2 or 3. P4 checks the structural half -- a "
        "tier implies source_type = image -- and names no EXIF field: which field "
        "belongs to which tier is P5's catalogue.",
    12: "No observation carries an absence, a conflict, or a resolution of a "
        "conflict (§2.6). P4 checks the structural half: the field set is closed, "
        "raw_value is one value and not a list of competing readings, and "
        "occurrence_count >= 1 because a count of zero is an absence. An absence "
        "written INSIDE raw_value as a string is P5's obligation -- detecting it "
        "would need a list of forbidden strings, and P4 authors no such list.",
})

#: §2.6's hierarchy is an image hierarchy. See rule 11 above and the module docstring.
_SIGNAL_TIER_SOURCE_TYPE = "image"


@dataclass(frozen=True, slots=True)
class Violation:
    rule: int
    message: str


class NonConforming(Exception):
    """Raised by `validate_observation` / `validate_run`, carrying every violation."""

    def __init__(self, violations: tuple[Violation, ...]) -> None:
        self.violations = tuple(violations)
        super().__init__("; ".join(
            f"rule {violation.rule}: {violation.message}" for violation in self.violations))


def _one_value(value) -> bool:
    return not isinstance(value, (list, tuple, set, frozenset))


def check_observation(candidate) -> tuple[Violation, ...]:
    """Every violation of the rules an observation can break on its own."""
    violations: list[Violation] = []
    if isinstance(candidate, Observation):
        mapping = candidate.to_mapping()
    elif isinstance(candidate, Mapping):
        mapping = dict(candidate)
    else:
        return (Violation(1, f"an observation is a record or a mapping, not "
                             f"{type(candidate).__name__}"),)

    # Rule 1 -- presence and nullability.
    missing = [name for name in OBSERVATION_FIELDS
               if name != "observation_key" and name not in mapping]
    if missing:
        violations.append(Violation(1, (
            f"missing fields {missing}. §2.8's \"Surrounding context\" is three "
            "fields here -- context_before, context_after, context_truncated -- and "
            "a single-field emission fails this rule (M5)")))
    for name in OBSERVATION_FIELDS:
        if name in mapping and mapping[name] is None and name not in NULLABLE_FIELDS:
            violations.append(Violation(1, f"{name} is not nullable"))

    # Rule 6 -- a closed field set, and exactly one file.
    unknown = sorted(set(mapping) - set(OBSERVATION_ROW_FIELDS))
    if unknown:
        violations.append(Violation(6, (
            f"{unknown} are not fields of the observation record. §2.8: extraction "
            "does not create a final folder path, invent domains, merge all files "
            "that share one string, or treat model output as proof")))
    if "file_id" in mapping and not _one_value(mapping["file_id"]):
        violations.append(Violation(6, (
            "an observation references exactly one file_id; two files sharing a raw "
            "value share nothing structurally, and that link is P6's or P9's")))

    # Rule 12 -- a reading, not a report or a comparison.
    for name in ("raw_value", "location", "normalized_value"):
        if name in mapping and not _one_value(mapping[name]):
            violations.append(Violation(12, (
                f"{name} is one value. §2.6's conflicting signals are two "
                "observations with two signal_tier values, never a third row: an "
                "observation is a reading, not a comparison of readings")))

    # Rule 2 -- the closed vocabularies, checked where they live.
    source_type = mapping.get("source_type")
    if source_type is not None and source_type not in SOURCE_TYPES:
        violations.append(Violation(2, f"source_type={source_type!r} is not one of "
                                       f"§2.9's families {SOURCE_TYPES}"))
    location = mapping.get("location")
    if isinstance(location, Location):
        location_mapping = {"zone": location.zone, "container_path": [
            {"kind": segment.kind} for segment in location.container_path]}
    elif isinstance(location, Mapping):
        location_mapping = location
    else:
        location_mapping = None
        if location is not None and _one_value(location):
            violations.append(Violation(1, "location is the structured record (D1)"))
    if location_mapping is not None:
        zone = location_mapping.get("zone")
        if zone not in ZONES:
            violations.append(Violation(2, f"zone={zone!r} is not one of {ZONES}"))
        for segment in location_mapping.get("container_path") or ():
            kind = segment.get("kind") if isinstance(segment, Mapping) else None
            if kind not in SEGMENT_KINDS:
                violations.append(
                    Violation(2, f"kind={kind!r} is not one of {SEGMENT_KINDS}"))

    # Rule 3 -- what an extractor may write.
    reliability = mapping.get("reliability")
    if reliability is not None and reliability not in EXTRACTOR_RELIABILITY_STATES:
        violations.append(Violation(3, (
            f"reliability={reliability!r}: an extractor may write "
            f"{EXTRACTOR_RELIABILITY_STATES}. validated, llm_supported, "
            "user_confirmed and rejected are fact-layer outcomes (§3.5), and §2.8 "
            "forbids extraction from treating model output as proof")))

    # Rule 7 -- presence, never absence.
    count = mapping.get("occurrence_count")
    if type(count) is not int or count < 1:
        violations.append(Violation(7, (
            f"occurrence_count={count!r}: an observation records presence, and a "
            "count of zero is an absence, which lives on the run record (§2.6)")))

    # Rule 11 -- §2.6's tier, in the half that is structural.
    tier = mapping.get("signal_tier")
    if tier is not None:
        if tier not in SIGNAL_TIERS:
            violations.append(
                Violation(11, f"signal_tier={tier!r} is not one of {SIGNAL_TIERS}"))
        if source_type != _SIGNAL_TIER_SOURCE_TYPE:
            violations.append(Violation(11, (
                f"signal_tier is set on a source_type={source_type!r} observation. "
                "§2.6's hierarchy is an image hierarchy, and the field is null on "
                "every observation outside it")))

    # Rule 4 -- the locator round-trips. Needs a constructed location.
    if location_mapping is not None and not violations:
        try:
            built = (location if isinstance(location, Location)
                     else location_from_mapping(location_mapping))
            serialized = serialize_locator(built)
            # Against `addressing`, not `built`: rule 2 keeps a descriptive label out
            # of the string and the grammar has no term for a bounding box, so those
            # two are deliberately not part of what a round-trip reproduces.
            if parse_locator(serialized) != addressing(built):
                violations.append(Violation(4, (
                    f"locator {serialized!r} does not parse back to the addressing it "
                    "serialized from")))
        except (MalformedLocation, MalformedLocator) as exc:
            violations.append(Violation(4, str(exc)))

    # Anything the record types catch that the rules above did not name.
    if not violations:
        try:
            observation_from_mapping(mapping) if not isinstance(
                candidate, Observation) else None
        except (MalformedObservation, MalformedLocation, MalformedLocator) as exc:
            violations.append(Violation(1, str(exc)))
    return tuple(violations)


def validate_observation(candidate) -> Observation:
    """The extractor's gate. Returns the constructed record, or raises with every
    violation. It never returns a repaired record (Done-means 2)."""
    violations = check_observation(candidate)
    if violations:
        raise NonConforming(violations)
    if isinstance(candidate, Observation):
        return candidate
    return observation_from_mapping(candidate)


def check_run(run, observations=(), text_units=()) -> tuple[Violation, ...]:
    """Rules 9, 10 and 5 -- the three that need a second record -- plus Task 13's
    per-observation rules over every member of the set.

    RAW-1 is decided by `text_units.check_span_anchor` and reported under rule 5, the
    rule that names it. Rule 10 keeps the half that is its own: a unit exists, on this
    run, at this address. One defect is reported once.
    """
    violations: list[Violation] = []
    if isinstance(run, ExtractionRun):
        record = run
    elif isinstance(run, Mapping):
        try:
            record = run_from_mapping(run)
        except (MalformedRun, NotInVocabulary) as exc:
            return (Violation(9, str(exc)),)
    else:
        return (Violation(9, f"a run is a record or a mapping, not "
                             f"{type(run).__name__}"),)

    members = tuple(observations)
    # Rule 9. The SPEC's three, and no others: M3 keeps `unreadable`, `partial` and
    # `metadata_only` carrying the metadata-level rows §2.9's "indexed" means.
    if record.completeness in ZERO_OBSERVATION_COMPLETENESS and members:
        violations.append(Violation(9, (
            f"a {record.completeness!r} run carries zero observations and this one "
            f"carries {len(members)}; what such a run knows is on the run record")))

    index: dict[str, TextUnit] = {}
    for unit in text_units:
        if not isinstance(unit, TextUnit):
            violations.append(Violation(10, f"a text unit is a TextUnit record, not "
                                            f"{type(unit).__name__}"))
            continue
        if unit.run_id != record.run_id:
            violations.append(Violation(10, (
                f"unit {unit.unit_locator!r} belongs to run {unit.run_id!r}, not to "
                f"{record.run_id!r}; text is per run, not per file (§8.2)")))
            continue
        index[unit.unit_locator] = unit

    for position, candidate in enumerate(members):
        own = check_observation(candidate)
        if own:
            violations.extend(
                Violation(violation.rule, f"observation {position}: {violation.message}")
                for violation in own)
            continue
        observation = (candidate if isinstance(candidate, Observation)
                       else observation_from_mapping(candidate))
        if observation.run_id != record.run_id:
            violations.append(Violation(9, (
                f"observation {position} belongs to run {observation.run_id!r}, not "
                f"to {record.run_id!r}; rules 9 and 10 are statements about this "
                "run's own set")))
            continue
        if observation.location.text_span is None:
            continue
        address = serialize_container_path(observation.location.container_path)
        unit = index.get(address)
        if unit is None:
            violations.append(Violation(10, (
                f"observation {position} has a text_span and no text_units row at "
                f"{address!r} on run {record.run_id!r}; a span is an offset into a "
                "stored unit, and without one no citation check can resolve it")))
            continue
        try:
            check_span_anchor(observation, unit)
        except SpanAnchorError as exc:
            violations.append(Violation(5, f"observation {position}: {exc}"))
    return tuple(violations)


def validate_run(run, observations=(), text_units=()) -> ExtractionRun:
    """The extractor's gate for a whole run. Returns the constructed record, or
    raises with every violation. It never drops an observation to make a run
    conform (Done-means 2)."""
    violations = check_run(run, observations, text_units)
    if violations:
        raise NonConforming(violations)
    if isinstance(run, ExtractionRun):
        return run
    return run_from_mapping(run)
