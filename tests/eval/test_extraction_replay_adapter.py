# tests/eval/test_extraction_replay_adapter.py
"""The one §8.5 stage a sealed bundle can measure on its own.

P2 walks ten attribution stages and, before this module, `src/` published one
`ReplayContext` adapter for any of them -- P8's, which needs live `Dossier`
objects, evidence resolvers and site dependencies that no bundle carries. So a
`replay` run over a real bundle recorded ten `not_implemented` rows and every
dimension scored `not_run`: the harness ran and measured nothing.

`extraction` is the exception and the only one. `bundle_extraction_run` holds
P4's whole row verbatim, and P5's `extraction_stage_output` maps exactly that row
to P2's envelope. Nothing else is needed -- no filesystem, no bytes, no live
part -- which is why these tests build the bundle in a database that has P2's
tables and NOTHING ELSE. `extraction_runs`, P4's own table, does not exist in it.
If the adapter ever reads the live table instead of the bundle, every test here
raises `sqlite3.OperationalError` rather than passing quietly.

What it measures and what it does not: this scores the extraction runs the
bundle RECORDED against the bundle's labels. Re-running a new extractor over the
snapshot is not possible and is not attempted -- §8.5's bundle carries content
hashes, not bytes, and `scan_agent.replay.replay` writes no `files` row for
exactly that reason.
"""
from __future__ import annotations

import json

import pytest

from eval_harness.assertions import assertions
from eval_harness.bundle import (
    add_expectation, add_extraction_run, open_bundle, seal_bundle,
)
from eval_harness.driver import evaluate_bundle
from eval_harness.stage_output import stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS

from evaluation import extraction_adapter

CONTENT_HASH = "sha256:" + "a" * 64
FILE_ID = "file-1"

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


def _p4_row(*, completeness: str, observation_count: int, coverage) -> dict:
    """P4's `extraction_runs` row as the LIVE path hands it to the bundle.

    `orchestrator._assemble_bundle` does `dict(conn.execute("SELECT * FROM
    extraction_runs ..."))`, and P4's `coverage` column is TEXT holding JSON --
    `extractors.runs.coverage` returns a mapping and the column stores its
    serialization. So the row that survives into `bundle_extraction_run` carries
    a coverage STRING, while `extraction_stage_output` does `dict(run["coverage"])`
    and needs a mapping. That impedance is the seam this adapter closes, and it
    is written into the fixture rather than smoothed over, because a fixture that
    handed the adapter a mapping would test a row no live run produces.
    """
    return {
        "run_id": f"run-{completeness}", "file_id": FILE_ID,
        "content_hash": CONTENT_HASH, "extractor_name": "pdf",
        "extractor_version": "pdf-1", "source_type": "document",
        "analysis_tier": "native", "config": "{}", "config_fingerprint": "cfg-1",
        "completeness": completeness,
        "coverage": None if coverage is None else json.dumps(coverage),
        "observation_count": observation_count,
        "started_at": "2026-09-02T00:00:00+00:00",
        "finished_at": "2026-09-02T00:00:01+00:00", "failure_reason": None,
    }


@pytest.fixture()
def bundled(eval_conn):
    """P2's tables and NOT P4's. `extraction_runs` does not exist here."""
    create_eval_schema(eval_conn)
    assert eval_conn.execute(
        "SELECT count(*) AS n FROM sqlite_master WHERE type = 'table' "
        "AND name = 'extraction_runs'").fetchone()["n"] == 0
    return eval_conn


