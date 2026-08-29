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
    #: For every observation as SUBMITTED, its position in `observations` after D10
    #: collapsed. A constructor argument only so the dataclass can hold it; it is
    #: always recomputed below, and passing one is not a way to state a different map.
    collapsed_index: tuple[int, ...] = ()

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

        The collapse RENUMBERS, so it also publishes `collapsed_index` and corrects
        `observation_count`. Nine extractors counted the SUBMITTED list -- the only
        list they hold when they call `run(...)` -- and `stage_output.py` copies that
        number into the P2 section 8.5 payload, so a batch with one repeated value
        reported a count its own batch cannot support, in every format. Correcting it
        here rather than in nine call sites is the same argument as collapsing here:
        the count is derived from the batch, and only the batch knows it.
        """
        collapsed, index = _collapse(self.observations)
        object.__setattr__(self, "observations", collapsed)
        object.__setattr__(self, "collapsed_index", index)
        if self.run.get("observation_count") != len(collapsed):
            object.__setattr__(self, "run",
                               {**self.run, "observation_count": len(collapsed)})


def _collapse(observations):
    """D10, plus where every submitted observation went.

    The map is returned because the collapse RENUMBERS, and a caller that recorded a
    position into the submitted list has no other way to follow it.
    `long_tail.SensitivitySignal.observation_index` is the only such caller and it
    filed section 2.9's sensitivity signal against a neighbour -- and raised
    IndexError on a third copy -- for as long as this returned only the survivors.
    """
    first: dict[tuple, int] = {}
    kept: list[dict] = []
    index: list[int] = []
    for candidate in observations:
        zone = (candidate.get("location") or {}).get("zone")
        key = (zone, candidate.get("raw_value"))
        if key not in first:
            first[key] = len(kept)
            row = dict(candidate)
            row.setdefault("occurrence_count", 1)
            kept.append(row)
        else:
            kept[first[key]]["occurrence_count"] = (
                kept[first[key]]["occurrence_count"]
                + (candidate.get("occurrence_count") or 1))
        index.append(first[key])
    return tuple(kept), tuple(index)


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
