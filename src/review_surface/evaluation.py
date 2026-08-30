"""§8.5's user-facing evaluation view. Per dimension, per stage, never collapsed.

    "A single overall 'accuracy' number hides the mechanism that needs repair."

P2 states that as a rule binding the RENDERER, and P13 is that renderer. So
`overall_accuracy` exists and always raises: the number is not merely absent from
this record, it is refused by name at the one place someone would add it. And no
arithmetic over the per-dimension blocks happens anywhere in this module -- a test
asserts the source contains no division, no sum over scores and no statistics
import, because a number nothing exposes today is a number something exposes
tomorrow.

P13 computes no metric and calls no P2 writer. `compare_runs`, `run_shadow`,
`attribute_run` and the adjudication writer are all P2's, and none is imported.

**P2's blocks are carried VERBATIM.** The live per-dimension block holds
`newly_matching`, `newly_divergent`, `unchanged_count`, `deferral_changed` and
`attribution_histogram` -- which is G13's per-stage attribution -- and a surfaced
example is one of P2's own disagreement entries. P13 renames none of it and adds
no field: renaming would make P13 the author of a shape P2 owns, and the moment
P2 adds a key the two would disagree about what a comparison says.

TWO OPEN QUESTIONS SHAPE WHAT THIS IS NOT:

* OQ8 -- what the user sees, and by what criterion shadow examples are selected.
  §8.5 says the replay system serves the engineering team AND the user without
  saying whether they see the same thing. So `select` is INJECTED with no default,
  and the SPEC's Deferred table already records the criterion as unsettled.
* OQ9 -- whether a reviewer adjudication becomes an §8.7 correction. If it does,
  this view routes actions like every other P13 surface; if not, it is read-only.
  It is `read_only=True` until that is settled, and no action is collectable here.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import NoReturn

from eval_harness.comparison import DIMENSIONS, get_comparison
from eval_harness.shadow import shadow_record


class AggregateAccuracyRefused(RuntimeError):
    """Someone asked the evaluation view for one overall number. §8.5 forbids it."""


@dataclass(frozen=True)
class SurfacedExample:
    """One of P2's disagreement entries, chosen for a person to look at.

    `example` is P2's own mapping, carried whole. P13 does not pull a
    `baseline_output` and a `candidate_output` out of it, because the keys of a
    disagreement entry are P2's and picking two of them would be P13 deciding
    which half of a disagreement matters.
    """

    example: Mapping[str, object]
    selection_reason: str


@dataclass(frozen=True)
class DimensionResult:
    """One of P2's ten dimensions, with its block exactly as P2 wrote it."""

    dimension: str
    block: Mapping[str, object]

    @property
    def attribution_histogram(self) -> Mapping[str, object]:
        """G13: which of §8.5's ten stages the errors in this dimension began in."""
        return dict(self.block.get("attribution_histogram", {}) or {})


@dataclass(frozen=True)
class EvaluationView:
    """Read-only. No aggregate exists on it and none can be asked for."""

    run_id: str
    comparison_id: str
    surfaced_examples: tuple[SurfacedExample, ...]
    per_dimension: tuple[DimensionResult, ...]
    read_only: bool

    def overall_accuracy(self) -> NoReturn:
        raise AggregateAccuracyRefused(
            "§8.5: a single overall 'accuracy' number hides the mechanism that "
            "needs repair. This view shows comparison results per dimension and "
            "names the stages errors were attributed to; it computes no "
            "aggregate and there is no number to return")


def evaluation_view(conn: sqlite3.Connection, *, shadow_run_id: str,
                    comparison_id: str,
                    select: Callable[[Sequence[Mapping[str, object]]],
                                     Sequence[Mapping[str, object]]],
                    selection_reason: str) -> EvaluationView:
    """Project P2's shadow and comparison records. `select` is the caller's.

    The two reads stay separate: shadow mode surfaces "only selected examples for
    human review" and the comparison is per dimension over the whole run. Merging
    them would produce exactly one collapsed picture, which is the thing §8.5
    forbids said a different way.
    """
    shadow = shadow_record(conn, shadow_run_id)
    comparison = get_comparison(conn, comparison_id)
    chosen = list(select(list(shadow.get("surfaced_examples", ()) or ())))
    examples = tuple(
        SurfacedExample(example=dict(item), selection_reason=selection_reason)
        for item in chosen)
    blocks = comparison.get("per_dimension", {}) or {}
    results = tuple(
        DimensionResult(dimension=dimension, block=dict(blocks[dimension]))
        for dimension in DIMENSIONS if dimension in blocks)
    return EvaluationView(
        run_id=shadow_run_id, comparison_id=comparison_id,
        surfaced_examples=examples, per_dimension=results, read_only=True)
