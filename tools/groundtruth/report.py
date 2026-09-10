"""The scorecard: what a person can read in ten seconds, and the detail under it.

Two rules about the shape. Protected comes first and is a verdict in words, not a
percentage, because the one number nobody may average is whether a vaccination
record reached a cloud model. And every rate is printed beside the count it came
from, so a denominator of four can never read like a denominator of two hundred.
"""
from __future__ import annotations

import collections
from typing import Iterable, Mapping, Sequence

from tools.groundtruth.labels import Label
from tools.groundtruth.measure import (
    AUTO_ELIGIBLE, COMPLETENESS_ORDER, DECIDED_BY_MODEL, DECIDERS, HELD_POLICIES,
    Observation, RunObservation,
)
from tools.groundtruth.score import (
    APPROPRIATE_ABSTENTION,
    CORRECT_PLACEMENT,
    INCORRECT_PLACEMENT,
    INVALID_OUTPUT,
    MISPLACED_BUCKETS,
    NO_OUTCOME,
    BREACH_NOT_MARKED,
    BREACH_RELEASED,
    OUTCOME_CLASSES,
    PLACED_BUCKETS,
    PLACED_EXACT,
    PLACED_FLAT,
    PLACED_PARENT,
    PLACED_WRONG,
    NOT_PLACED,
    NO_DECISION,
    SORTING_BUCKETS,
    UNNECESSARY_ABSTENTION,
    ProtectedBreach,
    SituationScore,
    family_cohesion,
    over_marked,
    score_fields,
    score_outcome,
    score_sorting,
)

_RULE = "=" * 78


def _pct(n: int, of: int) -> str:
    return f"{100 * n / of:5.1f}%" if of else "    --"


def _packed(parts: Sequence[str], *, head: str, indent: str,
            width: int = 78) -> list[str]:
    """`parts` over as few lines as they fit on, never breaking one in half.

    `textwrap.wrap` splits on spaces, and every part here reads `dossier=fresh 0 /
    reused 2` -- so wrapping it would leave half a count on one line and half on
    the next, which is the one thing a reader of a money line must not see, and the
    one thing a grep for it cannot survive.
    """
    lines: list[str] = []
    current, held = head, 0
    for index, part in enumerate(parts):
        piece = part + ("," if index < len(parts) - 1 else "")
        if held and len(current) + len(piece) + 1 > width:
            lines.append(current.rstrip())
            current, held = indent, 0
        current = current + piece if not held else f"{current} {piece}"
        held += 1
    lines.append(current.rstrip())
    return lines


def _merged_view(runs, labels):
    """One observation per file: the one from the run its label names.

    Every run reads the whole corpus, so seventeen runs hold seventeen
    observations of each file. Anything counted per FILE has to pick one, and
    the honest one is the run whose situation the person would have typed.
    """
    by_situation = {run.situation: run for run in runs}
    merged = {}
    for path, label in labels.items():
        run = by_situation.get(label.situation)
        if run is not None and path in run.files:
            merged[path] = run.files[path]
    return merged


def _split_buckets(runs, labels):
    """Sorting outcomes, kept apart for the two kinds of label.

    A file whose right folder is known and a file whose right answer is "ask the
    person" want opposite outcomes, so one column holding both would read as
    success to whichever half you had in mind.
    """
    confident = collections.Counter()
    uncertain = collections.Counter()
    for run in runs:
        for path, label in labels.items():
            if label.situation != run.situation or label.protected:
                continue
            observation = run.files.get(path)
            bucket = (NO_DECISION if observation is None
                      else score_sorting(label, observation))
            (uncertain if label.is_uncertain else confident)[bucket] += 1
    return confident, uncertain


#: The three things the run can have recorded about a placement it made, and the
#: word each gets on the block. `NOT_RECORDED` is not a fourth review policy: it is
#: the absence of one, printed only when it happens, by the same rule `NO_OUTCOME`
#: is printed beneath the five classes -- the arithmetic has to come to the number
#: of placements, or the line is flattering somebody.
HELD_FOR_THE_PERSON = "held for the person"
FREE_TO_MOVE = "free to move"
POLICY_NOT_RECORDED = "no review policy on the record"


def held_counts(runs: Sequence[RunObservation],
                labels: Mapping[str, Label]) -> collections.Counter:
    """Of the placements the two blocks scored, how many the run is HOLDING.

    `104` R-151. A `place` decision whose `review_policy` is `blocked_pending_user`
    or `review_required` is one the product will not carry out until the person
    says yes -- and a person reads that as a PROPOSAL: "we suggest this folder;
    confirm". The proposal is scored above like any other placement, because the
    model's answer is either the label's folder or it is not and the policy has no
    bearing on which. This counts the hold BESIDE those buckets so the two facts
    stay apart: where the file was proposed, and whether it went there.

    THE SAME DENOMINATOR AS `_split_buckets`, walked the same way and with
    protected files left out for the same reason, so a reader may add these against
    the four placed buckets in the blocks above and get the same number.
    """
    counted: collections.Counter = collections.Counter()
    for run in runs:
        for path, label in labels.items():
            if label.situation != run.situation or label.protected:
                continue
            observation = run.files.get(path)
            if observation is None or observation.outcome != "place":
                continue
            if observation.review_policy in HELD_POLICIES:
                counted[HELD_FOR_THE_PERSON] += 1
            elif observation.review_policy == AUTO_ELIGIBLE:
                counted[FREE_TO_MOVE] += 1
            else:
                counted[POLICY_NOT_RECORDED] += 1
    return counted


