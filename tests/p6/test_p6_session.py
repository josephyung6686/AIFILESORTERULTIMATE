"""G6 — Done-means 25. §3.9's bounded download session, pinned at `possible`."""
from __future__ import annotations

import dataclasses
import inspect
import json
from pathlib import Path

import pytest

from database_agent.files_table import get_file, record_file

from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run

from facts import session
from facts.fields import get_field
from facts.file_facts import FACT_ORIGINS, facts_for_file, write_fact, RULE
from facts.session import (
    DOWNLOAD_SESSION_FIELD, SESSION_STATE, SessionBoundary, SessionNeverPromoted,
    bounded_sessions, require_possible,
)
from facts.unresolved import unresolved_for_file
from facts.values import VALUE_ORIGINS, ensure_value

CLOCK = "2026-08-19T12:00:00+00:00"

#: Every number below is the TEST's, injected. §3.9 requires the clue and states no
#: numbers, so the module holds none.
TIGHT = SessionBoundary(window_seconds=120.0,
                        require_same_parent_folder_context=True,
                        minimum_members=2)


def _download(conn, tmp_path, *, name, body, mtime, parent="Downloads",
              with_path_observation=True, run_id=None):
    path = tmp_path / parent / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=Path(name).suffix, observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": mtime}),
        parent_folder_context=parent, mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(conn, file_id)["content_hash"]
    run_id = run_id or f"run-{name}"
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="filesystem.record", extractor_version="0.1.0",
        source_type="filesystem", analysis_tier="filesystem", config={},
        completeness="complete", started_at=CLOCK, finished_at=CLOCK))
    key = None
    if with_path_observation:
        # P5's `filesystem.py` emits §2.9's parent-folder context at zone `path`.
        observation = Observation(
            file_id=file_id, content_hash=content_hash,
            extractor_name="filesystem.record", extractor_version="0.1.0",
            source_type="filesystem", raw_value=parent,
            location=Location("path"), occurrence_count=1, observed_at=CLOCK,
            reliability="possible", run_id=run_id)
        record_observation(conn, observation)
        key = observation.observation_key
    return file_id, content_hash, key


def _session_rows(conn, file_id, content_hash):
    return [r for r in facts_for_file(conn, file_id, content_hash)
            if r["field_key"] == DOWNLOAD_SESSION_FIELD]


@pytest.fixture()
def one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="transcript.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    right = _download(p6_conn, tmp_path, name="resume.pdf", body=b"two",
                      mtime=1_700_000_060.0)
    return left, right


def test_a_session_derived_fact_is_possible(one_session, p6_conn):
    # Done-means 25, and §3.13's "a possible fact is a useful but insufficient clue,
    # such as membership in a short download session".
    (left, left_hash, _), (right, right_hash, _) = one_session
    written = bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    assert set(written) == {left, right}
    for file_id, digest in ((left, left_hash), (right, right_hash)):
        rows = _session_rows(p6_conn, file_id, digest)
        assert len(rows) == 1
        assert rows[0]["reliability_state"] == "possible"
    assert SESSION_STATE == "possible"


def test_no_code_path_can_write_the_session_field_at_another_state():
    # §3.9: it "should not carry the same confidence as a hash match or a directly
    # extracted document fact". Attempted, not inspected.
    assert require_possible("possible") == "possible"
    for state in ("validated", "direct", "llm_supported", "user_confirmed"):
        with pytest.raises(SessionNeverPromoted):
            require_possible(state)


def test_a_session_fact_is_absent_from_the_proposal_eligible_read(one_session, p6_conn):
    # §3.6 excludes `possible`, so the exclusion is the state and not a second rule.
    (left, left_hash, _), (right, _, _) = one_session
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    read_surface = pytest.importorskip("facts.read_surface")
    eligible = read_surface.proposal_eligible(p6_conn, file_id=left,
                                              content_hash=left_hash)
    assert [r["field_key"] for r in eligible] == []


def test_the_download_session_field_is_never_destination_eligible(p6_conn):
    # §3.9 makes it a purpose clue and a review aid; a folder level built from one
    # would put the download window into the tree.
    row = get_field(p6_conn, DOWNLOAD_SESSION_FIELD)
    assert row["scope"] == "universal"
    assert not row["destination_eligible"]


