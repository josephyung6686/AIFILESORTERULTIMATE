# tests/integration/test_the_editable_structure.py
"""The proposed structure, and the person editing it.

`00` "Amendments of 2026-09-14" item 2, the owner's own words: *"then we go
directly into a proposed file structure -- a general template and structure that
they can create and edit, with an AI proposal which is the templates we already
created based on what we see in their files; more customisation by the user on the
template side, so the file system does not have to auto-make everything."* The
first beat, the gist, is `test_the_gist`.

**THE TREE THE DESIGN STAGE PROPOSES IS THE PROPOSAL.** It is printed as an
outline -- each folder with what it is for in the library's own words, how many
files would sit under it, and the situation its branch is built from -- written to
a plain text file beside the database, and read back next run with `--structure`.

**THE FILE IS A FRONT END TO GESTURES THAT ALREADY EXIST**, which is the whole of
what makes it safe: a renamed label becomes `--rename`, a deleted line becomes
`--reject` on every file the folder held, a `situation:` line becomes the
`--answer` that branch's question was waiting for, and an edit none of them can
express -- moving a folder -- is REFUSED BY NAME with nothing else in the file
applied. Nothing here writes to the plan tables on a second path.

**THE DEPLOYMENT AND THE CORPUS** are the ones
`test_the_question_at_the_end_and_the_sort` authors: cloud only, no local model,
the cloud stubbed at `readers.model_routing.deepseek_invoke`, and eleven synthetic
files -- six coursework in the root, three of a student society's records in a
subfolder of their own, two the rules hold. Nothing below reads the owner's disk.

**NOTHING MOVES.** Every run carries `--accept-groups` and neither `--freeze` nor
`--apply`, so the corpus on disk is byte for byte what it was before the first
run -- including after the run that applied the person's edits.

**THE ONE THING MEASURED HERE THAT LOOKS LIKE A DETAIL.** The branch is not always
the folder at the top of the tree: on this corpus the branch is `nonprofit` and
the folder is the person's own `Debate Society`, so `cli._branch_question` tries
the folder's name first and answers the run's only open branch question when that
misses. A rule that guessed between two would put somebody's answer on the wrong
branch, which is the one failure a question exists to prevent.
"""
from __future__ import annotations

import io
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import cli  # noqa: E402
import structure_file  # noqa: E402
from readers import model_routing  # noqa: E402
from readers.model_deepseek import BASE_URL_NAME, CREDENTIAL_NAME  # noqa: E402
from readers.model_ollama import (  # noqa: E402
    BASE_URL_NAME as LOCAL_BASE_URL_NAME,
    MODEL_NAME as LOCAL_MODEL_NAME,
)
from readers.model_routing import MODEL_NAME_OF_TIER  # noqa: E402
from tree_design.store import latest_plan_version, nodes_for_version  # noqa: E402

from test_the_question_at_the_end_and_the_sort import (
    dark_level_stage,  # noqa: E402
    CHOSEN, CLUB, ENV, LABEL, SCHEMA, SITUATION, _Cloud, _corpus, _on_disk,
)
from test_the_gist import block  # noqa: E402

STRUCTURE = "The structure being proposed, and yours to change:"


# --- the harness ----------------------------------------------------------------


def _once(state, *extra: str) -> tuple[int, str]:
    """One run of the corpus against the database, with the cloud stubbed."""
    cloud = _Cloud()
    out = io.StringIO()
    root = state["database"].parent
    with pytest.MonkeyPatch.context() as patch:
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", root / "absent.env")
        for name, value in ENV.items():
            patch.setenv(name, value)
        patch.setattr(model_routing, "deepseek_invoke", cloud.factory)
        dark_level_stage(patch)
        code = cli.main(
            [str(state["corpus"]), "--situation", SITUATION, "--label", LABEL,
             "--user", "t", "--database", str(state["database"]),
             "--enable-cloud", "--accept-groups", *extra], out=out)
    return code, out.getvalue()


@pytest.fixture
def proposed(tmp_path):
    """One run, and the outline it wrote.

    FUNCTION SCOPED, unlike its sibling's module-scoped fixture, and deliberately:
    each test below edits the proposal and runs again, and two tests sharing one
    database would be measuring the second edit against the first one's plan.
    """
    corpus = _corpus(tmp_path)
    state = {"corpus": corpus, "database": tmp_path / "holder" / "plan.sqlite",
             "before": _on_disk(corpus)}
    code, said = _once(state)
    assert code == 0, said
    state["said"] = said
    state["structure"] = state["database"].parent / cli.STRUCTURE_FILENAME
    return state


