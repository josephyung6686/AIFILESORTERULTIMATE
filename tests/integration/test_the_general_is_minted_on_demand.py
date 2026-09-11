# tests/integration/test_the_general_is_minted_on_demand.py
"""`104` §18.2 gap 11c: the step after placement, over a real tree and real rows.

`00`:99 gives the product its answer to the commonest ambiguity there is -- a file
that clearly belongs to `Academics/Columbia/2026-Spring` and has no recoverable
work type gets `.../General` "rather than sending it to a global Unsorted folder"
-- and adds the rule that governs it: "a global catch-all folder should not become
the product's default answer to ambiguity". The owner's ruling of 10 Sep resolves
those two into one gesture: mint ON DEMAND, under a parent that actually has such
a file, never under every branch.

**WHAT THIS FILE PINS THAT `tests/p10/test_p10_the_general_on_demand.py` DOES
NOT.** That file pins the demand and the minting. This one pins the price of doing
it after the tree is frozen, which is what the ordering question was really about:
§8.8 makes an edit open a draft, a draft mints a new `node_id` for every node it
copies, and the report joins its labels to the run's decisions BY node id. So the
decisions have to be re-projected onto the version the person is shown, and that
is `placement.versions.carry_onto` -- §8.8's own "the decision carries", which the
design has always described and nothing had ever written.

**THE SHALLOW DECISION IS RECORDED, NOT SIMULATED.** It goes into the real store
through `record_decision`, against a node P10's real chain built out of P6's own
values, and the real writer supersedes it. How a shallow decision comes to exist
is gap 11b's subject and is pinned in
`tests/p11/test_p11_the_shallower_approved_parent.py`; what a run does with one is
this file's.

The corpus is the P10--P11 seam corpus: `BUSIB 4300` has `Homework` and `Syllabus`
beneath it and `PHYS1401` has nothing, so a file that settles the course and not
the work type is `00`:99's own case standing in a tree the product designs rather
than one this file wrote down.
"""
from __future__ import annotations

import dataclasses
import io

import pytest

import cli
from placement import vocabulary as v
from placement.fixtures import EXACT_PLACEMENT
from placement.index import entries_for_plan
from placement.pipeline import CorpusResult
from placement.records import DecisionDepth, Destination
from placement.store import decisions_for_plan, record_decision
from placement.versions import scoped_general_demand
from production import ProductionRun

from p10.seam_corpus import seed_seam_corpus
from p10.test_p10_pipeline import authorities as p10_authorities
from p10.test_p10_pipeline import decisions as p10_decisions
from test_p10_p11_live_seam import _bootstrap, _inputs, index, node_labelled

T0 = "2026-08-27T00:00:00Z"
T1 = "2026-08-27T01:00:00Z"

#: The course whose children are `Homework` and `Syllabus`. A file that settles
#: the course and not the work type belongs here and in neither of them.
COURSE = "BUSIB 4300"


@pytest.fixture()
def corpus(conn, tmp_path):
    _bootstrap(conn)
    return seed_seam_corpus(conn, tmp_path)


@pytest.fixture()
def placed(corpus):
    """A real frozen tree with NO General, indexed, and two decisions in the store.

    One file is filed as deep as its evidence goes and one stopped at the course
    -- which is the pair the whole step turns on, because the second is the only
    one that may move and the first is the one that must survive the move
    unchanged except for the id of the folder it was always going to.

    `authorities` is built once and shared with the minting, because the fixture's
    id mint is a counter and a second one would start again at zero, re-minting a
    plan version this chain has already written. `cli.py` draws a fresh token per
    call and has no such collision.
    """
    from tree_design.pipeline import design_tree

    authorities = p10_authorities(corpus)
    decisions = p10_decisions(scoped_general=())
    tree = design_tree(corpus.conn, authorities=authorities, decisions=decisions)
    index(corpus, tree)
    course = node_labelled(tree.tree, COURSE)
    homework = node_labelled(tree.tree, "Homework")
    short = _record(corpus, tree, node=course, name="hw3",
                    levels=("work_type",))
    deep = _record(corpus, tree, node=homework, name="syllabus", levels=())
    return corpus, authorities, decisions, tree, (short, deep)


