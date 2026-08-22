# src/privacy/consent.py
"""§8.4's consent question, its id, and the seam P13 collects the answer through.

§8.4: "If a model needs text containing sensitive content, the user should see that
requirement and choose whether to allow a local model, a cloud model, a redacted
prompt, or no model use." Those four, exactly, and always all four -- P13's SPEC: "A
surface that offers fewer has silently made the user's decision for them."

This module exists to make one failure unrepresentable. P8's SPEC: "P8 must never map
this branch to `abstain`: there is no reason code for it, and none may be added ... an
abstention makes the choice for them, silently selecting 'no model use' without
asking. Consent pending is not consent refused." P7 does two things about that:

- `NeedsConsent` carries no `reason` field, so it is not a `Denied` in disguise and
  cannot be mapped onto a denial reason by accident;
- a recorded `no_model_use` is a `consent_granted` event with a user and a time, so an
  answer and a silence are distinguishable in the log by anyone who looks.

Whether a caller absorbs the branch is P8 Done-means 13 and P13 Done-means 16. P7 does
not police it.

**No table.** Done-means 7's falsifiable form is "the audit log holds a
`consent_requested` event and no `model_release` for that request until a choice is
recorded", so the log IS the state, and a second store beside it would be a second
place for the two to disagree.

**One `consent_granted` per choice.** Live `policy.grant_consent` already appends
`consent_granted` inside its transaction (Task 5). This module therefore calls it
for the three authorizing options and does not append a second event. `no_model_use`
skips `grant_consent` and this module appends the one event, so an answer and a
silence stay distinguishable in the log. Two appends would put one act in the log
twice, and §8.4's `prior_releases` is read back out of that log.

This module imports no `privacy` module that imports it: `release.py` re-exports
`NeedsConsent` for the `ReleaseDecision` union, so the request object arrives here as
an argument and its type is an annotation only.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import (
    CONSENT_GRANTED, CONSENT_REQUESTED, SUBSYSTEM, event_defaults,
)
from privacy.policy import Policy, grant_consent
from privacy.vocabulary import CONSENT_OPTIONS

if TYPE_CHECKING:  # pragma: no cover - annotation only; see the module docstring
    from privacy.release import ModelCallRequest

#: Which of §8.4's four permit a model call. Data rather than a negated `if`, which
#: would be one edit away from silently granting. `no_model_use` is a CHOICE -- it is
#: recorded like the others and changes no policy.
CONSENT_AUTHORIZES: Mapping[str, bool] = MappingProxyType({
    "local_model": True,
    "cloud_model": True,
    "redacted_prompt": True,
    "no_model_use": False,
})

#: The key the scope is stored under, shared with Task 13's `REVOKED_SCOPE_KEY` and
#: Task 15's `revoke`. Grant here, withdraw there, deny in between.
_SCOPE_KEY: str = "scope"


class UnknownConsentOption(ValueError):
    """A value outside §8.4's four. SPEC §1: "a load error, not a fallback.\""""


class IncompleteConsentOptions(ValueError):
    """Fewer than four options.

    P13's SPEC: "All four options are always presentable. A surface that offers fewer
    has silently made the user's decision for them."
    """


class UnknownConsentRequest(LookupError):
    """No `consent_requested` event carries this id."""


class ConsentAlreadyRecorded(ValueError):
    """This request already has an answer.

    P8's SPEC: "the caller composes a NEW `ModelCallRequest` under the chosen option;
    the original is never resumed." A second answer would let a caller turn a recorded
    `no_model_use` into a `cloud_model` after the fact.
    """


@dataclass(frozen=True)
class ConsentRequirement:
    """SPEC §6: "which items require sensitive text, and why".

    `items` is `(observation_key, span)` pairs -- the same shape as
    `excerpts_included`, and for SPEC §7's reason: "not a second copy of the text".
    A consent prompt that embedded the value would have released it in order to ask
    permission to release it.
    """

    file_ids: tuple[str, ...]
    handling_class: str
    items: tuple[tuple[str, str], ...]
    why: str


@dataclass(frozen=True)
class NeedsConsent:
    """SPEC §6's third branch. It carries no `reason`, and that is load-bearing.

    "`Denied` is the gate's answer, `NeedsConsent` is a question that only the user
    can answer. Consent pending is not consent refused."
    """

    consent_request_id: str
    requirement: ConsentRequirement
    options: tuple[str, ...] = CONSENT_OPTIONS

    def __post_init__(self) -> None:
        unknown = [option for option in self.options if option not in CONSENT_OPTIONS]
        if unknown:
            raise UnknownConsentOption(
                f"{unknown} are not among §8.4's four options {CONSENT_OPTIONS}"
            )
        if tuple(self.options) != CONSENT_OPTIONS:
            raise IncompleteConsentOptions(
                f"{tuple(self.options)} is not §8.4's four in order; P13: 'A surface "
                "that offers fewer has silently made the user's decision for them'"
            )


def _requirement_form(requirement: ConsentRequirement) -> dict[str, object]:
    return {
        "file_ids": list(requirement.file_ids),
        "handling_class": requirement.handling_class,
        "items": [list(pair) for pair in requirement.items],
        "why": requirement.why,
    }


def _requirement_from(form: Mapping[str, object]) -> ConsentRequirement:
    return ConsentRequirement(
        file_ids=tuple(form["file_ids"]),
        handling_class=form["handling_class"],
        items=tuple(tuple(pair) for pair in form["items"]),
        why=form["why"],
    )


