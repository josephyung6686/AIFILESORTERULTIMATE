# tests/p15/test_p15_composition.py
"""§16 and §13:453 asked of the COMMAND: can a person reach any of this?

`tests/p15/test_p15_roles.py`, `test_p15_role_gestures.py`, `test_p15_proposal.py`
and `test_p15_inspect.py` prove the role surface thoroughly -- 40-odd tests over
declaration, correction, "not listed", skip, free text, the proposal step's three
refusals, and §13's five things. Every one of them calls the module directly.

**Nothing a person can type reaches any of it.** `src/cli.py` imports
`questions.store`, `questions.triggers`'s two nesting helpers and
`questions.vocabulary`, and imports `questions.roles`, `questions.proposal` and
`questions.explanation` not at all. `argparse` in `cli.main` defines nine flags
and none of them is a role or an explanation.

**The gap is visible from inside the part, which is what makes it a defect rather
than an absence.** `roles._split` refuses a malformed gesture with

    "The form is `--declare-role <name>=<what>`"

and `apply_descriptions`'s sibling error names `--describe-role`. Those are flags
`argparse` rejects. `84` §6: what the screen tells a person to type has to be
true, and here the product's own refusal message names two commands that do not
exist.

`80` §3 (R1) is the other half. `triggers.role_declaration_is_due` decides the
MOMENT the self-description may be introduced -- "precisely when it hits its first
genuinely ambiguous file" -- and returns a bool, minting nothing, so that a run
may say *this is the moment* while only the person's own gesture says *and here is
who I am*. Nothing calls it, so the moment never arrives and the two gestures it
would invite do not exist either. Both halves of R1 are dark for one reason.

Measured 2026-09-02 against `cli.main` with PATCH B applied to a copy: the run
prints the invitation, `--describe-role` echoes the sentence and offers all 23
layouts alphabetically (Option 1, `propose=None`, which `80` §1 makes the fallback
"whenever no local model is present"), `--declare-role` records the role and
`outcome_of_roles` reports `exact_activation`, a second run does NOT invite again
(R2, the friction budget is spent once), and `--declare-role teaching=barrister`
is refused with the whole closed list and exit code 2.

The wiring is `src/cli.py`'s and is held for its owner as PATCH B.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from database_agent.db import open_database
from questions.roles import apply_declarations, live_roles
from questions.store import open_questions
from questions.triggers import role_declaration_is_due

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import cli  # noqa: E402

#: A corpus the deterministic chain cannot settle, which is what makes the moment
#: due: `role_declaration_is_due` requires at least one open non-role question.
#:
#: TWO FILES, and the second one is what makes this measure anything. The single
#: syllabus this held first left exactly one question open -- `branch:Coursework`,
#: the `00`:78 nesting OFFER -- and an offer is not an ambiguity: this file's own
#: command prints it under a separate heading because "a nesting offer stops
#: nothing -- the branch has a shape either way". `80` §3 (R1) puts the moment at
#: "the first genuinely AMBIGUOUS file", so `role_declaration_is_due` stopped
#: counting branch-scoped offers and the guard below caught this corpus at once.
#:
#: These two put one subject, CHEM2210, in two readings the detector cannot choose
#: between, which is what `tied_readings` turns into `reading.organization:CHEM2210`
#: -- a decision genuinely blocked on the person, and the evidence R1 wants them to
#: have seen before being asked who they are.
CORPUS: dict[str, str] = {
    "CHEM 2210 chapter.txt":
        "CHEM 2210\n\nDissertation chapter. Literature review. Advisor.\n",
    "CHEM 2210 quiz 2.txt": "CHEM 2210\n\nQuiz 2. Due Friday. Grade.\n",
}


def _corpus(tmp_path: Path) -> tuple[Path, Path]:
    corpus = tmp_path / "corpus"
    for name, text in CORPUS.items():
        path = corpus / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return corpus, tmp_path / "plan.sqlite"


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    """The command a person types, through `cli.main`'s own argument parser."""
    out = io.StringIO()
    code = cli.main(
        [str(corpus), "--situation", "academic.coursework", "--label", "Coursework",
         "--user", "jy", "--database", str(database), *extra], out=out)
    return code, out.getvalue()


