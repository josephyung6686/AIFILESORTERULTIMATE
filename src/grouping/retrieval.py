# src/grouping/retrieval.py
"""Six channels that find neighbours, and none of them decides anything.

The graph is a context-assembly mechanism, not a label-propagation system.
Retrieval's whole job is to find files that MAY supply context for one another;
whether any of them belongs is the validator's question and then the user's.

Two rules make that real:

**Only a shared fact at P9's anchor bar sets `anchors`.** Every other channel
returns `anchors=False`, including the ones that feel strongest. A duplicate link
brings a genuinely related file and is not evidence of shared purpose; a download
session is explicitly "not a basis for automatic semantic propagation"; and
semantic retrieval is the channel most likely to look like agreement while being
nothing but proximity.

**Semantic retrieval is mutual.** A file whose vector is near the seed's proves
nothing on its own, because a heavily-cited hub is near everything. Both
directions must clear the injected threshold.

Nothing here holds a number or a rule. Limits come from `GroupingLimits`, channel
weights and the compatibility predicate and the similarity function are injected,
and a missing one omits its channel and says so rather than assuming a permissive
default — treating every document type as compatible would quietly widen every
group in the corpus.

A note on cost, so the next reader does not mistake it for an oversight: P6
publishes only per-file reads, so matching a shared fact means reading each
candidate's facts rather than consulting an index. The neighbourhood cap bounds
the RESULT, not the scan. An index read is P6's to publish if this becomes the
bottleneck; P9 inventing one would be P9 querying P6's tables.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field

from database_agent.vector_versions import current_embedding
from facts.read_surface import family_facts, proposal_eligible, session_facts

from grouping.config import ConfigurationRequired, GroupingLimits
from grouping.seeds import ANCHOR_STATES, Seed
from grouping.vocabulary import (
    BOUNDED_SESSION,
    COMPATIBLE_DOCUMENT_TYPE,
    DUPLICATE_OR_VERSION_LINK,
    EXISTING_RELATED_FOLDER,
    MUTUAL_SEMANTIC_RETRIEVAL,
    SHARED_VALIDATED_FACT,
)

#: Ranking order when no weight distinguishes two channels. Direct evidence
#: first, proximity last — the order a reviewer would read them in.
DEFAULT_CHANNEL_ORDER: tuple[str, ...] = (
    SHARED_VALIDATED_FACT,
    DUPLICATE_OR_VERSION_LINK,
    COMPATIBLE_DOCUMENT_TYPE,
    EXISTING_RELATED_FOLDER,
    BOUNDED_SESSION,
    MUTUAL_SEMANTIC_RETRIEVAL,
)

#: P1's own scan state for a file that is in the corpus. Anything else is out.
INCLUDED_SCAN_STATE = "included"


@dataclass(frozen=True)
class EmbeddingIdentity:
    """Which stored vector semantic retrieval reads. All three or none."""

    scope: str
    model_id: str
    model_version: str


@dataclass(frozen=True)
class RetrievalKnowledge:
    """Everything P9 does not author. Absent means omit, never assume."""

    document_compatible: Callable[[str, str, str], bool] | None
    channel_weights: Mapping[str, int]
    similarity: Callable[[bytes, bytes], float] | None
    similarity_threshold: float | None
    embedding_identity: EmbeddingIdentity | None
    domain: str | None


@dataclass(frozen=True)
class Neighbor:
    file_id: str
    content_hash: str
    channel: str
    anchors: bool
    evidence_ref: str | None
    detail: str | None


@dataclass(frozen=True)
class Neighborhood:
    seed: Seed
    neighbors: tuple[Neighbor, ...]
    omissions: tuple[str, ...] = field(default=())
    capped: bool = False


@dataclass(frozen=True)
class _Candidate:
    file_id: str
    content_hash: str
    directory_position: str | None
    detected_format: str | None


def _corpus(conn: sqlite3.Connection, *, seed: Seed) -> list[_Candidate]:
    """Every included file version except the seed's own.

    Reads P1's published columns only. `scan_state` is P3's, and a file that is
    not `included` never enters a neighbourhood — an excluded file reaching a
    dossier would be the scan boundary failing silently.
    """
    rows = conn.execute(
        "SELECT file_id, content_hash, directory_position, detected_format "
        "FROM files WHERE scan_state = ? ORDER BY content_hash, file_id",
        (INCLUDED_SCAN_STATE,),
    ).fetchall()
    return [
        _Candidate(
            file_id=row["file_id"],
            content_hash=row["content_hash"],
            directory_position=row["directory_position"],
            detected_format=row["detected_format"],
        )
        for row in rows
        if row["file_id"] != seed.file_id
    ]


def _seed_row(conn: sqlite3.Connection, seed: Seed) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT directory_position, detected_format FROM files WHERE file_id = ?",
        (seed.file_id,),
    ).fetchone()


def _first_ref(row: sqlite3.Row) -> str | None:
    import json

    raw = row["evidence_refs"]
    if not isinstance(raw, str) or not raw:
        return None
    try:
        refs = json.loads(raw)
    except ValueError:
        return None
    return refs[0] if isinstance(refs, list) and refs else None


def _values(rows: Sequence[sqlite3.Row]) -> dict[tuple[str, str], sqlite3.Row]:
    return {(row["field_key"], row["canonical_value"]): row for row in rows}


def _shared_fact_neighbors(
    conn: sqlite3.Connection, seed: Seed, candidates: Sequence[_Candidate],
) -> list[Neighbor]:
    """Channel 1. The only channel that may anchor, and only above the bar."""
    if seed.field_key is None or seed.value is None:
        return []
    found: list[Neighbor] = []
    for candidate in candidates:
        rows = proposal_eligible(
            conn, file_id=candidate.file_id, content_hash=candidate.content_hash,
        )
        match = _values(rows).get((seed.field_key, seed.value))
        if match is None:
            continue
        found.append(Neighbor(
            file_id=candidate.file_id,
            content_hash=candidate.content_hash,
            channel=SHARED_VALIDATED_FACT,
            anchors=match["reliability_state"] in ANCHOR_STATES,
            evidence_ref=_first_ref(match),
            detail=f"{seed.field_key}={seed.value}",
        ))
    return found


def _family_or_session_neighbors(
    conn: sqlite3.Connection,
    seed: Seed,
    candidates: Sequence[_Candidate],
    *,
    read,
    channel: str,
) -> list[Neighbor]:
    """Channels 2 and 5. Retrieval-only, at any reliability state.

    `possible` rows are read deliberately: a duplicate family or a download
    session brings a real neighbour, and neither is evidence the neighbour
    belongs. `anchors` is hardcoded False here and that is the point.
    """
    seed_values = _values(
        read(conn, file_id=seed.file_id, content_hash=seed.content_hash),
    )
    if not seed_values:
        return []
    found: list[Neighbor] = []
    for candidate in candidates:
        rows = _values(
            read(conn, file_id=candidate.file_id,
                 content_hash=candidate.content_hash),
        )
        shared = sorted(set(seed_values) & set(rows))
        if not shared:
            continue
        field_key, value = shared[0]
        found.append(Neighbor(
            file_id=candidate.file_id,
            content_hash=candidate.content_hash,
            channel=channel,
            anchors=False,
            evidence_ref=_first_ref(rows[(field_key, value)]),
            detail=f"{field_key}={value}",
        ))
    return found


def _compatible_document_neighbors(
    seed_row: sqlite3.Row,
    candidates: Sequence[_Candidate],
    knowledge: RetrievalKnowledge,
) -> list[Neighbor]:
    """Channel 3. Omitted entirely when the predicate is absent."""
    predicate = knowledge.document_compatible
    if predicate is None:
        return []
    left = seed_row["detected_format"]
    return [
        Neighbor(
            file_id=candidate.file_id,
            content_hash=candidate.content_hash,
            channel=COMPATIBLE_DOCUMENT_TYPE,
            anchors=False,
            evidence_ref=None,
            detail=f"{left} ~ {candidate.detected_format}",
        )
        for candidate in candidates
        if predicate(knowledge.domain, left, candidate.detected_format)
    ]


def _related_folder_neighbors(
    seed_row: sqlite3.Row, candidates: Sequence[_Candidate],
) -> list[Neighbor]:
    """Channel 4. An existing curated folder is the user's own grouping."""
    folder = seed_row["directory_position"]
    if not folder:
        return []
    return [
        Neighbor(
            file_id=candidate.file_id,
            content_hash=candidate.content_hash,
            channel=EXISTING_RELATED_FOLDER,
            anchors=False,
            evidence_ref=None,
            detail=folder,
        )
        for candidate in candidates
        if candidate.directory_position == folder
    ]


