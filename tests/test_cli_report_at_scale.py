# tests/test_cli_report_at_scale.py
"""The report a person reads when the corpus is a real disk and not a demo folder.

Two files produce forty readable lines. Five thousand produced 9,460 -- 236
screens -- and 97.7 % of them were the file section, because §8.6 splits a review
set over the batch ceiling rather than truncating it and the report keyed its
groups on the resulting shard LABEL. One hold, held for one reason, arrived as 420
report groups, each repeating the same reason and the same explanation verbatim.
The one thing the person could act on -- the questions -- sat at line 9,317.

Measured on a generated corpus with the realistic mess of a person's disk
(coursework, payslips, a lease, medical notes, a passport, memes, screenshots,
game saves, junk downloads, and one `.app` bundle):

    files      report lines    review sets    the questions block starts at
       10               126              1    line 67
      100               480             11    line 337
    1,000             2,366             86    line 2,223
    5,000             9,460            420    line 9,317

These tests are about the shape of that report, so they build the run directly
rather than scanning five thousand files: the stub is the same one
`tests/test_cli.py` uses, and the live path is covered end to end by
`tests/integration/test_production_corpus.py`.
"""
from __future__ import annotations

import io
import shlex
import sys

import pytest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402

#: The eight tests below describe the report AFTER
#: `scratchpad/report/CLI-PATCH.txt`'s four hunks are applied to `src/cli.py`,
#: which belongs to the lead and which this agent may not edit. They were written
#: first, run red, and then run green against the patched source -- `patchcli.py`
#: beside the patch reads `src/cli.py`, applies the hunks and imports the result,
#: so the whole of `tests/test_cli.py` and this file were run against exactly the
#: text that will be pasted in.
#:
#: Strict, and for the reason this repo already uses strict for: eleven sessions
#: share this suite and eight red tests would be eight false alarms, while eight
#: XPASSes the moment the hunks land is the unambiguous signal to strip these
#: markers. **Applying the patch means deleting every `@pytest.mark.xfail(...
#: PENDING_PATCH)` line in this file, and the identical one on
#: `tests/test_cli.py::test_a_printed_send_set_command_survives_being_pasted_
#: into_a_shell`, which those hunks also fix.**
PENDING_PATCH = (
    "Describes the report after scratchpad/report/CLI-PATCH.txt's four hunks are "
    "applied to src/cli.py, which the report agent may not edit. Verified green "
    "against the patched source by scratchpad/report/patchcli.py. Strict, so the "
    "suite goes red the day the hunks land and these markers come off with them.")

REASON = ("no destination in this tree matched them well enough to decide "
          "without asking you.")
PROTECTED_REASON = (
    "these are protected material, so they are counted and named here and "
    "nothing was assembled about them. They are not filed in one gesture with "
    "everything else; each one is yours to decide.")
EXPLANATION = (
    "Deciding this file needed a model, and §8.4 did not clear this file for a "
    "model call. Nothing about it left this device and nothing moved; the "
    "evidence is retained.")


def _decision(*, file_id, explanation, protected=False):
    return SimpleNamespace(
        outcome="abstain", explanation=explanation, marked_state=None,
        review_policy="auto_eligible",
        subject=SimpleNamespace(file_id=file_id, member_file_ids=()),
        destination=None, privacy=SimpleNamespace(protected=protected))


def _node(node_id, label, *, parent=None, accepts=True, role=None):
    node = SimpleNamespace(node_id=node_id, display_label=label,
                           parent_node_id=parent, accepts_placement=accepts)
    if role is not None:
        node.node_role = role
    return node


def _set(label, members, reason, *, protected=False):
    return SimpleNamespace(label=label, member_file_ids=tuple(members),
                           file_count=len(members), reason_not_placed=reason,
                           protected=protected)


def _run(*, nodes, decisions, sets):
    return SimpleNamespace(
        protected_areas=(),
        tree=SimpleNamespace(tree=SimpleNamespace(
            plan_version_id="version_2", nodes=tuple(nodes))),
        destinations=("node_0",),
        placement=SimpleNamespace(decisions=tuple(decisions),
                                  residual_sets=tuple(sets)))


