# src/privacy/release.py
"""SPEC §6's request and its three-branch return. Types and constants only.

This module sits at the BOTTOM of P7's decision stack on purpose. `denial.py` imports
`Denied` from it at run time and `binding.py` imports `Released` from it under
TYPE_CHECKING, so anything this module imported from those two would close a cycle.
It therefore imports exactly two `privacy` modules at run time:

    privacy.consent      for NeedsConsent, which Task 14 owns and this module
                         re-exports so the union reads as one union in one place
    privacy.vocabulary   a LEAF -- it imports no `privacy` module at all -- for
                         `check_denial_reason`, so a hand-built `Denied` with an
                         invented reason is refused at construction

Everything else is annotation-only, under TYPE_CHECKING, which `from __future__ import
annotations` makes sufficient.

There is no override parameter anywhere in this file, and `FORBIDDEN_PARAMETER_NAMES`
plus `RELEASE_PARAMETERS` are what `tests/p7/test_p7_release.py` proves that with --
by parsing signatures and `dataclasses.fields`, never by reading source text.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from privacy.consent import NeedsConsent
from privacy.vocabulary import check_denial_reason

if TYPE_CHECKING:  # pragma: no cover - annotations only; no run-time edge
    from privacy.denial import RemedyOption
    from privacy.items import RequestedItem
    from privacy.redaction import RedactionManifest

__all__ = [
    "LOCALITIES", "CLOUD_LOCALITY", "ModelTarget", "Target", "ModelCallRequest", "ReleasedItem",
    "Released", "Denied",
    "NeedsConsent", "ReleaseDecision", "REQUEST_FIELDS", "RELEASED_FIELDS",
    "RELEASED_EVIDENCE_FIELDS", "CONTENT_BOUND_FIELDS",
    "DENIED_FIELDS", "NEEDS_CONSENT_FIELDS", "DECISION_TYPES", "DECISION_ORDER",
    "FORBIDDEN_PARAMETER_NAMES", "RELEASE_PARAMETERS", "MalformedRequest",
    "HEADING_SEGMENT", "unit_is_a_heading", "released_whole_heading_unit",
    "MalformedDecision", "NoPolicyInForce",
]


class MalformedRequest(ValueError):
    """The request cannot be evaluated. Shape, not policy."""


class MalformedDecision(ValueError):
    """A branch value was constructed in a shape §8.4 does not permit."""


class NoPolicyInForce(RuntimeError):
    """No policy is stored for this plan version, so there is nothing to authorize by.

    NOT a fourth branch and NOT a `Denied`. §8.4's audit record names the "authorizing
    policy"; with none in force there is no answer to give, only a call that cannot be
    evaluated -- the same class as `resolve.UnresolvableSpan`, and it propagates.

    The gate deliberately does not synthesise a default. W1's local-first floor is
    resolved in `defaults.effective_policy`, which is where Done-means 12 is proven,
    and a second resolution here would be a second home for it.
    """


#: SPEC §6: `model_target { locality: local | cloud, model_id, provider }`.
LOCALITIES: tuple[str, str] = ("local", "cloud")

#: The member of `LOCALITIES` that means the bytes leave the device. Named because
#: modules were comparing against the literal `"cloud"`, and brief §11 bans a bare
#: string. SPELLED, not indexed: `LOCALITIES[1]` is the other half of that same rule
#: -- an index couples every consumer to the tuple's ORDER, and a reorder would then
#: change what this means with no test failing. The guard below is what ties the two
#: together, so a rename in `LOCALITIES` is an ImportError rather than a comparison
#: that silently stops matching.
CLOUD_LOCALITY: str = "cloud"
if CLOUD_LOCALITY not in LOCALITIES:
    raise ImportError(
        f"{CLOUD_LOCALITY!r} is not one of SPEC §6's localities {LOCALITIES}")


@dataclass(frozen=True, slots=True)
class ModelTarget:
    """Which model would receive the data. §8.4 audits it; §6 binds a release to it."""

    locality: str
    model_id: str
    provider: str
    #: THE CONTEXT WINDOW THE MODEL IS GIVEN, where the destination has one.
    #:
    #: §8.4 audits what the model was given, and for a local model the window is
    #: part of that: the same dossier under two windows is not the same question,
    #: because a window that does not hold the prompt is answered from what fits.
    #: `readers.model_ollama` refuses rather than truncating, and this is the row
    #: that says which window it refused against.
    #:
    #: A DEPLOYMENT FACT AND NOT A PER-CALL ONE, which is why it belongs beside
    #: the model id rather than in a record of one call. ollama holds ONE context
    #: length per loaded model, so the window is fixed for the life of a run and
    #: every call in that run is given it; `readers.model_ollama` is built from
    #: one number and `_Invoke.context_tokens` reports the same one back.
    #:
    #: `None` where the destination has no such number of ours to state. A cloud
    #: provider's window is the provider's, not this deployment's, and a target
    #: that named one would be recording a number nobody here chose. It is
    #: omitted from the stored form entirely in that case, so a cloud row is the
    #: same bytes it has always been.
    context_tokens: int | None = None

    def __post_init__(self) -> None:
        if self.locality not in LOCALITIES:
            raise MalformedRequest(
                f"locality {self.locality!r} is not one of {LOCALITIES}; a value "
                "outside a closed vocabulary is a load error, not a fallback")
        if not self.model_id or not self.provider:
            raise MalformedRequest(
                "§8.4 requires the audit record show WHICH MODEL received the data; "
                "an unnamed model or provider cannot satisfy that")
        if self.context_tokens is not None and (
                not isinstance(self.context_tokens, int)
                or isinstance(self.context_tokens, bool)
                or self.context_tokens < 1):
            raise MalformedRequest(
                f"context_tokens is {self.context_tokens!r}, which is not a window "
                f"a model could have been given. The audit record is read as a "
                f"statement of fact about what the model was shown, so a number "
                f"that could not have been sent makes it false where it is written. "
                f"Absent is how a target says it has no window of ours to state.")

    def to_mapping(self) -> dict[str, object]:
        """The stored form. `AuditRecord.model` and the ledger both use it.

        THE WINDOW IS OMITTED WHEN THERE IS NONE rather than stored as null. A
        cloud target has always been three keys and still is, so no existing row
        changes shape; the key appears exactly where there is a number to put in
        it. `binding._target_form` serialises through here for the same reason it
        matters at all -- two spellings of the stored form would let the ledger
        and the audit record drift into describing one release two ways.
        """
        mapping: dict[str, object] = {
            "locality": self.locality, "model_id": self.model_id,
            "provider": self.provider}
        if self.context_tokens is not None:
            mapping["context_tokens"] = self.context_tokens
        return mapping


@dataclass(frozen=True, slots=True)
class Target:
    """§4.4, §7.7 -- what the call is about. Files, and optionally a group."""

    file_ids: tuple[str, ...]
    group_id: str | None = None

    def __post_init__(self) -> None:
        if not self.file_ids:
            raise MalformedRequest(
                "a release decision is about file versions; a target with no files "
                "has nothing to classify and nothing to audit")
        if len(set(self.file_ids)) != len(self.file_ids):
            raise MalformedRequest(
                f"file_ids {self.file_ids!r} repeats an id; the audit record's "
                "content_hashes would then double-count what left the device")


@dataclass(frozen=True, slots=True)
class ModelCallRequest:
    """SPEC §6's SEVEN fields, and deliberately no eighth.

    Every field is a REFERENCE. No field accepts a document string, a path, or an
    `Observation`: §8.4 puts "complete extracted text", "paths", "OCR output" and
    "raw sensitive values" in the always-local set, and a request that could carry one
    would have moved content before the gate had decided anything.

    `call_site` is NOT a field: B2 puts it inside `prompt_fingerprint` (§3.4, §8.2,
    §8.4), so it is neither a separate request field nor a separate binding term.
    """

    stage: str
    target: Target
    model_target: ModelTarget
    requested_items: tuple[RequestedItem, ...]
    prompt_template_id: str
    prompt_fingerprint: str
    max_dossier_tokens: int

    def __post_init__(self) -> None:
        if not self.stage:
            raise MalformedRequest(
                "§8.5 requires per-stage decomposition, so a call with no stage "
                "cannot be replayed or attributed")
        if not self.prompt_fingerprint:
            raise MalformedRequest(
                "§8.4 audits the prompt fingerprint, and B2 puts `call_site` inside "
                "it rather than beside it; an empty fingerprint audits nothing")
        if not self.prompt_template_id:
            raise MalformedRequest(
                "§8.8 reproduces the prompt in force at each call; that needs the "
                "template id")
        if not self.requested_items:
            raise MalformedRequest(
                "a request with no items has nothing to release")
        if self.max_dossier_tokens <= 0:
            raise MalformedRequest(
                "§8.6's ceiling is the caller's echo of P1's stored value (M9); zero "
                "or negative is not an echo of anything")


REQUEST_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(ModelCallRequest))


#: The segment kind whose unit IS a heading. P4's own vocabulary, not a second copy:
#: `extractors/pdf.py` addresses a heading by `segment("heading", index=...)` and
#: `evidence_shape.location.Segment` checks the kind against `SEGMENT_KINDS`.
HEADING_SEGMENT: str = "heading"


def unit_is_a_heading(location) -> bool:
    """Whether this observation's UNIT is a heading rather than a document.

    **`104` R-135's ruling, and it is one line because the question is structural.**
    Both release-request builders refuse a span covering the whole of its unit, which is
    §8.4's *"should not send full documents where a short heading or OCR excerpt is
    enough"*. `extractors/pdf.py:181` makes every heading its OWN text unit and gives
    the heading observation a span of `(0, len)` over it -- so the refusal fired on
    every heading in the product, at site A and site C alike, and refused the very thing
    §8.4 names as the sufficient alternative to a full document.

    Measured before the ruling: the one reading in the owner's corpus that states
    `COMS W3134: Data Structures` -- the code and the course's name together -- reached
    no model, so 19 of 43 labelled course codes were missing and 19 more were the title
    recorded where the code belonged, and site C's own instruction to judge two
    spellings had nothing to judge from.

    **A heading unit is not a document, and that is the whole test.** The innermost
    container segment says which it is. There is NO LENGTH BOUND here on purpose: a
    bound is a number nobody authored, and this deployment refuses to invent one. The
    exposure is COUNTED instead -- `llm_harness.records.GroundingReport` carries how
    many whole heading units a call released and the longest one's length -- so the
    first scorecard shows the real number rather than an estimate of it.

    The known way this is wrong is not this function's to fix: `recognition/detector.py`
    records body prose set in large type being tagged `heading` by a typographic guess.
    A heading that is really prose is that detector's defect, and the count above is
    what will show it.
    """
    path = location.container_path
    return bool(path) and path[-1].kind == HEADING_SEGMENT


def released_whole_heading_unit(location, unit_length: int | None) -> bool:
    """Whether this item is the EXEMPTION above: a span covering a whole heading unit.

    **The rule and its count are one expression, and that is the only reason this is a
    function.** `104` R-135 releases a whole heading unit and sets no length bound, and
    reports the exposure instead -- `llm_harness.records.GroundingReport` carries how
    many whole heading units a call released and the longest one's length. A count
    computed from a second spelling of the condition would drift from the condition the
    moment either was edited, and the field it feeds would then report a number about
    something else. `model_facts.releasable_observations` and
    `model_placement.releasable_excerpts` admit by this predicate and
    `llm_harness.validation.report_from_verdicts` counts by it, so there is one.

    `unit_length` is `None` when P4 has no unit at the observation's own path -- §2.3's
    cell and §2.8's EXIF field -- and a value with no unit is not the whole of one.
    """
    if unit_length is None:
        return False
    span = location.text_span
    if span is None:
        return False
    return (span.start <= 0 and span.end >= unit_length
            and unit_is_a_heading(location))


@dataclass(frozen=True, slots=True)
class ReleasedItem:
    """One item as the MODEL sees it. SPEC §6: "post-redaction values only".

    There is deliberately no `context_before` and no `context_after`. The context
    is the raw text on either side of the requested span, and §8.4 puts "complete
    extracted text" in the always-local set. `resolve.Materialised` keeps all
    three -- it is the pre-redaction record, the classifier is given the context
    before a redaction decision is made, and `RedactionEntry` records it in the
    LOCAL audit manifest. A released item has no place to put them, which is the
    property rather than a discipline about it: for as long as this type was
    `Materialised`, an 8-character requested span released every character of its
    61-character unit, the value redacted and the account number beside it not.
    """

    observation_key: str
    span: str
    value: str
    zone: str
    unit_length: int | None

    def content_mapping(self) -> dict[str, str]:
        """What this item CONTRIBUTES to the model-visible bytes, and only that.

        `binding.content_digest` folds these into the fourth binding term, and
        `llm_harness.released_content` recomputes the same three fields from the
        payload at the door. The two must produce the same mapping or the term
        binds nothing, so the shape is published HERE -- next to the type that
        defines it -- rather than agreed between two modules that cannot import
        each other.

        `unit_length` is absent because it is never written to the wire: it is the
        measurement the whole-document refusal is taken against, not a value.

        `observation_key` is absent for a different reason, and it is the one worth
        writing down. It IS on the wire, but keyed: `llm_harness.wire_handles`
        emits `HMAC(install key, observation_key)` so a recipient cannot run the
        dictionary attack that recovered a redacted value from an unkeyed digest.
        The gate holds the unkeyed key and the transport holds neither key nor the
        keying function, so neither can compute what the other sees -- and binding
        the identifier would have meant either handing the transport the handle key
        or unkeying the wire. What is bound is the CONTENT: the address it came
        from, the post-redaction value, and the zone.
        """
        return {"address": self.span, "value": self.value, "zone": self.zone}


#: The four keys `llm_harness.dossier._released_body` writes for one released item.
#: The door checks the payload's entries carry exactly these -- a fifth is how the
#: `context_before` §8.4 keeps local rides along beside a value that was redacted.
RELEASED_EVIDENCE_FIELDS: tuple[str, ...] = (
    "address", "observation_key", "value", "zone",
)

#: The three of those four the release BINDS, read from the method rather than
#: retyped so the two cannot drift. See `ReleasedItem.content_mapping` for why the
#: identifier is not among them.
CONTENT_BOUND_FIELDS: tuple[str, ...] = tuple(
    ReleasedItem(observation_key="", span="", value="", zone="",
                 unit_length=None).content_mapping()
)


@dataclass(frozen=True, slots=True)
class Released:
    """SPEC §6's SIX fields. Single-use and bound; the ledger is Task 12's.

    Instantiating this dataclass outside the gate buys nothing: `consume_release`
    checks the ledger, and a `release_id` that was never minted raises
    `ReleaseNotIssued`. That is the property that makes the door real, and it is
    proven in Task 12, not here.
    """

    release_id: str
    audit_id: int
    policy_version: str
    materialised_items: tuple[ReleasedItem, ...]
    redaction_manifest: RedactionManifest
    model_target: ModelTarget

    def __post_init__(self) -> None:
        if not self.release_id:
            raise MalformedDecision(
                "a release with no id cannot be bound or consumed (§6)")
        if not self.policy_version:
            raise MalformedDecision(
                "§6: the gate owns the policy and STAMPS the version; an unstamped "
                "release cannot be replayed under §8.8")


RELEASED_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(Released))


@dataclass(frozen=True, slots=True)
class Denied:
    """The gate's answer. Evidence-referenced (§6), and never a dead end (§8.6).

    FOUR fields. The skeleton's Task 11 block lists three and omits `evidence_refs`;
    SPEC §6 requires the explanation be "evidence-referenced" and Task 13's published
    `deny(reason, *, explanation, remedy_options, evidence_refs)` takes them, so a
    three-field dataclass makes that constructor unwritable.

    `evidence_refs` holds P4 `observation_key` values and never `observation_id`
    (M14): a per-row id dies on extractor upgrade, and `observation_key` deliberately
    excludes `extractor_version` (MINOR 8) so it survives one. It defaults to `()`
    because six of the eight reasons are decided from the request and the policy and
    have no evidence to cite; an empty tuple there is honest, not lazy.
    """

    reason: str
    explanation: str
    remedy_options: tuple[RemedyOption, ...]
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        check_denial_reason(self.reason)
        if not self.explanation or not self.explanation.strip():
            raise MalformedDecision(
                "§8.6 requires the product show 'what has been deferred, and why'; a "
                "denial with an empty explanation shows only the first half")
        if not self.remedy_options:
            raise MalformedDecision(
                "a denial with no legitimate alternative is a dead end the user "
                "cannot act on (§8.6)")


DENIED_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(Denied))
NEEDS_CONSENT_FIELDS: tuple[str, ...] = tuple(f.name for f in fields(NeedsConsent))

#: SPEC §6: `ReleaseDecision = Released | Denied | NeedsConsent`. Three, and no fourth.
#: `NoPolicyInForce` is an exception, not a member: it says the call cannot be
#: evaluated, where all three of these say what the answer IS.
ReleaseDecision = Released | Denied | NeedsConsent

DECISION_TYPES: tuple[type, ...] = (Released, Denied, NeedsConsent)

#: The order `Gate.release` evaluates in, published so a reviewer can read it without
#: reading the function and so a reordering is a diff on a constant. It is forced, not
#: chosen: nothing materialises until every check that could deny has run, because a
#: gate that resolved first would hold the text in memory before deciding it was
#: allowed to. Task 13's `DECIDABLE_FROM_REQUEST` is the same principle as data, and
#: the test asserts the two agree.
DECISION_ORDER: tuple[str, ...] = (
    "collect_request_denials",
    "needs_consent",
    "materialise",
    "collect_content_denials",
    "append_audit",
    "mint_release",
)

#: The exact parameter names of `Gate.release`. Published so the whitelist assertion
#: is an EQUALITY against a named constant rather than a literal buried in a test.
RELEASE_PARAMETERS: frozenset[str] = frozenset({"self", "request"})

#: The words a future convenience would reach for. Compared TOKEN-WISE, on
#: `name.split("_")`, never by substring: substring matching would fail a legitimate
#: `unclassified_permits_local` and would tempt the next author to rename a parameter
#: to appease a test. This is the weaker of the two guards -- a blacklist only catches
#: the words someone thought of -- and it exists beside `RELEASE_PARAMETERS`, which
#: proves no unpublished parameter exists at all.
FORBIDDEN_PARAMETER_NAMES: frozenset[str] = frozenset({
    "force", "override", "bypass", "allow", "approved", "skip", "unsafe",
    "trusted", "internal", "escalate", "ignore", "disable", "raw", "plaintext",
})
