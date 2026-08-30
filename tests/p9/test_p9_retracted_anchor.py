# tests/p9/test_p9_retracted_anchor.py
"""What a retracted fact does to the membership that was built on it.

`--reject` retracts a claim: P6 supersedes the standing row with a `rejected`
one, and `read_surface.proposal_eligible` stops returning it. P9's SEED reader
goes through that surface, so the next run genuinely does not propose the group
again -- measured, and it is true.

The membership written on the FIRST run is a different record, and it was left
standing. `memberships_for_group` returns rows by `group_id` and asks nothing
about whether the evidence under them still stands, so the run that honoured the
retraction handed the group back to the caller with the retracted file still in
it -- and the person, who had just told the product it was wrong about that file,
was shown it filed under the same folder. Twice, in fact: once through the stale
membership and once through the group its surviving fact now seeds.

The SPEC decides this and does not leave it to taste.

  P9 SPEC, Provenance (§8.2): "Group and membership records key on `content_hash`
  alongside `file_id`, so a content change makes a membership's evidence STALE
  rather than silently re-pointing it at new bytes" -- and "A revised conclusion
  SUPERSEDES its predecessor with a recorded reason, and the earlier record stays
  inspectable."

  P11 SPEC, evidence_type: "§3.13's `rejected` is DROPPED: a rejected fact cannot
  support a placement, so a record resting on one would be a contradiction rather
  than a low-confidence decision."

So: superseded, not deleted, and carrying the evidence that produced it (§8.7).

The twin matters as much as the guard. A rejection is about ONE claim about ONE
file, and a fix that dropped the group, or every membership in it, would be a
blunt instrument wearing a correction's clothes: the person's OTHER PHYS1401 file
never had anything said against it, and it must be exactly where it was.
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
from facts.learning import reject_claim
from grouping.config import GroupingLimits
from grouping.embeddings import EmbeddingsOff
from grouping.pipeline import GroupingKnowledge, group_address, group_subject
from grouping.retrieval import RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.store import current_membership, memberships_for_group
from grouping.vocabulary import EXCLUDED, INCLUDED

T0 = "2026-08-27T00:00:00Z"
T1 = "2026-08-27T01:00:00Z"
PLAN = "plan-1"
ORDINARY_CLASS = "personal_non_sensitive"

#: P13's word for the gesture, which is the one `--reject` passes.
ACTION_REJECT = "reject"


# --- the corpus, through everybody's own writers ----------------------------------


@pytest.fixture()
def live(conn):
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
        parent_folder_context="Documents", mime_type="application/pdf",
        detected_format="pdf", scan_state="included", materialized=True)
    return file_id, get_file(conn, file_id)["content_hash"]


def _fact(conn, *, file_id, content_hash, field, value, run_id):
    """One P6 validated fact, through P6's own writers and nobody else's."""
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


def _classified():
    from privacy.classification import ClassificationRecord

    def store(file_id, content_hash):
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=ORDINARY_CLASS, protected=False, basis="detector",
            evidence_refs=("sha256:" + "a" * 64,), reliability_state="direct",
            observed_at=T0)
    return store


def _limits() -> GroupingLimits:
    return GroupingLimits(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)


def _knowledge() -> GroupingKnowledge:
    return GroupingKnowledge(
        retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=None,
            similarity_threshold=None, embedding_identity=None, domain=None),
        active_schema_for=lambda c, f, h: ("subject", "term"),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classified(),
        conflicts_for=lambda files: (),
        duplicate_or_version=None)


def _group_subject(conn, subject, *, created_at=T0):
    file_id, content_hash = subject
    return group_subject(
        conn, file_id=file_id, content_hash=content_hash, plan_version_id=PLAN,
        limits=_limits(), knowledge=_knowledge(),
        user_seed_for=lambda f, h: None, p8_run_call=None, p8_authorities=None,
        embeddings=EmbeddingsOff(), created_at=created_at)


@pytest.fixture()
def one_course(live, tmp_path):
    """Two files of one course, each stating the course and the term.

    Two files and not one, because the whole question is whether a correction
    about ONE of them stays about that one. `subject` sorts before `term`, so
    the seed of each is the course and the group they share is `PHYS1401`.
    """
    subjects = []
    for index, name in enumerate(("week 3.pdf", "week 4.pdf")):
        subject = _file(live, tmp_path, name, body=name.encode())
        file_id, content_hash = subject
        for field, value in (("subject", "PHYS1401"), ("term", "Spring2026")):
            _fact(live, file_id=file_id, content_hash=content_hash,
                  field=field, value=value, run_id=f"r{index}-{field}")
        subjects.append(subject)
    return subjects


def _members(conn, group_id) -> tuple:
    """Who the group still HAS, which is not the same as which rows it has.

    An `excluded` row is a record the group keeps deliberately -- §8.7 stores a
    rejected membership with its evidence, and `tree_design.upstream` reads them
    as `excluded_members`. `memberships_for_group` therefore returns it, and
    every question in this file is about membership rather than about rows.
    """
    return tuple(m for m in memberships_for_group(conn, group_id)
                 if m.decision == INCLUDED)


def _phys_group(results) -> str:
    labels = {result.group.group_id for result in results
              if result.group is not None}
    assert len(labels) == 1, (
        f"the two files of one course did not share one group: {labels}")
    return labels.pop()


# --- the guard ---------------------------------------------------------------------


def test_a_membership_built_on_a_retracted_fact_does_not_survive_the_next_run(
        live, one_course):
    """The person said the course was wrong. The file must leave the course.

    The first run puts both files in `PHYS1401`. The person rejects the claim
    about the first file only. The second run must not hand `PHYS1401` back with
    that file still in it -- which is what the report showed them, under the
    heading of the very folder they had just objected to.
    """
    week3, week4 = one_course
    group_id = _phys_group([_group_subject(live, s) for s in one_course])
    assert {m.file_id for m in _members(live, group_id)} == {
        week3[0], week4[0]}, "the first run did not put both files in the course"

    reject_claim(live, file_id=week3[0], content_hash=week3[1],
                 field_key="subject", value="PHYS1401", action=ACTION_REJECT,
                 user_id="jy", observed_at=T1)
    for subject in one_course:
        _group_subject(live, subject, created_at=T1)

    remaining = _members(live, group_id)
    assert week3[0] not in {m.file_id for m in remaining}, (
        "the file whose course the person retracted is still a member of that "
        "course; the correction was recorded, respected by the fact reader, and "
        "changed nothing anybody can see")


def test_the_retracted_membership_is_superseded_and_still_readable(
        live, one_course):
    """§8.2: superseded, never deleted, and it says why.

    A DELETE would satisfy the guard above and lose the record §8.7 requires --
    "rejected memberships are stored WITH their evidence" -- so what replaced it
    is checked here: an `excluded` row naming its predecessor, and the
    predecessor still on disk carrying the reason.
    """
    week3, _week4 = one_course
    group_id = _phys_group([_group_subject(live, s) for s in one_course])
    stale = next(m for m in _members(live, group_id)
                 if m.file_id == week3[0])

    reject_claim(live, file_id=week3[0], content_hash=week3[1],
                 field_key="subject", value="PHYS1401", action=ACTION_REJECT,
                 user_id="jy", observed_at=T1)
    _group_subject(live, week3, created_at=T1)

    was = current_membership(live, stale.membership_id)
    assert was.decision == INCLUDED, "the old row was rewritten, not superseded"
    assert was.superseded_by, "the old row was dropped without a successor"
    assert was.supersede_reason, (
        "a supersession with no reason leaves two rows and no account of why")

    now = current_membership(live, was.superseded_by)
    assert now.decision == EXCLUDED, now.decision
    assert now.supersedes == stale.membership_id
    assert now.support == stale.support, (
        "§8.7 stores a rejected membership WITH the evidence that produced it; "
        "this one cites nothing the person could inspect")


def test_a_rejection_about_one_file_leaves_the_other_file_where_it_was(
        live, one_course):
    """The twin. A correction is about one claim about one file.

    The second file shares the folder and was never mentioned. A fix that
    dropped the group, or swept every membership whose group had a retraction in
    it, would pass the guard above and take this file's home away from a person
    who never said anything was wrong with it.
    """
    week3, week4 = one_course
    group_id = _phys_group([_group_subject(live, s) for s in one_course])
    before = next(m for m in _members(live, group_id)
                  if m.file_id == week4[0])

    reject_claim(live, file_id=week3[0], content_hash=week3[1],
                 field_key="subject", value="PHYS1401", action=ACTION_REJECT,
                 user_id="jy", observed_at=T1)
    for subject in one_course:
        _group_subject(live, subject, created_at=T1)

    after = _members(live, group_id)
    assert [m.membership_id for m in after] == [before.membership_id], (
        "the untouched file's membership of the course did not survive a "
        "rejection about the OTHER file")
    assert after[0].superseded_by is None, (
        "the untouched file's membership was superseded by a correction that "
        "was never about it")


def test_the_surviving_fact_still_seeds_its_own_group(live, one_course):
    """And the retraction is not a demolition either.

    `week 3.pdf` still states `term = Spring2026`, which nobody rejected. After
    the correction it seeds the term group, and that membership is live: the
    file is not erased from the plan, it is filed by what is left standing about
    it. A fix that superseded every membership of the file would pass the first
    guard by making the file disappear.
    """
    week3, _week4 = one_course
    _phys_group([_group_subject(live, s) for s in one_course])

    reject_claim(live, file_id=week3[0], content_hash=week3[1],
                 field_key="subject", value="PHYS1401", action=ACTION_REJECT,
                 user_id="jy", observed_at=T1)
    result = _group_subject(live, week3, created_at=T1)
    # TWICE, because once cannot tell a membership that survived from one that
    # was retired and rewritten in the same breath. A rule that retires every
    # membership of a re-read file passes a single run -- the row it just took
    # away is the row it is about to write -- and erases the file on the run
    # after that, which is the run the person would actually be looking at.
    _group_subject(live, week3, created_at=T1)

    assert result.group is not None, (
        "the file lost every group it had, including the one built on a fact "
        "nobody rejected")
    term_group = group_address(result.seeds[0])
    assert result.group.group_id == term_group
    live_ids = {m.file_id for m in _members(live, term_group)}
    assert week3[0] in live_ids, live_ids
