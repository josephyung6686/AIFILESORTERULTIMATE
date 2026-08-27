# src/tree_design/validation.py
"""§5.7's six engine checks, run against the branch's actual values.

These are design-quality checks, not shape checks. P8 already enforced the
response shape and returned a verdict; §5.7 is explicit that a template "cannot
... become active merely because it is syntactically valid", so a clean P8
verdict arrives here and can still fail.

Each check answers one question about the tree the candidate WOULD produce, and
each failure names the values that produced it. No check returns a score: §5.2
requires an explanation "rather than a technical confidence score", and a check
that reported 0.72 would be exactly that.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired, TreeLimits
from tree_design.vocabulary import TEMPLATE_CHECKS


@dataclass(frozen=True)
class MaterialisedLevel:
    """One proposed level, with the real values the branch's evidence supplies."""

    dimension_role: str
    #: `None` on a template-local level, which has no P6 field by construction
    #: (Contract W5). Its identity for V1 is its role instead — see `_concept`.
    field_ref: str | None
    order_index: int
    metadata_only: bool
    values: tuple[str, ...]
    members_by_value: Mapping[str, int]
    handling_classes_by_value: Mapping[str, frozenset[str]]


@dataclass(frozen=True)
class MaterialisedCandidate:
    branch_node_id: str
    ancestor_field_refs: tuple[str, ...]
    ancestor_depth: int
    levels: tuple[MaterialisedLevel, ...]
    member_file_ids: frozenset[str]


@dataclass(frozen=True)
class CheckFailure:
    check: str
    reason: str
    affected: tuple[str, ...]


@dataclass(frozen=True)
class ValidationReport:
    report_id: str
    passed: tuple[str, ...]
    failures: tuple[CheckFailure, ...]

    @property
    def accepted(self) -> bool:
        return not self.failures


def _concept(level: MaterialisedLevel) -> str:
    """What this level actually splits by, for the repeat comparison.

    A schema-field level is identified by its P6 field: two roles resolving to
    one field express one meaning twice, and the role names would hide it.

    A template-local level has NO field (Contract W5), so its identity is its
    role. Comparing those on `field_ref` compared every local level against
    `None` — two different local roles read as a repeat of each other, and every
    two-level novel-domain branch failed V1 on a difference the check could not
    see. Field when there is one, role when there is not.
    """
    return level.field_ref if level.field_ref is not None else level.dimension_role


def _v1(candidate: MaterialisedCandidate) -> CheckFailure | None:
    """Repeats a parent dimension.

    The comparison is on `field_ref`, not on the role name: two roles that
    resolve to one field produce one level's worth of meaning twice, and the
    role names would hide it.
    """
    seen = list(candidate.ancestor_field_refs)
    for level in candidate.levels:
        if level.metadata_only:
            continue
        concept = _concept(level)
        if concept in seen:
            return CheckFailure(
                "V1",
                f"level {level.dimension_role!r} splits by {concept!r}, "
                "which an ancestor or an earlier level already expresses; the "
                "second level adds a folder and no meaning",
                (concept,),
            )
        seen.append(concept)
    return None


def _v2(candidate: MaterialisedCandidate) -> CheckFailure | None:
    """Creates meaningless one-child levels."""
    for level in candidate.levels:
        if level.metadata_only:
            continue
        if len(level.values) == 1:
            only = level.values[0]
            return CheckFailure(
                "V2",
                f"level {level.dimension_role!r} produces one child, {only!r}; a "
                "level with a single child is a folder the user opens to find one "
                "folder",
                (only,),
            )
    return None


def _v3(candidate: MaterialisedCandidate,
        limits: TreeLimits) -> CheckFailure | None:
    """Exceeds practical depth limits.

    The number is `tree.max_folder_proposals_and_depth`, read from P1. §5.7 and
    §8.6 both decline to state one, so there is nothing to hard-code.
    """
    folder_levels = [level for level in candidate.levels if not level.metadata_only]
    depth = candidate.ancestor_depth + len(folder_levels)
    if depth > limits.max_folder_proposals_and_depth:
        return CheckFailure(
            "V3",
            f"the candidate reaches depth {depth}, above the configured "
            f"{limits.max_folder_proposals_and_depth}",
            tuple(level.dimension_role for level in folder_levels),
        )
    return None


