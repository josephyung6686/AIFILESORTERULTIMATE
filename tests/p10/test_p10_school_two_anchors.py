"""`105` §14.4 at the tree: two anchors, independent, in one scope, or no level.

The owner ruled on 7 September 2026: "Answer school only when a permitted anchor
establishes the institution's relevant relationship to the course or enrollment
being organized, and create that scoped folder level only from two independently
originating, nonconflicting anchors, subject to the protected-document rule."

What that adds to `104` §11.2 step 2 is stated in the packet's own words. "Two
anchors agree" needed independence, because "two copies of one syllabus are one
source", and scope, because "documents from unrelated courses cannot jointly
establish a course's school". `104` R-131 is the row; `104` R-95 is the
measurement behind the filename half -- 38 `llm_supported` facts on 52 files,
every one a `school`, most of them the file's own name.

Every case below is a real group over real P6 rows, read through the reader
`tree_design.pipeline` builds, and the level case goes the whole way through
`materialise_branch` -- a value the reader returns is not yet a folder, and a
test that stopped at the reader could not tell the two apart.

**The rule governs the fields it is handed and no others.** The last test is the
guard for that: with no agreement, every field keeps the answer it had, which is
what "nothing here changes B" means for the term.
"""
from __future__ import annotations

import pytest

from evidence_shape.schema import create_evidence_schema
from facts.states import USER_CONFIRMED
from grouping.vocabulary import CONTEXT_SUPPORTED, DIRECT_ANCHOR
from tree_design.materialise import materialise_branch
from tree_design.routing import CompositionCandidate, ResolvedDimension
from tree_design.upstream import (
    AcceptedGroup,
    AnchorAgreement,
    GroupMember,
    group_level_reader,
)
from tree_design.vocabulary import ACTION_SELECTED, SCOPE_SCHEMA_FIELD

from p9.test_p9_retrieval import _fact, _file, _hash

SCHOOL, SUBJECT = "school", "subject"
DUPLICATE_FAMILY, VERSION_FAMILY = "duplicate_family", "version_family"
COLUMBIA, BARNARD = "Columbia", "Barnard"

#: The deployment's own agreement, as `cli.design_authorities` builds it, minus
#: the filename predicate: that one is injected per test, because whether a
#: citation IS the file's name is the composition root's question and this file
#: is about what the rule does with the answer.
AGREEMENT = AnchorAgreement(
    fields=frozenset({SCHOOL}),
    origin_fields=(DUPLICATE_FAMILY, VERSION_FAMILY),
    scope_field=SUBJECT)

#: P7 owns which classes are protected and publishes no ordering, so every caller
#: states it, exactly as `test_p10_materialise.py` does.
PROTECTED_CLASSES = frozenset({"highly_sensitive_credential_bearing"})
ONE_CLASS = lambda member: "personal_non_sensitive"


@pytest.fixture()
def corpus(conn):
    create_evidence_schema(conn)
    return conn


def _anchor(conn, tmp_path, name: str, *, school: str | None = COLUMBIA,
            subject: str | None = "BUSIB4300", folder: str = "Coursework",
            state: str = "validated", family: tuple[str, str] | None = None,
            ) -> GroupMember:
    """One direct anchor: a file, what it says, and how strongly it says it.

    `_file` writes the NAME as the file's bytes, so two anchors sharing a name in
    two folders share a content hash -- which is a copy, and is the fixture the
    independence half needs.
    """
    file_id = _file(conn, tmp_path, name, folder=folder)
    if school is not None:
        _fact(conn, file_id, field_key=SCHOOL, value=school,
              reliability_state=state, run_id=f"r-school-{folder}-{name}")
    if subject is not None:
        _fact(conn, file_id, field_key=SUBJECT, value=subject,
              run_id=f"r-subject-{folder}-{name}")
    if family is not None:
        field, value = family
        _fact(conn, file_id, field_key=field, value=value,
              run_id=f"r-family-{folder}-{name}")
    return GroupMember(file_id=file_id, content_hash=_hash(conn, file_id),
                       basis=DIRECT_ANCHOR)


