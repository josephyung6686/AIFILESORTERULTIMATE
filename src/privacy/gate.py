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
    UNREADABLE_UNCLASSIFIED, ClassificationRecord, resolve_class,
)
from privacy.consent import (ConsentRequirement, grant_authorizes,
                             open_consent_request)
from privacy.denial import (
    deny_always_local_item, deny_dossier_over_budget, deny_mode_forbids_target,
    deny_policy_revoked, deny_protected_cloud_target,
    deny_protected_records_template, deny_unclassified,
    deny_whole_document_requested, first_reason, is_protected_records, mode_forbids,
    over_dossier_ceiling, policy_revoked_for, protected_cloud_denies, record_denial,
    unclassified_denies,
)
from privacy.items import (
    AlwaysLocalRequested, Excerpt, ProtectedItemRequested, RedactedIdentifier,
    WholeDocumentRequested, check_item, sensitive_observation_keys,
)
from privacy.policy import current_policy
from privacy.redaction import RedactionManifest, apply_redaction, span_address
from privacy.release import (
    DECISION_ORDER, Denied, ModelCallRequest, NeedsConsent, NoPolicyInForce,
    ReleaseDecision, Released, ReleasedItem,
)
from privacy.resolve import (
    AmbiguousObservationKey, UnresolvableSpan, current_location, materialise,
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
                 template_for: Callable[[str], str | None] | None = None,
                 suspension_permits_self_description: bool = False) -> None:
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
        #: NAMED FOR THE RULING, not for the permission, and the difference is what
        #: `test_no_signature_and_no_branch_field_names_an_override` is protecting:
        #: P7's published names may not read as a back door. `unclassified_permits_
        #: local` is the precedent -- a legitimate permission says what CONDITION
        #: permits what, and this one says the `80` §8 suspension is what permits a
        #: self-description. It is not an override of the policy: a run without the
        #: suspension refuses exactly as it did before the amendment existed.
        #:
        #: PER-INVOCATION, AND DELIBERATELY NOT THE `--enable-cloud` CONSENT. The
        #: two look alike and have different cadences, so a later reader may be
        #: tempted to harmonise them. `--enable-cloud` is the operation mode for
        #: FILE facts: it recurs on every run and every file, which is why the
        #: owner's ruling on it is "once, recorded". A self-description is sent on
        #: the ONE run where the person types their sentence, because that is the
        #: run where the shortlist is computed; after they confirm a role the moment
        #: is over (`80` §4, R2) and nothing sends again.
        #:
        #: So this opt-in is never stored, and that is the whole design. R2 says a
        #: confirmation a person learns to click through is not a safety mechanism
        #: -- and there is nothing here to learn, because nothing repeats. A STORED
        #: opt-in would force the choice between a notice on every run (the
        #: click-through R2 forbids) and no notice at all (the silent send C2
        #: forbids), and both are worse than asking on the one run that sends.
        #:
        #: `80` §8.3's condition C1, at the composition surface. DEFAULTED, where
        #: `check_item` refuses to default, and the two are the same requirement
        #: read from its two ends: "a developer who forgets this exception exists
        #: gets the safe behaviour". Forgetting it HERE gives you `False`, which is
        #: the safe behaviour; forgetting it at `check_item` gives you a TypeError,
        #: because that is the layer where every caller must have chosen. A default
        #: in both places would be a caller who never chose; a default in neither
        #: would put a required argument on Task 20's pinned constructor.
        self._suspension_permits_self_description = suspension_permits_self_description

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

        caught = self._precheck_items(request, protected=bool(protected_ids),
                                      sensitive_keys=sensitive_keys)
        if isinstance(caught, AlwaysLocalRequested):
            builders["always_local_item"] = lambda: deny_always_local_item(
                caught, file_ids=file_ids)
        elif isinstance(caught, ProtectedItemRequested):
            builders["protected_records_template"] = \
                lambda: deny_protected_records_template(
                    file_ids=file_ids, model_target=request.model_target)

        unclassified = tuple(sorted(
            file_id for file_id, name in classes.items()
            if name == UNREADABLE_UNCLASSIFIED))
        if unclassified and unclassified_denies(
                locality=locality,
                local_calls_on_unclassified=self._unclassified_permits_local):
            builders["unclassified"] = lambda: deny_unclassified(
                file_ids=unclassified, locality=locality,
                completeness=self._completeness(rows, unclassified[0]))

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
        resolved, manifest = self._materialise(text_items)

        # 4 -- the two reasons that needed the resolved text.
        late: dict[str, Callable[[], Denied]] = {}
        caught = self._postcheck_items(request, resolved,
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

    def _located_zone(self, item: object) -> str | None:
        """The document zone an item addresses, WITHOUT reading its text.

        `current_location` selects `observation_id, observation_key, file_id,
        location, superseded_by` and no content column -- its own docstring is
        explicit that adding one "would move content access in front of the consent
        decision". The zone is therefore a locator fact, and §8.4's always-local zone
        refusal can be taken before anything is materialised.

        An unresolvable or ambiguous key returns `None` rather than raising, and the
        second reason is the one that matters. Raising here would turn a call the
        operation mode already forbids into an exception instead of a denial,
        putting a lookup in front of §7's answer. And a key `current_location` cannot
        resolve is a key `materialise` cannot resolve either -- so nothing is
        released down that path; `UnresolvableSpan` is raised there, which is where
        it was raised before this method existed.
        """
        key = getattr(item, "observation_key", None)
        if key is None:
            return None
        try:
            return current_location(self._conn, key).location.zone
        except (UnresolvableSpan, AmbiguousObservationKey):
            return None

    def _precheck_items(self, request: ModelCallRequest, *, protected: bool,
                        sensitive_keys) -> Exception | None:
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
        """
        for item in request.requested_items:
            try:
                check_item(item, unit_length=None, zone=self._located_zone(item),
                           protected=protected,
                           sensitive_keys=sensitive_keys, allow_unratified=True,
                           suspension_permits_self_description=self._suspension_permits_self_description)
            except (AlwaysLocalRequested, ProtectedItemRequested) as caught:
                return caught
        return None

    def _postcheck_items(self, request: ModelCallRequest,
                         resolved: Sequence[ReleasedItem], *, protected: bool,
                         sensitive_keys) -> Exception | None:
        """The one refusal that needs the resolved unit length.

        `zone` here is the RESOLVED zone -- the one `ReleasedItem` carries and
        `dossier._released_body` puts on the wire -- where the precheck used the
        locator's. They read the same evidence row, so an always-local zone has
        already been refused by the time this runs and the check below cannot fire
        from `zone`. It is passed anyway rather than as `None`, because `None` there
        would be this method telling `check_item` the zone is unknown when it is
        holding it; if the two readings ever disagreed, `AlwaysLocalRequested` would
        propagate out of `release` uncaught, which is the fail-closed direction.
        """
        lengths = {item.observation_key: item.unit_length for item in resolved}
        zones = {item.observation_key: item.zone for item in resolved}
        for item in request.requested_items:
            if not isinstance(item, TEXT_BEARING):
                continue
            try:
                check_item(item, unit_length=lengths.get(item.observation_key),
                           zone=zones.get(item.observation_key),
                           protected=protected, sensitive_keys=sensitive_keys,
                           allow_unratified=True,
                           suspension_permits_self_description=self._suspension_permits_self_description)
            except WholeDocumentRequested as caught:
                return caught
        return None

    def _consent_reference(
            self, item: object, target_file_ids: Sequence[str]
            ) -> tuple[str, tuple[str, str]]:
        """Return the live canonical reference without reading protected text."""
        current = current_location(self._conn, item.observation_key)
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

    def _materialise(self, text_items: Sequence[object]
                     ) -> tuple[tuple[ReleasedItem, ...], RedactionManifest]:
        """(observation_key, span) -> text -> redacted text. `resolve` is the only
        module under `src/privacy/` that binds a P4 text materialiser (L2).

        `found` is the PRE-redaction record and carries M5's three context fields;
        `apply_redaction` needs them for the local `RedactionEntry`, which travels
        inside the audit event's explanation. The RELEASED item is a different
        type and carries none of them: this built a `Materialised` with `value`
        redacted and `context_before` / `context_after` copied raw off `found`,
        so an 8-character requested span released its whole text unit.
        """
        resolved: list[ReleasedItem] = []
        entries = []
        for item in text_items:
            found = materialise(self._conn, item)
            value, entry = apply_redaction(
                found.value, observation_key=found.observation_key,
                span=found.span, context_before=found.context_before,
                context_after=found.context_after,
                context_truncated=found.context_truncated,
                classifier=self._classifier, transform=self._transform)
            resolved.append(ReleasedItem(
                observation_key=found.observation_key, span=found.span, value=value,
                zone=found.zone, unit_length=found.unit_length))
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
