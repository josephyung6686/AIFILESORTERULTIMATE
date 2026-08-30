# src/questions/registry.py
"""§21's registry -- of question KINDS, and never of questions.

`66` §21:665 states the debt: the structural-question system requires "a registry
of questions, their trigger conditions, the decisions they unblock, allowed answer
types, data classifications, scopes, revocation behavior, plan-version effects, and
the precise template or policy mechanisms that consume each answer".

**Why this is a registry of kinds and not of questions.** `triggers.py` opens by
refusing to write any question down: "no question is written down anywhere. Each one
is DERIVED from a specific blocked decision in a specific run, and a run with nothing
blocked asks nothing". That is right, and this module does not weaken it -- nothing
here holds a prompt, an option label, or an evidence context. What it holds is the
answer to a different question, the one §21's next sentence asks: "Questions must be
wired into those mechanisms intentionally." Intentionally is only checkable if the
set of kinds can be walked, and until this module existed it could not be. The two
kinds this deployment ships were discoverable only by reading `triggers.py`.

**What a kind is.** A trigger that derives questions, the scope kind those questions
take, the ONE consequence its options may set, and the module-level callable that
reads that consequence back out. The last field is the load-bearing one:
`records.py` states the discipline as "shipping a consequence that does nothing is
how a question comes to be asked for no reason", and a kind whose reader is absent is
refused here rather than reviewed later.
"""
from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass

from questions.records import QuestionOption
from questions.store import (
    activated_schemas, gated_template, selected_situation,
)
from questions.vocabulary import (
    SCOPE_BRANCH, SCOPE_CORPUS, SCOPE_ORGANIZATION, SCOPES, check,
)


class KindNotPermitted(ValueError):
    """A question kind that would leave a consequence unread."""


_OPTION_IDENTITY: frozenset[str] = frozenset({"option_id", "label"})


def option_consequence_fields() -> frozenset[str]:
    """Every field of `QuestionOption` that is a consequence rather than identity.

    Read from the dataclass rather than listed here. A hand-written list is how
    `record_question` once dropped `gates_template` silently -- the same defect,
    one layer up: a consequence the registry did not know about would be a
    consequence the registry could not report as unread.
    """
    return frozenset(field.name for field in dataclasses.fields(QuestionOption)
                     if field.name not in _OPTION_IDENTITY)


@dataclass(frozen=True, slots=True)
class QuestionKind:
    """One family of questions, and the mechanism that consumes its answers."""

    #: The prefix a derived question id carries, before its first `.` or `:`.
    #: Ids are built FROM this by the trigger, so a kind cannot be registered for
    #: questions nobody raises, nor questions raised under an unregistered kind.
    kind_id: str
    #: The scope those questions take. `66` §13 forbids an answer being "reused
    #: outside its stated scope", and the scope kind is half of what that means.
    scope_kind: str
    #: The single field of `QuestionOption` this kind's options may set.
    consequence_field: str
    #: The module-level reader that consumes it. Never `None`.
    reader: Callable[..., object] | None

    def __post_init__(self) -> None:
        if not self.kind_id:
            raise KindNotPermitted("a kind needs a kind_id")
        check(self.scope_kind, SCOPES, name="scope_kind")
        if self.consequence_field not in option_consequence_fields():
            raise KindNotPermitted(
                f"{self.kind_id!r} sets {self.consequence_field!r}, which is not a "
                f"consequence QuestionOption carries "
                f"({sorted(option_consequence_fields())})")
        if self.reader is None or not callable(self.reader):
            raise KindNotPermitted(
                f"{self.kind_id!r} sets {self.consequence_field!r} and names no "
                "reader. §21 requires 'the precise template or policy mechanisms "
                "that consume each answer'; a consequence nothing reads is a "
                "question asked for no reason")


#: `triggers.question_for_tied_reading`. The evidence supports two readings of one
#: subject equally; the person's answer says which, and `activated_schemas` hands it
#: to the detector as `settled_by_user`.
READING_KIND = QuestionKind(
    kind_id="reading",
    scope_kind=SCOPE_ORGANIZATION,
    consequence_field="activates_schema",
    reader=activated_schemas)

#: `triggers.question_for_nesting`. Two shapes pass every check for one branch; the
#: person picks one, and `gated_template` returns it to the nesting chooser.
NESTING_KIND = QuestionKind(
    kind_id=SCOPE_BRANCH,
    scope_kind=SCOPE_BRANCH,
    consequence_field="gates_template",
    reader=gated_template)

#: `triggers.question_for_situation`. Two situations the shipped library carries
#: both fire on one branch's evidence -- `68` F6's graduate student who also
#: teaches -- and the person says which this branch is. `kind_id` is its own word
#: rather than the scope's, because `branch` is already NESTING_KIND's: two kinds
#: share the branch SCOPE and cannot share a question-id prefix, or `kind_of` would
#: have to guess which mechanism an answer belongs to.
SITUATION_KIND = QuestionKind(
    kind_id="situation",
    scope_kind=SCOPE_BRANCH,
    consequence_field="selects_situation",
    reader=selected_situation)

#: `roles.question_for_role_declaration`. The person says what a scope is FOR
#: them, and a confirmed declaration turns on a schema. It shares
#: `activates_schema` and `activated_schemas` with READING_KIND deliberately:
#: `store.activated_schemas` promises "a reader can see every schema the user
#: turned on and where it came from", and a second activation path would falsify
#: that sentence. Two kinds, one surface, is what keeps the promise true.
ROLE_KIND = QuestionKind(
    kind_id="role",
    scope_kind=SCOPE_CORPUS,
    consequence_field="activates_schema",
    reader=activated_schemas)

#: Every kind this deployment ships, and the tests assert that every
#: consequence `QuestionOption` can carry is claimed by one of them.
QUESTION_KINDS: tuple[QuestionKind, ...] = (
    READING_KIND, NESTING_KIND, SITUATION_KIND, ROLE_KIND)


def kind_of(question_id: str) -> QuestionKind | None:
    """The kind a derived question id belongs to, or `None`.

    `None` rather than a nearest match, for the reason every closed vocabulary in
    this project gives: a refusal that named the nearest kind would be a suggestion,
    and a suggestion here would wire an answer to a mechanism nobody chose.
    """
    prefix = question_id.split(".", 1)[0].split(":", 1)[0]
    for kind in QUESTION_KINDS:
        if kind.kind_id == prefix:
            return kind
    return None
