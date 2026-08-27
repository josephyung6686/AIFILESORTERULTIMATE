# tests/integration/test_p9_walking_skeleton.py
"""P9's deterministic walking skeleton: P1 -> P4 -> P6 -> P9, no model, no vectors.

One real file, one real extraction run, one real P4 observation, one real P6
direct fact, and out the other end a group whose only member is that file on
direct-anchor evidence. Every part is the live one; nothing here is a fixture
standing in for a neighbour.

The point of the skeleton is what it proves about the SHAPE of the product: the
deterministic path is a complete path. A user with no cloud model and no
embeddings gets real groups, and the model is an escalation rather than the
engine.

What P9 hands P10 is published as a fixture so P10 can freeze from it, and the
last test in this file is the one that says the result names no destination.
"""
from __future__ import annotations

from dataclasses import replace

import json

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from facts.file_facts import facts_for_file, write_fact
from facts.read_surface import proposal_eligible
from facts.values import ensure_value
from grouping.config import GroupingLimits
from grouping.embeddings import EmbeddingsOff
from grouping.pipeline import NO_MODEL_CONFIGURED, GroupingKnowledge, group_subject
from grouping.retrieval import RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.store import current_group, memberships_for_group
from grouping.graph import meets_support_bar
from grouping.vocabulary import (
    CANDIDATE,
    DIRECT_ANCHOR,
    INCLUDED,
    RULES,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
    SUPPORTED,
)
from privacy.classification import ClassificationRecord

T0 = "2026-08-27T00:00:00Z"
PLAN = "plan-1"
COURSE = "PHYS1401"


@pytest.fixture()
def skeleton_conn(conn):
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    return conn


def _classified(file_id, content_hash):
    return ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class="public_low",
        protected=False, basis="detector",
        evidence_refs=("sha256:" + "a" * 64,), reliability_state="direct",
        observed_at=T0)


def _knowledge() -> GroupingKnowledge:
    return GroupingKnowledge(
        retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=None,
            similarity_threshold=None, embedding_identity=None, domain=None),
        active_schema_for=lambda c, f, h: ("subject",),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classified,
        conflicts_for=lambda files: (),
        duplicate_or_version=None,
    )


def _limits() -> GroupingLimits:
    return GroupingLimits(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)


@pytest.fixture()
def one_identified_file(skeleton_conn, tmp_path):
    """P1 records the file, P4 records what was seen, P6 concludes a direct fact."""
    body = f"{COURSE} Syllabus, Spring 2026".encode("utf-8")
    path = tmp_path / "Syllabus.pdf"
    path.write_bytes(body)
    file_id = record_file(
        skeleton_conn, path, filename="Syllabus.pdf",
        normalized_filename="syllabus.pdf", extension=".pdf",
        observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    content_hash = get_file(skeleton_conn, file_id)["content_hash"]

    record_run(skeleton_conn, ExtractionRun(
        run_id="r-1", file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, finished_at=T0))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=COURSE,
        location=Location(
            zone="heading", container_path=(Segment(kind="page", index=1),),
            text_span=TextSpan(start=0, end=len(COURSE))),
        occurrence_count=1, observed_at=T0, reliability="direct", run_id="r-1")
    record_observation(skeleton_conn, observation)

    value_id = ensure_value(
        skeleton_conn, field_key="subject", canonical_value=COURSE,
        first_evidence_ref=observation.observation_key, origin="automatic")
    write_fact(
        skeleton_conn, file_id=file_id, content_hash=content_hash,
        field_key="subject", value_id=value_id, reliability_state="validated",
        origin="deterministic_extractor",
        evidence_refs=(observation.observation_key,),
        cache_key=f"sha256:{file_id}-subject", active=True)
    return file_id, content_hash, observation.observation_key


def _walk(conn, subject, **overrides):
    file_id, content_hash, _key = subject
    values = dict(
        plan_version_id=PLAN, limits=_limits(), knowledge=_knowledge(),
        user_seed_for=lambda f, h: None, p8_run_call=None, p8_authorities=None,
        embeddings=EmbeddingsOff(), created_at=T0)
    values.update(overrides)
    return group_subject(
        conn, file_id=file_id, content_hash=content_hash, **values)


