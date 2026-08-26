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
from evidence_shape.canonical import canonical_json

from grouping.records import (
    AnchorFact,
    CandidateGroupDossier,
    Conflict,
    FailurePoint,
    Group,
    Membership,
    StopRuleOutcome,
    Support,
    TypedEdge,
)


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


def record_group(conn: sqlite3.Connection, group: Group) -> str:
    _check_supersession(conn, "groups", "group_id", group)
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


def record_membership(conn: sqlite3.Connection, membership: Membership) -> str:
    _check_supersession(conn, "memberships", "membership_id", membership)
    with transaction(conn):
        conn.execute(
            "INSERT INTO memberships ("
            "membership_id, group_id, file_id, content_hash, basis, decision, "
            "decision_source, support, insufficient_evidence, "
            "insufficiency_statement, conflicts, outlier_flag, "
            "validation_verdict_ref, created_at, supersedes, superseded_by, "
            "supersede_reason"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                membership.membership_id, membership.group_id, membership.file_id,
                membership.content_hash, membership.basis, membership.decision,
                membership.decision_source, _dump(membership.support),
                int(membership.insufficient_evidence),
                membership.insufficiency_statement, _dump(membership.conflicts),
                membership.outlier_flag, membership.validation_verdict_ref,
                membership.created_at, membership.supersedes,
                membership.superseded_by, membership.supersede_reason,
            ),
        )
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


def record_edges(
    conn: sqlite3.Connection, group_id: str, edges: Sequence[TypedEdge],
) -> tuple[str, ...]:
    """Every edge of one graph, in one transaction. `group_id` is the caller's
    context and is not stored: an edge relates two file VERSIONS and outlives the
    group that first drew it."""
    del group_id
    with transaction(conn):
        for edge in edges:
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
    return tuple(edge.edge_id for edge in edges)


def edges_for_group(
    conn: sqlite3.Connection, group_id: str,
) -> tuple[TypedEdge, ...]:
    """Every stored edge, in insertion order. `group_id` is the caller's context;
    the graph that reads them back knows which ids it drew."""
    del group_id
    return tuple(
        TypedEdge(
            edge_id=row["edge_id"], from_file_id=row["from_file_id"],
            to_file_id=row["to_file_id"], edge_type=row["edge_type"],
            evidence_ref=row["evidence_ref"], weight=row["weight"],
            bridge_entity_ref=row["bridge_entity_ref"],
            hub_suppressed=bool(row["hub_suppressed"]),
            created_at=row["created_at"], superseded_by=row["superseded_by"],
        )
        for row in conn.execute("SELECT * FROM group_edges ORDER BY rowid")
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
