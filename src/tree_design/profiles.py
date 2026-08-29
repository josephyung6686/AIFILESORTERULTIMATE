# src/tree_design/profiles.py
"""§6.1's destination profile. P10 emits it; P11 indexes it and publishes none.

Resolution B4: every §6.1 ingredient — the template, the expected field values,
the accepted group memberships, the user-selected label, the known exclusions and
the privacy restrictions — is a value P10 ALREADY HOLDS at freeze. None is
produced by placement. P11 builds the §6.2 retrieval index over these and carries
no profile in its own plan-version state, so there is one author for the concept.

Excerpts are cited by `observation_key`, P4's durable citation handle. An
`observation_id` is run-local, and a citation bound to one cannot say what was
actually released the day someone audits it.

No field here holds a composed path (DM11). P10 publishes `root_anchor` plus the
ancestor label chain; P12 composes, and applies §8.3's case, Unicode and length
rules.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from tree_design.config import ConfigurationRequired
from tree_design.records import ExpectedValue, Node
from tree_design.store import nodes_for_version
# `DIRECT_ANCHOR` is P9's constant and is reached through P10's ONE seam
# for another part's names. Imported straight from `grouping.vocabulary`
# it was a second place P9 could break P10 from, and `vocabulary.py` is
# explicitly not its home: that module's own docstring rules out naming
# `direct-anchor` there.
from tree_design.upstream import DIRECT_ANCHOR, AcceptedGroup


@dataclass(frozen=True)
class NodeContext:
    """One ancestor or child, as §6.1's "parent and child meanings".

    A node's own label does not identify a destination: `2026` under `Columbia`
    and `2026` under `Receipts` are different places, and a model given only the
    leaf label cannot tell them apart.
    """

    node_id: str
    display_label: str
    dimension: str | None
    expected_values: tuple[ExpectedValue, ...]


@dataclass(frozen=True)
class AnchorExcerpt:
    """A P9 direct anchor's cited evidence, addressed by P4's durable handle.

    Carries `node_id` beside `observation_key` because §6.1 asks for anchor
    evidence PER NODE, and a bare key cannot say which node an excerpt anchors.
    """

    observation_key: str
    node_id: str


@dataclass(frozen=True)
class Restrictions:
    """What P11 may do with this destination. Read, never re-derived.

    `accepts_placement` is the single legality authority and arrives here
    verbatim from the node. `disposition` is the §7.4 answer to a DIFFERENT
    question — what happens when a residual node is chosen — and P11's review
    policy is what reads it.
    """

    handling_class: str
    accepts_placement: bool
    node_role: str
    disposition: str | None


@dataclass(frozen=True)
class DestinationProfile:
    node_id: str
    display_label: str
    domains: tuple[str, ...]
    template_binding: str | None
    template_fields: tuple[str, ...]
    expected_values: tuple[ExpectedValue, ...]
    parent_context: tuple[NodeContext, ...]
    child_context: tuple[NodeContext, ...]
    accepted_group_ids: tuple[str, ...]
    group_labels: tuple[str, ...]
    representative_files: tuple[str, ...]
    anchor_files: tuple[str, ...]
    anchor_excerpts: tuple[AnchorExcerpt, ...]
    known_document_types: tuple[str, ...]
    known_exclusions: tuple[str, ...]
    user_edits: tuple[str, ...]
    restrictions: Restrictions


def _context(node: Node) -> NodeContext:
    return NodeContext(
        node_id=node.node_id, display_label=node.display_label,
        dimension=node.dimension, expected_values=tuple(node.expected_values))


def build_profiles(
    conn: sqlite3.Connection,
    *,
    plan_version_id: str,
    groups_by_id: Mapping[str, AcceptedGroup],
    document_types_by_node: Mapping[str, Sequence[str]],
    anchor_excerpts_by_node: Mapping[str, Sequence[AnchorExcerpt]],
    user_edits_by_node: Mapping[str, Sequence[str]],
    node_scoped_rejections: Mapping[str, Sequence[str]],
) -> tuple[DestinationProfile, ...]:
    """One profile per node in the version. Every value read, none derived.

    The four injected mappings are the things P10 holds but does not own the
    shape of: P4's excerpt handles, P6's observed document types, P13's recorded
    user edits and §8.7's node-scoped rejections. They arrive rather than being
    reconstructed, so no profile can assert evidence nobody recorded.
    """
    nodes = nodes_for_version(conn, plan_version_id)
    by_id = {node.node_id: node for node in nodes}
    children: dict[str, list[Node]] = {}
    for node in nodes:
        if node.parent_node_id is not None:
            children.setdefault(node.parent_node_id, []).append(node)

    profiles: list[DestinationProfile] = []
    for node in nodes:
        groups = tuple(
            groups_by_id[group_id] for group_id in node.associated_group_ids
            if group_id in groups_by_id)

        ancestors: list[NodeContext] = []
        current = by_id.get(node.parent_node_id) if node.parent_node_id else None
        seen = {node.node_id}
        while current is not None and current.node_id not in seen:
            seen.add(current.node_id)
            ancestors.append(_context(current))
            current = (by_id.get(current.parent_node_id)
                       if current.parent_node_id else None)

        # §6.1's "known exclusions" is the union of the group's own excluded
        # members and any rejection recorded against this node. Both are negative
        # evidence, and §8.7 keeps negatives so the same wrong destination is not
        # resurfaced.
        exclusions = list(node_scoped_rejections.get(node.node_id, ()))
        for group in groups:
            exclusions.extend(group.excluded_members)

        members = [member.file_id for group in groups for member in group.members]
        # `basis`, not `membership_basis`: `GroupMember` is P9's live record and
        # its field is `basis`, checked against `grouping.vocabulary`'s
        # MEMBERSHIP_BASES. §6.1 wants the DIRECT ANCHORS as anchor files —
        # a context-supported member is evidence about the group, not evidence
        # that anchors it.
        anchors = [
            member.file_id for group in groups for member in group.members
            if member.basis == DIRECT_ANCHOR
        ]

        profiles.append(DestinationProfile(
            node_id=node.node_id,
            display_label=node.display_label,
            domains=tuple(dict.fromkeys(
                group.domain for group in groups if group.domain)),
            template_binding=(None if node.template_context is None
                              else node.template_context.binding_id),
            template_fields=() if node.dimension is None else (node.dimension,),
            expected_values=tuple(node.expected_values),
            parent_context=tuple(ancestors),
            child_context=tuple(
                _context(child) for child in children.get(node.node_id, ())),
            accepted_group_ids=tuple(node.associated_group_ids),
            group_labels=tuple(group.label for group in groups),
            representative_files=tuple(dict.fromkeys(members)),
            anchor_files=tuple(dict.fromkeys(anchors)),
            anchor_excerpts=tuple(anchor_excerpts_by_node.get(node.node_id, ())),
            known_document_types=tuple(
                document_types_by_node.get(node.node_id, ())),
            known_exclusions=tuple(dict.fromkeys(exclusions)),
            user_edits=tuple(user_edits_by_node.get(node.node_id, ())),
            restrictions=Restrictions(
                handling_class=node.handling_class,
                accepts_placement=node.accepts_placement,
                node_role=node.node_role,
                disposition=node.disposition,
            ),
        ))
    return tuple(profiles)


def redacted_for_egress(
    profile: DestinationProfile,
    *,
    protected_handling_classes: frozenset[str] | None,
) -> DestinationProfile:
    """The egress form of a profile whose material must not reach a prompt.

    §7.3 on Protected Records: it "should normally remain local-only and must not
    cause filenames or content to be exposed in model prompts". So the file
    identifiers and the excerpt handles go, and NOTHING ELSE DOES.

    The node keeps its id, its label, its restrictions and its place in the tree,
    because the owner's rule is that a protected area is MARKED AND COUNTED,
    NEVER OPENED — present-but-untouched, never silently omitted. Dropping the
    profile entirely would be the omission; dropping only what reads or exposes
    contents is the rule.

    `protected_handling_classes` is injected with no default. P7 owns
    `HANDLING_CLASSES` and has published no ordering, so a set chosen here would
    be P10 deciding which material is sensitive.
    """
    if protected_handling_classes is None:
        raise ConfigurationRequired(
            "the protected handling classes are injected configuration with no "
            "default: P7 owns HANDLING_CLASSES and has published no ordering, "
            "and a set chosen here would let P10 decide which of a user's "
            "material may reach a model prompt"
        )
    if profile.restrictions.handling_class not in protected_handling_classes:
        return profile
    return replace(
        profile,
        representative_files=(),
        anchor_files=(),
        anchor_excerpts=(),
    )
