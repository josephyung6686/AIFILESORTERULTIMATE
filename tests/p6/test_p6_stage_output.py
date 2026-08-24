# tests/p6/test_p6_stage_output.py
"""§8.5 / B7 — P6's envelope, driven through P2's LIVE writer.

Nothing here is asserted against a reconstruction of P2. Every outcome pairing goes
into `eval_harness.stage_output.record_stage_output` and is read back out of the
`stage_output` table, because B7's claim is that a budget stop and a considered
refusal are "distinguishable from the records alone" — which is a claim about rows,
not about a mapping table.

Nor is `ResolveResult` reconstructed. Task 20's real dataclass is imported, and
`test_the_envelope_reads_only_task_20s_published_fields` pins the eight fields this
module reads, so a change on Task 20's side breaks this test rather than silently
changing what P6 reports to P2.
"""
from __future__ import annotations

import dataclasses
import json

import pytest

from eval_harness.replay import StageResult
from eval_harness.run import (
    VERSION_AXES, VERSION_TUPLE_FIELDS, record_version_tuple, start_run,
)
from eval_harness.stage_output import (
    DimensionValue, dimension_values, record_stage_output, stage_outputs,
)
from eval_harness.store import create_eval_schema
from eval_harness.vocabulary import (
    BUDGET_STATES, DIMENSIONS, OUTCOMES, STAGE_IDS, UnknownDimension, UnknownStage,
    check_dimension, check_stage,
)
from evidence_shape.fixtures import by_number
from evidence_shape.store import record_run

from extractors.stage_output import extraction_stage_output

import facts.stage_output as stage_output_module
from facts.resolver import ResolveResult
from facts.stage_output import (
    DIMENSION, ENVELOPE_FIELDS, STAGE_ID, UnsettledOutcome, fact_stage_output,
    fact_version_axes,
)

FILE_ID = "file-01"
#: Fixture 1's content hash, so the P4 half of this file uses the real one.
CONTENT_HASH = by_number(1).run.content_hash
#: Three more file VERSIONS. P2's `stage_dimension_value` is keyed
#: `(run_id, dimension, subject_ref)` — verified by execution below — so two results
#: emitted into the same run must be two different subjects. That is P2 enforcing
#: "one envelope per subject P6 decides about", not a test convenience.
CONTENT_HASH_B = "b" * 64
CONTENT_HASH_C = "c" * 64
CONTENT_HASH_D = "d" * 64

#: The eight fields Task 20 publishes on `ResolveResult`, which are exactly the
#: attributes `facts.stage_output` reads off a result and the whole of its input.
RESULT_FIELDS = ("file_id", "content_hash", "fact_ids", "reason_counts",
                 "stages_run", "stages_barred", "deferred_against",
                 "unresolved_ids", "error")


def a_result(**overrides) -> ResolveResult:
    base = dict(file_id=FILE_ID, content_hash=CONTENT_HASH,
                stages_run=("direct", "rule"))
    base.update(overrides)
    return ResolveResult(**base)


PRODUCED = a_result(fact_ids=("fact-1",))
ABSTAINED = a_result(content_hash=CONTENT_HASH_B,
                     reason_counts={"no_candidate_evidence": 2,
                                    "below_margin": 1})
DEFERRED = a_result(content_hash=CONTENT_HASH_C,
                    reason_counts={"budget_deferred": 3},
                    stages_barred={"llm": "budget"},
                    deferred_against=("model.max_cost_per_scan",))
ERRORED = ResolveResult.errored(file_id=FILE_ID, content_hash=CONTENT_HASH_D,
                                error="rules.apply_rules: boom")


@pytest.fixture()
def p2_run(p6_conn):
    """A live P2 run. Mirrors `tests/p5/test_p5_stage_output.py` exactly."""
    create_eval_schema(p6_conn)
    ref = record_version_tuple(
        p6_conn, extractor_versions={"pdf.text": "1.0.0"},
        graph_algorithm_version=None, prompt_fingerprint=None,
        model_identifier=None, template_library_version=None,
        placement_scorer_version=None,
        analysis_tiers_enabled=["filesystem", "native"])
    run_id = start_run(p6_conn, bundle_id="b-p6", run_kind="replay",
                       version_tuple_ref=ref, budget_ceilings={},
                       run_settings={"model_enabled": False,
                                     "embeddings_enabled": False},
                       pinned_plan_id=None, pinned_plan_version=None)
    return run_id, ref


def emit(conn, p2_run, result: ResolveResult) -> int:
    run_id, ref = p2_run
    envelope = fact_stage_output(result=result)
    return record_stage_output(
        conn, run_id=run_id, stage_id=envelope["stage_id"],
        subject_ref=envelope["subject_ref"], outcome=envelope["outcome"],
        payload=envelope["payload"], version_tuple_ref=ref,
        inputs=envelope["inputs"], budget_state=envelope["budget_state"],
        dimension_values=envelope["values"])


