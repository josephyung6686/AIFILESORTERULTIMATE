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
from dataclasses import asdict, dataclass, fields as _dataclass_fields

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


#: The three `IndexEntry` fields §6.3 can reach a node THROUGH, and the whole set
#: of them. `retrieve` reads a subject's stated fields, its accepted group ids,
#: its curated folder labels and a list of semantic node ids; the fourth is a
#: list of node ids and needs no term. Anything else on the entry -- the ancestor
#: labels, the representative files, the document types -- is read AFTER a node
#: is already a candidate, so indexing it would build a term nothing queries.
TERM_SOURCES: tuple[str, ...] = (
    "expected_values", "accepted_group_ids", "display_label",
)
assert set(TERM_SOURCES) <= {field.name for field in _dataclass_fields(IndexEntry)}


def _terms_of(entry: IndexEntry) -> tuple[tuple[str, str, str, int], ...]:
    """`(source_field, term_key, term_value, ordinal)` for one entry.

    `ordinal` exists for `expected_values` alone and is load-bearing there:
    `retrieve` walks a node's expected values IN ORDER and the facts it collects
    keep that order on the record. The other two sources are read as sets.

    The label is folded once here rather than per subject, which is the point of
    an index: `retrieve` casefolds the SUBJECT's labels, which are few, and never
    the tree's, which are many.
    """
    rows = [("expected_values", field, value, ordinal)
            for ordinal, (field, value) in enumerate(entry.expected_values)]
    rows += [("accepted_group_ids", group_id, "", ordinal)
             for ordinal, group_id in enumerate(entry.accepted_group_ids)]
    rows.append(("display_label", entry.display_label.casefold(),
                 entry.display_label, 0))
    return tuple(rows)


#: The byte that joins a field to its value inside one SQL parameter, and joins
#: node ids inside one `group_concat`. `char(31)` is ASCII Unit Separator: it
#: cannot occur in a P10 node id, a P6 field key or a fact value, all of which are
#: printable, so the join is unambiguous without escaping.
_UNIT: str = "\x1f"


@dataclass(frozen=True)
class Reachable:
    """Every node §6.3 can reach for one subject, and nothing else.

    A node absent from all of these carries none of the subject's stated fields,
    is in none of its groups, does not wear a label it named, and is not a
    semantic neighbour. §6.3's loop would have collected nothing from it and
    suppressed nothing on it, so skipping it is a provable no-op -- which is what
    makes this narrowing a performance change and not a behaviour change.

    The match/contradiction split is decided in SQL rather than in Python because
    it is the one part of retrieval that is unavoidably proportional to the tree:
    §6.3 requires every node ruled out by a conflicting value to be RECORDED
    (SPEC:502-504), and P8 Site C rejects a dossier citing a conflict this list
    omits. So the list is produced, but it is produced by one aggregate query
    instead of a Python pass over every node the user froze.
    """
    #: node_id -> the `(field, value)` pairs the subject's facts MATCH, in the
    #: entry's own order, which is the order the facts land on the record in.
    matched_pairs: dict[str, tuple[tuple[str, str], ...]]
    #: field -> the node ids that carry that field with a value the subject
    #: contradicts, one entry per contradicting value, exactly as §6.3's loop
    #: appended them.
    contradicted: dict[str, tuple[str, ...]]
    contradicted_node_ids: frozenset[str]
    accepted_groups: dict[str, frozenset[str]]
    label_matches: frozenset[str]
    semantic_matches: frozenset[str]

    @property
    def candidate_node_ids(self) -> tuple[str, ...]:
        """The nodes a channel reaches and no conflict rules out, sorted."""
        reached = (set(self.matched_pairs) | set(self.accepted_groups)
                   | self.label_matches | self.semantic_matches)
        return tuple(sorted(reached - self.contradicted_node_ids))


def _in_clause(count: int) -> str:
    return ", ".join("?" * count)


