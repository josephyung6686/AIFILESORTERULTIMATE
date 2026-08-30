"""§8.7: "inspect or reset learned preferences, so personalization remains
understandable and reversible".

`74` §6 B11's negative twin is
`test_a_reset_that_leaves_the_producing_evidence_unshown_is_refused`. Reversible is
the easy half; UNDERSTANDABLE is the one the twin is about. A reset made against a
view that never showed what produced the preferences is indistinguishable
afterwards from one made in full knowledge, which is exactly the state §8.7 exists
to prevent -- and it is the same rule `collect` already enforces for a rejection,
applied to the gesture that throws learning away rather than the one that adds to
it.
"""
from __future__ import annotations

import ast
import inspect
import pathlib
import pkgutil

import pytest

from database_agent.events import CORRECTION_SCOPES
from evidence_shape.observation import Location, Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from privacy.display import RedactionSettings

from review_surface.collect import collect
from review_surface.learning_view import (
    EvidenceNotShown,
    LearningNotAppliedHere,
    NothingIsDeletedHere,
    collect_reset,
    learning_view,
)
from review_surface.presentation import record_presentation
from review_surface.store import record_action
from review_surface.vocabulary import (
    ACTION_REJECT,
    ACTION_RESET_LEARNING,
    SURFACE_LEARNING,
    SURFACE_PLACEMENT,
)

T0 = "2026-08-29T00:00:00Z"
HASH_A = "a" * 64
SHOWN = RedactionSettings(names="shown", previews="shown", thumbnails="shown",
                          ocr_text="shown", location_data="shown")


def _observation(conn) -> str:
    record_run(conn, ExtractionRun(
        run_id="run-1", file_id="f-1", content_hash=HASH_A,
        extractor_name="fixture-pdf", extractor_version="1",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, observation_count=1,
        coverage=None, finished_at=T0, failure_reason=None))
    observation = Observation(
        file_id="f-1", content_hash=HASH_A, extractor_name="fixture-pdf",
        extractor_version="1", source_type="text_document",
        raw_value="Columbia University",
        location=Location(zone="body", container_path=(), text_span=None,
                          time_span=None, region=None),
        occurrence_count=1, observed_at=T0, reliability="direct",
        run_id="run-1", normalized_value="Columbia University",
        context_before="School form for ", context_after=".",
        context_truncated=False, confidence=None, signal_tier=None)
    record_observation(conn, observation)
    return observation.observation_key


def _projection(key):
    return (
        {"correction_scope": "file", "correction_subject": "f-1",
         "polarity": "reject", "proposal_class": "placement",
         "basis_key": "node:n-receipts", "observed_at": T0,
         "evidence_refs": (key,)},
        {"correction_scope": "corpus", "correction_subject": "corpus",
         "polarity": "accept", "proposal_class": "residual",
         "basis_key": "node:n-clips", "observed_at": T0,
         "evidence_refs": ()},
    )


def _learning_presentation(conn, *, evidence_refs):
    return record_presentation(
        conn, surface=SURFACE_LEARNING, subject_ref="learning",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=evidence_refs, user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref


def test_a_reset_that_leaves_the_producing_evidence_unshown_is_refused(p13_conn):
    """`74` §6 B11's negative twin, in both directions.

    The same reset is refused against a presentation that showed nothing, and
    accepted against one that showed the key the view's rows rest on. Asserting
    only the refusal would pass just as well against a `collect_reset` that
    refused everything; asserting only the acceptance would pass against one that
    checked nothing.
    """
    key = _observation(p13_conn)
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: _projection(key))
    assert view.evidence_keys() == (key,)

    blind = _learning_presentation(p13_conn, evidence_refs=())
    with pytest.raises(EvidenceNotShown) as caught:
        collect_reset(p13_conn, view, action_id="a-blind",
                      subject_ref="learning", plan_version="plan-1",
                      session_id="s-1", correction_scope="corpus",
                      presented_state_ref=blind, user_id="jy", acted_at=T0,
                      component_version="p13-1")
    assert key in str(caught.value)

    informed = _learning_presentation(p13_conn, evidence_refs=(key,))
    action = collect_reset(
        p13_conn, view, action_id="a-reset", subject_ref="learning",
        plan_version="plan-1", session_id="s-1", correction_scope="corpus",
        presented_state_ref=informed, user_id="jy", acted_at=T0,
        component_version="p13-1")
    assert action.action == ACTION_RESET_LEARNING
    assert action.routed_to == ("P1",)


