# src/grouping/stage_output.py
"""P9's three P2 stages, and the mapping from a P9 result to a P2 envelope.

P9 emits `retrieval`, `graph_construction` and `grouping`. It does not emit
`llm_interpretation`: that stage measures the model call, P8 makes the call, and
a second emitter would double-count every one of them in the replay.

The mapping is three lines and they are stated rather than derived. §8.6 requires
a budget deferral to be `deferred` with `ceiling_reached` and never `abstained`,
because P2's Done-means 6 needs a run whose only change is a lower ceiling to
produce zero new divergences -- which is only true if a deferral never reaches a
quality verdict. An evidence refusal is the opposite: a stop rule fired, or
coherence abstained, or retrieval found no plausible anchor, and each of those IS
a quality verdict, taken inside the ceiling.

Replay only. Emitting from ordinary ingestion would put a measurement in the
harness for a run nobody asked to evaluate.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from eval_harness.stage_output import DimensionValue, record_stage_output
from evidence_shape.canonical import canonical_json

from grouping.vocabulary import (
    P2_ABSTAINED,
    P2_CEILING_REACHED,
    P2_DEFERRED,
    P2_GRAPH_DIMENSION,
    P2_GRAPH_STAGE,
    P2_GROUPING_DIMENSION,
    P2_GROUPING_STAGE,
    P2_MODEL_CALL_STAGE,
    P2_PRODUCED,
    P2_RETRIEVAL_DIMENSION,
    P2_RETRIEVAL_STAGE,
    P2_WITHIN_CEILING,
)

#: The three P2 stage ids P9 owns, imported rather than re-spelled.
RETRIEVAL_STAGE: str = P2_RETRIEVAL_STAGE
GRAPH_STAGE: str = P2_GRAPH_STAGE
GROUPING_STAGE: str = P2_GROUPING_STAGE

P9_STAGES: tuple[str, ...] = (RETRIEVAL_STAGE, GRAPH_STAGE, GROUPING_STAGE)

#: Named so the exclusion is legible rather than merely absent: this is P8's
#: stage, and nothing in this module emits it.
P8_MODEL_CALL_STAGE: str = P2_MODEL_CALL_STAGE

#: The §8.5 dimension each stage hands over. One per stage, chosen by the emitting
#: stage rather than looked up from the stage id by P2.
DIMENSION_BY_STAGE: dict[str, str] = {
    RETRIEVAL_STAGE: P2_RETRIEVAL_DIMENSION,
    GRAPH_STAGE: P2_GRAPH_DIMENSION,
    GROUPING_STAGE: P2_GROUPING_DIMENSION,
}

#: What P9 did, in P9's words. Three results and no fourth: a fourth would be a
#: P9 outcome with no P2 envelope to carry it.
RECORD_WRITTEN: str = "record_written"
EVIDENCE_REFUSAL: str = "evidence_refusal"
BUDGET_DEFERRED: str = "budget_deferred"

P9_RESULTS: tuple[str, ...] = (RECORD_WRITTEN, EVIDENCE_REFUSAL, BUDGET_DEFERRED)

_ENVELOPE: dict[str, tuple[str, str]] = {
    RECORD_WRITTEN: (P2_PRODUCED, P2_WITHIN_CEILING),
    EVIDENCE_REFUSAL: (P2_ABSTAINED, P2_WITHIN_CEILING),
    BUDGET_DEFERRED: (P2_DEFERRED, P2_CEILING_REACHED),
}


class UnknownP9Result(ValueError):
    """A result P9 has no envelope for. Never mapped to the nearest one."""


def map_result(result: str) -> tuple[str, str]:
    """One P9 result to its `(outcome, budget_state)` pair."""
    try:
        return _ENVELOPE[result]
    except KeyError:
        raise UnknownP9Result(
            f"{result!r} is not one of P9's {P9_RESULTS}. Mapping it to the "
            "nearest outcome would put a measurement in the replay that no P9 "
            "code produced."
        ) from None


def _emit(
    conn: sqlite3.Connection,
    *,
    stage_id: str,
    run_id: str,
    subject_ref: str,
    result: str,
    payload: object,
    version_tuple_ref: str,
    inputs: Sequence[str],
) -> int:
    outcome, budget_state = map_result(result)
    return record_stage_output(
        conn,
        run_id=run_id,
        stage_id=stage_id,
        subject_ref=subject_ref,
        # Opaque to P2 and canonical, so two equal measurements serialise one way
        # and a replay diff is about the measurement rather than about key order.
        payload=canonical_json(payload),
        outcome=outcome,
        version_tuple_ref=version_tuple_ref,
        inputs=tuple(inputs),
        budget_state=budget_state,
        dimension_values=(DimensionValue(
            dimension=DIMENSION_BY_STAGE[stage_id],
            subject_ref=subject_ref,
            outcome=outcome,
            value=payload,
        ),),
    )


def emit_retrieval_stage(conn: sqlite3.Connection, **kwargs) -> int:
    """§4.2: did the correct anchors appear in the top candidate neighbourhood?"""
    return _emit(conn, stage_id=RETRIEVAL_STAGE, **kwargs)


def emit_graph_stage(conn: sqlite3.Connection, **kwargs) -> int:
    """§4.3: did edges reflect meaningful typed relationships, and did generic
    hubs create false neighbours?"""
    return _emit(conn, stage_id=GRAPH_STAGE, **kwargs)


def emit_grouping_stage(conn: sqlite3.Connection, **kwargs) -> int:
    """§4: did candidate groups include the correct members and exclude outliers?"""
    return _emit(conn, stage_id=GROUPING_STAGE, **kwargs)
