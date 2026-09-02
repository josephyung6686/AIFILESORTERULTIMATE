# tests/p15/test_p15_typable.py
"""§13's fifth thing has to be a command, not a description of one.

`84` §6's second standing ruling: **what the screen tells a person to type has to
be true.** It has been applied three times already -- to the unpasteable
`--answer` line the report printed, to the `revoke` that needed an invisible id,
and to an ambiguous send -- and `cli._typable` is the shape the fix took: one
`QUESTION=OPTION` argument per line, through `shlex.quote`, so the line that would
break is the only one altered.

`questions.explanation._how_to_change` builds the same instruction and does
neither. Measured 2026-09-02 by running the real command with `--explain` wired
against a real branch question:

    How to change it: --answer branch:Coursework=<school>term>subject>work_type |
    keep-as-it-is> to change it, --answer branch:Coursework=skip to put it aside,
    ...

Two separate defects on one line.

**It is a placeholder, not a command.** `<a | b>` is the notation a manual page
uses; a person reading it has to work out that the angle brackets and the bar are
not theirs to type. The report itself does not do this -- it prints one whole
line per option -- so the same product says the same thing two ways.

**It is not survivable.** `school>term>subject>work_type` is a real option id in
the shipped library, and `>` is the shell's redirect. Pasting that line does not
fail: it silently creates files called `term`, `subject` and `work_type` in
whatever directory the person is standing in, and reports nothing. A branch
scoped to `--label "Legal Matters"` breaks the other way -- the space splits the
argument in two -- which is exactly the case `cli._typable` was written for.

This file holds the surface to the same standard as the report, because it is the
same instruction.
"""
from __future__ import annotations

import shlex
import sqlite3

import pytest

from questions.explanation import explain_answer, render_explanation
from questions.records import QuestionOption, StructuralAnswer, StructuralQuestion
from questions.schema import create_questions_schema
from questions.store import record_answer, record_question
from questions.vocabulary import CONFIRMED, STRUCTURAL

CLOCK = "2026-09-02T09:30:00+00:00"

#: The shipped library's own nesting option ids, and a scope carrying the space a
#: person's `--label` puts there. Neither is invented for this test: the first is
#: what `--list-situations` prints for `academic.coursework`, and the second is
#: what `--label "Legal Matters"` produces.
HOSTILE = StructuralQuestion(
    question_id="branch:Legal Matters", answer_class=STRUCTURAL,
    prompt="How should Legal Matters be organised?",
    evidence_context="Four files sit under Legal Matters.",
    unlocks="This decides the folders inside this branch.",
    will_not_do="It will not move, rename or delete anything.",
    scope="branch:Legal Matters",
    handling_class="personal_non_sensitive",
    options=(QuestionOption("school>term>subject>work_type",
                            "school / term / subject / work type"),
             QuestionOption("keep-as-it-is", "Keep this branch as it is")),
    evidence_refs=("declared:branch:Legal Matters",))

#: The redirect ALONE, with nothing else wrong with the line. `HOSTILE` carries
#: both hazards at once and the space is the louder of the two -- an unquoted
#: `branch:Legal Matters=...` splits at the space and every assertion below fails
#: on THAT, which is how a guard comes to be named for a hazard it never tested.
#: Every question id that is not branch-scoped has no space in it, so this is the
#: ordinary case and the one the redirect would actually reach.
REDIRECTING = StructuralQuestion(
    question_id="branch:Coursework", answer_class=STRUCTURAL,
    prompt="How should Coursework be organised?",
    evidence_context="Four files sit under Coursework.",
    unlocks="This decides the folders inside this branch.",
    will_not_do="It will not move, rename or delete anything.",
    scope="branch:Coursework",
    handling_class="personal_non_sensitive",
    options=(QuestionOption("school>term>subject>work_type",
                            "school / term / subject / work type"),),
    evidence_refs=("declared:branch:Coursework",))


def _shell_tokens(line: str) -> list[str]:
    """What a SHELL makes of the line, which is not what `shlex.split` makes of it.

    **This function is the finding.** `shlex.split` has no opinion about `>`:
    `shlex.split("--answer q=a>b")` returns `['--answer', 'q=a>b']`, one happy
    token, so every assertion in this file passed on a line a real shell would
    treat as a redirect. The guard was named for a hazard it could not detect,
    and caught the unquoted case at all only because `HOSTILE`'s scope also
    contains a space -- the louder of the two, masking the other.

    `punctuation_chars=True` is what models the shell's own reading: it makes `>`
    a token in its own right. `whitespace_split=True` keeps the rest of the line
    splitting the way a command line does rather than on `shlex`'s default word
    characters.

    Raised by the role-matcher agent, who hit the identical hole in
    `role_report`'s three renders and proved it by sabotage. Measured here the
    same way: with the quoting removed, reverting this function to `shlex.split`
    turns the redirect test GREEN on the live defect.
    """
    lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


@pytest.fixture()
def qconn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_questions_schema(connection)
    yield connection
    connection.close()


def _explained(conn, question=HOSTILE, option_id="keep-as-it-is"):
    record_question(conn, question, asked_at=CLOCK)
    record_answer(conn, StructuralAnswer(
        question_id=question.question_id, option_id=option_id, state=CONFIRMED,
        scope=question.scope, user_id="jy", recorded_at=CLOCK))
    seen = explain_answer(conn, question_id=question.question_id,
                          scope=question.scope)
    assert seen is not None
    return seen


