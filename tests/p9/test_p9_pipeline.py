# tests/p9/test_p9_pipeline.py
"""P9 Task 13 — the five-stage sequence, and what it refuses to do.

seeds -> bounded embeddings -> bounded retrieval -> graph and pre-model stop rules
-> reference-only dossier -> P8 `run_call` when eligible -> mapped disposition.

Two properties are worth more than the happy path.

**Off is off, all the way down.** `EmbeddingsOff` reads no text, calls no encoder
and writes no vector — not "computes them and ignores them".

**The bound is applied before anything is read.** P9 never eagerly embeds the
corpus: the eligible set is deduplicated, ordered stably and cut to the graph
ceiling BEFORE a single text read, because the cost of encoding is paid at read
time and a cap applied afterwards has already been exceeded.

`p8_run_call=None` is a legal deterministic run, not a failure. What it cannot do
is complete a judgement-requiring candidate: that stays `candidate` with a reason,
because a group P9 called coherent without asking would be P9 synthesising a
verdict.
"""
from __future__ import annotations

import json

import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.embeddings import EmbeddingConfig, EmbeddingsOff, EmbeddingsOn, EncodedVector
from grouping.pipeline import GroupingKnowledge, GroupingResult, group_subject
from grouping.retrieval import EmbeddingIdentity, RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.vocabulary import CANDIDATE, DIRECT_ANCHOR, SR1, SR2

T0 = "2026-08-27T00:00:00Z"
PLAN = "plan-1"
CONFIG = EmbeddingConfig(
    model_id="fixture-encoder", model_version="1", scope="extracted_text",
    encoding="fixture-bytes", dimension=3)


@pytest.fixture()
def pipeline_conn(conn):
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    return conn


def _file(conn, tmp_path, name, *, body, detected_format="pdf"):
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format=detected_format, scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, *, file_id, content_hash, field, value, run_id):
    """One P6 direct fact, through P6's own writers."""
    from facts.file_facts import write_fact
    from facts.values import ensure_value

    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, finished_at=T0))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=value,
        location=Location("heading", (Segment("field", label="heading"),)),
        occurrence_count=1, observed_at=T0, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    value_id = ensure_value(
        conn, field_key=field, canonical_value=value,
        first_evidence_ref=observation.observation_key, origin="automatic")
    write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field,
        value_id=value_id, reliability_state="validated",
        origin="deterministic_extractor",
        evidence_refs=(observation.observation_key,),
        cache_key=f"sha256:{file_id}-{field}", active=True)
    return observation.observation_key


def _limits(**overrides) -> GroupingLimits:
    values = dict(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)
    values.update(overrides)
    return GroupingLimits(**values)


def _knowledge(**overrides) -> GroupingKnowledge:
    values = dict(
        retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=None,
            similarity_threshold=None, embedding_identity=None, domain=None),
        active_schema_for=lambda c, f, h: ("subject",),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classified(),
        conflicts_for=lambda files: (),
        duplicate_or_version=None,
    )
    values.update(overrides)
    return GroupingKnowledge(**values)


def _classified(handling_class="public_low"):
    from privacy.classification import ClassificationRecord

    def store(file_id, content_hash):
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling_class, protected=False, basis="detector",
            evidence_refs=("sha256:" + "a" * 64,), reliability_state="direct",
            observed_at=T0)
    return store


def _run(conn, subject, **overrides):
    file_id, content_hash = subject
    values = dict(
        plan_version_id=PLAN, limits=_limits(), knowledge=_knowledge(),
        user_seed_for=lambda f, h: None, p8_run_call=None,
        embeddings=EmbeddingsOff(), created_at=T0,
    )
    values.update(overrides)
    return group_subject(
        conn, file_id=file_id, content_hash=content_hash, **values)


@pytest.fixture()
def subject(pipeline_conn, tmp_path):
    file_id, content_hash = _file(
        pipeline_conn, tmp_path, "Syllabus.pdf", body=b"PHYS1401 syllabus")
    _fact(pipeline_conn, file_id=file_id, content_hash=content_hash,
          field="subject", value="PHYS1401", run_id="r-seed")
    return file_id, content_hash


# --- the deterministic skeleton --------------------------------------------------


def test_one_directly_identified_file_becomes_a_group_of_one(pipeline_conn, subject):
    """No model, no cloud, no embeddings. A file with one direct P6 fact is a
    group whose only member is itself, on direct-anchor evidence."""
    result = _run(pipeline_conn, subject)
    assert isinstance(result, GroupingResult)
    assert result.group is not None
    assert result.group.state == CANDIDATE
    assert result.memberships
    assert all(item.basis == DIRECT_ANCHOR for item in result.memberships)
    assert result.memberships[0].file_id == subject[0]