# --- the input is Task 20's, imported rather than re-described ------------------

def test_the_envelope_reads_only_task_20s_published_fields():
    # `ResolveResult` is Task 20's and P6 has exactly one definition of it. If that
    # field list changes, this breaks here rather than changing what P6 reports.
    assert tuple(f.name for f in dataclasses.fields(ResolveResult)) == RESULT_FIELDS
    for result in (PRODUCED, ABSTAINED, DEFERRED, ERRORED):
        assert fact_stage_output(result=result)["stage_id"] == STAGE_ID


# --- two vocabularies that look like one ----------------------------------------

def test_the_stage_id_is_one_of_section_8_5s_ten():
    assert STAGE_ID == "factual_validation"
    assert STAGE_ID in STAGE_IDS
    assert check_stage(STAGE_ID) == STAGE_ID


def test_the_dimension_is_fact_and_the_two_lists_are_not_interchangeable():
    assert DIMENSION == "fact"
    assert DIMENSION in DIMENSIONS
    assert DIMENSION not in STAGE_IDS
    assert STAGE_ID not in DIMENSIONS
    with pytest.raises(UnknownStage):
        check_stage(DIMENSION)
    with pytest.raises(UnknownDimension):
        check_dimension(STAGE_ID)


# --- the envelope shape ---------------------------------------------------------

def test_the_envelope_is_exactly_p2s_stage_result_shape():
    envelope = fact_stage_output(result=PRODUCED)
    assert set(ENVELOPE_FIELDS) == set(envelope) - {"stage_id"}
    StageResult(**{k: v for k, v in envelope.items() if k != "stage_id"})


def test_p6_fills_values_where_p5_does_not_because_the_fact_dimension_is_p6s():
    assert "values" in ENVELOPE_FIELDS
    envelope = fact_stage_output(result=PRODUCED)
    assert [value.dimension for value in envelope["values"]] == [DIMENSION]
    assert all(isinstance(value, DimensionValue) for value in envelope["values"])


def test_subject_ref_is_the_content_hash_because_a_fact_is_per_file_version():
    assert fact_stage_output(result=PRODUCED)["subject_ref"] == CONTENT_HASH


def test_inputs_carries_the_subject_refs_of_the_extraction_stage_outputs():
    # Asserted against P5 AS BUILT: `extraction_stage_output` keys its subject by
    # file id, so P6's `inputs[]` must be file ids even though P6's own subject is
    # the content hash. Reading P5's live envelope here means a change on that side
    # breaks this test instead of quietly mis-linking two stages.
    p5_envelope = extraction_stage_output(run={
        "file_id": FILE_ID, "content_hash": CONTENT_HASH,
        "extractor_name": "pdf.text", "extractor_version": "1.0.0",
        "source_type": "text_document", "analysis_tier": "native",
        "completeness": "complete", "observation_count": 3,
        "coverage": {"units": "pages", "processed": 1, "total": 1}})
    assert p5_envelope["subject_ref"] == FILE_ID
    assert fact_stage_output(result=PRODUCED)["inputs"] == (p5_envelope["subject_ref"],)


# --- the four outcomes ----------------------------------------------------------

def test_facts_written_is_produced_within_ceiling():
    envelope = fact_stage_output(result=PRODUCED)
    assert (envelope["outcome"], envelope["budget_state"]) == \
        ("produced", "within_ceiling")


def test_evidence_based_refusal_is_abstained_within_ceiling():
    envelope = fact_stage_output(result=ABSTAINED)
    assert (envelope["outcome"], envelope["budget_state"]) == \
        ("abstained", "within_ceiling")


def test_a_ceiling_is_deferred_ceiling_reached():
    envelope = fact_stage_output(result=DEFERRED)
    assert (envelope["outcome"], envelope["budget_state"]) == \
        ("deferred", "ceiling_reached")


def test_a_ceiling_outranks_facts_because_deferred_work_must_be_visible_as_deferred():
    # §00: the product must avoid "the false impression that an unprocessed file was
    # understood and found unimportant". A run that wrote two facts AND hit a ceiling
    # reports `deferred`; reporting `produced` would hide the unfinished half.
    mixed = a_result(fact_ids=("fact-1", "fact-2"),
                     reason_counts={"budget_deferred": 1},
                     stages_barred={"llm": "budget"},
                     deferred_against=("model.max_dossier_tokens_per_call",))
    envelope = fact_stage_output(result=mixed)
    assert (envelope["outcome"], envelope["budget_state"]) == \
        ("deferred", "ceiling_reached")


