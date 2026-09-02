# src/questions/roles.py
"""§16's role declaration: being more than one thing, without a matcher.

`66` §16 asks for a profession and role matcher. `62` §D is an owner ruling made
2026-08-29 that overturns the matcher AS A MECHANISM -- "These should not just be
directly matched -- the LLM uses that information to judge. This cannot be rule
based" -- and closes with "Nothing here should be built until it arrives." `69`
§4.3 keeps it open, and a decision brief is being prepared for an outside adviser
before the owner rules.

The two documents disagree about exactly one step and agree on either side of it.
**The step they disagree about is not in this module in any form.** Nothing here
reads a person's wording, ranks a schema against it, shortens the offered list, or
scores anything. The list this module offers is the product's whole closed schema
vocabulary, unfiltered, handed in by the caller. Narrowing it IS the proposal step.

What IS here is what both documents require and the product could not express:

> The system must support multiple roles, each with a scope and possibly a time
> period, rather than forcing one permanent profession. (§16:543)

**Built on A3's answer types, not beside them.** A declaration is a
`StructuralAnswer`. There is no roles table, and that is the design rather than an
economy: a second store would be a second place a schema could be turned on, and
`store.activated_schemas` promises "a reader can see every schema the user turned
on and where it came from". A confirmed declaration is a `CHOICE` naming an option
the product offered; an unmatched one is `FREE_TEXT`, which names no option and so
reaches `activated_schemas` and `gates_template` never. That bound is A3's, checked
by the record, and this module adds no way around it.

**Why each declaration is its own question.** `store.live_answer` defines the live
answer as the one nothing supersedes, so two roles held in one question would be
one role and a correction. Supersession is P15's correction mechanism and using it
for a second simultaneous role would encode "one permanent profession" in the
storage layer -- the exact thing §16:543 exists to prevent, and invisibly: the
person would declare a second role, watch the first vanish, and have no way to tell
a bug from a rule. So a declaration carries an id the person's own gesture minted,
and a correction is a re-declaration under the SAME id, which supersedes normally.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from questions.records import (
    AnswerNotPermitted, QuestionOption, StructuralAnswer, StructuralQuestion,
)
from questions.registry import ROLE_KIND
from questions.store import (
    live_answer, live_answer_id, questions_for, record_answer, record_question,
)
from questions.vocabulary import (
    CHOICE, CONFIRMED, EXACT_ACTIVATION, FREE_TEXT, MULTIPLE_ROLE_ACTIVATION,
    REVOKED, ROLE_OUTCOMES, SCOPE_CORPUS, SKIPPED, SKIPPED_ROLE, UNMATCHED, check,
    check_scope,
)

#: §16:551 requires "an explicit 'Other,' 'Not listed,' and 'Skip for now' path".
#: "Skip for now" is an answer STATE and already first-class; "Other" is the
#: free-text answer; this is the third. A real option carrying NO consequence,
#: because a person who says none of these fit has told the product something, and
#: the one thing that must not happen next is a resolution to the nearest schema.
NOT_LISTED: str = "not_listed"

#: The one question this module asks, in the words §16 uses for it. It is asked of
#: a PERSON who chose to declare a role, never of a corpus -- §12 permits a question
#: only where a decision is blocked, and no file blocks on what somebody does.
ROLE_PROMPT: str = "Which of these describes what this material is for you?"

#: A declaration holds the person's own description of themselves. It is not a
#: name, a credential or a document, so it is not either of the two classes above
#: this one -- and it is not `public_low` either, because §16:557 exists precisely
#: to stop it being published as a folder name. The owner should confirm this.
ROLE_HANDLING_CLASS: str = "sensitive_personal"


@dataclass(frozen=True, slots=True)
class RoleDeclaration:
    """One role a person holds, projected from the answer that records it.

    A read-side record. Nothing writes a `RoleDeclaration`; it is what
    `live_roles` returns so a caller has the four things §16:543 and §16:555 ask
    for -- the wording, the scope, the period, and the confirmation state --
    without reassembling them from two rows every time.
    """

    declaration_id: str
    scope: str
    #: §16:555: the matcher "should store the raw user wording". Set on an
    #: unmatched declaration, `None` on a confirmed one -- the two answer types
    #: are alternatives, and A3 refuses a row that is both.
    raw_wording: str | None
    #: The option the person picked, or `None`. The OPTION and not a copy of what
    #: it does: a declaration that carried the consequence as its own field would
    #: be a second place a schema is turned on, and a reader could then find the
    #: two disagreeing. It also keeps the wording and the consequence out of one
    #: another's reach -- see the note on `chosen_schema` below.
    chosen_option: QuestionOption | None
    applies_from: str | None
    applies_until: str | None
    outcome: str

    def __post_init__(self) -> None:
        check(self.outcome, ROLE_OUTCOMES, name="outcome")
        check_scope(self.scope)

    @property
    def activates_schema(self) -> str | None:
        """What the person's choice turns on, asked of the option they chose."""
        return self.chosen_option.activates_schema if self.chosen_option else None


