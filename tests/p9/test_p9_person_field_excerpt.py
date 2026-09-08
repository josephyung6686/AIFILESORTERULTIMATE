# tests/p9/test_p9_person_field_excerpt.py
"""`104` R-161's second half at SITE B: a signalled reading is withheld from the
group dossier's excerpts, and the group keeps its call.

WHY THIS SITE AND NOT THE OTHER TWO. The ruling's second half -- "make a signalled
observation be withheld from the offer instead of fatal to the request" -- was
already true where it had been built: `model_facts.may_be_released` drops a
signalled key at site A and `model_placement.releasable_excerpts` does the same at
site C, each of them one of the gate's own refusals asked a step early. Site B is
the third builder and had no such step: `grouping/p8_seam.build_dossier_request`
turns EVERY `dossier.excerpts` entry into a `ReleaseExcerpt`, so one signalled key
among twenty is `Denied(always_local_item)` for the whole group call.

THAT PATH IS REACHABLE AND WAS MEASURED, not imagined. On the owner's 199-file
corpus (`~/.graph-agent/lead/gt-w1bn`, read-only, 8 Sep 2026) **13 of the 95 active
P6 facts cite a person-valued metadata reading** -- every one a `duplicate_family`
fact, because an `observation_key` is content-addressed and two copies of one PDF
share their `/Author` row exactly. An `AnchorFact` carries its stating file's own
`observation_key` (`104` R-97) and `_excerpts_for` quotes it, so a group formed over
duplicates hands the door a signalled key.

The fact itself is NOT withheld. It travels in `key_facts` with its value, which is
`104` R-154's own answer to the same shape: "a fact whose only citations are
always-local is offered by its value with no citable item".
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
from extractors.long_tail import POTENTIALLY_SENSITIVE, record_sensitivity_signals
from extractors.long_tail import PERSON_VALUED_FIELD_BASIS, SensitivitySignal
from extractors.schema import create_extraction_schema
from grouping.config import GroupingLimits
from grouping.dossier import assemble_group_dossier
from grouping.graph import build_graph
from grouping.records import AnchorFact, CandidateGroupDossier, Group
from grouping.retrieval import Neighbor, Neighborhood
from grouping.seeds import Seed
from grouping.vocabulary import (
    CANDIDATE, RULES, SHARED_VALIDATED_FACT, STRONGLY_IDENTIFIED_FILE,
)
from privacy.classification import ClassificationRecord
from privacy.items import sensitive_observation_keys

T0 = "2026-09-08T00:00:00Z"
GROUP = "group-person"
AUTHOR = "Daniel Lacker"
COURSE = "PHYS1401 stated on the title page " + "x" * 200


@pytest.fixture()
def dossier_conn(conn):
    create_schema(conn)
    create_evidence_schema(conn)
    create_extraction_schema(conn)
    return conn


def _record(conn, tmp_path, name):
    path = tmp_path / name
    path.write_bytes(f"PHYS1401 {name}".encode("utf-8"))
    file_id = record_file(
        conn, path, filename=name, normalized_filename=name.lower(),
        extension=".pdf", observed_size=32,
        observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
        parent_folder_context="Downloads", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _observe(conn, *, file_id, content_hash, run_id, raw, zone, field):
    """One P4 reading at a `field` address -- P4 D7's own shape for a metadata slot."""
    record_run(conn, ExtractionRun(
        run_id=run_id, file_id=file_id, content_hash=content_hash,
        extractor_name="pdf.text", extractor_version="1.0.0",
        source_type="text_document", analysis_tier="native", config={},
        completeness="complete", started_at=T0, finished_at=T0))
    observation = Observation(
        file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
        extractor_version="1.0.0", source_type="text_document", raw_value=raw,
        location=Location(zone, (Segment("field", label=field),)),
        occurrence_count=1, observed_at=T0, reliability="direct", run_id=run_id)
    record_observation(conn, observation)
    return observation.observation_key


@pytest.fixture()
def corpus(dossier_conn, tmp_path):
    """Two files. Each states the course, and each carries the SAME `/Author` --
    which is what makes them a duplicate family and what puts the signalled key in
    front of the door."""
    made = {}
    for index, name in enumerate(("Lecture 3.pdf", "Lecture 3 copy.pdf")):
        file_id, content_hash = _record(dossier_conn, tmp_path, name)
        course_key = _observe(
            dossier_conn, file_id=file_id, content_hash=content_hash,
            run_id=f"run-course-{index}", raw=COURSE, zone="title", field="Title")
        author_key = _observe(
            dossier_conn, file_id=file_id, content_hash=content_hash,
            run_id=f"run-author-{index}", raw=AUTHOR, zone="metadata",
            field="Author")
        record_sensitivity_signals(
            dossier_conn, run_id=f"run-author-{index}",
            signals=(SensitivitySignal(observation_index=0,
                                       signal=POTENTIALLY_SENSITIVE,
                                       basis=PERSON_VALUED_FIELD_BASIS),),
            observation_keys=(author_key,), now=T0)
        made[name] = (file_id, content_hash, course_key, author_key)
    return made


def _limits() -> GroupingLimits:
    return GroupingLimits(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)


