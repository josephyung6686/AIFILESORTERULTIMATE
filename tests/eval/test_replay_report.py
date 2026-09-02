# tests/eval/test_replay_report.py
"""What a person reads after a replay, and the number it must never contain.

§8.5: "A single overall 'accuracy' number hides the mechanism that needs repair."
`driver.py` says the same and `comparison.py` says it a third time. The three
places that refuse to COMPUTE one are useless if the thing that PRINTS them
derives one, so the refusal is pinned here too, on the rendered text rather than
on a field name.

The second property these tests hold is emptiness. Every verdict of the seven and
every stage of the ten is printed including the ones at zero, for the reason
`compare_runs` writes a block for every dimension including an empty one: a
decomposition that omits its empty rows reads as a smaller problem than it is,
and "eight of the ten stages measured nothing" is the single most important thing
a reader of this report can learn.
"""
from __future__ import annotations

import re

import pytest

from eval_harness.assertions import assertions
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.comparison import compare_runs, get_comparison
from eval_harness.driver import EvaluationRun, evaluate_bundle
from eval_harness.replay import StageResult
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS, VERDICTS

import evaluation
from evaluation import (
    NOT_MEASURED, bundle_baseline, replay_lines, stage_status,
)

#: The one sentence nine of the ten stages get today, written out here rather
#: than imported, so a change to the wording has to be made twice on purpose.
ABSENT_LINE = ("  {stage} -- absent: no adapter, so its dimension could not be "
               "measured")

#: tests/eval/test_driver.py's list, applied to the rendered TEXT. Whole words:
#: prose may legitimately contain "corpus" and must not contain "accuracy".
FORBIDDEN_PARTS = {
    "accuracy", "score", "aggregate", "overall", "rate", "percent", "grade",
    "f1", "precision", "recall", "total",
}

SETTINGS = {"model_enabled": False, "embeddings_enabled": False}


def _tuple(**overrides):
    fields = dict(
        extractor_versions={}, graph_algorithm_version=None,
        prompt_fingerprint=None, model_identifier=None,
        template_library_version=None, placement_scorer_version=None,
        analysis_tiers_enabled=[],
    )
    fields.update(overrides)
    return fields


def _stage(dimension, value, *, outcome="produced"):
    # §8.6's one enforced pairing: `deferred` is `ceiling_reached` and never
    # anything else, so the fixture cannot produce a row P2 refuses to write.
    budget = "ceiling_reached" if outcome == "deferred" else "within_ceiling"

    def adapter(ctx):
        return [StageResult(
            subject_ref="file-1", outcome=outcome, payload=None, inputs=[],
            budget_state=budget,
            values=(DimensionValue(dimension=dimension, subject_ref="file-1",
                                   outcome=outcome, value=value),))]
    return adapter


@pytest.fixture()
def labelled(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(
        eval_conn, corpus_form="snapshot", source_scan_ref="scan-1",
        pinned_plan_id="plan-1", pinned_plan_version="1", policy_settings={})
    add_expectation(
        eval_conn, bundle_id, dimension="fact", subject_ref="file-1",
        expected_value={"field": "school", "value": "Columbia"},
        expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, bundle_id)
    return bundle_id


@pytest.fixture()
def unlabelled(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = open_bundle(
        eval_conn, corpus_form="snapshot", source_scan_ref="scan-1",
        pinned_plan_id=None, pinned_plan_version=None, policy_settings={})
    seal_bundle(eval_conn, bundle_id)
    return bundle_id


def _drive(conn, bundle_id, adapters):
    return evaluate_bundle(
        conn, bundle_id, version_tuple=_tuple(), budget_ceilings={},
        run_settings=SETTINGS, adapters=adapters)


def _forbidden_in(text: str) -> set[str]:
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    return words & FORBIDDEN_PARTS


def test_the_report_names_no_aggregate_and_derives_none(eval_conn, labelled):
    """§8.5's refusal, on the text a person actually reads."""
    driven = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})

    text = "\n".join(replay_lines(driven))

    assert _forbidden_in(text) == set()
    assert "%" not in text
    # A ratio is the shape that invites the number §8.5 forbids, even unnamed.
    assert re.search(r"\d\s*/\s*\d", text) is None
    assert re.search(r"\d+\s+of\s+\d+", text) is None


