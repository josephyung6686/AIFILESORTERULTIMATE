# tests/test_branch_situation_lives.py
"""`00` amendment 12 with 12a: the partition keys on the LIFE a file's situation
points at, and a life appears only where the person's own files put it.

Every signal is a table, as in `test_branch_situation.py`, so a rule that moves
is caught by name. `LIVES` is a fixture mapping and not the shipped library:
these tests are about the KEY, and `test_library_lives.py` is about the rows.
"""
from __future__ import annotations

import pytest

from branch_situation import Branch, BranchPartition, partition_by_branch
from facts.fields import DOMAIN_FIELDS


class _Verdict:
    def __init__(self, schema_id=None, tied=()):
        self.schema_id = schema_id
        self.tied_schema_ids = tuple(tied)


OWNERS = {"syllabus": "academic", "resume": "career"}
SITUATIONS = {"academic": ("academic.coursework", "academic.teaching"),
              "career": ("career.employment-records", "career.recruiting"),
              "college_applications": ("applications.undergraduate-packet",),
              "finance": ("finance.tax-filings", "finance.vehicle-records")}
LIVES = {"academic.coursework": "Education", "academic.teaching": "Teaching",
         "career.employment-records": "Career", "career.recruiting": "Career",
         "applications.undergraduate-packet": "Education",
         "finance.tax-filings": "Finance and Taxes",
         "finance.vehicle-records": "Vehicles"}
#: The library's word for each KIND (`lives.json`), the fixture's copy.
LIVES_OF_KIND = {"academic": "Education", "career": "Career",
                 "college_applications": "Education",
                 "finance": "Finance and Taxes"}


def _partition(files, *, named=None, facts=None, alternatives=None, anchors=None,
               chosen=None, default_situation="academic.coursework",
               default_label="Coursework", lives=LIVES,
               lives_of_kind=LIVES_OF_KIND, situations=SITUATIONS):
    named = named or {}
    facts = facts or {}
    alternatives = alternatives or {}
    anchors = anchors or {}
    chosen = chosen or {}
    return partition_by_branch(
        roster=tuple((name, "h" * 64) for name in files),
        default_label=default_label, default_situation=default_situation,
        default_schema="academic",
        anchor_facts_of=lambda file_id, _hash: anchors.get(file_id, ()),
        owner_of_term=OWNERS,
        fields_of_schema=lambda schema_id: DOMAIN_FIELDS.get(schema_id, ()),
        verdict_of=lambda file_id, _hash: _Verdict(),
        situations_of=lambda schema_id: situations.get(schema_id, ()),
        chosen_situation=lambda scope: chosen.get(scope),
        named_by_the_model=named,
        life_of=lambda situation: lives.get(situation),
        life_of_kind=lambda schema_id: lives_of_kind.get(schema_id),
        situation_fact_of=lambda file_id: facts.get(file_id),
        alternatives_of=lambda file_id: alternatives.get(file_id, ()))


def test_two_kinds_in_one_life_are_one_branch_labelled_with_the_life():
    """THE KEY. A coursework file and an application packet are two schemas
    and one life. SABOTAGE: key on the schema as before -- two branches
    `academic` and `college_applications`, the taxonomy of kinds."""
    partition = _partition(
        ["notes", "packet"], default_situation=None,
        named={"notes": "academic", "packet": "college_applications"},
        facts={"notes": "academic.coursework",
               "packet": "applications.undergraduate-packet"})

    education = partition.by_label("Education")
    assert education is not None
    assert education.life == "Education"
    assert education.folder_name == "Education"
    assert set(education.file_ids) == {"notes", "packet"}
    assert education.schemas == ("academic", "college_applications")
    assert education.situations == ("academic.coursework",
                                    "applications.undergraduate-packet")
    assert partition.by_label("college_applications") is None


