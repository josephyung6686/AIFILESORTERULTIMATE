"""§8.4's eight refusals -- and the one that is the ordinary case.

The detector is unwritten (D2). No task in any plan produces a rule set, so against a
real corpus `Gate.release` is asked about a file with no `ClassificationRecord`,
`resolve_class(None)` returns `unreadable_unclassified`, and the call is denied. That
is not a degraded mode. It is what a correct locked door does when nobody has been
given a key, and this module is written for it: `unclassified` carries the longest
explanation and the most remedies, because it is what the audit log will be full of.

Three things are decided here:

- **The eight reasons have a total order** (`DENIAL_ORDER`), because four of them
  overlap on real inputs and SPEC §6 requires one answer. The ordering principle is
  `DECIDABLE_FROM_REQUEST`: no denial that can be decided from the request alone may
  be decided after one that requires reading the file. A gate that materialised an
  excerpt and then discovered the mode forbade the call has read a sensitive file for
  a call that was never going to happen.
- **The builders are pure and the append is one function.** SPEC §7: "Denials and
  consent requests are also appended." The record needs the request and the policy,
  which a builder does not see; a builder that took them would compose §7's record
  eight times over, and Task 10 owns it once.
- **`unreadable_unclassified` goes in `AuditRecord.file_sensitivity` and nowhere
  else.** D2: it "lives on the release decision and never in that column, so 'nothing
  has looked' can never be read as 'this file carries nothing'." This module issues no
  `UPDATE files`.

It owns no detection rule, no numeric ceiling and no remedy vocabulary. The class of a
file arrives as a `ClassificationRecord`; the ceiling arrives from
`database_agent.budget.get_ceiling`; the remedies are composed per denial from the
design's own sentences, because §8.6 names four ladder rungs for one situation and
§8.4 names four consent options for another, and one enumeration over both would
invent a fifth thing no section states.
"""
from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from database_agent.budget import get_ceiling

from privacy.audit import AUDIT_FIELDS, AuditRecord, append_audit
from privacy.authorship import CONSENT_REVOKED, SUBSYSTEM
from privacy.classification import ClassificationRecord, resolve_class
from privacy.items import AlwaysLocalRequested, WholeDocumentRequested
from privacy.policy import Policy
from privacy.release import Denied
from privacy.vocabulary import check_denial_reason

#: §7.3's literal template name, the one residual-library name P7 uses.
PROTECTED_RECORDS_TEMPLATE: str = "Protected Records"

#: The key Task 15's `revoke` writes into the `consent_revoked` explanation. Pinned so
#: a rename on either side is a red test rather than a denial that stops firing.
REVOKED_SCOPE_KEY: str = "scope"

#: P1's key for §8.6's dossier ceiling. The VALUE is never P7's -- SPEC Deferred puts
#: "Numeric values for every ceiling" outside this contract.
_DOSSIER_CEILING_KEY: str = "model.max_dossier_tokens_per_call"

#: The eight, in evaluation order. See the module docstring for each position.
DENIAL_ORDER: tuple[str, ...] = (
    "mode_forbids_target",
    "policy_revoked",
    "always_local_item",
    "unclassified",
    "protected_records_template",
    "protected_cloud_target",
    "whole_document_requested",
    "dossier_over_budget",
)

#: The six decidable from the request, the policy and a row lookup. The other two need
#: the resolved text, and every member of this set precedes both of them.
DECIDABLE_FROM_REQUEST: frozenset[str] = frozenset({
    "mode_forbids_target",
    "policy_revoked",
    "always_local_item",
    "unclassified",
    "protected_records_template",
    "protected_cloud_target",
})

#: §8.4's two modes under which no content leaves the device.
_LOCAL_ONLY_MODES: tuple[str, str] = ("offline", "local_model")


class MalformedDenial(ValueError):
    """A denial missing its explanation or its remedy.

    §8.6 requires the UI to show "what has been deferred, and why", and a denial with
    no legitimate alternative is a dead end the user cannot act on.
    """