def _semantic_neighbors(
    conn: sqlite3.Connection,
    seed: Seed,
    candidates: Sequence[_Candidate],
    knowledge: RetrievalKnowledge,
) -> list[Neighbor]:
    """Channel 6. Mutual only, and never an anchor.

    One-way nearness is what a hub produces: it is near everything, and nothing
    is near it in return. Requiring both directions is what makes the channel
    mean "these two retrieved each other" rather than "one of them is popular".
    """
    identity = knowledge.embedding_identity
    similarity = knowledge.similarity
    threshold = knowledge.similarity_threshold
    assert identity is not None and similarity is not None  # checked by caller
    assert threshold is not None

    def vector(file_id: str, content_hash: str) -> bytes | None:
        record = current_embedding(
            conn, file_id=file_id, content_hash=content_hash,
            scope=identity.scope, embedding_model_id=identity.model_id,
            embedding_version=identity.model_version,
        )
        return None if record is None else record.array_bytes

    seed_vector = vector(seed.file_id, seed.content_hash)
    if seed_vector is None:
        return []
    found: list[Neighbor] = []
    for candidate in candidates:
        other = vector(candidate.file_id, candidate.content_hash)
        if other is None:
            continue
        forward = similarity(seed_vector, other)
        backward = similarity(other, seed_vector)
        if forward < threshold or backward < threshold:
            continue
        found.append(Neighbor(
            file_id=candidate.file_id,
            content_hash=candidate.content_hash,
            channel=MUTUAL_SEMANTIC_RETRIEVAL,
            anchors=False,
            evidence_ref=None,
            detail=f"mutual >= {threshold}",
        ))
    return found