def test_a_life_no_file_reaches_is_not_a_branch():
    """12a(i): the menu is not the tree. `LIVES` names Vehicles; nothing here
    is a vehicle record. SABOTAGE: open a branch per distinct value of `LIVES`
    -- the sixteen-folder skeleton amendment 12a forbids."""
    partition = _partition(["notes"], default_situation=None,
                           named={"notes": "academic"},
                           facts={"notes": "academic.coursework"})

    # The default is unsettled (two academic situations, none typed), so it has
    # no life and the coursework file leaves it for Education; nothing else
    # opens. Two branches, and neither is a life the file did not reach.
    assert [branch.label for branch in partition.branches] == ["Coursework", "Education"]
    assert partition.by_label("Vehicles") is None


def test_a_typed_runs_own_life_stays_in_the_default_branch():
    """THE BYTE PIN (`test_r37_single_branch_is_byte_identical`): a typed
    `--situation academic.coursework` over coursework is ONE branch, exactly as
    before. SABOTAGE: put every lived file in a life branch -- a second root
    named Education beside `Coursework`, and the pin's fixture breaks.
    SABOTAGE 2: keep the `len(schemas) == 1` early return. This stays green
    without the rule ever running -- which is why the untyped test below exists."""
    partition = _partition(["a", "b"], named={"a": "academic", "b": "academic"},
                           facts={"a": "academic.coursework",
                                  "b": "academic.coursework"})

    assert partition.single
    assert partition.default.life == "Education"
    assert set(partition.default.file_ids) == {"a", "b"}


def test_a_typed_run_gives_another_kind_of_its_own_life_a_branch_of_its_own():
    """`--situation academic.coursework --label Coursework`, and an application
    packet site G named `college_applications`: one life with the coursework,
    another KIND. Before amendment 12 it had a root of its own; the typed word
    is a statement about the run's own kind and covers nothing else
    (`cli._the_situation_this_file_is_under` treats a G-named other kind as not
    the run's). So it is under its life, beside the typed branch.

    SABOTAGE: keep every file of the typed life at home. Measured on the
    typed-run pin (`tests/integration/test_a_life_mate_of_another_kind_is_
    still_placed.py`): the packet then sits inside `Coursework`, its group is
    drafted there in its own kind, and P11 -- once allowed into the branch that
    holds it -- files an application essay into `PHYS1401/`, which is R-23,
    the thing R-37 exists to stop."""
    partition = _partition(["hw", "packet"],
                           named={"hw": "academic", "packet": "college_applications"},
                           facts={"hw": "academic.coursework",
                                  "packet": "applications.undergraduate-packet"})

    assert partition.default.file_ids == ("hw",)
    assert partition.default.life == "Education"
    education = partition.by_label("Education")
    assert education.file_ids == ("packet",)
    assert education.schemas == ("college_applications",)


def test_a_typed_label_that_is_the_life_itself_keeps_that_lifes_files_home():
    """The one collision: `--label Education --situation academic.coursework`.
    A life branch called Education beside a default called Education is two
    branches wearing one key, which the partition refuses; the person's own
    word for the folder IS the life, so the packet stays under it."""
    partition = _partition(["hw", "packet"], default_label="Education",
                           named={"hw": "academic", "packet": "college_applications"},
                           facts={"hw": "academic.coursework",
                                  "packet": "applications.undergraduate-packet"})

    assert partition.single
    assert set(partition.default.file_ids) == {"hw", "packet"}
    assert partition.default.schemas == ("academic", "college_applications")


