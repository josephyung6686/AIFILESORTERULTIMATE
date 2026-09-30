# src/grouping/store.py
"""Writers and readers for P9's six SHARED tables. Acceptance has its own module.

A group, its memberships, its dossier, its edges, its stop-rule outcome and its
failure points are facts about a corpus and survive every plan version.
`group_acceptance` is the one table that carries a version, and putting a version
here would duplicate the group, its dossier, its model response and every line of
its evidence per version.

Supersede-never-overwrite (§8.2). A revision inserts a new row and links the old
one; the schema's triggers refuse both a DELETE and an UPDATE of anything but the
supersession columns, so a writer that tried to correct a row in place fails
rather than losing the original.

No function here names a destination, a node, a path or a template. P9 says which
files belong together; where they go is P10's and P11's, and a P9 writer carrying
one of those would be P9 deciding it.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from dataclasses import fields, is_dataclass

from database_agent.db import transaction
from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from grouping.records import (
    AnchorFact,
    MalformedGroupRecord,
    CandidateGroupDossier,
    Conflict,
    FailurePoint,
    Group,
    Membership,
    StopRuleOutcome,
    Support,
    TypedEdge,
)


#: §8.2 names three P9 event types. This is the one for an edge; the other two
#: are the P8 seam's membership proposal and the review receiver's user decision.
GRAPH_EDGE_CREATION: str = "graph-edge creation"


class RecordAbsent(LookupError):
    """The row is not there. Never a blank record standing in for one."""


def _jsonable(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _jsonable(getattr(value, item.name))
                for item in fields(value)}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _dump(value: object) -> str:
    return canonical_json(_jsonable(value))


def _load(raw: str) -> object:
    return json.loads(raw)


def _tuple_of(record_type, raw: str) -> tuple:
    return tuple(record_type(**_rehydrate(record_type, item)) for item in _load(raw))


def _rehydrate(record_type, body: dict) -> dict:
    """Turn JSON lists back into the tuples the record's own validator requires."""
    out = dict(body)
    for item in fields(record_type):
        value = out.get(item.name)
        if isinstance(value, list):
            if item.name == "support":
                out[item.name] = tuple(Support(**entry) for entry in value)
            elif item.name == "conflicts":
                out[item.name] = tuple(Conflict(**_rehydrate(Conflict, entry))
                                       for entry in value)
            elif item.name == "anchor_facts" or item.name == "key_facts":
                out[item.name] = tuple(AnchorFact(**_rehydrate(AnchorFact, entry))
                                       for entry in value)
            else:
                out[item.name] = tuple(value)
    return out


def _check_supersession(conn: sqlite3.Connection, table: str, key: str,
                        record) -> None:
    """A revision names a predecessor that exists, and says why.

    A supersession with no reason leaves a later reader only the two rows and no
    account of the change, which is the thing §8.2 keeps history for.
    """
    predecessor = getattr(record, "supersedes", None)
    if predecessor is None:
        return
    if not getattr(record, "supersede_reason", None):
        raise ValueError(
            "a supersession carries the reason for the change; without it a later "
            "reader has two rows and no account of why the second exists"
        )
    row = conn.execute(
        f"SELECT {key} FROM {table} WHERE {key} = ?", (predecessor,),
    ).fetchone()
    if row is None:
        raise RecordAbsent(
            f"{predecessor!r} is not in {table}; a revision of a record that does "
            "not exist supersedes nothing"
        )


def _link(conn: sqlite3.Connection, table: str, key: str, record) -> None:
    predecessor = getattr(record, "supersedes", None)
    if predecessor is None:
        return
    conn.execute(
        f"UPDATE {table} SET superseded_by = ?, supersede_reason = ? "
        f"WHERE {key} = ?",
        (getattr(record, key), record.supersede_reason, predecessor),
    )


#: What a re-derivation does NOT assert. `created_at` is when the conclusion was
#: FIRST reached, and a replay re-confirms it rather than reaching it again. The
#: two supersession fields are stamped onto a record by whatever superseded it
#: LATER -- they are its history, not its content, and the part re-deriving it
#: knows nothing about them. `supersedes` is deliberately absent from this tuple:
#: the predecessor a record names IS a claim it makes.
_NOT_RE_DERIVED: tuple[str, ...] = ("created_at", "superseded_by",
                                    "supersede_reason")


