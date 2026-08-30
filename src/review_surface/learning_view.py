"""§8.7's inspect-and-reset surface. P13 renders; P1 stores; P13 applies nothing.

    §8.7 requires that the user "be able to inspect or reset learned preferences,
    so personalization remains understandable and reversible."

Reversible is the easy half. UNDERSTANDABLE is the one this module is built
around: a reset the user makes without having seen what produced the preferences
is a reset made blind, and it is indistinguishable afterwards from a reset made in
full knowledge. So `collect_reset` takes the view and REFUSES when the recorded
presentation does not carry the evidence the view's rows rest on. The rule is the
same one `collect` already enforces for a rejection, applied to the gesture that
throws learning away rather than the one that adds to it.

Two further refusals, both methods that raise rather than absences someone has to
notice:

* `apply` -- no learning is applied by P13. The store is P1's scoped projection
  over `events.correction_scope`, and the MEANING of each correction belongs to
  the part it was routed to.
* `delete` -- P13's tables are append-only by trigger and P13 deletes nothing.
  SPEC Open question 11 is open: §8.4 lets the user "review and delete local
  derived data" and §8.2 makes the event log append-only, and the same conflict
  P7 and P5 raise about stored observations applies to the record of what was
  displayed. Live `privacy.revocation.delete_derived` raises for the same reason.

NOTHING IS FILTERED. §8.7's own promise is that none of the learning is hidden
from this view, so every projected row reaches `rows` and a row with no evidence
says so in its explanation rather than being dropped for looking thin.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import NoReturn

from database_agent.events import CORRECTION_SCOPES

from review_surface.citations import ResolvedCitation, resolve_citation
from review_surface.collect import collect
from review_surface.presentation import presented_state
from review_surface.records import ReviewAction
from review_surface.rejections import PriorRejection, prior_rejections
from review_surface.vocabulary import ACTION_RESET_LEARNING, SURFACE_LEARNING


class LearningNotAppliedHere(RuntimeError):
    """Something asked P13 to apply a learned preference. It is not P13's."""


class NothingIsDeletedHere(RuntimeError):
    """Something asked P13 to delete a record. Its tables are append-only."""


class EvidenceNotShown(RuntimeError):
    """A reset collected against a view that did not show what produced it."""


@dataclass(frozen=True)
class LearnedPreferenceRow:
    """One row of P1's scoped projection, with the evidence behind it."""

    correction_scope: str
    correction_subject: str
    polarity: str | None
    proposal_class: str | None
    basis_key: str | None
    observed_at: str
    citations: tuple[ResolvedCitation, ...]
    explanation: str


@dataclass(frozen=True)
class LearningView:
    """What §8.7 requires a person be able to look at before they reset it."""

    scopes: tuple[str, ...]
    rows: tuple[LearnedPreferenceRow, ...]
    negative_examples: tuple[PriorRejection, ...]
    reset_action: str

    def evidence_keys(self) -> tuple[str, ...]:
        """Every observation key this view rests on, rows and rejections alike."""
        keys: list[str] = []
        for row in self.rows:
            keys.extend(citation.observation_key for citation in row.citations)
        for rejection in self.negative_examples:
            keys.extend(citation.observation_key
                        for citation in rejection.citations)
        return tuple(sorted(set(keys)))

    def apply(self) -> NoReturn:
        raise LearningNotAppliedHere(
            "P13 renders P1's scoped projection and collects the reset; it "
            "applies no learning. The store is P1's and the meaning of each "
            "correction belongs to the part it was routed to")

    def delete(self) -> NoReturn:
        raise NothingIsDeletedHere(
            "P13's tables are append-only by trigger and it owns no supersedable "
            "record. Whether a `review presentation` is deletable derived data "
            "is unresolved: §8.4 lets the user review and delete local derived "
            "data and §8.2 makes the event log append-only. A reset is collected "
            "and routed to P1, which records it")


def learning_view(conn: sqlite3.Connection, *, subject_refs: Sequence[str],
                  projection: Callable[[], Sequence[Mapping[str, object]]],
                  ) -> LearningView:
    """Render P1's projection and P13's own stored rejections. Filter nothing.

    `projection` is injected because the scoped store is P1's and its read surface
    is not P13's to name. Each row is expected to carry `correction_scope`,
    `correction_subject`, `polarity`, `proposal_class`, `basis_key`,
    `observed_at` and `evidence_refs`; anything missing reads as absent rather
    than raising, because a projection that grows a column must not break the view
    that renders it.
    """
    rows: list[LearnedPreferenceRow] = []
    for record in projection():
        refs = tuple(record.get("evidence_refs", ()) or ())
        citations = tuple(resolve_citation(conn, key) for key in refs)
        scope = str(record.get("correction_scope", ""))
        subject = str(record.get("correction_subject", ""))
        polarity = record.get("polarity")
        rows.append(LearnedPreferenceRow(
            correction_scope=scope, correction_subject=subject,
            polarity=polarity,
            proposal_class=record.get("proposal_class"),
            basis_key=record.get("basis_key"),
            observed_at=str(record.get("observed_at", "")),
            citations=citations,
            explanation=(
                f"a {polarity or 'neutral'} correction at {scope!r} scope about "
                f"{subject!r}"
                + (f", supported by {len(citations)} stored observation(s)"
                   if citations
                   else ", with no stored evidence reference; it is shown as it "
                        "is rather than omitted, because §8.7 requires that none "
                        "of the learning is hidden from this view"))))

    negatives: list[PriorRejection] = []
    for subject_ref in subject_refs:
        negatives.extend(prior_rejections(conn, subject_ref=subject_ref))

    return LearningView(
        scopes=CORRECTION_SCOPES, rows=tuple(rows),
        negative_examples=tuple(negatives),
        reset_action=ACTION_RESET_LEARNING)


def collect_reset(conn: sqlite3.Connection, view: LearningView, *,
                  action_id: str, subject_ref: str, plan_version: str,
                  session_id: str, correction_scope: str,
                  presented_state_ref: str, user_id: str, acted_at: str,
                  component_version: str) -> ReviewAction:
    """Collect the reset and route it to P1. P13 records nothing else.

    The view is a required argument, not a convenience: a reset is only
    understandable -- §8.7's own word -- if the person making it saw what produced
    the preferences they are throwing away. So every evidence key the view rests
    on must appear in the recorded presentation, and a reset whose producing
    evidence was never shown is refused rather than stored as though it were an
    informed decision.
    """
    state = presented_state(conn, presented_state_ref)
    shown = set(state.evidence_refs) if state is not None else set()
    unshown = [key for key in view.evidence_keys() if key not in shown]
    if unshown:
        raise EvidenceNotShown(
            f"this reset would discard learning resting on {len(unshown)} "
            f"evidence reference(s) the recorded presentation does not carry: "
            f"{unshown}. §8.7 requires learned preferences to be INSPECTABLE as "
            "well as resettable, and a reset made against a view that did not "
            "show what produced them is indistinguishable afterwards from one "
            "made in full knowledge")
    return collect(
        conn, action_id=action_id, surface=SURFACE_LEARNING,
        subject_ref=subject_ref, plan_version=plan_version,
        session_id=session_id, action=ACTION_RESET_LEARNING,
        correction_scope=correction_scope,
        presented_state_ref=presented_state_ref, user_id=user_id,
        acted_at=acted_at, component_version=component_version)