def _shards(count, per_set, *, base="Not yet placed", reason=REASON,
            protected=False, first=0):
    """One hold, split by the batch ceiling into `count` sets of `per_set` files.

    Exactly what `surface_residual_sets` produces: "Split, never truncate", with
    each batch carrying its own `(i of n)` label and the SAME reason.
    """
    sets, decisions, names = [], [], {}
    file_no = first
    for index in range(1, count + 1):
        members = []
        for _ in range(per_set):
            file_id = f"id-{file_no}"
            names[file_id] = f"folder-{file_no // 20}/note-{file_no:05d}.txt"
            members.append(file_id)
            decisions.append(_decision(
                file_id=file_id,
                explanation=PROTECTED_REASON if protected else EXPLANATION,
                protected=protected))
            file_no += 1
        sets.append(_set(f"{base} ({index} of {count})", members, reason,
                         protected=protected))
    return sets, decisions, names


def _at_scale(*, sets_count=420, per_set=8, areas=("Review Later",)):
    """A five-thousand-file run, as the measurement above found it."""
    nodes = [_node("node_0", "Coursework")]
    nodes += [_node(f"res_{n}", area, role="residual")
              for n, area in enumerate(areas)]
    sets, decisions, names = _shards(sets_count, per_set)
    protected_sets, protected_decisions, protected_names = _shards(
        12, 8, base="Protected, and not filed in bulk",
        reason=PROTECTED_REASON, protected=True, first=100000)
    return (_run(nodes=nodes, decisions=decisions + protected_decisions,
                 sets=sets + protected_sets),
            {**names, **protected_names})


def _printed(run, names):
    out = io.StringIO()
    cli.report(run, names, out=out)
    return out.getvalue()


def _files_section(printed: str) -> list[str]:
    lines = printed.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("Files:"))
    end = next((i for i, line in enumerate(lines)
                if i > start and line.startswith("Decisions made for you")),
               len(lines))
    return lines[start:end]


# ======================================================================================
# The measurement, as an assertion
# ======================================================================================

def test_a_hold_split_into_four_hundred_batches_is_one_reason_said_once():
    """§8.6 splits a set over the batch ceiling; it does not split the REASON.

    The reason was one fact the first time it was printed and stayed one fact the
    other 419 times. `report` already says that in a comment about file-level
    explanations -- "one line per KIND of outcome, not one per file" -- and then
    keyed the group on the shard label, which put the same sentence on the screen
    once per batch.
    """
    run, names = _at_scale()
    # Flattened, because the report wraps to the width of a terminal and the
    # sentence is the fact, not the line.
    flat = " ".join(_printed(run, names).split())

    assert flat.count(REASON) == 1, (
        f"the hold's reason is printed {flat.count(REASON)} times; it is one "
        "fact about 3,360 files and belongs on the screen once")
    assert flat.count(EXPLANATION) == 1, (
        f"the file-level explanation is printed {flat.count(EXPLANATION)} "
        "times for one reason shared by every one of those files")


def test_four_hundred_batches_of_one_hold_are_one_group_and_not_four_hundred():
    """The headings, which is what a person scrolls past."""
    run, names = _at_scale()
    headings = [line for line in _files_section(_printed(run, names))
                if line.startswith("  ") and " -- " in line
                and line.strip().endswith(("file", "files"))]

    assert len(headings) <= 4, (
        f"{len(headings)} group headings for two holds:\n"
        + "\n".join(headings[:12]))


