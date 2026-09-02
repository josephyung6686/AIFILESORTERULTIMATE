"""The freeze, as the person's approval. P13's record, written by a gesture.

The owner ruled on 2026-09-02 that `--freeze` **is** P13's review surface: a
person who has read the proposal and typed the word has approved those
placements. `91` §6 is the finding that ruling answers -- over the shipped
pipeline every placement came back `review_required`, so a freeze froze nothing
and the product could move a file and never would.

**Nothing here is new machinery, and that is the point.** The table exists
(`review_surface/schema.py`), the writer exists (`review_surface.approvals.approve`),
the reader exists (`store.approvals_for`), the gate exists
(`mutation.approval.approval_verdict`), and P13's guard against an uninformed
approval exists. What did not exist was a caller. This module is the two wires,
and it decides nothing that the parts had not already decided:

* `approval_writer` records what was displayed and then hands P13's own
  `approve` the decision, so every refusal a person meets is P13's sentence and
  not a paraphrase of it.
* `approval_reader` reads the rows back for P12's gate. It converts P13's record
  into the record P12 published for it -- nine fields, the same names -- because
  P12 deliberately does not import P13 (`mutation/approval.py`: *"no source
  module impersonates P13"*), so the copy has to happen at the composition seam
  and this is it.

**Why the presentation is recorded here and not when the report prints.** A
`ReviewApproval` names the plan it approves, and a plan does not exist until
`build_plan` has run -- which happens inside the freeze. So the moment that can
be recorded with `subject_ref = plan_id` is this one. The guard that makes the
approval informed is therefore not the timestamp; it is `shown_file_ids` in
`freeze`, which is the set of files the person's screen actually named. A file
the report counted but did not list is not in it.

**The latest approval wins, and the version check stays P12's.** `approvals_for`
is asked for every version on purpose -- its own docstring says why: a reader
that dropped an approval stamped with another version would leave P12's gate
untested and would tell a person their answered plan is still waiting. So this
returns the last answer the person gave and lets the gate say whether it fits.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable

from privacy.display import RedactionSettings
from review_surface.approvals import approve
from review_surface.presentation import record_presentation
from review_surface.store import approvals_for, record_approval
from review_surface.vocabulary import SURFACE_APPLY, VERDICT_APPROVED

from mutation.approval import ReviewApproval as GateApproval
from mutation.plan import MovePlan


def approval_writer(conn: sqlite3.Connection, *,
                    settings: RedactionSettings,
                    session_id: str,
                    user_id: str,
                    component_version: str,
                    mint_id: Callable[[], str],
                    ) -> Callable[[MovePlan, str], None]:
    """Record what was shown, then P13's approval of it. In that order.

    `settings` is the redaction policy in force when the person read the
    proposal, read from P7 at the composition root rather than assumed here: an
    approval given while the evidence was redacted is a different decision from
    one given with it visible (§8.4, §8.7), and this package has no standing to
    guess which happened.

    `evidence_refs` is empty because the report shows no observation key. That is
    a real answer rather than a missing one -- `record_presentation` says so in
    its own docstring -- and it is the honest one: what the person read was a
    filename, a destination and a sentence.

    Nothing here has a default. There is no user this module can name on a
    person's behalf, and no session, and no policy.
    """

    def write(plan: MovePlan, at: str) -> None:
        shown = record_presentation(
            conn, surface=SURFACE_APPLY, subject_ref=plan.plan_id,
            plan_version=plan.organization_plan_version,
            session_id=session_id, settings=settings, evidence_refs=(),
            user_id=user_id, component_version=component_version,
            rendered_at=at)
        record_approval(conn, approve(
            conn, approval_id=mint_id(), plan_id=plan.plan_id,
            placement_decision_ref=plan.placement_decision_reference,
            plan_version=plan.organization_plan_version,
            required_review_policy=plan.required_review_policy,
            verdict=VERDICT_APPROVED,
            presented_state_ref=shown.presented_state_ref,
            user_id=user_id, decided_at=at,
            component_version=component_version))

    return write


def approval_reader(conn: sqlite3.Connection,
                    ) -> Callable[[str], GateApproval | None]:
    """P12's `approval_for`, finally reading something.

    `None` for a plan nobody has approved, which is the refusal and not a gap in
    the wiring -- `mutation.approval` is explicit that absence IS the answer.
    """

    def read(plan_id: str) -> GateApproval | None:
        answers = approvals_for(conn, plan_id=plan_id)
        if not answers:
            return None
        latest = answers[-1]
        return GateApproval(
            approval_id=latest.approval_id, plan_id=latest.plan_id,
            placement_decision_ref=latest.placement_decision_ref,
            plan_version=latest.plan_version,
            required_review_policy=latest.required_review_policy,
            verdict=latest.verdict,
            presented_state_ref=latest.presented_state_ref,
            user_id=latest.user_id, decided_at=latest.decided_at)

    return read