def _nodes(state):
    conn = sqlite3.connect(f"file:{state['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return nodes_for_version(conn, latest_plan_version(conn))
    finally:
        conn.close()


def _labels(state) -> set[str]:
    return {node.display_label for node in _nodes(state)}


def _edited(state, change) -> str:
    """The outline with one change in it, written where a second run can read it."""
    lines = state["structure"].read_text(encoding="utf-8").splitlines()
    scratch = state["structure"].parent / "edited-structure.txt"
    scratch.write_text("\n".join(change(list(lines))) + "\n", encoding="utf-8")
    return str(scratch)


def _a_folder_named_by_a_value(state) -> tuple[int, str]:
    """A row the gestures CAN reach: one named by a value read out of a file.

    Chosen BY MEASUREMENT over the plan rather than by name, so these pins say
    "the first folder a rename reaches" and not "the folder this corpus happened
    to produce in September".
    """
    for marker, _depth, node in cli._outline_walk(_nodes(state)):
        if node.parent_node_id is not None and cli._node_claim(node) is not None:
            return marker, node.display_label
    raise AssertionError("this plan has no folder named by a value")


# --- the proposal -----------------------------------------------------------------


def test_the_outline_is_written_beside_the_database(proposed):
    """`--structure-out`'s default. Beside the DATABASE and not in the corpus:
    "nothing was moved" has to be true of a file the product MADE as well as of
    one it found."""
    assert proposed["structure"].exists(), proposed["structure"]
    assert proposed["structure"].parent == proposed["database"].parent
    assert _on_disk(proposed["corpus"]) == proposed["before"]


def test_a_named_path_is_where_the_outline_goes(tmp_path):
    """`--structure-out`, so the person keeps their proposal where they want it."""
    corpus = _corpus(tmp_path)
    mine = tmp_path / "somewhere else" / "my-folders.txt"
    state = {"corpus": corpus, "database": tmp_path / "holder" / "plan.sqlite"}
    code, said = _once(state, "--structure-out", str(mine))
    assert code == 0, said
    assert mine.exists(), said
    assert not (state["database"].parent / cli.STRUCTURE_FILENAME).exists()


def test_a_run_that_names_no_database_still_writes_outside_the_corpus(tmp_path):
    """The default path is beside the DATABASE the run resolved (since 3 Oct the
    shared one in ~/.graph-agent), not beside the folder it scanned nor the
    working directory.

    `--database` is optional and every other pin here types it, so the arm an
    ordinary invocation takes had no measurement at all: the outline was landing
    in the folder being scanned -- a file this product made in a place it promised
    to leave alone, and one the next scan would index.
    """
    corpus = _corpus(tmp_path)
    before = _on_disk(corpus)
    elsewhere = tmp_path / "not the corpus"
    elsewhere.mkdir()
    out = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        for name in (CREDENTIAL_NAME, BASE_URL_NAME, *MODEL_NAME_OF_TIER.values(),
                     LOCAL_MODEL_NAME, LOCAL_BASE_URL_NAME):
            patch.delenv(name, raising=False)
        patch.setattr(cli, "ENV_FILE", tmp_path / "absent.env")
        patch.chdir(elsewhere)
        code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                         "--user", "t", "--accept-groups"], out=out)
    said = out.getvalue()
    assert code == 0, said
    from database_agent.db import shared_database_path
    assert (shared_database_path().parent / cli.STRUCTURE_FILENAME).exists(), said
    assert not (elsewhere / cli.STRUCTURE_FILENAME).exists(), said
    assert _on_disk(corpus) == before, "the product wrote into the scanned folder"


def test_the_outline_rows_are_the_plans_own_nodes(proposed):
    """Row for row, in the plan's own order.

    The marker on a line is a POSITION, and a file whose rows did not match the
    plan's nodes would hand somebody's rename to the folder beside the one they
    renamed.
    """
    text = proposed["structure"].read_text(encoding="utf-8")
    written = [line for line in text.split("\n\n", 1)[1].splitlines()
               if not line.lstrip().startswith("#")]
    walked = cli._outline_walk(_nodes(proposed))
    assert len(written) == len(walked), text
    for line, (marker, depth, node) in zip(written, walked):
        assert line.startswith(structure_file.INDENT * depth + node.display_label)
        assert f"[{marker}]" in line, line


