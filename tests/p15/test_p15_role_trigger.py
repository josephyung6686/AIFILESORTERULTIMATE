# tests/p15/test_p15_role_trigger.py
"""WHEN the self-description question may be introduced, and when it may not.

`80` §3 (R1) is a design change and this file is where it lands. The brief assumed
onboarding; the ruling rejects onboarding outright -- "a brand-new user doesn't yet
trust the product enough to answer an identity question about themselves" -- and puts
the moment at the first genuinely ambiguous file instead, through the mechanism that
already raises every other question in this product.

`80` §7's third newly forbidden thing is here too, because it is the same function:

  3. No per-file re-confirmation of an established role (R2).

R2 is the sharpest constraint in the ruling -- "a confirmation a person has learned to
click through is not a safety mechanism" -- and it is a constraint on this moment
rather than on the question, so it is tested on this moment.
"""
from __future__ import annotations

import ast
import pathlib
import sqlite3

import pytest

from facts.domains import SCHEMA_IDS
from questions.roles import (
    declare_role, live_roles, question_for_role_declaration, skip_role,
)
from questions.schema import create_questions_schema
from questions.store import record_question
from questions.triggers import (
    NestingChoice, question_for_nesting, question_for_tied_reading,
    role_declaration_is_due,
)

T0 = "2026-08-31T10:00:00+00:00"

#: `68` F6's ambiguity, in the shape the run actually produces it: one subject whose
#: own words support two readings equally, which is what `recognition.detector`
#: abstains on and what `tied_readings` turns into a question.
AMBIGUOUS = question_for_tied_reading(
    subject_value="PHYS1401", tied_schema_ids=("academic", "research"),
    file_count=1, evidence_refs=("subject:PHYS1401",))

SECOND_AMBIGUITY = question_for_tied_reading(
    subject_value="CHEM2210", tied_schema_ids=("academic", "research"),
    file_count=1, evidence_refs=("subject:CHEM2210",))


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def _declare(conn, declaration_id, *, schema="academic", scope="corpus", at=T0):
    return declare_role(conn, declaration_id=declaration_id, scope=scope,
                        schemas=SCHEMA_IDS, chosen_schema=schema, user_id="jy",
                        recorded_at=at)


# --- R1: the first genuinely ambiguous file, and not before ------------------------


def test_a_run_with_nothing_blocked_never_asks_who_the_person_is():
    """R1's negative half, and the one the ruling cares most about.

    "The tool interrogated me before I'd even seen it work" is the failure. A first
    run that filed everything it found correctly has learned nothing about whether
    this feature is needed, so it asks nothing -- which is also §12's rule, unchanged:
    a question is asked only when a specific decision is blocked.
    """
    assert role_declaration_is_due(blocked=(), already_declared=()) is False


def test_the_first_genuinely_ambiguous_file_makes_the_moment_due():
    """R1's positive half.

    > ask the self-description question only once there's evidence the product needs
    > it -- i.e. precisely when it hits its first genuinely ambiguous file.

    The evidence is the question the run already raised. Nothing new detects
    ambiguity here; the moment reuses the one mechanism that does.
    """
    assert role_declaration_is_due(blocked=(AMBIGUOUS,), already_declared=()) is True


def test_the_moment_is_read_from_a_finished_runs_own_questions():
    """The trigger takes what `tied_readings` produced, not a file and not a corpus.
    A question raised from a finished run is the only evidence it has, which is what
    keeps "never up front" true by construction rather than by ordering."""
    blocked = (AMBIGUOUS, SECOND_AMBIGUITY)
    assert role_declaration_is_due(blocked=blocked, already_declared=()) is True


def test_a_blocked_role_question_does_not_make_itself_due():
    """The moment must not trigger on its own consequence. A role question that is
    open is one the person has already been shown and not yet answered; treating it
    as the ambiguity would re-raise the flow that raised it."""
    role_question = question_for_role_declaration(
        declaration_id="studying", scope="corpus", schemas=SCHEMA_IDS)

    assert role_declaration_is_due(blocked=(role_question,),
                                   already_declared=()) is False
    # ...and a real ambiguity beside it still counts.
    assert role_declaration_is_due(blocked=(role_question, AMBIGUOUS),
                                   already_declared=()) is True


# --- R2: the friction budget is spent ONCE ----------------------------------------


def test_an_established_role_is_never_re_confirmed_however_many_files_are_blocked(qconn):
    """`80` §7's third forbidden thing, and `80` §4's sharpest sentence.

    > If the design implies confirming every time the context gets used later ...
    > that becomes death by a thousand tiny interruptions, and a user will start
    > clicking through without reading, which defeats the entire safety rationale.

    So the check is on the PERSON's state and not on the files. One declaration
    settles the moment for every ambiguity there will ever be -- this run's two, and
    a later run's twenty -- because a confirmed role operates silently afterwards.
    """
    _declare(qconn, "studying")

    many = tuple(question_for_tied_reading(
        subject_value=f"COURSE{subject}", tied_schema_ids=("academic", "research"),
        file_count=1, evidence_refs=(f"subject:COURSE{subject}",))
        for subject in "abcdefghijklmnopqrst")

    assert role_declaration_is_due(blocked=(AMBIGUOUS,),
                                   already_declared=live_roles(qconn)) is False
    assert role_declaration_is_due(blocked=many,
                                   already_declared=live_roles(qconn)) is False


