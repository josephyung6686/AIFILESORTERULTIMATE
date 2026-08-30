# src/questions/effects.py
"""§17 -- what changing an answer does to a plan, and what it must never do.

> When a user edits or re-runs a structural answer, the product creates a draft
> plan version. It shows a meaningful diff... It must not silently rename folders,
> reclassify files, reveal protected records, or move anything as a consequence of
> a changed answer. (`66` §17:576-582)

Both halves of that existed and nothing joined them. `open_draft` and
`diff_versions` are P10's; `answered_options` is P15's. Today `--answer`
supersedes a row and the next run simply comes out different -- no draft, no diff,
and nothing a person can look at to see what their correction did.

**This module imports no part of P10.** `open_draft` arrives as an argument with
no default, the way every authority in this project arrives from the caller. P15
knows when an answer changed and what the answer controls; it does not know what a
plan version is, and a module that knew both would be the place where a question
started editing a tree.

**Three of §17's six diff questions have no producer, and are NAMED rather than
omitted.** Placement proposals are P11's -- `tree_design/diff.py` states that the
file-level consequence "is computed by P11 from this diff against its own
placement decisions". A protected-area record does not exist before §15's
relationship work. A filing policy has no producer at all. Each is an explicit
`None` carried with the reason, because an empty tuple reads as "nothing changed"
and this project's standing rule is that nothing is silently omitted.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.store import answer_by_id, live_answer, questions_for
from questions.vocabulary import CONFIRMED


@dataclass(frozen=True, slots=True)
class AnswerChange:
    """What a person said, and what they had said before.

    `before` is `None` only where there was no earlier answer -- and that is not a
    change: §17's trigger is "edits or re-runs", and a first answer is neither.
    """

    question: StructuralQuestion
    scope: str
    before: StructuralAnswer | None
    after: StructuralAnswer

    def _option(self, answer: StructuralAnswer | None) -> QuestionOption | None:
        """The option an answer selected, and only when it BINDS.

        A skipped, declined or revoked answer selected nothing that decides
        anything -- `answered_options` already draws that line and this must draw
        it in the same place, or a revocation would look like an activation.
        """
        if answer is None or answer.state != CONFIRMED or not answer.option_id:
            return None
        return next((option for option in self.question.options
                     if option.option_id == answer.option_id), None)

    @property
    def option_before(self) -> QuestionOption | None:
        return self._option(self.before)

    @property
    def option_after(self) -> QuestionOption | None:
        return self._option(self.after)


def changed_answer(conn: sqlite3.Connection, *, question_id: str,
                   scope: str) -> AnswerChange | None:
    """The live answer and the one it superseded, or `None` if nothing changed.

    `None` for a question nobody asked, a question nobody answered, and a FIRST
    answer -- §17 governs "edits or re-runs", and a first answer is the ordinary
    case the rest of P15 already handles.
    """
    asked = questions_for(conn, (question_id,))
    if not asked:
        return None
    after = live_answer(conn, question_id=question_id, scope=scope)
    if after is None or after.supersedes is None:
        return None
    return AnswerChange(question=asked[0], scope=scope,
                        before=answer_by_id(conn, after.supersedes), after=after)


#: Why each of §17:577's remaining three questions has no answer here. Carried on
#: the diff so a renderer can SAY so; an empty tuple in their place would read as
#: "nothing changed", which is the one thing they do not mean.
NOT_COMPUTED_BECAUSE: Mapping[str, str] = MappingProxyType({
    "placement_proposals": (
        "P11 owns placement. `tree_design/diff.py`: the file-level consequence "
        "'is computed by P11 from this diff against its own placement decisions'. "
        "P15 holds no placement decision and must not invent one."),
    "protected_area_change": (
        "Nothing records a protected AREA yet. §15's relationship work is the "
        "producer and it is held on the owner's vocabulary ruling."),
    "filing_policy_paused": (
        "No filing policy has a producer. `66` §22 puts automatic filing last, "
        "and there is nothing yet to pause."),
})


@dataclass(frozen=True, slots=True)
class PlanEffectDiff:
    """§17:577's six questions: three answered, three named as unanswered."""

    schemas_activated: tuple[str, ...]
    schemas_deactivated: tuple[str, ...]
    templates_affected: tuple[str, ...]
    branches_needing_review: tuple[str, ...]
    #: The three §17 asks for that P15 cannot produce. `None`, never `()`.
    placement_proposals: None = None
    protected_area_change: None = None
    filing_policy_paused: None = None

    @property
    def not_computed(self) -> tuple[str, ...]:
        return tuple(NOT_COMPUTED_BECAUSE)

    @property
    def why_not_computed(self) -> Mapping[str, str]:
        return NOT_COMPUTED_BECAUSE

    @property
    def is_empty(self) -> bool:
        """Nothing this diff CAN see has changed.

        Deliberately not called `nothing_changed`: three of §17's six questions
        were never asked, and `not_computed` says which. A reader that treats this
        as "the answer had no effect" would be reading past the names.
        """
        return not (self.schemas_activated or self.schemas_deactivated
                    or self.templates_affected or self.branches_needing_review)


