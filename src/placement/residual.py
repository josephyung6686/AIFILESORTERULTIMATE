"""§7's workflow. The library is P10's; the ordering, the sets and the gate are P11's.

Two orderings here are contractual and both are enforced by a raise rather than by
a convention, because both are about spend and about what the user was shown.

§7.1: residual runs only after normal classification has been attempted. A set
surfaced during the main pass would present a file as unplaceable before the
engine had finished trying to place it.

§7.6: no per-file residual model call may be issued for a set until that set has a
decision, and a set the user chose to leave in place produces ZERO calls. The gate
is the user's control over cost, so a caller that forgets it must fail loudly
rather than spend quietly.

A third refusal is not about spend. A protected set -- reports, applications and
system or credential-bearing files -- is surfaced and counted like every other set
and is NEVER opened. `require_model_call_permitted` raises on it rather than
returning `False`, because `False` is indistinguishable from "the user chose to
leave this alone" and the two must not read the same: one is a choice, the other
is a prohibition. The set still appears, still carries its count and still states
why, so the files are present-but-untouched rather than silently omitted.

P11 holds no residual template definitions (M10). An enabled residual branch
arrives as an ordinary node carrying `node_role = residual` and its `disposition`,
and a template the user did not enable has no node -- so the §7.7 model cannot
name it and P11 needs no residual-specific legality path at all.
"""
from __future__ import annotations

import dataclasses
import json
import sqlite3
from dataclasses import dataclass

from database_agent.db import transaction

from placement import events as placement_events
from placement.vocabulary import (
    LEAVE_IN_PLACE, REVIEW_WITH_MODEL, SEND_TO_APPROVED_NODE, SET_CHOICES, check,
)


class PlacementPassIncomplete(RuntimeError):
    """§7.1: residual is a second stage and the first has not finished."""


class SetDecisionRequired(RuntimeError):
    """§7.6: this set has no decision, so no per-file model call may be issued."""


class ModelCallNotAuthorised(RuntimeError):
    """The set HAS a decision and that decision did not ask for a model."""


class ProtectedSetNotReadable(RuntimeError):
    """The set is protected. Counted and explained, never opened, and never skipped."""


class ResidualPartitionRequired(RuntimeError):
    """§7.5's review sets are not a fixed taxonomy; the partition is injected."""


@dataclass(frozen=True)
class ResidualSet:
    set_id: str
    plan_version: str
    label: str
    file_count: int
    representative_examples: tuple[str, ...]
    file_type_distribution: tuple[tuple[str, int], ...]
    age_range: tuple[str, str]
    evidence_availability: str
    sensitivity_status: str
    protected: bool
    weak_graph_neighbours: tuple[str, ...]
    reason_not_placed: str
    member_file_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.reason_not_placed:
            raise ValueError(
                "§7.5 requires each set to say why the normal pipeline could not "
                "safely place these files; a set with no reason is a pile"
            )
        if self.file_count != len(self.member_file_ids):
            raise ValueError(
                "the count and the members must agree, or the review screen "
                "reports a number no one can expand"
            )
        if not isinstance(self.protected, bool):
            raise ValueError(
                "`protected` is P7's flag and is a boolean. §8.4 Open question 1 "
                "leaves its relation to the five handling classes unsettled and "
                "has neighbouring parts CONSUME the flag rather than infer it "
                "from the class, so a null here would be read as `false` by every "
                "consumer that tests it -- a protected set becoming an ordinary one"
            )


@dataclass(frozen=True)
class ResidualSetDecision:
    set_id: str
    plan_version: str
    choice: str
    node_id: str | None
    decided_at: str

    def __post_init__(self) -> None:
        check(self.choice, SET_CHOICES, name="choice")
        if (self.node_id is None) is (self.choice == SEND_TO_APPROVED_NODE):
            raise ValueError(
                f"{SEND_TO_APPROVED_NODE!r} names one approved node and every "
                "other choice names none; a node on `create_custom_branch` would "
                "be P11 minting a destination, which §7.4 forbids"
            )


