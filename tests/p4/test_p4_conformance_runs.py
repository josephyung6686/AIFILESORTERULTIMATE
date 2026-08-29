# tests/p4/test_p4_conformance_runs.py
import pytest

from evidence_shape.conformance import (
    NonConforming, check_run, validate_run,
)
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.text_units import TextUnit

PAGE_TEXT = "Syllabus — BUSIB 4300 — Spring 2026"
SPAN = TextSpan(PAGE_TEXT.index("BUSIB"), PAGE_TEXT.index("BUSIB") + len("BUSIB 4300"))


def _run(completeness="complete", run_id="r1", **overrides):
    fields = dict(
        run_id=run_id, file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124",
        extractor_name="pdf.text", extractor_version="3.1.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness=completeness, started_at="2026-08-19T14:00:00+00:00",
        finished_at="2026-08-19T14:03:22+00:00")
    fields.update(overrides)
    return ExtractionRun(**fields)


def _observation(run_id="r1", *, text_span=None, container_path=(Segment("page", 1),),
                 raw_value="BUSIB 4300", **overrides):
    fields = dict(
        file_id="f1", content_hash="67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124", extractor_name="pdf.text",
        extractor_version="3.1.0", source_type="text_document", raw_value=raw_value,
        location=Location("body", container_path, text_span=text_span),
        occurrence_count=1, observed_at="2026-08-19T14:03:22+00:00",
        reliability="possible", run_id=run_id)
    fields.update(overrides)
    return Observation(**fields)


def _unit(run_id="r1", *, text=PAGE_TEXT, container_path=(Segment("page", 1),),
          truncated=False):
    return TextUnit(run_id=run_id, container_path=container_path, text=text,
                    truncated=truncated)


def _rules(violations):
    return sorted({violation.rule for violation in violations})


def test_a_run_with_no_observations_and_no_units_passes():
    assert check_run(_run()) == ()


def test_a_run_whose_observations_carry_no_span_needs_no_units():
    # Rule 10 applies to a span. A metadata observation has none.
    observation = _observation(
        location=Location("metadata", (Segment("field", label="Producer"),)),
        raw_value="python-docx", reliability="direct")
    assert check_run(_run(), [observation]) == ()


def test_rule_9_the_three_zero_observation_states_reject_an_observation():
    # The SPEC's three, and only these three.
    for completeness in ("unsupported", "deferred", "failed"):
        violations = check_run(_run(completeness), [_observation()])
        assert 9 in _rules(violations), completeness
        assert completeness in violations[0].message


def test_rule_9_the_three_zero_observation_states_pass_with_zero_observations():
    for completeness in ("unsupported", "deferred", "failed"):
        assert check_run(_run(completeness)) == (), completeness


def test_rule_9_an_unreadable_run_still_carries_its_metadata_rows():
    # M3, and §2.9's "indexed-but-unreadable rather than silently treated as empty".
    # A rule forbidding these rows would make an indexed PSD indistinguishable from a
    # file nobody opened.
    layer = _observation(
        source_type="design_creative", reliability="direct", raw_value="Background",
        location=Location("metadata", (Segment("layer", 3),)))
    assert check_run(_run("unreadable"), [layer]) == ()


def test_rule_9_partial_and_capped_runs_may_carry_observations():
    for completeness in ("partial", "capped"):
        assert check_run(_run(completeness), [_observation()]) == (), completeness


def test_rule_9_a_metadata_only_run_carries_none(): 
    # Settled 2026-08-20 against worked example 19: the stopping extractor emits
    # nothing; the file stays indexed through its `filesystem` observations. Rule 9's
    # note used to say the opposite, and six extractors would have run that gate.
    assert 9 in _rules(check_run(_run("metadata_only"), [_observation()]))
    assert check_run(_run("metadata_only"), []) == ()


def test_rule_9_a_dataless_run_carries_none():
    # C4: nothing was opened, so nothing was seen.
    assert 9 in _rules(check_run(_run("dataless"), [_observation()]))
    assert check_run(_run("dataless"), []) == ()