def test_the_whole_report_fits_in_a_handful_of_screens_at_five_thousand_files():
    """236 screens is not a report. The budget is what makes this a test rather
    than an impression: a person's whole disk, on four screens."""
    run, names = _at_scale()
    printed = _printed(run, names)
    lines = printed.splitlines()

    # 220 and not 60, because about 110 of those lines are the ninety-six
    # protected filenames and the twelve protected sets, listed in full because
    # the standing rule says a protected thing is never summarised away. What
    # the budget bounds is everything the report is free to shorten.
    assert len(lines) <= 220, (
        f"{len(lines)} lines ({len(lines) / 40:.0f} screens) for 3,456 files:\n"
        + printed[:4000])
    # And the part that IS free to shorten: the ordinary hold, 420 batches and
    # 3,360 files, from the "Files:" headline to the next group.
    section = _files_section(printed)
    second = next(i for i, line in enumerate(section)
                  if i > 1 and line.startswith("  ") and " -- " in line
                  and line.strip().endswith(("file", "files")))
    assert second <= 40, (
        f"the first group runs to {second} lines:\n" + "\n".join(section[:second]))


def test_everything_a_person_can_type_is_reachable_without_scrolling_past_it():
    """`--send-set` is the gesture this report exists to offer. At 5,000 files the
    first one sat at line 86 and the four-hundredth at line 9,300, with the same
    two paragraphs between every pair. What a person needs is all of them
    together, in the first screen or two -- not one at the top of a hundred
    screens of prose that says the same thing each time."""
    run, names = _at_scale()
    lines = _printed(run, names).splitlines()

    offered = [i for i, line in enumerate(lines) if "--send-set" in line]
    assert offered, "no command was offered at all"
    assert max(offered) <= 80, (
        f"the last thing a person can type is on line {max(offered)}, "
        f"{max(offered) / 40:.0f} screens down")


# ======================================================================================
# Simpler must not mean less true
# ======================================================================================

def test_every_review_set_is_counted_even_when_the_names_are_shortened():
    """Nothing may be dropped to make the output shorter. A set that is not named
    is still counted, and the report says how many were counted rather than
    listed -- the same shortening the file lists already use, and the same
    sentence, so that the promise is one promise."""
    run, names = _at_scale()
    printed = _printed(run, names)

    commands = [line for line in printed.splitlines() if "--send-set" in line]
    assert len(commands) < 420, "420 set names is the list this shortening exists for"
    flat = " ".join(printed.split())
    assert f"and {420 - len(commands)} more review sets" in flat, flat
    assert "never summarised away" in flat, flat
    # The count of files is the whole hold, not the part that got named.
    assert "420 review sets of it have files under this heading" in flat, flat


def test_a_protected_hold_is_never_the_one_summarised_away():
    """The standing rule, arriving as a usability change.

    Shortening the ordinary list is fine. Shortening the part that says what was
    marked protected and left alone is the exact harm the rule forbids, so every
    protected set is named however many there are.
    """
    run, names = _at_scale()
    printed = _printed(run, names)

    for index in range(1, 13):
        label = f"Protected, and not filed in bulk ({index} of 12)"
        assert label in printed, (
            f"{label!r} was summarised away; a protected set is marked and "
            f"counted and never silently omitted:\n{printed}")


def test_a_protected_hold_is_still_offered_no_command():
    """P11 refuses `--send-set` over protected material before it reads any
    decision, so printing the flag beside a protected set would be an instruction
    that always fails. Collapsing the report may not put it back."""
    run, names = _at_scale()
    printed = _printed(run, names)

    for block in printed.split("\n\n"):
        if "Protected, and not filed in bulk" in block:
            assert "--send-set" not in block, block
    # The twin, in the same run: the ordinary hold IS still offered it.
    assert "--send-set" in printed


