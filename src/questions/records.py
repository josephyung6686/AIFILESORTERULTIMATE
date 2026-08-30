# src/questions/records.py
"""P15's records: a structural question, its options, and one person's answer.

`66` §12 is explicit that this is "a significant product and engineering
workstream" rather than a screen, and §21 lists what it owes: "a registry of
questions, their trigger conditions, the decisions they unblock, allowed answer
types, data classifications, scopes, revocation behavior, plan-version effects,
and the precise template or policy mechanisms that consume each answer."

These records own the middle of that list. The trigger conditions live in
`triggers.py` beside the evidence they read, and what consumes an answer lives in
the part that consumes it -- because §21's own warning is that questions "must be
wired into those mechanisms INTENTIONALLY", and a registry that also owned the
wiring would be the place where an unwired question could hide.

**The boundary these records enforce.** §13 says of a contextual answer that if it
"ever determines whether a folder exists, what a file is called, where a file is
placed, or what data is exposed, that is a DEFECT rather than a feature." A defect
that a record can make unrepresentable should not be left to a code review, so
`StructuralQuestion` refuses a contextual question whose options activate a
schema. It is the same treatment `Handling` gives `unreadable_unclassified`: the
type declines to hold the value that would collapse a distinction.
"""
from __future__ import annotations

from dataclasses import dataclass

from facts.domains import SCHEMA_IDS
# Imported, never respelled. `tree_design/vocabulary.py` states the rule and the
# reason: a second spelling of a privacy vocabulary is how two parts of one
# product come to disagree about how sensitive something is.
from privacy.classification import UNREADABLE_UNCLASSIFIED
from privacy.vocabulary import HANDLING_CLASSES

from questions.vocabulary import (
    ANSWER_CLASSES, ANSWER_STATES, ANSWER_TYPES, CHOICE, CONFIRMED, CONTEXTUAL,
    FREE_TEXT, NOT_APPLICABLE, SKIPPED, check, check_scope,
)


class AnswerNotPermitted(ValueError):
    """A question or an answer that P15's own contract forbids."""


@dataclass(frozen=True, slots=True)
class QuestionOption:
    """One answer a person may give, and what taking it would do.

    §13 permits a structural answer five consequences -- "activate a schema, gate
    a template, resolve role ambiguity, allow or prohibit a category of folder
    label, or require review". TWO of them are wired, and the rest are still
    absent rather than stubbed, because shipping a consequence that does nothing
    is how a question comes to be asked for no reason.

    `activates_schema` is the first. `gates_template` is the second: it names the
    NESTING a person chose for one branch -- `00`:99 shows them what each option
    would create, with the counts and the warnings, and :78 has them pick one.

    An option that does neither is still a real option -- "It is not about me"
    changes nothing and is the answer §14 insists stays first-class.
    """

    option_id: str
    label: str
    activates_schema: str | None = None
    #: The composition this option would build, as the ordered chain of the fields
    #: its levels resolve to (`subject>work_type`). The CHAIN and not a positional
    #: `opt_2`: an answer has to outlive the run that asked, and a position shifts
    #: the moment the corpus does, so a person would silently get a different tree
    #: from the same recorded answer.
    gates_template: str | None = None

    def __post_init__(self) -> None:
        for name in ("option_id", "label"):
            if not getattr(self, name):
                raise AnswerNotPermitted(f"an option needs a {name}")
        if (self.activates_schema is not None
                and self.activates_schema not in SCHEMA_IDS):
            raise AnswerNotPermitted(
                f"{self.activates_schema!r} is not one of the "
                f"{len(SCHEMA_IDS)} schemas the product recognises; a typo in an "
                "activation must not read as a policy")


@dataclass(frozen=True, slots=True)
class StructuralQuestion:
    """One question, asked because one decision is blocked.

    Every field below is required, and each one is a sentence `66` §12 uses:
    "ask a question only when a specific decision is blocked, EXPLAIN THE EXACT
    DECISION IT UNLOCKS, STATE WHAT IT WILL NOT AFFECT, allow the user to skip it,
    RECORD THE SCOPE of the answer". A question missing any of them is the "generic
    list of questions such as 'What do you do?'" that §12 rejects by name -- and
    optional fields are how a generic question gets asked by accident.

    `evidence_refs` is what makes it evidence-linked rather than a profile
    interview. §14: "the user can see WHY the question arose". A question the
    product cannot show a reason for is one it should not be asking.
    """

    question_id: str
    answer_class: str
    #: What the person is asked. §14's example: "Which describes your relationship
    #: to Columbia?"
    prompt: str
    #: The visible context that produced it: "We found files connected to Columbia."
    evidence_context: str
    #: The decision this unblocks: "This helps distinguish coursework from
    #: professional material."
    unlocks: str
    #: The promise: "It will not create or move folders by itself."
    will_not_do: str
    scope: str
    #: §21's fifth obligation: "data classifications". P7's §8.4 classes, for
    #: the data the question COLLECTS -- not for the files it arose from. It is
    #: required because §15:533 promises that names a person supplies "remain
    #: local, protected, scoped to the approved area, and removable", and a
    #: record that cannot say a question collects a name can keep none of that.
    handling_class: str
    options: tuple[QuestionOption, ...]
    #: P4 observation keys behind `evidence_context`.
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("question_id", "prompt", "evidence_context", "unlocks",
                     "will_not_do", "scope", "handling_class"):
            if not getattr(self, name):
                raise AnswerNotPermitted(
                    f"a structural question needs {name}; §12 requires a question "
                    "to name the decision it unlocks, what it will not affect, "
                    "the evidence it arose from and the scope of the answer")
        check(self.answer_class, ANSWER_CLASSES, name="answer_class")
        if self.handling_class == UNREADABLE_UNCLASSIFIED:
            raise AnswerNotPermitted(
                f"a question may not be classified {UNREADABLE_UNCLASSIFIED!r}. "
                "That is a gate OUTCOME -- what P7 resolves to when it could not "
                "read something -- and never a statement about what a question "
                "collects. Every question this product raises is one it wrote "
                "itself, from evidence it read")
        check(self.handling_class, HANDLING_CLASSES, name="handling_class")
        check_scope(self.scope)
        if not self.evidence_refs:
            raise AnswerNotPermitted(
                "a question with no evidence behind it is the profile interview "
                "§12 rejects; §14 requires the person to see why it arose")
        if not self.options:
            raise AnswerNotPermitted("a question with no options asks nothing")
        ids = [option.option_id for option in self.options]
        if len(set(ids)) != len(ids):
            raise AnswerNotPermitted(f"two options share an id: {sorted(ids)}")
        if self.answer_class == CONTEXTUAL:
            activating = [option.option_id for option in self.options
                          if option.activates_schema]
            if activating:
                raise AnswerNotPermitted(
                    f"a contextual question's options {activating} would activate "
                    "a schema. §13: a contextual answer must not 'create, remove, "
                    "hide, or rename folders' or 'silently become a structural "
                    "rule', and activating a schema changes which templates exist, "
                    "so it changes which folders exist")
            gating = [option.option_id for option in self.options
                      if option.gates_template]
            if gating:
                raise AnswerNotPermitted(
                    f"a contextual question's options {gating} would gate a "
                    "template. §13 forbids a contextual answer to 'create, remove, "
                    "hide, or rename folders', and a nesting IS which folders the "
                    "branch has -- the same reason activation is refused above")


