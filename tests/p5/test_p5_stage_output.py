# tests/p5/test_p5_stage_output.py
"""§8.5 / B7 — P5's envelope, through P2's live writer."""
import json

import pytest

import extractors.stage_output as stage_output_module
from eval_harness.replay import StageResult
from eval_harness.run import VERSION_AXES, record_version_tuple, start_run
from eval_harness.stage_output import record_stage_output, stage_outputs
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import BUDGET_STATES, OUTCOMES, STAGE_IDS

from extractors.stage_output import (
    CEILING_REACHED_COMPLETENESS, ENVELOPE_FIELDS, OUTCOME_BY_COMPLETENESS, STAGE_ID,
    extraction_stage_output, extractor_versions,
)

from conftest import FIXED_CLOCK

P4_COMPLETENESS = ("complete", "capped", "partial", "metadata_only", "deferred",
                   "unsupported", "unreadable", "failed", "dataless")


def a_run(completeness="complete", extractor_name="pdf.text", version="0.1.0"):
    return {"file_id": "f-1", "content_hash": "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
            "extractor_name": extractor_name, "extractor_version": version,
            "source_type": "text_document", "analysis_tier": "native",
            "completeness": completeness, "observation_count": 3,
            "coverage": {"units": "pages", "processed": 18, "total": 18}}


@pytest.fixture()
def p2_run(conn):
    create_eval_schema(conn)
    ref = record_version_tuple(
        conn, extractor_versions={"pdf.text": "0.1.0"}, graph_algorithm_version=None,
        prompt_fingerprint=None, model_identifier=None,
        template_library_version=None, placement_scorer_version=None,
        analysis_tiers_enabled=["filesystem", "native"])
    run_id = start_run(conn, bundle_id="b-p5", run_kind="replay",
                       version_tuple_ref=ref, budget_ceilings={},
                       run_settings={"model_enabled": False,
                                     "embeddings_enabled": False},
                       pinned_plan_id=None, pinned_plan_version=None)
    return run_id, ref


def test_the_stage_id_is_one_of_section_8_5s_ten():
    assert STAGE_ID == "extraction"
    assert STAGE_ID in STAGE_IDS


def test_the_envelope_is_exactly_p2s_stage_result_shape():
    envelope = extraction_stage_output(run=a_run())
    assert set(ENVELOPE_FIELDS) == set(envelope) - {"stage_id"}
    StageResult(**{k: v for k, v in envelope.items() if k != "stage_id"})


def test_every_completeness_maps_to_one_of_p2s_five_outcomes():
    assert set(OUTCOME_BY_COMPLETENESS) == set(P4_COMPLETENESS)
    assert set(OUTCOME_BY_COMPLETENESS.values()) <= set(OUTCOMES)


def test_abstention_and_budget_deferral_are_different_values():
    # B7: "an explicit abstention value, a distinct budget-deferral value".
    assert OUTCOME_BY_COMPLETENESS["unsupported"] == "abstained"
    assert OUTCOME_BY_COMPLETENESS["deferred"] == "deferred"
    assert OUTCOME_BY_COMPLETENESS["unsupported"] != OUTCOME_BY_COMPLETENESS["deferred"]


def test_inputs_is_the_content_hash_so_a_rename_is_free():
    envelope = extraction_stage_output(run=a_run())
    assert envelope["inputs"] == ("67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",)
    assert envelope["subject_ref"] == "f-1"


def test_the_payload_is_p5s_own_and_p2_never_parses_it():
    envelope = extraction_stage_output(run=a_run())
    payload = json.loads(envelope["payload"])
    assert payload["extractor_name"] == "pdf.text"
    assert payload["completeness"] == "complete"
    assert payload["coverage"] == {"units": "pages", "processed": 18, "total": 18}


def test_a_capped_run_produced_under_a_reached_ceiling(conn, p2_run):
    # §2.7: a capped run keeps the text it recognized. It produced.
    run_id, ref = p2_run
    envelope = extraction_stage_output(run=a_run(completeness="capped"))
    assert envelope["outcome"] == "produced"
    assert envelope["budget_state"] == "ceiling_reached"
    record_stage_output(conn, run_id=run_id, version_tuple_ref=ref,
                        **{k: v for k, v in envelope.items()
                           if k != "stage_id"}, stage_id=STAGE_ID)
    assert stage_outputs(conn, run_id)[0]["budget_state"] == "ceiling_reached"


def test_a_deferred_run_is_the_pairing_p2s_writer_requires(conn, p2_run):
    run_id, ref = p2_run
    envelope = extraction_stage_output(run=a_run(completeness="deferred"))
    assert (envelope["outcome"], envelope["budget_state"]) == ("deferred",
                                                               "ceiling_reached")
    record_stage_output(conn, run_id=run_id, version_tuple_ref=ref,
                        **{k: v for k, v in envelope.items()
                           if k != "stage_id"}, stage_id=STAGE_ID)
    assert stage_outputs(conn, run_id)[0]["outcome"] == "deferred"


def test_p5_never_produces_the_pairing_p2_refuses():
    # §8.6: a ceiling-reached stage is `deferred`, never `abstained`.
    assert set(CEILING_REACHED_COMPLETENESS) == {"deferred", "capped"}
    for completeness in CEILING_REACHED_COMPLETENESS:
        envelope = extraction_stage_output(run=a_run(completeness=completeness))
        assert envelope["outcome"] != "abstained"


def test_every_envelope_is_accepted_by_p2s_writer(conn, p2_run):
    run_id, ref = p2_run
    for completeness in P4_COMPLETENESS:
        envelope = extraction_stage_output(run=a_run(completeness=completeness))
        assert envelope["budget_state"] in BUDGET_STATES
        record_stage_output(conn, run_id=run_id, version_tuple_ref=ref,
                            **{k: v for k, v in envelope.items()
                               if k != "stage_id"}, stage_id=STAGE_ID)
    assert len(stage_outputs(conn, run_id)) == len(P4_COMPLETENESS)


def test_p5_supplies_one_axis_of_the_version_tuple(conn, p2_run):
    assert VERSION_AXES[0] == "extractor_versions"
    versions = extractor_versions([a_run(), a_run(extractor_name="ocr.apple-vision",
                                                  version="19.1")])
    assert versions == {"pdf.text": "0.1.0", "ocr.apple-vision": "19.1"}


def test_two_versions_of_one_extractor_are_refused():
    # §3.4's cache key is per (extractor, version); one map cannot hold two.
    with pytest.raises(ValueError):
        extractor_versions([a_run(version="0.1.0"), a_run(version="0.2.0")])


def test_p5_imports_no_part_of_p2():
    # P5 produces the envelope; P2 stores it. P5's only run-time dependency is P1.
    imported = {name for name, value in vars(stage_output_module).items()
                if getattr(value, "__module__", "").startswith("eval_harness")}
    assert imported == set()
    assert "eval_harness" not in [getattr(v, "__name__", "")
                                  for v in vars(stage_output_module).values()]
