"""P10 -> P2. The envelope's vocabulary is P2's, and P10 maps into it.

`record_stage_output` takes `inputs` and `budget_state` as REQUIRED keywords. A
P10 adapter that defaulted either would break P2 Done-means 6 -- a run whose only
change is a lower ceiling must produce zero new divergences, which is only true
if a deferral never reaches a quality verdict -- so their ABSENCE is tested here,
not just their presence. A required input with no test for its absence is not
required.

Every guard below is written as a PAIR. `abstain` is refused and `abstained` is
accepted; `ceiling_reached` forbids `abstained` and permits `deferred`;
`dimension_value=None` writes no row and a value writes exactly one;
`tree_design` carries `tree` and `template_generation` carries `template`. A test
that only shows a guard firing passes just as well when the guard always fires.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from eval_harness.stage_output import ForeignVocabulary
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS
from tree_design.stage_output import (
    emit_template_generation_stage,
    emit_tree_design_stage,
)


@dataclass(frozen=True)
class RunIdentity:
    run_id: str
    version_tuple_ref: str


@pytest.fixture()
def run(conn):
    """The minimal P2 run identity these envelopes attach to.

    `conn` is the ROOT `tests/conftest.py` fixture -- `tests/integration/` has no
    conftest of its own -- and `open_database` creates only P1's tables.
    `version_tuple`, `run_manifest`, `stage_output` and `stage_dimension_value`
    are P2's, so this fixture creates P2's schema. Without it the first line
    below raises `sqlite3.OperationalError: no such table: version_tuple`.

    Built against the LIVE signatures, re-confirmed with `inspect.signature`:
    `record_version_tuple(conn, **fields)` takes exactly `VERSION_TUPLE_FIELDS`
    (seven), and `start_run(...) -> str` returns the id rather than an object.
    """
    from database_agent.budget import all_ceilings
    from eval_harness.run import (
        ANALYSIS_TIERS, VERSION_TUPLE_FIELDS, record_version_tuple, start_run,
    )
    from eval_harness.store import create_eval_schema

    create_eval_schema(conn)
    fields = {name: "fixture" for name in VERSION_TUPLE_FIELDS}
    fields["extractor_versions"] = {}
    fields["analysis_tiers_enabled"] = list(ANALYSIS_TIERS)
    version_tuple_ref = record_version_tuple(conn, **fields)
    run_id = start_run(
        conn, bundle_id="bundle-1", run_kind="replay",
        version_tuple_ref=version_tuple_ref,
        budget_ceilings=all_ceilings(conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        pinned_plan_id=None, pinned_plan_version=None)
    return RunIdentity(run_id=run_id, version_tuple_ref=version_tuple_ref)


def _envelope(conn, stage_output_id):
    return conn.execute(
        "SELECT * FROM stage_output WHERE stage_output_id = ?",
        (stage_output_id,)).fetchone()


def _dimension_rows(conn, stage_output_id):
    return conn.execute(
        "SELECT * FROM stage_dimension_value WHERE stage_output_id = ?",
        (stage_output_id,)).fetchall()


def test_p10_emits_only_p2s_two_stage_ids():
    """`P10` is not a stage id. A part name in that field would leave two of
    §8.5's ten stages with no producer and P2's `attributed_stage` unable to
    name where a tree error began."""
    assert "P10" not in STAGE_IDS
    assert "template_generation" in STAGE_IDS and "tree_design" in STAGE_IDS


def test_a_produced_branch_carries_its_inputs_and_a_tree_dimension_value(conn, run):
    stage_output_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="produced",
        budget_state="within_ceiling",
        inputs=("grouping:g_phys", "factual_validation:lecture"),
        version_tuple_ref=run.version_tuple_ref,
        payload={"display_label": "Academics"},
        dimension_value={"accepted": True})

    row = _envelope(conn, stage_output_id)
    assert row["stage_id"] == "tree_design"
    assert "grouping:g_phys" in row["inputs"]
    assert "factual_validation:lecture" in row["inputs"]
    assert row["budget_state"] == "within_ceiling"

    values = _dimension_rows(conn, stage_output_id)
    assert [v["dimension"] for v in values] == ["tree"]
    assert "tree" in DIMENSIONS


def test_template_generation_carries_template_and_never_the_tree_dimension(conn, run):
    """The negative twin of the test above.

    Both adapters share one `_emit`, so a dimension resolved from anything but
    the calling stage -- a default, a constant, the wrong branch of a lookup --
    passes the `tree_design` test and fails here. Asserting only that
    `tree_design` writes `tree` cannot tell a correct mapping from a hard-coded
    one.
    """
    stage_output_id = emit_template_generation_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="produced",
        budget_state="within_ceiling", inputs=("grouping:g_phys",),
        version_tuple_ref=run.version_tuple_ref,
        payload={"template_id": "t.academic"}, dimension_value={"accepted": True})

    row = _envelope(conn, stage_output_id)
    assert row["stage_id"] == "template_generation"
    values = _dimension_rows(conn, stage_output_id)
    assert [v["dimension"] for v in values] == ["template"]
    assert "template" in DIMENSIONS


def test_one_branch_is_measured_on_both_axes_in_one_run(conn, run):
    """`stage_dimension_value`'s primary key is `(run_id, dimension,
    subject_ref)`, so one node may carry a `tree` verdict AND a `template`
    verdict in one run without contesting a row. If the two adapters shared a
    dimension this would raise `IntegrityError` instead."""
    tree_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="produced",
        budget_state="within_ceiling", inputs=(),
        version_tuple_ref=run.version_tuple_ref, payload=None,
        dimension_value={"accepted": True})
    template_id = emit_template_generation_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="produced",
        budget_state="within_ceiling", inputs=(),
        version_tuple_ref=run.version_tuple_ref, payload=None,
        dimension_value={"accepted": True})

    assert tree_id != template_id
    rows = conn.execute(
        "SELECT dimension FROM stage_dimension_value WHERE subject_ref = ? "
        "ORDER BY dimension", ("n_root",)).fetchall()
    assert [r["dimension"] for r in rows] == ["template", "tree"]


def test_the_envelope_and_its_dimension_share_one_subject_ref(conn, run):
    """P2 joins the measurement to the envelope by subject. A dimension row
    filed under a different subject is a verdict about a node nobody emitted."""
    stage_output_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_academics", outcome="produced",
        budget_state="within_ceiling", inputs=(),
        version_tuple_ref=run.version_tuple_ref, payload=None,
        dimension_value={"accepted": True})
    row = _envelope(conn, stage_output_id)
    (value,) = _dimension_rows(conn, stage_output_id)
    assert value["subject_ref"] == row["subject_ref"] == "n_academics"
    assert value["outcome"] == row["outcome"] == "produced"
    assert value["stage_id"] == row["stage_id"] == "tree_design"


def test_a_rejected_template_abstains_within_the_ceiling(conn, run):
    """A candidate template rejected by V1-V6 is an evidential abstention. It is
    a design judgement and belongs in the quality score."""
    stage_output_id = emit_template_generation_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="abstained",
        budget_state="within_ceiling", inputs=("grouping:g_phys",),
        version_tuple_ref=run.version_tuple_ref,
        payload={"failed": ["V2"]}, dimension_value={"accepted": False})
    row = _envelope(conn, stage_output_id)
    assert row["outcome"] == "abstained"
    assert row["budget_state"] == "within_ceiling"


def test_a_template_deferred_branch_is_deferred_and_never_abstained(conn, run):
    """§8.6 and P2 Done-means 6. A ceiling-truncated pass must never be scored as
    a design judgement, so P2 refuses the wrong pairing at the writer.

    The pair: `deferred` + `ceiling_reached` is written, and `abstained` +
    `ceiling_reached` raises. Without the first half, a `_emit` that refused
    every ceiling-reached call would pass the second half.
    """
    stage_output_id = emit_template_generation_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="deferred",
        budget_state="ceiling_reached", inputs=("grouping:g_phys",),
        version_tuple_ref=run.version_tuple_ref,
        payload={"reason": "template-deferred"}, dimension_value=None)
    row = _envelope(conn, stage_output_id)
    assert (row["outcome"], row["budget_state"]) == ("deferred", "ceiling_reached")

    with pytest.raises(ValueError):
        emit_template_generation_stage(
            conn, run_id=run.run_id, subject_ref="n_other", outcome="abstained",
            budget_state="ceiling_reached", inputs=(),
            version_tuple_ref=run.version_tuple_ref, payload={},
            dimension_value=None)


def test_a_parts_own_record_word_is_refused_where_p2s_own_word_is_accepted(conn, run):
    """`abstain` and `abstained` differ by two letters and by one vocabulary.

    The first is a producing part's RECORD value and P2 raises
    `ForeignVocabulary` for it; the second is P2's ENVELOPE value and is written.
    Testing only the refusal would pass against an adapter that refused
    everything, and testing it with a word that is merely misspelled -- P10 has
    no `template-deferred` outcome anywhere -- would exercise the generic
    `not in OUTCOMES` branch and never reach the foreign-vocabulary guard at all.
    """
    with pytest.raises(ForeignVocabulary):
        emit_tree_design_stage(
            conn, run_id=run.run_id, subject_ref="n_root", outcome="abstain",
            budget_state="within_ceiling", inputs=(),
            version_tuple_ref=run.version_tuple_ref, payload={},
            dimension_value=None)

    stage_output_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="abstained",
        budget_state="within_ceiling", inputs=(),
        version_tuple_ref=run.version_tuple_ref, payload={},
        dimension_value=None)
    assert _envelope(conn, stage_output_id)["outcome"] == "abstained"


def test_a_stage_that_measured_nothing_writes_no_dimension_row(conn, run):
    """The pair: `dimension_value=None` writes zero rows, a value writes one.

    `None` is the MARKER for "this stage handed P2 no measurement" -- a deferral
    reached no verdict, so there is nothing to score. Writing a row holding NULL
    would put an unscored subject into P2's measured set.
    """
    deferred_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_deferred", outcome="deferred",
        budget_state="ceiling_reached", inputs=(),
        version_tuple_ref=run.version_tuple_ref, payload=None,
        dimension_value=None)
    assert _dimension_rows(conn, deferred_id) == []

    measured_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_measured", outcome="produced",
        budget_state="within_ceiling", inputs=(),
        version_tuple_ref=run.version_tuple_ref, payload=None,
        dimension_value={"accepted": True})
    assert len(_dimension_rows(conn, measured_id)) == 1


def test_two_replays_of_one_tree_store_one_payload_form(conn, run):
    """DM10's replay property, at the seam that records it.

    §8.5 diffs STORED FORMS. Two runs that produced the same tree must store
    byte-identical payloads, or every replay reports divergences that are only
    dict insertion order. `canonical_json` is what makes that true, so the
    adapter must use it rather than `json.dumps`.
    """
    first = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_a", outcome="produced",
        budget_state="within_ceiling", inputs=("grouping:g1", "grouping:g2"),
        version_tuple_ref=run.version_tuple_ref,
        payload={"display_label": "Academics", "node_type": "proposed"},
        dimension_value=None)
    second = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_b", outcome="produced",
        budget_state="within_ceiling", inputs=("grouping:g1", "grouping:g2"),
        version_tuple_ref=run.version_tuple_ref,
        payload={"node_type": "proposed", "display_label": "Academics"},
        dimension_value=None)

    assert _envelope(conn, first)["payload"] == _envelope(conn, second)["payload"]
    assert _envelope(conn, first)["inputs"] == _envelope(conn, second)["inputs"]


def test_an_absent_payload_is_stored_as_null_not_as_the_string_null(conn, run):
    """`payload=None` means "this stage published no payload". Passed through
    `canonical_json` it would become the four characters `null`, which reads back
    as a payload whose content is the JSON null -- a stage that published
    something empty rather than one that published nothing."""
    stage_output_id = emit_tree_design_stage(
        conn, run_id=run.run_id, subject_ref="n_root", outcome="produced",
        budget_state="within_ceiling", inputs=(),
        version_tuple_ref=run.version_tuple_ref, payload=None,
        dimension_value=None)
    assert _envelope(conn, stage_output_id)["payload"] is None


def test_inputs_and_budget_state_are_required_of_every_caller(conn, run):
    """P2 requires both. If P10's adapter defaults either, P10 becomes the place
    the requirement is lost, and it is lost silently: an empty `inputs` still
    writes a row, and `attributed_stage` then blames the stage that surfaced a
    tree error rather than the one where it began.

    A required input with no test for its absence is not required.
    """
    for missing in ("inputs", "budget_state"):
        kwargs = dict(
            run_id=run.run_id, subject_ref="n_root", outcome="produced",
            budget_state="within_ceiling", inputs=(),
            version_tuple_ref=run.version_tuple_ref, payload=None,
            dimension_value=None)
        del kwargs[missing]
        with pytest.raises(TypeError):
            emit_tree_design_stage(conn, **kwargs)
        with pytest.raises(TypeError):
            emit_template_generation_stage(conn, **kwargs)
