# src/tree_design/diff.py
"""§8.8's node-level diff, keyed by lineage rather than by identity.

P10 emits nodes added, removed, renamed, re-parented, re-templated, re-ordered
and type-changed. §8.8's file-level consequence — "twenty-three files now require
renewed review because their previous destination no longer exists" — is computed
by P11 from this diff against its own placement decisions. P10 holds no placement
decision and computes none of it.

Every entry carries a semantic undo label, because a diff the user cannot act on
is a report rather than a control.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass

from tree_design.records import Node
from tree_design.store import nodes_for_version
from tree_design.vocabulary import (
    DIFF_ADDED,
    DIFF_REMOVED,
    DIFF_RENAMED,
    DIFF_REORDERED,
    DIFF_REPARENTED,
    DIFF_RETEMPLATED,
    DIFF_TYPE_CHANGED,
)


@dataclass(frozen=True)
class NodeDiffEntry:
    kind: str
    node_id: str
    origin_node_id: str
    before: Mapping[str, object] | None
    after: Mapping[str, object] | None
    undo_label: str


def _template_key(node: Node) -> tuple | None:
    context = node.template_context
    if context is None:
        return None
    return (context.binding_id, context.template_id, context.template_version,
            context.fragment_id, context.fragment_version, context.dimension_index)


def diff_versions(conn: sqlite3.Connection, *, before: str,
                  after: str) -> tuple[NodeDiffEntry, ...]:
    """Compare two versions by `origin_node_id`, which is what survives a copy."""
    old = {node.origin_node_id: node for node in nodes_for_version(conn, before)}
    new = {node.origin_node_id: node for node in nodes_for_version(conn, after)}
    entries: list[NodeDiffEntry] = []

    for origin, node in sorted(new.items()):
        if origin not in old:
            entries.append(NodeDiffEntry(
                DIFF_ADDED, node.node_id, origin, None,
                {"display_label": node.display_label, "node_type": node.node_type},
                f'Undo adding "{node.display_label}"'))
            continue
        previous = old[origin]
        if previous.display_label != node.display_label:
            entries.append(NodeDiffEntry(
                DIFF_RENAMED, node.node_id, origin,
                {"display_label": previous.display_label},
                {"display_label": node.display_label},
                f'Undo rename of "{previous.display_label}"'))
        if previous.node_type != node.node_type:
            entries.append(NodeDiffEntry(
                DIFF_TYPE_CHANGED, node.node_id, origin,
                {"node_type": previous.node_type},
                {"node_type": node.node_type},
                f'Undo changing "{node.display_label}" to {node.node_type}'))
        previous_parent_origin = _parent_origin(old, previous)
        current_parent_origin = _parent_origin(new, node)
        # A parent that is not in its own version says nothing about whether the
        # child moved. Its removal is already reported as `removed` on the parent
        # itself; a `re-parented` entry here would additionally offer the user an
        # undo control for an edit nobody made.
        unresolved = _PARENT_NOT_IN_VERSION in (previous_parent_origin,
                                                current_parent_origin)
        if not unresolved and previous_parent_origin != current_parent_origin:
            entries.append(NodeDiffEntry(
                DIFF_REPARENTED, node.node_id, origin,
                {"parent_origin": previous_parent_origin},
                {"parent_origin": current_parent_origin},
                f'Undo moving "{node.display_label}"'))
        if previous.ordinal != node.ordinal:
            entries.append(NodeDiffEntry(
                DIFF_REORDERED, node.node_id, origin,
                {"ordinal": previous.ordinal}, {"ordinal": node.ordinal},
                f'Undo reordering "{node.display_label}"'))
        if _template_key(previous) != _template_key(node):
            entries.append(NodeDiffEntry(
                DIFF_RETEMPLATED, node.node_id, origin,
                {"template_context": _template_key(previous)},
                {"template_context": _template_key(node)},
                f'Undo the recipe change on "{node.display_label}"'))

    for origin, node in sorted(old.items()):
        if origin not in new:
            entries.append(NodeDiffEntry(
                DIFF_REMOVED, node.node_id, origin,
                {"display_label": node.display_label, "node_type": node.node_type},
                None, f'Undo removing "{node.display_label}"'))

    return tuple(entries)


#: A parent this version does not hold. Distinct from `None`, which means the
#: node really is a root: reporting a dangling parent as `None` would say the
#: node was moved to the top level, and reporting it as the raw `parent_node_id`
#: is worse still — that id is minted PER VERSION (§8.8), so the two sides can
#: never compare equal and every child of a removed node reads as re-parented.
_PARENT_NOT_IN_VERSION = object()


def _parent_origin(by_origin: Mapping[str, Node],
                   node: Node) -> str | None | object:
    """The parent's LINEAGE id, so a version copy is not read as a re-parenting."""
    if node.parent_node_id is None:
        return None
    for candidate in by_origin.values():
        if candidate.node_id == node.parent_node_id:
            return candidate.origin_node_id
    return _PARENT_NOT_IN_VERSION
