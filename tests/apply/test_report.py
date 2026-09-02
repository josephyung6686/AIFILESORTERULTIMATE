"""The lines a person actually reads.

Two properties, and they are the two that have gone wrong in this repo before:
what the screen tells a person to type has to be true, and nothing may be
summarised away.
"""
from __future__ import annotations

import dataclasses
import re

from mutation import vocabulary as v

from placement.vocabulary import OUTCOMES, PLACE

from apply_run.branches import branches_named
from apply_run.freeze import (
    FrozenProposal, HOLD_REASONS, Held, NOT_A_MOVE, NOT_SHOWN,
    REFUSED_AT_CONSTRUCTION,
)
from apply_run.report import (
    _HOLD_SENTENCES, _NOT_A_MOVE_SENTENCES, _wrap, apply_lines, freeze_lines,
    undo_lines,
)
from apply_run.run import applied_entries, plans_under

from .conftest import NODES
from .test_apply_and_undo import _apply, _selected, _take_back
from .test_freeze import _freeze

#: A flag spelled inside a part package is a flag the package can be wrong
#: about, so the composition root passes finished command strings in. This is
#: the guard: no line the package composes may contain one.
_FLAG = re.compile(r"(?<![\w-])--[a-z]")


def _names(world):
    return {file_id: path.name for file_id, path in world.sources.items()}


#: Every (reason, detail) a hold can carry, and the explanation each is owed.
#: `not_a_move` expands over the outcomes because that is where its sentence is
#: keyed; every other reason has one entry and an empty detail.
def _every_explanation():
    for reason in HOLD_REASONS:
        if reason == NOT_A_MOVE:
            for outcome in OUTCOMES:
                if outcome != PLACE:
                    yield reason, outcome, _NOT_A_MOVE_SENTENCES[outcome]
        elif reason == REFUSED_AT_CONSTRUCTION:
            yield reason, "node_refuses_placement", _HOLD_SENTENCES[reason]
        else:
            yield reason, "", _HOLD_SENTENCES[reason]


def _held_block(reason, detail, count):
    """The lines a freeze prints for `count` files stopped for one reason."""
    proposal = FrozenProposal(
        frozen_at="2026-09-03T00:00:00Z", plan_version=None, plans=(),
        held=tuple(
            Held(file_id=f"file-{index}", source_path=None,
                 destination_node=None, reason=reason, detail=detail)
            for index in range(count)),
        replaces=None)
    return freeze_lines(
        proposal, names={f"file-{index}": f"name {index}.txt"
                         for index in range(count)},
        nodes=NODES, apply_command=lambda branch: "cmd",
        apply_everything_command="all")


def test_no_reason_is_glued_into_a_carrying_sentence():
    """`94` F23. What the screen printed, verbatim, before this was fixed:

        problem set 3.docx
        This one is nothing has looked inside it yet, so there is nothing
        here for you to approve.

    A reason phrased as a clause, dropped into `"This one is {reason}"`. Three of
    the seven reasons were phrased that way, so rewording the one on the screen
    would have left the other two waiting for a corpus that reached them.

    So the assertion is not that any particular sentence reads well: it is that
    the line on the screen is EXACTLY the sentence somebody wrote, wrapped, with
    nothing prepended to it. Under that, no glue is possible. Checked in both
    numbers, because a plural is where a carrying phrase would hide.
    """
    for reason, detail, explanation in _every_explanation():
        for count, expected in ((1, explanation.one), (2, explanation.many)):
            lines = _held_block(reason, detail, count)
            assert _wrap(expected, indent="      ") in lines, (
                f"{reason}/{detail} at count {count} did not print its own "
                f"sentence:\n" + "\n".join(lines))


