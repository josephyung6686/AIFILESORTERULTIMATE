# src/llm_harness/records.py
"""Immutable P8 contracts. Shapes freeze here; later tasks must not rename them.

Internal modules import `P8Verdict` by that name. This package exports no bare
`Verdict`. `NeedsConsent` is P7's class and is not a P8 outcome.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.vocabulary import RELIABILITY_STATES, check
from privacy.release import (
    Denied, MalformedRequest, ModelCallRequest, ModelTarget, NeedsConsent,
)
from privacy.resolve import AmbiguousObservationKey, UnresolvableSpan

from llm_harness.vocabulary import (
    ACCEPT_CONTEXT_SUPPORTED,
    ALL_REASON_CODES,
    CALL_SITES,
    DISPOSITIONS,
    ELIGIBILITY_BY_SITE,
    EVIDENCE_BASES,
    LEVEL_REQUIREMENTS,
    OUTCOMES,
    PRE_CALL_REASON_CODES,
    PRIVACY_GATE_REFUSED,
    REDUCTION_RUNGS,
    SITES_REQUIRING_PLAN_VERSION,
    VERDICT_SCOPES,
    WEAK,
)


class MalformedRecord(ValueError):
    """A frozen contract was constructed in a shape P8 does not permit."""


class MalformedVerdict(MalformedRecord):
    """A `P8Verdict` violated a construction-time SPEC invariant."""


def _require(value: str, vocabulary: tuple[str, ...] | frozenset[str], *,
             name: str) -> str:
    if value not in vocabulary:
        raise MalformedRecord(
            f"{name}={value!r} is not one of {tuple(vocabulary)}"
        )
    return value


def _freeze_sequence(instance: object, name: str) -> tuple:
    value = getattr(instance, name)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        length = len(value) if isinstance(value, (str, bytes)) else 0
        raise MalformedRecord(
            f"{name} is a sequence; a bare string would become {length} "
            "one-character references"
        )
    frozen = tuple(value)
    object.__setattr__(instance, name, frozen)
    return frozen


def _require_plan_version(call_site: str, plan_version: str | None) -> None:
    if call_site in SITES_REQUIRING_PLAN_VERSION and not plan_version:
        raise MalformedRecord(
            f"plan_version is required at {call_site}; it is null only at A and B"
        )


def assemble(prompt_definition: PromptDefinition,
             canonical_dossier_bytes: bytes) -> bytes:
    """Exact model-visible bytes. Provenance fields are not included."""
    return prompt_definition.template_bytes + canonical_dossier_bytes


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    template_id: str
    template_bytes: bytes
    response_schema_bytes: bytes
    call_site: str
    call_site_version: str
    shaping_policy_bytes: bytes
    #: WHETHER THE OWNER RATIFIED THIS TEXT, set by the loader from the packet
    #: manifest rather than inferred from the id. The finish line's invariant is
    #: that no verdict produced under an unratified prompt is ever applied,
    #: whatever mode flags say, and a property that governs application belongs on
    #: the object that carries the text.
    #:
    #: `False` BY DEFAULT, which is the safe direction: a caller that says nothing
    #: gets a prompt whose answers are recorded and not acted on. The opposite
    #: default would apply a verdict on the strength of an omission.
    #:
    #: The id convention is what the manifest enforces; this is what the code
    #: reads. A string test would make the invariant depend on a naming habit, and
    #: a renamed draft would start applying.
    ratified: bool = False

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        if not isinstance(self.ratified, bool):
            raise MalformedRecord(
                "prompt definition `ratified` is a bool set by the loader from "
                "the packet manifest; anything else is a caller guessing at "
                "whether the owner approved this text")
        if not self.template_id or not self.call_site_version:
            raise MalformedRecord("prompt definition requires template_id and call_site_version")
        if not self.template_bytes:
            raise MalformedRecord("template_bytes are injected; there is no default prompt")
        if not self.response_schema_bytes:
            raise MalformedRecord(
                "response_schema_bytes are injected; there is no default schema"
            )
        if not self.shaping_policy_bytes:
            raise MalformedRecord(
                "shaping_policy_bytes are injected; there is no default policy"
            )


@dataclass(frozen=True, slots=True)
class CallPayload:
    prompt_definition: PromptDefinition
    canonical_dossier_bytes: bytes
    model_visible_bytes: bytes
    model_target: ModelTarget
    prompt_fingerprint: str
    policy_version: str
    release_id: str
    dossier_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.prompt_definition, PromptDefinition):
            raise MalformedRecord("CallPayload.prompt_definition must be a PromptDefinition")
        if not isinstance(self.model_target, ModelTarget):
            raise MalformedRecord("CallPayload.model_target must be privacy.release.ModelTarget")
        expected = assemble(self.prompt_definition, self.canonical_dossier_bytes)
        if self.model_visible_bytes != expected:
            raise MalformedRecord(
                "model_visible_bytes must equal assemble(prompt_definition, "
                "canonical_dossier_bytes); callers cannot supply a mismatched "
                "preassembled representation"
            )
        if not self.prompt_fingerprint or not self.policy_version or not self.release_id:
            raise MalformedRecord(
                "prompt_fingerprint, policy_version, and release_id are required "
                "provenance fields and are not part of the model-visible bytes"
            )
        if not self.dossier_id:
            raise MalformedRecord(
                "dossier_id is the content address of the dossier these bytes carry. "
                "It is what the stored response and any call failure are keyed by; "
                "release_id is a single-use capability and cannot serve as an identity"
            )
        if self.dossier_id == self.release_id:
            raise MalformedRecord(
                "dossier_id must not be the release_id: two calls over identical "
                "content would then have two identities and neither could be "
                "recognised as the other's replay"
            )


def build_call_payload(
    prompt_definition: PromptDefinition,
    canonical_dossier_bytes: bytes,
    *,
    model_target: ModelTarget,
    policy_version: str,
    release_id: str,
    dossier_id: str,
) -> CallPayload:
    """Sole public factory. Always assembles model-visible bytes from the two sources.

    The stored fingerprint is computed from `prompt_definition`. It used to accept
    a `prompt_fingerprint` and silently discard it, which is the same footgun as
    honouring it: a caller passing a real digest got neither an error nor an
    effect. There is one source, and it is the definition.
    """
    from llm_harness.fingerprint import prompt_fingerprint as fingerprint_of

    return CallPayload(
        prompt_definition=prompt_definition,
        canonical_dossier_bytes=canonical_dossier_bytes,
        model_visible_bytes=assemble(prompt_definition, canonical_dossier_bytes),
        model_target=model_target,
        prompt_fingerprint=fingerprint_of(prompt_definition),
        policy_version=policy_version,
        release_id=release_id,
        dossier_id=dossier_id,
    )


@dataclass(frozen=True, slots=True)
class DossierRequest:
    """Reference-only. No materialised content, excerpts, or observation bodies."""

    call_site: str
    subject_ref: str
    eligibility_reason: str
    evidence_items: tuple[EvidenceItem, ...]
    conflicts: tuple[Conflict, ...]
    model_call_request: ModelCallRequest
    plan_version: str | None
    evidence_snapshot_id: str | None

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        _require(
            self.eligibility_reason,
            ELIGIBILITY_BY_SITE[self.call_site],
            name="eligibility_reason",
        )
        _require_plan_version(self.call_site, self.plan_version)
        if not self.subject_ref:
            raise MalformedRecord("DossierRequest.subject_ref is required")
        if not isinstance(self.model_call_request, ModelCallRequest):
            raise MalformedRecord(
                "DossierRequest.model_call_request must be the live "
                "privacy.release.ModelCallRequest"
            )
        _freeze_sequence(self, "evidence_items")
        _freeze_sequence(self, "conflicts")
        if not self.evidence_items:
            raise MalformedRecord(
                "a request with no builder evidence metadata cannot become a dossier; "
                "P8 does not synthesise kind, location, reliability or basis"
            )
        if any(not isinstance(item, EvidenceItem) for item in self.evidence_items):
            raise MalformedRecord(
                "DossierRequest.evidence_items must be reference-only EvidenceItem "
                "records supplied by the dossier builder"
            )
        if any(not isinstance(item, Conflict) for item in self.conflicts):
            raise MalformedRecord("DossierRequest.conflicts must be Conflict records")


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_ref: str
    kind: str
    location: str
    excerpt_span: tuple[int, int] | None
    reliability_state: str
    basis: str

    def __post_init__(self) -> None:
        if not self.evidence_ref:
            raise MalformedRecord("EvidenceItem.evidence_ref is required")
        if self.excerpt_span is not None:
            span = _freeze_sequence(self, "excerpt_span")
            if len(span) != 2 or any(not isinstance(n, int) for n in span):
                raise MalformedRecord("excerpt_span must be a pair of ints")
        try:
            check(self.reliability_state, RELIABILITY_STATES, name="reliability_state")
        except ValueError as exc:
            raise MalformedRecord(str(exc)) from exc
        _require(self.basis, EVIDENCE_BASES, name="basis")


@dataclass(frozen=True, slots=True)
class FolderLevel:
    """One level of the folder tree the person's chosen situation would build.

    Three values, and **P8 authors none of them**. `field` is a P6 field key,
    `label` is the shipped applicability row's own `RoleBinding.label` -- "My
    school", "Semester", "Course", "Kind of work" -- and `requirement` is the
    template definition's own word for that dimension, `required` or `optional`.
    The composition root reads all three off the template library and hands them in;
    nothing here mints a label, a word or an order.

    **Why it is a record and not a bare string.** `dossier._body` writes these into
    the model-visible bytes, and `canonical_dossier_bytes` re-derives those bytes
    from the `Dossier` RECORD, so a level that lived only in the body would not
    survive the round trip the transport actually makes.

    **Why nothing about the file may be added to it.** A level is the same on every
    file in the situation -- that is the whole reason it is safe to send. An example
    value, a matching excerpt or a per-file hint would make this key a channel for
    §8.4's always-local set, so the shape is closed at these three and
    `released_content` refuses any entry carrying a fourth.
    """

    field: str
    label: str
    requirement: str

    def __post_init__(self) -> None:
        if not self.field or not self.label:
            raise MalformedRecord(
                "FolderLevel requires a field key and the library's own label; a "
                "level with neither tells the model nothing it did not already have"
            )
        if self.requirement not in LEVEL_REQUIREMENTS:
            raise MalformedRecord(
                f"{self.requirement!r} is not one of the template library's own "
                f"words for a dimension {sorted(LEVEL_REQUIREMENTS)}. P8 does not "
                "translate the library's vocabulary and must not invent a third "
                "strength for a level nobody graded that way"
            )


@dataclass(frozen=True, slots=True)
class ReleasedEvidence:
    """One P7 `ReleasedItem` as the model saw it.

    `value` is the released/redacted value and is the ONLY span-matching source
    universal validation may use. `address` is P7's span locator; a citation that
    matches the raw P4 text but not this value is not grounded in what was released.

    It carried `context_before` / `context_after` / `context_truncated`, copied
    from P7 into `dossier._released_body` -- the canonical model-visible bytes --
    and nothing in P8 ever read them: `validation._check_citation` matches
    `cited_span` against `value` and nothing else. §8.4 puts "complete extracted
    text" in the always-local set, so they are gone from the record rather than
    emptied in it.
    """

    observation_key: str
    address: str
    value: str
    zone: str

    def __post_init__(self) -> None:
        if not self.observation_key or not self.address:
            raise MalformedRecord(
                "ReleasedEvidence requires observation_key and address; an item with "
                "no address cannot bind a citation to what P7 released"
            )


@dataclass(frozen=True, slots=True)
class Conflict:
    conflict_id: str
    kind: str

    def __post_init__(self) -> None:
        if not self.conflict_id or not self.kind:
            raise MalformedRecord("Conflict requires conflict_id and kind")


@dataclass(frozen=True, slots=True)
class Citation:
    evidence_ref: str
    cited_span: str | None
    metadata_field_name: str | None
    why_it_supports: str

    def __post_init__(self) -> None:
        if not self.evidence_ref or not self.why_it_supports:
            raise MalformedRecord("Citation requires evidence_ref and why_it_supports")
        has_span = bool(self.cited_span)
        has_field = bool(self.metadata_field_name)
        if has_span == has_field:
            raise MalformedRecord(
                "Citation carries exactly one of cited_span or metadata_field_name"
            )


@dataclass(frozen=True, slots=True)
class Unknown:
    insufficiency_statement: str

    def __post_init__(self) -> None:
        if not self.insufficiency_statement:
            raise MalformedRecord("Unknown requires an insufficiency_statement")


@dataclass(frozen=True, slots=True)
class Claim:
    payload: Mapping[str, object]
    citations: tuple[Citation, ...]
    unknown: Unknown | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
        _freeze_sequence(self, "citations")
        has_unknown = self.unknown is not None
        has_citations = bool(self.citations)
        if has_unknown == has_citations:
            raise MalformedRecord(
                "Claim carries exactly one of citations or Unknown, never both or neither"
            )
        if has_unknown and not isinstance(self.unknown, Unknown):
            raise MalformedRecord("Claim.unknown must be Unknown")
        if has_citations and any(not isinstance(item, Citation) for item in self.citations):
            raise MalformedRecord("Claim.citations must be Citation records")


@dataclass(frozen=True, slots=True)
class Dossier:
    dossier_id: str
    call_site: str
    subject_ref: str
    eligibility_reason: str
    plan_version: str | None
    policy_version: str
    allowed_vocabulary: tuple[str, ...]
    evidence_items: tuple[EvidenceItem, ...]
    conflicts: tuple[Conflict, ...]
    released_evidence: tuple[ReleasedEvidence, ...]
    max_dossier_tokens: int
    reduction_rung: str
    release_id: str
    #: The folder levels the person's chosen situation would build, in the template
    #: library's own order. A PROJECTION of `allowed_vocabulary` and never a second
    #: vocabulary -- `dossier._body` refuses a level naming a field the vocabulary
    #: does not carry, because a model told to fill a key the validator will reject
    #: for not being in the active schema is rejected for obeying its instructions.
    #:
    #: Empty at B, C and D, which design no tree, and that is a truthful answer
    #: rather than a default: the site that DOES design one refuses an empty list at
    #: composition (`model_facts.require_folder_levels`), where the deployment that
    #: forgot to read the library is a `TypeError` and not a quiet dossier.
    folder_levels: tuple[FolderLevel, ...] = ()

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        _require(
            self.eligibility_reason,
            ELIGIBILITY_BY_SITE[self.call_site],
            name="eligibility_reason",
        )
        _require_plan_version(self.call_site, self.plan_version)
        _require(self.reduction_rung, REDUCTION_RUNGS, name="reduction_rung")
        if not self.dossier_id or not self.subject_ref:
            raise MalformedRecord("Dossier requires dossier_id and subject_ref")
        if not self.policy_version or not self.release_id:
            raise MalformedRecord(
                "Dossier is content-bearing only after P7 release; "
                "policy_version and release_id are required"
            )
        if self.max_dossier_tokens <= 0:
            raise MalformedRecord("max_dossier_tokens must be a positive echo of the ceiling")
        _freeze_sequence(self, "allowed_vocabulary")
        _freeze_sequence(self, "evidence_items")
        _freeze_sequence(self, "conflicts")
        _freeze_sequence(self, "released_evidence")
        _freeze_sequence(self, "folder_levels")
        if any(not isinstance(item, FolderLevel) for item in self.folder_levels):
            raise MalformedRecord(
                "folder_levels must be FolderLevel records read off the shipped "
                "template library; a mapping here is a caller authoring a level"
            )
        if any(not isinstance(item, EvidenceItem) for item in self.evidence_items):
            raise MalformedRecord("evidence_items must be EvidenceItem records")
        if any(not isinstance(item, Conflict) for item in self.conflicts):
            raise MalformedRecord("conflicts must be Conflict records")
        if any(not isinstance(item, ReleasedEvidence) for item in self.released_evidence):
            raise MalformedRecord(
                "released_evidence must be ReleasedEvidence records built from P7's "
                "Materialised items"
            )


@dataclass(frozen=True, slots=True)
class CheckedCitation:
    citation_ref: str
    resolved: bool
    span_matched: bool

    def __post_init__(self) -> None:
        if not self.citation_ref:
            raise MalformedRecord("CheckedCitation.citation_ref is required")


@dataclass(frozen=True, slots=True)
class P8Verdict:
    verdict_id: str
    dossier_id: str
    claim_ref: str
    outcome: str
    disposition: str
    reasons: tuple[str, ...]
    may_propose: bool
    requires_review: bool
    citations_checked: tuple[CheckedCitation, ...]
    scope: str
    validator_version: str
    policy_version: str
    plan_version: str | None

    def __post_init__(self) -> None:
        try:
            _freeze_sequence(self, "reasons")
            _freeze_sequence(self, "citations_checked")
            _require(self.outcome, OUTCOMES, name="outcome")
            _require(self.disposition, DISPOSITIONS, name="disposition")
            _require(self.scope, VERDICT_SCOPES, name="scope")
            for reason in self.reasons:
                _require(reason, ALL_REASON_CODES, name="reason")
        except ValueError as exc:
            raise MalformedVerdict(str(exc)) from exc
        if not self.verdict_id or not self.dossier_id or not self.claim_ref:
            raise MalformedVerdict("verdict_id, dossier_id, and claim_ref are required")
        if not self.validator_version or not self.policy_version:
            raise MalformedVerdict("validator_version and policy_version are required")
        if self.outcome == ACCEPT_CONTEXT_SUPPORTED and not self.requires_review:
            raise MalformedVerdict(
                "accept_context_supported always requires_review=True"
            )
        if self.outcome == WEAK and self.may_propose:
            raise MalformedVerdict("weak forbids may_propose=True")
        if any(not isinstance(item, CheckedCitation) for item in self.citations_checked):
            raise MalformedVerdict("citations_checked must be CheckedCitation records")


@dataclass(frozen=True, slots=True)
class GroundingReport:
    dossier_id: str
    call_site: str
    model_id: str
    prompt_fingerprint: str
    validator_version: str
    citations_total: int
    citations_resolved: int
    citations_span_matched: int
    claims_total: int
    claims_abstained: int
    claims_accepted_direct: int
    claims_accepted_context: int
    claims_weak: int
    claims_rejected: int
    reasons_histogram: Mapping[str, int]
    reduction_rung: str
    release_audit_id: int | None
    dossier_builder: str
    #: `104` R-135'S EXPOSURE COUNT, AND IT STANDS IN FOR A NUMBER NOBODY AUTHORED.
    #: The ruling releases a span covering a whole HEADING unit, because §8.4 names a
    #: heading as what to send instead of a full document, and it sets no length bound:
    #: a bound would be an invented threshold and this deployment invents none. So the
    #: exposure is reported rather than capped. `heading_units_released` is how many
    #: released items were a whole heading unit; `longest_heading_unit_length` is the
    #: longest of them in characters.
    #:
    #: They are here rather than in a log because §8.5 replays a run and compares it,
    #: and because the first live scorecard has to show this number rather than an
    #: estimate of it. `recognition/detector.py` records body prose set in large type
    #: being tagged `heading` by a typographic guess; if that is releasing paragraphs,
    #: `longest_heading_unit_length` is where it becomes visible.
    #:
    #: Defaulted, unlike every field above, and that is deliberate: a caller that has
    #: not been taught to count reports zero rather than failing to construct, so this
    #: row cannot break a call site that has nothing to do with R-135.
    heading_units_released: int = 0
    longest_heading_unit_length: int = 0

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        _require(self.reduction_rung, REDUCTION_RUNGS, name="reduction_rung")
        object.__setattr__(
            self, "reasons_histogram", MappingProxyType(dict(self.reasons_histogram)),
        )
        if not self.dossier_id or not self.model_id or not self.prompt_fingerprint:
            raise MalformedRecord("GroundingReport requires dossier, model, and fingerprint")
        if not self.validator_version or not self.dossier_builder:
            raise MalformedRecord("validator_version and dossier_builder are required")
        for name in ("heading_units_released", "longest_heading_unit_length"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise MalformedRecord(f"{name} is a count, and a count is never negative")


@dataclass(frozen=True, slots=True)
class Refusal:
    """Gate-only. Constructed from P7 `Denied`. Not `NeedsConsent`.

    Carries the two P8 versions because `emit_stage_output` serialises this record
    verbatim into P2's opaque payload: without them, an `abstained` row is a
    measurement nobody can attribute to a validator build or a policy.
    """

    denied: Denied
    validator_version: str
    policy_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.denied, Denied):
            raise MalformedRecord(
                "Refusal is the Denied path only; construct from privacy.release.Denied"
            )
        if not self.validator_version or not self.policy_version:
            raise MalformedRecord(
                "a refusal measurement names the validator and policy versions it "
                "was produced under"
            )

    @property
    def reason(self) -> str:
        return PRIVACY_GATE_REFUSED

    @property
    def explanation(self) -> str:
        return self.denied.explanation

    @property
    def denial_reason(self) -> str:
        return self.denied.reason


@dataclass(frozen=True, slots=True)
class PreCallAbstention:
    reason: str
    call_site: str
    subject_ref: str

    def __post_init__(self) -> None:
        _require(self.reason, PRE_CALL_REASON_CODES, name="reason")
        _require(self.call_site, CALL_SITES, name="call_site")
        if not self.subject_ref:
            raise MalformedRecord("PreCallAbstention.subject_ref is required")


@dataclass(frozen=True, slots=True)
class CallFailed:
    """The bytes failed. Carries the two P8 versions for the same reason `Refusal`
    does: `emit_stage_output` serialises it verbatim into P2's `error` row."""

    request_identity: str
    release_id: str
    audit_id: int | None
    explanation: str
    validator_version: str
    policy_version: str

    def __post_init__(self) -> None:
        if not self.request_identity or not self.release_id or not self.explanation:
            raise MalformedRecord(
                "CallFailed requires request_identity, release_id, and explanation"
            )
        if not self.validator_version or not self.policy_version:
            raise MalformedRecord(
                "a failure measurement names the validator and policy versions it "
                "was produced under"
            )