def _same_derivation(stored, incoming) -> bool:
    """Whether a re-derived record differs from the stored one only in its history.

    `record_group` states the rule this serves: "A group id derived from its seed
    is an address, so a rerun over unchanged evidence is the same group and not a
    conflict." Two things defeated it, and neither is a claim about the file.

    The clock: `created_at` is the deployment's `now()`, a fresh value on every
    run, so a re-derived record differed from the stored one in that one field and
    was refused as a revision that superseded nothing.

    And supersession: the review step supersedes a membership when it carries it
    onto the group the user confirmed, stamping `superseded_by` and
    `supersede_reason` onto the ORIGINAL row. The next run re-derives that
    original -- correctly, from unchanged evidence -- with both fields empty,
    because P9 does not know what P10's review did afterwards.

    The consequence was that the shipped command crashed on its own SECOND
    invocation against the default database, with a traceback rather than a named
    refusal.

    The stored row stands, and this widens nothing else: a record differing in any
    field outside `_NOT_RE_DERIVED` is still refused exactly as before.
    """
    import dataclasses

    return dataclasses.replace(
        incoming, **{name: getattr(stored, name) for name in _NOT_RE_DERIVED},
    ) == stored


def record_group(conn: sqlite3.Connection, group: Group) -> str:
    """Insert one group, or return the id when the same one is already recorded.

    A group id derived from its seed is an address, so a rerun over unchanged
    evidence is the same group and not a conflict. A row under that id with
    DIFFERENT content is a different failure and is refused rather than
    overwritten -- the trigger would refuse it anyway, and later.
    """
    _check_supersession(conn, "groups", "group_id", group)
    existing = conn.execute(
        "SELECT * FROM groups WHERE group_id = ?", (group.group_id,)).fetchone()
    if existing is not None:
        stored = current_group(conn, group.group_id)
        if stored != group and not _same_derivation(stored, group):
            raise MalformedGroupRecord(
                f"group {group.group_id} is already recorded with different "
                "content; a revision supersedes rather than replaces"
            )
        return group.group_id
    with transaction(conn):
        conn.execute(
            "INSERT INTO groups ("
            "group_id, seed_ref, seed_kind, proposed_basis, anchor_facts, "
            "pre_model_signals, anchor_count, coherence_verdict, "
            "coherence_citations, group_category, display_label, label_source, "
            "conflicts, stop_rule_hits, state, sensitivity_state, dossier_id, "
            "llm_response_ref, validation_verdict_ref, created_by, created_at, "
            "supersedes, superseded_by, supersede_reason"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
            "?, ?, ?, ?, ?)",
            (
                group.group_id, group.seed_ref, group.seed_kind,
                group.proposed_basis, _dump(group.anchor_facts),
                _dump(dict(group.pre_model_signals)), group.anchor_count,
                group.coherence_verdict, _dump(group.coherence_citations),
                group.group_category, group.display_label, group.label_source,
                _dump(group.conflicts), _dump(group.stop_rule_hits), group.state,
                group.sensitivity_state, group.dossier_id, group.llm_response_ref,
                group.validation_verdict_ref, group.created_by, group.created_at,
                group.supersedes, group.superseded_by, group.supersede_reason,
            ),
        )
        _link(conn, "groups", "group_id", group)
    return group.group_id


