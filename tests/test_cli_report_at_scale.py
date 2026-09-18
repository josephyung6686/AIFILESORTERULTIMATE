# tests/test_cli_report_at_scale.py
"""The report a person reads when the corpus is a real disk and not a demo folder.

Two files produce forty readable lines. Five thousand produced 9,470 -- 237
screens -- and 97.7 % of them were the file section, because §8.6 splits a review
set over the batch ceiling rather than truncating it and the report keyed its
groups on the resulting shard LABEL. One hold, held for one reason, arrived as 420
report groups, each repeating the same reason and the same explanation verbatim:
1,072 of the report's sentences were repeats of one already printed, the worst of
them 432 times. The one thing the person could act on -- the questions -- sat at
line 9,317.

Measured on a generated corpus with the realistic mess of a person's disk
(coursework, payslips, a lease, medical notes, a passport, memes, screenshots,
game saves, junk downloads, and one `.app` bundle). Both columns against the same
`src/cli.py`, so the role-matcher block that landed the same day counts in both:

    files    lines BEFORE    AFTER    review sets    the questions block
       10             137      137              1    line 70 -> 70
      100             491      313             11    line 337 -> 159
    1,000           2,377      475             95    line 2,223 -> 337
    5,000           9,470        ?            420    line 9,317 -> ?

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

#: Eight of these were written before the change they describe and carried a
#: `strict=True` xfail while `src/cli.py`'s four hunks were waiting on the lead --
#: eight red tests in a suite eleven sessions share would have been eight false
#: alarms, and eight XPASSes was the signal that the hunks had landed. They landed
#: in `d99f501` and the markers came off with them, which is why there are none
#: here now.

REASON = ("no destination in this tree matched them well enough to decide "
          "without asking you.")
# `104` §18.100. The old words said these files are "counted and named here"
# while `_review_note` withholds every example on a protected card, and a
# protected filename reaches the plain report through no path. The screen
# promised what the standing rule forbids; this pin moved with the sentence.
PROTECTED_REASON = (
    "these are protected material, so they are counted here and not named, and "
    "nothing was assembled about them. They are not filed in one gesture with "
    "everything else; each one is yours to decide, and their names are shown "
    "only when you ask for them by the command below.")
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
    """`104` commit 9322206 wired `review_surface.residual.residual_card` into the
    report, and `residual_card` raises `IncompleteResidualCard` unless all seven
    of §7.5's attributes are present -- `WEAK_NEIGHBOURS` alone may be empty, an
    honest "there are none" rather than a gap. This helper used to build only
    `label`, `member_file_ids`/`file_count`, `reason_not_placed` and `protected`;
    the five below complete it so every card these tests build renders instead of
    falling back to `_review_note`'s "Nothing on this screen says the ..." line.
    """
    members = tuple(members)
    return SimpleNamespace(
        set_id=label, plan_version="version_2",
        label=label, member_file_ids=members,
        file_count=len(members), reason_not_placed=reason, protected=protected,
        # A placeholder id that is never one of `members`: `_set_card_lines`
        # filters `representative_examples` down to the ids under the heading
        # being rendered (`under`), so a set that spans several headings in these
        # tests -- `_three_groups_in_one_state`'s one set covering nine files
        # under three -- would print a DIFFERENT "Examples:" line per heading if
        # this carried real members, and a block that differs per heading cannot
        # fold even when its reason is the one fact these tests are about. The
        # completeness check only needs the tuple non-empty; it does not have to
        # resolve to a name, and nothing here asserts what the examples line says.
        representative_examples=("__unshown_example__",),
        file_type_distribution=(("txt", len(members)),),
        age_range=("2026-01-01", "2026-01-01"),
        evidence_availability="none",
        sensitivity_status="none",
        weak_graph_neighbours=())


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


def _printed(run, names, *, show_protected=False):
    """Forwarded only when it is True, so the eleven tests here that predate
    `--show-protected` keep running against a `report` that has never heard of
    it. Passing it unconditionally turned every one of them into a TypeError."""
    extra = {"show_protected": True} if show_protected else {}
    out = io.StringIO()
    cli.report(run, names, out=out, **extra)
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

    assert flat.count(EXPLANATION) == 1, (
        f"the file-level explanation is printed {flat.count(EXPLANATION)} "
        "times for one reason shared by every one of those files")
    # `104` R-124 MOVED WHERE THAT ONE PRINTING IS, and this assertion moved with
    # it. The reason used to be on the screen twice for a group that prints one:
    # four lines of "Same reason for each: <the decision's explanation>" and four
    # more of `Held for review as "<set>": <the set's wording of the same fact>`.
    # The held line is now the NAME only -- the part `--send-set` takes and the
    # part the sentence above it does not carry -- so the set's own wording is
    # not under the group at all. It is still on the screen wherever a set is
    # listed on its own, which is what `test_a_set_covering_no_decided_file...`
    # holds. The fact itself is still printed exactly once, which is what this
    # test has always been about.
    assert flat.count(REASON) == 0, (
        f"the set's reason is restated {flat.count(REASON)} times under a group "
        "whose 'Same reason for each' line has already said it")
    assert flat.count('Held for review as "Not yet placed (1 of 420)"') == 1, (
        "the set's NAME went with the restatement; it is what a person types")


def test_four_hundred_batches_of_one_hold_are_one_group_and_not_four_hundred():
    """The headings, which is what a person scrolls past."""
    run, names = _at_scale()
    headings = [line for line in _files_section(_printed(run, names))
                if line.startswith("  ") and " -- " in line
                and line.strip().endswith(("file", "files"))]

    assert len(headings) <= 4, (
        f"{len(headings)} group headings for two holds:\n"
        + "\n".join(headings[:12]))


#: The tests below describe the report AFTER the six hunks in
#: `scratchpad/report/SHOW-PROTECTED-PATCH.txt` are applied to `src/cli.py`,
#: which belongs to the lead and which this agent may not edit. Strict, for the
#: reason this repo already uses strict: eleven sessions share this suite, so a
#: dozen red tests would be a dozen false alarms, while a dozen XPASSes the
#: moment the hunks land is the signal to strip these markers. **Applying the
#: patch means deleting every `PENDING_SHOW_PROTECTED` marker in this file.**
def test_the_whole_report_fits_in_a_handful_of_screens_at_five_thousand_files():
    """237 screens is not a report. The budget is what makes this a test rather
    than an impression -- and it is 220 lines and not 60 because the protected
    group inside it is listed in full by rule, which the assertions below split
    apart: the part the report is free to shorten is held to forty."""
    run, names = _at_scale()
    printed = _printed(run, names)
    lines = printed.splitlines()

    # The budget was 220 while a protected group was listed in full: 96
    # filenames of the 203 lines. The owner's 2026-09-02 ruling summarises those
    # by default, so the whole report is now the part that was always free to
    # shorten, plus a count and a command. `104` commit 9322206 (11 Sep) then wired
    # §7.5's residual card into this screen, which is two more lines PER SET shown
    # -- "File types: ...; Age range: ..." and "Available OCR or text evidence:
    # ...; Sensitivity: ..." -- for the ten sets `NAMES_LISTED_PER_GROUP` shows of
    # the ordinary hold and for every one of the twelve protected batches, which
    # are never shortened. 120 was the budget before the card had a caller; 180
    # is the same budget with the card's two lines counted in for the 22 sets this
    # screen actually shows.
    assert len(lines) <= 180, (
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
    # `104` commit 9322206 (11 Sep) put §7.5's card ahead of each `--send-set` line
    # in the roll-call -- two more lines per set, for every one of the ten
    # `NAMES_LISTED_PER_GROUP` sets shown -- which pushes the last command a fixed
    # twenty lines further down than the 80 this budget was measured against
    # before the card had a caller. Still one screen or two, not the hundred this
    # test exists to refuse.
    assert max(offered) <= 100, (
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


def test_the_protected_list_no_longer_decides_how_long_the_report_is():
    """What the owner's ruling was measured against.

    The collapse fixed the repetition and left one thing growing linearly with
    the person's disk: the protected group, listed in full. At 5,000 files it was
    810 lines of 1,113 -- 73 % of the report -- and 710 of them were filenames.

    The property is precise, and it is NOT "the report stops growing". Protected
    review SET names are still uncapped -- deliberately, they are summaries
    already and leak nothing about the files -- so the report still grows, at a
    FIXED number of lines per BATCH. What it no longer does is grow at one line
    per FILE, which is the rate that made it 73 % filenames. Ten times the
    protected material here is 864 more files and 108 more batches, and the
    assertions below say the growth tracks the second number and not the first.

    **The per-batch constant moved from ~1 to 3, and that is `104` commit
    9322206 (11 Sep), not a regression of this property.** Before it, a protected
    batch was its own header line and nothing else; §7.5's card had been computed
    and never rendered. Now every protected batch's card renders too --
    `_set_card_lines` returns the "File types; Age range" line and the "Available
    OCR or text evidence; Sensitivity" line beside the header line that already
    existed, and `Denied a --send-set` for protected material means no command
    line is added on top of those three. The growth is still linear in BATCHES
    and not in files -- 3 lines for 8 files is well under the one-line-per-file
    rate this test exists to refuse -- so both budgets below are the same
    property, re-measured against the constant this commit actually produces.
    """
    small = _printed(*_at_scale())
    nodes = [_node("node_0", "Coursework"),
             _node("res_0", "Review Later", role="residual")]
    sets, decisions, names = _shards(420, 8)
    # Ten times the protected material, same everything else.
    big_sets, big_decisions, big_names = _shards(
        120, 8, base="Protected, and not filed in bulk",
        reason=PROTECTED_REASON, protected=True, first=100000)
    large = _printed(_run(nodes=nodes, decisions=decisions + big_decisions,
                          sets=sets + big_sets), {**names, **big_names})

    added_files, added_batches = 960 - 96, 120 - 12
    grew = len(large.splitlines()) - len(small.splitlines())
    assert grew <= added_batches * 3 + 20, (
        f"{added_batches} more review sets added {grew} lines; the growth should "
        "be three lines per batch (header, file types/age, evidence/sensitivity) "
        "and this is more than that")
    assert grew < added_files // 2, (
        f"ten times the protected material added {grew} lines for "
        f"{added_files} more files; the report is still growing at the file "
        "rate, which is what made it mostly a list of private filenames")
    # The twin: the count itself must still grow, or the summary is not counting.
    assert "960 protected files" in large, large
    assert "96 protected files" in small, small


def test_show_protected_is_the_only_thing_that_expands_the_names():
    """The negative twin of the summary: asking for it works, and nothing else
    turns it on by accident. An ordinary group stays shortened either way --
    `--show-protected` is about protected material, not a verbosity switch."""
    run, names = _at_scale()
    shown = _printed(run, names, show_protected=True)

    for index in range(100000, 100096):
        assert f"note-{index:05d}.txt" in shown, (
            f"note-{index:05d}.txt is missing from --show-protected; the "
            "expansion is every one of them")
    ordinary = [line for line in shown.splitlines()
                if line.strip().startswith("folder-0/note-")]
    assert len(ordinary) == cli.NAMES_LISTED_PER_GROUP, (
        f"--show-protected also lengthened the ordinary list to {len(ordinary)}; "
        "it is not a verbosity flag")
    # `104` R-125. The sentence that shortens the list ENDS. It read "...with the
    # way to see it printed there -- summarised, but never silently", and stopped
    # there: the reader is left to guess the word, and the word is the whole
    # promise the standing rule makes about protected material.
    flat = " ".join(shown.split())
    assert "summarised, but never silently omitted." in flat, (
        "the sentence about protected material trails off mid-clause")
    assert "never silently omitted. " in flat or flat.endswith(
        "never silently omitted."), flat




def test_the_flag_is_named_only_on_the_line_that_is_the_command():
    """What the screen tells a person to type has to be true, and FINDABLE.

    Caught by running it: the first line of the report containing
    `--show-protected` was the ordinary group's shortening sentence, which
    mentioned the flag in prose inside backticks. A person -- or a script --
    looking for the thing to type found the backticked one first,
    which a shell reads as three stray words. The command was correct and four
    lines further down, which is no help to anyone who took the first one.

    So the flag appears on exactly one kind of line: the one that is nothing but
    the command.
    """
    run, names = _at_scale()
    mentions = [line for line in _printed(run, names).splitlines()
                if "--show-protected" in line]

    assert mentions, "the way to see protected filenames was not offered at all"
    for line in mentions:
        assert line.strip() == "--show-protected", (
            f"{line.strip()!r} names the flag but is not the command; a person "
            "searching the report for what to type can land on it")


def test_showing_a_protected_name_does_not_let_a_freeze_approve_it():
    """A flag about what is on the SCREEN may not widen what a gesture may MOVE.

    `report` returns the file ids it printed by name, and that set is what a
    `--freeze` is allowed to approve -- the owner's rule that an approval covers
    what the person was shown. `--show-protected` prints protected filenames, so
    the naive merge of the two rulings hands a freeze permission over a passport
    by way of a display flag. That is the "acts on something other than what the
    person named" failure in its worst form: the person asked to SEE something
    and would have granted permission to MOVE it.

    A freeze already refuses protected placements downstream, so this is the
    second of two independent refusals, which is what "never" means.
    """
    run, names = _at_scale()
    protected = {f"id-{n}" for n in range(100000, 100096)}

    hidden = cli.report(run, names, out=io.StringIO())
    shown = cli.report(run, names, out=io.StringIO(), show_protected=True)

    assert not protected & set(hidden), "a protected id was approvable by default"
    assert not protected & set(shown), (
        "--show-protected put protected files into the set a freeze may "
        "approve; a flag about the screen has become a permission to move")
    # The twin: it IS returning the ordinary names, so the assertion above is
    # not passing because the function returns nothing.
    assert set(hidden) == set(shown), (
        "--show-protected changed which ORDINARY files a freeze may approve")
    assert len(hidden) >= cli.NAMES_LISTED_PER_GROUP, hidden


# ======================================================================================
# `104` R-114: a paragraph that is one fact about six groups
# ======================================================================================

#: Fresh offline walkthrough of a 52-file folder: 430 lines, of which the
#: eight-line "Nothing on this screen says what these are" explanation was
#: printed once per group in that state -- six times -- and the "Held for review
#: as ... this plan has nowhere to put them yet" block eight times, each followed
#: by the same list of review sets. Every printing was honest, and a person stops
#: reading at the third.
#:
#: Three destinations is what makes three groups here. A placement's headline
#: comes from its destination and its review policy, and its own explanation is
#: not printed at all -- `report` prints "Same reason for each" only where the
#: outcome is not a placement -- so the folder is the whole difference between
#: these three headings, which is exactly the case the measurement found.
BLOCKED = "blocked_pending_user"
COURSES = ("CS3134", "ECON2010", "PHYS1401")


def _blocked(*, file_id, node_id):
    """A placement with a destination, waiting on somebody to say what it is."""
    return SimpleNamespace(
        outcome="place", explanation="", marked_state=None,
        review_policy=BLOCKED,
        subject=SimpleNamespace(file_id=file_id, member_file_ids=()),
        destination=SimpleNamespace(node_id=node_id),
        privacy=SimpleNamespace(protected=False))


def _three_groups_in_one_state():
    """Three headings, one hold, and one review set covering all nine files."""
    nodes = [_node("node_0", "Coursework")]
    nodes += [_node(f"n_{label}", label, parent="node_0") for label in COURSES]
    decisions, names, members = [], {}, []
    for label in COURSES:
        for number in range(3):
            file_id = f"id-{label}-{number}"
            names[file_id] = f"{label.lower()}-note-{number}.txt"
            members.append(file_id)
            decisions.append(_blocked(file_id=file_id, node_id=f"n_{label}"))
    return (_run(nodes=nodes, decisions=decisions,
                 sets=[_set("Not yet placed", members, REASON)]), names)


def test_a_paragraph_that_is_one_fact_about_three_groups_is_printed_once():
    """`104` R-114. Said in full where it first applies, pointed at after that.

    Both shared paragraphs are asserted at once because both were measured on
    the same screen: the explanation for files nothing on the report reaches,
    and the hold offering the same set and the same command under every heading.
    Neither is a fact about the group it happens to sit under.
    """
    run, names = _three_groups_in_one_state()
    flat = " ".join(_printed(run, names).split())

    said = flat.count("Nothing on this screen says what these are")
    assert said == 1, (
        f"the explanation for files nothing here reaches is printed {said} "
        "times; it is one fact about all three groups")
    held = flat.count("This plan has nowhere to put them yet")
    assert held == 1, f"the hold's 'enable an area' block is printed {held} times"
    assert flat.count(REASON) == 1, flat

    # And the two groups that did not carry them say where they are, in one line
    # each rather than in silence.
    assert flat.count("Waiting on the same thing as the") == 2, flat
    assert flat.count("the set and the command are under the") == 2, flat
    # Pointed at by the name a person reads on the heading above it, which is
    # the folder when the group has one.
    assert flat.count("as the CS3134 group above") == 2, flat
    assert "ECON2010 group above" not in flat, (
        "a group was told to look at itself")


def test_folding_the_repeat_drops_no_file_no_heading_and_no_command():
    """The other half of R-114, and the half that matters more.

    Shortening may only ever remove a REPEAT. Every file this screen named
    before is still named, every heading is still there saying where its own
    files would go, and the one thing a person can type is still on the screen --
    once is enough, and none of it is the silent omission the standing rule
    forbids.
    """
    run, names = _three_groups_in_one_state()
    printed = _printed(run, names)
    flat = " ".join(printed.split())

    for name in names.values():
        assert name in printed, f"{name} is no longer on the screen"
    for label in COURSES:
        assert (f"Would go into {label}, once something can say what these are "
                "-- 3 files") in flat, (
            f"the heading for {label} lost its own destination or its count")
    assert "--list-residuals" in printed, (
        "the command the shared paragraph carries went with the repeat")


def test_the_count_of_sets_under_a_heading_survives_the_fold():
    """A hold split over the batch ceiling, straddling two headings.

    "N review sets of it have files under this heading" is the sentence that
    stopped the screen claiming a total it could not see, and it is about the
    heading it sits under. A block folds only when it is identical, so the N is
    the same N -- and being the same is not a reason to stop saying it under the
    second heading.
    """
    nodes = [_node("node_0", "Coursework"),
             _node("n_a", "CS3134", parent="node_0"),
             _node("n_b", "ECON2010", parent="node_0"),
             _node("res_0", "Review Later", role="residual")]
    decisions, names, sets = [], {}, []
    for index in range(1, 4):
        members = []
        for offset, node_id in enumerate(("n_a", "n_b") * 4):
            file_id = f"id-{index}-{offset}"
            names[file_id] = f"note-{index}-{offset}.txt"
            members.append(file_id)
            decisions.append(_blocked(file_id=file_id, node_id=node_id))
        sets.append(_set(f"Not yet placed ({index} of 3)", members, REASON))
    flat = " ".join(_printed(
        _run(nodes=nodes, decisions=decisions, sets=sets), names).split())

    assert flat.count("3 review sets of it have files under this heading") == 2, (
        "the second heading lost the count of the sets holding ITS files")
    # And the roll-call and its command are said once, which is the fold.
    assert flat.count("--send-set 'Not yet placed (1 of 3)=Review Later'") == 1, (
        flat)


def test_the_answers_that_reach_a_group_are_never_folded_into_another_group():
    """The negative twin, and `104` R-92 is why it exists.

    A group a printed question WOULD settle names the question and the answers,
    and the whole claim of those lines is that they reach THESE files. Two
    groups whose answer lines render alike are still two claims about two sets
    of files, so this is the one paragraph under a heading that is never
    replaced by a pointer at another heading.
    """
    question = SimpleNamespace(
        question_id="reading.organization:CV1", prompt="What are these?",
        evidence_context="4 files mention it.", unlocks="", will_not_do="",
        scope="reading:CV1",
        options=(SimpleNamespace(option_id="law_practice", label="Law practice",
                                 activates_schema="law"),
                 SimpleNamespace(option_id="teaching", label="Teaching",
                                 activates_schema="teaching")))
    nodes = [_node("node_0", "Coursework"),
             _node("n_a", "CS3134", parent="node_0"),
             _node("n_b", "ECON2010", parent="node_0")]
    decisions, names, reaching = [], {}, {}
    for index, node_id in enumerate(("n_a", "n_b")):
        file_id = f"id-{index}"
        names[file_id] = f"note-{index}.txt"
        reaching[file_id] = (question.question_id,)
        decisions.append(_blocked(file_id=file_id, node_id=node_id))
    out = io.StringIO()
    cli.report(_run(nodes=nodes, decisions=decisions, sets=()), names,
               out=out, questions=(question,), reaching=reaching)
    flat = " ".join(out.getvalue().split())

    assert flat.count("and each of these answers reaches these files") == 2, (
        "one group was told to read another group's answer lines; which files "
        "an --answer reaches is a fact about that group and about no other")
    assert flat.count(
        "--answer reading.organization:CV1=law_practice") == 3, flat


# ======================================================================================
# `104` R-122: a sentence about the PLAN, printed under every group
# ======================================================================================

#: R-114 folded a block only where it was word for word the same, and the block
#: under a hold never is: the `Held for review as "<set>"` line above it names a
#: different set under every heading. So the sentence at the bottom of it -- "This
#: plan has nowhere to put them yet: enable an area with `--residual`" -- was
#: printed once per held group and the 52-file screen stayed at 412 lines.
#:
#: The set name is the GROUP's fact and stays under every group; it is what a
#: person types after `--send-set`. Whether the plan has anywhere to put a held
#: set is one fact about the PLAN, and it is said once.
#:
#: Six reasons and six EXPLANATIONS, because the report keys a group on the
#: decision's explanation: six sets sharing one explanation are six lines under
#: one heading, which is the multi-reason case and not this one.
SIX_REASONS = (
    ("Not yet said what kind of material",
     "nothing has yet said what kind of material these are."),
    ("A model was not allowed to look",
     "the privacy settings on the folder they are in do not let one be asked."),
    ("No folder matched",
     "no folder in this plan matched them well enough to be worth proposing."),
    ("More than one folder fits",
     "more than one folder in this plan matches each of these well enough."),
    ("Two folders fit about equally well",
     "two folders fit each of these about equally well."),
    ("The readings disagree",
     "what this run read about these points at more than one folder."),
)

NOWHERE = "This plan has nowhere to put them yet"
POINTER = "Sent the same way as the first held group above, once an area exists."
OTHER_AREAS = "The other areas are named under the first held group above."


def _six_held_groups(*areas: str):
    """Six holds, six reasons, six headings, and one plan under all of them."""
    nodes = [_node("node_0", "Coursework")]
    nodes += [_node(f"res_{n}", area, role="residual")
              for n, area in enumerate(areas)]
    decisions, sets, names = [], [], {}
    for index, (label, reason) in enumerate(SIX_REASONS):
        members = []
        for offset in range(4):
            file_id = f"id-{index}-{offset}"
            names[file_id] = f"folder-{index}/note-{index}-{offset}.txt"
            members.append(file_id)
            decisions.append(_decision(
                file_id=file_id,
                explanation=f"Nothing was decided about this file: {reason}"))
        sets.append(_set(label, members, reason))
    return _run(nodes=nodes, decisions=decisions, sets=sets), names


def test_the_sentence_about_the_plan_is_printed_once_under_six_held_groups():
    """`104` R-122, stated as the property that fixes it.

    Six headings, six set names, and one sentence about whether the plan has
    anywhere to put any of them. Before this change that sentence was printed six
    times, because the block carrying it differed by the set's name and R-114's
    fold keys on the block being identical.
    """
    run, names = _six_held_groups()
    flat = " ".join(_printed(run, names).split())

    assert flat.count("Held for review as ") == 6, (
        f"six holds produced {flat.count('Held for review as ')} headings; the "
        "set name is each group's own fact and stays under it")
    said = flat.count(NOWHERE)
    assert said == 1, (
        f"the sentence about enabling an area is printed {said} times; it is "
        "one fact about the plan")
    assert flat.count(POINTER) == 5, (
        "the five later holds should each say in one line where that sentence "
        f"is; {flat.count(POINTER)} of them do:\n{flat}")


def test_folding_that_sentence_drops_no_set_name_no_command_and_no_file():
    """The half that matters more, and the same twin R-114 has.

    Shortening may only ever remove a REPEAT. Every set is still named where a
    person reads it, every `--send-set` is still on the screen with the name it
    addresses, and every file this report named before is still named.
    """
    run, names = _six_held_groups("Review Later", "Reading Inbox")
    printed = _printed(run, names)
    flat = " ".join(printed.split())

    for label, _ in SIX_REASONS:
        assert f'Held for review as "{label}"' in flat, (
            f'"{label}" is no longer named on the screen:\n{printed}')
        assert (f"      --send-set "
                f"{shlex.quote(f'{label}=Review Later')}") in printed, (
            f'the one command that files "{label}" went with the repeat:\n'
            + printed)
    for name in names.values():
        assert name in printed, f"{name} is no longer on the screen"


def test_with_a_residual_area_the_other_sentence_is_the_one_said_once():
    """The `--residual` screen, where a DIFFERENT sentence sits in that place.

    Three states and not two. With no area the sentence says how to make one.
    With exactly ONE area every set already carries its own `--send-set` line and
    nothing further is said -- there is no alternative sentence to fold, which is
    asserted here so that nobody adds one by mistake. With two or more, the
    sentence names the areas the commands do not go to, and that is one fact
    about the plan in the same way.
    """
    one = " ".join(_printed(*_six_held_groups("Review Later")).split())
    assert NOWHERE not in one, (
        "an area exists and the screen still says the plan has nowhere to put "
        "them")
    assert "This plan also has" not in one and OTHER_AREAS not in one, (
        "a second sentence appeared where one area means there is nothing "
        f"further to say:\n{one}")

    two = " ".join(_printed(*_six_held_groups("Review Later",
                                              "Reading Inbox")).split())
    assert two.count("This plan also has Reading Inbox.") == 1, (
        f"the areas this plan also has are named "
        f"{two.count('This plan also has Reading Inbox.')} times; that is one "
        "fact about the plan")
    assert two.count(OTHER_AREAS) == 5, (
        f"{two.count(OTHER_AREAS)} of the five later holds say where it is:\n"
        + two)


# ======================================================================================
# `104` R-124: the same reason, twice, in two vocabularies
# ======================================================================================

def test_a_held_group_says_its_reason_once_and_not_in_two_vocabularies():
    """`104` R-124. Measured on a 60-file corpus, a held group read like this:

        Same reason for each: Deciding this file needed a model, and this
        folder's privacy settings only let one that runs on this device be
        asked about it; none is set up. Nothing about it left this device and
        nothing moved; the evidence is retained.
        Held for review as "A model was not allowed to look": deciding these
        needed a model, and the privacy settings on the folder they are in do
        not let one be asked about them. Nothing about them left this device
        and nothing moved; the evidence is retained.

    Eight lines, one fact, and R-115 is why the second one exists at all -- it
    divided the sets by the reason the screen was already printing. The screen
    keeps the reason where it was and the held line keeps the NAME, which is the
    part a person types after `--send-set` and the part the sentence above it
    never carried.
    """
    run, names = _six_held_groups("Review Later")
    printed = _printed(run, names)
    flat = " ".join(printed.split())

    for label, reason in SIX_REASONS:
        assert flat.count(reason) == 1, (
            f"the reason behind {label!r} is on the screen "
            f"{flat.count(reason)} times:\n{printed}")
        # And the name is still there, with the one command that files it.
        assert f'Held for review as "{label}".' in flat, (
            f"the held line for {label!r} is not the name alone:\n{printed}")
        assert (f"      --send-set {shlex.quote(f'{label}=Review Later')}") \
            in printed, printed


def test_a_hold_under_a_group_that_says_no_reason_keeps_its_own():
    """The negative twin, and the reason R-124 is a condition and not a deletion.

    `report` computes a group's reason as `"" if outcome is PLACE else
    explanation`, so a placement waiting on somebody prints no "Same reason for
    each" line at all -- and that is a group that holds review sets. Dropping the
    set's reason there would leave a hold on the screen with nothing anywhere
    saying why, which is the silent omission the standing rule forbids, arrived
    at by way of a shortening.
    """
    run, names = _three_groups_in_one_state()
    flat = " ".join(_printed(run, names).split())

    assert "Same reason for each" not in flat, (
        "the fixture no longer models a group that says no reason of its own, "
        "so this test is no longer testing anything")
    assert flat.count(REASON) == 1, (
        "the only sentence on the screen saying why these are held went with a "
        f"shortening:\n{flat}")


def test_the_count_of_sets_under_a_heading_reads_after_the_name_alone():
    """R-93's sentence, which follows the held line and is not R-124's to move.

    "N review sets of it have files under this heading" is a fact about THIS
    heading and it is still said under it. What changed above it is that the
    line it follows is now a name and a full stop rather than a name, a colon
    and a paragraph.
    """
    nodes = [_node("node_0", "Coursework"),
             _node("res_0", "Review Later", role="residual")]
    decisions, names, sets = [], {}, []
    for index in range(1, 4):
        members = []
        for offset in range(8):
            file_id = f"id-{index}-{offset}"
            names[file_id] = f"note-{index}-{offset}.txt"
            members.append(file_id)
            decisions.append(_decision(
                file_id=file_id, explanation="Nothing was decided: " + REASON))
        sets.append(_set(f"No folder matched ({index} of 3)", members, REASON))
    flat = " ".join(_printed(
        _run(nodes=nodes, decisions=decisions, sets=sets), names).split())

    assert 'Held for review as "No folder matched (1 of 3)". 3 review sets of ' \
           'it have files under this heading' in flat, flat
    assert flat.count(REASON) == 1, flat



# --- `106` Phase 7 §D.3: every leftover set is offered a home, or is a block ------


def test_every_ordinary_review_set_key_has_an_offered_home_or_is_a_block():
    """`00` amendment 13: every leftover set is offered a home. A set that is a
    BLOCK (not classified, no model allowed, not allowed to cross, protected)
    or a QUESTION the report prints (waiting on an answer, a branch whose
    situation is not yet named, a run that stopped short, a model that gave no
    answer this run) is not a leftover no branch can hold and is deliberately
    absent. SABOTAGE: add a key to `REVIEW_SET_ORDER` without a row here and it
    is a set with nowhere."""
    from placement import vocabulary as pv

    blocks = {cli.NOT_YET_CLASSIFIED, cli.NO_MODEL_ALLOWED, cli.NOT_ALLOWED_TO_CROSS,
              cli.PROTECTED_REVIEW_SET, cli.WAITING_ON_AN_ANSWER,
              pv.SITUATION_UNANSWERED, pv.BUDGET_DEFERRED, pv.NO_MODEL_JUDGEMENT}
    for key in cli.REVIEW_SET_ORDER:
        assert key in cli.REVIEW_HOME_FOR_SET or key in blocks, key
    assert not set(cli.REVIEW_HOME_FOR_SET) & blocks
    # The two characteristics amendment 13 names and the product lacked.
    assert cli.UNSUPPORTED_REVIEW_SET in cli.REVIEW_SET_ORDER
    assert cli.DUPLICATES_REVIEW_SET in cli.REVIEW_SET_ORDER



# --- `106` Phase 7 §D.5: the screen offers each set its home, by name and command


def _set_keyed(label, members, reason, *, key, protected=False):
    item = _set(label, members, reason, protected=protected)
    item.set_key = key
    return item


def _residual_node(node_id, label, *, parent):
    node = _node(node_id, label, parent=parent, role="residual")
    node.disposition = "physical-destination"
    return node


def test_a_held_set_is_offered_its_home_and_the_command_that_takes_it():
    """`00` amendment 13: "every one is offered to the person before anything
    moves". SABOTAGE: print `areas[0]` -- every set is offered the same area,
    and the first enabled area is whichever sorted first."""
    screenshots = _set_keyed("Screenshots with no accepted project or event", ("f1",),
                             REASON, key=cli.SCREENSHOT_REVIEW_SET)
    locked = _set_keyed("Unsupported or encrypted", ("f2",), REASON,
                        key=cli.UNSUPPORTED_REVIEW_SET)
    run = _run(
        nodes=(_node("n_98", "98 Review and Unsorted"),
               _residual_node("n_ts", "Temporary Screenshots", parent="n_98"),
               _residual_node("n_ue", "Unsupported or Encrypted", parent="n_98")),
        decisions=(_decision(file_id="f1", explanation=REASON),
                   _decision(file_id="f2", explanation=REASON)),
        sets=(screenshots, locked))
    said = _printed(run, {"f1": "a.png", "f2": "b.zip"})
    assert "Offered home: 98 Review and Unsorted / Temporary Screenshots" in said
    assert "Offered home: 98 Review and Unsorted / Unsupported or Encrypted" in said
    assert "--send-set 'Screenshots with no accepted project or event=Temporary Screenshots'" in said
    assert "--send-set 'Unsupported or encrypted=Unsupported or Encrypted'" in said
    assert "nowhere to put them yet" not in said


def test_a_set_whose_home_is_not_in_the_tree_is_offered_what_exists_and_no_lie():
    """A set whose offered home was not minted (a block, or a tree the person
    trimmed) still gets a command the plan can honour -- the first area -- and
    never an `Offered home` line naming a folder the tree does not hold."""
    held = _set_keyed("Not yet placed", ("f1",), REASON, key=cli.NOT_YET_CLASSIFIED)
    run = _run(
        nodes=(_node("n_98", "98 Review and Unsorted"),
               _residual_node("n_rl", "Review Later", parent="n_98")),
        decisions=(_decision(file_id="f1", explanation=REASON),),
        sets=(held,))
    said = _printed(run, {"f1": "a.png"})
    assert "Offered home:" not in said
    assert "--send-set 'Not yet placed=Review Later'" in said