#: `104` R-165's fourth word, and it is not a fourth decider: it is the ABSENCE of
#: one, on a placement written by a build that had no such field or by a caller the
#: pipeline does not route. Printed only when it happens, by the same rule
#: `POLICY_NOT_RECORDED` above is -- the arithmetic has to come to the number of
#: placements, or the line is flattering somebody.
DECIDER_NOT_RECORDED = "not recorded"


def decided_by_counts(runs: Sequence[RunObservation]) -> collections.Counter:
    """Of every placement these runs recorded, WHO chose the folder. `104` R-165.

    §13.5 is "model decides, rules validate", and the scoreboard could not say
    whether that had happened. `place_file` knew, and wrote it into the explanation
    SENTENCE; a sentence is not countable, so a deterministic rule that fired first
    and skipped the model was indistinguishable from a model verdict on every
    number this report printed.

    EVERY PLACEMENT THE RUNS RECORDED, and not the labelled subset. The block this
    feeds says what the model path did, beside the tables it filled, and both are
    facts about the runs rather than about the labels -- so this is counted the way
    `run.model` is counted and not the way the six buckets are. A file outside the
    label set was still placed by somebody.

    NOT SPLIT FRESH VERSUS REUSED, unlike every other count in that block, and the
    reason is `reuse.py`'s own list of what `--reuse-answers-from` copies:
    "Nothing about placement". A seeded database is handed a prior run's model
    ANSWERS and no decision at all, so every placement counted here was decided by
    the run being reported, and a `reused` column beside it would print zero
    forever and read as a measurement.
    """
    counted: collections.Counter = collections.Counter()
    for run in runs:
        for observation in run.files.values():
            if observation.outcome != "place":
                continue
            counted[observation.decided_by or DECIDER_NOT_RECORDED] += 1
    return counted


def bucket_deciders(runs: Sequence[RunObservation],
                    labels: Mapping[str, Label]) -> tuple[dict, dict]:
    """Who decided each placement, kept apart BY SORTING BUCKET. `104` R-165.

    `decided_by_counts` above answers "what was the model's share of this run",
    which is a fact about the run and reaches the card as one line in the MODEL
    block. This answers "what was the model's share of THIS NUMBER", which is a
    fact about a bucket, and it exists because those two were a screen apart.

    THE CASE, and it is not hypothetical. Chain w1bl scored 5 of 41 `right
    parent, wrong leaf` and the next chain scored 0. The 5 were not lost; they
    were never real. A raw `.ipynb` is JSON whose dictionary KEYS include
    `cells`, `source` and `kernelspec`, the `code` schema's authored terms
    include all three, and the term counter matched the punctuation of the
    format rather than anything anyone had written -- so four notebooks the
    model never saw were "recognised" and placed. R-160 made a notebook read as
    its cells, the JSON went away, and the number fell to the one that had
    always been true. A rule artifact stood as a win for weeks because the
    scoreboard printed the count in one block and the actor in another.

    `00`:110 sanctions a deterministic pre-filter for a unique direct match and
    nothing else, so any other placement is the model's or it is a defect. That
    makes the decider part of what a bucket's number MEANS, and this walks the
    labels exactly as `_split_buckets` does -- same skip of protected files,
    same one observation per labelled file -- so the two are addable. It is a
    different denominator from `decided_by_counts` and deliberately so: the
    blocks score the labelled corpus, the MODEL line scores the run.
    """
    confident: dict[str, collections.Counter] = {}
    uncertain: dict[str, collections.Counter] = {}
    for run in runs:
        for path, label in labels.items():
            if label.situation != run.situation or label.protected:
                continue
            observation = run.files.get(path)
            if observation is None or observation.outcome != "place":
                continue
            bucket = score_sorting(label, observation)
            side = uncertain if label.is_uncertain else confident
            side.setdefault(bucket, collections.Counter())[
                observation.decided_by or DECIDER_NOT_RECORDED] += 1
    return confident, uncertain


def _decider_suffix(counted: collections.Counter | None) -> str:
    """The per-bucket split as it is printed, or nothing at all.

    EMPTY FOR A BUCKET THAT PLACED NOTHING, and that is the honest answer rather
    than a gap. `not placed` and `no decision` chose no folder, and an empty
    placed bucket holds no choice either -- naming three actors beside a zero
    would put a decision on the card that nobody made, which is the same reason
    `NO_OUTCOME` is kept out of the owner's five classes instead of folded into
    an abstention. The `0` already in the count column says it.
    """
    if not counted:
        return ""
    split = " / ".join(f"{name} {counted.get(name, 0)}" for name in DECIDERS)
    # After a COMMA and not a fourth slash, for the reason the MODEL line gives:
    # `not recorded` is the absence of a decider, not a fourth one.
    if counted.get(DECIDER_NOT_RECORDED):
        split += f", {DECIDER_NOT_RECORDED} {counted[DECIDER_NOT_RECORDED]}"
    return f"   -- decided by {split}"


def model_share_note(runs: Sequence[RunObservation]) -> str:
    """One clause for a run the model decided nothing in, or `""`. `104` R-165.

    The per-bucket split above puts the actor beside every number it can, but a
    bucket that placed nothing carries no split -- and a run that placed nothing
    at all is exactly the shape that flatters hardest. Chain w1bn read `41 100%
    not placed` in one block and `69 98.6% appropriate abstention` in another,
    both of them excellent-looking, and no model was asked anything. This is the
    clause that travels with those numbers.

    A STATEMENT AND NOT A VERDICT. It says how many of the run's placements the
    model decided and stops; there is no threshold at which the card starts
    calling a share bad, because a threshold is a judgement and R-165's row is
    an instrument. Zero is the one share that needs no judgement to report: it
    means §13.5's "model decides, rules validate" did not happen here.

    COUNTED OVER THE RUN, like the MODEL block's own line and unlike the buckets
    -- so the note is worded to say whose placements it is counting, because it
    is printed on a block whose denominator is the labelled corpus and the two
    numbers differ by the protected and unlabelled files.
    """
    counted = decided_by_counts(runs)
    if counted.get(DECIDED_BY_MODEL, 0):
        return ""
    placements = sum(counted.values())
    if not placements:
        # `0 of 0` reads as a rate and is not one. A run that placed nothing has
        # no share to report, and saying so is a different fact from a share of
        # zero -- the first is silence, the second is rules doing the deciding.
        return "this run placed nothing, so the model decided nothing"
    return f"the model decided none of this run's {placements} placements"


