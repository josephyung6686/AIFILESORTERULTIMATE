"""Moving a file deeper inside its own folder is not moving it out of one.

`00`'s amendment of line 22, ruled by the owner on 2026-09-05 and recorded as
`104` §13.8: **refinement allowed, removal constrained.** Moving a file deeper
inside the branch it already sits in is a decision the product may make. Moving it
OUT of the arrangement its owner built stays a constraint that is surfaced to
them rather than decided silently.

Two rules were treating those as one thing:

* `_without_kind_only_moves` refuses to carry a file out of where it is on an
  artifact kind or a period alone -- measured on the owner's 199 files, six
  university physics papers filed into `Desktop/AP world`, a high-school history
  folder, on `work_type = exam` and nothing else. Correct, and it also refused
  `Python 1006/lecture` for a file already in `Python 1006`, which is not a move
  out of anywhere.
* `_staying_put_wins_a_tie` gives a tie to the folder the file is already in,
  because a tie is not a reason to move somebody's file. Correct against a rival
  branch, and wrong against a CHILD of that same folder: the child is not a rival
  home, it is where staying leads. R-48 is the symptom -- six `Python 1006` files
  at "right parent, wrong leaf" in every run, `work_type = lecture` present, the
  level present, the file one level short.

THE EXEMPTION IS ANCHORED ON THE FILE'S OWN FOLDER AND NOTHING WIDER, and
`Desktop/AP world` is the reason. `AP world` IS one of the person's own folders,
so "a descendant of any folder they have" would let all six physics papers back in
through the child the exemption opens. What is exempt is a descendant of the folder
THIS FILE IS IN, which `AP world` is not for a paper sitting on the Desktop. Both
halves are pinned below.
"""
from __future__ import annotations

import pytest

from placement import vocabulary as v
from placement.config import PlacementLimits, SupportPolicy
from placement.pipeline import _refinements_of, _without_kind_only_moves
from placement.records import MatchingFact
from placement.retrieval import (
    CURATED_FOLDER, Candidate, DIRECT_FACT, Retrieval,
)
from placement.scoring import assess

#: `artifact_kind`'s field, as the shipped library binds it. What a file IS never
#: says whose it is, which is the whole of why it cannot carry a move.
KIND = "work_type"
PERIOD = "term"
CANNOT_ANCHOR = frozenset({KIND, PERIOD})

POLICY = SupportPolicy(policy_id="fixture-v1", support_scale_max=1.0,
                       minimum_support_threshold=0.4, margin_threshold=0.2)

#: The person's own folder, the child this run proposes inside it, and a folder
#: somewhere else entirely that holds the same kind of thing.
OWN = "n-python-1006"
CHILD = "n-python-1006-lecture"
ELSEWHERE = "n-ap-world"

#: `Python 1006` is the parent of its own `lecture` level; `AP world` is a
#: top-level folder of the person's own and is nobody's child.
PARENT_OF = {OWN: None, CHILD: OWN, ELSEWHERE: None}


def _fact(field=KIND, value="lecture"):
    return MatchingFact(file_fact_id=f"ff-{field}", field=field, value=value,
                        reliability=v.DIRECT, evidence_ref="obs-1")


def _candidate(node_id, *, channels=(DIRECT_FACT,), facts=None):
    return Candidate(node_id=node_id, channels=channels,
                     matching_facts=(_fact(),) if facts is None else facts,
                     group_ids=())


def _retrieval(*candidates):
    return Retrieval(subject_ref="file:f1:h1", plan_version="plan-1",
                     candidates=tuple(candidates), conflicts=(),
                     semantic_only_node_ids=frozenset())


def _refinements(own=OWN, nodes=(OWN, CHILD, ELSEWHERE)):
    return _refinements_of(own, PARENT_OF, nodes)


# --- `_refinements_of`: which nodes are inside the folder the file is in ---------


def test_a_child_of_the_files_own_folder_is_a_refinement():
    assert CHILD in _refinements()


def test_the_folder_itself_is_not_a_refinement_of_itself():
    """Staying put is the status quo, not a move deeper into anything.

    Counting it here would make `_staying_put_wins_a_tie`'s tie unreachable: the
    folder would win as a refinement before the rule that exists to protect it
    ever ran, and the two would be saying the same thing in two places.
    """
    assert OWN not in _refinements()


def test_another_folder_the_person_owns_is_not_a_refinement():
    """The `Desktop/AP world` half. It is theirs, and it is not where this file
    is, so carrying the file there is removal like any other."""
    assert ELSEWHERE not in _refinements()


