# src/tree_design/stage_output.py
"""P10's two §8.5 envelopes. P2 owns the vocabulary; P10 maps into it.

§8.5 names ten stages and P10 produces two of them: `tree_design` and
`template_generation`. `P10` is NOT a stage id — a part name in that field would
leave two of the ten with no producer, and P2's `attributed_stage` could not say
where a tree error began.

**Nothing here re-implements P2's rules.** `record_stage_output` already refuses
a foreign vocabulary, refuses `deferred` without `ceiling_reached`, and refuses
`abstained` WITH `ceiling_reached` — §8.6's rule that cost exhaustion must never
become a judgement about evidence. Restating any of that here would be a second
copy that drifts, so these adapters map and delegate.

What they DO own is the stage-to-dimension pairing, which is P10's because the
stages are: `tree_design` measures `tree`, `template_generation` measures
`template`, and neither may write the other's.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence

from evidence_shape.canonical import canonical_json
from eval_harness.stage_output import DimensionValue, record_stage_output

from tree_design.vocabulary import (
    DIMENSION_TEMPLATE,
    DIMENSION_TREE,
    TEMPLATE_GENERATION,
    TREE_DESIGN,
)

#: §8.5's two stage ids P10 produces, each with the §8.5 dimension it measures.
#: Paired in one place so a reader cannot find a stage without its dimension, and
#: so neither adapter can write the other's axis.
#:
#: The four names are IMPORTED, never spelled. `vocabulary.py` is their one home
#: (Task 1), and a literal here would be the second — so P2 renaming a stage
#: would leave this module green and emitting under a name nobody reads.
STAGE_DIMENSIONS: Mapping[str, str] = {
    TREE_DESIGN: DIMENSION_TREE,
    TEMPLATE_GENERATION: DIMENSION_TEMPLATE,
}


def _emit(conn: sqlite3.Connection, stage_id: str, *, run_id: str,
          subject_ref: str, outcome: str, budget_state: str,
          inputs: Sequence[str], version_tuple_ref: str,
          payload: Mapping[str, object] | None,
          dimension_value: Mapping[str, object] | None) -> int:
    """One envelope for one stage, plus at most one dimension value.

    `payload=None` stays NULL rather than becoming the four characters `null`.
    Canonicalising a `None` would read back as a payload whose content is the
    JSON null — a stage that published something empty rather than one that
    published nothing, which are different facts about the run.

    `dimension_value=None` writes NO row, and that is the MARKER for "this stage
    handed P2 no measurement". A deferral reached no verdict, so there is nothing
    to score; a row holding NULL would put an unscored subject into P2's measured
    set and P2 would divide by it.
    """
    values = ()
    if dimension_value is not None:
        values = (DimensionValue(
            dimension=STAGE_DIMENSIONS[stage_id], subject_ref=subject_ref,
            outcome=outcome, value=canonical_json(dict(dimension_value))),)
    return record_stage_output(
        conn, run_id=run_id, stage_id=stage_id, subject_ref=subject_ref,
        outcome=outcome,
        payload=None if payload is None else canonical_json(dict(payload)),
        version_tuple_ref=version_tuple_ref, inputs=inputs,
        budget_state=budget_state, dimension_values=values,
    )


def emit_tree_design_stage(conn: sqlite3.Connection, *, run_id: str,
                           subject_ref: str, outcome: str, budget_state: str,
                           inputs: Sequence[str], version_tuple_ref: str,
                           payload: Mapping[str, object] | None,
                           dimension_value: Mapping[str, object] | None) -> int:
    """§8.5's `tree_design` stage, measured on the `tree` dimension.

    `inputs` and `budget_state` are REQUIRED keywords with no defaults. P2
    requires both, and an adapter that defaulted either would make P10 the place
    the requirement was lost — silently, because an empty `inputs` still writes a
    row and `attributed_stage` would then blame the stage that surfaced a tree
    error rather than the one where it began.
    """
    return _emit(conn, TREE_DESIGN, run_id=run_id, subject_ref=subject_ref,
                 outcome=outcome, budget_state=budget_state, inputs=inputs,
                 version_tuple_ref=version_tuple_ref, payload=payload,
                 dimension_value=dimension_value)


def emit_template_generation_stage(
        conn: sqlite3.Connection, *, run_id: str, subject_ref: str,
        outcome: str, budget_state: str, inputs: Sequence[str],
        version_tuple_ref: str, payload: Mapping[str, object] | None,
        dimension_value: Mapping[str, object] | None) -> int:
    """§8.5's `template_generation` stage, measured on the `template` dimension.

    A candidate template refused by V1-V6 is `abstained` WITHIN the ceiling: it
    is an evidential judgement and belongs in the quality score. A branch the
    proposal ceiling cut off is `deferred` with `ceiling_reached` and carries no
    verdict at all.
    """
    return _emit(conn, TEMPLATE_GENERATION, run_id=run_id,
                 subject_ref=subject_ref, outcome=outcome,
                 budget_state=budget_state, inputs=inputs,
                 version_tuple_ref=version_tuple_ref, payload=payload,
                 dimension_value=dimension_value)
