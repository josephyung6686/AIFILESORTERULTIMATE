"""P10 Task 13 — counts before commit, warnings from data, health without blame.

§5.11 constrains the framing as much as the content: tree health "should not
imply that the system must account for every file immediately ... The goal is to
give the user a good enough structural gist of the corpus so that only a limited
number of high-leverage changes remain."

Every warning carries the data that fired it. None carries a number the design
did not state: §5.9 deliberately sets no threshold for "excessive" depth or "a
large number of tiny folders", so those arrive from configuration and cannot
fire without it.
"""
from __future__ import annotations

import pytest

from database_agent.budget import set_ceiling
from tree_design.config import tree_limits
from tree_design.health import (
    branch_counts,
    parent_concepts_for,
    tree_health,
    warnings_for,
)
from tree_design.records import MalformedTreeRecord, Node
from tree_design.vocabulary import (
    RECOMMEND_FLATTEN,
    WARN_EXCESSIVE_DEPTH,
    WARN_ONE_CHILD,
    WARN_REPEATED_PARENT,
    WARN_TINY_FOLDERS,
)


@pytest.fixture()
def limits(conn):
    set_ceiling(conn, "tree.max_folder_proposals", 6)
    set_ceiling(conn, "tree.max_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    return tree_limits(
        conn, excessive_depth_warning=3, tiny_folder_max_files=2,
        tiny_folder_count_warning=3,
        materially_improves_retrieval=lambda preview: None)


def _node(node_id, parent, label, *, role="ordinary", dimension=None,
          dimension_role=None):
    return Node(
        node_id=node_id, plan_version_id="plan_1", node_type="proposed",
        display_label=label, parent_node_id=parent, root_anchor="root_documents",
        ordinal=0, associated_group_ids=(),
        explanation=f"{label} appeared from the accepted groups beneath it.",
        node_role=role, accepts_placement=True,
        handling_class="personal_non_sensitive", origin_node_id=node_id,
        dimension=dimension, dimension_role=dimension_role,
    )


def test_counts_report_children_descendants_and_members():
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "Columbia"),
        _node("n_b", "n_root", "NYU"),
        _node("n_a1", "n_a", "PHYS1401"),
    )
    counts = branch_counts(
        nodes, node_id="n_root",
        members_by_node={"n_root": ("f1", "f2", "f3")},
        unresolved_by_node={"n_root": ("f9",)},
        evidence_gaps_by_node={"n_root": ("f8",)},
        sensitive_node_ids=frozenset())
    assert counts.child_count == 2
    assert counts.descendant_count == 3
    assert counts.member_count == 3
    assert counts.example_members == ("f1", "f2", "f3")
    assert counts.unresolved_file_ids == ("f9",)
    assert counts.evidence_gap_file_ids == ("f8",)
    assert counts.stale is False


def test_counts_can_report_themselves_stale_while_recomputing():
    """The composable-template design requires "explicit stale/loading state
    while counts recompute". A stale count shown as fresh is a number the user
    will act on."""
    counts = branch_counts(
        (_node("n_root", None, "Academics"),), node_id="n_root",
        members_by_node={}, unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset(), stale=True)
    assert counts.stale is True


def test_a_one_child_level_warns(limits):
    nodes = (_node("n_root", None, "Academics"), _node("n_a", "n_root", "Columbia"))
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert [w.kind for w in fired] == [WARN_ONE_CHILD]
    assert fired[0].node_id == "n_root"


