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
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

from facts.fields import get_field
from facts.read_surface import (
    PROPOSAL_ELIGIBLE_STATES, facts_for, is_destination_eligible,
    preferred_in_field,
)
from facts.states import strength
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
            # `AnchorFact` has no id. Its fields are (field, value, file_ids,
            # reliability_state, observation_key, observation_keys) —
            # `src/grouping/records.py` — and `observation_key` is P4's durable
            # citation handle for the fact itself, which is what §6.1's anchor
            # excerpts are cited by as well. Reading `.fact_id` raises
            # AttributeError. `observation_keys` is the per-stating-file answer
            # (`104` R-97) and is a dossier's question, not an accepted group's:
            # what travels here is one handle per fact.
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
    #: P6's own reliability state for the fact this value came from. Carried
    #: rather than dropped because `00`:42 turns on it: a model output "too weak
    #: to establish a fact may remain a possible clue for review; it must not
    #: quietly become a folder proposal". `PROPOSAL_ELIGIBLE_STATES` admits the
    #: whole ladder above `possible`, which is the right bar for a value SEVERAL
    #: files carry and too low for one file saying something once --
    #: `materialise._project` is where that difference is applied and carries the
    #: measurement. Defaulted to the weakest admissible state so a caller that
    #: builds a `FieldValue` without one gets the cautious answer rather than a
    #: silent promotion.
    reliability: str = PROPOSAL_ELIGIBLE_STATES[0]


def anchors_a_level(reliability: str) -> bool:
    """Is a fact at this state strong enough to stand behind a level on its own?

    P6's ladder, asked here because THIS is P10's declared seam onto it.
    `materialise.py` is not one -- `tests/p10/test_p10_no_invention.py::
    test_only_the_declared_seams_name_another_parts_records` refuses any module
    outside the allow-list naming another part's records, and the first draft of
    `_unanchored_single_values` imported `facts.read_surface` and `facts.states`
    straight into the materialiser and was caught by it.

    `PROPOSAL_ELIGIBLE_STATES[0]` is the weakest state a folder proposal may rest
    on at all, and this asks for STRONGER than that: `00`:63's "direct or
    validated anchor", read off the ladder rather than spelled. No state name is
    written down here, for the reason `facts/read_surface.py` gives where it
    derives the same set.
    """
    return strength(reliability) > strength(PROPOSAL_ELIGIBLE_STATES[0])


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
    return _as_value(preferred_fact(conn, file_id=file_id, field_key=field_ref),
                     field_ref=field_ref)


def _as_value(row: sqlite3.Row | None, *, field_ref: str) -> FieldValue | None:
    """P6's preferred row, as the value P10 reads off it -- or `None`.

    The state filter and the shaping, stated ONCE. `_preferred_values_in_field`
    below asks P6 the same question of the whole corpus at once, and if it built
    its own `FieldValue` the two would be two places for §3.6's exclusion to
    drift apart. Both go through here, so P10 has one rule for what a file
    contributes at a dimension however the row was fetched.
    """
    if row is None:
        return None
    if row["reliability_state"] not in PROPOSAL_ELIGIBLE_STATES:
        return None
    return FieldValue(
        field_ref=field_ref,
        canonical_value=row["canonical_value"],
        display_label=row["display_label"] or row["canonical_value"],
        reliability=row["reliability_state"],
    )


def _preferred_values_in_field(conn: sqlite3.Connection, *,
                               field_ref: str) -> dict[str, FieldValue]:
    """`preferred_value_for` for every file in the corpus, in one read.

    P6 publishes the read (`facts.read_surface.preferred_in_field`); this adds
    P10's state filter and P10's shape and nothing else, through `_as_value`,
    which is the same function the per-file path returns through. A file whose
    slot resolves to nothing, or to a state a folder proposal may not rest on, is
    ABSENT -- so `.get(file_id)` is `preferred_value_for`'s own `None`.
    """
    return {
        file_id: value
        for file_id, row in preferred_in_field(conn, field_key=field_ref).items()
        if (value := _as_value(row, field_ref=field_ref)) is not None
    }