def test_every_row_says_how_much_would_sit_under_it(proposed):
    """A person judging a proposed folder is judging how much of their disk it
    takes, and the count is the SUBTREE's: a top folder that files nothing
    directly would otherwise read as empty while holding the lot."""
    text = proposed["structure"].read_text(encoding="utf-8")
    rows = [line for line in text.split("\n\n", 1)[1].splitlines()
            if not line.lstrip().startswith("#")]
    assert rows and all(" file" in row for row in rows), rows


def test_a_branch_says_which_situation_it_is_in_the_librarys_own_words(proposed):
    """`00` amendment 2's "a general template and structure", said in a sentence a
    person can judge: the situation's id on the line and the research's own `name`
    and `one_line` under it."""
    text = proposed["structure"].read_text(encoding="utf-8")
    assert f"{structure_file.SITUATION_PREFIX} {SITUATION}" in text, text
    words = cli.situation_words(SITUATION)
    assert words
    noted = " ".join(line.lstrip(" #") for line in text.splitlines()
                     if line.lstrip().startswith("#"))
    assert " ".join(words.split()) in " ".join(noted.split()), (words, noted)


def test_the_screen_prints_the_same_outline_and_names_the_command(proposed):
    """One proposal, two places, word for word -- and the command that hands it
    back, typed out, which is `84` §6's rule about what a screen tells a person to
    type."""
    said = proposed["said"]
    body = proposed["structure"].read_text(encoding="utf-8").split("\n\n", 1)[1]
    written = body.splitlines()
    assert [line[2:] for line in block(said, STRUCTURE)[:len(written)]] == written
    assert str(proposed["structure"]) in said
    assert "--structure " in said


# --- the person edits it ----------------------------------------------------------


def test_a_renamed_label_reaches_the_next_plan(proposed):
    """Through `apply_renames`, the gesture that already existed: the value the
    folder is named by answers to the person's spelling from here on."""
    marker, label = _a_folder_named_by_a_value(proposed)
    mine = f"{label} of mine"

    def rename(lines):
        return [line.replace(label, mine, 1) if f"[{marker}]" in line else line
                for line in lines]

    code, said = _once(proposed, "--structure", _edited(proposed, rename))
    assert code == 0, said
    assert mine in _labels(proposed), sorted(_labels(proposed))


def test_a_deleted_line_is_a_folder_the_next_plan_does_not_build(proposed):
    """"A node removed is a node not built", through `--reject`.

    The folder exists because the files under it carry a value; deleting its line
    retracts that value on EVERY one of them, and the folder is gone from the plan
    the next run proposes. Retracting it on one would leave the folder standing
    for the rest while the screen said it had been removed.
    """
    marker, label = _a_folder_named_by_a_value(proposed)

    def remove(lines):
        return [line for line in lines if f"[{marker}]" not in line]

    code, said = _once(proposed, "--structure", _edited(proposed, remove))
    assert code == 0, said
    assert label not in _labels(proposed), sorted(_labels(proposed))


def test_a_deleted_line_that_cannot_be_taken_is_refused_in_the_persons_own_terms(
        proposed, monkeypatch):
    """The person deleted a line; they never typed `--reject`. When the rejection
    behind that line is refused -- two files share the basename, say -- the
    sentence names the line they deleted and the remedy, and keeps the reason.

    SABOTAGE: hand the structure file's rejections to `apply_rejections` with
    the typed ones and the screen says "`--reject` ..." about a flag nobody used.
    """
    marker, _label = _a_folder_named_by_a_value(proposed)

    def remove(lines):
        return [line for line in lines if f"[{marker}]" not in line]

    def refuse(conn, rejections, **_):
        raise cli.RejectionRefused(
            f"{rejections[0].partition(':')[0]!r} names 2 files in this plan")

    monkeypatch.setattr(cli, "apply_rejections", refuse)
    code, said = _once(proposed, "--structure", _edited(proposed, remove))
    assert code != 0
    # Named by the file the person handed back, whatever they called it.
    assert "A line you deleted in edited-structure.txt could not be taken" in said, said
    assert "names 2 files in this plan" in said, said
    assert "Put the line back" in said, said