@dataclass(frozen=True, slots=True)
class CallResult:
    """Completed P8 attempt. NeedsConsent is not a branch of this type."""

    value: P8Verdict | Refusal | PreCallAbstention | CallFailed

    def __post_init__(self) -> None:
        if isinstance(self.value, NeedsConsent):
            raise MalformedRecord(
                "NeedsConsent is not a P8 CallResult branch; return it unchanged"
            )
        if not isinstance(
            self.value, (P8Verdict, Refusal, PreCallAbstention, CallFailed),
        ):
            raise MalformedRecord(
                "CallResult.value must be P8Verdict, Refusal, PreCallAbstention, "
                "or CallFailed"
            )


#: `104` R-O. The exceptions that mean A PART OF THE PRODUCT REFUSED, raised where
#: a caller expected a decision, and the whole of that set.
#:
#: Every member is a refusal the raising site describes as one in its own words.
#: `privacy.gate`: *"A kind this door has no reading for is REFUSED, by name ...
#: this is a request the gate cannot evaluate at all."* `privacy.resolve`: an
#: observation that belongs to a file outside the request, or that two rows answer
#: two ways. `ModelCallRequest.__post_init__`: a request §8.4's audit record could
#: not describe truthfully. None is a bug in the caller and none is a judgement
#: about the subject; each is one call that cannot be made.
#:
#: **`NoPolicyInForce` IS NOT HERE, and that is the line between the two kinds.**
#: The members above are per-subject and the next subject may well succeed; a run
#: with no policy in force is misconfigured for every call it will ever make, and
#: 199 identical refusal rows would bury the one sentence a person could act on.
#:
#: **Nor is anything wider.** A `TypeError` or an `AttributeError` at these seams is
#: a programming error, and a catch that swallowed one would turn every future bug
#: there into a quiet "0 facts written" -- which is the failure this exists to stop,
#: wearing its name.
#:
#: HERE, and not in `harness.py`, because the sites that must catch it are not all
#: allowed to know `harness.py`: `tests/p9/test_p9_no_invention.py` and
#: `tests/p11/test_p11_connections.py` both hold `run_call` to one importer per
#: package, and `privacy.resolve` is banned outright under `src/grouping/`. The
#: records module is the surface every one of them already reads.
REFUSAL_EXCEPTIONS: tuple[type[BaseException], ...] = (
    MalformedRequest, UnresolvableSpan, AmbiguousObservationKey,
)


