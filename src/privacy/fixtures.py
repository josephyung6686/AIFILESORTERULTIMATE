# src/privacy/fixtures.py
"""SPEC §11's published fixtures: the door's behaviour as data, so P8 can be built
against P7 before P8 exists.

§11: "Request -> decision pairs, one per `Denied.reason`, plus: a clean `Released`
with redaction applied; a `NeedsConsent` returning all four options; a protected file
under each of the four modes; an `unreadable_unclassified` file; a `Protected Records`
residual request. Each fixture carries the audit record the gate would have appended."

Three things are true of this module and none of them is a style choice:

- **It is a LEAF.** Nothing else under `src/privacy/` imports it. That is what keeps
  the numbers it holds -- one dossier ceiling, one span -- out of the gate: a fixture
  records a value the way a recorded call records one.
- **Every excerpt stands on one of P4's nineteen published fixtures.** The keys are
  computed from `evidence_shape.fixtures` at import, never copied. `observation_key`
  is derived from `(content_hash, extractor_name, locator, raw_value)` (M14), so a P4
  fixture that moves moves P7's key with it and the replay keeps resolving.
- **The always-local set is enforced twice, and fixture 7 is why.** Task 7 makes the
  nine named kinds unconstructible, so a request holding "OCR output" cannot be built
  and cannot be a fixture. `Denied(always_local_item)` is reached the other way, and
  there is exactly ONE way: `check_item` raises `AlwaysLocalRequested` when
  `item.observation_key in sensitive_keys`, and `sensitive_keys` is
  `sensitive_observation_keys(conn, file_id)` -- P4's runs for the file joined to P5's
  `POTENTIALLY_SENSITIVE` signals. So fixture 7 names the signalled key and the replay
  seeds the signal through P5's own writer. It is NOT reached through a zone:
  `check_item` has no zone branch and P4 fixture 8's text unit carries `zone = None`,
  so a fixture standing on that reading resolves and is RELEASED.

Four things the PLAN's draft of this module asserted are false against the SHIPPED
code, and each is recorded here rather than worked around silently:

1. **`policy_version` is minted, not carried.** `policy._persist` refuses a
   caller-supplied version (`CallerSuppliedPolicyVersion`) and mints
   `policy-{uuid4().hex}`. Every fixture policy therefore carries
   `UNSET_POLICY_VERSION`, and `policy_version` / `authorizing_policy` join `file_id`
   in `SUBSTITUTED_FIELDS`: they are identities a replay cannot preserve, not values
   a fixture may state.
2. **`unreadable_unclassified` cannot be a stored `ClassificationRecord`.**
   `ClassificationStore.write` raises `GateOutcomeNotAFileFact` on it (D2: "the
   absence of a record already says nothing has looked"). So fixture 15 does NOT
   carry a record with that class -- it carries none, and stands on P4 fixture 18,
   whose run completeness is `unreadable`. That extraction status is what the gate
   reads (`_completeness`), and it is what separates fixture 15's explanation from
   fixture 2's. The distinction D2 protects survives; it just does not live in the
   store, because D2 is precisely the ruling that it must not.
3. **`Denied.remedy_options` are `denial.RemedyOption` records, not strings**, and
   every fixture denial is built through `denial.deny`, which validates the
   explanation and the remedy list. A hand-built `Denied` would be a second
   constructor for a type that already refuses malformed values.
4. **No P4 fixture addresses its own text unit in full**, so
   `Denied(whole_document_requested)` is unreachable against the published nineteen:
   `resolve.materialise` refuses a request span that disagrees with the record, and
   every published span is a proper substring of its unit. `EXTRA_OBSERVATIONS`
   carries the one observation that closes the gap -- P4 fixture 11's own run, its own
   text unit, addressed `0..length` -- and nothing else. It is not a fixture of P7's
   own evidence: the bytes, the unit and the run are P4's, and the key is computed by
   P4's own `observation_key`. Reported as a gap in P4's fixture set.
"""
from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from evidence_shape.fixtures import FIXTURES as P4_FIXTURES
from evidence_shape.location import Location, TextSpan
from evidence_shape.observation import Observation

from privacy.audit import AUDIT_FIELDS, AuditRecord
from privacy.classification import ClassificationRecord
from privacy.consent import ConsentRequirement, NeedsConsent
from privacy.denial import PROTECTED_RECORDS_TEMPLATE, RemedyOption, deny
from privacy.items import (
    CandidateLabel, EvidenceReference, Excerpt, Filename, MetadataField,
    RedactedIdentifier,
)
from privacy.policy import UNSET_POLICY_VERSION, Policy
from privacy.redaction import RedactionEntry, RedactionManifest
from privacy.release import Denied, ModelCallRequest, ModelTarget, Released, Target
from privacy.resolve import Materialised
from privacy.vocabulary import CONSENT_OPTIONS

#: One clock for every fixture. A fixture whose timestamps drift is a fixture whose
#: golden audit record cannot be compared field for field.
FIXTURE_CLOCK: str = "2026-08-22T09:00:00+00:00"

#: The area name every scoped fixture uses. It is a STRING THE CALLER SUPPLIED and not
#: a definition: SPEC Open question 3 asks "What is a 'corpus area'?" and P7 answers
#: nothing. `Gate` takes a `scope_for` resolver with no default for the same reason.
FIXTURE_AREA: str = "Academics"

#: The acting component and user every fixture replays under. M8: the acting part
#: authors and P1 stores -- neither of these is a P7 rule.
FIXTURE_COMPONENT_VERSION: str = "0.1.0"
FIXTURE_USER_ID: str = "joseph"

#: P13 owns §8.4's retraction wording; `revocation.revoke` only enforces that it is
#: present. Fixture 3 needs a revocation to have happened, so it supplies one.
FIXTURE_RETRACTION_LIMIT: str = (
    "revoking consent stops future runs; it cannot retract what an external provider "
    "already received"
)