def held_lines(runs: Sequence[RunObservation],
               labels: Mapping[str, Label]) -> list[str]:
    """The held-versus-free count, printed beneath a sorting block.

    A count and never a bucket. The six buckets say where each file was proposed
    and the five classes say whether that was right; neither changes because a
    move is waiting, and R-128's classes are closed.
    """
    counted = held_counts(runs, labels)
    placed = sum(counted.values())
    held = counted.get(HELD_FOR_THE_PERSON, 0)
    lines = [f"            {placed} of the files above were placed: {held} "
             f"{HELD_FOR_THE_PERSON}, "
             f"{counted.get(FREE_TO_MOVE, 0)} {FREE_TO_MOVE}"]
    lines.append(f"              a hold ({', '.join(HELD_POLICIES)}) is a PROPOSAL:")
    lines.append("              the folder above is scored either way, the MOVE "
                 "waits for the person")
    unrecorded = counted.get(POLICY_NOT_RECORDED, 0)
    if unrecorded:
        lines.append(f"              {unrecorded} {POLICY_NOT_RECORDED}")
    return lines


def outcome_counts(runs: Sequence[RunObservation],
                   labels: Mapping[str, Label]) -> collections.Counter:
    """`105` §14.7's five classes over the labelled files, plus the remainder.

    THE SAME DENOMINATOR AS `_split_buckets`, and by the same rule: one observation
    per file, from the run whose situation that file's label names, protected files
    left out. So the five classes and the two blocks above them are counted over
    exactly the same files, and a reader may add the five and compare the total
    with the two blocks' totals.
    """
    counted: collections.Counter = collections.Counter()
    for run in runs:
        for path, label in labels.items():
            if label.situation != run.situation or label.protected:
                continue
            counted[score_outcome(label, run.files.get(path),
                                  node_paths=run.node_paths)] += 1
    return counted


def outcome_lines(runs: Sequence[RunObservation],
                  labels: Mapping[str, Label]) -> list[str]:
    """The five-class table, printed beneath a sorting block.

    Beneath both blocks and from THIS function, for the reason `sorting_lines`
    itself is shared: the shadow row's promise is that it is scored with exactly
    the same rules as the applied one, and a second renderer would drift the first
    time a class's wording moved.
    """
    counted = outcome_counts(runs, labels)
    total = sum(counted.values())
    buckets = collections.Counter()
    for pair in _split_buckets(runs, labels):
        buckets.update(pair)

    # `104` R-165's second half, on these five as well as on the six buckets
    # above them, because THESE are the numbers the owner reads. `correct
    # placement` is the card's headline and `score_outcome` builds it from
    # `PLACED_EXACT` alone, so it carries exactly that bucket's split; the two
    # here are one mapping and not a second scoring. The other three classes are
    # abstentions and an invalid answer -- no folder was chosen, so there is
    # nobody to name, and the same silence `_decider_suffix` keeps over
    # `not placed` applies for the same reason.
    #
    # BOTH LABEL KINDS ADDED, unlike the blocks above, because `outcome_counts`
    # counts over both and a split on a different denominator from the number it
    # sits beside would be the misreading this row exists to stop.
    confident_by, uncertain_by = bucket_deciders(runs, labels)
    by_bucket: dict[str, collections.Counter] = {}
    for side in (confident_by, uncertain_by):
        for bucket, deciders in side.items():
            by_bucket.setdefault(bucket, collections.Counter()).update(deciders)
    misplaced_by: collections.Counter = collections.Counter()
    for bucket in MISPLACED_BUCKETS:
        misplaced_by.update(by_bucket.get(bucket, ()))
    class_deciders = {CORRECT_PLACEMENT: by_bucket.get(PLACED_EXACT),
                      INCORRECT_PLACEMENT: misplaced_by}

    lines = [f"            {total} labelled files in the owner's five outcome "
             f"classes (`105` §14.7)"]
    for name in OUTCOME_CLASSES:
        n = counted.get(name, 0)
        lines.append(f"              {n:4d}  {_pct(n, total)}  "
                     f"{name}{_decider_suffix(class_deciders.get(name))}")
        if name != INCORRECT_PLACEMENT:
            continue
        # The roll-up, taken apart. `incorrect placement` is the owner's class and
        # these three are what a person fixing the product needs -- right parent
        # wrong leaf is a leaf that was never built, top folder only is no
        # structure at all, and wrong is a different branch entirely. They are the
        # same numbers as the block above, counted over the same files.
        for bucket in MISPLACED_BUCKETS:
            lines.append(f"                    {buckets.get(bucket, 0):4d}  "
                         f"of which {bucket}"
                         f"{_decider_suffix(by_bucket.get(bucket))}")
    remainder = counted.get(NO_OUTCOME, 0)
    if remainder:
        # Shown rather than folded into an abstention, because nobody decided
        # anything about these and calling that caution would be crediting the
        # product with a judgement it never made.
        lines.append(f"              {remainder:4d}  {_pct(remainder, total)}  "
                     f"{NO_OUTCOME}")
    return lines


