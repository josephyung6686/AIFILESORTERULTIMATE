"""P7's state, carried; §8.4's consequence for placement, derived here.

P11 reclassifies nothing. `handling_class` and `protected` come from P7's
`ClassificationRecord`, which D2 made authoritative, and the operation mode comes
from P7's `Policy`. An absent classification blocks: P7's detector is behind an
injection nothing produces yet, so on a real corpus every file resolves to
`unreadable_unclassified`, and treating that as "probably fine" is the one failure
§8.4 exists to prevent.

`model_eligibility` is DERIVED rather than read, because §8.4's three values have
no producer in `src/privacy/` at all. Every input to the derivation is a live P7
authority rather than a P11 restatement of one:

* the mode gate is `privacy.denial.mode_forbids`, so if P7 ever moves a mode
  across the line P11 moves with it;
* the protected gate is P7's `ClassificationRecord.protected` FLAG, never the
  class -- Open question 1 leaves the relation between them unsettled and says in
  terms that neighbouring parts consume the flag and do not infer it;
* the unclassified case needs no gate at all, and that is a live fact rather
  than an omission: `ClassificationStore.write` REFUSES `unreadable_unclassified`
  because it is a gate outcome and absence already carries it (D2). A branch here
  comparing `record.handling_class` against it could never fire, so the absence
  branch above is not the first of two paths -- it is the only one.

Two things §8.4 keeps apart, and this module keeps apart with it. **Model
eligibility is about egress; the review policy is about a MOVE.** Design:185 --
protected material "should not be moved automatically without a user policy that
explicitly permits it" -- keys the move on the flag, and `offline` (one of the two
modes that may ship as the install default) makes every file local_only. Reading
local_only as "review everything" would leave §6.6's deterministic path dead on
every default install while protecting nothing extra.

**§7.4's residual disposition is read here too**, and it is a different question
from §8.4's. `IndexEntry.disposition` was written and validated by
`placement/index.py` and read by nothing; P10 escalated that as an open cross-part
question rather than settling it alone, because the field holds the only thing that
stops an automatic file move. 00:121 decides the shape: all three dispositions
"become legal nodes in the frozen destination tree" and "the LLM may choose among
them later", so the disposition does not govern WHETHER a node may be chosen --
`accepts_placement` remains the one legality authority, and a second gate here
would be exactly the two-callables-one-question defect `index.py` warns about. It
governs WHAT HAPPENS when a node IS chosen, which is this module's business.

The move permission itself is not re-derived here either: P7 publishes
`privacy.moves.may_move_automatically`, which already checks absence before the
flag and reads the policy at the asked-for plan version. `automatic_move_permitted_for`
is a one-line binding to it, so P11 never touches the key space of
`Policy.automatic_move_permissions` and cannot key it on the wrong thing.
"""
from __future__ import annotations

import sqlite3

from privacy.classification_store import ClassificationStore
from privacy.denial import mode_forbids
from privacy.moves import may_move_automatically
from privacy.policy import current_policy
from privacy.release import LOCALITIES

from placement.records import PrivacyState, USER_ATTACHED
from placement.vocabulary import (
    AUTO_ELIGIBLE, BLOCKED_PENDING_USER, DISPOSITIONS, DOSSIER_PERMITTED,
    LEAVE_IN_PLACE_DISPOSITION, LOCAL_ONLY, PHYSICAL_DESTINATION, REVIEW_ONLY,
    REVIEW_REQUIRED, check,
)

#: The locality every §8.4 question in this module is asked about. `local` is the
#: other member and P11 never asks about it: a local model call is Open question 6
#: and P7 owns the answer.
CLOUD: str = "cloud"
assert CLOUD in LOCALITIES

class ClassificationRequired(RuntimeError):
    """No P7 classification for this file version. Never defaulted to public."""


class PolicyRequired(RuntimeError):
    """No P7 policy in force for this plan version. Never assumed."""


def privacy_state_for(conn: sqlite3.Connection, *, file_id: str,
                      content_hash: str, plan_version: str) -> PrivacyState:
    """P7's answer for one file version, carried onto P11's record unchanged."""
    record = ClassificationStore(conn).current(file_id, content_hash)
    if record is None:
        raise ClassificationRequired(
            f"no P7 classification for ({file_id!r}, {content_hash!r}); §8.4 puts "
            "the gate before every dossier, and an unclassified file is blocked "
            "rather than presumed low-sensitivity"
        )
    policy = current_policy(conn, plan_version=plan_version)
    if policy is None:
        raise PolicyRequired(
            f"no P7 policy in force for {plan_version!r}; the operation mode "
            "decides whether anything may leave the device and P11 assumes none"
        )
    local_only = mode_forbids(policy.operation_mode, CLOUD) or record.protected
    return PrivacyState(
        handling_class=record.handling_class,
        protected=record.protected,
        model_eligibility=LOCAL_ONLY if local_only else DOSSIER_PERMITTED,
        consent_audit_ref=None,
    )