def test_the_session_fact_is_written_for_the_member_file_only(one_session, p6_conn):
    # §3.9: "not a basis for automatic semantic propagation"; §4.1: the graph "does
    # not automatically copy those missing facts onto sparse files".
    (left, left_hash, left_key), (right, right_hash, _) = one_session
    value_id = ensure_value(p6_conn, field_key="subject",
                            canonical_value="BUSIB 4300",
                            first_evidence_ref=left_key, origin=VALUE_ORIGINS[0])
    write_fact(p6_conn, file_id=left, content_hash=left_hash, field_key="subject",
               value_id=value_id, reliability_state="validated",
               origin=RULE, evidence_refs=(left_key,),
               cache_key="sha256:cache", active=True)
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    right_fields = {r["field_key"]
                    for r in facts_for_file(p6_conn, right, right_hash)}
    assert right_fields == {DOWNLOAD_SESSION_FIELD}


def test_the_boundary_is_injected_and_the_module_states_no_window():
    # §3.9 requires the clue and states no numbers, so none is here.
    fields = dataclasses.fields(SessionBoundary)
    assert [f.name for f in fields] == ["window_seconds",
                                        "require_same_parent_folder_context",
                                        "minimum_members"]
    for field in fields:
        assert field.default is dataclasses.MISSING
        assert field.default_factory is dataclasses.MISSING
    parameter = inspect.signature(bounded_sessions).parameters["boundary"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty
    # Task 25's technique: runtime introspection of the namespace, not a text search.
    numbers = {name: value for name, value in vars(session).items()
               if isinstance(value, (int, float)) and not isinstance(value, bool)}
    assert numbers == {}


def test_files_outside_the_window_are_not_one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_009_999.0)
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    assert _session_rows(p6_conn, left[0], left[1]) == []
    assert _session_rows(p6_conn, right[0], right[1]) == []


def test_a_session_below_the_minimum_is_not_a_session(p6_conn, tmp_path):
    # "Tightly bounded" is the caller's definition, including how many files make one.
    only = _download(p6_conn, tmp_path, name="alone.pdf", body=b"one",
                     mtime=1_700_000_000.0)
    assert bounded_sessions(p6_conn, file_ids=(only[0],), boundary=TIGHT) == {}
    assert _session_rows(p6_conn, only[0], only[1]) == []
    # Silence, not a refusal: a window that contained one file was never a proposal.
    assert unresolved_for_file(p6_conn, only[0], only[1]) == []


def test_a_member_with_no_citable_parent_folder_observation_abstains(
        p6_conn, tmp_path):
    # Rule 1: an uninspectable clue is not a clue. P5 writes no timestamp
    # observation, so a member with no `path` observation has nothing to cite.
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0, with_path_observation=False)
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_000_060.0, with_path_observation=False)
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    for file_id, digest, _ in (left, right):
        rows = unresolved_for_file(p6_conn, file_id, digest,
                                   field_key=DOWNLOAD_SESSION_FIELD)
        assert [r["reason"] for r in rows] == ["no_candidate_evidence"]


def test_the_session_value_is_deterministic_and_carries_no_path(one_session, p6_conn):
    (left, left_hash, _), (right, right_hash, _) = one_session
    bounded_sessions(p6_conn, file_ids=(left, right), boundary=TIGHT)
    values = {_session_rows(p6_conn, file_id, digest)[0]["canonical_value"]
              for file_id, digest in ((left, left_hash), (right, right_hash))}
    assert len(values) == 1
    value = values.pop()
    assert value.startswith("sha256:")
    assert "Downloads" not in value


def test_different_parent_folder_contexts_are_not_one_session(p6_conn, tmp_path):
    left = _download(p6_conn, tmp_path, name="a.pdf", body=b"one",
                     mtime=1_700_000_000.0, parent="Downloads")
    right = _download(p6_conn, tmp_path, name="b.pdf", body=b"two",
                      mtime=1_700_000_060.0, parent="Desktop")
    assert bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                            boundary=TIGHT) == {}
    relaxed = SessionBoundary(window_seconds=120.0,
                              require_same_parent_folder_context=False,
                              minimum_members=2)
    assert set(bounded_sessions(p6_conn, file_ids=(left[0], right[0]),
                                boundary=relaxed)) == {left[0], right[0]}