def test_every_verdict_of_the_seven_is_printed_including_the_empty_ones(
        eval_conn, labelled):
    """Seven stay seven. None is collapsed into another and none is omitted for
    being zero."""
    driven = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})

    lines = replay_lines(driven)

    printed = {verdict: line for verdict in VERDICTS for line in lines
               if re.fullmatch(rf"  {verdict} +\d+", line)}
    assert set(printed) == set(VERDICTS)
    assert printed["match"].split()[-1] == "1"
    assert printed["divergent"].split()[-1] == "0"
    assert printed["not_run"].split()[-1] == "0"


def test_every_stage_of_the_ten_is_printed_including_the_eight_that_are_absent(
        eval_conn, labelled):
    """The report's most load-bearing line. A bundle can be evaluated with nine of
    the ten stages absent, and a reader must be able to see that they were."""
    driven = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Cornell"})})

    lines = replay_lines(driven)

    # Matched on the block's own shape -- name, padding, count -- and not on
    # `stage + " "`, which the Stages block's `extraction -- ...` lines also
    # satisfy. The two blocks print the same ten names and a matcher either one
    # can answer silently reads whichever was rendered last.
    printed = {stage: line for stage in STAGE_IDS for line in lines
               if re.fullmatch(rf"  {stage} +\d+", line)}
    assert set(printed) == set(STAGE_IDS)
    assert printed["factual_validation"].split()[-1] == "1"
    assert printed["extraction"].split()[-1] == "0"
    assert printed["placement_scoring"].split()[-1] == "0"


def test_a_bundle_with_no_labels_says_so_rather_than_reporting_seven_zeroes(
        eval_conn, unlabelled):
    """The state every bundle this pipeline records is in today: sealed inside
    P1--P7, before any acceptance or any hand label exists. Seven zeroes and no
    sentence would read as a clean run."""
    driven = _drive(eval_conn, unlabelled, {})

    lines = replay_lines(driven)
    text = "\n".join(lines)

    assert driven.assertions_written == 0
    assert "carries no expectation" in text
    assert "corpus snapshot, not a reference corpus" in text
    assert _forbidden_in(text) == set()


def test_a_labelled_bundle_does_not_print_the_no_labels_sentence(
        eval_conn, labelled):
    """The negative half of the one above: the sentence is conditional on the
    thing it describes, not printed always."""
    driven = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})

    text = "\n".join(replay_lines(driven))

    assert "carries no expectation" not in text


def test_the_count_p2_cannot_know_is_a_sentence_and_never_a_zero(
        eval_conn, labelled):
    """`bundle_counts` returns None for `files_requiring_model_review` because it
    is P8's count and a zero would assert something P2 cannot know. §8.6 asks that
    unmeasured work stay visible AS unmeasured, and printing `0` or `None` for it
    is how that gets lost."""
    driven = _drive(eval_conn, labelled, {})

    lines = replay_lines(driven)
    line = next(line for line in lines if "awaiting model review" in line)

    assert driven.counts["files_requiring_model_review"] is None
    # The whole line, not a containment: what matters is that the value half is
    # the sentence and nothing else has been appended to it.
    assert line == '  files awaiting model review:               ' + NOT_MEASURED
    assert line.endswith("P2 does not guess it)")
    # Every other count line does carry a number, so the sentence is this one
    # count's treatment and not the renderer refusing to print any.
    assert next(other for other in lines
                if "files in the bundle" in other).split()[-1] == "0"


def test_the_baseline_diff_prints_every_dimension_including_the_empty_ones(
        eval_conn, labelled):
    """`compare_runs` writes a block for every dimension, always. A renderer that
    printed only the non-empty ones would undo that."""
    baseline = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})
    candidate = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Cornell"})})
    comparison_id = compare_runs(eval_conn, baseline.run_id, candidate.run_id)

    lines = replay_lines(
        candidate, comparison=get_comparison(eval_conn, comparison_id))

    printed = {d: line for d in DIMENSIONS for line in lines
               if line.strip().startswith(d + " ")}
    assert set(printed) == set(DIMENSIONS)
    assert "newly divergent 1" in printed["fact"]
    assert "newly divergent 0" in printed["placement"]
    assert _forbidden_in("\n".join(lines)) == set()


