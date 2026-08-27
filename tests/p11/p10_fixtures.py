"""P10's frozen tree, for P11's tests. TESTS ONLY.

`src/placement/` may never import this module and a test asserts it does not: a
source stub here would be P11 deciding what a node is, which is P10's to say.

**`Node`, `ExpectedValue` and `TemplateContext` are P10's LIVE records**, imported
from `tree_design.records`. They shipped, so mirroring them here would be the drift
this file exists to avoid: P10 could add a field or tighten a check and every
fixture below would keep passing against a record the product no longer has.

`NodeContext`, `AnchorExcerpt`, `Restrictions`, `DestinationProfile`,
`FreezeRecord` and `FrozenTree` were DECLARED HERE while `tree_design.profiles`
and `tree_design.freeze` were unbuilt -- six duplicate record classes, so P11's
suite could have been green against a shape P10 no longer had and nothing
anywhere would have said so. That is the hand-built-double defect, sitting at
P11's own boundary. P10 ships them now, so they are imported and the duplicates
are gone.

What stays is the INSTANCE, not the type: `NODES`, `FREEZE_RECORD` and
`FROZEN_TREE` are P11's own small tree, built through P10's live constructors.
That is a fixture, not a double -- §6.10's arithmetic below turns on these exact
nodes and groups, and P10's own `frozen_tree_fixture()` is a different corpus
answering a different question. `tests/integration/test_p11_p10_tree.py` is where
P11 runs against P10's own published tree.

`refinement_disposition` is the field that matters most among them: it is the
user's own answer to whether a branch is shallow ON PURPOSE, and §6.7 and
`decision_depth.unsupported_levels` are decisions about exactly that. P11 reading
it beats P11 re-deriving it. It is `str | None` on P10's record because a DRAFT
node may not carry one yet; `frozen_tree` guarantees it non-`None` on every node
it returns, which is why the index may read it as a `str`.
"""
from __future__ import annotations

from dataclasses import replace

from tree_design.freeze import FreezeRecord, FrozenTree
from tree_design.profiles import (
    AnchorExcerpt, DestinationProfile, NodeContext, Restrictions,
)
from tree_design.records import ExpectedValue, Node, TemplateContext

__all__ = [
    "AnchorExcerpt", "DestinationProfile", "ExpectedValue", "FREEZE_RECORD",
    "FROZEN_TREE", "FreezeRecord", "FrozenTree", "NODES", "Node", "NodeContext",
    "Restrictions", "TemplateContext", "tree_with",
]


def _node(**overrides) -> Node:
    values = dict(
        node_id="n-course", plan_version_id="plan-1", node_type="proposed",
        display_label="PHYS1401", parent_node_id="n-academics",
        root_anchor="root_documents", ordinal=1,
        associated_group_ids=("g-phys1401",),
        template_context=TemplateContext(
            binding_id="tb-academic-coursework",
            template_id="academic-coursework", template_version=1,
            dimension_index=2),
        dimension_role="course", dimension="subject",
        expected_values=(ExpectedValue(field="subject", value="PHYS1401"),),
        explanation="Six files in the accepted PHYS1401 group carry subject = PHYS1401.",
        existing_path=None, handling_class="personal_non_sensitive",
        node_role="ordinary", disposition=None, accepts_placement=True,
        protected_movement_permitted=False,
        refinement_disposition="refined",
        refinement_reason="The course has enough populated work types for this level.",
    )
    values.update(overrides)
    # P10 mints a new `node_id` per plan version and records lineage in
    # `origin_node_id` (P10 OQ5). In plan-1 every node IS its own origin, so the
    # default follows `node_id` rather than a fixed literal; a later version
    # overrides it explicitly and that is what Task 17 matches on.
    values.setdefault("origin_node_id", values["node_id"])
    return Node(**values)