def test_a_person_can_say_what_this_material_is_for_them(tmp_path: Path):
    """§16:543's whole point, reached the only way a person has: by typing it.

    Asserted on the STORE and not on the screen, because the screen could print
    an acknowledgement without recording anything. `live_roles` is the reader
    §16 publishes, and a role it does not return is a role the rest of the
    product cannot act on.
    """
    corpus, database = _corpus(tmp_path)
    code, _ = _run(corpus, database, "--declare-role", "teaching=academic")
    assert code == 0
    roles = live_roles(open_database(database))
    assert [role.declaration_id for role in roles] == ["teaching"]
    assert roles[0].activates_schema == "academic"


test_a_person_can_say_what_this_material_is_for_them = pytest.mark.xfail(
    strict=True, raises=SystemExit,
    reason="measured 2026-09-02: `cli.main` defines no `--declare-role`, so "
           "argparse exits 2 before the run starts. `questions.roles` is imported "
           "by nothing in `src/`, and `roles._split` refuses with \"The form is "
           "`--declare-role <name>=<what>`\" -- a command that does not exist. "
           "XPASSes -- and fails the suite, forcing this marker off -- with "
           "PATCH B in the reachability agent's CLI-PATCH.txt.",
)(test_a_person_can_say_what_this_material_is_for_them)


def test_a_person_can_say_it_in_their_own_words_and_the_words_survive(
        tmp_path: Path):
    """`80` §4 (R5): "the raw sentence stays recorded and visible".

    Recorded it has been since A3. Both halves are checked here because they fail
    separately: a gesture that stored the sentence and printed nothing would
    satisfy §16:555 and leave R5's "visible" unmet, which is the state the
    product was in when `80` was written.
    """
    corpus, database = _corpus(tmp_path)
    sentence = "I mark undergraduate lab reports"
    code, printed = _run(corpus, database, "--describe-role", f"teaching={sentence}")
    assert code == 0
    assert sentence in printed, "the person's own words were not shown back"
    roles = live_roles(open_database(database))
    assert [role.raw_wording for role in roles] == [sentence]
    assert roles[0].activates_schema is None, (
        "§16:547 -- an unmatched answer must remain unmatched; a sentence may "
        "turn nothing on")


test_a_person_can_say_it_in_their_own_words_and_the_words_survive = (
    pytest.mark.xfail(
        strict=True, raises=SystemExit,
        reason="`cli.main` defines no `--describe-role`. XPASSes with PATCH B.",
    )(test_a_person_can_say_it_in_their_own_words_and_the_words_survive))


def test_the_run_invites_the_declaration_at_the_moment_r1_names(tmp_path: Path):
    """`80` §3 (R1): the moment, said out loud, and only when it is due.

    A person who is never told the gesture exists does not have it, however well
    the parser would accept it -- so this is a separate failure from the two
    above and stays a separate test.

    The invitation must name the flags, because R1's own reason for putting the
    moment after a real run rather than in onboarding is that the person now has
    evidence the product needs the answer. Evidence with no way to act on it is
    the same dead end one step later.
    """
    corpus, database = _corpus(tmp_path)
    code, printed = _run(corpus, database)
    assert code == 0
    assert "--declare-role" in printed and "--describe-role" in printed


test_the_run_invites_the_declaration_at_the_moment_r1_names = pytest.mark.xfail(
    strict=True,
    reason="`triggers.role_declaration_is_due` has no caller in `src/`, so the "
           "moment `80` §3 defines never arrives. XPASSes with PATCH B.",
)(test_the_run_invites_the_declaration_at_the_moment_r1_names)