def _classified():
    def store(file_id, content_hash):
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class="public_low", protected=False, basis="detector",
            evidence_refs=("sha256:" + "a" * 64,), reliability_state="direct",
            observed_at=T0)
    return store


def _assemble(conn, corpus, facts):
    seed_id, seed_hash, seed_course, _ = corpus["Lecture 3.pdf"]
    other_id, other_hash, other_course, _ = corpus["Lecture 3 copy.pdf"]
    graph = build_graph(
        group_id=GROUP,
        neighborhood=Neighborhood(
            seed=Seed(seed_kind=STRONGLY_IDENTIFIED_FILE, file_id=seed_id,
                      content_hash=seed_hash, field_key="subject",
                      value="PHYS1401", reliability_state="validated",
                      observation_key=seed_course, basis=None),
            neighbors=(Neighbor(
                file_id=other_id, content_hash=other_hash,
                channel=SHARED_VALIDATED_FACT, anchors=True,
                evidence_ref=other_course, detail="subject=PHYS1401"),)),
        limits=_limits(), duplicate_or_version=None, created_at=T0)
    group = Group(
        group_id=GROUP, seed_ref="seed-1", seed_kind=STRONGLY_IDENTIFIED_FILE,
        proposed_basis="course_code=PHYS1401", anchor_facts=tuple(facts),
        pre_model_signals={}, anchor_count=len(facts), coherence_verdict=None,
        coherence_citations=(), group_category=None, display_label=None,
        label_source=None, conflicts=(), stop_rule_hits=(), state=CANDIDATE,
        sensitivity_state="none", dossier_id=None, llm_response_ref=None,
        validation_verdict_ref=None, created_by=RULES, created_at=T0)
    return assemble_group_dossier(
        conn, group=group, graph=graph, limits=_limits(),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classified(), conflicts=(), created_at=T0)


def _duplicate_family_fact(corpus) -> AnchorFact:
    """The shape 13 of the owner's 95 active facts have: one value, both files, and
    the reading behind it is the `/Author` row the two copies share."""
    seed_id, _sh, _course, author_key = corpus["Lecture 3.pdf"]
    other_id, _oh, _oc, other_author = corpus["Lecture 3 copy.pdf"]
    return AnchorFact(field="duplicate_family", value="family-1",
                      file_ids=(seed_id, other_id),
                      reliability_state="validated", observation_key=author_key,
                      observation_keys=(author_key, other_author))


def _course_fact(corpus) -> AnchorFact:
    seed_id, _sh, course_key, _ak = corpus["Lecture 3.pdf"]
    other_id, _oh, other_course, _ok = corpus["Lecture 3 copy.pdf"]
    return AnchorFact(field="subject", value="PHYS1401",
                      file_ids=(seed_id, other_id),
                      reliability_state="validated", observation_key=course_key,
                      observation_keys=(course_key, other_course))


def test_the_signal_is_readable_for_both_copies(dossier_conn, corpus):
    """The fixture's own premise, asserted so a fixture that stops reproducing the
    defect fails rather than passes (`104` R-150's rule)."""
    for name in corpus:
        file_id, _hash, _course, author_key = corpus[name]
        assert sensitive_observation_keys(dossier_conn, file_id) == frozenset(
            {author_key})


def test_a_signalled_reading_is_not_offered_as_a_group_excerpt(dossier_conn, corpus):
    """The withhold. Without it `build_dossier_request` hands the door a signalled
    key and the group's whole call comes back `Denied(always_local_item)`."""
    dossier = _assemble(dossier_conn, corpus,
                        [_course_fact(corpus), _duplicate_family_fact(corpus)])
    assert isinstance(dossier, CandidateGroupDossier)
    quoted = {excerpt.observation_key for excerpt in dossier.excerpts}
    signalled = {corpus[name][3] for name in corpus}
    assert not quoted & signalled, (
        "site B offered a reading P5 signalled; every item in a group request goes "
        "through the door together, so this costs the group its whole call")
    assert AUTHOR not in {excerpt.text for excerpt in dossier.excerpts}


def test_the_fact_itself_still_travels_and_so_does_every_other_excerpt(
        dossier_conn, corpus):
    """Withheld from the OFFER, not dropped from the dossier. `104` R-154's answer
    to the same shape: the fact is offered by its value with no citable item."""
    dossier = _assemble(dossier_conn, corpus,
                        [_course_fact(corpus), _duplicate_family_fact(corpus)])
    assert "duplicate_family" in {fact.field for fact in dossier.key_facts}
    quoted = {excerpt.observation_key for excerpt in dossier.excerpts}
    assert corpus["Lecture 3.pdf"][2] in quoted
    assert corpus["Lecture 3 copy.pdf"][2] in quoted


def test_a_group_whose_only_citation_is_signalled_still_assembles(
        dossier_conn, corpus):
    """The site-B twin of `fact_call_stage`'s empty-offer guard. A group left with
    no quotable excerpt is still a group with anchor files and facts, and P9's own
    refusal (`DossierRefused`) is about having no ANCHOR FILE, not no excerpt."""
    dossier = _assemble(dossier_conn, corpus, [_duplicate_family_fact(corpus)])
    assert isinstance(dossier, CandidateGroupDossier)
    assert dossier.anchor_files
    assert not {e.observation_key for e in dossier.excerpts} & {
        corpus[name][3] for name in corpus}
