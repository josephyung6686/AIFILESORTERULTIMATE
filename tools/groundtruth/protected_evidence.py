"""Was the detector starved, or does its vocabulary lack the word?

Wired into nothing, like `discrimination.py`, so an error here cannot take the
working scorer down while the thing it measures is still moving.

THE EXPERIMENT
--------------
Eight files in the ground truth are protected. On 2026-09-04, before the PDF and
docx extractors emitted body prose, NONE of the eight was marked. Two hypotheses
were offered for that, and they were not distinguishable on the evidence then
available:

  STARVATION  the detector never saw the words, because PDFs carried no body
              evidence at all -- only `.txt`, `.html` and `.md` ever did.
  VOCABULARY  the detector saw the words and has no term for them: the missing
              members are `vaccination`, `immunisation`, `hkid`, which are
              precisely what these documents contain.

The extractor change makes them distinguishable, because it removes the
starvation without touching the vocabulary. So this is a real experiment with a
prediction recorded BEFORE the result, and the point of putting it in code is
that the harness scores it rather than whoever reads the output afterwards --
including me. A narrated experiment is one whose story can be fitted to its
result.

WHAT THE PREDICTION IS
----------------------
Recorded by the detector agent, before the re-baseline, and reproduced here
verbatim in `PREDICTION`: the picture will NOT move much, because more prose
gives more text and still no matching term. If the marked count rises, the
prediction is WRONG and starvation was the answer. If it does not rise while the
same files now carry substantial text, the vocabulary diagnosis has survived a
much harder test than the one that produced it.

Half the original finding was already withdrawn on inspection: two of the eight
had ZERO text-bearing observations and a third had eight characters, so for
those three "the vocabulary has no word for it" was never testable at all. Those
three are the ones to watch.

A NOTE ON WHAT IS COUNTED
-------------------------
`text_units` here is the number of `text_units` rows the extraction runs
produced, which is NOT the same as the "text-bearing observations" the detector
agent counted -- observations are `evidence` rows. They move together and
neither is a substitute for the other. The column is named for what it is.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from tools.groundtruth.labels import Labels
from tools.groundtruth.measure import Observation, RunObservation

#: Recorded BEFORE the measurement, so the result cannot be fitted to it.
PREDICTION = (
    "the picture will NOT move much: the missing words (vaccination, "
    "immunisation, hkid) are precisely the ones these documents contain, so "
    "more prose gives more text and still no matching term"
)

#: The state the prediction was made against. Dated, because a stale prior that
#: reads as current is worse than no prior at all.
PRIOR_MARKED = 0
PRIOR_OF = 8
PRIOR_MEASURED = "2026-09-04, before the extractors emitted body prose"


@dataclass(frozen=True)
class ProtectedFile:
    """One protected file, and whether it had anything to be recognised by."""

    path: str
    text_units: int
    prose_evidence_rows: int
    content_recovered: bool
    marked: bool
    handling_class: str | None
    opened: bool

    @property
    def had_evidence(self) -> bool:
        """Was there text for a vocabulary to match against at all?

        A file with no text cannot test a vocabulary, and counting it as a
        vocabulary failure is the mistake this whole module exists to prevent.

        Measured in PROSE observations, not text units. The first version of
        this asked `text_units > 0` and put two files carrying a single
        filesystem-record unit each into the vocabulary's column -- exactly the
        accusation the three-way split exists to prevent, made by the code that
        exists to prevent it.
        """
        return self.prose_evidence_rows > 0


def protected_evidence(runs: Sequence[RunObservation], labels: Labels,
                       ) -> tuple[ProtectedFile, ...]:
    """Per protected file, the two facts that separate the hypotheses.

    Read from the run that saw the MOST text for each file. Every run reads the
    whole corpus, and taking the best-evidenced observation is the reading most
    favourable to the vocabulary hypothesis -- if the detector still did not
    mark a file when shown the most text any run recovered, starvation is not
    the explanation.
    """
    best: dict[str, Observation] = {}
    for run in runs:
        for path, observation in run.files.items():
            if path not in labels or not labels[path].protected:
                continue
            if (path not in best or observation.prose_evidence_rows
                    > best[path].prose_evidence_rows):
                best[path] = observation

    rows = []
    for path, label in sorted(labels.items()):
        if not label.protected:
            continue
        observation = best.get(path)
        if observation is None:
            rows.append(ProtectedFile(path, 0, 0, False, False, None, False))
            continue
        rows.append(ProtectedFile(
            path=path,
            text_units=observation.text_units,
            prose_evidence_rows=observation.prose_evidence_rows,
            content_recovered=observation.content_recovered,
            marked=observation.protected_marked,
            handling_class=observation.handling_class,
            opened=observation.opened))
    return tuple(rows)


def three_way(rows: Sequence[ProtectedFile]) -> dict[str, tuple[ProtectedFile, ...]]:
    """The standing shape: marked / vocabulary-failed / never-testable.

    A STANDING shape, not this run's prose. The two starved files must stay
    visible as UNTESTABLE rather than folding into "unmarked" the first time a
    future extractor gives them a single unit of text -- because "unmarked" is
    an accusation against the vocabulary, and it is only fair to make it about a
    file the vocabulary was actually shown.

    The three buckets are exhaustive and disjoint by construction, so a file
    cannot quietly leave the denominator.
    """
    marked = tuple(r for r in rows if r.marked)
    unmarked = [r for r in rows if not r.marked]
    return {
        # It crossed the line. Whatever the vocabulary lacked, it did not lack
        # this one -- and for the ones that only just started carrying text,
        # starvation was the whole blocker.
        "marked": marked,
        # Shown the words and still silent. This is the vocabulary on trial,
        # and the only bucket that may be counted against it.
        "vocabulary failed": tuple(r for r in unmarked if r.had_evidence),
        # Never shown anything. Counts against neither hypothesis, and must not
        # be read as either a pass or a failure.
        "never testable": tuple(r for r in unmarked if not r.had_evidence),
    }


def verdict(rows: Sequence[ProtectedFile]) -> str:
    """Which hypothesis the numbers support, decided by a rule set in advance."""
    marked = sum(1 for r in rows if r.marked)
    testable = [r for r in rows if r.had_evidence]
    untestable = [r for r in rows if not r.had_evidence]

    if marked > PRIOR_MARKED:
        return (f"PREDICTION WRONG. {marked} of {len(rows)} now marked, against "
                f"{PRIOR_MARKED} before. Starvation was at least part of the "
                f"answer: the detector marks files it could not previously see.")
    if not testable:
        return ("STILL UNTESTABLE. No protected file carries text, so the "
                "vocabulary has still never been asked a question it could "
                "answer. Neither hypothesis has been tested.")
    if untestable:
        return (f"PREDICTION HELD, PARTLY. {marked} of {len(rows)} marked. "
                f"{len(testable)} files now carry text and were still not "
                f"marked, which tests the vocabulary and finds it wanting. "
                f"{len(untestable)} still carry none and remain untestable -- "
                f"do not count those against the vocabulary.")
    return (f"PREDICTION HELD. All {len(rows)} protected files carry text and "
            f"{marked} were marked. The vocabulary was shown the words and has "
            f"no term for them; starvation is excluded.")


def report(runs: Sequence[RunObservation], labels: Labels) -> str:
    rows = protected_evidence(runs, labels)
    lines = [
        "PROTECTED EVIDENCE -- starvation or vocabulary?",
        f"  prediction on record: {PREDICTION}",
        f"  prior: {PRIOR_MARKED} of {PRIOR_OF} marked, {PRIOR_MEASURED}",
        "",
        "  text units  prose obs  marked  file",
    ]
    for row in rows:
        lines.append(
            f"  {row.text_units:10d}  {row.prose_evidence_rows:9d}"
            f"  {'YES' if row.marked else ' no':>6}  {row.path}")
    lines.append("")
    buckets = three_way(rows)
    lines.append("  the three-way split, which is the actionable part:")
    for name, members in buckets.items():
        lines.append(f"    {len(members):2d}  {name}")
        for member in members:
            lines.append(f"          {member.prose_evidence_rows:5d} prose obs  "
                         f"{member.path}")
    lines.append("")
    lines.append("  " + verdict(rows))
    return "\n".join(lines)
