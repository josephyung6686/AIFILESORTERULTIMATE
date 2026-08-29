# src/eval_harness/driver.py
"""The replay driver — one bundle in, one evaluated run out.

P2 publishes four steps and, until this module, joined none of them from
`src/`: `replay_bundle` walks §8.5's ten stages, `assert_run` turns each
`stage_dimension_value` into a verdict against the bundle's expectation,
`attribute_run` fills §8.5's "where the error BEGAN", and the readers report
what happened. Every scored run in this repository was assembled inside a test,
which meant `verdict_for` — the whole of P2's judgement — was unreachable from a
live composition.

**This module decides nothing.** It owns the ORDER of those four steps and
nothing else, exactly as `orchestrator.run_p1_p7` owns the order of P1–P7 and
injects every policy-bearing dependency. The version tuple, the §8.6 ceilings,
the two run disables and the stage adapters are all the caller's; there is no
threshold, no tolerance and no clock here, because §8.5 states none and SPEC
Open question 2 is open.

It also computes no single number. §8.5: "A single overall 'accuracy' number
hides the mechanism that needs repair." What comes back is a count per verdict,
a count per attributed stage, and §8.6's bundle count line — three
decompositions and nothing over them.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any, Mapping

from eval_harness.assertions import assert_run, verdict_counts
from eval_harness.attribution import attribute_run, attribution_histogram
from eval_harness.counts import bundle_counts
from eval_harness.replay import StageAdapter, replay_bundle


@dataclass(frozen=True)
class EvaluationRun:
    """What one evaluated run reports. Three decompositions, no number over them.

    `assertions_written` and `attributed` are row counts of work done, not
    quality readings: `assertions_written` is one per expectation in the bundle
    and `attributed` is one per wrong terminal outcome. Neither divides by
    anything, and §8.6's legibility requirement is why they are here at all — a
    partial evaluation must be reported as partial.
    """

    run_id: str
    bundle_id: str
    assertions_written: int
    attributed: int
    #: verdict -> count, with the two cases §8.5 defines no verdict for under
    #: `unverdicted`. Seven verdicts stay seven; none is collapsed into another.
    verdicts: Mapping[str, int]
    #: attributed_stage -> count. §8.5's ten stages, never summed.
    attribution: Mapping[str, int]
    #: §8.6's count line, read off the bundle with no live filesystem present.
    counts: Mapping[str, Any]


def evaluate_bundle(
        conn: sqlite3.Connection, bundle_id: str, *,
        version_tuple: dict, budget_ceilings: Mapping[str, int],
        run_settings: Mapping[str, bool],
        adapters: Mapping[str, StageAdapter],
        run_kind: str = "replay") -> EvaluationRun:
    """Replay one bundle through `adapters`, then assert and attribute the run.

    `adapters` is a stage id -> adapter mapping and is an ARGUMENT for the same
    reason `replay_bundle` makes it one: a run's stage set must be visible in
    the call that started it. A stage with no adapter reports `not_implemented`
    and its dimension scores `not_run`, so a bundle can be evaluated while nine
    of the ten measured stages are still absent.

    `run_kind` has the one default `replay_bundle` already publishes; it is the
    only defaulted argument here, and it names a KIND of run rather than a
    policy. Everything a §8.5 comparison must be able to name — the six version
    axes, the ceilings the run was given, the two independent stage disables —
    arrives from the caller and is recorded verbatim on the run manifest.

    Raises `KeyError` for a bundle that does not exist, from `replay_bundle`,
    before a run manifest is opened.
    """
    run_id = replay_bundle(
        conn, bundle_id, version_tuple=version_tuple,
        budget_ceilings=budget_ceilings, run_settings=run_settings,
        adapters=adapters, run_kind=run_kind)
    written = assert_run(conn, run_id)
    # After the assertions and never before: `attribute_run` reads
    # `assertion.verdict` to decide which stages qualify as an origin, so an
    # attribution pass over an unasserted run attributes nothing and reports
    # zero failures on a run that may be full of them.
    attributed = attribute_run(conn, run_id)
    return EvaluationRun(
        run_id=run_id,
        bundle_id=bundle_id,
        assertions_written=written,
        attributed=attributed,
        verdicts=verdict_counts(conn, run_id),
        attribution=attribution_histogram(conn, run_id),
        counts=bundle_counts(conn, bundle_id),
    )