def test_an_untyped_default_is_settled_only_by_the_persons_answer_at_its_own_scope():
    """`00` amendment 25, first half: WHAT STILL SETTLES THE DEFAULT, and what no
    longer does.

    THE RULE THIS REPLACES was `test_an_untyped_run_keeps_only_the_residue_in_
    the_default_branch`: with nothing typed the default's situation was settled
    "by exactly the rule every other branch already has" (the 11 Sep ruling) --
    the person's answer at the branch's scope, else the library's ONE situation
    for the default's schema. It was ratified because, with nothing typed, there
    was no reason to treat the branch the corpus named differently from the
    branches its anchors opened.

    WHY AMENDMENT 25 OVERRIDES IT. On an untyped run the default's schema is the
    corpus's MAJORITY KIND, and the files under the default are the ones no
    life could be read for -- the residue nothing judged. The library's one
    situation for a kind those files were never shown to have is a situation
    neither the person nor the model gave (`104` §18.114); §17.9 licenses no
    third voice. So the default is settled by the person's answer at ITS OWN
    scope and by nothing else: that answer is the person saying what THIS
    folder's leftover files are, which is their word and stands (first half of
    this test, unchanged from the old one). With a one-situation kind and no
    answer the default is unsettled, offers no menu -- one situation is not a
    question -- and carries no life; `Downloads` is not a life either way.

    SABOTAGE: restore `the_one_situation` for the default. The second partition
    wears `academic.coursework` and `z`, which nothing read, is filed as
    coursework."""
    answered = _partition(["a", "z"], default_situation=None,
                          default_label="Downloads",
                          named={"a": "academic"},
                          facts={"a": "academic.coursework"},
                          chosen={"branch:Downloads": "academic.coursework"})

    assert answered.default.situation == "academic.coursework"
    assert answered.default.life == "Education"
    assert answered.default.file_ids == ("z",)
    assert answered.by_label("Education").file_ids == ("a",)

    one_situation = _partition(
        ["a", "z"], default_situation=None, default_label="Downloads",
        named={"a": "academic"}, facts={"a": "academic.coursework"},
        situations={**SITUATIONS, "academic": ("academic.coursework",)})

    assert one_situation.default.situation is None
    assert one_situation.default.life is None
    assert one_situation.default.candidate_situations == ()
    assert one_situation.default.file_ids == ("z",)
    assert one_situation.by_label("Education").file_ids == ("a",)


def test_a_file_of_another_life_leaves_the_default_branch():
    """Priya teaches. `68` F6's graduate student: her teaching material was
    filed as coursework because the command line took one situation for the
    disk. Under amendment 12 it is under Teaching -- on a run where nobody
    typed a word for the folder, so the judge's answer is the only one."""
    partition = _partition(["hw", "rubric"], default_situation=None,
                           named={"hw": "academic", "rubric": "academic"},
                           facts={"hw": "academic.coursework",
                                  "rubric": "academic.teaching"})

    assert partition.by_label("Education").file_ids == ("hw",)
    assert partition.by_label("Teaching").file_ids == ("rubric",)
    assert partition.default.file_ids == ()


def test_the_typed_word_covers_the_runs_own_kind_and_a_fact_does_not_move_it():
    """`104` §17.9: the model's answer is a refinement of the person's, never a
    replacement. The person typed `--situation academic.coursework`; a fact on
    an academic file naming `academic.teaching` (a stale row from an earlier,
    untyped run -- a typed run never asks the judge the run's own kind) does
    not carry the file out from under the word they typed. This is the rule
    `cli._the_situation_this_file_is_under` already applies to the same file;
    the partition must not hold a second answer.

    SABOTAGE: read the fact before the person's word. The rubric goes to
    Teaching here and to `Coursework` in the fact pass and in P11."""
    partition = _partition(["hw", "rubric"],
                           named={"hw": "academic", "rubric": "academic"},
                           facts={"hw": "academic.coursework",
                                  "rubric": "academic.teaching"})

    assert partition.single
    assert set(partition.default.file_ids) == {"hw", "rubric"}


def test_the_persons_stored_answer_for_a_kind_still_decides_that_kinds_files():
    """THE CONDITION ON AMENDMENT 12 (the lead, 18 Sep): the owner's database
    holds answers keyed `branch:academic` and the like, given across runs 13-23
    when a KIND was a branch. After this change there is no `academic` branch.
    The answer must still reach the files it was always about, or the judge's
    fact is read where the person's answer is not -- `104` §17.9 inverted.

    The judge says coursework for both; the person had said teaching for
    academic files. The person decides, and Education is not even opened.
    SABOTAGE: drop the per-kind answer arm. Both files land in Education."""
    partition = _partition(
        ["a", "b"], default_situation=None, default_label="Downloads",
        named={"a": "academic", "b": "academic"},
        facts={"a": "academic.coursework", "b": "academic.coursework"},
        chosen={"branch:academic": "academic.teaching"})

    assert partition.by_label("Teaching").file_ids == ("a", "b")
    assert partition.by_label("Education") is None


