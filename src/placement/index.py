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
from placement.vocabulary import (
    DISPOSITIONS, NODE_ROLES, PROPOSED, RESIDUAL_ROLE, check,
)


class FrozenTreeRequired(RuntimeError):
    """The tree P11 was handed is not a complete frozen tree. Never a partial index."""


class IndexCountsUnavailable(RuntimeError):
    """`placement_index_term_counts` does not cover a term the index carries.

    §6.3's suppression is recorded as a bounded list of names and an exact count,
    and the count is served from that aggregate. Missing, it would silently fall
    back to the length of the list -- four destinations reported where the plan
    ruled out eight hundred -- so it is refused rather than approximated.
    """


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
    #: P10's `Node.node_type`, carried verbatim -- §6 has to be able to tell one
    #: of the person's own folders from one the engine proposes, and P10 owns
    #: that distinction.
    #:
    #: The TYPE and not the path, deliberately. §7.11 and B3 keep every composed
    #: path out of P11 entirely -- "P11 names a node and P12 resolves a path" --
    #: and `Node.existing_path` is the one field in the tree that holds one.
    #: Carrying it here would have put a filesystem path in a published P11
    #: record to answer a question the enum already answers.
    node_type: str = PROPOSED


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
        node_type=node.node_type,
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


#: The byte that joins a field to its value inside one SQL parameter. `char(31)`
#: is ASCII Unit Separator: it cannot occur in a P10 node id, a P6 field key or a
#: fact value, all of which are printable, so the join is unambiguous without
#: escaping.
_UNIT: str = "\x1f"



@dataclass(frozen=True)
class Reachable:
    """Every node §6.3 can reach for one subject, and nothing else.

    A node absent from all of these carries none of the subject's stated fields,
    is in none of its groups, does not wear a label it named, and is not a
    semantic neighbour. §6.3's loop would have collected nothing from it and
    suppressed nothing on it, so skipping it is a provable no-op -- which is what
    makes this narrowing a performance change and not a behaviour change.

    **Suppression is counted in full and named up to a ceiling, and that split is
    the whole of the second narrowing.** §6.3 suppresses a node when the subject
    states a field the node states differently, and every legal node stating that
    field with any other value is one -- so on `planning/58-SCALE-STRESS.md` §2's
    tree the list is 799 long for every file in the corpus, eight million ids
    across a 10,000-file disk, and the sentence the user reads names every folder
    they own. That is the failure the same document records against §5.9's
    warnings under its own heading: "the warning list outgrows the tree it
    describes".

    So the list is a BOUNDED SAMPLE and the count is EXACT. Nothing is silently
    omitted: a conflict that ruled out 799 branches says 799 either way, and the
    ones it does name are the ones a reader can act on.

    Which ones get named is not arbitrary. The nodes a retrieval channel REACHED
    go first, always -- they are the ones §6.3's own sentence is about
    (`00`:107's Columbia branches, pulled at by the essays and ruled out by the
    Duke fact), and they are the ones the user is about to ask "why not that
    one?". The remainder of the budget is filled from the field's own index order,
    which is stable across runs and therefore replayable.

    The budget is `max_retrieved_neighbors`, and reusing it is deliberate rather
    than convenient. `planning/58-SCALE-STRESS.md` item 9 is a complaint about one
    P1 key serving two jobs that "want opposite values"; these two want the SAME
    value, because both answer one question -- how many destinations should a
    human read about one file -- from opposite sides. The candidates it kept and
    the rejections it explains are the same list length by construction.
    """
    #: node_id -> the `(field, value)` pairs the subject's facts MATCH, in the
    #: entry's own order, which is the order the facts land on the record in.
    matched_pairs: dict[str, tuple[tuple[str, str], ...]]
    #: field -> the NAMED node ids that carry that field with a value the subject
    #: contradicts, one entry per contradicting value, exactly as §6.3's loop
    #: appended them. Reached nodes first, then the field's index order, bounded.
    contradicted: dict[str, tuple[str, ...]]
    #: field -> how many `(node, value)` rows in the whole plan that field ruled
    #: out, named or not. Always >= `len(contradicted[field])`.
    contradicted_counts: dict[str, int]
    contradicted_node_ids: frozenset[str]
    accepted_groups: dict[str, frozenset[str]]
    label_matches: frozenset[str]
    semantic_matches: frozenset[str]

    @property
    def candidate_node_ids(self) -> tuple[str, ...]:
        """The nodes a channel reaches and no conflict rules out, sorted.

        `contradicted_node_ids` is the SUPPRESSION set and not the naming set: it
        holds every reached node a conflict removed, whether or not the bounded
        list above found room to name it, so the sample can never let a
        contradicted node back into the candidates.
        """
        reached = (set(self.matched_pairs) | set(self.accepted_groups)
                   | self.label_matches | self.semantic_matches)
        return tuple(sorted(reached - self.contradicted_node_ids))


