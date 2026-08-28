# src/tree_design/health.py
"""§5.5's live counts, §5.9's warnings, §5.11's tree health.

All three are computed from local facts and involve no model call, which is why
§8.6 can leave them out of the ceilings: they are cheap by construction.

Two framing rules carry as much weight as the arithmetic. §5.2 requires an
explanation "rather than a technical confidence score", so nothing here returns a
number the user is meant to read as certainty. §5.11 says health "should not
imply that the system must account for every file immediately", so there is no
completeness score and no percentage presented as a grade.

WHAT §5.9 IS FOR, AND THE FAILURE THAT SHAPED THIS MODULE. §5.11 asks for "a good
enough structural gist of the corpus so that only a LIMITED NUMBER of
high-leverage changes remain". A warning that fires on a correct tree spends that
budget on nothing and teaches the user to skip the list, which is worse than
having no list at all. Two of the five warnings here used to do exactly that:
they fired on `00`:78's own recommended path,
`Academics/Columbia/2026-Spring/PHYS1401/Homework`. Neither was mistuned. Both
measured the wrong thing, and the corrections are documented at their call sites.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import TreeLimits
from tree_design.records import MalformedTreeRecord, Node
from tree_design.vocabulary import (
    PROTECTED,
    RECOMMEND_FLATTEN,
    WARN_EXCESSIVE_DEPTH,
    WARN_ONE_CHILD,
    WARN_REPEATED_PARENT,
    WARN_TINY_FOLDERS,
)

def sample_size(limits: TreeLimits) -> int:
    """How many items one list names before it states a count instead.

    READ, NEVER CHOSEN. §8.6's ceiling is called "Maximum folder proposals", and
    every use of it here is one question: how many things does the interface put
    in front of the user at once. `tests/p10/test_p10_no_invention.py` refuses a
    numeric literal anywhere in this package for exactly this reason — a
    presentation constant chosen here would be P10 authoring a number the design
    did not state, and "it is only display" is how the first one always arrives.

    That this key now answers several questions is a real complaint about the
    key and not about the answer; `config.py` documents it, and
    `test_one_ceiling_can_serve_both_the_picker_and_the_depth_limit` is the
    standing evidence that P1 should publish more than one.
    """
    return limits.max_folder_proposals


@dataclass(frozen=True)
class BranchCounts:
    node_id: str
    child_count: int
    descendant_count: int
    member_count: int
    example_members: tuple[str, ...]
    unresolved_file_ids: tuple[str, ...]
    evidence_gap_file_ids: tuple[str, ...]
    sensitive_isolated: bool
    stale: bool


@dataclass(frozen=True)
class Warning_:
    kind: str
    node_id: str
    reason: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class TreeHealth:
    group_coverage: Mapping[str, float]
    files_with_enough_facts: int
    unresolved_node_ids: tuple[str, ...]
    context_supported_node_ids: tuple[str, ...]
    sensitive_isolated_node_ids: tuple[str, ...]
    nodes_needing_decisions: tuple[str, ...]


class _TreeIndex:
    """Every structural fact §5.5 and §5.9 ask for, computed in one pass.

    `_children` used to filter the whole tree to find one node's children,
    `_descendants` called it once per node it reached, and `_depth` rebuilt a
    `{node_id: node}` dict on every call — all three inside a loop over nodes. A
    3,200-node tree took 3.3 seconds and projected to fourteen minutes at 50,000,
    which is the canvas the user is waiting on. Each fact below is O(n) once.
    """

    __slots__ = ("by_id", "children", "depth", "descendants", "concepts",
                 "divides_below")

    def __init__(self, nodes: Sequence[Node]) -> None:
        self.by_id: dict[str, Node] = {node.node_id: node for node in nodes}
        children: dict[str, list[Node]] = {node.node_id: [] for node in nodes}
        roots: list[Node] = []
        for node in nodes:
            parent = node.parent_node_id
            if parent is not None and parent in self.by_id:
                children[parent].append(node)
            else:
                roots.append(node)
        self.children: dict[str, tuple[Node, ...]] = {
            node_id: tuple(kids) for node_id, kids in children.items()}

        # Breadth-first from the roots. A node the walk never reaches sits under
        # a cycle: `tree_nodes.parent_node_id` carries no foreign key, so stored
        # state can hold one, and walking it would hang the canvas instead of
        # reporting anything. It is refused by name, exactly as
        # `parent_concepts_for` refuses it.
        self.depth: dict[str, int] = {}
        self.concepts: dict[str, int] = {}
        dimensions: dict[str, frozenset[str]] = {}
        order: list[Node] = []
        frontier = list(roots)
        for root in roots:
            # A node whose parent_node_id names a node that is not here has one
            # level above it that this tree cannot show. Depth 1 is what the
            # previous walk reported for it and the count is still true.
            self.depth[root.node_id] = 0 if root.parent_node_id is None else 1
            dimensions[root.node_id] = (
                frozenset() if root.dimension is None
                else frozenset({root.dimension}))
            self.concepts[root.node_id] = len(dimensions[root.node_id])
        while frontier:
            current = frontier.pop()
            order.append(current)
            above = dimensions[current.node_id]
            for child in self.children[current.node_id]:
                self.depth[child.node_id] = self.depth[current.node_id] + 1
                if child.dimension is None or child.dimension in above:
                    dimensions[child.node_id] = above
                else:
                    dimensions[child.node_id] = above | {child.dimension}
                self.concepts[child.node_id] = len(dimensions[child.node_id])
                frontier.append(child)
        if len(order) != len(self.by_id):
            unreached = next(node.node_id for node in nodes
                             if node.node_id not in self.depth)
            raise MalformedTreeRecord(
                f"the parent chain above {unreached!r} never reaches a root; a "
                "tree with a cycle has no ancestors to report and no depth to "
                "warn about"
            )

        # Post-order, by walking the breadth-first order backwards: every node's
        # children were appended after it, so they are already answered.
        self.descendants: dict[str, int] = {}
        self.divides_below: dict[str, bool] = {}
        for node in reversed(order):
            kids = self.children[node.node_id]
            self.descendants[node.node_id] = sum(
                1 + self.descendants[kid.node_id] for kid in kids)
            self.divides_below[node.node_id] = len(kids) > 1 or any(
                self.divides_below[kid.node_id] for kid in kids)


#: One tree at a time, held by identity. `branch_counts` is called once per node
#: with the whole tree each time — that is its published signature and its
#: callers' shape — so the index has to survive between calls or the work is
#: quadratic again. Only tuples are cached: a list could be mutated in place
#: between calls and the index would then describe a tree that no longer exists.
#: The tuple is held STRONGLY, which is what makes `id()` safe as a key: a live
#: reference cannot have its address reused. One entry bounds the memory.
_INDEX_CACHE: dict[int, tuple[tuple[Node, ...], _TreeIndex]] = {}


def _index(nodes: Sequence[Node]) -> _TreeIndex:
    if not isinstance(nodes, tuple):
        return _TreeIndex(nodes)
    cached = _INDEX_CACHE.get(id(nodes))
    if cached is not None and cached[0] is nodes:
        return cached[1]
    built = _TreeIndex(nodes)
    _INDEX_CACHE.clear()
    _INDEX_CACHE[id(nodes)] = (nodes, built)
    return built


def _children(nodes: Sequence[Node], node_id: str) -> tuple[Node, ...]:
    return _index(nodes).children.get(node_id, ())


def _descendants_count(nodes: Sequence[Node], node_id: str) -> int:
    return _index(nodes).descendants.get(node_id, 0)


def _depth(nodes: Sequence[Node], node_id: str) -> int:
    return _index(nodes).depth.get(node_id, 0)


def parent_concepts_for(
    nodes: Sequence[Node],
) -> Mapping[str, tuple[str, ...]]:
    """`warnings_for`'s `parent_concepts`, produced from published tree state.

    Each node maps to the dimensions its ANCESTORS express, nearest first. That
    chain is the order the branch was materialised in, and materialisation nests
    by the order the user took — `templates.branch_dimension_roles` reads
    `BranchTemplateBinding.chosen_order_id` and refuses to answer with the
    recipe's recommendation. Nothing in this module can reach a definition, so no
    recommended ordering can arrive here by any route.

    A node with no `dimension` expresses no concept and contributes nothing. A
    `None` in the chain would make two such ancestors look like a repeat of one
    another, and the §5.9 warning would fire on a level nobody split by.
    """
    by_id = {node.node_id: node for node in nodes}
    concepts: dict[str, tuple[str, ...]] = {}
    for node in nodes:
        chain: list[str] = []
        # `tree_nodes.parent_node_id` carries no foreign key, so a cycle is
        # reachable in stored state. Walking one would hang the canvas instead of
        # reporting anything, so it is refused by name.
        seen = {node.node_id}
        current = by_id.get(node.parent_node_id) if node.parent_node_id else None
        while current is not None:
            if current.node_id in seen:
                raise MalformedTreeRecord(
                    f"the parent chain above {node.node_id!r} returns to "
                    f"{current.node_id!r}; a tree with a cycle has no ancestors "
                    "to report and no depth to warn about"
                )
            seen.add(current.node_id)
            if current.dimension is not None:
                chain.append(current.dimension)
            current = (by_id.get(current.parent_node_id)
                       if current.parent_node_id else None)
        concepts[node.node_id] = tuple(chain)
    return concepts


def branch_counts(
    nodes: Sequence[Node],
    *,
    node_id: str,
    members_by_node: Mapping[str, Sequence[str]],
    unresolved_by_node: Mapping[str, Sequence[str]],
    evidence_gaps_by_node: Mapping[str, Sequence[str]],
    sensitive_node_ids: frozenset[str],
    stale: bool = False,
) -> BranchCounts:
    """§5.5's numbers, before a split is committed.

    Members are counted by CANONICAL file identity. An alias or an alternate view
    points at the same file, and counting it twice would tell the user a branch
    holds more than it does.

    `example_members` here is one preview node's own members and is NOT sampled:
    this function is handed one node's list by its caller and has no `limits` to
    read a sample size from. The sample the user actually reads is
    `VerticalOption.example_members`, which is where the whole-branch membership
    was being copied into every option.
    """
    members = tuple(dict.fromkeys(members_by_node.get(node_id, ())))
    index = _index(nodes)
    return BranchCounts(
        node_id=node_id,
        child_count=len(index.children.get(node_id, ())),
        descendant_count=index.descendants.get(node_id, 0),
        member_count=len(members),
        example_members=members,
        unresolved_file_ids=tuple(unresolved_by_node.get(node_id, ())),
        evidence_gap_file_ids=tuple(evidence_gaps_by_node.get(node_id, ())),
        sensitive_isolated=node_id in sensitive_node_ids,
        stale=stale,
    )


def _run_below(index: _TreeIndex, node_id: str) -> tuple[str, ...]:
    """The chain of single-child levels starting here, top first."""
    run = [node_id]
    kids = index.children.get(node_id, ())
    while len(kids) == 1:
        run.append(kids[0].node_id)
        kids = index.children.get(kids[0].node_id, ())
    return tuple(run)


def warnings_for(
    nodes: Sequence[Node],
    counts_by_node: Mapping[str, BranchCounts],
    *,
    limits: TreeLimits,
    parent_concepts: Mapping[str, Sequence[str]],
) -> tuple[Warning_, ...]:
    """§5.9's four warnings and its flattening recommendation.

    Every threshold arrives from `limits`. There is no warning for uneven depth,
    because §5.8 makes uneven depth a REQUIREMENT and a warning against it would
    push the user toward the symmetrical tree the design rejects.

    TWO OF THESE MEASURED THE WRONG THING and fired on `00`:78's own recommended
    path. What changed, and why the numbers were not the problem:

    **One child.** §5.7's wording is "create MEANINGLESS one-child levels", and
    `00`:78 shows which ones are meaningful. `Academics/Columbia/2026-Spring` is
    three single-child levels in a row and the design recommends the path,
    because each supplies what §5.6 requires — "a parent dimension should provide
    the context required to understand the child" — for the three work-type
    folders that DO divide beneath. A single-child level whose subtree never
    divides supplies context for nothing: the user clicks through folders that
    separate no files. That is the one this warns about, once for the whole run
    rather than once per level in it.

    **Excessive depth.** `00`:78 forbids reading depth by itself as a defect —
    "The canvas must support uneven depth ... One branch may require four levels,
    while another should remain flat" — and the ABSOLUTE depth limit is §5.7's
    V3, which uses §8.6's published `tree.max_folder_proposals` and
    REFUSES rather than advises. So the advice cannot be a second absolute-depth
    rule with a number nobody published. What `00`:78 does say is that a branch
    "should offer the dimensions that are actually present in its member groups";
    a level that expresses no new dimension adds a click and no meaning. Depth is
    excessive here when the path is deeper than the number of distinct concepts
    it expresses. `excessive_depth_warning` stays exactly what it was — an
    injected authority with no default — and stays a PRECONDITION: below it
    nothing is said at all. `00`:78's path is four levels expressing five
    distinct concepts, so it is silent; five nested folders expressing one
    concept between them is not.

    THE LIST IS SUMMARISED, AND THE SUMMARY HAS ONE EXEMPTION. A 3,200-node tree
    produced 2,991 warnings, which is not a gist of anything. Past the sample size of
    one kind the rest are counted rather than listed. A warning on a PROTECTED or
    isolated-sensitive node is never one of the counted ones: the standing rule
    is that protected material is marked and counted and never silently omitted,
    and a shortened list that dropped the line saying "this area was protected
    and not opened" would be that omission arriving as a usability improvement.
    """
    index = _index(nodes)
    sample = sample_size(limits)
    fired: list[Warning_] = []

    for node in nodes:
        counts = counts_by_node.get(node.node_id)
        if counts is None:
            continue

        children = index.children.get(node.node_id, ())
        parent = (index.by_id.get(node.parent_node_id)
                  if node.parent_node_id else None)
        if (len(children) == 1
                and not index.divides_below[node.node_id]
                and not (parent is not None
                         and len(index.children[parent.node_id]) == 1)):
            run = _run_below(index, node.node_id)
            only = children[0]
            fired.append(Warning_(
                WARN_ONE_CHILD, node.node_id,
                f"this level produces one child, {only.display_label!r}, and "
                f"nothing below it divides the files either: {len(run) - 1} "
                "level(s) open onto a single folder each, so none of them "
                "separates anything",
                run,
            ))

        repeated = [
            concept for concept in parent_concepts.get(node.node_id, ())
            if node.dimension is not None and concept == node.dimension
        ]
        if repeated:
            fired.append(Warning_(
                WARN_REPEATED_PARENT, node.node_id,
                f"this level splits by {node.dimension!r}, which a parent already "
                "expresses",
                tuple(repeated[:sample]),
            ))

        depth = index.depth[node.node_id]
        concepts = index.concepts[node.node_id]
        if depth > limits.excessive_depth_warning and concepts < depth:
            fired.append(Warning_(
                WARN_EXCESSIVE_DEPTH, node.node_id,
                f"this node sits at depth {depth}, past the configured warning "
                f"depth of {limits.excessive_depth_warning}, and the levels "
                f"above it express {concepts} distinct concept(s) between them; "
                "the rest are folders to click through rather than a division of "
                "the files",
                (node.node_id,),
            ))

        tiny = [
            child.node_id for child in children
            if counts_by_node.get(child.node_id) is not None
            and counts_by_node[child.node_id].member_count
            <= limits.tiny_folder_max_files
        ]
        if len(tiny) >= limits.tiny_folder_count_warning:
            reason = (
                f"{len(tiny)} of this level's children hold "
                f"{limits.tiny_folder_max_files} file(s) or fewer")
            if len(tiny) > sample:
                reason += f"; {sample} of them are named here"
            fired.append(Warning_(
                WARN_TINY_FOLDERS, node.node_id, reason, tuple(tiny[:sample])))

        if node.dimension is not None:
            verdict = limits.materially_improves_retrieval(counts)
            if verdict is False:
                fired.append(Warning_(
                    RECOMMEND_FLATTEN, node.node_id,
                    f"the configured retrieval test says {node.dimension!r} does "
                    "not earn its level here; flattening it keeps the files "
                    "together",
                    (node.dimension,),
                ))

    return _ranked_and_summarised(fired, index, counts_by_node, sample)


def _protected(index: _TreeIndex, counts_by_node: Mapping[str, BranchCounts],
               node_id: str) -> bool:
    """Protected material, by either of the two records that can say so."""
    node = index.by_id.get(node_id)
    counts = counts_by_node.get(node_id)
    return ((node is not None and node.node_type == PROTECTED)
            or (counts is not None and counts.sensitive_isolated))


def _ranked_and_summarised(
    fired: Sequence[Warning_],
    index: _TreeIndex,
    counts_by_node: Mapping[str, BranchCounts],
    sample: int,
) -> tuple[Warning_, ...]:
    """Highest-leverage first, then counted rather than listed past the sample size.

    Leverage is the size of the subtree the warning is about, which is a fact
    already computed and not a score: fixing the level that holds nine hundred
    folders is worth more than fixing the one that holds two. Protected nodes
    sort first and are never summarised away.
    """
    ranked = sorted(
        fired,
        key=lambda w: (
            not _protected(index, counts_by_node, w.node_id),
            -index.descendants.get(w.node_id, 0),
            w.kind,
            w.node_id,
        ),
    )
    by_kind: dict[str, list[Warning_]] = {}
    for warning in ranked:
        by_kind.setdefault(warning.kind, []).append(warning)

    kept: list[Warning_] = []
    for kind, group in by_kind.items():
        protected = [w for w in group
                     if _protected(index, counts_by_node, w.node_id)]
        rest = [w for w in group
                if not _protected(index, counts_by_node, w.node_id)]
        kept.extend(protected)
        kept.extend(rest[:sample])
        remainder = rest[sample:]
        if remainder:
            kept.append(Warning_(
                kind, remainder[0].node_id,
                f"{len(remainder)} further level(s) in this tree raise the same "
                "finding. They are counted here rather than listed one by one, "
                "so that the list stays shorter than the tree it describes; none "
                "of them is a protected area, which is never summarised away",
                tuple(w.node_id for w in remainder[:sample]),
            ))
    # One stable order for the whole list, not one per kind.
    return tuple(sorted(kept, key=lambda w: (
        not _protected(index, counts_by_node, w.node_id),
        -index.descendants.get(w.node_id, 0),
        w.kind,
        w.node_id,
    )))



def tree_health(
    nodes: Sequence[Node],
    *,
    members_by_group: Mapping[str, Sequence[str]],
    placed_by_group: Mapping[str, Sequence[str]],
    files_with_enough_facts: int,
    unresolved_node_ids: Sequence[str],
    context_supported_node_ids: Sequence[str],
    sensitive_isolated_node_ids: Sequence[str],
    nodes_needing_decisions: Sequence[str],
) -> TreeHealth:
    """§5.11's six measures. No completeness score, on purpose.

    §5.11: health "should not imply that the system must account for every file
    immediately ... The goal is to give the user a good enough structural gist of
    the corpus so that only a limited number of high-leverage changes remain." A
    single number would be read as a grade to raise, which is the opposite.
    """
    coverage = {}
    for group_id, members in members_by_group.items():
        total = len(set(members))
        placed = len(set(placed_by_group.get(group_id, ())) & set(members))
        coverage[group_id] = 0.0 if total == 0 else placed / total
    return TreeHealth(
        group_coverage=coverage,
        files_with_enough_facts=files_with_enough_facts,
        unresolved_node_ids=tuple(unresolved_node_ids),
        context_supported_node_ids=tuple(context_supported_node_ids),
        sensitive_isolated_node_ids=tuple(sensitive_isolated_node_ids),
        nodes_needing_decisions=tuple(nodes_needing_decisions),
    )
