# tests/p10/test_p10_the_general_on_demand.py
"""`104` §18.2 gap 11c: the scoped General is minted ON DEMAND, and by nothing else.

`00`:99 makes it optional in its own words -- "the future tree CAN include
`Academics/Columbia/2026-Spring/General` rather than sending it to a global
Unsorted folder" -- and `cli.py` answered the question with `()` under a recorded
argument that is still true as far as it goes: an unasked question answered by
default is a folder nobody wanted. Minting one under every branch would be that.

The owner's ruling of 10 Sep (`104` §18.30, §18.33) is the third answer between
every branch and none: mint under a parent that ACTUALLY HAS a file whose accepted
facts support the parent and no leaf. That makes the question a placement outcome,
and the tree pass runs first -- which is the ordering question §18.30 put to the
owner and these pins are the answer to.

**THE DEMAND IS READ, NEVER GUESSED.** It is gap 11b's own decision half: a file
placed on an ancestor the shortlist offered, whose record names the levels below
it as deliberately unfilled (`DecisionDepth.unsupported_levels`, SPEC:401-404).
Nothing here inspects a fact table or a filename; a folder in somebody's tree that
no decision asked for is the thing this file exists to prevent.

**THE CHAIN IS THE REAL ONE.** `design_tree` builds and freezes the tree from the
seam corpus, and `mint_scoped_generals` continues that version chain with the SAME
`ADD_SCOPED_GENERAL` review action a person at the canvas would send. The corpus's
`BUSIB 4300` has `Homework` and `Syllabus` beneath it and `PHYS1401` has nothing,
so a file that settles the course and not the work type is `00`:99's own case
standing in the tree the product actually designs.
"""
from __future__ import annotations

import dataclasses

import pytest

from evidence_shape.schema import create_evidence_schema
from grouping.schema import create_grouping_schema
from placement.fixtures import EXACT_PLACEMENT
from placement.records import DecisionDepth, Destination
from placement.versions import scoped_general_demand
from placement.vocabulary import ORDINARY, SCOPED_GENERAL
from tree_design.pipeline import mint_scoped_generals
from tree_design.schema import create_tree_schema
from tree_design.store import nodes_for_version
from tree_design.vocabulary import USER_CREATED

from p10 import test_p10_pipeline as chain
from p10.seam_corpus import seed_seam_corpus

#: The branch whose leaves are `Homework` and `Syllabus`. Its ORIGIN, because
#: that is the identity a review action names and the identity a draft
#: preserves -- and since `106` Phase 5.1 the origin is the node's KEY, spelled
#: from the branch and what each folder is named by (`tree_design.node_key`),
#: so it reads the same in every version of the chain and on every run.
COURSE = "branch:Columbia coursework/subject=BUSIB 4300"
HOMEWORK = COURSE + "/work_type=Homework"
OTHER_COURSE = "branch:Columbia coursework/subject=PHYS1401"


@pytest.fixture()
def corpus(conn, tmp_path):
    create_evidence_schema(conn)
    create_grouping_schema(conn)
    create_tree_schema(conn)
    return seed_seam_corpus(conn, tmp_path)


@pytest.fixture()
def designed(corpus):
    """One real frozen tree with NO General in it, and the ids to continue from.

    `authorities` is built once and shared with the minting below, because the
    fixture's id mint is a counter and a second one would start again at zero --
    re-minting a plan version this chain has already written. `cli.py` draws a
    fresh token per call and has no such collision; this is the fixture keeping
    the same promise a different way.
    """
    authorities = chain.authorities(corpus)
    decisions = chain.decisions(scoped_general=())
    tree = chain.design(corpus, auth=authorities, dec=decisions)
    return corpus, authorities, decisions, tree


def _placed_on(node_id: str, *, file_id: str, levels: tuple[str, ...],
               role: str = ORDINARY):
    """One placement, on P11's own published record rather than a copy of it.

    Only three fields are the subject here -- where the file went, whose file it
    is, and which levels the decision left unfilled -- so the other twenty-eight
    are the golden record's, and a shape change breaks this at import rather than
    leaving it asserting against a record the product no longer has.
    """
    return dataclasses.replace(
        EXACT_PLACEMENT, decision_id=f"d-{file_id}",
        subject=dataclasses.replace(EXACT_PLACEMENT.subject, file_id=file_id,
                                    content_hash=f"h-{file_id}"),
        destination=Destination(node_id=node_id, node_role=role),
        decision_depth=DecisionDepth(node_depth=1, supported_depth=1,
                                     unsupported_levels=levels))


def _node_of(tree, origin: str):
    return next(node for node in tree.nodes if node.origin_node_id == origin)


def _generals(tree):
    return tuple(node for node in tree.nodes
                 if node.node_role == SCOPED_GENERAL)


