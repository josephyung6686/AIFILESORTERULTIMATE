"""One file, one model answer, nothing behind it — that is a clue, not a folder.

`00`:42 is explicit that a model output "useful but too weak to establish a fact
may remain a possible clue for review; it must not quietly become a folder
proposal or an asserted file property". `PROPOSAL_ELIGIBLE_STATES` admits the
whole ladder above `possible`, which is the right bar for a value several files
carry and far too low for one file saying something once — and a LEVEL is the
strongest assertion this product makes about a value, because it becomes a folder
the person is shown and offered.

MEASURED ON THE OWNER'S 199 FILES (the `gt-cloud` run behind `104` §11). Every
`school` value in that run is `llm_supported`, and eight of the twelve were stated
by exactly one file. The tree grew a `Cliffs Notes` level — a study-guide
publisher — and a `Dr. Beer`, a `Robert Beer` (an instructor), a `Hong Kong` (a
place), a `DF 205` and a `University Writing`. Two PDFs that should have stayed
"ask the person" were filed into `Coursework/Cliffs Notes/notes`. Against that,
`subject` carried `E1006` on five files and `ELTU3017` on three, both `validated`.

`104` §11.2 step 3 names the rule: "P10 may not mint a `subject` or `school` node
from one `llm_supported` value with no direct or validated anchor and no group;
such a value is a candidate for review." Two ways out and a value needs only one —
an anchor (some file states it more strongly) or a group (more than one file
states it).

THE FIELD IS NOT NAMED ANYWHERE. `104` writes the example as `subject`, and the
run minted `Cliffs Notes` as a `school`; a rule keyed to either word would have
missed the defect it was written for. The predicate is reliability and count, and
it is applied at every level alike.
"""
from __future__ import annotations

import json

import pytest

from database_agent.files_table import get_file, record_file
from evidence_shape.location import Location, Segment
from evidence_shape.observation import Observation
from evidence_shape.runs import ExtractionRun
from evidence_shape.store import record_observation, record_run
from facts.file_facts import write_fact
from facts.states import LLM_SUPPORTED, VALIDATED
from facts.values import ensure_value
from grouping.vocabulary import DIRECT_ANCHOR
from tree_design.materialise import materialise_branch
from tree_design.routing import CompositionCandidate, ResolvedDimension
from tree_design.upstream import GroupMember
from tree_design.vocabulary import ACTION_SELECTED, SCOPE_SCHEMA_FIELD

CLOCK = "2026-08-27T00:00:00+00:00"
ONE_CLASS = lambda member: "personal_non_sensitive"
PROTECTED_CLASSES = frozenset({"highly_sensitive_credential_bearing"})


@pytest.fixture()
def seeded(conn, tmp_path):
    from evidence_shape.schema import create_evidence_schema

    create_evidence_schema(conn)
    return _Corpus(conn, tmp_path)


class _Corpus:
    """Files whose facts this test chooses the RELIABILITY of.

    `p10/p6_fixtures.py` writes everything `validated`, which is the anchored case
    and cannot express the defect. Every row here still goes through the live
    writers, for the reason that fixture gives: a materialiser tested against a
    stubbed fact reader proves nothing about the seam it exists to cross.
    """

    def __init__(self, conn, tmp_path):
        self.conn = conn
        self.tmp_path = tmp_path
        self.by_name: dict[str, tuple[str, str, str]] = {}

    def file(self, name: str) -> tuple[str, str, str]:
        if name in self.by_name:
            return self.by_name[name]
        raw = f"{name} contents"
        path = self.tmp_path / f"{name}.pdf"
        path.write_bytes(raw.encode("utf-8"))
        file_id = record_file(
            self.conn, path, filename=path.name,
            normalized_filename=path.name.lower(), extension=".pdf",
            observed_size=len(raw),
            observed_timestamps=json.dumps({"mtime": 1_700_000_000.0}),
            parent_folder_context="Downloads", mime_type="application/pdf",
            detected_format="pdf", scan_state="included", materialized=True)
        content_hash = get_file(self.conn, file_id)["content_hash"]
        record_run(self.conn, ExtractionRun(
            run_id=f"r_{name}", file_id=file_id, content_hash=content_hash,
            extractor_name="pdf.text", extractor_version="1.0.0",
            source_type="text_document", analysis_tier="native", config={},
            completeness="complete", started_at=CLOCK, finished_at=CLOCK))
        observation = Observation(
            file_id=file_id, content_hash=content_hash, extractor_name="pdf.text",
            extractor_version="1.0.0", source_type="text_document", raw_value=raw,
            location=Location("heading", (Segment("field", label="heading"),)),
            occurrence_count=1, observed_at=CLOCK, reliability="possible",
            run_id=f"r_{name}")
        record_observation(self.conn, observation)
        self.by_name[name] = (file_id, content_hash, observation.observation_key)
        return self.by_name[name]

    def fact(self, name: str, field_key: str, value: str, state: str) -> None:
        file_id, content_hash, key = self.file(name)
        value_id = ensure_value(
            self.conn, field_key=field_key, canonical_value=value,
            first_evidence_ref=key, origin="automatic")
        write_fact(
            self.conn, file_id=file_id, content_hash=content_hash,
            field_key=field_key, value_id=value_id, reliability_state=state,
            origin="llm_interpretation" if state == LLM_SUPPORTED else "rule",
            evidence_refs=(key,),
            cache_key=f"ck_{file_id}_{field_key}_{value}", active=True)

    def members(self, *names: str) -> tuple[GroupMember, ...]:
        return tuple(
            GroupMember(file_id=self.file(name)[0],
                        content_hash=self.file(name)[1], basis=DIRECT_ANCHOR)
            for name in names)

    def file_id(self, name: str) -> str:
        return self.file(name)[0]


