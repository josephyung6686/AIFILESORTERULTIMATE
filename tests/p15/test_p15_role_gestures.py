# tests/p15/test_p15_role_gestures.py
"""The two gestures a person makes, and what each one may and may not reach.

`80` §7's second forbidden thing -- "No model output activates anything. Activation
requires the person's confirmation, as a hard invariant rather than a default" -- has
two halves. `test_p15_proposal.py` holds the half about the model: the proposal step
imports nothing that writes. This file holds the half about the person: everything
that writes takes a string the person typed, and there is no argument on either
entry point through which a proposal could arrive instead.

The second gesture is `80` §4 (R5): "The raw sentence stays recorded and visible
rather than discarded." Recorded it has been since A3. Visible it was not -- nothing
printed `raw_wording` anywhere -- which made "we kept your words" a promise with no
surface behind it.
"""
from __future__ import annotations

import inspect
import sqlite3

import pytest

from facts.domains import SCHEMA_IDS
from questions.explanation import explain_question, render_explanation
from questions.records import AnswerNotPermitted
from questions.roles import (
    NOT_LISTED, apply_declarations, apply_descriptions, live_roles,
    outcome_of_roles,
)
from questions.schema import create_questions_schema
from questions.store import activated_schemas, set_aside_questions
from questions.vocabulary import MULTIPLE_ROLE_ACTIVATION, UNMATCHED

T0 = "2026-08-31T10:00:00+00:00"
T1 = "2026-08-31T11:00:00+00:00"


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def _declare(conn, *declarations, at=T0):
    return apply_declarations(conn, declarations, schemas=SCHEMA_IDS, user_id="jy",
                              recorded_at=at)


def _describe(conn, *descriptions, at=T0):
    return apply_descriptions(conn, descriptions, schemas=SCHEMA_IDS, user_id="jy",
                              recorded_at=at)


# --- the confirming gesture ---------------------------------------------------------


def test_two_roles_in_one_invocation_are_two_roles(qconn):
    """§16:543 through the gesture rather than through the record. Two names are two
    declarations; using one name twice is the correction."""
    _declare(qconn, "studying=academic", "teaching=research")

    assert outcome_of_roles(live_roles(qconn)) == MULTIPLE_ROLE_ACTIVATION
    assert activated_schemas(qconn) == frozenset({"academic", "research"})


def test_reusing_a_name_corrects_that_role_and_leaves_the_other_alone(qconn):
    _declare(qconn, "studying=academic", "teaching=research")
    _declare(qconn, "studying=legal", at=T1)

    assert activated_schemas(qconn) == frozenset({"legal", "research"})
    assert len(live_roles(qconn)) == 2


def test_not_listed_is_a_real_answer_and_turns_nothing_on(qconn):
    """§16:551 requires the explicit path; §16:547 requires that taking it resolves
    to nothing. A person who says none of these fit has told the product something,
    and the one thing that must not happen next is a snap to the nearest schema."""
    _declare(qconn, f"sound={NOT_LISTED}")

    assert live_roles(qconn)[0].outcome == UNMATCHED
    assert activated_schemas(qconn) == frozenset()


def test_skipping_leaves_the_question_where_a_person_can_find_it_again(qconn):
    """§14's first-class "skip for now", and the way back. `set_aside_questions`
    exists because a skipped question's id is otherwise printed nowhere, which made
    a choice the design calls reversible reversible only by someone who had kept the
    earlier screen."""
    _declare(qconn, "studying=skip")

    assert activated_schemas(qconn) == frozenset()
    assert [question.question_id for question in set_aside_questions(qconn)] == [
        "role:studying"]


def test_a_layout_this_product_does_not_have_is_refused_with_the_whole_list(qconn):
    """Refused here rather than at the store, for the message rather than for the
    rule. `record_answer` refuses it too and can only name one question's options;
    this can name the flag and the closed vocabulary.

    Naming ALL of them is not the suggestion `privacy._check` forbids. A suggestion
    names the NEAREST member, which is how a misspelling becomes a silent choice.
    """
    with pytest.raises(AnswerNotPermitted) as refusal:
        _declare(qconn, "sound=sound_engineering")

    assert "academic" in str(refusal.value)
    assert "legal" in str(refusal.value)
    assert live_roles(qconn) == ()


def test_a_gesture_with_no_name_is_refused(qconn):
    """The name is how the person changes or withdraws this role later, and holding
    two at once means giving two names. A declaration with none would be one
    permanent profession arriving through the command line."""
    for malformed in ("academic", "=academic", "studying=", ""):
        with pytest.raises(AnswerNotPermitted, match="is not a role"):
            _declare(qconn, malformed)