#: `n-academics` as a parent, in P10's `NodeContext` shape. §6.1 asks for the
#: parent's MEANING -- its dimension and expected values -- not just its label,
#: which is why the profile carries a record here and a bare string nowhere.
_ACADEMICS_CONTEXT = NodeContext(
    node_id="n-academics", display_label="Academics", dimension=None,
    expected_values=(),
)


def _profile(node: Node, **overrides) -> DestinationProfile:
    values = dict(
        node_id=node.node_id, display_label=node.display_label,
        domains=("academic",), template_binding="tb-academic-coursework",
        template_fields=("subject", "work_type"),
        expected_values=node.expected_values,
        parent_context=(_ACADEMICS_CONTEXT,),
        child_context=(), accepted_group_ids=node.associated_group_ids,
        group_labels=("PHYS1401 course",), representative_files=("f-syllabus",),
        anchor_files=("f-syllabus",),
        anchor_excerpts=(AnchorExcerpt(observation_key="obs-syllabus",
                                       node_id=node.node_id),),
        known_document_types=("syllabus",), known_exclusions=(), user_edits=(),
        restrictions=Restrictions(handling_class=node.handling_class,
                                  accepts_placement=node.accepts_placement,
                                  node_role=node.node_role,
                                  disposition=node.disposition),
    )
    values.update(overrides)
    return DestinationProfile(**values)


#: The walking skeleton's tree. B8(b) (`planning/04-resolutions.md:143-146`) gives
#: it a SECOND RETRIEVABLE node on purpose, so the margin path is exercised rather
#: than bypassed.
#:
#: `n-course-alt` is NOT that node. Its expected `subject = PHYS1402` CONTRADICTS
#: the skeleton file's `subject = PHYS1401`, so `retrieve` suppresses it as a
#: conflict (`retrieval.py`'s `contradicted` branch) and it never becomes a
#: candidate. It earns its place proving §6.3's suppression and populating
#: `conflicts_considered`, but a suppressed node measures no margin.
#:
#: `n-course-shared` is the second CANDIDATE. It carries no expected value, so it
#: can never be contradicted, and it is reached through the accepted-group channel
#: -- which is §6.9's own "Shared Application Materials" shape one level down.
NODES: tuple[Node, ...] = (
    _node(),
    _node(node_id="n-course-alt", display_label="PHYS1402", ordinal=2,
          associated_group_ids=("g-phys1402",),
          expected_values=(ExpectedValue(field="subject", value="PHYS1402"),)),
    _node(node_id="n-course-shared", display_label="Shared Course Materials",
          ordinal=3, associated_group_ids=("g-shared",),
          dimension_role=None, dimension=None, expected_values=(),
          node_role="shared-material",
          explanation="Material shared across courses, reached by accepted group.",
          refinement_disposition="shallow-by-choice",
          refinement_reason="Shared material is one level by design (§6.9)."),
    _node(node_id="n-academics", display_label="Academics",
          parent_node_id=None, ordinal=0, associated_group_ids=(),
          dimension_role=None, dimension=None, expected_values=(),
          refinement_disposition="shallow-by-choice",
          refinement_reason="The user wants one level here and said so."),
    _node(node_id="n-general", display_label="General",
          parent_node_id="n-academics", ordinal=9, node_role="scoped-general",
          associated_group_ids=(), dimension_role=None, dimension=None,
          expected_values=(), refinement_disposition="shallow-by-choice",
          refinement_reason="§5.9's scoped fallback under a meaningful parent."),
    # No `existing_path`: P10's `Node.__post_init__` raises `MalformedTreeRecord`
    # when one is set on a node whose `node_type != existing`, and ignoring a
    # folder RECLASSIFIES it away from `existing`. §5.10's guarantee is carried
    # by `accepts_placement = false`, which is the field the index reads.
    _node(node_id="n-ignored", display_label="Old Downloads",
          node_type="ignored", parent_node_id=None, ordinal=8,
          associated_group_ids=(), dimension_role=None, dimension=None,
          expected_values=(),
          accepts_placement=False, refinement_disposition="shallow-by-choice",
          refinement_reason="The user chose to leave this folder untouched (§5.10)."),
    _node(node_id="n-review-later", display_label="To Sort",
          node_type="existing", parent_node_id=None, ordinal=7,
          node_role="residual", disposition="review-only",
          associated_group_ids=(), dimension_role=None, dimension=None,
          expected_values=(), existing_path="/Users/x/To Sort",
          refinement_disposition="shallow-by-choice",
          refinement_reason="Review Later mapped onto an existing folder (§7.4)."),
)

