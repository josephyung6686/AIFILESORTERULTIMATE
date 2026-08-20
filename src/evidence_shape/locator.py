# src/evidence_shape/locator.py
"""The canonical serialization of a Location, and its parser.

    locator   := zone [ ":" segments ] [ "#" text_span | "@" time_span ]
    segments  := segment ( "/" segment )*
    segment   := kind "=" addr
    addr      := <1-based decimal integer>     ; indexed kinds
               | <escaped label>               ; field | entry | key
    text_span := start "-" end                 ; 0-based code points, half-open
    time_span := start_ms "-" end_ms           ; integer milliseconds

Redundant with the structured fields by construction. It exists because §8.2
provenance events, §4.4 dossiers and §3.6/§4.8/§6.10/§7.9 citation checks all need
one short stable handle -- and because it is one of the four inputs to
`observation_key`, which §8.7 requires to stay resolvable across extractor upgrades.

Escaping, in labels only: percent-encode `%` `/` `=` `#` `@` `:` and any control
character (Unicode category Cc) as %XX, uppercase hex, over UTF-8 bytes. Archive
member paths contain `/` and this is not optional. Non-ASCII is not escaped.

The bounding box (`Location.region`) has no term in the grammar and never appears
here; `Segment(kind="region")` does, and they are different things.
"""
from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence

from evidence_shape.location import (
    Location, MalformedLocation, Region, Segment, TextSpan, TimeSpan,
)
from evidence_shape.vocabulary import LABEL_SEGMENT_KINDS, SEGMENT_KINDS, ZONES, check

_RESERVED = ("%", "/", "=", "#", "@", ":")
_ZONE_MARK = ":"
_SEGMENT_MARK = "/"
_ADDR_MARK = "="
_SPAN_MARK = "#"
_TIME_MARK = "@"
_RANGE_MARK = "-"
_HEX = "0123456789ABCDEF"

_LOCATION_KEYS = frozenset(
    {"zone", "container_path", "text_span", "time_span", "region", "locator"})


class MalformedLocator(ValueError):
    """A locator that does not parse. P4 rejects it; no consumer guesses."""


def escape_label(label: str) -> str:
    """Percent-encode the reserved set and control characters, and nothing else."""
    out: list[str] = []
    for character in label:
        if character in _RESERVED or unicodedata.category(character) == "Cc":
            out.extend(f"%{byte:02X}" for byte in character.encode("utf-8"))
        else:
            out.append(character)
    return "".join(out)


def unescape_label(text: str) -> str:
    """The inverse. A malformed escape is a rejection, never a passed-through `%`."""
    raw = bytearray()
    index = 0
    while index < len(text):
        character = text[index]
        if character == "%":
            token = text[index + 1:index + 3]
            if len(token) != 2 or any(digit not in _HEX for digit in token):
                raise MalformedLocator(
                    f"%-escape must be two uppercase hex digits, got {text[index:index + 3]!r}"
                )
            raw.append(int(token, 16))
            index += 3
            continue
        if character in _RESERVED:
            raise MalformedLocator(f"unescaped {character!r} inside a label")
        raw.extend(character.encode("utf-8"))
        index += 1
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise MalformedLocator(f"%-escapes do not decode as UTF-8: {text!r}") from exc


def serialize_container_path(segments: Sequence[Segment]) -> str:
    """The address alone, with no zone. This is `text_units.unit_locator` (D12)."""
    return _SEGMENT_MARK.join(
        f"{segment.kind}{_ADDR_MARK}{segment.index}" if segment.index is not None
        else f"{segment.kind}{_ADDR_MARK}{escape_label(segment.label)}"
        for segment in segments
    )


def parse_container_path(text: str) -> tuple[Segment, ...]:
    if not text:
        return ()
    segments: list[Segment] = []
    for chunk in text.split(_SEGMENT_MARK):
        kind, mark, addr = chunk.partition(_ADDR_MARK)
        if not mark:
            raise MalformedLocator(f"segment {chunk!r} has no {_ADDR_MARK!r}")
        check(kind, SEGMENT_KINDS, name="kind")
        if kind in LABEL_SEGMENT_KINDS:
            segments.append(Segment(kind, label=unescape_label(addr)))
            continue
        if not addr.isdigit():
            raise MalformedLocator(
                f"{kind!r} is addressed by a 1-based decimal integer, got {addr!r}"
            )
        segments.append(Segment(kind, int(addr)))
    return tuple(segments)