@dataclass(frozen=True)
class RemedyOption:
    """One thing the caller may legitimately do instead (SPEC §6, §8.6).

    Not a closed vocabulary, deliberately. `action` is a short identifier for the
    surface to key on and `detail` is the sentence it came from.
    """

    action: str
    detail: str


def deny(reason: str, *, explanation: str,
         remedy_options: Sequence[RemedyOption],
         evidence_refs: Sequence[str]) -> Denied:
    """Build one refusal, validated.

    `evidence_refs` carries whatever the classification carried. M14's key-versus-id
    rule is Task 3's, on `ClassificationRecord.evidence_refs`; a second copy of it
    here would be a second place for it to drift.
    """
    check_denial_reason(reason)
    if not explanation or not explanation.strip():
        raise MalformedDenial(
            f"{reason}: SPEC §6 requires the explanation be 'user-facing, "
            "evidence-referenced'; an empty one is neither"
        )
    if not remedy_options:
        raise MalformedDenial(
            f"{reason}: §8.6 requires the product show 'what has been deferred, and "
            "why'. A denial with no legitimate alternative is a dead end"
        )
    refs = tuple(evidence_refs)
    if any(not isinstance(ref, str) or not ref for ref in refs):
        raise MalformedDenial(f"{reason}: every evidence ref must be a non-empty key")
    return Denied(reason=reason, explanation=explanation,
                  remedy_options=tuple(remedy_options), evidence_refs=refs)


def first_reason(reasons: Iterable[str]) -> str | None:
    """The highest-precedence reason among those that fired, or None.

    SPEC §6 gives one `reason`, and four of the eight overlap on real inputs, so the
    gate needs a total order rather than whichever check happened to run first.
    """
    triggered = {check_denial_reason(reason) for reason in reasons}
    for reason in DENIAL_ORDER:
        if reason in triggered:
            return reason
    return None


# --- the six decidable from the request -------------------------------------

def mode_forbids(operation_mode: str, locality: str) -> bool:
    """§8.4: under `offline` and `local_model`, no content leaves the device.

    A LOCAL model is permitted under both -- "only local rules and local models may
    run" -- so this refuses the target's locality, never the call.
    """
    return locality == "cloud" and operation_mode in _LOCAL_ONLY_MODES


def policy_revoked_for(conn: sqlite3.Connection, policy: Policy, scope: str) -> bool:
    """Granted and then withdrawn -- not "never granted", which is a different reason.

    Two-sided on purpose: a re-grant puts the scope back in `policy.consent_grants`
    and this stops firing, which is what makes revocation forward-only rather than
    permanent (§8.4: "revoke a policy for future runs").
    """
    if any(granted == scope for granted, _option in policy.consent_grants):
        return False
    for row in conn.execute(
            "SELECT explanation FROM events WHERE event_type = ?", (CONSENT_REVOKED,)):
        payload = json.loads(row["explanation"])
        if payload.get(REVOKED_SCOPE_KEY) == scope:
            return True
    return False


def unclassified_denies(*, locality: str, local_calls_on_unclassified: bool) -> bool:
    """§8.4 makes classification a precondition of escalation.

    `local_calls_on_unclassified` has NO default. Open question 5: "Does
    `unreadable_unclassified` permit a LOCAL model call? ... Reading escalation
    strictly denies local calls on unclassified files, which may block exactly the
    OCR-opaque screenshots §2.7 and §7.8 want a model to interpret." Unanswered, so
    the caller answers it and P7 names no winner.
    """
    if locality == "cloud":
        return True
    return not local_calls_on_unclassified


def is_protected_records(template_name: str | None) -> bool:
    """§7.3's carve-out, and it binds local calls too."""
    return template_name == PROTECTED_RECORDS_TEMPLATE