def question_for_role_declaration(*, declaration_id: str, scope: str,
                                  schemas: Sequence[str]) -> StructuralQuestion:
    """The declaration question, offering the product's whole closed schema list.

    `schemas` is handed in with no default. This module holds no list of the
    world's professions and no list of the product's schemas: the vocabulary is
    `facts.domains.SCHEMA_IDS` and the composition root passes it, the same way
    every other authority in this project arrives from the caller.

    **Unfiltered, and that is the point.** Nothing here ranks the list against
    what the person typed, shortens it, or puts a likely answer first. Doing any
    of those from the wording IS §16's proposal step, and `62` §D holds it shut.
    When the owner's guidance arrives it changes which options this function
    offers and nothing else in this module.

    `evidence_refs` is the person's own gesture rather than a file, the same shape
    §15's household question takes: they chose to declare a role, and §14's "the
    user can see why the question arose" is answered by saying so.
    """
    check_scope(scope)
    if not declaration_id:
        raise AnswerNotPermitted(
            "a role declaration needs an id the person's own gesture minted; "
            "two roles held under one id would be one role and a correction")
    offered = tuple(dict.fromkeys(schemas))
    if not offered:
        raise AnswerNotPermitted(
            "a declaration question with no schemas offers only 'not listed'. "
            "The closed vocabulary is the caller's to supply and absent must "
            "refuse rather than resolve to an empty list")
    return StructuralQuestion(
        question_id=f"{ROLE_KIND.kind_id}:{declaration_id}",
        answer_class="structural",
        prompt=ROLE_PROMPT,
        evidence_context=(
            f"You chose to describe your role for {scope}. Nothing in your files "
            "asked this."),
        unlocks=(
            "This turns on one of the layouts the product knows, for this scope. "
            "You can hold more than one role at once, and change or withdraw any "
            "of them."),
        will_not_do=(
            "It will not become a folder name, and it will not give anything "
            "permission to move. Answering will not move, rename or delete "
            "anything."),
        scope=scope,
        handling_class=ROLE_HANDLING_CLASS,
        options=tuple(
            QuestionOption(schema_id, schema_id.replace("_", " "),
                           activates_schema=schema_id)
            for schema_id in offered
        ) + (QuestionOption(NOT_LISTED, "None of these describe it"),),
        evidence_refs=(f"declared:{scope}",))


def _record(conn: sqlite3.Connection, *, declaration_id: str, scope: str,
            schemas: Sequence[str], answer_type: str, option_id: str | None,
            raw_wording: str | None, applies_from: str | None,
            applies_until: str | None, state: str, user_id: str,
            recorded_at: str) -> str:
    """One declaration, as a question and its answer, with supersession by id.

    Re-declaring under the SAME id supersedes -- that is a correction, and §12
    requires an answer to be "edited, revoked, or re-run". Declaring under a NEW
    id does not, and that is a second role. The id is where the two are told
    apart, and it is the caller's because only the person knows which they meant.
    """
    question = question_for_role_declaration(
        declaration_id=declaration_id, scope=scope, schemas=schemas)
    record_question(conn, question, asked_at=recorded_at)
    previous = live_answer_id(conn, question_id=question.question_id, scope=scope)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=option_id, state=state,
        scope=scope, user_id=user_id, recorded_at=recorded_at,
        answer_type=answer_type, raw_wording=raw_wording,
        applies_from=applies_from, applies_until=applies_until,
        supersedes=previous,
        supersede_reason="the person corrected this role" if previous else None))
    return question.question_id