def row_128(runs: Sequence[RunObservation],
            labels: Mapping[str, Label]) -> str:
    """`105` §14.7's five counts on one line, in the owner's own order.

    One line and one grep -- `grep 'ROW (128)'` -- for the same reason `row_104`
    exists: a reader who has to paste these into the diagnosis should not have to
    re-add the table above by hand, and a chain that reads them should not have to
    parse a table whose spacing may move.
    """
    counted = outcome_counts(runs, labels)
    # `104` R-165, and `row_104`'s argument applies here twice over: three of
    # these five are ABSTENTIONS, which score well on a run that asked nobody
    # anything -- chain w1bn's 98.6% appropriate abstention is the case.
    note = model_share_note(runs)
    return (f"correct placement {counted.get(CORRECT_PLACEMENT, 0)}"
            f" / incorrect placement {counted.get(INCORRECT_PLACEMENT, 0)}"
            f" / appropriate abstention {counted.get(APPROPRIATE_ABSTENTION, 0)}"
            f" / unnecessary abstention {counted.get(UNNECESSARY_ABSTENTION, 0)}"
            f" / invalid output {counted.get(INVALID_OUTPUT, 0)}"
            + (f"   -- {note}" if note else ""))


def sorting_lines(runs: Sequence[RunObservation],
                  labels: Mapping[str, Label],
                  *, heading: str, confident_on_uncertain: int) -> list[str]:
    """The two sorting blocks, for any set of runs.

    A FUNCTION rather than lines inside `scorecard`, because `--shadow` renders
    this same pair over observations whose placement came from a site-C verdict
    instead of from `placement_decisions`. The promise there is that the shadow
    row is scored "with exactly the same rules as the applied placement", and the
    only way to keep that promise honest is for both to be THIS code -- a second
    renderer would drift the first time a bucket's wording or a denominator moved,
    and the drift would read as a fact about the model.
    """
    confident_buckets, uncertain_buckets = _split_buckets(runs, labels)
    n_confident = sum(confident_buckets.values())
    n_uncertain = sum(uncertain_buckets.values())
    # `104` R-165's second half. The actor goes ON the line the number is on --
    # `bucket_deciders` argues the case from chain w1bl -- and the run-level
    # clause goes on the two block HEADINGS, which is where the numbers a bucket
    # split cannot reach are: an empty bucket and a run that placed nothing.
    confident_by, uncertain_by = bucket_deciders(runs, labels)
    note = model_share_note(runs)
    aside = f"   -- {note}" if note else ""
    lines = [f"{heading:<12}{n_confident} files whose right folder is known. "
             f"Exact is the goal; the 99% target is this block.{aside}"]
    for bucket in SORTING_BUCKETS:
        n = confident_buckets.get(bucket, 0)
        lines.append(f"              {n:4d}  {_pct(n, n_confident)}  "
                     f"{bucket}{_decider_suffix(confident_by.get(bucket))}")
    lines.append("")
    lines.append(f"            {n_uncertain} files whose right answer is 'ask the "
                 f"person'. Here NOT PLACED is the pass.{aside}")
    for bucket in SORTING_BUCKETS:
        n = uncertain_buckets.get(bucket, 0)
        if n:
            lines.append(f"              {n:4d}  {_pct(n, n_uncertain)}  "
                         f"{bucket}{_decider_suffix(uncertain_by.get(bucket))}")
    lines.append(f"            {confident_on_uncertain} of them were answered "
                 f"confidently anyway")
    # `104` R-151, beneath both blocks because it is counted over both: a hold is
    # not a seventh bucket and changes no number above it. It says which of the
    # placements just scored the product would CARRY OUT and which it is holding
    # out as a proposal -- the difference between "your file is in that folder"
    # and "we suggest that folder; confirm", which the buckets cannot express.
    lines.append("")
    lines.extend(held_lines(runs, labels))
    # `105` §14.7, beneath the two blocks and never instead of them. The blocks say
    # WHERE each file went; these five say whether that was the right thing to do,
    # which the blocks cannot: `not placed` is the pass in one and the miss in the
    # other, and neither knows whether the run had built anywhere to put the file.
    lines.append("")
    lines.extend(outcome_lines(runs, labels))
    return lines


def spillover_lines(scores: Sequence[SituationScore], *, heading: str) -> list[str]:
    """What one answer applied to every file in the folder costs. Shared with `--shadow`."""
    lines = [f"{heading:<12}a run answers one situation for EVERY file in the folder"]
    for s in scores:
        lines.append(f"              {s.situation:<32} placed {s.contaminated:4d} of "
                     f"{s.contaminated_of} files labelled as something else")
    return lines


def row_104(runs: Sequence[RunObservation], labels: Mapping[str, Label],
            scores: Sequence[SituationScore]) -> str:
    """`104` §14.5's row, in its own order, so a reader need not re-derive it.

    One line, and the same line for the applied row and the shadow one, because a
    reader comparing them by eye is comparing two lines that were built the same
    way.
    """
    confident_buckets, uncertain_buckets = _split_buckets(runs, labels)
    n_confident = sum(confident_buckets.values())
    abstained = uncertain_buckets.get(NOT_PLACED, 0)
    n_uncertain = sum(uncertain_buckets.values())
    # `104` R-165. THE CLAUSE TRAVELS WITH THE ROW. This line and `row_128` exist
    # to be pasted into a diagnosis on their own, away from the block that
    # qualified them, so a row that left the fact behind would be the w1bl
    # misreading with a shorter path: five numbers and no way to tell whether a
    # model produced any of them.
    note = model_share_note(runs)
    return (f"{confident_buckets.get(PLACED_EXACT, 0)} / "
            f"{confident_buckets.get(PLACED_PARENT, 0)} / "
            f"{confident_buckets.get(PLACED_FLAT, 0)} / "
            f"{confident_buckets.get(PLACED_WRONG, 0)} / "
            f"{confident_buckets.get(NOT_PLACED, 0) + confident_buckets.get(NO_DECISION, 0)}"
            f" ({n_confident})   abstained {abstained} of {n_uncertain}"
            f"   spillover {sum(s.contaminated for s in scores)}"
            + (f"   -- {note}" if note else ""))


