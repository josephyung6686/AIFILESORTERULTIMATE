# src/extractors/image.py
"""E5 - images (section 2.6).

"Images require their own extraction pipeline because filenames often carry little
semantic meaning."

E5 exposes section 2.6's hierarchy of signals and resolves nothing. It emits no
photo/screenshot conclusion - `media type` is a Photos-domain fact (section 3.11) and
belongs to P6 - it writes no row about an absence, and it writes no conflict row:
"conflicting signals should lead to abstention rather than an invented
classification", and the abstention is section 3.7's margin rule, which is P6's.

Three of section 2.6's inputs are Deferred - which display resolutions are "exact",
which aspect ratios are "sensor-shaped", and the camera-filename pattern set - so
`dimension_signal` and `filename_pattern` are required keywords with no default and
no list of any of the three exists in this package.

File size and content hash are section 1.2's and P1's. O5 gives them to the
`filesystem` run and P5 recomputes neither, so neither appears here even though
section 2.6 lists both.
"""
from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.failure import unsupported_result
from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import (
    location, normalize_mechanical, observation, run, segment,
)
from extractors.long_tail import POTENTIALLY_SENSITIVE, SensitivitySignal
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "image.metadata"
SOURCE_TYPE = "image"
ANALYSIS_TIER = "native"

#: Section 2.6's hierarchy, as section 2.6 states it: "camera EXIF is strong photo
#: evidence; capture time, GPS, and sensor-shaped dimensions reinforce it; exact
#: display resolutions, PNG format, and software metadata may support a screenshot
#: hypothesis". P4's `signal_tier` is where each lands (M2), so the hierarchy is
#: carried on the record and never re-derived downstream.
SIGNAL_TIER: dict[str, int] = {
    "camera EXIF": 1,
    "capture time": 2,
    "GPS": 2,
    "sensor-shaped dimensions": 2,
    "exact display resolution": 3,
    "PNG format": 3,
    "software metadata": 3,
}

#: The two section 2.6 signals that are readings of the pixel dimensions. A caller
#: returns at most one: the design gives no tiebreak for dimensions that are both,
#: and P5 invents none. See NEEDS JOSEPH.
DIMENSION_SIGNALS: tuple[str, str] = ("sensor-shaped dimensions",
                                      "exact display resolution")

#: Section 2.6 names "PNG format" as a tier-3 signal, so this token is the design's
#: and not a format list of P5's. The comparison folds case on one word.
PNG_FORMAT = "PNG"

#: Section 2.6's own names for the slots that are not EXIF tags.
FORMAT_FIELD = "format"
DIMENSIONS_FIELD = "pixel dimensions"
PERCEPTUAL_HASH_FIELD = "perceptual hash"
FILENAME_PATTERN_FIELD = "filename pattern"

#: Why every EXIF tag is signalled, recorded on the row. `00` §8.4's own words, so
#: the reason travels with the signal instead of living in a commit message.
EXIF_BASIS: str = (
    "§8.4 places image EXIF and GPS in the always-local set; the zone a tag is "
    "emitted into is `metadata`, which is releasable and truthful for it")


class UnknownSignal(Exception):
    """A signal name section 2.6's hierarchy does not contain."""


@dataclass(frozen=True)
class ExifValue:
    """One EXIF tag, at the format's own tag name (P4 D7).

    `kind` is which of section 2.6's signals this tag is. WHICH TAG IS WHICH is
    library knowledge - EXIF tag names are an external, versioned vocabulary - so the
    reader classifies and P5 places. An `orientation` tag that section 2.6 lists but
    does not rank carries `kind=None` and no tier.
    """
    name: str
    value: str
    kind: str | None = None


@dataclass(frozen=True)
class ImageRecord:
    """What an injected `read_image` returns.

    `dimensions` is the format's own rendering of the pair, verbatim, because a raw
    value is never constructed by P5 (RAW-1); `width` and `height` are ints supplied
    for the caller's dimension signal and are emitted nowhere.
    """
    image_format: str
    dimensions: str
    width: int
    height: int
    perceptual_hash: str | None = None
    exif: tuple[ExifValue, ...] = ()
    color: Mapping[str, str] = dataclass_field(default_factory=dict)
    software: Mapping[str, str] = dataclass_field(default_factory=dict)


