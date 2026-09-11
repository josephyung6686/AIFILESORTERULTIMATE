"""`00`:109's ninth typed relationship, and the gesture it was waiting for.

`placement.graph.DESIGN_RELATIONSHIPS` carried eight producers and one empty
string. The ninth -- "user-confirmed membership" -- said in its own note that it
had *"none yet AS AN EDGE ... which needs a gesture P7 has not shipped"*, and the
missing half was never the edge. It was somebody to have spoken: §3.13's
`user_confirmed` is the strongest state P6 publishes and nothing could produce
it, so the screen printed a proposal and the only gesture on it was `--reject`.

`104` §18.2 gap 3 shipped the other one. `--confirm 'file:field=value'` reaches
`facts.learning.confirm_claim`, which supersedes the standing claim with a
`user_confirmed` row carrying the same evidence. This file is the edge that
becomes.

**What the edge is allowed to mean, and it is narrower than it looks.** A
confirmation is about ONE file. That one person said "yes, this file's subject is
PHYS1401" is not a statement about any other file, so an edge drawn from it would
put their name on a pairing they never made. The relationship is between two
files whose SHARED basis they BOTH confirmed -- and the basis has to be the one
the membership rests on, or a confirmed `work_type` on two files in a course
group would read as a ratified course membership nobody was asked about.

This file is the sibling of `test_cli_observation_edges.py` for the sibling
reason: the composition root produces this edge because P9 groups on evidence and
this one rests on a CORRECTION, which P6 owns and P9 never reads. P9 gains no
second engine.
"""
from __future__ import annotations

import hashlib

import pytest

import cli
from facts.fields import create_fields
from facts.file_facts import write_fact
from facts.states import POSSIBLE, USER_CONFIRMED
from facts.values import ensure_value
from grouping.records import Membership, Support
from grouping.schema import create_grouping_schema
from grouping.store import record_membership
from grouping.vocabulary import (
    DIRECT_ANCHOR, EXCLUDED, INCLUDED, NOT_FLAGGED, RULES,
    SHARED_VALIDATED_FACT,
)

AT = "2026-09-10T00:00:00+00:00"
GROUP = "group:subject=PHYS1401"
FIELD = "subject"
VALUE = "PHYS1401"


def _hash(file_id: str) -> str:
    return hashlib.sha256(file_id.encode("utf-8")).hexdigest()


def _ref(file_id: str, field: str) -> str:
    """A P4 observation key. `facts.values.ensure_value` refuses anything else for
    an automatically created value -- §3.1, a value cites the observation that
    introduced it -- so the fixture uses P4's own shape rather than a short name."""
    return f"sha256:{_hash(file_id + field)}"


@pytest.fixture()
def corpus(conn):
    create_grouping_schema(conn)
    create_fields(conn)
    return conn


def _member(conn, file_id: str, *, group: str = GROUP, field: str = FIELD,
            decision: str = INCLUDED, superseded_by: str | None = None) -> None:
    """One live membership, with the support that says WHY the file belongs.

    `quote_or_field` is the field the membership rests on, and it is what ties a
    confirmation to a membership: P9 records it because the shared-validated-fact
    channel is the reason this file is in this group.
    """
    record_membership(conn, Membership(
        membership_id=f"{group}:{file_id}", group_id=group, file_id=file_id,
        content_hash=_hash(file_id), basis=DIRECT_ANCHOR, decision=decision,
        decision_source=RULES,
        support=(Support(support_kind=SHARED_VALIDATED_FACT,
                         observation_key=_ref(file_id, field),
                         quote_or_field=field,
                         location=None, edge_ref=None),),
        insufficient_evidence=False, insufficiency_statement=None,
        conflicts=(), outlier_flag=NOT_FLAGGED, validation_verdict_ref=None,
        created_at=AT, superseded_by=superseded_by))


def _fact(conn, file_id: str, *, state: str, field: str = FIELD,
          value: str = VALUE) -> None:
    ref = _ref(file_id, field)
    value_id = ensure_value(conn, field_key=field, canonical_value=value,
                            first_evidence_ref=ref, origin="automatic")
    write_fact(conn, file_id=file_id, content_hash=_hash(file_id),
               field_key=field, value_id=value_id, reliability_state=state,
               origin="deterministic_extractor", evidence_refs=(ref,),
               cache_key=f"sha256:{file_id}-{field}", active=True)