def test_the_view_lists_scoped_learning_records_with_their_evidence(p13_conn):
    """Done-means 20, first two clauses."""
    key = _observation(p13_conn)
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: _projection(key))
    assert len(view.rows) == 2
    assert {row.correction_scope for row in view.rows} == {"file", "corpus"}
    assert set(view.scopes) == set(CORRECTION_SCOPES)
    scoped = next(row for row in view.rows if row.correction_scope == "file")
    assert scoped.citations[0].observation_key == key
    assert scoped.citations[0].excerpt == "Columbia University"


def test_a_row_with_no_evidence_says_so_rather_than_looking_evidenced(p13_conn):
    """§8.7: none of the learning is hidden from this view, so a thin row is
    shown as thin rather than dropped for looking unconvincing."""
    key = _observation(p13_conn)
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: _projection(key))
    corpus_row = next(row for row in view.rows
                      if row.correction_scope == "corpus")
    assert corpus_row.citations == ()
    assert "no stored evidence" in corpus_row.explanation
    assert len(view.rows) == len(_projection(key))


def test_negative_examples_appear_beside_the_preferences(p13_conn):
    key = _observation(p13_conn)
    ref = record_presentation(
        p13_conn, surface=SURFACE_PLACEMENT, subject_ref="d1",
        plan_version="plan-1", session_id="s-1", settings=SHOWN,
        evidence_refs=(key,), user_id="jy", component_version="p13-1",
        rendered_at=T0).presented_state_ref
    record_action(p13_conn, collect(
        p13_conn, action_id="a-rej", surface=SURFACE_PLACEMENT,
        subject_ref="d1", plan_version="plan-1", session_id="s-1",
        action=ACTION_REJECT, correction_scope="node",
        presented_state_ref=ref, user_id="jy", acted_at=T0,
        component_version="p13-1", payload={"node_id": "n-receipts"}))
    view = learning_view(p13_conn, subject_refs=("d1",),
                         projection=lambda: _projection(key))
    assert len(view.negative_examples) == 1
    assert view.negative_examples[0].subject_ref == "d1"
    assert key in view.evidence_keys()


def test_no_learning_is_applied_by_p13_and_nothing_is_deleted(p13_conn):
    """P13 renders P1's projection and collects the reset.

    SPEC Open question 11 is OPEN -- whether a `review presentation` is deletable
    derived data -- so P13's tables stay append-only by trigger and the delete
    door says so by name instead of being an absence someone has to notice.
    """
    key = _observation(p13_conn)
    view = learning_view(p13_conn, subject_refs=(),
                         projection=lambda: _projection(key))
    with pytest.raises(LearningNotAppliedHere):
        view.apply()
    with pytest.raises(NothingIsDeletedHere):
        view.delete()


#: Every module that would send something somewhere. §8.7: "No silent global
#: training" -- P13 has no telemetry path and sends nothing anywhere.
EGRESS_MODULES: tuple[str, ...] = (
    "urllib", "requests", "httpx", "http", "socket", "smtplib", "ftplib",
    "telnetlib", "subprocess")


def _imports(tree) -> set[str]:
    """Every module name imported, by parsing rather than by searching text."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_p13_has_no_telemetry_path(p13_conn):
    """§8.7: every surface P13 renders and every action it collects stays local.

    Parsed, not grepped, and asserted against a sabotage module -- a text search
    would match these very module names in this file's own prose, which is the
    false result this project has produced before.
    """
    import review_surface

    for module_info in pkgutil.iter_modules(review_surface.__path__):
        module = __import__(f"review_surface.{module_info.name}",
                            fromlist=["_"])
        tree = ast.parse(pathlib.Path(inspect.getfile(module)).read_text())
        offenders = _imports(tree) & set(EGRESS_MODULES)
        assert not offenders, (
            f"review_surface.{module_info.name} imports {sorted(offenders)}")
    # And the check can fail.
    assert _imports(ast.parse("import urllib.request\n")) & set(EGRESS_MODULES)
    assert _imports(ast.parse("from requests import post\n")) & set(
        EGRESS_MODULES)
