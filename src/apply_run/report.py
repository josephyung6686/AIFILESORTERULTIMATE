"""What the person reads after freezing, after applying, and after undoing.

Three rules shape every line here.

**What the screen tells a person to type has to be true.** Three defects in this
repo were exactly this. No flag is spelled in this module -- the composition root
owns the flag names and passes in the finished command strings, already quoted --
because a part package that spells a flag is a part package that can be wrong
about one.

**Nothing is summarised away.** Every file that did not move is named with the
sentence saying why. A protected file is counted and named and never opened; a
held file is named; a file the run never reached because it halted is named.
A list may be long. A list that is short because it dropped somebody's file is
worse.

**A count and the list under it say the same thing.** The headline is derived
from the same tuple the body walks, never recomputed from a second source.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from textwrap import fill

from mutation.vocabulary import APPLIED
from placement.vocabulary import (
    ABSTAIN, ASK_USER, LEAVE_IN_PLACE, MARK_REVIEW_LATER, MARK_STATE,
    RETURN_TO_PLACEMENT,
)
from tree_design.records import Node

from apply_run.branches import qualified_path
from apply_run.freeze import (
    ALREADY_AT_DESTINATION, AWAITING_APPROVAL, AWAITING_CLASSIFICATION,
    FrozenProposal, NOT_A_MOVE, NOT_SHOWN, NO_SAFE_NAME,
    PROTECTED_NEEDS_PERMISSION, REFUSED_AT_CONSTRUCTION,
)
from apply_run.run import ApplyOutcome, TakeBackOutcome


@dataclass(frozen=True)
class _Explanation:
    """One hold's explanation, whole, in both numbers.

    `94` F23 is why this is a pair of finished sentences rather than a fragment
    and a carrying phrase. This table used to hold half-sentences that a caller
    completed with `"This one is "`, and it produced, on the screen a person
    reads to find out what happened to their files:

        This one is nothing has looked inside it yet, so there is nothing
        here for you to approve.

    Three of the seven reasons were phrased as clauses rather than as predicates
    and read like that. Rewording the three would have left the shape intact for
    the fourth, so the shape is gone: nothing is prepended to these strings, and
    the sentence on the screen is a sentence somebody wrote and read.
    """

    #: What is printed when exactly one file stopped for this reason.
    one: str
    #: And when more than one did. Not derived from `one`: English plurals of a
    #: whole sentence are not a suffix, and a rule that guessed would reintroduce
    #: F23 by another road.
    many: str


#: One explanation per hold, in the register `66` §10 sets for a decline: say
#: what occurred, and say what is available. Held is not refused -- nothing was
#: attempted -- so none of these tells the person to try again.
_HOLD_SENTENCES: Mapping[str, _Explanation] = {
    # The sentence this used to carry -- "the review screen is not built" -- was
    # true until the owner ruled that freezing IS the review. What is left under
    # this reason is a `review_policy` P11 adds after this was written, and the
    # honest sentence for that is that nothing was assumed about it.
    AWAITING_APPROVAL: _Explanation(
        one="This one is waiting on a kind of review this build has no rule "
            "for, so nothing was assumed on your behalf. It stays where it is.",
        many="Each of these is waiting on a kind of review this build has no "
             "rule for, so nothing was assumed on your behalf. They stay where "
             "they are."),
    AWAITING_CLASSIFICATION: _Explanation(
        one="Nothing has looked inside this one yet, so there is nothing here "
            "for you to approve. Freezing says where a file goes; it cannot say "
            "what a file is. It stays where it is.",
        many="Nothing has looked inside these yet, so there is nothing here for "
             "you to approve. Freezing says where a file goes; it cannot say "
             "what a file is. They stay where they are."),
    NOT_SHOWN: _Explanation(
        one="This one was not named on the screen you froze, so freezing did "
            "not approve it. It stays where it is.",
        many="These were not named on the screen you froze, so freezing did not "
             "approve them. They stay where they are."),
    PROTECTED_NEEDS_PERMISSION: _Explanation(
        one="This one is protected, and freezing a proposal is not permission "
            "to move it. Nothing has been opened, and it stays where it is: "
            "this build has no gesture yet for granting one protected file a "
            "move.",
        many="Each of these is protected, and freezing a proposal is not "
             "permission to move them. Nothing has been opened, and they stay "
             "where they are: this build has no gesture yet for granting one "
             "protected file a move."),
    ALREADY_AT_DESTINATION: _Explanation(
        one="This one is already in the folder the plan would put it in, so "
            "there is nothing to move.",
        many="Each of these is already in the folder the plan would put it in, "
             "so there is nothing to move."),
    REFUSED_AT_CONSTRUCTION: _Explanation(
        one="No plan could be made for this one.",
        many="No plan could be made for these."),
    NO_SAFE_NAME: _Explanation(
        one="No filename safe for this filesystem could be made from its name.",
        many="No filename safe for this filesystem could be made from their "
             "names."),
    # `not_a_move` never reaches this table: its explanation is keyed on the
    # OUTCOME below, because that is what the detail carries. The entry is here
    # so the table still covers `HOLD_REASONS` in full, and it is the sentence a
    # hold under this reason with an empty detail would get.
    NOT_A_MOVE: _Explanation(
        one="Nothing about this one became a move, so there was nothing to "
            "freeze. It stays where it is.",
        many="Nothing about these became a move, so there was nothing to "
             "freeze. They stay where they are."),
}

#: `94` F22's sentences, keyed on P11's outcome. Six of P11's seven outcomes are
#: not `place`, and each is a different thing to have happened to somebody's
#: file: the run declining to guess is not the run being asked a question, and
#: neither is a note recorded about a file that was always staying put. One
#: sentence for all six would be the accounting fixed and the explanation still
#: missing.
#:
#: Every one of them says DECIDED rather than kept back, which is the distinction
#: `freeze`'s docstring used to defend by leaving the file off the screen
#: altogether.
_NOT_A_MOVE_SENTENCES: Mapping[str, _Explanation] = {
    ABSTAIN: _Explanation(
        one="Nothing here could say where this one belongs, so the run declined "
            "to place it rather than guess. That is a decision and not a file "
            "held back, and it stays where it is.",
        many="Nothing here could say where these belong, so the run declined to "
             "place them rather than guess. That is a decision and not files "
             "held back, and they stay where they are."),
    LEAVE_IN_PLACE: _Explanation(
        one="This one was decided to stay where it is, so there was never a "
            "move to freeze.",
        many="These were decided to stay where they are, so there was never a "
             "move to freeze."),
    MARK_REVIEW_LATER: _Explanation(
        one="This one was marked to review later, so no destination was chosen "
            "for it and it stays where it is.",
        many="These were marked to review later, so no destination was chosen "
             "for them and they stay where they are."),
    RETURN_TO_PLACEMENT: _Explanation(
        one="This one went back to be placed again, so this run has no "
            "destination for it to freeze. It stays where it is.",
        many="These went back to be placed again, so this run has no "
             "destination for them to freeze. They stay where they are."),
    MARK_STATE: _Explanation(
        one="What was recorded about this one is a note rather than a "
            "destination, so there is nothing to freeze. It stays where it is.",
        many="What was recorded about these is a note rather than a "
             "destination, so there is nothing to freeze. They stay where they "
             "are."),
    ASK_USER: _Explanation(
        one="This one is a question for you rather than a placement, so there "
            "is nothing here to approve. It stays where it is.",
        many="These are questions for you rather than placements, so there is "
             "nothing here to approve. They stay where they are."),
}

#: The last sentence before silence. Nothing reaches it today -- the two tables
#: above are pinned against `HOLD_REASONS` and `OUTCOMES` by test -- and it
#: exists because the alternative to an unlisted reason is a `KeyError` in the
#: middle of the freeze block, which is `94` F22 again with a traceback on top.
#: `cli.report` keeps an unknown outcome's own name for the same reason: a gap in
#: this deployment's vocabulary must never become a file that vanished.
_UNEXPLAINED: _Explanation = _Explanation(
    one="This one was not frozen, and this build has no sentence for why. It "
        "is named here rather than left off the list, and it stays where it is.",
    many="These were not frozen, and this build has no sentence for why. They "
         "are named here rather than left off the list, and they stay where "
         "they are.")

#: The reasons whose DETAIL is part of the fact rather than a footnote, so two
#: holds under one reason with different details group apart and get their own
#: sentence. For `refused_at_construction` the detail IS the reason -- two files
#: refused by different rules have not stopped for the same thing -- and for
#: `not_a_move` it is the outcome, which is the whole of what happened.
_KEYED_ON_DETAIL: frozenset[str] = frozenset(
    {REFUSED_AT_CONSTRUCTION, NOT_A_MOVE})


def _explain(reason: str, detail: str, *, count: int) -> str:
    """The whole sentence for one group of holds. Never a fragment to glue."""
    if reason == NOT_A_MOVE:
        explanation = _NOT_A_MOVE_SENTENCES.get(detail, _UNEXPLAINED)
    else:
        explanation = _HOLD_SENTENCES.get(reason, _UNEXPLAINED)
    return explanation.one if count == 1 else explanation.many


def _wrap(text: str, *, indent: str = "  ") -> str:
    return fill(text, width=78, initial_indent=indent,
                subsequent_indent=indent)


def _name(names: Mapping[str, str], file_id: str) -> str:
    return names.get(file_id, file_id)


def freeze_lines(proposal: FrozenProposal, *,
                 names: Mapping[str, str],
                 nodes: Sequence[Node],
                 apply_command: Callable[[str], str],
                 apply_everything_command: str) -> tuple[str, ...]:
    """What was frozen, branch by branch, and the exact line to type for each."""
    labels = {node.node_id: qualified_path(node, nodes) for node in nodes}
    by_branch: dict[str, list] = {}
    for plan in proposal.plans:
        by_branch.setdefault(
            labels.get(plan.requested_destination_node,
                       plan.requested_destination_node), []).append(plan)

    lines: list[str] = [""]
    if proposal.replaces is not None:
        lines.append(_wrap(
            f"This replaces the {proposal.replaces.count} file(s) you froze on "
            f"{proposal.replaces.frozen_at}. Anything from that plan you had "
            "already filed stays filed and can still be taken back."))
        lines.append("")

    total = len(proposal.plans)
    if not total:
        lines.append("Nothing was frozen: no placement in this run is ready to "
                     "move.")
    else:
        lines.append(f"Frozen: {total} file(s) are ready to move, in "
                     f"{len(by_branch)} branch(es).")
    for branch in sorted(by_branch):
        plans = by_branch[branch]
        lines.append("")
        lines.append(f"  {branch} -- {len(plans)} file(s)")
        for plan in plans:
            lines.append(f"    {_name(names, plan.file_id)}")
        lines.append(f"    Move these:  {apply_command(branch)}")

    if proposal.held:
        lines.append("")
        lines.append(f"Not frozen, and still exactly where they are "
                     f"-- {len(proposal.held)} file(s):")
        # One sentence per REASON, not per file, and every name printed under
        # it. The reason was one fact the first time it was printed and stayed
        # one fact for the other fourteen -- which is the rule `cli.report`
        # already follows for decisions, and the one that took a real corpus
        # from 9,460 lines to 472. It matters more here than it used to: before
        # the owner ruled that a freeze is an approval, a hold was the unusual
        # case, and now the files a person must still deal with all arrive here.
        #
        # `refused_at_construction` keys on its detail as well, because there
        # the detail IS the reason -- two files refused by different rules have
        # not stopped for the same thing.
        grouped: dict[tuple[str, str], list[str]] = {}
        for item in proposal.held:
            key = (item.reason,
                   item.detail if item.reason in _KEYED_ON_DETAIL else "")
            grouped.setdefault(key, []).append(_name(names, item.file_id))
        for (reason, detail), held_names in grouped.items():
            sentence = _explain(reason, detail, count=len(held_names))
            if reason == PROTECTED_NEEDS_PERMISSION:
                # Counted and explained, and NOT named. The owner ruled on
                # 2026-09-02 that protected filenames sit behind
                # `--show-protected`, and a freeze has no claim on them that the
                # ordinary report does not: it cannot approve a protected file
                # at all, so listing the names here would buy the person
                # nothing and would put a passport on the screen at the moment
                # they are being asked to approve a batch.
                #
                # Not silently omitted, which is the other half of the standing
                # rule: the count is on the screen, the reason is under it, and
                # the total above already includes them. No command is offered,
                # because the gesture that would grant one of these a move is
                # `74` Wave B9's and is not reachable from anything a person can
                # type -- and a line that refuses is worse than no line.
                lines.append(f"    {len(held_names)} protected file(s), counted "
                             f"here and not named")
                lines.append(_wrap(sentence, indent="      "))
                continue
            for name in sorted(held_names):
                lines.append(f"    {name}")
            lines.append(_wrap(sentence, indent="      "))
            # Only `refused_at_construction` prints its detail. The other reason
            # keyed on one carries an OUTCOME there, which the sentence above has
            # already said in the person's words; printing `abstain` under it
            # would put a machine token on the screen and say nothing new.
            if reason == REFUSED_AT_CONSTRUCTION and detail:
                lines.append(_wrap(detail, indent="      "))

    if total:
        lines.append("")
        lines.append(_wrap(
            "Nothing has moved yet. Type one of the lines above to move one "
            "branch, or several of them to move several. To move all of it:",
            indent="  "))
        lines.append(f"    {apply_everything_command}")
    return tuple(lines)


def apply_lines(outcome: ApplyOutcome, *,
                names: Mapping[str, str],
                already_filed: Sequence[str],
                undo_command: str) -> tuple[str, ...]:
    """What moved, what did not, and how to take it back."""
    lines: list[str] = [""]
    moved = outcome.applied
    stopped = outcome.stopped

    if not outcome.outcomes and not already_filed:
        lines.append("Nothing was frozen for the branch(es) you named, so "
                     "nothing moved.")
        return tuple(lines)

    lines.append(f"Moved: {len(moved)} file(s). Not moved: "
                 f"{len(stopped) + len(outcome.not_attempted)}.")
    for item in moved:
        lines.append(f"    {_name(names, item.file_id)}")
        lines.append(f"      -> {item.final_path}")

    if stopped:
        lines.append("")
        lines.append("Left exactly where they were:")
        for item in stopped:
            lines.append(f"    {_name(names, item.file_id)}")
            lines.append(_wrap(item.sentence or item.result, indent="      "))

    if outcome.not_attempted:
        lines.append("")
        lines.append(_wrap(
            "The run stopped before these, and they were not touched:"))
        for plan in outcome.not_attempted:
            lines.append(f"    {_name(names, plan.file_id)}")

    if already_filed:
        lines.append("")
        lines.append(f"Already filed by an earlier run, so not moved again "
                     f"-- {len(already_filed)} file(s):")
        for file_id in already_filed:
            lines.append(f"    {_name(names, file_id)}")

    if moved:
        lines.append("")
        lines.append(_wrap("To put every one of them back exactly where it "
                           "came from:"))
        lines.append(f"    {undo_command}")
    return tuple(lines)


def undo_lines(outcome: TakeBackOutcome, *,
               names: Mapping[str, str],
               file_of: Mapping[str, str]) -> tuple[str, ...]:
    """What went back, and what could not, with the reason for each."""
    lines: list[str] = [""]
    put_back = outcome.reversed_entries
    if not outcome.outcomes:
        lines.append("There is nothing to take back: nothing from the "
                     "branch(es) you named has been moved.")
        return tuple(lines)

    lines.append(f"Put back: {len(put_back)} file(s). Could not be put back: "
                 f"{len(outcome.outcomes) - len(put_back)}.")
    for item in outcome.outcomes:
        entry_id = item.verdict.entry_id
        name = _name(names, file_of.get(entry_id, entry_id))
        if item.verdict.reversed_successfully:
            lines.append(f"    {name}")
            lines.append(f"      -> {item.verdict.original_source_path}")
        else:
            lines.append(f"    {name}")
            lines.append(_wrap(item.sentence or item.verdict.verdict,
                               indent="      "))
            lines.append(f"      it is at: {item.verdict.destination_path}")
            lines.append(f"      it came from: "
                         f"{item.verdict.original_source_path}")

    removed = [path for item in outcome.outcomes
               for path, result in item.verdict.directory_outcomes
               if result == "removed"]
    if removed:
        lines.append("")
        lines.append(f"{len(removed)} folder(s) this product had made are gone "
                     "again. No folder you made was removed.")
    return tuple(lines)


#: Re-exported so a caller rendering a mixed list does not import two modules
#: to ask one question.
__all__ = ["apply_lines", "freeze_lines", "undo_lines", "APPLIED"]