def _candidate(*pairs):
    return CompositionCandidate(
        applicability_refs=(), privacy_floor="policy.public",
        covered_file_ids=frozenset(), gates_passed=("C1",),
        overridden_gates=(),
        explanation="The academic coursework recipe matched this branch.",
        resolved_dimensions=tuple(
            ResolvedDimension(
                role_ref=role, field_ref=field, action=ACTION_SELECTED,
                order_index=index, display_label=None, scope=SCOPE_SCHEMA_FIELD)
            for index, (role, field) in enumerate(pairs)))


def _levels(corpus, field, *names):
    _, evidence = materialise_branch(
        corpus.conn, _candidate((field, field)), branch_node_id="n_academics",
        members=corpus.members(*names), ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES)
    return evidence


# --- the defect ------------------------------------------------------------------


def test_a_lone_model_supported_value_with_no_anchor_builds_no_level(seeded):
    """THE GUARD. One file, one model answer, no anchor and no second file.

    `Cliffs Notes` is a study-guide publisher and the file that named it is a
    study guide, not a course. Before this rule it became a folder.
    """
    seeded.fact("guide", "school", "Cliffs Notes", LLM_SUPPORTED)

    evidence = _levels(seeded, "school", "guide")

    assert evidence.levels[0].values == (), (
        "a folder was built from one model answer about one file, with no "
        "stronger fact and no second file behind it")


def test_that_file_is_left_for_the_person_rather_than_dropped(seeded):
    """`00`:42 keeps the clue. The fact stays on the file exactly as P6 wrote it;
    what does not happen is the folder. The file becomes unresolved AT THIS LEVEL,
    which is §5.11's own state and reaches the person as "waiting for you to say
    what this is"."""
    seeded.fact("guide", "school", "Cliffs Notes", LLM_SUPPORTED)

    evidence = _levels(seeded, "school", "guide")

    assert evidence.unresolved_by_field["school"] == frozenset(
        {seeded.file_id("guide")})
    still_there = seeded.conn.execute(
        "SELECT COUNT(*) FROM file_facts WHERE file_id = ? AND active = 1",
        (seeded.file_id("guide"),)).fetchone()[0]
    assert still_there == 1, "the clue was destroyed rather than held for review"


def test_the_field_is_never_named_so_the_same_rule_reaches_subject(seeded):
    """`104` writes the example as `subject`; the run minted it as a `school`. A
    rule keyed to either word would have missed the defect it was written for."""
    seeded.fact("guide", "subject", "Cliffs Notes", LLM_SUPPORTED)

    evidence = _levels(seeded, "subject", "guide")

    assert evidence.levels[0].values == ()


# --- the two ways out, each on its own --------------------------------------------


def test_an_anchored_value_still_builds_its_level(seeded):
    """A syllabus stating the course directly is the anchor `00`:63 names, and one
    file is enough when the fact is not a guess. `E1006` on five `validated` files
    is the measured case; one is the harder one and it passes."""
    seeded.fact("syllabus", "subject", "E1006", VALIDATED)

    evidence = _levels(seeded, "subject", "syllabus")

    assert evidence.levels[0].values == ("E1006",)
    assert evidence.unresolved_by_field["subject"] == frozenset()


def test_a_value_several_files_agree_on_still_builds_its_level(seeded):
    """The other way out. `Georgetown Preparatory School` is `llm_supported` on
    SEVEN files in the measured run and survives this rule — deliberately.

    It is also the WRONG level for five university essays, and that is a different
    defect with a different fix (`104` §11.2 step 1: the `school` glossary means
    the institution offering the course, not any school the person attended).
    Taking it here would have made this rule look like it worked while hiding the
    one that matters.
    """
    seeded.fact("essay-a", "school", "Georgetown Preparatory School", LLM_SUPPORTED)
    seeded.fact("essay-b", "school", "Georgetown Preparatory School", LLM_SUPPORTED)

    evidence = _levels(seeded, "school", "essay-a", "essay-b")

    assert evidence.levels[0].values == ("Georgetown Preparatory School",)
    assert evidence.unresolved_by_field["school"] == frozenset()


def test_one_unanchored_value_does_not_take_its_anchored_neighbour_with_it(seeded):
    """The twin that keeps this a correction rather than a demolition. Two values
    at one level, one anchored and one not: exactly one folder disappears."""
    seeded.fact("syllabus", "subject", "E1006", VALIDATED)
    seeded.fact("guide", "subject", "Cliffs Notes", LLM_SUPPORTED)

    evidence = _levels(seeded, "subject", "syllabus", "guide")

    assert evidence.levels[0].values == ("E1006",)
    assert evidence.unresolved_by_field["subject"] == frozenset(
        {seeded.file_id("guide")})


def test_a_second_file_stating_it_more_strongly_anchors_the_first(seeded):
    """The anchor need not be on the file being placed. `00`:63's stop rule is
    about the VALUE having something behind it, and a syllabus stating the course
    directly anchors every sparse member that names the same course."""
    seeded.fact("guide", "subject", "E1006", LLM_SUPPORTED)
    seeded.fact("syllabus", "subject", "E1006", VALIDATED)

    evidence = _levels(seeded, "subject", "guide", "syllabus")

    assert evidence.levels[0].values == ("E1006",)
    assert evidence.unresolved_by_field["subject"] == frozenset()
