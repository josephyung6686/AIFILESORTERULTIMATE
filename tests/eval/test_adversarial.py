# tests/eval/test_adversarial.py
import pytest

from eval_harness.adversarial import (
    CASE_IDS, GateReport, build_case_bundle, load_all_cases, load_case, run_case,
    run_gate,
)
from eval_harness.replay import ReplayContext, StageResult
from eval_harness.stage_output import DimensionValue
from eval_harness.store import create_eval_schema


def _tuple():
    return dict(extractor_versions={}, graph_algorithm_version=None,
                prompt_fingerprint=None, model_identifier=None,
                template_library_version=None, placement_scorer_version=None,
                analysis_tiers_enabled=["filesystem"])


def _settings():
    return {"model_enabled": False, "embeddings_enabled": False}


def test_there_are_exactly_twelve_cases():
    # §8.5 names twelve failure modes observed in real corpora.
    assert CASE_IDS == ("A01", "A02", "A03", "A04", "A05", "A06",
                        "A07", "A08", "A09", "A10", "A11", "A12")
    assert len(load_all_cases()) == 12


def test_every_case_has_an_expected_a_forbidden_and_a_section():
    for case in load_all_cases():
        assert case["wording"], case["case_id"]
        assert case["sections"], case["case_id"]
        subjects = case.get("subjects") or [case]
        for subject in subjects:
            assert "expected_outcome_kind" in subject, case["case_id"]
            assert "forbidden_value" in subject, case["case_id"]


def test_a3_carries_two_fixtures_one_zip_and_one_device():
    # SPEC Contract out §9: "at least two fixtures, one of each".
    subjects = load_case("A03")["subjects"]
    assert len(subjects) == 2
    assert {s["subject_ref"] for s in subjects} == {"A03::zip::course",
                                                    "A03::device::course"}


def test_the_gate_with_no_adapters_reports_not_run_and_never_pass(eval_conn):
    # The property this whole task exists for. Nine of the ten stages are absent.
    create_eval_schema(eval_conn)
    report = run_gate(eval_conn, adapters={}, version_tuple=_tuple(),
                      budget_ceilings={}, run_settings=_settings())
    assert isinstance(report, GateReport)
    assert report.not_run_count == 11        # every case but A09, which reads the bundle
    assert report.pass_count == 1
    assert report.fail_count == 0
    assert not hasattr(report, "passed")     # SPEC Open question 9 is OPEN
    assert not hasattr(report, "accuracy")


def test_a_case_verdict_borrows_only_not_run_from_8_5(eval_conn):
    # `pass | fail | not_run` is a THIRD vocabulary and no SPEC publishes it — see
    # *Known gaps*. This pins the exact relationship to the two vocabularies that
    # ARE published, so the overlap stays a decision instead of an accident:
    #   * `pass` and `fail` are P2-local. They appear in neither §8.5's seven
    #     assertion verdicts nor Contract out §4's five outcomes, so nothing can
    #     read a case verdict as either.
    #   * `not_run` is §8.5's own verdict name, reused with §8.5's own meaning —
    #     the stage did not run — because a case that could not run and an
    #     assertion that could not run are the same fact at two scales. Minting
    #     `case_not_run` beside it would be two names for one concept.
    # If a later edit reaches for `divergent`, `abstained` or `deferred` here,
    # this fails.
    from eval_harness.vocabulary import OUTCOMES, VERDICTS
    create_eval_schema(eval_conn)
    report = run_gate(eval_conn, adapters={}, version_tuple=_tuple(),
                      budget_ceilings={}, run_settings=_settings())
    case_verdicts = {r.verdict for r in report.results}
    assert case_verdicts <= {"pass", "fail", "not_run"}
    assert case_verdicts & set(VERDICTS) <= {"not_run"}
    assert not {"pass", "fail"} & set(VERDICTS)
    assert not {"pass", "fail", "not_run"} & set(OUTCOMES)


def test_a9_passes_today_from_the_bundle_alone(eval_conn):
    # SPEC Contract out §9: A9's expected outcome IS a `capped` run row with its
    # coverage. No stage is needed and none exists.
    create_eval_schema(eval_conn)
    result = run_case(eval_conn, load_case("A09"), adapters={},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "pass"
    assert result.case_id == "A09"


def test_a_case_fails_when_the_forbidden_outcome_appears(eval_conn):
    # A01: a school facet from a substring hit inside "submit".
    create_eval_schema(eval_conn)

    def forbidden_adapter(ctx: ReplayContext):
        return [StageResult(subject_ref="A01::essay::school", outcome="produced",
                            payload=None, inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("fact", "A01::essay::school",
                                                   "produced",
                                                   {"field": "school", "value": "MIT"})])]

    result = run_case(eval_conn, load_case("A01"),
                      adapters={"factual_validation": forbidden_adapter},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "fail"
    assert "forbidden" in result.reason


def test_a_case_passes_when_the_stage_abstains(eval_conn):
    # §3.7's word-boundary rule: no MIT facet is created.
    create_eval_schema(eval_conn)

    def abstaining(ctx: ReplayContext):
        return [StageResult(subject_ref="A01::essay::school", outcome="abstained",
                            payload=None, inputs=[], budget_state="within_ceiling",
                            values=[DimensionValue("fact", "A01::essay::school",
                                                   "abstained", None)])]

    result = run_case(eval_conn, load_case("A01"),
                      adapters={"factual_validation": abstaining},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "pass"


def test_a_deferral_is_not_a_pass_and_not_a_fail(eval_conn):
    # §8.6 again: a budget event is neither quality outcome.
    create_eval_schema(eval_conn)

    def deferring(ctx: ReplayContext):
        return [StageResult(subject_ref="A01::essay::school", outcome="deferred",
                            payload=None, inputs=[], budget_state="ceiling_reached",
                            values=[DimensionValue("fact", "A01::essay::school",
                                                   "deferred", None)])]

    result = run_case(eval_conn, load_case("A01"),
                      adapters={"factual_validation": deferring},
                      version_tuple=_tuple(), budget_ceilings={},
                      run_settings=_settings())
    assert result.verdict == "not_run"
    assert "deferred" in result.reason


def test_the_gate_raises_nothing_and_decides_nothing(eval_conn):
    # SPEC Open question 9: is the gate blocking or advisory, and who enforces it?
    # P2 returns a report. It raises no exception and exits no process.
    import inspect

    from eval_harness import adversarial
    create_eval_schema(eval_conn)
    source = inspect.getsource(adversarial.run_gate)
    assert "raise" not in source
    assert "sys.exit" not in source
    run_gate(eval_conn, adapters={}, version_tuple=_tuple(), budget_ceilings={},
             run_settings=_settings())


def test_case_text_lives_in_fixtures_not_in_source():
    from pathlib import Path
    src = Path(__file__).resolve().parents[2] / "src" / "eval_harness"
    for path in src.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for term in ("submit", "uncertainty", "python-docx", "Mozilla",
                     "syllabus", "lecture", "instructor", "semester"):
            assert term not in text, f"{path.name} carries case text {term!r}"


def test_a_missing_case_file_is_an_error_not_a_silent_skip(eval_conn):
    from eval_harness.adversarial import MissingCase
    with pytest.raises(MissingCase):
        load_case("A13")
