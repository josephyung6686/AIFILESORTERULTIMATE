# src/tree_design/health.py
"""§5.5's live counts, §5.9's warnings, §5.11's tree health.

All three are computed from local facts and involve no model call, which is why
§8.6 can leave them out of the ceilings: they are cheap by construction.

Two framing rules carry as much weight as the arithmetic. §5.2 requires an
explanation "rather than a technical confidence score", so nothing here returns a
number the user is meant to read as certainty. §5.11 says health "should not
imply that the system must account for every file immediately", so there is no
completeness score and no percentage presented as a grade.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from tree_design.config import TreeLimits
from tree_design.records import MalformedTreeRecord, Node
from tree_design.vocabulary import (
    RECOMMEND_FLATTEN,
    WARN_EXCESSIVE_DEPTH,
    WARN_ONE_CHILD,
    WARN_REPEATED_PARENT,
    WARN_TINY_FOLDERS,
)


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


def _children(nodes: Sequence[Node], node_id: str) -> tuple[Node, ...]:
    return tuple(node for node in nodes if node.parent_node_id == node_id)


def _descendants(nodes: Sequence[Node], node_id: str) -> tuple[Node, ...]:
    found: list[Node] = []
    frontier = [node_id]
    while frontier:
        current = frontier.pop()
        for child in _children(nodes, current):
            found.append(child)
            frontier.append(child.node_id)
    return tuple(found)


def _depth(nodes: Sequence[Node], node_id: str) -> int:
    by_id = {node.node_id: node for node in nodes}
    depth = 0
    current = by_id.get(node_id)
    while current is not None and current.parent_node_id is not None:
        depth += 1
        current = by_id.get(current.parent_node_id)
    return depth


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
    """
    members = tuple(dict.fromkeys(members_by_node.get(node_id, ())))
    return BranchCounts(
        node_id=node_id,
        child_count=len(_children(nodes, node_id)),
        descendant_count=len(_descendants(nodes, node_id)),
        member_count=len(members),
        example_members=members,
        unresolved_file_ids=tuple(unresolved_by_node.get(node_id, ())),
        evidence_gap_file_ids=tuple(evidence_gaps_by_node.get(node_id, ())),
        sensitive_isolated=node_id in sensitive_node_ids,
        stale=stale,
    )


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
    """
    fired: list[Warning_] = []

    for node in nodes:
        counts = counts_by_node.get(node.node_id)
        if counts is None:
            continue

        if counts.child_count == 1:
            only = _children(nodes, node.node_id)[0]
            fired.append(Warning_(
                WARN_ONE_CHILD, node.node_id,
                f"this level produces one child, {only.display_label!r}; opening "
                "it shows a single folder",
                (only.node_id,),
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
                tuple(repeated),
            ))

        depth = _depth(nodes, node.node_id)
        if depth > limits.excessive_depth_warning:
            fired.append(Warning_(
                WARN_EXCESSIVE_DEPTH, node.node_id,
                f"this node sits at depth {depth}, past the configured warning "
                f"depth of {limits.excessive_depth_warning}",
                (node.node_id,),
            ))

        children = _children(nodes, node.node_id)
        tiny = [
            child.node_id for child in children
            if counts_by_node.get(child.node_id) is not None
            and counts_by_node[child.node_id].member_count
            <= limits.tiny_folder_max_files
        ]
        if len(tiny) >= limits.tiny_folder_count_warning:
            fired.append(Warning_(
                WARN_TINY_FOLDERS, node.node_id,
                f"{len(tiny)} of this level's children hold "
                f"{limits.tiny_folder_max_files} file(s) or fewer",
                tuple(tiny),
            ))

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

    return tuple(fired)


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