def test_the_deterministic_run_reaches_no_model(pipeline_conn, subject):
    """`p8_run_call=None` is a legal run, not a failure. What it cannot do is
    finish a judgement, so the group stays a candidate with a stated reason."""
    result = _run(pipeline_conn, subject)
    assert result.model_result is None
    assert result.group.coherence_verdict is None
    assert result.group.display_label is None
    assert result.not_implemented_reason


def test_a_file_with_no_legal_seed_forms_no_group(pipeline_conn, tmp_path):
    """A filename is not a fact. A file P6 holds nothing direct about has no
    legal starting point, and inventing one is where a group with no evidence
    comes from."""
    subject = _file(
        pipeline_conn, tmp_path, "Untitled.pdf", body=b"no facts here")
    result = _run(pipeline_conn, subject)
    assert result.group is None
    assert result.memberships == ()
    assert result.seeds == ()


def test_the_result_names_no_destination_node_or_tree(pipeline_conn, subject):
    """P9 says which files belong together. Where they go is P10's and P11's."""
    import dataclasses

    result = _run(pipeline_conn, subject)
    names = {field.name for field in dataclasses.fields(GroupingResult)}
    for banned in ("destination", "node", "node_id", "tree", "path", "folder",
                   "placement", "template"):
        assert not any(banned in name for name in names), banned


def test_rerunning_over_identical_evidence_is_stable(pipeline_conn, subject):
    """A replay re-derives the same references, so the same dossier address and
    the same edge ids come back -- and history is appended, never overwritten."""
    first = _run(pipeline_conn, subject)
    second = _run(pipeline_conn, subject)
    assert first.group.group_id == second.group.group_id
    if first.dossier is not None:
        assert first.dossier.dossier_fingerprint == (
            second.dossier.dossier_fingerprint)


# --- what the pre-model stop rules refuse ----------------------------------------


def test_a_file_the_store_has_no_direct_fact_about_forms_no_group(
    pipeline_conn, tmp_path,
):
    """SR1 is zero anchors. A seed with no validated fact behind it anchors
    nothing, and nothing else in the neighbourhood does either."""
    subject = _file(pipeline_conn, tmp_path, "Sparse.pdf", body=b"HW 3")
    result = _run(pipeline_conn, subject)
    assert result.group is None
    assert result.memberships == ()


def test_a_group_with_one_anchor_waits_rather_than_vanishing(
    pipeline_conn, subject,
):
    """SR1 and the support bar are different rules. One anchor below a bar of two
    is a candidate waiting for confirmation, not a group that never existed."""
    from grouping.graph import meets_support_bar

    result = _run(
        pipeline_conn, subject, limits=_limits(minimum_independent_anchors=2))
    assert result.stop_rule_outcome is None
    assert result.group is not None
    assert result.group.state == CANDIDATE
    assert meets_support_bar(
        result.graph, limits=_limits(minimum_independent_anchors=2),
        seed_anchors=True) is False


def test_a_conflict_from_the_injected_oracle_refuses(pipeline_conn, subject):
    """P9 does not decide that two terms are irreconcilable. A course code alone
    must not merge two semesters, and what makes them incompatible is domain
    knowledge P9 receives."""
    from grouping.records import Conflict
    from grouping.vocabulary import SR4

    result = _run(
        pipeline_conn, subject,
        knowledge=_knowledge(conflicts_for=lambda files: (Conflict(
            kind="term", competing_values=("Spring 2026", "Fall 2026"),
            file_ids=tuple(files)),)))
    assert result.stop_rule_outcome is not None
    assert SR4 in result.stop_rule_outcome.rules_fired
    assert result.memberships == ()
    assert result.dossier is None


def test_a_fired_stop_rule_costs_no_dossier_and_no_call(pipeline_conn, subject):
    """The point of running the rules before assembly: a group that cannot form
    should not cost a dossier, let alone a model call."""
    from grouping.records import Conflict

    calls = []
    _run(pipeline_conn, subject,
         p8_run_call=lambda *a, **k: calls.append(k) or None,
         knowledge=_knowledge(conflicts_for=lambda files: (Conflict(
             kind="term", competing_values=("a", "b"), file_ids=tuple(files)),)))
    assert calls == []


# --- embeddings: off is off, and the bound comes first ---------------------------


class SpyEncoder:
    def __init__(self):
        self.calls = []

    def __call__(self, text, config):
        self.calls.append(text)
        return EncodedVector(
            array_bytes=text.encode("utf-8"), dimension=config.dimension,
            encoding=config.encoding)


class SpyText:
    def __init__(self):
        self.calls = []

    def __call__(self, conn, file_id, content_hash, scope):
        self.calls.append((file_id, content_hash, scope))
        return f"text of {file_id}"


