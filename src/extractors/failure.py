# src/extractors/failure.py
"""§2.4's `completeness = failed` — the run a file gets when its reader raised.

`src/extractors/` contained **zero** `except` until this module. A password-protected
PDF, a corrupt ZIP, a truncated DOCX or any reader that raised propagated out of the
extractor and ended the scan. `failed` is in P4's vocabulary and in conformance rule 9,
and nothing produced it — so a real corpus, which always has such files, could not be
scanned to the end.

**The exception is the signal.** There is no threshold here for "too corrupt", no
retry count, and no judgement about the file: a reader either returned or it raised,
and raising is the fact recorded. §2.4's rule is that an unsupported or unreadable
file must never be *"silently treated as an empty document"*, and a crashed scan is a
worse version of the same lie — the file is not empty, it is unexamined, and the run
row is what says so.
"""
from __future__ import annotations

from typing import Any, Mapping

from extractors.shape import run
from extractors.sink import ExtractionResult


def failed_result(*, file_row: Mapping[str, Any], error: BaseException,
                  extractor_name: str, extractor_version: str,
                  source_type: str, now: str,
                  analysis_tier: str = "native") -> ExtractionResult:
    """The run for a reader that raised. Zero observations, per P4 rule 9.

    `failure_reason` carries the exception's type and message and nothing else. It is
    not a diagnosis and not a classification: P5 does not decide whether the file is
    encrypted, truncated or malformed, because deciding that would require the read
    that just failed.
    """
    return ExtractionResult(
        run=run(file_id=file_row["file_id"], content_hash=file_row["content_hash"],
                extractor_name=extractor_name, extractor_version=extractor_version,
                source_type=source_type, analysis_tier=analysis_tier, config={},
                completeness="failed",
                coverage={"units": "files", "processed": 0, "total": 1},
                observation_count=0, started_at=now, finished_at=now,
                failure_reason=f"{type(error).__name__}: {error}"),
        observations=(), text_units=(),
    )