def _mint(designed, demand):
    corpus, authorities, decisions, tree = designed
    from tree_design.pipeline import ScopedGeneralAnswer

    return mint_scoped_generals(
        corpus.conn, authorities=authorities,
        decisions=dataclasses.replace(
            decisions,
            scoped_general=tuple(ScopedGeneralAnswer(parent_origin_id=parent)
                                 for parent in demand)),
        tree=tree)


# --- what demand is ----------------------------------------------------------------


def test_a_file_that_settles_the_parent_and_no_leaf_is_the_demand(designed):
    """`00`:99's own sentence, read off the record instead of off a rule.

    The file is in `BUSIB 4300` and nothing in it says which work type, so the
    decision named `work_type` as a level it deliberately left unfilled. That file
    -- and only that file -- is what a General under that course would be for.
    """
    _corpus, _auth, _dec, tree = designed
    course = _node_of(tree.tree, COURSE)

    demand = scoped_general_demand(
        (_placed_on(course.node_id, file_id="f-quiz", levels=("work_type",)),),
        tree=tree.tree)

    assert demand == {COURSE: ("f-quiz",)}


def test_a_file_filed_as_deep_as_its_evidence_goes_demands_nothing(designed):
    """The control, and the commonest shape in any real run.

    A decision that left no level unfilled is a file in the deepest folder that
    fits it. It wants no catch-all, and a run that minted one for it would be
    putting a folder in somebody's tree on the strength of nothing.
    """
    _corpus, _auth, _dec, tree = designed
    homework = _node_of(tree.tree, HOMEWORK)

    assert scoped_general_demand(
        (_placed_on(homework.node_id, file_id="f-hw3", levels=()),),
        tree=tree.tree) == {}


def test_two_files_under_one_parent_are_one_parents_demand(designed):
    """One branch, two files short of a leaf, ONE folder between them.

    A General is a property of the branch and not of the file, so the demand
    collapses on the parent. Two folders here would be two catch-alls inside one
    course, which is the ambiguity `00`:99 refuses spelled twice.
    """
    _corpus, _auth, _dec, tree = designed
    course = _node_of(tree.tree, COURSE)

    demand = scoped_general_demand(
        (_placed_on(course.node_id, file_id="f-quiz", levels=("work_type",)),
         _placed_on(course.node_id, file_id="f-notes", levels=("work_type",))),
        tree=tree.tree)

    assert demand == {course.origin_node_id: ("f-quiz", "f-notes")}


def test_a_parent_that_already_has_a_general_is_not_asked_for_a_second(corpus):
    """The judgement this step asked for is not overruled by this step.

    The default chain puts a General under the top branch, so a file placed on
    that branch was SHOWN that folder -- `_the_parents_own_general_is_offered`
    puts a contender's own General on the shortlist as a set-aside -- and whoever
    decided put the file on the parent anyway. Minting a second one, or moving the
    file into the first, would be the rules answering a question they handed to
    the judge.
    """
    authorities = chain.authorities(corpus)
    tree = chain.design(corpus, auth=authorities, dec=chain.decisions())
    root = next(node for node in tree.tree.nodes if node.parent_node_id is None
                and node.node_role != SCOPED_GENERAL)

    assert _generals(tree.tree), "the fixture's own General must be in this tree"
    assert scoped_general_demand(
        (_placed_on(root.node_id, file_id="f-stray", levels=("subject",)),),
        tree=tree.tree) == {}


def test_a_file_already_in_a_general_does_not_demand_a_general_inside_it(corpus):
    """A General under a General is the global catch-all, one level down.

    A file filed in a catch-all carries the levels its SIBLINGS bind, which is the
    same field saying something else entirely -- so reading it as demand would
    make every catch-all grow one, run after run.
    """
    authorities = chain.authorities(corpus)
    tree = chain.design(corpus, auth=authorities, dec=chain.decisions())
    general = _generals(tree.tree)[0]

    assert scoped_general_demand(
        (_placed_on(general.node_id, file_id="f-stray", levels=("subject",),
                    role=SCOPED_GENERAL),),
        tree=tree.tree) == {}


def test_the_parents_are_named_in_an_order_two_runs_agree_on(designed):
    """Replay. The same corpus and the same answers mint the same folders.

    A mapping in decision order would name two parents in whichever order the
    roster happened to reach them, and `mint_scoped_generals` sends one review
    action per key -- so the order IS which folder gets minted first, and a plan
    that differed between two identical runs would be a plan nobody could replay.
    """
    _corpus, _auth, _dec, tree = designed
    course = _node_of(tree.tree, COURSE)
    other = _node_of(tree.tree, OTHER_COURSE)
    forwards = (_placed_on(course.node_id, file_id="f-a", levels=("work_type",)),
                _placed_on(other.node_id, file_id="f-b", levels=("work_type",)))

    assert (list(scoped_general_demand(forwards, tree=tree.tree))
            == list(scoped_general_demand(forwards[::-1], tree=tree.tree))
            == sorted([course.origin_node_id, other.origin_node_id]))


