# src/eval_harness/replay.py
"""The replay runner.

Every run walks all ten §8.5 stages in §8.5's order. A stage with no adapter
reports `not_implemented`, which is what makes the harness runnable while nine of
the ten measured stages are still absent (02-segmentation-map.md, Order).

Adapters are an ARGUMENT, never a module-level registry: a run's stage set must be
visible in the call that started it and must not be mutable from elsewhere.
"""
from __future__ import annotations

import sqlite3
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from eval_harness.run import finish_run, record_version_tuple, start_run
from eval_harness.stage_output import DimensionValue, record_stage_output
from eval_harness.vocabulary import STAGE_IDS


@dataclass(frozen=True)
class ReplayContext:
    """What an adapter is given. It reads the bundle; it never reads the disk."""
    conn: sqlite3.Connection
    run_id: str
    bundle_id: str
    stage_id: str
    run_settings: Mapping[str, bool]
    budget_ceilings: Mapping[str, int]


@dataclass(frozen=True)
class StageResult:
    """One subject's outcome from one stage. `payload` stays the stage's own."""
    subject_ref: str
    outcome: str
    payload: str | None
    inputs: Sequence[str]
    budget_state: str
    values: Sequence[DimensionValue] = field(default_factory=tuple)


StageAdapter = Callable[[ReplayContext], Sequence[StageResult]]


def replay_bundle(conn: sqlite3.Connection, bundle_id: str, *,
                  version_tuple: dict, budget_ceilings: Mapping[str, int],
                  run_settings: Mapping[str, bool],
                  adapters: Mapping[str, StageAdapter],
                  run_kind: str = "replay") -> str:
    """Replay one bundle through whatever stages exist. Returns the run_id.

    No live filesystem is touched: adapters read the bundle through `ctx.conn`.
    P2 enforces no §8.6 ceiling — it hands the set to the stage that owns it and
    records what the stage reports.
    """
    from eval_harness.bundle import get_bundle

    manifest = get_bundle(conn, bundle_id)
    if manifest is None:
        raise KeyError(f"no bundle {bundle_id!r}")
    version_tuple_ref = record_version_tuple(conn, **version_tuple)
    run_id = start_run(
        conn, bundle_id=bundle_id, run_kind=run_kind,
        version_tuple_ref=version_tuple_ref, budget_ceilings=dict(budget_ceilings),
        run_settings=dict(run_settings),
        pinned_plan_id=manifest["pinned_plan_id"],
        pinned_plan_version=manifest["pinned_plan_version"],
    )
    for stage_id in STAGE_IDS:
        adapter = adapters.get(stage_id)
        if adapter is None:
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id, subject_ref=bundle_id,
                outcome="not_implemented", payload=None,
                version_tuple_ref=version_tuple_ref, inputs=[],
                budget_state="within_ceiling",
            )
            continue
        ctx = ReplayContext(conn=conn, run_id=run_id, bundle_id=bundle_id,
                            stage_id=stage_id, run_settings=dict(run_settings),
                            budget_ceilings=dict(budget_ceilings))
        try:
            results = list(adapter(ctx))
        except Exception:
            # A crash is `error`, which is distinct from an abstention and from a
            # deferral. It is never silently swallowed and never scored as either.
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id, subject_ref=bundle_id,
                outcome="error", payload=traceback.format_exc(),
                version_tuple_ref=version_tuple_ref, inputs=[],
                budget_state="within_ceiling",
            )
            continue
        if not results:
            # P2's own bookkeeping for a stage that ran and returned nothing, NOT
            # 6.10's abstention. Contract out 4's five outcomes are closed, so
            # this borrows `abstained` rather than minting a sixth name. What
            # separates the two is `subject_ref`: 4's domain is content hash,
            # group id, node id, branch id, model-call id, plan-version id, and a
            # bundle id is none of them, so a row keyed on the bundle is always
            # the runner's and never a stage's decision about a subject. A reader
            # counting a stage's abstentions excludes subject_ref = bundle_id.
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id, subject_ref=bundle_id,
                outcome="abstained", payload=None,
                version_tuple_ref=version_tuple_ref, inputs=[],
                budget_state="within_ceiling",
            )
            continue
        for result in results:
            record_stage_output(
                conn, run_id=run_id, stage_id=stage_id,
                subject_ref=result.subject_ref, outcome=result.outcome,
                payload=result.payload, version_tuple_ref=version_tuple_ref,
                inputs=result.inputs, budget_state=result.budget_state,
                dimension_values=result.values,
            )
    finish_run(conn, run_id)
    return run_id
