# tests/p15/test_p15_roles.py
"""§16's buildable half: being more than one thing, without a matcher.

`66` §16 and the owner ruling at `62` §D disagree about exactly one step -- how a
person's WORDING becomes a candidate schema -- and agree about everything on either
side of it. `62` §D: "These should not just be directly matched -- the LLM uses that
information to judge. This cannot be rule based." `69` §4.3 keeps it open, and a
decision brief is being written for an outside adviser before the owner rules.

So the proposal step is not here, in any form. What IS here is what both documents
agree on, and what the product cannot express without it:

> The system must support multiple roles, each with a scope and possibly a time
> period, rather than forcing one permanent profession. (§16:543)
> Being more than one thing is normal. (§16:542)

**The bound, restated, because this is where it would break.** A declaration is a
structural answer. A confirmed one selects an option the product offered from its
own closed schema list -- the person picking, not the product matching. An unmatched
one is `FREE_TEXT`, names no option, and so reaches `activated_schemas` and
`gated_template` never. Nothing here narrows the list, ranks it, or reads the
wording. Narrowing is the gated half.
"""
from __future__ import annotations

import ast
import pathlib
import sqlite3

import pytest

from facts.domains import SCHEMA_IDS
from questions.records import AnswerNotPermitted
from questions.store import AnswerConflict
from questions.registry import ROLE_KIND, QUESTION_KINDS, kind_of
from questions.roles import (
    EXACT_ACTIVATION, MULTIPLE_ROLE_ACTIVATION, NOT_LISTED, RoleDeclaration,
    SKIPPED_ROLE, UNMATCHED, declare_role, live_roles, outcome_of_roles,
    question_for_role_declaration, skip_role,
)
from questions.schema import create_questions_schema
from questions.store import activated_schemas, gated_template, selected_situation
from questions.vocabulary import (
    CHOICE, FREE_TEXT, OutOfVocabulary, ROLE_OUTCOMES, check,
)

T0 = "2026-08-31T10:00:00+00:00"
T1 = "2026-08-31T11:00:00+00:00"

#: `68` F6's person, in her own two lives. Priya is a graduate student who also
#: teaches, and today the product makes her pick one for her whole disk.
STUDYING = "I'm a graduate student in physics"
TEACHING = "I teach one undergraduate lab section"


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def _declare(conn, declaration_id, *, scope="corpus", wording=None, schema=None,
             at=T0, **kw):
    return declare_role(
        conn, declaration_id=declaration_id, scope=scope, schemas=SCHEMA_IDS,
        raw_wording=wording, chosen_schema=schema, user_id="jy",
        recorded_at=at, **kw)


# --- D1: several roles, each with a scope and possibly a period --------------------


def test_a_person_may_hold_a_student_role_and_a_teaching_role_at_once(qconn):
    """§16:543 verbatim. Two live declarations, neither cancelling the other."""
    _declare(qconn, "studying", schema="academic")
    _declare(qconn, "teaching", schema="research", at=T1)

    live = live_roles(qconn)
    assert {role.declaration_id for role in live} == {"studying", "teaching"}
    assert {role.activates_schema for role in live} == {"academic", "research"}


def test_a_second_role_does_not_supersede_the_first(qconn):
    """The twin that matters, and the reason a declaration gets its own question.

    Supersession is P15's CORRECTION mechanism -- `store.live_answer` defines the
    live answer as the one nothing supersedes -- and reaching for it to hold a
    second simultaneous role would encode "one permanent profession" in the
    storage layer. That is the exact thing §16:543 exists to prevent, and it would
    be invisible: the person would declare a second role, see the first vanish,
    and have no way to tell a bug from a rule.
    """
    _declare(qconn, "studying", schema="academic")
    first = live_roles(qconn)
    assert len(first) == 1

    _declare(qconn, "teaching", schema="research", at=T1)
    assert len(live_roles(qconn)) == 2
    assert first[0].declaration_id in {role.declaration_id
                                       for role in live_roles(qconn)}
    # And the store agrees: neither answer supersedes anything.
    assert qconn.execute(
        "SELECT COUNT(*) FROM structural_answers WHERE supersedes IS NOT NULL"
    ).fetchone()[0] == 0


def test_a_role_carries_a_scope_and_may_carry_a_period(qconn):
    """§16:543: "each with a scope and possibly a time period". A person stops
    teaching; the declaration that says they taught stays true of its period."""
    _declare(qconn, "teaching", scope="branch:Teaching", schema="research",
             applies_from="2024-09-01", applies_until="2026-06-30")

    role = live_roles(qconn, scope="branch:Teaching")[0]
    assert role.scope == "branch:Teaching"
    assert role.applies_from == "2024-09-01"
    assert role.applies_until == "2026-06-30"
    assert live_roles(qconn, scope="corpus") == ()