def _record(corpus, tree, *, node, name: str, levels: tuple[str, ...],
            supersedes=None):
    """One placement of a REAL corpus file on a REAL node, through P11's store.

    `supersedes` is how a subject comes to be decided twice in one pass, which is
    a real shape (`run_corpus` extends its list, and a member placed by its packet
    can be resolved again as shared material) and the one the carry has to survive.
    `one_current_placement_decision` refuses a second live row for one subject, so
    the link is not optional decoration -- it is what makes the second row legal.
    """
    file_id, content_hash, _key = corpus.files[name]
    decision = dataclasses.replace(
        EXACT_PLACEMENT,
        decision_id=f"{tree.tree.plan_version_id}:file:{file_id}"
                    f"{'' if supersedes is None else ':again'}",
        plan_version=tree.tree.plan_version_id, supersedes=supersedes,
        subject=dataclasses.replace(EXACT_PLACEMENT.subject, file_id=file_id,
                                    content_hash=content_hash),
        destination=Destination(node_id=node.node_id, node_role=node.node_role),
        decision_depth=DecisionDepth(node_depth=1, supported_depth=1,
                                     unsupported_levels=levels),
        decided_by=v.DECIDED_BY_MODEL,
        explanation=f"{node.display_label} expects subject = {COURSE}.")
    record_decision(corpus.conn, decision, component_version="seam",
                    observed_at=T0,
                    supersede_reason=None if supersedes is None else
                    "the pass decided this subject again before it ended")
    return decision


def _run(tree, decisions):
    """The finished run this step is handed, on the records the run really uses.

    `ProductionRun` and `CorpusResult` are plain records with no invariants, so
    the two fields the step reads are real and the rest are the empty values a
    corpus with nothing else in it would produce.
    """
    return ProductionRun(
        p1_p7=None, grouping=(), tree=tree, destinations=(),
        placement=CorpusResult(
            decisions=tuple(decisions), group_plans=(), residual_sets=(),
            unplaced_file_ids=(), subjects=(), calls_at_once=1),
        evaluation=None)


def _mint(placed, run=None):
    corpus, authorities, decisions, tree, made = placed
    return cli.mint_generals_on_demand(
        corpus.conn, run if run is not None else _run(tree, made),
        authorities=authorities, decisions=decisions,
        placement_inputs=lambda result: _inputs(corpus, result),
        component_version="seam", observed_at=T1)


def _generals(tree):
    return tuple(node for node in tree.nodes
                 if node.node_role == v.SCOPED_GENERAL)


def _for(result, file_id: str):
    return next(decision for decision in result.placement.decisions
                if decision.subject.file_id == file_id)


# --- the folder ---------------------------------------------------------------------


def test_the_branch_with_a_parent_only_file_gains_one_general_and_the_others_none(
        placed):
    """The ruling in one assertion, over the tree P10 actually designed.

    Two courses and a top-level branch; one file short of a leaf under one of
    them. The plan gains ONE folder, inside that course. `PHYS1401` and the branch
    above both gain nothing -- which is the difference between minting on demand
    and minting everywhere, and it is the difference a person would notice.
    """
    _corpus, _auth, _dec, tree, _made = placed
    assert _generals(tree.tree) == (), "the run starts with no catch-all anywhere"

    result = _mint(placed)

    generals = _generals(result.tree.tree)
    assert len(generals) == 1
    parent = {node.node_id: node
              for node in result.tree.tree.nodes}[generals[0].parent_node_id]
    assert parent.display_label == COURSE
    assert generals[0].display_label == "General"


def test_the_file_that_minted_it_is_placed_in_it(placed):
    """`00`:99's whole sentence: the file goes into the General, not beside it.

    "Never left at the parent's own level once the General exists" -- a run that
    minted the folder and left the file one level above it would have built the
    person a folder and then not used it.
    """
    corpus, _auth, _dec, _tree, (short, _deep) = placed

    result = _mint(placed)

    general = _generals(result.tree.tree)[0]
    moved = _for(result, short.subject.file_id)
    assert moved.destination.node_id == general.node_id
    assert moved.destination.node_role == v.SCOPED_GENERAL
    # And it is the LIVE decision about that file in the plan the person is shown.
    live = decisions_for_plan(corpus.conn,
                              plan_version=result.tree.tree.plan_version_id)
    assert moved.decision_id in {decision.decision_id for decision in live}


def test_the_move_supersedes_the_shallow_decision_and_says_why(placed):
    """§8.2: a revised decision is a NEW row naming the one it revises.

    The shallow decision is not rewritten and not deleted -- it stays readable,
    with the reason the run moved on from it, which is what makes the plan
    explicable after the fact rather than merely current.
    """
    corpus, _auth, _dec, _tree, (short, _deep) = placed

    result = _mint(placed)

    moved = _for(result, short.subject.file_id)
    assert moved.supersedes == short.decision_id
    row = corpus.conn.execute(
        "SELECT superseded_by, supersede_reason FROM placement_decisions "
        "WHERE record_id = ?", (short.decision_id,)).fetchone()
    assert row["superseded_by"] == moved.decision_id
    assert "created because of this file" in row["supersede_reason"]