def test_a_deferral_is_reported_apart_from_a_divergence(eval_conn, labelled):
    """§8.6: a run whose only change is a budget event must show no regression.
    The renderer keeps the two on separate counters because `compare_runs` does."""
    baseline = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})
    candidate = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", None, outcome="deferred")})
    comparison_id = compare_runs(eval_conn, baseline.run_id, candidate.run_id)

    lines = replay_lines(
        candidate, comparison=get_comparison(eval_conn, comparison_id))

    fact = next(line for line in lines if line.strip().startswith("fact "))
    assert "deferral changed 1" in fact
    assert "newly divergent 0" in fact


def test_without_a_comparison_no_baseline_block_is_printed(eval_conn, labelled):
    """A first run over a bundle has nothing to be compared against, and a block
    of zeroes would read as a comparison that found no change."""
    driven = _drive(eval_conn, labelled, {})

    text = "\n".join(replay_lines(driven))

    assert "Against baseline" not in text


def test_the_baseline_is_the_earliest_run_and_the_first_run_has_none(
        eval_conn, labelled):
    """`--replay` compares against a baseline only when one exists. The first run
    over a bundle IS the baseline and is compared against nothing."""
    assert bundle_baseline(eval_conn, labelled) is None

    first = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})
    assert bundle_baseline(eval_conn, labelled) == first.run_id

    second = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Cornell"})})
    assert bundle_baseline(eval_conn, labelled) == first.run_id
    assert second.run_id != first.run_id


def test_the_report_names_the_run_and_the_bundle_it_read(eval_conn, labelled):
    """Two runs over one bundle are the whole of §8.5's comparison, so a report
    that named only the bundle could not be told apart from the other one."""
    driven = _drive(eval_conn, labelled, {})

    first = replay_lines(driven)[0]

    assert isinstance(driven, EvaluationRun)
    assert driven.bundle_id in first
    assert driven.run_id in first
    assert [row["verdict"] for row in assertions(eval_conn, driven.run_id)] \
        == ["not_run"]


# ======================================================================================
# Which of the ten stages actually ran
# ======================================================================================

def test_a_stage_that_failed_is_named_and_not_left_as_a_zero(eval_conn, labelled):
    """The failure this block exists to prevent, and it is not hypothetical.

    A stage that raised writes an `error` row and attributes nothing, so the
    attribution histogram prints `extraction 0` -- indistinguishable from a stage
    that ran cleanly and found nothing wrong. Over a real corpus this repository's
    extraction adapter refuses on every file (two recorded runs per file version,
    a filesystem-tier and a native-tier pass, disagreeing), so `0` was the report
    for a stage that measured nothing at all. §8.6: unfinished work stays visible
    AS unfinished."""
    def raises(ctx):
        raise RuntimeError("the reason nothing was measured")

    driven = _drive(eval_conn, labelled, {"extraction": raises})

    lines = replay_lines(driven, stages=stage_status(eval_conn, driven.run_id))
    text = "\n".join(lines)

    line = next(l for l in lines if l.strip().startswith("extraction --"))
    assert line == ("  extraction -- failed: RuntimeError: the reason nothing "
                    "was measured")


def test_the_eight_stages_with_no_adapter_are_named_as_absent(eval_conn, labelled):
    """Absent is a third thing, distinct from ran-and-found-nothing and from
    failed. Nine of the ten stages are absent in this repository today and a
    reader must be able to see which."""
    driven = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})

    lines = replay_lines(driven, stages=stage_status(eval_conn, driven.run_id))

    printed = {stage: line for stage in STAGE_IDS for line in lines
               if line.strip().startswith(stage + " --")}
    assert set(printed) == set(STAGE_IDS)
    assert printed["factual_validation"] == "  factual_validation -- ran"
    assert printed["extraction"] == ABSENT_LINE.format(stage="extraction")
    assert printed["placement_scoring"] == \
        ABSENT_LINE.format(stage="placement_scoring")