def test_a_level_repeating_a_parent_concept_warns(limits):
    nodes = (
        _node("n_root", None, "Academics", dimension="subject",
              dimension_role="subject"),
        _node("n_a", "n_root", "PHYS1401", dimension="subject",
              dimension_role="course"),
        _node("n_b", "n_root", "CHEM1101", dimension="subject",
              dimension_role="course"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits,
                         parent_concepts={"n_a": ("subject",), "n_b": ("subject",)})
    assert WARN_REPEATED_PARENT in {w.kind for w in fired}


def test_excessive_depth_uses_the_injected_threshold_not_the_hard_ceiling(limits):
    chain = [_node("n_0", None, "L0")]
    for depth in range(1, 5):
        chain.append(_node(f"n_{depth}", f"n_{depth - 1}", f"L{depth}"))
    nodes = tuple(chain)
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    depth_warnings = [w for w in fired if w.kind == WARN_EXCESSIVE_DEPTH]
    assert depth_warnings
    assert str(limits.excessive_depth_warning) in depth_warnings[0].reason


def test_a_large_number_of_tiny_folders_warns(limits):
    nodes = (_node("n_root", None, "Receipts"),) + tuple(
        _node(f"n_{i}", "n_root", f"Vendor {i}") for i in range(4))
    counts = {}
    for node in nodes:
        members = () if node.node_id == "n_root" else ("f",)
        counts[node.node_id] = branch_counts(
            nodes, node_id=node.node_id,
            members_by_node={node.node_id: members}, unresolved_by_node={},
            evidence_gaps_by_node={}, sensitive_node_ids=frozenset())
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert WARN_TINY_FOLDERS in {w.kind for w in fired}


def test_the_flatten_recommendation_stays_silent_while_the_test_is_unauthored(limits):
    """§5.9 asks for a recommendation "when a dimension does not materially
    improve retrieval" and states no test. `None` means unknown, and unknown must
    not become a recommendation."""
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "2026"),
        _node("n_b", "n_root", "2025"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert RECOMMEND_FLATTEN not in {w.kind for w in fired}


def test_the_flatten_recommendation_fires_once_a_test_says_no(conn):
    set_ceiling(conn, "tree.max_folder_proposals", 6)
    set_ceiling(conn, "tree.max_depth", 6)
    set_ceiling(conn, "model.max_dossier_tokens_per_call", 4000)
    limits = tree_limits(
        conn, excessive_depth_warning=3, tiny_folder_max_files=2,
        tiny_folder_count_warning=3,
        materially_improves_retrieval=lambda preview: False)
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "2026", dimension="term", dimension_role="term"),
        _node("n_b", "n_root", "2025", dimension="term", dimension_role="term"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert RECOMMEND_FLATTEN in {w.kind for w in fired}


def test_every_warning_is_data_backed_and_carries_no_score(limits):
    nodes = (_node("n_root", None, "Academics"), _node("n_a", "n_root", "Columbia"))
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    for warning in warnings_for(nodes, counts, limits=limits, parent_concepts={}):
        assert warning.evidence
        assert not any(
            token in warning.reason.lower()
            for token in ("confidence", "score", "probability"))


def test_uneven_depth_produces_no_warning_of_its_own(limits):
    """§5.8. Sibling parity is not a health property, and a warning that fired on
    it would push the user toward the symmetrical tree the design rejects."""
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "Columbia"),
        _node("n_b", "n_root", "Reading"),
        _node("n_a1", "n_a", "PHYS1401"),
        _node("n_a2", "n_a", "CHEM1101"),
    )
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert WARN_EXCESSIVE_DEPTH not in {w.kind for w in fired}
    assert all(w.kind != "uneven-depth" for w in fired)


def test_health_reports_coverage_without_demanding_every_file():
    nodes = (_node("n_root", None, "Academics"), _node("n_a", "n_root", "Columbia"))
    health = tree_health(
        nodes,
        members_by_group={"g_phys": ("lecture", "hw", "quiz")},
        placed_by_group={"g_phys": ("lecture", "hw")},
        files_with_enough_facts=2,
        unresolved_node_ids=("n_a",),
        context_supported_node_ids=(),
        sensitive_isolated_node_ids=(),
        nodes_needing_decisions=("n_a",),
    )
    assert health.group_coverage == {"g_phys": 2 / 3}
    assert health.nodes_needing_decisions == ("n_a",)
    assert not hasattr(health, "completeness_score")