def test_whoever_decided_the_shallow_placement_still_decided_this_one(placed):
    """`104` R-165. The actor is carried, because the actor did not change.

    A model chose that branch for that file and this step did not revisit the
    judgement; what changed is that the branch now has the folder `00`:99 says
    the file belongs in. A row that said `rule` here would take a placement off
    the model's count for a reason that has nothing to do with who decided it.
    """
    _corpus, _auth, _dec, _tree, (short, _deep) = placed

    moved = _for(_mint(placed), short.subject.file_id)

    assert moved.decided_by == short.decided_by == v.DECIDED_BY_MODEL
    assert moved.two_condition == short.two_condition
    assert moved.review_policy == short.review_policy


def test_the_person_is_told_the_file_is_the_reason_the_folder_exists(placed):
    """§6.4 and `84` §6: the record says the basis, in the person's own words.

    A folder appearing in somebody's tree with no reason attached is the thing
    `00`:99's "should not become the default answer" is protecting them from. The
    sentence names no section and no field.
    """
    _corpus, _auth, _dec, _tree, (short, _deep) = placed

    moved = _for(_mint(placed), short.subject.file_id)

    assert "created for this file" in moved.explanation
    assert short.explanation.rstrip(".") in moved.explanation
    assert "§" not in moved.explanation


# --- the price of doing it after the freeze -----------------------------------------


def test_every_other_decision_is_carried_onto_the_version_the_person_is_shown(
        placed):
    """§8.8's "the decision carries", and the join it exists to keep true.

    The draft re-minted every node id, so the file that never moved now names a
    node the frozen tree does not contain -- and the report looks its label up by
    that id. Carried, the decision points at the SAME folder under the new id, by
    lineage and never by a plausible match.
    """
    corpus, _auth, _dec, tree, (_short, deep) = placed
    was = node_labelled(tree.tree, "Homework")

    result = _mint(placed)

    now = node_labelled(result.tree.tree, "Homework")
    carried = _for(result, deep.subject.file_id)
    assert now.node_id != was.node_id
    assert now.origin_node_id == was.origin_node_id
    assert carried.destination.node_id == now.node_id
    assert carried.decision_depth == deep.decision_depth
    assert carried.supersedes == deep.decision_id
    # Every decision in the run is about the version the tree now is, and none is
    # still live under the old one.
    assert {decision.plan_version for decision in result.placement.decisions} \
        == {result.tree.tree.plan_version_id}
    assert decisions_for_plan(
        corpus.conn, plan_version=tree.tree.plan_version_id) == ()


def test_a_decision_the_pass_already_withdrew_does_not_demand_a_folder(placed):
    """A subject decided twice in one pass leaves a superseded row in the tuple.

    `run_corpus` returns what it decided in the order it decided it, and a subject
    can be decided twice -- a member placed by its packet and then resolved again
    as shared material is the shape that does it. Here the pass ended on the DEEP
    decision, so the shallow one is a placement the run itself withdrew, and
    minting a folder for it would build the person a catch-all for a decision that
    no longer stands.
    """
    corpus, _auth, _dec, tree, (short, deep) = placed
    homework = node_labelled(tree.tree, "Homework")
    again = _record(corpus, tree, node=homework, name="hw3", levels=(),
                    supersedes=short.decision_id)

    assert scoped_general_demand((short, deep, again), tree=tree.tree) == {}

    result = _mint(placed, run=_run(tree, (short, deep, again)))
    assert result.tree is tree
    assert _generals(result.tree.tree) == ()


def test_only_the_decision_the_pass_ended_on_is_carried(placed):
    """And the same reading on the other side, so the two cannot disagree.

    The folder that gets minted and the decision that lands in it are read from
    one state of the run. A carry that re-projected a withdrawn row would make it
    live again in the new version, and `mark_superseded` would refuse to link a
    row that is already linked -- so it would end the run rather than quietly do
    it. One row per subject, and it is the last one.
    """
    corpus, _auth, _dec, tree, (short, deep) = placed
    course = node_labelled(tree.tree, COURSE)
    again = _record(corpus, tree, node=course, name="syllabus",
                    levels=("work_type",), supersedes=deep.decision_id)

    result = _mint(placed, run=_run(tree, (short, deep, again)))

    rows = [d for d in result.placement.decisions
            if d.subject.file_id == deep.subject.file_id]
    assert len(rows) == 1
    assert rows[0].supersedes == again.decision_id
    # Both files were short of a leaf under the same course, so they share ONE
    # catch-all and both are in it.
    generals = _generals(result.tree.tree)
    assert len(generals) == 1
    assert {row.destination.node_id for row in result.placement.decisions} \
        == {generals[0].node_id}


