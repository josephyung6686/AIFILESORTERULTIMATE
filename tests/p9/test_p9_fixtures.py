# tests/p9/test_p9_fixtures.py
"""P9 Task 3 — the golden dossiers, and the fixture isolation rule.

Every excerpt in a golden dossier must resolve to a real P4 observation. A fixture
that minted its own key would be a citation nothing can check, and the whole point
of these two shapes is that a later part can build against them and know the
citations are the real thing.

`src/grouping/` may never import a test fixture. The P8 and P13 fixtures live
under `tests/` and stand in only until those producers exist; a source module
importing one would make the stand-in part of the product.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

import grouping
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import observations_by_key, record_observation, record_run
from grouping.fixtures import (
    APPLICATION_CANDIDATE,
    APPLICATION_FILES,
    CONFLICTING_FILE,
    COURSE_CANDIDATE,
    COURSE_FILES,
    EXTRACTOR,
    GOLDEN_DOSSIERS,
    application_dossier_fixture,
    course_dossier_fixture,
    fixture_location,
)
from grouping.records import CandidateGroupDossier
from grouping.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR

GROUPING_ROOT = pathlib.Path(grouping.__file__).resolve().parent
OBSERVED_AT = "2026-08-26T00:00:00Z"


@pytest.fixture()
def seeded_conn(conn):
    """A real evidence store holding every observation the fixtures cite."""
    from database_agent.db import create_schema

    create_schema(conn)
    create_evidence_schema(conn)
    seeded = (
        *COURSE_FILES,
        COURSE_CANDIDATE,
        *APPLICATION_FILES,
        APPLICATION_CANDIDATE,
        CONFLICTING_FILE,
    )
    for index, (file_id, content_hash, _kind, raw_value) in enumerate(seeded):
        run_id = f"run-{index}"
        record_run(conn, ExtractionRun(
            run_id=run_id, file_id=file_id, content_hash=content_hash,
            extractor_name=EXTRACTOR, extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=OBSERVED_AT,
            finished_at=OBSERVED_AT,
        ))
        location = fixture_location()
        record_observation(conn, Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name=EXTRACTOR, extractor_version="1.0.0",
            source_type="text_document", raw_value=raw_value,
            location=location, occurrence_count=1, observed_at=OBSERVED_AT,
            reliability="direct", run_id=run_id,
        ))
    return conn


# --- the course dossier ---------------------------------------------------------


def test_the_course_dossier_has_two_anchors_and_one_context_candidate():
    """A homework-like name and a semantic link are not an anchor."""
    course = course_dossier_fixture()
    assert {item.basis for item in course.anchor_files} == {DIRECT_ANCHOR}
    assert sorted(item.file_id for item in course.anchor_files) == [
        "lecture-08", "midterm-practice",
    ]
    assert [item.file_id for item in course.candidate_files] == ["hw-3"]
    assert course.candidate_files[0].basis == CONTEXT_SUPPORTED


def test_the_course_candidate_carries_no_anchor_fact():
    course = course_dossier_fixture()
    assert course.candidate_files[0].key_facts == ()
    assert course.candidate_files[0].why_retrieved


def test_each_course_anchor_states_the_basis_value_independently():
    """§4.3 counts how many anchor documents independently state the same course."""
    course = course_dossier_fixture()
    stating = {
        fact.file_ids[0]
        for item in course.anchor_files
        for fact in item.key_facts
        if fact.value == "PHYS1401"
    }
    assert stating == {"lecture-08", "midterm-practice"}


# --- the application dossier ----------------------------------------------------


def test_the_application_dossier_shows_the_conflicting_essay_rather_than_hiding_it():
    """A packet must not silently absorb a conflicting target institution.

    It can only avoid that if the model is shown the conflict, so the Duke essay
    is a flagged candidate in the dossier, not an omission.
    """
    application = application_dossier_fixture()
    candidates = {item.file_id for item in application.candidate_files}
    assert "essay-duke" in candidates
    assert "essay-duke" in application.engine_flagged_outliers
    assert application.conflicts
    conflict = application.conflicts[0]
    assert conflict.kind == "target_institution"
    assert set(conflict.competing_values) == {"Columbia", "Duke"}
    assert application.omissions.budget_cap_dropped == ()


def test_the_application_anchors_carry_direct_columbia_evidence():
    application = application_dossier_fixture()
    values = {
        fact.value
        for item in application.anchor_files
        for fact in item.key_facts
    }
    assert values == {"Columbia"}


# --- every citation resolves ----------------------------------------------------


@pytest.mark.parametrize("build", GOLDEN_DOSSIERS, ids=lambda fn: fn.__name__)
def test_every_excerpt_resolves_to_a_seeded_p4_observation(seeded_conn, build):
    dossier = build()
    assert dossier.excerpts
    for excerpt in dossier.excerpts:
        found = observations_by_key(seeded_conn, excerpt.observation_key)
        assert found, excerpt.observation_key


@pytest.mark.parametrize("build", GOLDEN_DOSSIERS, ids=lambda fn: fn.__name__)
def test_every_anchor_fact_resolves_to_a_seeded_p4_observation(seeded_conn, build):
    dossier = build()
    for fact in dossier.key_facts:
        assert observations_by_key(seeded_conn, fact.observation_key), fact


@pytest.mark.parametrize("build", GOLDEN_DOSSIERS, ids=lambda fn: fn.__name__)
def test_a_golden_dossier_is_the_frozen_record_and_not_a_dict(build):
    assert isinstance(build(), CandidateGroupDossier)


def test_the_fixtures_are_deterministic():
    """Two calls produce equal dossiers, so a replay diff is a real diff."""
    for build in GOLDEN_DOSSIERS:
        assert build() == build()


# --- isolation ------------------------------------------------------------------


def test_src_grouping_imports_no_test_fixture():
    """A source module importing a stand-in makes the stand-in part of the product."""
    offenders = []
    for path in sorted(GROUPING_ROOT.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                if "p8_fixtures" in name or "p13_fixtures" in name:
                    offenders.append(f"{path.name}:{node.lineno}:{name}")
                if name.startswith("tests") or name in {"p8", "p9", "p13"}:
                    offenders.append(f"{path.name}:{node.lineno}:{name}")
    assert offenders == [], offenders


def test_src_grouping_imports_no_later_part():
    """P10, P11 and P13 do not exist. P8 is reached only at the named seam."""
    allowed_p8_importers = {"p8_seam.py"}
    offenders = []
    for path in sorted(GROUPING_ROOT.glob("*.py")):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            module = ""
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
            elif isinstance(node, ast.Import):
                module = node.names[0].name
            if module.startswith("llm_harness") and path.name not in allowed_p8_importers:
                offenders.append(f"{path.name}:{node.lineno}:{module}")
    assert offenders == [], offenders


# --- the stand-in fixtures ------------------------------------------------------


def test_the_p8_fixture_builds_p8s_own_verdict_and_not_a_lookalike():
    """P9 publishes no verdict enum. A shape-alike would be the second one."""
    from llm_harness.records import P8Verdict
    from p9.p8_fixtures import RECORDED_P8_VERDICTS

    assert RECORDED_P8_VERDICTS
    for build in RECORDED_P8_VERDICTS:
        assert isinstance(build(), P8Verdict), build.__name__


def test_the_p8_fixture_covers_both_outcomes_p9_had_no_word_for():
    """`weak` and `abstain` are the two P8 outcomes P9's old enum could not say."""
    from p9.p8_fixtures import RECORDED_P8_VERDICTS

    outcomes = {build().outcome for build in RECORDED_P8_VERDICTS}
    assert "weak" in outcomes
    assert "abstain" in outcomes