def protected_cloud_denies(*, protected: bool, locality: str, operation_mode: str,
                           scope: str, granted_scopes: Sequence[str]) -> bool:
    """SPEC §2's first protected consequence: "not included in cloud-model prompts BY
    DEFAULT" -- and `cloud_assisted` plus an explicit grant is the carve-out.

    §8.4: "Cloud-assisted mode: User explicitly permits selected corpus areas to use a
    cloud model." What a "corpus area" is stays Open question 3, so `scope` is an
    opaque string the caller supplies and P7 resolves none.
    """
    if not protected or locality != "cloud":
        return False
    if operation_mode == "cloud_assisted" and scope in tuple(granted_scopes):
        return False
    return True


# --- the two that need the resolved content ---------------------------------

def over_dossier_ceiling(conn: sqlite3.Connection, *, measured_tokens: int) -> bool:
    """M9's backstop. An UNSET ceiling cannot deny.

    `get_ceiling` returns `int | None` and `None` is the ordinary state. P7 owns no
    number, so with nothing configured there is nothing to exceed. `measured_tokens`
    is the caller's -- P7 has no tokenizer and inventing one would invent a number.
    Reads P1's stored ceiling and never `request.max_dossier_tokens`, which is "the
    caller's echo of it (M9)": a caller must not raise its own ceiling by echoing a
    larger one.
    """
    ceiling = get_ceiling(conn, _DOSSIER_CEILING_KEY)
    if ceiling is None:
        return False
    return measured_tokens > ceiling


# --- the eight builders -----------------------------------------------------

def deny_mode_forbids_target(*, operation_mode: str, model_target,
                             file_ids: Sequence[str]) -> Denied:
    return deny(
        "mode_forbids_target",
        explanation=(
            f"the operation mode is {operation_mode!r} and the request targets a "
            f"{model_target.locality} model ({model_target.provider}/"
            f"{model_target.model_id}). §8.4: under fully offline mode 'No content "
            "leaves the device; only local rules and local models may run.' "
            f"{len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("use_local_model",
                         "§8.4: local rules and local models may run under this mode"),
            RemedyOption("change_operation_mode",
                         "§8.4's four modes are the user's to choose; the default is "
                         "local-first and changing it is an explicit act (W1)"),
        ),
        evidence_refs=(),
    )


def deny_policy_revoked(*, scope: str, policy: Policy,
                        file_ids: Sequence[str]) -> Denied:
    return deny(
        "policy_revoked",
        explanation=(
            f"consent for {scope!r} was granted and then withdrawn; policy "
            f"{policy.policy_version} carries no grant for it. §8.4 gives the user "
            "the right to 'revoke a policy for future runs', and this is a future "
            f"run. {len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("grant_consent",
                         "§8.4's four options are offered again through P13 -- offered, "
                         "not re-proposed: §8.7 stores the withdrawal as negative "
                         "feedback so the same proposal does not resurface by itself"),
            RemedyOption("use_local_model",
                         "§8.4: a local model is one of the four consent options"),
            RemedyOption("do_not_repropose",
                         "§8.7: the withdrawal is negative feedback, so the same "
                         "proposal does not resurface by itself"),
        ),
        evidence_refs=(),
    )


def deny_always_local_item(caught: AlwaysLocalRequested, *,
                           file_ids: Sequence[str]) -> Denied:
    """Task 7's construction-time refusal, translated into the gate's answer.

    The nine names live in `vocabulary.ALWAYS_LOCAL` and the refusal in `items`. A
    builder that re-decided which of them are always-local would be a second copy of
    §8.4's list.
    """
    return deny(
        "always_local_item",
        explanation=(
            f"{caught}. §8.4: 'Paths, complete extracted text, OCR output, file "
            "hashes, image EXIF, GPS, user edits, group memberships, and raw "
            "sensitive values should remain local.' Nothing in that set can be named "
            f"as a releasable item kind. {len(tuple(file_ids))} file(s) were not "
            "released."
        ),
        remedy_options=(
            RemedyOption("request_excerpt",
                         "§8.4's compact dossier: 'selected excerpts, redacted "
                         "identifiers, candidate labels, non-sensitive metadata, and "
                         "evidence references'"),
        ),
        evidence_refs=(),
    )