def test_a_second_role_does_not_open_the_moment_again_either(qconn):
    """R6's half of the same requirement. A person whose situation changes "makes a
    small localised edit. They do not re-run an onboarding flow" -- so declaring a
    second role goes through `declare_role`, and this moment stays shut."""
    _declare(qconn, "studying")
    _declare(qconn, "teaching", schema="research", at="2026-08-31T11:00:00+00:00")

    assert live_roles(qconn) != ()
    assert role_declaration_is_due(blocked=(AMBIGUOUS,),
                                   already_declared=live_roles(qconn)) is False


def test_a_person_who_skipped_is_not_asked_again(qconn):
    """§14 makes "skip for now" a first-class answer and §12 forbids re-asking. A
    declined identity question that came back at the next ambiguous file would be
    the interrogation R1 exists to prevent, arriving one file later."""
    skip_role(qconn, declaration_id="studying", scope="corpus", schemas=SCHEMA_IDS,
              user_id="jy", recorded_at=T0)

    assert live_roles(qconn) != ()
    assert role_declaration_is_due(blocked=(AMBIGUOUS,),
                                   already_declared=live_roles(qconn)) is False


def test_the_moment_reads_a_presence_and_never_a_count(qconn):
    """One role and six roles are the same fact here: the person has been asked.
    A count would be a threshold, and a threshold is a number this package has no
    authority to choose."""
    _declare(qconn, "studying")
    one = role_declaration_is_due(blocked=(AMBIGUOUS,),
                                  already_declared=live_roles(qconn))
    for index, name in enumerate(("teaching", "books", "photos", "flat", "band")):
        _declare(qconn, name, schema="research",
                 at=f"2026-08-31T1{index}:30:00+00:00")
    many = role_declaration_is_due(blocked=(AMBIGUOUS,),
                                   already_declared=live_roles(qconn))

    assert one is many is False


# --- the boundary that survives R1 -------------------------------------------------


def test_nothing_a_run_consults_mints_a_role_declaration():
    """R1 moved WHEN the question may be introduced; it did not move WHO introduces
    it.

    This is the guard that stood before `80` and it still stands, on the same
    reading: `triggers.py` is what a run consults, and it neither builds a role
    question nor records a declaration. What it may now do is say the moment has
    arrived -- a bool, with no `declaration_id` in it, because only the person knows
    whether they are one thing or two.
    """
    triggers = pathlib.Path("src/questions/triggers.py").read_text()
    called = {node.func.id for node in ast.walk(ast.parse(triggers))
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}

    assert "question_for_role_declaration" not in called
    assert "declare_role" not in called
    assert "skip_role" not in called
    assert "record_answer" not in called


def test_the_moment_arriving_records_nothing(qconn):
    """The behavioural twin of the guard above. Asking whether the moment is due is
    a question about state and changes none of it -- no question raised, no answer
    written, no schema on."""
    before = qconn.execute("SELECT COUNT(*) FROM structural_questions").fetchone()[0]

    assert role_declaration_is_due(blocked=(AMBIGUOUS,), already_declared=()) is True

    after = qconn.execute("SELECT COUNT(*) FROM structural_questions").fetchone()[0]
    assert before == after == 0
    assert qconn.execute(
        "SELECT COUNT(*) FROM structural_answers").fetchone()[0] == 0


def test_the_run_still_records_the_ambiguity_it_found(qconn):
    """The positive twin: the moment being due must not replace the question the run
    actually raised. Priya's tied PDF still needs its own narrow question -- `80`
    §1.4: "knowing both roles doesn't tell the system which one a specific ambiguous
    PDF belongs to; the in-context question does"."""
    record_question(qconn, AMBIGUOUS, asked_at=T0)

    assert qconn.execute(
        "SELECT COUNT(*) FROM structural_questions").fetchone()[0] == 1


# --- R1 again: an offer is not an ambiguity -----------------------------------------


#: `00`:78's nesting question, which cli.py's report deliberately prints under a
#: SEPARATE heading -- "You can change how this is organised (it is already decided;
#: this is yours to overrule)" -- with the reason recorded beside it: "A blocked
#: reading STOPS something ... A nesting offer stops nothing -- the branch has a
#: shape either way."
AN_OFFER = question_for_nesting(
    branch_label="Coursework",
    choices=(NestingChoice(chain=("school", "term", "subject", "work_type"),
                           summary="This option would create 1 term, and 1 subject.",
                           child_counts=(("term", 1), ("subject", 1)),
                           warnings=()),
             NestingChoice(chain=("term", "subject"),
                           summary="This option would create 2 terms.",
                           child_counts=(("term", 2),), warnings=())),
    file_count=2)


def test_an_offer_to_reshape_a_branch_is_not_a_genuinely_ambiguous_file():
    """Found by running the product. A first run on two coursework files raised no
    blocked reading at all -- both files came back "needed a model" -- and left one
    nesting offer open. The moment fired on it and told the person that "those are
    the decisions above that are waiting for you", when nothing was waiting.

    Two rulings at once. `80` §3 (R1) puts the moment at "the first genuinely
    ambiguous file", and a branch with a shape either way is not one; `84` §6 says
    what the screen tells a person has to be true, and it was not."""
    assert role_declaration_is_due(blocked=(AN_OFFER,), already_declared=()) is False


def test_a_blocked_reading_alongside_an_offer_still_makes_the_moment_due():
    """The other direction, so this is a distinction and not a way of never
    asking."""
    assert role_declaration_is_due(blocked=(AN_OFFER, AMBIGUOUS),
                                   already_declared=()) is True
