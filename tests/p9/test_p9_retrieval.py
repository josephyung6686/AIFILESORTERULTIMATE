# tests/p9/test_p9_retrieval.py
"""P9 Task 6 — six retrieval channels, none of them authoritative.

Retrieval finds files that MAY supply context for one another. It decides nothing.
The two rules that make that true, and that this file exists to hold:

**A channel that retrieved a file never anchors it.** A duplicate link and a
download session both bring real neighbours, and neither is evidence that the
neighbour belongs: §3.9 says a bounded session is "not a basis for automatic
semantic propagation". Semantic retrieval is the same, harder — it is the channel
most likely to look like agreement.

**Mutual, not one-way.** A file whose vector is near the seed's proves nothing on
its own; a heavily-cited hub is near everything. Both directions are required.

Nothing here defaults. Missing limits, a missing similarity function, an
incomplete vector identity: all `ConfigurationRequired`. A missing compatibility
predicate OMITS its channel and says so, rather than treating every document type
as compatible — which is the failure that would quietly widen every group.
"""
from __future__ import annotations

import json

import pytest

from database_agent.budget import set_ceiling
from database_agent.db import create_schema
from database_agent.files_table import record_file
from database_agent.vector_versions import record_embedding
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from facts.fields import create_fields
from facts.file_facts import write_fact
from facts.read_surface import (
    DOWNLOAD_SESSION_FIELD,
    VERSION_FAMILY_FIELD,
)
from facts.values import ensure_value
from grouping.config import ConfigurationRequired, grouping_limits
from grouping.retrieval import (
    DEFAULT_CHANNEL_ORDER,
    EmbeddingIdentity,
    RetrievalKnowledge,
    retrieve_neighbors,
)
from grouping.seeds import Seed
from grouping.vocabulary import (
    BOUNDED_SESSION,
    COMPATIBLE_DOCUMENT_TYPE,
    DUPLICATE_OR_VERSION_LINK,
    EXISTING_RELATED_FOLDER,
    MUTUAL_SEMANTIC_RETRIEVAL,
    SHARED_VALIDATED_FACT,
    STRONGLY_IDENTIFIED_FILE,
)

OBSERVED_AT = "2026-08-26T00:00:00Z"
SCOPE = "extracted_text"
MODEL_ID = "fixture-encoder"
MODEL_VERSION = "1"

CEILINGS = {
    "grouping.max_retrieved_neighbors": 10,
    "grouping.max_local_graph_neighborhood": 60,
    "grouping.max_candidate_cluster_size": 25,
    "model.max_dossier_tokens_per_call": 4000,
}


@pytest.fixture()
def corpus(conn, tmp_path):
    create_schema(conn)
    create_evidence_schema(conn)
    create_fields(conn)
    for key, value in CEILINGS.items():
        set_ceiling(conn, key, value)
    return conn


def _file(conn, tmp_path, name: str, *, folder: str = "Coursework",
          scan_state: str = "included", detected_format: str = "pdf") -> str:
    path = tmp_path / folder / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(name.encode("utf-8"))
    return record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=len(name),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context=folder, mime_type="application/pdf",
        detected_format=detected_format, scan_state=scan_state,
        materialized=True,
    )


def _hash(conn, file_id: str) -> str:
    from database_agent.files_table import get_file

    return get_file(conn, file_id)["content_hash"]


def _observe(conn, file_id: str, content_hash: str, raw_value: str,
             run_id: str) -> str:
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="fixture.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=OBSERVED_AT, finished_at=OBSERVED_AT,
    ))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="fixture.text",
        extractor_version="1.0.0", source_type="text_document",
        raw_value=raw_value,
        location=Location(
            zone="heading", container_path=(Segment(kind="page", index=1),),
            text_span=TextSpan(start=0, end=len(raw_value)),
        ),
        occurrence_count=1, observed_at=OBSERVED_AT, reliability="direct",
        run_id=run_id,
    )
    record_observation(conn, observation)
    return observation.observation_key