def declare_role(conn: sqlite3.Connection, *, declaration_id: str, scope: str,
                 schemas: Sequence[str], user_id: str, recorded_at: str,
                 chosen_schema: str | None = None,
                 raw_wording: str | None = None, not_listed: bool = False,
                 applies_from: str | None = None,
                 applies_until: str | None = None) -> str:
    """Record one role a person holds. Two of §16:553's four outcomes.

    `chosen_schema` is an EXACT_ACTIVATION: they picked one of the product's own
    schemas. `raw_wording` or `not_listed` is UNMATCHED: their words are kept and
    nothing is turned on.

    **The parameter is `chosen_schema` and not `activates_schema`, and the
    distinction is the point rather than a spelling.** What arrives here is the
    person's CHOICE. The consequence belongs to the option they chose, and this
    function never names it -- which is why D4's guard passes over this function
    honestly rather than by exemption: no function in P15 both reads a person's
    wording and names a schema activation, this one included.

    Both together is refused. A row carrying a chosen schema AND the sentence the
    person typed would let a later reader take the sentence as the thing that
    chose the schema -- which is the mapping `62` §D holds shut, arriving through
    the data rather than through a function.
    """
    if chosen_schema and (raw_wording or not_listed):
        raise AnswerNotPermitted(
            "a declaration names a schema AND carries the person's own wording. "
            "The two answer types are alternatives: a reader could take either as "
            "the thing that chose the schema, and reading the wording as the "
            "chooser is exactly what `62` §D holds shut")
    if not chosen_schema and not raw_wording and not not_listed:
        raise AnswerNotPermitted(
            "a declaration that names no schema and carries no wording says "
            "nothing. To leave the decision unresolved, skip it -- §14 keeps that "
            "a first-class answer and it is a different fact")
    if chosen_schema:
        return _record(
            conn, declaration_id=declaration_id, scope=scope, schemas=schemas,
            answer_type=CHOICE, option_id=chosen_schema, raw_wording=None,
            applies_from=applies_from, applies_until=applies_until,
            state=CONFIRMED, user_id=user_id, recorded_at=recorded_at)
    if not_listed:
        # A real option with no consequence, not a silence. §16:551 requires the
        # path to be explicit, and an explicit path that resolved to the nearest
        # schema would be worse than none.
        return _record(
            conn, declaration_id=declaration_id, scope=scope, schemas=schemas,
            answer_type=CHOICE, option_id=NOT_LISTED, raw_wording=None,
            applies_from=applies_from, applies_until=applies_until,
            state=CONFIRMED, user_id=user_id, recorded_at=recorded_at)
    return _record(
        conn, declaration_id=declaration_id, scope=scope, schemas=schemas,
        answer_type=FREE_TEXT, option_id=None, raw_wording=raw_wording,
        applies_from=applies_from, applies_until=applies_until,
        state=CONFIRMED, user_id=user_id, recorded_at=recorded_at)


def skip_role(conn: sqlite3.Connection, *, declaration_id: str, scope: str,
              schemas: Sequence[str], user_id: str, recorded_at: str) -> str:
    """§16:553's fourth outcome: "a skipped answer that leaves the related
    organizational decisions unresolved".

    A separate entry point rather than a flag on `declare_role`, because skipping
    is not declaring. §14 makes "skip for now" first-class and a first-class answer
    that arrives as `declare_role(..., skip=True)` is one an argument default can
    produce by accident.
    """
    return _record(
        conn, declaration_id=declaration_id, scope=scope, schemas=schemas,
        answer_type=CHOICE, option_id=None, raw_wording=None, applies_from=None,
        applies_until=None, state=SKIPPED, user_id=user_id,
        recorded_at=recorded_at)


def _outcome(answer: StructuralAnswer, option: QuestionOption | None) -> str:
    if answer.state == SKIPPED:
        return SKIPPED_ROLE
    if option is not None and option.activates_schema:
        return EXACT_ACTIVATION
    return UNMATCHED