def _require_semantic_configuration(knowledge: RetrievalKnowledge) -> None:
    missing = [
        name
        for name, value in (
            ("similarity", knowledge.similarity),
            ("similarity_threshold", knowledge.similarity_threshold),
            ("embedding_identity", knowledge.embedding_identity),
        )
        if value is None
    ]
    if missing:
        raise ConfigurationRequired(
            f"semantic retrieval was requested and {missing} were not supplied; "
            "P9 authors no similarity measure and no threshold"
        )


def retrieve_neighbors(
    conn: sqlite3.Connection,
    *,
    seed: Seed,
    limits: GroupingLimits | None,
    knowledge: RetrievalKnowledge,
    embeddings_enabled: bool,
) -> Neighborhood:
    """A bounded neighbourhood for one seed. Deterministic, and decides nothing."""
    if limits is None:
        raise ConfigurationRequired(
            "retrieval is bounded by P1's ceilings; without GroupingLimits there "
            "is no bound and P9 supplies none"
        )
    if embeddings_enabled:
        _require_semantic_configuration(knowledge)

    seed_row = _seed_row(conn, seed)
    if seed_row is None:
        return Neighborhood(seed=seed, neighbors=(), omissions=("seed_not_in_corpus",))

    candidates = _corpus(conn, seed=seed)
    omissions: list[str] = []
    found: list[Neighbor] = []

    found.extend(_shared_fact_neighbors(conn, seed, candidates))
    found.extend(_family_or_session_neighbors(
        conn, seed, candidates, read=family_facts,
        channel=DUPLICATE_OR_VERSION_LINK,
    ))
    if knowledge.document_compatible is None:
        omissions.append("missing_document_compatibility")
    else:
        found.extend(
            _compatible_document_neighbors(seed_row, candidates, knowledge),
        )
    found.extend(_related_folder_neighbors(seed_row, candidates))
    found.extend(_family_or_session_neighbors(
        conn, seed, candidates, read=session_facts, channel=BOUNDED_SESSION,
    ))
    if embeddings_enabled:
        found.extend(_semantic_neighbors(conn, seed, candidates, knowledge))

    def rank(neighbor: Neighbor) -> tuple[int, str, str]:
        weight = knowledge.channel_weights.get(neighbor.channel, 0)
        return (-weight, neighbor.content_hash, neighbor.file_id)

    ordered = sorted(found, key=rank)
    kept = ordered[: limits.max_retrieved_neighbors]
    capped = len(ordered) > len(kept)
    if capped:
        omissions.append("neighbourhood_cap")
    return Neighborhood(
        seed=seed,
        neighbors=tuple(kept),
        omissions=tuple(omissions),
        capped=capped,
    )
