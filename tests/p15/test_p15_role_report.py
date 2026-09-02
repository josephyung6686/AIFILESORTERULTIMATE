# tests/p15/test_p15_role_report.py
"""What a person actually SEES of `80`: the moment, and the panel R6 asks for.

Everything `80` rules was built and none of it reached a screen. `role-1` through
`role-5` landed the proposal step, the declarations, the two gestures and the
trigger, and then `src/cli.py` imported none of them -- so R2's once-only friction
budget was enforced inside a function no run called, and a person could not see the
roles they held or find the words to change one.

Two requirements are the whole of this file.

**R2 -- the friction budget is spent ONCE.** `role_declaration_is_due` says when the
moment is due. This module cannot render the ask WITHOUT asking it: the ask takes
the trigger's own two inputs and calls it, so a caller cannot print the question by
forgetting to check. That is the difference between R2 being a rule and R2 being a
property.

**R6 -- the roles are editable, not a gate.** "a light, editable settings panel the
person can glance at and adjust anytime, not a one-time gate they went through and
now can't see again." The panel is the glancing half. The adjusting half already
exists as two gestures, and the panel's job is to say them truly -- `84` §6: "What
the screen tells a person to type has to be true", which is checked here by taking
the line the panel printed and running it.
"""
from __future__ import annotations

import inspect
import sqlite3

import pytest

from facts.domains import SCHEMA_IDS
from questions.proposal import RoleProposal
from questions.registry import ROLE_KIND
from questions.roles import apply_declarations, apply_descriptions, live_roles
from questions.schema import create_questions_schema
from questions.triggers import question_for_tied_reading
from questions.vocabulary import SCOPE_CORPUS

T0 = "2026-08-31T10:00:00+00:00"
T1 = "2026-08-31T11:00:00+00:00"


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def _blocked(subject="PHYS1401"):
    """The ambiguity in the shape the run actually produces it: one subject whose own
    words support two readings equally."""
    return (question_for_tied_reading(
        subject_value=subject, tied_schema_ids=("academic", "research"),
        file_count=1, evidence_refs=(f"subject:{subject}",)),)


def _declare(conn, *declarations, at=T0):
    return apply_declarations(conn, declarations, schemas=SCHEMA_IDS, user_id="jy",
                              recorded_at=at)


def _describe(conn, *descriptions, at=T0):
    return apply_descriptions(conn, descriptions, schemas=SCHEMA_IDS, user_id="jy",
                              recorded_at=at)


# --- the moment: R1 and R2 -----------------------------------------------------------


def test_a_run_with_nothing_blocked_says_nothing_about_who_the_person_is():
    """`80` §3 (R1): never up front. A first run that settled everything asks
    nothing about the person, because nothing needed it."""
    from questions.role_report import role_moment_lines

    assert role_moment_lines(blocked=(), already_declared=()) == ()


def test_the_first_genuinely_ambiguous_file_puts_the_question_on_screen():
    from questions.role_report import role_moment_lines

    lines = role_moment_lines(blocked=_blocked(), already_declared=())

    assert lines
    assert any("--describe-role" in line for line in lines)


def test_an_established_role_is_never_asked_about_again_however_many_are_blocked(qconn):
    """R2, composed. This is the test the trigger already had at the unit level and
    the report did not: a caller cannot render the ask without consulting the
    person's existing declarations, because the ask takes them."""
    from questions.role_report import role_moment_lines

    _declare(qconn, "teaching=research")
    blocked = _blocked("PHYS1401") + _blocked("CHEM2210") + _blocked("HIST1000")

    assert role_moment_lines(blocked=blocked,
                             already_declared=live_roles(qconn)) == ()


def test_a_person_who_only_typed_a_sentence_has_already_spent_the_budget(qconn):
    """R2 again, for the answer that turns nothing on. Describing a role in your own
    words is answering the question; being asked it again the next run because the
    words matched no layout would be the interruption R2 forbids."""
    from questions.role_report import role_moment_lines

    _describe(qconn, 'me=I teach one course and I am doing my own PhD')

    assert role_moment_lines(blocked=_blocked(),
                             already_declared=live_roles(qconn)) == ()


