# src/extractors/runs.py
"""What P5 owes about a run, derived - and nothing that names an outcome.

B1: "P4's `extraction_runs` is THE record. P5's parallel status vocabulary is
deleted." The nine `completeness` values are P4's and are not restated here; what is
here is the coverage helper, section 3.4's cache key, and the analysis-tier map I4
gave P5.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from extractors.shape import ANALYSIS_TIERS, canonical_json

#: I4, closed. SPEC: "filesystem observations re-emitted as `source_type: filesystem`
#: are `filesystem`; E1-E5 are `native`; E6 is `ocr`."
ANALYSIS_TIER_BY_EXTRACTOR: dict[str, str] = {
    "filesystem.record": "filesystem",
    "pdf.text": "native",
    "docx.structure": "native",
    "text.structured": "native",
    "archive.manifest": "native",
    "image.metadata": "native",
}

#: Section 2.7's OCR provider is named by the ENGINE, not by P5 - S1 makes Apple
#: Vision the one engine v1 ships and the engine reports its own name and version
#: (section 2.7, "OCR provider and version"). Keying the tier on the family prefix
#: means a second provider needs no edit here and P5 spells no provider name.
OCR_EXTRACTOR_PREFIX = "ocr."


class TierConflict(Exception):
    """Two runs landed on one analysis tier with different outcomes.

    In the normal case each tier has at most one run per file: the router selects one
    native extractor, the filesystem record is its own run, and OCR is its own tier.
    The design does not rule on the collision, so P5 refuses rather than picking a
    winner and losing the other outcome.
    """


def analysis_tier_for(extractor_name: str) -> str:
    """The tier this extractor writes. Never guessed for an unknown name."""
    if extractor_name.startswith(OCR_EXTRACTOR_PREFIX):
        return "ocr"
    return ANALYSIS_TIER_BY_EXTRACTOR[extractor_name]


def coverage(units: str, processed: int, total: int) -> Mapping[str, Any]:
    """P4's `coverage {units, processed, total}` - "says how far it got".

    Section 8.6 needs it to make "89 scanned PDFs deferred after the OCR limit"
    computable rather than estimated, so a run may not claim more progress than the
    work it was given.
    """
    if processed < 0 or total < 0:
        raise ValueError(f"coverage cannot be negative: {processed}/{total}")
    if processed > total:
        raise ValueError(
            f"coverage claims {processed} of {total} {units}; a run cannot process "
            "more units than it had"
        )
    return {"units": units, "processed": processed, "total": total}


def cache_key(*, content_hash: str, extractor_name: str, extractor_version: str,
              analysis_tier: str, config_fingerprint: str) -> str:
    """Section 3.4's key, as the SPEC quotes it: "Content hash + extractor version +
    `analysis_tier`, plus provider/version/configuration for OCR."

    Provider is `extractor_name` and configuration is `config_fingerprint`, so there
    is one key shape and no OCR-specific one (B1). There is no `path` parameter: that
    absence is what "a rename is free and a content rewrite is expensive" means.
    """
    return canonical_json([content_hash, extractor_name, extractor_version,
                           analysis_tier, config_fingerprint])


def extraction_status_by_tier(runs: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    """Section 8.2's "extraction status by extractor tier", as a map.

    A missing key means that tier was not attempted. P1 stores the map opaquely on
    `files.extraction_status_by_tier`; P1 publishes no setter for it and `files` is
    P1's table, so this function computes the map and a caller hands it over.
    """
    status: dict[str, str] = {}
    for run in runs:
        tier = run["analysis_tier"]
        if tier not in ANALYSIS_TIERS:
            raise ValueError(f"{tier!r} is not one of I4's four tiers")
        if tier == "llm":
            raise ValueError("P8 is the only writer of `llm` (I4); P5 writes none")
        existing = status.get(tier)
        if existing is not None and existing != run["completeness"]:
            raise TierConflict(
                f"two runs at tier {tier!r} disagree: {existing!r} and "
                f"{run['completeness']!r}. The design does not rule on this and P5 "
                "does not pick a winner."
            )
        status[tier] = run["completeness"]
    return status