def test_every_explanation_is_a_whole_sentence():
    """The guard against the next fragment, rather than against the last one.

    A half-sentence added to either table would pass the test above -- it would
    still be printed verbatim -- and would read as nonsense on the screen the
    moment a carrying phrase came back. Capital in, full stop out: cheap, and it
    is exactly the shape the three broken reasons failed.
    """
    for _, _, explanation in _every_explanation():
        for sentence in (explanation.one, explanation.many):
            assert sentence[:1].isupper(), sentence
            assert sentence.endswith("."), sentence


def test_the_two_sentence_tables_cover_every_reason_and_every_outcome():
    """A reason with no sentence is `94` F22 again, with a traceback on top."""
    assert set(_HOLD_SENTENCES) == set(HOLD_REASONS)
    assert set(_NOT_A_MOVE_SENTENCES) == set(OUTCOMES) - {PLACE}


def test_an_outcome_with_no_sentence_of_its_own_still_gets_a_true_one():
    """The fallback for an outcome P11 adds after this was written.

    "Nothing about this one became a move" is true of every outcome that is not
    `place`, including one nobody has invented yet, so that is what it gets --
    not `_UNEXPLAINED`, which says this build has no sentence for why and is a
    shrug where a true sentence was available. `_UNEXPLAINED` is for an unknown
    REASON, which is the case where nothing true is known.
    """
    lines = _held_block(NOT_A_MOVE, "an_outcome_from_the_future", 1)
    assert _wrap(_HOLD_SENTENCES[NOT_A_MOVE].one, indent="      ") in lines


def test_two_outcomes_that_are_not_moves_do_not_share_one_sentence():
    """Grouping keys on the detail, so `abstain` and `leave_in_place` part.

    The accounting fixed and one sentence printed over six different things
    would be the file back on the screen and the explanation still missing.
    """
    proposal = FrozenProposal(
        frozen_at="2026-09-03T00:00:00Z", plan_version=None, plans=(),
        held=(Held(file_id="a", source_path=None, destination_node=None,
                   reason=NOT_A_MOVE, detail="abstain"),
              Held(file_id="b", source_path=None, destination_node=None,
                   reason=NOT_A_MOVE, detail="leave_in_place")),
        replaces=None)
    text = " ".join("\n".join(freeze_lines(
        proposal, names={"a": "a.txt", "b": "b.txt"}, nodes=NODES,
        apply_command=lambda branch: "cmd",
        apply_everything_command="all")).split())

    assert "declined to place it rather than guess" in text
    assert "was decided to stay where it is" in text
    # And the machine word for the outcome is not on the screen: the sentence
    # above has already said it in the person's words.
    assert "abstain" not in text and "leave_in_place" not in text


def test_freeze_prints_the_command_it_was_given_and_invents_no_flag(
        world, ids, clock):
    proposal = _freeze(world, world.decisions, ids=ids, clock=clock)
    lines = freeze_lines(
        proposal, names=_names(world), nodes=NODES,
        apply_command=lambda branch: f"THE-COMMAND-FOR[{branch}]",
        apply_everything_command="THE-COMMAND-FOR-EVERYTHING")

    text = "\n".join(lines)
    assert "THE-COMMAND-FOR[Coursework/PHYS1401]" in text
    assert "THE-COMMAND-FOR-EVERYTHING" in text
    # Every branch that got a plan got a line to type, and no flag was spelled.
    assert text.count("THE-COMMAND-FOR[") == 3
    assert _FLAG.search(text) is None, _FLAG.search(text).group(0)


def test_the_headline_count_and_the_files_under_it_agree(world, ids, clock):
    proposal = _freeze(world, world.decisions, ids=ids, clock=clock)
    lines = freeze_lines(proposal, names=_names(world), nodes=NODES,
                         apply_command=lambda branch: "cmd",
                         apply_everything_command="cmd-all")
    headline = next(line for line in lines if line.startswith("Frozen:"))
    assert headline.startswith(f"Frozen: {len(proposal.plans)} file(s)")
    for plan in proposal.plans:
        assert any(_names(world)[plan.file_id] in line for line in lines)


