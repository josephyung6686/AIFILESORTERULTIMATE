"""`104` §18.2 gap 12 — the two typed relationships P9 does not draw.

`00`:109 names nine typed relationships and `placement.graph` carried five of
them. Two of the four missing ones have producers the store can answer
truthfully today, and neither is a GROUPING: they are two files' own observations
agreeing about a third thing, so the composition root produces them and P9 gains
no second engine.

* `attachment_of` is `00`:109's derivation link. The email reader emits one
  `attachment` value per named part; a part whose name is a file this run
  indexed is a derivation link between the message and that file.
* `direct_reference` is `00`:109's direct reference, from the DOI kind `104`
  §18.31 added. UNDIRECTED, because P4 has no kind column: the kind reaches the
  store as a ZONE, and `link` holds URLs, email addresses and DOIs alike, so what
  the store can say is that two files carry one DOI and not which of them is the
  paper.
"""
from __future__ import annotations

import hashlib

import pytest

import cli
from evidence_shape.location import Location, Segment, TextSpan
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.schema import create_evidence_schema
from evidence_shape.store import record_observation, record_run
from placement.graph import build_node_local_graph

AT = "2026-09-10T00:00:00+00:00"
#: Crossref's own example, and one `cli._DOI` matches whole.
DOI = "10.1038/s41586-020-2649-2"


def _hash(file_id: str) -> str:
    """P1's own identity shape: a sha256 digest, which `ExtractionRun` checks."""
    return hashlib.sha256(file_id.encode("utf-8")).hexdigest()


def _file(conn, file_id: str, name: str) -> None:
    conn.execute(
        "INSERT INTO files (file_id, current_path, filename, "
        "normalized_filename, extension, content_hash, hash_algorithm, "
        "observed_size, observed_timestamps, scan_state) "
        "VALUES (?, ?, ?, ?, ?, ?, 'sha256', 10, '{}', 'included')",
        (file_id, f"/corpus/{name}", name, name.casefold(),
         name.rpartition(".")[2], _hash(file_id)))
    record_run(conn, ExtractionRun(
        run_id=f"run-{file_id}", file_id=file_id,
        content_hash=_hash(file_id), extractor_name="fixture",
        extractor_version="1.0.0", source_type="text_document",
        analysis_tier="native", config={}, completeness="complete",
        started_at=AT, observation_count=1))


def _observation(conn, file_id: str, *, zone: str, value: str,
                 container_path=()) -> None:
    record_observation(conn, Observation(
        file_id=file_id, content_hash=_hash(file_id),
        extractor_name="fixture", extractor_version="1.0.0",
        source_type="text_document", raw_value=value,
        location=Location(zone=zone, container_path=container_path,
                          text_span=TextSpan(0, len(value))),
        occurrence_count=1, observed_at=AT, reliability="direct",
        run_id=f"run-{file_id}", context_before=None, context_after=None,
        context_truncated=False))


def _attachment(conn, message: str, name: str) -> None:
    """One named part of an email, in the shape the long-tail extractor stores.

    `readers/long_tail_stdlib._message_values` emits `LongTailValue(name=
    "attachment", ...)` and `extractors/long_tail.py` writes it as a `metadata`
    observation whose container path ends `segment("field", label=<slot>)`. This
    reads the reader's own word rather than a second spelling of it.
    """
    _observation(conn, message, zone="metadata", value=name,
                 container_path=(Segment("entry", None, "1"),
                                 Segment("field", None, "attachment")))


@pytest.fixture()
def corpus(conn):
    create_evidence_schema(conn)
    return conn


def _edges(conn, file_id: str):
    attachments, references = cli.observation_edge_index(conn)
    return cli.observation_edges_of(file_id, attachments=attachments,
                                    references=references)


def test_an_email_naming_a_part_this_run_indexed_draws_a_derivation_link(corpus):
    """`00`:109's derivation link, from the email reader's own parts.

    The message names `invoice.pdf`; the run indexed a file of that name; the two
    are related. The MESSAGE anchors it whichever end is being placed, because
    the relationship was read out of the message's observations.

    SABOTAGE: draw the edge from only the message's side -- the attachment placed
    on its own has no way to reach the folder its covering email is in, which is
    the case `00`:112's packet is about.
    """
    _file(corpus, "msg", "thread.eml")
    _file(corpus, "part", "invoice.pdf")
    _attachment(corpus, "msg", "invoice.pdf")

    (from_message,) = _edges(corpus, "msg")
    assert from_message["edge_type"] == "attachment_of"
    assert from_message["to_file_id"] == "part"
    assert from_message["anchor_file_id"] == "msg"
    assert from_message["to_content_hash"] == _hash("part")

    (from_part,) = _edges(corpus, "part")
    assert from_part["to_file_id"] == "msg"
    assert from_part["anchor_file_id"] == "msg"