def group_level_value(conn: sqlite3.Connection, *, group: AcceptedGroup,
                      field_ref: str) -> FieldValue | None:
    """The one value this GROUP contributes at this dimension, or `None`.

    `104` §11.2 step 2, and `00`:57 is what it implements: "the syllabus and
    lecture may each state PHYS1401 directly ... the homework may have a
    homework-like name" — the course's school and term are stated by the anchors
    and the sparse members are carried by the group. So the level's value for
    EVERY member of a course group is the course's, read once from the files that
    state the group's basis directly.

    **The direct anchors and nobody else.** A context-supported member is in the
    group because something retrieved it; what it happens to say about a school is
    the collector `00`:44 names by name and `104` §11.1 measured — twenty `school`
    facts, five essays from a university course filed under a high school. Its own
    reading is not the group's.

    **Disagreement is `None`, which is `preferred_value_for`'s own posture one
    level up.** Two anchors naming two schools is a real state and picking between
    them here would close P6's OQ6 by accident at the group grain; the members
    become unresolved AT THIS LEVEL, which §5.11 permits and which reaches the
    person as "waiting for you to say what this is".

    The strongest reliability among the agreeing anchors is what comes back, so
    `materialise_branch`'s `anchors_a_level` test asks the same question of a
    group-level value that it asks of a per-file one.

    **One group at a time is the expensive way to ask it.** The answer is the
    GROUP's and not the member's, so a caller with a branch of groups wants
    `group_level_values` below, and a caller materialising a level wants
    `group_level_reader`, which asks once per group and hands the same answer to
    every member. This form remains for a caller holding one group.
    """
    return group_level_values(conn, groups=(group,),
                              field_ref=field_ref)[group.group_id]


def group_level_values(conn: sqlite3.Connection, *,
                       groups: Sequence[AcceptedGroup],
                       field_ref: str) -> dict[str, FieldValue | None]:
    """`group_level_value` for SEVERAL groups at one dimension, in one read.

    **The rule is unchanged and the reads are not**, which is
    `settled_values_by_directory`'s sentence one dimension over. Each group is
    still decided on its own anchors alone -- direct anchors only, disagreement is
    `None`, the strongest agreeing reliability wins -- and no group looks at
    another. What the list buys is the field read: the anchors' settled values are
    a property of the CORPUS at that field, so P6 answers it once
    (`facts.read_surface.preferred_in_field`) instead of once per anchor per
    asking.

    Nothing is cached between calls and nothing is keyed by connection, for the
    reason `settled_values_by_directory` gives: a group's value is a function of
    what the facts say NOW. The reading lives exactly as long as the question.

    An empty list returns an empty mapping rather than reading anything.
    """
    if not groups:
        return {}
    reading = _preferred_values_in_field(conn, field_ref=field_ref)
    return {group.group_id: _group_level_from(group, reading)
            for group in groups}


def _group_level_from(group: AcceptedGroup,
                      reading: dict[str, FieldValue]) -> FieldValue | None:
    """`group_level_value`'s rule, over a reading already in hand.

    Written once and reached both ways, so the one-group form and the many-group
    form cannot come to differ about what a group's value IS. `group.members` is
    walked in its own order because `max` returns the FIRST maximal element and
    that order is therefore part of the answer.
    """
    found: list[FieldValue] = []
    for member in group.members:
        if member.basis != DIRECT_ANCHOR:
            continue
        value = reading.get(member.file_id)
        if value is not None:
            found.append(value)
    if not found:
        return None
    if len({item.canonical_value for item in found}) != 1:
        return None
    return max(found, key=lambda item: strength(item.reliability))


def group_level_reader(conn: sqlite3.Connection, *,
                       groups: Sequence[AcceptedGroup],
                       ) -> Callable[[GroupMember, str], FieldValue | None]:
    """`materialise_branch`'s `group_value_for_member`, for one branch's groups.

    **The answer is the group's, so it is computed per group and not per member.**
    `materialise_branch` asks this once per member per group-level dimension,
    because that is the shape of the loop it is in; the answer it gets back does
    not vary between the members of a group, and computing it again for each of
    them is the corpus squared. Measured (`104` R-110, 1,000-file synthetic
    corpus, P8--P11 under cProfile): 1,000 asks made 1,003,000
    `preferred_value_for` calls -- one per anchor per member -- and cost 47.9 of
    77.8 profiled seconds; at 5,000 files it is essentially the whole of the
    2,365.6 s the same span took.

    So each dimension is answered once for every group of the branch, out of one
    corpus read, and each member reads its group's answer off that. A member in
    no group of this branch has no such value and is `None` at that level, which
    is `00`:57's "an essay outside any group gets no school level".

    **Which group a shared member is under is the caller's rule, kept here:**
    first group wins, in the order the branch lists them, which is `_members`'
    own rule for the same shared file -- two groups in one branch may both claim
    it and it is counted once.

    The reading lives as long as the reader, which is one branch's pass over its
    own candidates. Nothing survives it: a new pass asks P6 again, for the reason
    `settled_values_by_directory` gives.
    """
    group_of: dict[str, AcceptedGroup] = {}
    for group in groups:
        for member in group.members:
            group_of.setdefault(member.file_id, group)
    answered: dict[str, dict[str, FieldValue | None]] = {}

    def value_for(member: GroupMember, field_ref: str) -> FieldValue | None:
        group = group_of.get(member.file_id)
        if group is None:
            return None
        by_group = answered.get(field_ref)
        if by_group is None:
            by_group = answered[field_ref] = group_level_values(
                conn, groups=groups, field_ref=field_ref)
        return by_group[group.group_id]

    return value_for


