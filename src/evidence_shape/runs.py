# src/evidence_shape/runs.py
"""Record 2 -- `extraction_runs`, one row per (file version × extractor).

D5: two records for outcomes, not one. §2.4 forbids conflating "unsupported format"
with "empty document"; §2.5 requires "partially inspected"; §2.7 requires provider,
version, languages, configuration and whether extraction was complete or capped be
preserved; §2.9 requires "indexed-but-unreadable"; §8.6 requires the deferred stage
be marked. None of those can live on an observation, because the cases that need them
produce ZERO observations.

B1 makes this THE extraction-outcome record for the whole system: P5 writes one row
per (file version × extractor) and publishes no parallel status vocabulary of its own.
An opaque image runs the image extractor and OCR, which is two rows -- one may be
`complete` while the other is `capped`.

Absence is recorded here or nowhere. A `complete` run that emitted no `metadata`
observations IS the record that the file carried no such metadata; §2.6's "no EXIF"
is exactly this case. No field is added for it and no observation is written for it.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from evidence_shape.canonical import canonical_json, sha256_of
from evidence_shape.vocabulary import (
    ANALYSIS_TIERS, COMPLETENESS, SOURCE_TYPES, check,
)

#: The SPEC's Record 2, in the SPEC's order.
RUN_FIELDS: tuple[str, ...] = (
    "run_id", "file_id", "content_hash", "extractor_name", "extractor_version",
    "source_type", "analysis_tier", "config", "config_fingerprint", "completeness",
    "coverage", "observation_count", "started_at", "finished_at", "failure_reason",
)

#: §2.4, §2.9. Free text, and only for a run that did not complete on its own terms.
_FAILURE_COMPLETENESS = frozenset({"unreadable", "failed"})


class MalformedRun(ValueError):
    """A non-conforming run record. P4 fails it rather than coercing it."""


def config_fingerprint(config: Mapping) -> str:
    """So §3.4's cache key and §8.5's diff can tell two configurations apart."""
    return sha256_of(canonical_json(config))


_fingerprint = config_fingerprint


@dataclass(frozen=True, slots=True)
class Coverage:
    """§8.6's "how far it got". `units` is caller-supplied: §8.6 names none."""

    units: str
    processed: int
    total: int

    def __post_init__(self) -> None:
        if not isinstance(self.units, str) or not self.units:
            raise MalformedRun("coverage.units is a non-empty string")
        for name in ("processed", "total"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise MalformedRun(f"coverage.{name} is a non-negative integer")
        if self.processed > self.total:
            raise MalformedRun("coverage.processed <= coverage.total")

    def to_mapping(self) -> dict[str, object]:
        return {"units": self.units, "processed": self.processed, "total": self.total}


@dataclass(frozen=True, slots=True)
class ExtractionRun:
    """What happened when one extractor ran over one content version."""

    run_id: str
    file_id: str
    content_hash: str
    extractor_name: str
    extractor_version: str
    source_type: str
    analysis_tier: str
    config: Mapping
    completeness: str
    started_at: str
    observation_count: int = 0
    coverage: Coverage | None = None
    finished_at: str | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("run_id", "file_id", "content_hash", "extractor_name",
                     "extractor_version", "started_at"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise MalformedRun(f"{name} is a non-empty string, not {value!r}")
        check(self.source_type, SOURCE_TYPES, name="source_type")
        # I4: "A value outside the four is rejected."
        check(self.analysis_tier, ANALYSIS_TIERS, name="analysis_tier")
        check(self.completeness, COMPLETENESS, name="completeness")
        if not isinstance(self.config, Mapping):
            raise MalformedRun("config is a mapping; P4 defines no schema for it")
        if self.coverage is not None and not isinstance(self.coverage, Coverage):
            raise MalformedRun("coverage is a Coverage or None")
        if type(self.observation_count) is not int or self.observation_count < 0:
            raise MalformedRun("observation_count is a non-negative integer")
        if self.failure_reason is not None:
            if not isinstance(self.failure_reason, str):
                raise MalformedRun("failure_reason is free text or None")
            if self.completeness not in _FAILURE_COMPLETENESS:
                raise MalformedRun(
                    f"failure_reason belongs to completeness in "
                    f"{sorted(_FAILURE_COMPLETENESS)}, not {self.completeness!r}: a "
                    "capped run did not fail, and metadata_only is a deliberate "
                    "policy stop (§2.9), not a gap in the product")

    @property
    def config_fingerprint(self) -> str:
        return _fingerprint(self.config)

    def to_mapping(self) -> dict[str, object]:
        mapping = {
            "run_id": self.run_id, "file_id": self.file_id,
            "content_hash": self.content_hash, "extractor_name": self.extractor_name,
            "extractor_version": self.extractor_version,
            "source_type": self.source_type, "analysis_tier": self.analysis_tier,
            "config": dict(self.config), "config_fingerprint": self.config_fingerprint,
            "completeness": self.completeness,
            "coverage": None if self.coverage is None else self.coverage.to_mapping(),
            "observation_count": self.observation_count,
            "started_at": self.started_at, "finished_at": self.finished_at,
            "failure_reason": self.failure_reason,
        }
        return {name: mapping[name] for name in RUN_FIELDS}


def run_from_mapping(mapping: Mapping[str, object]) -> ExtractionRun:
    missing = [name for name in RUN_FIELDS
               if name != "config_fingerprint" and name not in mapping]
    if missing:
        raise MalformedRun(f"missing run fields: {missing}")
    unknown = sorted(set(mapping) - set(RUN_FIELDS))
    if unknown:
        raise MalformedRun(f"{unknown} are not fields of the run record")
    coverage = mapping["coverage"]
    run = ExtractionRun(
        run_id=mapping["run_id"], file_id=mapping["file_id"],
        content_hash=mapping["content_hash"],
        extractor_name=mapping["extractor_name"],
        extractor_version=mapping["extractor_version"],
        source_type=mapping["source_type"], analysis_tier=mapping["analysis_tier"],
        config=mapping["config"], completeness=mapping["completeness"],
        started_at=mapping["started_at"],
        observation_count=mapping["observation_count"],
        coverage=coverage if coverage is None or isinstance(coverage, Coverage)
        else Coverage(coverage["units"], coverage["processed"], coverage["total"]),
        finished_at=mapping["finished_at"], failure_reason=mapping["failure_reason"],
    )
    stated = mapping.get("config_fingerprint")
    if stated is not None and stated != run.config_fingerprint:
        raise MalformedRun(
            f"config_fingerprint {stated!r} is not the fingerprint of this config; "
            "§3.4's cache key would then name a configuration that never ran")
    return run