def _set_payload(item: ResidualSet) -> str:
    return json.dumps(dataclasses.asdict(item), sort_keys=True)


def surface_residual_sets(conn: sqlite3.Connection, *, plan_version: str,
                          unplaced, partition, limits,
                          placement_pass_complete: bool,
                          component_version: str,
                          observed_at: str) -> tuple[ResidualSet, ...]:
    """§7.5's screen. A visible summary in review sets, not an automatic cleanup."""
    if not placement_pass_complete:
        raise PlacementPassIncomplete(
            "§7.1: residual review runs only after normal group-aware "
            "classification has been attempted for the corpus. Surfacing now "
            "would call a file unplaceable before the engine finished trying."
        )
    if partition is None:
        raise ResidualPartitionRequired(
            "§7.5's eight-line example is prefaced 'It may show' -- illustrative "
            "counts, not a fixed taxonomy (SPEC Open question 10). The partition "
            "is injected and P11 invents no set names."
        )
    remaining = tuple(unplaced)
    groups = tuple(partition(remaining))
    # The residual screen is the last place a file can be mentioned at all, so a
    # partition that drops one leaves it never shown and never explained -- the
    # "understood and found unimportant" impression §8.6 exists to prevent. An
    # invented id is refused for the mirror-image reason: a count the user cannot
    # expand into real files.
    partitioned = [file_id for group in groups for file_id in group["member_file_ids"]]
    if sorted(partitioned) != sorted(remaining):
        missing = sorted(set(remaining) - set(partitioned))
        extra = sorted(set(partitioned) - set(remaining))
        raise ValueError(
            f"the partition covers {sorted(partitioned)} and the unplaced files "
            f"are {sorted(remaining)}: missing {missing}, invented {extra}. Every "
            "unplaced file appears in exactly one review set or it is never shown"
        )
    surfaced: list[ResidualSet] = []
    with transaction(conn):
        for group in groups:
            members = tuple(group["member_file_ids"])
            ceiling = limits.max_residual_files_per_batch
            # Split, never truncate: §8.6 reduces work and never drops files.
            batches = [members[i:i + ceiling] for i in range(0, len(members), ceiling)]
            for index, batch in enumerate(batches, start=1):
                suffix = f"-{index}" if len(batches) > 1 else ""
                label = group["label"] + (f" ({index} of {len(batches)})"
                                          if len(batches) > 1 else "")
                item = ResidualSet(
                    set_id=f"{plan_version}:{group['label']}{suffix}",
                    plan_version=plan_version, label=label,
                    file_count=len(batch),
                    representative_examples=tuple(group["representative_examples"]),
                    file_type_distribution=tuple(group["file_type_distribution"]),
                    age_range=tuple(group["age_range"]),
                    evidence_availability=group["evidence_availability"],
                    sensitivity_status=group["sensitivity_status"],
                    protected=group["protected"],
                    weak_graph_neighbours=tuple(group["weak_graph_neighbours"]),
                    reason_not_placed=group["reason_not_placed"],
                    member_file_ids=batch,
                )
                conn.execute(
                    "INSERT INTO residual_sets (record_id, plan_version, label, "
                    "payload, created_at) VALUES (?, ?, ?, ?, ?)",
                    (item.set_id, plan_version, item.label,
                     _set_payload(item), observed_at),
                )
                placement_events.residual_set_surfaced(
                    conn, set_id=item.set_id, label=item.label,
                    file_count=item.file_count,
                    reason_not_placed=item.reason_not_placed,
                    component_version=component_version, observed_at=observed_at,
                )
                surfaced.append(item)
    return tuple(surfaced)


def set_decision_id(decision: ResidualSetDecision) -> str:
    """One row address for one set answer, at the moment it was given."""
    return f"{decision.plan_version}:{decision.set_id}:{decision.decided_at}"


