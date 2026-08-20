# src/eval_harness/adversarial.py
"""Contract out §9 — the twelve-case adversarial suite, as a gate.

§8.5: "Every new extractor, model, prompt, or graph mechanism should run against
this suite before it affects a user's live plan."

A case that could not run is `not_run`, never `pass`. Whether a failing case
BLOCKS the change, and whether P2 or the release process enforces it, is SPEC Open
question 9: `run_gate` returns a report, raises nothing, and decides nothing.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

CASE_IDS: tuple[str, ...] = (
    "A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10", "A11", "A12",
)

_CASE_DIR = (Path(__file__).resolve().parents[2]
             / "tests" / "eval" / "fixtures" / "adversarial")


class MissingCase(Exception):
    """A named case has no fixture file. Never treated as a skip."""


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    verdict: str          # pass | fail | not_run
    reason: str
    subject_results: tuple


@dataclass(frozen=True)
class GateReport:
    """Per-case results and three counts. No boolean and no aggregate.

    There is deliberately no `passed` attribute: collapsing twelve failure modes
    into one flag is the shape §8.5 rejects, and whether the gate blocks at all is
    Open question 9.
    """
    results: tuple
    pass_count: int
    fail_count: int
    not_run_count: int


def load_case(case_id: str) -> dict:
    path = _CASE_DIR / f"{case_id}.json"
    if not path.exists():
        raise MissingCase(f"no fixture for adversarial case {case_id} at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_cases() -> list[dict]:
    return [load_case(case_id) for case_id in CASE_IDS]


def _subjects(case: dict) -> list[dict]:
    """A case is one subject unless it declares several (A03 declares two)."""
    return case.get("subjects") or [case]


def build_case_bundle(conn: sqlite3.Connection, case: dict) -> str:
    """One sealed bundle per case, carrying its fixture rows and its expectations."""
    from eval_harness.bundle import (
        add_expectation, add_extraction_run, add_text_unit, open_bundle, seal_bundle,
    )
    bundle_id = open_bundle(
        conn, corpus_form="snapshot", source_scan_ref=f"{case['case_id']}-scan",
        pinned_plan_id=f"{case['case_id']}-plan", pinned_plan_version="1",
        policy_settings={},
    )
    for row in case.get("extraction_runs", []):
        add_extraction_run(conn, bundle_id, row=row)
    for row in case.get("text_units", []):
        add_text_unit(conn, bundle_id, row=row)
    for subject in _subjects(case):
        add_expectation(
            conn, bundle_id, dimension=case["dimension"],
            subject_ref=subject["subject_ref"],
            expected_value=subject.get("expected_value"),
            expected_outcome_kind=subject["expected_outcome_kind"],
            source="hand-labelled",
        )
    seal_bundle(conn, bundle_id)
    return bundle_id


def _bundle_verdict(conn: sqlite3.Connection, bundle_id: str,
                    case: dict, subject: dict) -> tuple[str, str]:
    """A case assertable from the bundle alone. A9 is the only one today."""
    from eval_harness.bundle import extraction_runs
    from eval_harness.store import canonical_json

    expected = subject["expected_value"]
    forbidden = subject["forbidden_value"]
    for row in extraction_runs(conn, bundle_id):
        observed = {k: row.get(k) for k in expected}
        if canonical_json(observed) == canonical_json(expected):
            if canonical_json({k: row.get(k) for k in forbidden}) == \
                    canonical_json(forbidden):
                return "fail", "forbidden outcome present on the same row"
            return "pass", "expected run row found in the bundle"
    return "fail", "no run row in the bundle matches the expected outcome"


def _stage_verdict(conn: sqlite3.Connection, run_id: str, case: dict,
                   subject: dict) -> tuple[str, str]:
    from eval_harness.store import canonical_json

    row = conn.execute(
        "SELECT outcome, value FROM stage_dimension_value "
        "WHERE run_id = ? AND dimension = ? AND subject_ref = ?",
        (run_id, case["dimension"], subject["subject_ref"])).fetchone()
    if row is None:
        return "not_run", "no stage produced a value for this subject"
    if row["outcome"] in ("not_implemented", "error"):
        return "not_run", f"stage outcome was {row['outcome']}"
    if row["outcome"] == "deferred":
        # §8.6: a budget event is neither a pass nor a failure.
        return "not_run", "stage outcome was deferred (§8.6)"
    observed = None if row["value"] is None else json.loads(row["value"])
    if observed is not None and canonical_json(observed) == \
            canonical_json(subject["forbidden_value"]):
        return "fail", "forbidden outcome was produced"
    if subject["expected_outcome_kind"] == "abstained":
        if row["outcome"] == "abstained":
            return "pass", "abstained as required"
        return "fail", "produced where abstention was required"
    if row["outcome"] != "produced":
        return "fail", f"expected a produced value, got {row['outcome']}"
    if canonical_json(observed) == canonical_json(subject["expected_value"]):
        return "pass", "expected outcome produced, forbidden outcome absent"
    return "fail", "produced value does not match the expected outcome"


def run_case(conn: sqlite3.Connection, case: dict, *, adapters: Mapping[str, object],
             version_tuple: dict, budget_ceilings: Mapping[str, int],
             run_settings: Mapping[str, bool]) -> CaseResult:
    """One case. A case passes only when the expected outcome is observed AND the
    forbidden outcome is absent."""
    from eval_harness.replay import replay_bundle

    bundle_id = build_case_bundle(conn, case)
    run_id = None
    if case["assert_against"] == "stage":
        run_id = replay_bundle(conn, bundle_id, version_tuple=version_tuple,
                               budget_ceilings=budget_ceilings,
                               run_settings=run_settings, adapters=adapters,
                               run_kind="adversarial")
    results = []
    for subject in _subjects(case):
        if case["assert_against"] == "bundle":
            verdict, reason = _bundle_verdict(conn, bundle_id, case, subject)
        else:
            verdict, reason = _stage_verdict(conn, run_id, case, subject)
        results.append((subject["subject_ref"], verdict, reason))
    verdicts = [v for _, v, _ in results]
    if "fail" in verdicts:
        case_verdict, reason = "fail", next(r for _, v, r in results if v == "fail")
    elif "not_run" in verdicts:
        case_verdict, reason = "not_run", next(r for _, v, r in results if v == "not_run")
    else:
        case_verdict, reason = "pass", "every subject passed"
    return CaseResult(case_id=case["case_id"], verdict=case_verdict, reason=reason,
                      subject_results=tuple(results))


def run_gate(conn: sqlite3.Connection, *, adapters: Mapping[str, object],
             version_tuple: dict, budget_ceilings: Mapping[str, int],
             run_settings: Mapping[str, bool]) -> GateReport:
    """All twelve cases. Returns a report and takes no action on it.

    Wiring this to "before it affects a user's live plan" (§8.5) is a release-
    process obligation. Whether a failing case blocks is SPEC Open question 9, and
    P2 does not answer it: this function signals nothing and exits nothing.
    """
    results = tuple(
        run_case(conn, case, adapters=adapters, version_tuple=version_tuple,
                 budget_ceilings=budget_ceilings, run_settings=run_settings)
        for case in load_all_cases()
    )
    return GateReport(
        results=results,
        pass_count=sum(1 for r in results if r.verdict == "pass"),
        fail_count=sum(1 for r in results if r.verdict == "fail"),
        not_run_count=sum(1 for r in results if r.verdict == "not_run"),
    )
