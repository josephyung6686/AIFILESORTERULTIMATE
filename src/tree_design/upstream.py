# src/tree_design/upstream.py
"""The only module in P10 that names another part's symbols.

Concentrating the seam here has one purpose: when P9 publishes its reader, or P7
adds a handling class, or P3 renames a column, exactly one module breaks and the
error says which upstream name moved. Seven modules importing seven upstream
names produce seven unrelated failures and one long afternoon.

Three of P10's SPEC field names do not exist upstream, and the live name wins:

* the user-approved label is `GroupAcceptance.user_edited_label`, falling back to
  `Group.display_label`; there is no `Group.label`.
* the membership axis is `Membership.basis` over `MEMBERSHIP_BASES`; there is no
  `membership_kind`.
* rejection is `GroupAcceptance.acceptance`, resolved as of a plan version.
  `Group.state = rejected` is impossible — the record checks `state` against
  `GROUP_STATES`, which does not contain it.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from facts.fields import get_field
from facts.read_surface import PROPOSAL_ELIGIBLE_STATES, is_destination_eligible
from facts.supersede import preferred_fact
from grouping.vocabulary import (
    ACCEPTED,
    EXCLUDED,
    INCLUDED,
    DIRECT_ANCHOR,
    MEMBERSHIP_BASES,
    REJECTED,
    TENTATIVE_DISCOVERY,
)
from scan_agent.exclusion import (
    RULE_PROTECTED_CONTAINER,
    exclusion_verdicts,
)
from scan_agent.inventory import CURATION_SIGNAL_VALUES, directory_inventory
from scan_agent.selection import get_selection, selection_candidate_roots
from tree_design.vocabulary import HANDLING_CLASSES, check

#: D2: absent is a gate outcome, not a file fact. P7's store refuses to write it,
#: so P10 renders it and never hands it back.
UNCLASSIFIED = "unreadable_unclassified"


class UpstreamUnavailable(RuntimeError):
    """An upstream value P10 needs is missing, ineligible, or not P6's."""


@dataclass(frozen=True)
class GroupMember:
    file_id: str
    content_hash: str
    basis: str


@dataclass(frozen=True)
class AcceptedGroup:
    """P10's view of one accepted P9 group, in P10's field names.

    `domain` is P9's `group_category` (resolution M12): domain and category are
    one field, not two, so P10 requests no separate `domain`.
    """

    group_id: str
    label: str
    domain: str | None
    members: tuple[GroupMember, ...]
    anchor_facts: tuple[str, ...]
    excluded_members: tuple[str, ...]


@dataclass(frozen=True)
class ExistingFolder:
    directory_path: str
    parent_directory: str | None
    file_count: int
    curation_signal: str


class AcceptedGroupReader(Protocol):
    """What P10 needs from P9.

    Three of the four map onto callables `grouping` has now SHIPPED:

        group(group_id)              -> `store.current_group(conn, group_id)`
        memberships(group_id)        -> `store.memberships_for_group(conn, group_id)`
        stop_rule_outcome(group_id)  -> `store.stop_rule_outcome_for(conn, group_id)`

    `accepted(plan_version_id)` does NOT. P9 publishes
    `acceptance.group_state_as_of(conn, *, group_id, plan_version_id)`, which
    answers for ONE group; nothing enumerates a version's acceptances. Closing
    that is P9's — SPEC corrections row 17 — and it is not worked around here,
    because an enumeration P10 wrote itself would be P10 deciding which groups a
    plan version contains.
    """

    def accepted(self, plan_version_id: str) -> Sequence[object]: ...
    def group(self, group_id: str) -> object: ...
    def memberships(self, group_id: str) -> Sequence[object]: ...
    def stop_rule_outcome(self, group_id: str) -> object | None: ...