#: The bytes every fixture's document carries on disk, and the digest P1 computes from
#: them. `record_file` stats the path, so a `files` row needs real bytes; a fixture
#: with no P4 substrate has no published content hash to borrow, and this is the one
#: it gets -- computed, never invented.
FIXTURE_BYTES: bytes = b"%PDF-1.4 fixture bytes"
UNEXTRACTED_CONTENT_HASH: str = hashlib.sha256(FIXTURE_BYTES).hexdigest()

#: The placeholder `file_id` every fixture request carries before a replay rebinds it.
#: `record_file` mints the real one, which is why `file_id` is a substituted field.
FIXTURE_FILE_ID: str = "fixture-file"

#: The four identities a decision carries that only the gate can mint. `Released`
#: refuses an empty `release_id` and an unstamped `policy_version` (§6: "the gate owns
#: the policy and STAMPS the version"), so a fixture cannot leave them blank -- it
#: states a placeholder and the replay compares everything except these four.
PLACEHOLDER_RELEASE_ID: str = "release-minted-by-the-gate"
PLACEHOLDER_AUDIT_ID: int = 0
PLACEHOLDER_POLICY_VERSION: str = "policy-minted-by-the-gate"
PLACEHOLDER_CONSENT_REQUEST_ID: str = "consent-minted-by-the-gate"

#: The decision fields a replay cannot reproduce, by name.
MINTED_DECISION_FIELDS: frozenset[str] = frozenset(
    {"release_id", "audit_id", "policy_version", "consent_request_id"})

LOCAL_MODEL = ModelTarget(locality="local", model_id="local-small", provider="local")
CLOUD_MODEL = ModelTarget(locality="cloud", model_id="acme-large", provider="Acme")

#: SPEC §11's five "plus" items, in the SPEC's own words. This is the checklist, so a
#: paraphrase here stops it checking the document it came from.
SPEC_11_ITEMS: tuple[str, ...] = (
    "a clean `Released` with redaction applied",
    "a `NeedsConsent` returning all four options",
    "a protected file under each of the four modes",
    "an `unreadable_unclassified` file",
    "a `Protected Records` residual request",
)

#: The TWELVE keywords `Gate.__init__` accepts, in signature order. Pinned here
#: because the fixtures cannot be replayed without them, and because the signature had
#: no owner until the assembly gave it to this task: Task 11 said Task 20 pinned it
#: and Task 20 said it reported a pin on Task 11.
#:
#: The last two are OPTIONAL in the signature and mandatory here. Their `None` defaults
#: make two denial branches unreachable rather than untaken -- `template_for` gates
#: `protected_records_template` on an excerpt (fixture 4) and `measure_tokens` gates
#: `dossier_over_budget` (fixture 6) -- so a replay that left them unset would release
#: two fixtures and raise nothing.
GATE_ARGUMENTS: tuple[str, ...] = (
    "store", "plan_version", "classifier", "transform",
    "unclassified_permits_local", "scope_for", "files_in_scope",
    "component_version", "now", "user_id",
    "measure_tokens", "template_for",
)


class UnknownFixture(KeyError):
    """A fixture number nobody published. Not a fallback, not the nearest neighbour."""


def _p4(number: int):
    for fixture in P4_FIXTURES:
        if fixture.number == number:
            return fixture
    raise UnknownFixture(f"P4 publishes no fixture {number}")


def _key(number: int) -> str:
    """P4 fixture `number`'s first observation key, computed by P4 and read here."""
    return _p4(number).observations[0].observation_key


def _locator(number: int) -> str:
    """The same observation's canonical address -- what `redaction.span_address`
    returns and what the audit record stores as the `span` half of a pair."""
    return _p4(number).observations[0].locator


def _hash(number: int) -> str:
    return _p4(number).run.content_hash


def _zone(number: int) -> str:
    return _p4(number).observations[0].location.zone


def _span(number: int) -> TextSpan | None:
    return _p4(number).observations[0].location.text_span


def _unit_length(number: int) -> int:
    return _p4(number).text_units[0].length


# --- the one gap in P4's fixture set, closed with P4's own material ----------

def _whole_unit_observation(number: int) -> Observation:
    """P4 fixture `number`'s own text unit, addressed in full.

    `resolve.materialise` refuses a request span that disagrees with the record, and
    `items.is_whole_document` needs `span.end >= unit_length`. Every one of P4's
    published spans is a proper substring of its unit, so the two rules together make
    `Denied(whole_document_requested)` unreachable against the nineteen. This is the
    observation that closes it: P4's run, P4's content hash, P4's extractor, P4's text
    unit -- addressed `0..length`, which is what "the whole document was requested"
    means. The key is computed by P4's own `observation_key`.
    """
    source = _p4(number)
    unit = source.text_units[0]
    published = source.observations[0]
    return Observation(
        file_id=source.run.file_id, content_hash=source.run.content_hash,
        extractor_name=source.run.extractor_name,
        extractor_version=source.run.extractor_version,
        source_type=source.run.source_type, raw_value=unit.text,
        location=Location(zone=published.location.zone,
                          container_path=unit.container_path,
                          text_span=TextSpan(0, unit.length)),
        occurrence_count=1, observed_at=published.observed_at,
        reliability=published.reliability, run_id=source.run.run_id)


#: The P4 fixture the whole-document request stands on.
WHOLE_UNIT_P4_FIXTURE: int = 11
WHOLE_UNIT_OBSERVATION: Observation = _whole_unit_observation(WHOLE_UNIT_P4_FIXTURE)

