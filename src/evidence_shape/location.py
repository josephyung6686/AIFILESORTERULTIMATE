# src/evidence_shape/location.py
"""D1 -- one structured location record for every source type.

P5 OQ1, closed in 05-minor-resolutions.md: "Is `Location` structured? Yes -- P4's
structured record plus the canonical locator. §2.8's per-source-type examples
(page/heading, table/row/column, EXIF field, OCR region, manifest path) cannot be
expressed by a string."

`zone` answers what kind of place (which §3.7 weights); `container_path` answers
which one (which §8.2 explanations cite). Container indices are 1-based (D3, matching
§2.8's own "page 1, heading 2"); text offsets are 0-based half-open in Unicode scalar
values (D3, D4), which is what makes `raw_value == text[start:end]` hold.

Two published names spell `region` and they are different things: `Segment(kind=
"region")` is §2.8's "an OCR region", an addressing step that appears in the locator;
`Location.region` is §2.7's "locations or bounding boxes where available", which the
locator grammar has no term for. Neither name is P4's to change.
"""
from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from evidence_shape.vocabulary import (
    LABEL_SEGMENT_KINDS, REGION_UNITS, SEGMENT_KINDS, ZONES, check,
)


class MalformedLocation(ValueError):
    """A structurally invalid location. P4 rejects it; it never repairs one."""


@dataclass(frozen=True, slots=True)
class Segment:
    """One addressing step, outermost to innermost (segment-kind rule 1)."""

    kind: str
    index: int | None = None
    label: str | None = None

    def __post_init__(self) -> None:
        check(self.kind, SEGMENT_KINDS, name="kind")
        if self.kind in LABEL_SEGMENT_KINDS:
            if self.index is not None:
                raise MalformedLocation(
                    f"{self.kind!r} is addressed by its label and carries no index "
                    "(segment-kind rule 2)"
                )
            if not self.label:
                raise MalformedLocation(
                    f"{self.kind!r} is addressed by its label, which is required "
                    "(segment-kind rule 2)"
                )
            return
        if type(self.index) is not int or self.index < 1:
            raise MalformedLocation(
                f"{self.kind!r} is addressed by a 1-based index, not {self.index!r} "
                "(D3: §2.8's own examples are 1-based and reach §8.2 explanations)"
            )


@dataclass(frozen=True, slots=True)
class TextSpan:
    """0-based, half-open, in Unicode scalar values (D3, D4)."""

    start: int
    end: int

    def __post_init__(self) -> None:
        for name, value in (("start", self.start), ("end", self.end)):
            if type(value) is not int or value < 0:
                raise MalformedLocation(
                    f"text_span.{name} is a 0-based code-point offset, not {value!r}"
                )
        if self.end < self.start:
            raise MalformedLocation("text_span is half-open: start <= end (D3)")


@dataclass(frozen=True, slots=True)
class TimeSpan:
    """Integer milliseconds from media start. §2.9 audio/video."""

    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        for name, value in (("start_ms", self.start_ms), ("end_ms", self.end_ms)):
            if type(value) is not int or value < 0:
                raise MalformedLocation(
                    f"time_span.{name} is integer milliseconds, not {value!r}"
                )
        if self.end_ms < self.start_ms:
            raise MalformedLocation("time_span: start_ms <= end_ms")


@dataclass(frozen=True, slots=True)
class Region:
    """§2.7's "locations or bounding boxes where available". Null when unreported."""

    x: float
    y: float
    w: float
    h: float
    unit: str

    def __post_init__(self) -> None:
        for name in ("x", "y", "w", "h"):
            value = getattr(self, name)
            if type(value) not in (int, float):
                raise MalformedLocation(f"region.{name} is a number, not {value!r}")
        check(self.unit, REGION_UNITS, name="region.unit")


@dataclass(frozen=True, slots=True)
class Location:
    """§2.8's "Location", as one shape for every source type."""

    zone: str
    container_path: tuple[Segment, ...] = ()
    text_span: TextSpan | None = None
    time_span: TimeSpan | None = None
    region: Region | None = None

    def __post_init__(self) -> None:
        check(self.zone, ZONES, name="zone")
        if not isinstance(self.container_path, tuple):
            if isinstance(self.container_path, (str, bytes)) or not isinstance(
                    self.container_path, Iterable):
                raise MalformedLocation("container_path is an ordered sequence of Segments")
            object.__setattr__(self, "container_path", tuple(self.container_path))
        for segment in self.container_path:
            if not isinstance(segment, Segment):
                raise MalformedLocation(
                    f"container_path holds Segments, not {segment!r}"
                )
        for name, expected in (("text_span", TextSpan), ("time_span", TimeSpan),
                               ("region", Region)):
            value = getattr(self, name)
            if value is not None and not isinstance(value, expected):
                raise MalformedLocation(f"{name} is a {expected.__name__} or None")
        if self.text_span is not None and self.time_span is not None:
            raise MalformedLocation(
                "a location carries one span or the other, never both: the locator "
                'grammar is `[ "#" text_span | "@" time_span ]`'
            )
