# src/evaluation.py
"""§8.5's replay, at the layer that is allowed to join two parts.

P2 walks ten attribution stages and asks each for a `StageAdapter`. Until this
module `src/` published exactly one -- P8's `replay_stage_adapter`, which needs
live `Dossier` objects, evidence resolvers and site dependencies no bundle
carries -- so a replay over a real bundle recorded ten `not_implemented` rows and
every dimension scored `not_run`. The harness ran, and measured nothing.

**Why this is a composition module and not part of P5 or P2.** The adapter below
reads P2's `bundle_extraction_run` and hands the row to P5's
`extraction_stage_output`. Neither part may do that. P5's only run-time
dependency is P1 and `test_p5_imports_no_part_of_p2` holds it there; P2 re-spells
P5 rather than importing it, which `counts.py` says in its own docstring. A
`ReplayContext`-typed function that touches both is therefore neither part's, and
it lives here beside `orchestrator.py` and `production.py` for the same reason
they do: this is the layer that owns ORDER and joins, and decides no policy.

**What this measures and what it cannot.** It scores the extraction runs a bundle
RECORDED against that bundle's labels. It does not re-extract: §8.5's bundle
carries content hashes, not bytes, which is why `scan_agent.replay.replay` writes
no `files` row. "The same bundle processed by a new extractor version" is not
reachable from anything in this repository today, and nothing here pretends
otherwise.

**Nine stages are absent and stay absent.** `factual_validation`, `retrieval`,
`graph_construction`, `grouping`, `template_generation`, `tree_design`,
`candidate_node_retrieval` and `placement_scoring` publish `emit_*` writers that
take LIVE part objects -- a `ResolveResult`, a `GroupingResult`, a placement
decision -- and a sealed bundle holds none of them. `llm_interpretation` has a
real adapter in P8 and it needs live dossiers. An adapter fabricated for any of
them would make a number look better while measuring nothing, so there is none.
A stage with no adapter reports `not_implemented` and its dimension scores
`not_run`, by design, and the renderer below prints that rather than hiding it.

No threshold, no tolerance, no score and no single number: §8.5 is explicit that
"a single overall 'accuracy' number hides the mechanism that needs repair", and
SPEC Open question 2 is open.
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from eval_harness.bundle import extraction_runs
from eval_harness.driver import EvaluationRun
from eval_harness.replay import ReplayContext, StageResult
from eval_harness.store import canonical_json
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS, VERDICTS
from extractors.stage_output import STAGE_ID, extraction_stage_output


class AmbiguousExtractionMeasurement(Exception):
    """Two recorded runs measure one file version, and §8.5 does not say which wins.

    P5 keys its extraction measurement on the CONTENT HASH -- §8.2's identity for
    a file version, and what every `extraction` expectation is written against --
    while `stage_dimension_value`'s primary key is (run_id, dimension,
    subject_ref). One file version therefore admits exactly one extraction
    measurement per run, and a bundle that recorded a native pass AND a targeted
    OCR pass over the same hash offers two.

    That is a real conflict between two published surfaces and not a bug here.
    Resolving it means choosing which run is authoritative, or minting a merged
    measurement shape, and both are policy: §8.5 names neither, and §8.5's version
    tuple carries "one version per extractor" precisely so two extractors can both
    be in scope. So this refuses, `replay_bundle` records the stage as `error`
    with this traceback, and the run reports a stage that failed rather than a
    measurement nobody chose. Identical measurements are not ambiguous and do not
    raise -- there is nothing to choose between them.
    """


def _decoded(row: Mapping[str, Any]) -> dict:
    """P4's row as `extraction_stage_output` reads it.

    One field is re-shaped and it is not cosmetic. P4's `coverage` column is TEXT
    holding JSON; `orchestrator._assemble_bundle` copies the row out of the
    database with `SELECT *`, so what survives into `bundle_extraction_run` is a
    coverage STRING, while `extraction_stage_output` does `dict(run["coverage"])`
    and needs the mapping `extractors.runs.coverage` returned. Decoding it here
    keeps P5's mapping the single authority over the envelope: a live row and a
    replayed row must not come to disagree about one run, and they would if this
    module built the envelope itself.
    """
    coverage = row.get("coverage")
    if isinstance(coverage, str):
        coverage = json.loads(coverage)
    return {**row, "coverage": coverage}


def extraction_adapter(ctx: ReplayContext) -> list[StageResult]:
    """§8.5's `extraction` stage, read out of the bundle and nothing else.

    One envelope per recorded run, always: two extractor versions over one file
    version are two runs and two rows, and collapsing them would delete the thing
    §8.5's version tuple exists to let a reader diff. The `payload` is P5's and
    carries the extractor name and version, so both survive in full.

    The measured VALUE is a different keying -- P5 puts it on the content hash --
    and P2 admits one per subject per run. Where the recorded runs agree, the one
    they agree on is emitted; where they disagree, this refuses rather than
    picking. See `AmbiguousExtractionMeasurement`.

    Reads `ctx.conn` and `ctx.bundle_id` only. It opens no file, and it does not
    read P4's `extraction_runs` table -- the tests drive it in a database where
    that table does not exist, so a regression to the live table raises rather
    than passing quietly.
    """
    envelopes = [extraction_stage_output(run=_decoded(row))
                 for row in extraction_runs(ctx.conn, ctx.bundle_id)]

    by_subject: dict[str, list] = {}
    for envelope in envelopes:
        for value in envelope["values"]:
            by_subject.setdefault(value.subject_ref, []).append(value)

    for subject_ref, values in by_subject.items():
        distinct = {canonical_json([value.outcome, value.value]) for value in values}
        if len(distinct) > 1:
            raise AmbiguousExtractionMeasurement(
                f"{len(values)} recorded extraction runs measure file version "
                f"{subject_ref} and {len(distinct)} of them disagree. §8.5 "
                "names no rule for which analysis tier is authoritative over one "
                "file version, and `stage_dimension_value` admits one measurement "
                "per subject per run. An owner decision, not P2's and not P5's."
            )

    results = []
    written: set[str] = set()
    for envelope in envelopes:
        # The agreed measurement is written once, by the first envelope that
        # carries it. The rest keep their own row and no value, so they stay
        # complete records of what ran without claiming a second measurement of
        # a subject P2 admits one measurement of.
        values = tuple(value for value in envelope["values"]
                       if value.subject_ref not in written)
        written.update(value.subject_ref for value in values)
        results.append(StageResult(
            subject_ref=envelope["subject_ref"], outcome=envelope["outcome"],
            payload=envelope["payload"], inputs=list(envelope["inputs"]),
            budget_state=envelope["budget_state"], values=values))
    return results


#: The stage adapters a bundle alone can drive. One of §8.5's ten, and the count
#: is the honest reading of what this repository can measure from a sealed bundle
#: today -- not a target to be met by inventing the other nine.
BUNDLE_ADAPTERS: Mapping[str, Any] = {STAGE_ID: extraction_adapter}


# ======================================================================================
# The report
# ======================================================================================

#: What §8.6 calls the count line, with the reason each number is what it is. The
#: order is the order they are printed in; it is presentation, not a contract.
COUNT_LINES: tuple[tuple[str, str], ...] = (
    ("files_indexed", "files in the bundle"),
    ("files_with_any_run", "of those, files an extractor ran against"),
    ("files_fully_extracted", "files whose every run finished complete"),
    ("runs_deferred", "runs stopped at a ceiling"),
    ("runs_unreadable", "runs that could not read the file"),
    ("runs_dataless", "runs whose bytes are not on this machine"),
    ("files_requiring_model_review", "files awaiting model review"),
)

#: `bundle_counts` returns None for a count P2 cannot know -- it is P8's, and a
#: zero would assert something. §8.6 asks that unmeasured work stay visible AS
#: unmeasured, so it is printed as a sentence and never as a number.
NOT_MEASURED = "not measured (P8's count, and P2 does not guess it)"


#: What a stage with no adapter gets. Nine of the ten get it today.
ABSENT = "absent: no adapter, so its dimension could not be measured"


def stage_status(conn, run_id: str) -> Mapping[str, str]:
    """Which of the ten stages ran, which were absent, and which failed.

    A second read of the database, kept out of `replay_lines` so that renderer
    stays a pure function over what the driver returned.

    This block exists because of a failure that is not hypothetical. A stage that
    raised writes an `error` row and attributes nothing, so the attribution
    histogram prints it at zero -- indistinguishable from a stage that ran
    cleanly and found nothing wrong. Over a real corpus this repository's
    extraction adapter refuses on every single file, and the report for that was
    `extraction 0`. §8.6 asks that unfinished work stay visible AS unfinished,
    and a zero is the opposite of that.

    The exception's own first line is carried through verbatim. It is the only
    actionable thing in the row, and a reader who is told "failed" without being
    told why has to go into the database to find out.

    There are four answers and not three. A stage whose adapter returned nothing
    RAN -- P2's runner writes its own `abstained` row keyed on the bundle to say
    so -- and emitted no measurement, and calling that "ran" beside a stage that
    produced real values erases a distinction P2 keeps at the row level.
    """
    outcomes: dict[str, set[str]] = {}
    errors: dict[str, str] = {}
    for row in conn.execute(
            "SELECT stage_id, outcome, payload FROM stage_output WHERE run_id = ?",
            (run_id,)):
        outcomes.setdefault(row["stage_id"], set()).add(row["outcome"])
        if row["outcome"] == "error" and row["stage_id"] not in errors:
            # `traceback.format_exc()`'s last non-empty line is the exception
            # line: the type and its message, which is what names the refusal.
            lines = [line for line in (row["payload"] or "").splitlines() if line]
            errors[row["stage_id"]] = lines[-1] if lines else "no detail recorded"
    measured = {row["stage_id"] for row in conn.execute(
        "SELECT DISTINCT stage_id FROM stage_dimension_value WHERE run_id = ?",
        (run_id,))}

    status = {}
    for stage_id in STAGE_IDS:
        seen = outcomes.get(stage_id, set())
        if stage_id in errors:
            status[stage_id] = f"failed: {errors[stage_id]}"
        elif seen == {"not_implemented"}:
            status[stage_id] = ABSENT
        elif stage_id in measured:
            status[stage_id] = "ran"
        else:
            status[stage_id] = "ran, and measured nothing"
    return status


def replay_lines(run: EvaluationRun, *,
                 stages: Mapping[str, str] | None = None,
                 comparison: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    """§8.5's three decompositions, and a fourth block when a baseline exists.

    Every verdict of the seven and every stage of the ten is printed, including
    the ones at zero, for the reason `comparison.py` prints every dimension
    including an empty one: a decomposition that hides its empty rows reads as a
    smaller problem than it is, and an absent stage is the single most important
    thing a reader of this report can learn.

    There is no total, no ratio, no percentage and no aggregate line, here or
    anywhere it could be derived from -- §8.5: "a single overall 'accuracy' number
    hides the mechanism that needs repair." The counts are counts of rows.
    """
    lines = [f"Evaluated bundle {run.bundle_id} as run {run.run_id}.", ""]

    if stages is not None:
        lines.append("Stages")
        for stage_id in STAGE_IDS:
            lines.append(f"  {stage_id} -- {stages[stage_id]}")
        lines.append("")

    lines.append("Verdicts")
    # Widths measured off the vocabulary rather than typed, the way
    # `--list-situations` measures its column: a name that grows past a
    # hand-picked number silently loses the gap between it and its count.
    width = max(len(verdict) for verdict in VERDICTS)
    for verdict in VERDICTS:
        lines.append(f"  {verdict:<{width}}  {run.verdicts.get(verdict, 0)}")
    if not run.assertions_written:
        lines.append("  -- this bundle carries no expectation, so nothing was")
        lines.append("     measured against a label. A bundle with no labels is a")
        lines.append("     corpus snapshot, not a reference corpus, and the")
        lines.append("     labelling is hand work (§8.5).")
    lines.append("")

    lines.append("Where the error began")
    width = max(len(stage_id) for stage_id in STAGE_IDS)
    for stage_id in STAGE_IDS:
        lines.append(f"  {stage_id:<{width}}  {run.attribution.get(stage_id, 0)}")
    if not run.attributed:
        lines.append("  -- no wrong terminal outcome to attribute.")
    lines.append("")

    lines.append("Counts")
    width = max(len(wording) for _, wording in COUNT_LINES) + len(":")
    for key, wording in COUNT_LINES:
        value = run.counts.get(key)
        lines.append(f"  {wording + ':':<{width}}  "
                     f"{NOT_MEASURED if value is None else value}")

    if comparison is not None:
        lines.append("")
        lines.extend(_comparison_lines(comparison))
    return tuple(lines)


def _comparison_lines(comparison: Mapping[str, Any]) -> list[str]:
    """The baseline diff, decomposed by dimension and never summed.

    A deferral is printed on its own line and never counted as a divergence
    (§8.6): a run whose only change is a different ceiling must show no
    regression. The four per-dimension counts are a floor on a dimension's
    subjects and not a total -- a move between two failing verdicts is in
    `disagreements` and in none of them -- so they are printed as what they are
    and nothing here adds them up.
    """
    lines = [f"Against baseline run {comparison['baseline_run_id']}"]
    delta = comparison["version_tuple_delta"]
    if delta:
        for field in sorted(delta):
            change = delta[field]
            axis = "§8.5 axis" if change["is_8_5_axis"] else "not one of §8.5's axes"
            lines.append(f"  {field}: {change['baseline']!r} -> "
                         f"{change['candidate']!r}  ({axis})")
    else:
        lines.append("  the version tuple is unchanged.")
    if comparison["ceilings_differ"]:
        lines.append("  ceilings differ: "
                     + ", ".join(comparison["ceilings_differing_keys"])
                     + " -- a budget change, which §8.6 does not read as better "
                       "or worse.")
    for dimension in DIMENSIONS:
        block = comparison["per_dimension"][dimension]
        lines.append(
            f"  {dimension:<16}"
            f"newly matching {len(block['newly_matching'])}, "
            f"newly divergent {len(block['newly_divergent'])}, "
            f"unchanged {block['unchanged_count']}, "
            f"deferral changed {len(block['deferral_changed'])}")
    return lines


def bundle_baseline(conn, bundle_id: str) -> str | None:
    """The earliest finished run over this bundle, or None if this is the first.

    "Earliest" is `started_at` and then insertion order, never `run_id`: a run id
    is a uuid4, so under the injected fixed clock every test and every replay run
    is driven by, "the first run" would otherwise have been decided by random hex
    -- the same trap `llm_harness.replay_recorded_response` names in its own query.

    A baseline is the run a comparison is made AGAINST and nothing more. It is not
    a target, it carries no verdict of its own, and choosing it by age rather than
    by quality is deliberate: §8.5 compares the same bundle re-processed, and any
    other rule would need a number §8.5 does not supply.
    """
    row = conn.execute(
        "SELECT run_id FROM run_manifest WHERE bundle_id = ? "
        "ORDER BY started_at, rowid", (bundle_id,)).fetchone()
    return None if row is None else row["run_id"]


def recorded_bundles(conn, *, source_scan_ref: str | None = None) -> Sequence[dict]:
    """Every sealed bundle, newest first, with what a person needs to name one.

    `--replay` refuses without a bundle id -- absent means refuse, never guess and
    never "the latest one" -- so a person needs a way to see the ids that exist.
    This is that listing and it chooses nothing.
    """
    sql = ("SELECT bundle_id, created_at, corpus_form, source_scan_ref, sealed_at "
           "FROM bundle_manifest WHERE sealed_at IS NOT NULL")
    args: list = []
    if source_scan_ref is not None:
        sql += " AND source_scan_ref = ?"
        args.append(source_scan_ref)
    return [dict(row) for row in conn.execute(sql + " ORDER BY created_at DESC, rowid DESC", args)]