#: Fixture number -> the observations a replay must record beyond P4's published set.
#: ONE entry, and it exists because P4 publishes no observation that addresses its own
#: text unit in full. If P4 ever publishes one, this mapping empties and the fixture
#: names it instead.
EXTRA_OBSERVATIONS: Mapping[int, tuple[Observation, ...]] = MappingProxyType({
    5: (WHOLE_UNIT_OBSERVATION,),
})


# --- the injected seams, all three of which enumerate nothing ----------------

def _identifier_classifier(value: str, *, context_before: str | None,
                           context_after: str | None) -> str | None:
    """The injected classifier, as a fixture. SPEC *Deferred* keeps the class opaque:
    "Which identifier classes exist and how each is transformed is not enumerated
    anywhere in the design."

    It returns ONE constant for every value and enumerates nothing. Deliberately not
    value-dependent: a rule that decided a class FROM the value would be a detector,
    which P7 does not own.
    """
    return FIXTURE_IDENTIFIER_CLASS


#: The one opaque class this module's classifier returns. Not a vocabulary.
FIXTURE_IDENTIFIER_CLASS: str = "institution"


def _redaction_transform(value: str, *, identifier_class: str) -> str:
    """The injected transform, also deferred and also enumerating nothing.

    It must not return its input: `apply_redaction` raises `RedactionIneffective` if
    it does, because recording that as `redacted = True` would put a false statement
    in the §8.4 audit record.
    """
    return f"[{identifier_class}]"


def _measure_tokens(request: ModelCallRequest, resolved) -> int:
    """The caller's measurement, as a fixture. `Gate` takes it with a `None` default
    and P7 owns no tokenizer -- SPEC *Deferred*: "Numeric values for every ceiling ...
    Deferred to configuration, not to this contract."

    It counts the characters of what would be sent and calls the count what it is. It
    holds no number and defines no ceiling; the ceiling is P1's, read by
    `over_dossier_ceiling`, and with nothing configured there is nothing to exceed.
    """
    return sum(len(item.value) for item in resolved)


#: The value `_redaction_transform` produces for `FIXTURE_IDENTIFIER_CLASS`, which is
#: what `_measure_tokens` counts and what a released item carries.
REDACTED_VALUE: str = _redaction_transform("", identifier_class=FIXTURE_IDENTIFIER_CLASS)


def gate_arguments(fixture: "GateFixture", *, store: object) -> dict[str, object]:
    """The twelve keywords `Gate(conn, **...)` takes, filled for one fixture.

    Every value is either the fixture's own or a constant this module already
    publishes; nothing here is a rule. `unclassified_permits_local` in particular is
    read off the fixture and has no default anywhere, because SPEC Open question 5 --
    "Does `unreadable_unclassified` permit a LOCAL model call?" -- is unanswered and
    fixtures 17 and 18 are its two branches.

    `scope_for` and `files_in_scope` answer for whatever request the fixture carries,
    so a caller replaying against a real database rebinds the request first and the
    resolvers follow it.
    """
    return {
        "store": store,
        "plan_version": fixture.policy.plan_version,
        "classifier": _identifier_classifier,
        "transform": _redaction_transform,
        "unclassified_permits_local": fixture.unclassified_permits_local,
        "scope_for": lambda _file_id: fixture.area,
        "files_in_scope": lambda _scope: tuple(fixture.request.target.file_ids),
        "component_version": FIXTURE_COMPONENT_VERSION,
        "now": lambda: FIXTURE_CLOCK,
        "user_id": FIXTURE_USER_ID,
        "measure_tokens": _measure_tokens,
        "template_for": lambda _file_id: fixture.residual_template,
    }


# --- the building blocks ----------------------------------------------------

def _policy(mode: str, *, grants: tuple[tuple[str, str], ...] = ()) -> Policy:
    """A policy at `mode`. Every redaction facet is at its more redacting value.

    W1's second half: "Where the design is silent on a redaction default, the more
    redacting option is the default." A fixture that shipped a `shown` facet would be
    publishing a posture §8.4's `must` forbids.

    `policy_version` is `UNSET_POLICY_VERSION`, and that is not a placeholder: the
    gate owns the version and `policy._persist` refuses a caller-supplied one.
    """
    return Policy(
        policy_version=UNSET_POLICY_VERSION, operation_mode=mode,
        consent_grants=grants,
        redaction_settings={"names": "redacted", "previews": "redacted",
                            "thumbnails": "redacted", "ocr_text": "redacted",
                            "location_data": "redacted"},
        automatic_move_permissions={}, plan_version="plan-1",
        set_at=FIXTURE_CLOCK)


def _classified(p4_number: int, handling_class: str, *, protected: bool,
                basis: str = "detector",
                reliability_state: str = "validated") -> ClassificationRecord:
    """A classification over P4 fixture `p4_number`'s bytes.

    `protected` is a PARAMETER here, never derived from `handling_class`. SPEC §2:
    "Neighbouring parts should consume the `protected` flag, not infer it from the
    class", and C5 -- whether `protected` is exactly the top two classes -- is
    unsettled.
    """
    return ClassificationRecord(
        file_id=FIXTURE_FILE_ID, content_hash=_hash(p4_number),
        handling_class=handling_class, protected=protected, basis=basis,
        evidence_refs=(_key(p4_number),) if basis == "detector" else (),
        reliability_state=reliability_state, observed_at=FIXTURE_CLOCK)


def _request(*, stage: str, model_target: ModelTarget, items: tuple,
             fingerprint: str, max_dossier_tokens: int,
             template: str = "tpl.resolve_subject") -> ModelCallRequest:
    return ModelCallRequest(
        stage=stage, target=Target(file_ids=(FIXTURE_FILE_ID,), group_id=None),
        model_target=model_target, requested_items=items,
        prompt_template_id=template, prompt_fingerprint=fingerprint,
        max_dossier_tokens=max_dossier_tokens)


