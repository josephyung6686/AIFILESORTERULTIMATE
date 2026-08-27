# src/tree_design/template_schema.py
"""P10's half of §5.7: what "the required template shape" means.

§5.7: "Structured output constraints and schema validation should enforce the
required template shape." P8 enforces; P10 defines. The callable this module
builds is handed to P8 as `TemplateDependencies.schema_validator`, and P8 turns a
False into its own REJECT / SCHEMA_INVALID verdict. P10 coins no refusal type and
reads no model response itself.

The fragment boundary lives here and nowhere else. A proposal may REFERENCE a
published fragment by exact id and version, and may add template-local semantic
dimensions. It may not publish or propose a canonical fragment, because a
fragment is shared organization logic and sharing it is a human review decision
made once, not a side effect of one branch's model call. P10 owns the boundary
because P10 owns the published catalogue and is the only part that can answer
whether a named fragment exists.

The boundary is a SECOND authority — `published_fragment_authority`, handed to P8
as `TemplateDependencies.published_fragment` — and not a check inside
`template_schema_validator`. An authority can be absent, and an absent one is
`ValidationUnavailable` like every other missing dependency in P8; a folded check
can only be silent, and it would report `SCHEMA_INVALID` for a defect that is not
a shape defect. `schema_validator` therefore answers exactly one question, "is
this shape legal", which is all it ever claimed to.

`allowed_vocabulary_for` IS THE PRODUCT'S REACH. P8 reads
`dossier.allowed_vocabulary` per call and imposes no global ceiling
(`src/llm_harness/template_validation.py`), so whatever this function returns is
the real limit on what the product can organize. It is therefore NOT the bound
fields alone: a group from an unresearched domain would then have every proposed
dimension rejected on vocabulary, and §5.7's custom-template path would be dead
on arrival. It is the schema's bound fields PLUS template-local dimension names
the branch's own evidence justifies. The asymmetry
`planning/43-ROLE-VOCABULARY-AND-RECUT.md` §9 requires is preserved exactly: the
product adapts to a new domain immediately at template-local scope, and the
shared vocabulary grows deliberately, after a human sees the pattern recur.
Nothing here promotes a local name to canonical — there is no writer into the
catalogue in this package at all.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from llm_harness.records import Conflict, DossierRequest, EvidenceItem
from llm_harness.template_validation import TemplateDependencies
from facts.fields import FIELD_ROWS
from llm_harness.vocabulary import (
    ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
    E_TEMPLATE,
    FORBIDDEN_PUBLISHING_KEYS as _P8_FORBIDDEN_PUBLISHING_KEYS,
)
from tree_design.catalogue import TemplateCatalogue
from tree_design.vocabulary import (
    DIMENSION_REQUIREMENTS,
    DIMENSION_SCOPE_VALUES,
    SCOPE_TEMPLATE_LOCAL,
)

#: Every field key P6 defines, across every schema — DERIVED from P6's single
#: catalogue rather than listed, so a field P6 adds is guarded the same day.
#: Contract W3's borrowed-field guard is a membership test against this: a
#: "template-local" dimension named `target_school` is not a novel label, it is
#: another schema's field being smuggled in by relabelling.
_LIVE_P6_FIELD_KEYS: frozenset[str] = frozenset(
    row.field_key for row in FIELD_ROWS)

_SEPARATORS = frozenset({"/", "\\", os.sep, os.altsep or "/"})

#: Every key §5.7 names for a generated template: "a domain name, allowed fields,
#: recommended folder dimensions, field order, optional versus required levels,
#: metadata-only fields, sensitivity policy, and example paths". `fragment_refs`
#: is the ninth, and it is what makes reuse expressible without copying.
TEMPLATE_PAYLOAD_KEYS: tuple[str, ...] = (
    "domain",
    "allowed_fields",
    "fragment_refs",
    "dimensions",
    "levels",
    "sensitivity_policy_ref",
    "example_label_chains",
)

#: A payload carrying any of these is trying to publish shared logic from inside
#: one branch's model call. P8 scans for them, because reading a model response
#: is P8's, and returns `FRAGMENT_PUBLICATION_ATTEMPTED`. IMPORTED, never
#: respelled: a second copy here would be a list P10 rejects and P8 accepts the
#: day either changes.
FORBIDDEN_PUBLISHING_KEYS: tuple[str, ...] = _P8_FORBIDDEN_PUBLISHING_KEYS


def _is_sequence(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _fragment_refs_are_well_formed(payload: Mapping[str, object]) -> bool:
    """A SHAPE check, and only that: is `fragment_refs` a list of
    `{fragment_id: str, fragment_version: int}`?

    Whether those fragments EXIST is `published_fragment_authority`'s question,
    not this one. The split is not cosmetic: a `"1"` where an `int` belongs would
    otherwise reach the authority, and an authority that has to guard its own
    argument types cannot return a clean verdict. Shape first, membership second,
    two reason codes at P8.
    """
    refs = payload.get("fragment_refs")
    if not _is_sequence(refs):
        return False
    for ref in refs:
        if not isinstance(ref, Mapping):
            return False
        fragment_id = ref.get("fragment_id")
        fragment_version = ref.get("fragment_version")
        if not isinstance(fragment_id, str) or not fragment_id:
            return False
        if not isinstance(fragment_version, int) or isinstance(fragment_version, bool):
            return False
    return True


def _dimensions_are_well_formed(payload: Mapping[str, object]) -> bool:
    dimensions = payload.get("dimensions")
    if not _is_sequence(dimensions) or not dimensions:
        return False
    allowed = payload.get("allowed_fields")
    if not _is_sequence(allowed) or not allowed:
        return False
    allowed_names = {name for name in allowed if isinstance(name, str)}
    if len(allowed_names) != len(list(allowed)):
        return False
    indices: list[int] = []
    for item in dimensions:
        if not isinstance(item, Mapping):
            return False
        name = item.get("name")
        if not isinstance(name, str) or name not in allowed_names:
            return False
        scope = item.get("scope")
        if scope not in DIMENSION_SCOPE_VALUES:
            # Contract W2: the tier is declared, never inferred. Inferring it is
            # exactly the assertion the classifier exists to make out loud.
            return False
        if scope == SCOPE_TEMPLATE_LOCAL and name in _LIVE_P6_FIELD_KEYS:
            # Contract W3. This is the real attack the one-row-one-schema rule
            # defends against: not a novel name, but another schema's field
            # relabelled as "local" to slip past the closure. The check lives
            # here because P10 holds the catalogue and P8 deliberately does not.
            return False
        if not item.get("evidence_ref"):
            return False
        if item.get("requirement") not in DIMENSION_REQUIREMENTS:
            return False
        if not isinstance(item.get("metadata_only"), bool):
            return False
        index = item.get("order_index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            return False
        indices.append(index)
    return len(set(indices)) == len(indices)


def _levels_are_well_formed(payload: Mapping[str, object]) -> bool:
    """P10 requires the KEY; P8's Site E judges its content.

    Site E downgrades a level with a falsy `retrieval_justification` to WEAK.
    Duplicating that judgement here would give one rule two homes and let the
    two disagree about the same response.
    """
    levels = payload.get("levels")
    if not _is_sequence(levels) or not levels:
        return False
    for level in levels:
        if not isinstance(level, Mapping):
            return False
        if "retrieval_justification" not in level:
            return False
        if not isinstance(level.get("dimension"), str):
            return False
    return True


def _examples_are_labels(payload: Mapping[str, object]) -> bool:
    chains = payload.get("example_label_chains")
    if not _is_sequence(chains):
        return False
    for chain in chains:
        if not _is_sequence(chain):
            return False
        for label in chain:
            if not isinstance(label, str) or not label:
                return False
            if any(sep in label for sep in _SEPARATORS):
                return False
    return True


def template_schema_validator(
        catalogue: TemplateCatalogue) -> Callable[[object], bool]:
    """The callable P8 calls. True means "this shape is legal", nothing more.

    A True here is not an approval, not an activation, and not a claim that the
    design is good. §5.7 is explicit that a technically valid template can still
    be a poor organization design, so semantic validation (V1-V6) and user
    approval both still stand between this and a node.
    """

    def validate(payload: object) -> bool:
        if not isinstance(payload, Mapping):
            return False
        if any(key not in payload for key in TEMPLATE_PAYLOAD_KEYS):
            return False
        domain = payload.get("domain")
        if not isinstance(domain, str) or not domain:
            return False
        if not isinstance(payload.get("sensitivity_policy_ref"), str):
            return False
        if not payload.get("sensitivity_policy_ref"):
            return False
        if not _fragment_refs_are_well_formed(payload):
            return False
        if not _dimensions_are_well_formed(payload):
            return False
        if not _levels_are_well_formed(payload):
            return False
        return _examples_are_labels(payload)

    return validate


def published_fragment_authority(
        catalogue: TemplateCatalogue) -> Callable[[str, int], bool]:
    """"Does this exact fragment, at this exact version, exist in the published
    catalogue?" — the one question P10 alone can answer, and the whole of the
    fragment boundary.

    Exact version, never nearest: version 2 of a fragment is a different recipe,
    and accepting it because the id is familiar would activate organization logic
    nobody reviewed. A model proposal may REFERENCE published shared logic; it
    may not publish any, because sharing logic is a human review decision made
    once and not a side effect of one branch's model call.
    """

    def published(fragment_id: str, fragment_version: int) -> bool:
        if not isinstance(fragment_id, str) or not fragment_id:
            return False
        if not isinstance(fragment_version, int) or isinstance(fragment_version, bool):
            return False
        return catalogue.has_fragment(fragment_id, fragment_version)

    return published


def template_dependencies(catalogue: TemplateCatalogue) -> TemplateDependencies:
    """P8's record, carrying P10's two callables. P10 constructs nothing else
    of P8's, coins no refusal type, and reads no model response.

    `schema_validator` answers "is this shape legal" and nothing more — which is
    what its docstring always claimed and what it now actually does.
    `published_fragment` answers "does this fragment exist". P8 walks the
    response, scans it for `FORBIDDEN_PUBLISHING_KEYS`
    (-> `FRAGMENT_PUBLICATION_ATTEMPTED`) and calls this authority once per
    `fragment_refs` entry (-> `FRAGMENT_NOT_PUBLISHED`). Response reading is P8's;
    the catalogue is P10's; neither part does the other's half.
    """
    return TemplateDependencies(
        schema_validator=template_schema_validator(catalogue),
        published_fragment=published_fragment_authority(catalogue),
    )


def allowed_vocabulary_for(catalogue: TemplateCatalogue, *,
                           uses_schema: str) -> tuple[str, ...]:
    """The closure P8's Site E classifies every proposed dimension name against.

    It is the union of the allowed fields of the rows for ONE schema. Unioning
    across schemas here would widen a P6 allow-list at the dossier boundary,
    which is the one thing the one-row-one-schema rule exists to prevent — and
    `allowed_vocabulary` is ONE field on a `Dossier` shared by five call sites,
    so anything added here is also offered as a placement destination at Site C
    and a target node id at Site D.

    It is therefore never extended — not with role names, not with node ids, not
    with model-authored strings (Contract W1). There is deliberately no parameter
    through which a caller could widen it.

    An empty result is not a dead end. Under Contract W2 the closure classifies
    rather than rejects: a name outside it that is no live P6 field is a
    `template-local` label, so a schema with no declared fields still produces a
    reviewable branch design.
    """
    return tuple(sorted({
        field
        for row in catalogue.rows_for_schema(uses_schema)
        for field in row.allowed_fields
    }))


def build_template_request(*, subject_ref: str, plan_version: str,
                           evidence_items: Sequence[EvidenceItem],
                           conflicts: Sequence[Conflict],
                           model_call_request) -> DossierRequest:
    """The reference-only Site-E request. P10 builds this; P8 materialises.

    `E_template` is in P8's `SITES_REQUIRING_PLAN_VERSION`, so a request without
    one is refused by P8's own record — which is correct: §8.8 captures template
    versions and ordering choices per plan version, and a template call outside a
    version has nothing to attribute its result to.

    The record's fields are EXACTLY these eight
    (`llm_harness.records.DossierRequest`). There is no `budget_context`: P8's
    ceiling rides inside `ModelCallRequest.max_dossier_tokens`, which is the
    caller's echo of P1's stored value, and a ninth keyword here raises
    `TypeError` at construction.
    """
    return DossierRequest(
        call_site=E_TEMPLATE,
        subject_ref=subject_ref,
        eligibility_reason=ACCEPTED_GROUP_FITS_NO_EXISTING_TEMPLATE,
        evidence_items=tuple(evidence_items),
        conflicts=tuple(conflicts),
        model_call_request=model_call_request,
        plan_version=plan_version,
        evidence_snapshot_id=None,
    )
