# src/privacy/policy.py
"""§8.4's operation modes, consent grants and redaction settings, as one versioned
policy record.

**One policy version is the whole snapshot.** §8.8 lists "Privacy and model-consent
policies" as a single plan-version item, and B2 makes `policy_version` a binding term
of every release. A consent grant that did not mint a new version would leave a
release minted before the grant still spendable after it, which is the one silent
widening of egress policy §8.8 calls the least acceptable silent change in the
product. So mode, grants, redaction settings and automatic-move permissions travel
together and a change to any of them is a new version.

**The gate mints the version; the caller echoes it.** SPEC §6. A `Policy` handed in
carries `UNSET_POLICY_VERSION` and is refused if it carries anything else.

**Supersede, never mutate (§8.2).** The prior version stays loadable by name forever,
because §8.5 replay must reproduce "the policy in force at each call".

**One act, one event.** `_persist` appends nothing. `set_policy` adds `policy_set`;
`grant_consent` adds `consent_granted`; `revoke_consent` adds NOTHING -- the
`consent_revoked` append belongs to `privacy.revocation.revoke`, which assembles
§8.4's prior-release list and retraction limit and reads that event back out of the
log.

**One act, one commit.** The row and its event go in under one transaction, because
§8.2 reconstructs a transition from the log: a committed policy row whose event
never landed is a policy change nothing can account for, and the prior version
would stay superseded with nothing recording why.

**The supplied version is a concurrency token.** `grant_consent` and
`revoke_consent` derive a complete next snapshot from the snapshot handed in, so
one that has been superseded is refused (`StalePolicyVersion`) inside the same
transaction as the write. `set_policy` is exempt: it replaces rather than derives.

**This module holds no default.** §8.4's local-first `must` is W1 and lives in
`privacy.defaults`. `current_policy` returns `None` when nothing has been set. A
default in two modules is a default that can disagree with itself, and the thing it
would disagree about is whether content leaves the device.

**`scope` is opaque.** SPEC Open question 3 -- "What is a 'corpus area'?" -- is open,
so a scan root, a frozen node id, a group id and a domain name are all accepted,
unparsed. P7 has no basis to prefer one and does not invent it.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass, replace

from database_agent.db import transaction
from database_agent.events import append_event
from database_agent.supersede import mark_superseded

from evidence_shape.canonical import canonical_json

from privacy.authorship import CONSENT_GRANTED, POLICY_SET, event_defaults
from privacy.schema import POLICIES_TABLE
from privacy.vocabulary import (
    CONSENT_OPTIONS,
    DISPLAY_FACETS,
    REDACTED,
    REDACTION_VALUES,
    SHOWN,
    OutOfVocabulary,
    check_mode,
)

# SPEC §10: "names | previews | thumbnails | ocr_text | location_data -- each
# shown | redacted". `SHOWN`, `REDACTED` and `REDACTION_VALUES` are imported above
# and RE-EXPORTED under the same three names, because `privacy.vocabulary` owns them
# (A7, resolved) and because they are the value vocabulary of `DISPLAY_FACETS`, which
# lives there too. This module defined them once, Task 18 defined them again as
# `REDACTION_VALUES` and a third section as `REDACTION_VALUES`; three homes for two strings
# is the defect class this project has paid the most for. Consumers keep importing
# them from `privacy.policy` -- the names did not move, only the definition did.

#: The consent option that authorizes nothing. Named so `transcription_authorized_for`
#: does not index into a tuple, and validated at import so it cannot drift from
#: Task 2's vocabulary.
NO_MODEL_USE = "no_model_use"
if NO_MODEL_USE not in CONSENT_OPTIONS:
    raise ImportError(
        f"{NO_MODEL_USE!r} is not one of §8.4's four consent options "
        f"{CONSENT_OPTIONS!r}; a value outside the set is a load error"
    )

#: What a `Policy` carries before the gate mints one (SPEC §6).
UNSET_POLICY_VERSION = ""

_COLUMNS = (
    "policy_version", "plan_version", "operation_mode", "consent_grants",
    "redaction_settings", "automatic_move_permissions", "set_at",
)


class CallerSuppliedPolicyVersion(Exception):
    """The gate owns the policy version; a caller offered one (SPEC §6)."""


class UnknownPolicyVersion(Exception):
    """No policy was ever minted under that version."""


class AmbiguousCurrentPolicy(Exception):
    """Two live policies at one plan version. Raised, never resolved by picking."""


class StalePolicyVersion(Exception):
    """A consent change was derived from a snapshot that is no longer in force.

    One policy version is the whole snapshot, so `grant_consent` and
    `revoke_consent` compute a COMPLETE next snapshot from the one handed in. If
    that one has been superseded, writing the derivation would discard every
    change made since it was read -- and two revocations from one snapshot would
    put the first-revoked grant back in force. The version is therefore the
    concurrency token: refused here, and the caller re-reads `current_policy`.
    """


@dataclass(frozen=True)
class Policy:
    """§8.4's authorizing policy: the mode, the grants, and the redaction settings.

    `redaction_settings` may be PARTIAL. Filling an absent facet with its more
    redacting value is W1's job (`privacy.defaults`), and a `Policy` that refused a
    partial map would make the migrated-from-nothing case unreachable.
    """

    policy_version: str
    operation_mode: str
    consent_grants: tuple[tuple[str, str], ...]
    redaction_settings: dict
    automatic_move_permissions: dict
    plan_version: str
    set_at: str

    def __post_init__(self) -> None:
        check_mode(self.operation_mode)
        for facet, value in self.redaction_settings.items():
            if facet not in DISPLAY_FACETS:
                raise OutOfVocabulary(
                    f"{facet!r} is not one of §8.4's five configurable facets "
                    f"{DISPLAY_FACETS!r}")
            if value not in REDACTION_VALUES:
                raise OutOfVocabulary(
                    f"{value!r} is not one of {REDACTION_VALUES!r} for facet {facet!r}")
        for scope, option in self.consent_grants:
            if option not in CONSENT_OPTIONS:
                raise OutOfVocabulary(
                    f"{option!r} is not one of §8.4's four consent options "
                    f"{CONSENT_OPTIONS!r} (scope {scope!r})")
        for scope, permitted in self.automatic_move_permissions.items():
            if not isinstance(permitted, bool):
                raise OutOfVocabulary(
                    f"automatic-move permission for {scope!r} is {permitted!r}; "
                    "§8.4 permits or does not permit, and nothing between")


def _row_to_policy(row: sqlite3.Row) -> Policy:
    return Policy(
        policy_version=row["policy_version"],
        operation_mode=row["operation_mode"],
        consent_grants=tuple(tuple(pair) for pair in
                             json.loads(row["consent_grants"])),
        redaction_settings=json.loads(row["redaction_settings"]),
        automatic_move_permissions=json.loads(row["automatic_move_permissions"]),
        plan_version=row["plan_version"],
        set_at=row["set_at"],
    )


def _live_row(conn: sqlite3.Connection, plan_version: str) -> sqlite3.Row | None:
    rows = list(conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} "
        "WHERE plan_version = ? AND superseded_by IS NULL ORDER BY set_at, rowid",
        (plan_version,)))
    if len(rows) > 1:
        raise AmbiguousCurrentPolicy(
            f"{len(rows)} live policies at plan version {plan_version!r}; "
            "one must supersede the other (§8.2)")
    return rows[0] if rows else None


def _require_in_force(conn: sqlite3.Connection, policy: Policy) -> None:
    """Refuse a derivation from a snapshot that is not the live one.

    Called inside the same transaction as the persist, so a policy that goes live
    between the check and the insert cannot slip past it. `set_policy` does NOT
    call this: it is a full replacement, not a derivation, so it has nothing to
    silently discard.
    """
    live = _live_row(conn, policy.plan_version)
    if live is None:
        raise StalePolicyVersion(
            f"no policy is in force at plan version {policy.plan_version!r}; "
            "a consent change derives from the live snapshot, and "
            f"{policy.policy_version!r} is not one")
    if live["policy_version"] != policy.policy_version:
        raise StalePolicyVersion(
            f"policy {policy.policy_version!r} was superseded by "
            f"{live['policy_version']!r}; re-read `current_policy` and derive the "
            "change from the snapshot in force (§8.2, §8.4)")


def _persist(conn: sqlite3.Connection, policy: Policy, *,
             supersede_reason: str) -> str:
    """Mint a version, insert the row, supersede the prior one. Appends no event."""
    if policy.policy_version != UNSET_POLICY_VERSION:
        raise CallerSuppliedPolicyVersion(
            f"policy_version {policy.policy_version!r} was supplied by the caller; "
            "the gate owns the policy and the caller echoes it (SPEC §6)")
    version = f"policy-{uuid.uuid4().hex}"
    with transaction(conn):
        prior = _live_row(conn, policy.plan_version)
        conn.execute(
            f"INSERT INTO {POLICIES_TABLE} ({','.join(_COLUMNS)}) "
            f"VALUES ({','.join('?' * len(_COLUMNS))})",
            (version, policy.plan_version, policy.operation_mode,
             canonical_json([list(pair) for pair in policy.consent_grants]),
             canonical_json(policy.redaction_settings),
             canonical_json(policy.automatic_move_permissions), policy.set_at),
        )
        if prior is not None:
            mark_superseded(conn, POLICIES_TABLE, old_id=prior["policy_version"],
                            new_id=version, reason=supersede_reason)
    return version


def _explanation(conn: sqlite3.Connection, version: str, **extra) -> str:
    policy = policy_at(conn, version)
    prior = conn.execute(
        f"SELECT supersedes FROM {POLICIES_TABLE} WHERE policy_version = ?",
        (version,)).fetchone()["supersedes"]
    payload = {
        "policy_version": version,
        "superseded_policy_version": prior,
        "plan_version": policy.plan_version,
        "operation_mode": policy.operation_mode,
        "consent_grants": [list(pair) for pair in policy.consent_grants],
        "redaction_settings": policy.redaction_settings,
        "automatic_move_permissions": policy.automatic_move_permissions,
    }
    payload.update(extra)
    return canonical_json(payload)


def set_policy(conn: sqlite3.Connection, policy: Policy, *,
               component_version: str, user_id: str, reason: str) -> str:
    """Mint and record a policy version, and append §8.4's `policy_set` event.

    `reason` is required and is the caller's: §8.8 requires the plan diff to be
    "meaningful", and a fixed sentence held here would make every privacy-policy
    diff line read the same. There is no `author` parameter -- M8 makes the acting
    part the author, and a log where the author is a caller-supplied value cannot
    answer §8.2's reconstruction question.
    """
    if not reason.strip():
        raise ValueError("a policy change carries a reason (§8.2, §8.8)")
    with transaction(conn):
        version = _persist(conn, policy, supersede_reason=reason)
        append_event(conn, **event_defaults(
            event_type=POLICY_SET, user_id=user_id, observed_at=policy.set_at,
            component_version=component_version,
            explanation=_explanation(conn, version, reason=reason)))
    return version


def current_policy(conn: sqlite3.Connection, *, plan_version: str) -> Policy | None:
    """The policy in force for this plan version, or None if none has been set.

    None is a fact, not a gap: §8.4's local-first floor is W1's and lives in
    `privacy.defaults`, which is what turns None into a resolved posture.
    """
    row = _live_row(conn, plan_version)
    return None if row is None else _row_to_policy(row)


def policy_at(conn: sqlite3.Connection, policy_version: str) -> Policy:
    """Any policy version, superseded or not. §8.5 replay reads through this."""
    row = conn.execute(
        f"SELECT * FROM {POLICIES_TABLE} WHERE policy_version = ?",
        (policy_version,)).fetchone()
    if row is None:
        raise UnknownPolicyVersion(policy_version)
    return _row_to_policy(row)


def grant_consent(conn: sqlite3.Connection, policy: Policy, scope: str, option: str,
                  *, user_id: str, component_version: str, observed_at: str) -> str:
    """Add one §8.4 consent grant, as a new policy version. Appends `consent_granted`."""
    if option not in CONSENT_OPTIONS:
        raise OutOfVocabulary(
            f"{option!r} is not one of §8.4's four consent options {CONSENT_OPTIONS!r}")
    grants = tuple(pair for pair in policy.consent_grants if pair[0] != scope)
    revised = replace(policy, policy_version=UNSET_POLICY_VERSION,
                      consent_grants=grants + ((scope, option),), set_at=observed_at)
    with transaction(conn):
        _require_in_force(conn, policy)
        version = _persist(conn, revised, supersede_reason=canonical_json(
            {"act": "consent_granted", "scope": scope, "option": option}))
        append_event(conn, **event_defaults(
            event_type=CONSENT_GRANTED, user_id=user_id, observed_at=observed_at,
            component_version=component_version,
            explanation=_explanation(conn, version, granted_scope=scope,
                                     granted_option=option)))
    return version


def revoke_consent(conn: sqlite3.Connection, policy: Policy, scope: str, *,
                   user_id: str, component_version: str, observed_at: str) -> str:
    """Withdraw every grant at `scope` and return the new policy version.

    **Appends no event.** `privacy.revocation.revoke` appends `consent_revoked`
    once, because that is where §8.4's prior-release list and retraction limit are
    assembled and where the event is read back out of the log. `user_id` is on the
    signature because it is the acting user and `revoke` carries it into the event.
    """
    revised = replace(
        policy, policy_version=UNSET_POLICY_VERSION, set_at=observed_at,
        consent_grants=tuple(p for p in policy.consent_grants if p[0] != scope))
    with transaction(conn):
        _require_in_force(conn, policy)
        version = _persist(conn, revised, supersede_reason=canonical_json(
            {"act": "consent_revoked", "scope": scope, "user_id": user_id,
             "component_version": component_version}))
    return version


@dataclass(frozen=True)
class TranscriptionAuthorization:
    """P5's `Callable[[], bool]`, with the scope P5's call site cannot pass.

    `src/extractors/long_tail.py:204` calls `transcription_authorized()` with no
    arguments. P7's surfaces are per-file or per-scope, so the scope has to be
    closed over -- and it is carried as a FIELD rather than captured in a lambda so
    the mismatch stays visible to a reader and to a test.
    """

    conn: sqlite3.Connection
    scope: str
    plan_version: str

    def __call__(self) -> bool:
        policy = current_policy(self.conn, plan_version=self.plan_version)
        if policy is None:
            return False
        return any(scope == self.scope and option != NO_MODEL_USE
                   for scope, option in policy.consent_grants)


def transcription_authorized_for(conn: sqlite3.Connection, scope: str, *,
                                 plan_version: str) -> TranscriptionAuthorization:
    """§2.9's speech-to-text authorization, as P5's zero-argument predicate (M10).

    §2.9 permits transcripts "only under an explicit privacy and compute policy".
    **Which of the four consent options authorizes speech-to-text is not stated
    anywhere in the design.** The rule here is the narrowest one expressible in the
    vocabulary P7 owns -- an explicit grant naming this scope, whose option is
    anything other than `no_model_use` -- and it is a reported reading, not a
    ratification.
    """
    return TranscriptionAuthorization(conn, scope, plan_version)