def settled_values_in_directory(conn: sqlite3.Connection, *,
                                directory_path: str,
                                stated_by_every_file: bool = False,
                                ) -> tuple[FieldValue, ...]:
    """What the files ALREADY IN one of the person's folders agree about.

    `00`:100 asks that a folder the person made be "treated as a strong
    expression of user intent", and `00`:102 puts it in the tree as an `existing`
    node. Neither is worth anything while the node cannot be CHOSEN, and §6.2
    scores a destination on its expected values: a node carrying none competes
    for nothing. Measured before this existed, on a corpus with the person's own
    `Uni/CHEM1500`: their folder carried no expectation, the engine's own
    `Coursework/CHEM1500` carried `subject=CHEM1500`, and the product offered to
    move a file out of the right folder into a duplicate of its own, with both
    folders showing the same name. Adoption without this is worse than none.

    **Nothing here is composed.** §5.4 is explicit that the product "does not
    invent PHYS1401, UChicago, Spring 2026" and that "those names emerge from
    validated facts", so the answer comes entirely from `preferred_value_for` --
    P6's own settled reading, under P6's own proposal-eligible states -- and this
    function only reports where those readings AGREE.

    Three rules, each of which is a refusal:

    * **Unanimity, not majority.** A folder holding two courses is not a folder
      about either of them. A majority rule would let the product claim an
      expectation the person's own filing contradicts, and would turn a mixed
      folder into a magnet for half its own contents.
    * **Immediate children only.** A file in `Uni/PHYS1401` is evidence about
      `PHYS1401`, not about `Uni`. Counting it for both would give every ancestor
      its deepest descendant's expectations and put the person's whole tree in
      competition with itself.
    * **`is_destination_eligible` decides which fields may count**, because §3.8
      rules out authorship as a destination dimension and P6 owns that answer.
      Asking here would be P10 authoring a second, rival one.

    A file with no settled value at a field is not a disagreement -- it is
    silent, and §5.11 permits a tree "even if some files remain unresolved". A
    field where NOBODY settled a value yields nothing, so an empty folder and a
    folder of unreadable files both expect nothing, which is the honest answer
    for each.

    `stated_by_every_file` narrows the third rule and nothing else: it keeps only
    the values that are not merely unanimous among the files that spoke but are
    stated by every file in the folder. That is a different question from this
    one -- what the folder was MADE for rather than what it expects -- and
    `settled_values_stated_by_every_file` below is where it is asked and
    explained. No caller of the expectations needs it, which is why it is off.
    """
    return settled_values_by_directory(
        conn, directory_paths=(directory_path,),
        stated_by_every_file=stated_by_every_file)[directory_path]