def record_set_decision(conn: sqlite3.Connection, decision: ResidualSetDecision, *,
                        component_version: str, observed_at: str,
                        user_id: str) -> str:
    """The user's set-level answer, recorded before any per-file spend.

    The row address carries `decided_at`, and that is not decoration.
    `one_current_set_decision` is a partial unique index over UNSUPERSEDED rows,
    so it already forbids two live answers for one set in one plan version.
    Addressing the row as `plan_version:set_id` as well would forbid a SECOND
    ROW OF ANY KIND -- including the superseding one -- and the three supersede
    columns on this table would be columns no writer could ever reach. §7.10 lets
    a user change a set answer, so the change has to be recordable: supersede the
    old row, then append the new one, exactly as `store.record_decision` does.
    """
    with transaction(conn):
        conn.execute(
            "INSERT INTO residual_set_decisions (record_id, plan_version, set_id, "
            "choice, node_id, decided_at, payload) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (set_decision_id(decision), decision.plan_version,
             decision.set_id, decision.choice, decision.node_id,
             decision.decided_at, json.dumps(dataclasses.asdict(decision),
                                             sort_keys=True)),
        )
        placement_events.residual_set_decided(
            conn, set_id=decision.set_id, choice=decision.choice,
            node_id=decision.node_id, component_version=component_version,
            observed_at=observed_at, user_id=user_id,
        )
    return decision.set_id


def require_set_decision(conn: sqlite3.Connection, *, plan_version: str,
                         set_id: str) -> ResidualSetDecision:
    """§7.6's gate. The set-level answer this plan version recorded, or a refusal."""
    row = conn.execute(
        "SELECT choice, node_id, decided_at FROM residual_set_decisions "
        "WHERE plan_version = ? AND set_id = ? AND superseded_by IS NULL",
        (plan_version, set_id),
    ).fetchone()
    if row is None:
        raise SetDecisionRequired(
            f"set {set_id!r} has no §7.6 decision in {plan_version!r}, so no "
            "per-file residual model call may be issued for it. The set-level "
            "answer is what the user controls the cost with."
        )
    return ResidualSetDecision(
        set_id=set_id, plan_version=plan_version, choice=row["choice"],
        node_id=row["node_id"], decided_at=row["decided_at"],
    )


def model_calls_permitted(decision: ResidualSetDecision) -> bool:
    """Exactly one of §7.6's four choices asks for a model, and it says so.

    `leave_in_place` produces zero calls (SPEC:547). `send_to_approved_node` is
    already a decision and needs no interpretation. `create_custom_branch` is a
    tree edit routed to P10 and produces a new plan version, so the current
    version's residual review for that set is over.

    This answers only "did the user's set choice ask for a model?".
    `require_model_call_permitted` is the gate a caller uses before spending,
    because a boolean cannot express the difference between a choice and a
    prohibition.
    """
    return decision.choice == REVIEW_WITH_MODEL


def require_model_call_permitted(conn: sqlite3.Connection, *, plan_version: str,
                                 residual_set: ResidualSet) -> ResidualSetDecision:
    """The one gate in front of a per-file residual model call.

    Three refusals, each named, and the order matters. Protection is checked
    FIRST and independently of any decision: a protected set that refuses for
    want of a decision would invite the fix "decide it", and the answer to a
    protected set is never a decision. It is counted, explained and left closed.
    """
    if residual_set.protected:
        raise ProtectedSetNotReadable(
            f"set {residual_set.set_id!r} holds protected material "
            f"({residual_set.sensitivity_status!r}) and is marked and counted, "
            "never opened. It stays on the review screen with its count and its "
            "reason; a model call over it is refused rather than skipped, so no "
            "caller can record it as understood and found unimportant."
        )
    decision = require_set_decision(conn, plan_version=plan_version,
                                    set_id=residual_set.set_id)
    if not model_calls_permitted(decision):
        raise ModelCallNotAuthorised(
            f"set {residual_set.set_id!r} was decided {decision.choice!r}, and "
            f"only {REVIEW_WITH_MODEL!r} asks for a model. §7.6: a set the user "
            f"chose to {LEAVE_IN_PLACE!r} produces zero model calls."
        )
    return decision