def _label(acceptance: object, group: object) -> str:
    edited = getattr(acceptance, "user_edited_label", None)
    if edited:
        return edited
    display = getattr(group, "display_label", None)
    if not display:
        raise UpstreamUnavailable(
            f"group {getattr(group, 'group_id', '?')!r} carries no label. P9 sets "
            "`display_label` only when `coherence_verdict` is 'coherent', so an "
            "unlabelled accepted group is a real state and a branch cannot be "
            "named from it."
        )
    return display


def _is_tentative(reader: AcceptedGroupReader, group_id: str) -> bool:
    """`tentative-discovery` is a STOP RULE OUTCOME, never a `Group.state`.

    The string is in both `GROUP_STATES` and `STOP_RULE_OUTCOMES`, and only the
    second is ever written: `src/grouping/graph.py:334` sets it on a
    `StopRuleOutcome` when SR1 fired alone. Nothing in `src/grouping/` assigns it
    to a group — `pipeline.py:344-347` is the only originating writer of the
    field and it writes `supported` or `candidate`. A guard written as
    `group.state == TENTATIVE_DISCOVERY` would be unreachable — green forever
    and enforcing nothing.
    """
    outcome = reader.stop_rule_outcome(group_id)
    return outcome is not None and outcome.outcome == TENTATIVE_DISCOVERY


def renders_as_branch(reader: AcceptedGroupReader, *, group_id: str) -> bool:
    """Whether P10 may show this group as a destination branch at all.

    Published so a canvas surface can ask directly rather than inferring the
    answer from an absence in `accepted_groups`.
    """
    return not _is_tentative(reader, group_id)


def accepted_groups(reader: AcceptedGroupReader, *,
                    plan_version_id: str) -> tuple[AcceptedGroup, ...]:
    """Every group this plan version accepted, with its members and exclusions."""
    result = []
    for acceptance in reader.accepted(plan_version_id):
        if acceptance.acceptance != ACCEPTED:
            continue
        if _is_tentative(reader, acceptance.group_id):
            # §4.9 permits a group whose only stop rule was SR1 to be shown
            # "only as tentative discovery candidates, if at all". P10's answer
            # is "not at all": a destination branch IS the strong presentation,
            # and a group with no anchor has not earned one. Skipped HERE rather
            # than by each caller, because one caller forgetting is one folder
            # the user never agreed to.
            continue
        group = reader.group(acceptance.group_id)
        memberships = reader.memberships(acceptance.group_id)
        members = []
        excluded = []
        for membership in memberships:
            check(membership.basis, MEMBERSHIP_BASES, name="membership.basis")
            if membership.decision == INCLUDED:
                members.append(GroupMember(
                    file_id=membership.file_id,
                    content_hash=membership.content_hash,
                    basis=membership.basis,
                ))
            elif membership.decision == EXCLUDED:
                excluded.append(membership.file_id)
        result.append(AcceptedGroup(
            group_id=group.group_id,
            label=_label(acceptance, group),
            domain=group.group_category,
            members=tuple(members),
            # `AnchorFact` has no id. Its five fields are (field, value,
            # file_ids, reliability_state, observation_key) —
            # `src/grouping/records.py:85-89` — and `observation_key` is P4's
            # durable citation handle, which is what §6.1's anchor excerpts are
            # cited by as well. Reading `.fact_id` raises AttributeError.
            anchor_facts=tuple(f.observation_key for f in group.anchor_facts),
            excluded_members=tuple(excluded),
        ))
    return tuple(result)


def rejected_group_ids(reader: AcceptedGroupReader, *,
                       plan_version_id: str) -> frozenset[str]:
    """§4.9 and §8.7: a rejected proposal must not resurface as a candidate."""
    return frozenset(
        acceptance.group_id
        for acceptance in reader.accepted(plan_version_id)
        if acceptance.acceptance == REJECTED
    )