def test_canonical_counts_are_reported_once_across_aliases():
    """The composable-template design: "Aliases and alternate views point to
    canonical node/item identities and do not duplicate counts or facts."
    """
    nodes = (
        _node("n_root", None, "Academics"),
        _node("n_a", "n_root", "Columbia"),
    )
    counts = branch_counts(
        nodes, node_id="n_root",
        members_by_node={"n_root": ("f1", "f1", "f2")},
        unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset())
    assert counts.member_count == 2


def test_warnings_follow_the_order_the_user_chose_not_the_recipe_default(limits):
    """§5.3, §5.8 and the owner ruling: the dimension order is a RUNTIME choice.

    `TemplateDefinition` carries `candidate_orders` and only RECOMMENDS one; the
    branch records what the user took in `BranchTemplateBinding.chosen_order_id`.
    A §5.9 warning computed against the recipe's default would describe a tree
    that does not exist — telling a user who chose kind-first that their
    subject-first nesting repeats a parent.

    The guard is structural: `warnings_for` reads the NODES, which materialise
    built from the chosen order, and never reaches a definition at all. Below,
    the same two dimensions in the reversed nesting produce the warning at the
    reversed node, and `health.py` imports nothing that could tell it otherwise.
    """
    import ast
    from pathlib import Path

    # subject over work_type: the repeat lands on the `subject` level.
    subject_first = (
        _node("n_root", None, "Academics"),
        _node("n_s", "n_root", "PHYS1401", dimension="subject",
              dimension_role="course"),
        _node("n_w", "n_s", "Homework", dimension="work_type",
              dimension_role="artifact_kind"),
    )
    # work_type over subject: the SAME two dimensions, the other nesting.
    kind_first = (
        _node("n_root", None, "Academics"),
        _node("n_w", "n_root", "Homework", dimension="work_type",
              dimension_role="artifact_kind"),
        _node("n_s", "n_w", "PHYS1401", dimension="subject",
              dimension_role="course"),
    )

    def _fire(nodes, parent_concepts):
        counts = {n.node_id: branch_counts(
            nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
            evidence_gaps_by_node={}, sensitive_node_ids=frozenset())
            for n in nodes}
        return warnings_for(nodes, counts, limits=limits,
                            parent_concepts=parent_concepts)

    on_subject = _fire(subject_first, {"n_w": ("work_type",)})
    assert {w.node_id for w in on_subject if w.kind == WARN_REPEATED_PARENT} == {"n_w"}

    on_kind = _fire(kind_first, {"n_s": ("subject",)})
    assert {w.node_id for w in on_kind if w.kind == WARN_REPEATED_PARENT} == {"n_s"}

    # And nothing in health.py can consult a recipe's default ordering.
    source = (Path(__file__).resolve().parents[2]
              / "src" / "tree_design" / "health.py").read_text()
    imported = {
        node.module for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "tree_design.templates" not in imported
    assert "tree_design.catalogue" not in imported
    assert "candidate_orders" not in source and "default_order" not in source


def test_parent_concepts_are_read_off_the_stored_parent_chain(limits):
    """`warnings_for` took `parent_concepts` from its caller and NOTHING in src/
    produced one — the §5.9 repeated-parent warning could only fire from a value
    a test handed it. This is that producer.

    It walks the stored parent chain, which is the order the branch was
    MATERIALISED in, which is the order the user chose (`branch_dimension_roles`
    reads `BranchTemplateBinding.chosen_order_id`, never the recipe's default).
    Nothing here consults a recipe, so no recommendation can leak in.
    """
    nodes = (
        _node("n_root", None, "Academics", dimension="subject",
              dimension_role="subject"),
        _node("n_a", "n_root", "PHYS1401", dimension="subject",
              dimension_role="course"),
        _node("n_b", "n_a", "Homework", dimension="work_type",
              dimension_role="artifact_kind"),
    )
    concepts = parent_concepts_for(nodes)
    assert concepts["n_root"] == ()
    assert concepts["n_a"] == ("subject",)
    assert concepts["n_b"] == ("subject", "subject")

    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts=concepts)
    assert {w.node_id for w in fired if w.kind == WARN_REPEATED_PARENT} == {"n_a"}