def test_every_held_file_is_named_with_its_reason(world, review_required,
                                                  ids, clock):
    unseen = next(d.subject.file_id for d in review_required
                  if d.review_policy == "review_required")
    proposal = _freeze(world, review_required, ids=ids, clock=clock,
                       shown=frozenset(world.sources) - {unseen})
    text = "\n".join(freeze_lines(
        proposal, names=_names(world), nodes=NODES,
        apply_command=lambda branch: "cmd", apply_everything_command="all"))
    assert proposal.held[0].reason == NOT_SHOWN
    assert "saved article.pdf" in text
    assert "not named on the screen you froze" in text


def test_one_reason_is_printed_once_however_many_files_stopped_for_it(
        world, review_required, ids, clock):
    """The 9,460-line report, arriving in the freeze screen instead.

    Before the owner ruled that a freeze is an approval, a hold was the unusual
    case. Now every file a person still has to deal with arrives here, and one
    sentence per file would repeat the same paragraph until the names were
    unreadable. Every name is still printed; the reason is printed once.
    """
    proposal = _freeze(world, review_required, ids=ids, clock=clock,
                       shown=frozenset())
    text = "\n".join(freeze_lines(
        proposal, names=_names(world), nodes=NODES,
        apply_command=lambda branch: "cmd", apply_everything_command="all"))

    assert len(proposal.held) == 1
    # Widened to a world where several files stop for the same reason, which is
    # what a real corpus is.
    many = dataclasses.replace(
        proposal, held=tuple(
            dataclasses.replace(proposal.held[0], file_id=file_id)
            for file_id in world.sources))
    text = "\n".join(freeze_lines(
        many, names=_names(world), nodes=NODES,
        apply_command=lambda branch: "cmd", apply_everything_command="all"))
    for name in _names(world).values():
        assert name in text
    assert text.count("not named on the screen you froze") == 1


def test_a_protected_file_is_named_in_the_apply_report_with_its_sentence(
        world, ids, clock):
    """`84` §1 again, at the surface: counted and named, never summarised away."""
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    outcome = _apply(world, _selected(plans, "Coursework"), ids=ids, clock=clock)
    text = "\n".join(apply_lines(outcome, names=_names(world),
                                 already_filed=(), undo_command="UNDO-COMMAND"))

    assert "Moved: 2 file(s). Not moved: 1." in text
    assert "passport scan.pdf" in text
    assert "This item is protected by your privacy policy." in text
    assert "UNDO-COMMAND" in text
    assert _FLAG.search(text) is None


def test_undo_says_what_went_back_and_that_no_folder_of_yours_was_removed(
        world, ids, clock):
    plans = _freeze(world, world.decisions, ids=ids, clock=clock).plans
    _apply(world, _selected(plans, "Coursework"), ids=ids, clock=clock)
    world.conn.commit()
    entries = [entry for entry, _ in applied_entries(world.conn)]
    outcome = _take_back(world, entries, ids=ids, clock=clock)

    text = "\n".join(undo_lines(
        outcome, names=_names(world),
        file_of={item.verdict.entry_id: entry.file_id
                 for item, entry in zip(outcome.outcomes, entries)}))
    assert "Put back: 2 file(s). Could not be put back: 0." in text
    assert "No folder you made was removed." in text


def test_an_apply_that_selected_nothing_says_so_rather_than_printing_a_zero(
        world, ids, clock):
    _freeze(world, world.decisions, ids=ids, clock=clock)
    empty = plans_under((), branches_named(("Reading Inbox",), nodes=NODES))
    outcome = _apply(world, empty, ids=ids, clock=clock)
    text = "\n".join(apply_lines(outcome, names={}, already_filed=(),
                                 undo_command="UNDO"))
    assert "Nothing was frozen for the branch(es) you named" in text
    assert "Moved:" not in text
