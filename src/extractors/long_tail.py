# src/extractors/long_tail.py
"""E3's section 2.9 half - the six long-tail families, and the sensitivity signal.

Section 2.9 gives spreadsheets, presentations, email, calendar, contacts and
audio/video a field list each and no record of their own; P4's three records are the
homes and this module is the placement. `EXTRACTOR_NAME` is `text.structured`, the
same family Task 10 publishes, because the SPEC has one E3.

Two things here are policy, not format:

  Speech-to-text runs only under P7's explicit privacy and compute policy (section
  2.9). The authorization is an injected predicate with no default and is passed to
  the reader, so absent the policy no recognition is performed at all. Embedded
  subtitles and captions are section 2.9's unconditional half and are not
  speech-to-text.

  Email addresses, message content and every VCF value are marked POTENTIALLY
  SENSITIVE at emission, for P7 to act on. P5 assigns no handling class: section 8.4
  gives classification to P7 and SPEC Open question 7 is exactly where the line
  falls. There is one signal value here and no vocabulary.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from extractors.failure import unsupported_result
from extractors.reading import ZONE_BY_STRUCTURED_KIND, StructuredString
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    context_for, location, normalize_mechanical, observation, run, segment, text_unit,
)
from extractors.sink import ExtractionResult
from extractors.structured_text import (
    ANALYSIS_TIER, EXTRACTOR_NAME, VERSION,
)

#: Section 2.9's six long-tail families, in P4's `source_type` vocabulary. Together
#: with structured_text.STRUCTURED_TEXT_SOURCE_TYPES they partition the eight the
#: router sends to `text.structured`.
LONG_TAIL_SOURCE_TYPES: tuple[str, ...] = (
    "spreadsheet", "presentation", "email", "calendar", "contacts", "audio_video",
)

#: Section 2.9's own phrase, and the WHOLE of P5's sensitivity vocabulary. A class, a
#: level or a policy would be P7's (section 8.4); SPEC Open question 7 is the line.
POTENTIALLY_SENSITIVE = "potentially sensitive"

#: Section 2.9, Email: "while treating addresses and message content as potentially
#: sensitive". Message content is the body; a found address in it is zone `link`.
SENSITIVE_EMAIL_ZONES: tuple[str, ...] = ("body", "link")

#: The value classes section 2.9 names as sensitive in an email header. WHICH SLOTS
#: hold an address is format knowledge (RFC 5322 address fields), so the reader says
#: so and P5 does not pattern-match a header name.
SENSITIVE_EMAIL_VALUE_KINDS: tuple[str, ...] = ("address",)

#: Section 2.9, Contacts: "normally privacy-protected rather than used to create
#: folder proposals" - every value of a VCF, with no exception to enumerate.
FULLY_SENSITIVE_SOURCE_TYPES: tuple[str, ...] = ("contacts",)


class UnauthorizedTranscription(Exception):
    """A speech-derived text arrived without P7's explicit policy (section 2.9)."""


class DuplicateUnit(Exception):
    """Two texts claimed one `(run_id, container_path)` key (G1)."""


@dataclass(frozen=True)
class LongTailEntry:
    """One addressable place: a sheet, a slide, a message, an event, a card.

    `kind` is a P4 segment kind. `sheet` and `slide` are indexed; `entry` is
    label-addressed (P4 segment-kind rule 2) and carries the format's own identifier.
    """
    kind: str
    index: int | None = None
    label: str | None = None


@dataclass(frozen=True)
class LongTailValue:
    """One named value from a family's section 2.9 field list.

    `name` is the format's own slot name, verbatim (P4 D7). `kind` is set only where
    section 2.9 names a class P5 must act on - `address` for an email header.
    """
    name: str
    value: str
    entry_ordinal: int | None = None
    kind: str | None = None


@dataclass(frozen=True)
class LongTailText:
    """One stretch of text: a cell, a text box, a body, a note, a caption.

    `region` makes the container path unique where an entry holds several texts; a
    cell uses `row`/`column` instead. `from_speech` marks section 2.9's speech-to-text
    transcript, which no reader may return unless P7 authorized it.
    """
    zone: str
    text: str
    entry_ordinal: int | None = None
    row: int | None = None
    column: int | None = None
    column_header: str | None = None
    region: int | None = None
    time_span: Mapping[str, int] | None = None
    from_speech: bool = False