#: Built from `AUDIT_FIELDS` rather than from a literal keyword list. Task 10 owns SPEC
#: §7's names; constructing from the published tuple means a field these fixtures never
#: vary can be respelled without breaking eighteen of them, while a field they DO vary
#: disappearing fails loudly at the seam that cares.
_AUDIT_DEFAULTS: Mapping[str, object] = MappingProxyType({
    "audit_id": None,
    "release_id": None,
    "policy_version": UNSET_POLICY_VERSION,
    "plan_version": "plan-1",
    "stage": "grouping",
    "outcome": "denied",
    "operation_mode": "offline",
    "authorizing_policy": UNSET_POLICY_VERSION,
    "file_sensitivity": "unreadable_unclassified",
    "excerpts_included": (),
    "redaction_applied": False,
    "model": {"locality": "local", "model_id": "local-small", "provider": "local"},
    "content_hashes": (),
    "content_hash": None,
    "prompt_fingerprint": "fp-fixture",
    "file_id": FIXTURE_FILE_ID,
    "file_ids": (FIXTURE_FILE_ID,),
    "group_id": None,
    "observed_at": FIXTURE_CLOCK,
})

_CLOUD_MODEL_MAPPING: Mapping[str, str] = MappingProxyType({
    "locality": "cloud", "model_id": "acme-large", "provider": "Acme"})


def _audit(**over: object) -> AuditRecord:
    """Built from `AUDIT_FIELDS`, never from a literal keyword list."""
    missing = [name for name in AUDIT_FIELDS if name not in _AUDIT_DEFAULTS]
    if missing:
        raise KeyError(
            f"AUDIT_FIELDS names {missing} and this module has no value for them; "
            "SPEC §7 changed and the fixtures need a value, not a default")
    unknown = [name for name in over if name not in _AUDIT_DEFAULTS]
    if unknown:
        raise KeyError(
            f"{unknown} is not an audit field this module knows; a silently dropped "
            "keyword is how a fixture stops carrying the value it claims to carry")
    values = {name: _AUDIT_DEFAULTS[name] for name in AUDIT_FIELDS}
    values.update(over)
    return AuditRecord(**values)


def _cloud_audit(**over: object) -> AuditRecord:
    return _audit(model=dict(_CLOUD_MODEL_MAPPING), **over)


@dataclass(frozen=True)
class GateFixture:
    """One published request -> decision pair, replayable against the real gate.

    Six fields are the plan skeleton's. Eight are added here: `classification`,
    `p4_fixture`, `revoked` and `sensitive_keys` because a fixture that cannot be
    seeded cannot be replayed, and Done-means 11 turns on replay; `area`,
    `unclassified_permits_local` and `residual_template` because Open questions 3 and
    5 and §7.3's unbuilt template library are open, so each answer is DATA the fixture
    supplies to a resolver the gate takes rather than a rule P7 holds; and
    `downstream_obligation` because SPEC §11 puts an obligation on P8 for two of these
    and a comment in P7's source is not a contract P8 can read.

    The last three carry defaults so the fixtures that do not use them state nothing.
    `unclassified_permits_local = False` is the stricter reading and a FIXTURE default
    only -- `Gate` and `unclassified_denies` still have none, and fixtures 17 and 18
    hold both branches.
    """

    number: int
    spec_case: str
    policy: Policy
    classification: ClassificationRecord | None
    area: str | None
    request: ModelCallRequest
    decision: Released | Denied | NeedsConsent
    audit_record: AuditRecord
    p4_fixture: int | None
    downstream_obligation: str | None
    revoked: bool
    #: The observation keys P5 signalled `POTENTIALLY_SENSITIVE` for this file. The
    #: ONLY route to `Denied(always_local_item)` on a constructible item.
    sensitive_keys: tuple[str, ...] = ()
    #: Open question 5's parameter, carried as data. Fixtures 17 and 18 are its two
    #: branches and nothing here names a winner.
    unclassified_permits_local: bool = False
    #: §7.3's residual template for this file, if any. The library is P10's and P11's
    #: and is unbuilt, so `Gate` takes a `template_for` resolver and the fixture
    #: answers it.
    residual_template: str | None = None


def _denied(reason: str, explanation: str, *remedies: RemedyOption,
            evidence_refs: tuple[str, ...] = ()) -> Denied:
    """Every denial goes through `denial.deny`, which validates it.

    §8.6 requires the UI to show "what has been deferred, and why", and a denial whose
    remedy list is empty is a dead end the user cannot act on -- `deny` refuses both.
    """
    return deny(reason, explanation=explanation, remedy_options=remedies,
                evidence_refs=evidence_refs)


_LOCAL_INSTEAD = RemedyOption(
    "use_local_model", "§8.4: a local model is one of the four consent options")
_GRANT_CONSENT = RemedyOption(
    "grant_consent", "§8.4: 'Cloud-assisted mode: User explicitly permits selected "
    "corpus areas to use a cloud model'")
_DECIDE_LOCALLY = RemedyOption(
    "decide_locally", "§7.3: normally local-only; deterministic rules and local "
    "placement still apply")
_REVIEW = RemedyOption(
    "review", "§8.6: the user 'should be able to see what is running, what has been "
    "deferred, and why'")
_CLASSIFY = RemedyOption(
    "classify", "§8.4: the classification 'is itself evidence-backed and can be "
    "revised by the user'")
_CHANGE_MODE = RemedyOption(
    "change_operation_mode", "§8.4's four modes are the user's to choose; the default "
    "is local-first and changing it is an explicit act (W1)")