def reachable_entries(conn: sqlite3.Connection, *, plan_version: str,
                      pairs: frozenset[tuple[str, str]],
                      group_ids: frozenset[str], labels: frozenset[str],
                      node_ids: frozenset[str]) -> Reachable:
    """§6.2's index used as an index: four narrow reads, no payload parsed.

    `retrieve` used to open with `entries_for_plan` and walk every legal node,
    deserialising each one -- `planning/58-SCALE-STRESS.md` §2 measured x4.2 per
    file for a four-fold tree, which makes total placement cost files x nodes.

    Two reads carry the direct-fact channel and they are asymmetric on purpose.
    The MATCH is an exact index seek on `(field, value)`, so it costs the size of
    the answer. The CONTRADICTION cannot be: §6.3 requires every node a
    conflicting value ruled out to be recorded (SPEC:502-504) and P8's Site C
    rejects a dossier citing a conflict this list omits, so the list is as long
    as the number of nodes carrying that field however it is computed. What this
    does is stop paying PYTHON for each of them -- SQLite assembles the ids into
    one string per field and the matched rows are removed from it here.

    Nothing here decides anything. `retrieval.retrieve` applies every §6.3 rule.
    """
    fields = sorted({field for field, _ in pairs})
    matched: dict[str, list[tuple[int, str, str]]] = {}
    matched_rows: dict[tuple[str, str], int] = {}
    contradicted: dict[str, tuple[str, ...]] = {}
    if fields:
        scope = ("FROM placement_index_terms WHERE plan_version = ? AND "
                 "source_field = 'expected_values' AND superseded_by IS NULL")
        values = ", ".join("(?, ?)" for _ in pairs)
        flat = [item for pair in sorted(pairs) for item in pair]
        for row in conn.execute(
                f"SELECT node_id, ordinal, term_key, term_value {scope} AND "
                f"(term_key, term_value) IN (VALUES {values})",
                (plan_version, *flat)):
            matched.setdefault(row["node_id"], []).append(
                (row["ordinal"], row["term_key"], row["term_value"]))
            key = (row["term_key"], row["node_id"])
            matched_rows[key] = matched_rows.get(key, 0) + 1
        # ONE row per stated field rather than one per node. The predicate is a
        # pure index range so SQLite never evaluates an expression per row; the
        # rows that MATCHED are subtracted below, as a multiset, because a node
        # carrying two values for one field is contradicted once per value it
        # states that the subject does not -- which is what §6.3's loop did when
        # it appended inside the inner iteration.
        for row in conn.execute(
                f"SELECT term_key, group_concat(node_id, char(31)) AS ids {scope} "
                f"AND term_key IN ({_in_clause(len(fields))}) GROUP BY term_key",
                (plan_version, *fields)):
            field = row["term_key"]
            ruled_out: list[str] = []
            for node_id in row["ids"].split(_UNIT):
                key = (field, node_id)
                if matched_rows.get(key):
                    matched_rows[key] -= 1
                else:
                    ruled_out.append(node_id)
            if ruled_out:
                contradicted[field] = tuple(ruled_out)
    groups: dict[str, set[str]] = {}
    if group_ids:
        for row in conn.execute(
                "SELECT node_id, term_key FROM placement_index_terms WHERE "
                "plan_version = ? AND source_field = 'accepted_group_ids' AND "
                f"term_key IN ({_in_clause(len(group_ids))}) AND "
                "superseded_by IS NULL", (plan_version, *sorted(group_ids))):
            groups.setdefault(row["node_id"], set()).add(row["term_key"])
    matched_labels: set[str] = set()
    if labels:
        matched_labels = {
            row["node_id"] for row in conn.execute(
                "SELECT node_id FROM placement_index_terms WHERE "
                "plan_version = ? AND source_field = 'display_label' AND "
                f"term_key IN ({_in_clause(len(labels))}) AND "
                "superseded_by IS NULL", (plan_version, *sorted(labels)))
        }
    semantic: set[str] = set()
    if node_ids:
        # Legality, asked of the entries table rather than assumed of the
        # caller's list. §5.10: an `ignored` node is not in the index at all, so
        # a semantic neighbour naming one is not a candidate the user argues with.
        semantic = {
            row["node_id"] for row in conn.execute(
                "SELECT node_id FROM placement_index_entries WHERE "
                f"plan_version = ? AND node_id IN ({_in_clause(len(node_ids))}) "
                "AND superseded_by IS NULL", (plan_version, *sorted(node_ids)))
        }
    return Reachable(
        matched_pairs={
            node_id: tuple((field, value) for _, field, value in sorted(rows))
            for node_id, rows in matched.items()
        },
        contradicted=contradicted,
        contradicted_node_ids=frozenset(
            node_id for found in contradicted.values() for node_id in found),
        accepted_groups={node_id: frozenset(found)
                         for node_id, found in groups.items()},
        label_matches=frozenset(matched_labels),
        semantic_matches=frozenset(semantic),
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
            for source_field, term_key, term_value, ordinal in _terms_of(entry):
                conn.execute(
                    "INSERT INTO placement_index_terms (record_id, plan_version, "
                    "node_id, source_field, term_key, term_value, ordinal, "
                    "created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (f"{entry.plan_version}:{entry.node_id}:{source_field}:"
                     f"{ordinal}:{term_key}",
                     entry.plan_version, entry.node_id, source_field, term_key,
                     term_value, ordinal, observed_at),
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


def _entry_of(payload: str) -> IndexEntry:
    body = json.loads(payload)
    for name, value in body.items():
        if isinstance(value, list):
            body[name] = tuple(value)
    body["expected_values"] = tuple(tuple(pair) for pair in body["expected_values"])
    return IndexEntry(**body)


def entry_for(conn: sqlite3.Connection, *, plan_version: str,
              node_id: str) -> IndexEntry | None:
    row = conn.execute(
        "SELECT payload FROM placement_index_entries WHERE plan_version = ? AND "
        "node_id = ? AND superseded_by IS NULL", (plan_version, node_id),
    ).fetchone()
    return None if row is None else _entry_of(row["payload"])


def entries_for_plan(conn: sqlite3.Connection, *,
                     plan_version: str) -> tuple[IndexEntry, ...]:
    """One query. It was `legal_node_ids` plus one `SELECT` and one `json.loads`
    PER NODE, which made a whole-plan read N+1 round trips
    (`planning/58-SCALE-STRESS.md` §2). The node id order is unchanged, because
    callers in `versions.py` compare sets built from it."""
    return tuple(
        _entry_of(row["payload"]) for row in conn.execute(
            "SELECT payload FROM placement_index_entries WHERE plan_version = ? "
            "AND superseded_by IS NULL ORDER BY node_id", (plan_version,))
    )