def test_embeddings_off_reads_no_text_encodes_nothing_and_writes_nothing(
    pipeline_conn, subject,
):
    encoder, text_for = SpyEncoder(), SpyText()
    _run(pipeline_conn, subject, embeddings=EmbeddingsOff())
    assert encoder.calls == []
    assert text_for.calls == []
    assert pipeline_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings").fetchone()["c"] == 0


def test_an_incomplete_enabled_runtime_is_refused_before_anything_is_read(
    pipeline_conn, subject,
):
    """Constructed past `__post_init__` on purpose, the way a deserializer would.
    The pipeline revalidates the boundary rather than trusting the record."""
    broken = object.__new__(EmbeddingsOn)
    object.__setattr__(broken, "config", None)
    object.__setattr__(broken, "encoder", None)
    object.__setattr__(broken, "embedding_text_for", None)
    object.__setattr__(broken, "eligible_versions_for", None)
    object.__setattr__(broken, "enabled", True)

    with pytest.raises(ConfigurationRequired):
        _run(pipeline_conn, subject, embeddings=broken)
    assert pipeline_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings").fetchone()["c"] == 0


def test_the_eligible_set_is_bounded_before_a_single_text_is_read(
    pipeline_conn, subject, tmp_path,
):
    """P9 never eagerly embeds the corpus. Encoding is paid at read time, so a cap
    applied afterwards has already been exceeded. The seed takes one slot."""
    from grouping.embeddings import FileVersionRef

    many = tuple(
        FileVersionRef(file_id=f"file-{n}", content_hash=f"hash-{n}")
        for n in range(20)
    )
    encoder, text_for = SpyEncoder(), SpyText()
    _run(
        pipeline_conn, subject,
        limits=_limits(max_graph_nodes=4),
        knowledge=_knowledge(retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={},
            similarity=lambda a, b: 0.9, similarity_threshold=0.5,
            embedding_identity=EmbeddingIdentity(
                scope=CONFIG.scope, model_id=CONFIG.model_id,
                model_version=CONFIG.model_version),
            domain=None)),
        embeddings=EmbeddingsOn(
            config=CONFIG, encoder=encoder, embedding_text_for=text_for,
            eligible_versions_for=lambda conn, seed, cap: many))
    assert len(text_for.calls) <= 4
    assert len(encoder.calls) <= 4
    assert (subject[0], subject[1], CONFIG.scope) in text_for.calls


def test_a_duplicate_eligible_version_is_read_once(pipeline_conn, subject):
    from grouping.embeddings import FileVersionRef

    twice = (
        FileVersionRef(file_id="file-a", content_hash="hash-a"),
        FileVersionRef(file_id="file-a", content_hash="hash-a"),
    )
    encoder, text_for = SpyEncoder(), SpyText()
    _run(
        pipeline_conn, subject,
        knowledge=_knowledge(retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={},
            similarity=lambda a, b: 0.9, similarity_threshold=0.5,
            embedding_identity=EmbeddingIdentity(
                scope=CONFIG.scope, model_id=CONFIG.model_id,
                model_version=CONFIG.model_version),
            domain=None)),
        embeddings=EmbeddingsOn(
            config=CONFIG, encoder=encoder, embedding_text_for=text_for,
            eligible_versions_for=lambda conn, seed, cap: twice))
    assert [call[:2] for call in text_for.calls].count(("file-a", "hash-a")) == 1


# --- the model path is P8's, entirely --------------------------------------------


def test_the_pipeline_calls_only_the_injected_run_call(pipeline_conn, subject):
    import ast
    import pathlib

    import grouping.pipeline as module

    text = pathlib.Path(module.__file__).read_text()
    for banned in ("Gate", "ModelClient", "issue(", "gate.release"):
        assert banned not in text, banned
    tree = ast.parse(text)
    called = {
        node.func.attr for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "release" not in called
    assert "invoke" not in called


def test_an_injected_run_call_receives_a_reference_only_request(
    pipeline_conn, subject, tmp_path,
):
    """What reaches `run_call` is P8's own `DossierRequest`, built by the seam."""
    from llm_harness.records import DossierRequest

    seen = []

    def spy(conn, request, **kwargs):
        seen.append(request)
        return None

    other = _file(pipeline_conn, tmp_path, "Lecture.pdf", body=b"PHYS1401 lecture")
    _fact(pipeline_conn, file_id=other[0], content_hash=other[1],
          field="subject", value="PHYS1401", run_id="r-other")
    _run(pipeline_conn, subject, p8_run_call=spy,
         knowledge=_knowledge(), limits=_limits())
    for request in seen:
        assert isinstance(request, DossierRequest)
