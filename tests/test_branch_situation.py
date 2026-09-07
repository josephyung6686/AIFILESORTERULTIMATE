# tests/test_branch_situation.py
"""`branch_situation.partition_by_branch`, on the signals alone.

The composition root's tests (`tests/integration/test_r37_*`) drive the whole
command; these pin the rules of the partition itself, with every signal handed in
as a table, so a rule that moves is caught by name rather than by a changed screen.
"""
from __future__ import annotations

import pytest

from branch_situation import (
    BRIDGES_THAT_DO_NOT_REACH, SCOPE_BRANCH, BranchPartition, partition_by_branch,
    single_owner_terms,
)
from facts.fields import DOMAIN_FIELDS
from questions.vocabulary import SCOPE_BRANCH as QUESTIONS_SCOPE_BRANCH


class _Verdict:
    def __init__(self, schema_id=None, tied=()):
        self.schema_id = schema_id
        self.tied_schema_ids = tuple(tied)


OWNERS = {"syllabus": "academic", "lecture": "academic",
          "cover letter": "career", "resume": "career"}
SITUATIONS = {"academic": ("academic.coursework", "academic.teaching"),
              "career": ("career.employer-side-hiring", "career.employment-records",
                         "career.recruiting"),
              "code": ("code.software-project",)}


def _partition(files, *, facts, verdicts=None, chosen=None, situations=SITUATIONS):
    verdicts = verdicts or {}
    chosen = chosen or {}
    return partition_by_branch(
        roster=tuple((name, "h" * 64) for name in files),
        default_label="Coursework", default_situation="academic.coursework",
        default_schema="academic",
        anchor_facts_of=lambda file_id, _hash: facts.get(file_id, ()),
        owner_of_term=OWNERS,
        fields_of_schema=lambda schema_id: DOMAIN_FIELDS.get(schema_id, ()),
        verdict_of=lambda file_id, _hash: verdicts.get(file_id, _Verdict()),
        situations_of=lambda schema_id: situations.get(schema_id, ()),
        chosen_situation=lambda scope: chosen.get(scope))


def test_the_two_spellings_this_module_keeps_agree_with_their_owners():
    """Spelled here rather than imported so the module stays free of `cli`; the
    owners are asserted equal so a renamed word cannot drift apart."""
    import cli
    assert BRIDGES_THAT_DO_NOT_REACH == cli.FIELDS_THAT_CANNOT_ANCHOR_A_MOVE
    assert SCOPE_BRANCH == QUESTIONS_SCOPE_BRANCH


def test_a_term_two_schemas_author_anchors_neither():
    owners = single_owner_terms({"academic": ("syllabus", "reference letter"),
                                 "career": ("cover letter", "reference letter")})
    assert owners == {"syllabus": "academic", "cover letter": "career"}


def test_one_branch_is_the_whole_folder_and_holds_nothing():
    """Ruling (4): with one branch the partition IS the folder, whatever the
    recogniser says about any file in it."""
    partition = _partition(
        ("syllabus", "notes", "survey"),
        facts={"syllabus": (("work_type", "syllabus"), ("subject", "PHYS1401"))},
        verdicts={"survey": _Verdict("medical")})

    assert partition.single
    assert partition.default.file_ids == ("syllabus", "notes", "survey")
    assert partition.default.situation == "academic.coursework"
    assert partition.held == ()


def test_an_anchor_of_another_schema_opens_a_second_branch():
    partition = _partition(
        ("syllabus", "cover letter"),
        facts={"syllabus": (("work_type", "syllabus"),),
               "cover letter": (("work_type", "cover letter"),)})

    assert not partition.single
    assert [branch.label for branch in partition.branches] == ["Coursework", "career"]
    assert partition.branch_of("cover letter").schema == "career"
    assert partition.branch_of("cover letter").anchor_file_ids == ("cover letter",)


def test_a_fact_on_the_schemas_own_field_reaches_and_a_bridge_does_not():
    """A course code reaches coursework -- with or without a syllabus stating the
    same course; a term does not: `Summer2026` is the bridge that filed two cover
    letters under Coursework, and `work_type` never carries a file anywhere."""
    partition = _partition(
        ("syllabus", "notes", "other course", "posting", "cover letter"),
        facts={"syllabus": (("work_type", "syllabus"), ("subject", "PHYS1401"),
                            ("term", "Spring2026")),
               "notes": (("subject", "PHYS1401"),),
               "other course": (("subject", "MATH2000"),),
               "posting": (("term", "Spring2026"),),
               "cover letter": (("work_type", "cover letter"),)})

    assert partition.branch_of("notes").label == "Coursework"
    assert partition.branch_of("other course").label == "Coursework"
    # `104` R-140: a term alone reaches nothing, and a file nothing reaches is
    # the default branch's, not held.
    assert partition.branch_of("posting").is_default
    assert partition.held == ()