@dataclass(frozen=True)
class ImageResult:
    """The P4 batch, and §8.4's always-local signals raised while building it.

    Two values rather than one, for the reason `long_tail.LongTailResult` gives: P4
    conformance rule 6 forbids an extractor-private field on an observation, and the
    signal is per located value so it cannot ride on the run either.

    ADDED 2026-09-02 against the security review's CR-05b. Every EXIF tag is emitted
    into `zone="metadata"` -- which is the truthful zone for one, so P7's always-local
    ZONE rule cannot reach it, and a GPS coordinate came back `Released` from the real
    gate. `ZONES` has no `exif` member to move them to and adding one needs owner
    approval and a `SHAPE_VERSION` bump; the signal is the channel the design already
    has for "this located value is sensitive", and it is the one WR-07 records as
    missing for every format but E3's.
    """

    extraction: ExtractionResult
    sensitivity: tuple[SensitivitySignal, ...] = ()

    def __post_init__(self) -> None:
        """Every signal indexes into the batch beside it, checked HERE.

        The same invariant `LongTailResult` states, for the same reason: this is the
        only place a batch position and the batch it indexes into exist side by side.
        By the time `record_sensitivity_signals` sees them a database is open, and a
        position past the end raises `IndexError`, which nothing catches.
        """
        held = len(self.extraction.observations)
        beyond = [s.observation_index for s in self.sensitivity
                  if not 0 <= s.observation_index < held]
        if beyond:
            raise ValueError(
                f"sensitivity signals at batch positions {beyond} index outside a "
                f"batch of {held}; `observation_index` is a position in THIS "
                "extraction's observations (D10 collapses and renumbers them)")


def _tier(signal: str | None) -> int | None:
    if signal is None:
        return None
    if signal not in SIGNAL_TIER:
        raise UnknownSignal(
            f"{signal!r} is not one of section 2.6's signals {tuple(SIGNAL_TIER)}"
        )
    return SIGNAL_TIER[signal]


