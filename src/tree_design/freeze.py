# src/tree_design/freeze.py
"""Freeze, the legality projection, and the hand-over bundle P11 reads.

DM3 is the whole design of `FreezeRecord`: "given a frozen tree fixture and an
arbitrary destination string, a caller can decide legality without consulting
facts, templates or the filesystem." So the record carries
`legal_destination_ids` as a frozenset of ids and answers by set membership. An
answer that needed a join could disagree with itself the day the join changed.

`FreezeRecord` and `FrozenTree` are two records, not two names for one.
`FreezeRecord` is what freeze RECORDS — §8.8's adopted-version row, ids and
configuration only. `FrozenTree` is what freeze HANDS OVER: that record plus the
nodes and the §6.1 profiles, because `build_destination_index` reads
`tree.nodes`, `tree.profiles`, `tree.plan_version_id` and
`tree.shared_material_policy`, and an id list cannot feed any of them.

`frozen_tree(conn, *, plan_version)` is the seam and the spelling is
load-bearing: P11's dependency gate imports exactly this name with exactly this
keyword. Every P10 RECORD FIELD keeps `plan_version_id`; the conversion to P11's
`plan_version` happens once, here.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from collections.abc import Callable

from evidence_shape.canonical import canonical_json
from tree_design.candidates import protected_area_nodes
from tree_design.profiles import (
    AnchorExcerpt,
    DestinationProfile,
    NodeContext,
    Restrictions,
)
from tree_design.provenance import (
    actor_phrase,
    record_plan_version_adoption,
    surface_phrase,
)
from tree_design.records import ExpectedValue, Node
from tree_design.upstream import ProtectedArea
from tree_design.store import (
    freeze_version,
    nodes_for_version,
    one_transaction,
    write_node,
)
from tree_design.vocabulary import (
    ADOPT_VERSION,
    MANDATORY_REVIEW,
    SHARED_MATERIAL_POLICIES,
)


class FreezeRefused(RuntimeError):
    """A version that cannot be frozen, with every reason at once.

    Every reason, not the first: a user who fixes one and is handed the next has
    no idea how many remain, and §8.6 requires showing what is outstanding rather
    than revealing it one refusal at a time.
    """

    def __init__(self, reasons: Sequence[str]) -> None:
        self.reasons: tuple[str, ...] = tuple(reasons)
        super().__init__(
            f"this plan version cannot be frozen ({len(self.reasons)} reason(s)): "
            + "; ".join(self.reasons)
        )


class NotFrozen(RuntimeError):
    """A frozen bundle was asked for and this version has none."""


class ReleaseNotRecorded(RuntimeError):
    """This tree does not say which library built it, so it cannot be compared.

    `64` §5a: a tree that names no release makes a library upgrade UNDETECTABLE,
    not merely unhandled. Reporting `None` as the release would be worse than
    refusing — two different libraries would compare equal — so the reader
    refuses and names the version that cannot answer.
    """


@dataclass(frozen=True)
class FreezeRecord:
    """§8.8's adopted-plan-version record. Ids and configuration only."""

    plan_version_id: str
    created_at: str
    node_ids: tuple[str, ...]
    legal_destination_ids: frozenset[str]
    template_bindings: tuple[str, ...]
    labels_and_aliases: Mapping[str, tuple[str, ...]]
    residual_configuration: Mapping[str, str]
    shared_material_policy_ids: tuple[str, ...]
    cross_folder_moves: bool
    selection_id: str
    #: `64` §5a. WHICH LIBRARY BUILT THIS TREE. `load_shipped_catalogue` already
    #: derives `release_id` as a digest of exactly the bytes it read — "a library
    #: that changed moves it" — so the value existed and simply was not carried
    #: onto the frozen tree, which made an upgrade undetectable rather than
    #: merely unhandled.
    #:
    #: `None` is not a default anybody should reach for; it is the state of a
    #: tree frozen by a caller that named no catalogue, and `catalogue_release`
    #: refuses it by name rather than reporting it as a release.
    catalogue_release_id: str | None = None
    #: The `(template_id, template_version)` set the tree actually used, sorted.
    #: The release id says which library; this says which of its recipes, so an
    #: upgrade that republished one definition can be told from one that
    #: republished all of them.
    template_versions: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class FrozenTree:
    """P10's hand-over bundle.

    `shared_material_policy` is the resolved VALUE, not one of
    `FreezeRecord.shared_material_policy_ids`: §6.9 makes P11 branch on which of
    four rules applies, and an id list cannot tell it which.
    """

    plan_version_id: str
    freeze_record: FreezeRecord
    nodes: tuple[Node, ...]
    profiles: tuple[DestinationProfile, ...]
    shared_material_policy: str
    shared_material_policy_scope: str | None = None


