# src/tree_design/records.py
"""P10's frozen records. Construction is where a malformed tree is refused.

Two invariants live here rather than in a validator, because a record that can
be built wrong is a record that will be stored wrong:

1. `accepts_placement` is derived and then checked against the stored value.
   P11 reads one flag (resolution B6); the derivation stays visible so the flag
   cannot drift from the rule that produced it.
2. No field but `existing_path` may hold a path separator. `existing_path` is an
   observed fact about the corpus (§5.10); every other location is `root_anchor`
   plus the ancestor label chain, which P12 composes.

An ABSENT required value and an OUT-OF-VOCABULARY one are different errors and
raise different exceptions. `MalformedTreeRecord` means the record's own shape
is wrong — a residual node with no disposition states nothing about how its
files are treated. `OutOfVocabulary` means a value P10 does not define reached a
field that has a closed set. Collapsing the two would make `check(None, ...)`
the report for a missing field, and "not one of the 3 values" is a poor
description of a field nobody filled in.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from tree_design.vocabulary import (
    EXISTING,
    HANDLING_CLASSES,
    IGNORED,
    NODE_ROLES,
    NODE_TYPES,
    PROTECTED,
    REFINEMENT_DISPOSITIONS,
    RESIDUAL,
    RESIDUAL_DISPOSITIONS,
    SHARED_MATERIAL_POLICIES,
    check,
)

_SEPARATORS = frozenset({"/", "\\", os.sep, os.altsep or "/"})


class MalformedTreeRecord(ValueError):
    """A record that cannot be built is a tree that cannot be stored wrong."""


def _require(value: object, *, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MalformedTreeRecord(f"{name} is required and cannot be empty")
    return value


def _no_separator(value: str, *, name: str) -> str:
    if any(sep in value for sep in _SEPARATORS):
        raise MalformedTreeRecord(
            f"{name} holds a path separator. P10 publishes root_anchor plus the "
            "ancestor label chain; P12 composes the path and applies §8.3's "
            "case-sensitivity, Unicode and length rules (resolution B3)."
        )
    return value


def derive_accepts_placement(node_type: str, *,
                             protected_movement_permitted: bool) -> bool:
    """The §5.12/§5.10/§8.4 rule, in one place.

    `ignored` is false because §5.10 guarantees a user may leave an existing
    folder untouched. `protected` is true only under an explicit user policy,
    because §8.4 says protected material "should not be moved automatically
    without a user policy that explicitly permits it".

    THE §7.4 RESIDUAL DISPOSITION IS DELIBERATELY NOT READ HERE, and that is a
    RULING rather than an omission. `00`:121: "Once the user approves the desired
    residual branches, those branches become legal nodes in the frozen
    destination tree. The LLM may choose among them later." All three
    dispositions produce LEGAL nodes, so `accepts_placement` — "is this a node
    the model may choose" — is True for all three, and deriving it from the
    disposition would make a review-only branch illegal.

    The disposition governs what happens WHEN a node is chosen, not WHETHER it
    can be. "Never moves files AUTOMATICALLY" is a statement about automation,
    and `00`:120's "represent without moving" is a first-class outcome. That
    belongs to P11's review policy, which reads `IndexEntry.disposition`.
    """
    check(node_type, NODE_TYPES, name="node_type")
    if node_type == IGNORED:
        return False
    if node_type == PROTECTED:
        return bool(protected_movement_permitted)
    return True


@dataclass(frozen=True)
class ExpectedValue:
    """One `field = value` assertion a level makes (§6.1)."""

    field: str
    value: str

    def __post_init__(self) -> None:
        _require(self.field, name="ExpectedValue.field")
        _require(self.value, name="ExpectedValue.value")


@dataclass(frozen=True)
class TemplateContext:
    """Which branch-local composition, and which level of it, produced a node.

    Exact versions are pinned so no library update can retroactively alter a
    frozen tree (§8.8, "Template versions and ordering choices").
    """

    binding_id: str
    template_id: str
    template_version: int
    dimension_index: int
    fragment_id: str | None = None
    fragment_version: int | None = None

    def __post_init__(self) -> None:
        for name in ("binding_id", "template_id"):
            _require(getattr(self, name), name=f"TemplateContext.{name}")
        for name in ("template_version", "dimension_index"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise MalformedTreeRecord(
                    f"TemplateContext.{name} is a non-negative integer version")
        if (self.fragment_id is None) != (self.fragment_version is None):
            raise MalformedTreeRecord(
                "a fragment reference is an id AND an exact version; half a "
                "reference cannot identify what supplied this level"
            )


@dataclass(frozen=True)
class Node:
    """§5.12's node, with §6.1's and §8.8's additions.

    `origin_node_id` exists because SPEC open question 5 is open: whether a
    `node_id` is stable across plan versions or minted per version is unsettled,
    and it decides whether a pending move survives a tree edit (§8.3). P10 mints
    per version and records the lineage, so neither answer needs a migration and
    no code depends on cross-version identity until the question is closed.
    """

    node_id: str
    plan_version_id: str
    node_type: str
    display_label: str
    parent_node_id: str | None
    root_anchor: str
    ordinal: int
    associated_group_ids: tuple[str, ...]
    explanation: str
    node_role: str
    accepts_placement: bool
    handling_class: str
    origin_node_id: str
    template_context: TemplateContext | None = None
    dimension_role: str | None = None
    dimension: str | None = None
    expected_values: tuple[ExpectedValue, ...] = ()
    existing_path: str | None = None
    disposition: str | None = None
    # §5.8. OPTIONAL here and non-`None` in `FrozenTree`, deliberately.
    # `P10 SPEC:230` requires it on an APPROVED branch, and a draft node has not
    # been approved yet — a required field would make the state the user is
    # actually in while editing unstorable. `validate_for_freeze` refuses a
    # version carrying a `None` on an approved branch, and `freeze` refuses to
    # hand over a bundle carrying a `None` anywhere. The guarantee belongs to the
    # record that only exists after freeze, which is why P11's `IndexEntry` may
    # declare the same field `str`.
    refinement_disposition: str | None = None
    refinement_reason: str | None = None
    protected_movement_permitted: bool = False

    def __post_init__(self) -> None:
        for name in ("node_id", "plan_version_id", "root_anchor", "origin_node_id"):
            _require(getattr(self, name), name=f"Node.{name}")
        check(self.node_type, NODE_TYPES, name="node_type")
        check(self.node_role, NODE_ROLES, name="node_role")
        check(self.handling_class, HANDLING_CLASSES, name="handling_class")
        _no_separator(_require(self.display_label, name="Node.display_label"),
                      name="Node.display_label")
        if not isinstance(self.ordinal, int) or isinstance(self.ordinal, bool):
            raise MalformedTreeRecord("Node.ordinal is the sibling order, an integer")
        if not self.explanation or not self.explanation.strip():
            raise MalformedTreeRecord(
                "every node states the facts or accepted groups that caused it to "
                "appear (§5.12); an unexplained node is one the user cannot judge"
            )
        object.__setattr__(self, "associated_group_ids",
                           tuple(self.associated_group_ids))
        object.__setattr__(self, "expected_values", tuple(self.expected_values))

        derived = derive_accepts_placement(
            self.node_type,
            protected_movement_permitted=self.protected_movement_permitted,
        )
        if bool(self.accepts_placement) is not derived:
            raise MalformedTreeRecord(
                f"accepts_placement={self.accepts_placement!r} contradicts the "
                f"derivation for node_type={self.node_type!r}, which is {derived!r}. "
                "P11 reads the flag and re-derives nothing, so a flag that "
                "disagrees with the rule is a destination nobody chose."
            )

        if self.existing_path is not None and self.node_type != EXISTING:
            raise MalformedTreeRecord(
                "existing_path is present only on an `existing` node; it is an "
                "observed fact about the corpus, never a composition"
            )
        if self.node_role == RESIDUAL:
            if self.disposition is None:
                raise MalformedTreeRecord(
                    "a residual node states its §7.4 disposition. Absence is a "
                    "malformed record, not an out-of-vocabulary value: without "
                    "one, nothing says whether the node is a real destination, a "
                    "review queue, or files left where they are."
                )
            check(self.disposition, RESIDUAL_DISPOSITIONS, name="disposition")
        elif self.disposition is not None:
            raise MalformedTreeRecord(
                "disposition is meaningless on a role other than `residual`")
        if self.refinement_disposition is not None:
            check(self.refinement_disposition, REFINEMENT_DISPOSITIONS,
                  name="refinement_disposition")
            if not (self.refinement_reason or "").strip():
                raise MalformedTreeRecord(
                    "a refinement disposition without a reason cannot tell an "
                    "intentionally shallow branch from an unfinished one (§5.8)"
                )
        elif self.refinement_reason is not None:
            raise MalformedTreeRecord(
                "a refinement reason belongs to a refinement disposition")
        if self.dimension is not None and self.dimension_role is None:
            raise MalformedTreeRecord(
                "a level built from a live P6 field also records the semantic role "
                "that field resolved for (C2)"
            )
        # The reverse is NOT an error any more. A role with NO field is the
        # declared template-local form (Contract W4.3, W5): a level whose children
        # are accepted group labels rather than fact values, so there is no field
        # to name and `expected_values` stays empty.
        #
        # This loosens a guard that used to catch "a role resolved to nothing", so
        # the null must be unreachable except through the declared path — and it
        # is: `ResolvedDimension` refuses `field_ref = None` unless its scope is
        # template-local, and refuses a template-local level that names a field.
        # `materialise` reads that pairing and never invents either side.


@dataclass(frozen=True)
class SharedMaterialPolicy:
    """§6.9's policy for a file that belongs in two places.

    Without one recorded, §6.9 requires P11 to abstain on a transcript belonging
    to two application packets rather than pick a university.
    """

    policy_id: str
    plan_version_id: str
    policy: str
    policy_scope: str | None
    reason: str

    def __post_init__(self) -> None:
        for name in ("policy_id", "plan_version_id", "reason"):
            _require(getattr(self, name), name=f"SharedMaterialPolicy.{name}")
        check(self.policy, SHARED_MATERIAL_POLICIES, name="policy")


@dataclass(frozen=True)
class PlanVersion:
    """§8.8's plan version. `cross_folder_moves` is P3's value, stored by P10.

    P3 records the user's §1.1 choice; P10 stores it in the freeze record under
    "Placement policy settings"; P12 enforces it at mutation time. Three parts,
    one value, and the reason it is stored here is that P12 reads a frozen plan,
    not a scan selection.
    """

    plan_version_id: str
    predecessor_id: str | None
    state: str
    created_at: str
    cross_folder_moves: bool
    selection_id: str

    def __post_init__(self) -> None:
        for name in ("plan_version_id", "state", "created_at", "selection_id"):
            _require(getattr(self, name), name=f"PlanVersion.{name}")
        if self.state not in ("draft", "frozen", "superseded"):
            raise MalformedTreeRecord(
                f"plan version state {self.state!r} is not draft, frozen or "
                "superseded; a frozen version is immutable and an edit opens a "
                "draft (§8.8)"
            )
        if not isinstance(self.cross_folder_moves, bool):
            raise MalformedTreeRecord(
                "cross_folder_moves is P3's boolean permission, carried verbatim")
