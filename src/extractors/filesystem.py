# src/extractors/filesystem.py
"""O5 - P3's section 1.2 record, re-emitted as `source_type: filesystem` observations.

"P3 computes the section 1.2 basic filesystem record; P5 emits `source_type:
filesystem` observations referencing it, NEVER recomputing it." This module reads
values out of a `files` row. It stats nothing, opens nothing, hashes nothing,
normalizes no filename and determines no MIME type - O5's stated reason is drift:
"the two would drift and section 3.4's cache key is built on the hash."

Also here, because they are made of the same material: the run a file gets when the
router found no extractor for it. Section 2.4 forbids the three cases being one:

    unsupported     no extractor exists           zero observations
    metadata_only   section 2.9's safe stop       zero observations; the FILESYSTEM
                                                  run above is how the file is still
                                                  indexed (P4 fixture 19)
    unreadable      indexed-but-unreadable        carries metadata-level rows (M3)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from extractors.runs import coverage
from extractors.safety import SafetyPolicy, admit
from extractors.shape import context_for, location, observation, run, segment, text_unit
from extractors.sink import ExtractionResult

VERSION = "0.1.0"
EXTRACTOR_NAME = "filesystem.record"
SOURCE_TYPE = "filesystem"
ANALYSIS_TIER = "filesystem"

#: Named slots on P3's row that become `direct` observations at zone `metadata`.
#: Section 2.9's remaining basic-extraction fields are deliberately absent: G5 gives
#: duplicate and version-family signals to P6 "from P1's content hashes", and G6
#: gives the bounded download session to P6 "computed from P3 timestamps". P6 reads
#: those from `files`; a second copy here would be two homes for one value.
METADATA_SLOTS: tuple[str, ...] = ("normalized_filename", "extension", "mime_type")


def extract_filesystem(*, file_row: Mapping[str, Any], path: Path,
                       policy: SafetyPolicy, now: str,
                       context_window: int) -> ExtractionResult:
    """One run whose observations are P3's record, made citable.

    The filename gets the run's single `container_path: ()` text unit, so P4's
    fixture 11 (`filename#0-6`, a SPAN into the filename) has a unit to index into.
    `text_units` is keyed by (run_id, container_path), so a run holds exactly one
    unit at `()`; the parent-folder observation therefore carries no span and
    degrades to the coarser address, which is P4's segment-kind rule 4.
    """
    admit(path, policy=policy)

    filename = file_row["filename"]
    observations = []
    before, after, truncated = context_for(filename, 0, len(filename),
                                           window=context_window)
    observations.append(observation(
        file_id=file_row["file_id"], content_hash=file_row["content_hash"],
        extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
        source_type=SOURCE_TYPE, raw_value=filename,
        location=location(zone="filename", text_span={"start": 0,
                                                      "end": len(filename)}),
        context_before=before, context_after=after, context_truncated=truncated,
        observed_at=now, reliability="possible",
    ))

    parent = file_row.get("directory_position")
    if parent:
        # MINOR 11: section 2.9's name for this value is "parent-folder context";
        # `directory_position` is only the column P1 stores it in.
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=parent,
            location=location(zone="path"),
            observed_at=now, reliability="possible",
        ))

    for slot in METADATA_SLOTS:
        value = file_row.get(slot)
        if not value:
            continue        # an observation records presence, never absence
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=SOURCE_TYPE, raw_value=str(value),
            location=location(zone="metadata",
                              container_path=(segment("field", label=slot),)),
            observed_at=now, reliability="direct",
        ))

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=SOURCE_TYPE, analysis_tier=ANALYSIS_TIER, config={},
                completeness="complete", coverage=coverage("files", 1, 1),
                observation_count=len(observations), started_at=now, finished_at=now),
        observations=tuple(observations),
        text_units=(text_unit(text=filename),),
    )


def unrouted_result(*, file_row: Mapping[str, Any], decision,
                    now: str) -> ExtractionResult:
    """The run a file gets when the router found no extractor for it.

    Section 2.4: "The system should never silently treat an unsupported format as an
    empty document, because an empty extraction result is different from an extractor
    that does not yet exist." Which of P4's three values applies is the router's
    decision; what it means in rows is here.
    """
    completeness = decision.unrouted_completeness
    source_type = decision.source_type or "opaque_binary"
    observations: list[Mapping[str, Any]] = []
    failure_reason = None

    if completeness == "unreadable":
        # M3 and section 2.9: "unsupported proprietary formats should be recorded as
        # indexed-but-unreadable rather than silently treated as empty", and its
        # metadata-level rows - "at minimum filename, format" - are what "indexed"
        # means. Both come from P3's row: reading the format is exactly what there is
        # no library for.
        failure_reason = (
            f"no extractor exists for {decision.detected_format or 'this format'}; "
            "recorded as indexed-but-unreadable (section 2.9, M3)"
        )
        observations.append(observation(
            file_id=file_row["file_id"], content_hash=file_row["content_hash"],
            extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
            source_type=source_type, raw_value=file_row["filename"],
            location=location(zone="filename"),
            observed_at=now, reliability="possible",
        ))
        detected = decision.detected_format
        if detected:
            observations.append(observation(
                file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, raw_value=detected,
                location=location(zone="metadata",
                                  container_path=(segment("field", label="format"),)),
                observed_at=now, reliability="direct",
            ))

    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=EXTRACTOR_NAME, extractor_version=VERSION,
                source_type=source_type, analysis_tier=ANALYSIS_TIER, config={},
                completeness=completeness,
                coverage=coverage("files", 0, 1),
                observation_count=len(observations), started_at=now, finished_at=now,
                failure_reason=failure_reason),
        observations=tuple(observations),
    )
