# tests/p5/test_p5_stage_output.py
"""§8.5 / B7 — P5's envelope, through P2's live writer."""
import json

import pytest

import extractors.stage_output as stage_output_module
from eval_harness.replay import StageResult
from eval_harness.run import VERSION_AXES, record_version_tuple, start_run
from eval_harness.stage_output import (
    dimension_values, record_stage_output, stage_outputs,
)
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import (
    BUDGET_STATES, DIMENSIONS, OUTCOMES, STAGE_IDS,
)

from extractors.stage_output import (
    CEILING_REACHED_COMPLETENESS, DIMENSION, ENVELOPE_FIELDS,
    OUTCOME_BY_COMPLETENESS, STAGE_ID, extraction_stage_output,
    extraction_subject_ref, extractor_versions,
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
    _record(conn, run_id, ref, envelope)
    assert stage_outputs(conn, run_id)[0]["budget_state"] == "ceiling_reached"


def test_a_deferred_run_is_the_pairing_p2s_writer_requires(conn, p2_run):
    run_id, ref = p2_run
    envelope = extraction_stage_output(run=a_run(completeness="deferred"))
    assert (envelope["outcome"], envelope["budget_state"]) == ("deferred",
                                                               "ceiling_reached")
    _record(conn, run_id, ref, envelope)
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
        # One content hash each: `stage_dimension_value` is keyed
        # (run_id, dimension, subject_ref), so nine measurements of one file
        # version in one run would collide.
        #
        # This comment used to end "a collision no real replay produces". That was
        # wrong, and measuring a live corpus is what showed it: every file version
        # there carried two passes at one hash and the second insert raised. The
        # subject now carries the extractor as well, so the real case no longer
        # collides -- nine COMPLETENESS values at one extractor still would, which
        # is why the hashes here stay distinct.
        envelope = extraction_stage_output(run={**a_run(completeness=completeness),
                                                "content_hash": completeness})
        assert envelope["budget_state"] in BUDGET_STATES
        _record(conn, run_id, ref, envelope)
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


# --- section 8.5's `extraction` dimension, which had no producer -------------------

def _record(conn, run_id, ref, envelope):
    """The envelope through P2's writer, the way a replay adapter hands it over."""
    fields = {k: v for k, v in envelope.items() if k not in ("stage_id", "values")}
    return record_stage_output(conn, run_id=run_id, version_tuple_ref=ref,
                               stage_id=STAGE_ID, dimension_values=envelope["values"],
                               **fields)


def test_the_dimension_is_one_of_section_8_5s_ten_and_is_not_the_stage_id():
    """Two ten-item lists that are not one list. They happen to share the spelling
    `extraction`, and P2 still checks each under its own checker."""
    assert DIMENSION == "extraction"
    assert DIMENSION in DIMENSIONS


def test_the_envelope_carries_the_dimension_value_p2_asserts_on():
    """`assertions.assert_run` reads `stage_dimension_value` and nothing else, so an
    envelope with no `values` leaves the stage that ran scoring `not_run` --
    section 8.5's word for the stage that did NOT run."""
    envelope = extraction_stage_output(run=a_run())
    assert "values" in ENVELOPE_FIELDS
    assert [value.dimension for value in envelope["values"]] == [DIMENSION]
    assert [value.outcome for value in envelope["values"]] == ["produced"]
    StageResult(**{k: v for k, v in envelope.items() if k != "stage_id"})


def test_the_dimension_value_is_keyed_on_the_file_version_and_the_pass():
    """The envelope's subject is the file id; the DIMENSION's subject is the file
    version AND the extractor that read it.

    Section 8.2's identity for a file version is the content hash, and the hash
    alone was this key until it was measured against a real corpus: EVERY file
    there carries two recorded runs, a `filesystem`-tier pass and a `native`-tier
    pass, which read different things and produce different observation counts.
    `stage_dimension_value` is keyed (run_id, dimension, subject_ref), so the hash
    alone made those two one contested row -- and section 8.5's question, "did the
    expected text, metadata, table values appear?", has a different answer for
    each of them.

    The extractor VERSION is deliberately not in the key. Section 8.7 keeps a
    citation alive across an upgrade -- `observation_key` excludes the version for
    exactly that reason -- and a label that died on every extractor bump would be
    hand work thrown away on a schedule."""
    envelope = extraction_stage_output(run=a_run())
    assert envelope["subject_ref"] == "f-1"
    assert [value.subject_ref for value in envelope["values"]] == [
        "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
        ":pdf.text"]
    assert extraction_subject_ref(
        "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
        "pdf.text") == envelope["values"][0].subject_ref


def test_two_passes_over_one_file_version_are_two_measurements(conn, p2_run):
    """The collision this key exists to end, written against P2's real writer.

    Measured on a live three-file corpus before this change: every file version
    carried a `filesystem.record` pass and a `text.structured` pass with
    different observation counts, and the second insert raised on the primary
    key. The comment above `test_every_envelope_is_accepted_by_p2s_writer` called
    that "a collision no real replay produces"; it was the only collision a real
    replay produced."""
    run_id, ref = p2_run
    for extractor in ("filesystem.record", "text.structured"):
        _record(conn, run_id, ref,
                extraction_stage_output(run=a_run(extractor_name=extractor)))

    rows = dimension_values(conn, run_id, dimension=DIMENSION)
    assert sorted(row["subject_ref"] for row in rows) == [
        "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
        ":filesystem.record",
        "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
        ":text.structured"]


def test_one_pass_measures_as_one_subject_not_one_of_a_notional_two(conn, p2_run):
    """A format only one extractor reads produces one run, one measurement and one
    subject. Nothing here mints a placeholder for a pass that never happened: a
    row for an absent tier would be a measurement of nothing, and the counts would
    stop meaning what they say."""
    run_id, ref = p2_run
    _record(conn, run_id, ref,
            extraction_stage_output(run=a_run(extractor_name="text.structured")))

    rows = dimension_values(conn, run_id, dimension=DIMENSION)
    assert [row["subject_ref"] for row in rows] == [
        "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"
        ":text.structured"]


def test_the_version_is_not_in_the_key_so_a_label_survives_an_upgrade():
    """Section 8.7's rule, applied to the measured subject. Two versions of one
    extractor measure the same subject -- which is what makes them comparable,
    and what section 8.5's whole version-tuple comparison rests on."""
    before = extraction_stage_output(run=a_run(version="0.1.0"))
    after = extraction_stage_output(run=a_run(version="0.2.0"))

    assert before["values"][0].subject_ref == after["values"][0].subject_ref


def test_the_measurement_is_what_the_extraction_actually_produced(conn, p2_run):
    run_id, ref = p2_run
    _record(conn, run_id, ref, extraction_stage_output(run=a_run()))

    rows = dimension_values(conn, run_id, dimension=DIMENSION)
    assert [row["stage_id"] for row in rows] == [STAGE_ID]
    assert [row["outcome"] for row in rows] == ["produced"]
    assert json.loads(rows[0]["value"]) == {
        "observation_count": 3,
        "coverage": {"units": "pages", "processed": 18, "total": 18},
    }


def test_a_partial_run_does_not_measure_the_same_as_a_complete_one(conn, p2_run):
    """Section 8.6: a degraded result must never be reported as a good one. `partial`
    and `capped` both map to `produced`, and coverage is the only thing that keeps
    the three apart."""
    run_id, ref = p2_run
    complete = extraction_stage_output(run=a_run())
    partial = extraction_stage_output(run={
        **a_run(completeness="partial"), "observation_count": 1,
        "coverage": {"units": "pages", "processed": 2, "total": 18}})

    assert complete["values"][0].value != partial["values"][0].value
    assert partial["values"][0].value["coverage"]["processed"] == 2


def test_a_stage_that_ran_and_produced_nothing_still_writes_a_row(conn, p2_run):
    """A row with a NULL value, not an absent row: an absent row reads as `not_run`,
    which would say the extractor never ran on a file it deliberately abstained on."""
    run_id, ref = p2_run
    for completeness in ("unsupported", "unreadable", "metadata_only", "dataless",
                         "failed", "deferred"):
        envelope = extraction_stage_output(run={**a_run(completeness=completeness),
                                                "content_hash": completeness})
        assert envelope["values"][0].value is None, completeness
        _record(conn, run_id, ref, envelope)

    rows = dimension_values(conn, run_id, dimension=DIMENSION)
    assert len(rows) == 6
    assert all(row["value"] is None for row in rows)
    assert {row["outcome"] for row in rows} == {"abstained", "error", "deferred"}


def test_assert_run_scores_the_extraction_that_ran_rather_than_not_run(conn, p2_run):
    """The cross-part join, from P5's real envelope through P2's writer to P2's
    assertion record."""
    from eval_harness.assertions import assert_run, assertions
    from eval_harness.bundle import add_expectation, open_bundle, seal_bundle
    from eval_harness.run import start_run

    run_id, ref = p2_run
    content_hash = a_run()["content_hash"]
    bundle_id = open_bundle(conn, corpus_form="snapshot", source_scan_ref="p5-seam",
                            pinned_plan_id=None, pinned_plan_version=None,
                            policy_settings={})
    # The label names WHICH PASS it is about. `extraction_subject_ref` is the
    # subject a measurement is keyed on, so a label written against the bare hash
    # matches nothing and scores `not_run` -- which is the failure this test was
    # already built to catch, now with a second way of causing it.
    add_expectation(conn, bundle_id, dimension=DIMENSION,
                    subject_ref=extraction_subject_ref(content_hash, "pdf.text"),
                    expected_value={"observation_count": 3,
                                    "coverage": {"units": "pages", "processed": 18,
                                                 "total": 18}},
                    expected_outcome_kind="produced", source="hand-labelled")
    seal_bundle(conn, bundle_id)
    joined = start_run(conn, bundle_id=bundle_id, run_kind="replay",
                       version_tuple_ref=ref, budget_ceilings={},
                       run_settings={"model_enabled": False,
                                     "embeddings_enabled": False},
                       pinned_plan_id=None, pinned_plan_version=None)
    _record(conn, joined, ref, extraction_stage_output(run=a_run()))

    assert assert_run(conn, joined) == 1
    row = assertions(conn, joined, dimension=DIMENSION)[0]
    assert row["verdict"] != "not_run", (
        "the extraction stage ran and produced observations; `not_run` is "
        "section 8.5's word for the stage that did not")
    assert row["verdict"] == "match"