def test_a_node_with_no_dimension_contributes_no_parent_concept(limits):
    """A level with no `dimension` expresses no concept. Contributing a `None`
    would make two such ancestors look like a repeat of each other."""
    nodes = (
        _node("n_root", None, "Documents"),
        _node("n_mid", "n_root", "2026"),
        _node("n_leaf", "n_mid", "PHYS1401", dimension="subject",
              dimension_role="course"),
    )
    concepts = parent_concepts_for(nodes)
    assert concepts["n_leaf"] == ()
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts=concepts)
    assert WARN_REPEATED_PARENT not in {w.kind for w in fired}


def test_a_parent_chain_that_cycles_is_refused_not_walked_forever():
    """Stored rows carry no foreign key on `parent_node_id`, so a cycle is
    reachable. Walking it would hang the canvas rather than report anything."""
    nodes = (
        _node("n_a", "n_b", "A", dimension="subject", dimension_role="course"),
        _node("n_b", "n_a", "B", dimension="term", dimension_role="term"),
    )
    with pytest.raises(MalformedTreeRecord):
        parent_concepts_for(nodes)


# --- §5.9 measured the wrong thing: the two warnings that fired on `00`:78 -------
#
# Each pair below is a positive and a negative. The positive alone is satisfied
# by a warning that never fires, and a §5.9 list that fires on nothing passes
# every "does not fire on a correct tree" test while being useless.


def _canonical_academic_branch():
    """`00`:78 verbatim: `Academics/Columbia/2026-Spring/PHYS1401/Homework`.

    One school, one term, one course, three work types. Three single-child levels
    and depth four, and the design recommends every part of it.
    """
    return (
        _node("n0", None, "Academics", dimension="area", dimension_role="area"),
        _node("n1", "n0", "Columbia", dimension="school", dimension_role="school"),
        _node("n2", "n1", "2026-Spring", dimension="term", dimension_role="term"),
        _node("n3", "n2", "PHYS1401", dimension="course", dimension_role="course"),
        _node("n4", "n3", "Homework", dimension="work_type",
              dimension_role="work_type"),
        _node("n5", "n3", "Lectures", dimension="work_type",
              dimension_role="work_type"),
        _node("n6", "n3", "Syllabus", dimension="work_type",
              dimension_role="work_type"),
    )


def _fire(nodes, limits, members=None):
    members = members or {}
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node=members,
        unresolved_by_node={}, evidence_gaps_by_node={},
        sensitive_node_ids=frozenset()) for n in nodes}
    return warnings_for(nodes, counts, limits=limits,
                        parent_concepts=parent_concepts_for(nodes))


def test_the_one_child_warning_is_silent_on_the_designs_own_example(limits):
    """§5.7's wording is "create MEANINGLESS one-child levels", and `00`:78 is
    the example that says which ones are meaningful: each of Academics, Columbia
    and 2026-Spring supplies the context §5.6 requires — "a parent dimension
    should provide the context required to understand the child" — for the three
    work types that DO divide beneath them."""
    nodes = _canonical_academic_branch()
    members = {"n4": [f"hw{i}" for i in range(12)],
               "n5": [f"lec{i}" for i in range(20)], "n6": ["syllabus"]}
    fired = [w for w in _fire(nodes, limits, members) if w.kind == WARN_ONE_CHILD]
    assert fired == [], [w.reason for w in fired]


def test_the_one_child_warning_still_fires_when_nothing_below_divides(limits):
    """The twin. The same three levels, with no work-type level under the course:
    the user clicks through four folders and none of them separated a file."""
    nodes = _canonical_academic_branch()[:4] + (
        _node("n4", "n3", "Homework", dimension="work_type",
              dimension_role="work_type"),)
    fired = [w for w in _fire(nodes, limits) if w.kind == WARN_ONE_CHILD]
    assert [w.node_id for w in fired] == ["n0"], (
        "one warning, at the top of the run, naming the whole run")
    assert fired[0].evidence == ("n0", "n1", "n2", "n3", "n4")