def _carried(conn, tmp_path, name: str, *, subject: str = "BUSIB4300",
             folder: str = "Coursework") -> GroupMember:
    """`00`:57's sparse member: it states the course and not the school."""
    file_id = _file(conn, tmp_path, name, folder=folder)
    _fact(conn, file_id, field_key=SUBJECT, value=subject,
          run_id=f"r-subject-{folder}-{name}")
    return GroupMember(file_id=file_id, content_hash=_hash(conn, file_id),
                       basis=CONTEXT_SUPPORTED)


def _group(*members: GroupMember, group_id: str = "g_busib") -> AcceptedGroup:
    return AcceptedGroup(group_id=group_id, label="BUSIB 4300", domain="academic",
                         members=tuple(members), anchor_facts=(),
                         excluded_members=())


def _school_of(conn, group: AcceptedGroup, *, agreement=AGREEMENT,
               groups=None):
    reader = group_level_reader(conn, groups=groups or (group,),
                                agreement=agreement)
    return reader(group.members[0], SCHOOL)


def _candidate():
    return CompositionCandidate(
        applicability_refs=(), privacy_floor="policy.public",
        covered_file_ids=frozenset(), gates_passed=("C1",), overridden_gates=(),
        explanation="The academic coursework recipe matched this branch.",
        resolved_dimensions=(ResolvedDimension(
            role_ref="holder_institution", field_ref=SCHOOL,
            action=ACTION_SELECTED, order_index=0, display_label=None,
            scope=SCOPE_SCHEMA_FIELD),))


def _level(conn, group: AcceptedGroup, members):
    _, evidence = materialise_branch(
        conn, _candidate(), branch_node_id="n_academics", members=members,
        ancestor_field_refs=(), ancestor_depth=0,
        handling_class_for_member=ONE_CLASS,
        protected_handling_classes=PROTECTED_CLASSES,
        group_level_roles=frozenset({"holder_institution"}),
        group_value_for_member=group_level_reader(
            conn, groups=(group,), agreement=AGREEMENT))
    return evidence


def test_two_syllabi_of_one_course_from_one_school_make_the_level(corpus,
                                                                  tmp_path):
    """The case the ruling permits, and the only one that builds a folder.

    Two documents, two sets of bytes, one course, one school: the level is
    `Columbia`, and it carries the sparse essay that never stated a school --
    which is `00`:57's whole shape and what `104` R-102 has been unable to
    produce since the per-file question was withdrawn.
    """
    conn = corpus
    first = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    second = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus (updated).pdf")
    essay = _carried(conn, tmp_path, "Essay 2 Final Draft.pdf")
    group = _group(first, second, essay)

    evidence = _level(conn, group, (first, second, essay))

    assert evidence.levels[0].values == (COLUMBIA,)
    assert evidence.levels[0].members_by_value[COLUMBIA] == frozenset(
        {first.file_id, second.file_id, essay.file_id})
    assert evidence.unresolved_by_field[SCHOOL] == frozenset()


def test_an_essay_that_names_a_high_school_does_not_file_the_course_under_it(
        corpus, tmp_path):
    """The mentioned school is not a destination.

    The essay is coursework and it names a high school. That value is the
    essay's own, and it is not an anchor of the course. The course's folder is
    the school the two syllabi state. An essay in no course group states the
    same high school and grows no folder from it.
    """
    conn = corpus
    first = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    second = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus (updated).pdf")
    essay = _carried(conn, tmp_path, "Essay 2 Final Draft.pdf")
    _fact(conn, essay.file_id, field_key=SCHOOL, value="Westfield Prep",
          reliability_state="llm_supported", run_id="r-mention")
    outside_id = _file(conn, tmp_path, "Essay outside.pdf", folder="Downloads")
    _fact(conn, outside_id, field_key=SCHOOL, value="Westfield Prep",
          reliability_state="llm_supported", run_id="r-outside")
    outside = GroupMember(file_id=outside_id, content_hash=_hash(conn, outside_id),
                          basis=CONTEXT_SUPPORTED)
    group = _group(first, second, essay)

    evidence = _level(conn, group, (first, second, essay, outside))

    assert evidence.levels[0].values == (COLUMBIA,)
    assert "Westfield Prep" not in evidence.levels[0].display_labels
    assert outside.file_id in evidence.unresolved_by_field[SCHOOL]
    assert essay.file_id in evidence.levels[0].members_by_value[COLUMBIA]


