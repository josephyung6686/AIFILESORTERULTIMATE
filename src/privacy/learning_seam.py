# src/privacy/learning_seam.py
"""§8.7's query-before-classify, and reclassification as supersession.

Two directions across one seam. Reading: before the product assigns a handling class
it asks P1 whether the user has already rejected that class for that file, because
10-i4-learning-ops.md puts P7 in the query-before-propose table -- "Before assigning a
handling class the user has already set or rejected at this scope | Do not re-prompt
the same classification". Writing: a user reclassification is a new `user_confirmed`
fact that supersedes the prior one and leaves a negative example behind, because §8.7
requires rejections be "stored with the evidence that produced them".

P1's `learning_records(conn, scope, subject_id)` filters on `correction_scope`,
`correction_subject` and `user_id IS NOT NULL` and nothing else. `proposal_class` and
`basis_key` filtering is the acting part's, by 10-i4's own assignment, so it happens
here.

**Suppression guards `assign` and never `reclassify`.** What is suppressed is the
product re-proposing, not the user acting. A `reclassify` that consulted the
suppression store would refuse the user's own correction on the grounds that they had
already made it.

**The projection is `classification_store.mirror`, imported.** D2's write-through to
`files.sensitivity_state` already has a home; a private copy here would be a second
place for one rule to live, which is the defect the preamble's §3.4 names.

**A broader `correction_scope` is written and never read.** `reclassify` stores
whichever of §8.7's six scopes the caller passes; `suppressed` reads `file` only.
Widening it would answer Open question 7 -- whether repeated privacy corrections may
raise a sensitivity floor for a class of files -- and that ruling is not this module's.
The behaviour is pinned by a test rather than left to be discovered.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence
from types import MappingProxyType

from database_agent.events import CORRECTION_SCOPES, append_event
from database_agent.learning import learning_records

from evidence_shape.canonical import canonical_json

from privacy.authorship import (
    CLASSIFICATION_ASSIGNED, CLASSIFICATION_SUPERSEDED, event_defaults,
)
from privacy.classification import ClassificationRecord
from privacy.classification_store import ClassificationStore, mirror
from privacy.vocabulary import USER, USER_CONFIRMED, check_handling_class

#: 10-i4-learning-ops.md's table: `privacy` | `(file_id, handling_class)` | P7.
PROPOSAL_CLASS: str = "privacy"

#: §8.7's default, and the only scope this module supplies. "one particular transcript
#: belongs in a Columbia packet but should not teach the engine that all transcripts
#: belong there."
FILE_SCOPE: str = "file"

#: 10-i4: `polarity` is supplied by the acting part and never inferred.
ACCEPT: str = "accept"
REJECT: str = "reject"

#: SPEC *Correction learning*, "Recorded actions". The identifiers are P7's; the
#: phrases are the SPEC's, held beside them so a later paraphrase is a failing test.
RECORDED_ACTIONS: tuple[str, ...] = (
    "reclassify_private",
    "mark_private_residual_review",
    "downgrade_classification",
    "set_policy",
    "change_redaction_setting",
    "set_automatic_move_permission",
)

RECORDED_ACTION_SOURCES: Mapping[str, str] = MappingProxyType({
    "reclassify_private": "reclassifying a file as private",
    "mark_private_residual_review": "mark it as private",
    "downgrade_classification": "downgrading a classification",
    "set_policy": "granting, changing, or revoking a policy",
    "change_redaction_setting": "changing a redaction setting",
    "set_automatic_move_permission":
        "granting or withdrawing an automatic-move permission for protected material",
})


class UnknownRecordedAction(ValueError):
    """A §8.7 action outside the SPEC's six. A value outside the set is a load error."""


def check_recorded_action(value: str) -> str:
    if value not in RECORDED_ACTIONS:
        raise UnknownRecordedAction(
            f"{value!r} is not one of SPEC Correction learning's six recorded actions "
            f"{RECORDED_ACTIONS}")
    return value


def basis_key_for(file_id: str, handling_class: str) -> str:
    """10-i4's `basis_key` for `proposal_class = privacy`: `(file_id, handling_class)`.

    P1 stores `basis_key` as one opaque TEXT column, so the pair is composed here as
    canonical JSON -- the same encoding P4 uses for its own comparable bytes, so two
    parts never disagree about how a tuple becomes a string.
    """
    return canonical_json([file_id, handling_class])


def suppressed(conn: sqlite3.Connection, file_id: str, handling_class: str) -> bool:
    """Has the user rejected this exact classification for this file, unreset?

    P1's reader already honours a later `reset_preferences` as a cutoff, so a reset
    restores emission without anything being deleted (R6).
    """
    key = basis_key_for(file_id, handling_class)
    for row in learning_records(conn, FILE_SCOPE, file_id):
        if row["proposal_class"] != PROPOSAL_CLASS:
            continue                                     # 10-i4 rule 1
        if row["basis_key"] != key:
            continue                                     # 10-i4 rule 2
        if row["polarity"] == REJECT:                    # 10-i4 rule 4
            return True
    return False


