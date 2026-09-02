# src/llm_harness/stage_output.py
"""Map a P8 result onto P2's llm_interpretation envelope.

P2 owns the envelope vocabulary. This module translates P8 outcomes onto
`produced` / `abstained` / `deferred` / `error` and never writes P8's own
`abstain` into the envelope. `NeedsConsent` is not a P8 measurement and
creates no row. `ValidationUnavailable` IS one -- P8 ran and reached no
judgement -- and is written as `error`, whose verdict is no verdict at all.

The version tuple is live P2 `VERSION_TUPLE_FIELDS`. P8 supplies fingerprint
and model identifier; every other axis is caller-authored. `validator_version`
and `policy_version` stay in the opaque payload (and on P8 verdict/report
rows), not in that tuple.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, Sequence

from eval_harness.replay import ReplayContext, StageResult
from eval_harness.run import VERSION_TUPLE_FIELDS, record_version_tuple
from eval_harness.stage_output import DimensionValue, record_stage_output
from eval_harness.vocabulary import check_dimension
from evidence_shape.canonical import canonical_json

from llm_harness.records import (
    CallFailed, Dossier, P8Verdict, Refusal, ValidationUnavailable,
)
from llm_harness.sites import dispatch
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    BUDGET_EXHAUSTED,
    REJECT,
    WEAK,
)
from privacy.release import NeedsConsent

#: §8.5's `llm_grounding` dimension -- NOT this module's stage id. P8's stage is
#: `llm_interpretation`; each of the two raises under the other's checker. Checked
#: at import, so a P2 rename is a startup failure rather than a silent no-op.
DIMENSION: str = check_dimension("llm_grounding")

_QUALITY_OUTCOMES = frozenset({
    ACCEPT_DIRECT, ACCEPT_CONTEXT_SUPPORTED, WEAK, REJECT,
})
_STALE_TUPLE_KEYS = frozenset({"model_id", "validator_version", "policy_version"})


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, bytes):
        return value.hex()
    return value


def record_p8_version_tuple(conn: sqlite3.Connection, **axes) -> str:
    """Store the seven-field live P2 tuple. No P8 defaults for unused axes.

    Extra keys (including `validator_version` / `policy_version` / `model_id`)
    and the stale four-field SPEC tuple are refused. An intentionally empty
    caller axis must still be passed.
    """
    extra = set(axes) - set(VERSION_TUPLE_FIELDS)
    missing = set(VERSION_TUPLE_FIELDS) - set(axes)
    if extra or missing:
        raise ValueError(
            "version tuple fields: missing "
            f"{sorted(missing)}, unexpected {sorted(extra)}; "
            f"live VERSION_TUPLE_FIELDS are {VERSION_TUPLE_FIELDS}; "
            f"stale keys {_STALE_TUPLE_KEYS} belong in the opaque P8 payload"
        )
    return record_version_tuple(conn, **{name: axes[name] for name in VERSION_TUPLE_FIELDS})


def _envelope(result: object) -> tuple[str, str]:
    if isinstance(result, NeedsConsent):
        raise TypeError("NeedsConsent writes no P2 row")
    if isinstance(result, (CallFailed, ValidationUnavailable)):
        # `ValidationUnavailable` is a real stage outcome and gets a row. P8 was
        # called, walked into a missing injected capability, and reached no
        # judgement -- `dispatch` returns it from eight places (a null `conn`,
        # each site's absent dependencies, an unknown call site), so a replay
        # driver meets it on ordinary paths. Unmapped it fell through the
        # catch-all `TypeError` below, and inside `replay_bundle` an adapter's
        # exception collapses the WHOLE stage into one `error` row keyed on the
        # bundle: every other subject's row absent, and `verdict_for` scores an
        # absent row `not_run`, §8.5's word for the stage that did not run.
        #
        # `error` and not one of the other four. `abstained` is refused by the
        # record itself ("Never an abstain outcome") and would score
        # `abstained_correctly` -- a PASSING verdict -- against any label that
        # expected an abstention, which is §8.6's "false impression that an
        # unprocessed file was understood and found unimportant". `deferred`
        # pairs only with `ceiling_reached` and a missing capability is not a
        # budget event. `not_implemented` is the harness's word for a stage with
        # no adapter and scores `not_run`, the absent row this exists to stop
        # writing. `produced` claims a measurement nothing reached.
        #
        # `error` is the one outcome `verdict_for` refuses to score at all: NULL
        # verdict, `no_verdict_reason = 'stage_error'`. A degraded measurement
        # reported as degraded. P9 records the same result as a `_failure` with
        # cause `validation_unavailable` (grouping/p8_seam.py) and P11 groups it
        # with `CallFailed` as "not judgements about evidence"
        # (placement/pipeline.py `ModelJudgementUnavailable`); neither treats it
        # as an abstention either.
        return "error", "within_ceiling"
    if isinstance(result, Refusal):
        return "abstained", "within_ceiling"
    if isinstance(result, P8Verdict):
        if result.outcome in _QUALITY_OUTCOMES:
            return "produced", "within_ceiling"
        if result.outcome == ABSTAIN:
            if BUDGET_EXHAUSTED in result.reasons:
                return "deferred", "ceiling_reached"
            return "abstained", "within_ceiling"
        raise ValueError(f"unmapped P8 outcome {result.outcome!r}")
    raise TypeError(
        "emit_stage_output accepts P8Verdict, Refusal, CallFailed, or "
        f"ValidationUnavailable; got {type(result).__name__}"
    )


def _grounding_value(result: object, outcome: str) -> dict | None:
    """§8.5's `llm_grounding` question, answered from the verdict P8 actually reached.

    "Did every cited excerpt exist?" is `citations_checked`: each `CheckedCitation`
    carries `resolved` (the citation named something in the dossier) and
    `span_matched` (the excerpt was where the model said it was). The tallies are
    counted from that tuple, so a call whose citations resolved to nothing cannot
    read like one whose citations all held.

    `result.outcome` rides along because P8 maps four quality outcomes onto the one
    P2 outcome `produced` (`_QUALITY_OUTCOMES`): without it a `reject` -- which is
    P8's word for a grounding failure -- and an `accept_direct` over the same
    citation tallies would be the same measurement.

    NULL for everything else. "Did the model return unknown rather than guessing?"
    is answered by the row's OUTCOME, which is `abstained`; §8.6 forbids reporting a
    degraded or absent measurement as a good one, and a NULL value is P2's way of
    saying nothing was measured while the row still says the stage ran.

    No threshold and no score: SPEC Open question 2 is open and this module does not
    answer it. What counts as enough resolved citations is the label's business, and
    the label is `bundle_expectation.expected_value`.
    """
    if outcome != "produced":
        return None
    checked = result.citations_checked
    return {
        "outcome": result.outcome,
        "citations_checked": len(checked),
        "citations_resolved": sum(1 for item in checked if item.resolved),
        "citations_span_matched": sum(1 for item in checked if item.span_matched),
    }


def stage_result_fields(
    result: P8Verdict | Refusal | CallFailed | ValidationUnavailable, *,
    subject_ref: str, inputs: Sequence[str],
) -> dict:
    """The envelope fields for one P8 result, without writing them.

    P5's `extraction_stage_output` and P6's `fact_stage_output` publish the same
    shape: the fields `eval_harness.replay.StageResult` carries and P2 fills
    `run_id`, `stage_id` and `version_tuple_ref` around. P8 has two writers --
    `emit_stage_output`, which inserts directly, and `replay_stage_adapter`,
    whose rows P2's runner inserts -- and both read the mapping from here, so a
    live row and a replayed row cannot come to disagree about one result.
    """
    outcome, budget_state = _envelope(result)
    return {
        "subject_ref": subject_ref,
        "outcome": outcome,
        "payload": canonical_json(_jsonable(result)),
        "inputs": tuple(inputs),
        "budget_state": budget_state,
        # §8.5 is decomposed BY STAGE, and that decomposition is only real if the
        # stage hands over the row `assertions.assert_run` reads. Omitting this
        # left `stage_dimension_value` empty, and `verdict_for` scores an absent
        # row `not_run` -- §8.5's word for the stage that did not run at all.
        # One row always, including for an abstention, a deferral, a failure and
        # an unavailable validator: an absent row would report each of those as a
        # stage that never ran.
        "values": (DimensionValue(
            dimension=DIMENSION,
            subject_ref=subject_ref,
            outcome=outcome,
            value=_grounding_value(result, outcome),
        ),),
    }


def emit_stage_output(
    conn: sqlite3.Connection, *, run_id: str, subject_ref: str,
    result: P8Verdict | Refusal | CallFailed | ValidationUnavailable,
    inputs: tuple[str, ...], version_tuple_ref: str,
) -> int:
    """Write one `llm_interpretation` envelope. `produced_at` is stamped by P2."""
    envelope = stage_result_fields(result, subject_ref=subject_ref, inputs=inputs)
    manifest = conn.execute(
        "SELECT rm.version_tuple_ref AS manifest_version_tuple_ref, "
        "vt.version_tuple_ref AS existing_version_tuple_ref "
        "FROM run_manifest AS rm "
        "LEFT JOIN version_tuple AS vt "
        "ON vt.version_tuple_ref = rm.version_tuple_ref "
        "WHERE rm.run_id = ?",
        (run_id,),
    ).fetchone()
    if manifest is None:
        raise KeyError(f"run_id {run_id!r} does not identify an existing run_manifest")
    manifest_ref = manifest["manifest_version_tuple_ref"]
    if manifest["existing_version_tuple_ref"] is None:
        raise KeyError(
            f"run_manifest {run_id!r} references missing version_tuple {manifest_ref!r}"
        )
    if version_tuple_ref != manifest_ref:
        raise ValueError(
            f"version_tuple_ref {version_tuple_ref!r} does not match run_manifest "
            f"{run_id!r} version_tuple_ref {manifest_ref!r}"
        )
    return record_stage_output(
        conn,
        run_id=run_id,
        stage_id="llm_interpretation",
        subject_ref=envelope["subject_ref"],
        outcome=envelope["outcome"],
        payload=envelope["payload"],
        version_tuple_ref=version_tuple_ref,
        inputs=envelope["inputs"],
        budget_state=envelope["budget_state"],
        dimension_values=envelope["values"],
    )


def replay_recorded_response(
    conn: sqlite3.Connection,
    dossier: Dossier,
    *,
    evidence_resolver,
    site_dependencies,
    contradicts,
    dossier_builder: str,
    policy_version: str,
    handle_key: bytes,
):
    """Re-validate stored response bytes against the current evidence snapshot.

    Loads `llm_response.response_bytes`. Does not call a model client. Does not
    return a previously stored verdict, and does not append a second consequence
    to another part's store: Site A's `apply_verdict` writes P6's fact or its
    `unresolved` row, and `write_unresolved` is always an INSERT.

    `handle_key` is the same local-only key the dossier's bytes were built with.
    The stored bytes carry the handles the model was shown, so a replay reads
    them back through the same map the live call did -- which is the property
    that makes a replay comparable to the call it replays.
    """
    row = conn.execute(
        "SELECT response_bytes, model_id, prompt_fingerprint, release_audit_id "
        "FROM llm_response WHERE dossier_id = ? "
        # `response_id` is a uuid4, so under an injected fixed clock -- which is
        # how every test and every replay run is driven -- "the latest response"
        # was decided by random hex. `rowid` is insertion order.
        "ORDER BY observed_at DESC, rowid DESC",
        (dossier.dossier_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"no stored response for dossier {dossier.dossier_id!r}")
    return dispatch(
        conn,
        dossier,
        bytes(row["response_bytes"]),
        site_dependencies=site_dependencies,
        evidence_resolver=evidence_resolver,
        contradicts=contradicts,
        model_id=row["model_id"],
        prompt_fingerprint=row["prompt_fingerprint"],
        dossier_builder=dossier_builder,
        release_audit_id=row["release_audit_id"],
        policy_version=policy_version,
        apply_consequence=False,
        handle_key=handle_key,
    )


@dataclass(frozen=True)
class RecordedCall:
    """One recorded model call to re-validate, with the authorities it needs.

    Every field is the caller's. P8 chooses none of them here, exactly as
    `emit_stage_output` takes `subject_ref` and `inputs` from its caller rather
    than deriving them: which subject a measurement is ABOUT is what the
    bundle's expectation is keyed on, and the site authorities are per-file (Site
    A's `FactRequest` is built over one file's own P4 observations), so they
    cannot be shared across a corpus by this module's choice.
    """

    dossier: Dossier
    #: The `bundle_expectation.subject_ref` this call is measured against. It is
    #: also `stage_dimension_value`'s primary key with the run and the dimension,
    #: so two calls measured as one subject are a labelling error, not a merge.
    subject_ref: str
    #: §8.5's "where the error BEGAN" is computable only over these edges.
    inputs: tuple[str, ...]
    evidence_resolver: Callable[[str], Any]
    site_dependencies: Any
    contradicts: Callable[..., bool]


def replay_stage_adapter(
    calls: Sequence[RecordedCall], *, dossier_builder: str, policy_version: str,
    handle_key: bytes,
) -> Callable[[ReplayContext], list[StageResult]]:
    """P2's `llm_interpretation` stage adapter over recorded responses.

    This is what makes §8.5's LLM-grounding dimension measurable from a live
    composition: `eval_harness.driver.evaluate_bundle` walks the ten stages,
    hands this adapter the run it opened, and every result P8 reaches becomes
    one row `assert_run` can score.

    No model client is constructed and none is reachable from here --
    `replay_recorded_response` reads `llm_response.response_bytes` and
    re-validates them against the CURRENT evidence snapshot, which is the whole
    point of a replay: a stored verdict would reproduce itself.

    `apply_consequence` is false throughout, so a replay writes no second P6
    fact and no second `unresolved` row.

    A dossier with no stored response is a missing recording, not an outcome:
    `replay_recorded_response` raises `KeyError` and P2's runner records the
    stage as `error` rather than inventing a measurement for it.
    """
    def adapter(ctx: ReplayContext) -> list[StageResult]:
        results: list[StageResult] = []
        for call in calls:
            outcome = replay_recorded_response(
                ctx.conn, call.dossier,
                evidence_resolver=call.evidence_resolver,
                site_dependencies=call.site_dependencies,
                contradicts=call.contradicts,
                dossier_builder=dossier_builder,
                policy_version=policy_version,
                handle_key=handle_key,
            )
            # `dispatch` returns either `ValidationUnavailable` or a
            # (verdicts, report) pair. The report is P8's own record and is not
            # P2's envelope; the verdicts are what §8.5 measures.
            if isinstance(outcome, ValidationUnavailable):
                verdicts = (outcome,)
            else:
                verdicts, _report = outcome
            for verdict in verdicts:
                results.append(StageResult(**stage_result_fields(
                    verdict, subject_ref=call.subject_ref, inputs=call.inputs)))
        return results

    return adapter