#: Invariant 3 of the seam contract: the freeze record's legal set IS the set of
#: nodes that accept placement. `build_destination_index` asserts the index equals
#: it, so a fixture that let the two drift would hide the defect the assert exists
#: to catch.
FREEZE_RECORD = FreezeRecord(
    plan_version_id="plan-1", created_at="2026-01-01T00:00:00Z",
    node_ids=tuple(node.node_id for node in NODES),
    legal_destination_ids=frozenset(
        node.node_id for node in NODES if node.accepts_placement),
    template_bindings=("tb-academic-coursework",),
    labels_and_aliases={}, residual_configuration={},
    shared_material_policy_ids=("smp-1",), cross_folder_moves=False,
    selection_id="sel-1",
)

FROZEN_TREE = FrozenTree(
    plan_version_id="plan-1", freeze_record=FREEZE_RECORD, nodes=NODES,
    profiles=tuple(_profile(node) for node in NODES),
    shared_material_policy="mandatory-review",
    shared_material_policy_scope=None,
)


def tree_with(**overrides) -> FrozenTree:
    return replace(FROZEN_TREE, **overrides)


def next_version(tree: FrozenTree = None, *, plan_version_id: str,
                 suffix: str, drop: tuple[str, ...] = (),
                 edit=None) -> FrozenTree:
    """The same tree, adopted as a new plan version, minted P10's way.

    P10 answered its OQ5 by minting a **new `node_id` for every plan version** and
    recording lineage in `origin_node_id`
    (`planning/38-p10-p11-connection-contract.md` §5.2; P10's own
    `test_a_copied_node_keeps_its_lineage_and_gets_a_new_identity` asserts
    `before["n_root"].node_id != after["n_root"].node_id`). So NO `node_id`
    survives a draft, and a fixture that reused the previous version's ids would
    be testing a world P10 does not build -- and would hide the exact defect
    Task 17 exists to prevent.

    `drop` names ORIGIN ids to remove, because that is the only identity that
    spans the two versions. `edit` is applied after minting, so a test can rename
    or relocate a node the way a real draft does.
    """
    tree = FROZEN_TREE if tree is None else tree
    mint = lambda node_id: f"{node_id}{suffix}"
    survivors = tuple(node for node in tree.nodes
                      if node.origin_node_id not in drop)
    minted = []
    for node in survivors:
        node = replace(
            node, plan_version_id=plan_version_id, node_id=mint(node.node_id),
            parent_node_id=(None if node.parent_node_id is None
                            else mint(node.parent_node_id)),
            origin_node_id=node.origin_node_id)
        minted.append(node if edit is None else edit(node))
    minted = tuple(minted)
    kept = {node.origin_node_id for node in survivors}
    by_origin = {node.node_id: node.origin_node_id for node in tree.nodes}
    profiles = tuple(
        replace(profile, node_id=mint(profile.node_id))
        for profile in tree.profiles if by_origin[profile.node_id] in kept)
    return replace(
        tree, plan_version_id=plan_version_id, nodes=minted, profiles=profiles,
        freeze_record=replace(
            tree.freeze_record, plan_version_id=plan_version_id,
            node_ids=tuple(node.node_id for node in minted),
            legal_destination_ids=frozenset(
                node.node_id for node in minted if node.accepts_placement)))
