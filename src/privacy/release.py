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
    from privacy.resolve import Materialised

__all__ = [
    "LOCALITIES", "ModelTarget", "Target", "ModelCallRequest", "Released", "Denied",
    "NeedsConsent", "ReleaseDecision", "REQUEST_FIELDS", "RELEASED_FIELDS",
    "DENIED_FIELDS", "NEEDS_CONSENT_FIELDS", "DECISION_TYPES", "DECISION_ORDER",
    "FORBIDDEN_PARAMETER_NAMES", "RELEASE_PARAMETERS", "MalformedRequest",
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


@dataclass(frozen=True, slots=True)
class ModelTarget:
    """Which model would receive the data. §8.4 audits it; §6 binds a release to it."""

    locality: str
    model_id: str
    provider: str

    def __post_init__(self) -> None:
        if self.locality not in LOCALITIES:
            raise MalformedRequest(
                f"locality {self.locality!r} is not one of {LOCALITIES}; a value "
                "outside a closed vocabulary is a load error, not a fallback")
        if not self.model_id or not self.provider:
            raise MalformedRequest(
                "§8.4 requires the audit record show WHICH MODEL received the data; "
                "an unnamed model or provider cannot satisfy that")

    def to_mapping(self) -> dict[str, str]:
        """The stored form. `AuditRecord.model` and the ledger both use it."""
        return {"locality": self.locality, "model_id": self.model_id,
                "provider": self.provider}


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
    materialised_items: tuple[Materialised, ...]
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