def _fact(conn, file_id: str, *, field_key: str, value: str,
          reliability_state: str = "validated", run_id: str) -> str:
    content_hash = _hash(conn, file_id)
    key = _observe(conn, file_id, content_hash, value, run_id)
    value_id = ensure_value(
        conn, field_key=field_key, canonical_value=value,
        first_evidence_ref=key, origin="automatic",
    )
    write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key=field_key,
        value_id=value_id, reliability_state=reliability_state,
        origin="deterministic_extractor", evidence_refs=(key,),
        cache_key=f"sha256:{file_id}-{field_key}", active=True,
    )
    return key


def _vector(conn, file_id: str, payload: bytes) -> None:
    record_embedding(
        conn, file_id=file_id, content_hash=_hash(conn, file_id), scope=SCOPE,
        embedding_model_id=MODEL_ID, embedding_version=MODEL_VERSION,
        dimension=1, encoding="fixture-bytes", array_bytes=payload,
        created_at=OBSERVED_AT,
    )


def _seed(conn, file_id: str, *, field_key: str = "subject",
          value: str = "PHYS1401") -> Seed:
    return Seed(
        seed_kind=STRONGLY_IDENTIFIED_FILE,
        file_id=file_id,
        content_hash=_hash(conn, file_id),
        field_key=field_key,
        value=value,
        reliability_state="validated",
        observation_key="sha256:seed",
        basis=None,
    )


def _limits(conn):
    return grouping_limits(
        conn, generic_hub_frequency=25, minimum_independent_anchors=2,
        max_excerpt_characters=240,
    )


def _knowledge(**overrides) -> RetrievalKnowledge:
    values = dict(
        document_compatible=lambda domain, left, right: left == right,
        channel_weights={
            channel: len(DEFAULT_CHANNEL_ORDER) - index
            for index, channel in enumerate(DEFAULT_CHANNEL_ORDER)
        },
        similarity=None,
        similarity_threshold=None,
        embedding_identity=None,
        domain="academic",
    )
    values.update(overrides)
    return RetrievalKnowledge(**values)


def _retrieve(conn, seed, *, limits=..., knowledge=None, semantic=False):
    return retrieve_neighbors(
        conn,
        seed=seed,
        limits=_limits(conn) if limits is ... else limits,
        knowledge=knowledge if knowledge is not None else _knowledge(),
        embeddings_enabled=semantic,
    )


def _channels(result) -> set[str]:
    return {neighbour.channel for neighbour in result.neighbors}


def _files(result, channel: str) -> set[str]:
    return {n.file_id for n in result.neighbors if n.channel == channel}


# --- nothing defaults -----------------------------------------------------------


