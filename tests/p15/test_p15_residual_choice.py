# tests/p15/test_p15_residual_choice.py
"""§13's fifth consequence: what happens to one of §7.4's catch-all areas.

`110` §2.4 item 1. The other four consequences a structural answer may carry each
have a kind in the registry and a reader in the store, and a residual choice had
neither -- it lived in one invocation's argv, so the product forgot which areas a
person had turned on the moment the command ended.

**The action and nothing else.** `RESIDUAL_LIBRARY_ACTIONS` is already a closed
vocabulary and no member is added here. What a `QuestionOption` cannot carry is
the ARGUMENT four of the six actions take -- the name for a rename, the folder for
a relocate, the area for a merge, the node for a replace -- and
`StructuralAnswer.raw_wording`, the record's only free-text field, is refused
beside a chosen option by name. So the two actions that ARE their whole decision
are the two this kind records, and the composition root says which ones it could
not keep rather than dropping them quietly.

**The reader returns a MAPPING** where `gated_template` returns one value. A
nesting answer is about one branch and the branch IS the scope; every residual
area is settled at the same scope and the area is in the question id, so a reader
that returned one value could not say which area it was about.
"""
from __future__ import annotations

import dataclasses
import sqlite3

import pytest

from questions.records import (
    AnswerNotPermitted, QuestionOption, StructuralAnswer, StructuralQuestion,
)
from questions.registry import (
    QUESTION_KINDS, RESIDUAL_KIND, option_consequence_fields, kind_of,
)
from questions.schema import create_questions_schema
from questions.store import record_answer, record_question, residual_choices
from questions.vocabulary import (
    CONFIRMED, CONTEXTUAL, REVOKED, SCOPE_CORPUS, SKIPPED, STRUCTURAL,
)
from tree_design.vocabulary import DISABLE, ENABLE, RESIDUAL_LIBRARY_ACTIONS

T0 = "2026-09-20T10:00:00+00:00"
T1 = "2026-09-20T11:00:00+00:00"
AREA = "Review Later"


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    return connection


def _question(area: str = AREA, *, answer_class: str = STRUCTURAL
              ) -> StructuralQuestion:
    return StructuralQuestion(
        question_id=f"{RESIDUAL_KIND.kind_id}:{area}",
        answer_class=answer_class,
        prompt=f"What should happen to the catch-all area {area}?",
        evidence_context=f"You named {area} on the command line.",
        unlocks="This decides whether the area is in your plan.",
        will_not_do="Answering moves nothing.",
        scope=SCOPE_CORPUS,
        handling_class="public_low",
        options=(QuestionOption(ENABLE, "Keep it", residual_action=ENABLE),
                 QuestionOption(DISABLE, "Leave it out",
                                residual_action=DISABLE)),
        evidence_refs=(f"typed:{area}",))


def _answer(conn, area: str, option_id: str, *, state: str = CONFIRMED,
            recorded_at: str = T0, supersedes: str | None = None) -> str:
    return record_answer(conn, StructuralAnswer(
        question_id=f"{RESIDUAL_KIND.kind_id}:{area}", option_id=option_id,
        state=state, scope=SCOPE_CORPUS, user_id="jy",
        recorded_at=recorded_at, supersedes=supersedes,
        supersede_reason="the person changed their mind" if supersedes
        else None))


def test_the_kind_is_registered_and_claims_the_consequence():
    """`registry.py` refuses a kind whose consequence nothing reads, and
    `test_p15_registry` refuses a consequence no kind claims. Both directions."""
    assert RESIDUAL_KIND in QUESTION_KINDS
    assert RESIDUAL_KIND.consequence_field == "residual_action"
    assert RESIDUAL_KIND.consequence_field in option_consequence_fields()
    assert RESIDUAL_KIND.scope_kind == SCOPE_CORPUS
    assert callable(RESIDUAL_KIND.reader)
    assert kind_of(f"{RESIDUAL_KIND.kind_id}:{AREA}") is RESIDUAL_KIND


def test_the_reader_returns_the_area_and_what_was_settled_about_it(qconn):
    record_question(qconn, _question(), asked_at=T0)
    _answer(qconn, AREA, ENABLE)
    assert residual_choices(qconn, scope=SCOPE_CORPUS) == {AREA: ENABLE}


def test_an_area_with_a_colon_in_its_name_is_still_read_back(qconn):
    """The question id is `residual:<area>` and an area name may hold a `:` --
    `--define-residual` lets a person name one of their own. Splitting on the
    LAST colon would take the area apart; the reader splits once, after the kind.
    """
    area = "Notes: 2024"
    record_question(qconn, _question(area), asked_at=T0)
    _answer(qconn, area, ENABLE)
    assert residual_choices(qconn, scope=SCOPE_CORPUS) == {area: ENABLE}


def test_a_revoked_answer_leaves_no_choice_behind(qconn):
    """§12: an answer is "edited, revoked, or re-run". A withdrawn enablement is
    an area the product has not been told to build, which is the same fact about
    the tree as never having been told."""
    record_question(qconn, _question(), asked_at=T0)
    first = _answer(qconn, AREA, ENABLE)
    _answer(qconn, AREA, ENABLE, state=REVOKED, recorded_at=T1,
            supersedes=first)
    assert residual_choices(qconn, scope=SCOPE_CORPUS) == {}


def test_a_skipped_answer_settles_nothing(qconn):
    """`option_id` is `None` on a skip and the record refuses it any other way:
    "skipping is not choosing, and a record that cannot tell them apart will
    treat a decline as a decision"."""
    record_question(qconn, _question(), asked_at=T0)
    _answer(qconn, AREA, None, state=SKIPPED)
    assert residual_choices(qconn, scope=SCOPE_CORPUS) == {}


def test_a_disable_is_remembered_as_a_disable_and_not_as_an_absence(qconn):
    """Two different facts: an area nobody decided about, and one the person
    said to leave out. §7.4 asks one question per area and `disable` is an
    answer to it."""
    record_question(qconn, _question(), asked_at=T0)
    _answer(qconn, AREA, DISABLE)
    assert residual_choices(qconn, scope=SCOPE_CORPUS) == {AREA: DISABLE}


def test_only_the_actions_the_vocabulary_already_holds_may_be_recorded(qconn):
    """No new member. `110` §2.4: "The area names and action words are already
    closed vocabulary (`RESIDUAL_LIBRARY_ACTIONS`); no new member"."""
    for action in (ENABLE, DISABLE):
        assert action in RESIDUAL_LIBRARY_ACTIONS


def test_a_contextual_question_may_not_settle_an_area(qconn):
    """§13 forbids a contextual answer to "create, remove, hide, or rename
    folders", and a catch-all area IS a folder -- the same refusal the four
    consequences above it already carry."""
    with pytest.raises(AnswerNotPermitted, match="residual"):
        _question(answer_class=CONTEXTUAL)


def test_the_consequence_round_trips_through_the_store(qconn):
    """`record_question` stores options with `asdict` for exactly this reason:
    the hand-written field list it replaced dropped `gates_template` silently,
    and the question stored fine, rehydrated fine, and gated nothing."""
    record_question(qconn, _question(), asked_at=T0)
    from questions.store import questions_for

    stored = questions_for(qconn, [f"{RESIDUAL_KIND.kind_id}:{AREA}"])
    assert len(stored) == 1
    assert {option.residual_action for option in stored[0].options} == {
        ENABLE, DISABLE}
    assert "residual_action" in {
        field.name for field in dataclasses.fields(QuestionOption)}