def settled_values_by_directory(conn: sqlite3.Connection, *,
                                directory_paths: Sequence[str],
                                stated_by_every_file: bool = False,
                                ) -> dict[str, tuple[FieldValue, ...]]:
    """`settled_values_in_directory` for SEVERAL folders, reading each field once.

    **The rule is unchanged and the reads are not.** Every refusal above still
    decides each folder on its own -- unanimity, immediate children,
    `is_destination_eligible`, and `_divides_the_corpus` -- and none of them looks
    at the other folders in the list. What the list buys is the corpus read:
    asked one folder at a time, `_divides_the_corpus` walked every file in the
    corpus and asked P6 for its settled value at the field, so D folders and F
    fields over N files asked D x F x N times and each ask re-read one file's
    whole slot (`104` R-79: 175,892 of them over 588 invocations at a thousand
    files, 7.8 s, and the term the corpus squares). Asked together, each field is
    read once for the whole corpus (`facts.read_surface.preferred_in_field`) and
    every folder answers out of that one reading.

    Nothing is cached between calls and nothing is keyed by connection. A folder's
    expectations are a function of what the facts say NOW, and a reading held
    across calls would answer from what they said before -- the failure `104`
    R-78 is about, one part over. The caller says which folders it is asking
    about, and the reading lives exactly as long as the question.

    An empty list returns an empty mapping rather than reading anything, for the
    reason `versions_in_fields` gives: a caller with no folders is asking about
    nothing.
    """
    if not directory_paths:
        return {}

    roster = _rows_of_every_file(conn)
    within: dict[str, list[sqlite3.Row]] = {}
    for row in roster:
        within.setdefault(_parent_directory_of(row["current_path"]), []).append(row)
    # `_rows_directly_inside`'s answer, for every folder asked at once and in the
    # same order: one pass over `files` grouped by the parent it computes, rather
    # than one pass over `files` per folder.
    asked = {path: within.get(_normalised(path), []) for path in directory_paths}

    fields_of: dict[str, list[str]] = {}
    for path, here in asked.items():
        # A SET OF ONE IS ALWAYS UNANIMOUS, which is why one file is not enough.
        # Measured: a person had `Scans/` holding one scanned retainer agreement;
        # that file settled `subject=CV20261234`, the folder "agreed" with it, and
        # the product then offered to file a deposition transcript into a folder
        # called Scans. One file agreeing with itself is evidence about the FILE.
        # It becomes evidence about the FOLDER when a second file agrees -- which
        # is the whole difference between a folder somebody curated and a folder
        # things land in. `TreeLimits.tiny_folder_max_files` already carries the
        # idea that a folder of one file says little; this is that idea where it
        # decides a destination.
        # `<= 1` rather than `< 2`: `test_p10_no_invention` forbids a numeric
        # literal beyond zero and one in this package, and the rule is right --
        # a threshold spelled here would be a number nobody authored.
        if len(here) <= 1:
            continue
        fields: list[str] = []
        for row in here:
            for fact in facts_for(conn, file_id=row["file_id"],
                                  content_hash=row["content_hash"]):
                key = fact["field_key"]
                if key not in fields and is_destination_eligible(
                        conn, field_key=key):
                    fields.append(key)
        fields_of[path] = fields

    reading_of: dict[str, dict[str, FieldValue]] = {}
    for fields in fields_of.values():
        for field_ref in fields:
            if field_ref not in reading_of:
                reading_of[field_ref] = _preferred_values_in_field(
                    conn, field_ref=field_ref)

    corpus = [row["file_id"] for row in roster]
    answers: dict[str, tuple[FieldValue, ...]] = {}
    for path, here in asked.items():
        settled: list[FieldValue] = []
        for field_ref in fields_of.get(path, ()):
            reading = reading_of[field_ref]
            readings = [reading.get(row["file_id"]) for row in here]
            present = [found for found in readings if found is not None]
            if not present:
                continue
            if len({found.canonical_value for found in present}) != 1:
                continue
            if not _divides_the_corpus(reading, corpus,
                                       value=present[0].canonical_value,
                                       inside={row["file_id"] for row in here}):
                continue
            if stated_by_every_file and len(present) != len(here):
                continue
            settled.append(present[0])
        answers[path] = tuple(settled)
    return answers


def settled_values_stated_by_every_file(conn: sqlite3.Connection, *,
                                        directory_path: str,
                                        ) -> tuple[FieldValue, ...]:
    """WHAT A FOLDER WAS MADE FOR, WHICH IS NOT WHAT IT EXPECTS.

    **UNANIMITY IS NOT COVERAGE, AND THE DIFFERENCE IS THE WHOLE OF THIS.**
    `settled_values_in_directory` counts a silent file as silent, deliberately:
    §5.11 permits a tree "even if some files remain unresolved" and a file that
    says nothing has not disagreed with anything. That is the right rule for what
    a folder may be said to EXPECT. It is the wrong rule for what a folder was
    MADE for, and one measurement on the owner's own disk separates them:

        `Kid` holds two files and BOTH are report cards.
        `Desktop` holds four résumés among eleven files.

    Both fold to `work_type` unanimously, because the seven other things on the
    desktop are silent about what kind of thing they are. But a folder whose
    EVERY file is one kind was made for that kind, and a folder where one kind
    merely leads is a place things land. Somebody made `Kid` for their child's
    school papers; nobody made `Desktop` for résumés.

    Measured, 2026-09-05, and this is why the distinction had to be exactly this
    one: the two failed candidates before it were "refuse a move when the file
    states no anchoring fact", which also refuses the nine résumés, and "refuse a
    move out of a folder the person made that holds files like it", which
    describes `Desktop` as accurately as it describes `Kid`. Coverage is the
    first test that comes out different on the two.

    HOW MANY FILES ARE ENOUGH is not answered here and must not be. The floor is
    already there -- `settled_values_in_directory` returns nothing for a folder
    of one, because a set of one is always unanimous -- and any band above it is
    a number the composition root authors. `cli.py` reads
    `TreeLimits.tiny_folder_max_files` for exactly that and decides which files
    it applies to.
    """
    return settled_values_in_directory(conn, directory_path=directory_path,
                                       stated_by_every_file=True)