def test_one_syllabus_alone_makes_no_level(corpus, tmp_path):
    """The rule's own cost, stated as a test so it is not discovered as a bug.

    Before the ruling this group had a school level. `00`:42 is what the ruling
    applies: one document's word "may remain a possible clue for review; it must
    not quietly become a folder proposal". The school stays on the syllabus and
    the members wait for the person.
    """
    conn = corpus
    only = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    essay = _carried(conn, tmp_path, "Essay 2 Final Draft.pdf")
    group = _group(only, essay)

    assert _school_of(conn, group) is None

    evidence = _level(conn, group, (only, essay))
    assert evidence.levels[0].values == ()
    assert evidence.unresolved_by_field[SCHOOL] == frozenset(
        {only.file_id, essay.file_id})


def test_a_syllabus_and_its_copy_are_one_source(corpus, tmp_path):
    """"Two copies of one syllabus are one source" (§14.4), by their bytes.

    The copy sits in another folder under the same name, which is how a
    downloaded file arrives twice, and `_file` writes the name as the content --
    so the two carry one content hash and the group has one source, not two.
    """
    conn = corpus
    original = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    copy = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf", folder="Downloads")
    assert original.content_hash == copy.content_hash

    assert _school_of(conn, _group(original, copy)) is None


def test_a_syllabus_and_its_re_export_are_one_source(corpus, tmp_path):
    """The same sentence for a document that is not byte-identical.

    A re-export has its own bytes and its own hash, and P6 records what it is: a
    `version_family` shared with the document it came from. Independence is a
    question about documents, not about files.
    """
    conn = corpus
    original = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf",
                       family=(VERSION_FAMILY, "vf_busib_syllabus"))
    exported = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.docx",
                       family=(VERSION_FAMILY, "vf_busib_syllabus"))
    assert original.content_hash != exported.content_hash

    assert _school_of(conn, _group(original, exported)) is None


def test_a_duplicate_family_makes_two_files_one_source(corpus, tmp_path):
    """The other family field, and the reason both are handed to the rule."""
    conn = corpus
    original = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf",
                       family=(DUPLICATE_FAMILY, "df_busib_syllabus"))
    near = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus copy.pdf",
                   family=(DUPLICATE_FAMILY, "df_busib_syllabus"))

    assert _school_of(conn, _group(original, near)) is None


def test_syllabi_of_two_unrelated_courses_do_not_make_a_school_level(corpus,
                                                                    tmp_path):
    """§14.4's own example: "documents from unrelated courses cannot jointly
    establish a course's school".

    Two real syllabi, two independent sources, one school between them -- and no
    course whose school they both state. Each group has one anchor of its own,
    and one anchor is not two.
    """
    conn = corpus
    busib = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf",
                    subject="BUSIB4300")
    phys = _anchor(conn, tmp_path, "PHYS 1401 Syllabus.pdf", subject="PHYS1401")
    one = _group(busib, group_id="g_busib")
    two = _group(phys, group_id="g_phys")

    reader = group_level_reader(conn, groups=(one, two), agreement=AGREEMENT)
    assert reader(busib, SCHOOL) is None
    assert reader(phys, SCHOOL) is None


def test_two_anchors_in_one_group_stating_two_courses_are_not_in_scope(corpus,
                                                                       tmp_path):
    """The same rule where the group is what puts the two documents together.

    A group is P9's answer to what belongs with what, and it can be wrong. Scope
    is asked of the ANCHORS -- do they state one course -- so a group holding two
    courses' syllabi cannot use one to corroborate the other.
    """
    conn = corpus
    busib = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf",
                    subject="BUSIB4300")
    phys = _anchor(conn, tmp_path, "PHYS 1401 Syllabus.pdf", subject="PHYS1401")

    assert _school_of(conn, _group(busib, phys)) is None