def _in_clause(count: int) -> str:
    return ", ".join("?" * count)


def _chunks(conn: sqlite3.Connection, node_ids: list[str], *, reserved: int):
    """`node_ids` in slices SQLite will accept as bound parameters.

    Every other `IN (...)` in `src/` is fixed-width, which is why
    `planning/58-SCALE-STRESS.md`'s "What was checked and found sound" could say
    `SQLITE_MAX_VARIABLE_NUMBER` "is not reachable no matter how large a group
    gets". This one is the width of an answer, so the limit becomes reachable and
    the read is sliced to stay under it.

    The size is ASKED OF THE CONNECTION rather than chosen. A constant here would
    be a number P11 invented about somebody else's library, and it would be wrong
    in both directions: 999 on a build compiled to 32,766 wastes reads, and 32,766
    on a build compiled to 999 raises.
    """
    width = conn.getlimit(sqlite3.SQLITE_LIMIT_VARIABLE_NUMBER) - reserved
    if width < 1:
        raise ValueError(
            f"this subject states {reserved} terms, which already exhausts "
            "SQLite's bound-parameter limit before a single node id is named"
        )
    for start in range(0, len(node_ids), width):
        yield node_ids[start:start + width]


def reachable_entries(conn: sqlite3.Connection, *, plan_version: str,
                      pairs: frozenset[tuple[str, str]],
                      group_ids: frozenset[str], labels: frozenset[str],
                      node_ids: frozenset[str], name_limit: int) -> Reachable:
    """§6.2's index used as an index. Every read is the size of its own answer.

    `retrieve` used to open with `entries_for_plan` and walk every legal node,
    deserialising each one -- `planning/58-SCALE-STRESS.md` §2 measured x4.2 per
    file for a four-fold tree, which makes total placement cost files x nodes.

    Four reads find what the subject's own evidence reaches. A fifth asks those
    nodes -- and only those -- which of the subject's stated fields they state
    differently, which is §6.3's suppression over the set it can actually apply
    to. A sixth reads `name_limit` more of the ruled-out nodes per stated field,
    so a small tree still says WHICH branch it rejected. A seventh reads one
    integer per stated field, so the conflict can say how many it ruled out in
    total without visiting them.

    `name_limit` is §8.6's `max_retrieved_neighbors`, passed in rather than known
    here: P11 reads no ceiling of its own (`config.py`).

    Nothing here decides anything. `retrieval.retrieve` applies every §6.3 rule.
    """
    if not isinstance(name_limit, int) or isinstance(name_limit, bool) or (
            name_limit <= 0):
        raise ValueError(
            f"name_limit is {name_limit!r}; §6.3's suppression names at least one "
            "node or the review surface cannot answer 'why not that folder?' at "
            "all, and this module ships no ceiling of its own"
        )
    fields = sorted({field for field, _ in pairs})
    matched: dict[str, list[tuple[int, str, str]]] = {}
    #: field -> how many rows in the WHOLE plan the subject matched, which is the
    #: subtrahend for the plan-wide contradiction count below.
    matched_per_field: dict[str, int] = {}
    if fields:
        values = ", ".join("(?, ?)" for _ in pairs)
        flat = [item for pair in sorted(pairs) for item in pair]
        for row in conn.execute(
                "SELECT node_id, ordinal, term_key, term_value "
                "FROM placement_index_terms WHERE plan_version = ? AND "
                "source_field = 'expected_values' AND superseded_by IS NULL AND "
                f"(term_key, term_value) IN (VALUES {values})",
                (plan_version, *flat)):
            matched.setdefault(row["node_id"], []).append(
                (row["ordinal"], row["term_key"], row["term_value"]))
            matched_per_field[row["term_key"]] = (
                matched_per_field.get(row["term_key"], 0) + 1)
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

    reached = sorted(set(matched) | set(groups) | matched_labels | semantic)
    contradicted: dict[str, list[str]] = {}
    #: The REACHED nodes a conflict removed. This is the suppression set and it is
    #: kept apart from the naming list on purpose: the list is bounded and the
    #: exclusion is not, so a node the sample had no room to name is still barred
    #: from the candidates.
    suppressed: set[str] = set()
    #: The `(field, node, value)` rows already named, so the fill below cannot
    #: name one twice. It is the ROW and not the node, because a node stating two
    #: values the subject does not hold is ruled out twice -- which is what §6.3's
    #: loop did when it appended inside the per-expected-value iteration.
    named_rows: set[tuple[str, str, str]] = set()
    if fields and reached:
        # The reached nodes' own rows for the stated fields. One index seek per
        # chunk, and every row it returns belongs to a node a channel already
        # named -- so this read is the size of the CANDIDATE set, not of the tree.
        for chunk in _chunks(conn, reached, reserved=len(fields) + 1):
            rows = [tuple(row) for row in conn.execute(
                    "SELECT node_id, term_key, term_value FROM "
                    "placement_index_terms WHERE plan_version = ? AND "
                    "source_field = 'expected_values' AND "
                    f"node_id IN ({_in_clause(len(chunk))}) AND "
                    f"term_key IN ({_in_clause(len(fields))}) AND "
                    "superseded_by IS NULL",
                    (plan_version, *chunk, *fields))]
            for node_id, field, value in sorted(rows):
                if (field, value) in pairs:
                    continue
                contradicted.setdefault(field, []).append(node_id)
                named_rows.add((field, node_id, value))
                suppressed.add(node_id)

    # The rest of the naming budget, filled from the field's own index order.
    # `LIMIT` is what makes this affordable: the read stops after `name_limit`
    # rows however many nodes state the field, so a tree of eight hundred courses
    # costs the same as a tree of four. The subject's own values are excluded in
    # SQL so a matched row can never be named as a rejection.
    for field in fields:
        if len(contradicted.get(field, ())) >= name_limit:
            continue
        held = sorted(value for key, value in pairs if key == field)
        for node_id, value in conn.execute(
                "SELECT node_id, term_value FROM placement_index_terms WHERE "
                "plan_version = ? AND source_field = 'expected_values' AND "
                f"term_key = ? AND term_value NOT IN ({_in_clause(len(held))}) "
                "AND superseded_by IS NULL LIMIT ?",
                (plan_version, field, *held, name_limit)):
            if (field, node_id, value) in named_rows:
                continue
            contradicted.setdefault(field, []).append(node_id)
            named_rows.add((field, node_id, value))
            if len(contradicted[field]) >= name_limit:
                break

    counts: dict[str, int] = {}
    if fields:
        # ONE integer per stated field, written when the index was built. The
        # alternative -- `COUNT(*)` over the term rows -- is the same walk over
        # every node stating that field, in C rather than in Python, and still
        # files x nodes.
        answered: set[str] = set()
        for row in conn.execute(
                "SELECT term_key, row_count FROM placement_index_term_counts "
                "WHERE plan_version = ? AND source_field = 'expected_values' AND "
                f"term_key IN ({_in_clause(len(fields))}) AND "
                "superseded_by IS NULL", (plan_version, *fields)):
            answered.add(row["term_key"])
            total = row["row_count"] - matched_per_field.get(row["term_key"], 0)
            if total > 0:
                counts[row["term_key"]] = total
        # A field with no aggregate row is a field no node in this plan states,
        # so it rules nothing out and needs no count. A field with no aggregate
        # row that DID match or contradict something is the aggregate disagreeing
        # with the table it summarises -- and the failure mode is silent: the
        # count would fall back to the bounded list and report four destinations
        # ruled out where the plan ruled out eight hundred. Under-reporting a
        # suppression is the omission the count exists to prevent, so it raises.
        unanswered = sorted(
            {*(field for field in contradicted), *matched_per_field} - answered)
        if unanswered:
            raise IndexCountsUnavailable(
                f"{unanswered} match or contradict rows in "
                f"`placement_index_terms` for {plan_version!r} and have no row in "
                "`placement_index_term_counts`; the aggregate disagrees with the "
                "table it summarises, and a suppression counted from the "
                "bounded list instead would report a handful of destinations "
                "ruled out where the plan ruled out the whole tree"
            )
    # The named ones are always a subset of the counted ones, so no caller can
    # read a count smaller than the list beside it.
    for field, found in contradicted.items():
        counts[field] = max(counts.get(field, 0), len(found))

    return Reachable(
        matched_pairs={
            node_id: tuple((field, value) for _, field, value in sorted(rows))
            for node_id, rows in matched.items()
        },
        contradicted={field: tuple(found[:name_limit])
                      for field, found in sorted(contradicted.items())},
        contradicted_counts=counts,
        contradicted_node_ids=frozenset(suppressed),
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
    #: (plan_version, source_field, term_key) -> how many term rows this build
    #: writes for it. Counted from the same `_terms_of` call the rows come from --
    #: one loop, one source -- so the aggregate cannot describe a different set
    #: from the table. The plan version is part of the key rather than taken from
    #: the tree, because the rows below are written with the ENTRY's version and a
    #: count filed under a different one would be a count of nothing.
    totals: dict[tuple[str, str, str], int] = {}
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
                key = (entry.plan_version, source_field, term_key)
                totals[key] = totals.get(key, 0) + 1
            placement_events.index_entry_built(
                conn, node_id=entry.node_id, plan_version=entry.plan_version,
                component_version=component_version, observed_at=observed_at,
            )
        for (version, source_field, term_key), row_count in sorted(totals.items()):
            conn.execute(
                "INSERT INTO placement_index_term_counts (record_id, "
                "plan_version, source_field, term_key, row_count, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (f"{version}:{source_field}:{term_key}", version, source_field,
                 term_key, row_count, observed_at),
            )
    # The one bulk write P11 makes, and the only place a checkpoint belongs.
    #
    # `open_database` runs WAL with `synchronous = FULL`, so every later autocommit
    # write -- and §8.2 makes `retrieve` write one event per subject -- is an
    # `F_FULLFSYNC`. Until the log is checkpointed, that fsync is paid against
    # whatever this build left in it: four thousand rows for an 800-node tree.
    # Measured, per-file `retrieve` over 20 subjects on the mixed tree:
    #
    #   tree      before        after
    #   200       0.39 ms       0.190 ms
    #   800       0.78 ms       0.185 ms
    #   3200      0.23 ms       0.197 ms
    #
    # -- flat, and the 3200 column is why the diagnosis is the log and not the
    # tree: that build alone was large enough to trip SQLite's own auto-checkpoint,
    # so it was already paying the cheap price before this line existed.
    #
    # PASSIVE and not TRUNCATE: it never blocks a reader, and it is an
    # optimisation of WHERE committed pages live, not of whether they are
    # committed. `synchronous` is untouched and nothing here is a durability
    # trade. On a non-WAL connection it is a no-op.
    #
    # And only from autocommit. SQLite answers a checkpoint issued inside an open
    # transaction with `database table is locked`, and a caller who opened the
    # handle with `sqlite3.connect` rather than `open_database` is holding one:
    # Python's implicit-transaction mode opens a transaction before the first
    # write and holds it until `commit()`, so the boundary above took the SAVEPOINT
    # branch and the caller's transaction is still in flight. Skipping costs the
    # measurement nothing -- a checkpoint moves COMMITTED pages out of the log and
    # with a write still in flight there are none to move -- and issuing it anyway
    # would throw away a completed index build over an optimisation.
    if not conn.in_transaction:
        conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
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