def test_a_caller_that_named_no_folder_gets_no_refinements():
    """`None` is what every file outside the person's folders looks like, and
    what a caller that does not supply the mapping looks like. The exemption is
    off, and both rules behave exactly as they did before it existed."""
    assert _refinements(own=None) == frozenset()


# --- `_without_kind_only_moves`: out is still refused, in is allowed -------------


def test_a_kind_only_move_out_of_the_folder_is_still_refused():
    """THE GUARD THAT MUST NOT MOVE. `AP world` claims this file on
    `work_type = exam` alone and is not where the file is."""
    kept = _without_kind_only_moves(
        _retrieval(_candidate(ELSEWHERE)),
        dimension_of={ELSEWHERE: None},
        fields_that_cannot_anchor_a_move=CANNOT_ANCHOR,
        refinements=_refinements())

    assert [c.node_id for c in kept.candidates] == [], (
        "a folder that is merely somewhere else holding the same KIND of thing "
        "was allowed to claim the file on that agreement alone")


def test_a_kind_only_move_into_the_folders_own_child_is_allowed():
    """THE FIX. Same evidence, same fields, same absence of a dimension on the
    node -- the only difference is that the destination is inside the folder the
    file is already in, and that is refinement rather than removal."""
    kept = _without_kind_only_moves(
        _retrieval(_candidate(CHILD)),
        dimension_of={CHILD: None},
        fields_that_cannot_anchor_a_move=CANNOT_ANCHOR,
        refinements=_refinements())

    assert [c.node_id for c in kept.candidates] == [CHILD], (
        "a file was refused the child of the folder it is already in, on the "
        "rule that exists to stop it being carried OUT of that folder")


def test_the_child_is_refused_again_when_it_is_not_this_files_folder():
    """The negative twin for the exemption itself. The same child node, the same
    evidence -- but this file lives somewhere else, so the child is not a
    refinement of anything and the ordinary refusal applies."""
    kept = _without_kind_only_moves(
        _retrieval(_candidate(CHILD)),
        dimension_of={CHILD: None},
        fields_that_cannot_anchor_a_move=CANNOT_ANCHOR,
        refinements=_refinements(own=ELSEWHERE))

    assert [c.node_id for c in kept.candidates] == []


def test_a_period_only_move_into_the_child_is_allowed_too():
    """`cycle_period` is the library's other what-or-when role and the rule
    treats them alike; so does the exemption."""
    kept = _without_kind_only_moves(
        _retrieval(_candidate(CHILD, facts=(_fact(PERIOD, "Spring2023"),))),
        dimension_of={CHILD: None},
        fields_that_cannot_anchor_a_move=CANNOT_ANCHOR,
        refinements=_refinements())

    assert [c.node_id for c in kept.candidates] == [CHILD]


# --- `_staying_put_wins_a_tie`: the parent no longer beats its own child ---------


def test_a_tied_child_of_the_folder_the_file_is_in_wins_the_tie():
    """R-48's mechanism, at the function that causes it.

    `_CHANNEL_WEIGHT` sums DEDUPLICATED channels, so the folder the file is in and
    the child this run proposes inside it score exactly the same. Before the
    split, `already_there` gave the tie to the parent and the file stopped one
    level short of the level built for it.
    """
    retrieval = _retrieval(
        _candidate(OWN, channels=(DIRECT_FACT, CURATED_FOLDER)),
        _candidate(CHILD))

    result = assess(retrieval, {}, policy=POLICY,
                    their_own_folder_node_ids=frozenset({OWN}),
                    refinements=_refinements())

    assert result.scored[0].node_id == CHILD, (
        "the folder the file is in beat the level built for it inside that same "
        "folder, and the file stopped one level short")
    assert result.stays_put is False, (
        "a file that went one level deeper was recorded as having stayed put")


def test_a_tied_rival_somewhere_else_still_loses_to_staying_put():
    """THE GUARD THAT MUST NOT MOVE. A tie between where a file already is and a
    folder this run would like to create is not a question; it is a proposal
    against a home, and the answer is the one that moves nothing."""
    retrieval = _retrieval(
        _candidate(OWN, channels=(DIRECT_FACT, CURATED_FOLDER)),
        _candidate(ELSEWHERE))

    result = assess(retrieval, {}, policy=POLICY,
                    their_own_folder_node_ids=frozenset({OWN}),
                    refinements=_refinements())

    assert result.scored[0].node_id == OWN
    assert result.stays_put is True