def test_a_weak_verdict_may_never_propose():
    """§3.6: a possible-clue never becomes a folder proposal."""
    from p9.p8_fixtures import weak_verdict

    verdict = weak_verdict()
    assert verdict.outcome == "weak"
    assert verdict.may_propose is False


def test_a_context_supported_verdict_always_requires_review():
    """Invariant 3: valid on context is sent to review, never silently accepted."""
    from p9.p8_fixtures import accepted_context_supported_verdict

    verdict = accepted_context_supported_verdict()
    assert verdict.requires_review is True


def test_the_p13_fixture_is_test_only_and_names_its_swap_boundary():
    from p9 import p13_fixtures

    assert "TESTS ONLY" in p13_fixtures.__doc__
    assert "P13" in p13_fixtures.__doc__
    for build in p13_fixtures.RECORDED_REVIEW_ACTIONS:
        action = build()
        assert action.action in p13_fixtures.REVIEW_ACTIONS
        assert action.basis


def test_a_review_action_outside_p13s_set_is_refused():
    from p9.p13_fixtures import accept_group

    with pytest.raises(ValueError):
        accept_group(action="delete")


def test_no_review_action_deletes_or_moves_a_file():
    """P9 records a decision. It does not delete or move source files."""
    from p9.p13_fixtures import REVIEW_ACTIONS

    for banned in ("delete", "move", "trash", "remove"):
        assert not any(banned in action for action in REVIEW_ACTIONS), banned