def resolve_role_to_field(conn: sqlite3.Connection, *, role_ref: str,
                          field_ref: str) -> str:
    """C2: an organization-layer role resolves to a LIVE, destination-eligible
    P6 field, or the composition fails closed.

    §3.12 forbids inventing a field, and §5.7 asks templates to "use existing
    field types wherever possible". A role that resolves to nothing is a
    configuration gap, never a new fact.
    """
    try:
        row = get_field(conn, field_ref)
    except Exception as exc:  # P6 raises its own lookup error
        raise UpstreamUnavailable(
            f"role {role_ref!r} maps to {field_ref!r}, which P6's field catalogue "
            "does not define. A template may not mint a field (§3.12)."
        ) from exc
    if row is None:
        raise UpstreamUnavailable(
            f"role {role_ref!r} maps to {field_ref!r}, which P6's field catalogue "
            "does not define. A template may not mint a field (§3.12)."
        )
    if not is_destination_eligible(conn, field_key=field_ref):
        raise UpstreamUnavailable(
            f"role {role_ref!r} maps to {field_ref!r}, which P6 marks not "
            "destination-eligible. §3.8 keeps an authoring role out of the tree; "
            "it is supporting evidence, not a folder level."
        )
    return field_ref


def existing_folders(conn: sqlite3.Connection, *,
                     scan_run_id: str) -> tuple[ExistingFolder, ...]:
    """§5.10's inventory, with P3's curation signal carried verbatim.

    `CURATION_SIGNAL_VALUES` is THREE values, not §5.10's two: P3 publishes
    `undetermined` and today returns it for every directory, because §1.1 gives
    one worked case and no threshold. P10 renders it and never rounds it to
    `incidental` — §8.6 requires leaving something in review rather than guessing.
    """
    folders = []
    for row in directory_inventory(conn, scan_run_id):
        signal = row["curation_signal"]
        if signal not in CURATION_SIGNAL_VALUES:
            raise UpstreamUnavailable(
                f"curation signal {signal!r} is not one of P3's "
                f"{CURATION_SIGNAL_VALUES}; P10 renders this signal and derives "
                "none of it (resolution G9)"
            )
        folders.append(ExistingFolder(
            directory_path=row["directory_path"],
            parent_directory=row["parent_directory"],
            file_count=row["file_count"],
            curation_signal=signal,
        ))
    return tuple(folders)


@dataclass(frozen=True)
class ProtectedArea:
    """One area P3 marked, counted and never opened.

    The product owner's standing rule: "reports, apps and system files MUST NOT
    BE MOVED OR READ OR ANYTHING SYSTEM OR SENSITIVE IN THAT SENSE." P3 enforces
    the not-reading half — `exclusion_for` tests `is_protected_container` FIRST,
    before every weaker §1.1 rule, so a `.app` inside `node_modules` is still
    recorded as protected rather than under the rule that understates it.

    This record is the other half: the area has to REACH the tree design, because
    a protected container that is pruned and then never mentioned has been
    silently omitted, and silent omission is the one outcome the rule forbids.
    """

    path: str
    display_label: str
    rule_subject: str
    applies_to: str
    label: str | None
    observed_at: str


def protected_areas(conn: sqlite3.Connection, *,
                    scan_run_id: str) -> tuple[ProtectedArea, ...]:
    """P3's protected containers, for this scan run.

    Filtered on `rule`, not on `label`. The rule is the DECISION P3 made; the
    label is §8.6's display category for the progress line. Selecting on the
    display string would make a presentation change silently alter which areas
    the tree represents.
    """
    areas = []
    for row in exclusion_verdicts(conn, scan_run_id):
        if row["rule"] != RULE_PROTECTED_CONTAINER:
            continue
        areas.append(ProtectedArea(
            path=row["path"],
            display_label=_folder_name(row["path"]),
            rule_subject=row["rule_subject"],
            applies_to=row["applies_to"],
            label=row["label"],
            observed_at=row["observed_at"],
        ))
    return tuple(areas)