def test_without_the_stage_status_no_such_block_is_printed(eval_conn, labelled):
    """`replay_lines` stays pure over `EvaluationRun`: the stage outcomes are a
    second read of the database and arrive as an argument, so a caller that has
    not made that read prints no block rather than an empty one."""
    driven = _drive(eval_conn, labelled, {})

    text = "\n".join(replay_lines(driven))

    assert "Stages" not in text
    assert "no adapter" not in text


def test_the_stage_block_names_no_aggregate(eval_conn, labelled):
    """The same refusal, over the block that was added last."""
    def raises(ctx):
        raise RuntimeError("boom")

    driven = _drive(eval_conn, labelled, {"extraction": raises})

    text = "\n".join(
        replay_lines(driven, stages=stage_status(eval_conn, driven.run_id)))

    assert _forbidden_in(text) == set()
    assert "%" not in text


def test_a_stage_that_ran_and_measured_nothing_is_not_reported_as_having_run(
        eval_conn, labelled):
    """The third case, between absent and failed.

    An adapter that returns no result is a stage that RAN -- P2's runner writes
    its own `abstained` row keyed on the bundle to say so -- and it emitted no
    dimension value, so nothing it could have measured was measured. Reporting
    that as "ran" beside a stage that produced real values erases the
    distinction P2 keeps at the row level, and §8.6 asks the opposite: work that
    did not happen stays visible as work that did not happen."""
    driven = _drive(eval_conn, labelled, {"extraction": lambda ctx: []})

    lines = replay_lines(driven, stages=stage_status(eval_conn, driven.run_id))

    printed = {stage: line for stage in STAGE_IDS for line in lines
               if line.strip().startswith(stage + " --")}
    assert printed["extraction"] == \
        "  extraction -- ran, and measured nothing"
    assert printed["placement_scoring"] == \
        ABSENT_LINE.format(stage="placement_scoring")


def test_a_stage_that_measured_something_says_so(eval_conn, labelled):
    """The negative half: "ran" is reserved for a stage that emitted a value."""
    driven = _drive(eval_conn, labelled, {"factual_validation": _stage(
        "fact", {"field": "school", "value": "Columbia"})})

    lines = replay_lines(driven, stages=stage_status(eval_conn, driven.run_id))

    line = next(l for l in lines if l.strip().startswith("factual_validation --"))
    assert line == "  factual_validation -- ran"


# ======================================================================================
# One home for one vocabulary
# ======================================================================================

def test_the_composition_module_carries_p2s_outcomes_and_respells_none():
    """`test_p13_one_vocabulary.py`'s move, applied to the module this work added.

    That guard scans exactly three packages -- `grouping`, `placement`,
    `tree_design` -- so a new top-level composition module is not read by it, and
    a bare string constant here would be a second home for a vocabulary P2 owns.
    It is not added to that scan, because it carries no P13 gesture: what it
    carries is P2's Contract out §4 outcomes.

    Source-level for the reason that guard gives: Python interns short
    identifier-like strings, so an identity assertion would pass whether the name
    was imported or respelled. What distinguishes carrying from respelling is the
    ASSIGNMENT, and that is visible only in the source.
    """
    import ast
    import pathlib

    from eval_harness.vocabulary import OUTCOMES

    source = pathlib.Path(evaluation.__file__).read_text()
    literals = {
        node.value for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        # A docstring may name an outcome in prose; what is forbidden is a
        # comparison or an assignment against a respelt one.
        and not isinstance(getattr(node, "parent", None), ast.Expr)
    }
    respelt = literals & set(OUTCOMES)
    assert respelt == set(), (
        f"{sorted(respelt)} are P2's Contract out §4 outcomes, respelt here "
        "rather than imported from eval_harness.vocabulary")


def test_p2_names_each_of_its_five_outcomes_so_a_reader_can_carry_one():
    """A tuple alone cannot be carried: there is no name to import for one
    member, so every reader that needs a single outcome respells it. Naming the
    five is what makes the guard above satisfiable."""
    from eval_harness import vocabulary

    named = (vocabulary.OUTCOME_PRODUCED, vocabulary.OUTCOME_ABSTAINED,
             vocabulary.OUTCOME_DEFERRED, vocabulary.OUTCOME_NOT_IMPLEMENTED,
             vocabulary.OUTCOME_ERROR)
    assert named == vocabulary.OUTCOMES