def test_an_answered_branch_is_not_waiting_so_the_one_open_branch_takes_the_line():
    """The fallback counts OPEN branch questions. Two branches were asked; the
    person answered one on an earlier run; a `situation:` line under a folder
    named for neither branch answers the one still open, instead of refusing
    with "2 of them waiting".

    SABOTAGE: count every `situation:` question row and the second line ever
    typed is refused for the rest of the corpus's life.
    """
    import sqlite3 as _sqlite3
    from questions.records import QuestionOption, StructuralQuestion
    from questions.schema import create_questions_schema
    from questions.store import StructuralAnswer, record_answer, record_question

    conn = _sqlite3.connect(":memory:"); conn.row_factory = _sqlite3.Row
    create_questions_schema(conn)
    for kind in ("academic", "nonprofit"):
        record_question(conn, StructuralQuestion(
            question_id=f"situation:{kind}", answer_class="structural",
            prompt=f"Which of these is {kind}?", evidence_context="files under it",
            unlocks="which fields its files are asked", will_not_do="move nothing",
            scope=f"branch:{kind}", handling_class="personal_non_sensitive",
            options=(QuestionOption("a", "one"), QuestionOption("b", "two")),
            evidence_refs=(f"obs:{kind}",)),
            asked_at="2026-09-14T00:00:00+00:00")
    record_answer(conn, StructuralAnswer(
        question_id="situation:academic", option_id="a", state="confirmed",
        scope="branch:academic", user_id="jy",
        recorded_at="2026-09-14T00:01:00+00:00", supersedes=None))
    assert cli._branch_question(conn, "Debate Society") == "situation:nonprofit"


def test_a_situation_line_answers_that_branchs_question(proposed):
    """`00` amendment 1 of 14 Sep read through amendment 2: the branch question
    becomes an EDIT to the proposal rather than a menu of identifiers.

    The society's three files are under `nonprofit`, which the shipped library
    carries two situations for and no recogniser raised either of, so the first
    run asked "Which of these is nonprofit?" and got no answer. Writing
    `situation: <id>` under that branch answers it, through `apply_answers`.
    """
    branch = next((marker for marker, _depth, node
                   in cli._outline_walk(_nodes(proposed))
                   if node.parent_node_id is None
                   and node.display_label == CLUB), None)
    assert branch is not None, f"this plan has no {CLUB!r} branch"

    def answer(lines):
        out = []
        for line in lines:
            out.append(line)
            if f"[{branch}]" in line:
                out.append(f"{structure_file.INDENT}"
                           f"{structure_file.SITUATION_PREFIX} {CHOSEN}")
        return out

    code, said = _once(proposed, "--structure", _edited(proposed, answer))
    assert code == 0, said
    conn = sqlite3.connect(f"file:{proposed['database']}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT option_id FROM structural_answers WHERE question_id = ? "
            "ORDER BY rowid DESC LIMIT 1", (f"situation:{SCHEMA}",)).fetchone()
    finally:
        conn.close()
    assert row is not None and row["option_id"] == CHOSEN, row


def test_an_edit_no_gesture_can_express_is_refused_by_name(proposed):
    """The build rule at the seam: the file is a front end to gestures that exist,
    so an edit none of them makes is refused and NAMED, never invented.

    Moving a folder is the case -- a folder is where the facts about the files
    under it put it -- and the refusal says so, says what to do instead, and
    applies nothing else in the file.
    """
    deep = next((marker for marker, depth, _node
                 in cli._outline_walk(_nodes(proposed)) if depth > 0), None)
    assert deep is not None, "this plan is one level deep"
    before = _labels(proposed)

    def move(lines):
        return [line[len(structure_file.INDENT):]
                if f"[{deep}]" in line and line.startswith(structure_file.INDENT)
                else line for line in lines]

    code, said = _once(proposed, "--structure", _edited(proposed, move))
    assert code == 2, said
    assert "no gesture moves one" in said, said
    assert _labels(proposed) == before, "a refused file changed the plan"


def test_an_outline_from_an_older_proposal_is_refused(proposed):
    """A marker is a POSITION in one proposal's walk.

    Applying an edit mints a new plan that walks differently, so the SAME file
    handed back a second time would carry `[3]` against whichever folder now
    stands third -- a rename of a folder the person never touched, applied in
    silence. The header stamps the proposal it was written from and a file that
    names an older one is refused by name.
    """
    marker, label = _a_folder_named_by_a_value(proposed)
    edited = _edited(proposed, lambda lines: [
        line.replace(label, f"{label} of mine", 1) if f"[{marker}]" in line
        else line for line in lines])
    code, said = _once(proposed, "--structure", edited)
    assert code == 0, said
    after = _labels(proposed)
    # THE SAME FILE AGAIN, against the plan the run above minted.
    code, said = _once(proposed, "--structure", edited)
    assert code == 2, said
    assert "was written from proposal" in said, said
    assert _labels(proposed) == after, "a refused file changed the plan"


