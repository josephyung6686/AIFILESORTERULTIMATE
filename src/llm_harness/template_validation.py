"""Site E template validation using an injected strict schema validator.

P10 owns template design quality. P8 does not invent or score a hierarchy.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from llm_harness.records import Dossier, P8Verdict, ValidationUnavailable
from llm_harness.validation import validate_response
from llm_harness.vocabulary import (
    ABSTAIN,
    ACCEPT_CONTEXT_SUPPORTED,
    ACCEPT_DIRECT,
    FORBIDDEN_PUBLISHING_KEYS,
    FRAGMENT_NOT_PUBLISHED,
    FRAGMENT_PUBLICATION_ATTEMPTED,
    REJECT,
    REJECTED,
    SCHEMA_INVALID,
    SCOPE_TEMPLATE_LOCAL,
    UNRESOLVED,
    WEAK,
)


@dataclass(frozen=True, slots=True)
class TemplateDependencies:
    """The two questions P8 cannot answer about a template proposal.

    `schema_validator` answers "is this shape legal" and nothing more.
    `published_fragment` answers "does this exact fragment, at this exact
    version, exist in the published catalogue" — the fragment boundary, held as
    a DISTINCT authority rather than folded into the schema check. An authority
    can be ABSENT, and an absent one is `ValidationUnavailable` like every other
    missing dependency here; a folded check can only be silent for a caller that
    supplies its own validator, and it would report `SCHEMA_INVALID` for a defect
    that is not a shape defect.
    """

    schema_validator: Callable[[object], bool]
    published_fragment: Callable[[str, int], bool]


def _payload_of(raw: object) -> Mapping[str, object]:
    if not isinstance(raw, Mapping):
        return {}
    payload = raw.get("payload")
    if isinstance(payload, Mapping):
        return payload
    return {}


def _rewrite(
    verdict: P8Verdict,
    *,
    outcome: str | None = None,
    disposition: str | None = None,
    reasons: tuple[str, ...] | None = None,
    may_propose: bool | None = None,
    requires_review: bool | None = None,
) -> P8Verdict:
    new_outcome = verdict.outcome if outcome is None else outcome
    new_review = verdict.requires_review if requires_review is None else requires_review
    if new_outcome == ACCEPT_CONTEXT_SUPPORTED:
        new_review = True
    new_propose = verdict.may_propose if may_propose is None else may_propose
    if new_outcome == WEAK:
        new_propose = False
    return dataclasses.replace(
        verdict,
        outcome=new_outcome,
        disposition=verdict.disposition if disposition is None else disposition,
        reasons=verdict.reasons if reasons is None else reasons,
        may_propose=new_propose,
        requires_review=new_review,
    )


def _dimensions(payload: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    raw = payload.get("dimensions")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    return tuple(item for item in raw if isinstance(item, Mapping))


def _names_an_unpublished_fragment(
    payload: Mapping[str, object],
    published_fragment: Callable[[str, int], bool],
) -> bool:
    """Every `fragment_refs` entry, asked of the injected authority.

    The shape of each entry is the schema validator's question, already answered
    by the time this runs; a malformed entry that reached here is still refused
    rather than passed to the authority, because an authority that has to guard
    its own argument types cannot return a clean verdict.
    """
    refs = payload.get("fragment_refs")
    if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes)):
        return False
    for ref in refs:
        if not isinstance(ref, Mapping):
            return True
        fragment_id = ref.get("fragment_id")
        fragment_version = ref.get("fragment_version")
        if not isinstance(fragment_id, str) or not isinstance(fragment_version, int):
            return True
        if isinstance(fragment_version, bool):
            return True
        if not published_fragment(fragment_id, fragment_version):
            return True
    return False


def _cited_refs(raw: object) -> set[str]:
    if not isinstance(raw, Mapping):
        return set()
    citations = raw.get("citations")
    if not isinstance(citations, Sequence) or isinstance(citations, (str, bytes)):
        return set()
    refs: set[str] = set()
    for item in citations:
        if isinstance(item, Mapping) and item.get("evidence_ref"):
            refs.add(str(item["evidence_ref"]))
    return refs


def _template_site(
    dossier: Dossier,
    raw: object,
    verdict: P8Verdict,
    dependencies: TemplateDependencies,
) -> P8Verdict | None:
    payload = _payload_of(raw)
    if any(key in payload for key in FORBIDDEN_PUBLISHING_KEYS):
        # Rejected on sight, before any content is read. A proposal may REFERENCE
        # published shared logic; creating any is a human review decision made
        # once, not a side effect of one branch's model call.
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(FRAGMENT_PUBLICATION_ATTEMPTED,),
            may_propose=False,
            requires_review=False,
        )
    if not dependencies.schema_validator(payload):
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(SCHEMA_INVALID,),
            may_propose=False,
            requires_review=False,
        )
    if _names_an_unpublished_fragment(payload, dependencies.published_fragment):
        # NOT `SCHEMA_INVALID`: the shape is legal and the reference is not
        # published. Site C already keeps this pair apart as `INVENTED_NODE`
        # versus `NODE_NOT_IN_FROZEN_TREE`.
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(FRAGMENT_NOT_PUBLISHED,),
            may_propose=False,
            requires_review=False,
        )
    # The closure is a CLASSIFIER, not a whole-payload rejection. A name inside
    # it is fact-backed; a name outside it is a template-local label, which is
    # how a group from a schema with no declared fields still gets a reviewable
    # design. The protective force is kept intact and its blast radius narrowed:
    # claiming `schema-field` for a name the dossier never granted is the model
    # asserting a field it was not given, and that is still a REJECT. A
    # template-local name that is a live P6 field key belonging to another schema
    # is caught upstream by P10's own `schema_validator`, which holds the
    # catalogue this part deliberately cannot reach.
    vocab = set(dossier.allowed_vocabulary)
    dimensions = _dimensions(payload)
    #
    # An UNDECLARED tier is read as the strict one. Only an explicit
    # `template-local` exempts a name from the closure, so silence cannot buy
    # leniency and every payload written before the tier existed keeps the
    # verdict it was recorded with. Requiring the tier to be stated is P10's
    # `schema_validator`; defaulting a missing one to the claim that carries the
    # most obligation is this gate's.
    if any(
        item.get("scope") != SCOPE_TEMPLATE_LOCAL and item.get("name") not in vocab
        for item in dimensions
    ):
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    cited = _cited_refs(raw)
    if any(item.get("evidence_ref") not in cited for item in dimensions):
        return _rewrite(
            verdict,
            outcome=REJECT,
            disposition=REJECTED,
            reasons=(),
            may_propose=False,
            requires_review=False,
        )
    levels = payload.get("levels")
    if isinstance(levels, Sequence) and not isinstance(levels, (str, bytes)):
        if any(
            isinstance(level, Mapping) and not level.get("retrieval_justification")
            for level in levels
        ):
            return _rewrite(
                verdict,
                outcome=WEAK,
                disposition=UNRESOLVED,
                reasons=(),
                may_propose=False,
                requires_review=False,
            )
    return None


def _template_disposition(verdict: P8Verdict) -> P8Verdict:
    if verdict.outcome == REJECT and not verdict.reasons:
        return _rewrite(verdict, disposition=REJECTED)
    if verdict.outcome == WEAK:
        return _rewrite(verdict, disposition=UNRESOLVED)
    if verdict.outcome == ABSTAIN:
        return verdict
    if verdict.outcome == ACCEPT_DIRECT:
        return verdict
    if verdict.outcome == ACCEPT_CONTEXT_SUPPORTED:
        return verdict
    return verdict


def validate_template_response(
    dossier: Dossier,
    response_bytes: bytes,
    *,
    evidence_resolver,
    contradicts,
    dependencies: TemplateDependencies | None,
    model_id: str,
    prompt_fingerprint: str,
    dossier_builder: str,
    release_audit_id: int | None,
    handle_key: bytes,
):
    if dependencies is None or dependencies.schema_validator is None:
        return ValidationUnavailable(missing=("schema_validator",))
    if dependencies.published_fragment is None:
        # The fragment boundary is an authority, so its ABSENCE is reportable.
        # A caller that supplies only a schema validator used to get silence,
        # and against that silence a payload naming any fragment at all passed.
        return ValidationUnavailable(missing=("published_fragment",))

    def site(dossier_arg, raw, verdict):
        return _template_site(dossier_arg, raw, verdict, dependencies)

    result = validate_response(
        dossier,
        response_bytes,
        evidence_resolver=evidence_resolver,
        site_validator=site,
        contradicts=contradicts,
        model_id=model_id,
        prompt_fingerprint=prompt_fingerprint,
        dossier_builder=dossier_builder,
        release_audit_id=release_audit_id,
        handle_key=handle_key,
    )
    if isinstance(result, ValidationUnavailable):
        return result
    verdicts, report = result
    return tuple(_template_disposition(item) for item in verdicts), report