def current_group(conn: sqlite3.Connection, group_id: str) -> Group:
    row = conn.execute(
        "SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
    if row is None:
        raise RecordAbsent(f"no group {group_id!r}")
    return Group(
        group_id=row["group_id"], seed_ref=row["seed_ref"],
        seed_kind=row["seed_kind"], proposed_basis=row["proposed_basis"],
        anchor_facts=_tuple_of(AnchorFact, row["anchor_facts"]),
        pre_model_signals=_load(row["pre_model_signals"]),
        anchor_count=row["anchor_count"],
        coherence_verdict=row["coherence_verdict"],
        coherence_citations=tuple(_load(row["coherence_citations"])),
        group_category=row["group_category"], display_label=row["display_label"],
        label_source=row["label_source"],
        conflicts=_tuple_of(Conflict, row["conflicts"]),
        stop_rule_hits=tuple(_load(row["stop_rule_hits"])), state=row["state"],
        sensitivity_state=row["sensitivity_state"], dossier_id=row["dossier_id"],
        llm_response_ref=row["llm_response_ref"],
        validation_verdict_ref=row["validation_verdict_ref"],
        created_by=row["created_by"], created_at=row["created_at"],
        supersedes=row["supersedes"], superseded_by=row["superseded_by"],
        supersede_reason=row["supersede_reason"],
    )


def standing_group(conn: sqlite3.Connection, group_id: str) -> Group | None:
    """The recorded group under this id, or `None`. `current_group` without the raise.

    Published because `apply_p8_verdict` has to answer "is this group on disk yet"
    without treating absence as an error: `104` R-16 moves the group's INSERT to
    the moment its AUTHOR is known, so a group reaching the P8 seam unrecorded is
    the normal case for a deployment whose model decides, not a missing row.
    """
    row = conn.execute(
        "SELECT group_id FROM groups WHERE group_id = ?", (group_id,)).fetchone()
    return None if row is None else current_group(conn, group_id)


_MEMBERSHIP_INSERT = (
    "INSERT INTO memberships ("
    "membership_id, group_id, file_id, content_hash, basis, decision, "
    "decision_source, support, insufficient_evidence, "
    "insufficiency_statement, conflicts, outlier_flag, "
    "validation_verdict_ref, created_at, supersedes, superseded_by, "
    "supersede_reason"
    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)


def _membership_values(membership: Membership) -> tuple:
    return (
        membership.membership_id, membership.group_id, membership.file_id,
        membership.content_hash, membership.basis, membership.decision,
        membership.decision_source, _dump(membership.support),
        int(membership.insufficient_evidence),
        membership.insufficiency_statement, _dump(membership.conflicts),
        membership.outlier_flag, membership.validation_verdict_ref,
        membership.created_at, membership.supersedes,
        membership.superseded_by, membership.supersede_reason,
    )


def _stored_membership(conn: sqlite3.Connection,
                       membership_id: str) -> Membership | None:
    row = conn.execute(
        "SELECT * FROM memberships WHERE membership_id = ?",
        (membership_id,)).fetchone()
    return None if row is None else _membership_from(row)


def _refuse_a_different_membership(stored: Membership, membership: Membership) -> None:
    if stored != membership and not _same_derivation(stored, membership):
        raise MalformedGroupRecord(
            f"membership {membership.membership_id} is already recorded with "
            "different content; a revision supersedes rather than replaces"
        )


def record_membership(conn: sqlite3.Connection, membership: Membership) -> str:
    """Insert one membership, or return the id when the same one is recorded."""
    _check_supersession(conn, "memberships", "membership_id", membership)
    existing = _stored_membership(conn, membership.membership_id)
    if existing is not None:
        _refuse_a_different_membership(existing, membership)
        return membership.membership_id
    with transaction(conn):
        conn.execute(_MEMBERSHIP_INSERT, _membership_values(membership))
        _link(conn, "memberships", "membership_id", membership)
    return membership.membership_id


def _membership_from(row: sqlite3.Row) -> Membership:
    return Membership(
        membership_id=row["membership_id"], group_id=row["group_id"],
        file_id=row["file_id"], content_hash=row["content_hash"],
        basis=row["basis"], decision=row["decision"],
        decision_source=row["decision_source"],
        support=tuple(Support(**item) for item in _load(row["support"])),
        insufficient_evidence=bool(row["insufficient_evidence"]),
        insufficiency_statement=row["insufficiency_statement"],
        conflicts=_tuple_of(Conflict, row["conflicts"]),
        outlier_flag=row["outlier_flag"],
        validation_verdict_ref=row["validation_verdict_ref"],
        created_at=row["created_at"], supersedes=row["supersedes"],
        superseded_by=row["superseded_by"],
        supersede_reason=row["supersede_reason"],
    )


def current_membership(conn: sqlite3.Connection, membership_id: str) -> Membership:
    row = conn.execute(
        "SELECT * FROM memberships WHERE membership_id = ?", (membership_id,),
    ).fetchone()
    if row is None:
        raise RecordAbsent(f"no membership {membership_id!r}")
    return _membership_from(row)


def memberships_for_group(
    conn: sqlite3.Connection, group_id: str,
) -> tuple[Membership, ...]:
    return tuple(
        _membership_from(row) for row in conn.execute(
            "SELECT * FROM memberships WHERE group_id = ? AND superseded_by IS NULL "
            "ORDER BY rowid", (group_id,),
        )
    )


def carried_membership(membership: Membership, group_id: str) -> Membership:
    """One membership, as the same file's membership of another group.

    NOT a supersession, and the two `None`s are the whole point. A file's
    membership of the group that was superseded and its membership of the group
    that superseded it are two records about two groups, not two versions of one:
    superseding the first makes it invisible to `memberships_for_group`, so the
    next run over the same database re-proposes the group, carries nothing and
    hands the next part an empty branch. That is measured, not hypothetical --
    it is why `cli.review_and_accept`'s carry says so in its own comment.

    Published here because there are now TWO carries and they must be one
    transform. The person's is `cli.review_and_accept`, merging P9's groups under
    the label they typed. The model's is `104` R-80: a second, differing answer
    about a group mints a superseding row, and the memberships have to arrive on
    it or the new row is a group with no members while the old one keeps them.
    """
    import dataclasses

    return dataclasses.replace(
        membership, membership_id=f"{membership.membership_id}:{group_id}",
        group_id=group_id, supersedes=None, supersede_reason=None)


def carry_memberships(
    conn: sqlite3.Connection, *, from_group_id: str, into_group_id: str,
    except_files: frozenset[str] = frozenset(),
) -> tuple[Membership, ...]:
    """Every standing membership of one group, recorded again as another's.

    `except_files` is the caller saying "this file already has a row on the new
    group, written by whatever authored it". `104` R-80's superseding group is
    written by a model answer that decided some of these files ITSELF, and
    carrying those as well would leave one file two standing memberships of one
    group with two decisions -- nothing in the schema forbids it and every reader
    would then be reading whichever it reached first. The person's carry passes
    none, because a merge decides nothing about a file.
    """
    carried = tuple(
        carried_membership(membership, into_group_id)
        for membership in memberships_for_group(conn, from_group_id)
        if membership.file_id not in except_files
    )
    # The records, not their ids: a carried membership keeps its DECISION, and an
    # uncertain one carries a review obligation its new group has to record too.
    #
    # One transaction for the rows that are new. A carried id is
    # `{source}:{destination}`, so a second carry of the same group finds every
    # row already stored and inserts nothing. The comparison is the one
    # `record_membership` uses, so a row that is already there with different
    # content is still refused.
    fresh: list[Membership] = []
    for membership in carried:
        _check_supersession(conn, "memberships", "membership_id", membership)
        existing = _stored_membership(conn, membership.membership_id)
        if existing is not None:
            _refuse_a_different_membership(existing, membership)
            continue
        fresh.append(membership)
    if fresh:
        with transaction(conn):
            conn.executemany(
                _MEMBERSHIP_INSERT, [_membership_values(item) for item in fresh])
            for membership in fresh:
                _link(conn, "memberships", "membership_id", membership)
    return carried


def live_memberships_of_file(
    conn: sqlite3.Connection, *, file_id: str, content_hash: str,
) -> tuple[Membership, ...]:
    """Every membership still standing for ONE file version, in any group.

    `memberships_for_group` asks the other question -- who is in this group --
    and there was no reader for this one, which is why nothing could notice that
    a file's membership had outlived the fact that put it there.

    Keyed on `content_hash` as well as `file_id`, which is the SPEC's own rule
    for these records: "Group and membership records key on `content_hash`
    alongside `file_id`, so a content change makes a membership's evidence stale
    rather than silently re-pointing it at new bytes." A caller re-deriving one
    file version is asking about that version's memberships and no other's.
    """
    return tuple(
        _membership_from(row) for row in conn.execute(
            "SELECT * FROM memberships WHERE file_id = ? AND content_hash = ? "
            "AND superseded_by IS NULL ORDER BY rowid",
            (file_id, content_hash),
        )
    )


def record_edges(
    conn: sqlite3.Connection, group_id: str, edges: Sequence[TypedEdge], *,
    created_at: str,
) -> tuple[str, ...]:
    """Every edge of one graph, in one transaction, each with its §8.2 event.

    `group_id` is the caller's context and is not stored: an edge relates two file
    VERSIONS and outlives the group that first drew it.

    An edge id is content-derived, so a replay re-derives the same edge and the
    event is appended only for one that is genuinely new -- two creation events
    for one edge would say it was created twice.

    **AND WHEN THE ADDRESS ITSELF MOVES, THE OLD EDGE IS SUPERSEDED (`104` R-67).**
    `_edge_id` hashes the bridge entity, so R-61's change -- from the neighbour's
    `detail` to its `bridge_entity` -- gives the same logical edge a different id.
    Under `INSERT OR IGNORE` alone a re-run then ADDS the newly addressed edge
    BESIDE the old one and both stay live, so the same pair of files is related
    twice and a reader cannot tell which relation the product currently believes.

    `00`:136-153 settles what to do about it, and it is not deletion: *"The product
    must never overwrite the evidence record merely because a later extractor or
    model produces a different answer. A newer result should supersede an earlier
    result while retaining the old observation and the reason it was superseded."*
    The table already agrees -- its delete trigger says "an edge is superseded,
    never removed" -- so the old row stays readable and gains a forward pointer.

    Superseded on the PAIR AND THE KIND, `(from_file_id, to_file_id, edge_type)`,
    which is the edge's identity as a statement about the corpus; `edge_id` is the
    identity of one derivation of it. Only rows that are still live are touched, so
    the first supersede_reason sticks the way §8.2 requires everywhere else.

    `supersedes` is deliberately left NULL on the new row. One new edge may
    supersede several old derivations, and a single-valued column cannot say so;
    the back-pointers on the old rows carry the whole relation without lying about
    its shape.
    """
    del group_id
    # One lookup for the ids in this call. A per-edge select was one round trip
    # per edge of every file that formed a graph. The insert and the supersede
    # stay in call order: an earlier edge must not see a later one that the
    # sequential update had not inserted yet.
    known: set[str] = set()
    if edges:
        # One call's edges, not the corpus. A graph does not approach SQLite's
        # variable limit; the whole-corpus count is many calls, not one.
        placeholders = ",".join("?" * len(edges))
        for row in conn.execute(
                "SELECT edge_id FROM group_edges WHERE edge_id IN "
                f"({placeholders})",
                [edge.edge_id for edge in edges]):
            known.add(row[0])
    with transaction(conn):
        for edge in edges:
            already = edge.edge_id in known
            known.add(edge.edge_id)
            conn.execute(
                "INSERT OR IGNORE INTO group_edges ("
                "edge_id, from_file_id, to_file_id, edge_type, evidence_ref, "
                "weight, bridge_entity_ref, hub_suppressed, created_at, "
                "supersedes, superseded_by, supersede_reason"
                ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    edge.edge_id, edge.from_file_id, edge.to_file_id,
                    edge.edge_type, edge.evidence_ref, edge.weight,
                    edge.bridge_entity_ref, int(edge.hub_suppressed),
                    edge.created_at, None, edge.superseded_by, None,
                ),
            )
            if not already:
                append_event(
                    conn,
                    event_type=GRAPH_EDGE_CREATION,
                    file_id=edge.to_file_id,
                    content_hash=None,
                    subsystem="P9",
                    component_version="p9",
                    observed_at=created_at,
                    explanation=(
                        f"{edge.edge_id} is a {edge.edge_type} edge from "
                        f"{edge.from_file_id} to {edge.to_file_id}, resting on "
                        f"{edge.evidence_ref}"
                    ),
                )
            # `104` R-67. Every OTHER live derivation of this same statement --
            # same files, same kind, different address -- is superseded by the one
            # just written. Run after the insert so the superseding row exists to
            # be pointed at, and scoped to `superseded_by IS NULL` so a reason
            # already recorded is never rewritten.
            conn.execute(
                "UPDATE group_edges SET superseded_by = ?, supersede_reason = ? "
                "WHERE from_file_id = ? AND to_file_id = ? AND edge_type = ? "
                "AND edge_id <> ? AND superseded_by IS NULL",
                (
                    edge.edge_id,
                    "a later run re-derived this relation under a different "
                    "content address; the earlier derivation is kept and is no "
                    "longer the product's current answer about these two files",
                    edge.from_file_id, edge.to_file_id, edge.edge_type,
                    edge.edge_id,
                ),
            )
    return tuple(edge.edge_id for edge in edges)


