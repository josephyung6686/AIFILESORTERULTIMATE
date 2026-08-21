# src/extractors/archive.py
"""E4 - archives (section 2.5).

"Archives should be inspected without being unpacked to disk. The engine should read
and store the archive type, contained paths, filenames, folder names, extensions,
file count, uncompressed size where available, and recognizable markers such as
source-code manifests or document names."

This module imports no archive library, opens no file and writes nothing: the
manifest reader is injected, so there is no code path here that could unpack an
archive. That is how "the normal scan should never extract archive contents to the
filesystem" is kept - by absence, not by a flag.

Uncompressed size is read from the manifest where the format declares it, and IS the
decompression-bomb signal. P5 holds no size ceiling: section 8.6's ceilings are
configuration the reader was given (G4), and the reader reports that it stopped.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from extractors.failure import unsupported_result
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "archive.manifest"
SOURCE_TYPE = "archive"
ANALYSIS_TIER = "native"

#: Section 2.5's own names for the two values that describe the archive itself.
ARCHIVE_TYPE_FIELD = "archive type"
UNCOMPRESSED_SIZE_FIELD = "uncompressed size"

#: Section 2.5's "recognizable markers such as source-code manifests or document
#: names" - the two classes section 2.5 names. WHICH files are markers is Deferred
#: ("Archive recognizable markers beyond the above | The marker set"), so no member
#: name appears here and the recognizer is caller-supplied.
MARKER_KINDS: tuple[str, ...] = ("source-code manifest", "document name")


class UnknownMarkerKind(Exception):
    """A marker class section 2.5 does not name."""


@dataclass(frozen=True)
class ArchiveMember:
    """One manifest entry. `uncompressed_size` is what the manifest DECLARES."""
    path: str
    is_directory: bool = False
    uncompressed_size: int | None = None


@dataclass(frozen=True)
class ArchiveManifest:
    """What an injected `read_manifest` returns.

    `unreadable_reason` is section 2.5's password-protected and malformed cases;
    `partial_reason` is its nested and oversized ones. The reader names the reason
    because the reason is format knowledge; P5 places it.
    """
    archive_type: str
    members: tuple[ArchiveMember, ...] = ()
    uncompressed_size: int | None = None
    inspected: int = 0
    total: int = 0
    unreadable_reason: str | None = None
    partial_reason: str | None = None


@dataclass(frozen=True)
class ArchiveMarker:
    """One of section 2.5's recognizable markers, as the caller recognized it."""
    member_path: str
    kind: str


def _name_spans(path_text: str, *, is_directory: bool) -> list[tuple[int, int]]:
    """Section 2.5's "contained paths, filenames, folder names, extensions" as spans
    of one member path - four readings of one string, so each is a located value and
    no character is stored twice."""
    spans = [(0, len(path_text))]
    parts = path_text.rstrip("/").split("/")
    offset = 0
    for position, part in enumerate(parts):
        start, end = offset, offset + len(part)
        offset = end + 1
        if not part:
            continue
        spans.append((start, end))
        if position == len(parts) - 1 and not is_directory:
            dot = part.rfind(".")
            if dot > 0:
                spans.append((start + dot, end))
    seen, unique = set(), []
    for span in spans:
        if span not in seen:
            seen.add(span)
            unique.append(span)
    return unique


def extract_archive(*, file_row: Mapping[str, Any], path: Path,
                    policy: SafetyPolicy,
                    read_manifest: Callable[[Path], ArchiveManifest],
                    recognize_markers: Callable[[Sequence[str]],
                                                Sequence[ArchiveMarker]],
                    now: str, context_window: int) -> ExtractionResult:
    """Section 2.5's manifest, as P4 records. Reads one manifest and recurses never.

    SPEC Open question 8 - whether a nested archive's manifest may be read one level
    down, in memory - is left open by that: an inner archive is one ordinary entry
    whose path ends in an archive extension, and nothing here looks inside it.
    """
    admit(path, policy=policy)
    manifest = read_manifest(path)
    if manifest is None:
        # §2.4: no reader for this format in this deployment. `unsupported`, never
        # `failed` -- the bytes were never looked at, so a `failed` run would report
        # a missing library as a corrupt file.
        return unsupported_result(
            file_row=file_row, extractor_name=EXTRACTOR_NAME,
            extractor_version=VERSION, source_type=SOURCE_TYPE,
            analysis_tier=ANALYSIS_TIER, now=now)


    candidates: list[tuple[str, str, tuple, dict | None, str | None, str]] = []
    units: list[Mapping[str, Any]] = []

    candidates.append(("metadata", manifest.archive_type,
                       (segment("field", label=ARCHIVE_TYPE_FIELD),), None, None,
                       "direct"))
    if manifest.uncompressed_size is not None:
        candidates.append(("metadata", str(manifest.uncompressed_size),
                           (segment("field", label=UNCOMPRESSED_SIZE_FIELD),), None,
                           None, "direct"))

    for member in manifest.members:
        container = (segment("entry", label=member.path),)
        units.append(text_unit(text=member.path, container_path=container))
        for start, end in _name_spans(member.path,
                                      is_directory=member.is_directory):
            candidates.append(("manifest", member.path[start:end], container,
                               {"start": start, "end": end}, member.path,
                               "possible"))

    for marker in recognize_markers([m.path for m in manifest.members]):
        if marker.kind not in MARKER_KINDS:
            raise UnknownMarkerKind(
                f"{marker.kind!r} is not one of section 2.5's marker classes "
                f"{MARKER_KINDS}"
            )
        candidates.append(("metadata", marker.member_path,
                           (segment("field", label=marker.kind),), None, None,
                           "direct"))

    observations = _collapse(candidates, file_row=file_row, now=now,
                             context_window=context_window)

    completeness = "complete"
    failure_reason = None
    if manifest.unreadable_reason:
        # Section 2.9 / M3: indexed-but-unreadable, never zero rows. The archive type
        # is still evidence and P4's rule 9 does not list `unreadable` as a
        # zero-observation state.
        completeness = "unreadable"
        failure_reason = (
            f"{manifest.unreadable_reason}; section 2.5 marks it rather than forcing "
            "it open"
        )
    elif manifest.partial_reason:
        completeness = "partial"

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected"}, completeness=completeness,
                coverage=coverage("entries", manifest.inspected, manifest.total),
                observation_count=len(observations), started_at=now, finished_at=now,
                failure_reason=failure_reason),
        observations=observations,
        text_units=tuple(units),
    )


def _collapse(candidates, *, file_row: Mapping[str, Any], now: str,
              context_window: int) -> tuple[Mapping[str, Any], ...]:
    """P4 D10: one observation per (run, exact raw value, zone); `location` addresses
    the first occurrence in manifest order. `src` in two member paths is one row with
    an occurrence count of two."""
    first: dict[tuple[str, str], tuple] = {}
    counts: dict[tuple[str, str], int] = {}
    order: list[tuple[str, str]] = []
    for candidate in candidates:
        key = (candidate[0], candidate[1])
        if key not in first:
            first[key] = candidate
            counts[key] = 0
            order.append(key)
        counts[key] += 1

    observations = []
    for key in order:
        zone, raw, container, span, unit_text, reliability = first[key]
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=raw,
            normalized_value=normalize_mechanical(raw),
            location=location(zone=zone, container_path=container, text_span=span),
            context_before=before, context_after=after, context_truncated=truncated,
            occurrence_count=counts[key], observed_at=now, reliability=reliability,
        ))
    return tuple(observations)