def test_the_persons_answer_for_the_folders_kind_no_longer_settles_the_default():
    """`00` amendment 25, second half: THE KIND'S ANSWER IS NOT THE DEFAULT'S.

    THE RULE THIS REPLACES was `test_the_persons_stored_answer_for_the_folders_
    kind_still_settles_the_default`: an untyped run used to label its default
    with the kind, so the person's answer to "Which of these is academic?" was
    stored at `branch:academic`; when the default came to be called by the
    folder (amendment 12) the old answer was read at the kind's scope as well,
    so that the person would not be asked again what they had answered. It was
    ratified on `104` §17.9 -- the person's answer is never dropped for a
    rename.

    WHY AMENDMENT 25 OVERRIDES IT. That answer was about the KIND's files, and
    it still reaches every one of them (`_persons_answer_for`, asserted below:
    `a` goes to Education on the strength of it). The default branch on an
    untyped run holds the files that have NO kind or no life -- the residue --
    and reading the kind's answer onto them was the product asserting, for 113
    of the owner's 371 files, a situation the person gave for OTHER files
    (`104` §18.114). §17.9 orders the person above the model and the model
    above silence; nowhere does it let a rename carry an answer onto files it
    was never about. So the kind's answer settles the kind's files and NOT the
    default; the default stays visibly unjudged, its question standing with its
    menu, until the person answers at ITS scope or a model names the residue.

    SABOTAGE: read `branch:<default_schema>` for the default. `z`, which nothing
    read, is filed as coursework and the question disappears from the screen."""
    partition = _partition(["a", "z"], default_situation=None,
                           default_label="Downloads",
                           named={"a": "academic"},
                           chosen={"branch:academic": "academic.coursework"})

    assert partition.by_label("Education").file_ids == ("a",)
    assert partition.default.situation is None
    assert partition.default.life is None
    assert partition.default.file_ids == ("z",)
    assert partition.default.candidate_situations == SITUATIONS["academic"]


def test_the_alternatives_decide_only_when_they_agree_on_one_life():
    """The tie-break. No first choice; two alternatives in one life is that
    life; two alternatives in two lives is nothing -- the kind's own word then
    answers (arm 3), and with none the default holds the file. SABOTAGE: take
    the first alternative. `sorted()` order decides a life."""
    agree = _partition(["x"], default_situation=None, named={"x": "career"},
                       alternatives={"x": ("career.recruiting",
                                           "career.employment-records")})
    disagree = _partition(["y"], default_situation=None, named={"y": "finance"},
                          alternatives={"y": ("finance.tax-filings",
                                              "finance.vehicle-records")})
    no_word = _partition(["y"], default_situation=None, named={"y": "finance"},
                         lives_of_kind={},
                         alternatives={"y": ("finance.tax-filings",
                                             "finance.vehicle-records")})

    assert agree.by_label("Career").file_ids == ("x",)
    assert disagree.by_label("Finance and Taxes").file_ids == ("y",)
    assert no_word.default.file_ids == ("y",)


def test_a_file_with_no_situation_takes_the_librarys_life_for_its_kind():
    """Arm 3: the gate-refused résumé. No judge reached it; its `resume` anchor
    is career's, and the library says career IS Career (`life_of_kind`).
    SABOTAGE: drop the arm. The 87 files the gate refused all fall to the
    default branch, and a résumé is placed under the run's coursework levels
    -- R-23 again."""
    partition = _partition(["cv"], default_situation=None,
                           anchors={"cv": (("work_type", "resume"),)})

    assert partition.by_label("Career").file_ids == ("cv",)
    assert partition.by_label("Career").situation is None


