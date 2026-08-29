# src/tree_design/catalogue.py
"""The packaged template library, loaded through an injected reader.

`planning/domains/` is a research and authorship surface, not a runtime import
target. A later deterministic compiler consumes ratified catalogue records and
emits a versioned manifest with provenance and validation-report hashes; this
module reads that manifest and nothing else. It does not import planning code,
does not touch the filesystem, and does not fall back to an empty catalogue —
an empty release would make C1 pass by having nothing to resolve.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from tree_design.config import ConfigurationRequired
from tree_design.templates import (
    ApplicabilityRef,
    DimensionOrder,
    FragmentRef,
    PurposeProfileRef,
    RoleBinding,
    TemplateApplicability,
    TemplateDefinition,
    TemplateDimension,
    TemplateFragment,
)


@dataclass(frozen=True)
class TemplateCatalogue:
    release_id: str
    fragments: Mapping[tuple[str, int], TemplateFragment]
    definitions: Mapping[tuple[str, int], TemplateDefinition]
    applicabilities: Mapping[tuple[str, int], TemplateApplicability]

    def has_fragment(self, fragment_id: str, fragment_version: int) -> bool:
        return (fragment_id, fragment_version) in self.fragments

    def fragment(self, ref: FragmentRef) -> TemplateFragment:
        return self.fragments[ref.key()]

    def applicability(self, ref: ApplicabilityRef) -> TemplateApplicability:
        return self.applicabilities[ref.key()]

    def rows_for_schema(self, uses_schema: str) -> tuple[TemplateApplicability, ...]:
        """Every row that makes a recipe eligible in this one schema context.

        A schema may have several rows and a definition may be referenced by rows
        for several schemas. That is the whole many-to-many seam, and it stays
        safe because each row still resolves against exactly one schema.
        """
        return tuple(
            row for row in self.applicabilities.values()
            if row.uses_schema == uses_schema
        )


def _fragment(raw: dict) -> TemplateFragment:
    return TemplateFragment(
        fragment_id=raw["fragment_id"],
        fragment_version=raw["fragment_version"],
        roles=tuple(raw["roles"]),
        relative_order=tuple(tuple(pair) for pair in raw["relative_order"]),
        imports=tuple(FragmentRef(**ref) for ref in raw["imports"]),
        optional_roles=tuple(raw["optional_roles"]),
        metadata_only_roles=tuple(raw["metadata_only_roles"]),
        allowed_values=raw["allowed_values"],
        privacy_floor=raw["privacy_floor"],
        provenance=tuple(raw["provenance"]),
    )


def _order(raw: dict) -> DimensionOrder:
    return DimensionOrder(
        order_id=raw["order_id"],
        dimensions=tuple(TemplateDimension(**d) for d in raw["dimensions"]),
        is_default=raw["is_default"],
        rationale=raw["rationale"],
    )


def _definition(raw: dict) -> TemplateDefinition:
    return TemplateDefinition(
        template_id=raw["template_id"],
        template_version=raw["template_version"],
        origin_kind=raw["origin_kind"],
        scope_kind=raw["scope_kind"],
        publication_state=raw["publication_state"],
        fragment_refs=tuple(FragmentRef(**ref) for ref in raw["fragment_refs"]),
        candidate_orders=tuple(_order(o) for o in raw["candidate_orders"]),
        optional_branch_patterns=tuple(raw["optional_branch_patterns"]),
        sensitivity_policy_ref=raw["sensitivity_policy_ref"],
        validation_constraints=tuple(raw["validation_constraints"]),
        example_label_chains=tuple(tuple(c) for c in raw["example_label_chains"]),
        relative_order=tuple(
            (before, after) for before, after in raw.get("relative_order", ())),
        privacy_floor=raw.get("privacy_floor"),
        sole_order_attestation=raw.get("sole_order_attestation"),
    )


def _applicability(raw: dict) -> TemplateApplicability:
    profile = raw.get("purpose_profile_ref")
    return TemplateApplicability(
        applicability_id=raw["applicability_id"],
        applicability_version=raw["applicability_version"],
        template_id=raw["template_id"],
        template_version=raw["template_version"],
        uses_schema=raw["uses_schema"],
        purpose_profile_ref=None if profile is None else PurposeProfileRef(**profile),
        allowed_fields=tuple(raw["allowed_fields"]),
        detection_signal_refs=tuple(raw["detection_signal_refs"]),
        role_bindings=tuple(RoleBinding(**b) for b in raw["role_bindings"]),
        exclusions=tuple(raw["exclusions"]),
        provenance=tuple(raw["provenance"]),
        privacy_floor=raw.get("privacy_floor"),
    )


def load_catalogue(read_manifest: Callable[[], str]) -> TemplateCatalogue:
    """Parse one compiled release. The caller supplies the bytes.

    An injected reader rather than a path keeps this module out of the
    filesystem entirely, which is what makes the "no repository scanning" guard
    checkable by import inspection rather than by hope.
    """
    if not callable(read_manifest):
        raise ConfigurationRequired(
            "the packaged template catalogue is supplied by the caller; P10 does "
            "not locate it, scan for it, or default to an empty release"
        )
    manifest = json.loads(read_manifest())
    release_id = manifest.get("release_id")
    if not release_id:
        raise ConfigurationRequired(
            "a compiled catalogue carries a release identity; without one, two "
            "different libraries are indistinguishable in a frozen tree"
        )
    fragments = {}
    for raw in manifest["fragments"]:
        record = _fragment(raw)
        fragments[(record.fragment_id, record.fragment_version)] = record
    definitions = {}
    for raw in manifest["definitions"]:
        record = _definition(raw)
        definitions[(record.template_id, record.template_version)] = record
    applicabilities = {}
    for raw in manifest["applicabilities"]:
        record = _applicability(raw)
        applicabilities[
            (record.applicability_id, record.applicability_version)] = record
    return TemplateCatalogue(
        release_id=release_id,
        fragments=fragments,
        definitions=definitions,
        applicabilities=applicabilities,
    )
