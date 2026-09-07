# tests/integration/test_p9_embedding_pipeline.py
"""P9 Task 13 — the live embedding path, with real P1 storage in the middle.

The claim under test is about the SHAPE of the path, not about similarity:

    encoder -> versioned P1 record -> P1 read -> mutual semantic retrieval

Retrieval receives no encoder output. A vector that was never stored cannot
become a neighbour by shortcut, and the test that proves it deletes the stored
rows between encoding and retrieval and watches the semantic channel go quiet.

Mutual means both directions. A hub whose vector is near everything is near
nothing in particular, and a one-directional check would let it into every
neighbourhood in the corpus.
"""
from __future__ import annotations

import json

import pathlib
import pytest

from database_agent.db import create_schema
from database_agent.files_table import get_file, record_file
from database_agent.vector_versions import current_embedding
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from facts.file_facts import write_fact
from facts.values import ensure_value
from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.embeddings import (
    EmbeddingConfig,
    EmbeddingsOff,
    EmbeddingsOn,
    EncodedVector,
    FileVersionRef,
)
from grouping.pipeline import GroupingKnowledge, group_subject
from grouping.vocabulary import MUTUAL_SEMANTIC_RETRIEVAL, SHARED_VALIDATED_FACT
from grouping.retrieval import EmbeddingIdentity, RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.vocabulary import MUTUAL_SEMANTIC_RETRIEVAL
from privacy.classification import ClassificationRecord

T0 = "2026-08-27T00:00:00Z"
PLAN = "plan-1"
CONFIG = EmbeddingConfig(
    model_id="fixture-encoder", model_version="1", scope="extracted_text",
    encoding="fixture-bytes", dimension=3)
IDENTITY = dict(
    scope=CONFIG.scope, embedding_model_id=CONFIG.model_id,
    embedding_version=CONFIG.model_version)


@pytest.fixture()
def embed_conn(conn):
    from facts.fields import create_fields

    create_schema(conn)
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_fields(conn)
    return conn


def _file(conn, tmp_path, name, *, body):
    path = tmp_path / name
    path.write_bytes(body)
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=len(body),
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, *, file_id, content_hash, value, run_id):
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, finished_at=T0))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=value,
        location=Location(
            zone="heading", container_path=(Segment(kind="page", index=1),),
            text_span=TextSpan(start=0, end=len(value))),
        occurrence_count=1, observed_at=T0, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    value_id = ensure_value(
        conn, field_key="subject", canonical_value=value,
        first_evidence_ref=observation.observation_key, origin="automatic")
    write_fact(
        conn, file_id=file_id, content_hash=content_hash, field_key="subject",
        value_id=value_id, reliability_state="validated",
        origin="deterministic_extractor",
        evidence_refs=(observation.observation_key,),
        cache_key=f"sha256:{file_id}-subject", active=True)
    return observation.observation_key


class SpyEncoder:
    def __init__(self):
        self.calls: list[str] = []

    def __call__(self, text, config):
        self.calls.append(text)
        return EncodedVector(
            array_bytes=text.encode("utf-8"), dimension=config.dimension,
            encoding=config.encoding)


class BoundedText:
    """The configured scope, and only it. P9 defines no default scope."""

    def __init__(self):
        self.calls: list[tuple[str, str, str]] = []

    def __call__(self, conn, file_id, content_hash, scope):
        self.calls.append((file_id, content_hash, scope))
        return f"the {scope} of {file_id}"


def _mutual(anchor_id: str, sparse_id: str):
    """Near in both directions, and only between these two.

    Forward and backward are computed from the stored bytes, so a check that
    only looked one way would still pass here -- the one-directional test lives
    in `tests/p9/test_p9_retrieval.py`, where the fixture is asymmetric.
    """
    def similarity(left: bytes, right: bytes) -> float:
        pair = {left, right}
        return 0.9 if len(pair) == 2 else 1.0
    return similarity


def _classified(file_id, content_hash):
    return ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class="public_low",
        protected=False, basis="detector",
        evidence_refs=("sha256:" + "a" * 64,), reliability_state="direct",
        observed_at=T0)


def _limits(**overrides) -> GroupingLimits:
    values = dict(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)
    values.update(overrides)
    return GroupingLimits(**values)