def test_the_stage_failed_is_error():
    envelope = fact_stage_output(result=ERRORED)
    assert envelope["outcome"] == "error"
    assert envelope["budget_state"] in BUDGET_STATES


def test_every_outcome_p6_can_emit_is_one_of_p2s_five():
    for result in (PRODUCED, ABSTAINED, DEFERRED, ERRORED):
        assert fact_stage_output(result=result)["outcome"] in OUTCOMES


# --- through P2's live writer ---------------------------------------------------

def test_produced_and_abstained_are_written_and_read_back(p6_conn, p2_run):
    emit(p6_conn, p2_run, PRODUCED)
    emit(p6_conn, p2_run, ABSTAINED)
    rows = stage_outputs(p6_conn, p2_run[0], stage_id=STAGE_ID)
    assert [row["outcome"] for row in rows] == ["produced", "abstained"]
    assert {row["budget_state"] for row in rows} == {"within_ceiling"}
    assert {row["subject_ref"] for row in rows} == {CONTENT_HASH, CONTENT_HASH_B}
    assert json.loads(rows[0]["inputs"]) == [FILE_ID]


def test_the_two_are_distinguishable_from_the_records_alone(p6_conn, p2_run):
    # Done-means 20. Nothing in this assertion consults P6: the reader has the
    # `stage_output` rows and only those.
    emit(p6_conn, p2_run, ABSTAINED)
    emit(p6_conn, p2_run, DEFERRED)
    rows = stage_outputs(p6_conn, p2_run[0], stage_id=STAGE_ID)
    pairs = [(row["outcome"], row["budget_state"]) for row in rows]
    assert pairs == [("abstained", "within_ceiling"),
                     ("deferred", "ceiling_reached")]
    deferred_payload = json.loads(rows[1]["payload"])
    assert deferred_payload["unresolved_reasons"] == {"budget_deferred": 3}
    assert deferred_payload["deferred_against"] == ["model.max_cost_per_scan"]


def test_p2s_writer_refuses_the_pairing_p6_must_never_emit(p6_conn, p2_run):
    # P6 does not need to invent B7's rule; it needs to not fight it. Proof that the
    # rule is live rather than remembered.
    run_id, ref = p2_run
    with pytest.raises(ValueError):
        record_stage_output(p6_conn, run_id=run_id, stage_id=STAGE_ID,
                            subject_ref=CONTENT_HASH, outcome="abstained",
                            payload=None, version_tuple_ref=ref, inputs=(FILE_ID,),
                            budget_state="ceiling_reached")
    with pytest.raises(ValueError):
        record_stage_output(p6_conn, run_id=run_id, stage_id=STAGE_ID,
                            subject_ref=CONTENT_HASH, outcome="deferred",
                            payload=None, version_tuple_ref=ref, inputs=(FILE_ID,),
                            budget_state="within_ceiling")


def test_an_envelope_is_emitted_for_a_file_that_produced_facts_and_for_one_that_did_not(
        p6_conn, p2_run):
    # Done-means 21, both halves, in one run.
    emit(p6_conn, p2_run, PRODUCED)
    emit(p6_conn, p2_run, ABSTAINED)
    rows = stage_outputs(p6_conn, p2_run[0], stage_id=STAGE_ID)
    assert len(rows) == 2
    assert all(row["version_tuple_ref"] == p2_run[1] for row in rows)


def test_the_dimension_value_lands_under_fact_and_carries_its_own_outcome(
        p6_conn, p2_run):
    emit(p6_conn, p2_run, PRODUCED)
    values = dimension_values(p6_conn, p2_run[0], dimension=DIMENSION)
    assert len(values) == 1
    assert values[0]["stage_id"] == STAGE_ID
    assert values[0]["subject_ref"] == CONTENT_HASH
    assert values[0]["outcome"] == "produced"
    assert json.loads(values[0]["value"]) == {"fact_count": 1, "unresolved_count": 0}


def test_a_dimension_value_with_nothing_produced_is_null(p6_conn, p2_run):
    emit(p6_conn, p2_run, ABSTAINED)
    values = dimension_values(p6_conn, p2_run[0], dimension=DIMENSION)
    assert values[0]["outcome"] == "abstained"
    assert values[0]["value"] is None


# --- the payload ----------------------------------------------------------------

def test_the_payload_is_p6s_own_and_carries_no_fact_id():
    # §8.5 diffs STORED FORMS across two runs. A `fact_id` is minted per row and is
    # not stable between two runs of the same corpus, so one in the payload would
    # report a divergence that is not one.
    payload = json.loads(fact_stage_output(result=PRODUCED)["payload"])
    assert payload["fact_count"] == 1
    assert "fact-1" not in fact_stage_output(result=PRODUCED)["payload"]
    assert set(payload) == {"fact_count", "unresolved_reasons", "stages_run",
                            "stages_barred", "deferred_against", "error"}