def _divides_the_corpus(reading: dict[str, FieldValue], corpus: Sequence[str], *,
                        value: str, inside: set[str]) -> bool:
    """Does anything OUTSIDE this folder disagree? If not, the claim says nothing.

    **The fourth appearance of one mistake, and the reason to name it as a class.**
    V5 failed a whole candidate for one level's fault, V2 failed a whole tree for
    one level's, `_project` truncated a whole branch for one level's -- and an
    expectation the entire corpus satisfies is the same error again: a statement
    that divides nothing, treated as though it distinguished something.

    Measured. Every file in one person's corpus was Columbia's and in the same
    term, so all four of their adopted folders expected `term=Spring2026`. Each
    then matched every file, §6.10 called that multiple supported homes, and six
    files that had been placing fine abstained to a model that offline mode
    forbids. The folders were not wrong about the term. It simply was not news.

    This is V2's own test -- "a level your files do not divide is measured and not
    built" -- applied to a folder instead of a level, and it needs no threshold:
    either some file disagrees or none does.

    **It is handed the corpus's reading rather than asking for it, and that is the
    whole of `104` R-79.** The question is unchanged -- every file outside, at one
    field -- but this used to ask P6 for each of them one at a time, once per
    folder per field, which is the same read repeated D x F times over the same N
    files. `settled_values_by_directory` reads each field once and passes the
    reading in; `reading.get` is `preferred_value_for`'s own answer for a file, and
    absent is its `None`. The walk is still over `files`, so a fact whose file the
    scan never recorded is still consulted by nobody.
    """
    for file_id in corpus:
        if file_id in inside:
            continue
        other = reading.get(file_id)
        if other is not None and other.canonical_value != value:
            return True
    return False


def _normalised(path: str) -> str:
    """One spelling for one directory, so a trailing separator is not a folder.

    P3 records a scan root as the user typed it and a parent directory as the
    walk produced it, and `Uni/` and `Uni` are the same folder in every sense the
    person has.
    """
    cleaned = path.rstrip("/\\")
    return cleaned or path


def _parent_directory_of(path: str) -> str:
    """The directory a file sits DIRECTLY in. Never an ancestor of it."""
    cleaned = _normalised(path)
    for separator in ("/", "\\"):
        if separator in cleaned:
            return _normalised(cleaned.rsplit(separator, 1)[0])
    return ""


def _rows_of_every_file(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """P3's roster, in P3's own order, which is what `files` returns.

    One statement in one place, so the folder read and the corpus walk cannot come
    to disagree about which files exist or in what order they are considered.
    """
    return conn.execute(
        "SELECT file_id, content_hash, current_path FROM files").fetchall()


def _rows_directly_inside(conn: sqlite3.Connection, directory_path: str):
    """The file rows sitting DIRECTLY in one directory. Never in a descendant."""
    return [row for row in _rows_of_every_file(conn)
            if _parent_directory_of(row["current_path"]) == _normalised(
                directory_path)]


def file_ids_in_directory(conn: sqlite3.Connection, *,
                          directory_path: str) -> frozenset[str]:
    """Which files the person has already put directly in one of their folders.

    `00`:100 asks that the canvas show "which extracted facts and accepted groups
    overlap with" an existing folder, and an overlap is a set of files. Immediate
    children only, for the reason `settled_values_in_directory` gives: a file in
    `Uni/PHYS1401` is evidence about `PHYS1401`, not about `Uni`.
    """
    return frozenset(row["file_id"] for row in _rows_directly_inside(
        conn, directory_path))