def _bundle(conn, *, rows, expected_value, expected_outcome_kind="produced"):
    bundle_id = open_bundle(
        conn, corpus_form="snapshot", source_scan_ref="scan-1",
        pinned_plan_id=None, pinned_plan_version=None, policy_settings={})
    for row in rows:
        add_extraction_run(conn, bundle_id, row=row)
    add_expectation(
        conn, bundle_id, dimension="extraction", subject_ref=CONTENT_HASH,
        expected_value=expected_value,
        expected_outcome_kind=expected_outcome_kind, source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _drive(conn, bundle_id, adapters):
    return evaluate_bundle(
        conn, bundle_id, version_tuple=_tuple(), budget_ceilings={},
        run_settings=SETTINGS, adapters=adapters)


COVERAGE = {"units": "pages", "processed": 3, "total": 3}
MEASURED = {"observation_count": 7, "coverage": COVERAGE}


def test_a_recorded_extraction_run_becomes_a_scored_verdict(bundled):
    """The join this module exists to make: a sealed bundle, no live filesystem,
    and a verdict on §8.5's extraction question."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=7,
                      coverage=COVERAGE)],
        expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    assert driven.verdicts == {"match": 1}
    assert driven.attribution == {}
    assert driven.assertions_written == 1
    assert driven.attributed == 0


def test_without_the_adapter_the_extraction_dimension_scores_not_run(bundled):
    """The negative twin. This is the state every real bundle in this repository
    was in: ten `not_implemented` stages and a dimension P2 could not read."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=7,
                      coverage=COVERAGE)],
        expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {})

    assert driven.verdicts == {"not_run": 1}
    outcomes = [row["outcome"] for row in stage_outputs(bundled, driven.run_id)]
    assert outcomes == ["not_implemented"] * len(STAGE_IDS)


def test_a_wrong_recorded_extraction_is_attributed_to_extraction(bundled):
    """§8.5's "where the error BEGAN", over the first of its ten stages."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=7,
                      coverage=COVERAGE)],
        expected_value={"observation_count": 9, "coverage": COVERAGE})

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    assert driven.verdicts == {"divergent": 1}
    assert driven.attribution == {"extraction": 1}


def test_a_recorded_deferral_is_a_deferral_and_never_a_divergence(bundled):
    """§8.6: a budget event is reported as one and never as a regression. P4's
    `deferred` must arrive as P2's `deferred` with `ceiling_reached`, which is the
    one pairing `record_stage_output` refuses to let a stage get wrong."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="deferred", observation_count=0,
                      coverage={"units": "pages", "processed": 0, "total": 9})],
        expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    assert driven.verdicts == {"deferred": 1}
    assert driven.attribution == {}
    row = stage_outputs(bundled, driven.run_id, stage_id="extraction")[0]
    assert (row["outcome"], row["budget_state"]) == ("deferred", "ceiling_reached")


def test_an_unsupported_file_abstains_and_the_abstention_is_scored(bundled):
    """§8.5 measures abstention as an outcome, not as an absence. P4's
    `unsupported` -- no extractor exists -- is P2's `abstained`, and a bundle
    labelled `abstained` scores it a PASS rather than a miss."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="unsupported", observation_count=0,
                      coverage={"units": "files", "processed": 0, "total": 1})],
        expected_value=None, expected_outcome_kind="abstained")

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    assert driven.verdicts == {"abstained_correctly": 1}
    assert driven.attribution == {}


def test_a_null_coverage_errors_rather_than_being_given_a_number(bundled):
    """P4's `coverage` column is nullable and `extraction_stage_output` does
    `dict(run["coverage"])`, so a recorded run with no coverage raises inside P5's
    mapping and P2 records the stage as `error`.

    Pinned rather than papered over. Every live writer supplies a coverage
    mapping today -- `extractors.failure` fills one even for a run that failed --
    so this is a shape the schema permits and the pipeline does not currently
    produce. The fix belongs to P5, whose mapping it is; the alternative here
    would be for this module to substitute a coverage of its own, and "processed
    0 of 0" is a measurement nobody took. An `error` says the stage could not
    measure, which is true."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=0,
                      coverage=None)],
        expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    rows = stage_outputs(bundled, driven.run_id, stage_id="extraction")
    assert [row["outcome"] for row in rows] == ["error"]
    assert "TypeError" in rows[0]["payload"]
    assert driven.verdicts == {"not_run": 1}


def _ocr_row(*, observation_count: int):
    row = _p4_row(completeness="complete", observation_count=observation_count,
                  coverage=COVERAGE)
    row["run_id"], row["extractor_version"] = "run-ocr", "ocr-1"
    row["analysis_tier"], row["extractor_name"] = "ocr", "ocr"
    return row


