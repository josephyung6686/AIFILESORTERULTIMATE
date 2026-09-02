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
from textwrap import fill

from mutation.vocabulary import APPLIED
from tree_design.records import Node

from apply_run.branches import qualified_path
from apply_run.freeze import (
    ALREADY_AT_DESTINATION, AWAITING_APPROVAL, AWAITING_CLASSIFICATION,
    FrozenProposal, NOT_SHOWN, NO_SAFE_NAME, PROTECTED_NEEDS_PERMISSION,
    REFUSED_AT_CONSTRUCTION,
)
from apply_run.run import ApplyOutcome, TakeBackOutcome

#: One sentence per hold, in the register `66` §10 sets for a decline: say what
#: occurred, and say what is available. Held is not refused -- nothing was
#: attempted -- so none of these tells the person to try again.
_HOLD_SENTENCES: Mapping[str, str] = {
    # The sentence this used to carry -- "the review screen is not built" -- was
    # true until the owner ruled that freezing IS the review. What is left under
    # this reason is a `review_policy` P11 adds after this was written, and the
    # honest sentence for that is that nothing was assumed about it.
    AWAITING_APPROVAL:
        "waiting on a kind of review this build has no rule for, so nothing "
        "was assumed on your behalf. It stays where it is.",
    AWAITING_CLASSIFICATION:
        "nothing has looked inside it yet, so there is nothing here for you to "
        "approve. Freezing says where a file goes; it cannot say what a file "
        "is. It stays where it is.",
    NOT_SHOWN:
        "not named on the screen you froze, so freezing did not approve it. "
        "It stays where it is.",
    PROTECTED_NEEDS_PERMISSION:
        "protected, and freezing a proposal is not permission to move it. "
        "Nothing has been opened, and it stays where it is: this build has no "
        "gesture yet for granting one protected file a move.",
    ALREADY_AT_DESTINATION:
        "already in the folder the plan would put it in, so there is nothing "
        "to move.",
    REFUSED_AT_CONSTRUCTION:
        "no plan could be made for it.",
    NO_SAFE_NAME:
        "no filename safe for this filesystem could be made from its name.",
}


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
        for item in proposal.held:
            lines.append(f"    {_name(names, item.file_id)} -- "
                         f"{_HOLD_SENTENCES[item.reason]}")
            if item.reason == REFUSED_AT_CONSTRUCTION:
                lines.append(_wrap(item.detail, indent="      "))

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