def test_the_moment_promises_nothing_about_where_the_words_go():
    """`80` §8 suspends the always-local ENFORCEMENT for one item, so a screen that
    told a person their sentence stays on this device would be making a promise this
    build may not keep. `proposal.sending_notice` is where the truth about a send is
    told, in the same breath as `00`:200, and it is told on the run that sends.

    The ask runs BEFORE any sentence exists, so it cannot know. It therefore says
    nothing about it rather than guessing in the reassuring direction."""
    from questions.role_report import role_moment_lines

    said = " ".join(role_moment_lines(blocked=_blocked(), already_declared=())).lower()

    for promise in ("device", "local", "private", "never leaves", "stays here"):
        assert promise not in said, (
            f"the ask claims {promise!r}; `80` §8 can make that untrue for exactly "
            "this sentence, and a screen that has to be true may not say it")


def test_the_moment_says_what_the_question_will_not_do():
    """§14's obligation and `62` §D's fear in one line: a sentence about yourself
    does not become a folder and does not authorise a move."""
    from questions.role_report import role_moment_lines

    said = " ".join(role_moment_lines(blocked=_blocked(), already_declared=()))

    assert "folder" in said.lower()


# --- the panel: R6 -------------------------------------------------------------------


def test_a_person_holding_no_roles_has_no_panel(qconn):
    from questions.role_report import role_panel_lines

    assert role_panel_lines(live_roles(qconn)) == ()


def test_the_panel_shows_every_role_at_once_and_never_one_of_them(qconn):
    """§16:543 on screen. A person who is several things sees several things; a
    panel that showed "your role" would be the one permanent profession the whole
    requirement exists to refuse."""
    from questions.role_report import role_panel_lines

    _declare(qconn, "studying=academic", "teaching=research")
    said = " ".join(role_panel_lines(live_roles(qconn)))

    assert "studying" in said and "teaching" in said
    assert "academic" in said and "research" in said


def test_the_panel_reads_a_persons_own_words_back_to_them(qconn):
    """`80` §4 (R5): "The raw sentence stays recorded and visible rather than
    discarded." Visible is this."""
    from questions.role_report import role_panel_lines

    _describe(qconn, 'me=I run PHYS 1401 and my thesis is due in March')
    said = " ".join(role_panel_lines(live_roles(qconn)))

    assert "I run PHYS 1401 and my thesis is due in March" in said


def test_the_panel_says_that_an_unmatched_role_turned_nothing_on(qconn):
    """§16:547: an unmatched answer remains unmatched. A panel that listed a kept
    sentence beside a confirmed choice without saying which had done something would
    let a person believe their words had had an effect they did not have."""
    from questions.role_report import role_panel_lines

    _describe(qconn, 'me=something this product has no layout for')
    said = " ".join(role_panel_lines(live_roles(qconn))).lower()

    assert "nothing" in said


def test_the_panel_carries_the_period_a_role_is_true_of(qconn):
    """§16:543: "each with a scope and possibly a time period". A role that ends in
    June is the case R6 was written about -- "finishes teaching a course" -- and a
    panel that hid the period would make the person guess whether it had taken."""
    from questions.role_report import role_panel_lines
    from questions.roles import declare_role

    declare_role(qconn, declaration_id="teaching", scope=SCOPE_CORPUS,
                 schemas=SCHEMA_IDS, chosen_schema="research", user_id="jy",
                 recorded_at=T0, applies_from="2026-01-01", applies_until="2026-06-30")
    said = " ".join(role_panel_lines(live_roles(qconn)))

    assert "2026-01-01" in said and "2026-06-30" in said


def test_a_skipped_role_is_still_on_the_panel(qconn):
    """§14 makes "skip for now" a first-class answer, and R2 means it is not asked
    again -- so if the panel omitted it the person would have put a question aside
    and lost every trace of it."""
    from questions.role_report import role_panel_lines

    _declare(qconn, "teaching=skip")
    said = " ".join(role_panel_lines(live_roles(qconn)))

    assert "teaching" in said


def test_what_the_panel_tells_a_person_to_type_actually_withdraws_the_role(qconn):
    """`84` §6, applied: the line is not read for plausibility, it is RUN.

    R6's "adjust anytime" is only true if the withdrawal gesture on the panel is the
    one this product implements. It is `--answer`, whose form is `<question>=revoke`
    and whose question id for a role is `role:<the name you chose>` -- three facts a
    panel can get wrong in three different ways, none of them visible by reading."""
    import cli
    from questions.role_report import role_panel_lines

    _declare(qconn, "teaching=research", "studying=academic")
    lines = role_panel_lines(live_roles(qconn))
    printed = [word for line in lines for word in line.split()
               if word.startswith(f"{ROLE_KIND.kind_id}:teaching=")]
    assert printed, f"the panel never says how to withdraw a role: {lines}"

    cli.apply_answers(qconn, printed, user_id="jy", recorded_at=T1)

    held = {role.declaration_id for role in live_roles(qconn)}
    assert held == {"studying"}, (
        "the command the panel printed did not withdraw the role it named")


