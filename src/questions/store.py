# src/questions/store.py
"""Writing and reading P15's questions and answers.

The one property everything here serves: **an answer outlives the run that asked
for it**. `66` §12 rejects "a weekly questionnaire" and requires the product to
"ask a question only when a specific decision is blocked" -- and a product that
forgot the answer would block on the same decision, and ask again, on every run.
That is what makes this a store rather than a value passed down a call stack.

Append-only, with supersession, for the reason §12 gives: an answer must be
"edited, revoked, or re-run". An edit that overwrote the row would lose that the
person once said something else, and a plan frozen under the old answer would have
no record of why it looks the way it does.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
import uuid
from collections.abc import Mapping, Sequence

from evidence_shape.canonical import canonical_json

from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.vocabulary import BINDING_STATES, REVOKED, SKIPPED


#: The prefix a `residual:<area>` question id carries. Here and not in
#: `registry.py`, where the other five kind ids are literals, because
#: `residual_choices` below has to take the id APART to name the area and
#: `registry` imports its readers from this module -- so the reader and the
#: prefix it parses live together and the kind reads both from one place.
RESIDUAL_KIND_ID: str = "residual"


class AnswerConflict(ValueError):
    """An answer that does not belong to the question it names."""


def _forget_settled(conn: sqlite3.Connection) -> None:
    """Drop the binding-answer cache. The next read sees this write."""
    from database_agent.db import connection_cache

    cache = connection_cache(conn, "_answered_options")
    if cache is not None:
        cache.clear()


def record_question(conn: sqlite3.Connection, question: StructuralQuestion, *,
                    asked_at: str) -> str:
    """Record that the product raised this question. Idempotent by question id.

    A second run over the same corpus raises the same question from the same
    evidence, and that is ONE question asked twice -- not two. `first_asked_at` is
    preserved on the re-ask, because when the person was first asked something is
    part of the history §12's revocation story reads, and a product that keeps
    resetting it cannot tell a question it has raised once from one it has raised
    for the fortieth time.
    """
    _forget_settled(conn)
    conn.execute(
        "INSERT INTO structural_questions "
        "(question_id, answer_class, prompt, evidence_context, unlocks, "
        " will_not_do, scope, handling_class, options, evidence_refs, "
        " first_asked_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT (question_id) DO NOTHING",
        (question.question_id, question.answer_class, question.prompt,
         question.evidence_context, question.unlocks, question.will_not_do,
         question.scope, question.handling_class,
         # `asdict`, not a hand-written field list. The list was here first and
         # dropped `gates_template` silently the day it was added: the question
         # stored fine, rehydrated fine, and simply gated nothing. Any field this
         # record gains now round-trips, and `_question_of` already reconstructs
         # with `QuestionOption(**option)`, so the two halves cannot drift apart.
         canonical_json([asdict(option) for option in question.options]),
         canonical_json(list(question.evidence_refs)), asked_at))
    return question.question_id


def reask_question(conn: sqlite3.Connection, question: StructuralQuestion, *,
                   recorded_at: str, reason: str) -> None:
    """Ask a question again because its live answer names an option it no
    longer offers.

    The question row takes today's wording and options (`first_asked_at` is
    kept), and the live answer is superseded by a `revoked` row carrying
    `reason` -- append-only, so what the person said before stays readable.
    A revoked answer reopens its question in `open_questions`.
    """
    record_question(conn, question, asked_at=recorded_at)
    conn.execute(
        "UPDATE structural_questions SET prompt = ?, evidence_context = ?, "
        "unlocks = ?, options = ? WHERE question_id = ?",
        (question.prompt, question.evidence_context, question.unlocks,
         canonical_json([asdict(option) for option in question.options]),
         question.question_id))
    previous = live_answer(conn, question_id=question.question_id,
                           scope=question.scope)
    if previous is None or previous.state == REVOKED:
        return
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=None, state=REVOKED,
        scope=question.scope, user_id=previous.user_id,
        recorded_at=recorded_at,
        supersedes=live_answer_id(conn, question_id=question.question_id,
                                  scope=question.scope),
        supersede_reason=reason))


def _question_row(conn: sqlite3.Connection, question_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM structural_questions WHERE question_id = ?",
        (question_id,)).fetchone()


def _question_of(row: sqlite3.Row) -> StructuralQuestion:
    return StructuralQuestion(
        question_id=row["question_id"], answer_class=row["answer_class"],
        prompt=row["prompt"], evidence_context=row["evidence_context"],
        unlocks=row["unlocks"], will_not_do=row["will_not_do"],
        scope=row["scope"], handling_class=row["handling_class"] or "",
        options=tuple(QuestionOption(**option)
                      for option in json.loads(row["options"])),
        evidence_refs=tuple(json.loads(row["evidence_refs"])))


def the_option_they_named(conn: sqlite3.Connection, question_id: str,
                          typed: str) -> str:
    """The option id for the word the person typed.

    The id itself is accepted, which is every answer already on record. The
    word printed beside that id is accepted too, when exactly one option
    wears it: the screen says Coursework, and that is what they can paste.
    Two options with one word is not a choice they can make by that word, so
    the typed string is returned unchanged and the recorder refuses it.
    """
    row = _question_row(conn, question_id)
    if row is None:
        return typed
    options = _question_of(row).options
    if typed in {option.option_id for option in options}:
        return typed
    matched = [option.option_id for option in options if option.label == typed]
    return matched[0] if len(matched) == 1 else typed


def record_answer(conn: sqlite3.Connection, answer: StructuralAnswer) -> str:
    """Record one answer, and return its id so a later edit can supersede it."""
    _forget_settled(conn)
    row = _question_row(conn, answer.question_id)
    if row is None:
        raise AnswerConflict(
            f"{answer.question_id!r} names no question this run asked. An answer "
            "with no question is an assertion about the user that nothing "
            "prompted, which is the profile data §12 declines to collect")
    question = _question_of(row)
    if (answer.option_id is not None
            and answer.option_id not in {option.option_id
                                         for option in question.options}):
        raise AnswerConflict(
            f"{question.question_id!r} does not offer {answer.option_id!r}; it "
            f"offers {sorted(option.option_id for option in question.options)}. "
            "A caller must not widen the option set by answering")
    answer_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO structural_answers "
        "(answer_id, question_id, option_id, answer_type, raw_wording, "
        " applies_from, applies_until, state, scope, user_id, "
        " recorded_at, inferred, supersedes, supersede_reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (answer_id, answer.question_id, answer.option_id, answer.answer_type,
         answer.raw_wording, answer.applies_from, answer.applies_until,
         answer.state, answer.scope, answer.user_id, answer.recorded_at,
         1 if answer.inferred else 0, answer.supersedes, answer.supersede_reason))
    return answer_id


def _answer_of(row: sqlite3.Row) -> StructuralAnswer:
    return StructuralAnswer(
        question_id=row["question_id"], option_id=row["option_id"],
        answer_type=row["answer_type"], raw_wording=row["raw_wording"],
        applies_from=row["applies_from"], applies_until=row["applies_until"],
        state=row["state"], scope=row["scope"], user_id=row["user_id"],
        recorded_at=row["recorded_at"], inferred=bool(row["inferred"]),
        supersedes=row["supersedes"], supersede_reason=row["supersede_reason"])


def answer_by_id(conn: sqlite3.Connection,
                 answer_id: str) -> StructuralAnswer | None:
    """One answer by the id `record_answer` minted for it.

    The store is append-only and an edit writes a new row naming the one it
    supersedes, so the ONLY way to read what a person said before is by that name.
    Without this reader `supersedes` was a pointer with nothing to follow it, and
    §17's diff -- which is entirely about what changed FROM what -- could not be
    computed at all.
    """
    row = conn.execute("SELECT * FROM structural_answers WHERE answer_id = ?",
                       (answer_id,)).fetchone()
    return None if row is None else _answer_of(row)


def _live_row(conn: sqlite3.Connection, *, question_id: str,
              scope: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT a.* FROM structural_answers AS a "
        "WHERE a.question_id = ? AND a.scope = ? AND NOT EXISTS ("
        "  SELECT 1 FROM structural_answers AS later "
        "  WHERE later.supersedes = a.answer_id) "
        "ORDER BY a.recorded_at DESC, a.answer_id DESC LIMIT 1",
        (question_id, scope)).fetchone()


def live_answer(conn: sqlite3.Connection, *, question_id: str,
                scope: str) -> StructuralAnswer | None:
    """The answer that governs this question in this scope, or None.

    The live one is the one nothing supersedes. Ordered by `recorded_at` as the
    tie-break so a database written by two processes in one clock tick still has a
    deterministic answer rather than an arbitrary one.
    """
    row = _live_row(conn, question_id=question_id, scope=scope)
    return None if row is None else _answer_of(row)


def live_answer_id(conn: sqlite3.Connection, *, question_id: str,
                   scope: str) -> str | None:
    """The id of the answer `live_answer` returns, so an edit can supersede it.

    `StructuralAnswer` carries no `answer_id` -- the id is minted at write time by
    `record_answer`, which returns it "so a later edit can supersede it". A caller
    holding only the record therefore has the answer and not its name, and a caller
    that wants to supersede needs the name. This is that reader, over the SAME row
    `live_answer` selects, so the two can never disagree about which answer is live.

    Without it the tie-break above is doing work it was never meant to do. It exists
    so two processes in one clock tick still resolve deterministically; it is not a
    way to choose between two answers ONE person gave, and it decides at random
    which correction the product obeys when it is asked to.
    """
    row = _live_row(conn, question_id=question_id, scope=scope)
    return None if row is None else row["answer_id"]


def open_questions(conn: sqlite3.Connection) -> tuple[StructuralQuestion, ...]:
    """Every question the product has raised and the person has not settled.

    A REVOKED answer reopens its question. That is the point of revocation: the
    person has withdrawn what they said, and a question that stayed closed would
    leave them unable ever to be asked again about a decision they deliberately
    reopened.
    """
    out: list[StructuralQuestion] = []
    for row in conn.execute(
            "SELECT * FROM structural_questions ORDER BY first_asked_at, "
            "question_id"):
        answer = live_answer(conn, question_id=row["question_id"],
                             scope=row["scope"])
        if answer is None or answer.state == REVOKED:
            out.append(_question_of(row))
    return tuple(out)


def set_aside_questions(conn: sqlite3.Connection) -> tuple[StructuralQuestion, ...]:
    """Every question the person skipped and has not since settled or withdrawn.

    `open_questions` deliberately excludes these: §14 makes "skip for now"
    first-class and §12 forbids re-asking, so a skipped question does not come
    back. That is right, and this is not a way around it -- nothing here is
    asked again.

    It exists because the way BACK was unreachable. Revocation reopens a
    question, but `--answer <id>=revoke` needs the id, and once a question is
    skipped its id is printed nowhere at all. So a choice the design calls
    reversible was reversible only by someone who had kept the earlier screen.
    The caller shows the id and nothing else.
    """
    out: list[StructuralQuestion] = []
    for row in conn.execute(
            "SELECT * FROM structural_questions ORDER BY first_asked_at, "
            "question_id"):
        answer = live_answer(conn, question_id=row["question_id"],
                             scope=row["scope"])
        if answer is not None and answer.state == SKIPPED:
            out.append(_question_of(row))
    return tuple(out)


def answered_options(conn: sqlite3.Connection, *,
                     scope: str | None = None) -> tuple[QuestionOption, ...]:
    """Every option a BINDING answer selected, with what that option does.

    This is the seam the rest of the product consumes: a caller asks what the
    person has actually settled and gets back the options, not the raw rows. Only
    `confirmed` answers are binding -- a skip, a "not about me" and a revocation
    all decide nothing, which is what makes them safe to offer.

    A scan asks this once per explanation, and an explanation is asked several
    times per file. The table does not change between those reads. A question
    or an answer written on this connection drops the cache, so a gesture
    recorded earlier in the same invocation is visible to the next read.
    """
    from database_agent.db import connection_cache

    cache = connection_cache(conn, "_answered_options")
    if cache is not None and scope in cache:
        return cache[scope]
    out: list[QuestionOption] = []
    for row in conn.execute("SELECT * FROM structural_questions "
                            "ORDER BY question_id"):
        if scope is not None and row["scope"] != scope:
            continue
        answer = live_answer(conn, question_id=row["question_id"],
                             scope=row["scope"])
        if answer is None or answer.state not in BINDING_STATES:
            continue
        for option in _question_of(row).options:
            if option.option_id == answer.option_id:
                out.append(option)
    found = tuple(out)
    if cache is not None:
        cache[scope] = found
    return found


def activated_schemas(conn: sqlite3.Connection, *,
                      scope: str | None = None) -> frozenset[str]:
    """The schemas the person's own confirmed answers activate.

    `66` §13: a structural answer "may ACTIVATE A SCHEMA". This is the whole of
    that consequence, in one place, so a reader can see every schema the user
    turned on and where it came from.
    """
    return frozenset(
        option.activates_schema
        for option in answered_options(conn, scope=scope)
        if option.activates_schema)


def gated_template(conn: sqlite3.Connection, *, scope: str) -> str | None:
    """The nesting the person chose for ONE branch, or `None` if they have not.

    `66` §13: a structural answer "may ... GATE A TEMPLATE". This is the whole of
    that consequence, in one place, for the same reason `activated_schemas` is.

    Scoped, and required to be -- `scope` has no default here where it does on
    `activated_schemas`, because a nesting answer is about one branch and §13
    forbids reusing an answer "outside its stated scope". A corpus-wide read would
    let the shape somebody chose for their coursework decide the shape of their
    legal matters.

    `None` for unanswered AND for skipped, which are different facts about the
    person and the same fact about the tree: neither chose a nesting, so the
    caller keeps whatever default it would have used. That is what makes asking
    free -- the run still produces the tree it produced before.
    """
    chosen = [option.gates_template
              for option in answered_options(conn, scope=scope)
              if option.gates_template]
    return chosen[0] if chosen else None


def selected_situation(conn: sqlite3.Connection, *, scope: str) -> str | None:
    """The situation the person chose for ONE branch, or `None` if they have not.

    `66` §13: a structural answer may "RESOLVE ROLE AMBIGUITY". This is the whole
    of that consequence, in one place, for the same reason `activated_schemas` and
    `gated_template` are each in one place.

    Scoped, and required to be -- no default, exactly as `gated_template` has none.
    A corpus-wide read would be `--situation` again under a new name, and
    `--situation` is the thing this exists to narrow: `68` F6 recorded a graduate
    student who also teaches having her whole disk filed as coursework because the
    command line takes one string.

    `None` for unanswered AND for skipped and "not about me". Those are different
    facts about the person and the same fact about the tree: nobody chose, so the
    caller keeps the situation the run was given, and the run produces the tree it
    produced before. That is what makes asking free.
    """
    chosen = [option.selects_situation
              for option in answered_options(conn, scope=scope)
              if option.selects_situation]
    return chosen[0] if chosen else None


def chosen_destination(conn: sqlite3.Connection, *,
                       scope: str) -> str | None:
    """The destination the person named for ONE folder, or `None` if they have not.

    `66` §13's fourth consequence, in one place, for the same reason the three
    above it are each in one place: a reader can see every destination the user
    chose and where it came from, and a second path to the same effect would
    falsify that sentence.

    Scoped, and required to be. `gated_template` records why a nesting answer may
    not be read corpus-wide; this is the same rule with more at stake, because the
    thing being reused outside its scope would be an instruction about where files
    go. A person who says a folder of unreadable scans belongs under `Vaccine
    records` has said that about THOSE files.

    `None` for unanswered, for skipped and for revoked -- `answered_options`
    already draws that line. All three mean the same thing to placement: nobody
    named a destination, so the run decides exactly as it did before, which is
    what makes asking free.
    """
    named = [option.chooses_destination
             for option in answered_options(conn, scope=scope)
             if option.chooses_destination]
    return named[0] if named else None


def residual_choices(conn: sqlite3.Connection, *,
                     scope: str) -> Mapping[str, str]:
    """What the person has settled about each catch-all area, by area.

    `66` §13's fifth consequence, in one place, for the reason the four above it
    are each in one place: a reader can see every area the user decided about and
    where the decision came from, and a second path to the same effect would
    falsify that sentence.

    **A MAPPING where `gated_template` returns one value.** A nesting answer is
    about one branch and the branch IS the scope, so naming the scope names the
    answer. Every residual area is settled at the SAME scope -- §7.4's areas are
    the whole corpus's -- and which area an answer is about is in the question
    id. A reader returning one value could not say which of the nine it meant,
    and one call per area would walk this table nine times to read at most nine
    rows.

    The id is split ONCE, after the kind. `--define-residual` lets a person name
    an area of their own and an area name may hold a `:`; splitting on the last
    one would take `Notes: 2024` apart and report an area nobody named.

    Absent for unanswered, for skipped and for revoked -- `answered_options`
    already draws that line, and all three mean the same thing to the tree:
    nobody told this run to build the area, so it builds the plan it built
    before. That is what makes asking free.
    """
    prefix = f"{RESIDUAL_KIND_ID}:"
    out: dict[str, str] = {}
    for row in conn.execute("SELECT * FROM structural_questions "
                            "ORDER BY question_id"):
        question_id = row["question_id"]
        if not question_id.startswith(prefix) or row["scope"] != scope:
            continue
        answer = live_answer(conn, question_id=question_id, scope=row["scope"])
        if answer is None or answer.state not in BINDING_STATES:
            continue
        for option in _question_of(row).options:
            if option.option_id == answer.option_id and option.residual_action:
                out[question_id[len(prefix):]] = option.residual_action
    return out


def _confirmed_values(conn: sqlite3.Connection, field: str) -> tuple[str, ...]:
    """The values a confirmed answer set on one option field, in question order.

    Skipped, revoked, and not-about-me answers contribute nothing. That is the
    same line `answered_options` draws, so a decline cannot become a life.
    """
    values: list[str] = []
    for option in answered_options(conn):
        value = getattr(option, field, None)
        if value and value not in values:
            values.append(value)
    return tuple(values)


def declared_lives(conn: sqlite3.Connection, *,
                   scope: str | None = None) -> frozenset[str]:
    """Schemas the person has declared as filing lives for this corpus.

    A refusal wins a contradiction: a schema both declared and refused is not
    declared. An empty set means nobody has confirmed a life, which is not an
    allow-list of nothing — the recogniser treats empty as 'no profile'.
    """
    if scope is not None:
        declared = [
            option.declares_life for option in answered_options(conn, scope=scope)
            if option.declares_life]
        refused = {
            option.refuses_life for option in answered_options(conn, scope=scope)
            if option.refuses_life}
    else:
        declared = list(_confirmed_values(conn, "declares_life"))
        refused = set(_confirmed_values(conn, "refuses_life"))
    return frozenset(value for value in declared if value not in refused)


def refused_lives(conn: sqlite3.Connection, *,
                  scope: str | None = None) -> frozenset[str]:
    """Schemas the person has explicitly refused for this corpus."""
    if scope is not None:
        return frozenset(
            option.refuses_life for option in answered_options(conn, scope=scope)
            if option.refuses_life)
    return frozenset(_confirmed_values(conn, "refuses_life"))


def named_projects(conn: sqlite3.Connection) -> tuple[str, ...]:
    """Folder names the person asked to treat as one project."""
    return _confirmed_values(conn, "names_project")


def left_alone(conn: sqlite3.Connection) -> tuple[str, ...]:
    """Names the person asked the product to leave alone."""
    return _confirmed_values(conn, "leaves_alone")


def named_courses(conn: sqlite3.Connection) -> tuple[str, ...]:
    """Courses the person named. Not matched against files by this reader."""
    return _confirmed_values(conn, "names_course")


def profile_wording(conn: sqlite3.Connection) -> tuple[str, ...]:
    """Sentences the person typed about this folder, in the order they were kept.

    Free text only. A choice that named a schema is not a sentence, and this
    reader does not turn the sentence into a schema. The words stay in this
    database; nothing here builds a request.
    """
    out: list[str] = []
    for row in conn.execute(
            "SELECT question_id, scope FROM structural_questions "
            "WHERE question_id LIKE 'wording:%' ORDER BY first_asked_at, "
            "question_id"):
        answer = live_answer(conn, question_id=row["question_id"],
                             scope=row["scope"])
        if (answer is None or answer.state not in BINDING_STATES
                or not answer.raw_wording):
            continue
        if answer.raw_wording not in out:
            out.append(answer.raw_wording)
    return tuple(out)


def questions_for(conn: sqlite3.Connection,
                  question_ids: Sequence[str]) -> tuple[StructuralQuestion, ...]:
    """The named questions, for a caller that already knows which it wants."""
    out: list[StructuralQuestion] = []
    for question_id in question_ids:
        row = _question_row(conn, question_id)
        if row is not None:
            out.append(_question_of(row))
    return tuple(out)