def assign(conn: sqlite3.Connection, record: ClassificationRecord, *,
           store: ClassificationStore,
           component_version: str) -> ClassificationRecord | None:
    """The system-side write, guarded by §8.7. Returns None when suppressed.

    None is the zero re-emission 10-i4's Done-means requires: "a fixture with one
    unresected reject at the stated `basis_key` produces zero re-emissions of that
    proposal". Nothing is written and no event is appended, so the log shows the
    proposal was not made rather than that it was made and hidden.

    This appends no `correction_*` field and no `user_id`, so a system assignment can
    never become the learning record that suppresses the next one -- P1's reader
    requires `user_id IS NOT NULL`.
    """
    check_handling_class(record.handling_class)
    if suppressed(conn, record.file_id, record.handling_class):
        return None
    store.write(record)
    mirror(conn, record, component_version=component_version)
    append_event(conn, **event_defaults(
        event_type=CLASSIFICATION_ASSIGNED,
        file_id=record.file_id,
        content_hash=record.content_hash,
        component_version=component_version,
        observed_at=record.observed_at,
        explanation=canonical_json({
            "handling_class": record.handling_class,
            "protected": record.protected,
            "basis": record.basis,
            "reliability_state": record.reliability_state,
            "evidence_refs": list(record.evidence_refs),
        }),
    ))
    return record


def reclassify(conn: sqlite3.Connection, file_id: str, handling_class: str,
               reason: str, *, store: ClassificationStore, content_hash: str,
               protected: bool, evidence_refs: Sequence[str], user_id: str,
               component_version: str, observed_at: str,
               correction_scope: str = FILE_SCOPE) -> ClassificationRecord:
    """§8.4's "can be revised by the user", as a supersession and a negative example.

    `protected` is a parameter and is never derived from `handling_class`. Open
    question 1 -- "Is `protected` exactly the top two handling classes?" -- is
    unsettled, and SPEC §2 says outright: "Neighbouring parts should consume the
    `protected` flag, not infer it from the class."

    `evidence_refs` carries P4 `observation_key` values (M14) -- the keys the detector
    fired on. They land on the new record and are echoed into the superseding event so
    §8.7's "stored with the evidence that produced them" has somewhere to be true.

    One event per act, and the event is the rejection. Over an existing classification
    that is one `classification_superseded` at the PRIOR class's basis key; over
    nothing it is one `classification_assigned` at the new class's. There is no
    accept-and-reject pair: 10-i4 rule 4 makes an accept at the same key not a
    suppression, so the second row would change nothing and give the two somewhere to
    disagree.
    """
    check_handling_class(handling_class)
    if not reason or not reason.strip():
        raise ValueError(
            "§8.2 retains 'the old observation and the reason it was superseded'; a "
            "revision without a reason cannot satisfy it")
    if correction_scope not in CORRECTION_SCOPES:
        raise ValueError(
            f"correction_scope {correction_scope!r} is not one of §8.7's six "
            f"{tuple(sorted(CORRECTION_SCOPES))}")
    prior = store.current(file_id, content_hash)
    prior_fact_id = store.current_fact_id(file_id, content_hash)
    record = ClassificationRecord(
        file_id=file_id, content_hash=content_hash, handling_class=handling_class,
        protected=protected, basis=USER, evidence_refs=tuple(evidence_refs),
        reliability_state=USER_CONFIRMED, observed_at=observed_at)
    fact_id = store.write(record)
    if prior is not None and prior_fact_id is not None:
        store.supersede(prior_fact_id, fact_id, reason)
    mirror(conn, record, component_version=component_version)

    if prior is None:
        event_type, polarity, subject = CLASSIFICATION_ASSIGNED, ACCEPT, handling_class
    else:
        event_type, polarity, subject = (
            CLASSIFICATION_SUPERSEDED, REJECT, prior.handling_class)
    append_event(conn, **event_defaults(
        event_type=event_type,
        file_id=file_id,
        content_hash=content_hash,
        user_id=user_id,
        component_version=component_version,
        observed_at=observed_at,
        explanation=canonical_json({
            "handling_class": handling_class,
            "protected": protected,
            "reason": reason,
            "superseded_handling_class":
                None if prior is None else prior.handling_class,
            "rejected_evidence_refs": list(evidence_refs),
        }),
        correction_scope=correction_scope,
        correction_subject=file_id,
        polarity=polarity,
        proposal_class=PROPOSAL_CLASS,
        basis_key=basis_key_for(file_id, subject),
    ))
    return record