def _commands(how_to_change: str) -> list[str]:
    """Every line of the instruction that is offered as something to type."""
    return [line.strip() for line in how_to_change.splitlines()
            if line.strip().startswith("--answer")]


def test_every_command_the_explanation_offers_survives_a_shell(qconn):
    """The flag and its argument reach `--answer` undamaged.

    `shlex.split` is the shell's own reading of the line, and the first two
    tokens are what the person is being told to type -- the report's own form
    (`--answer <typable>   <label>`), so this holds the explanation to exactly the
    standard the report already meets. An option truncated at the `>`, or split
    at the space in `Legal Matters`, is one the shell acts on differently from
    how the screen described it -- and in the `>` case it acts SILENTLY, writing
    files nobody asked for into whatever directory the person is standing in.
    """
    seen = _explained(qconn)
    offered = {option.option_id for option in HOSTILE.options} | {"skip", "revoke"}
    for command in _commands(seen.how_to_change):
        parts = _shell_tokens(command)
        assert parts[:1] == ["--answer"], (
            f"{command!r} does not begin with the flag it claims to use")
        assert len(parts) >= 2, f"{command!r} names the flag and nothing else"
        question_id, separator, option_id = parts[1].partition("=")
        assert separator and question_id == HOSTILE.question_id, (
            f"a shell reads {command!r} as {parts}; {parts[1]!r} does not name "
            f"this question")
        assert option_id in offered, (
            f"{option_id!r} is not one of this question's answers; the shell "
            f"took the line apart somewhere the screen did not say it would")


def test_a_redirect_alone_is_caught_when_nothing_else_is_wrong(qconn):
    """The `>` on a question id with no space in it -- the ordinary case.

    Separate from the test above and on a separate fixture, because the two
    hazards mask each other. `HOSTILE` splits at its space whether or not the
    redirect is handled, so it cannot tell a line that survives a shell from one
    that merely survives `shlex.split`. Every question id that is not
    branch-scoped has no space, so this is the case the redirect actually reaches.

    What a person loses if this is wrong is not an error message. Pasting
    `--answer branch:Coursework=school>term>subject>work_type` creates empty files
    called `term`, `subject` and `work_type` in whatever directory they are
    standing in, and prints nothing at all.
    """
    seen = _explained(qconn, question=REDIRECTING,
                      option_id="school>term>subject>work_type")
    for command in _commands(seen.how_to_change):
        tokens = _shell_tokens(command)
        assert ">" not in tokens, (
            f"a shell reads {command!r} as {tokens} -- the `>` is a redirect it "
            f"will act on, silently, and the option is truncated before it "
            f"reaches `--answer`")


def test_the_explanation_offers_the_options_the_way_the_report_does(qconn):
    """One line per answer, and no placeholder notation anywhere in it.

    The report prints one whole `--answer` line per option. An explanation that
    collapsed them into `<a | b>` would be the same product describing the same
    gesture two ways, and the manual-page form is the one a person has to decode
    before they can use it.
    """
    seen = _explained(qconn)
    commands = _commands(seen.how_to_change)
    assert len(commands) == len(HOSTILE.options) + 2, (
        f"{len(commands)} lines offered for {len(HOSTILE.options)} options plus "
        f"skip and revoke: {commands}")
    assert "|" not in seen.how_to_change and "<" not in seen.how_to_change, (
        f"the instruction still uses placeholder notation: {seen.how_to_change!r}")


def test_the_rendered_lines_are_still_one_command_each(qconn):
    """The same, through the renderer a person actually reads.

    `render_explanation` puts the instruction on a labelled line, and a
    multi-line instruction that arrived flattened would undo the whole of this
    file without changing `how_to_change` at all.
    """
    rendered = render_explanation(_explained(qconn))
    typable = [line.strip() for line in rendered.splitlines()
               if line.strip().startswith("--answer")]
    assert len(typable) == len(HOSTILE.options) + 2, (
        f"the renderer offers {len(typable)} typable lines:\n{rendered}")
    for line in typable:
        parts = _shell_tokens(line)
        assert parts[1].startswith(f"{HOSTILE.question_id}="), (
            f"a shell reads {line!r} as {parts}, whose argument is not this "
            f"question's")


def test_a_line_that_needs_no_quoting_is_left_exactly_as_it_was(qconn):
    """The falsifying twin: quoting must not become decoration.

    `cli._typable`'s own reason -- "`shlex.quote` leaves an argument that needs no
    quoting exactly as it was, so the ordinary line is unchanged and only the one
    that would break is altered." A fix that wrapped every line in quotes would
    pass every assertion above while making the ordinary report harder to read,
    and would hide a later regression that stopped quoting the hostile case.
    """
    plain = StructuralQuestion(
        question_id="reading.organization:columbia", answer_class=STRUCTURAL,
        prompt="What kind of material is Columbia?",
        evidence_context="Four files mention Columbia.",
        unlocks="This decides which folder layout is offered.",
        will_not_do="It will not move, rename or delete anything.",
        scope="organization:columbia", handling_class="personal_non_sensitive",
        options=(QuestionOption("study", "I study there"),),
        evidence_refs=("sha256:" + "ef" * 32,))
    seen = _explained(qconn, question=plain, option_id="study")
    assert "--answer reading.organization:columbia=study" in seen.how_to_change, (
        "an argument needing no quoting was quoted anyway")
    assert "'" not in seen.how_to_change and '"' not in seen.how_to_change, (
        f"nothing on this question needs quoting: {seen.how_to_change!r}")