def edges_for_group(
    conn: sqlite3.Connection, group_id: str, *, include_superseded: bool = False,
) -> tuple[TypedEdge, ...]:
    """The LIVE edges, in insertion order. `group_id` is the caller's context;
    the graph that reads them back knows which ids it drew.

    **Live, not all (`104` R-67).** A superseded edge is kept -- `00`:136-153
    requires the old record to stay readable -- and keeping it is not the same as
    still believing it. Returning both left the same pair of files related twice,
    once under each derivation, so a reader could not tell which relation the
    product currently holds and a count of edges grew with every re-run.

    `include_superseded` is for the reader that wants the history rather than the
    answer, which is the other half of what §8.2 preserves them for.
    """
    del group_id
    if include_superseded:
        return tuple(
            _edge_from(row)
            for row in conn.execute("SELECT * FROM group_edges ORDER BY rowid")
        )
    return tuple(
        _edge_from(row)
        for row in conn.execute(
            "SELECT * FROM group_edges WHERE superseded_by IS NULL "
            "ORDER BY rowid")
    )


def _edge_from(row) -> TypedEdge:
    return TypedEdge(
        edge_id=row["edge_id"], from_file_id=row["from_file_id"],
        to_file_id=row["to_file_id"], edge_type=row["edge_type"],
        evidence_ref=row["evidence_ref"], weight=row["weight"],
        bridge_entity_ref=row["bridge_entity_ref"],
        hub_suppressed=bool(row["hub_suppressed"]),
        created_at=row["created_at"], superseded_by=row["superseded_by"],
    )