@dataclass(frozen=True, slots=True)
class CallRefused:
    """`104` R-O: a part of the product refused where a decision was expected.

    NOT a `Refusal` and not a `PreCallAbstention`, and the difference is the whole
    reason this exists. A `Refusal` carries P7's `Denied` -- §8.4's answer to "may
    this be sent", drawn from a closed vocabulary of reasons the owner approved. A
    `PreCallAbstention` says this subject was never eligible or the scan had no
    budget left. `privacy.gate` names the third thing itself, at the site that
    raises it: *"this is a request the gate cannot evaluate at all -- the same class
    as `NoPolicyInForce` and `resolve.UnresolvableSpan`, which is why it
    propagates."*

    Propagating is right at the gate and wrong at the caller. Twice on a real
    corpus the raise reached `main`: thirty-seven minutes of fact calls and then a
    traceback with no report, and the same screen again after the first cause was
    fixed. `00` §8 and `104` §7's Phase 1 step 6 want the other shape -- the call is
    recorded as refused, by reason; the subject falls back to what this device could
    decide alone; the run goes on and the report says how many were refused and why.

    **`refusal_class` is the exception's TYPE NAME and never its message.** The
    message that ended the second run named a file id and a filename;
    `transport._client_exception_explanation` made the same reduction for the same
    reason, and §8.4's property 4 -- nothing reaches a screen, a log or a durable
    record that a person did not agree to send there -- is why. Nothing in `src/`
    branches on the free text, so removing the channel costs no reader.

    NOT a member of `CallResult`. That union is the four outcomes a call that
    HAPPENED can have; a refusal at the door is not one of them, and widening it
    here would let a refusal be recorded as though bytes had been sent.
    """

    call_site: str
    subject_ref: str
    refusal_class: str

    def __post_init__(self) -> None:
        _require(self.call_site, CALL_SITES, name="call_site")
        if not self.subject_ref:
            raise MalformedRecord("CallRefused.subject_ref is required")
        if not self.refusal_class:
            raise MalformedRecord(
                "a refused call names what refused it; an unnamed refusal is a "
                "silence with a row"
            )


@dataclass(frozen=True, slots=True)
class ValidationUnavailable:
    """Missing injected capabilities. Never an abstain outcome."""

    missing: tuple[str, ...]

    def __post_init__(self) -> None:
        _freeze_sequence(self, "missing")
        if not self.missing or any(not name for name in self.missing):
            raise MalformedRecord(
                "ValidationUnavailable must name the missing injected capabilities"
            )
