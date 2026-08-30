"""§8.5: "A single overall 'accuracy' number hides the mechanism that needs repair."

`74` §6 B11's named test is
`test_no_aggregate_accuracy_is_reachable_from_any_evaluation_view`; its negative
twin lives in `test_p13_learning.py`.

SPEC Open questions 8 and 9 are both OPEN and both are left open by construction:
the selection criterion is injected with no default, and the view is read-only
because whether a reviewer adjudication becomes an §8.7 correction is unsettled.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from eval_harness.comparison import DIMENSIONS

from review_surface.evaluation import (
    AggregateAccuracyRefused,
    DimensionResult,
    EvaluationView,
    SurfacedExample,
    evaluation_view,
)


def _view() -> EvaluationView:
    return EvaluationView(
        run_id="shadow-1", comparison_id="cmp-1",
        surfaced_examples=(
            SurfacedExample(
                example={"subject_ref": "d1", "baseline": {"node_id": "n-2"},
                         "candidate": {"node_id": "n-7"}},
                selection_reason="baseline and candidate disagree on destination"),
        ),
        per_dimension=(
            DimensionResult(dimension="placement", block={
                "newly_matching": [], "newly_divergent": ["d1"],
                "unchanged_count": 39, "deferral_changed": [],
                "attribution_histogram": {"placement_scoring": 1}}),
            DimensionResult(dimension="extraction", block={
                "newly_matching": [], "newly_divergent": [],
                "unchanged_count": 100, "deferral_changed": [],
                "attribution_histogram": {}}),
        ),
        read_only=True)


#: Every name that would compute or fetch one number over many. `statistics` and
#: `mean` are the obvious ones; `sum` and a division are how it gets written by
#: hand; the four P2 WRITERS are here because a renderer that produced the record
#: it renders could not honestly be called a renderer.
FORBIDDEN_NAMES: tuple[str, ...] = (
    "statistics", "mean", "fmean", "sum",
    "record_adjudication", "compare_runs", "run_shadow", "attribute_run")


def _documentation_strings(tree):
    """Docstrings and bare string statements, by NODE IDENTITY, not by regex.

    A text search over this module matches the banned words in its OWN prose --
    which is exactly what happened when this test was first written, and what has
    happened before on this project. Prose is excluded structurally instead.
    """
    return {id(node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)}


def _aggregating(trees):
    """Every place a module divides, or names something that makes one number."""
    offenders = []
    for name, tree in trees:
        documentation = _documentation_strings(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(
                    node.op, (ast.Div, ast.FloorDiv)):
                offenders.append(f"{name}:{node.lineno} division")
            found = None
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
                found = node.id
            elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_NAMES:
                found = node.attr
            elif isinstance(node, ast.alias) and node.name in FORBIDDEN_NAMES:
                found = node.name
            elif (isinstance(node, ast.Constant)
                  and isinstance(node.value, str)
                  and node.value in FORBIDDEN_NAMES
                  and id(node) not in documentation):
                found = node.value
            if found is not None:
                offenders.append(f"{name}:{getattr(node, 'lineno', 0)} {found}")
    return offenders


def _module_tree():
    import review_surface.evaluation as module

    return [("evaluation.py",
             ast.parse(pathlib.Path(module.__file__).read_text()))]


def _fake(source):
    return [("offender.py", ast.parse(source))]


def test_no_aggregate_accuracy_is_reachable_from_any_evaluation_view():
    """`74` §6 B11's named test, and Done-means 19 in both its clauses.

    The number is not merely absent: it is refused by name at the one place
    someone would add it, and the module computes none. A number nothing exposes
    today is a number something exposes tomorrow, so the second half is a guard
    over the PARSED module -- asserted against sabotage too, because a guard that
    has only ever found nothing is indistinguishable from one that cannot find
    anything.
    """
    with pytest.raises(AggregateAccuracyRefused) as caught:
        _view().overall_accuracy()
    assert "mechanism that needs repair" in str(caught.value)

    assert _aggregating(_module_tree()) == []
    assert _aggregating(_fake("rate = matching / total\n"))
    assert _aggregating(_fake("import statistics\n"))
    assert _aggregating(_fake("score = statistics.mean(values)\n"))
    assert _aggregating(_fake("total = sum(counts)\n"))
    assert _aggregating(_fake(
        "from eval_harness.comparison import compare_runs\n"))
    # Reading a per-dimension block is not aggregating, so the guard is about
    # collapsing rather than about touching P2's records at all.
    assert _aggregating(_fake("block = blocks[dimension]\n")) == []


def test_comparison_results_are_shown_per_dimension_and_never_collapsed():
    view = _view()
    assert len(view.per_dimension) == 2
    assert {d.dimension for d in view.per_dimension} <= set(DIMENSIONS)
    # Two dimensions, two separate blocks. Nothing merges them.
    assert view.per_dimension[0].block != view.per_dimension[1].block


def test_each_dimension_carries_p2s_own_block_verbatim():
    """P13 renames nothing and adds no field: renaming would make P13 the author
    of a shape P2 owns, and the day P2 adds a key the two would disagree."""
    placement = next(d for d in _view().per_dimension
                     if d.dimension == "placement")
    assert set(placement.block) == {
        "newly_matching", "newly_divergent", "unchanged_count",
        "deferral_changed", "attribution_histogram"}


def test_the_attribution_histogram_names_the_stage_an_error_began_in():
    """G13, read off P2's own block rather than recomputed."""
    placement = next(d for d in _view().per_dimension
                     if d.dimension == "placement")
    assert placement.attribution_histogram == {"placement_scoring": 1}
    extraction = next(d for d in _view().per_dimension
                      if d.dimension == "extraction")
    assert extraction.attribution_histogram == {}


def test_a_surfaced_example_is_p2s_disagreement_entry_carried_whole():
    example = _view().surfaced_examples[0]
    assert example.example["subject_ref"] == "d1"
    assert example.example["baseline"] != example.example["candidate"]
    assert example.selection_reason


def test_the_view_is_read_only():
    """SPEC Open question 9 is OPEN: whether an adjudication becomes an §8.7
    correction. Read-only until it is settled, and no action is collectable."""
    assert _view().read_only is True


def test_the_selection_criterion_is_injected_and_has_no_default():
    """SPEC Open question 8 is OPEN, and the SPEC's Deferred table already
    records the criterion as unsettled by the design."""
    signature = inspect.signature(evaluation_view)
    for name in ("select", "selection_reason"):
        assert signature.parameters[name].default is inspect.Parameter.empty
