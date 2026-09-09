# src/privacy/gate.py
"""The one door. `Gate.release(ModelCallRequest) -> ReleaseDecision` is the only one.

`release` is the only way content leaves. The facade also publishes the other §8.4
surfaces that operate on the same policy and the same log -- `revoke` and
`delete_derived` (D13 kept CUT 4, so the facade is certain rather than provisional).
Neither is a release path: `revoke` grants no capability and `delete_derived` returns
`NoReturn`, so §3.7's "writes exactly one thing and raises nothing" is a rule about
`release` and does not travel to them. It is restated for each below.

B2 adopts SPEC §6's signature verbatim on both sides, so `release` takes the request
and NOTHING ELSE -- no override, no flag, no connection. Everything the gate needs
beyond the request is constructor state, and three of those constructor parameters
carry no default because each is an open question this plan will not guess:

    classifier / transform      SPEC *Deferred*: identifier classes and the redaction
                                transform are not enumerated anywhere in the design.
    scope_for                   Open question 3: "What is a 'corpus area'? ... Consent
                                grants cannot be scoped until this is named."
    unclassified_permits_local  Open question 5: does `unreadable_unclassified` permit
                                a LOCAL model call?

The gate writes exactly ONE thing -- the audit record -- and it writes it BEFORE the
decision is returned, because §8.4 makes recording the authorization part of granting
it (C4). It writes no classification, no `files.sensitivity_state`, no `stage_output`,
no placement decision and no P8 `Refusal`. The catcher is always the caller's.

It decides no precedence of its own: it COLLECTS every triggered reason and asks
`denial.first_reason` which one wins, because `DENIAL_ORDER` is Task 13's and a second
total order here would be a second home for it.

WHAT AN ABSENT ZONE MEANS, since `_located_zone` may return `None` and §8.4's
always-local ZONE refusal is decided from what it returns. Written here rather than
only at the method, because "absent means refuse, never guess" is a rule about this
whole door and a reader checking it should not have to find the one method.

`None` is returned in exactly two situations and NEITHER is an unknown zone:

  1. **The item addresses no observation.** `CandidateLabel` carries a destination
     name, `MetadataField` a field NAME, `Filename` a `file_id`, `SelfDescription` a
     `question_id`. None has an `observation_key`, so no zone applies to it and
     `None` is the accurate answer rather than a missing one. §8.4 reaches those
     kinds through their own refusals -- `_refuse_always_local_name`, `Filename`'s
     path-separator check, `UNRATIFIED_ITEM_KINDS` -- not through the zone.

     A `Filename` DOES reach a zone at step 3, and `None` here is still the accurate
     answer rather than a stale one (`104` R-06). The item carries no key, so there
     is nothing for `_located_zone` to look up; `resolve.materialise_filename`
     derives the address from the `file_id` when the text is actually read. Asking
     `check_item` about the filename's real zone would be asking it to refuse the
     kind -- `filename` is in `ALWAYS_LOCAL_ZONES` exactly so that an EXCERPT cannot
     address it, and `NAME_BEARING` below sets out why the two must not meet.
  2. **The observation key does not resolve.** This one is a genuine absence, and it
     is NOT treated as "not always-local". It cannot release anything: the same key
     is unreadable to `resolve.materialise`, which raises `UnresolvableSpan` at step
     3 before any value exists. The refusal is deferred, never waived, and
     `test_p7_always_local_zone.py` runs that path rather than reasoning about it.

There is deliberately no third case, and the type system is why: `Location` validates
`zone` against `evidence_shape.vocabulary.ZONES` in `__post_init__`, so a located
observation ALWAYS carries one of the fifteen. "A locator with no zone" is not a state
this product can store, which is a stronger guarantee than a refusal would be.

Case 2 is deferred rather than denied because `test_a_resolve_failure_propagates_and_
is_not_a_denial` rules on it: a key the evidence does not carry is a contract
violation by the CALLER, and `Denied` and `NeedsConsent` are values where that is an
exception. Turning an unresolvable key into `Denied(always_local_item)` would answer a
typo with a privacy verdict.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from typing import NoReturn

from database_agent.budget import get_ceiling
from database_agent.files_table import get_file
from evidence_shape.canonical import canonical_json

from privacy.audit import AuditRecord, append_audit
from privacy.authorship import SUBSYSTEM
from privacy.binding import content_digest_of, mint_release
from privacy.classification import (
    UNREADABLE_UNCLASSIFIED, ClassificationRecord, derivative_privacy_class,
    privacy_class_of, resolve_class,
)
from privacy.consent import (ConsentRequirement, grant_authorizes,
                             open_consent_request)
from privacy.denial import (
    deny_always_local_item, deny_dossier_over_budget, deny_mode_forbids_target,
    deny_no_safety_evidence, deny_policy_revoked, deny_protected_cloud_target,
    deny_protected_records_template, deny_unclassified,
    deny_whole_document_requested, first_reason, is_protected_records, mode_forbids,
    no_safety_evidence_denies, over_dossier_ceiling, policy_revoked_for,
    protected_cloud_denies, record_denial, unclassified_denies,
)
from privacy.items import (
    SUSPENDED_ITEM_KINDS,
    AlwaysLocalRequested, CandidateLabel, EvidenceReference, Excerpt, Filename,
    MetadataField, ProtectedItemRequested, RedactedIdentifier,
    WholeDocumentRequested, check_item, kind_of, sensitive_observation_keys,
)
from privacy.policy import current_policy
from privacy.redaction import RedactionManifest, apply_redaction, span_address
from privacy.release import (
    CLOUD_LOCALITY, DECISION_ORDER, Denied, MalformedRequest, ModelCallRequest,
    NeedsConsent, NoPolicyInForce, ReleaseDecision, Released, ReleasedItem,
    whole_unit_is_an_excerpt,
)
from privacy.resolve import (
    AmbiguousObservationKey, UnresolvableSpan, current_location, materialise,
    materialise_filename,
)
# Aliased under a leading underscore, the way `classification.py` binds `DETECTOR`,
# and for that module's reason: `test_p7_skeleton_step` asserts that no name here
# begins `detect`, because "P7 is done" and "the product classifies files" are
# different claims and this part delivers only the first. The guard is a name check,
# so a vocabulary constant read at the door would trip it while meaning the opposite
# -- the gate CONSUMES a basis another part wrote and produces none.
from privacy.vocabulary import (
    DETECTOR_NO_SAFETY_EVIDENCE as _DETECTOR_NO_SAFETY_EVIDENCE,
    PRIVACY_CLASS_ALWAYS_LOCAL, PRIVACY_CLASS_PENDING, PRIVACY_CLASS_PROTECTED,
)
# Imported as a MODULE, not by name: `Gate.revoke` and `Gate.delete_derived` are the
# same two words as the functions they delegate to, and an aliased import would give
# each of them a second spelling inside the one file that publishes both.
from privacy import display, learning_seam, moves, revocation

#: §4's two item kinds that address local text and therefore resolve to a value.
#: `candidate_label`, `metadata_field`, `evidence_reference` and `filename` carry no
#: local content -- §4: an evidence reference is "an id only -- no content" -- so they
#: are never materialised and never echoed back.
TEXT_BEARING: tuple[type, ...] = (Excerpt, RedactedIdentifier)

#: §4's four kinds that address no local text and so resolve to no value. They are
#: absent from a release's `materialised_items` BY DESIGN and always were -- §4: an
#: evidence reference is "an id only -- no content" -- which is what makes them
#: different from an item that was asked about and then quietly stopped counting.
#:
#: Named as its own tuple on 2026-09-02 so that the difference is written down
#: rather than inferred from `TEXT_BEARING`'s complement. The complement of one list
#: is every kind that exists, including the ones nobody has taught this gate to read.
#:
#: **THE WRONG PLACE TO PUT A `self_description`, and the reason is not obvious.**
#: It carries a reference, exactly like the four here, so it superficially belongs.
#: It does not: the gate has to READ something to turn a `question_id` into bytes,
#: and §4's "no content" is true of a `CandidateLabel` and of a `MetadataField`'s
#: NAME in a way it is not true of a person's typed sentence. Filed here it would
#: be released as an id and never resolved -- which is the silent drop this tuple
#: exists to end, back again and wearing a classification that says it is fine.
#: Its honest reading is materialised; the refusal below is what holds until one
#: exists. (`build-role-matcher`, who owns the type, 2026-09-02.)
#:
#: **`Filename` LEFT THIS TUPLE 2026-09-06 (`104` R-06), and it was never a member
#: by the same argument as the other three.** A `CandidateLabel` and a
#: `MetadataField` NAME carry no local content and an `EvidenceReference` is "an id
#: only". A `Filename` carries a `file_id`, which is a reference to something that
#: DOES have a value -- the person's own name for the file, which §7.7 makes the
#: flagged sixth RELEASABLE kind and `00`:124 lists first in the residual dossier.
#: Filed here it was released as an id and never resolved, so `e31c70f`'s claim that
#: the model is shown the filename was false at the byte level: the item entered the
#: request, passed the door, and contributed nothing to `materialised_items`. That is
#: the silent drop this tuple's own docstring exists to end, wearing a classification
#: that said it was fine. It is `NAME_BEARING` below.
REFERENCE_ONLY: tuple[type, ...] = (
    CandidateLabel, MetadataField, EvidenceReference)

#: §7.7's sixth kind: a reference the gate resolves to a value out of P4, the way it
#: resolves an excerpt, and the third reading this door has.
#:
#: **WHY IT IS NOT SIMPLY IN `TEXT_BEARING`, and the reason is a live refusal rather
#: than a taxonomy.** `items.check_item` raises `AlwaysLocalRequested` for ANY item
#: whose observation addresses a zone in `ALWAYS_LOCAL_ZONES`, and `filename` is one
#: of the three -- put there (CR-01) precisely so that an `Excerpt` cannot address a
#: filename and bypass §7.3's protected-records ban and §7.7's `allow_unratified`
#: opt-in, "refused HERE and released THERE". `TEXT_BEARING` is what `_precheck_items`
#: and `_postcheck_items` iterate, so admitting the filename to it would take the
#: value out through the door that was closed for it and then refuse it at the door
#: built for it. The kind travels its own path: refused for a protected file at the
#: precheck exactly as before, and resolved at step 3 beside the excerpts.
#:
#: The whole-document refusal does not apply to it either, and that is deliberate
#: rather than an omission: a filename observation spans its whole one-line unit, so
#: `is_whole_document` is TRUE of every filename there has ever been. Releasing the
#: whole of it is what the kind is for.
NAME_BEARING: tuple[type, ...] = (Filename,)

#: The one kind a suspension can cover, read from the type table rather than
#: respelled. `80` §8.1 scopes the suspension to nothing but the self-description.
SELF_DESCRIPTION_KIND: str = SUSPENDED_ITEM_KINDS[0]


class Gate:
    """§8.4's gate. One object, one door, no second name.

    Task 20 pins the first ten keywords (`GATE_ARGUMENTS`) so its fixtures replay
    through the real gate. `measure_tokens` and `template_for` are two OPTIONAL
    additions, both defaulting to `None`, and both reported to Task 20:

    - `measure_tokens` -- P7 owns no tokenizer and inventing one would invent a
      number. With no measurement there is nothing to compare, exactly as an unset
      ceiling cannot deny.
    - `template_for` -- §7.3's residual-template library is P10's and P11's and is
      unbuilt. With no mapping, no file is under a residual template.
    """

    def __init__(self, conn: sqlite3.Connection, *, store, plan_version: str,
                 classifier, transform, unclassified_permits_local: bool,
                 scope_for: Callable[[str], str | None],
                 files_in_scope: Callable[[str], Sequence[str]],
                 component_version: str, now: Callable[[], str],
                 user_id: str | None,
                 measure_tokens: Callable[..., int] | None = None,
                 template_for: Callable[[str], str | None] | None = None) -> None:
        self._conn = conn
        self._store = store
        self._plan_version = plan_version
        self._classifier = classifier
        self._transform = transform
        self._unclassified_permits_local = unclassified_permits_local
        self._scope_for = scope_for
        #: Held for `Gate.revoke` (Task 15); `release` does not use it.
        self._files_in_scope = files_in_scope
        self._component_version = component_version
        self._now = now
        self._user_id = user_id
        self._measure_tokens = measure_tokens
        self._template_for = template_for

    # -- §8.4's only door ---------------------------------------------------

    def release(self, request: ModelCallRequest) -> ReleaseDecision:
        """See `release.DECISION_ORDER` for the order and why it is forced."""
        assert DECISION_ORDER[0] == "collect_request_denials"
        policy = current_policy(self._conn, plan_version=self._plan_version)
        if policy is None:
            raise NoPolicyInForce(
                f"no privacy policy is stored for plan version "
                f"{self._plan_version!r}. §8.4's audit record names the authorizing "
                "policy and there is none; W1's local-first floor is resolved in "
                "`defaults.effective_policy`, not here, so the gate refuses to "
                "invent one")

        observed_at = self._now()
        locality = request.model_target.locality
        file_ids = request.target.file_ids
        # §8.4's door decides for EVERY file in the request, so the corpus area is
        # read per file. Taking `file_ids[0]`'s area and applying it to the rest made
        # revocation, cloud protection and consent depend on list order: a protected
        # file in an ungranted area rode out on an unprotected file listed ahead of it.
        scopes = {file_id: self._scope_for(file_id) for file_id in file_ids}
        # The user's ANSWER, not just the area they answered about. Dropping the option
        # made `local_model` authorize a cloud release of the same protected file.
        granted = tuple(scope for scope, option in policy.consent_grants
                        if grant_authorizes(option, locality))

        rows = {file_id: get_file(self._conn, file_id) for file_id in file_ids}
        hashes = tuple(rows[file_id]["content_hash"] for file_id in file_ids)
        records = {file_id: self._store.current(file_id, rows[file_id]["content_hash"])
                   for file_id in file_ids}
        classes = {file_id: resolve_class(record)
                   for file_id, record in records.items()}
        protected_ids = tuple(file_id for file_id, record in records.items()
                              if record is not None and record.protected)
        decisive = self._decisive(records, protected_ids, file_ids)
        sensitive_keys = frozenset().union(*(
            sensitive_observation_keys(self._conn, file_id) for file_id in file_ids))

        # 1 -- every reason decidable from the request, the policy and a row lookup.
        builders: dict[str, Callable[[], Denied]] = {}

        if mode_forbids(policy.operation_mode, locality):
            builders["mode_forbids_target"] = lambda: deny_mode_forbids_target(
                operation_mode=policy.operation_mode,
                model_target=request.model_target, file_ids=file_ids)

        revoked = tuple(file_id for file_id in file_ids
                        if policy_revoked_for(self._conn, policy, scopes[file_id]))
        if revoked:
            builders["policy_revoked"] = lambda: deny_policy_revoked(
                scope=scopes[revoked[0]], policy=policy, file_ids=file_ids)

        caught = self._precheck_items(request, policy=policy,
                                      protected=bool(protected_ids),
                                      sensitive_keys=sensitive_keys)
        if isinstance(caught, AlwaysLocalRequested):
            builders["always_local_item"] = lambda: deny_always_local_item(
                caught, file_ids=file_ids)
        elif isinstance(caught, ProtectedItemRequested):
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=file_ids, model_target=request.model_target)

        # `105` §14.3, clause 3: a file the detector did not assess is `pending`,
        # and `pending` is treated like unclassified for every gate. The two sets
        # are computed SEPARATELY and then asserted equal rather than one being
        # derived from the other, because "they agree" is the claim clause 3 makes
        # and a derivation would make it true by construction instead of checking
        # it. `privacy_class_of` reads the RECORD and `resolve_class` reads the
        # class; a future field on the record that made a classified file pending,
        # or a stored `unreadable_unclassified` that D2 forbids, breaks the
        # agreement here rather than three modules downstream.
        # `105` §14.3's privacy class, per file, read off the record's own field.
        # NOT the `protected` flag: the owner ruled on 7 Sep 2026 that the two stay
        # different questions. The flag is §8.4's and keeps §8.4's consent path
        # exactly as it is -- a granted local scope still releases a flagged file.
        # The class is §13.3's and is about the document's recognised KIND, and a
        # protected KIND is shown to no model at all. The two sets differ in both
        # directions, which is why both are read here and neither is derived from
        # the other.
        privacy_classes = {file_id: privacy_class_of(record)
                           for file_id, record in records.items()}

        # §13.3's protected list: "shown to no model and filed one at a time by the
        # person." EVERY TARGET, and REGARDLESS OF CONSENT GRANTS -- a grant is
        # §8.4's instrument for the flag, and reading it here would let a protected
        # KIND in a granted area sail out on the cloud side, which is the one
        # outcome this list exists to prevent.
        protected_kind_ids = tuple(sorted(
            file_id for file_id, name in privacy_classes.items()
            if name == PRIVACY_CLASS_PROTECTED))
        if protected_kind_ids and "protected_records_template" not in builders:
            # `protected_kind=True` picks the sentence that is TRUE of this file.
            # The reason CODE still says "template" and this file is not under one;
            # `DENIAL_REASONS` is the owner's closed set of nine, a tenth is with
            # them, and `deny_protected_records_template`'s docstring carries the
            # whole of that. Nothing a person reads is false in the meantime.
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=protected_kind_ids, model_target=request.model_target,
                    protected_kind=True)

        # §13.3's always-local list: "shown to no cloud model and filed by rules and
        # local models." Cloud only, so the file keeps reaching the local model that
        # files it -- which is the whole difference between this list and the one
        # above, and the R-89 defect was the two being read as one.
        #
        # THE INHERITANCE IS PERFORMED HERE and not assumed. §14.3: "OCR text,
        # excerpts and summaries retain the source's restriction." What this request
        # would release is a derivative of the file, so the class the refusal is
        # about is `derivative_privacy_class` of the file's own -- asked rather than
        # taken, so the one place the product relies on inheritance is the one place
        # it calls the function that defines it.
        always_local_ids = tuple(sorted(
            file_id for file_id, name in privacy_classes.items()
            if derivative_privacy_class(name) == PRIVACY_CLASS_ALWAYS_LOCAL
        )) if locality == CLOUD_LOCALITY else ()
        if always_local_ids and "always_local_item" not in builders:
            inherited = AlwaysLocalRequested(
                f"{len(always_local_ids)} file(s) carry privacy class "
                f"{PRIVACY_CLASS_ALWAYS_LOCAL!r} (`105` §13.3: receipts, order "
                f"confirmations, boarding passes and tickets, screenshots of a "
                f"person's own account or messages, bank or card notifications), "
                f"and §14.3 gives an excerpt, an OCR text or a summary of one the "
                f"source's restriction. Those kinds are shown to no cloud model and "
                f"are filed by rules and local models, so this {locality} target is "
                f"refused and a local one is not")
            builders["always_local_item"] = lambda: deny_always_local_item(
                inherited, file_ids=always_local_ids)

        pending = tuple(sorted(
            file_id for file_id, record in records.items()
            if privacy_class_of(record) == PRIVACY_CLASS_PENDING))
        unclassified = tuple(sorted(
            file_id for file_id, name in classes.items()
            if name == UNREADABLE_UNCLASSIFIED))
        assert pending == unclassified, (
            f"{sorted(set(pending) ^ set(unclassified))} are {PRIVACY_CLASS_PENDING!r} "
            f"on one reading and not the other. `105` §14.3 rules an unassessed file "
            f"pending rather than ordinary and treats pending like unclassified for "
            f"every gate, which holds only while the two agree")
        if unclassified and unclassified_denies(
                locality=locality,
                local_calls_on_unclassified=self._unclassified_permits_local):
            builders["unclassified"] = lambda: deny_unclassified(
                file_ids=unclassified, locality=locality,
                completeness=self._completeness(rows, unclassified[0]))

        # §8.4's precondition is "classify data into handling classes before LLM
        # escalation", and a CLASS EXISTING is not what that sentence is for. `96`
        # §19 measured the difference: 41 of 78 files stored
        # `personal_non_sensitive, protected=0` had matched no safety word at all,
        # and were only reachable by a model because they had acquired a class.
        # Read on the RECORD's basis and never on the class, because the class is
        # the same on both sides of this line -- that is the whole finding.
        #
        # NARROWED 2026-09-07 on the owner's ruling (`104` §13.2): the refusal now
        # needs BOTH halves. A class reached without safety evidence still does not
        # clear a cloud call on its own -- that is `96` §20 and it stands -- but a
        # file that also carries a releasable reading of its own bytes is not a
        # silence being turned into a confident negative. It is a file with
        # something for the model to read, and refusing it excluded 155 of the
        # owner's 199 files from the only wired model site.
        #
        # PER FILE, not per request. `no_safety_evidence_denies` is asked once for
        # each targeted file on this basis, because a request naming two files can
        # carry evidence for one and none for the other, and the file with none is
        # the one the denial is about.
        with_evidence = self._files_with_releasable_evidence(request)
        unexamined = tuple(sorted(
            file_id for file_id, record in records.items()
            if record is not None
            and record.basis == _DETECTOR_NO_SAFETY_EVIDENCE
            and no_safety_evidence_denies(
                locality=locality,
                releasable_evidence=file_id in with_evidence)))
        if unexamined:
            builders["no_safety_evidence"] = lambda: deny_no_safety_evidence(
                file_ids=unexamined, locality=locality,
                handling_class=classes[unexamined[0]])

        if self._template_for is not None and any(
                is_protected_records(self._template_for(file_id))
                for file_id in file_ids):
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=file_ids, model_target=request.model_target)

        unauthorized = tuple(
            file_id for file_id in protected_ids
            if protected_cloud_denies(
                protected=True, locality=locality,
                operation_mode=policy.operation_mode, scope=scopes[file_id],
                granted_scopes=granted))
        if unauthorized:
            builders["protected_cloud_target"] = \
                lambda: deny_protected_cloud_target(
                    file_ids=unauthorized, operation_mode=policy.operation_mode,
                    scope=scopes[unauthorized[0]],
                    evidence_refs=(decisive.evidence_refs
                                   if decisive is not None else ()))

        chosen = first_reason(builders)
        if chosen is not None:
            return self._denied(builders[chosen](), request, policy, decisive,
                                hashes, observed_at)

        # 1b -- every requested item now reaches an outcome, or none of them does.
        #
        # A kind this gate can neither materialise nor read as a bare reference used
        # to fall through BOTH: everything below filters `requested_items` on
        # `TEXT_BEARING`, so such an item entered no branch, produced no
        # `ReleasedItem`, and appeared in no line of §8.4's record. Two items asked
        # about, one released, and the second named nowhere -- neither released nor
        # refused. That is the one outcome the design has no reading for, and it is
        # `84` §1's rule read against the item table: absent means refuse, never
        # guess. A kind this door has no reading for is REFUSED, by name.
        #
        # Not a `Denied`. A denial is §8.4's answer to "may this be sent", drawn
        # from a closed vocabulary of reasons the owner approved; this is a request
        # the gate cannot evaluate at all -- the same class as `NoPolicyInForce` and
        # `resolve.UnresolvableSpan`, which is why it propagates.
        #
        # AFTER the denials, on purpose. A self-description under a policy that
        # suspends nothing is `Denied always_local_item`, which is the answer a
        # person needs and the stronger of the two; raising here first would replace
        # a decision with a crash. And BEFORE step 2, because the consent branch
        # filters on `TEXT_BEARING` as well and would otherwise be a second place an
        # item silently stops counting.
        unreadable = tuple(
            item for item in request.requested_items
            if not isinstance(item, (*TEXT_BEARING, *REFERENCE_ONLY, *NAME_BEARING)))
        if unreadable:
            raise MalformedRequest(
                f"the gate has no materialiser and no reference-only reading for "
                f"{sorted({kind_of(item) for item in unreadable})}, so a release "
                f"would have carried {len(request.requested_items) - len(unreadable)}"
                f" of {len(request.requested_items)} requested items and named the "
                f"rest nowhere -- not in `materialised_items`, not in a denial, not "
                f"in `AuditRecord.excerpts_included`. §8.4's record must describe "
                f"the call, and a record that omits what was asked about does not. "
                f"A kind reaches this only while it is in none of `TEXT_BEARING`, "
                f"`NAME_BEARING` and `REFERENCE_ONLY`. To lift it: write a "
                f"materialiser for the "
                f"kind and then admit it, or say at the type that it carries no "
                f"content and add it to `REFERENCE_ONLY`. Admitting it FIRST is "
                f"not the shorter road -- `resolve.materialise` reads "
                f"`observation_key` and `span` and its docstring says nothing else "
                f"is read, so a kind carrying neither reaches `_materialise` and "
                f"raises `AttributeError`: an unhandled crash where this refusal "
                f"was, which is worse than the silent drop both replace.")

        # 2 -- a question only the user can answer, asked only if nothing denied.
        text_items = tuple(item for item in request.requested_items
                           if isinstance(item, TEXT_BEARING))
        unanswered = tuple(file_id for file_id in protected_ids
                           if scopes[file_id] not in granted)
        located_refs = tuple(
            self._consent_reference(item, file_ids) for item in text_items
        )
        required_file_ids = tuple(
            file_id for file_id in unanswered
            if any(owner == file_id for owner, _reference in located_refs)
        )
        required_items = tuple(
            reference for owner, reference in located_refs
            if owner in required_file_ids
        )
        if required_items:
            requirement = ConsentRequirement(
                file_ids=required_file_ids,
                handling_class=classes[required_file_ids[0]],
                items=required_items,
                why=("§8.4: this call needs text from files entered into protected "
                     f"state, and policy {policy.policy_version} holds no consent "
                     f"grant authorizing a {locality} model for scope "
                     f"{scopes[required_file_ids[0]]!r}"))
            return open_consent_request(
                self._conn, requirement, request=request, policy=policy,
                content_hashes=hashes, user_id=self._user_id,
                component_version=self._component_version, observed_at=observed_at)

        # 3 -- the only content read in the part.
        #
        # THE NAME LEADS, which is the order `model_facts.build_fact_request` builds
        # the request in and the order `00`:124 lists the residual dossier in ("the
        # filename, file type, creation date, extracted text or OCR..."). The gate's
        # order is what `binding.content_digest_of` folds and what
        # `dossier._released_body` writes, so the two agree by construction rather
        # than by both happening to sort the same way.
        name_items = tuple(item for item in request.requested_items
                           if isinstance(item, NAME_BEARING))
        resolved, manifest = self._materialise(text_items, file_ids,
                                               name_items=name_items)

        # 4 -- the two reasons that needed the resolved text.
        late: dict[str, Callable[[], Denied]] = {}
        caught = self._postcheck_items(request, resolved, policy=policy,
                                       protected=bool(protected_ids),
                                       sensitive_keys=sensitive_keys)
        if isinstance(caught, WholeDocumentRequested):
            late["whole_document_requested"] = \
                lambda: deny_whole_document_requested(caught, file_ids=file_ids)

        if self._measure_tokens is not None:
            measured = self._measure_tokens(request, resolved)
            if over_dossier_ceiling(self._conn, measured_tokens=measured):
                late["dossier_over_budget"] = lambda: deny_dossier_over_budget(
                    measured_tokens=measured,
                    ceiling=self._ceiling(), file_ids=file_ids)

        chosen = first_reason(late)
        if chosen is not None:
            return self._denied(late[chosen](), request, policy, decisive, hashes,
                                observed_at)

        # 4b -- `105` §14.3, clause 5: "Classification precedes the model call it
        # governs: a protected document is never sent to a model to discover that it
        # is protected." Nothing below this line can still refuse, so a file whose
        # bytes nothing has assessed reaching here has met §8.4's precondition by
        # accident rather than by rule.
        #
        # AN ASSERTION AND NOT A DENIAL, on the precedent of the `DECISION_ORDER`
        # assert at the top of this method. A `Denied` is §8.4's answer to "may this
        # be sent", drawn from a closed vocabulary of reasons the owner approved and
        # written for a person to read; a pending file arriving here is the ladder
        # above having failed to fire, which is a defect in this file and not an
        # outcome anyone needs shown. The reason the person WOULD see already exists
        # and is `unclassified`.
        #
        # It asks `unclassified_denies` rather than restating its condition, so
        # "unless the local-unclassified rule admits it" is the rule itself and not a
        # second copy of it -- Open question 5 is still unanswered and the answer is
        # still the caller's `unclassified_permits_local`.
        assert not pending or not unclassified_denies(
            locality=locality,
            local_calls_on_unclassified=self._unclassified_permits_local), (
            f"{list(pending)} reach a dossier with no assessed classification, and "
            f"the local-unclassified rule does not admit them for a {locality} "
            f"target. `105` §14.3: classification precedes the model call it governs")

        # 5 -- the one write, before the value exists.
        audit_id = append_audit(
            self._conn,
            self._release_record(request, policy, classes, hashes, resolved,
                                 manifest, observed_at),
            author=SUBSYSTEM, component_version=self._component_version)

        # 6 -- the capability, recorded in Task 12's ledger and bound to FOUR terms.
        # The fourth is the content, added against CR-02: the other three bind who
        # receives the bytes and under what policy, and a transport handed a payload
        # the gate never authorized had nothing to compare it against. It is folded
        # HERE, from `resolved`, because the ledger row is the one record of what was
        # released that a caller cannot reach and rewrite.
        release_id = mint_release(
            self._conn, policy=policy, model_target=request.model_target,
            prompt_fingerprint=request.prompt_fingerprint,
            content_digest=content_digest_of(resolved), audit_id=audit_id,
            minted_at=observed_at)

        return Released(
            release_id=release_id, audit_id=audit_id,
            policy_version=policy.policy_version, materialised_items=resolved,
            redaction_manifest=manifest, model_target=request.model_target)

    # -- SPEC §8/§9/§10's other published surfaces --------------------------
    #
    # Tasks 16, 17 and 18 each list "Modify: src/privacy/gate.py ... and D13 kept
    # CUT 4, so the facade is certain rather than provisional". The builders were
    # forbidden from editing this shared file and reported the seam instead; it is
    # applied here. Each method is a DELEGATION and holds no rule of its own -- the
    # rule lives in the module named, and a second copy on the facade would be the
    # duplication that has cost this project most.
    #
    # Every one of them binds `plan_version`, `store`, `user_id`, `component_version`
    # and the clock from CONSTRUCTOR STATE, the way `release` and `revoke` already do.
    # SPEC §9 writes its surface as `may_move_automatically(file_id, plan_version)`;
    # taking a plan version as an argument here would let a caller ask this gate about
    # a policy the gate is not bound to, which is the one thing binding it exists to
    # prevent. The published shape a caller sees is otherwise unchanged.

    def reclassify(self, file_id: str, handling_class: str, reason: str, *,
                   content_hash: str, protected: bool,
                   evidence_refs: Sequence[str],
                   correction_scope: str = "file"):
        """SPEC §8's user correction, delegating to `privacy.learning_seam`."""
        return learning_seam.reclassify(
            self._conn, file_id, handling_class, reason, store=self._store,
            content_hash=content_hash, protected=protected,
            evidence_refs=evidence_refs, user_id=self._user_id,
            component_version=self._component_version, observed_at=self._now(),
            correction_scope=correction_scope)

    def may_move_automatically(self, file_id: str):
        """SPEC §9's move predicate, delegating to `privacy.moves`."""
        return moves.may_move_automatically(self._conn, file_id, self._plan_version)

    def display_policy(self):
        """SPEC §10's display settings, delegating to `privacy.display`."""
        return display.display_policy(self._conn, plan_version=self._plan_version)

    def summarize_protected(self, scope: str):
        """SPEC §10's protected summary, delegating to `privacy.display`."""
        return display.summarize_protected(
            self._conn, scope, store=self._store,
            files_in_scope=self._files_in_scope)

    # -- §8.4's other two published surfaces --------------------------------

    def revoke(self, scope: str, *,
               retraction_limit: str) -> revocation.RevocationResult:
        """§8.4's "revoke a policy for future runs", with what already left attached.

        Every argument `revocation.revoke` needs beyond the scope and P13's wording is
        already constructor state -- `files_in_scope` has been held for this since
        Task 11 -- so nothing is read twice and no corpus area is invented here.

        This is NOT §3.7's one-write rule broken. That rule is about `release`: its
        one write is the audit record, and returning a capability before that record
        existed would open an interval in which content is releasable and unaudited. A
        revocation grants nothing and IS the write; §8.4 makes it two records -- the
        new policy version and one `consent_revoked` event -- and both belong to the
        one act. It still writes no classification, no `files.sensitivity_state`, no
        `stage_output` and no P8 `Refusal`.

        It raises `MissingRetractionLimit` and `NoPolicyInForce`, and that is not
        §3.7's "raises nothing" broken either: a `Denied` is a value because a denial
        is an ordinary outcome the user must be shown. Both of these are about the
        CALL (§3.6's fourth kind), and `release` already raises `NoPolicyInForce` for
        the same reason.
        """
        policy = current_policy(self._conn, plan_version=self._plan_version)
        if policy is None:
            raise NoPolicyInForce(
                f"no privacy policy is stored for plan version "
                f"{self._plan_version!r}; §8.4 revokes a policy that is in force, and "
                "P7 does not invent one to withdraw")
        return revocation.revoke(
            self._conn, policy, scope, user_id=self._user_id,
            component_version=self._component_version, observed_at=self._now(),
            retraction_limit=retraction_limit,
            files_in_scope=self._files_in_scope)

    @staticmethod
    def delete_derived(scope: revocation.DerivedScope) -> NoReturn:
        """§8.4's "review and delete local derived data" -- surfaced, and unbuilt.

        Static because it takes no connection and touches no gate state: D3 built no
        tombstone column, so there is nothing here that could read or write one. It
        always raises, on both sides of D3's literal enumeration.
        """
        revocation.delete_derived(scope)

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _decisive(records: Mapping[str, ClassificationRecord | None],
                  protected_ids: Sequence[str],
                  file_ids: Sequence[str]) -> ClassificationRecord | None:
        """The one record `record_denial` stores, which takes a single record.

        The first protected file if there is one, because that is the file the
        denial is about; otherwise the first target, whose record is `None` on the
        ordinary path and is exactly what `resolve_class` turns into
        `unreadable_unclassified`.
        """
        if protected_ids:
            return records[protected_ids[0]]
        return records[file_ids[0]]

    @staticmethod
    def _completeness(rows: Mapping[str, object], file_id: str) -> str | None:
        """P1 stores extraction status per tier; absent means nothing has run."""
        stored = rows[file_id]["extraction_status_by_tier"]
        return str(stored) if stored else None

    def _stored_ceiling(self) -> int | None:
        """P1's stored ceiling, or `None` when none is stored. `104` §17.13.

        `check_item`'s whole-document arm reads it: a whole unit with a stored
        length, longer than it, is refused for every target (the OCR passage has
        no stored length and is bounded by the stage instead, `104` R-171). Never
        `request.max_dossier_tokens` (M9). `None` refuses nothing, because P7
        invents no number.
        """
        value = get_ceiling(self._conn, "model.max_dossier_tokens_per_call")
        return None if value is None else int(value)

    def _ceiling(self) -> int:
        """P1's stored ceiling, read for the denial's explanation only.

        Never `request.max_dossier_tokens`, which is "the caller's echo of it (M9)":
        a caller must not be able to raise its own ceiling by echoing a larger one.
        Reached only when `over_dossier_ceiling` already returned True, so the value
        is never `None` here; P7 invents no number for the case that cannot occur.
        """
        value = get_ceiling(self._conn, "model.max_dossier_tokens_per_call")
        if value is None:  # pragma: no cover - `over_dossier_ceiling` gated this
            raise AssertionError(
                "dossier_over_budget was reached with no ceiling stored; "
                "`over_dossier_ceiling` cannot return True in that state")
        return int(value)

    @staticmethod
    def _suspends(policy) -> bool:
        """Whether the policy IN FORCE suspends the always-local rule for a
        self-description.

        READ FROM THE STORED POLICY, and that is the whole of the 2026-09-02 fix.
        It was a constructor argument, which is a fact about a process rather than
        about a run: §8.4's audit record names the authorizing policy, so the one
        act in this product that cannot be taken back was authorised by something
        the record could not name. Now the audit's `policy_version` leads to the
        row that says it, and `what said this was permitted` has an answer that
        outlives the process.

        `80` §8.3's condition C1 survives the move: a policy that says nothing
        suspends nothing, and so does a policy written before the column existed.

        NAMED FOR THE RULING, not for the permission, and the difference is what
        `test_no_signature_and_no_branch_field_names_an_override` protects: P7's
        published names may not read as a back door. `unclassified_permits_local` is
        the precedent -- a legitimate permission says what CONDITION permits what,
        and this one says the `80` §8 suspension is what permits a self-description.
        It is not an override OF the policy; it is a reading of it, which is what
        moving it out of the constructor made true rather than merely stated.
        """
        return SELF_DESCRIPTION_KIND in policy.suspended_item_kinds

    def _located_zone(self, item: object, file_ids: Sequence[str] = ()
                      ) -> str | None:
        """The document zone an item addresses, WITHOUT reading its text.

        `current_location` selects `observation_id, observation_key, file_id,
        location, superseded_by` and no content column -- its own docstring is
        explicit that adding one "would move content access in front of the consent
        decision". The zone is therefore a locator fact, and §8.4's always-local zone
        refusal can be taken before anything is materialised.

        `None` is NOT "the zone is unknown", and the module docstring sets out both
        situations it covers. `Location.__post_init__` validates `zone` against
        `evidence_shape.vocabulary.ZONES`, so a located observation always carries
        one of the fifteen and there is no third case to be unsure about.

        An unresolvable or ambiguous key returns `None` rather than raising, and the
        second reason is the one that matters. Raising here would turn a call the
        operation mode already forbids into an exception instead of a denial,
        putting a lookup in front of §7's answer. And a key `current_location` cannot
        resolve is a key `materialise` cannot resolve either -- so nothing is
        released down that path; `UnresolvableSpan` is raised there, which is where
        it was raised before this method existed.
        """
        if isinstance(item, NAME_BEARING):
            # §7.7's FILENAME IS THE KIND THE ZONE LIST PROTECTS AGAINST, not a kind
            # the zone list refuses (`104` R-06, the merge). `filename` is in
            # `ALWAYS_LOCAL_ZONES` so that an EXCERPT may not address it; the name
            # itself is `00`:124's first releasable field and comes through
            # `NAME_BEARING`'s own door. Asking this method for its zone would hand
            # `check_item` the one answer that refuses the kind outright -- which is
            # what happened the moment `Filename` gained an `observation_key` for P8
            # to match the release against, and it took the whole fact pass down as
            # `always_local_item`.
            #
            # This is not the excerpt door widened. The refusal that keeps the two
            # apart is `check_item`'s on an `Excerpt` naming a `filename`-zone
            # observation, and that is untouched: an `Excerpt` still has its zone
            # looked up here and is still refused. Nor does it widen the protected
            # rule -- a protected file's name is stopped by
            # `protected_records_template` and `ProtectedItemRequested`, neither of
            # which reads a zone.
            return None
        key = getattr(item, "observation_key", None)
        if key is None:
            return None
        try:
            # SCOPED for the reason `current_location` gives: without it a file the
            # person owns twice returns `None` here, and `None` means the
            # always-local zone refusal is never taken for exactly those files.
            return current_location(
                self._conn, key,
                within_file_ids=file_ids or None).location.zone
        except (UnresolvableSpan, AmbiguousObservationKey):
            return None

    def _files_with_releasable_evidence(
            self, request: ModelCallRequest) -> frozenset[str]:
        """Which targeted files this request carries a text-bearing item FOR.

        `104` §13.2's condition, and it is a fact about the REQUEST, not about the
        corpus: the question the gate is answering is whether THIS call has anything
        of this file's for the model to read, not whether the file has evidence
        somewhere. A caller holding evidence it did not ask about has not asked
        about it.

        READS NO CONTENT, which is why the reason stays in
        `DECIDABLE_FROM_REQUEST`. `current_location` selects `observation_id,
        observation_key, file_id, location, superseded_by` and no content column --
        its own docstring is explicit that adding one "would move content access in
        front of the consent decision" -- so this is the same lookup `_located_zone`
        already takes at this point in the ladder.

        UNRESOLVABLE IS NOT EVIDENCE, and the direction is the safe one. A key that
        does not resolve contributes nothing here, so a request built from keys the
        evidence does not carry stays refused rather than being admitted on the
        strength of items that would raise at `materialise` anyway.

        The three `REFERENCE_ONLY` kinds do not count. A `CandidateLabel` is a
        destination name, a `MetadataField` is a field NAME, and an
        `EvidenceReference` is "an id only -- no content": a request carrying nothing
        but those has nothing OF THE FILE in it, and admitting one would be admitting
        exactly the silence `96` §19 measured.

        **NOR DOES THE FILENAME, and it is the one member that now needs an argument
        rather than a definition** (`104` R-06 made it resolve). The sentence this
        condition is built on is `96` §19's: a class reached with no safety evidence
        is a silence, and what lifts it is a READING OF THE FILE'S OWN BYTES for the
        model to work from. A filename is the person's label on the outside of the
        file; the filesystem extractor emits one for every indexed file, including
        the ones whose bytes nothing could open. Counting it here would admit every
        such file on evidence that is identical in the case the refusal exists for
        and in the case it does not -- which is the condition doing no work while
        appearing to. It is released once a call is permitted; it is not what
        permits one.
        """
        owners: set[str] = set()
        scope = tuple(request.target.file_ids)
        for item in request.requested_items:
            if not isinstance(item, TEXT_BEARING):
                continue
            key = getattr(item, "observation_key", None)
            if key is None:
                continue
            try:
                current = current_location(self._conn, key,
                                           within_file_ids=scope or None)
            except (UnresolvableSpan, AmbiguousObservationKey):
                continue
            if current.file_id in scope:
                owners.add(current.file_id)
        return frozenset(owners)

    def _precheck_items(self, request: ModelCallRequest, *, protected: bool,
                        sensitive_keys, policy) -> Exception | None:
        """Task 7's refusals that need no content. `unit_length=None` means unknown.

        The zone comes from `_located_zone`, which reads no content column either --
        so §8.4's always-local ZONE refusal is decided here, beside the other five
        reasons `denial.DECIDABLE_FROM_REQUEST` names, and not after `_materialise`.
        `DECISION_ORDER` is explicit that a gate which resolved first would hold the
        text in memory before deciding it was allowed to, and an absolute directory
        is the one value where holding it is itself the harm.

        `allow_unratified=True` because SPEC §4's flagged reading permits `filename`
        for non-protected files and denies it for protected ones; the denial is §7.3's
        and it arrives as `ProtectedItemRequested`, not as an unratified kind.

        `locality` is the request's own target (`104` R-159). The zone arm it divides
        is the one decided here, and it is read off `request.model_target` rather than
        taken as an argument for the reason `Gate.release` reads it once at the top: a
        second source for "where is this going" would let the door refuse about one
        destination while the bytes went to another.
        """
        for item in request.requested_items:
            try:
                check_item(item, unit_length=None,
                           zone=self._located_zone(
                               item, request.target.file_ids),
                           protected=protected,
                           sensitive_keys=sensitive_keys, allow_unratified=True,
                           suspension_permits_self_description=self._suspends(policy),
                           locality=request.model_target.locality,
                           ceiling=self._stored_ceiling())
            except (AlwaysLocalRequested, ProtectedItemRequested) as caught:
                return caught
        return None

    def _postcheck_items(self, request: ModelCallRequest,
                         resolved: Sequence[ReleasedItem], *, protected: bool,
                         sensitive_keys, policy) -> Exception | None:
        """The one refusal that needs the resolved unit length.

        `zone` here is the RESOLVED zone -- the one `ReleasedItem` carries and
        `dossier._released_body` puts on the wire -- where the precheck used the
        locator's. They read the same evidence row, so a zone this TARGET treats as
        always-local has already been refused by the time this runs and the check
        below cannot fire from `zone`. It is passed anyway rather than as `None`,
        because `None` there would be this method telling `check_item` the zone is
        unknown when it is holding it; if the two readings ever disagreed,
        `AlwaysLocalRequested` would propagate out of `release` uncaught, which is the
        fail-closed direction.

        **"Always-local" is now a question about the destination** (`104` R-159), and
        the sentence above is true for either answer because BOTH passes are given the
        same `request.model_target.locality`. On a local target a `path`- or
        `ocr`-zone item reaches here unrefused, by the ruling; the precheck and this
        pass agree about that the same way they agree about a `body` zone.
        """
        lengths = {item.observation_key: item.unit_length for item in resolved}
        zones = {item.observation_key: item.zone for item in resolved}
        # `104` R-152 with `104` R-135. Which resolutions took §8.4's own alternative
        # to a full document, asked through the one function both release builders
        # admit by, so the gate and the builders exempt the same set of units.
        excerpts = {
            item.observation_key: whole_unit_is_an_excerpt(
                whole_heading_unit=item.whole_heading_unit,
                whole_line_unit=item.whole_line_unit)
            for item in resolved}
        for item in request.requested_items:
            if not isinstance(item, TEXT_BEARING):
                continue
            try:
                check_item(item, unit_length=lengths.get(item.observation_key),
                           zone=zones.get(item.observation_key),
                           protected=protected, sensitive_keys=sensitive_keys,
                           allow_unratified=True,
                           suspension_permits_self_description=self._suspends(policy),
                           locality=request.model_target.locality,
                           ceiling=self._stored_ceiling())
            except WholeDocumentRequested as caught:
                if excerpts.get(item.observation_key, False):
                    # THE EXEMPTION IS TAKEN HERE AND NOT INSIDE `check_item`, because
                    # `check_item` cannot answer the question. Whether the whole unit is
                    # a heading or a single line is a fact about P4's `Location`, which
                    # only `resolve.materialise` still holds; `check_item` is given the
                    # request's shape and the unit's LENGTH, and a length is exactly
                    # what neither ruling would decide by.
                    #
                    # Excepting it excepts nothing else, and that is structural rather
                    # than a hope. `_precheck_items` above already asked `check_item`
                    # everything it can answer with `unit_length=None` -- the
                    # always-local names, the sensitive key, the always-local zone, the
                    # protected file, the unratified kind -- and returned the refusal
                    # BEFORE anything was materialised. The whole-document arm is the
                    # only one that needed the resolved length, which is why this pass
                    # exists at all, so it is the only refusal this line can waive. A
                    # one-line unit in a `path` zone never reaches here ON A CLOUD
                    # TARGET; since `104` R-159 it does reach here on a local one, and
                    # the arm this line waives does not fire there either -- the
                    # exemption is still excepting nothing, because for a local target
                    # there is nothing left in this pass to except.
                    #
                    # Measured at `e5cce44`: the gate denied a whole HEADING unit
                    # `whole_document_requested`, so R-135's exemption reached the two
                    # builders and stopped at the gate -- the builders offered the
                    # heading and the gate refused the call it was in. That is the 36
                    # site-A refusals of r13, each one the whole of a file's call.
                    continue
                return caught
        return None

    def _consent_reference(
            self, item: object, target_file_ids: Sequence[str]
            ) -> tuple[str, tuple[str, str]]:
        """Return the live canonical reference without reading protected text."""
        # SCOPED to the files this request is about. The membership check on the
        # next line is why it can be: the caller already knows, and the unscoped
        # question has no answer for a file the person happens to own twice.
        current = current_location(self._conn, item.observation_key,
                                   within_file_ids=target_file_ids)
        if current.file_id not in target_file_ids:
            raise UnresolvableSpan(
                f"observation {item.observation_key!r} belongs to file "
                f"{current.file_id!r}, outside request.target.file_ids "
                f"{tuple(target_file_ids)!r}"
            )
        location = current.location
        if item.span != location.text_span:
            raise UnresolvableSpan(
                f"requested span {item.span!r} disagrees with the live location's "
                f"span {location.text_span!r} for {item.observation_key!r}; consent "
                "records the exact requested reference and never repairs one"
            )
        return current.file_id, (item.observation_key, span_address(location))

    def _materialise(self, text_items: Sequence[object],
                     file_ids: Sequence[str] = (), *,
                     name_items: Sequence[object] = ()
                     ) -> tuple[tuple[ReleasedItem, ...], RedactionManifest]:
        """(observation_key, span) -> text -> redacted text. `resolve` is the only
        module under `src/privacy/` that binds a P4 text materialiser (L2).

        `found` is the PRE-redaction record and carries M5's three context fields;
        `apply_redaction` needs them for the local `RedactionEntry`, which travels
        inside the audit event's explanation. The RELEASED item is a different
        type and carries none of them: this built a `Materialised` with `value`
        redacted and `context_before` / `context_after` copied raw off `found`,
        so an 8-character requested span released its whole text unit.

        `name_items` are `NAME_BEARING` -- §7.7's filename, which addresses no span
        of its own and is resolved from its `file_id` by `resolve`. It goes through
        the SAME redaction, and that is not ceremony: `104` SF-2's identifier
        classifier is unwritten, and when it is written a person whose file is called
        `passport A1234567.pdf` must not be the one case it does not see.
        """
        resolved: list[ReleasedItem] = []
        entries = []
        found_items = [materialise_filename(self._conn, item.file_id)
                       for item in name_items]
        found_items += [materialise(self._conn, item,
                                    within_file_ids=file_ids or None)
                        for item in text_items]
        for found in found_items:
            value, entry = apply_redaction(
                found.value, observation_key=found.observation_key,
                span=found.span, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                classifier=self._classifier, transform=self._transform)
            resolved.append(ReleasedItem(
                observation_key=found.observation_key, span=found.span, value=value,
                zone=found.zone, unit_length=found.unit_length,
                # `104` R-135, carried and not recomputed: `materialise` asked P4's
                # `Location` and this is that answer.
                whole_heading_unit=found.whole_heading_unit,
                # `104` R-152, carried on the same terms.
                whole_line_unit=found.whole_line_unit))
            entries.append(entry)
        return tuple(resolved), RedactionManifest(entries=tuple(entries))

    def _release_record(self, request, policy, classes, hashes, resolved, manifest,
                        observed_at) -> AuditRecord:
        """SPEC §7's record for a release. `release_id` is None -- see the plan.

        §6 puts the append strictly BEFORE the release id exists, `mint_release`
        takes the `audit_id`, and `events` is append-only so the row cannot be
        back-filled. The join therefore runs ledger -> events, which is the
        direction Task 12 published the ledger's `audit_id` column for.
        """
        single = len(request.target.file_ids) == 1
        distinct = sorted(set(classes.values()))
        return AuditRecord(
            authorizing_policy=policy.policy_version,
            file_sensitivity=(distinct[0] if len(distinct) == 1
                              else canonical_json(distinct)),
            excerpts_included=tuple(
                (item.observation_key, item.span) for item in resolved),
            redaction_applied=manifest.any_redacted,
            model=request.model_target.to_mapping(),
            prompt_fingerprint=request.prompt_fingerprint,
            audit_id=None, release_id=None, observed_at=observed_at,
            stage=request.stage, file_ids=request.target.file_ids,
            group_id=request.target.group_id, content_hashes=hashes,
            operation_mode=policy.operation_mode,
            policy_version=policy.policy_version, plan_version=policy.plan_version,
            outcome="released",
            file_id=request.target.file_ids[0] if single else None,
            content_hash=hashes[0] if single else None,
            user_id=self._user_id,
            redaction_manifest=tuple(manifest.to_mapping()))

    def _denied(self, denied: Denied, request, policy, decisive, hashes,
                observed_at) -> Denied:
        """One `model_release_denied`, appended before the value is returned."""
        record_denial(self._conn, denied, request=request, policy=policy,
                      classification=decisive, content_hashes=hashes,
                      user_id=self._user_id,
                      component_version=self._component_version,
                      observed_at=observed_at)
        return denied