def test_rule_9_a_run_with_no_completeness_is_reported():
    mapping = _run().to_mapping()
    del mapping["completeness"]
    assert 9 in _rules(check_run(mapping))


def test_rule_9_a_completeness_outside_the_closed_vocabulary_is_reported():
    mapping = _run().to_mapping()
    mapping["completeness"] = "empty"
    assert 9 in _rules(check_run(mapping))


def test_rule_9_an_observation_from_another_run_is_reported():
    # Rules 9 and 10 are both statements about THIS run's set.
    assert 9 in _rules(check_run(_run(), [_observation(run_id="r2")]))


def test_rule_10_a_span_with_no_unit_is_reported():
    violations = check_run(_run(), [_observation(text_span=SPAN)])
    assert _rules(violations) == [10]
    assert "page=1" in violations[0].message


def test_rule_10_a_unit_at_another_address_does_not_satisfy_the_span():
    violations = check_run(_run(), [_observation(text_span=SPAN)],
                           [_unit(container_path=(Segment("page", 2),))])
    assert _rules(violations) == [10]


def test_rule_10_a_unit_on_another_run_does_not_satisfy_the_span():
    # Text is per run, not per file: a text-layer pass and an OCR pass over one PDF
    # produce two texts under two run_ids (§8.2).
    violations = check_run(_run(), [_observation(text_span=SPAN)], [_unit(run_id="r2")])
    assert 10 in _rules(violations)


def test_rule_10_and_rule_5_are_satisfied_by_the_unit_the_span_points_into():
    assert check_run(_run(), [_observation(text_span=SPAN)], [_unit()]) == ()


def test_rule_10_matches_on_the_address_and_not_on_the_descriptive_label():
    # Segment-kind rule 2: a label is descriptive only and never appears in the
    # locator, and `(run_id, unit_locator)` is what text_units is keyed on. A unit at
    # `page=1` satisfies an observation whose segment carries a heading's text.
    labelled = _observation(text_span=SPAN,
                            container_path=(Segment("page", 1, label="Course Information"),))
    assert check_run(_run(), [labelled], [_unit()]) == ()


def test_rule_5_a_raw_value_that_is_not_the_substring_is_reported():
    # RAW-1 is checked ONCE and reported under rule 5, the rule that names it.
    violations = check_run(_run(), [_observation(text_span=SPAN, raw_value="Columbia")],
                           [_unit()])
    assert _rules(violations) == [5]
    assert "RAW-1" in violations[0].message


def test_rule_5_a_span_beyond_a_truncated_unit_is_reported():
    # §8.6: never truncate silently. An observation whose span lies beyond the stored
    # prefix is not written.
    violations = check_run(
        _run(), [_observation(text_span=TextSpan(0, 40))],
        [_unit(text=PAGE_TEXT[:20], truncated=True)])
    assert _rules(violations) == [5]
    assert "truncated" in violations[0].message


def test_the_per_observation_rules_are_checked_through_the_run_gate_too():
    # One call is the whole gate: a set whose members are individually non-conforming
    # does not pass because the run-level rules happen to hold.
    mapping = _observation().to_mapping()
    mapping["occurrence_count"] = 0
    violations = check_run(_run(), [mapping])
    assert 7 in _rules(violations)


def test_a_violation_from_the_set_names_which_member_it_came_from():
    mapping = _observation().to_mapping()
    mapping["occurrence_count"] = 0
    violations = check_run(_run(), [_observation(), mapping])
    assert violations[0].message.startswith("observation 1: ")


def test_validate_run_returns_the_constructed_run():
    run = _run()
    assert validate_run(run) is run
    assert validate_run(run.to_mapping()) == run


def test_validate_run_reports_every_violation_before_raising():
    with pytest.raises(NonConforming) as raised:
        validate_run(_run("failed"), [_observation(text_span=SPAN)])
    assert _rules(raised.value.violations) == [9, 10]


def test_validate_run_fails_rather_than_coercing():
    # Done-means 2. Nothing comes back repaired, and no observation is dropped to
    # make a `failed` run conform.
    with pytest.raises(NonConforming):
        validate_run(_run("unsupported"), [_observation()])
