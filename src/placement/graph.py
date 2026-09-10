"""§6.4's node-local evidence graph. Local by construction, never by intention.

The graph is built around ONE candidate node and the subject being placed. Its
vertices are the subject plus the files already accepted in that node; its edges
are typed relationships between them. §6.4 asks for the target to be compared
against "the node's approved community, not against a folder name", and that is
what makes the comparison meaningful when a label happens to look right.

Two different things keep it local, and they are not the same strength:

* The COMMUNITY FILTER is structural. An edge survives only if it touches a file
  already accepted in this node, so a related file belonging elsewhere has no way
  in and there is no code path along which whole-corpus reclustering could
  happen. A node with no approved community anchors nothing -- the honest answer
  when there is nothing to compare against, and the one that keeps an empty
  community from reading as "keep everything".
* `foreign_node_ids` is a SEAM ASSERTION. The caller declares which other nodes
  its neighbourhood reached, and a non-empty declaration is refused. It cannot
  catch a caller that stays silent; the filter above is what makes silence safe.

§8.6 gives this object two ceilings and they are both enforced here: the cluster
of files the graph reaches (`max_candidate_cluster_size`) and the edges between
them (`max_local_graph_neighborhood`). They are separate bounds on separate
things, and a graph that satisfied only the second could still show a model fifty
files reached by one edge each.

Two §6.5 rules produce the `is_typed_support` answer. A semantic embedding is not
an edge type here at all, so it contributes nothing; and a neighbourhood held
together by one entity that appears everywhere is not support, which is why the
frequency arrives injected and P11 picks no cut-off of its own.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from placement.records import GraphAnchor

SHARED_VALIDATED_FACT: str = "shared_validated_fact"
DUPLICATE: str = "duplicate"
VERSION_FAMILY: str = "version_family"
COMPATIBLE_DOCUMENT_TYPE: str = "compatible_document_type"
EXISTING_RELATED_FOLDER: str = "existing_related_folder"
#: `104` §18.2 gap 12's two new types, and the only two of `00`:109's nine that
#: had no carrier AND have a producer the store can answer truthfully today.
#: `DESIGN_RELATIONSHIPS` below says which of the nine each type carries and what
#: produces it; nothing here is minted for a relationship nothing can observe.
ATTACHMENT_OF: str = "attachment_of"
DIRECT_REFERENCE: str = "direct_reference"

#: §6.5's typed relationships. A semantic neighbour is deliberately absent: it is
#: a retrieval channel (`placement.retrieval.SEMANTIC_NEIGHBOUR`) and never an edge,
#: because an embedding alone is insufficient and an edge type would make it look
#: like evidence of the same kind as a shared fact.
EDGE_TYPES: tuple[str, ...] = (
    SHARED_VALIDATED_FACT, DUPLICATE, VERSION_FAMILY, COMPATIBLE_DOCUMENT_TYPE,
    EXISTING_RELATED_FOLDER, ATTACHMENT_OF, DIRECT_REFERENCE,
)


@dataclass(frozen=True)
class Relationship:
    """One of `00`:109's nine typed relationships, and what answers it today.

    `carried_by` is the edge type (or the retrieval channel) that carries it;
    `producer` names the code that writes it, or is EMPTY for a relationship
    nothing produces yet. `104` §18.2 gap 12 opened as "five of nine edge types"
    with no way to check the count, so the count lives here and a test walks it.
    """

    design_name: str
    carried_by: tuple[str, ...]
    producer: str
    note: str = ""


#: `00`:109 in its own words: *"The node-local graph should include typed
#: relationships, such as shared validated facts, accepted group membership,
#: duplicate or version links, derivation links, compatible document type,
#: matching time period, direct references, mutual semantic retrieval, and
#: user-confirmed membership."*
#:
#: NINE, EACH WITH ITS PRODUCER OR WITH NONE, which is `104` §18.2 gap 12's
#: second half: the ranked list says "five of nine edge types" and no reader
#: could check the five, the nine, or which four were missing. Two of the nine
#: are not edges here AT ALL and never will be -- an accepted group and a
#: semantic neighbour reach P11 as `placement.retrieval` CHANNELS, which is
#: `00`:107's own placement of them ("accepted group membership should retrieve
#: the branch that was created from that group ... full-text and OCR embeddings
#: should retrieve semantically compatible node profiles") and §6.5's rule that
#: an embedding alone is insufficient. Recording them here as channels is what
#: stops them being counted as missing edges forever.
#:
#: `EXISTING_RELATED_FOLDER` is a TENTH carrier and is deliberately not one of
#: the nine: it is P9's own channel (a folder the person already made), which
#: `00`:107 names under retrieval rather than under the graph's relationships.
DESIGN_RELATIONSHIPS: tuple[Relationship, ...] = (
    Relationship(
        "shared validated facts", (SHARED_VALIDATED_FACT,),
        "grouping.graph, from P9's shared-fact channel",
        # `authored_by` is a P6 field like any other (`facts/fields.py`), so two
        # files by one author are already related by this edge. A `same_author`
        # type would be a second name for one relationship, and the graph would
        # count it twice.
        "carries a shared author, a shared institution and a shared course "
        "alike; the bridge names which"),
    Relationship(
        "accepted group membership", ("retrieval.accepted_group",),
        "cli.accepted_memberships_of, as a RETRIEVAL CHANNEL",
        "never an edge: `00`:107 makes an accepted group retrieve the branch "
        "built from it, and `pipeline._accepted_group_items` carries it into "
        "the dossier in its own shape"),
    Relationship(
        "duplicate or version links", (DUPLICATE, VERSION_FAMILY),
        "grouping.graph, typed by cli._duplicate_or_version",
        "two edge types for one design phrase, because a duplicate and a "
        "revision are not the same statement about two files"),
    Relationship(
        "derivation links", (ATTACHMENT_OF,),
        "cli.observation_edges_of, from the email reader's attachment names",
        "one derivation the product can observe. A derived export, a rendered "
        "PDF of a document, a crop of a photograph: none has a producer yet"),
    Relationship(
        "compatible document type", (COMPATIBLE_DOCUMENT_TYPE,),
        "grouping.graph, from P9's compatible-document-type channel"),
    Relationship(
        "matching time period", (SHARED_VALIDATED_FACT,),
        "grouping.graph, when the shared fact IS the period",
        "no type of its own: a term or a capture date is a P6 field, so two "
        "files sharing one are already related by the shared-fact edge and a "
        "second type would double-count the one relationship"),
    Relationship(
        "direct references", (DIRECT_REFERENCE,),
        "cli.observation_edges_of, from `104` §18.31's DOI kind",
        "UNDIRECTED, and the store is why: gap 20 stores a structured string's "
        "ZONE and not its kind, so two files carrying one DOI are known to "
        "share a reference and not which of them is the paper"),
    Relationship(
        "mutual semantic retrieval", ("retrieval.semantic_neighbour",),
        "cli.semantic_neighbour_nodes, as a RETRIEVAL CHANNEL",
        "never an edge: §6.5 says an embedding alone is insufficient, and an "
        "edge type would make it look like evidence of a shared fact's kind"),
    Relationship(
        "user-confirmed membership", ("retrieval.accepted_group",),
        "",
        "none yet AS AN EDGE. §3.13's `user_confirmed` is a state on a FACT, "
        "and a membership the person confirmed arrives as the accepted-group "
        "channel above; what has no producer is an edge between two files the "
        "person confirmed belong together, which needs a gesture P7 has not "
        "shipped"),
)

#: What produced an edge, in one phrase, for the dossier item's `location`. This
#: is the PRODUCER and never the bridge entity: `existing_related_folder` bridges
#: through a folder path label and `attachment_of` through a filename, and
#: §8.4's always-local list opens with the word "Paths". The model is told where
#: the relationship came from, not the string it rests on.
EDGE_PRODUCER: dict[str, str] = {
    SHARED_VALIDATED_FACT: "a validated fact both files state",
    DUPLICATE: "the duplicate-family detection",
    VERSION_FAMILY: "the version-family detection",
    COMPATIBLE_DOCUMENT_TYPE: "both files being the same kind of document",
    EXISTING_RELATED_FOLDER: "a folder the person already keeps both in",
    ATTACHMENT_OF: "an attachment named in an email this run read",
    DIRECT_REFERENCE: "a reference identifier both files carry",
}


class WholeCorpusReclusteringRefused(RuntimeError):
    """A neighbourhood reached beyond the one node it belongs to."""


@dataclass(frozen=True)
class NodeLocalGraph:
    subject_ref: str
    node_id: str
    anchors: tuple[GraphAnchor, ...]
    distinct_entities: frozenset[str]
    high_frequency_entities: frozenset[str]
    #: How many EDGES survived, bounded by `max_local_graph_neighborhood`.
    neighbourhood_size: int
    #: How many distinct community FILES they span, bounded by
    #: `max_candidate_cluster_size`. Separate from the count above because §8.6
    #: bounds both and one does not imply the other: fifty edges between three
    #: files and fifty edges to fifty files are different neighbourhoods.
    cluster_size: int
    #: True if EITHER ceiling cut something. §8.6 renders a bounded neighbourhood
    #: differently from a complete one, and which of the two bounds did the
    #: cutting does not change that a reviewer is looking at a reduction.
    reduced_to_strongest: bool


def build_node_local_graph(*, subject, candidate, entry, related_files, limits,
                           entity_frequency, generic_entity_frequency,
                           foreign_node_ids=()) -> NodeLocalGraph:
    """One subject, one node, one neighbourhood.

    `related_files` are edges the caller already resolved from P6 facts, P9
    memberships and P3 folder context; P11 discovers no relationship of its own
    here, because that would be a second grouping engine and P9 owns grouping.

    **THE CALLER'S ORDER IS PART OF THE CONTRACT (`104` R-111).** §8.6's two
    ceilings below cut, and a stable sort on weight alone leaves everything they
    did not rank in the order it arrived -- so an arbitrary order here is an
    arbitrary answer, and `cli.typed_edges_of` is where the content order that
    makes it reproducible is established.
    """
    from placement.store import subject_ref_of

    if foreign_node_ids:
        raise WholeCorpusReclusteringRefused(
            f"the neighbourhood named {sorted(foreign_node_ids)} besides "
            f"{candidate.node_id!r}; §6.5 permits local clustering only, and a "
            "graph spanning nodes is whole-corpus reclustering under another name"
        )
    for item in related_files:
        if item["edge_type"] not in EDGE_TYPES:
            raise ValueError(
                f"{item['edge_type']!r} is not one of §6.5's {len(EDGE_TYPES)} typed "
                "relationships; an untyped edge is a similarity wearing a name"
            )

    community = set(entry.representative_files) if entry is not None else set()
    kept = [
        item for item in related_files
        if item["to_file_id"] in community or item["anchor_file_id"] in community
    ]
    # Weight, and NOTHING ELSE. A stable sort, so edges of equal weight keep the
    # order the caller handed them in -- which `cli.typed_edges_of` reads out of
    # `group_edges` ordered by the other end's `(content_hash, current_path)`,
    # then edge type and bridge.
    #
    # **IT USED TO BE `(-weight, to_file_id)`, AND THAT WAS `104` R-111.** A
    # `file_id` is a `uuid4` P1 mints when it first indexes a path, and P9 stores
    # no weight at all -- `typed_edges_of` gives every edge 1.0 -- so the whole of
    # this ranking was a comparison between two minted ids, and the two cuts
    # below are the ones that CHOOSE: `max_candidate_cluster_size` decides which
    # files reach the graph and `max_local_graph_neighborhood` which edges
    # survive. Two runs over one folder therefore recorded a different
    # `graph_anchors` for the same placement -- 24 of 36 rows on R-78's corpus,
    # 870 of 1,000 on the scale corpus -- while every other derived table was
    # byte-identical. The file went to the same folder both times and could not
    # be shown the same reason twice.
    #
    # Weight stays the cut's own business rather than moving to the caller: the
    # day P9 records a real one it must dominate, and content break its ties.
    # This is `104` R-78's `grouping.graph._rank` at the P11 seam, for the same
    # reason -- an address is for finding a thing again, not for choosing between
    # things.
    ordered = sorted(kept, key=lambda item: -item["weight"])
    # §8.6's two ceilings on this object, applied in the order that makes both
    # hold. They bound different things and neither implies the other: a vague
    # file can reach five files through fifty edges, or fifty files through
    # fifty. `max_candidate_cluster_size` bounds the CLUSTER -- §6.5's "small
    # local cluster around an approved destination profile", which is a set of
    # files -- and `max_local_graph_neighborhood` bounds the EDGES between them.
    #
    # The cluster is cut first because the other order does not converge: trimming
    # edges can leave the surviving ones still spanning more files than the
    # cluster ceiling allows, so the bound would not be a bound.
    #
    # Both cuts follow §8.6's own rule -- "reduce to the strongest anchors and
    # highest-quality edges" -- over the one ordering above. The cluster cut skips
    # rather than stops: every edge to a member already in the cluster survives,
    # and only edges that would admit a surplus MEMBER are dropped, so no strong
    # edge is lost to a weaker one that happened to come first.
    cluster_ceiling = limits.max_candidate_cluster_size
    members: set[str] = set()
    within: list = []
    for item in ordered:
        if item["to_file_id"] not in members and len(members) >= cluster_ceiling:
            continue
        members.add(item["to_file_id"])
        within.append(item)
    reduced = len(within) < len(ordered)
    ordered = within

    ceiling = limits.max_local_graph_neighborhood
    reduced = reduced or len(ordered) > ceiling
    ordered = ordered[:ceiling]
    cluster = {item["to_file_id"] for item in ordered}

    anchors = tuple(
        # `subject.file_id` is passed through, never coerced: `GraphAnchor`
        # requires it non-empty and a `""` stand-in would be a placeholder
        # satisfying a type. A group subject has no single originating file and
        # fails here by name rather than storing one.
        GraphAnchor(edge_type=item["edge_type"], from_file_id=subject.file_id,
                    to_file_id=item["to_file_id"],
                    anchor_file_id=item["anchor_file_id"])
        for item in ordered
    )
    entities = Counter(item["entity"] for item in ordered)
    high_frequency = frozenset(
        entity for entity in entities
        if entity_frequency.get(entity, 0) >= generic_entity_frequency
    )
    return NodeLocalGraph(
        subject_ref=subject_ref_of(subject), node_id=candidate.node_id,
        anchors=anchors, distinct_entities=frozenset(entities),
        high_frequency_entities=high_frequency,
        neighbourhood_size=len(ordered), cluster_size=len(cluster),
        reduced_to_strongest=reduced,
    )


def is_typed_support(graph: NodeLocalGraph) -> bool:
    """§6.5's bar: a typed relationship that is not one everywhere-entity.

    A target connected by nothing, or only by an entity that appears across the
    corpus, stays uncertain. This is the deterministic half of the same judgement
    P8 makes about a model's answer as `GENERIC_HUB_ONLY`; P11 answers it about
    its own evidence, before any dossier exists.

    "Connected by nothing" needs no clause of its own. `anchors` and
    `distinct_entities` are built from the same surviving edges, so a graph with
    no anchors has no entities either and the subtraction below is already empty.
    An `if not graph.anchors` guard here would be a check that can never fire --
    it reads as a second rule and enforces none.
    """
    informative = graph.distinct_entities - graph.high_frequency_entities
    return bool(informative)