def test_a_transcript_naming_a_transfer_institution_does_not_make_it_the_school(
        corpus, tmp_path):
    """§14.4: "a transcript may name transfer institutions".

    The transcript is a permitted anchor kind and it is not a statement about
    this course: it names Barnard, the syllabus names Columbia, and the anchors
    disagree. The members stay unresolved rather than being filed under whichever
    document sorted first -- and `Barnard` never appears as a folder.
    """
    conn = corpus
    syllabus = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    transcript = _anchor(conn, tmp_path, "Transcript.pdf", school=BARNARD)
    essay = _carried(conn, tmp_path, "Essay 2 Final Draft.pdf")
    group = _group(syllabus, transcript, essay)

    assert _school_of(conn, group) is None

    evidence = _level(conn, group, (syllabus, transcript, essay))
    assert evidence.levels[0].values == ()
    assert BARNARD not in evidence.levels[0].display_labels


def test_a_transcript_out_of_the_courses_scope_cannot_be_the_second_anchor(
        corpus, tmp_path):
    """A transcript that agrees is still not evidence about THIS course.

    It names Columbia and no course, so it shares the syllabus's school and not
    the syllabus's scope. One anchor in scope is one anchor, and §14.4 asks for
    two.
    """
    conn = corpus
    syllabus = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    transcript = _anchor(conn, tmp_path, "Transcript.pdf", subject=None)

    assert _school_of(conn, _group(syllabus, transcript)) is None


def test_a_filename_is_never_a_source_for_school(corpus, tmp_path):
    """`104` R-95's measurement, refused at the level rather than at the value.

    The second syllabus's school rests on nothing but the file's own name. It is
    dropped before it is counted, so the group is back to one anchor and gets no
    level -- and the same two files, with the same value read from the document,
    do make one. The predicate is the composition root's (`cli.
    rests_on_a_name_alone`); what is pinned here is that the rule uses it.
    """
    conn = corpus
    first = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    named = _anchor(conn, tmp_path, "Columbia BUSIB 4300 Syllabus.pdf")

    from_the_name = AnchorAgreement(
        fields=frozenset({SCHOOL}),
        origin_fields=(DUPLICATE_FAMILY, VERSION_FAMILY), scope_field=SUBJECT,
        rests_on_a_name_alone=lambda file_id, fact_id: file_id == named.file_id)

    group = _group(first, named)
    assert _school_of(conn, group, agreement=from_the_name) is None
    assert _school_of(conn, group).canonical_value == COLUMBIA


def test_the_persons_own_answer_stands_alone(corpus, tmp_path):
    """R-80 and R-103: "a person's acceptance always outranks both answers".

    §14.4 excludes a protected anchor from the model and names the remedy in the
    same sentence -- "manual confirmation can supply that information" -- so a
    rule that made a confirmed school wait for a second document to agree would
    leave the person no way to answer at all.
    """
    conn = corpus
    confirmed = _anchor(conn, tmp_path, "Tuition Statement.pdf",
                        state=USER_CONFIRMED)
    essay = _carried(conn, tmp_path, "Essay 2 Final Draft.pdf")

    settled = _school_of(conn, _group(confirmed, essay))
    assert settled is not None
    assert settled.canonical_value == COLUMBIA


def test_a_field_the_agreement_does_not_name_keeps_the_rule_it_had(corpus,
                                                                  tmp_path):
    """The guard on the blast radius, and it is `104` R-101's business.

    The term is a group-level field too, and R-101 puts it on B's per-course
    acceptances. The agreement names `school` alone, so one anchor still settles
    every other field exactly as it did before this rule existed.
    """
    conn = corpus
    only = _anchor(conn, tmp_path, "BUSIB 4300 Syllabus.pdf")
    essay = _carried(conn, tmp_path, "Essay 2 Final Draft.pdf")
    group = _group(only, essay)

    reader = group_level_reader(conn, groups=(group,), agreement=AGREEMENT)
    assert reader(only, SUBJECT).canonical_value == "BUSIB4300"
    assert reader(only, SCHOOL) is None

    without = group_level_reader(conn, groups=(group,))
    assert without(only, SCHOOL).canonical_value == COLUMBIA
