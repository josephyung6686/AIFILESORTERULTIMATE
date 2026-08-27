"""§6.2's destination-node retrieval index, built after freeze over P10's profiles.

P10 emits the §6.1 profile; P11 builds the index over it and publishes no profile
of its own (B4). The boundary is that the index is a placement MECHANISM while the
profile describes what the user approved.

One entry exists per node with `accepts_placement = true`, and per nothing else.
That is where §5.10's guarantee lives: an `ignored` node is not merely rejected at
validation, it is never retrieved, so a file that resembles it produces an
abstention rather than a suppressed candidate the user has to read about.

`node_exists` is the closure P8's Sites C and D take as their `node_exists`
authority. One source answers both P11's legality test and P8's
NODE_NOT_IN_FROZEN_TREE check; two sources could disagree and the disagreement
would look like a model error.

Nothing here mints a node, names a path, or decides legality. P10 decides it in
`freeze_record.legal_destination_ids` and this module is provably its projection.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from dataclasses import asdict, dataclass

from database_agent.db import transaction

from placement import events as placement_events
from placement.vocabulary import DISPOSITIONS, NODE_ROLES, RESIDUAL_ROLE, check


class FrozenTreeRequired(RuntimeError):
    """The tree P11 was handed is not a complete frozen tree. Never a partial index."""


@dataclass(frozen=True)
class IndexEntry:
    node_id: str
    origin_node_id: str
    plan_version: str
    node_role: str
    disposition: str | None
    display_label: str
    parent_node_id: str | None
    root_anchor: str
    depth: int
    ancestor_labels: tuple[str, ...]
    template_fields: tuple[str, ...]
    expected_values: tuple[tuple[str, str], ...]
    accepted_group_ids: tuple[str, ...]
    group_labels: tuple[str, ...]
    representative_files: tuple[str, ...]
    anchor_excerpt_keys: tuple[str, ...]
    known_document_types: tuple[str, ...]
    parent_context: tuple[str, ...]
    child_context: tuple[str, ...]
    known_exclusions: tuple[str, ...]
    user_edits: tuple[str, ...]
    handling_class: str
    refinement_disposition: str


def _ancestry(node, by_id) -> tuple[int, tuple[str, ...]]:
    labels: list[str] = []
    cursor = node.parent_node_id
    seen: set[str] = {node.node_id}
    while cursor is not None:
        if cursor in seen:
            raise FrozenTreeRequired(f"the ancestry of {node.node_id!r} cycles")
        seen.add(cursor)
        parent = by_id.get(cursor)
        if parent is None:
            raise FrozenTreeRequired(
                f"{node.node_id!r} names parent {cursor!r}, which the frozen tree "
                "does not contain; an index over a broken chain would compose a "
                "path P12 could not resolve"
            )
        labels.append(parent.display_label)
        cursor = parent.parent_node_id
    return len(labels), tuple(reversed(labels))


def _entry(node, profile, by_id) -> IndexEntry:
    depth, ancestors = _ancestry(node, by_id)
    check(node.node_role, NODE_ROLES, name="node_role")
    if node.node_role == RESIDUAL_ROLE:
        check(node.disposition, DISPOSITIONS, name="disposition")
    elif node.disposition is not None:
        raise FrozenTreeRequired(
            f"{node.node_id!r} is {node.node_role!r} and carries a disposition; "
            "§7.4 makes disposition required on a residual node and meaningless "
            "on every other role"
        )
    # P10's `Node.refinement_disposition` is optional because a DRAFT node has not
    # been approved yet; `frozen_tree` guarantees it non-`None`. The index declares
    # the field a `str` on the strength of that guarantee, so it verifies it here
    # rather than storing a null under a non-null type.
    if not node.refinement_disposition:
        raise FrozenTreeRequired(
            f"{node.node_id!r} is in a frozen tree and carries no §5.8 refinement "
            "disposition; without it §6.7 cannot tell a branch that is shallow on "
            "purpose from one nobody finished, and P11 would have to re-derive an "
            "answer the user already gave"
        )
    return IndexEntry(
        node_id=node.node_id, origin_node_id=node.origin_node_id,
        plan_version=node.plan_version_id,
        node_role=node.node_role, disposition=node.disposition,
        display_label=node.display_label, parent_node_id=node.parent_node_id,
        root_anchor=node.root_anchor, depth=depth, ancestor_labels=ancestors,
        template_fields=tuple(profile.template_fields),
        # `ExpectedValue` is P10's frozen dataclass, not a mapping: `item["field"]`
        # would raise `TypeError` on the first real node.
        expected_values=tuple(
            (item.field, item.value) for item in node.expected_values
        ),
        accepted_group_ids=tuple(profile.accepted_group_ids),
        group_labels=tuple(profile.group_labels),
        representative_files=tuple(profile.representative_files),
        # The index FLATTENS what P10 publishes; it never assumes it arrived flat.
        # `AnchorExcerpt` carries `node_id` beside `observation_key` because §6.1
        # wants anchor evidence per node, and the entry keeps only the keys it
        # scores on -- a projection of P10's record, not a rival shape for it.
        anchor_excerpt_keys=tuple(
            excerpt.observation_key for excerpt in profile.anchor_excerpts),
        known_document_types=tuple(profile.known_document_types),
        parent_context=tuple(c.display_label for c in profile.parent_context),
        child_context=tuple(c.display_label for c in profile.child_context),
        known_exclusions=tuple(profile.known_exclusions),
        user_edits=tuple(profile.user_edits),
        handling_class=node.handling_class,
        refinement_disposition=node.refinement_disposition,
    )


def build_destination_index(conn: sqlite3.Connection, tree, *,
                            component_version: str,
                            observed_at: str) -> tuple[IndexEntry, ...]:
    """Build one entry per legal node. Nothing partial reaches the table."""
    if not getattr(tree, "plan_version_id", ""):
        raise FrozenTreeRequired("an index projects one frozen plan version")
    if not getattr(tree, "shared_material_policy", ""):
        raise FrozenTreeRequired(
            "§6.9 requires the frozen tree to carry a shared-material policy; "
            "without one a transcript belonging to two packets has no rule and "
            "P11 would have to pick an institution"
        )
    by_id = {node.node_id: node for node in tree.nodes}
    profiles = {profile.node_id: profile for profile in tree.profiles}
    missing = sorted(node_id for node_id in by_id if node_id not in profiles)
    if missing:
        raise FrozenTreeRequired(
            f"no §6.1 destination profile for {missing}; every frozen node has one "
            "at freeze (B4) and an index built over a partial set would silently "
            "make those nodes unreachable"
        )

    entries = tuple(
        _entry(node, profiles[node.node_id], by_id)
        for node in tree.nodes if node.accepts_placement
    )
    # ONE legality authority, and this line is what keeps it one. P10's freeze
    # record decides the legal set (`freeze_record.legal_destination_ids`); this
    # index is its PROJECTION and must be provably equal. Two callables that can
    # answer the same question differently is the defect
    # `planning/22-p1-p7-connection-contract.md` §6 check 5 names: "exactly one
    # part writes each concept". `legal_node_ids` reads this table, so if the two
    # ever drifted P8's `NODE_NOT_IN_FROZEN_TREE` would fire on a legal node and
    # look like a model error.
    indexed = {entry.node_id for entry in entries}
    if indexed != set(tree.freeze_record.legal_destination_ids):
        raise FrozenTreeRequired(
            "the index disagrees with the freeze record's legal set: "
            f"{sorted(indexed ^ set(tree.freeze_record.legal_destination_ids))} "
            "differ; P10 owns legality and P11 only projects it"
        )
    with transaction(conn):
        for entry in entries:
            conn.execute(
                "INSERT INTO placement_index_entries (record_id, plan_version, "
                "node_id, payload, created_at) VALUES (?, ?, ?, ?, ?)",
                (f"{entry.plan_version}:{entry.node_id}", entry.plan_version,
                 entry.node_id, json.dumps(asdict(entry), sort_keys=True),
                 observed_at),
            )
            placement_events.index_entry_built(
                conn, node_id=entry.node_id, plan_version=entry.plan_version,
                component_version=component_version, observed_at=observed_at,
            )
    return entries


def legal_node_ids(conn: sqlite3.Connection, *, plan_version: str) -> frozenset[str]:
    """SPEC:135-136's set, read from the index rather than recomputed."""
    return frozenset(
        row["node_id"] for row in conn.execute(
            "SELECT node_id FROM placement_index_entries WHERE plan_version = ? "
            "AND superseded_by IS NULL", (plan_version,),
        )
    )