def scorecard(runs: Sequence[RunObservation],
              scores: Sequence[SituationScore],
              labels: Mapping[str, Label],
              breaches: Sequence[ProtectedBreach],
              overmarks: Sequence[str],
              *, corpus_files: int, seconds: float) -> str:
    lines: list[str] = []
    w = lines.append

    merged = _merged_view(runs, labels)
    scored = sum(s.scored for s in scores)
    buckets = collections.Counter()
    for s in scores:
        buckets.update(s.sorting)
    uncertain = sum(1 for l in labels.values() if l.is_uncertain)
    protected = sum(1 for l in labels.values() if l.protected)
    confident = sum(s.confident_on_uncertain for s in scores)

    w(_RULE)
    w("GROUND TRUTH SCORECARD")
    w(f"{corpus_files} files in the corpus, {len(labels)} labelled "
      f"({uncertain} uncertain, {protected} protected), "
      f"{len(runs)} situation runs, {seconds / 60:.1f} minutes")
    w(_RULE)
    w("")

    # ---- protected: a verdict, never a percentage --------------------------
    # Counted in FILES, not in breaches. Every run is checked, so eight files
    # across seventeen runs would otherwise print as several hundred.
    kinds: dict[str, set[str]] = {}
    for breach in breaches:
        kinds.setdefault(breach.kind, set()).add(breach.path)
    hurt = {p for paths in kinds.values() for p in paths}
    if breaches:
        w(f"PROTECTED   FAIL -- {len(hurt)} of {protected} protected files")
        for kind in sorted(kinds):
            w(f"              {len(kinds[kind]):3d}  {kind}")
    else:
        w(f"PROTECTED   PASS -- all {protected} marked, counted, kept off every "
          f"cloud model, and never filed")
    if overmarks:
        w(f"            and {len(overmarks)} files were marked protected that are "
          f"not: {', '.join(overmarks[:3])}")

    # The two halves of this failure do NOT have the same fixability, and a
    # reader watching the total improve will not see that unless it is said.
    #
    # `not marked` can improve on its own as extraction improves: a detector
    # starved of body prose cannot recognise a vaccination record it was never
    # shown. So it is the experiment: if it falls once the extractors emit prose,
    # the defect was upstream in extraction all along; if it does not move with a
    # hundred text units of medical record in front of the detector, the
    # corroboration diagnosis has survived a much harder test.
    #
    # `released` is the other half, and it is NOT the old `opened` line under a
    # new word. `104` §18.7 amended the rule: protected material is opened on this
    # machine for the local model, so reading one is the product working. What is
    # unfixable is not the reading but the SENDING -- bytes on a provider's server
    # cannot be recalled by any later release of this product, and every file this
    # line counts is a file whose privacy was already spent. It is decided before
    # the call, by the per-file route and the door, which is where a fix goes.
    if breaches:
        w(f"            of these, {len(kinds.get(BREACH_NOT_MARKED, ())):2d} "
          f"not marked -- CAN improve as extraction improves; the detector")
        w("                         may simply never have been shown the prose "
          "it needed")
        w(f"                      {len(kinds.get(BREACH_RELEASED, ())):2d} "
          f"released   -- CANNOT be undone for the files it already names.")
        w("                         The bytes are off the device. The route and "
          "the door")
        w("                         decide this before the call, and they are the "
          "only")
        w("                         place it can be fixed.")
    w("")

    # ---- sorting, in two blocks --------------------------------------------
    # Because `not placed` is the miss in one block and the PASS in the other,
    # and one column holding both would be unreadable in either direction.
    confident_buckets, uncertain_buckets = _split_buckets(runs, labels)
    n_uncertain = sum(uncertain_buckets.values())

    for line in sorting_lines(runs, labels, heading="SORTING",
                              confident_on_uncertain=confident):
        w(line)
    w("")

    # ---- copies, versions, one work in two formats -------------------------
    # Scored ONCE over the merged view, never summed across runs: every run
    # reads the whole corpus, so the same family placed the same way in all
    # seventeen would otherwise be counted seventeen times and read as a rate.
    together, considered, scattered = family_cohesion(labels, merged)
    w(f"FAMILIES    {together} of {considered} families of copies, versions and "
      f"formats landed in ONE folder")
    w("            -- one folder, not the right one: a family filed together in "
      "the wrong place counts here")
    if scattered:
        w(f"            split across folders: {', '.join(scattered[:6])}")
    w("")

    # ---- extraction --------------------------------------------------------
    seen: dict[str, Observation] = {}
    for run in runs:
        for path, observation in run.files.items():
            seen.setdefault(path, observation)
    # A file set aside by a §1.1 rule was never offered to an extractor, so it
    # has no completeness word: calling it `unreadable` would blame the readers
    # for a decision the scan made before them.
    read = {p: o for p, o in seen.items() if o.indexed}
    set_aside = [o for o in seen.values() if not o.indexed]
    recovered = sum(1 for o in read.values() if o.content_recovered)
    observed = sum(1 for o in read.values() if o.prose_evidence_rows > 0)
    w(f"EXTRACTION  {recovered} of {len(read)} files read had TEXT recovered "
      f"({_pct(recovered, len(read))})")
    # Two measures of one stage, because they move independently and quoting
    # either as the other misleads. A PDF can yield a page of text and no
    # observation at all -- that is what "PDFs carried no body evidence" meant,
    # while their text-unit count was never zero. Everything downstream of P4
    # consumes OBSERVATIONS, so the second line is the one that predicts
    # whether classification and facts have anything to work with.
    w(f"            {observed} of {len(read)} yielded a PROSE OBSERVATION "
      f"({_pct(observed, len(read))}) -- this is what P5 onwards can use")
    words = collections.Counter(o.completeness for o in read.values())
    for word in COMPLETENESS_ORDER:
        if words.get(word):
            w(f"              {words[word]:4d}  {word}")
    if set_aside:
        rules = collections.Counter(o.excluded_by or "not scanned" for o in set_aside)
        for rule, n in rules.most_common():
            w(f"              {n:4d}  set aside before anything was read: {rule}")
    w("")
    by_extension: dict[str, list] = {}
    for observation in read.values():
        by_extension.setdefault(observation.extension, []).append(observation)
    worst = sorted(by_extension.items(),
                   key=lambda kv: sum(o.content_recovered for o in kv[1]) / len(kv[1]))
    w("            by format, weakest first:")
    for extension, group in worst[:8]:
        got = sum(o.content_recovered for o in group)
        w(f"              {extension:<8} {got:3d} of {len(group):3d}  "
          f"{_pct(got, len(group))}")
    w("")

    # ---- classification: the gate everything downstream stands behind ------
    # Its own line, above fields and below extraction, because §8.4 makes a
    # handling class a PRECONDITION of asking a model. A file P7 never
    # classified cannot reach a model however well the model is wired, so this
    # number bounds every number under it -- and reading it as part of
    # extraction (the file WAS read) or as part of sorting (it was not placed)
    # would attribute the loss to the wrong stage.
    classified = [o for o in read.values() if o.classified]
    w(f"CLASSIFY    {len(classified)} of {len(read)} files read got a handling "
      f"class ({_pct(len(classified), len(read))})")
    w(f"            {len(read) - len(classified)} did not, and §8.4 makes a "
      f"handling class a precondition of asking a model,")
    w("               so they cannot reach one however well the model is wired.")
    by_class = collections.Counter(o.handling_class for o in classified)
    for name, n in by_class.most_common():
        w(f"              {n:4d}  {name}")
    unclassified = collections.Counter(
        o.extension for o in read.values() if not o.classified)
    if unclassified:
        w("            unclassified, by format: " + ", ".join(
            f"{ext} x{n}" for ext, n in unclassified.most_common(8)))
    w("")

    # ---- what the model path actually did ----------------------------------
    tally = collections.Counter()
    for run in runs:
        tally.update(run.model)
    origins = collections.Counter()
    for observation in merged.values():
        origins.update(observation.field_origins.values())
    # `104` R-123. What THIS run bought, and what it was handed, on two lines and
    # never added together. `--reuse-answers-from` copies a prior run's answers
    # into the fresh database before the run starts, so `llm_dossier` and
    # `llm_verdict` hold rows nobody paid for today -- and a single total would
    # report a rerun that spent nothing as one that spent everything again.
    seeded = collections.Counter()
    for run in runs:
        seeded.update(run.seeded)
    own = {k: tally[k] - seeded.get(k, 0) for k in tally}
    # `104` R-128 / `105` §14.7: EVERY count says fresh versus reused, and not only
    # the tables a seeding happened to touch. A run that was handed nothing prints
    # `reused 0` on every line, which is the measurement -- the version that fell
    # silent when there was nothing to report is the version in which a reader
    # could not tell "bought today" from "not seeded" without knowing the flag.
    parts = [f"{k.removeprefix('llm_')}=fresh {own[k]} / reused {seeded.get(k, 0)}"
             for k in sorted(own)]
    if not parts:
        parts = ["no model tables in these databases"]
    for line in _packed(parts, head="MODEL       ", indent="            "):
        w(line)
    if any(seeded.values()):
        w("            seeded from a prior run, not bought here: " + ", ".join(
            f"{k.removeprefix('llm_')}={seeded[k]}" for k in sorted(seeded)
            if seeded[k]))
        # WHERE FROM, and not only how many. A count nobody can trace back to the
        # run that produced it is a number a reader has to take on trust, and this
        # one is about money somebody either did or did not spend.
        for source in sorted({run.seeded_from for run in runs if run.seeded_from}):
            w(f"            from {source}")
    # `104` R-165. WHO DECIDED, beside what the model path cost. Every line above
    # counts CALLS, and a call is not a placement: §13.5 rules that every placement
    # goes through the model, and until this line existed the report could not say
    # whether one had. A rule that fired first and skipped the model was
    # indistinguishable from a model verdict on every number on this card.
    #
    # PRINTED ON EVERY RUN, including one with no model configured. `model 0 / rule
    # N` is the measurement on a deterministic-only run, not a line with nothing to
    # say -- so it is written unconditionally and never folded into the `parts`
    # above, which collapse to "no model tables in these databases".
    #
    # NO fresh/reused SPLIT, unlike every other count in this block, because there
    # is nothing to split: `reuse.py` copies "nothing about placement", so every
    # placement counted here was decided by the run being reported.
    # `decided_by_counts` carries the argument at length.
    deciders = decided_by_counts(runs)
    line = ("            placed by="
            + " / ".join(f"{name} {deciders.get(name, 0)}" for name in DECIDERS))
    # The remainder, printed only when it happened, so the three above plus this
    # come to the number of placements the runs made -- `POLICY_NOT_RECORDED`'s
    # rule, and for the same reason. After a COMMA and not a fourth slash: it is
    # the absence of a decider and not one of them, and a reader scanning three
    # counts separated by slashes must not read a fourth actor into the line.
    if deciders.get(DECIDER_NOT_RECORDED):
        line += f", {DECIDER_NOT_RECORDED} {deciders[DECIDER_NOT_RECORDED]}"
    w(line)
    w("            field values by origin: " + (
        ", ".join(f"{k}={n}" for k, n in origins.most_common())
        or "none filled at all"))

    # ---- R-46: a file that reached no model is counted somewhere ------------
    # THE TWO-SIDED COUNT. A scoreboard that asked `cli.model_route_permitted`
    # and stopped reported "19 blocked" while 130 more were refused at the door,
    # so a number meaning "the route let N through" was read as "N reached a
    # model". They are different questions and both are printed.
    at_route = sum(run.blocked_at_route for run in runs)
    gate = collections.Counter()
    for run in runs:
        gate.update(run.gate_refusals)
    never = sum(run.never_built for run in runs)
    # A RUN WITH NO MODEL BLOCKED NOTHING, and three zeros beside a count of
    # never-built files would read as a corpus the product had nothing to say
    # about. The route is only consulted when a model is configured, so on such a
    # run every one of these numbers is a fact about the configuration and none of
    # them is a fact about the files. `tools.groundtruth.payload` is the
    # instrument that answers the same question offline, and it is named here
    # because that is what a person who wanted these numbers should run.
    # `own`, not `tally`: a seeded dossier is a record of a call some EARLIER run
    # made, and reading one as proof that a model was configured for this one
    # would put three misleading numbers under a heading that exists to say the
    # opposite.
    if not own.get("llm_dossier") and not own.get("llm_refusal"):
        w("BLOCKED     no model was configured for these runs, so nothing was "
          "offered to the route or the door")
        w("            -- run `python3 -m tools.groundtruth.payload` for what the "
          "gate WOULD refuse; these tables record only what it did refuse.")
    else:
        w(f"BLOCKED     {at_route} withheld at the route, {sum(gate.values())} "
          f"stopped at the gate, {never} never built")
        w("            -- the route is `cli.model_route_permitted`; the gate is "
          "`Gate.release`; never built is nothing releasable to ask about.")
        if gate:
            w("            gate reasons: " + ", ".join(
                f"{reason}={n}" for reason, n in gate.most_common()))
    w("")

    # ---- fields ------------------------------------------------------------
    correct = sum(s.fields_correct for s in scores)
    wrong = sum(s.fields_wrong for s in scores)
    missing = sum(s.fields_missing for s in scores)
    extra = sum(s.fields_extra for s in scores)
    total = correct + wrong + missing
    w(f"FIELDS      {total} labelled field values, of 56 fields in the schema")
    w(f"              {correct:4d}  {_pct(correct, total)}  filled correctly")
    w(f"              {wrong:4d}  {_pct(wrong, total)}  filled WRONG")
    w(f"              {missing:4d}  {_pct(missing, total)}  not filled")
    w(f"            {extra} more fields were filled that nobody labelled "
      f"(reported, not counted against it)")
    w("")

    # ---- tree shape --------------------------------------------------------
    w("TREE        situation                          promised  built  folders")
    for s in scores:
        w(f"              {s.situation:<32} {len(s.promised_levels):8d}  "
          f"{s.built_depth:5d}  {s.node_count:7d}")
    w("")

    # ---- questions ---------------------------------------------------------
    # Kept apart, because adding them hides the one that is zero. A question
    # about the SHAPE of a branch is asked once per run however many files it
    # covers; a question about a FILE is the thing a person is owed when the
    # answer is genuinely theirs, and there were none.
    shape = [run.structural_questions for run in runs]
    per_file = sum(1 for o in merged.values() if o.asked)
    w(f"QUESTIONS   {min(shape)}-{max(shape)} questions per run about the shape of "
      f"a branch")
    w(f"            {per_file} questions about a FILE, across {scored} scored files")
    w(f"            -- so the {n_uncertain} files whose right answer is 'ask the "
      f"person' were not asked about.")
    w("               They were set aside silently, which is not the same thing.")
    unresolved = sum(s.unresolved_per_file * s.scored for s in scores)
    w(f"            {unresolved / scored if scored else 0:.1f} fields per file the "
      f"product could not settle and did not ask about")
    w("")

    # ---- what one answer applied to everything costs -----------------------
    for line in spillover_lines(scores, heading="SPILLOVER"):
        w(line)
    w("")
    # `104` §14.5's own order, so the row a reader has to paste into the diagnosis
    # is printed rather than re-derived from the buckets above by hand.
    w(f"ROW (104)   {row_104(runs, labels, scores)}")
    # `105` §14.7's own order, beside `104` §14.5's. Two rows and not one merged
    # line, because they are counted over the same files and answer different
    # questions, and a reader comparing this run with an earlier one needs the
    # older row to still be the older row.
    w(f"ROW (128)   {row_128(runs, labels)}")
    w("")
    # Printed on the card itself, not left in a handover message. Two numbers
    # on this scorecard were wrong in exactly this way before anyone noticed --
    # FAMILIES read "18 of 18" for what is one family seen seventeen times, and
    # QUESTIONS read "204 asked" for seventeen copies of the same twelve. Both
    # flattered the product, and a reader who does not know which lines are
    # per-file and which are per-run cannot tell.
    w("HOW TO READ THIS")
    w("  Every situation run reads the WHOLE corpus, so each file is observed "
      "once per run.")
    w("  Lines counted PER FILE -- protected, sorting, families, extraction, "
      "classify, fields --")
    w("    use one observation per file: the run whose situation that file's "
      "label names.")
    w("  Lines counted PER RUN -- tree, questions about branch shape, spillover "
      "-- are shown per run")
    w("    and never summed. Summing a per-file property across runs multiplies "
      "it by the number")
    w("    of runs and reads as a rate. That is the mistake this note exists to "
      "stop.")
    w("")
    w(_RULE)
    return "\n".join(lines)


