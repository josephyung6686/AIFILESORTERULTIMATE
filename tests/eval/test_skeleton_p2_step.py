# tests/eval/test_skeleton_p2_step.py
"""The walking skeleton's P2 step (02-segmentation-map.md):
"the whole run replays from a bundle and asserts each stage's output."

Deterministic: no model, no cloud, no embeddings. Nine of the ten stages are
absent, which is a valid run with nine not_run verdicts.
"""
from pathlib import Path

from p1_contract import p3_basic_record   # the R2 fields P3 computes once (O5)
from database_agent.budget import all_ceilings
from database_agent.db import create_schema
from database_agent.files_table import get_file, observe_path

from eval_harness.assertions import assert_run, assertions, verdict_counts
from eval_harness.attribution import attribute_run
from eval_harness.bundle import (
    add_expectation, add_extraction_run, add_file_entry, add_text_unit, open_bundle,
    seal_bundle,
)
from eval_harness.counts import bundle_counts
from eval_harness.replay import ReplayContext, StageResult, replay_bundle
from eval_harness.stage_output import DimensionValue, stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import DIMENSIONS, STAGE_IDS


def test_skeleton_p2_step(eval_conn, tmp_path: Path):
    create_schema(eval_conn)
    create_eval_schema(eval_conn)

    # ---- P1's step: one PDF whose title carries a course code. P3's fixture
    # authors the scan events; P1 writes (M8).
    document = tmp_path / "corpus" / "syllabus-fixture.pdf"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_bytes(b"%PDF-1.4 COMS 4995 syllabus fixture bytes")
    file_id = observe_path(
        eval_conn, document, author="P3", component_version="p3-fixture",
        # R2 is P3's to compute once (O5); P1 stores it and derives none of it, so
        # the fixture standing in for P3 supplies it. P1's signature requires these
        # with no default — a default would let P1 re-derive them silently.
        **p3_basic_record(document),
        parent_folder_context="corpus", mime_type="application/pdf",
        detected_format="pdf", scan_state="scanned", materialized=True,
    )
    content_hash = get_file(eval_conn, file_id)["content_hash"]

    # ---- P2's step, part one: capture the bundle.
    bundle_id = open_bundle(
        eval_conn, corpus_form="snapshot", source_scan_ref="skeleton-scan",
        pinned_plan_id="skeleton-plan", pinned_plan_version="1",
        policy_settings={"privacy_mode": "offline",
                         "placement_policy": "skeleton-policy",
                         "budget_ceilings": all_ceilings(eval_conn)},
    )
    add_file_entry(eval_conn, bundle_id, file_id=file_id, content_hash=content_hash,
                   hash_algorithm="sha256", handling_class=None,
                   payload_ref="blobs/skeleton")
    add_extraction_run(eval_conn, bundle_id, row={
        "run_id": "skeleton-run", "file_id": file_id, "content_hash": content_hash,
        "extractor_name": "pdf.native", "extractor_version": "1.0.0",
        "source_type": "text", "config_fingerprint": "sha256:cfg",
        "completeness": "complete",
        "coverage": {"units": "pages", "processed": 1, "total": 1},
        "observation_count": 1})
    add_text_unit(eval_conn, bundle_id, row={
        "run_id": "skeleton-run", "container_path": [], "unit_locator": "",
        "text": "COMS 4995 syllabus", "length": 18, "truncated": False})
    add_expectation(eval_conn, bundle_id, dimension="extraction",
                    subject_ref=content_hash,
                    expected_value={"text": "COMS 4995 syllabus"},
                    expected_outcome_kind="produced", source="hand-labelled")
    add_expectation(eval_conn, bundle_id, dimension="placement",
                    subject_ref=file_id, expected_value={"node_id": "n-academics"},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(eval_conn, bundle_id)

    # §8.5: "without touching a live filesystem". The source is gone from here on.
    document.unlink()
    assert not document.exists()

    # ---- P2's step, part two: replay. One minimal stage, nine absent.
    def extraction_from_the_bundle(ctx: ReplayContext):
        from eval_harness.bundle import text_units
        unit = text_units(ctx.conn, ctx.bundle_id, run_id="skeleton-run")[0]
        return [StageResult(
            subject_ref=content_hash, outcome="produced",
            payload='{"stands in for P4/P5": true}', inputs=[],
            budget_state="within_ceiling",
            values=[DimensionValue("extraction", content_hash, "produced",
                                   {"text": unit["text"]})])]

    run_id = replay_bundle(
        eval_conn, bundle_id,
        version_tuple=dict(extractor_versions={"pdf.native": "1.0.0"},
                           graph_algorithm_version=None, prompt_fingerprint=None,
                           model_identifier=None, template_library_version=None,
                           placement_scorer_version=None,
                           analysis_tiers_enabled=["filesystem", "native"]),
        budget_ceilings=all_ceilings(eval_conn),
        run_settings={"model_enabled": False, "embeddings_enabled": False},
        adapters={"extraction": extraction_from_the_bundle},
    )

    # ---- assert each stage's output.
    outputs = {r["stage_id"]: r for r in stage_outputs(eval_conn, run_id)}
    assert set(outputs) == set(STAGE_IDS)
    assert outputs["extraction"]["outcome"] == "produced"
    assert sum(1 for r in outputs.values() if r["outcome"] == "not_implemented") == 9

    assert assert_run(eval_conn, run_id) == 2
    attribute_run(eval_conn, run_id)
    by_dimension = {r["dimension"]: r for r in assertions(eval_conn, run_id)}
    assert by_dimension["extraction"]["verdict"] == "match"
    assert by_dimension["extraction"]["attributed_stage"] is None
    # The absent stage yields not_run, not a failure (Done-means 7).
    assert by_dimension["placement"]["verdict"] == "not_run"
    assert by_dimension["placement"]["attributed_stage"] is None

    counts = verdict_counts(eval_conn, run_id)
    assert counts == {"match": 1, "not_run": 1}
    assert "divergent" not in counts

    # §8.6's count line, from the bundle, with the corpus deleted (Done-means 13).
    assert bundle_counts(eval_conn, bundle_id) == {
        "files_indexed": 1, "files_with_any_run": 1, "files_fully_extracted": 1,
        "runs_deferred": 0, "runs_unreadable": 0, "runs_dataless": 0,
        "files_requiring_model_review": None,
    }

    # Every dimension is representable even when only two were asserted.
    assert len(DIMENSIONS) == 10