def _knowledge(similarity, **overrides) -> GroupingKnowledge:
    values = dict(
        retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=similarity,
            similarity_threshold=0.5,
            embedding_identity=EmbeddingIdentity(
                scope=CONFIG.scope, model_id=CONFIG.model_id,
                model_version=CONFIG.model_version),
            domain=None),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classified,
        conflicts_for=lambda files: (),
        duplicate_or_version=None,
    )
    values.update(overrides)
    return GroupingKnowledge(**values)


@pytest.fixture()
def corpus(embed_conn, tmp_path):
    anchor = _file(embed_conn, tmp_path, "Syllabus.pdf", body=b"PHYS1401")
    _fact(embed_conn, file_id=anchor[0], content_hash=anchor[1],
          value="PHYS1401", run_id="r-anchor")
    sparse = _file(embed_conn, tmp_path, "HW3.pdf", body=b"homework three")
    return anchor, sparse


def _run(conn, anchor, *, embeddings, knowledge, limits=None):
    return group_subject(
        conn, file_id=anchor[0], content_hash=anchor[1], plan_version_id=PLAN,
        limits=limits or _limits(), knowledge=knowledge,
        user_seed_for=lambda f, h: None, p8_run_call=None, p8_authorities=None,
        embeddings=embeddings, created_at=T0)


def _on(encoder, text_for, eligible):
    return EmbeddingsOn(
        config=CONFIG, encoder=encoder, embedding_text_for=text_for,
        eligible_versions_for=lambda conn, seed, cap: eligible)


# --- the path: encoder -> P1 -> P1 read -> retrieval -----------------------------


def test_the_encoder_writes_versioned_p1_records_for_the_bounded_set(
    embed_conn, corpus,
):
    anchor, sparse = corpus
    encoder, text_for = SpyEncoder(), BoundedText()
    _run(embed_conn, anchor,
         embeddings=_on(encoder, text_for, (
             FileVersionRef(file_id=sparse[0], content_hash=sparse[1]),)),
         knowledge=_knowledge(_mutual(anchor[0], sparse[0])))

    assert len(encoder.calls) == 2
    assert current_embedding(
        embed_conn, file_id=anchor[0], content_hash=anchor[1], **IDENTITY)
    assert current_embedding(
        embed_conn, file_id=sparse[0], content_hash=sparse[1], **IDENTITY)


def test_the_semantic_edge_comes_from_the_stored_vector_not_the_encoder(
    embed_conn, corpus,
):
    """The whole shape of the path in one test. Encoding happens, the rows are
    then removed, and the semantic channel goes quiet -- so retrieval was reading
    P1 rather than holding onto what the encoder returned."""
    anchor, sparse = corpus
    eligible = (FileVersionRef(file_id=sparse[0], content_hash=sparse[1]),)
    similarity = _mutual(anchor[0], sparse[0])

    with_vectors = _run(
        embed_conn, anchor, embeddings=_on(SpyEncoder(), BoundedText(), eligible),
        knowledge=_knowledge(similarity))
    semantic = [
        edge for edge in with_vectors.graph.edges
        if edge.edge_type == MUTUAL_SEMANTIC_RETRIEVAL
    ]
    assert semantic
    assert {edge.to_file_id for edge in semantic} == {sparse[0]}

    embed_conn.execute("DELETE FROM vector_embeddings")
    without = group_subject(
        embed_conn, file_id=anchor[0], content_hash=anchor[1],
        plan_version_id=PLAN, limits=_limits(), knowledge=_knowledge(similarity),
        user_seed_for=lambda f, h: None, p8_run_call=None, p8_authorities=None,
        embeddings=EmbeddingsOff(), created_at=T0)
    assert not [
        edge for edge in without.graph.edges
        if edge.edge_type == MUTUAL_SEMANTIC_RETRIEVAL
    ]


def test_the_encoder_sees_only_the_configured_scope(embed_conn, corpus):
    anchor, sparse = corpus
    encoder, text_for = SpyEncoder(), BoundedText()
    _run(embed_conn, anchor,
         embeddings=_on(encoder, text_for, (
             FileVersionRef(file_id=sparse[0], content_hash=sparse[1]),)),
         knowledge=_knowledge(_mutual(anchor[0], sparse[0])))
    assert {call[2] for call in text_for.calls} == {CONFIG.scope}