def test_the_report_names_the_minted_general_and_the_file_it_was_minted_for(
        placed):
    """`00`:100 -- the person sees the proposal, and this folder owes them a why.

    Every other folder in the tree is there because a group or a settled value put
    it there. This one is there because of one particular file, so the tree the
    person reads names that file beside it, by the name they know it by.
    """
    corpus, _auth, _dec, _tree, (short, _deep) = placed
    result = _mint(placed)
    names = {file_id: f"{name}.txt"
             for name, (file_id, _hash, _key) in corpus.files.items()}

    out = io.StringIO()
    cli.report(result, names, out=out)
    printed = out.getvalue()

    assert "General   [created for hw3.txt]" in printed
    # Under the course, which is what "scoped" means on a screen with no styles:
    # the General is indented one level deeper than the folder it belongs to.
    lines = printed.splitlines()
    course = next(i for i, line in enumerate(lines) if line.strip() == COURSE)
    general = next(i for i, line in enumerate(lines) if "General" in line)
    assert general > course
    assert (len(lines[general]) - len(lines[general].lstrip())
            > len(lines[course]) - len(lines[course].lstrip()))


# --- replay -------------------------------------------------------------------------


def test_a_second_pass_over_the_same_run_mints_nothing_and_writes_nothing(placed):
    """Idempotence, and it falls out of the rule rather than being enforced.

    After the mint the file is IN the branch's General, so it is no longer a file
    on a parent with no catch-all -- there is no demand left to answer. A step
    that minted again would grow a folder per run forever, which is the failure
    `00`:99's own second clause names.
    """
    corpus, authorities, decisions, _tree, _made = placed
    once = _mint(placed)
    versions = corpus.conn.execute(
        "SELECT COUNT(*) FROM plan_versions").fetchone()[0]
    nodes = corpus.conn.execute("SELECT COUNT(*) FROM tree_nodes").fetchone()[0]
    rows = corpus.conn.execute(
        "SELECT COUNT(*) FROM placement_decisions").fetchone()[0]

    twice = cli.mint_generals_on_demand(
        corpus.conn, once, authorities=authorities, decisions=decisions,
        placement_inputs=lambda result: _inputs(corpus, result),
        component_version="seam", observed_at=T1)

    assert twice is once
    assert scoped_general_demand(once.placement.decisions,
                                 tree=once.tree.tree) == {}
    assert corpus.conn.execute(
        "SELECT COUNT(*) FROM plan_versions").fetchone()[0] == versions
    assert corpus.conn.execute(
        "SELECT COUNT(*) FROM tree_nodes").fetchone()[0] == nodes
    assert corpus.conn.execute(
        "SELECT COUNT(*) FROM placement_decisions").fetchone()[0] == rows


def test_a_run_where_every_file_settles_its_levels_is_untouched(placed):
    """The r37 shape, and the reason this step is invisible on most corpora.

    Not "produces an equivalent run" -- the same object, and a database that has
    not gained a version, a node or a row. `tests/integration/
    test_r37_single_branch_is_byte_identical.py` is the same claim measured
    against a captured screen; this is it measured against the writes.
    """
    corpus, _auth, _dec, tree, (_short, deep) = placed
    before = _run(tree, (deep,))
    counts = tuple(corpus.conn.execute(
        "SELECT (SELECT COUNT(*) FROM plan_versions), "
        "(SELECT COUNT(*) FROM tree_nodes), "
        "(SELECT COUNT(*) FROM placement_decisions)").fetchone())

    after = _mint(placed, run=before)

    assert after is before
    assert tuple(corpus.conn.execute(
        "SELECT (SELECT COUNT(*) FROM plan_versions), "
        "(SELECT COUNT(*) FROM tree_nodes), "
        "(SELECT COUNT(*) FROM placement_decisions)").fetchone()) == counts


def test_the_general_is_legal_in_the_version_it_was_minted_into(placed):
    """A catch-all P11 may not place into is a folder that catches nothing.

    `legal_node_ids` refuses any destination P10 did not build, and the index is
    what publishes it -- so the minting has to re-index, or the very folder it
    created would be an `INVENTED_NODE` the moment anything named it.
    """
    corpus, _auth, _dec, _tree, _made = placed

    result = _mint(placed)

    general = _generals(result.tree.tree)[0]
    entries = entries_for_plan(
        corpus.conn, plan_version=result.tree.tree.plan_version_id)
    entry = next(e for e in entries if e.node_id == general.node_id)
    assert entry.node_role == v.SCOPED_GENERAL
    assert general.node_id in set(
        result.tree.tree.freeze_record.legal_destination_ids)