def record_stop_rule_outcome(
    conn: sqlite3.Connection, outcome: StopRuleOutcome, *, created_at: str,
) -> str:
    outcome_id = f"{outcome.group_id}:{'+'.join(outcome.rules_fired)}"
    conn.execute(
        "INSERT OR IGNORE INTO stop_rule_outcomes ("
        "outcome_id, group_id, rules_fired, evidence_refs, outcome, created_at"
        ") VALUES (?, ?, ?, ?, ?, ?)",
        (
            outcome_id, outcome.group_id, _dump(outcome.rules_fired),
            _dump(outcome.evidence_refs), outcome.outcome, created_at,
        ),
    )
    return outcome_id


def stop_rule_outcome_for(
    conn: sqlite3.Connection, group_id: str,
) -> StopRuleOutcome | None:
    """`None` when no rule fired. Most groups never fire one, and an empty
    `rules_fired` is refused by the record precisely because it is not an outcome.
    """
    row = conn.execute(
        "SELECT * FROM stop_rule_outcomes WHERE group_id = ? ORDER BY rowid DESC",
        (group_id,),
    ).fetchone()
    if row is None:
        return None
    return StopRuleOutcome(
        group_id=row["group_id"], rules_fired=tuple(_load(row["rules_fired"])),
        evidence_refs=tuple(_load(row["evidence_refs"])), outcome=row["outcome"],
    )