def live_roles(conn: sqlite3.Connection, *,
               scope: str | None = None) -> tuple[RoleDeclaration, ...]:
    """Every role the person currently holds, in declaration order.

    SEVERAL, always -- the return type is a tuple and never an Optional, because
    the shape of the answer is the whole of §16:543. A reader that had to ask for
    "the role" would be asking a question the design says has no answer.

    **A WITHDRAWN role is not one you hold**, and that was wrong here until the
    panel printed its own withdrawal command and a test ran it. `live_answer`
    returns a revoked answer -- deliberately, so `open_questions` can see that the
    question was reopened -- and reading it as live made `--answer role:x=revoke`
    look like it had done nothing: the role stayed on the panel, and a revoked
    CHOICE reappeared as UNMATCHED, which says the person typed words they never
    typed. `answered_options` has excluded revoked answers since P15 shipped, so
    the schema really was off; only this reader disagreed, which is the worst
    shape for a disagreement to have.

    SKIPPED stays. §14 makes "skip for now" first-class and it is a different fact
    from a withdrawal: the person put the question aside rather than taking back an
    answer, and R2 counts it as spent because they were asked and responded.
    """
    out: list[RoleDeclaration] = []
    for row in conn.execute(
            "SELECT question_id, scope FROM structural_questions "
            "WHERE question_id LIKE ? ORDER BY first_asked_at, question_id",
            (f"{ROLE_KIND.kind_id}:%",)):
        if scope is not None and row["scope"] != scope:
            continue
        answer = live_answer(conn, question_id=row["question_id"],
                             scope=row["scope"])
        if answer is None or answer.state == REVOKED:
            continue
        question = questions_for(conn, (row["question_id"],))[0]
        option = next((candidate for candidate in question.options
                       if candidate.option_id == answer.option_id), None)
        out.append(RoleDeclaration(
            declaration_id=row["question_id"].split(":", 1)[1],
            scope=row["scope"],
            raw_wording=answer.raw_wording,
            chosen_option=option,
            applies_from=answer.applies_from,
            applies_until=answer.applies_until,
            outcome=_outcome(answer, option)))
    return tuple(out)


def outcome_of_roles(declarations: Iterable[RoleDeclaration]) -> str:
    """§16:553's outcome for the whole interaction, not for one row.

    The second outcome -- "a confirmed multiple-role activation" -- is a fact
    about the SET. Storing it on a row would make one declaration the multiple
    one, which is a first among equals in a design whose whole point is that being
    more than one thing is normal.

    No declarations at all is SKIPPED_ROLE: nothing was resolved, which is what
    that outcome means, and it is the state a person who never opened this is in.
    """
    live = tuple(declarations)
    activating = [role for role in live if role.outcome == EXACT_ACTIVATION]
    if len(activating) > 1:
        return MULTIPLE_ROLE_ACTIVATION
    if activating:
        return EXACT_ACTIVATION
    if any(role.outcome == UNMATCHED for role in live):
        return UNMATCHED
    return SKIPPED_ROLE


def _split(raw: str, *, flag: str) -> tuple[str, str]:
    """`<declaration_id>=<value>`, split at the FIRST `=` and no other.

    The first only, because `--describe-role` carries a person's own sentence and a
    sentence may contain an equals sign. Splitting on the last, or refusing more than
    one, would silently truncate somebody's words -- and §16:555 requires them stored
    "byte for byte", which a parser is as able to break as a normaliser is.
    """
    declaration_id, separator, value = raw.partition("=")
    if not declaration_id or not separator or not value:
        raise AnswerNotPermitted(
            f"{raw!r} is not a role. The form is `{flag} <name>=<what>`, where the "
            "name is yours to choose and is how you change or withdraw this one "
            "later. Holding two roles at once means giving two names.")
    return declaration_id, value


