# src/extractors/budgets.py
"""Section 8.6 - the four ceilings P5 consumes, deferral, and the count line.

G4 gives the section 8.6 configuration object to P1, namespaced. P5 names four of
P1's fifteen keys and stores no value; the membership check below runs at import, so
a rename in P1 is an ImportError here rather than a silent drift.

Section 8.6's degradation order puts P5 in the cheap tier with one expensive tail:
"Direct facts and high-precision rules run first ... Full local extraction and OCR run
within the configured budget." Every P5 budget lives on that tail.

"Cost exhaustion must never turn into lower-quality automatic classification." So a
deferred run carries no evidence, and this module publishes no fallback extractor, no
filename guess and no downgraded mode. There is nothing to downgrade to.
"""
from __future__ import annotations

import sqlite3
from typing import Any, Iterable, Mapping

from database_agent.budget import CEILING_KEYS, get_ceiling

from extractors.runs import coverage
from extractors.shape import run
from extractors.sink import ExtractionResult

#: Section 8.6's "Maximum pages OCRed per file / Maximum OCR time per file / Maximum
#: OCR time per scan / Maximum image-analysis operations per scan", in P1's spelling.
P5_CEILING_KEYS: tuple[str, ...] = (
    "ocr.max_pages_per_file",
    "ocr.max_time_per_file",
    "ocr.max_time_per_scan",
    "image.max_analysis_ops_per_scan",
)

_unknown = set(P5_CEILING_KEYS) - set(CEILING_KEYS)
if _unknown:
    raise ImportError(
        f"P5 names ceiling keys P1 does not publish: {sorted(_unknown)}. P1 owns the "
        "section 8.6 configuration object (G4) and P5 defines no key of its own."
    )

#: Section 8.6's "89 scanned PDFs deferred after the OCR limit" - one query.
DEFERRED_COMPLETENESS: tuple[str, ...] = ("deferred", "capped")

#: Section 8.6's "18 files remain unreadable" - a different query against different
#: values (B1). The two sets are disjoint and stay that way.
UNREADABLE_COMPLETENESS: tuple[str, ...] = ("unreadable", "failed")


def p5_ceilings(conn: sqlite3.Connection) -> dict[str, int | None]:
    """The four values P1 holds for P5. `None` means P1 holds none yet.

    Reading a ceiling is not enforcing it, and P5 enforces none here: the OCR engine
    and the image reader are given their ceilings and report that they stopped.
    """
    return {key: get_ceiling(conn, key) for key in P5_CEILING_KEYS}


def deferred_result(*, file_row: Mapping[str, Any], source_type: str,
                    extractor_name: str, extractor_version: str,
                    analysis_tier: str, units: str, total: int,
                    now: str) -> ExtractionResult:
    """The run for an extractor the budget stopped before it started.

    No `failure_reason`: P4's `completeness: deferred` IS section 8.6's mark, and a
    deferral carrying a failure reason reads as a failure - which is exactly the
    confusion section 8.6 exists to prevent. The reason lives in section 8.2's
    structured explanation on the `extraction` event.
    """
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=extractor_name, extractor_version=extractor_version,
                source_type=source_type, analysis_tier=analysis_tier, config={},
                completeness="deferred", coverage=coverage(units, 0, total),
                observation_count=0, started_at=now, finished_at=now))


def extraction_counts(runs: Iterable[Mapping[str, Any]], *,
                      files_scanned: int) -> dict[str, int]:
    """Section 8.6's user-facing sentence, as four queries over P4's `completeness`.

    Two file counts and two run counts, which is the SPEC's own asymmetry: a capped
    OCR run on a file whose EXIF read fine is a deferred RUN, and the file is not
    fully extracted. "Files require model review" is P8's count and is absent.
    """
    by_file: dict[str, list[str]] = {}
    deferred = unreadable = 0
    for record in runs:
        by_file.setdefault(record["file_id"], []).append(record["completeness"])
        if record["completeness"] in DEFERRED_COMPLETENESS:
            deferred += 1
        if record["completeness"] in UNREADABLE_COMPLETENESS:
            unreadable += 1
    fully = sum(1 for states in by_file.values()
                if all(state == "complete" for state in states))
    return {
        "files_scanned": files_scanned,
        "indexed": len(by_file),
        "fully_extracted": fully,
        "deferred": deferred,
        "unreadable": unreadable,
    }
