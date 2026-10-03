"""The sorter's questions, asked in the conversation from the store."""
from __future__ import annotations

from dataclasses import dataclass

from assistant.engine_tools import question_event, wording_problems
from assistant.events import Message, Question
from assistant.session import Session
from questions.records import QuestionOption, StructuralQuestion
from questions.schema import create_questions_schema
from questions.store import record_question
from questions.vocabulary import STRUCTURAL

CLOCK = "2026-10-03T12:00:00+00:00"


@dataclass(frozen=True)
class IndexCounts:  # the Index agent's shape, stubbed until it lands
    indexed: int
    set_aside: int
    set_aside_folders: int
    protected: int
    held: int
    open_questions: int


def a_question(qid, prompt="What kind of material is Columbia?", **kw):
    fields = dict(
        question_id=qid,
        answer_class=STRUCTURAL,
        prompt=prompt,
        evidence_context="Four files mention Columbia.",
        unlocks="This decides which folder layout is offered.",
        will_not_do="It will not move, rename or delete anything.",
        scope="organization:columbia",
        handling_class="personal_non_sensitive",
        options=(QuestionOption("study", "I study there",
                                activates_schema="academic"),
                 QuestionOption("not_mine", "It is not about me")),
        evidence_refs=("sha256:" + "cd" * 32,))
    fields.update(kw)
    return StructuralQuestion(**fields)


def seed(conn, *questions):
    create_questions_schema(conn)
    for q in questions:
        record_question(conn, q, asked_at=CLOCK)
    conn.commit()


def two(conn):
    seed(conn, a_question("reading.organization:columbia"),
         a_question("reading.organization:nyu", prompt="What is NYU to you?",
                    scope="organization:nyu"))


def opened(conn, monkeypatch):
    import assistant.session as session_mod
    monkeypatch.setattr(session_mod, "_counts", lambda c: IndexCounts(
        indexed=5, set_aside=0, set_aside_folders=0, protected=0, held=0,
        open_questions=2))
    out = []
    s = Session(conn, provider_turn=lambda **k: {"role": "assistant",
                                                  "content": "ok"},
                emit=out.append)
    s.open()
    return s, out


def answers(conn):
    return conn.execute(
        "SELECT question_id, option_id, answer_type, raw_wording, state "
        "FROM structural_answers ORDER BY recorded_at, rowid").fetchall()


def test_open_offers_the_queued_questions(conn, monkeypatch):
    two(conn)
    _, out = opened(conn, monkeypatch)
    assert isinstance(out[-1], Message)
    assert "while you were away i have 2 questions" in out[-1].text.lower()


def test_yes_asks_one_at_a_time_and_records_a_choice(conn, monkeypatch):
    two(conn)
    s, out = opened(conn, monkeypatch)
    s.say("yes")
    first = out[-1]
    assert isinstance(first, Question) and (first.index, first.of) == (1, 2)
    assert [o.label for o in first.options] == ["I study there",
                                               "It is not about me"]
    assert first.why == "Four files mention Columbia."
    s.answer(first.question_id, "study")
    row = answers(conn)[0]
    assert (row["option_id"], row["state"]) == ("study", "confirmed")
    second = out[-1]
    assert isinstance(second, Question) and (second.index, second.of) == (2, 2)


def test_typed_text_matching_no_option_is_free_text(conn, monkeypatch):
    two(conn)
    s, out = opened(conn, monkeypatch)
    s.say("yes")
    s.answer(out[-1].question_id, "I used to work there")
    row = answers(conn)[0]
    assert row["answer_type"] == "free_text"
    assert row["option_id"] is None
    assert row["raw_wording"] == "I used to work there"


def test_skip_records_skipped(conn, monkeypatch):
    two(conn)
    s, out = opened(conn, monkeypatch)
    s.say("yes")
    s.answer(out[-1].question_id, "skip")
    assert answers(conn)[0]["state"] == "skipped"


def test_last_answer_says_done(conn, monkeypatch):
    seed(conn, a_question("reading.organization:columbia"))
    s, out = opened(conn, monkeypatch)
    s.say("yes")
    s.answer(out[-1].question_id, "not_mine")
    assert isinstance(out[-1], Message)
    assert "that's all" in out[-1].text.lower()


def test_codes_never_reach_the_person():
    assert wording_problems("Is this academic.coursework or not?")
    assert wording_problems("Files under situation_code here")
    assert wording_problems("Branch 3fa9c1d2e4 has files")
    assert wording_problems("Which describes your relationship to Columbia?") == []
    q = a_question("q1", prompt="Is this academic.coursework or teaching?",
                   options=(QuestionOption("c", "Coursework",
                                           selects_situation="academic.coursework"),
                            QuestionOption("t", "Teaching")))
    event = question_event(q, 1, 1)
    assert "academic.coursework" not in event.text
    assert "Coursework" in event.text
    plain = question_event(a_question("q2", prompt="Is this snake_case_id x?"), 1, 1)
    assert "snake_case_id" not in plain.text