FIXTURES: tuple[GateFixture, ...] = (
    GateFixture(
        number=1,
        spec_case="Denied.reason = protected_cloud_target (an excerpt)",
        policy=_policy("hybrid", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3), span=_span(3),
                                        reason="resolve the institution"),),
                         fingerprint="fp-01", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4: protected material is not included in cloud-model prompts by "
            "default, and this policy is `hybrid` -- 'Sensitive files remain local; "
            "non-sensitive bounded dossiers may use a cloud LLM.'",
            _LOCAL_INSTEAD, _GRANT_CONSENT,
            evidence_refs=(_key(3),)),
        audit_record=_cloud_audit(file_sensitivity="sensitive_personal",
                                  content_hash=_hash(3), content_hashes=(_hash(3),),
                                  operation_mode="hybrid", prompt_fingerprint="fp-01"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=2,
        spec_case="Denied.reason = unclassified (nothing has looked)",
        policy=_policy("local_model"),
        classification=None,
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-02", max_dossier_tokens=2000),
        decision=_denied(
            "unclassified",
            "§8.4 makes classification a precondition of escalation -- 'classify data "
            "into handling classes before LLM escalation' -- and no classification "
            "exists for this file, and its extraction status is still empty -- "
            "nothing has looked. Absence resolves to `unreadable_unclassified`, "
            "never to `public_low`.",
            _CLASSIFY, _REVIEW),
        audit_record=_audit(stage="fact_resolution", operation_mode="local_model",
                            content_hash=UNEXTRACTED_CONTENT_HASH,
                            content_hashes=(UNEXTRACTED_CONTENT_HASH,),
                            prompt_fingerprint="fp-02"),
        # No P4 substrate on purpose: "nothing has looked" is the whole content of
        # this fixture, and a run would make the gate say something has.
        p4_fixture=None, downstream_obligation=None, revoked=False),
    GateFixture(
        number=3,
        spec_case="Denied.reason = policy_revoked",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "public_low", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(CandidateLabel(label="Columbia"),),
                         fingerprint="fp-03", max_dossier_tokens=2000),
        decision=_denied(
            "policy_revoked",
            "the consent grant authorizing a cloud model for this area was granted "
            "and then withdrawn. §8.4: revocation applies to future runs, so this "
            "call is decided against the policy version in force now.",
            _GRANT_CONSENT, _LOCAL_INSTEAD),
        audit_record=_cloud_audit(file_sensitivity="public_low",
                                  content_hash=_hash(3), content_hashes=(_hash(3),),
                                  operation_mode="cloud_assisted",
                                  prompt_fingerprint="fp-03"),
        p4_fixture=3, downstream_obligation=None, revoked=True),
    GateFixture(
        number=4,
        spec_case="Denied.reason = protected_records_template (the content half)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "highly_sensitive_credential_bearing",
                                   protected=True, basis="safety_domain"),
        area=FIXTURE_AREA,
        request=_request(stage="placement", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3), span=_span(3),
                                        reason="identify the issuing body"),),
                         fingerprint="fp-04", max_dossier_tokens=2000),
        decision=_denied(
            "protected_records_template",
            f"the file is held under the {PROTECTED_RECORDS_TEMPLATE!r} residual "
            "template, which 'must not cause filenames or content to be exposed in "
            "model prompts' (§7.3). That binds every model, so the target does not "
            "change the answer.",
            _DECIDE_LOCALLY, _REVIEW,
            evidence_refs=(_key(3),)),
        audit_record=_cloud_audit(
            stage="placement",
            file_sensitivity="highly_sensitive_credential_bearing",
            content_hash=_hash(3), content_hashes=(_hash(3),),
            operation_mode="cloud_assisted", prompt_fingerprint="fp-04"),
        p4_fixture=3, downstream_obligation=None, revoked=False,
        # The content half is an `Excerpt`, which `check_item` does not refuse -- only
        # `template_for` reaches this denial for it. With the signature's `None`
        # default the branch is unreachable and this fixture releases.
        residual_template=PROTECTED_RECORDS_TEMPLATE),
    GateFixture(
        number=5,
        spec_case="Denied.reason = whole_document_requested",
        policy=_policy("local_model"),
        classification=_classified(WHOLE_UNIT_P4_FIXTURE, "public_low",
                                   protected=False),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(
                             observation_key=WHOLE_UNIT_OBSERVATION.observation_key,
                             span=WHOLE_UNIT_OBSERVATION.location.text_span,
                             reason="read the whole unit"),),
                         fingerprint="fp-05", max_dossier_tokens=20000),
        decision=_denied(
            "whole_document_requested",
            "the requested span covers the whole text unit. §8.4: the engine 'should "
            "not send full documents where a short heading or OCR excerpt is enough "
            "to resolve the question.'",
            RemedyOption("narrow_span",
                         "§8.4's compact dossier is 'selected excerpts' -- a bounded "
                         "span, addressed by (observation_key, span)"),
            evidence_refs=(_key(WHOLE_UNIT_P4_FIXTURE),)),
        audit_record=_audit(stage="fact_resolution", operation_mode="local_model",
                            file_sensitivity="public_low",
                            content_hash=_hash(WHOLE_UNIT_P4_FIXTURE),
                            content_hashes=(_hash(WHOLE_UNIT_P4_FIXTURE),),
                            prompt_fingerprint="fp-05"),
        p4_fixture=WHOLE_UNIT_P4_FIXTURE, downstream_obligation=None, revoked=False),
    GateFixture(
        number=6,
        spec_case="Denied.reason = dossier_over_budget (M9's backstop)",
        policy=_policy("local_model"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3), span=_span(3),
                                        reason="resolve the institution"),),
                         fingerprint="fp-06", max_dossier_tokens=1),
        decision=_denied(
            "dossier_over_budget",
            "the resolved dossier exceeds the `max_dossier_tokens` the caller is "
            "operating under. This is a backstop: §8.6's ladder -- 'summarize "
            "deterministic facts, preserve anchor excerpts, split the task, or defer "
            "the decision' -- runs in P8 before the call (M9).",
            RemedyOption("summarize_deterministic_facts", "§8.6, rung one"),
            RemedyOption("defer_the_decision", "§8.6, rung four"),
            evidence_refs=(_key(3),)),
        audit_record=_audit(stage="fact_resolution", operation_mode="local_model",
                            file_sensitivity="public_low", content_hash=_hash(3),
                            content_hashes=(_hash(3),), prompt_fingerprint="fp-06"),
        p4_fixture=3,
        downstream_obligation=(
            "so P8 can prove its ladder ran first -- a P8 test that reaches this "
            "denial through the normal path is a P8 failure, not a gate result"),
        revoked=False),
    GateFixture(
        number=7,
        spec_case="Denied.reason = always_local_item (a key P5 signalled)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(8, "public_low", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(8), span=_span(8),
                                        reason="read the status banner"),),
                         fingerprint="fp-07", max_dossier_tokens=2000),
        decision=_denied(
            "always_local_item",
            "P5 signalled this observation 'potentially sensitive' at emission, and "
            "§8.4 places 'raw sensitive values' in the always-local set: 'Paths, "
            "complete extracted text, OCR output, file hashes, image EXIF, GPS, user "
            "edits, group memberships, and raw sensitive values should remain local.' "
            "The run is `ocr.apple_vision`, so the value is OCR output as well -- but "
            "the signal is what the gate reads. §8.4 permits 'redacted identifiers', "
            "so the same key is releasable as a RedactedIdentifier.",
            RemedyOption("request_excerpt",
                         "§8.4's compact dossier: 'selected excerpts, redacted "
                         "identifiers, candidate labels, non-sensitive metadata, and "
                         "evidence references'"),
            evidence_refs=(_key(8),)),
        audit_record=_cloud_audit(file_sensitivity="public_low",
                                  content_hash=_hash(8), content_hashes=(_hash(8),),
                                  operation_mode="cloud_assisted",
                                  prompt_fingerprint="fp-07"),
        p4_fixture=8, downstream_obligation=None, revoked=False,
        # The whole fixture turns on this. `check_item` has no zone branch and P4
        # fixture 8's text unit carries `zone = None`, so the earlier "an excerpt in
        # the ocr zone" reading resolved and RELEASED. The replay writes this key as a
        # P5 `POTENTIALLY_SENSITIVE` signal through `record_sensitivity_signals`.
        sensitive_keys=(_key(8),)),
    GateFixture(
        number=8,
        spec_case="Denied.reason = mode_forbids_target (the mode axis, unprotected)",
        policy=_policy("offline"),
        classification=_classified(3, "public_low", protected=False),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(CandidateLabel(label="Columbia"),),
                         fingerprint="fp-08", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's fully offline mode: 'No content leaves the device; only local "
            "rules and local models may run.' The file is neither sensitive nor "
            "protected; the mode alone forbids the target.",
            _LOCAL_INSTEAD, _CHANGE_MODE),
        audit_record=_cloud_audit(file_sensitivity="public_low",
                                  content_hash=_hash(3), content_hashes=(_hash(3),),
                                  operation_mode="offline",
                                  prompt_fingerprint="fp-08"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=9,
        spec_case="a clean `Released` with redaction applied",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "personal_non_sensitive", protected=False),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(Excerpt(observation_key=_key(3), span=_span(3),
                                        reason="resolve the institution"),
                                RedactedIdentifier(
                                    observation_key=_key(3), span=_span(3),
                                    identifier_class=FIXTURE_IDENTIFIER_CLASS),
                                EvidenceReference(observation_key=_key(3))),
                         fingerprint="fp-09", max_dossier_tokens=2000),
        decision=Released(
            release_id=PLACEHOLDER_RELEASE_ID, audit_id=PLACEHOLDER_AUDIT_ID,
            policy_version=PLACEHOLDER_POLICY_VERSION,
            materialised_items=tuple(
                Materialised(observation_key=_key(3), span=_locator(3),
                             value=REDACTED_VALUE, zone=_zone(3),
                             context_before=None, context_after=None,
                             context_truncated=False, unit_length=_unit_length(3))
                for _ in range(2)),
            redaction_manifest=RedactionManifest(entries=tuple(
                RedactionEntry(observation_key=_key(3), span=_locator(3),
                               identifier_class=FIXTURE_IDENTIFIER_CLASS,
                               redacted=True, context_before=None,
                               context_after=None, context_truncated=False)
                for _ in range(2))),
            model_target=CLOUD_MODEL),
        audit_record=_cloud_audit(
            outcome="released", file_sensitivity="personal_non_sensitive",
            content_hash=_hash(3), content_hashes=(_hash(3),),
            operation_mode="cloud_assisted", prompt_fingerprint="fp-09",
            excerpts_included=((_key(3), _locator(3)), (_key(3), _locator(3))),
            redaction_applied=True),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=10,
        spec_case="a `NeedsConsent` returning all four options",
        # NO grant for this area, and the target is LOCAL. Both are forced by the
        # consent branch read together with `protected_cloud_denies`: the branch is
        # `text_items and protected_ids and scope not in granted`, and under
        # `cloud_assisted` `protected_cloud_denies` returns False only when the scope
        # IS granted. So a protected file with a CLOUD target denies before it can
        # ask -- the consent branch is reachable only through a non-cloud target.
        policy=_policy("cloud_assisted"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3), span=_span(3),
                                        reason="the sensitive passage names the "
                                               "institution"),),
                         fingerprint="fp-10", max_dossier_tokens=2000),
        decision=NeedsConsent(
            consent_request_id=PLACEHOLDER_CONSENT_REQUEST_ID,
            requirement=ConsentRequirement(
                file_ids=(FIXTURE_FILE_ID,),
                handling_class="sensitive_personal",
                items=((_key(3), _locator(3)),),
                why="§8.4: this call needs text from files entered into protected "
                    "state, and policy holds no consent grant authorizing a local "
                    f"model for scope {FIXTURE_AREA!r}"),
            options=CONSENT_OPTIONS),
        audit_record=_audit(
            stage="fact_resolution", outcome="consent_requested",
            file_sensitivity="sensitive_personal", content_hash=_hash(3),
            content_hashes=(_hash(3),), operation_mode="cloud_assisted",
            prompt_fingerprint="fp-10"),
        p4_fixture=3,
        downstream_obligation=(
            "so P8 can prove it returns the branch to its caller intact"),
        revoked=False),
    GateFixture(
        number=11,
        spec_case="a protected file under `offline`",
        policy=_policy("offline"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-11", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's fully offline mode: 'No content leaves the device; only local "
            "rules and local models may run.' The mode is evaluated first, because "
            "under `offline` this target is unreachable for every file and naming the "
            "file's protection would be a narrower reason than the true one.",
            _LOCAL_INSTEAD, _CHANGE_MODE),
        audit_record=_cloud_audit(file_sensitivity="sensitive_personal",
                                  content_hash=_hash(3), content_hashes=(_hash(3),),
                                  operation_mode="offline",
                                  prompt_fingerprint="fp-11"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=12,
        spec_case="a protected file under `local_model`",
        policy=_policy("local_model"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=None,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-12", max_dossier_tokens=2000),
        decision=_denied(
            "mode_forbids_target",
            "§8.4's local-model mode: 'Local extraction plus a user-installed local "
            "LLM for eligible dossiers.' No cloud target is reachable under it.",
            _LOCAL_INSTEAD, _CHANGE_MODE),
        audit_record=_cloud_audit(file_sensitivity="sensitive_personal",
                                  content_hash=_hash(3), content_hashes=(_hash(3),),
                                  operation_mode="local_model",
                                  prompt_fingerprint="fp-12"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=13,
        spec_case="a protected file under `hybrid` (a metadata field, not an excerpt)",
        policy=_policy("hybrid", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-13", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4: 'Protected material should not be included in cloud-model prompts "
            "by default.' The sentence names no item kind, so an innocuous metadata "
            "field is refused on the same ground as an excerpt.",
            _LOCAL_INSTEAD, _GRANT_CONSENT,
            evidence_refs=(_key(3),)),
        audit_record=_cloud_audit(file_sensitivity="sensitive_personal",
                                  content_hash=_hash(3), content_hashes=(_hash(3),),
                                  operation_mode="hybrid",
                                  prompt_fingerprint="fp-13"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=14,
        spec_case="a protected file under `cloud_assisted`, with no grant for the area",
        policy=_policy("cloud_assisted"),
        classification=_classified(3, "sensitive_personal", protected=True),
        area=FIXTURE_AREA,
        request=_request(stage="grouping", model_target=CLOUD_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-14", max_dossier_tokens=2000),
        decision=_denied(
            "protected_cloud_target",
            "§8.4's cloud-assisted mode: 'User explicitly permits selected corpus "
            "areas to use a cloud model.' No grant covers this area, and the material "
            "is protected.",
            _GRANT_CONSENT, _LOCAL_INSTEAD,
            evidence_refs=(_key(3),)),
        audit_record=_cloud_audit(file_sensitivity="sensitive_personal",
                                  content_hash=_hash(3), content_hashes=(_hash(3),),
                                  operation_mode="cloud_assisted",
                                  prompt_fingerprint="fp-14"),
        p4_fixture=3, downstream_obligation=None, revoked=False),
    GateFixture(
        number=15,
        spec_case="an `unreadable_unclassified` file (something looked and failed)",
        policy=_policy("local_model"),
        # NOT a stored record with `handling_class = unreadable_unclassified`:
        # `ClassificationStore.write` raises `GateOutcomeNotAFileFact` on exactly that
        # (D2 -- "the absence of a record already says nothing has looked"). What makes
        # this fixture different from fixture 2 is the EXTRACTION: P4 fixture 18's run
        # carries `completeness = 'unreadable'` (§2.9's indexed-but-unreadable case),
        # the replay writes it through P1's `set_extraction_status`, and the gate's
        # explanation names it. Collapsing the two would delete the distinction D2
        # exists to protect; storing the class would break the rule D2 states.
        classification=None,
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(MetadataField(name="file type"),),
                         fingerprint="fp-15", max_dossier_tokens=2000),
        decision=_denied(
            "unclassified",
            "the extraction is §2.9's indexed-but-unreadable case and its "
            "completeness is 'unreadable'. §8.4 makes classification a precondition "
            "of escalation, and §8.6 forbids the alternative: 'Cost exhaustion must "
            "never turn into lower-quality automatic classification.'",
            _REVIEW, _CLASSIFY),
        audit_record=_audit(stage="fact_resolution", operation_mode="local_model",
                            content_hash=_hash(18), content_hashes=(_hash(18),),
                            prompt_fingerprint="fp-15"),
        p4_fixture=18, downstream_obligation=None, revoked=False),
    GateFixture(
        number=16,
        spec_case="a `Protected Records` residual request (the filename half)",
        policy=_policy("cloud_assisted", grants=((FIXTURE_AREA, "cloud_model"),)),
        classification=_classified(3, "highly_sensitive_credential_bearing",
                                   protected=True, basis="safety_domain"),
        area=FIXTURE_AREA,
        request=_request(stage="placement", model_target=CLOUD_MODEL,
                         items=(Filename(file_id=FIXTURE_FILE_ID),),
                         fingerprint="fp-16", max_dossier_tokens=2000),
        decision=_denied(
            "protected_records_template",
            f"the file is held under the {PROTECTED_RECORDS_TEMPLATE!r} residual "
            "template. §7.3 forbids both nouns: it 'must not cause filenames or "
            "content to be exposed in model prompts'.",
            _DECIDE_LOCALLY, _REVIEW),
        audit_record=_cloud_audit(
            stage="placement",
            file_sensitivity="highly_sensitive_credential_bearing",
            content_hash=_hash(3), content_hashes=(_hash(3),),
            operation_mode="cloud_assisted", prompt_fingerprint="fp-16"),
        p4_fixture=3, downstream_obligation=None, revoked=False,
        residual_template=PROTECTED_RECORDS_TEMPLATE),
    GateFixture(
        number=17,
        spec_case="Open question 5, read strictly: a local call on an unclassified "
                  "file is denied",
        policy=_policy("local_model"),
        classification=None,
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3), span=_span(3),
                                        reason="resolve the institution"),),
                         fingerprint="fp-17", max_dossier_tokens=2000),
        decision=_denied(
            "unclassified",
            "§8.4 makes classification a precondition of escalation and this caller "
            "answered Open question 5 strictly: `unclassified_permits_local` is "
            "False, so a LOCAL model call on an unclassified file is denied.",
            _CLASSIFY, _REVIEW),
        audit_record=_audit(stage="fact_resolution", operation_mode="local_model",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-17"),
        p4_fixture=3, downstream_obligation=None, revoked=False,
        unclassified_permits_local=False),
    GateFixture(
        number=18,
        spec_case="Open question 5, read permissively: the same call is released",
        policy=_policy("local_model"),
        classification=None,
        area=None,
        request=_request(stage="fact_resolution", model_target=LOCAL_MODEL,
                         items=(Excerpt(observation_key=_key(3), span=_span(3),
                                        reason="resolve the institution"),),
                         fingerprint="fp-17", max_dossier_tokens=2000),
        decision=Released(
            release_id=PLACEHOLDER_RELEASE_ID, audit_id=PLACEHOLDER_AUDIT_ID,
            policy_version=PLACEHOLDER_POLICY_VERSION,
            materialised_items=(
                Materialised(observation_key=_key(3), span=_locator(3),
                             value=REDACTED_VALUE, zone=_zone(3),
                             context_before=None, context_after=None,
                             context_truncated=False, unit_length=_unit_length(3)),),
            redaction_manifest=RedactionManifest(entries=(
                RedactionEntry(observation_key=_key(3), span=_locator(3),
                               identifier_class=FIXTURE_IDENTIFIER_CLASS,
                               redacted=True, context_before=None, context_after=None,
                               context_truncated=False),)),
            model_target=LOCAL_MODEL),
        audit_record=_audit(stage="fact_resolution", outcome="released",
                            operation_mode="local_model",
                            content_hash=_hash(3), content_hashes=(_hash(3),),
                            prompt_fingerprint="fp-17",
                            excerpts_included=((_key(3), _locator(3)),),
                            redaction_applied=True),
        p4_fixture=3, downstream_obligation=None, revoked=False,
        unclassified_permits_local=True),
)


