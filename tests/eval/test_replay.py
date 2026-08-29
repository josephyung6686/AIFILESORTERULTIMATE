# tests/eval/test_replay.py
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.run import get_run, run_settings
from eval_harness.stage_output import DimensionValue, dimension_values, stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import STAGE_IDS


def _tuple():
    return dict(extractor_versions={"pdf.native": "1.0.0"},
                graph_algorithm_version=None, prompt_fingerprint=None,
                model_identifier=None, template_library_version=None,
                placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem", "native"])


def _bundle(conn):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(conn, bundle_id, dimension="extraction",
                    subject_ref="20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a", expected_value={"text": "COMS 4995"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _extraction_adapter(ctx: ReplayContext) -> list[StageResult]:
    """Stands in for P5, which does not exist. It reads the bundle, not the disk."""
    return [StageResult(
        subject_ref="20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a", outcome="produced",
        payload='{"p5": "opaque"}', inputs=[], budget_state="within_ceiling",
        values=[DimensionValue("extraction", "20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a", "produced",
                               {"text": "COMS 4995"})],
    )]


def _settings(**overrides):
    s = {"model_enabled": False, "embeddings_enabled": False}
    s.update(overrides)
    return s


def test_a_run_with_no_adapters_completes_with_ten_not_implemented_stages(eval_conn):
    # Done-means 7 / 02-segmentation-map.md, Order.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={})
    rows = stage_outputs(eval_conn, run_id)
    assert [r["stage_id"] for r in rows] == list(STAGE_IDS)
    assert {r["outcome"] for r in rows} == {"not_implemented"}
    assert get_run(eval_conn, run_id)["finished_at"]


def test_one_adapter_runs_and_the_other_nine_report_not_implemented(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"extraction": _extraction_adapter})
    by_stage = {r["stage_id"]: r["outcome"] for r in stage_outputs(eval_conn, run_id)}
    assert by_stage["extraction"] == "produced"
    assert sum(1 for v in by_stage.values() if v == "not_implemented") == 9
    value = dimension_values(eval_conn, run_id, dimension="extraction")[0]
    assert value["value"] == '{"text":"COMS 4995"}'


def test_stages_run_in_8_5s_order(eval_conn):
    # The order is §8.5's list, which is also §4.10's and §6.12's pipeline order,
    # and Task 11 depends on it for tie-breaking.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    seen = []

    def spy(stage_id):
        def adapter(ctx: ReplayContext) -> list[StageResult]:
            seen.append(ctx.stage_id)
            return []
        return adapter

    replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(), budget_ceilings={},
                  run_settings=_settings(),
                  adapters={s: spy(s) for s in STAGE_IDS})
    assert seen == list(STAGE_IDS)


def test_the_adapter_receives_the_run_settings_and_the_ceilings(eval_conn):
    # A bundle must be re-runnable with the model disabled and with embeddings
    # disabled, independently (Contract out §5).
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    captured = {}

    def adapter(ctx: ReplayContext) -> list[StageResult]:
        captured["settings"] = dict(ctx.run_settings)
        captured["ceilings"] = dict(ctx.budget_ceilings)
        captured["bundle_id"] = ctx.bundle_id
        return []

    replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                  budget_ceilings={"ocr.max_pages_per_file": 3},
                  run_settings=_settings(embeddings_enabled=True),
                  adapters={"retrieval": adapter})
    assert captured["settings"] == {"model_enabled": False, "embeddings_enabled": True}
    assert captured["ceilings"] == {"ocr.max_pages_per_file": 3}
    assert captured["bundle_id"] == bundle_id


def test_an_adapter_that_defers_is_recorded_as_deferred(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)

    def deferring(ctx: ReplayContext) -> list[StageResult]:
        return [StageResult(subject_ref="20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a", outcome="deferred",
                            payload=None, inputs=[],
                            budget_state="ceiling_reached",
                            values=[DimensionValue("extraction", "20047214e6930e1557c8bbd7f229baaf1e671e86f2640ac0520e4e7dfbe7d00a",
                                                   "deferred", None)])]

    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"extraction": deferring})
    row = [r for r in stage_outputs(eval_conn, run_id)
           if r["stage_id"] == "extraction"][0]
    assert row["outcome"] == "deferred"
    assert row["budget_state"] == "ceiling_reached"


def test_an_adapter_that_raises_is_recorded_as_error_not_swallowed(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)

    def broken(ctx: ReplayContext) -> list[StageResult]:
        raise RuntimeError("the stage crashed")

    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"grouping": broken})
    row = [r for r in stage_outputs(eval_conn, run_id)
           if r["stage_id"] == "grouping"][0]
    assert row["outcome"] == "error"
    assert "the stage crashed" in row["payload"]


def test_an_adapter_that_returns_nothing_is_the_runners_own_row(eval_conn):
    # The `abstained` written here is P2's bookkeeping, not §6.10's abstention,
    # and `subject_ref` is the only thing that says so. Contract out §4's domain
    # for subject_ref is content hash | group id | node id | branch id |
    # model-call id | plan-version id; a bundle id is none of the six, so a row
    # keyed on the bundle is never a stage's decision about a subject. A consumer
    # counting a stage's abstentions filters exactly this. Without this test the
    # convention is a comment, and a comment is not a mechanism.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)

    def decides_about_nothing(ctx: ReplayContext) -> list[StageResult]:
        return []

    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"extraction": decides_about_nothing})
    rows = stage_outputs(eval_conn, run_id, stage_id="extraction")
    assert len(rows) == 1
    assert rows[0]["outcome"] == "abstained"
    assert rows[0]["subject_ref"] == bundle_id
    # It carries no dimension value, so it can reach no verdict in Task 10.
    assert dimension_values(eval_conn, run_id) == []
    # All ten stages still appear, and every runner row uses the same key, so one
    # filter separates bookkeeping from stage decisions for all three cases.
    every = stage_outputs(eval_conn, run_id)
    assert [r["stage_id"] for r in every] == list(STAGE_IDS)
    assert {r["subject_ref"] for r in every} == {bundle_id}


def test_there_is_no_global_stage_registry(eval_conn):
    # P1's lesson: a process-local mutable registry makes a run's stage set
    # invisible and mutable from anywhere. Adapters are an argument.
    import inspect

    from eval_harness import replay
    assert not [n for n, v in vars(replay).items()
                if callable(v) and n.lower().startswith("register")]
    assert "adapters" in inspect.signature(replay.replay_bundle).parameters


def test_the_run_records_its_settings_verbatim(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    run_id = replay_bundle(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={})
    assert run_settings(eval_conn, run_id) == {"model_enabled": False,
                                               "embeddings_enabled": False}