def node_exists(conn: sqlite3.Connection, *,
                plan_version: str) -> Callable[[str, str], bool]:
    """P8's Site C and Site D `node_exists` authority, closed over one version.

    P8 calls it with `(node_id, dossier.plan_version)`. A dossier stamped with a
    different version answers False, because the legal set is per version and a
    decision made against a stale tree is not a legal decision (§8.8).
    """
    legal = legal_node_ids(conn, plan_version=plan_version)

    def exists(node_id: str, called_plan_version: str) -> bool:
        return called_plan_version == plan_version and node_id in legal

    return exists


def entry_for(conn: sqlite3.Connection, *, plan_version: str,
              node_id: str) -> IndexEntry | None:
    row = conn.execute(
        "SELECT payload FROM placement_index_entries WHERE plan_version = ? AND "
        "node_id = ? AND superseded_by IS NULL", (plan_version, node_id),
    ).fetchone()
    if row is None:
        return None
    body = json.loads(row["payload"])
    for name, value in body.items():
        if isinstance(value, list):
            body[name] = tuple(value)
    body["expected_values"] = tuple(tuple(pair) for pair in body["expected_values"])
    return IndexEntry(**body)


def entries_for_plan(conn: sqlite3.Connection, *,
                     plan_version: str) -> tuple[IndexEntry, ...]:
    return tuple(
        entry_for(conn, plan_version=plan_version, node_id=node_id)
        for node_id in sorted(legal_node_ids(conn, plan_version=plan_version))
    )