# --- off, and broken -------------------------------------------------------------


def test_off_reads_no_text_encodes_nothing_and_writes_nothing(embed_conn, corpus):
    anchor, _sparse = corpus
    encoder, text_for = SpyEncoder(), BoundedText()
    _run(embed_conn, anchor, embeddings=EmbeddingsOff(),
         knowledge=_knowledge(None))
    assert text_for.calls == []
    assert encoder.calls == []
    assert embed_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings").fetchone()["c"] == 0


def test_an_enabled_runtime_built_past_its_own_validator_is_refused(
    embed_conn, corpus,
):
    """Constructed the way a deserializer would. The pipeline revalidates rather
    than trusting the record, because an incomplete enabled runtime reaching
    retrieval is a semantic channel with no vectors behind it."""
    anchor, _sparse = corpus
    broken = object.__new__(EmbeddingsOn)
    for name in ("config", "encoder", "embedding_text_for",
                 "eligible_versions_for"):
        object.__setattr__(broken, name, None)
    object.__setattr__(broken, "enabled", True)

    with pytest.raises(ConfigurationRequired):
        _run(embed_conn, anchor, embeddings=broken,
             knowledge=_knowledge(_mutual(anchor[0], "x")))
    assert embed_conn.execute(
        "SELECT count(*) AS c FROM vector_embeddings").fetchone()["c"] == 0


# --- the bound, applied before any text is read ----------------------------------


def test_the_neighbour_that_sorts_last_by_hash_is_still_offered(embed_conn, corpus):
    """`104` R-59's second finding, and the case that shows why the cut was wrong.

    This test used to assert the opposite -- "a large eligible set is CUT before a
    single text is read", five texts read out of thirty, and the survivors named as
    `file-00` to `file-03`, "the stable `(content_hash, file_id)` order". That
    order is a digest. On the owner's 199 files it meant every seed in the corpus
    was compared against the same nine versions, and `00`:56's own example --
    "embeddings ... can find files such as HW 3.pdf that lack the course code but
    resemble lecture notes and earlier problem sets" -- could only ever succeed if
    those lecture notes happened to sort into the nine.

    Here the seed's TRUE neighbour is listed among thirty and sorts last of all by
    content hash. Under the cut it was never encoded, so the channel could not see
    it however near it was. Now it is offered.

    `00`:257's two reductions are both intact and both come after a score:
    `retrieve_neighbors` cuts at `max_retrieved_neighbors` having ranked every
    channel, and `build_graph` cuts at `max_graph_nodes` having ranked the edges.
    """
    anchor, sparse = corpus
    decoys = tuple(
        FileVersionRef(file_id=f"file-{n:02d}",
                       content_hash="0" * 60 + f"{n:04d}")
        for n in range(30)
    )
    assert all(sparse[1] > ref.content_hash for ref in decoys), (
        "the neighbour must sort last by content hash for this to bite")
    many = decoys + (FileVersionRef(file_id=sparse[0], content_hash=sparse[1]),)

    encoder, text_for = SpyEncoder(), BoundedText()
    result = _run(embed_conn, anchor, limits=_limits(max_graph_nodes=5),
                  embeddings=_on(encoder, text_for, many),
                  knowledge=_knowledge(_mutual(anchor[0], sparse[0])))

    encoded = {call[0] for call in text_for.calls}
    assert sparse[0] in encoded, (
        "the seed's real neighbour was never encoded, so the channel could not "
        "find it -- which is the defect, not the bound")
    assert (anchor[0], anchor[1], CONFIG.scope) in text_for.calls
    assert len(text_for.calls) == len(many) + 1
    assert result.graph is not None
    assert sparse[0] in {edge.to_file_id for edge in result.graph.edges}