def catalogue_release(tree: FrozenTree) -> str:
    """Which library built this tree (`64` §5a). Refuses rather than guessing."""
    release = tree.freeze_record.catalogue_release_id
    if not release:
        raise ReleaseNotRecorded(
            f"plan version {tree.plan_version_id!r} was frozen without a "
            "catalogue release id, so which library built it is not recorded and "
            "an upgrade against it cannot be detected"
        )
    return release


def legal_destination_ids(record: FreezeRecord) -> frozenset[str]:
    """The legal set, verbatim. One authority, and this is it."""
    return record.legal_destination_ids


def is_legal_destination(record: FreezeRecord, node_id: str) -> bool:
    """DM3, in one line: no facts, no templates, no filesystem."""
    return node_id in record.legal_destination_ids


def validate_for_freeze(
    conn: sqlite3.Connection,
    *,
    plan_version_id: str,
    residual_configuration: Mapping[str, str],
    approved_branch_ids: Sequence[str],
    protected_areas: Sequence[ProtectedArea] = (),
) -> tuple[str, ...]:
    """Every reason this version cannot be frozen. Empty means it can.

    The `refinement_disposition` rule reaches every node the freeze will publish
    as a LEGAL DESTINATION, plus whatever the caller names as approved.
    `P10 SPEC:230` requires it on an approved branch, and freezing IS the
    approval of the version: a node in the legal set is one P11 may place files
    into, and §6.7 cannot tell a branch that is shallow on purpose from one
    nobody finished without the user's own answer. It is still NOT blanket — an
    `ignored` folder and a protected area are in the tree, are not destinations,
    and are asked nothing.
    """
    reasons: list[str] = []
    nodes = nodes_for_version(conn, plan_version_id)
    if not nodes:
        reasons.append(
            f"plan version {plan_version_id!r} holds no node; an empty tree is "
            "not a design the user approved")
    approved = set(approved_branch_ids)
    by_id = {node.node_id: node for node in nodes}

    for node_id in sorted(approved - set(by_id)):
        reasons.append(
            f"{node_id!r} is named as an approved branch but this version does "
            "not contain it")

    for node in nodes:
        # `accepts_placement` and not only `approved`: `approved_branch_ids` is
        # what the CALLER names, so a caller that names nothing gets no check,
        # while the LEGAL SET is what the freeze record publishes and what P11
        # indexes. `placement/index.py`'s `_entry` raises `FrozenTreeRequired` on
        # any legal node with a falsy `refinement_disposition`, so a version that
        # froze without one broke at the consumer — where the user cannot act on
        # it — instead of here. Same repair, same wording, as the §6.9 gate below.
        if ((node.node_id in approved or node.accepts_placement)
                and not node.refinement_disposition):
            reasons.append(
                f"approved branch {node.node_id!r} ({node.display_label!r}) "
                "carries no refinement disposition. §5.8 needs it to tell a "
                "branch that is shallow ON PURPOSE from one that is unfinished, "
                "and P11 reads it rather than re-deriving it")
        if node.accepts_placement and node.node_type == "protected":
            reasons.append(
                f"protected area {node.node_id!r} accepts placement. It is "
                "marked and counted and never opened, so it is never a place "
                "files are put")
    # "Never silently omitted", enforced at the last moment it still can be. A
    # frozen tree is permanent: an area missing here is invisible for good, and
    # every later part inherits the omission.
    #
    # Matched on `display_label`, which is the ONLY identifier a protected node
    # can carry: `Node.existing_path` is refused on any type but `existing`, so
    # two bundles with the same basename in different directories are
    # indistinguishable here. That is a real limit of the record, reported rather
    # than papered over with a key that merges them.
    represented = {
        node.display_label for node in nodes if node.node_type == "protected"}
    for area in protected_areas:
        if area.display_label not in represented:
            reasons.append(
                f"protected area {area.display_label!r} ({area.path}) was marked "
                "by the scan and has no node in this version. It must be present "
                "and untouched, never silently omitted")

    # §6.9's gate, at the stage the user can still act on it. Without this the
    # user designs a tree, reviews it, approves it, presses freeze, IT FREEZES —
    # and `build_destination_index` refuses at the next stage, phrased as a
    # contract violation about a policy nobody asked them to choose.
    #
    # Unconditional, matching `placement/index.py`'s own precondition exactly.
    # That is deliberate rather than lazy: `resolve_multi_home` receives
    # `candidate_node_ids` computed during PLACEMENT from retrieval, so whether
    # any file will turn out to belong in two homes is not knowable at freeze by
    # anyone. The question is never contentless — it is "what should happen IF" —
    # and §6.9's four answers include `mandatory-review` for a user who would
    # rather decide case by case.
    _, tree_global, _scope = _shared_material(conn, plan_version_id)
    if not tree_global:
        reasons.append(
            f"plan version {plan_version_id!r} carries no §6.9 shared-material "
            "policy. A file can belong to two homes — a transcript in two "
            "application packets — and without a rule P11 would have to pick an "
            "institution. Choose one of "
            f"{', '.join(SHARED_MATERIAL_POLICIES)}; `{MANDATORY_REVIEW}` keeps "
            "the decision with you, file by file"
        )

    for name, state in residual_configuration.items():
        if not isinstance(state, str) or not state.strip():
            reasons.append(
                f"residual template {name!r} has no recorded enablement state; "
                "§7.4 makes that the user's decision and P10 supplies none")
    return tuple(reasons)


