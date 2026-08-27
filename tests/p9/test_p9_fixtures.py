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


# --- the builder's conflicts, and the guard that keeps them wired ----------------

#: Every `conflicts=()` allowed to remain in `src/grouping/`, with the reason.
#: A seventh cannot appear without failing the test below. Adding an entry here is
#: a reviewable decision; adding a bare `conflicts=()` to a module is not.
CONFLICT_FREE_BY_DESIGN = {
    ("fixtures.py", "course_dossier_fixture"):
        "SS4.4's coherent course example has no conflicting course code; the "
        "conflict-bearing shape published beside it is application_dossier_fixture",
}


def test_no_unexplained_empty_conflicts_survives_in_src_grouping():
    """`planning/30-p8-p9-connection-contract.md:60-61` added `conflicts` BECAUSE
    P8 hardcoded `()` and Site B's `target_institution` check could never fire. P9
    then hardcoded it from the other side at five sites. This is the third chance
    for the same defect, and an allowlist is what makes a fourth reviewable."""
    root = pathlib.Path(grouping.__file__).resolve().parent
    found = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text())
        scopes = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(node):
                    scopes[id(inner)] = node.name
        for node in ast.walk(tree):
            if not isinstance(node, ast.keyword) or node.arg != "conflicts":
                continue
            if isinstance(node.value, ast.Tuple) and not node.value.elts:
                found.append((path.name, scopes.get(id(node.value), "<module>")))

    unexplained = [site for site in found if site not in CONFLICT_FREE_BY_DESIGN]
    assert unexplained == [], (
        f"bare conflicts=() at {unexplained}; either wire the builder's conflicts "
        f"or add the site to CONFLICT_FREE_BY_DESIGN with a reason")
    stale = [site for site in CONFLICT_FREE_BY_DESIGN if site not in found]
    assert stale == [], f"allowlist entry no longer matches any line: {stale}"


def test_a_published_fixture_can_exercise_every_site_b_conflict_check():
    """P10 and P11 build against `GOLDEN_DOSSIERS`. If no published dossier carried
    a conflict of a kind Site B checks, they would be developed against a fixture
    that cannot reach the check -- the frozen contract's defect, one layer out."""
    from grouping.fixtures import GOLDEN_DOSSIERS

    published = {conflict.kind
                 for build in GOLDEN_DOSSIERS for conflict in build().conflicts}
    assert "target_institution" in published, published


def test_the_published_conflict_survives_into_the_dossier_request():
    """Carrying it on the fixture is not enough -- `build_dossier_request` is where
    P9 hardcoded `()`, so the conflict has to be shown crossing that seam. Site B's
    `_conflicting_institution` (`llm_harness/group_validation.py:113`) reads
    `dossier.conflicts`, and P8 builds those from the request's."""
    from privacy.release import ModelTarget

    from grouping.fixtures import application_dossier_fixture
    from grouping.p8_seam import build_dossier_request

    request = build_dossier_request(
        application_dossier_fixture(),
        model_target=ModelTarget(
            locality="local", model_id="fixture", provider="fixture"),
        prompt_template_id="template.grouping",
        prompt_fingerprint="fixture-application-fingerprint",
        max_dossier_tokens=4000)
    assert [conflict.kind for conflict in request.conflicts] == [
        "target_institution"]


# --- the span P9 sends is the observation's, never one it computed ---------------

#: The keyword arguments that carry a span to P7 or P8.
_SPAN_KEYWORDS = {"span", "excerpt_span", "text_span"}


def _spans_built_from_text_length():
    """Every span in `src/grouping/` whose value is derived from `len(...)`.

    A span computed from the length of the excerpt text is not the observation's
    span. It coincides with it only when the observation's span starts at 0 AND
    the excerpt was not truncated, which is why `(0, len(text))` looked right and
    why it broke on every metadata observation, whose span is `None`.
    """
    root = pathlib.Path(grouping.__file__).resolve().parent
    found = []
    for path in sorted(root.glob("*.py")):
        tree = ast.parse(path.read_text())
        scopes = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for inner in ast.walk(node):
                    scopes[id(inner)] = node.name

        def _uses_len(node):
            return any(
                isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
                and inner.func.id == "len"
                for inner in ast.walk(node))

        for node in ast.walk(tree):
            # `TextSpan(...)` built from a length, positionally or by keyword.
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "TextSpan" and _uses_len(node)):
                found.append((path.name, scopes.get(id(node), "<module>"),
                              "TextSpan"))
            # `span=` / `excerpt_span=` / `text_span=` built from a length.
            if (isinstance(node, ast.keyword) and node.arg in _SPAN_KEYWORDS
                    and _uses_len(node.value)):
                found.append((path.name, scopes.get(id(node.value), "<module>"),
                              node.arg))
    return found


def test_no_span_in_src_grouping_is_computed_from_the_text_it_describes():
    """P7 refuses a requested span that disagrees with the observation's own, and
    it refuses it AFTER minting the release -- "consent records the exact requested
    reference and never repairs one" (`src/privacy/gate.py:460`). P9 built
    `(0, len(excerpt.text))` at two sites, so every observation whose span was
    `None` or did not start at 0 was unreleasable.

    There is no allowlist. A span is either the observation's or it is invented,
    and `Excerpt.text_span` now carries the observation's, so nothing under
    `src/grouping/` has a reason to compute one."""
    assert _spans_built_from_text_length() == [], (
        "a span computed from text length is not the observation's span; carry "
        "`Excerpt.text_span` through instead")
