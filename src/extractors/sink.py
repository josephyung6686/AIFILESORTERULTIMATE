# src/extractors/sink.py
"""The P4 write seam.

`evidence`, `extraction_runs` and `text_units` are P4's tables. P5 creates none of
them and writes none of them directly: an extractor returns ONE `ExtractionResult` -
the run plus every observation and text unit it produced - and a sink writes it.

Why one batch rather than open/append/close: it is atomic, so there is no
half-written run; P4's conformance rule 9 ("unsupported, deferred and failed runs
carry zero observations") is checkable at the boundary; and section 8.5's determinism
comparison becomes a comparison of two whole batches rather than of two row streams.

The real sink is P4's. `RecordingSink` in tests/p5/conftest.py is the test one; when
P4 lands, the only change is which object the caller constructs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class ExtractionResult:
    """One run and everything it produced. The unit P5 hands to P4."""
    run: Mapping[str, Any]
    observations: tuple[Mapping[str, Any], ...] = ()
    text_units: tuple[Mapping[str, Any], ...] = ()

    def __post_init__(self) -> None:
        """P4 D10 is applied HERE, once, for every extractor.

        D10: one observation per (run, exact raw value, zone); `occurrence_count`
        counts within that zone and `location` addresses the FIRST occurrence in
        document order. Six extractors promised it and two delivered -- `_collapse`
        lived in `pdf.py` and `archive.py` only, so DOCX, structured text, long-tail,
        OCR, image and filesystem emitted one row per hit. That explodes row counts
        and splits P6's §3.7 weight across clones of one string, and it passed every
        test because no test read the same value twice from those formats.

        Collapsing at the result rather than in each emitter fixes six at one point
        and means a seventh extractor inherits it instead of silently skipping it --
        every extractor already constructs exactly this object.

        Exact raw match, because P4 makes no normalization judgement: `Columbia` and
        `columbia` stay two observations and cross-form aggregation is P6's.
        Idempotent: a batch `pdf.py` already collapsed sums its counts rather than
        double-counting.
        """
        object.__setattr__(self, "observations", _collapse(self.observations))


def _collapse(observations):
    first: dict[tuple, dict] = {}
    order: list[tuple] = []
    for candidate in observations:
        zone = (candidate.get("location") or {}).get("zone")
        key = (zone, candidate.get("raw_value"))
        if key not in first:
            first[key] = dict(candidate)
            first[key].setdefault("occurrence_count", 1)
            order.append(key)
        else:
            first[key]["occurrence_count"] = (
                first[key]["occurrence_count"] + (candidate.get("occurrence_count") or 1))
    return tuple(first[key] for key in order)


class EvidenceSink(Protocol):
    """P4's writer, as P5 sees it.

    `supersede_reason` is section 8.2's "the reason it was superseded": a later,
    improved extractor over the same content supersedes an earlier run, and BOTH
    remain available. P5 supplies the reason; P4 owns the supersede columns.
    """

    def write(self, result: ExtractionResult, *,
              supersede_reason: str | None = None) -> str:
        """Write the batch and return P4's `run_id`."""
        ...