def test_a_level_inside_the_persons_folder_beats_a_tied_level_outside_it():
    """THE TIE THE FULL-CORPUS RUN ACTUALLY RECORDED, and the folder the file is
    in is not one of its two sides.

    `tests/test_cli.py`'s xfail on `test_the_lectures_get_a_folder_of_their_own_
    inside_the_folder_they_are_in` reads the mechanism out of a treatment
    database for `lecture01_introduction.ipynb`: support 0.714 on BOTH of

        `Coursework/.../Spring2023/lecture`   proposed
        `Desktop/Python 1006/lecture`         proposed

    and the file abstained between them. A level built under an adopted folder is
    a `proposed` node with no `existing_path`, so it has none of its parent's
    standing -- neither side is a folder the person made, `_staying_put_wins_a_
    tie` saw no candidate the file was already in, and the note ends "that is the
    thing to solve before designing adopted branches again".

    IT IS SOLVED HERE AND THE TEST ABOVE DOES NOT REACH IT. That one ties the
    child against its own PARENT, which is the tie R-48 names; this one ties two
    strangers, and the exemption still applies because `refined` is read over
    every tied candidate rather than only when the parent is among them. One of
    the two lies inside the folder this file is already sitting in and the other
    does not, and that is a difference §6.9 does not have to arbitrate: it is not
    a choice between two institutions, it is where staying leads against
    somewhere else.

    THE TREE STILL BUILDS NO SUCH LEVEL, so the xfail stays xfailed and stays
    strict. What this pins is that the placement half no longer refuses the
    answer when the level exists.
    """
    rival_parent = "n-coursework-spring2023"
    rival = "n-coursework-spring2023-lecture"
    parents = dict(PARENT_OF, **{rival_parent: None, rival: rival_parent})
    retrieval = _retrieval(_candidate(rival), _candidate(CHILD))
    theirs = frozenset({OWN, ELSEWHERE})

    abstained = assess(retrieval, {}, policy=POLICY,
                       their_own_folder_node_ids=theirs)
    assert abstained.scored[0].node_id == rival, (
        "the baseline this test measures against is not the one the run "
        "recorded: the level outside the person's folder has to be the one that "
        "wins without the exemption, or nothing below is about the exemption")

    result = assess(retrieval, {}, policy=POLICY,
                    their_own_folder_node_ids=theirs,
                    refinements=_refinements_of(OWN, parents, (CHILD, rival)))

    assert result.scored[0].node_id == CHILD, (
        "two proposed levels tied, one of them inside the folder this file is "
        "already in, and the run still could not tell them apart")
    assert result.stays_put is False, (
        "a file that went deeper inside its own folder was recorded as having "
        "stayed put, which tells `needs_model_call` the opposite of what "
        "happened")


def test_two_tied_refinements_leave_the_file_at_the_parent():
    """WHEN THE DEEPER LEVEL CANNOT BE TOLD APART, THE APPROVED SHALLOWER PATH
    WINS -- which is `00`:111's own answer and not a gap in this rule.

    "If the system cannot distinguish Spring 2025 from Spring 2026 but a parent
    path such as `Academics/Columbia/PHYS1401/Homework` exists, the model should
    choose the approved shallower path." Two tied children inside the person's
    folder is exactly that: the exemption says a deeper level is reachable, and
    says nothing about WHICH, so the rule falls through and the file stays at the
    folder it is in. `stays_put` is true because that is what happened.

    This is also why the exemption is written as "exactly one": picking either
    child here would be the arbitrary choice §6.9 exists to prevent, made one
    level down.
    """
    second = "n-python-1006-homework"
    parents = dict(PARENT_OF, **{second: OWN})
    retrieval = _retrieval(
        _candidate(OWN, channels=(DIRECT_FACT, CURATED_FOLDER)),
        _candidate(CHILD), _candidate(second))

    result = assess(
        retrieval, {}, policy=POLICY,
        their_own_folder_node_ids=frozenset({OWN}),
        refinements=_refinements_of(OWN, parents, (OWN, CHILD, second)))

    assert result.scored[0].node_id == OWN
    assert result.stays_put is True


def test_a_run_that_names_no_refinements_behaves_exactly_as_before():
    """The whole exemption is off by default, and this is what off looks like.

    Every caller that does not supply `the_folder_each_file_is_in` -- which is
    every test written before this rule and every deployment that has not wired
    it -- gets the answer it got before.
    """
    retrieval = _retrieval(
        _candidate(OWN, channels=(DIRECT_FACT, CURATED_FOLDER)),
        _candidate(CHILD))

    result = assess(retrieval, {}, policy=POLICY,
                    their_own_folder_node_ids=frozenset({OWN}))

    assert result.scored[0].node_id == OWN
    assert result.stays_put is True