def test_the_invitation_is_spent_once_and_does_not_come_back(tmp_path: Path):
    """`80` §4 (R2), which is the ruling that constrains this most.

    "The friction budget is spent ONCE... a user will start clicking through
    without reading, which defeats the entire safety rationale." A run that
    re-invited on every invocation would satisfy the test above and break the
    ruling it exists to serve, so the two are asserted apart.
    """
    corpus, database = _corpus(tmp_path)
    _run(corpus, database, "--declare-role", "teaching=academic")
    code, printed = _run(corpus, database)
    assert code == 0
    assert "--declare-role" not in printed, (
        "the invitation came back after the person had already answered it")


test_the_invitation_is_spent_once_and_does_not_come_back = pytest.mark.xfail(
    strict=True, raises=SystemExit,
    reason="the first run cannot record a declaration, so this cannot yet "
           "measure the second. XPASSes with PATCH B.",
)(test_the_invitation_is_spent_once_and_does_not_come_back)


def test_a_person_can_ask_what_one_of_their_answers_controls(tmp_path: Path):
    """§13:453's five things, reached from the command line.

    Asserted on the labels §13 names rather than on exact sentences, so the test
    measures that all five reached the screen without freezing anybody's wording.
    """
    corpus, database = _corpus(tmp_path)
    _run(corpus, database)
    question = open_questions(open_database(database))[0]
    code, printed = _run(corpus, database, "--explain", question.question_id)
    assert code == 0
    for label in ("What it controls", "Where it applies", "When it was supplied",
                  "How it was settled", "How to change it"):
        assert label in printed, f"§13's {label!r} is not on the screen"


test_a_person_can_ask_what_one_of_their_answers_controls = pytest.mark.xfail(
    strict=True, raises=SystemExit,
    reason="`cli.main` defines no `--explain` and imports "
           "`questions.explanation` not at all, so §13:453's inspection has no "
           "surface. XPASSes with PATCH B.",
)(test_a_person_can_ask_what_one_of_their_answers_controls)


def test_this_file_is_really_driving_the_command_and_the_moment_is_really_due(
        tmp_path: Path):
    """The falsifying twin, and it has to catch three ways this file stops measuring.

    The five xfails above would all report the composition root while measuring
    nothing if the run stopped blocking a question, if `role_declaration_is_due`
    stopped being able to say yes, or if `apply_declarations` stopped writing --
    and the first of those is a property of a one-file corpus, which is the kind
    of thing that changes under this project's feet.

    So this pins the state each xfail depends on, working against the same
    database the command produced, and anchors none of it to the gap: it holds
    whether or not the gestures exist, which is what keeps this file from
    punishing its own finding being fixed.
    """
    corpus, database = _corpus(tmp_path)
    code, printed = _run(corpus, database)
    assert code == 0 and "Folders in this plan" in printed, (
        "this is not the run's report, so a passing assertion above would be "
        "about a string nobody printed")

    conn = open_database(database)
    blocked = open_questions(conn)
    assert blocked, (
        "the corpus settled everything, so R1's moment is not due and the "
        "invitation test would be true of nothing")
    assert not live_roles(conn), "nothing declared a role; the run must not"
    assert role_declaration_is_due(blocked=blocked, already_declared=()), (
        "`role_declaration_is_due` cannot say yes about this run's own state, so "
        "the invitation xfail is measuring the predicate rather than the wiring")

    apply_declarations(conn, ("teaching=academic",),
                       schemas=("academic",), user_id="jy",
                       recorded_at="2026-09-02T10:00:00+00:00")
    assert [role.declaration_id for role in live_roles(conn)] == ["teaching"], (
        "the writer the xfails are waiting on does not write")
    assert not role_declaration_is_due(blocked=blocked,
                                       already_declared=live_roles(conn)), (
        "R2's 'spent once' is not enforced by the predicate, so the fourth xfail "
        "would be measuring the composition root for something no part promises")
