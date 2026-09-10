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
  * protected is a hard pass/fail with named files, never a percentage -- and
    since `104` §18.7 it fails on where the bytes WENT rather than on whether
    the file was read, because the owner ruled that protected material is opened
    on this machine for the local model.
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

# ---------------------------------------------------------------------------
# `105` §14.7's five outcome classes
# ---------------------------------------------------------------------------
# The six buckets above answer "where did it go". These five answer "was that the
# right thing to do", which is a different question and the one the owner asks. A
# file left alone is a pass or a miss depending on whether anywhere existed to put
# it, and no bucket can tell those apart.
CORRECT_PLACEMENT = "correct placement"
INCORRECT_PLACEMENT = "incorrect placement"
APPROPRIATE_ABSTENTION = "appropriate abstention"
UNNECESSARY_ABSTENTION = "unnecessary abstention"
INVALID_OUTPUT = "invalid output"

OUTCOME_CLASSES = (CORRECT_PLACEMENT, INCORRECT_PLACEMENT, APPROPRIATE_ABSTENTION,
                   UNNECESSARY_ABSTENTION, INVALID_OUTPUT)

#: NOT one of the five, and named so it cannot be mistaken for one. A labelled file
#: the run holds no decision about at all is not an abstention -- nobody decided
#: anything -- and folding it into one would credit the product with a caution it
#: did not show. Printed beneath the five and only when there is one, because
#: "never silently omitted" applies to the scorecard's own arithmetic: the five
#: plus this must come to the labelled files.
NO_OUTCOME = "no decision at all (outside the five)"

#: The buckets that mean the run filed the file SOMEWHERE ELSE than its label's
#: folder. Rolled up into `INCORRECT_PLACEMENT` and still counted separately, which
#: is why both spellings survive: the roll-up is the owner's class, and the three
#: underneath it are what a person fixing the product needs.
MISPLACED_BUCKETS = (PLACED_PARENT, PLACED_FLAT, PLACED_WRONG)

#: The buckets that mean a folder was CHOSEN -- the four above plus the one that
#: got it right. `104` R-165's second half names these and not the other two: a
#: placement has a decider and `NOT_PLACED` and `NO_DECISION` do not, so they are
#: the only lines on the block that can carry who decided them.
PLACED_BUCKETS = (PLACED_EXACT, PLACED_PARENT, PLACED_FLAT, PLACED_WRONG)

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


def has_legal_candidate(label: Label,
                        node_paths: Sequence[Sequence[str]]) -> bool:
    """The run built a folder this file could legally have been filed into.

    Compared with `_ends_with`, the same suffix rule `score_sorting` uses, so a
    label that would have scored `exact` against a chain is exactly a label this
    says had a candidate. Any other comparison here would let a file be scored as
    an unnecessary abstention for not reaching a folder that would not have
    counted as reaching it.

    A label with no destination -- protected, or a genuinely unknown home -- has no
    candidate by definition. That is why `is_uncertain` is checked FIRST in
    `score_outcome` and never here: "the person has to be asked" is a reason of its
    own and must not be reported as "the tree was missing a folder".
    """
    if not label.destinations:
        return False
    return any(_ends_with(tuple(chain), wanted)
               for chain in node_paths for wanted in label.destinations)