def test_neither_gesture_can_be_handed_a_proposal(qconn):
    """`80` §7's second forbidden thing, at the two functions that write.

    Both take strings and a schema list, and neither takes a `RoleProposal`, a
    model, or anything a model produced. There is no argument through which a
    proposal could arrive, which is what makes "activation requires the person's
    confirmation" an invariant rather than a convention about how to call these.
    """
    for gesture in (apply_declarations, apply_descriptions):
        parameters = set(inspect.signature(gesture).parameters)
        assert parameters & {"proposal", "propose", "model", "candidates",
                             "shortlist"} == set()


# --- the describing gesture, and R5's "visible" ------------------------------------


def test_a_persons_own_words_are_kept_and_turn_nothing_on(qconn):
    """§16:555 and §16:547 together. The sentence is stored byte for byte, and
    because it is FREE_TEXT it selects no option, so it reaches `activated_schemas`
    never -- the data model doing the work rather than a downstream policy."""
    sentence = "I run sound for a venue and do the books for my mum's shop"
    _describe(qconn, f"sound={sentence}")

    role = live_roles(qconn)[0]
    assert role.raw_wording == sentence
    assert role.outcome == UNMATCHED
    assert activated_schemas(qconn) == frozenset()


def test_a_sentence_with_an_equals_sign_in_it_is_kept_whole(qconn):
    """Split at the FIRST `=` and no other. §16:555 requires the raw wording, and a
    parser can truncate somebody's words as surely as a normaliser can."""
    sentence = "I teach A=B logic and I am also a parent"
    _describe(qconn, f"teaching={sentence}")

    assert live_roles(qconn)[0].raw_wording == sentence


def test_the_sentence_a_person_typed_is_visible_afterwards(qconn):
    """`80` §4 (R5): "The raw sentence stays recorded and visible rather than
    discarded." Both halves, and until this landed only the first was true.

    It prints BEFORE "what it controls: nothing", because a person reading that the
    answer controls nothing without first seeing their own words would reasonably
    read it as their words having been thrown away.
    """
    sentence = "I'm a graduate student who also teaches one lab section"
    _describe(qconn, f"studying={sentence}")

    explanation = explain_question(qconn, "role:studying")
    assert explanation.your_words == sentence

    rendered = render_explanation(explanation)
    assert sentence in rendered
    assert rendered.index(sentence) < rendered.index("What it controls")


def test_an_answer_that_chose_an_option_has_no_words_of_its_own(qconn):
    """The negative twin. The two answer types are alternatives, and an explanation
    showing both would let a reader take the sentence as the thing that chose the
    schema -- which is the mapping `62` §D held shut and `80` §1.3 replaced with a
    step the person confirms."""
    _declare(qconn, "studying=academic")

    explanation = explain_question(qconn, "role:studying")
    assert explanation.your_words is None
    assert explanation.controls == ("It turns on the `academic` schema.",)


def test_describing_then_confirming_supersedes_and_activates(qconn):
    """The whole of Option 2's shape, in two gestures the person makes.

    They say it in their own words; nothing is turned on. They then confirm one of
    the product's own layouts under the same name; that one is on, and it is on
    because they picked it. A local model, if one existed, would only have made the
    list they picked from shorter.
    """
    _describe(qconn, "studying=I'm a graduate student in physics")
    assert activated_schemas(qconn) == frozenset()

    _declare(qconn, "studying=academic", at=T1)

    assert activated_schemas(qconn) == frozenset({"academic"})
    assert len(live_roles(qconn)) == 1
    assert live_roles(qconn)[0].raw_wording is None


def test_the_sentences_are_parsed_in_one_place(qconn):
    """`described_sentences` is the same parser `apply_descriptions` uses, exposed
    because the composition root needs the sentences too -- the proposal step takes
    a sentence and not a database.

    One home, because a second `partition("=")` in `cli.py` would eventually disagree
    with this one about a sentence containing an equals sign, and the person whose
    words got truncated would have no way to see why.
    """
    from questions.roles import described_sentences

    raw = ("studying=I do a part-time diploma", "logic=I teach A=B logic")
    assert described_sentences(raw) == (
        ("studying", "I do a part-time diploma"), ("logic", "I teach A=B logic"))

    _describe(qconn, *raw)
    assert {role.raw_wording for role in live_roles(qconn)} == {
        wording for _, wording in described_sentences(raw)}


def test_the_parser_writes_nothing(qconn):
    """A parser that took a connection would be a second writer, and the invariant
    that matters most is that only the person's confirmation writes."""
    import inspect

    from questions.roles import described_sentences

    assert list(inspect.signature(described_sentences).parameters) == ["descriptions"]
    described_sentences(("studying=anything at all",))
    assert live_roles(qconn) == ()