@dataclass(frozen=True)
class LongTailFile:
    """What an injected `read_long_tail` returns, or None when this deployment ships
    no reader for the format (section 2.4's `unsupported`)."""
    entries: tuple[LongTailEntry, ...] = ()
    values: tuple[LongTailValue, ...] = ()
    texts: tuple[LongTailText, ...] = ()
    iso_dates: Mapping[str, str] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class SensitivitySignal:
    """One located value section 2.9 says to treat as potentially sensitive.

    `observation_index` is the observation's position in the batch, which is the only
    handle that exists at EMIT time -- P4 assigns `observation_key` at write time. The
    index is therefore how a signal is carried, not how it is stored: at write time
    `record_sensitivity_signals` takes P4's assigned keys and the row is keyed on
    `observation_key`, which is what survives a re-run and what P7 can redact against.
    The seam gap that forced position-keying is closed: P4 publishes
    `observation_keys_for_run(conn, run_id)`.
    """
    observation_index: int
    signal: str
    basis: str


@dataclass(frozen=True)
class LongTailResult:
    """The P4 batch, and the signals raised while building it.

    Two values rather than one because P4 conformance rule 6 forbids an
    extractor-private field on an observation, and the signal is per located value so
    it cannot ride on the run either.
    """
    extraction: ExtractionResult
    sensitivity: tuple[SensitivitySignal, ...] = ()


def _entry_segment(entry: LongTailEntry) -> dict:
    return segment(entry.kind, index=entry.index, label=entry.label)


def _entry_path(document: LongTailFile, ordinal: int | None) -> tuple:
    if ordinal is None:
        return ()
    return (_entry_segment(document.entries[ordinal - 1]),)


def _path_key(container_path: tuple) -> tuple:
    """A hashable form of a container path. Segments are P4 mappings, so the key is
    built rather than assumed - G1's uniqueness check needs one and P5 owns no
    locator serialization to borrow."""
    return tuple((s["kind"], s["index"], s["label"]) for s in container_path)


def _text_path(document: LongTailFile, text: LongTailText) -> tuple:
    path = _entry_path(document, text.entry_ordinal)
    if text.row is not None:
        path = path + (segment("row", index=text.row),
                       segment("column", index=text.column,
                               label=text.column_header))
    if text.region is not None:
        path = path + (segment("region", index=text.region),)
    return path


#: Zones whose whole text is itself a located value. A heading, a note and a cell are
#: short labelled positions (sections 2.3 and 2.9); a body and a transcript are bulk
#: text and G1 gives bulk text to `text_units`.
WHOLE_TEXT_ZONES: tuple[str, ...] = ("heading", "notes", "table")


