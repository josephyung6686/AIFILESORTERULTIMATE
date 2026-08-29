# src/privacy/moves.py
"""§8.4's automatic-move predicate -- one of the two surfaces P7 publishes off the model path.

§8.4's sentence is the whole specification: protected material "should not be included
in cloud-model prompts by default, should not display raw content in general group
summaries, and should not be moved automatically without a user policy that explicitly
permits it." The third clause is this module. §7.11 states the same rule from the
residual side -- the system "must not delete files, mark them disposable, or move them
out of a protected area without explicit user action" -- which is why refusal is the
default branch and permission is the exception.

Four properties are deliberate and each has a test:

- **Absence is checked first.** A file nothing has classified has no `protected` flag,
  and "no flag" must never be read as "flag false". The verdict is
  `unreadable_unclassified`, which is Task 3's value and not a second spelling of it.
  With no detector built (D2) this is the verdict for every file in a real corpus.
- **The flag decides, never the class.** SPEC §2: "Neighbouring parts should consume
  the `protected` flag, not infer it from the class", and Open question 1 -- whether
  `protected` is exactly the top two handling classes -- is unsettled.
- **The policy is read at the asked-for plan version and the classification is not.**
  §8.8: "The evidence database remains shared across plan versions, but the destination
  tree and user policy define which projections are valid in each version", and "A new
  plan should never silently reclassify or move old files."
- **No policy at all is no permission.** `privacy.policy.current_policy` returns
  `Policy | None` and "None is a fact, not a gap" -- on a fresh install nothing has
  been set, and that is the ordinary state rather than an error. §7.11 makes refusal
  the default branch, so absence of a policy joins the refusing branch. W1's
  local-first floor (`privacy.defaults`) is not composed in here because it resolves
  the operation mode and the redaction facets and leaves `automatic_move_permissions`
  empty: routing None through it would reach this same answer by a longer path, and
  would require an `install_mode` this predicate has no way to know.

This module writes nothing (C4). It appends no event, mints no policy version and
issues no `UPDATE files`.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from database_agent.files_table import get_file

from privacy.classification import resolve_class
from privacy.classification_store import ClassificationStore
from privacy.policy import current_policy

#: The file carries no `protected` flag, so §8.4's restriction does not attach.
NOT_PROTECTED: str = "not_protected"

#: Protected, and a user policy at this plan version explicitly permits this file.
POLICY_PERMITS: str = "policy_permits"

#: Protected, and no policy at this plan version permits it. §8.4's default answer.
PROTECTED_WITHOUT_PERMITTING_POLICY: str = "protected_without_permitting_policy"

#: Nothing has classified this file. Bound to Task 3's resolver rather than typed a
#: second time: `privacy.classification` owns the rule that absence resolves here and
#: never to `public_low`, and two literals would be two places for one rule to drift.
UNREADABLE_UNCLASSIFIED: str = resolve_class(None)

#: The four, in the order the predicate decides them (§1: absence, then the flag,
#: then the policy). A closed vocabulary with one home, per §3.1.
MOVE_REASONS: tuple[str, ...] = (
    UNREADABLE_UNCLASSIFIED,
    NOT_PROTECTED,
    POLICY_PERMITS,
    PROTECTED_WITHOUT_PERMITTING_POLICY,
)


@dataclass(frozen=True)
class MoveVerdict:
    """SPEC §9's return: `{ allowed, reason, permitting_policy? }`.

    `permitting_policy` is populated only when a policy permitted the move, and it
    carries the `policy_version` the gate minted. P11 records it in the placement
    decision (§6.11 "required review policy") and P12 in the plan precondition (§8.3
    "Sensitivity and consent state"); neither re-derives the answer, and neither can
    record a permission that did not exist, because a refusal names none.
    """

    allowed: bool
    reason: str
    permitting_policy: str | None


def may_move_automatically(conn: sqlite3.Connection, file_id: str,
                           plan_version: str) -> MoveVerdict:
    """May P11/P12 move this file without asking the user, under this plan version?

    Reads only. The branch order is absence, then the flag, then the policy, and it
    is not interchangeable: checking the flag first would answer `not_protected` for
    every file in a corpus nothing has classified, which is §8.6's forbidden move --
    cost exhaustion "must never turn into lower-quality automatic classification" --
    reached from a different direction.
    """
    content_hash = get_file(conn, file_id)["content_hash"]
    record = ClassificationStore(conn).current(file_id, content_hash)
    if record is None:
        return MoveVerdict(allowed=False, reason=UNREADABLE_UNCLASSIFIED,
                           permitting_policy=None)
    if not record.protected:
        return MoveVerdict(allowed=True, reason=NOT_PROTECTED,
                           permitting_policy=None)
    policy = current_policy(conn, plan_version=plan_version)
    if policy is not None and policy.automatic_move_permissions.get(file_id) is True:
        return MoveVerdict(allowed=True, reason=POLICY_PERMITS,
                           permitting_policy=policy.policy_version)
    return MoveVerdict(allowed=False, reason=PROTECTED_WITHOUT_PERMITTING_POLICY,
                       permitting_policy=None)