def per_file_table(runs: Sequence[RunObservation],
                   labels: Mapping[str, Label],
                   shadow: Sequence[RunObservation] = (),
                   sources: Mapping[str, str] | None = None) -> str:
    """One row per file, against the run its label names. Tab separated.

    `shadow` and `sources` are `--shadow`'s three extra COLUMNS, appended and never
    interleaved: the file names and every existing column keep their positions, so
    a reader's eye and anything parsing this file are unaffected by a flag they did
    not pass. `got` is the node the run APPLIED and `shadow_got` the node the
    site-C verdict would have placed, which is the "observed versus applied" pair.
    `shadow_source` says which of the two the shadow row came from -- `verdict`, or
    the word for why the applied outcome was carried instead.

    `review_policy` (`104` R-151) is P11's own word for the decision in `sorting`,
    and it is what tells "placed exact" apart from "placed exact, and waiting for
    you": `blocked_pending_user` and `review_required` are holds, `auto_eligible`
    is a move the product would make on its own, and empty means the run was not
    placing this file or recorded no policy for it. The RAW word rather than a
    yes/no, because which hold it is -- nothing has classified this file yet, or
    somebody should look -- is the first thing a person debugging the row asks. It
    is appended after `family` and before the shadow cells, so every column above
    keeps the position the paragraph above promises it.

    `decided_by` (`104` R-165) is who chose the folder in the `got` cell -- `model`,
    `rule`, `user`, or empty. It sits directly after `review_policy` because the two
    answer the neighbouring halves of one question a person debugging a row asks:
    who decided this, and does the product need permission to act on it. Empty by
    the same rule as the policy beside it: only a placement names a decider, so an
    abstention's cell is blank rather than reporting an actor for a folder nobody
    proposed.
    """
    by_situation = {run.situation: run for run in runs}
    shadow_by_situation = {run.situation: run for run in shadow}
    header = ["path", "group", "situation", "sorting", "wanted", "got",
              "completeness", "recovered", "protected_label", "protected_marked",
              "opened", "fields_correct", "fields_wrong", "fields_missing",
              "uncertain", "family", "review_policy", "decided_by"]
    if shadow:
        header += ["shadow_sorting", "shadow_got", "shadow_source"]
    rows = ["\t".join(header)]

    def tail(path: str, label: Label) -> list[str]:
        """The three shadow cells for one file, or none at all."""
        if not shadow:
            return []
        run = shadow_by_situation.get(label.situation)
        observation = run.files.get(path) if run else None
        source = (sources or {}).get(path, "")
        if observation is None:
            return [NO_DECISION, "", source]
        bucket = ("protected" if label.protected
                  else score_sorting(label, observation))
        return [bucket, "/".join(observation.destination), source]

    for path in sorted(labels):
        label = labels[path]
        run = by_situation.get(label.situation)
        observation = run.files.get(path) if run else None
        if observation is None:
            rows.append("\t".join([
                path, label.group, label.situation, NO_DECISION,
                "/".join(label.destination or ()), "", "", "",
                str(label.protected), "", "", "", "", "",
                "yes" if label.is_uncertain else "", label.family or "", "", "",
                *tail(path, label)]))
            continue
        c, wr, m, _ = score_fields(label, observation)
        rows.append("\t".join([
            path, label.group, label.situation,
            "protected" if label.protected else score_sorting(label, observation),
            "/".join(label.destination or ()),
            "/".join(observation.destination),
            observation.completeness,
            "yes" if observation.content_recovered else "no",
            "yes" if label.protected else "",
            "yes" if observation.protected_marked else "",
            "yes" if observation.opened else "no",
            str(c), str(wr), str(m),
            "yes" if label.is_uncertain else "", label.family or "",
            # Only a placement can be held, so an abstention's policy -- P11 writes
            # one for every decision -- is left out rather than read as a hold on
            # a file nothing was proposed for. `Observation.held` is the same rule.
            ((observation.review_policy or "")
             if observation.outcome == "place" else ""),
            # Only a placement names a decider, exactly as only a placement can be
            # held: an abstention chose no folder, so an actor beside it would
            # credit a decision nobody made.
            ((observation.decided_by or "")
             if observation.outcome == "place" else ""),
            *tail(path, label)]))
    return "\n".join(rows)


def breach_detail(breaches: Iterable[ProtectedBreach]) -> str:
    """One line per file per kind, however many runs found it.

    Protected is checked in every run, so eight files across seventeen runs
    arrive as two hundred and seventy-two rows describing eight problems. The
    run that found it does not matter; the file does.
    """
    lines = ["PROTECTED BREACHES", _RULE]
    seen: set[tuple[str, str]] = set()
    for breach in sorted(breaches, key=lambda b: (b.path, b.kind)):
        if (breach.path, breach.kind) in seen:
            continue
        seen.add((breach.path, breach.kind))
        lines.append(f"{breach.kind:<12} {breach.path}")
        lines.append(f"             {breach.detail}")
    return "\n".join(lines)