def test_the_depth_warning_is_silent_on_the_designs_own_example(limits):
    """`excessive_depth_warning` is 3 here, which is what every call site in this
    repository passes, and `00`:78's Homework sits at depth 4.

    THE NUMBER WAS NEVER THE PROBLEM; THE UNIT WAS. Absolute depth is §5.7's V3,
    which refuses rather than advises and uses §8.6's published ceiling. §5.9's
    advice is about depth the material does not support: `00`:78 is four levels
    expressing five distinct concepts, so every level of it added a meaning.
    """
    fired = [w for w in _fire(_canonical_academic_branch(), limits)
             if w.kind == WARN_EXCESSIVE_DEPTH]
    assert fired == [], [w.reason for w in fired]


def test_the_depth_warning_still_fires_when_the_levels_repeat_themselves(limits):
    """The twin. Five levels that express two concepts between them: the same
    dimension over and over is depth the evidence never asked for."""
    nodes = (
        _node("n0", None, "Academics", dimension="area", dimension_role="area"),
        _node("n1", "n0", "2024", dimension="year", dimension_role="year"),
        _node("n2", "n1", "2024-Q1", dimension="year", dimension_role="year"),
        _node("n3", "n2", "2024-01", dimension="year", dimension_role="year"),
        _node("n4", "n3", "2024-01-05", dimension="year", dimension_role="year"),
        _node("n5", "n3", "2024-01-06", dimension="year", dimension_role="year"),
    )
    fired = [w for w in _fire(nodes, limits) if w.kind == WARN_EXCESSIVE_DEPTH]
    assert {w.node_id for w in fired} == {"n4", "n5"}
    assert str(limits.excessive_depth_warning) in fired[0].reason


# --- the list has to be shorter than the tree, without losing a protected area ---


def _wide_tree(width):
    """One parent whose children are all tiny, plus a protected area beside them."""
    nodes = [_node("n_root", None, "Receipts")]
    for index in range(width):
        nodes.append(_node(f"n_{index}", "n_root", f"Vendor {index}"))
    return tuple(nodes)


def test_the_warning_list_states_a_count_rather_than_listing_everything(limits):
    """§5.11: the goal is "a good enough structural gist ... so that only a
    LIMITED NUMBER of high-leverage changes remain". A 3,200-node tree produced
    2,991 warnings, each one node with one sentence and no ranking."""
    from tree_design.health import sample_size

    width = 400
    nodes = _wide_tree(width)
    members = {node.node_id: () for node in nodes}
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node=members, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    tiny = [w for w in fired if w.kind == WARN_TINY_FOLDERS]
    assert len(tiny) == 1
    assert len(tiny[0].evidence) == sample_size(limits)
    assert str(width) in tiny[0].reason, "the whole count is still stated"


def test_a_summarised_list_never_drops_a_protected_area(limits):
    """The standing rule: a protected container is MARKED AND COUNTED, NEVER
    OPENED — present-but-untouched, counted, never silently omitted.

    A "top N warnings" that hides the one saying "this area was protected and
    not opened" is that omission arriving as a usability improvement. Here the
    protected node is the LAST of many identical findings, so nothing but the
    exemption can keep it in the list.
    """
    from tree_design.health import sample_size
    from tree_design.vocabulary import PROTECTED

    # Many identical one-child runs, one of which hangs off a protected area.
    nodes = [_node("n_root", None, "Documents")]
    runs = sample_size(limits) * 3
    for index in range(runs):
        nodes.append(_node(f"n_a{index}", "n_root", f"Area {index}"))
        nodes.append(_node(f"n_b{index}", f"n_a{index}", f"Only {index}"))
    protected = Node(
        node_id="n_protected", plan_version_id="plan_1", node_type=PROTECTED,
        display_label="Numbers.app", parent_node_id="n_root",
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="marked and counted, never opened",
        node_role="ordinary", accepts_placement=False,
        handling_class="personal_non_sensitive", origin_node_id="n_protected")
    nodes.append(protected)
    nodes.append(_node("n_inside", "n_protected", "Only child"))
    nodes = tuple(nodes)

    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset())
        for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})

    one_child = [w for w in fired if w.kind == WARN_ONE_CHILD]
    assert len(one_child) < runs, "the list is summarised at all"
    assert "n_protected" in {w.node_id for w in one_child}, (
        "the protected area's own warning was summarised away")
    assert one_child[0].node_id == "n_protected", "and it is ranked first"