def deny_unclassified(*, file_ids: Sequence[str], locality: str,
                      completeness: str | None) -> Denied:
    """The ordinary denial. No detector exists (D2), so this is the normal path.

    The explanation says `unreadable_unclassified` and never `public_low`: SPEC §1's
    "Absence of a classification resolves to `unreadable_unclassified`, never to
    `public_low`", which is §8.6's "Cost exhaustion must never turn into
    lower-quality automatic classification" applied to the one case that matters.
    """
    seen = ("no extraction run has completed for it"
            if completeness is None else f"its extraction completeness is {completeness!r}")
    return deny(
        "unclassified",
        explanation=(
            f"{len(tuple(file_ids))} file(s) resolve to handling class "
            "'unreadable_unclassified': no classification record exists and "
            f"{seen}. §8.4 requires the system to 'classify data into handling "
            "classes before LLM escalation', so an unclassified file has not met the "
            f"precondition for a {locality} model call. Absence of a classification "
            "is not evidence that the file carries nothing, and it never resolves to "
            "a lower class so the pipeline can continue."
        ),
        remedy_options=(
            RemedyOption("classify",
                         "§8.4: the classification 'is itself evidence-backed and can "
                         "be revised by the user'; a user may set one directly"),
            RemedyOption("defer",
                         "§8.6: 'retain extracted evidence, mark the deferred stage, "
                         "and leave the file or group in review rather than guessing'"),
            RemedyOption("review",
                         "§8.6: the user 'should be able to see what is running, what "
                         "has been deferred, and why'"),
        ),
        evidence_refs=(),
    )


def deny_protected_records_template(*, file_ids: Sequence[str],
                                    model_target) -> Denied:
    """§7.3, and it binds a LOCAL target too -- which is why it outranks the cloud rule."""
    return deny(
        "protected_records_template",
        explanation=(
            f"{len(tuple(file_ids))} file(s) are held under the "
            f"{PROTECTED_RECORDS_TEMPLATE!r} residual template. §7.3: it 'should "
            "normally remain local-only and must not cause filenames or content to "
            "be exposed in model prompts.' That binds every model, so the "
            f"{model_target.locality} target does not change the answer."
        ),
        remedy_options=(
            RemedyOption("decide_locally",
                         "§7.3: normally local-only; deterministic rules and local "
                         "placement still apply"),
            RemedyOption("review",
                         "§7.11: the system must not 'move them out of a protected "
                         "area without explicit user action'"),
        ),
        evidence_refs=(),
    )


def deny_protected_cloud_target(*, file_ids: Sequence[str], operation_mode: str,
                                scope: str,
                                evidence_refs: Sequence[str] = ()) -> Denied:
    return deny(
        "protected_cloud_target",
        explanation=(
            f"{len(tuple(file_ids))} file(s) are protected and the request targets a "
            f"cloud model under mode {operation_mode!r}. §8.4: 'Protected material "
            "should not be included in cloud-model prompts by default', and 'Hybrid "
            f"mode: Sensitive files remain local.' Scope {scope!r} carries no "
            "explicit grant."
        ),
        remedy_options=(
            RemedyOption("use_local_model",
                         "§8.4: 'Local-model mode: Local extraction plus a "
                         "user-installed local LLM for eligible dossiers'"),
            RemedyOption("grant_consent",
                         "§8.4: 'Cloud-assisted mode: User explicitly permits "
                         "selected corpus areas to use a cloud model'"),
        ),
        evidence_refs=evidence_refs,
    )


def deny_whole_document_requested(caught: WholeDocumentRequested, *,
                                  file_ids: Sequence[str]) -> Denied:
    return deny(
        "whole_document_requested",
        explanation=(
            f"{caught}. §8.4: the engine 'should not send full documents where a "
            "short heading or OCR excerpt is enough to resolve the question.' "
            f"{len(tuple(file_ids))} file(s) were not released."
        ),
        remedy_options=(
            RemedyOption("narrow_span",
                         "§8.4's compact dossier is 'selected excerpts' -- a bounded "
                         "span, addressed by (observation_key, span)"),
        ),
        evidence_refs=(),
    )


