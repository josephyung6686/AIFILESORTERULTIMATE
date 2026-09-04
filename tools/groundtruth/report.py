"""The scorecard: what a person can read in ten seconds, and the detail under it.

Two rules about the shape. Protected comes first and is a verdict in words, not a
percentage, because the one number nobody may average is whether a vaccination
record was opened. And every rate is printed beside the count it came from, so a
denominator of four can never read like a denominator of two hundred.
"""
from __future__ import annotations

import collections
from typing import Iterable, Mapping, Sequence

from tools.groundtruth.labels import Label
from tools.groundtruth.measure import COMPLETENESS_ORDER, Observation, RunObservation
from tools.groundtruth.score import (
    PLACED_EXACT,
    PLACED_FLAT,
    PLACED_PARENT,
    PLACED_WRONG,
    NOT_PLACED,
    NO_DECISION,
    SORTING_BUCKETS,
    ProtectedBreach,
    SituationScore,
    family_cohesion,
    over_marked,
    score_fields,
    score_sorting,
)

_RULE = "=" * 78


def _pct(n: int, of: int) -> str:
    return f"{100 * n / of:5.1f}%" if of else "    --"


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
        w(f"PROTECTED   PASS -- all {protected} marked, counted, and never opened")
    if overmarks:
        w(f"            and {len(overmarks)} files were marked protected that are "
          f"not: {', '.join(overmarks[:3])}")

    # The two halves of this failure do NOT have the same fixability, and a
    # reader watching the total improve will not see that unless it is said.
    #
    # `not marked` can improve on its own as extraction improves: a detector
    # starved of body prose cannot recognise a vaccination record it was never
    # shown. `opened` cannot, ever, by any amount of better classifying --
    # extraction runs BEFORE classify in the same loop, so by the time a class
    # exists the file has already been read. Only a guard that runs before the
    # extractor, on the filename and the folder, can move that number.
    #
    # So the two numbers below answer different questions, and one of them is
    # the experiment: if `not marked` falls once the extractors emit prose, the
    # defect was upstream in extraction all along; if it does not move with a
    # hundred text units of medical record in front of the detector, the
    # corroboration diagnosis has survived a much harder test.
    if breaches:
        w(f"            of these, {len(kinds.get('not marked', ())):2d} not marked "
          f"-- CAN improve as extraction improves; the detector may simply")
        w("                 never have been shown the prose it needed")
        w(f"                  {len(kinds.get('opened', ())):2d} opened     -- CANNOT "
          f"improve by classifying better. Extraction runs")
        w("                 before classify, so the reading already happened. Only a "
          "pre-extraction")
        w("                 guard on the filename and folder can move this one.")
    w("")

    # ---- sorting, in two blocks --------------------------------------------
    # Because `not placed` is the miss in one block and the PASS in the other,
    # and one column holding both would be unreadable in either direction.
    confident_buckets, uncertain_buckets = _split_buckets(runs, labels)
    n_confident = sum(confident_buckets.values())
    n_uncertain = sum(uncertain_buckets.values())

    w(f"SORTING     {n_confident} files whose right folder is known. "
      f"Exact is the goal; the 99% target is this block.")
    for bucket in SORTING_BUCKETS:
        n = confident_buckets.get(bucket, 0)
        w(f"              {n:4d}  {_pct(n, n_confident)}  {bucket}")
    w("")
    w(f"            {n_uncertain} files whose right answer is 'ask the person'. "
      f"Here NOT PLACED is the pass.")
    for bucket in SORTING_BUCKETS:
        n = uncertain_buckets.get(bucket, 0)
        if n:
            w(f"              {n:4d}  {_pct(n, n_uncertain)}  {bucket}")
    w(f"            {confident} of them were answered confidently anyway")
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
    w("MODEL       " + (
        ", ".join(f"{k.removeprefix('llm_')}={tally[k]}" for k in sorted(tally))
        or "no model tables in these databases"))
    w("            field values by origin: " + (
        ", ".join(f"{k}={n}" for k, n in origins.most_common())
        or "none filled at all"))
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
    w("SPILLOVER   a run answers one situation for EVERY file in the folder")
    for s in scores:
        w(f"              {s.situation:<32} placed {s.contaminated:4d} of "
          f"{s.contaminated_of} files labelled as something else")
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
                   labels: Mapping[str, Label]) -> str:
    """One row per file, against the run its label names. Tab separated."""
    by_situation = {run.situation: run for run in runs}
    header = ("path", "group", "situation", "sorting", "wanted", "got",
              "completeness", "recovered", "protected_label", "protected_marked",
              "opened", "fields_correct", "fields_wrong", "fields_missing",
              "uncertain", "family")
    rows = ["\t".join(header)]
    for path in sorted(labels):
        label = labels[path]
        run = by_situation.get(label.situation)
        observation = run.files.get(path) if run else None
        if observation is None:
            rows.append("\t".join([
                path, label.group, label.situation, NO_DECISION,
                "/".join(label.destination or ()), "", "", "",
                str(label.protected), "", "", "", "", "",
                "yes" if label.is_uncertain else "", label.family or ""]))
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
            "yes" if label.is_uncertain else "", label.family or ""]))
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