def score_outcome(label: Label, observation: Observation | None, *,
                  node_paths: Sequence[Sequence[str]] = ()) -> str:
    """Which of `105` §14.7's five classes this file's outcome falls in.

    THE ORDER IS THE POINT, and it is: placed, then invalid, then abstained.

      * A file the run FILED is scored on where it landed, whatever the model's
        answer did, so `correct placement` and `incorrect placement` come to the
        same numbers as the `exact` and the three placed-elsewhere buckets printed
        directly above them in the same block. A reader can check the table against
        the card, which they could not if an invalid response quietly moved a file
        out of `exact`.
      * A file that was NOT filed and whose model answer failed schema or
        validation is `invalid output`: the answer is why there is no placement,
        and it is the honest thing to call it.
      * Only then is an abstention judged, and it is appropriate when the person
        genuinely had to be asked, or when the run built nowhere legal to put the
        file. Everything else it abstained on was a file it could have filed and
        did not.

    Consequence, stated because it will be read in the shadow block: a file whose
    site-C verdict named a node the plan does not hold CARRIES its applied outcome,
    so if that applied outcome was a top-folder placement the file reads here as
    `incorrect placement` and not as `invalid output`. The shadow block's own
    provenance lines name it; this table scores what happened to the file.
    """
    bucket = NO_DECISION if observation is None else score_sorting(label, observation)
    if bucket == PLACED_EXACT:
        return CORRECT_PLACEMENT
    if bucket in MISPLACED_BUCKETS:
        return INCORRECT_PLACEMENT
    if observation is not None and observation.invalid_model_output:
        return INVALID_OUTPUT
    if bucket == NOT_PLACED:
        if label.is_uncertain or not has_legal_candidate(label, node_paths):
            return APPROPRIATE_ABSTENTION
        return UNNECESSARY_ABSTENTION
    return NO_OUTCOME


def _named_the_same(got: str, aliases: Sequence[str]) -> bool:
    """Whether the label's own file says this spelling names the labelled value.

    `104` R-147. The scoreboard could not tell a right answer in the document's
    spelling from a wrong one. §16.2: for 18 of the 43 labelled coursework files
    the course code is nowhere in the file's bytes -- it is in the folder path
    or on a neighbouring syllabus -- "under a spelling the label does not use",
    and 23 dossiers held the code's digits and scored as misses anyway. The
    documents of one course print `ENGI E1006`; its label spells it
    `PYTHON1006`.

    `_same` handles the spellings that differ only in punctuation and case, and
    that was already enough for `AAAAAA9999` against a printed `Aaaaaa 9999`.
    It cannot know a code and a course NAME are one course, because that is not
    a property of the two strings -- it is something a person knows and writes
    down. `Label.aliases` is where they wrote it.

    THIS IS THE WHOLE READER. Nothing else in this module or in `src/` consults
    `aliases`: `score_sorting`, `_ends_with` and `family_cohesion` compare folder
    names and never see it, so an equivalence can move a fact from `wrong` to
    `correct` and can never move a file, build a node, or rename one. `00`'s
    2026-09-05 amendment -- "There are no alias tables or equivalence maps in
    code" -- is why the table is in the labels file and why this is its only
    door.

    Compared with `_same` rather than by equality, so an alias inherits the
    separator-blindness the labelled spelling already has and nobody has to
    write out every punctuation of it.
    """
    return any(_same(got, spelling) for spelling in aliases)


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
        elif _same(got, wanted) or _named_the_same(got, label.aliases.get(key, ())):
            correct += 1
        else:
            wrong += 1
    extra = sum(1 for key in observation.fields if key not in label.expected_fields)
    return correct, wrong, missing, extra


#: The file was not in the run at all. `00`'s "never silently omitted".
BREACH_ABSENT = "absent"
#: The run held no protected flag for it, so nothing downstream could route it.
BREACH_NOT_MARKED = "not marked"
#: Its dossier reached a target off this device. The one that cannot be undone.
BREACH_RELEASED = "released"
#: The run filed it without being asked. `104` §18.7's "never filed automatically".
BREACH_FILED = "filed"

#: The closed set `protected_verdict` returns, in the order a person reads them:
#: the file was missing, the mark was missing, the bytes left, the file moved.
#: Published so consumers assert against these and never re-spell them -- a test
#: carrying its own copy of the words is a test that keeps passing after a rename.
PROTECTED_BREACH_KINDS = (BREACH_ABSENT, BREACH_NOT_MARKED, BREACH_RELEASED,
                          BREACH_FILED)


@dataclass(frozen=True)
class ProtectedBreach:
    """One protected file the run did not hold the line on."""

    path: str
    kind: str        # one of `PROTECTED_BREACH_KINDS`
    detail: str