def apply_declarations(conn: sqlite3.Connection, declarations: Sequence[str], *,
                       schemas: Sequence[str], user_id: str,
                       recorded_at: str) -> tuple[str, ...]:
    """The person's own confirmations, one gesture per role they hold.

    `80` §7's second forbidden thing is what this exists to keep true: activation
    requires the person's confirmation. Every string here was typed by the person;
    nothing a model proposed reaches this function, and there is no argument through
    which it could.

    Several, and additive: each name is its own declaration, so two in one invocation
    are two roles and not a role and a correction. §16:543. Re-using a name is the
    correction, and `_record` supersedes on it.

    A value outside the offered list is refused HERE rather than by `record_answer`,
    which would refuse it too. The difference is the message: this one can say the
    flag and the closed list, where the store can only say the option ids of one
    question. Listing the whole vocabulary is not the suggestion `privacy` forbids --
    a suggestion names the NEAREST member, and this names all of them.
    """
    offered = tuple(dict.fromkeys(schemas))
    recorded: list[str] = []
    for raw in declarations:
        declaration_id, value = _split(raw, flag="--declare-role")
        if value in (SKIPPED, "skip"):
            recorded.append(skip_role(
                conn, declaration_id=declaration_id, scope=SCOPE_CORPUS,
                schemas=offered, user_id=user_id, recorded_at=recorded_at))
            continue
        if value == NOT_LISTED:
            recorded.append(declare_role(
                conn, declaration_id=declaration_id, scope=SCOPE_CORPUS,
                schemas=offered, not_listed=True, user_id=user_id,
                recorded_at=recorded_at))
            continue
        if value not in offered:
            raise AnswerNotPermitted(
                f"{value!r} is not one of the layouts this product knows, so there "
                f"is nothing for it to turn on. They are: {', '.join(offered)}. "
                f"`{NOT_LISTED}` says none of them fits, which is a real answer and "
                "turns nothing on; `skip` puts the question aside. If you would "
                "rather say it in your own words, `--describe-role` keeps them.")
        recorded.append(declare_role(
            conn, declaration_id=declaration_id, scope=SCOPE_CORPUS,
            schemas=offered, chosen_schema=value, user_id=user_id,
            recorded_at=recorded_at))
    return tuple(recorded)


def described_sentences(descriptions: Sequence[str]) -> tuple[tuple[str, str], ...]:
    """`<name>=<sentence>` pairs, parsed once and in one place.

    The composition root needs the same sentences this module records -- it hands
    them to the proposal step, which takes a sentence and not a database. Parsing
    them there as well would put a second `partition("=")` in the one module that is
    supposed to hold no logic, and the two would eventually disagree about a sentence
    containing an equals sign, which is the case `_split` exists for.

    A PARSER and nothing else: it takes no connection, records nothing, and proposes
    nothing. `apply_descriptions` is what writes.
    """
    return tuple(_split(raw, flag="--describe-role") for raw in descriptions)


def apply_descriptions(conn: sqlite3.Connection, descriptions: Sequence[str], *,
                       schemas: Sequence[str], user_id: str,
                       recorded_at: str) -> tuple[str, ...]:
    """The person's own words, kept whole and turned into nothing.

    §16:555 requires the raw wording stored, and `80` §1.3 requires that nothing
    discards the sentence. This is where a sentence enters the product, and it is
    the ONLY place: `proposal.propose_roles` reads one and writes nothing, and a
    local model that narrowed the list would still leave the choosing to the person
    through `apply_declarations` above.

    It activates nothing, and not by policy: the answer is `FREE_TEXT`, `FREE_TEXT`
    selects no option, and an answer that selects no option reaches
    `store.activated_schemas` never. §16:547's "an unmatched answer must remain
    unmatched", enforced by the data model.

    `80` §2 rules the sentence a `user_edits` item -- always local, no exception,
    consent does not unlock it -- and `proposal.SELF_DESCRIPTION_ITEM` is where this
    package names the same member P7 refuses on.
    """
    offered = tuple(dict.fromkeys(schemas))
    recorded: list[str] = []
    for declaration_id, wording in described_sentences(descriptions):
        recorded.append(declare_role(
            conn, declaration_id=declaration_id, scope=SCOPE_CORPUS,
            schemas=offered, raw_wording=wording, user_id=user_id,
            recorded_at=recorded_at))
    return tuple(recorded)
