# src/privacy/revocation.py
"""§8.4's revocation, its stated limit, and the derived-data deletion D3 left unbuilt.

Three things are decided here and each is a quotation rather than a choice:

- **Revocation is forward-only.** §8.4 gives the user the right to "revoke a policy
  for future runs". A revocation appends; it never rewrites the record of what has
  already happened, because §8.4 also requires the product to say what already left,
  and that is unsatisfiable once the send record is erasable.
- **The retraction limit is mandatory and its wording is not P7's.** §8.4: "Revocation
  cannot necessarily retract data already sent to an external provider, so the product
  must communicate that distinction clearly." The SPEC defers the copy to P13; this
  module enforces presence and holds no sentence.
- **`delete_derived` refuses, on both sides of a literal list (D3).** §8.4 gives the
  user the right to "review and delete local derived data" and §8.2 forbids updating
  or deleting an event. D3 ratifies the direction -- events append-only forever,
  derived projections tombstonable, "derived" a literal enumeration -- and ratifies
  that NOTHING IS BUILT until P13 drives it. So the surface exists and the semantics
  do not, and an unenumerated scope fails differently from an unbuilt one.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import NoReturn

from database_agent.events import append_event
from evidence_shape.canonical import canonical_json

from privacy.audit import audit_records_for
from privacy.authorship import CONSENT_REVOKED, event_defaults
from privacy.policy import Policy, revoke_consent

#: The `AuditRecord.outcome` value that means content left the device (SPEC §7).
RELEASED: str = "released"


class MissingRetractionLimit(ValueError):
    """§8.4 requires the distinction be communicated; a blank statement is not one."""


class DeleteDerivedRefused(Exception):
    """`delete_derived` never succeeds today. It refuses for one of two reasons."""


class ScopeNotDerived(DeleteDerivedRefused):
    """The scope is outside D3's literal enumeration.

    This is why the list is literal rather than a predicate: a table nobody enumerated
    produces a red test here instead of being quietly deleted from, or quietly skipped,
    depending on which way a clever rule happened to fall.
    """


class UnratifiedResolution(DeleteDerivedRefused):
    """The scope IS derived, and no tombstone column is built (D3, I6).

    The name is the one the plan skeleton published and it is kept so the contract does
    not move; what it now reports is *unbuilt*, not *unratified*. D3 settled the
    direction on 2026-08-21 and deliberately built nothing, because a writer-less column
    is the defect `files.sensitivity_state` demonstrated for the length of this project.
    """


@dataclass(frozen=True)
class PriorRelease:
    """One row of SPEC §8's `prior_releases[]`: "model, provider, when, which excerpts"."""

    model: str
    provider: str
    when: str
    excerpts: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class RevocationResult:
    """SPEC §8's return: forward-only, evidenced, and limited."""

    effective_from: str
    prior_releases: tuple[PriorRelease, ...]
    retraction_limit: str


@dataclass(frozen=True)
class DerivedScope:
    """One table-and-column D3's enumeration may or may not name."""

    table: str
    column: str


#: D3's literal enumerated table-and-column list. These five columns are where the text
#: extracted from a file's bytes actually lives -- checked against the live schema, not
#: against a PLAN. Anything else is `NOT_DERIVED` and refused by name.
DERIVED_PROJECTIONS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "evidence": ("raw_value", "normalized_value", "context_before", "context_after"),
    "text_units": ("text",),
})

#: The live tables outside the enumeration, each with the reason. Absence and oversight
#: are indistinguishable, so the reason is written down.
NOT_DERIVED: Mapping[str, str] = MappingProxyType({
    "events": (
        "append-only forever (R6, §8.2, D3). Three triggers and an authorizer hook "
        "enforce it, and §8.4's retraction limit is unsatisfiable without the log."
    ),
    "files": (
        "`sensitivity_state` is a projection of P7's authoritative ClassificationRecord "
        "(D2). The supported user act is reclassification, which supersedes."
    ),
    "extraction_runs": (
        "the record THAT a run happened, not what it read. §2.4 distinguishes an empty "
        "extraction result from an extractor that does not yet exist, and dropping the "
        "run row collapses the two."
    ),
    "exclusion_verdicts": (
        "P3's refusal record. Deleting it deletes the evidence that a refusal occurred, "
        "which is the whole record a protected container leaves behind (11 §4b)."
    ),
})