def test_a_kinds_life_is_the_librarys_word_and_not_the_rows_unanimity():
    """THE OWNER'S CORPUS (the lead, 18 Sep): 218 of 257 situation facts hold
    the KIND, and a life read only off situations left 218 files in no life.
    `academic` spans Education and Teaching in its rows, so unanimity over the
    rows says nothing; the library's own word for the kind says Education,
    and a syllabus nobody judged lands there whatever this folder's judged
    files say. SABOTAGE: derive the kind's life from its rows' agreement, or
    from the corpus's. The syllabus falls to the default with no question."""
    partition = _partition(
        ["s", "a", "b"], default_situation=None,
        named={"a": "academic", "b": "academic"},
        facts={"a": "academic.coursework", "b": "academic.teaching"},
        anchors={"s": (("work_type", "syllabus"),)})

    assert partition.by_label("Education").file_ids == ("s", "a")
    assert partition.by_label("Teaching").file_ids == ("b",)


def test_a_kind_the_library_places_in_no_life_leaves_the_file_in_the_default():
    """No word for the kind, no fact, no alternatives: the file has no life;
    R-140 puts it under the default branch and NOTHING picks. SABOTAGE: fall
    back to the rows' plurality -- this module choosing a life on the person's
    behalf."""
    partition = _partition(
        ["s", "a"], default_situation=None,
        lives_of_kind={"career": "Career"},
        named={"a": "academic"}, facts={"a": "academic.coursework"},
        anchors={"s": (("work_type", "syllabus"),)})

    assert partition.default.file_ids == ("s",)
    assert partition.by_label("Education").file_ids == ("a",)


def test_a_life_branch_holding_two_situations_is_unsettled_and_asks_nothing():
    """"Which situation is Education?" is not a question when Education holds
    coursework and a thesis. Unsettled, no candidates: Phase 2(a)'s third arm
    hands the router every situation its files carry."""
    partition = _partition(["n", "p"], default_situation=None,
                           named={"n": "academic", "p": "college_applications"},
                           facts={"n": "academic.coursework",
                                  "p": "applications.undergraduate-packet"})

    education = partition.by_label("Education")
    assert education.situation is None
    assert education.candidate_situations == ()


def test_a_life_branch_the_judge_named_one_situation_for_is_settled_by_it():
    """`_settled_by_the_judge`, unchanged: unanimous over every file."""
    partition = _partition(["n", "m"], default_situation=None,
                           named={"n": "academic", "m": "academic"},
                           facts={"n": "academic.coursework",
                                  "m": "academic.coursework"})

    assert partition.by_label("Education").situation == "academic.coursework"


def test_a_life_branch_of_one_kind_the_judge_could_not_settle_still_asks_the_person():
    """`00` amendment 1 of 14 Sep: the person is asked only where the judge
    cannot -- and IS asked there. A gate-refused résumé alone under Career:
    nobody named its situation, `career` has three, and the branch holds one
    kind, so the question is the kind's question and the branch carries the
    kind's situations for it. SABOTAGE: `candidate_situations=()` for every
    life branch (the draft's rule). The résumé sits under Career with no
    situation, no levels, no question and no way out until Phase 5."""
    partition = _partition(["cv"], default_situation=None,
                           anchors={"cv": (("work_type", "resume"),)})

    career = partition.by_label("Career")
    assert career.situation is None
    assert career.candidate_situations == ("career.employment-records",
                                           "career.recruiting")


def test_the_candidates_of_a_life_branch_are_its_own_lifes_situations_only():
    """`academic` spans Education and Teaching. An Education branch of academic
    files is asked which EDUCATION situation it is: an answer naming a
    Teaching situation would settle nothing (`_settled_by_its_files` checks
    the life), so it is not offered."""
    # Three academic situations, two of them Education; `s` resolves to
    # nothing (no answer, no fact, two Education situations for its kind), so
    # the branch is open and asks between the two.
    partition = partition_by_branch(
        roster=(("s", "h"), ("a", "h"), ("b", "h")),
        default_label="Downloads", default_situation=None,
        default_schema="academic",
        anchor_facts_of=lambda f, _h: {"s": (("work_type", "syllabus"),)}.get(f, ()),
        owner_of_term=OWNERS,
        fields_of_schema=lambda schema_id: DOMAIN_FIELDS.get(schema_id, ()),
        verdict_of=lambda f, _h: _Verdict(),
        situations_of=lambda schema_id: {
            "academic": ("academic.coursework", "academic.teaching",
                         "academic.transcripts")}.get(schema_id, ()),
        chosen_situation=lambda scope: None,
        named_by_the_model={"a": "academic", "b": "academic"},
        life_of={**LIVES, "academic.transcripts": "Education"}.get,
        life_of_kind=LIVES_OF_KIND.get,
        situation_fact_of={"a": "academic.coursework",
                           "b": "academic.coursework"}.get,
        alternatives_of=lambda f: ())

    education = partition.by_label("Education")
    assert set(education.file_ids) == {"s", "a", "b"}
    assert education.situation is None
    assert education.candidate_situations == ("academic.coursework",
                                              "academic.transcripts")


