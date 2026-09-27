"""What a first run may offer under the outline.

The six launch lives are a choice. Finance, identity, medical, and legal are
holds. Every other domain stays on disk unless these files already named it.
The word on the question is the life. The answer key is the kind. The label
beside the key is the situation's own last word.
"""
from __future__ import annotations

from facts.domains import SCHEMA_IDS
from questions.triggers import HOLD_SCHEMA_IDS, LAUNCH_SCHEMA_IDS
from production import (
    load_shipped_catalogue, read_packaged_library_file, schema_for_situation,
    shipped_situations,
)
from questions.triggers import (
    question_for_situation, situations_a_first_run_may_offer, words_of_a_situation,
)


def test_the_situation_word_is_its_own_last_word():
    assert words_of_a_situation("academic.coursework") == "Coursework"
    assert words_of_a_situation("academic.k12-schooling") == "K12 schooling"


def test_the_outline_prints_each_choice_as_a_line_that_can_be_typed():
    from cli import _what_these_folders_are

    question = question_for_situation(
        branch_label="Education", scope_label="academic",
        situations=("academic.coursework", "academic.online-course"),
        file_count=2)
    text = _what_these_folders_are((question,))

    assert "Coursework" in text
    assert "Online course" in text
    assert "--answer situation:academic=Coursework" in text
    assert "situation:academic=Online course" in text
    assert "academic.coursework" not in text
    assert "=ID" not in text


def test_the_word_on_the_screen_is_the_situation_the_answer_stores():
    import sqlite3

    from questions.schema import create_questions_schema
    from questions.store import record_question, the_option_they_named

    question = question_for_situation(
        branch_label="Education", scope_label="academic",
        situations=("academic.coursework", "academic.online-course"),
        file_count=2)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_questions_schema(conn)
    record_question(conn, question, asked_at="2026-09-24T00:00:00+00:00")

    assert the_option_they_named(
        conn, question.question_id, "Coursework") == "academic.coursework"
    assert the_option_they_named(
        conn, question.question_id, "academic.coursework") == "academic.coursework"


def test_the_life_is_the_word_and_the_kind_is_the_key():
    question = question_for_situation(
        branch_label="Education", scope_label="academic",
        situations=("academic.coursework", "academic.teaching"), file_count=2)

    assert question.prompt == "Which of these is Education?"
    assert question.question_id == "situation:academic"
    assert question.scope == "branch:academic"
    assert "2 files sit under Education" in question.evidence_context
    coursework = next(option for option in question.options
                      if option.option_id == "academic.coursework")
    assert coursework.label == "Coursework"
    assert coursework.selects_situation == "academic.coursework"


def test_a_first_run_offers_the_six_and_holds_back_the_rest():
    catalogue = load_shipped_catalogue(read_packaged_library_file)
    by_schema: dict[str, list[str]] = {}
    for item in shipped_situations(catalogue):
        by_schema.setdefault(item.schema, []).append(item.name)

    def schema_of(situation: str) -> str:
        return schema_for_situation(catalogue, situation)

    academic = by_schema["academic"][:2]
    finance = by_schema["finance"][:1]
    manufacturing = by_schema["manufacturing"][:1]
    nonprofit = by_schema["nonprofit"][:1]
    named_apart = [name for name in by_schema["college_applications"]
                   if not name.startswith("college_applications")]
    assert academic and finance and manufacturing and nonprofit and named_apart

    offered = situations_a_first_run_may_offer(
        (*academic, *finance, *manufacturing, *nonprofit, named_apart[0]),
        named_by_the_files=("academic", "nonprofit"),
        schema_of=schema_of)
    domains = {schema_of(situation) for situation in offered}

    assert "academic" in domains
    assert "nonprofit" in domains
    assert "college_applications" in domains
    assert "finance" not in domains
    assert "manufacturing" not in domains
    assert named_apart[0] in offered

    held = situations_a_first_run_may_offer(
        finance, named_by_the_files=("finance",), schema_of=schema_of)
    assert held == ()


def test_a_term_and_a_subject_name_coursework_and_a_kind_of_work_does_not():
    import cli
    from production import folder_levels_for, life_of

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    academic = tuple(
        item.name for item in shipped_situations(catalogue)
        if item.schema == "academic")

    def levels(situation: str) -> tuple[str, ...]:
        return tuple(level.field
                     for level in folder_levels_for(catalogue, situation))

    named = cli.one_situation_whose_levels_cover(
        academic, life="Education",
        life_of_situation=lambda situation: life_of(catalogue, situation),
        levels_of_situation=levels,
        fields_carried={"term", "subject", "work_type"})
    assert named == "academic.coursework"

    assert cli.one_situation_whose_levels_cover(
        academic, life="Education",
        life_of_situation=lambda situation: life_of(catalogue, situation),
        levels_of_situation=levels,
        fields_carried={"work_type"}) is None


