# src/review_gestures.py
"""P13's write side: the review sets a run shows, and the gesture typed at them.

**Why this file exists at all.** `review_surface.collect` is the one function in
the product that turns a person's gesture into a stored `review_action`, and until
now nothing in `src/` called it. Five modules INSIDE P13 call it -- `bulk`,
`consent_surface`, `learning_view`, `move_permission`, `versions_view` -- and
every one of them is itself unreachable, so the whole chain terminated in a table
that stayed empty on every real run. Audited over the owner's own folder,
`review_actions` had 0 rows, and the report on the same screen offered
`--send-set "SET=AREA"` and a person could type it. The gesture happened; the
record of it did not.

`apply_run/approval.py` is the same shape for the same reason at the freeze
gesture, and it is the worked example this file follows: the seam records what was
displayed, then hands P13's own function the decision, so **every refusal a person
meets is P13's sentence and not a paraphrase of it**.

**Why it is a top-level module and not in `review_run/` or `apply_run/`.**
`review_run` declares itself the composition layer "for the screens a person
READS" and holds no writer; `apply_run` is P12's wiring, and a residual-set send
moves nothing and freezes nothing. So this is the deployment layer, a sibling of
`model_facts.py`, which is where the same argument put P6's model producer.

**Nothing here is a number and nothing here is a policy.** `correction_scope` in
particular has no default anywhere on this path -- P13's own `collect` refuses to
supply one, and neither does this file. §8.7's whole example is about not
inferring a scope, so the composition root chooses it and hands it down.

**A known limitation, written here rather than solved.** The presentation is
recorded when the run has assembled its review sets, which is a moment BEFORE the
report prints them. A run that refuses between those two points -- P15 raising a
blocked question, say -- leaves a presentation row for a screen that was never
printed. The alternative is threading a callback through the report's line
builders, which would put P13's writer inside a pure renderer; the honest fix is
for the report to record it, and that is owed.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Mapping, Sequence

from placement.residual import ResidualSet
from privacy.display import RedactionSettings

from review_surface.collect import collect
from review_surface.presentation import PresentedState, record_presentation
from review_surface.records import ReviewAction
from review_surface.store import record_action
from review_surface.vocabulary import (
    ACTION_ACCEPT_BULK,
    SURFACE_RESIDUAL_SET,
    UNTOUCHED_PROTECTED,
)

#: P13's own name for the subject kind that carries no action, imported and never
#: respelled. `collect` refuses on it, which is how a protected set meets P13's
#: paragraph instead of a sentence written here.
PROTECTED_SUBJECT_KIND: str = UNTOUCHED_PROTECTED


def record_set_presentations(
    conn: sqlite3.Connection, *,
    sets: Sequence[ResidualSet],
    plan_version: str,
    session_id: str,
    settings: RedactionSettings,
    user_id: str,
    component_version: str,
    rendered_at: str,
) -> dict[str, PresentedState]:
    """One §8.4 presentation per surfaced set, keyed by the label a person types.

    **Every set, protected included.** The protected set carries no action, and
    that is the next function's refusal; it is still on the screen, and "marked
    and counted, never silently omitted" has no exception for the record of
    having shown it. A seam that recorded only the actionable sets would leave
    the one set the standing rule is about as the only unrecorded one.

    `evidence_refs` is empty and that is a real answer rather than a missing one:
    §7.5's card shows a count, a reason, examples and a distribution, and no
    observation key. `record_presentation` says so in its own docstring.

    **Keyed by `set_id`, not by the label a person types.** The label is what
    `--send-set` ADDRESSES -- `act_on_residual_sets` explains why: the `set_id` is
    minted per plan version and differs in every run, while the label is what
    §7.5 puts on the screen. But P11 lets two sets carry one label (its own
    `by_label` holds a LIST), and a mapping keyed by label would silently keep the
    last of them -- so the first set's gesture would be recorded against a
    presentation of a DIFFERENT set. The label resolves to sets in
    `collect_set_sends`, which is P11's own job; the presentation is about one
    set, so it is keyed by the one thing that names one set.
    """
    return {
        item.set_id: record_presentation(
            conn, surface=SURFACE_RESIDUAL_SET, subject_ref=item.set_id,
            plan_version=plan_version, session_id=session_id, settings=settings,
            evidence_refs=(), user_id=user_id,
            component_version=component_version, rendered_at=rendered_at)
        for item in sets
    }


def collect_set_send(
    conn: sqlite3.Connection, *,
    item: ResidualSet,
    area_label: str,
    presented: Mapping[str, PresentedState],
    action_id: str,
    plan_version: str,
    session_id: str,
    correction_scope: str,
    user_id: str,
    component_version: str,
    acted_at: str,
) -> ReviewAction:
    """One `--send-set` pair, collected as P13's record and stored.

    **`accept_bulk`, because that is what the gesture is.** One `--send-set`
    files a whole set into one area without a per-file look, and P13's rule for
    that action is that it enumerates its members -- "a filter expression cannot
    be re-read later to say which files a reversal applies to". The members are
    P11's own `member_file_ids`; nothing here counts or re-derives them.

    **The protected refusal is P13's and is reached rather than repeated.** The
    subject kind goes into the payload so `collect` raises
    `ProtectedContainerHasNoAction` on the set P7 flagged. Testing
    `item.protected` here and raising would be a second home for the rule, and a
    caller catching one while the other fired would see it as a crash. P11
    refuses the same set again at `require_set_actionable`; two refusals are the
    point, and this is the one that fires first.

    `bulk_basis` is the area the person named, which is the whole of why these
    files were filed together. It is stored so a later reversal can say what the
    gesture was for without re-reading a plan that no longer exists.
    """
    shown = presented.get(item.set_id)
    record = collect(
        conn, action_id=action_id, surface=SURFACE_RESIDUAL_SET,
        subject_ref=item.set_id, plan_version=plan_version,
        session_id=session_id, action=ACTION_ACCEPT_BULK,
        correction_scope=correction_scope,
        # A set with no recorded presentation reaches `collect` with a ref no row
        # carries, which is the state §8.7 refuses -- and it is passed rather
        # than short-circuited so the refusal names the missing ref.
        presented_state_ref="" if shown is None else shown.presented_state_ref,
        user_id=user_id, acted_at=acted_at, component_version=component_version,
        bulk_member_refs=item.member_file_ids,
        bulk_basis=area_label,
        payload={"subject_kind": (PROTECTED_SUBJECT_KIND if item.protected
                                  else SURFACE_RESIDUAL_SET),
                 "residual_area": area_label})
    record_action(conn, record)
    conn.commit()
    return record


def collect_set_sends(
    conn: sqlite3.Connection, *,
    sends: Mapping[str, str],
    sets: Sequence[ResidualSet],
    presented: Mapping[str, PresentedState],
    mint_action_id,
    plan_version: str,
    session_id: str,
    correction_scope: str,
    user_id: str,
    component_version: str,
    acted_at: str,
) -> tuple[ReviewAction, ...]:
    """Every `--send-set` pair this run was given, collected BEFORE P11 acts.

    **The order is the whole point and it was measured.** Run today against the
    owner's own folder, `--send-set "Protected, and not filed in bulk=Review
    Later"` reaches `act_on_residual_sets`, which writes a
    `residual_set_decisions` row saying that protected material is to be filed
    into a residual area, and only THEN does `review_residual_sets` raise
    `ProtectedSetNotReadable` -- which `src/cli.py` does not catch, so the run
    ends "No plan was made" and the person loses the whole proposal. The decision
    row survives. Collecting the gesture first moves P13's refusal in front of
    that write: nothing is decided, nothing is recorded, the plan lives, and the
    person reads P13's paragraph about why a protected set carries no action.

    **A refused batch can leave rows for the pairs before it, and that is the
    record being true rather than a partial write.** P13 "presents and collects;
    it never decides": a `review_action` says the person made this gesture and
    names the part it was handed to. Whether the filing then happened is P11's
    decision row, not this one. What the seam does NOT do is let a refusal land
    after P11 has written anything -- every pair is collected before
    `act_on_residual_sets` is called at all.

    A label this run did not surface is not matched here and not refused here
    either: it has no presentation, so `collect` refuses it by name, and P11
    refuses it again with the list of what this run DID surface.
    """
    by_label: dict[str, list[ResidualSet]] = {}
    for item in sets:
        by_label.setdefault(item.label, []).append(item)
    return tuple(
        collect_set_send(
            conn, item=item, area_label=area_label, presented=presented,
            action_id=mint_action_id(), plan_version=plan_version,
            session_id=session_id, correction_scope=correction_scope,
            user_id=user_id, component_version=component_version,
            acted_at=acted_at)
        for label, area_label in sends.items()
        for item in by_label.get(label, ()))