def _v4(candidate: MaterialisedCandidate,
        collector_field_keys: frozenset[str]) -> CheckFailure | None:
    """Uses an author or organization merely as a collector.

    §3.8: "A folder should not become a collection point for everything produced
    by the same person or organization." A collector role beside another level is
    fine — `Applications/Columbia/Essays` is useful. A branch whose ONLY level is
    a collector is the failure.
    """
    if not collector_field_keys:
        raise ConfigurationRequired(
            "V4 needs §3.8's set of author/organization field keys. P6 owns "
            "which fields those are, and a set P10 guessed would either miss a "
            "collector or reject a legitimate counterpart level."
        )
    folder_levels = [level for level in candidate.levels if not level.metadata_only]
    if len(folder_levels) == 1 and folder_levels[0].field_ref in collector_field_keys:
        level = folder_levels[0]
        return CheckFailure(
            "V4",
            f"the branch's only level is {level.field_ref!r}, an author or "
            "organization role; the branch would collect everything from the same "
            "counterpart with no further meaning",
            (level.field_ref,),
        )
    return None


def _v5(candidate: MaterialisedCandidate,
        value_discloses_protected_material:
            Callable[[str | None, str], bool] | None) -> CheckFailure | None:
    """Exposes protected information.

    A folder name is visible in the filesystem and in every prompt that names a
    destination, so a level whose VALUES are protected material publishes that
    material. A metadata-only role over the same values does not, which is
    exactly what §5.4's `metadata_only` is for.

    **This asks about the VALUE STRING, not about the files under it**, and the
    distinction is the whole check. `00`:97 lists V5 among the STRUCTURAL faults
    of a proposed template — "does not repeat a parent dimension, create
    meaningless one-child levels, exceed practical depth limits, use an author or
    organization merely as a collector, expose protected information, or produce
    empty branches" — so it is a claim about the DIMENSION.

    It used to read `handling_classes_by_value`, the union of every member file's
    class, which meant one passport scan under `Columbia` gave the string
    "Columbia" a protected class and V5 refused the branch. A university's name
    is not protected material; the passport is. The user lost the organisation
    and kept none of the protection. Protected files are now ISOLATED in
    `materialise_branch` instead, and this check answers its own question.

    Nothing upstream classifies a VALUE: P6 classifies FIELDS
    (`destination_eligible`, already enforced by C2 before this runs) and P7
    classifies FILES (`handling_class`). So the judgement is injected, like
    `collector_field_keys` for V4, and absent means refuse rather than guess.
    """
    if value_discloses_protected_material is None:
        raise ConfigurationRequired(
            "V5 needs a test for whether a VALUE would disclose protected "
            "material as a folder name. Nothing upstream answers it: P6 "
            "classifies fields and P7 classifies files, and neither classifies "
            "the string a folder is named after. A test invented here would be "
            "P10 deciding what counts as a disclosure."
        )
    exposed: list[str] = []
    for level in candidate.levels:
        if level.metadata_only:
            continue
        for value in level.values:
            if value_discloses_protected_material(level.field_ref, value):
                exposed.append(value)
    if exposed:
        return CheckFailure(
            "V5",
            "these values would themselves become folder names that disclose "
            "protected material; a folder name is visible material",
            tuple(exposed),
        )
    return None


def _v6(candidate: MaterialisedCandidate) -> CheckFailure | None:
    """Produces empty branches when tested against the accepted group."""
    empty = [
        value
        for level in candidate.levels if not level.metadata_only
        for value in level.values
        if level.members_by_value.get(value, 0) == 0
    ]
    if empty:
        return CheckFailure(
            "V6",
            "these levels have no member in the accepted group, so the branch "
            "would be created empty",
            tuple(empty),
        )
    return None


def run_checks(candidate: MaterialisedCandidate, *, report_id: str,
               limits: TreeLimits, collector_field_keys: frozenset[str],
               value_discloses_protected_material:
                   Callable[[str | None, str], bool] | None) -> ValidationReport:
    """All six, in order, collecting every failure rather than stopping at one.

    Stopping at the first failure would make the user fix one problem, re-run,
    and find the next — which is how a review surface teaches someone that the
    product cannot be trusted to tell them what is wrong.
    """
    outcomes = {
        "V1": _v1(candidate),
        "V2": _v2(candidate),
        "V3": _v3(candidate, limits),
        "V4": _v4(candidate, collector_field_keys),
        "V5": _v5(candidate, value_discloses_protected_material),
        "V6": _v6(candidate),
    }
    failures = tuple(
        outcomes[check] for check in TEMPLATE_CHECKS if outcomes[check] is not None
    )
    passed = tuple(check for check in TEMPLATE_CHECKS if outcomes[check] is None)
    return ValidationReport(report_id=report_id, passed=passed, failures=failures)