def _event_for(conn: sqlite3.Connection, event_type: str,
               consent_request_id: str) -> sqlite3.Row | None:
    """The one event of this type carrying this id.

    `consent_request_id` has no `events` column, so it lives in the canonical-JSON
    `explanation` the skeleton's *The audit record's home* decided on, and is read
    back with `json_extract`.
    """
    return conn.execute(
        "SELECT * FROM events WHERE event_type = ? "
        "AND json_extract(explanation, '$.consent_request_id') = ? "
        "ORDER BY event_id LIMIT 1",
        (event_type, consent_request_id),
    ).fetchone()


def open_consent_request(conn: sqlite3.Connection, requirement: ConsentRequirement, *,
                         request: ModelCallRequest, policy: Policy,
                         content_hashes: Sequence[str], user_id: str | None,
                         component_version: str, observed_at: str) -> NeedsConsent:
    """Ask §8.4's question, record that it was asked, and return all four options.

    The id is `uuid.uuid4()`, not `secrets`: a `release_id` is a capability and must
    not be guessable, while a `consent_request_id` is a join key P13 puts in a
    `subject_ref` column and carries no authority at all.
    """
    consent_request_id = "consent-" + str(uuid.uuid4())
    needs = NeedsConsent(consent_request_id=consent_request_id,
                         requirement=requirement)
    file_ids = tuple(request.target.file_ids)
    values = {
        "audit_id": None,
        "release_id": None,
        "policy_version": policy.policy_version,
        "plan_version": policy.plan_version,
        "stage": request.stage,
        "outcome": "consent_requested",
        "operation_mode": policy.operation_mode,
        "authorizing_policy": policy.policy_version,
        "file_sensitivity": requirement.handling_class,
        "excerpts_included": (),
        "redaction_applied": False,
        "redaction_manifest": (),
        "model": {"locality": request.model_target.locality,
                  "model_id": request.model_target.model_id,
                  "provider": request.model_target.provider},
        "content_hashes": tuple(content_hashes),
        "content_hash": content_hashes[0] if len(tuple(content_hashes)) == 1 else None,
        "prompt_fingerprint": request.prompt_fingerprint,
        "file_id": file_ids[0] if len(file_ids) == 1 else None,
        "file_ids": file_ids,
        "group_id": request.target.group_id,
        "consent_request_id": consent_request_id,
        "user_id": user_id,
        "observed_at": observed_at,
        "appended_at": observed_at,
    }
    unfilled = [name for name in AUDIT_FIELDS if name not in values]
    if unfilled:
        raise ValueError(
            f"SPEC §7 names {unfilled} and the consent path has no value for them; a "
            "field Task 10 publishes must be filled at the seam, not defaulted"
        )
    # Live Task 10: consent_request_id / user_id / redaction_manifest are CARRIED
    # fields, not AUDIT_FIELDS. They still have to land on the record so
    # append_audit writes them into explanation JSON (no events column, no extra
    # collision with EXPLANATION_FIELDS).
    record = AuditRecord(
        **{name: values[name] for name in AUDIT_FIELDS},
        user_id=values["user_id"],
        consent_request_id=values["consent_request_id"],
        redaction_manifest=values["redaction_manifest"],
    )
    append_audit(conn, record, author=SUBSYSTEM,
                 component_version=component_version, extra={
                     "requirement": _requirement_form(requirement),
                     "options": list(needs.options),
                 })
    return needs


def pending_consent(conn: sqlite3.Connection,
                    consent_request_id: str) -> NeedsConsent | None:
    """The open question, or None if it was never asked or has been answered."""
    asked = _event_for(conn, CONSENT_REQUESTED, consent_request_id)
    if asked is None:
        return None
    if _event_for(conn, CONSENT_GRANTED, consent_request_id) is not None:
        return None
    payload = json.loads(asked["explanation"])
    return NeedsConsent(consent_request_id=consent_request_id,
                        requirement=_requirement_from(payload["requirement"]),
                        options=tuple(payload["options"]))


def record_consent_choice(conn: sqlite3.Connection, consent_request_id: str,
                          option: str, *, policy: Policy, scope: str,
                          user_id: str, component_version: str,
                          observed_at: str) -> None:
    """Record the user's answer, and grant only where the answer authorizes a model.

    Returns None. SPEC §6: "the gate owns the policy, so the caller does not supply
    this value, it echoes it" -- handing a freshly minted `policy_version` back from a
    consent recorder would give the caller a value from a path that is not the gate.
    The caller re-reads `current_policy`, which it has to do anyway: the original
    request is never resumed.

    `scope` has no default. Open question 3: "What is a 'corpus area'? ... Consent
    grants cannot be scoped until this is named."
    """
    if option not in CONSENT_OPTIONS:
        raise UnknownConsentOption(
            f"{option!r} is not among §8.4's four options {CONSENT_OPTIONS}"
        )
    if _event_for(conn, CONSENT_REQUESTED, consent_request_id) is None:
        raise UnknownConsentRequest(
            f"no consent_requested event carries {consent_request_id!r}"
        )
    if _event_for(conn, CONSENT_GRANTED, consent_request_id) is not None:
        raise ConsentAlreadyRecorded(
            f"{consent_request_id!r} already has an answer; P8's SPEC: 'the caller "
            "composes a NEW ModelCallRequest under the chosen option; the original is "
            "never resumed'"
        )
    authorized = CONSENT_AUTHORIZES[option]
    if authorized:
        # Live Task 5: grant_consent already appends consent_granted inside its
        # transaction. A second append here would put one act in the log twice.
        grant_consent(conn, policy, scope, option, user_id=user_id,
                      component_version=component_version, observed_at=observed_at)
        return
    append_event(conn, **event_defaults(
        event_type=CONSENT_GRANTED,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "consent_request_id": consent_request_id,
            "option": option,
            "authorized": authorized,
            _SCOPE_KEY: scope,
            "collected_by": "P13",
        }),
    ))
