"""Comparing what the product did against what a person would have wanted.

Every rule here exists to stop a number flattering the product:

  * the top-level folder gets its own bucket, so "one flat folder" can never be
    read as partial success;
  * an `uncertain` file passes only by abstaining, so a confident answer where a
    person would have to be asked is counted as the defect it is;
  * folder-name spelling is normalised away, because which spelling the product
    mints is a normalisation decision and not a sorting one;
  * a field filled with the wrong value is separated from a field left empty,
    because a wrong confident answer is worse than a question;
  * protected is a hard pass/fail with named files, never a percentage.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping, Sequence

from tools.groundtruth.labels import Label
from tools.groundtruth.measure import Observation, RunObservation

PLACED_EXACT = "exact"
PLACED_PARENT = "right parent, wrong leaf"
PLACED_FLAT = "top folder only"
PLACED_WRONG = "wrong"
NOT_PLACED = "not placed"
NO_DECISION = "no decision"

SORTING_BUCKETS = (PLACED_EXACT, PLACED_PARENT, PLACED_FLAT, PLACED_WRONG,
                   NOT_PLACED, NO_DECISION)

_NOT_ALNUM = re.compile(r"[^0-9a-z]+")


def _norm(segment: str) -> str:
    return _NOT_ALNUM.sub("", segment.casefold())


def _same(a: str, b: str) -> bool:
    """Two folder names a person would call the same folder.

    "PHYS 1403" and "phys1403"; "figure" and "figure or plot output". Containment
    only counts from three characters, so a one-letter folder does not match
    everything.
    """
    a, b = _norm(a), _norm(b)
    if not a or not b:
        return False
    if a == b:
        return True
    return len(min(a, b, key=len)) >= 3 and (a in b or b in a)


def _ends_with(actual: Sequence[str], wanted: Sequence[str]) -> bool:
    """`actual` finishes with `wanted`.

    Compared as a suffix, not as a whole path, because the label records the
    folders BELOW the top-level one and the run supplies that top level -- and
    because a branch anchored on a folder the person already had carries that
    folder's name at its root.
    """
    if not wanted or len(wanted) > len(actual):
        return False
    tail = actual[len(actual) - len(wanted):]
    return all(_same(x, y) for x, y in zip(tail, wanted))


def score_sorting(label: Label, observation: Observation) -> str:
    """Which of the six sorting outcomes this file got."""
    if observation.outcome is None:
        return NO_DECISION
    if observation.outcome != "place":
        return NOT_PLACED

    # A file whose right answer is "ask the person" has no right folder, so any
    # confident placement is wrong -- including one that happens to look right.
    if label.is_uncertain or label.destination is None:
        return PLACED_WRONG

    actual = observation.destination
    for wanted in label.destinations:
        if _ends_with(actual, wanted):
            return PLACED_EXACT

    # The whole branch and nothing under it. Its own bucket: it is the right
    # place to start and no structure at all.
    if len(actual) <= 1:
        return PLACED_FLAT

    for wanted in label.destinations:
        for cut in range(len(wanted) - 1, 0, -1):
            if _ends_with(actual, wanted[:cut]):
                return PLACED_PARENT
    return PLACED_WRONG


def score_fields(label: Label, observation: Observation) -> tuple[int, int, int, int]:
    """`(correct, wrong, missing, extra)` for one file.

    Only the labelled fields are scored. Nobody hand-labels fifty-six cells for
    two hundred files, and a field nobody labelled cannot be called wrong -- so
    the ones the product filled anyway are counted as `extra` and reported,
    never held against it.
    """
    correct = wrong = missing = 0
    for key, wanted in label.expected_fields.items():
        got = observation.fields.get(key)
        if got is None:
            missing += 1
        elif _same(got, wanted):
            correct += 1
        else:
            wrong += 1
    extra = sum(1 for key in observation.fields if key not in label.expected_fields)
    return correct, wrong, missing, extra


@dataclass(frozen=True)
class ProtectedBreach:
    """One protected file the run did not hold the line on."""

    path: str
    kind: str        # 'absent' | 'not marked' | 'opened' | 'placed'
    detail: str


def protected_verdict(labels: Mapping[str, Label],
                      observations: Mapping[str, Observation],
                      ) -> tuple[ProtectedBreach, ...]:
    """Every way the run failed protected material. Empty means it held.

    Not a percentage. "Marked and counted, never opened, never silently omitted"
    is four conditions and each of them is a pass or a fail, so a run that opens
    one vaccination record has failed even if it left seven alone.
    """
    breaches = []
    for path, label in sorted(labels.items()):
        if not label.protected:
            continue
        observation = observations.get(path)
        if observation is None:
            breaches.append(ProtectedBreach(
                path, "absent",
                "not in the run at all: never silently omitted is the other half "
                "of the rule, and a file that is not there has not been counted"))
            continue
        if not observation.protected_marked:
            breaches.append(ProtectedBreach(
                path, "not marked",
                f"handling class {observation.handling_class!r}, protected flag not set"))
        if observation.opened:
            opened_by = ", ".join(e for e in observation.extractors
                                  if e != "filesystem.record") or "an extractor"
            breaches.append(ProtectedBreach(
                path, "opened",
                f"{opened_by}: {observation.text_units} text units recorded"))
        if observation.outcome == "place":
            breaches.append(ProtectedBreach(
                path, "placed", "/".join(observation.destination)))
    return tuple(breaches)


def over_marked(labels: Mapping[str, Label],
                observations: Mapping[str, Observation]) -> tuple[str, ...]:
    """Files the product called protected that the ground truth does not.

    A defect, but a different one: calling a payment-brand logo sensitive
    personal material spends the person's attention on nothing and teaches them
    to ignore the mark. Reported beside the hard pass/fail, never folded into it.
    """
    return tuple(sorted(
        path for path, observation in observations.items()
        if observation.protected_marked and not (
            path in labels and labels[path].protected)))


def family_cohesion(labels: Mapping[str, Label],
                    observations: Mapping[str, Observation],
                    ) -> tuple[int, int, tuple[str, ...]]:
    """`(kept together, families with two or more placed members, the scattered)`.

    Copies, versions and one work saved in two formats belong in one folder. A
    product that files three identical PDFs into three places has not organised
    anything, and no per-file bucket notices it: each of the three can be
    `exact` on its own.
    """
    families: dict[str, list[tuple[str, ...]]] = {}
    for path, label in labels.items():
        if not label.family or label.protected:
            continue
        observation = observations.get(path)
        if observation is None or observation.outcome != "place":
            continue
        families.setdefault(label.family, []).append(
            tuple(_norm(segment) for segment in observation.destination))
    # A family with one placed member says nothing about keeping things together.
    considered = {name: places for name, places in families.items() if len(places) > 1}
    scattered = tuple(sorted(n for n, p in considered.items() if len(set(p)) > 1))
    return len(considered) - len(scattered), len(considered), scattered


@dataclass(frozen=True)
class SituationScore:
    """One `--situation` run, scored against the files whose label names it."""

    situation: str
    label: str
    promised_levels: tuple[str, ...]
    built_depth: int
    node_count: int
    scored: int
    sorting: Mapping[str, int]
    fields_correct: int
    fields_wrong: int
    fields_missing: int
    fields_extra: int
    confident_on_uncertain: int
    questions: int
    unresolved_per_file: float
    #: Files whose label names a DIFFERENT situation but which this run placed
    #: confidently anyway. The run applied one answer to every file in the
    #: folder, and this counts what that cost.
    contaminated: int
    contaminated_of: int

    @property
    def exact_rate(self) -> float:
        return self.sorting.get(PLACED_EXACT, 0) / self.scored if self.scored else 0.0


def score_situation(run: RunObservation, labels: Mapping[str, Label]) -> SituationScore:
    mine = {p: l for p, l in labels.items() if l.situation == run.situation}
    buckets = dict.fromkeys(SORTING_BUCKETS, 0)
    correct = wrong = missing = extra = confident = 0
    questions = run.structural_questions
    unresolved = 0

    for path, label in mine.items():
        if label.protected:
            continue
        observation = run.files.get(path)
        if observation is None:
            buckets[NO_DECISION] += 1
            continue
        bucket = score_sorting(label, observation)
        buckets[bucket] += 1
        if label.is_uncertain and observation.outcome == "place":
            confident += 1
        c, w, m, e = score_fields(label, observation)
        correct, wrong, missing, extra = correct + c, wrong + w, missing + m, extra + e
        questions += 1 if observation.asked else 0
        unresolved += len(observation.unresolved_fields)

    scored = sum(buckets.values())
    others = {p: l for p, l in labels.items()
              if l.situation != run.situation and not l.protected}
    contaminated = sum(
        1 for p in others
        if (obs := run.files.get(p)) is not None and obs.outcome == "place")

    return SituationScore(
        situation=run.situation,
        label=run.label,
        promised_levels=run.promised_levels,
        built_depth=run.built_depth,
        node_count=run.node_count,
        scored=scored,
        sorting=buckets,
        fields_correct=correct,
        fields_wrong=wrong,
        fields_missing=missing,
        fields_extra=extra,
        confident_on_uncertain=confident,
        questions=questions,
        unresolved_per_file=unresolved / scored if scored else 0.0,
        contaminated=contaminated,
        contaminated_of=len(others),
    )