def extract_image(*, file_row: Mapping[str, Any], path: Path, policy: SafetyPolicy,
                  read_image: Callable[[Path], ImageRecord],
                  dimension_signal: Callable[[int, int], str | None],
                  filename_pattern: Callable[[str], str | None],
                  now: str, context_window: int) -> ImageResult:
    """Section 2.6's fields, as P4 records, with the hierarchy on the record.

    `context_window` builds no context here: every value is a whole metadata slot
    with no surrounding text, so P4's three context fields are empty. It is still
    recorded in the run's `config` (B4) so the six extractors have one calling shape
    AND one fingerprinted configuration -- a run whose config omits the budget it was
    given cannot be told apart from one given a different budget, and which
    extractors happen to consume it is not a distinction section 8.5's replay makes.
    """
    admit(path, policy=policy)
    record = read_image(path)
    if record is None:
        # §2.4: no reader for this format in this deployment. `unsupported`, never
        # `failed` -- the bytes were never looked at, so a `failed` run would report
        # a missing library as a corrupt file.
        # Wrapped, so this function has ONE return type. A bare `ExtractionResult`
        # on the early path and an `ImageResult` on the late one would make every
        # caller test which it got, and the caller that forgot would drop §8.4's
        # signals on the path that has them.
        return ImageResult(extraction=unsupported_result(
            file_row=file_row, extractor_name=EXTRACTOR_NAME,
            extractor_version=VERSION, source_type=SOURCE_TYPE,
            analysis_tier=ANALYSIS_TIER, now=now))


    observations: list[Mapping[str, Any]] = []
    #: Positions in the SUBMITTED list, remapped through `collapsed_index` below.
    #: Recorded rather than recomputed from the finished batch: after D10 there is no
    #: way to tell an EXIF tag from any other `metadata` row, which is the whole
    #: reason P7 could not refuse one.
    exif_positions: list[int] = []

    def emit(*, zone, raw, label, reliability, signal=None):
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=raw,
            normalized_value=normalize_mechanical(raw),
            location=location(zone=zone,
                              container_path=(segment("field", label=label),)
                              if label is not None else ()),
            observed_at=now, reliability=reliability, signal_tier=_tier(signal),
        ))

    emit(zone="metadata", raw=record.image_format, label=FORMAT_FIELD,
         reliability="direct",
         signal="PNG format"
         if record.image_format.strip().upper() == PNG_FORMAT else None)

    chosen = dimension_signal(record.width, record.height)
    if chosen is not None and chosen not in DIMENSION_SIGNALS:
        raise UnknownSignal(
            f"{chosen!r} is not one of section 2.6's two readings of the pixel "
            f"dimensions {DIMENSION_SIGNALS}"
        )
    emit(zone="metadata", raw=record.dimensions, label=DIMENSIONS_FIELD,
         reliability="direct", signal=chosen)

    if record.perceptual_hash:
        emit(zone="metadata", raw=record.perceptual_hash,
             label=PERCEPTUAL_HASH_FIELD, reliability="direct")

    for tag in record.exif:
        if not tag.value:
            continue                    # presence only; an absence is never a row
        # §8.4 puts `image_exif` in the always-local nine, and `record.exif` IS the
        # EXIF tags -- so the position is noted for EVERY one, not for the ranked
        # kinds only. `gps` is a second member of the nine and arrives inside this
        # same loop, which is why keying on `kind` would have been the narrower and
        # wrong rule. No tag-name list is needed anywhere: the reader classifies and
        # P5 places, exactly as `ExifValue`'s docstring says.
        exif_positions.append(len(observations))
        emit(zone="metadata", raw=tag.value, label=tag.name, reliability="direct",
             signal=tag.kind)

    for slot in sorted(record.color):
        if record.color[slot]:
            emit(zone="metadata", raw=record.color[slot], label=slot,
                 reliability="direct")

    for slot in sorted(record.software):
        if record.software[slot]:
            emit(zone="metadata", raw=record.software[slot], label=slot,
                 reliability="direct", signal="software metadata")

    matched = filename_pattern(file_row["filename"])
    if matched:
        # Zone `filename`, and no span: the filename's text unit belongs to the
        # `filesystem` run and P4 conformance rule 10 keys units on the SAME run, so
        # this degrades to the coarser address (P4 segment-kind rule 4).
        emit(zone="filename", raw=matched, label=None, reliability="possible")

    extraction = ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER,
                config={"reader": "injected",
                        "context_window": context_window},
                completeness="complete",
                coverage=coverage("images", 1, 1),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
    )

    # D10 collapsed and renumbered, so a submitted position is mapped through before
    # it leaves this function -- after this point nothing remembers what the
    # submitted list looked like. The identical step `long_tail` takes, and for the
    # identical reason.
    #
    # Two tags can land on one survivor: `DateTime` and `DateTimeOriginal` agree on
    # almost every photo, and once collapsed they ARE one located value. One located
    # value gets one row -- `extraction_sensitivity_signal` is UNIQUE on (run_id,
    # observation_key) -- so the first is kept and the rest dropped rather than
    # written. A tag can also collapse onto an EARLIER non-EXIF row carrying the same
    # string, and then that row is the one signalled: it is now the row that carries
    # the EXIF value, and D10's rule is one row per located value.
    seen: set[int] = set()
    signals: list[SensitivitySignal] = []
    for position in exif_positions:
        moved = extraction.collapsed_index[position]
        if moved in seen:
            continue
        seen.add(moved)
        signals.append(SensitivitySignal(
            observation_index=moved, signal=POTENTIALLY_SENSITIVE,
            basis=EXIF_BASIS))

    return ImageResult(extraction=extraction, sensitivity=tuple(signals))