def _edges(conn, file_id: str):
    return cli.confirmed_membership_edges_of(
        file_id, confirmations=cli.confirmed_membership_index(conn))


def test_two_files_the_person_confirmed_are_related_by_a_typed_edge(corpus):
    """The producer, and the whole point of the row.

    Both files are in the course group on the same shared fact, and the person
    has confirmed that fact on each of them. That is the one thing a person can
    do today that says "these two belong together in my own words", and until
    this producer existed the graph had no way to carry it.

    UNDIRECTED: the anchor is whichever file is being placed. `attachment_of` is
    directed because the message is where the relationship was READ; nothing here
    is read out of one end, and neither confirmation came first in any sense the
    graph can use.
    """
    for file_id in ("syllabus", "notes"):
        _member(corpus, file_id)
        _fact(corpus, file_id, state=USER_CONFIRMED)

    (from_syllabus,) = _edges(corpus, "syllabus")
    assert from_syllabus["edge_type"] == "user_confirmed_membership"
    assert from_syllabus["to_file_id"] == "notes"
    assert from_syllabus["anchor_file_id"] == "syllabus"
    assert from_syllabus["to_content_hash"] == _hash("notes")

    (from_notes,) = _edges(corpus, "notes")
    assert from_notes["to_file_id"] == "syllabus"
    assert from_notes["anchor_file_id"] == "notes"


def test_an_unconfirmed_claim_draws_nothing(corpus):
    """The falsifying twin, and it is the assertion that keeps the edge honest.

    `possible` is what `normalize_for_review` writes for a value the product has
    proposed and nobody has answered -- `00`:57's HW 3.pdf. Two files carrying a
    proposal are related by the SHARED FACT edge, which P9 already draws and
    which says the product thinks so. This edge says the PERSON does, and drawing
    it from a proposal would be the product signing the person's name.
    """
    for file_id in ("syllabus", "notes"):
        _member(corpus, file_id)
        _fact(corpus, file_id, state=POSSIBLE)

    assert _edges(corpus, "syllabus") == ()
    assert _edges(corpus, "notes") == ()


def test_one_confirmation_relates_nothing_because_it_is_about_one_file(corpus):
    """§8.7's scope rule, arriving as a shape rather than as a policy.

    A person saying that one particular transcript belongs in a Columbia packet
    "should not teach the engine that all transcripts belong there" -- and it
    should not teach the graph that this transcript is related to every other
    file the engine had already grouped with it either. Both ends carry the
    confirmation or there is no edge.
    """
    _member(corpus, "syllabus")
    _fact(corpus, "syllabus", state=USER_CONFIRMED)
    _member(corpus, "notes")
    _fact(corpus, "notes", state=POSSIBLE)

    assert _edges(corpus, "syllabus") == ()
    assert _edges(corpus, "notes") == ()


def test_a_confirmed_value_the_membership_does_not_rest_on_draws_nothing(corpus):
    """The over-claim this producer is most likely to make, refused by name.

    Two files in one course group may both carry a confirmed `work_type`. That is
    a person answering about what KIND of document each one is; it is not a
    ratified membership of the course, and an edge reading "you confirmed these
    belong together" would claim they had answered a question nobody asked. So
    the confirmed field must be one the membership's own `support` cites, which
    is P9's record of why the file is in this group.
    """
    for file_id in ("syllabus", "notes"):
        _member(corpus, file_id, field=FIELD)
        _fact(corpus, file_id, state=USER_CONFIRMED, field="work_type",
              value="syllabus")

    assert _edges(corpus, "syllabus") == ()


def test_a_member_p9_retracted_is_not_paired(corpus):
    """A superseded membership is not a live one.

    `grouping.pipeline._retract_unsupported_memberships` supersedes a membership
    whose anchor fact is gone -- which is the route a `--reject` takes to P9 --
    and an excluded member is not in the group either. Pairing on a retracted
    membership would relate two files the product no longer believes are grouped,
    on the strength of a confirmation that was about the fact rather than about
    the pairing.
    """
    _member(corpus, "syllabus")
    _fact(corpus, "syllabus", state=USER_CONFIRMED)
    _member(corpus, "notes", decision=EXCLUDED)
    _fact(corpus, "notes", state=USER_CONFIRMED)

    assert _edges(corpus, "syllabus") == ()