def propose_group_category(
    conn: sqlite3.Connection, *, proposed_value: str, group_id: str,
    display_label: str, proposed_by: str, verdict_ref: str,
    dossier_id: str | None, created_at: str,
) -> bool:
    """`00`'s Q-C: a category the library has not seen, written down ONCE.

    §13.7 is "model names, user confirms": a value the library has not seen "is
    proposed once; the user confirms or renames it; it then belongs to that user's
    vocabulary in the database". Until this existed the value was dropped to NULL
    and nothing said it had been said, so the person had nothing to confirm and
    the model's answer left no trace at all.

    **The proposal is not a filing.** `groups.group_category` stays NULL for the
    same group: `Group.__post_init__` refuses an unrecognised value and P10 selects
    an applicability row BY that field, so writing one would put the material under
    a schema that speaks for somebody else's life. What this records is that a
    question exists.

    `True` when the row was written, `False` when this value had already been
    proposed -- which is the "once" and is not an error: the third group the model
    calls `hobby_projects` is more evidence for the same question, not a second
    question, and the group that first said it is the one a person is shown.
    """
    if not proposed_value:
        raise MalformedGroupRecord(
            "a proposal with no value is not a proposal; the caller checks that "
            "the model said something before recording that it did")
    with transaction(conn):
        cursor = conn.execute(
            "INSERT OR IGNORE INTO group_category_proposals ("
            "proposed_value, group_id, display_label, proposed_by, verdict_ref, "
            "dossier_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (proposed_value, group_id, display_label, proposed_by, verdict_ref,
             dossier_id, created_at))
        return cursor.rowcount == 1