def test_two_roles_may_share_one_scope(qconn):
    """"Being more than one thing is normal" is not "being more than one thing in
    different folders". A sound engineer who teaches an evening class is both
    things about the same disk."""
    _declare(qconn, "engineering", schema="engineering")
    _declare(qconn, "teaching", schema="research", at=T1)

    assert len(live_roles(qconn, scope="corpus")) == 2


def test_correcting_a_role_still_supersedes_it(qconn):
    """The positive twin. Making a second role additive must not make a
    CORRECTION additive too, or a person could never take back a mistake."""
    _declare(qconn, "studying", schema="academic")
    _declare(qconn, "studying", schema="legal", at=T1)

    live = live_roles(qconn)
    assert len(live) == 1
    assert live[0].activates_schema == "legal"


# --- D2: the four outcomes, closed --------------------------------------------------


def test_the_outcomes_are_16s_four_and_no_fifth():
    assert set(ROLE_OUTCOMES) == {
        EXACT_ACTIVATION, MULTIPLE_ROLE_ACTIVATION, UNMATCHED, SKIPPED_ROLE}


def test_a_declaration_may_not_be_stored_in_a_fifth_outcome():
    """The negative twin. §16:553 says "one of four outcomes"; a fifth is the
    nearest-neighbour snap §16:547 forbids, arriving as a status value rather
    than as a mapping -- and just as invisible to the person it is wrong about.

    Checked on the RECORD, not by calling `check` in the test. A twin that
    exercised the vocabulary helper would pass just as well against a
    `RoleDeclaration` that never consulted it.
    """
    with pytest.raises(OutOfVocabulary, match="probably_academic"):
        RoleDeclaration(
            declaration_id="sound", scope="corpus",
            raw_wording="I'm a sound engineer", chosen_option=None,
            applies_from=None, applies_until=None,
            outcome="probably_academic")

    # ...and the four real ones are all constructible.
    for outcome in ROLE_OUTCOMES:
        RoleDeclaration(
            declaration_id="sound", scope="corpus", raw_wording="x",
            chosen_option=None, applies_from=None, applies_until=None,
            outcome=outcome)


def test_an_unmatched_declaration_is_stored_and_activates_no_schema(qconn):
    """§16:547: "An unmatched answer must remain unmatched." The person's words are
    kept; nothing is turned on."""
    _declare(qconn, "sound", wording="I'm a sound engineer")

    role = live_roles(qconn)[0]
    assert role.outcome == UNMATCHED
    assert role.raw_wording == "I'm a sound engineer"
    assert role.activates_schema is None
    assert activated_schemas(qconn) == frozenset()


def test_a_skipped_declaration_leaves_the_decision_unresolved(qconn):
    """§16:553's fourth outcome, and §14's first-class "skip for now"."""
    skip_role(qconn, declaration_id="sound", scope="corpus", schemas=SCHEMA_IDS,
              user_id="jy", recorded_at=T0)

    role = live_roles(qconn)[0]
    assert role.outcome == SKIPPED_ROLE
    assert role.activates_schema is None
    assert activated_schemas(qconn) == frozenset()


def test_not_listed_is_an_answer_and_activates_nothing(qconn):
    """§16:551 requires "an explicit 'Other,' 'Not listed,' and 'Skip for now'
    path". `NOT_LISTED` is a real option carrying no consequence -- the person has
    told the product something, and it must not resolve to the nearest schema."""
    _declare(qconn, "sound", schema=None, not_listed=True)

    role = live_roles(qconn)[0]
    assert role.outcome == UNMATCHED
    assert role.activates_schema is None
    assert activated_schemas(qconn) == frozenset()


def test_more_than_one_confirmed_role_is_the_multiple_role_outcome(qconn):
    """§16:553's second outcome is a property of the SET, not of one declaration,
    which is why it is computed over the live roles rather than stored on a row."""
    _declare(qconn, "studying", schema="academic")
    assert outcome_of_roles(live_roles(qconn)) == EXACT_ACTIVATION

    _declare(qconn, "teaching", schema="research", at=T1)
    assert outcome_of_roles(live_roles(qconn)) == MULTIPLE_ROLE_ACTIVATION

    assert outcome_of_roles(()) == SKIPPED_ROLE


# --- D3: one activation surface, and one only ---------------------------------------


def test_a_confirmed_role_activates_its_schema_through_activated_schemas(qconn):
    """`store.activated_schemas` promises "a reader can see every schema the user
    turned on and where it came from". A second activation path would falsify that
    docstring, so a role goes through this one or through none."""
    _declare(qconn, "studying", schema="academic")

    assert activated_schemas(qconn) == frozenset({"academic"})
    assert activated_schemas(qconn, scope="corpus") == frozenset({"academic"})


def test_a_role_is_registered_as_a_kind_whose_reader_is_that_surface():
    assert ROLE_KIND in QUESTION_KINDS
    assert ROLE_KIND.consequence_field == "activates_schema"
    assert ROLE_KIND.reader is activated_schemas
    assert kind_of("role:studying") is ROLE_KIND