def test_agreeing_runs_are_two_rows_and_one_measurement(bundled):
    """Two extractor versions over one file version is two runs and two envelope
    rows: §8.5's version tuple exists so two versions can be diffed, and
    collapsing them would delete the thing being compared.

    The MEASUREMENT is keyed the other way -- P5 puts it on the content hash and
    `stage_dimension_value` admits one per subject per run -- so where the two
    runs agree, the value they agree on is written once. Nothing is chosen: there
    is nothing to choose between identical measurements."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=7,
                      coverage=COVERAGE), _ocr_row(observation_count=7)],
        expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    rows = stage_outputs(bundled, driven.run_id, stage_id="extraction")
    assert len(rows) == 2
    assert sorted(json.loads(row["payload"])["extractor_version"]
                  for row in rows) == ["ocr-1", "pdf-1"]
    # One expectation, one subject, one assertion -- the second row does not mint
    # a second verdict on a label that names one subject (§8.7).
    assert driven.assertions_written == 1
    assert driven.verdicts == {"match": 1}


def test_disagreeing_runs_over_one_file_version_refuse_and_the_stage_errors(bundled):
    """The undecided case, reported as undecided.

    A native pass and a targeted OCR pass over one PDF are two recorded runs on
    one content hash with two different measurements, and P5 keys the extraction
    measurement on the content hash while P2 admits one per subject per run.
    Nothing in §8.5 says which extractor version is authoritative -- its version
    tuple carries "one version per extractor" precisely so both can be in scope --
    so the adapter refuses, `replay_bundle` records the stage as `error` with the
    traceback, and the run reports a stage that failed rather than a measurement
    nobody chose. `error` is P2's own word for this and is distinct from an
    abstention and from a deferral."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=7,
                      coverage=COVERAGE), _ocr_row(observation_count=4)],
        expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    rows = stage_outputs(bundled, driven.run_id, stage_id="extraction")
    assert [row["outcome"] for row in rows] == ["error"]
    assert "AmbiguousExtractionMeasurement" in rows[0]["payload"]
    # The failure is never scored as a quality verdict on the file.
    assert driven.verdicts == {"not_run": 1}
    assert driven.attribution == {}


def test_the_refusal_is_reachable_on_its_own_terms(bundled):
    """The same refusal, raised rather than swallowed, so the message is pinned
    where a reader of the traceback will meet it."""
    from eval_harness.replay import ReplayContext

    from evaluation import AmbiguousExtractionMeasurement

    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=7,
                      coverage=COVERAGE), _ocr_row(observation_count=4)],
        expected_value=MEASURED)
    ctx = ReplayContext(conn=bundled, run_id="run-x", bundle_id=bundle_id,
                        stage_id="extraction", run_settings={}, budget_ceilings={})

    with pytest.raises(AmbiguousExtractionMeasurement) as raised:
        extraction_adapter(ctx)

    # The whole message. It is what a person reads on the `--replay` screen when
    # the stage fails, so its wording is the report and not an internal detail.
    assert str(raised.value) == (
        f"2 recorded extraction runs measure file version {CONTENT_HASH} "
        "and 2 of them disagree. §8.5 names no rule for which analysis tier is "
        "authoritative over one file version, and `stage_dimension_value` admits "
        "one measurement per subject per run. An owner decision, not P2's and "
        "not P5's.")


def test_the_adapter_measures_the_extraction_dimension_and_no_other(bundled):
    """A stage emits values for the dimension it owns. An adapter that filled
    nine more would be P2 scoring parts that never ran."""
    bundle_id = _bundle(
        bundled,
        rows=[_p4_row(completeness="complete", observation_count=7,
                      coverage=COVERAGE)],
        expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    measured = {row["dimension"] for row in bundled.execute(
        "SELECT dimension FROM stage_dimension_value WHERE run_id = ?",
        (driven.run_id,))}
    assert measured == {"extraction"}
    assert measured < set(DIMENSIONS)


def test_an_empty_bundle_reports_the_stage_ran_and_produced_nothing(bundled):
    """A bundle with no recorded run is not a stage that never ran. P2's runner
    writes its own `abstained` row keyed on the BUNDLE, which is how a reader
    tells the runner's bookkeeping from a stage's judgement about a subject."""
    bundle_id = _bundle(bundled, rows=[], expected_value=MEASURED)

    driven = _drive(bundled, bundle_id, {"extraction": extraction_adapter})

    row = stage_outputs(bundled, driven.run_id, stage_id="extraction")[0]
    assert (row["outcome"], row["subject_ref"]) == ("abstained", bundle_id)
    # The label still scores `not_run`: nothing measured this subject.
    assert driven.verdicts == {"not_run": 1}
    assert [r["verdict"] for r in assertions(bundled, driven.run_id)] == ["not_run"]
