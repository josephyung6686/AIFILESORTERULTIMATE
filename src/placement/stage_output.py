"""P11 -> P2. The envelope's vocabulary is P2's; the record's is P11's.

They are different vocabularies and P2 already refuses the wrong one:
`eval_harness/stage_output.py` enumerates P11's seven record outcomes and raises
`ForeignVocabulary` if one is written into an envelope. So this module is the
mapping between them and never a copy of either.

**One row must not collapse into another, and the shape says so.** P11 has three
results; each has its own envelope; the three envelopes are asserted distinct at
import. A budget deferral is `deferred` with `ceiling_reached` and NEVER
`abstained`, even though it rides on a record whose own outcome reads `abstain`.
Scored as `abstained`, P2 would grade a ceiling-truncated run
`abstained_correctly` or `abstained_incorrectly` -- a judgement about evidence --
when no judgement was made. Writing it as three named results rather than two
ordered `if`s is what keeps the distinction from being an ordering a later edit
can quietly reverse; P2's writer then enforces the pairing as well, so a wrong
mapping fails at the write.

The deferral is read off `deferred_stage`, which SPEC:734 says "exists
specifically so the interface can distinguish deferred work from completed work".
`PlacementDecision` enforces `deferred_stage is not None` if and only if
`abstention_reason == budget_deferred`, so the two can never drift apart.

`residual` is a P2 dimension with no same-named stage, which P2 records as its own
open question (`eval_harness/vocabulary.py`). P11 attaches it to
`placement_scoring` and says so here, rather than inventing an eleventh stage that
P2's closed ten does not contain.
"""
from __future__ import annotations

import json
import sqlite3
from types import MappingProxyType

from eval_harness.stage_output import DimensionValue, record_stage_output

from placement.vocabulary import (
    CANDIDATE_NODE_RETRIEVAL, DIMENSION_PLACEMENT, DIMENSION_RESIDUAL,
    DIMENSION_RETRIEVAL, P2_ABSTAINED, P2_CEILING_REACHED, P2_DEFERRED,
    P2_PRODUCED, P2_WITHIN_CEILING, PLACEMENT_SCORING, RESIDUAL,
)

#: What P11 did, in P11's words. Three results and no fourth: a fourth would be a
#: P11 outcome with no P2 envelope to carry it. The names are P11's own, because
#: neither `place`/`abstain` (the record's) nor `produced`/`deferred` (P2's) can
#: say "an §8.6 ceiling stopped the work" without borrowing the other's axis.
DECISION_WRITTEN: str = "decision_written"
EVIDENTIAL_ABSTENTION: str = "evidential_abstention"
BUDGET_DEFERRAL: str = "budget_deferral"

P11_RESULTS: tuple[str, ...] = (
    DECISION_WRITTEN, EVIDENTIAL_ABSTENTION, BUDGET_DEFERRAL,
)

_ENVELOPE: MappingProxyType = MappingProxyType({
    DECISION_WRITTEN: (P2_PRODUCED, P2_WITHIN_CEILING),
    EVIDENTIAL_ABSTENTION: (P2_ABSTAINED, P2_WITHIN_CEILING),
    BUDGET_DEFERRAL: (P2_DEFERRED, P2_CEILING_REACHED),
})

#: SPEC:280-288's "must not collapse", made structural. Three results, three
#: envelopes, checked at import -- so a mapping that ever sent a deferral to the
#: abstention envelope is a load error and not a quiet regrading of a whole run.
assert set(_ENVELOPE) == set(P11_RESULTS)
assert len(set(_ENVELOPE.values())) == len(P11_RESULTS)


class UnknownP11Result(ValueError):
    """A result P11 has no envelope for. Never mapped to the nearest one."""


def envelope_of(result: str) -> tuple[str, str]:
    """One P11 result to one `(outcome, budget_state)` pair. SPEC:273-278."""
    try:
        return _ENVELOPE[result]
    except KeyError:
        raise UnknownP11Result(
            f"{result!r} is not one of P11's {P11_RESULTS}; a result with no "
            "envelope is a measurement P2 cannot carry, and picking the nearest "
            "one is how a deferral becomes a judgement about evidence"
        ) from None


def result_of(decision) -> str:
    """Which of P11's three results this decision is.

    `deferred_stage` is the discriminator rather than `abstention_reason`, because
    it is the field SPEC:734 gives that job -- and because the record makes the
    two equivalent, so reading the one that names the concept costs nothing.
    """
    if decision.deferred_stage is not None:
        return BUDGET_DEFERRAL
    if decision.destination is None and decision.abstention_reason is not None:
        return EVIDENTIAL_ABSTENTION
    return DECISION_WRITTEN


def envelope_for(decision) -> tuple[str, str]:
    """SPEC:273-278's mapping, as a function over one decision."""
    return envelope_of(result_of(decision))


def dimension_for(decision) -> DimensionValue:
    """§8.5's two metrics. A correct abstention passes both (Done-means 11).

    The value is the decision's own shape rather than its content: a replay
    compares what the engine decided and why, and dumping the explanation here
    would make every prose edit look like a divergence.
    """
    from placement.store import subject_ref_of

    outcome, _ = envelope_for(decision)
    dimension = (DIMENSION_RESIDUAL if decision.origin_stage == RESIDUAL
                 else DIMENSION_PLACEMENT)
    return DimensionValue(
        dimension=dimension, subject_ref=subject_ref_of(decision.subject),
        outcome=outcome,
        value={
            "outcome": decision.outcome,
            "node_id": (decision.destination.node_id
                        if decision.destination else None),
            "abstention_reason": decision.abstention_reason,
            "support_score": decision.two_condition.support_score,
            "support_threshold": decision.two_condition.support_threshold,
            "margin_over_next": decision.two_condition.margin_over_next,
            "margin_threshold": decision.two_condition.margin_threshold,
            "meets_margin": decision.two_condition.meets_margin,
            "verdict": decision.two_condition.verdict,
            "unsupported_levels": list(decision.decision_depth.unsupported_levels),
        },
    )