#: SPEC §11's list, mapped to the fixtures that satisfy it. Thirteen keys: the eight
#: `Denied.reason` values and the five `SPEC_11_ITEMS`. A key with an empty tuple is a
#: §11 item with no fixture, which is the failure this map exists to make visible.
FIXTURE_COVERAGE: Mapping[str, tuple[int, ...]] = MappingProxyType({
    "protected_cloud_target": (1, 13, 14),
    "unclassified": (2, 15, 17),
    "policy_revoked": (3,),
    "protected_records_template": (4, 16),
    "whole_document_requested": (5,),
    "dossier_over_budget": (6,),
    "always_local_item": (7,),
    "mode_forbids_target": (8, 11, 12),
    "a clean `Released` with redaction applied": (9,),
    "a `NeedsConsent` returning all four options": (10,),
    "a protected file under each of the four modes": (11, 12, 13, 14),
    "an `unreadable_unclassified` file": (15,),
    "a `Protected Records` residual request": (4, 16),
})

#: The four-mode sweep, mode -> fixture number. `offline` and `local_model` deny on the
#: mode; `hybrid` and `cloud_assisted` deny on the protection. That difference is the
#: precedence rule, published as data so Task 13 cannot quietly invert it.
MODE_SWEEP: Mapping[str, int] = MappingProxyType({
    "offline": 11,
    "local_model": 12,
    "hybrid": 13,
    "cloud_assisted": 14,
})

#: 11 §9's second fixture path, named as data rather than left to be rediscovered:
#:
#:     P7/P8   a dossier that requires sensitive text
#:             Gate.release returns NeedsConsent
#:             P13 presents the four §8.4 options
#:             choosing no_model_use does not become abstain inside P8
#:
#: 11 §9 also says what kind of test that is -- "a contract test of B2, not an LLM
#: test ... the minimum that makes the one privacy-failure seam exercisable without
#: waiting for full depth". P7 owns the first two lines; the third is P13's and the
#: fourth is P8's Done-means 13.
SKELETON_FIXTURE: int = 10

_BY_NUMBER: Mapping[int, GateFixture] = MappingProxyType(
    {fixture.number: fixture for fixture in FIXTURES})


def by_number(number: int) -> GateFixture:
    """The fixture with this number, or `UnknownFixture`. Never a nearest neighbour."""
    try:
        return _BY_NUMBER[number]
    except KeyError:
        raise UnknownFixture(
            f"P7 publishes no gate fixture {number}; the published numbers are "
            f"{tuple(sorted(_BY_NUMBER))}") from None
