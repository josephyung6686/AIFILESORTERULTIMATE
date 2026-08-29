# src/evidence_shape/text_units.py
"""Record 3 -- `text_units`, the home for the bulk text (D12, G1).

§2.2 requires "complete text by page", §2.4 the full text of a text-bearing file,
§2.7 "raw recognized text". None of those is a LOCATED VALUE, so none is an
observation -- yet a `text_span` is defined as an offset into a stored, addressable
text unit, so the unit must exist and must be addressed by the same `container_path`
vocabulary the observation uses. P4 owns the span semantics, so P4 owns the unit.

Text is per RUN, not per file: a text-layer pass and an OCR pass over the same PDF
produce two different texts under two run_ids, and §8.2 requires both remain
available. Superseding a run never rewrites or deletes the earlier run's units.

RAW-1, checked here, is the anchor for every citation check in §3.6, §4.8, §6.10 and
§7.9: `raw_value` is byte-for-byte the substring of the stored text at that span.
Offsets are Unicode scalar values (D4) and a Python `str` is already a sequence of
code points, so there is no conversion in this module -- which is the property D4
was chosen for, and which holds for CJK (§2.7) and astral-plane characters alike.

These rows are always local (§8.4). §4.4's "short evidence excerpts" are cut FROM
them by P8 under P7's gate; the rows themselves never leave the machine.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from evidence_shape.location import Segment, TextSpan
from evidence_shape.locator import serialize_container_path
from evidence_shape.observation import Observation

#: The SPEC's Record 3, in the SPEC's order.
TEXT_UNIT_FIELDS: tuple[str, ...] = (
    "run_id", "container_path", "unit_locator", "text", "length", "truncated",
)


class MalformedTextUnit(ValueError):
    """A non-conforming text unit. P4 fails it rather than coercing it."""


class SpanAnchorError(ValueError):
    """RAW-1 or rule 10 does not hold between an observation and a unit."""


@dataclass(frozen=True, slots=True)
class TextUnit:
    """One addressable text unit an extraction run emitted."""

    run_id: str
    container_path: tuple[Segment, ...]
    text: str
    truncated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id:
            raise MalformedTextUnit("run_id is a non-empty string")
        if not isinstance(self.container_path, tuple):
            if isinstance(self.container_path, (str, bytes)) or not isinstance(
                    self.container_path, Iterable):
                raise MalformedTextUnit("container_path is a sequence of Segments")
            object.__setattr__(self, "container_path", tuple(self.container_path))
        for segment in self.container_path:
            if not isinstance(segment, Segment):
                raise MalformedTextUnit(
                    f"container_path holds Segments, not {segment!r}")
        if not isinstance(self.text, str):
            raise MalformedTextUnit("text is a string, exactly as extracted")
        if type(self.truncated) is not bool:
            raise MalformedTextUnit(
                "truncated is a bool and is never absent (§8.6: never silently)")

    @property
    def unit_locator(self) -> str:
        """The canonical serialization of `container_path`. No zone: a unit is an
        address, not a located value."""
        return serialize_container_path(self.container_path)

    @property
    def length(self) -> int:
        """The STORED length, in Unicode scalar values (D4, rule 5)."""
        return len(self.text)

    def to_mapping(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "container_path": [
                {"kind": segment.kind,
                 **({"index": segment.index} if segment.index is not None else {}),
                 **({"label": segment.label} if segment.label is not None else {})}
                for segment in self.container_path],
            "unit_locator": self.unit_locator,
            "text": self.text,
            "length": self.length,
            "truncated": self.truncated,
        }


def text_unit_from_mapping(mapping: Mapping[str, object]) -> TextUnit:
    missing = [name for name in TEXT_UNIT_FIELDS
               if name not in ("unit_locator", "length") and name not in mapping]
    if missing:
        raise MalformedTextUnit(f"missing text-unit fields: {missing}")
    unknown = sorted(set(mapping) - set(TEXT_UNIT_FIELDS))
    if unknown:
        raise MalformedTextUnit(f"{unknown} are not fields of the text-unit record")
    path = mapping["container_path"]
    unit = TextUnit(
        run_id=mapping["run_id"],
        container_path=path if isinstance(path, tuple) else tuple(
            Segment(segment["kind"], segment.get("index"), segment.get("label"))
            for segment in path),
        text=mapping["text"],
        truncated=mapping["truncated"],
    )
    stated_locator = mapping.get("unit_locator")
    if stated_locator is not None and stated_locator != unit.unit_locator:
        raise MalformedTextUnit(
            f"unit_locator {stated_locator!r} does not serialize from this "
            "container_path; the unit and the observations that point into it are "
            "addressed identically or not at all")
    stated_length = mapping.get("length")
    if stated_length is not None and stated_length != unit.length:
        raise MalformedTextUnit(
            f"length {stated_length!r} is not the stored length {unit.length}")
    return unit


def raw_value_at(unit: TextUnit, text_span: TextSpan) -> str:
    """The substring RAW-1 compares against, in code points (D4)."""
    return unit.text[text_span.start:text_span.end]


def check_span_anchor(observation: Observation, unit: TextUnit) -> None:
    """Conformance rule 10 and RAW-1, together. Raises; never returns a repair."""
    text_span = observation.location.text_span
    if text_span is None:
        raise SpanAnchorError(
            "rule 10 applies to an observation with a non-null text_span; this one "
            "has none and needs no unit")
    if unit.run_id != observation.run_id:
        raise SpanAnchorError(
            f"the unit belongs to run {unit.run_id!r} and the observation to "
            f"{observation.run_id!r}; text is per run, not per file (rule 4)")
    address = serialize_container_path(observation.location.container_path)
    if unit.unit_locator != address:
        raise SpanAnchorError(
            f"the unit is addressed {unit.unit_locator!r} and the observation's span "
            f"is into {address!r}; rule 10 requires they be equal. The comparison is "
            "on the ADDRESS and not on the record: segment-kind rule 2 makes a label "
            "descriptive only, so a labelled `slide=6` and a bare `slide=6` are one "
            "address -- and `(run_id, unit_locator)` is the key `text_units` is "
            "stored under")
    if text_span.end > unit.length:
        raise SpanAnchorError(
            f"the span ends at {text_span.end} and the stored unit is "
            f"{unit.length} long"
            + (" -- the unit is truncated, and an observation whose span lies beyond "
               "the stored prefix is not written (rule 5)" if unit.truncated else ""))
    found = raw_value_at(unit, text_span)
    if found != observation.raw_value:
        raise SpanAnchorError(
            f"RAW-1: raw_value {observation.raw_value!r} is not the substring at "
            f"{text_span.start}-{text_span.end}, which is {found!r}")
