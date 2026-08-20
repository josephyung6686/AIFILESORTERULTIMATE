# tests/eval/test_shadow.py
import pytest
from database_agent.db import create_schema

from eval_harness.assertions import assert_run
from eval_harness.attribution import attribute_run
from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.shadow import (
    ShadowWroteLiveState, UnauditedModelCall, adjudications,
    assert_shadow_wrote_nothing, record_adjudication, run_shadow, shadow_record,
)
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema


def _tuple(**overrides):
    fields = dict(extractor_versions={}, graph_algorithm_version=None,
                  prompt_fingerprint=None, model_identifier=None,
                  template_library_version=None, placement_scorer_version=None,
                  analysis_tiers_enabled=["filesystem"])
    fields.update(overrides)
    return fields


def _settings(**overrides):
    s = {"model_enabled": False, "embeddings_enabled": False}
    s.update(overrides)
    return s


def _bundle(conn):
    bundle_id = open_bundle(conn, corpus_form="snapshot",
                            source_scan_ref="scan-fixture",
                            pinned_plan_id="plan-fixture", pinned_plan_version="1",
                            policy_settings={})
    add_expectation(conn, bundle_id, dimension="placement", subject_ref="file-1",
                    expected_value={"node_id": "n-right"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(conn, bundle_id)
    return bundle_id


def _places(node_id):
    def adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="file-1", outcome="produced", payload=None,
                            inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("placement", "file-1", "produced",
                                                   {"node_id": node_id})])]
    return adapter


def _live(conn, bundle_id):
    run_id = replay_bundle(conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-wrong")})
    assert_run(conn, run_id)
    attribute_run(conn, run_id)
    return run_id


def _select_all(disagreements):
    """A fixture selector. SPEC Open question 12 is open: P2 ships none."""
    return list(disagreements)


def test_a_shadow_run_produces_a_disagreement_set_and_a_surfaced_set(eval_conn):
    # Done-means 9.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(
        placement_scorer_version="scorer-2"), budget_ceilings={},
        run_settings=_settings(),
        adapters={"placement_scoring": _places("n-right")},
        live_run_id=live, select=_select_all)
    record = shadow_record(eval_conn, shadow_id)
    assert record["disagreement_set"]
    assert record["disagreement_set"][0]["subject_ref"] == "file-1"
    assert record["surfaced_examples"] == record["disagreement_set"]
    assert record["shadow_namespace"] == shadow_id


def test_the_three_empties_are_provable(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-right")},
                           live_run_id=live, select=_select_all)
    record = shadow_record(eval_conn, shadow_id)
    assert record["plan_version_writes"] == []
    assert record["move_plan_entries"] == []
    assert record["user_visible_tree_delta"] == []
    assert_shadow_wrote_nothing(eval_conn, shadow_id)     # does not raise


def test_a_shadow_run_that_wrote_live_state_is_caught(eval_conn):
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-right")},
                           live_run_id=live, select=_select_all)
    eval_conn.execute(
        "UPDATE shadow_run SET move_plan_entries = '[\"move-1\"]' "
        "WHERE shadow_run_id = ?", (shadow_id,))
    with pytest.raises(ShadowWroteLiveState):
        assert_shadow_wrote_nothing(eval_conn, shadow_id)


