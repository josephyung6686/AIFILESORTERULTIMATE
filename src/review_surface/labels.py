"""B3: a node and its ancestor `display_label` chain. Never a path.

P12 alone composes paths. This module composes a TUPLE of labels and never a
string, because a joined string is a path in every way that matters: it acquires
a separator, it gets logged, and the next reader treats it as one. A tuple cannot
be mistaken for a path by anything.

Four failures are raised rather than papered over, and each has the same shape:
returning a shorter or a laundered chain would be a confident lie about where a
node sits.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence

from tree_design.records import Node
from tree_design.store import nodes_for_version

#: The two characters that turn a label into a path fragment. Spelled here once,
#: because a check that spells them again somewhere else is a second home for
#: the rule.
PATH_SEPARATORS: tuple[str, ...] = ("/", "\\")


class NodeNotInVersion(LookupError):
    """A node id, or an ancestor of one, that this plan version does not hold."""


class AncestorCycle(RuntimeError):
    """A parent chain that returns to a node it already visited."""


class LabelIsAPath(ValueError):
    """A display label carrying a path separator.

    Refused rather than escaped or stripped. B3 draws the line between what P13
    shows and what P12 composes, and a label holding a separator has already
    crossed it -- whoever wrote it into the tree meant a path, and P13 rendering
    it would put a path on a surface that promises there are none.
    """


def refuse_path_separator(labels: Sequence[str], *, node_id: str = "") -> tuple[str, ...]:
    """Return `labels` as a tuple, or raise naming the NODE, never the label.

    The message does not repeat the offending label: a refusal that prints it
    has printed a path fragment into whatever reads the message.
    """
    for label in labels:
        for separator in PATH_SEPARATORS:
            if separator in label:
                where = f" on node {node_id!r}" if node_id else ""
                raise LabelIsAPath(
                    f"a display label{where} carries a path separator, so it is "
                    "a path fragment rather than a label. B3 gives P13 display "
                    "labels and gives P12 the paths; the label is not repeated "
                    "here because repeating it would put the fragment in this "
                    "message")
    return tuple(labels)


def label_chain(nodes: Sequence[Node], node_id: str) -> tuple[str, ...]:
    """Root-first labels from the root anchor down to `node_id`.

    A dangling parent raises instead of truncating: a truncated chain reads as
    "this node sits directly under the root", which is a claim about the tree
    rather than an admission that the tree could not be walked.
    """
    by_id = {node.node_id: node for node in nodes}
    if node_id not in by_id:
        raise NodeNotInVersion(
            f"{node_id!r} is not in this plan version; an empty chain would read "
            "as 'at the root', which is a different claim")
    chain: list[str] = []
    seen: set[str] = set()
    current: str | None = node_id
    while current is not None:
        if current in seen:
            raise AncestorCycle(
                f"the parent chain from {node_id!r} revisits {current!r}")
        seen.add(current)
        node = by_id.get(current)
        if node is None:
            raise NodeNotInVersion(
                f"{current!r} is named as a parent but is not in this plan "
                f"version, so the chain to {node_id!r} cannot be composed")
        refuse_path_separator((node.display_label,), node_id=node.node_id)
        chain.append(node.display_label)
        current = node.parent_node_id
    chain.reverse()
    return tuple(chain)


def label_chain_for_version(conn: sqlite3.Connection, *, plan_version: str,
                            node_id: str) -> tuple[str, ...]:
    """The chain as of one plan version. §8.8 mints node ids per version, so the
    version is not optional: the same label sits under a different id per draft."""
    return label_chain(nodes_for_version(conn, plan_version), node_id)