def test_the_graph_ceiling_bounds_the_graph_and_not_the_vectors(embed_conn, corpus):
    """`max_graph_nodes` is `00`:257's reduction of a scored GRAPH -- "reduce to
    the strongest anchors and highest-quality edges" -- and it still does that.
    What it no longer does is decide, before any similarity exists, which files
    the channel is allowed to have an opinion about."""
    anchor, sparse = corpus
    encoder, text_for = SpyEncoder(), BoundedText()
    result = _run(embed_conn, anchor, limits=_limits(max_graph_nodes=1),
                  embeddings=_on(encoder, text_for, (
                      FileVersionRef(file_id=sparse[0], content_hash=sparse[1]),)),
                  knowledge=_knowledge(_mutual(anchor[0], sparse[0])))

    assert sorted(call[0] for call in text_for.calls) == sorted(
        [anchor[0], sparse[0]])
    # the GRAPH is still bounded at one node, which is the seed
    assert result.graph is not None and result.graph.edges == ()


def test_a_duplicate_eligible_version_does_not_consume_a_cap_slot(
    embed_conn, corpus,
):
    """`ensure_file_embedding` is already idempotent, so a repeat costs no second
    encode. What it costs without deduplication is a SLOT: the cap is applied to
    the list, and a version listed twice starves a real one out of the bound."""
    anchor, _sparse = corpus
    listed_twice = (
        FileVersionRef(file_id="file-a", content_hash="hash-a"),
        FileVersionRef(file_id="file-a", content_hash="hash-a"),
        FileVersionRef(file_id="file-b", content_hash="hash-b"),
        FileVersionRef(file_id="file-c", content_hash="hash-c"),
    )
    encoder, text_for = SpyEncoder(), BoundedText()
    _run(embed_conn, anchor, limits=_limits(max_graph_nodes=4),
         embeddings=_on(encoder, text_for, listed_twice),
         knowledge=_knowledge(_mutual(anchor[0], "file-a")))
    encoded = [call[0] for call in text_for.calls if call[0] != anchor[0]]
    assert encoded == ["file-a", "file-b", "file-c"]


# --- the deployment's own wiring: §4.4's channel, on a measured threshold ---------

WEIGHTS = pathlib.Path.home() / ".graph-agent" / "models" / "minilm"


def test_the_semantic_channel_is_off_when_no_weights_are_named():
    """Absent means off, and off means every similarity input is `None`.

    `RetrievalKnowledge` is "absent means omit, never assume", and
    `_require_semantic_configuration` refuses a half-configured channel. A
    deployment that named no weights must produce the shape retrieval reads as
    "there is no semantic channel", not one with a threshold and no encoder.
    """
    import cli

    runtime, retrieval = cli._embedding_runtime(None, versions_for=lambda c, n: ())

    assert runtime.enabled is False
    assert retrieval.similarity is None
    assert retrieval.similarity_threshold is None
    assert retrieval.embedding_identity is None


@pytest.mark.skipif(not (WEIGHTS / "model.onnx").is_file(),
                    reason="the weights are machine state; this run has none")
def test_the_threshold_is_the_measured_one_and_the_identity_matches_the_vectors():
    """MEASURED, not chosen. `planning/103` records the run this number comes from.

    On the owner's own corpus, over every pair of labelled files: same-course pairs
    have a median cosine of 0.417 and a 10th percentile of 0.212; different-course
    pairs have a median of 0.057 and a 90th percentile of 0.165. The distributions
    separate, and 0.30 is where F1 peaks -- 90.7% precision at 67.1% recall.

    The identity is asserted against the config rather than restated, because a
    vector stored under one identity and read back under another is the failure
    `EmbeddingIdentity` exists to prevent -- "all three or none".
    """
    import cli

    runtime, retrieval = cli._embedding_runtime(
        WEIGHTS, versions_for=lambda conn, cap: ())

    assert runtime.enabled is True
    assert retrieval.similarity_threshold == cli.SEMANTIC_SIMILARITY_THRESHOLD == 0.30
    assert retrieval.similarity is not None
    assert retrieval.embedding_identity.scope == runtime.config.scope
    assert retrieval.embedding_identity.model_id == runtime.config.model_id
    assert retrieval.embedding_identity.model_version == runtime.config.model_version
    # §4.4's own precedence: a shared validated fact ESTABLISHES a group and a
    # semantic neighbour never does, so when the neighbourhood is capped the fact
    # channel must survive the cut first.
    assert (retrieval.channel_weights[SHARED_VALIDATED_FACT]
            > retrieval.channel_weights[MUTUAL_SEMANTIC_RETRIEVAL])