def extract_long_tail(
        *, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
        source_type: str,
        read_long_tail: Callable[..., LongTailFile | None],
        find_structured_strings: Callable[[str], tuple[StructuredString, ...]],
        transcription_authorized: Callable[[], bool],
        now: str, context_window: int) -> LongTailResult:
    """Section 2.9's long-tail families, as P4 records."""
    if source_type not in LONG_TAIL_SOURCE_TYPES:
        raise ValueError(
            f"{source_type!r} is not one of section 2.9's long-tail families "
            f"{LONG_TAIL_SOURCE_TYPES}"
        )
    admit(path, policy=policy)
    transcribe = bool(transcription_authorized())
    document = read_long_tail(path, transcribe=transcribe)
    if document is None:
        return LongTailResult(
            extraction=unsupported_result(
                file_row=file_row, extractor_name=EXTRACTOR_NAME,
                extractor_version=VERSION, analysis_tier=ANALYSIS_TIER,
                source_type=source_type, now=now))

    iso_dates = document.iso_dates
    observations: list[Mapping[str, Any]] = []
    units: list[Mapping[str, Any]] = []
    signals: list[SensitivitySignal] = []

    def emit(*, zone, raw, container_path, span, unit_text, reliability,
             normalized=None, sensitive_basis=None, time_span=None):
        before = after = ""
        truncated = False
        if span is not None and unit_text is not None:
            before, after, truncated = context_for(unit_text, span["start"],
                                                   span["end"], window=context_window)
        # A time-addressed medium locates by time: P4's `location` publishes
        # `text_span` and `time_span` as alternatives, and section 2.8's own
        # audio/video example is a time. The offset still produced the context.
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=source_type, raw_value=raw,
            normalized_value=normalized if normalized is not None
            else normalize_mechanical(raw),
            location=location(zone=zone, container_path=container_path,
                              text_span=None if time_span is not None else span,
                              time_span=time_span),
            context_before=before, context_after=after, context_truncated=truncated,
            observed_at=now, reliability=reliability,
        ))
        basis = sensitive_basis
        if basis is None and source_type in FULLY_SENSITIVE_SOURCE_TYPES:
            basis = ("section 2.9, Contacts: address-book output is normally "
                     "privacy-protected")
        if basis is not None:
            signals.append(SensitivitySignal(observation_index=len(observations) - 1,
                                             signal=POTENTIALLY_SENSITIVE,
                                             basis=basis))

    for value in document.values:
        if not value.value:
            continue                     # presence only; an absence is never a row
        basis = None
        if (source_type == "email"
                and value.kind in SENSITIVE_EMAIL_VALUE_KINDS):
            basis = "section 2.9, Email: addresses are potentially sensitive"
        emit(zone="metadata", raw=value.value,
             container_path=_entry_path(document, value.entry_ordinal)
             + (segment("field", label=value.name),),
             span=None, unit_text=None, reliability="direct",
             normalized=iso_dates.get(value.name), sensitive_basis=basis)

    seen_paths: set[tuple] = set()
    for text in document.texts:
        if text.from_speech and not transcribe:
            raise UnauthorizedTranscription(
                "a speech-to-text transcript arrived without P7's explicit privacy "
                "and compute policy; section 2.9 authorizes one only under it"
            )
        if not text.text:
            continue
        container = _text_path(document, text)
        if _path_key(container) in seen_paths:
            raise DuplicateUnit(
                f"two texts claim the container path {container!r}; `text_units` is "
                "keyed by (run_id, container_path) (G1) and the second would be lost"
            )
        seen_paths.add(_path_key(container))
        units.append(text_unit(text=text.text, container_path=container))
        body_basis = (
            "section 2.9, Email: message content is potentially sensitive"
            if source_type == "email" and text.zone in SENSITIVE_EMAIL_ZONES
            else None)
        if text.zone in WHOLE_TEXT_ZONES:
            emit(zone=text.zone, raw=text.text, container_path=container,
                 span={"start": 0, "end": len(text.text)}, unit_text=text.text,
                 reliability="possible", sensitive_basis=body_basis)
        for found in find_structured_strings(text.text):
            zone = ZONE_BY_STRUCTURED_KIND.get(found.kind, text.zone)
            found_basis = body_basis
            if (found_basis is None and source_type == "email"
                    and zone in SENSITIVE_EMAIL_ZONES):
                found_basis = ("section 2.9, Email: addresses are potentially "
                               "sensitive")
            emit(zone=zone, raw=text.text[found.start:found.end],
                 container_path=container,
                 span={"start": found.start, "end": found.end},
                 unit_text=text.text, reliability="possible",
                 sensitive_basis=found_basis, time_span=text.time_span)

    entries = len(document.entries) or 1
    return LongTailResult(
        extraction=ExtractionResult(
            run=run(file_id=file_row["file_id"],
                    content_hash=file_row["content_hash"],
                    extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                    source_type=source_type, analysis_tier=ANALYSIS_TIER,
                    config={"reader": "injected", "transcribe": transcribe},
                    completeness="complete",
                    coverage=coverage("entries", entries, entries),
                    observation_count=len(observations), started_at=now,
                    finished_at=now),
            observations=tuple(observations),
            text_units=tuple(units)),
        sensitivity=tuple(signals),
    )


SENSITIVITY_DDL = """
CREATE TABLE IF NOT EXISTS extraction_sensitivity_signal (
    signal_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL,
    observation_key TEXT NOT NULL,   -- P4's handle, not a batch position
    signal          TEXT NOT NULL,
    basis           TEXT NOT NULL,
    observed_at     TEXT NOT NULL,
    UNIQUE (run_id, observation_key)
);
"""


def record_sensitivity_signals(conn: sqlite3.Connection, *, run_id: str,
                               signals: Sequence[SensitivitySignal],
                               observation_keys: Sequence[str],
                               now: str) -> int:
    """Persist the signals for one written batch. Returns how many were stored.

    `observation_keys` is P4's assignment for this batch, in emit order --
    `evidence_shape.store.observation_keys_for_run(conn, run_id)`. It is required with
    no default: a default would let a caller store a batch position in a column named
    `observation_key`, which is the two-vocabularies defect wearing the right name.
    """
    for signal in signals:
        if signal.observation_index >= len(observation_keys):
            raise IndexError(
                f"signal at batch position {signal.observation_index} has no key: "
                f"P4 assigned {len(observation_keys)} for run {run_id}")
        conn.execute(
            "INSERT INTO extraction_sensitivity_signal (run_id, observation_key, "
            "signal, basis, observed_at) VALUES (?, ?, ?, ?, ?)",
            (run_id, observation_keys[signal.observation_index],
             signal.signal, signal.basis, now),
        )
    return len(signals)


def sensitivity_signals_for(conn: sqlite3.Connection,
                            run_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM extraction_sensitivity_signal WHERE run_id = ? "
        # signal_id is insertion order, which is emit order: `observation_index`
        # is no longer a column, the row is keyed on P4's `observation_key`.
        "ORDER BY signal_id", (run_id,)).fetchall()