# --- what minting does -------------------------------------------------------------


def test_exactly_one_general_is_minted_under_exactly_that_parent(designed):
    """The ruling in one assertion: on demand, and never under every branch.

    The corpus has two courses and a top-level branch. One file wants a catch-all
    under one course, so the plan gains ONE folder, inside that course -- and the
    other course and the branch above them gain nothing, which is the whole
    difference from a General everywhere.
    """
    _corpus, _auth, _dec, tree = designed
    minted = _mint(designed, {COURSE: ("f-quiz",)})

    generals = _generals(minted.tree)
    assert len(generals) == 1
    assert generals[0].display_label == "General"
    parent = {node.node_id: node for node in minted.tree.nodes}[
        generals[0].parent_node_id]
    assert parent.origin_node_id == COURSE
    assert parent.display_label == "BUSIB 4300"


def test_the_minted_general_is_a_proposal_and_a_destination(designed, tmp_path):
    """It enters the PLAN, and P12's apply is what would create a folder.

    `00`:102 -- the tree "does not yet move or classify files" -- and this node is
    no exception to it: it is a node in a frozen plan with a type and an
    explanation, and nothing on disk. The corpus is on `tmp_path` and no folder of
    this name appears anywhere under it. It IS a legal destination, because a
    catch-all P11 may not place into would be a folder that catches nothing.
    """
    _corpus, _auth, _dec, _tree = designed
    minted = _mint(designed, {COURSE: ("f-quiz",)})
    general = _generals(minted.tree)[0]

    assert general.node_type == USER_CREATED
    assert general.accepts_placement is True
    assert general.existing_path is None
    assert general.explanation, "a proposed folder says why it is there"
    assert list(tmp_path.rglob(general.display_label)) == []


def test_a_run_with_no_demand_writes_nothing_at_all(designed):
    """The r37 shape, and the reason this step is invisible on most corpora.

    Not "produces an equivalent tree" -- writes NOTHING. `apply_review_action`
    refuses a silent no-op for the same reason: a person who changed nothing must
    not be shown a new plan version with a full copy of their tree in it. So the
    frozen tree that comes back is the one that went in, by identity, and the
    database has not gained a version or a node.
    """
    corpus, _auth, _dec, tree = designed
    before = corpus.conn.execute(
        "SELECT COUNT(*) FROM plan_versions").fetchone()[0]
    nodes_before = corpus.conn.execute(
        "SELECT COUNT(*) FROM tree_nodes").fetchone()[0]

    unchanged = _mint(designed, {})

    assert unchanged is tree
    assert unchanged.tree.plan_version_id == tree.tree.plan_version_id
    assert corpus.conn.execute(
        "SELECT COUNT(*) FROM plan_versions").fetchone()[0] == before
    assert corpus.conn.execute(
        "SELECT COUNT(*) FROM tree_nodes").fetchone()[0] == nodes_before


def test_two_files_under_one_parent_share_one_general(designed):
    """Two files, one folder. The count is the assertion.

    §5.9 warns about "a large number of tiny folders" and one catch-all per file
    is the worst version of it -- a folder per thing that did not fit, which is
    not an organisation at all.
    """
    minted = _mint(designed, {COURSE: ("f-quiz", "f-notes")})

    assert len(_generals(minted.tree)) == 1


def test_the_minting_continues_the_version_chain_and_freezes_it(designed):
    """§8.8, and the reason the run's other decisions have to be re-projected.

    An edit opens a DRAFT and the draft mints a new `node_id` for every node it
    copies, so the version the person is shown is not the version the files were
    placed against. The plan the run ends on is a FROZEN one, because a draft is
    not something a person has approved.
    """
    corpus, _auth, _dec, tree = designed
    minted = _mint(designed, {COURSE: ("f-quiz",)})

    assert minted.tree.plan_version_id != tree.tree.plan_version_id
    assert minted.plan_version_ids[:len(tree.plan_version_ids)] \
        == tree.plan_version_ids
    assert corpus.conn.execute(
        "SELECT state FROM plan_versions WHERE plan_version_id = ?",
        (minted.tree.plan_version_id,)).fetchone()["state"] == "frozen"
    # Every node re-minted, and every LINEAGE preserved -- which is what makes the
    # re-projection of the decisions possible at all.
    was = {node.origin_node_id for node in tree.tree.nodes}
    now = {node.origin_node_id for node in minted.tree.nodes}
    assert was < now
    assert not ({node.node_id for node in nodes_for_version(
        corpus.conn, minted.tree.plan_version_id)}
        & {node.node_id for node in tree.tree.nodes})