def test_the_panel_names_the_gesture_that_changes_a_role_without_withdrawing_it(qconn):
    """R6's other half. Re-using the name is the correction, and a person who could
    only withdraw would have to take a role back to change it."""
    from questions.role_report import role_panel_lines

    _declare(qconn, "teaching=research")
    said = " ".join(role_panel_lines(live_roles(qconn)))

    assert "--declare-role" in said


# --- the shortlist: R7 ---------------------------------------------------------------


def test_the_shortlist_is_rendered_in_the_order_the_caller_supplies(qconn):
    """`80` §5 (R7). The order arrives from the surface, so a surface that
    randomises per render or lays out no first item can."""
    from questions.role_report import shortlist_lines

    proposal = RoleProposal(self_description="I teach and I study",
                            candidates=frozenset({"academic", "research"}),
                            from_model=True)
    said = " ".join(shortlist_lines(proposal, name="me",
                                 order=lambda c: ("research", "academic")))
    other = " ".join(shortlist_lines(proposal, name="me",
                                  order=lambda c: ("academic", "research")))

    assert said.index("research") < said.index("academic")
    assert other.index("academic") < other.index("research")


def test_a_shortlist_render_supplies_no_order_of_its_own():
    """The refusal `proposal.shortlist_for_question` already makes, kept at the
    render site: a module that fell back to sorted() would reintroduce a ranking by
    an irrelevance, which R7 says is not a mitigation."""
    from questions.proposal import ProposalRefused
    from questions.role_report import shortlist_lines

    proposal = RoleProposal(self_description="I teach", candidates=frozenset({"a"}),
                            from_model=True)
    with pytest.raises(ProposalRefused):
        shortlist_lines(proposal, name="me", order=None)


def test_a_shortlist_that_matched_nothing_is_rendered_in_the_same_shape(qconn):
    """`80` §4 (R5): "none of these" is a normal outcome, not an error -- same visual
    weight, same tone, no apology shape.

    The specific no-match WORDING is the owner's (`80` §6), so this module authors
    none. What it must do structurally is not change shape: the sentence is still
    read back, and the way to declare a role is still offered."""
    from questions.role_report import shortlist_lines

    matched = RoleProposal(self_description="I teach",
                           candidates=frozenset({"academic"}), from_model=True)
    none = RoleProposal(self_description="I teach", candidates=frozenset(),
                        from_model=True)

    matched_lines = shortlist_lines(matched, name="me", order=lambda c: tuple(sorted(c)))
    none_lines = shortlist_lines(none, name="me", order=lambda c: ())

    assert "I teach" in " ".join(none_lines)
    assert "--declare-role" in " ".join(none_lines)
    for apology in ("sorry", "unfortunately", "failed", "could not", "error"):
        assert apology not in " ".join(none_lines).lower()
    assert len(none_lines) < len(matched_lines), (
        "the no-match render should differ from the matched one only by the "
        "candidates it has to show")


def test_the_shortlist_never_says_which_candidate_is_likeliest(qconn):
    """`78` §3.5's risk and R7's: a shortlist item read as the product's
    endorsement. The data carries no confidence and the render may not invent one."""
    from questions.role_report import shortlist_lines

    proposal = RoleProposal(self_description="I teach",
                            candidates=frozenset({"academic", "research"}),
                            from_model=True)
    said = " ".join(shortlist_lines(proposal, name="me",
                                 order=lambda c: tuple(sorted(c)))).lower()

    for ranking in ("best", "most likely", "recommend", "top", "first choice"):
        assert ranking not in said


# --- what this module may not become -------------------------------------------------


def test_nothing_in_this_module_writes(qconn):
    """A render that recorded something would be a second place a role is
    established, and `roles.declare_role` promises to be the only one."""
    from questions import role_report

    assert "sqlite3" not in inspect.getsource(role_report)
    for name in ("role_moment_lines", "role_panel_lines", "shortlist_lines"):
        assert "conn" not in inspect.signature(
            getattr(role_report, name)).parameters


def test_the_ask_cannot_be_rendered_without_consulting_r2():
    """The structural half of R2. `role_moment_lines` has no signature under which a
    caller can print the ask while forgetting the person already answered it: both
    of the trigger's inputs are required and neither has a default."""
    from questions import role_report

    parameters = inspect.signature(role_report.role_moment_lines).parameters
    assert set(parameters) == {"blocked", "already_declared"}
    for parameter in parameters.values():
        assert parameter.default is inspect.Parameter.empty