def test_a_role_declaration_never_becomes_a_folder_name_or_a_filing_permission(qconn):
    """§16:557 verbatim: "It should never convert a role answer directly into a
    folder name or automatic-filing permission."

    Two halves. The wording reaches no other consequence -- `gated_template` and
    `selected_situation` are the only two that build or shape folders, and a role
    answer reaches neither. And `roles.py` itself names no placement, eligibility
    or filing symbol, checked over the parsed AST so a docstring cannot pass for
    an implementation or fail for a mention.
    """
    _declare(qconn, "sound", wording="Sound Engineering Ltd")
    _declare(qconn, "studying", schema="academic", at=T1)

    for scope in ("corpus", "branch:Sound Engineering Ltd",
                  "organization:Sound Engineering Ltd"):
        assert gated_template(qconn, scope=scope) is None
        assert selected_situation(qconn, scope=scope) is None

    source = (pathlib.Path("src/questions/roles.py")).read_text()
    forbidden = {"destination_eligible", "is_destination_eligible",
                 "display_label", "accepts_placement", "auto_eligible",
                 "write_node", "materialise"}
    named = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name):
            named.add(node.id)
        elif isinstance(node, ast.Attribute):
            named.add(node.attr)
        elif isinstance(node, ast.keyword) and node.arg:
            named.add(node.arg)
    assert named & forbidden == set(), f"roles.py names {sorted(named & forbidden)}"


def test_the_role_guard_fires_on_a_role_that_became_a_folder_name():
    """The sabotage fixture. A guard that cannot fire is not a guard."""
    sabotage = "def build(role):\n    return write_node(display_label=role.raw_wording)\n"
    named = set()
    for node in ast.walk(ast.parse(sabotage)):
        if isinstance(node, ast.Name):
            named.add(node.id)
        elif isinstance(node, ast.keyword) and node.arg:
            named.add(node.arg)
    assert named & {"display_label", "write_node"} == {"display_label", "write_node"}


# --- the gate: nothing here reads the wording ---------------------------------------


def test_the_question_offers_the_closed_list_and_narrows_it_by_nothing(qconn):
    """The whole shape of the ungated half, in one assertion.

    Every schema the product recognises is offered, plus `NOT_LISTED`. Nothing
    ranks, filters or shortens that list, because narrowing it from the person's
    wording IS the proposal step, and the proposal step is what `62` §D holds
    shut. When the owner's guidance arrives it changes this list; it changes
    nothing else in this file.
    """
    question = question_for_role_declaration(
        declaration_id="studying", scope="corpus", schemas=SCHEMA_IDS)

    activating = {option.activates_schema for option in question.options
                  if option.activates_schema}
    assert activating == set(SCHEMA_IDS)
    assert NOT_LISTED in {option.option_id for option in question.options}


def test_a_declaration_naming_a_schema_the_product_does_not_have_is_refused(qconn):
    """Refused by `store.record_answer`, not by this module -- "a caller must not
    widen the option set by answering". That is the right layer: the option set IS
    the closed schema list, and a declaration that reached past it would be the
    invention §16:547 forbids, arriving through the back door."""
    with pytest.raises((AnswerNotPermitted, AnswerConflict),
                       match="sound_engineering"):
        _declare(qconn, "studying", schema="sound_engineering")


def test_wording_and_a_schema_may_not_be_given_together(qconn):
    """A3's rule, reaching here: the two answer types are alternatives. A
    declaration carrying both would let a later reader take the WORDING as the
    thing that chose the schema, which is the mapping nothing may do yet."""
    with pytest.raises(AnswerNotPermitted):
        _declare(qconn, "studying", schema="academic",
                 wording="I'm a graduate student")


def test_a_declaration_with_neither_wording_nor_a_choice_is_refused(qconn):
    with pytest.raises(AnswerNotPermitted):
        _declare(qconn, "studying")


def test_an_unmatched_declaration_is_stored_as_free_text_and_a_choice_as_choice(qconn):
    _declare(qconn, "sound", wording="I'm a sound engineer")
    _declare(qconn, "studying", schema="academic", at=T1)

    types = {row["answer_type"] for row in
             qconn.execute("SELECT answer_type FROM structural_answers")}
    assert types == {FREE_TEXT, CHOICE}


def test_no_run_over_files_can_raise_a_role_declaration():
    """§12 permits a question only when a decision is blocked, and no evidence
    blocks on what somebody's profession is. A role declaration is raised by the
    PERSON: `declaration_id` is minted by the caller, and nothing in `triggers.py`
    -- which is what a run consults -- mints one or calls this builder."""
    triggers = pathlib.Path("src/questions/triggers.py").read_text()
    called = {node.func.id for node in ast.walk(ast.parse(triggers))
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert "question_for_role_declaration" not in called
    assert "declare_role" not in called