def candidate_subject_ref(plan_version: str, subject_ref: str) -> str:
    """The namespaced subject `candidate_node_retrieval` is measured under.

    `stage_dimension_value` declares `PRIMARY KEY (run_id, dimension,
    subject_ref)`, and `retrieval` is already P9's dimension for its own retrieval
    stage (`grouping/stage_output.py`). An un-namespaced ref would make a
    full-pipeline replay raise `IntegrityError` the moment P9 and P11 both keyed a
    `retrieval` row on the same file -- and would collide with this part's own
    `placement_scoring` row for that subject too.

    The `plan_version` in the key is not decoration. `retrieval` sits in
    `SHARED_EVIDENCE_DIMENSIONS` (`eval_harness/vocabulary.py`) while P11's
    candidate retrieval is plan-scoped by construction -- it retrieves only the
    legal destinations of one frozen version. Keying on the version means two plan
    versions produce two measurements rather than one contested row.
    """
    return f"candidates:{plan_version}:{subject_ref}"


def _retrieval_value(retrieval) -> dict:
    """What was retrieved, what was ruled out, and what was only semantic.

    The suppression is in here because §6.3 suppresses actively and SPEC:502-504
    requires the record: a replay that cannot see what was ruled out cannot tell a
    retrieval miss from a deliberate exclusion, and a review surface that cannot
    see it cannot answer "why not that folder?".
    """
    return {
        "plan_version": retrieval.plan_version,
        "retrieved": [candidate.node_id for candidate in retrieval.candidates],
        "suppressed": sorted({node_id for conflict in retrieval.conflicts
                              for node_id in conflict.suppressed_node_ids}),
        "semantic_only": sorted(retrieval.semantic_only_node_ids),
    }


def emit_retrieval_stage(conn: sqlite3.Connection, *, run_id: str, retrieval,
                         version_tuple_ref: str, inputs) -> int:
    """§6.2's stage. Its subject is the file or group a candidate set was for.

    It carries a `DimensionValue` because a stage that writes none is
    structurally unattributable: `eval_harness/attribution.py` reads ONLY
    `stage_dimension_value` rows to decide both which stage emitted a failing
    assertion and which stages qualify as ancestors. Without one, a placement
    error that began in retrieval could never be measured as a retrieval error,
    no matter what P2 did.

    The dimension is `retrieval`, and the design settles which one: §8.5's list
    reads *"Retrieval quality: for sparse files, did the correct anchors appear in
    the top candidate neighborhood?"* -- which is this stage, in the design's own
    words. §8.5's ten dimensions are a shorter and separate list from its ten
    stages ON PURPOSE, so two stages sharing one dimension is the shape the design
    already has, and no eleventh dimension is invented to avoid it.
    """
    outcome = P2_PRODUCED if retrieval.candidates else P2_ABSTAINED
    subject_ref = candidate_subject_ref(retrieval.plan_version,
                                        retrieval.subject_ref)
    value = _retrieval_value(retrieval)
    return record_stage_output(
        conn, run_id=run_id, stage_id=CANDIDATE_NODE_RETRIEVAL,
        subject_ref=subject_ref, outcome=outcome,
        payload=json.dumps(value, sort_keys=True),
        version_tuple_ref=version_tuple_ref, inputs=list(inputs),
        budget_state=P2_WITHIN_CEILING,
        # The envelope's subject_ref and the dimension row's must be EQUAL:
        # `_stage_verdicts` keys on the dimension row's while `_edges` keys on the
        # envelope's, so a mismatch attributes nothing.
        dimension_values=(DimensionValue(
            dimension=DIMENSION_RETRIEVAL, subject_ref=subject_ref,
            outcome=outcome, value=value),),
    )


def emit_scoring_stage(conn: sqlite3.Connection, *, run_id: str, decision,
                       version_tuple_ref: str, inputs) -> int:
    """§6.10's stage, with the measured dimension attached.

    `inputs` are the `subject_ref`s of the `grouping`, `tree_design` and
    `factual_validation` stage outputs this decision consumed. Naming them is
    what lets P2 attribute a placement error to the stage it began in, rather
    than to the last stage that touched the file.

    `candidate_node_retrieval`'s own ref is appended here rather than left to the
    caller, because the ancestor walk reaches a stage ONLY through `inputs[]`.
    Emitting a dimension value from the retrieval stage and then omitting it from
    this list would leave the stage measured and still unreachable -- both halves
    are required.
    """
    from placement.store import subject_ref_of

    outcome, budget_state = envelope_for(decision)
    subject_ref = subject_ref_of(decision.subject)
    retrieval_ref = candidate_subject_ref(decision.plan_version, subject_ref)
    return record_stage_output(
        conn, run_id=run_id, stage_id=PLACEMENT_SCORING,
        subject_ref=subject_ref, outcome=outcome,
        payload=json.dumps({
            "decision_id": decision.decision_id,
            "plan_version": decision.plan_version,
            "origin_stage": decision.origin_stage,
            "confidence_class": decision.confidence_class,
            "review_policy": decision.review_policy,
            "deferred_stage": decision.deferred_stage,
        }, sort_keys=True),
        version_tuple_ref=version_tuple_ref,
        inputs=[*inputs, retrieval_ref],
        budget_state=budget_state,
        dimension_values=(dimension_for(decision),),
    )