def test_a_fact_outranks_the_recognisers_reading():
    """The reverted merge's case: a course with no kind word in any name, whose
    files read as `career` to the term recogniser. The validated course code is
    P6's conclusion and wins; the reading is consulted only where no fact of any
    branch's own speaks."""
    partition = _partition(
        ("syllabus", "cover letter", "week 1", "week 2"),
        facts={"syllabus": (("work_type", "syllabus"),),
               "cover letter": (("work_type", "cover letter"),),
               "week 1": (("subject", "MATH2000"),),
               "week 2": (("subject", "MATH2000"),)},
        verdicts={"week 1": _Verdict("career"), "week 2": _Verdict("career")})

    assert partition.branch_of("week 1").label == "Coursework"
    assert partition.branch_of("week 2").label == "Coursework"


def test_the_recognisers_reading_reaches_a_branch_that_exists_and_opens_none():
    partition = _partition(
        ("syllabus", "cover letter", "posting", "survey", "cv"),
        facts={"syllabus": (("work_type", "syllabus"),),
               "cover letter": (("work_type", "cover letter"),)},
        verdicts={"posting": _Verdict("career"),
                  "survey": _Verdict("medical"),
                  "cv": _Verdict(None, tied=("career", "college_applications"))})

    assert partition.branch_of("posting").label == "career"
    assert partition.branch_of("cv").label == "career"
    # `medical` opens no branch and the survey reaches none: the default's.
    assert partition.branch_of("survey").is_default
    assert partition.held == ()
    assert {branch.schema for branch in partition.branches} == {"academic", "career"}


def test_a_file_two_branches_reach_is_held_not_guessed():
    """Facts of two branches' own fields, or a reading that ties between two
    branches with no fact to settle it: nothing decides, so nobody guesses.
    `104` R-140 keeps this the ONLY held case; a file nothing reaches defaults."""
    partition = _partition(
        ("syllabus", "cover letter", "both facts", "tied reading"),
        facts={"syllabus": (("work_type", "syllabus"), ("subject", "PHYS1401")),
               "cover letter": (("work_type", "cover letter"),),
               "both facts": (("subject", "PHYS1401"), ("employer", "Acme")),
               "tied reading": ()},
        verdicts={"tied reading": _Verdict(None, tied=("academic", "career"))})

    assert partition.held == ("both facts", "tied reading")


def test_an_anchors_own_reading_never_moves_it():
    """The résumé the recogniser reads as `college_applications` is career's by
    the library's own kind term, and stays so."""
    partition = _partition(
        ("syllabus", "resume"),
        facts={"syllabus": (("work_type", "syllabus"),),
               "resume": (("work_type", "resume"),)},
        verdicts={"resume": _Verdict("college_applications")})

    assert partition.branch_of("resume").label == "career"


def test_a_branch_with_one_shipped_situation_is_settled_and_otherwise_asked():
    owners = dict(OWNERS, notebook="code")
    partition = partition_by_branch(
        roster=(("syllabus", "h" * 64), ("nb", "h" * 64), ("cv", "h" * 64)),
        default_label="Coursework", default_situation="academic.coursework",
        default_schema="academic",
        anchor_facts_of=lambda file_id, _h: {
            "syllabus": (("work_type", "syllabus"),),
            "nb": (("work_type", "notebook"),),
            "cv": (("work_type", "resume"),)}[file_id],
        owner_of_term=owners,
        fields_of_schema=lambda schema_id: DOMAIN_FIELDS.get(schema_id, ()),
        verdict_of=lambda *_: _Verdict(),
        situations_of=lambda schema_id: SITUATIONS.get(schema_id, ()),
        chosen_situation=lambda scope: None)

    code = partition.by_label("code")
    career = partition.by_label("career")
    assert code.settled and code.situation == "code.software-project"
    assert not career.settled
    assert career.candidate_situations == SITUATIONS["career"]
    assert career.scope == "branch:career"


def test_the_persons_answer_settles_the_branch_and_only_that_branch():
    partition = _partition(
        ("syllabus", "cover letter"),
        facts={"syllabus": (("work_type", "syllabus"),),
               "cover letter": (("work_type", "cover letter"),)},
        chosen={"branch:career": "career.recruiting"})

    assert partition.by_label("career").situation == "career.recruiting"
    assert partition.default.situation == "academic.coursework"


def test_an_answer_naming_a_situation_of_another_schema_settles_nothing():
    partition = _partition(
        ("syllabus", "cover letter"),
        facts={"syllabus": (("work_type", "syllabus"),),
               "cover letter": (("work_type", "cover letter"),)},
        chosen={"branch:career": "academic.teaching"})

    assert not partition.by_label("career").settled


def test_the_partition_refuses_a_file_in_two_places():
    from branch_situation import Branch
    default = Branch(label="a", schema="academic", situation="academic.coursework",
                     is_default=True, anchor_file_ids=(), file_ids=("f",))
    other = Branch(label="career", schema="career", situation=None,
                   is_default=False, anchor_file_ids=(), file_ids=("f",))
    with pytest.raises(ValueError):
        BranchPartition(branches=(default, other), held=())
    with pytest.raises(ValueError):
        BranchPartition(branches=(default,), held=("f",))