def group_category_proposals(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Every category still waiting on a person, oldest first.

    Published as rows rather than as a record because P9 owns no answer shape for
    one: confirming, renaming and leaving a proposal are Release 2 gestures on a
    surface this part does not own, and a record with no reader would be the
    hand-kept field list `104` R-09 removed.
    """
    return list(conn.execute(
        "SELECT * FROM group_category_proposals ORDER BY rowid"))


def record_failure_point(
    conn: sqlite3.Connection, point: FailurePoint, *, created_at: str,
) -> str:
    """One failure, at one stage. §4.8 keeps the six stages apart because a bad
    group can fail because retrieval brought irrelevant neighbours, because the
    model overgeneralised, or because the label was simply not useful, and a
    collapsed error class cannot tell them apart."""
    failure_id = f"{point.group_id}:{point.stage}:{point.cause_code}"
    conn.execute(
        "INSERT OR IGNORE INTO group_failure_points ("
        "failure_id, group_id, dossier_id, membership_id, stage, cause_code, "
        "evidence_ref, detected_by, created_at"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            failure_id, point.group_id, point.dossier_id, point.membership_id,
            point.stage, point.cause_code, point.evidence_ref, point.detected_by,
            created_at,
        ),
    )
    return failure_id


def record_dossier(
    conn: sqlite3.Connection, dossier: CandidateGroupDossier,
) -> str:
    """The fingerprint is content-derived, so recording the same references twice
    is one row rather than a conflict."""
    conn.execute(
        "INSERT OR IGNORE INTO group_dossiers ("
        "dossier_id, group_id, proposed_basis, payload, dossier_fingerprint, "
        "created_at"
        ") VALUES (?, ?, ?, ?, ?, ?)",
        (
            dossier.dossier_id, dossier.group_id, dossier.proposed_basis,
            _dump(dossier), dossier.dossier_fingerprint, dossier.created_at,
        ),
    )
    return dossier.dossier_id


def stored_dossier(
    conn: sqlite3.Connection, dossier_id: str,
) -> CandidateGroupDossier:
    row = conn.execute(
        "SELECT payload FROM group_dossiers WHERE dossier_id = ?", (dossier_id,),
    ).fetchone()
    if row is None:
        raise RecordAbsent(f"no dossier {dossier_id!r}")
    return _dossier_from(_load(row["payload"]))


def _dossier_from(body: dict) -> CandidateGroupDossier:
    from grouping.records import (
        BudgetSummary,
        DossierFile,
        Excerpt,
        Omissions,
        PrivacySummary,
    )

    def _file(entry: dict) -> DossierFile:
        return DossierFile(
            file_id=entry["file_id"], content_hash=entry["content_hash"],
            document_type=entry["document_type"], basis=entry["basis"],
            key_facts=tuple(
                AnchorFact(**_rehydrate(AnchorFact, item))
                for item in entry["key_facts"]),
            excerpts=tuple(Excerpt(**item) for item in entry["excerpts"]),
            why_retrieved=entry["why_retrieved"],
        )

    return CandidateGroupDossier(
        dossier_id=body["dossier_id"], group_id=body["group_id"],
        proposed_basis=body["proposed_basis"],
        anchor_files=tuple(_file(item) for item in body["anchor_files"]),
        candidate_files=tuple(_file(item) for item in body["candidate_files"]),
        typed_edges=tuple(TypedEdge(**item) for item in body["typed_edges"]),
        key_facts=tuple(
            AnchorFact(**_rehydrate(AnchorFact, item)) for item in body["key_facts"]),
        excerpts=tuple(Excerpt(**item) for item in body["excerpts"]),
        conflicts=tuple(
            Conflict(**_rehydrate(Conflict, item)) for item in body["conflicts"]),
        engine_flagged_outliers=tuple(body["engine_flagged_outliers"]),
        omissions=Omissions(**{
            name: tuple(value) for name, value in body["omissions"].items()
        }),
        privacy=PrivacySummary(
            handling_classes=tuple(body["privacy"]["handling_classes"]),
            redactions_applied=body["privacy"]["redactions_applied"],
            release_decision_ref=body["privacy"]["release_decision_ref"],
        ),
        budget=BudgetSummary(**body["budget"]),
        dossier_fingerprint=body["dossier_fingerprint"],
        created_at=body["created_at"],
    )
