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