def test_a_file_from_another_life_does_not_take_this_life_s_folders_away():
    import cli
    from production import life_of

    catalogue = load_shipped_catalogue(read_packaged_library_file)
    kept = cli.signals_this_life_can_use(
        ("recognition:academic.coursework", "recognition:academic.teaching"),
        life="Education",
        life_of_situation=lambda situation: life_of(catalogue, situation))
    assert kept == frozenset({"recognition:academic.coursework"})


def test_a_course_path_is_a_shape_and_a_kind_of_work_is_not():
    import cli

    class Opt:
        def __init__(self, counts):
            self.resulting_child_counts = counts

    assert cli._course_path(Opt({
        "school": 0, "term": 1, "subject": 3, "work_type": 5}))
    assert not cli._course_path(Opt({"work_type": 5}))
    assert not cli._course_path(Opt({"school": 0, "work_type": 5}))


def test_a_course_keeps_a_file_another_life_only_shares_a_kind_of_work_with():
    import cli
    from types import SimpleNamespace

    def node(node_id, parent, expected):
        return SimpleNamespace(
            node_id=node_id, parent_node_id=parent, expected_values=tuple(
                SimpleNamespace(field=field, value=value) for field, value in expected))

    education = node("edu", None, ())
    hello = node("hello", "edu", (("subject", "Hello 1006"), ("work_type", "lecture")))
    career = node("career", None, ())
    lecture = node("lecture", "career", (("work_type", "lecture"),))
    nodes = (education, hello, career, lecture)
    by_id = {item.node_id: item for item in nodes}
    depth = {"edu": 0, "hello": 1, "career": 0, "lecture": 1}
    named = {"subject": {"Hello 1006"}, "work_type": {"lecture"}}
    assert cli._deepest_folder_under(
        nodes, named, root_id="edu", depth=depth, by_id=by_id) == "hello"
    assert cli._deepest_folder_under(
        nodes, {"work_type": {"lecture"}}, root_id="career",
        depth=depth, by_id=by_id) == "lecture"


def test_a_left_out_course_does_not_take_the_file_from_the_folder_it_sits_in():
    import cli
    from types import SimpleNamespace

    def node(node_id, parent, expected, node_type="proposed"):
        return SimpleNamespace(
            node_id=node_id, parent_node_id=parent, node_type=node_type,
            expected_values=tuple(
                SimpleNamespace(field=field, value=value)
                for field, value in expected))

    course = node("python", "desk", (), node_type="existing")
    lecture = node("lecture", "python",
                   (("subject", "ENGI E1006"), ("work_type", "lecture")))
    left_out = node("code", "edu",
                    (("subject", "ENGI E1006"), ("work_type", "lecture")),
                    node_type="ignored")
    nodes = (node("desk", None, (), node_type="existing"), course, lecture,
             node("edu", None, ()), left_out)
    by_id = {item.node_id: item for item in nodes}
    depth = {"desk": 0, "python": 1, "lecture": 2, "edu": 0, "code": 1}
    named = {"subject": {"ENGI E1006"}, "work_type": {"lecture"}}
    assert cli._deepest_folder_under(
        nodes, named, root_id="python", depth=depth, by_id=by_id) == "lecture"
    assert cli._deepest_folder_under(
        nodes, named, root_id="edu", depth=depth, by_id=by_id) is None


def test_a_file_is_counted_on_the_folder_it_sits_in():
    import cli
    from types import SimpleNamespace

    parent = SimpleNamespace(node_id="desk", existing_path="/disk/Desktop")
    child = SimpleNamespace(
        node_id="course", existing_path="/disk/Desktop/Python 1006")
    proposed = SimpleNamespace(node_id="edu", existing_path=None)
    holds = cli._files_sitting_in_their_own_folders(
        (("loose", "/disk/Desktop/notes.txt"),
         ("lecture", "/disk/Desktop/Python 1006/week1.pdf"),
         ("elsewhere", "/disk/Downloads/a.pdf")),
        (parent, child, proposed))
    assert holds["course"] == ["lecture"]
    assert holds["desk"] == ["loose"]
    assert "edu" not in holds


def test_the_six_and_the_four_are_the_front_of_the_closed_list():
    assert LAUNCH_SCHEMA_IDS == SCHEMA_IDS[:6]
    assert HOLD_SCHEMA_IDS == SCHEMA_IDS[6:10]
    assert set(LAUNCH_SCHEMA_IDS).isdisjoint(HOLD_SCHEMA_IDS)