def revoke(conn: sqlite3.Connection, policy: Policy, scope: str, *, user_id: str,
           component_version: str, observed_at: str, retraction_limit: str,
           files_in_scope: Callable[[str], Sequence[str]]) -> RevocationResult:
    """Withdraw consent for `scope`, forward only, and say what already left.

    `files_in_scope` has no default. Open question 3 -- "What is a 'corpus area'? ...
    Consent grants cannot be scoped until this is named" -- is unanswered, so the
    resolver is the caller's and P7 defines no area.

    `retraction_limit` has no default either, and for the opposite reason: §8.4 makes
    the statement mandatory and the SPEC defers its wording, so presence is enforced
    here and the words come from P13.
    """
    if not retraction_limit or not retraction_limit.strip():
        raise MissingRetractionLimit(
            "§8.4: revocation 'cannot necessarily retract data already sent to an "
            "external provider, so the product must communicate that distinction "
            "clearly' -- an empty statement does not communicate it"
        )
    new_version = revoke_consent(conn, policy, scope, user_id=user_id,
                                 component_version=component_version,
                                 observed_at=observed_at)
    prior = _prior_releases(conn, files_in_scope(scope))
    append_event(conn, **event_defaults(
        event_type=CONSENT_REVOKED,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "scope": scope,
            "revoked_policy_version": policy.policy_version,
            "policy_version": new_version,
            "effective_from": observed_at,
            "prior_release_count": len(prior),
            "retraction_limit": retraction_limit,
        }),
    ))
    return RevocationResult(effective_from=observed_at, prior_releases=prior,
                            retraction_limit=retraction_limit)


def _prior_releases(conn: sqlite3.Connection,
                    file_ids: Sequence[str]) -> tuple[PriorRelease, ...]:
    """Every release in scope, oldest first, read out of the one audit log.

    Not filtered to the revoked policy version. §8.4's purpose is to tell the user what
    has already been sent; a list narrowed to one version answers a different question,
    and each record carries `policy_version` for a reader who wants it.
    """
    found: list[tuple[str, int, PriorRelease]] = []
    for file_id in file_ids:
        for record in audit_records_for(conn, file_id=file_id):
            if record.outcome != RELEASED:
                continue
            target = record.model
            found.append((record.observed_at, int(record.audit_id), PriorRelease(
                model=target["model_id"],
                provider=target["provider"],
                when=record.observed_at,
                excerpts=tuple(tuple(pair) for pair in record.excerpts_included),
            )))
    found.sort(key=lambda item: (item[0], item[1]))
    return tuple(entry for _, _, entry in found)


def delete_derived(scope: DerivedScope) -> NoReturn:
    """§8.4's "review and delete local derived data" -- surfaced, and unbuilt (D3, I6).

    Raises `ScopeNotDerived` for anything outside `DERIVED_PROJECTIONS` and
    `UnratifiedResolution` for anything inside it. There is no third branch: no
    tombstone column exists, this function writes nothing, and P13 is the part that
    will drive the migration that gives it one.
    """
    columns = DERIVED_PROJECTIONS.get(scope.table)
    if columns is None or scope.column not in columns:
        reason = NOT_DERIVED.get(scope.table)
        enumerated = {table: list(cols)
                      for table, cols in DERIVED_PROJECTIONS.items()}
        raise ScopeNotDerived(
            f"{scope.table}.{scope.column} is not in D3's enumerated derived list "
            f"{enumerated}" + (f"; {reason}" if reason else "")
        )
    raise UnratifiedResolution(
        f"{scope.table}.{scope.column} is derived (D3), and no tombstone column is "
        "built. D3, ratified 2026-08-21, settled the direction and deliberately built "
        "nothing until P13 drives it; I6 named the §8.4-versus-§8.2 conflict it "
        "resolves. Deletion later is always available; un-deletion never is."
    )