def _folder_name(path: str) -> str:
    """The last segment, as a display label. Never the path (resolution B3)."""
    cleaned = path.rstrip("/\\")
    for separator in ("/", "\\"):
        if separator in cleaned:
            cleaned = cleaned.rsplit(separator, 1)[-1]
    return cleaned


def candidate_roots(conn: sqlite3.Connection, *,
                    selection_id: str) -> tuple[str, ...]:
    """§1.1's high-level locations. Every node's `root_anchor` names one."""
    return tuple(str(path) for path in selection_candidate_roots(conn, selection_id))


def cross_folder_moves(conn: sqlite3.Connection, *, selection_id: str) -> bool:
    """§1.1's "whether files may move across high-level folders".

    P3 records it, P10 stores it in the freeze record under §8.8's placement
    policy settings, P12 enforces it at mutation time. P10 neither derives nor
    overrides it.
    """
    row = get_selection(conn, selection_id)
    if row is None:
        raise UpstreamUnavailable(
            f"corpus selection {selection_id!r} does not exist; §1.1's roots and "
            "movement permission are the user's choices and P10 supplies neither"
        )
    return bool(row["cross_folder_moves"])


def handling_class_for(store, *, file_id: str, content_hash: str) -> str:
    """P7's class for one file version, carried, never re-derived (§8.4).

    An absent record reads as the gate outcome. P10 does not classify: §5.2 and
    §8.4 make sensitivity an evidence-backed, user-revisable class that P7 owns.
    """
    record = store.current(file_id, content_hash)
    if record is None:
        return UNCLASSIFIED
    return check(record.handling_class, HANDLING_CLASSES, name="handling_class")


@dataclass(frozen=True)
class FieldValue:
    """One file's settled value for one P6 field, in P6's own spelling.

    `display_label` is P6's, never P10's. §5.4: the system "does not invent
    PHYS1401, UChicago, Spring 2026, or PVA/RDP; those names emerge from
    validated facts". A node label composed here rather than carried would be
    exactly that invention.
    """

    field_ref: str
    canonical_value: str
    display_label: str


def preferred_value_for(conn: sqlite3.Connection, *, file_id: str,
                        field_ref: str) -> FieldValue | None:
    """The one value this file contributes at this dimension, or `None`.

    `facts.supersede.preferred_fact` is the live surface and it answers exactly
    three cases (`src/facts/supersede.py:180-210`): a `user_confirmed` live row
    wins outright; a single live row is the answer; among several, the one
    carrying `preferred` is the pointer. **Anything else returns `None`, and
    `None` is not a failure here** — P6's OQ6 (multiplicity) is open, and a
    reader that picked among simultaneous values would close an open question by
    accident. A file that reaches `None` is unresolved AT THIS LEVEL and gets no
    branch, which is what §5.11 permits: a tree "can be accepted even if some
    files remain unresolved".

    `canonical_value` and `display_label` are read off the row rather than
    joined here: `file_facts` itself carries neither column, and `preferred_fact`
    returns the row `facts_for_file` produced, which joins `"values"` and aliases
    both (`src/facts/file_facts.py:300-308`). A second join in P10 would be a
    second place the two representations can drift.

    The state filter is P6's own `PROPOSAL_ELIGIBLE_STATES`
    (`src/facts/read_surface.py:143-152`), whose docstring names this caller:
    "The facts a folder proposal may rest on." §3.6 keeps a weak model output out
    — it "must not quietly become a folder proposal". P10 neither widens nor
    narrows that set.
    """
    row = preferred_fact(conn, file_id=file_id, field_key=field_ref)
    if row is None:
        return None
    if row["reliability_state"] not in PROPOSAL_ELIGIBLE_STATES:
        return None
    return FieldValue(
        field_ref=field_ref,
        canonical_value=row["canonical_value"],
        display_label=row["display_label"] or row["canonical_value"],
    )