def addressing(location: Location) -> Location:
    """The part of a location the locator carries.

    Segment-kind rule 2: "A kind with an index is addressed by its index; its label
    is descriptive only and never appears in the locator." So a round-trip through
    the string reproduces this projection, not the original record -- and conformance
    rule 4 is written against it. The bounding box is dropped for the same reason:
    the grammar has no term for it.
    """
    return Location(
        location.zone,
        tuple(Segment(segment.kind, segment.index) if segment.index is not None
              else segment for segment in location.container_path),
        text_span=location.text_span,
        time_span=location.time_span,
    )


def serialize_locator(location: Location) -> str:
    """Canonical and deterministic: the same location always produces this string."""
    out = location.zone
    if location.container_path:
        out += _ZONE_MARK + serialize_container_path(location.container_path)
    if location.text_span is not None:
        out += (f"{_SPAN_MARK}{location.text_span.start}"
                f"{_RANGE_MARK}{location.text_span.end}")
    elif location.time_span is not None:
        out += (f"{_TIME_MARK}{location.time_span.start_ms}"
                f"{_RANGE_MARK}{location.time_span.end_ms}")
    return out


def _split_span(text: str) -> tuple[str, TextSpan | None, TimeSpan | None]:
    marks = [(text.index(mark), mark) for mark in (_SPAN_MARK, _TIME_MARK) if mark in text]
    if not marks:
        return text, None, None
    if len(marks) == 2:
        raise MalformedLocator(
            "a locator carries one span or the other, never both: the grammar is "
            '`[ "#" text_span | "@" time_span ]`'
        )
    at, mark = marks[0]
    head, tail = text[:at], text[at + 1:]
    start, separator, end = tail.partition(_RANGE_MARK)
    if not separator or not start.isdigit() or not end.isdigit():
        raise MalformedLocator(
            f"span {tail!r} is start{_RANGE_MARK}end in non-negative decimals"
        )
    if mark == _SPAN_MARK:
        return head, TextSpan(int(start), int(end)), None
    return head, None, TimeSpan(int(start), int(end))


def parse_locator(text: str, *, region: Region | None = None) -> Location:
    """Parse, or reject. The bounding box is not in the string, so it is a keyword."""
    if not isinstance(text, str) or not text:
        raise MalformedLocator("a locator is a non-empty string")
    head, text_span, time_span = _split_span(text)
    zone, mark, segments = head.partition(_ZONE_MARK)
    check(zone, ZONES, name="zone")
    if mark and not segments:
        raise MalformedLocator(f"{text!r} carries a {_ZONE_MARK!r} and no segments")
    return Location(zone, parse_container_path(segments), text_span=text_span,
                    time_span=time_span, region=region)


def location_to_mapping(location: Location) -> dict[str, object]:
    """The SPEC's JSON shape, including the redundant-by-construction `locator`."""
    return {
        "zone": location.zone,
        "container_path": [
            {"kind": segment.kind,
             **({"index": segment.index} if segment.index is not None else {}),
             **({"label": segment.label} if segment.label is not None else {})}
            for segment in location.container_path
        ],
        "text_span": None if location.text_span is None
        else {"start": location.text_span.start, "end": location.text_span.end},
        "time_span": None if location.time_span is None
        else {"start_ms": location.time_span.start_ms,
              "end_ms": location.time_span.end_ms},
        "region": None if location.region is None
        else {"x": location.region.x, "y": location.region.y, "w": location.region.w,
              "h": location.region.h, "unit": location.region.unit},
        "locator": serialize_locator(location),
    }


def location_from_mapping(mapping: Mapping[str, object]) -> Location:
    """The inverse, with the two halves checked against each other."""
    unknown = sorted(set(mapping) - _LOCATION_KEYS)
    if unknown:
        raise MalformedLocation(f"unknown location fields: {unknown}")
    text_span = mapping.get("text_span")
    time_span = mapping.get("time_span")
    region = mapping.get("region")
    location = Location(
        mapping["zone"],
        tuple(Segment(segment["kind"], segment.get("index"), segment.get("label"))
              for segment in mapping.get("container_path", ())),
        text_span=None if text_span is None
        else TextSpan(text_span["start"], text_span["end"]),
        time_span=None if time_span is None
        else TimeSpan(time_span["start_ms"], time_span["end_ms"]),
        region=None if region is None
        else Region(region["x"], region["y"], region["w"], region["h"], region["unit"]),
    )
    stated = mapping.get("locator")
    if stated is not None and stated != serialize_locator(location):
        raise MalformedLocation(
            f"locator {stated!r} does not serialize from the structured fields; the "
            "two halves of a location must agree or no citation check can use it"
        )
    return location