def _branch_of(scope: str) -> tuple[str, ...]:
    """The branch a branch-scoped answer names, and nothing for any other scope.

    §17:577 asks "which branches may need review". The answer is scoped, and §13
    forbids reusing it outside that scope, so the branches it can affect are
    exactly the one it names.
    """
    kind, _, entity = scope.partition(":")
    return (entity,) if kind == "branch" and entity else ()


def diff_for_answer_change(change: AnswerChange | None) -> PlanEffectDiff:
    """§17:577, for the three of its six questions P15 can answer."""
    if change is None:
        return PlanEffectDiff((), (), (), ())
    before, after = change.option_before, change.option_after
    was = before.activates_schema if before else None
    now = after.activates_schema if after else None

    # §17:577's "which templates are affected". Both sides, because a person needs
    # to see the shape they are leaving as well as the one they are taking -- a
    # diff naming only the destination is a decision announced, not a diff.
    def _named(option: QuestionOption | None) -> frozenset[str]:
        if option is None:
            return frozenset()
        return frozenset(value for value in (option.gates_template,
                                             option.selects_situation) if value)

    was_templates, now_templates = _named(before), _named(after)
    # A template named on both sides did not change, and listing it would report
    # motion where there was none.
    templates = tuple(sorted(was_templates ^ now_templates))
    changed = bool(templates) or was != now
    return PlanEffectDiff(
        schemas_activated=(now,) if now and now != was else (),
        schemas_deactivated=(was,) if was and was != now else (),
        templates_affected=templates,
        branches_needing_review=_branch_of(change.scope) if changed else ())


def draft_for_answer_change(conn: sqlite3.Connection, *,
                            change: AnswerChange | None, from_version: str,
                            new_version_id: str, created_at: str,
                            mint_node_id: Callable[[], str],
                            open_draft: Callable[..., object]) -> object | None:
    """§17:576's draft, opened only when the change actually changes something.

    Returns `None` when nothing did. A person who re-types the answer they already
    gave has not edited anything, and should not find a draft plan waiting for
    them -- a product that opened one would teach them that re-confirming is
    dangerous, which is the opposite of what §12's revocability promises.

    `open_draft` is P10's, injected. This module knows what an answer controls and
    nothing about what a plan version is, and joining those two kinds of knowledge
    in one module is how a question comes to edit a tree.

    **WHETHER TO CALL THIS AT ALL IS NOT DECIDED HERE.** §17:576 reads "the product
    creates a draft plan version" and does not say whether that is automatic or
    offered -- `75` §6 Q5 puts the question to the owner. The composition root
    holds that policy, as it holds every other one.
    """
    if change is None or diff_for_answer_change(change).is_empty:
        return None
    return open_draft(conn, from_version=from_version,
                      new_version_id=new_version_id, created_at=created_at,
                      mint_node_id=mint_node_id)