def test_the_edge_reaches_the_node_local_graph_through_p11s_own_builder(corpus):
    """The seam, asked end to end: `build_node_local_graph` raises on a type it
    does not know, so a producer whose spelling P11 did not publish would fail on
    the first real corpus rather than here.

    `cli.NOT_A_P9_EDGE` is what keeps `test_cli_p9_p11_edge_seam.py` honest about
    it -- the type is P11's and P9 does not draw it, and that is stated rather
    than left as a hole in the translation table.
    """
    from placement.config import PlacementLimits
    from placement.graph import build_node_local_graph
    from placement.records import Subject
    from placement.retrieval import Candidate
    from placement.vocabulary import FILE

    for file_id in ("syllabus", "notes"):
        _member(corpus, file_id)
        _fact(corpus, file_id, state=USER_CONFIRMED)

    class _Entry:
        representative_files = ("notes",)

    limits = PlacementLimits(**{
        name: 10 for name in PlacementLimits.__dataclass_fields__})
    graph = build_node_local_graph(
        subject=Subject(kind=FILE, file_id="syllabus", content_hash="c" * 64,
                        group_id=None, member_file_ids=()),
        candidate=Candidate(node_id="node-1", channels=(), matching_facts=(),
                            group_ids=()),
        entry=_Entry(), related_files=_edges(corpus, "syllabus"),
        limits=limits, entity_frequency={}, generic_entity_frequency=200)

    assert graph.neighbourhood_size == 1
    assert graph.anchors[0].edge_type == "user_confirmed_membership"


def test_the_bridge_is_the_shared_fact_and_is_keyed_as_one(corpus):
    """§6.5's hub test is one `.get`, and it has to find this edge's entity.

    `fact_bridge_ref` is the one spelling both halves of that test use, so a
    confirmed `subject = PHYS1401` counts against the same entity frequency the
    inferred one does. That is the right answer rather than a convenient one: a
    course code on four hundred files is a generic entity whoever vouched for it,
    and an edge keyed on a second spelling would miss the lookup and answer 0 for
    ever -- which is the defect `104` R-59's third finding already cost once.
    """
    from grouping.vocabulary import fact_bridge_ref

    for file_id in ("syllabus", "notes"):
        _member(corpus, file_id)
        _fact(corpus, file_id, state=USER_CONFIRMED)

    (edge,) = _edges(corpus, "syllabus")
    assert edge["entity"] == fact_bridge_ref(FIELD, VALUE)
    assert edge["entity"] != VALUE


def test_the_ninth_relationship_now_names_its_producer(corpus):
    """`DESIGN_RELATIONSHIPS` is the census `104` §18.2 gap 12 built so the count
    could be checked instead of asserted, and one entry carried an empty producer.

    Both halves: nine relationships, and none of them left with nothing behind
    it. The ninth keeps the accepted-group CHANNEL as well as gaining the edge --
    they answer different questions, and dropping the channel would take the
    branch retrieval `00`:107 assigns to it away.
    """
    from placement.graph import (
        DESIGN_RELATIONSHIPS, EDGE_PRODUCER, EDGE_TYPES,
        USER_CONFIRMED_MEMBERSHIP,
    )

    assert [r.design_name for r in DESIGN_RELATIONSHIPS if not r.producer] == []
    (ninth,) = [r for r in DESIGN_RELATIONSHIPS
                if r.design_name == "user-confirmed membership"]
    assert ninth.producer == "cli.confirmed_membership_edges_of, from `--confirm`'s own rows"
    assert USER_CONFIRMED_MEMBERSHIP in ninth.carried_by
    assert "retrieval.accepted_group" in ninth.carried_by
    # Every edge type the graph publishes tells the model what produced it.
    assert set(EDGE_TYPES) == set(EDGE_PRODUCER)
