# tests/p9/test_p9_group_naming.py
"""What a live P9 run says a group IS -- and what it refuses to say.

`src/grouping/pipeline.py` wrote `coherence_verdict`, `group_category`,
`display_label` and `label_source` as `None` on every path, and
`apply_p8_verdict` wrote none of them either. The cost was not local:
`AcceptedGroup.domain` carries P9's `group_category`, so it was always `None`,
so `BranchContext.domains` was always empty, so `route_branch` answered C3 for
every branch on every corpus and all 208 shipped applicability rows were
unreachable from a live run.

Every test here drives the real chain. The P6 facts are written through P6's own
writers, the groups are P9's through `group_subject`, and the routing half calls
`tree_design.upstream.accepted_groups` and `tree_design.routing.route_branch`
over the SHIPPED catalogue. A hand-built `AcceptedGroup` or a literal
`BranchContext.domains` here would prove only that this file and P10 agree about
a value neither of them got from P9.

Each guard has its negative twin, because the positive half of a monotone
property cannot tell a right answer from a confident wrong one:

    a named group  <-> a group whose facts name no domain, still `None`
    a recognised category <-> an unrecognised one, refused
    the engine speaks <-> the engine below its own bar, silent
    P10 routes it <-> P10 refuses it visibly, and does not drop it
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
from facts.domains import SCHEMA_IDS
from grouping.acceptance import record_acceptance
from grouping.config import GroupingLimits
from grouping.embeddings import EmbeddingsOff
from grouping.naming import domain_for, engine_proposal, label_for, schemas_referencing
from grouping.pipeline import GroupingKnowledge, group_subject
from grouping.records import Group, GroupAcceptance, MalformedGroupRecord
from grouping.retrieval import RetrievalKnowledge
from grouping.schema import create_grouping_schema
from grouping.store import (
    current_group,
    memberships_for_group,
    stop_rule_outcome_for,
)
from grouping.vocabulary import (
    ACCEPTED,
    CANDIDATE,
    COHERENT,
    ENGINE,
    PENDING_REVIEW,
    SUPPORTED,
    USER,
)

T0 = "2026-08-27T00:00:00Z"
PLAN = "plan-1"

#: P7's classification for an ordinary file in these corpora.
ORDINARY_CLASS = "personal_non_sensitive"

#: The one situation the shipped library recognises for coursework. The whole
#: `academic` schema unioned collides on C4; one row is what composes.
SIGNAL = "recognition:academic.coursework"


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


def _classified(handling_class=ORDINARY_CLASS):
    from privacy.classification import ClassificationRecord

    def store(file_id, content_hash):
        return ClassificationRecord(
            file_id=file_id, content_hash=content_hash,
            handling_class=handling_class, protected=False, basis="detector",
            evidence_refs=("sha256:" + "a" * 64,), reliability_state="direct",
            observed_at=T0)
    return store


def _limits(**over) -> GroupingLimits:
    values = dict(
        max_retrieved_neighbors=50, max_graph_nodes=10, max_candidate_members=10,
        max_dossier_tokens=4000, generic_hub_frequency=9,
        minimum_independent_anchors=1, max_excerpt_characters=240)
    values.update(over)
    return GroupingLimits(**values)


def _knowledge(**over) -> GroupingKnowledge:
    values = dict(
        retrieval=RetrievalKnowledge(
            document_compatible=None, channel_weights={}, similarity=None,
            similarity_threshold=None, embedding_identity=None, domain=None),
        active_schema_for=lambda c, f, h: ("school", "subject", "work_type"),
        signal_evaluator_for=lambda domain: True,
        classification_store=_classified(),
        conflicts_for=lambda files: (),
        duplicate_or_version=None,
    )
    values.update(over)
    return GroupingKnowledge(**values)


def _group_subject(conn, subject, **over):
    file_id, content_hash = subject
    values = dict(
        plan_version_id=PLAN, limits=_limits(), knowledge=_knowledge(),
        user_seed_for=lambda f, h: None, p8_run_call=None, p8_authorities=None,
        embeddings=EmbeddingsOff(), created_at=T0)
    values.update(over)
    return group_subject(
        conn, file_id=file_id, content_hash=content_hash, **values)


def _coursework(conn, tmp_path):
    """Three files a person actually has, with the facts P6 would validate.

    `school` is the seed: `seeds_for_file` orders anchors by field key and
    `school` sorts first, so the group's basis is the school every file states.
    """
    subjects = []
    for index, (name, school) in enumerate((
        ("Columbia PHYS1401 Syllabus.pdf", "Columbia"),
        ("Columbia PHYS1401 Homework.pdf", "Columbia"),
        ("NYU BUSIB4300 Syllabus.pdf", "NYU"),
    )):
        subject = _file(conn, tmp_path, name, body=name.encode())
        file_id, content_hash = subject
        for field, value in (("school", school),
                             ("subject", "PHYS1401" if school == "Columbia"
                              else "BUSIB4300"),
                             ("work_type", "syllabus" if "Syllabus" in name
                              else "homework")):
            _fact(conn, file_id=file_id, content_hash=content_hash,
                  field=field, value=value, run_id=f"r{index}-{field}")
        subjects.append(subject)
    return subjects


def _cross_domain(conn, tmp_path):
    """One file whose only anchor is `project` -- a key EIGHT schemas reference.

    Research, code, business operations, law practice, creative, construction,
    engineering and government all claim it. Nothing about this file says which,
    and that is the state `None` exists to express.
    """
    subject = _file(conn, tmp_path, "Notes.pdf", body=b"PVA/RDP notes")
    file_id, content_hash = subject
    _fact(conn, file_id=file_id, content_hash=content_hash,
          field="project", value="PVA/RDP", run_id="r-project")
    return subject


# --- A. the live chain, P9 into P10 -----------------------------------------------


class _Reader:
    """The enumeration P9 does not publish, over P9's own shipped readers.

    `tree_design.upstream.AcceptedGroupReader` names four calls and says three of
    them map onto `grouping.store` today; `accepted(plan_version_id)` is the one
    with no P9 home. It is written here rather than worked around inside P10,
    which is what that docstring asks for, and every group, membership and stop
    rule it hands over is read back out of P9's own tables.
    """

    def __init__(self, conn):
        self.conn = conn

    def accepted(self, plan_version_id):
        from grouping.acceptance import group_state_as_of

        rows = self.conn.execute(
            "SELECT * FROM group_acceptance WHERE plan_version_id = ? "
            "AND superseded_by IS NULL ORDER BY group_id", (plan_version_id,)
        ).fetchall()
        return tuple(
            GroupAcceptance(
                acceptance_id=row["acceptance_id"],
                plan_version_id=plan_version_id, group_id=row["group_id"],
                membership_id=row["membership_id"],
                # P9's own answer, asked per group rather than read off the row.
                acceptance=group_state_as_of(
                    self.conn, group_id=row["group_id"],
                    plan_version_id=plan_version_id),
                review_state=row["review_state"],
                user_edited_label=row["user_edited_label"],
                aliases=tuple(json.loads(row["aliases"] or "[]")),
                review_decision_ref=row["review_decision_ref"],
                decided_by=row["decided_by"], created_at=row["created_at"])
            for row in rows)

    def group(self, group_id):
        return current_group(self.conn, group_id)

    def memberships(self, group_id):
        return memberships_for_group(self.conn, group_id)

    def stop_rule_outcome(self, group_id):
        return stop_rule_outcome_for(self.conn, group_id)


def _accept(conn, group_id):
    record_acceptance(conn, GroupAcceptance(
        acceptance_id=f"acc:{group_id}", plan_version_id=PLAN,
        group_id=group_id, membership_id=None, acceptance=ACCEPTED,
        review_state=PENDING_REVIEW, user_edited_label=None, aliases=(),
        review_decision_ref=None, decided_by=USER, created_at=T0))


def _accepted_groups(conn):
    from tree_design.upstream import accepted_groups

    return accepted_groups(_Reader(conn), plan_version_id=PLAN)


def _route(conn, groups, *, signals):
    from tree_design.config import TreeLimits
    from tree_design.routing import BranchContext, route_branch
    from production import load_shipped_catalogue, read_packaged_library_file

    context = BranchContext(
        branch_node_id="n_branch",
        # NOT a literal. Exactly what `tree_design.pipeline._route` builds, from
        # the domain P9 wrote: if P9 writes none, this is empty and C3 fires.
        domains=tuple(dict.fromkeys(
            group.domain for group in groups if group.domain is not None)),
        accepted_groups=tuple(groups),
        member_file_ids=frozenset(
            member.file_id for group in groups for member in group.members),
        handling_classes=frozenset({ORDINARY_CLASS}),
        detection_signals=frozenset(signals))
    report = route_branch(
        conn, load_shipped_catalogue(read_packaged_library_file), context,
        limits=TreeLimits(
            max_folder_proposals_and_depth=5, max_dossier_tokens=4000,
            excessive_depth_warning=4, tiny_folder_max_files=1,
            tiny_folder_count_warning=4,
            materially_improves_retrieval=lambda _option: True),
        privacy_rank=lambda floor: 0,
        satisfies_purpose_profile=lambda ref, groups: True,
        rank_candidates=lambda candidates: list(candidates))
    return context, report


def test_a_live_p9_run_produces_a_group_p10_can_route(live, tmp_path):
    """THE defect, end to end and from the live chain only.

    P9 wrote no category, so `AcceptedGroup.domain` was `None`, so
    `BranchContext.domains` was empty, so `route_branch` answered C3 -- "no
    applicability row makes any recipe eligible" -- for every branch on every
    corpus, and none of the 208 shipped rows could ever be reached.

    Nothing below is hand-assembled. The facts are P6's, the group is P9's, the
    `AcceptedGroup` is `tree_design.upstream`'s over P9's own tables, and the
    catalogue is the shipped one.
    """
    subjects = _coursework(live, tmp_path)
    made = [_group_subject(live, subject) for subject in subjects]
    groups = [result.group for result in made if result.group is not None]
    assert groups, "P9 made no group at all, which is a different failure"
    for group in groups:
        _accept(live, group.group_id)

    accepted = _accepted_groups(live)
    assert accepted
    assert {group.domain for group in accepted} == {"academic"}

    context, report = _route(live, accepted, signals={SIGNAL})
    assert context.domains == ("academic",)
    assert report.candidates, [
        (conflict.gate, conflict.explanation) for conflict in report.conflicts]
    assert "C3" not in {conflict.gate for conflict in report.conflicts}


def test_a_group_whose_facts_name_no_domain_is_none_and_still_reaches_p10(
        live, tmp_path):
    """The negative twin, and the one that matters more.

    `project` is referenced by eight schemas. Nothing about this file chooses
    between them, so the honest answer is `None` -- not `research` because it
    sorts first, and not `code` because it is common. A confident wrong domain
    files somebody's matters into their coursework; `None` routes to a refusal
    they can read.

    And `None` must survive the whole way down: the group is still named, still
    enumerated by `accepted_groups`, and still carried into the branch. What it
    is not is routable, and P10 says so by gate rather than by dropping it.
    """
    subject = _cross_domain(live, tmp_path)
    result = _group_subject(live, subject)
    assert result.group is not None
    assert result.group.group_category is None
    # Coherent and named without a domain: the pairing is the point.
    assert result.group.coherence_verdict == COHERENT
    assert result.group.display_label == "PVA/RDP"
    _accept(live, result.group.group_id)

    accepted = _accepted_groups(live)
    assert [group.domain for group in accepted] == [None]
    assert [group.label for group in accepted] == ["PVA/RDP"]

    context, report = _route(live, accepted, signals={SIGNAL})
    assert context.domains == ()
    assert not report.candidates
    assert "C3" in {conflict.gate for conflict in report.conflicts}


def test_a_domain_that_did_not_activate_is_still_offered_on_the_canvas(
        live, tmp_path):
    """`2a1834e`: a group whose domain is outside `active_domains` used to be
    dropped from `horizontal_candidates` with no record anywhere, which is how a
    multi-life person loses a whole life. This fix feeds that path; it must not
    undo it. So a live-P9 `academic` group survives an activation set that does
    not name `academic`, and its card says why."""
    from tree_design.candidates import horizontal_candidates

    subjects = _coursework(live, tmp_path)
    for subject in subjects:
        result = _group_subject(live, subject)
        if result.group is not None:
            _accept(live, result.group.group_id)
    accepted = _accepted_groups(live)
    assert {group.domain for group in accepted} == {"academic"}

    candidates = horizontal_candidates(
        live, accepted=accepted, existing_folders=(), user_labels=(),
        active_domains=("finance",), sensitive_group_ids=frozenset())
    assert candidates, "the group vanished with its domain, which is the defect"
    assert any("did not activate" in candidate.why_suggested
               for candidate in candidates)
    assert any("academic" in candidate.why_suggested
               for candidate in candidates), "the card names the schema P9 wrote"


# --- B. where the category comes from ---------------------------------------------


def test_every_category_a_live_run_writes_is_one_the_product_recognises(
        live, tmp_path):
    for subject in _coursework(live, tmp_path):
        result = _group_subject(live, subject)
        assert result.group.group_category in SCHEMA_IDS


def test_a_category_the_product_does_not_recognise_is_refused(live):
    """The negative twin. A monotone "it is in the set" check cannot tell a
    derived value from a substituted one; this is the half that can.

    `course` and `application` read like categories and are not domains. M12
    settled that `group_category` IS the domain vocabulary, and P10 selects an
    applicability row BY it -- so one the product does not recognise reaches no
    row, answers C3, and is indistinguishable from a library with no template.
    """
    from grouping.store import record_group

    def _with(category):
        return Group(
            group_id="g-1", seed_ref="f:h", seed_kind="strongly-identified-file",
            proposed_basis="subject=PHYS1401", anchor_facts=(),
            pre_model_signals={}, anchor_count=0, coherence_verdict=COHERENT,
            coherence_citations=(), group_category=category,
            display_label="PHYS1401", label_source=ENGINE, conflicts=(),
            stop_rule_hits=(), state=SUPPORTED, sensitivity_state="none",
            dossier_id=None, llm_response_ref=None, validation_verdict_ref=None,
            created_by="rules", created_at=T0)

    for rejected in ("course", "application", "Academic", "academic "):
        with pytest.raises(MalformedGroupRecord) as excinfo:
            _with(rejected)
        assert "SCHEMA_IDS" in str(excinfo.value)
    # And the writer never sees one either, because the record refuses first.
    assert record_group(live, _with("academic")) == "g-1"


def test_the_domain_vocabulary_is_read_from_p6_and_spelled_nowhere_here():
    """P9 authors no domain. `_SCHEMAS_BY_FIELD` is inverted from P6's own
    `schema_fields`, so a schema added upstream -- ten became twenty-three --
    moves this with it instead of leaving a stale copy behind."""
    import pathlib

    from facts.domains import schema_fields

    source = pathlib.Path("src/grouping/naming.py").read_text()
    for schema_id in SCHEMA_IDS:
        assert f'"{schema_id}"' not in source, schema_id
        for field_key in schema_fields(schema_id):
            assert schema_id in schemas_referencing(field_key)


def test_the_three_field_less_safety_domains_are_never_derived():
    """`identity`, `medical` and `legal` carry no P6 field, so no anchor fact can
    point at one and the engine returns `None` for a group of passports.

    That is the safe answer, not a gap. P7 is the part that decides a file is
    identity material, and it says so through the handling class that travels
    beside the group and keeps a protected container marked, counted and unopened.
    A `group_category` P9 invented here would be a second, weaker claim about the
    same thing -- and it would route the passports into a template.
    """
    from facts.domains import FIELD_LESS_SCHEMA_IDS

    assert set(FIELD_LESS_SCHEMA_IDS) == {"identity", "medical", "legal"}
    derivable = {
        schema_id
        for field_key in _every_field_key()
        for schema_id in schemas_referencing(field_key)
    }
    assert derivable.isdisjoint(FIELD_LESS_SCHEMA_IDS)


def _every_field_key():
    from facts.domains import schema_fields

    return {field_key for schema_id in SCHEMA_IDS
            for field_key in schema_fields(schema_id)}


def test_the_domain_is_the_intersection_and_not_a_first_match():
    """Two facts that agree sharpen the answer; two that disagree remove it.

    `work_type` alone is four schemas and names none. Beside `school` it is
    academic, because that is the only reading both facts allow. Beside
    `employer` it is two lives at once, and §3.11's "activation adds; it never
    chooses" leaves nothing to choose from.
    """
    from grouping.records import AnchorFact

    def fact(field, value):
        return AnchorFact(field=field, value=value, file_ids=("f",),
                          reliability_state="validated", observation_key=f"o:{field}")

    assert domain_for((fact("school", "Columbia"),)) == "academic"
    assert domain_for((fact("work_type", "homework"),)) is None
    assert domain_for(
        (fact("school", "Columbia"), fact("work_type", "homework"))) == "academic"
    assert domain_for(
        (fact("school", "Columbia"), fact("employer", "EY"))) is None
    assert domain_for(()) is None
    assert label_for((fact("subject", "PHYS1401"), fact("term", "Spring 2026"))) == (
        "PHYS1401 — Spring 2026")


# --- C. when the engine speaks, and when it does not -------------------------------


def test_a_group_at_the_independent_anchor_bar_is_named_by_the_engine(
        live, tmp_path):
    """§4.9's bar is a COUNT over facts P6 validated, not an interpretation, so
    reporting it is not P9 synthesising a verdict. `label_source` says who spoke."""
    subject = _coursework(live, tmp_path)[0]
    group = _group_subject(live, subject).group
    assert group.state == SUPPORTED
    assert group.coherence_verdict == COHERENT
    assert group.label_source == ENGINE
    assert group.display_label == "Columbia"
    assert group.coherence_citations, "a verdict cites the evidence for it"
    # And it is what was STORED, not what was returned.
    assert current_group(live, group.group_id) == group


def test_a_group_below_the_support_bar_is_left_unjudged(live, tmp_path):
    """The negative twin: the SPEC's third row. A group the engine's own rule
    does not settle keeps its anchor memberships and carries NO verdict and NO
    label, which is the honest thing for a deployment with no model to show."""
    subject = _coursework(live, tmp_path)[0]
    result = _group_subject(live, subject, limits=_limits(
        minimum_independent_anchors=4))
    group = result.group
    assert group.state == CANDIDATE
    assert group.coherence_verdict is None
    assert group.group_category is None
    assert group.display_label is None
    assert group.label_source is None
    assert result.memberships, "the anchor memberships stay intact"


def test_a_group_a_stop_rule_destroyed_is_never_named(live, tmp_path):
    """SR1: no valid anchor. The verdict is written between the stop rules and
    `record_group`, so a group that never forms never acquires one -- a label on
    material SR4 destroyed would be a claim about a group that does not exist."""
    subject = _file(live, tmp_path, "Untitled.pdf", body=b"no facts")
    from grouping.seeds import UserSeed

    result = _group_subject(
        live, subject,
        user_seed_for=lambda f, h: UserSeed(
            file_id=f, content_hash=h, basis="the user started here",
            decided_at=T0))
    assert result.stop_rule_outcome is not None
    assert result.group.coherence_verdict is None
    assert result.group.display_label is None


def test_an_engine_coherent_group_can_always_be_named(live, tmp_path):
    """The property that keeps P10 from raising.

    `tree_design.upstream._label` raises `UpstreamUnavailable` for an accepted
    group with no label and no user edit -- for the whole plan version, not just
    that group. So the engine's verdict and its label must be written together
    or not at all, and this is the check that they are.
    """
    subjects = [*_coursework(live, tmp_path), _cross_domain(live, tmp_path)]
    for subject in subjects:
        group = _group_subject(live, subject).group
        if group is None:
            continue
        assert (group.coherence_verdict == COHERENT) == (
            group.display_label is not None)


def test_naming_a_group_reads_the_record_and_opens_nothing(live, tmp_path):
    """The standing rule, at this seam. `engine_proposal` takes one argument and
    it is the group: with no connection and no path it cannot open a container,
    so no protected file can be read to name the group it is in. A corpus P7
    declined to classify still forms, is still counted, and is still named from
    the facts P6 already holds -- present, counted, never opened.
    """
    import inspect

    from privacy.classification import UNREADABLE_UNCLASSIFIED

    assert list(inspect.signature(engine_proposal).parameters) == ["group"]

    subject = _coursework(live, tmp_path)[0]
    result = _group_subject(live, subject, knowledge=_knowledge(
        classification_store=_classified(UNREADABLE_UNCLASSIFIED)))
    assert result.group.display_label == "Columbia"
    assert result.group.group_category == "academic"
    # Marked and counted, never opened: the dossier is refused and names it.
    assert result.dossier is None
    assert result.omissions, "a withheld file is named, never silently omitted"


# --- D. the model path ------------------------------------------------------------


def test_apply_p8_verdict_writes_no_category_and_no_label(live, tmp_path):
    """The decision, pinned so it cannot drift into an invention.

    §4.5 task 4 is the MODEL's: it proposes the label and the category, and P8's
    validator has a reason code for proposing them without coherence. But
    `P8Verdict` carries neither field, so the model's answer never arrives here.
    Deriving one from `result.outcome` would be P9 authoring the model's proposal
    on its behalf.

    The group on disk is byte-identical across the call: what P8 said is recorded
    where P8's answers live -- `validation_verdict_ref` on each membership.
    """
    from grouping.fixtures import course_dossier_fixture
    from grouping.p8_seam import apply_p8_verdict
    from p9.p8_fixtures import accepted_direct_verdict

    subject = _coursework(live, tmp_path)[0]
    group = _group_subject(live, subject).group
    before = current_group(live, group.group_id)

    dossier = course_dossier_fixture()
    verdict = accepted_direct_verdict(dossier_id=dossier.dossier_id)
    apply_p8_verdict(
        live, group=group, dossier=dossier, result=verdict,
        plan_version_id=PLAN, created_at=T0)

    after = current_group(live, group.group_id)
    assert after == before
    written = memberships_for_group(live, group.group_id)
    assert any(item.validation_verdict_ref == verdict.verdict_id
               for item in written)