def test_an_outline_from_no_run_at_all_is_refused(tmp_path):
    """`--structure` on a database that holds no proposal. The person believes
    they have handed something back, and a silently ignored file is the worst of
    both -- no effect and no way to tell."""
    corpus = _corpus(tmp_path)
    mine = tmp_path / "invented.txt"
    mine.write_text("Whatever  [1]\n", encoding="utf-8")
    state = {"corpus": corpus, "database": tmp_path / "holder" / "plan.sqlite"}
    code, said = _once(state, "--structure", str(mine))
    assert code == 2, said
    assert "holds no proposal" in said, said


def test_editing_the_structure_moves_no_file(proposed):
    """`--freeze` and `--apply` are untouched by any of this. The proposal is a
    proposal, and editing it is still a proposal."""
    marker, label = _a_folder_named_by_a_value(proposed)
    mine = f"{label} of mine"
    code, said = _once(proposed, "--structure", _edited(
        proposed,
        lambda lines: [line.replace(label, mine, 1) if f"[{marker}]" in line
                       else line for line in lines]))
    assert code == 0, said
    assert _on_disk(proposed["corpus"]) == proposed["before"]


# --- `106` Phase 7 §B.3 and §C: what a row says about a fold, and about a bundle --


def _run_with_nodes(nodes):
    """A `ProductionRun` with these nodes and nothing placed, the two fields
    `structure_rows` reads."""
    from types import SimpleNamespace

    return SimpleNamespace(
        tree=SimpleNamespace(tree=SimpleNamespace(nodes=tuple(nodes))),
        placement=SimpleNamespace(decisions=()))


def _a_node(node_id, label, *, parent=None, node_type="proposed",
            dimension=None, expected=(), accepts=True):
    from tree_design.records import ExpectedValue, Node

    return Node(
        node_id=node_id, plan_version_id="p", node_type=node_type,
        display_label=label, parent_node_id=parent,
        root_anchor="root_documents", ordinal=0, associated_group_ids=(),
        explanation="x", node_role="ordinary", accepts_placement=accepts,
        handling_class="personal_non_sensitive", origin_node_id=node_id,
        dimension_role=dimension, dimension=dimension,
        expected_values=tuple(ExpectedValue(f, v) for f, v in expected))


def test_a_row_names_the_values_folded_into_its_folder():
    """`106` Phase 7 §B.3. A folder that claims more than its own level says so
    on its line, so the person editing the outline sees what is inside without
    a level for it. SABOTAGE: print only the count -- the fold is a decision
    the product made and did not say."""
    top = _a_node("n_g", "Georgetown Prep", parent="n_root", dimension="school",
                  expected=(("school", "Georgetown Prep"), ("term", "2024-Fall"),
                            ("subject", "ENG101")))
    assert cli._node_claim(top) == ("school", "Georgetown Prep")
    assert cli._folded_words(top) == (
        "also every file's term 2024-Fall and subject ENG101")
    rows = cli.structure_rows(
        _run_with_nodes((_a_node("n_root", "Academics"), top)),
        situations={}, words_of=lambda s: "", holds={})
    assert "also every file's term 2024-Fall and subject ENG101" in rows[1].words


def test_an_ancestors_value_on_the_chain_is_the_path_and_not_a_fold():
    """Every node's chain carries its ancestors' values too (`materialise.py`),
    and those are the path the person can already see. Only what was folded
    INTO this folder is named on its line. SABOTAGE: name every value past the
    node's own -- every term folder reads "also every file's school Columbia",
    which is the folder above it."""
    school = _a_node("n_c", "Columbia", parent="n_root", dimension="school",
                     expected=(("school", "Columbia"),))
    term = _a_node("n_t", "2026-Spring", parent="n_c", dimension="term",
                   expected=(("school", "Columbia"), ("term", "2026-Spring")))
    assert cli._node_claim(term) == ("term", "2026-Spring")
    assert cli._folded_words(term, frozenset({"school"})) == ""
    rows = cli.structure_rows(
        _run_with_nodes((_a_node("n_root", "Academics"), school, term)),
        situations={}, words_of=lambda s: "", holds={})
    assert "also" not in rows[2].words


def test_a_protected_root_says_it_is_protected_and_not_a_folder_of_the_plan():
    """`106` Phase 7 §C producer 3. `represent_protected_areas` puts a bundle at
    the root by the standing rule; the outline printed "0 files" beside it.
    SABOTAGE: keep the count -- an app reads as an empty folder of the plan."""
    area = _a_node("n_app", "Numbers.app", node_type="protected", accepts=False)
    rows = cli.structure_rows(_run_with_nodes((area,)), situations={},
                              words_of=lambda s: "", holds={})
    assert rows[0].words == cli.PROTECTED_ROW_WORDS
    assert "0 files" not in rows[0].words