def deny_dossier_over_budget(*, measured_tokens: int, ceiling: int,
                             file_ids: Sequence[str]) -> Denied:
    """M9's backstop. It should never fire in a correct pipeline. Do not delete it.

    §8.6 forbids a prompt that "truncate[s] silently in a way that removes the
    decisive evidence", and the gate is the last place to catch a caller that skipped
    its ladder. The four remedies ARE that ladder, in §8.6's own order and words.
    """
    return deny(
        "dossier_over_budget",
        explanation=(
            f"the dossier measures {measured_tokens} tokens against a ceiling of "
            f"{ceiling} for {len(tuple(file_ids))} file(s). §8.6's ladder runs in the "
            "caller before the gate is asked (M9); reaching this denial in a running "
            "pipeline is a caller defect, not a gate result. The gate never truncates "
            "and never reduces -- reduction changes what the model sees, which is a "
            "dossier decision."
        ),
        remedy_options=(
            RemedyOption("summarize_deterministic_facts", "§8.6, rung one"),
            RemedyOption("preserve_anchor_excerpts", "§8.6, rung two"),
            RemedyOption("split_the_task", "§8.6, rung three"),
            RemedyOption("defer_the_decision", "§8.6, rung four"),
        ),
        evidence_refs=(),
    )


# --- the one append ---------------------------------------------------------

def record_denial(conn: sqlite3.Connection, denied: Denied, *, request,
                  policy: Policy, classification: ClassificationRecord | None,
                  content_hashes: Sequence[str], user_id: str | None,
                  component_version: str, observed_at: str) -> int:
    """Append the one `model_release_denied` record and return its `audit_id`.

    `file_sensitivity` is computed with `classification.resolve_class`, the same
    function the rest of P7 uses, so the gate outcome is not re-derived. It lands
    HERE -- on the release decision -- and never in `files.sensitivity_state` (D2).

    The `events` table has one `file_id` column, so it carries the id only when the
    call is about exactly one file and `WHERE file_id = ?` therefore never
    over-reports. The full tuple is always in the explanation as `file_ids`.

    SPEC §7 enumerates a RELEASE record, so it has no field for a denial's own
    `reason` and `remedy_options[]`. They go through `append_audit`'s `extra`, into
    the same canonical-JSON `explanation` -- §8.2's "structured explanation or
    evidence reference" slot -- because §8.6 requires the product to show "what has
    been deferred, and why" and there is nowhere else for the why to live.
    """
    file_ids = tuple(request.target.file_ids)
    values = {
        "audit_id": None,
        "release_id": None,
        "policy_version": policy.policy_version,
        "plan_version": policy.plan_version,
        "stage": request.stage,
        "outcome": "denied",
        "operation_mode": policy.operation_mode,
        "authorizing_policy": policy.policy_version,
        "file_sensitivity": resolve_class(classification),
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
        "consent_request_id": None,
        "user_id": user_id,
        "observed_at": observed_at,
        "appended_at": observed_at,
    }
    unfilled = [name for name in AUDIT_FIELDS if name not in values]
    if unfilled:
        raise MalformedDenial(
            f"SPEC §7 names {unfilled} and the denial path has no value for them; a "
            "field Task 10 publishes must be filled at the seam, not defaulted"
        )
    record = AuditRecord(**{name: values[name] for name in AUDIT_FIELDS})
    return append_audit(conn, record, author=SUBSYSTEM,
                        component_version=component_version, extra={
                            "reason": denied.reason,
                            "explanation": denied.explanation,
                            "remedy_options": [option.action
                                               for option in denied.remedy_options],
                            "evidence_refs": list(denied.evidence_refs),
                        })