def test_an_attachment_name_no_file_carries_draws_nothing(corpus):
    """A name is not a relationship until there is a file at the other end.

    An email listing a part nobody saved names something this corpus does not
    hold, and an edge to it would be an edge to nothing.
    """
    _file(corpus, "msg", "thread.eml")
    _attachment(corpus, "msg", "never-saved.pdf")

    assert _edges(corpus, "msg") == ()


def test_two_files_carrying_one_doi_draw_a_direct_reference(corpus):
    """`00`:109's direct reference, from `104` §18.31's DOI kind.

    Undirected, and `graph.DESIGN_RELATIONSHIPS` records why: gap 20 stores a
    structured string's ZONE and not its kind, so what the store can say is that
    both files carry this identifier.

    SABOTAGE: name it `cited_by` and give it a direction -- the store cannot tell
    the paper from the file citing it, and the dossier would tell the model
    something nothing in it knows.
    """
    _file(corpus, "paper", "nature.pdf")
    _file(corpus, "notes", "reading.md")
    _observation(corpus, "paper", zone="link", value=DOI)
    _observation(corpus, "notes", zone="link", value=DOI)

    (edge,) = _edges(corpus, "notes")
    assert edge["edge_type"] == "direct_reference"
    assert edge["to_file_id"] == "paper"
    assert edge["anchor_file_id"] == "notes"
    assert edge["entity"] == cli.fact_bridge_ref("reference", DOI)


def test_a_shared_url_or_address_is_not_a_reference(corpus):
    """The other two `link` kinds draw nothing, and the reason is §6.5's hub test.

    `ZONE_BY_STRUCTURED_KIND` sends `url`, `email` and `doi` alike to `link`. An
    email address is shared by every file a mailing list touched and a bare URL by
    every file quoting one page, and §6.5's generic-entity test cannot catch
    either: `entity_frequency` is a count over FACTS and a link value is not one.
    So the kind that is a globally unique DOCUMENT identifier is the kind that
    becomes an edge, recovered by re-asking the pattern that stored the value --
    which is recovering the kind, not guessing at the string's shape.

    SABOTAGE: draw an edge for every shared `link` -- one department address
    relates every file in the corpus to every other, and `is_typed_support`
    answers True for all of them.
    """
    _file(corpus, "one", "a.pdf")
    _file(corpus, "two", "b.pdf")
    for file_id in ("one", "two"):
        _observation(corpus, file_id, zone="link", value="registrar@school.edu")
        _observation(corpus, file_id, zone="link",
                     value="https://school.edu/handbook")

    assert _edges(corpus, "one") == ()


def test_the_new_edges_go_into_the_real_graph_builder_unchanged(corpus):
    """The end-to-end claim: `build_node_local_graph` accepts these dicts.

    It raises `ValueError` on an edge type it does not know, which is what a
    spelling invented at this seam would have done on the first row -- the same
    property `test_cli_p9_p11_edge_seam.py` holds for P9's five.
    """
    from placement.config import PlacementLimits
    from placement.records import Subject
    from placement.retrieval import Candidate
    from placement.vocabulary import FILE

    _file(corpus, "msg", "thread.eml")
    _file(corpus, "part", "invoice.pdf")
    _attachment(corpus, "msg", "invoice.pdf")

    graph = build_node_local_graph(
        subject=Subject(kind=FILE, file_id="msg", content_hash=_hash("msg"),
                        group_id=None, member_file_ids=()),
        candidate=Candidate(node_id="n-1", channels=(), matching_facts=(),
                            group_ids=()),
        entry=type("E", (), {"representative_files": ("part",)})(),
        related_files=_edges(corpus, "msg"),
        limits=PlacementLimits(
            max_retrieved_neighbors=4, max_local_graph_neighborhood=3,
            max_candidate_cluster_size=6, max_residual_files_per_batch=50,
            max_dossier_tokens=4000, max_llm_calls_per_thousand_files=100,
            max_cost_per_scan=5),
        entity_frequency={}, generic_entity_frequency=200)

    assert [anchor.edge_type for anchor in graph.anchors] == ["attachment_of"]