def may_assemble_dossier(privacy_state: PrivacyState) -> bool:
    """§8.4's gate, asked before the dossier exists rather than after it is built."""
    return privacy_state.model_eligibility != LOCAL_ONLY


def automatic_move_permitted_for(conn: sqlite3.Connection, *, file_id: str,
                                 plan_version: str) -> bool:
    """P7's own §8.4 move predicate, asked rather than re-derived.

    A caller reads this once per file and hands the answer to `review_policy_for`.
    Keeping the read here is what stops P11 from ever looking inside
    `Policy.automatic_move_permissions`, whose keys are file ids and whose shape
    is P7's to change.
    """
    return may_move_automatically(conn, file_id, plan_version).allowed


#: Whether a destination with this §7.4 disposition moves a file at all. A
#: residual node the user made a real physical destination does; a review-only
#: category and a leave-in-place policy do not. `None` is the ordinary case --
#: §7.4 makes the disposition required on a residual node and meaningless on every
#: other role, which `placement/index.py` enforces at build time.
_MOVES_FILES: dict[str | None, bool] = {
    None: True,
    PHYSICAL_DESTINATION: True,
    REVIEW_ONLY: False,
    LEAVE_IN_PLACE_DISPOSITION: False,
}


def moves_files(disposition: str | None) -> bool:
    """Does a destination carrying this §7.4 disposition move the file?

    00:120 makes the negative answer a first-class outcome rather than a failure:
    `Unsupported or Encrypted` may "hold -- or, more safely, represent without
    moving -- password-protected archives, unreadable documents, damaged files,
    and unknown formats". A file represented at a node it was never moved to is
    present-but-untouched, which is what the standing rule about protected
    material requires and what a silent omission would destroy.

    A value outside the closed set raises. Answering it through a permissive
    default would make a misspelling mean "yes, move it", which is the one answer
    this predicate must never give by accident.
    """
    if disposition is not None:
        check(disposition, DISPOSITIONS, name="disposition")
    return _MOVES_FILES[disposition]


def review_policy_for(*, privacy_state: PrivacyState, two_condition,
                      group_support, unique_direct_match: bool,
                      destination_disposition: str | None,
                      automatic_move_permitted: bool = False) -> str:
    """§6.11's review policy. Every path to `auto_eligible` is a narrow one.

    Five things each forbid it on their own, and every one traces to a design
    sentence: a destination whose §7.4 disposition does not move files (00:121 --
    a review-only category "never moves files automatically"), material the user
    marked protected without a policy permitting the move (Design:185, §8.4), a
    verdict that requires review (§6.10), a manual attachment with nothing read
    from the file (M12), and a decision that is not a unique direct match (§6.6's
    deterministic path is the only one the design lets through unreviewed).

    The disposition is checked FIRST and no confidence clears it. That ordering is
    the point: 00:121's word is "never", and a gate placed after the scoring
    checks would be one a high enough score could reason its way past.

    `destination_disposition` has no default. A caller that forgot it would get
    the ordinary-node answer and silently lose the gate, which is precisely the
    state this field was already in -- written, validated, and read by nothing.

    `automatic_move_permitted` is a parameter rather than a read because the
    permission is a fact about the file and this function takes no connection;
    `automatic_move_permitted_for` above is where it comes from.
    """
    if not moves_files(destination_disposition):
        return REVIEW_REQUIRED
    if privacy_state.protected and not automatic_move_permitted:
        return REVIEW_REQUIRED
    if two_condition.requires_review:
        return REVIEW_REQUIRED
    if group_support is not None and group_support.membership == USER_ATTACHED:
        return REVIEW_REQUIRED
    if not unique_direct_match:
        return REVIEW_REQUIRED
    return AUTO_ELIGIBLE


def blocked_policy() -> str:
    """The policy for a decision whose subject P7 has not classified.

    Distinct from `review_required` on purpose: a reviewer can act on a decision
    that merely needs confirming, and cannot act on one whose subject nothing has
    classified. Collapsing the two would put an unclassified file in the ordinary
    approve queue.
    """
    return BLOCKED_PENDING_USER