def test_a_shadow_run_that_wrote_a_foreign_table_is_caught_without_confessing(eval_conn):
    # The test above only reaches the FIRST check: `move_plan_entries` is one of
    # the three self-reported columns, and an adapter that lies about them never
    # sets one. This is the check that does not depend on the adapter's honesty,
    # and without this test its raising branch is never executed by anything.
    #
    # The write goes to a table P2 does not own and did not create, standing in
    # for P10's plan version table and P12's move plan. Using a table invented
    # here rather than one of P1's is the point: `foreign_table_counts` subtracts
    # `EVAL_TABLES` from `sqlite_master`, so it covers tables that do not exist
    # yet, and this stays green the day P10 and P12 land WITHOUT shadow.py being
    # edited. That is the property the docstring claims; this is what checks it.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    eval_conn.execute("CREATE TABLE a_table_p2_does_not_own (id TEXT PRIMARY KEY)")
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)

    def writes_behind_p2s_back(ctx: ReplayContext):
        ctx.conn.execute(
            "INSERT INTO a_table_p2_does_not_own (id) VALUES ('smuggled')")
        return _places("n-right")(ctx)

    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": writes_behind_p2s_back},
                           live_run_id=live, select=_select_all)
    # The adapter confessed to nothing: all three self-reported columns are empty,
    # so the first check passes and only the snapshot comparison can catch this.
    record = shadow_record(eval_conn, shadow_id)
    assert record["plan_version_writes"] == []
    assert record["move_plan_entries"] == []
    assert record["user_visible_tree_delta"] == []
    with pytest.raises(ShadowWroteLiveState) as caught:
        assert_shadow_wrote_nothing(eval_conn, shadow_id)
    assert "a_table_p2_does_not_own" in str(caught.value)


def test_a_model_enabled_shadow_run_needs_its_audit_refs(eval_conn):
    # §8.4: every model call is recorded in the consent-aware audit record. P2
    # requires the reference; P7 writes the record.
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    with pytest.raises(UnauditedModelCall):
        run_shadow(eval_conn, bundle_id, version_tuple=_tuple(model_identifier="m1"),
                   budget_ceilings={}, run_settings=_settings(model_enabled=True),
                   adapters={}, live_run_id=live, select=_select_all)
    shadow_id = run_shadow(
        eval_conn, bundle_id, version_tuple=_tuple(model_identifier="m1"),
        budget_ceilings={}, run_settings=_settings(model_enabled=True), adapters={},
        live_run_id=live, select=_select_all, model_call_audit_refs=["audit-1"])
    assert shadow_record(eval_conn, shadow_id)["model_call_audit_refs"] == ["audit-1"]


def test_the_selector_is_required_and_p2_ships_none(eval_conn):
    # SPEC Open question 12: "By what criterion are shadow examples selected?"
    # A default here would be an answer.
    import inspect

    from eval_harness import shadow
    parameter = inspect.signature(shadow.run_shadow).parameters["select"]
    assert parameter.default is inspect.Parameter.empty
    for name, fn in inspect.getmembers(shadow, inspect.isfunction):
        assert "select" not in name or name == "run_shadow", name


def test_an_adjudication_is_run_scoped_and_appends_no_event(eval_conn):
    # SPEC Open question 10 is OPEN. Promoting an adjudication into an §8.7
    # correction would give shadow mode a path into user-visible state.
    create_schema(eval_conn)
    create_eval_schema(eval_conn)
    bundle_id = _bundle(eval_conn)
    live = _live(eval_conn, bundle_id)
    shadow_id = run_shadow(eval_conn, bundle_id, version_tuple=_tuple(),
                           budget_ceilings={}, run_settings=_settings(),
                           adapters={"placement_scoring": _places("n-right")},
                           live_run_id=live, select=_select_all)
    before = eval_conn.execute("SELECT count(*) AS n FROM events").fetchone()["n"]
    record_adjudication(eval_conn, shadow_id, subject_ref="file-1",
                        dimension="placement", reviewer_verdict="candidate_better",
                        note="fixture")
    after = eval_conn.execute("SELECT count(*) AS n FROM events").fetchone()["n"]
    assert after == before
    row = adjudications(eval_conn, shadow_id)[0]
    assert row["shadow_run_id"] == shadow_id      # run scope, not file scope
    assert row["reviewer_verdict"] == "candidate_better"


def test_there_is_no_promotion_path_to_a_correction(eval_conn):
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "append_event" not in text, path.name
        assert "correction_scope" not in text, path.name


def test_shadow_adds_no_ceiling_key_of_its_own():
    # SPEC Open question 8 is OPEN: §8.6's list has no shadow entry.
    from database_agent.budget import CEILING_KEYS
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness" / "shadow.py"
    text = src.read_text(encoding="utf-8")
    assert "shadow.max" not in text
    assert len(CEILING_KEYS) == 15