def test_the_payload_is_byte_stable_for_the_same_result():
    first = fact_stage_output(result=DEFERRED)["payload"]
    second = fact_stage_output(result=a_result(
        content_hash=CONTENT_HASH_C, reason_counts={"budget_deferred": 3},
        stages_barred={"llm": "budget"},
        deferred_against=("model.max_cost_per_scan",)))["payload"]
    assert first == second


# --- the two refusals this module makes -----------------------------------------

def test_a_privacy_only_refusal_has_no_settled_outcome_and_is_held_open():
    # NEEDS-JOSEPH, stated in this task's preamble: the §8.5 table would call this
    # `abstained`, the SPEC's `unresolved` rule 4 forbids exactly that, and P2's
    # writer makes `deferred` unreachable without a ceiling. Held open as a raise.
    withheld = a_result(reason_counts={"privacy_withheld": 2},
                        stages_barred={"llm": "privacy"})
    with pytest.raises(UnsettledOutcome):
        fact_stage_output(result=withheld)


def test_a_privacy_bar_that_still_produced_a_fact_reports_produced():
    # The raise is narrow: any field reachable by `direct` or `rule` is still
    # answered, and P8 absent means nothing is ever withheld at all.
    partial = a_result(fact_ids=("fact-1",),
                       reason_counts={"privacy_withheld": 1},
                       stages_barred={"llm": "privacy"})
    assert fact_stage_output(result=partial)["outcome"] == "produced"


def test_a_result_with_no_record_at_all_is_refused():
    # B7's whole point: without the `unresolved` row, §3.6's "no fact" is a missing
    # row and P2 cannot tell a considered refusal from a crash or a skip. A result
    # with neither a fact nor a reason is that missing row, and it is a bug in the
    # producer, not an outcome to report.
    with pytest.raises(ValueError):
        fact_stage_output(result=a_result())


# --- P6's slice of the version tuple --------------------------------------------

@pytest.fixture()
def p4_run(p6_conn):
    record_run(p6_conn, by_number(1).run)
    return by_number(1).run


def test_fact_version_axes_supplies_p6s_three_and_assembles_no_tuple(p6_conn, p4_run):
    axes = fact_version_axes(p6_conn, content_hash=p4_run.content_hash,
                             model_identifier=None, prompt_fingerprint=None)
    assert set(axes) == {"extractor_versions", "model_identifier",
                         "prompt_fingerprint"}
    assert set(axes) < set(VERSION_AXES)
    assert axes["extractor_versions"] == {"pdf.text": "1.0.0"}


def test_the_axes_merge_into_p2s_seven_field_tuple(p6_conn, p4_run):
    create_eval_schema(p6_conn)
    axes = fact_version_axes(p6_conn, content_hash=p4_run.content_hash,
                             model_identifier="claude-x",
                             prompt_fingerprint="sha256:ab")
    ref = record_version_tuple(
        p6_conn, graph_algorithm_version=None, template_library_version=None,
        placement_scorer_version=None, analysis_tiers_enabled=["native"], **axes)
    assert ref.startswith("sha256:")
    assert set(axes) <= set(VERSION_TUPLE_FIELDS)


def test_a_content_hash_p4_never_ran_yields_an_empty_extractor_map(p6_conn):
    # Not an error: §8.5's tuple for a file version with no extraction run is empty
    # on P6's first axis, and the caller still gets a mergeable dict.
    axes = fact_version_axes(p6_conn, content_hash=CONTENT_HASH_B,
                             model_identifier=None, prompt_fingerprint=None)
    assert axes == {"extractor_versions": {}, "model_identifier": None,
                    "prompt_fingerprint": None}


def test_two_versions_of_one_extractor_are_refused_rather_than_resolved(p6_conn):
    # §3.4's cache key is per (extractor, version) and a map cannot hold both, so a
    # caller comparing two extractor versions is comparing two runs. Same rule P5
    # states on its own half of this axis.
    run = by_number(1).run
    record_run(p6_conn, run)
    record_run(p6_conn, dataclasses.replace(run, run_id="run-01b",
                                            extractor_version="2.0.0"))
    with pytest.raises(ValueError):
        fact_version_axes(p6_conn, content_hash=run.content_hash,
                          model_identifier=None, prompt_fingerprint=None)


def test_the_module_defines_no_number():
    numbers = {name: value for name, value in vars(stage_output_module).items()
               if not name.startswith("_") and not isinstance(value, bool)
               and isinstance(value, (int, float))}
    assert numbers == {}