def protected_verdict(labels: Mapping[str, Label],
                      observations: Mapping[str, Observation],
                      ) -> tuple[ProtectedBreach, ...]:
    """Every way the run failed protected material. Empty means it held.

    Not a percentage. Each condition is a pass or a fail, so a run that sends one
    vaccination record to a cloud model has failed even if it kept seven home.

    **`opened` WAS A BREACH HERE UNTIL 10 Sep 2026 AND IS NOT ONE NOW.** `104` §18.7:
    the owner was asked and answered on 9 Sep, and confirmed twice -- "protected
    containers are extracted and classified by the LOCAL model, never sent to the
    cloud, still marked and counted in every report". §18.4's sentence 6 was amended
    to say it: "Protected files reach the local model only, opened on this machine
    for it and never sent to the cloud; protected containers are marked and counted
    in every report." A vaccination record that this machine read, classified, marked
    and counted is the product doing exactly what it was told to do.

    Leaving the old check in place was not a conservative choice, which is the reason
    this is a defect and not a preference. r19 printed `PROTECTED FAIL -- 8 of 8
    protected files ... opened` on a run whose every call was local (§18.16: 119
    usage rows, all `qwen3:8b`) -- a scoreboard reporting total failure on a run that
    held the line perfectly. A measure that cannot be passed is not a strict measure;
    it is a broken one, and the number it prints teaches a reader to stop looking at
    the protected block, which is the one block on the card that must never be
    skimmed.

    **What replaced it is the breach the ruling actually forbids: RELEASED.** Not
    "was this file read" but "did any of it leave this device", read off
    `Observation.cloud_releases` -- see that field for why the locality comes out of
    the release the gate minted and never out of a model's name.

    THE FOUR ARE NOT INTERCHANGEABLE and are listed in the order the damage is:

      * `absent` -- the file is not in the run. Marked and counted is half the rule
        and never silently omitted is the other half; a file that is not there has
        been neither.
      * `not marked` -- the run has the file and no protected flag on it. Nothing
        downstream can route what is not marked, so this is the breach that makes the
        other two possible.
      * `released` -- bytes or a name went to a cloud target. The only one of the
        four that no later fix can recall.
      * `filed` -- the run moved it. §18.7: protected material "is never filed
        automatically".

    **One interpretation, stated so the owner can strike it.** A HELD placement is
    counted here too. R-151 says a held placement is a placement -- the model named a
    folder and the only thing P11 withholds is the move -- and this refuses to grade
    the product on a distinction the person's next click erases: a protected file
    sitting on screen under "we suggest this folder; confirm" is the product having
    decided about protected material on its own. The `detail` says which it was, so a
    reader who disagrees can see the split without the verdict having assumed it. If
    the owner rules that a held proposal on a protected file is acceptable, this is
    one condition on `observation.held` and the tests say so.
    """
    breaches = []
    for path, label in sorted(labels.items()):
        if not label.protected:
            continue
        observation = observations.get(path)
        if observation is None:
            breaches.append(ProtectedBreach(
                path, BREACH_ABSENT,
                "not in the run at all: never silently omitted is the other half "
                "of the rule, and a file that is not there has not been counted"))
            continue
        if not observation.protected_marked:
            breaches.append(ProtectedBreach(
                path, BREACH_NOT_MARKED,
                f"handling class {observation.handling_class!r}, protected flag not set"))
        if observation.released_to_cloud:
            breaches.append(ProtectedBreach(
                path, BREACH_RELEASED,
                f"this file's dossier was released to "
                f"{', '.join(observation.cloud_releases)}"))
        if observation.outcome == "place":
            breaches.append(ProtectedBreach(
                path, BREACH_FILED,
                "{} ({})".format(
                    "/".join(observation.destination) or "no folder recorded",
                    "held for the person to confirm" if observation.held
                    else "nothing was holding the move")))
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
