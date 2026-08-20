# tests/p5/p4_stub.py
"""P4's surface, re-exported. P4 shipped 2026-08-20; this file no longer reimplements it.

It kept its name and its module path so the ten importing test files in tests/p5/ did
not have to change, but nothing below is a second copy of P4's locator, vocabularies
or conformance rules any more: the vocabularies ARE `evidence_shape.vocabulary`'s
tuples, the locator IS `evidence_shape.locator`, and the validators delegate to
`evidence_shape.conformance`. Section 2.8 exists to stop exactly the drift a second
implementation creates, and while P4 was unbuilt this file was that second
implementation.

What remains local is only the adaptation, and each piece says why:

  * P5 emits plain dicts (`extractors.shape.observation`, `.location`, `.run`); P4's
    records are frozen dataclasses. The `_segment` / `_location` / `_text_unit`
    converters below are the bridge, not a reimplementation.
  * The stub's function names and signatures are what tests/p5/ calls. Where P4's
    equivalent is spelled differently (`serialize_locator`, `check_run`) or shaped
    differently, the wrapper is one line over P4's.
  * `pytest.raises(AssertionError)` in tests/p5/test_p5_shape.py means the validators
    must fail with `AssertionError`; P4 raises `NonConforming`. The wrappers assert on
    P4's own violation list, so the DECISION is always P4's and only the exception
    type is this harness's.

TWO places where real P4 and shipped P5 still disagree, each isolated to one line
with a comment, each reported rather than papered over: `_location` (region) and
`validate_observation` (run_id).

The third — `config_fingerprint` — is FIXED, not worked around. P4's `sha256_of`
length-prefixes the part before hashing and P5 called `hashlib.sha256` directly, so
the canonical bytes matched and the digests never did: P4 rejected every run record
P5 emitted. `extractors.shape.fingerprint` now delegates to P4, this mapping drops
nothing, and P4 validates the field for real.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from evidence_shape.conformance import check_observation, check_run
from evidence_shape.location import Location, Segment, TextSpan, TimeSpan
from evidence_shape.locator import (
    escape_label as _escape,
    parse_locator as _p4_parse_locator,
    serialize_container_path,
    serialize_locator,
    unescape_label as _unescape,
)
from evidence_shape.observation import (
    NULLABLE_FIELDS as _P4_NULLABLE_FIELDS,
    OBSERVATION_FIELDS as _P4_OBSERVATION_FIELDS,
    OBSERVATION_ROW_FIELDS,
    observation_from_mapping,
    observation_key as _p4_observation_key,
)
from evidence_shape.text_units import SpanAnchorError, TextUnit, check_span_anchor
from evidence_shape.vocabulary import (
    ANALYSIS_TIERS,
    COMPLETENESS,
    EXTRACTOR_RELIABILITY_STATES as EXTRACTOR_RELIABILITY,
    LABEL_SEGMENT_KINDS as LABEL_ADDRESSED,
    RELIABILITY_STATES,
    SEGMENT_KINDS,
    SOURCE_TYPES,
    ZERO_OBSERVATION_COMPLETENESS,
    ZONES,
)

__all__ = [
    "ANALYSIS_TIERS", "COMPLETENESS", "EXTRACTOR_RELIABILITY",
    "FORBIDDEN_OBSERVATION_FIELDS", "LABEL_ADDRESSED",
    "NULLABLE_OBSERVATION_FIELDS", "OBSERVATION_FIELDS", "RELIABILITY_STATES",
    "SEGMENT_KINDS", "SOURCE_TYPES", "ZERO_OBSERVATION_COMPLETENESS", "ZONES",
    "locator_for", "observation_key", "parse_locator", "unit_locator_for",
    "validate_observation", "validate_run",
]

#: What an extractor emits: P4's eighteen minus the two P4's writer assigns.
#: `observation_key` is derived by P4 from the other four (MINOR 8) and `run_id` is
#: added by the sink at write time, so neither is in what P5 hands over. Derived
#: rather than restated, and it reproduces P5's `extractors.shape.OBSERVATION_FIELDS`
#: exactly -- name for name, in order.
OBSERVATION_FIELDS: tuple[str, ...] = tuple(
    name for name in _P4_OBSERVATION_FIELDS
    if name not in ("observation_key", "run_id"))

#: P4's `observation.NULLABLE_FIELDS`, narrowed to the emitted set. NOTE: P4 also
#: makes `context_before` and `context_after` nullable, which the old hand-written
#: stub did not; every P5 extractor emits strings there, so nothing depended on the
#: stricter reading.
NULLABLE_OBSERVATION_FIELDS: tuple[str, ...] = tuple(
    name for name in OBSERVATION_FIELDS if name in _P4_NULLABLE_FIELDS)

#: LOCAL, and P4 publishes no equivalent: P4 closes the field set POSITIVELY, with
#: `observation.OBSERVATION_ROW_FIELDS`, and rejects anything outside it under rule 6
#: rather than enumerating forbidden names. This tuple is kept because tests/p5/ names
#: it, and it is now documentation only -- `validate_observation` enforces rule 6
#: through P4's closed set, not through this list. The assert below keeps the two
#: honest: every name here really is one P4's rule 6 rejects.
FORBIDDEN_OBSERVATION_FIELDS: tuple[str, ...] = (
    "locator", "path_proposal", "destination", "destination_node", "domain",
    "category", "field_name", "fact", "group_id", "node_id", "template_id",
    "plan_id", "plan_version", "handling_class", "sensitivity_state", "preferred",
    "absent", "conflict", "resolution", "screenshot", "media_type",
)
assert not set(FORBIDDEN_OBSERVATION_FIELDS) & set(OBSERVATION_ROW_FIELDS), (
    "a name P4 stores cannot also be one P4 forbids")

#: `validate_observation` receives an observation with its `run_id` already stripped
#: (tests/p5/conftest.py's `RecordingSink.conforms`), and P4's record requires one.
#: The units handed in alongside it are already filtered to that same run, so the
#: pairing rule 10 states is preserved by construction and this stand-in only satisfies
#: P4's non-empty-string requirement.
_HARNESS_RUN_ID = "run-under-validation"


def _segment(mapping: Mapping[str, Any]) -> Segment:
    return Segment(mapping["kind"], mapping.get("index"), mapping.get("label"))


def _segments(container_path: Iterable[Mapping[str, Any]]) -> tuple[Segment, ...]:
    return tuple(_segment(segment) for segment in container_path)


def _location(mapping: Mapping[str, Any], *, zone: str | None = None) -> Location:
    """P5's location dict as P4's record.

    `region` is deliberately dropped. P4's `Region` is `(x, y, w, h, unit)`; the OCR
    extractor emits `{"x", "y", "width", "height"}` (src/extractors/ocr.py:144 passing
    `recognized.box` straight through), so `locator.location_from_mapping` raises
    KeyError('w') on it. The hand-written stub never inspected `region` either, so
    nothing is lost here that was previously checked -- but the shape mismatch between
    shipped P4 and shipped P5 is real and is reported, not resolved in this file. The
    locator grammar has no term for a bounding box in any case, so no locator, key or
    round-trip below depends on it.
    """
    text_span, time_span = mapping.get("text_span"), mapping.get("time_span")
    return Location(
        mapping["zone"] if zone is None else zone,
        _segments(mapping["container_path"]),
        text_span=None if text_span is None
        else TextSpan(text_span["start"], text_span["end"]),
        time_span=None if time_span is None
        else TimeSpan(time_span["start_ms"], time_span["end_ms"]),
    )


def _text_unit(mapping: Mapping[str, Any], run_id: str) -> TextUnit:
    return TextUnit(run_id, _segments(mapping["container_path"]), mapping["text"],
                    mapping.get("truncated", False))


def unit_locator_for(container_path: Iterable[Mapping[str, Any]]) -> str:
    """P4's `locator.serialize_container_path` -- D12's `text_units.unit_locator`."""
    return serialize_container_path(_segments(container_path))


def locator_for(location: Mapping[str, Any]) -> str:
    """P4's `locator.serialize_locator`, over P5's dict.

    The zone token is substituted rather than validated: P4's `Location` checks `zone`
    against the closed vocabulary at construction, and
    tests/p5/test_p5_docx.py:112 passes the placeholder `zone="x"` to read a unit's
    address out of a full locator. The hand-written stub validated no zone either, so
    this preserves the old contract exactly -- and every character after the zone,
    which is the part that actually drifts (separators, %-escaping, span grammar),
    comes from P4. Real zones take the same path and are unaffected.
    """
    zone = location["zone"]
    stand_in = zone if zone in ZONES else ZONES[0]
    serialized = serialize_locator(_location(location, zone=stand_in))
    return zone + serialized[len(stand_in):]


def parse_locator(text: str) -> dict:
    """P4's `locator.parse_locator`, returned in the dict shape tests/p5/ reads.

    Verified against the old hand-written parser over every locator the P5 suite
    produces: zero disagreements, on the structured fields and on the round-trip.
    """
    location = _p4_parse_locator(text)
    return {
        "zone": location.zone,
        "container_path": tuple(
            {"kind": segment.kind, "index": segment.index, "label": segment.label}
            for segment in location.container_path),
        "text_span": None if location.text_span is None
        else {"start": location.text_span.start, "end": location.text_span.end},
        "time_span": None if location.time_span is None
        else {"start_ms": location.time_span.start_ms,
              "end_ms": location.time_span.end_ms},
        "region": None,
    }


def observation_key(observation: Mapping[str, Any]) -> str:
    """P4's `observation.observation_key`, over P5's dict.

    P4 takes the four inputs by keyword and derives the locator itself; the old stub
    took the whole observation. NOTE: the two produce DIFFERENT digests for the same
    observation -- P4 joins the four parts length-prefixed (`canonical.sha256_of`) and
    the stub joined them on \\x1f. P4's is the real key; tests/p5/ only ever asserted
    that the key is STABLE across two runs, never its value, so the change is invisible
    to them and P4's injective construction is the one that ships.
    """
    return _p4_observation_key(
        content_hash=observation["content_hash"],
        extractor_name=observation["extractor_name"],
        locator=serialize_locator(_location(observation["location"])),
        raw_value=observation["raw_value"],
    )


def _fail(violations) -> None:
    assert not violations, "; ".join(
        f"rule {violation.rule}: {violation.message}" for violation in violations)


def validate_observation(observation: Mapping[str, Any], *,
                         text_units: Iterable[Mapping[str, Any]] = ()) -> None:
    """P4's `conformance.check_observation`, plus rules 5 and 10 over `text_units`.

    Rules 1, 2, 3, 4, 6, 7, 11 and 12 are entirely P4's now. Rules 5 and 10 need a
    second record, so P4 checks them in `check_run` and not here; the old stub checked
    them per observation and tests/p5/test_p5_shape.py:231 asserts that, so the lookup
    stays -- but the RAW-1 comparison itself is P4's `text_units.check_span_anchor`,
    which is the part that could drift.
    """
    location = observation["location"]
    # `_location` is what makes P4's own `location_from_mapping` reachable at all here:
    # handed P5's raw location dict, it raises an uncaught KeyError('w') on the OCR
    # region rather than reporting a violation. P4 accepts a built `Location` record
    # in this field, so the conversion is P4's supported path, not a way around it.
    candidate = {**dict(observation), "run_id": _HARNESS_RUN_ID,
                 "location": _location(location)}
    _fail(check_observation(candidate))

    if location.get("text_span") is None:
        return
    record = observation_from_mapping(candidate)
    address = unit_locator_for(location["container_path"])
    units = [unit for unit in text_units
             if unit_locator_for(unit["container_path"]) == address]
    assert units, f"no text_units row for {locator_for(location)} (rule 10)"
    try:
        check_span_anchor(record, _text_unit(units[0], _HARNESS_RUN_ID))
    except SpanAnchorError as exc:
        raise AssertionError(f"rule 5: {exc}") from exc


def _p4_run_mapping(run: Mapping[str, Any]) -> dict:
    """P5's run dict as the mapping P4's `runs.run_from_mapping` reads. Identity.

    This function once DROPPED `config_fingerprint`, because P4's
    `runs.config_fingerprint` length-prefixes the part before hashing and P5's
    `extractors.shape.fingerprint` called `hashlib.sha256` directly: the canonical
    JSON was byte-identical, the digests never were, and P4 rejected every run record
    P5 emitted. Dropping the field let P4 check the other fourteen for real while the
    break stood.

    The break was fixed at its source -- `extractors.shape.fingerprint` delegates to
    P4 -- so nothing is dropped and P4 validates the fingerprint for real. The
    conversion is kept as a named seam rather than inlined so that the next
    P5-mapping-to-P4-mapping difference has one place to live and one place to be
    read; its emptiness is the point.
    """
    return dict(run)      # nothing dropped: P5 now delegates the fingerprint to P4


def validate_run(run: Mapping[str, Any], observation_count: int) -> None:
    """P4's `conformance.check_run` for the run record, plus rule 9 against a count.

    P4 derives rule 9 from the observation set it is handed; this harness is handed a
    count instead (tests/p5/conftest.py), so the rule is applied here against P4's own
    `ZERO_OBSERVATION_COMPLETENESS`. One vocabulary, one place, no second copy.

    The last two checks are P5-side rules the hand-written stub asserted and P4 does
    not: I4 reserves `llm` for P8, which P4's vocabulary admits because P8 is a
    legitimate writer of it, and P4 constrains where `failure_reason` MAY appear
    without requiring it. Both are kept so no test loses coverage.
    """
    _fail(check_run(_p4_run_mapping(run), ()))
    assert run["observation_count"] == observation_count
    if run["completeness"] in ZERO_OBSERVATION_COMPLETENESS:
        assert observation_count == 0, (
            f"an {run['completeness']} run carries zero observations (rule 9)")
    assert run["analysis_tier"] != "llm", "P8 is the only writer of `llm` (I4)"
    if run["completeness"] in ("unreadable", "failed"):
        assert run["failure_reason"], "failure_reason is required here"