def test_one_walk_goes_p1_to_p4_to_p6_to_p9_with_no_model_and_no_vectors(
    skeleton_conn, one_identified_file,
):
    file_id, content_hash, key = one_identified_file

    # P6 holds the fact, resting on P4's observation, resting on P1's file.
    facts = facts_for_file(skeleton_conn, file_id, content_hash)
    assert [row["field_key"] for row in facts] == ["subject"]
    assert proposal_eligible(
        skeleton_conn, file_id=file_id, content_hash=content_hash)

    result = _walk(skeleton_conn, one_identified_file)

    # P9's seed came from P6, not from the filename.
    assert [seed.seed_kind for seed in result.seeds] == [STRONGLY_IDENTIFIED_FILE]
    assert result.seeds[0].observation_key == key

    # A group of one, on its own direct evidence.
    assert result.group is not None
    # `supported`, not `candidate`: this walk injects
    # `minimum_independent_anchors=1` and the seed's own validated fact is one
    # independent anchor, so SS4.9's bar is met. The assertion read `CANDIDATE`
    # while `_group_for` hardcoded that state and no caller consulted
    # `meets_support_bar`; a constant that could not be wrong proved nothing about
    # the bar. The next two lines are what make this a check rather than a flip:
    # this same graph under a bar of two does not meet it. (Asserted through the
    # bar rather than through a second walk: the group store is append-only and
    # refuses to re-record one group id with a different state.)
    assert result.group.state == SUPPORTED
    assert meets_support_bar(
        result.graph, limits=_limits(), seed_anchors=True) is True
    assert meets_support_bar(
        result.graph,
        limits=replace(_limits(), minimum_independent_anchors=2),
        seed_anchors=True) is False
    assert result.group.created_by == RULES
    assert result.group.proposed_basis == f"subject={COURSE}"
    membership = result.memberships[0]
    assert membership.basis == DIRECT_ANCHOR
    assert membership.decision == INCLUDED
    assert membership.decision_source == RULES
    assert membership.support[0].support_kind == SHARED_VALIDATED_FACT
    assert membership.support[0].observation_key == key

    # And it is on disk, through P9's own writers.
    assert current_group(skeleton_conn, result.group.group_id) == result.group
    assert memberships_for_group(skeleton_conn, result.group.group_id) == (
        membership,)

    # Nothing was released, nothing was called, nothing was embedded.
    assert result.model_result is None
    assert result.not_implemented_reason == NO_MODEL_CONFIGURED
    assert skeleton_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings").fetchone()["c"] == 0


def test_the_deterministic_path_is_a_complete_path(skeleton_conn, one_identified_file):
    """A user with no cloud model and no embeddings gets real groups. The model is
    an escalation, and this is the test that says so."""
    result = _walk(skeleton_conn, one_identified_file)
    assert result.group is not None
    assert result.memberships
    assert result.dossier is not None
    assert result.stop_rule_outcome is None


def test_the_dossier_p9_hands_on_is_reference_only(skeleton_conn, one_identified_file):
    _file_id, _hash, key = one_identified_file
    result = _walk(skeleton_conn, one_identified_file)
    dossier = result.dossier
    assert [item.observation_key for item in dossier.excerpts] == [key]
    assert dossier.anchor_files
    assert dossier.candidate_files == ()
    assert dossier.privacy.handling_classes == ("public_low",)
    assert dossier.omissions.privacy_redacted == ()


def test_the_walk_names_no_destination_node_tree_or_placement(
    skeleton_conn, one_identified_file,
):
    """P9 says which files belong together. Where they go is P10's and P11's, and
    a P9 field carrying one would be P9 deciding it."""
    import dataclasses

    result = _walk(skeleton_conn, one_identified_file)
    seen: set[str] = set()

    def walk(value, depth=0):
        if depth > 4 or not dataclasses.is_dataclass(value):
            return
        for item in dataclasses.fields(value):
            seen.add(item.name)
            walk(getattr(value, item.name), depth + 1)

    walk(result)
    walk(result.group)
    walk(result.memberships[0])
    walk(result.dossier)
    for banned in ("destination", "node", "tree", "folder", "placement",
                   "template", "path"):
        assert not any(banned in name for name in seen), (banned, sorted(seen))


def test_a_rerun_over_unchanged_evidence_appends_nothing(
    skeleton_conn, one_identified_file,
):
    """A replay re-derives the same references. Two runs are one group, one
    membership and one dossier address -- history is appended, never rewritten."""
    first = _walk(skeleton_conn, one_identified_file)
    second = _walk(skeleton_conn, one_identified_file)
    assert first.group.group_id == second.group.group_id
    assert first.dossier.dossier_fingerprint == second.dossier.dossier_fingerprint
    assert skeleton_conn.execute(
        "SELECT count(*) AS c FROM groups").fetchone()["c"] == 1
    assert skeleton_conn.execute(
        "SELECT count(*) AS c FROM memberships").fetchone()["c"] == 1