def represent_protected_areas(
    conn: sqlite3.Connection,
    *,
    plan_version_id: str,
    areas: Sequence[ProtectedArea],
    root_anchor: str,
    mint_node_id: Callable[[], str],
    handling_class_for: Callable[[ProtectedArea], str] | None,
) -> tuple[Node, ...]:
    """Write one protected node per marked area into the draft version.

    THIS IS THE JOIN. `upstream.protected_areas` reads P3's verdicts and
    `candidates.protected_area_nodes` turns them into nodes; for a while nothing
    in `src/` connected the two, so a protected container was pruned by the scan
    and then absent from the tree — silently omitted, the one outcome the owner's
    standing rule names.

    It runs BEFORE the profiles are built, not inside `freeze`. §6.1 requires a
    profile for every frozen node, and nodes written after the profiles were
    computed would be nodes P11's index refuses to build over.
    """
    nodes = protected_area_nodes(
        areas, plan_version_id=plan_version_id, root_anchor=root_anchor,
        mint_node_id=mint_node_id, handling_class_for=handling_class_for)
    with one_transaction(conn):
        for node in nodes:
            write_node(conn, node)
    return nodes


def _expected(values) -> list[dict]:
    return [{"field": v.field, "value": v.value} for v in values]


def _context_json(contexts) -> list[dict]:
    return [
        {"node_id": c.node_id, "display_label": c.display_label,
         "dimension": c.dimension, "expected_values": _expected(c.expected_values)}
        for c in contexts
    ]


def _profile_json(profile: DestinationProfile) -> dict:
    return {
        "node_id": profile.node_id,
        "display_label": profile.display_label,
        "domains": list(profile.domains),
        "template_binding": profile.template_binding,
        "template_fields": list(profile.template_fields),
        "expected_values": _expected(profile.expected_values),
        "parent_context": _context_json(profile.parent_context),
        "child_context": _context_json(profile.child_context),
        "accepted_group_ids": list(profile.accepted_group_ids),
        "group_labels": list(profile.group_labels),
        "representative_files": list(profile.representative_files),
        "anchor_files": list(profile.anchor_files),
        "anchor_excerpts": [
            {"observation_key": e.observation_key, "node_id": e.node_id}
            for e in profile.anchor_excerpts],
        "known_document_types": list(profile.known_document_types),
        "known_exclusions": list(profile.known_exclusions),
        "user_edits": list(profile.user_edits),
        "restrictions": {
            "handling_class": profile.restrictions.handling_class,
            "accepts_placement": profile.restrictions.accepts_placement,
            "node_role": profile.restrictions.node_role,
            "disposition": profile.restrictions.disposition,
        },
    }