def test_a_life_branch_of_one_kind_whose_files_carry_two_situations_asks_nothing():
    """Two situations of one life under one branch: the branch is not one piece
    of work and "which of these is Finance and Taxes?" has no answer."""
    lives = {**LIVES, "finance.receipts-expenses": "Finance and Taxes"}
    partition = _partition(
        ["x", "y"], default_situation=None, lives=lives,
        named={"x": "finance", "y": "finance"},
        facts={"x": "finance.tax-filings", "y": "finance.receipts-expenses"})

    finance = partition.by_label("Finance and Taxes")
    assert finance.situation is None
    assert finance.candidate_situations == ()


def test_the_persons_answer_at_the_kinds_scope_settles_the_life_branch():
    """The question a single-kind life branch asks is recorded at the KIND's
    scope (`cli._ask_which_situation_each_branch_is`), so the answer is read
    where every other reader of the person's answer reads it -- one key, old
    answers and new."""
    partition = _partition(["n", "p"], default_situation=None,
                           named={"n": "academic", "p": "academic"},
                           facts={"n": "academic.coursework",
                                  "p": "academic.teaching"},
                           chosen={"branch:academic": "academic.teaching"})

    teaching = partition.by_label("Teaching")
    assert teaching.file_ids == ("n", "p")
    assert teaching.situation == "academic.teaching"
    assert partition.by_label("Education") is None


def test_no_file_is_lost_in_the_fold():
    """Coverage is sacred. Every rostered file is under exactly one branch or
    held -- `BranchPartition.__post_init__` refuses two places, this refuses
    none."""
    files = ["a", "b", "c", "d", "e"]
    partition = _partition(
        files, default_situation=None,
        named={"a": "academic", "b": "career", "c": "finance"},
        facts={"a": "academic.coursework", "b": "career.recruiting",
               "c": "finance.tax-filings"},
        anchors={"d": (("work_type", "resume"),)})

    placed = [f for branch in partition.branches for f in branch.file_ids]
    assert sorted(placed + list(partition.held)) == sorted(files)


def test_a_file_two_branches_reach_is_still_held_before_any_life_is_read():
    """`held` is computed by the reach, before the fold, and a held file is
    given no life: nothing decides, so nobody guesses."""
    partition = _partition(
        ["both", "cv"], default_situation=None,
        anchors={"both": (("subject", "PHYS1401"), ("employer", "Acme")),
                 "cv": (("work_type", "resume"),)})

    assert partition.held == ("both",)
    assert partition.by_label("Career").file_ids == ("cv",)


def test_the_partition_refuses_two_branches_wearing_one_label():
    """Risk #13: the label is an identity in five places. A scanned folder named
    exactly as a life its files reach (`Education/` scanned untyped) would give
    two branches one key; the partition refuses, and the person types
    `--label`."""
    default = Branch(label="Education", life=None, schemas=("academic",),
                     situations=(), situation=None, is_default=True,
                     anchor_file_ids=(), file_ids=("z",))
    life = Branch(label="Education", life="Education", schemas=("academic",),
                  situations=(), situation=None, is_default=False,
                  anchor_file_ids=(), file_ids=("a",))
    with pytest.raises(ValueError, match="Education"):
        BranchPartition(branches=(default, life), held=())
