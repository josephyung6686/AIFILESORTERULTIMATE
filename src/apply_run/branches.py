"""Which branches did the person name?

The owner's ruling: *"you can blast both one branch or the entire thing or
multiple branches. Like a checkbox. Most flexibility."* This module is the
checkbox. It answers one question -- which destination nodes did these words
select -- and its whole job is to refuse rather than guess.

**A branch is any node in the frozen tree, and naming it names its subtree.**
Not only the top level: `00`:98 makes real trees uneven, and a person who wants
one course filed and not the other three has named a node three levels down.

**Two spellings, both true.** The bare `display_label` when it is unique in the
tree, and the `/`-joined path from the root always. The second exists because
the refusal for an ambiguous label has to name the alternatives, and `84` §6's
other standing rule is that what the screen tells a person to type has to be
true. A refusal that names something untypeable is not a refusal, it is a dead
end.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Mapping

from tree_design.records import Node

#: The separator between a parent's label and a child's in a qualified path. It
#: is `/` because that is what a person reading a folder tree already reads, and
#: because the labels this joins are folder names.
SEPARATOR: str = "/"


class BranchRefused(ValueError):
    """The words named no branch, or named more than one.

    One class for both, because to the person they are one situation -- *this
    did not select what you meant* -- and the message, not the type, is what
    says which. Every message names what there is instead.
    """


def _by_id(nodes: Sequence[Node]) -> Mapping[str, Node]:
    return {node.node_id: node for node in nodes}


def qualified_path(node: Node, nodes: Sequence[Node]) -> str:
    """The node's label, joined to its ancestors' labels, root first."""
    by_id = _by_id(nodes)
    chain, current, seen = [], node, set()
    while current is not None and current.node_id not in seen:
        seen.add(current.node_id)
        chain.append(current.display_label)
        parent = current.parent_node_id
        current = by_id.get(parent) if parent else None
    return SEPARATOR.join(reversed(chain))


def labels_offered(nodes: Sequence[Node]) -> tuple[str, ...]:
    """Every branch, by its full path, sorted.

    Full paths for all of them rather than bare labels for the unambiguous ones:
    a list that mixes the two spellings makes the reader work out which rule each
    line followed, and every one of these is typeable.
    """
    return tuple(sorted(qualified_path(node, nodes) for node in nodes))


def _subtree(node_id: str, nodes: Sequence[Node]) -> frozenset[str]:
    children: dict[str, list[str]] = {}
    for node in nodes:
        children.setdefault(node.parent_node_id or "", []).append(node.node_id)
    found, pending = set(), [node_id]
    while pending:
        current = pending.pop()
        if current in found:
            continue
        found.add(current)
        pending.extend(children.get(current, ()))
    return frozenset(found)


def _matches(name: str, nodes: Sequence[Node]) -> tuple[Node, ...]:
    wanted = name.strip()
    exact = tuple(node for node in nodes
                  if qualified_path(node, nodes) == wanted)
    if exact:
        return exact
    return tuple(node for node in nodes if node.display_label == wanted)


def branches_named(names: Sequence[str], *,
                   nodes: Sequence[Node]) -> frozenset[str]:
    """The node ids the person's words select, or a refusal naming the choices.

    An empty `names` refuses. Selecting nothing and selecting everything are the
    two answers a slip is most likely to produce, and neither may be what a
    silence means: "everything" has its own word in the composition root, and it
    is not the absence of one.
    """
    if not names:
        raise BranchRefused(
            "no branch was named. Name one or more branches, or use the "
            "flag that says every branch, which is spelled out in full so it "
            "cannot be typed by accident.")
    selected: set[str] = set()
    for name in names:
        found = _matches(name, nodes)
        if not found:
            raise BranchRefused(
                f"{name!r} names no branch in this plan. It has "
                f"{len(nodes)}:\n  " + "\n  ".join(labels_offered(nodes)))
        if len(found) > 1:
            paths = sorted(qualified_path(node, nodes) for node in found)
            raise BranchRefused(
                f"{name!r} names {len(found)} branches in this plan and this "
                "will not choose between them. Name the one you meant, "
                "exactly as written here:\n  " + "\n  ".join(paths))
        selected |= _subtree(found[0].node_id, nodes)
    return frozenset(selected)