def test_a_printed_send_set_command_is_a_line_a_shell_can_parse():
    """What the screen tells a person to type has to be true.

    `--answer` learned this first: a command a text wrapper has broken across two
    lines is not a command, because the quote never closes. Every shipped
    residual-area name is exercised rather than one, because the defect is a
    width accident -- `Review Later` happens to fit and
    `Receipts and Confirmations` happens not to.
    """
    from tree_design.vocabulary import RESIDUAL_TEMPLATE_NAMES

    for area in RESIDUAL_TEMPLATE_NAMES:
        run, names = _at_scale(sets_count=3, areas=(area,))
        printed = _printed(run, names)
        offered = [line for line in printed.splitlines() if "--send-set" in line]
        assert offered, f"no --send-set was offered for {area!r}:\n{printed}"
        for line in offered:
            command = line[line.index("--send-set"):]
            tokens = shlex.split(command)
            assert tokens[0] == "--send-set", line
            assert len(tokens) == 2, (
                f"{command!r} splits into {tokens!r}: pasting it would pass "
                f"{tokens[1]!r} to --send-set and leave the rest as stray "
                "arguments")
            assert tokens[1].endswith(f"={area}"), tokens[1]


def test_the_command_names_the_set_it_would_actually_send():
    """A gesture that acts on something other than what the person named is worse
    than one that stops and asks -- and `act_on_residual_sets` refuses a bare
    label that names no surfaced set. So the command printed beside a batch names
    THAT batch, and the sentence beside it does not promise it files the rest."""
    run, names = _at_scale(sets_count=4)
    printed = _printed(run, names)

    offered = [line for line in printed.splitlines() if "--send-set" in line]
    assert [shlex.split(line[line.index("--send-set"):])[1] for line in offered] \
        == [f"Not yet placed ({n} of 4)=Review Later" for n in range(1, 5)], offered
    flat = " ".join(printed.split())
    assert "To file them all at once" not in flat, (
        "one --send-set names one review set, and this run has four of them")


def test_with_no_area_enabled_the_report_says_how_to_make_one_and_names_the_sets():
    """The sentence that exists because naming a flag that would refuse is worse
    than naming none. It survives the collapse, and so do the set names."""
    run, names = _at_scale(sets_count=3, areas=())
    printed = _printed(run, names)

    flat = " ".join(printed.split())
    assert "--send-set" not in printed, (
        "a plan with no residual area offers a command that would refuse")
    assert '--residual "Review Later"' in flat, flat
    assert "Not yet placed (1 of 3)" in printed, printed


def test_a_batch_whose_files_straddle_two_headings_claims_no_total_it_cannot_see():
    """The sentence beside a hold may only say what that heading can see.

    §8.6's batches do not respect the boundaries the report groups by: a batch of
    eight files where five stopped for one reason and three for another has files
    under two headings. A sentence saying "the hold is split into N review sets"
    is then printed twice with two different Ns, neither of them the hold's, and
    a person adding them up gets a number that is not a number of anything.

    So each heading counts only the batches with files under IT, and says so in
    those words. Four batches, every one of them straddling, and the count under
    each heading is four -- which is true of that heading and claims nothing about
    the hold.
    """
    nodes = [_node("node_0", "Coursework"),
             _node("res_0", "Review Later", role="residual")]
    other = ("This file has not been classified, so it was not shown to a model.")
    sets, decisions, names = [], [], {}
    file_no = 0
    for index in range(1, 5):
        members = []
        for offset in range(8):
            file_id = f"id-{file_no}"
            names[file_id] = f"note-{file_no:03d}.txt"
            members.append(file_id)
            decisions.append(_decision(
                file_id=file_id,
                explanation=EXPLANATION if offset < 5 else other))
            file_no += 1
        sets.append(_set(f"Not yet placed ({index} of 4)", members, REASON))
    printed = _printed(_run(nodes=nodes, decisions=decisions, sets=sets), names)
    flat = " ".join(printed.split())

    assert flat.count("4 review sets of it have files under this heading") == 2, (
        flat)
    assert "split into" not in flat, flat
    # And the twin: the count is a real count, not the constant 4. A hold that is
    # ONE batch under a heading is named in the sentence and gets no roll-call.
    one_sets, one_decisions, one_names = _shards(1, 4)
    solo = " ".join(_printed(_run(nodes=nodes, decisions=one_decisions,
                                  sets=one_sets), one_names).split())
    assert "review sets of it" not in solo, solo
    assert 'Held for review as "Not yet placed (1 of 1)"' in solo, solo