def _profile_from_json(raw: dict) -> DestinationProfile:
    def contexts(items):
        return tuple(
            NodeContext(
                node_id=i["node_id"], display_label=i["display_label"],
                dimension=i["dimension"],
                expected_values=tuple(
                    ExpectedValue(e["field"], e["value"])
                    for e in i["expected_values"]))
            for i in items)

    return DestinationProfile(
        node_id=raw["node_id"],
        display_label=raw["display_label"],
        domains=tuple(raw["domains"]),
        template_binding=raw["template_binding"],
        template_fields=tuple(raw["template_fields"]),
        expected_values=tuple(
            ExpectedValue(e["field"], e["value"]) for e in raw["expected_values"]),
        parent_context=contexts(raw["parent_context"]),
        child_context=contexts(raw["child_context"]),
        accepted_group_ids=tuple(raw["accepted_group_ids"]),
        group_labels=tuple(raw["group_labels"]),
        representative_files=tuple(raw["representative_files"]),
        anchor_files=tuple(raw["anchor_files"]),
        anchor_excerpts=tuple(
            AnchorExcerpt(e["observation_key"], e["node_id"])
            for e in raw["anchor_excerpts"]),
        known_document_types=tuple(raw["known_document_types"]),
        known_exclusions=tuple(raw["known_exclusions"]),
        user_edits=tuple(raw["user_edits"]),
        restrictions=Restrictions(**raw["restrictions"]),
    )


def _record_json(record: FreezeRecord) -> dict:
    return {
        "plan_version_id": record.plan_version_id,
        "created_at": record.created_at,
        "node_ids": list(record.node_ids),
        "legal_destination_ids": sorted(record.legal_destination_ids),
        "template_bindings": list(record.template_bindings),
        "labels_and_aliases": {
            k: list(v) for k, v in record.labels_and_aliases.items()},
        "residual_configuration": dict(record.residual_configuration),
        "shared_material_policy_ids": list(record.shared_material_policy_ids),
        "cross_folder_moves": record.cross_folder_moves,
        "selection_id": record.selection_id,
        "catalogue_release_id": record.catalogue_release_id,
        "template_versions": [list(pair) for pair in record.template_versions],
    }


def _record_from_json(raw: dict) -> FreezeRecord:
    return FreezeRecord(
        plan_version_id=raw["plan_version_id"],
        created_at=raw["created_at"],
        node_ids=tuple(raw["node_ids"]),
        legal_destination_ids=frozenset(raw["legal_destination_ids"]),
        template_bindings=tuple(raw["template_bindings"]),
        labels_and_aliases={
            k: tuple(v) for k, v in raw["labels_and_aliases"].items()},
        residual_configuration=dict(raw["residual_configuration"]),
        shared_material_policy_ids=tuple(raw["shared_material_policy_ids"]),
        cross_folder_moves=bool(raw["cross_folder_moves"]),
        selection_id=raw["selection_id"],
        # `.get`, because a bundle written before §5a landed holds neither key
        # and reading it must report "this tree names no release" rather than
        # failing to load a tree the user already adopted.
        catalogue_release_id=raw.get("catalogue_release_id"),
        template_versions=tuple(
            (name, version) for name, version in raw.get("template_versions", ())),
    )


def _shared_material(conn: sqlite3.Connection,
                     plan_version_id: str) -> tuple[list, str | None, str | None]:
    rows = conn.execute(
        "SELECT * FROM shared_material_policies WHERE plan_version_id = ? "
        "ORDER BY policy_id", (plan_version_id,)).fetchall()
    ids = [row["policy_id"] for row in rows]
    tree_global = next((r for r in rows if r["policy_scope"] is None), None)
    if tree_global is None:
        return ids, None, None
    return ids, tree_global["policy"], tree_global["policy_scope"]