def test_missing_limits_is_configuration_required(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    with pytest.raises(ConfigurationRequired):
        _retrieve(corpus, _seed(corpus, seed_file), limits=None)


def test_semantic_retrieval_without_a_similarity_function_is_refused(
    corpus, tmp_path,
):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    with pytest.raises(ConfigurationRequired) as excinfo:
        _retrieve(
            corpus, _seed(corpus, seed_file), semantic=True,
            knowledge=_knowledge(
                embedding_identity=EmbeddingIdentity(
                    scope=SCOPE, model_id=MODEL_ID, model_version=MODEL_VERSION,
                ),
                similarity_threshold=0.5,
            ),
        )
    assert "similarity" in str(excinfo.value)


def test_semantic_retrieval_without_a_complete_vector_identity_is_refused(
    corpus, tmp_path,
):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    with pytest.raises(ConfigurationRequired) as excinfo:
        _retrieve(
            corpus, _seed(corpus, seed_file), semantic=True,
            knowledge=_knowledge(
                similarity=lambda a, b: 1.0, similarity_threshold=0.5,
                embedding_identity=None,
            ),
        )
    assert "embedding_identity" in str(excinfo.value)


def test_semantic_retrieval_without_a_threshold_is_refused(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    with pytest.raises(ConfigurationRequired):
        _retrieve(
            corpus, _seed(corpus, seed_file), semantic=True,
            knowledge=_knowledge(
                similarity=lambda a, b: 1.0,
                embedding_identity=EmbeddingIdentity(
                    scope=SCOPE, model_id=MODEL_ID, model_version=MODEL_VERSION,
                ),
                similarity_threshold=None,
            ),
        )


def test_a_missing_compatibility_predicate_omits_its_channel_and_says_so(
    corpus, tmp_path,
):
    """Treating every document type as compatible would widen every group."""
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    other = _file(corpus, tmp_path, "lecture.pdf")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-1")
    _fact(corpus, other, field_key="subject", value="PHYS1401", run_id="r-2")
    result = _retrieve(
        corpus, _seed(corpus, seed_file),
        knowledge=_knowledge(document_compatible=None),
    )
    assert COMPATIBLE_DOCUMENT_TYPE not in _channels(result)
    assert "missing_document_compatibility" in result.omissions


# --- the six channels -----------------------------------------------------------


def test_channel_one_retrieves_files_sharing_a_validated_fact(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    sharing = _file(corpus, tmp_path, "lecture.pdf")
    unrelated = _file(corpus, tmp_path, "taxes.pdf", folder="Finance")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-1")
    _fact(corpus, sharing, field_key="subject", value="PHYS1401", run_id="r-2")
    _fact(corpus, unrelated, field_key="subject", value="TAX2025", run_id="r-3")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    assert _files(result, SHARED_VALIDATED_FACT) == {sharing}


def test_channel_two_retrieves_a_version_family_including_possible_rows(
    corpus, tmp_path,
):
    """A `possible` family row is retrieval-only. It brings a file and anchors none."""
    seed_file = _file(corpus, tmp_path, "essay-v2.pdf")
    sibling = _file(corpus, tmp_path, "essay-v1.pdf")
    _fact(corpus, seed_file, field_key=VERSION_FAMILY_FIELD, value="family-1",
          reliability_state="possible", run_id="r-1")
    _fact(corpus, sibling, field_key=VERSION_FAMILY_FIELD, value="family-1",
          reliability_state="possible", run_id="r-2")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    assert sibling in _files(result, DUPLICATE_OR_VERSION_LINK)


def test_channel_three_uses_the_injected_compatibility_predicate(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf", detected_format="pdf")
    same_kind = _file(corpus, tmp_path, "lecture.pdf", detected_format="pdf")
    other_kind = _file(corpus, tmp_path, "photo.jpg", detected_format="jpeg")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    compatible = _files(result, COMPATIBLE_DOCUMENT_TYPE)
    assert same_kind in compatible
    assert other_kind not in compatible


def test_channel_four_retrieves_the_existing_related_folder(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf", folder="Coursework")
    same_folder = _file(corpus, tmp_path, "lecture.pdf", folder="Coursework")
    elsewhere = _file(corpus, tmp_path, "taxes.pdf", folder="Finance")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    folder_hits = _files(result, EXISTING_RELATED_FOLDER)
    assert same_folder in folder_hits
    assert elsewhere not in folder_hits


def test_channel_five_retrieves_a_bounded_session(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "download-a.pdf")
    together = _file(corpus, tmp_path, "download-b.pdf")
    _fact(corpus, seed_file, field_key=DOWNLOAD_SESSION_FIELD, value="session-1",
          reliability_state="possible", run_id="r-1")
    _fact(corpus, together, field_key=DOWNLOAD_SESSION_FIELD, value="session-1",
          reliability_state="possible", run_id="r-2")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    assert together in _files(result, BOUNDED_SESSION)


def test_channel_six_requires_similarity_in_both_directions(corpus, tmp_path):
    """A hub is near everything. One-way nearness is not mutual retrieval."""
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    mutual = _file(corpus, tmp_path, "lecture.pdf")
    one_way = _file(corpus, tmp_path, "hub.pdf")
    _vector(corpus, seed_file, b"seed")
    _vector(corpus, mutual, b"seed")
    _vector(corpus, one_way, b"hub")

    def similarity(left: bytes, right: bytes) -> float:
        # The seed looks near the hub, and the hub is not near the seed back.
        # Forward alone therefore ACCEPTS it; only the backward check excludes it,
        # which is the whole property under test.
        if left == b"seed" and right == b"hub":
            return 0.9
        if left == b"hub" and right == b"seed":
            return 0.1
        return 1.0 if left == right else 0.0

    result = _retrieve(
        corpus, _seed(corpus, seed_file), semantic=True,
        knowledge=_knowledge(
            similarity=similarity, similarity_threshold=0.5,
            embedding_identity=EmbeddingIdentity(
                scope=SCOPE, model_id=MODEL_ID, model_version=MODEL_VERSION,
            ),
        ),
    )
    semantic_hits = _files(result, MUTUAL_SEMANTIC_RETRIEVAL)
    assert mutual in semantic_hits
    assert one_way not in semantic_hits


def test_semantic_retrieval_is_absent_when_embeddings_are_off(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    other = _file(corpus, tmp_path, "lecture.pdf")
    _vector(corpus, seed_file, b"same")
    _vector(corpus, other, b"same")
    result = _retrieve(corpus, _seed(corpus, seed_file), semantic=False)
    assert MUTUAL_SEMANTIC_RETRIEVAL not in _channels(result)


# --- no channel anchors ---------------------------------------------------------


@pytest.mark.parametrize(
    ("field_key", "channel"),
    [
        (VERSION_FAMILY_FIELD, DUPLICATE_OR_VERSION_LINK),
        (DOWNLOAD_SESSION_FIELD, BOUNDED_SESSION),
    ],
)
def test_a_family_or_session_channel_never_sets_an_anchor_flag(
    corpus, tmp_path, field_key, channel,
):
    seed_file = _file(corpus, tmp_path, "a.pdf")
    other = _file(corpus, tmp_path, "b.pdf")
    _fact(corpus, seed_file, field_key=field_key, value="shared",
          reliability_state="possible", run_id="r-1")
    _fact(corpus, other, field_key=field_key, value="shared",
          reliability_state="possible", run_id="r-2")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    for neighbour in result.neighbors:
        if neighbour.channel == channel:
            assert neighbour.anchors is False


def test_a_semantic_neighbour_never_sets_an_anchor_flag(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    other = _file(corpus, tmp_path, "lecture.pdf")
    _vector(corpus, seed_file, b"same")
    _vector(corpus, other, b"same")
    result = _retrieve(
        corpus, _seed(corpus, seed_file), semantic=True,
        knowledge=_knowledge(
            similarity=lambda a, b: 1.0 if a == b else 0.0,
            similarity_threshold=0.5,
            embedding_identity=EmbeddingIdentity(
                scope=SCOPE, model_id=MODEL_ID, model_version=MODEL_VERSION,
            ),
        ),
    )
    for neighbour in result.neighbors:
        if neighbour.channel == MUTUAL_SEMANTIC_RETRIEVAL:
            assert neighbour.anchors is False


def test_only_a_shared_validated_fact_ever_anchors(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    sharing = _file(corpus, tmp_path, "lecture.pdf")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-1")
    _fact(corpus, sharing, field_key="subject", value="PHYS1401", run_id="r-2")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    anchoring = {n.channel for n in result.neighbors if n.anchors}
    assert anchoring <= {SHARED_VALIDATED_FACT}


def test_a_shared_fact_below_the_anchor_bar_retrieves_without_anchoring(
    corpus, tmp_path,
):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    sharing = _file(corpus, tmp_path, "guess.pdf")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-1")
    _fact(corpus, sharing, field_key="subject", value="PHYS1401",
          reliability_state="possible", run_id="r-2")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    for neighbour in result.neighbors:
        if neighbour.file_id == sharing and neighbour.channel == SHARED_VALIDATED_FACT:
            assert neighbour.anchors is False


# --- bounds and exclusions ------------------------------------------------------


def test_an_excluded_file_never_enters_the_neighbourhood(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    excluded = _file(corpus, tmp_path, "secret.pdf", scan_state="excluded")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-1")
    _fact(corpus, excluded, field_key="subject", value="PHYS1401", run_id="r-2")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    assert excluded not in {n.file_id for n in result.neighbors}


def test_the_seed_is_never_its_own_neighbour(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-1")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    assert seed_file not in {n.file_id for n in result.neighbors}


def test_the_neighbourhood_is_capped_and_the_drop_is_recorded(corpus, tmp_path):
    corpus.execute(
        "UPDATE budget_ceilings SET value = 2 WHERE key = ?",
        ("grouping.max_retrieved_neighbors",),
    )
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    for index in range(6):
        _file(corpus, tmp_path, f"lecture-{index}.pdf")
    result = _retrieve(corpus, _seed(corpus, seed_file))
    assert len(result.neighbors) <= 2
    assert result.capped is True
    assert "neighbourhood_cap" in result.omissions


def test_retrieval_is_deterministic(corpus, tmp_path):
    seed_file = _file(corpus, tmp_path, "syllabus.pdf")
    for index in range(4):
        other = _file(corpus, tmp_path, f"lecture-{index}.pdf")
        _fact(corpus, other, field_key="subject", value="PHYS1401",
              run_id=f"r-{index}")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-seed")
    first = _retrieve(corpus, _seed(corpus, seed_file))
    second = _retrieve(corpus, _seed(corpus, seed_file))
    assert [(n.file_id, n.channel) for n in first.neighbors] == [
        (n.file_id, n.channel) for n in second.neighbors
    ]


def test_retrieval_never_calls_an_encoder():
    """Task 5 owns encoding. Retrieval reads stored vectors and nothing else."""
    import ast
    import pathlib

    import grouping.retrieval as module

    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    names = {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    } | {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    for banned in ("encoder", "ensure_file_embedding", "recompute_file_embedding"):
        assert banned not in names, banned


def test_retrieval_reads_only_the_versioned_vector_store():
    import ast
    import pathlib

    import grouping.retrieval as module

    tree = ast.parse(pathlib.Path(module.__file__).read_text())
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "put_embedding" not in names
    assert "get_embedding" not in names


# --- a description is not an entity ---------------------------------------------


def test_only_the_folder_channel_publishes_a_bridge_entity(corpus, tmp_path):
    """`detail` describes why a channel returned a file; `bridge_entity` names the
    third thing the edge runs THROUGH. They were one field, and the graph read the
    description as an entity -- so `subject=PHYS1401`, the string every
    corroborating file carries, became a §4.3 hub and the suppression destroyed
    the group with the most evidence.

    A folder is a named thing that exists independently of the two files it joins,
    which is what makes `~/Downloads` bridging half the corpus the case §4.3 is
    about. The other five channels carry either the group's own basis or a
    description of the relation, and neither is an entity.
    """
    seed_file = _file(corpus, tmp_path, "syllabus.pdf", folder="Coursework")
    sharing = _file(corpus, tmp_path, "lecture.pdf", folder="Coursework")
    _fact(corpus, seed_file, field_key="subject", value="PHYS1401", run_id="r-1")
    _fact(corpus, sharing, field_key="subject", value="PHYS1401", run_id="r-2")
    _fact(corpus, seed_file, field_key=DOWNLOAD_SESSION_FIELD, value="session-1",
          reliability_state="possible", run_id="r-3")
    _fact(corpus, sharing, field_key=DOWNLOAD_SESSION_FIELD, value="session-1",
          reliability_state="possible", run_id="r-4")

    result = _retrieve(corpus, _seed(corpus, seed_file))
    with_entity = {
        neighbour.channel for neighbour in result.neighbors
        if neighbour.bridge_entity is not None
    }
    assert with_entity == {EXISTING_RELATED_FOLDER}, with_entity

    folder = next(n for n in result.neighbors if n.channel == EXISTING_RELATED_FOLDER)
    assert folder.bridge_entity == "Coursework"

    # The basis is never the hub: it is what the group IS, and counting how many
    # files state it is counting corroboration.
    anchor = next(n for n in result.neighbors if n.channel == SHARED_VALIDATED_FACT)
    assert anchor.detail == "subject=PHYS1401"
    assert anchor.bridge_entity is None