def test_a_sensitive_isolated_node_is_also_never_summarised_away(limits):
    """§5.11 asks health to show "where sensitive material has been isolated".
    `BranchCounts.sensitive_isolated` is the other record that says so, and it
    buys the same exemption as `node_type=protected`."""
    from tree_design.health import sample_size

    nodes = [_node("n_root", None, "Documents")]
    runs = sample_size(limits) * 3
    for index in range(runs):
        nodes.append(_node(f"n_a{index}", "n_root", f"Area {index}"))
        nodes.append(_node(f"n_b{index}", f"n_a{index}", f"Only {index}"))
    nodes = tuple(nodes)
    # The LAST run is the sensitive one, so ordering alone cannot save it.
    sensitive = frozenset({f"n_a{runs - 1}"})
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=sensitive) for n in nodes}
    fired = warnings_for(nodes, counts, limits=limits, parent_concepts={})
    assert f"n_a{runs - 1}" in {w.node_id for w in fired if w.kind == WARN_ONE_CHILD}


# --- the fast path answers the same question the slow one did --------------------


def _naive_warning_facts(nodes, limits):
    """§5.9 recomputed the way `health.py` used to, with no index at all.

    The point of an index is that it changes the COST and not the ANSWER. This
    rebuilds every structural fact by rescanning the whole tree per node, which
    is what the module did before, and the test below asserts the two agree.
    """
    def children(node_id):
        return tuple(n for n in nodes if n.parent_node_id == node_id)

    def depth(node_id):
        by_id = {n.node_id: n for n in nodes}
        found, current = 0, by_id.get(node_id)
        while current is not None and current.parent_node_id is not None:
            found += 1
            current = by_id.get(current.parent_node_id)
        return found

    def descendants(node_id):
        found, frontier = 0, [node_id]
        while frontier:
            for child in children(frontier.pop()):
                found += 1
                frontier.append(child.node_id)
        return found

    return {n.node_id: (len(children(n.node_id)), depth(n.node_id),
                        descendants(n.node_id)) for n in nodes}


def test_the_indexed_walk_reports_what_the_rescanning_walk_reported(limits):
    """Same tree, same numbers. A faster path that answers differently is not
    an optimisation."""
    import random

    rng = random.Random(11)
    nodes = [_node("n_0", None, "Root", dimension="area", dimension_role="area")]
    dims = ["area", "school", "term", "course", "work_type", "year"]
    depths = {"n_0": 0}
    for index in range(1, 600):
        parent = nodes[int(len(nodes) * (rng.random() ** 2.2))]
        node_depth = depths[parent.node_id] + 1
        dim = dims[min(len(dims) - 1, node_depth)]
        node = _node(f"n_{index}", parent.node_id, f"L{index}", dimension=dim,
                     dimension_role=dim)
        depths[node.node_id] = node_depth
        nodes.append(node)
    nodes = tuple(nodes)

    expected = _naive_warning_facts(nodes, limits)
    counts = {n.node_id: branch_counts(
        nodes, node_id=n.node_id, members_by_node={}, unresolved_by_node={},
        evidence_gaps_by_node={}, sensitive_node_ids=frozenset()) for n in nodes}
    for node_id, (kids, node_depth, kin) in expected.items():
        assert counts[node_id].child_count == kids
        assert counts[node_id].descendant_count == kin
        from tree_design.health import _depth
        assert _depth(nodes, node_id) == node_depth