def freeze(
    conn: sqlite3.Connection,
    *,
    plan_version_id: str,
    created_at: str,
    user_id: str,
    component_version: str,
    #: Which of P13's review surfaces the adoption happened on -- or
    #: `SURFACE_UNATTENDED`, when it happened on none of them. Required and not
    #: defaulted: a default here would be this function deciding, on every
    #: caller's behalf, that somebody was watching.
    surface: str,
    residual_configuration: Mapping[str, str],
    approved_branch_ids: Sequence[str],
    profiles: Sequence[DestinationProfile],
    protected_areas: Sequence[ProtectedArea] = (),
    catalogue_release_id: str | None = None,
    template_versions: Sequence[tuple[str, int]] = (),
) -> FrozenTree:
    """Validate, write the bundle once, mark the version frozen, record adoption.

    The bundle is written rather than recomputed on read because §8.8 makes a
    frozen version immutable and P11's DM3 promise is that legality is decidable
    "without consulting facts, templates or the filesystem". Rebuilding the §6.1
    profiles at read time would consult all three, against a P9/P4/P6 state that
    has moved on since the user adopted this plan.

    All of it in one transaction: a bundle written beside a version that is still
    a draft, or a frozen version with no bundle, are both states no reader can
    make sense of.
    """
    reasons = validate_for_freeze(
        conn, plan_version_id=plan_version_id,
        residual_configuration=residual_configuration,
        approved_branch_ids=approved_branch_ids,
        protected_areas=protected_areas)
    if reasons:
        raise FreezeRefused(reasons)

    version = conn.execute(
        "SELECT * FROM plan_versions WHERE plan_version_id = ?",
        (plan_version_id,)).fetchone()
    nodes = nodes_for_version(conn, plan_version_id)
    policy_ids, policy, scope = _shared_material(conn, plan_version_id)

    record = FreezeRecord(
        plan_version_id=plan_version_id,
        created_at=created_at,
        node_ids=tuple(node.node_id for node in nodes),
        # ONE legality authority. §5.10's `ignored`, §8.4's `protected` and
        # §7.4's dispositions have all already been answered by
        # `derive_accepts_placement` and checked by `Node.__post_init__`; this
        # line reads that answer and re-derives none of it.
        legal_destination_ids=frozenset(
            node.node_id for node in nodes if node.accepts_placement),
        template_bindings=tuple(dict.fromkeys(
            node.template_context.binding_id for node in nodes
            if node.template_context is not None)),
        labels_and_aliases={node.node_id: (node.display_label,) for node in nodes},
        residual_configuration=dict(residual_configuration),
        shared_material_policy_ids=tuple(policy_ids),
        cross_folder_moves=bool(version["cross_folder_moves"]),
        selection_id=version["selection_id"],
        catalogue_release_id=catalogue_release_id,
        # Sorted and deduplicated: two branches built from one recipe used it
        # once, and "which recipes built this tree" is a set rather than a log.
        template_versions=tuple(sorted(
            {(name, int(number)) for name, number in template_versions})),
    )
    bundle = FrozenTree(
        plan_version_id=plan_version_id, freeze_record=record, nodes=nodes,
        profiles=tuple(profiles), shared_material_policy=policy,
        shared_material_policy_scope=scope)

    with one_transaction(conn):
        conn.execute(
            "INSERT OR REPLACE INTO frozen_trees "
            "(plan_version_id, created_at, freeze_record, profiles) "
            "VALUES (?, ?, ?, ?)",
            (plan_version_id, created_at, canonical_json(_record_json(record)),
             canonical_json([_profile_json(p) for p in profiles])))
        freeze_version(conn, plan_version_id)
        record_plan_version_adoption(
            conn, plan_version_id=plan_version_id, action=ADOPT_VERSION,
            # §8.8's adoption sentence, and the one place P10 records that a
            # person accepted this whole tree. On `SURFACE_UNATTENDED` nobody
            # did: `src/cli.py` freezes by rule with no screen to show. The
            # counts stay either way, because the version really was frozen and
            # really is the one P11 will place into.
            explanation=(
                f"{actor_phrase(surface)} adopted plan version "
                f"{plan_version_id!r}{surface_phrase(surface)}: "
                f"{len(nodes)} node(s), {len(record.legal_destination_ids)} of "
                "them legal destinations."),
            observed_at=created_at, user_id=user_id,
            component_version=component_version)
    return bundle


def frozen_tree(conn: sqlite3.Connection, *, plan_version: str) -> FrozenTree:
    """The bundle P11 reads. `plan_version`, not `plan_version_id`, on purpose.

    P11's spelling is already live at the P8 seam, every P10 record FIELD keeps
    `plan_version_id`, and the conversion happens once — here.
    """
    row = conn.execute(
        "SELECT * FROM frozen_trees WHERE plan_version_id = ?",
        (plan_version,)).fetchone()
    if row is None:
        raise NotFrozen(
            f"plan version {plan_version!r} has no frozen bundle. §8.8 makes the "
            "adopted version the one P11 places into, and a version that was "
            "never frozen was never adopted"
        )
    record = _record_from_json(json.loads(row["freeze_record"]))
    profiles = tuple(
        _profile_from_json(raw) for raw in json.loads(row["profiles"]))
    _, policy, scope = _shared_material(conn, plan_version)
    return FrozenTree(
        plan_version_id=plan_version, freeze_record=record,
        nodes=nodes_for_version(conn, plan_version), profiles=profiles,
        shared_material_policy=policy, shared_material_policy_scope=scope)
