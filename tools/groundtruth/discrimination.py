"""Does the situation the person typed change what the product concludes?

Deliberately a module of its own, wired into nothing. `scorecard()` does not
import it and `__main__` does not call it, so a mistake in here cannot take the
working scorer down with it.

THE QUESTION IT ASKS, and why it is the prior one
-------------------------------------------------
The harness supplies `--situation` from the label. That is its largest gap: it
hands the product the north star's hard part for free. The obvious next step is
to measure whether the product could DISCOVER the situation -- but that measures
a chooser, and before building a chooser it is worth knowing whether there is
anything to choose between.

Every situation run reads the WHOLE corpus, so N runs hold N observations of
each file. That is a natural experiment nobody had to pay for: hold the file
constant, vary only the situation, and see what moves. If nothing moves, the
situation is a folder template and not an interpretation, discovery has no
signal to work from, and a chooser built on it would be a coin flip whatever its
implementation.

Measured 2026-09-04 over 199 files x 17 situations, BEFORE the extractors began
emitting body prose: facts differed for 0 of 55 files, handling class for 0 of
38, placement outcome for 3 of 199. That result is stale by construction -- its
denominators were small precisely because the product concluded so little -- and
re-running it after the extractor change is the point of keeping this module.

WHAT A NULL RESULT HERE DOES NOT MEAN
-------------------------------------
It does not mean the situation is inert: it still selects the folder template,
and the promised depths do vary correctly. It means the situation changes nothing
the product concludes ABOUT A FILE. And it is a black-box measurement -- it can
say the schemas are not discriminating, never why.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from tools.groundtruth.labels import Labels
from tools.groundtruth.measure import RunObservation


@dataclass(frozen=True)
class Divergence:
    """How much one dimension moved when only the situation changed."""

    dimension: str          # 'facts' | 'handling class' | 'placement outcome'
    compared: int           # files observed under two or more situations
    differing: int          # of those, how many were not identical throughout
    examples: tuple[str, ...]

    @property
    def rate(self) -> float:
        return self.differing / self.compared if self.compared else 0.0

    def line(self) -> str:
        return (f"{self.dimension:<20} {self.differing:4d} of {self.compared:4d} "
                f"files differ across the situations ({100 * self.rate:5.1f}%)")


def _divergence(dimension: str, per_file: Mapping[str, Mapping[str, object]],
                ) -> Divergence:
    # Only files seen under two or more situations can say anything: one
    # observation is never evidence that a value is stable.
    compared = {p: v for p, v in per_file.items() if len(v) >= 2}
    differing = [p for p, v in compared.items() if len(set(v.values())) > 1]
    return Divergence(dimension, len(compared), len(differing),
                      tuple(sorted(differing)[:6]))


def situation_divergence(runs: Sequence[RunObservation]) -> tuple[Divergence, ...]:
    """One row per dimension: facts, handling class, placement outcome.

    Values are compared for EQUALITY, not for correctness. A file that is wrong
    the same way under every situation counts as stable here, and that is the
    intended reading -- the question is whether the situation moves the answer,
    not whether the answer is good.
    """
    facts: dict[str, dict[str, object]] = {}
    handling: dict[str, dict[str, object]] = {}
    outcome: dict[str, dict[str, object]] = {}

    for run in runs:
        for path, observation in run.files.items():
            if not observation.indexed:
                continue
            # A file with no facts under either situation is two absences
            # agreeing, which is not evidence of stability. Only files that
            # produced something are compared.
            if observation.fields:
                facts.setdefault(path, {})[run.situation] = frozenset(
                    observation.fields.items())
            if observation.handling_class is not None:
                handling.setdefault(path, {})[run.situation] = observation.handling_class
            if observation.outcome is not None:
                outcome.setdefault(path, {})[run.situation] = observation.outcome

    return (_divergence("facts", facts),
            _divergence("handling class", handling),
            _divergence("placement outcome", outcome))


@dataclass(frozen=True)
class TwoThings:
    """A file the ground truth says has two right answers, and what happened.

    The north star measured directly: a research abstract that is also
    application material, a receipt that is also an application record. If the
    file reaches destination A under one situation and destination B under
    another, the product's evidence already supports both readings and what is
    missing is only a way to OFFER the person both. If only one ever fires, the
    second reading is not in the evidence and no interface can surface it.
    """

    path: str
    reached: tuple[str, ...]       # the distinct destinations it reached
    wanted: int                    # how many acceptable destinations it has
    both_readings_reachable: bool


def two_things_reachable(runs: Sequence[RunObservation], labels: Labels,
                         ) -> tuple[TwoThings, ...]:
    """Every file the ground truth gave more than one acceptable destination."""
    from tools.groundtruth.score import _ends_with

    found = []
    for path, label in labels.items():
        if label.protected or not label.also_acceptable:
            continue
        reached: set[str] = set()
        for run in runs:
            observation = run.files.get(path)
            if observation is None or observation.outcome != "place":
                continue
            for wanted in label.destinations:
                if _ends_with(observation.destination, wanted):
                    reached.add("/".join(wanted))
        found.append(TwoThings(path, tuple(sorted(reached)),
                               len(label.destinations), len(reached) > 1))
    return tuple(found)


def report(runs: Sequence[RunObservation], labels: Labels) -> str:
    lines = ["SITUATION DISCRIMINATION",
             "  Hold the file constant, vary only the situation, see what moves.",
             ""]
    for row in situation_divergence(runs):
        lines.append("  " + row.line())
        if row.examples:
            lines.append(f"      e.g. {row.examples[0]}")
    lines.append("")

    pairs = two_things_reachable(runs, labels)
    both = [p for p in pairs if p.both_readings_reachable]
    placed = [p for p in pairs if p.reached]
    lines.append(f"  THE NORTH STAR: {len(pairs)} files the ground truth says are "
                 f"two things at once")
    lines.append(f"    {len(placed)} reached ANY of their acceptable destinations")
    lines.append(f"    {len(both)} reached MORE THAN ONE")

    # WHAT A ZERO HERE DOES AND DOES NOT MEAN. Recorded before the measurement
    # ran, for the same reason the protected prediction was: a null is the most
    # likely outcome and the easiest to over-read.
    #
    # This question is only askable of a file the product actually PLACED. In
    # the last full baseline it placed 11 of 144. So "0 reached more than one"
    # is consistent with two completely different worlds -- the evidence
    # carries one reading, or the evidence carries both and nothing was placed
    # at all -- and only the placement rate tells them apart.
    if not placed:
        lines.append("")
        lines.append("    NOT MEASURED. None of these files was placed under any "
                     "situation, so the")
        lines.append("      question was never asked. This is NOT evidence that "
                     "the evidence carries")
        lines.append("      one reading; it is evidence that placement did not "
                     "happen. The measurement")
        lines.append("      becomes informative only once these files are being "
                     "placed at all.")
    elif both:
        lines.append("      -- the evidence carries both readings and only the "
                     "offer is missing,")
        lines.append("         which is a tractable interface problem.")
    else:
        lines.append(f"      -- {len(placed)} were placed and none reached a second "
                     f"reading. On this evidence")
        lines.append("         the second reading is not there to be offered.")
    return "\n".join(lines)