@dataclass(frozen=True, slots=True)
class StructuralAnswer:
    """What one person said, when, and over what.

    `inferred` exists to be RECORDED AND REFUSED rather than to be a second way of
    answering. §13 requires the person to be able to see "whether it was inferred
    or explicitly confirmed", so the field has to exist; §12 says a structural
    answer must never "be inferred silently from weak evidence", so a confirmed
    structural answer that claims to be inferred is a contradiction and is refused
    here rather than somewhere further downstream.
    """

    question_id: str
    option_id: str | None
    state: str
    scope: str
    user_id: str
    recorded_at: str
    #: §21's "allowed answer types". `CHOICE` is what every row written before
    #: 2026-08-30 is, so the default leaves them all unchanged.
    answer_type: str = CHOICE
    #: §16:555: the matcher "should store the raw user wording". Their words,
    #: byte for byte -- not normalised, not nearest-matched. Set on FREE_TEXT and
    #: refused on CHOICE, because an answer carrying both a chosen option and a
    #: sentence has two answers in it that need never agree.
    raw_wording: str | None = None
    #: §16:543: a role carries "a scope and possibly a time period, rather than
    #: forcing one permanent profession". A person stops teaching; the answer
    #: that says they taught stays true of the period it names.
    applies_from: str | None = None
    applies_until: str | None = None
    inferred: bool = False
    #: Set when this answer supersedes an earlier one for the same question and
    #: scope. §12 requires answers to be "edited, revoked, or re-run"; an edit that
    #: overwrote the earlier row would lose that the person once said otherwise.
    supersedes: str | None = None
    supersede_reason: str | None = None

    def __post_init__(self) -> None:
        for name in ("question_id", "user_id", "recorded_at"):
            if not getattr(self, name):
                raise AnswerNotPermitted(f"an answer needs {name}")
        check(self.state, ANSWER_STATES, name="state")
        check_scope(self.scope)
        if not isinstance(self.inferred, bool):
            raise AnswerNotPermitted("`inferred` is a flag, not a value")
        if self.inferred:
            raise AnswerNotPermitted(
                "a structural answer may not be inferred. §12: it must never 'be "
                "inferred silently from weak evidence'. The field is here so the "
                "record can SAY it was confirmed, not so it can say it was not")
        check(self.answer_type, ANSWER_TYPES, name="answer_type")
        if self.answer_type == FREE_TEXT:
            if self.option_id:
                raise AnswerNotPermitted(
                    f"a free text answer names the option {self.option_id!r}. §16 "
                    "requires that 'an unmatched answer must remain unmatched', and "
                    "the whole of that guarantee here is that free text selects "
                    "nothing: an answer that selected something would reach "
                    "`answered_options`, and from there a schema activation nobody "
                    "confirmed")
            if self.state == CONFIRMED and not self.raw_wording:
                raise AnswerNotPermitted(
                    "a confirmed free text answer with no raw_wording says nothing, "
                    "and would sit in the store looking like a settled decision")
        elif self.raw_wording is not None:
            raise AnswerNotPermitted(
                "a choice answer carries raw_wording as well as an option. The two "
                "types are alternatives: a reader could take either as the answer "
                "and they need never agree")
        if (self.applies_from and self.applies_until
                and self.applies_until < self.applies_from):
            raise AnswerNotPermitted(
                f"the period {self.applies_from}..{self.applies_until} ends before "
                "it starts. Nothing can be inside it, so it would silently disable "
                "an answer the person believes they gave")
        if self.state == CONFIRMED and self.answer_type == CHOICE and not self.option_id:
            raise AnswerNotPermitted(
                "a confirmed answer names the option the person chose")
        if self.state in (SKIPPED, NOT_APPLICABLE) and self.option_id:
            raise AnswerNotPermitted(
                f"a {self.state} answer names an option ({self.option_id!r}); "
                "skipping is not choosing, and a record that cannot tell them "
                "apart will treat a decline as a decision")
