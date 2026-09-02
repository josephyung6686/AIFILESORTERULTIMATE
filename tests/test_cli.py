# tests/test_cli.py
"""The command a person actually types.

`--situation` and `--label` are required on a real run and that is deliberate:
nothing upstream can answer them and the command will not guess. But a flag whose
whole purpose is to tell you what to pass to `--situation` cannot itself require
`--situation`, or there is no way in.
"""
from __future__ import annotations

import io
import shlex
import sqlite3
import pathlib
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from tree_design.vocabulary import RESIDUAL_TEMPLATE_NAMES  # noqa: E402
from facts.unresolved import (  # noqa: E402
    BELOW_MARGIN, NO_CANDIDATE_EVIDENCE,
)


def _run(argv):
    out = io.StringIO()
    code = cli.main(argv, out=out)
    return code, out.getvalue()


def test_listing_the_situations_needs_nothing_else():
    """The discovery flag is reachable without the answer it exists to supply.

    `--list-situations` prints what `--situation` accepts. Requiring `--situation`
    to reach it is a closed door: the only way to learn a situation name would be
    to already know one.
    """
    code, printed = _run(["--list-situations"])

    assert code == 0, printed
    lines = [line for line in printed.splitlines() if line.strip()]
    assert lines, "the shipped library carries situations and none were printed"
    # Each situation is now indented under the domain it is filed under, with
    # the folder levels it would build beside it, so the name is the first token
    # of an indented line rather than the whole line.
    names = [line.split()[0] for line in lines if line.startswith("  ")]
    assert "academic.coursework" in names, names[:20]
    # Printed for a human to copy into `--situation`, so no internal prefix.
    assert not [name for name in names if name.startswith("recognition:")]
    # And the thing the listing exists to say. A bare column of 208 names asks a
    # person to already know which one they want in order to find it, which is
    # the closed door this flag was invented to open -- so a name printed with
    # nothing beside it is the regression to catch.
    coursework = next(line for line in lines
                      if line.strip().startswith("academic.coursework"))
    assert coursework.split(maxsplit=1)[1].strip(), coursework
    assert not [line for line in lines
                if line.startswith("  ") and len(line.split()) < 2], (
        "a situation was printed with no indication of what it files")


def test_a_real_run_still_refuses_to_guess_the_situation():
    """The negative twin. Making the discovery flag reachable must not make the
    two required answers optional on a run that actually designs a tree -- that
    is the whole reason they are required."""
    for argv in (["somewhere"],
                 ["somewhere", "--situation", "academic.coursework"],
                 ["somewhere", "--label", "Coursework"]):
        with pytest.raises(SystemExit) as exited:
            cli.main(argv, out=io.StringIO())
        assert exited.value.code == 2, argv


def test_a_file_the_detector_declines_is_not_written_up_as_a_passport():
    """An unreadable scan and a passport are different things and must stay so.

    This deployment once answered the detector's abstention with
    `highly_sensitive_credential_bearing, protected=True`, as a workaround for
    `placement.privacy` refusing the whole corpus run over one unclassified file.
    That refusal is fixed -- P11 reads P7's own `resolve_class(None)` -- so the
    workaround now only collapses the two: every file the detector declined to
    guess about would enter P7's store indistinguishable from a passport, and
    the honest `unreadable_unclassified` path would be unreachable from the CLI.

    `00`: "sensitive personal material is not the same thing as `Numbers.app`."
    """
    # A real P4 observation key: `sha256:` plus 64 hex. The record validates the
    # shape, so a placeholder would fail this test for the wrong reason.
    key = "sha256:" + "ab" * 32

    classify = cli.classifier(lambda conn, f, c: None,
                              now=lambda: "2026-01-01T00:00:00Z")

    class _Conn:
        def execute(self, *_a):
            class _Cur:
                def fetchone(_self):
                    return {"observation_key": key}
            return _Cur()

    record = classify(_Conn(), "file-1", "sha256:abc")
    assert record is None, (
        "the detector declined and the CLI invented a classification for it: "
        f"{record}. An unclassified file must reach P11 unclassified so P7's "
        "own resolve_class(None) decides, not this deployment.")


def test_a_file_the_detector_does_recognise_still_gets_its_candidate():
    """The negative twin. Returning None for everything would pass the test above
    and disable classification entirely."""
    sentinel = object()
    classify = cli.classifier(lambda conn, f, c: sentinel,
                              now=lambda: "2026-01-01T00:00:00Z")
    assert classify(None, "file-1", "sha256:abc") is sentinel


def test_the_help_says_nothing_is_moved(capsys):
    """`00`'s promise, in the first sentence a person reads. This command reads and
    proposes; P12 is what moves files and P12 does not exist, so a help text that
    left this out would be describing a product that does not ship."""
    with pytest.raises(SystemExit):
        cli.main(["--help"], out=io.StringIO())
    assert "Nothing is moved" in capsys.readouterr().out


# ======================================================================================
# The report, read as a person reads it
# ======================================================================================
#
# `report` takes what the run returned and a name for every file, so these build
# both directly. A stub rather than a live corpus because the cases that matter
# here -- forty files of one kind, a protected group among them -- are cases a
# four-file demo folder cannot produce, and the live path is covered end to end by
# `tests/integration/test_production_corpus.py`.

from types import SimpleNamespace  # noqa: E402

ABSTAINED = (
    "This file has not been classified -- nothing has been able to read enough "
    "of it to say what kind of material it is -- so it was not shown to a model "
    "and nothing moved. It is waiting for you to say what it is, not marked "
    "sensitive and not judged on thin evidence.")

UNTOUCHED = ("Nothing inside these was read, indexed, classified or moved, and "
             "none of them is a place anything can be filed.")


def _decision(*, outcome, file_id, explanation="", node_id=None,
              protected=False, marked_state=None,
              review_policy="auto_eligible"):
    """`review_policy` defaults to the CLEARED one, and every caller that means
    something else must say so.

    It is a required field on the real `PlacementDecision` and this double did
    not carry it at all, which is how the report came to key its headline on the
    outcome alone: `place` looked like the whole answer here, so "Ready to file"
    looked like the whole word for it. `place` is P11 saying WHERE; the review
    policy is what says whether anything may be done about it.
    """
    return SimpleNamespace(
        outcome=outcome, explanation=explanation, marked_state=marked_state,
        review_policy=review_policy,
        subject=SimpleNamespace(file_id=file_id, member_file_ids=()),
        destination=SimpleNamespace(node_id=node_id) if node_id else None,
        privacy=SimpleNamespace(protected=protected))


def _node(node_id, label, *, parent=None, accepts=True):
    return SimpleNamespace(node_id=node_id, display_label=label,
                           parent_node_id=parent, accepts_placement=accepts)


def _set(label, members, reason, *, protected=False):
    return SimpleNamespace(label=label, member_file_ids=tuple(members),
                           file_count=len(members), reason_not_placed=reason,
                           protected=protected)


def _area(name, path):
    return SimpleNamespace(display_label=name, label="untouched_protected",
                           path=path)


def _fake_run(*, nodes=(), decisions=(), sets=(), areas=(), destinations=()):
    return SimpleNamespace(
        protected_areas=tuple(areas),
        tree=SimpleNamespace(tree=SimpleNamespace(
            plan_version_id="version_2", nodes=tuple(nodes))),
        destinations=tuple(destinations),
        placement=SimpleNamespace(decisions=tuple(decisions),
                                  residual_sets=tuple(sets)))


def _printed(run, names):
    out = io.StringIO()
    cli.report(run, names, out=out)
    return out.getvalue()


def _coursework(count=4):
    """Four files, one folder, one shared reason -- the demo run's own shape."""
    names = {f"id-{n}": f"Homework {n}.txt" for n in range(count)}
    run = _fake_run(
        nodes=[_node("node_0", "Coursework")], destinations=["node_0"],
        decisions=[_decision(outcome="abstain", file_id=file_id,
                             explanation=ABSTAINED) for file_id in names],
        sets=[_set("Not yet placed", tuple(names),
                   "no destination in this tree matched them well enough to "
                   "decide without asking you")])
    return run, names


def test_the_report_calls_files_by_their_name_and_never_by_a_uuid():
    """A person cannot tell which of their own files `74ce335f-...` is.

    `files.current_path` is in the database and always has been, so the id was
    never the only thing the report could print.
    """
    run, names = _coursework()
    printed = _printed(run, names)

    for name in names.values():
        assert name in printed, printed
    for file_id in names:
        assert file_id not in printed, (
            f"{file_id} reached the report; a person cannot act on an id")


def test_one_reason_shared_by_four_files_is_said_once():
    """The wording is right and stays verbatim; saying it four times is not."""
    run, names = _coursework()
    printed = _printed(run, names)

    assert printed.count("not judged on thin evidence") == 1, printed
    # Grouped, not weakened: the three things it keeps apart are all still there.
    flat = " ".join(printed.split())
    assert ABSTAINED in flat, flat


#: The tests below describe the report AFTER the six hunks in
#: `scratchpad/report/SHOW-PROTECTED-PATCH.txt` are applied to `src/cli.py`,
#: which belongs to the lead and which this agent may not edit. Strict, for the
#: reason this repo already uses strict: eleven sessions share this suite, so a
#: dozen red tests would be a dozen false alarms, while a dozen XPASSes the
#: moment the hunks land is the signal to strip these markers. **Applying the
#: patch means deleting every `PENDING_SHOW_PROTECTED` marker in this file.**
PENDING_SHOW_PROTECTED = (
    "Describes the report after scratchpad/report/SHOW-PROTECTED-PATCH.txt's six "
    "hunks are applied to src/cli.py, which the report agent may not edit. "
    "Verified green against the patched source by scratchpad/report/patch2.py. "
    "Strict, so the suite goes red the day the hunks land and the markers come "
    "off with them. planning/93-PROTECTED-DISCLOSURE-RULING.md.")

@pytest.mark.xfail(strict=True, reason=PENDING_SHOW_PROTECTED)
def test_every_decided_file_is_accounted_for_when_the_list_is_shortened():
    """Forty files of one kind are not forty lines, but they are still forty.

    `src/tree_design/health.py` shortens its warning list the same way. What may
    never happen is a file leaving the report: the count is the whole corpus and
    the remainder says how many were counted rather than listed.
    """
    names = {f"id-{n}": f"note-{n:02d}.txt" for n in range(40)}
    run = _fake_run(
        nodes=[_node("node_0", "Coursework")], destinations=["node_0"],
        decisions=[_decision(outcome="abstain", file_id=file_id,
                             explanation=ABSTAINED) for file_id in names])
    printed = _printed(run, names)

    assert "40 files" in printed, printed
    listed = [name for name in names.values() if name in printed]
    assert len(listed) < 40, "forty names is the list this shortening exists for"
    assert f"and {40 - len(listed)} more" in printed, printed
    # The sentence used to promise "none of them is a protected area, which is
    # never summarised away". Under the owner's 2026-09-02 ruling protected
    # material IS summarised -- behind `--show-protected`, and never silently --
    # so the promise it makes about this list is the one that is still true.
    # Flattened: the report wraps to a terminal's width, and the sentence is the
    # fact rather than the line it happens to land on.
    assert "never silently" in " ".join(printed.split()), printed


@pytest.mark.xfail(strict=True, reason=PENDING_SHOW_PROTECTED)
def test_a_protected_group_is_counted_and_reachable_rather_than_listed():
    """The standing rule, as the owner re-decided it on 2026-09-02.

    THIS TEST USED TO ASSERT THE OPPOSITE, and the reversal is his, recorded in
    `planning/93-PROTECTED-DISCLOSURE-RULING.md`. It read: "a protected group is
    listed in full however long it is". That was decided when the longest such
    list anyone had seen was four names in a demo folder. Measured on a corpus
    the size of a real disk, the full list was 710 filenames -- 73 % of the whole
    report -- and what a person's screen mostly showed was their own payslips,
    bank statements, medical notes and passport scans, by name.

    Shown that number, he chose `00`:201's other half: "a summary such as '11
    protected identity records' may be safe to show, while a visible list of
    passport filenames on a shared screen may not be."

    "Never silently omitted" is unchanged and is what the three assertions below
    hold. The word that carries the whole weight is SILENTLY: the count is always
    on the screen, and the command that prints every name is always printed
    beside it. A summary with no way out of it would be the concealment the rule
    forbids; a summary with the command next to it is the person choosing when
    the names are safe to show. `test_show_protected_lists_every_one` is the
    other half and asserts the expansion is complete rather than the first N.
    """
    names = {f"ord-{n}": f"note-{n:02d}.txt" for n in range(40)}
    names.update({f"prot-{n}": f"secret-{n:02d}.key" for n in range(40)})
    decisions = [_decision(outcome="abstain", file_id=f"ord-{n}",
                           explanation=ABSTAINED) for n in range(40)]
    decisions += [_decision(outcome="mark_state", file_id=f"prot-{n}",
                            marked_state="protected", protected=True,
                            explanation="this is protected material and was "
                                        "marked rather than opened")
                  for n in range(40)]
    run = _fake_run(nodes=[_node("node_0", "Coursework")],
                    destinations=["node_0"], decisions=decisions)
    printed = _printed(run, names)

    # Not named -- that is the change.
    for n in range(40):
        assert f"secret-{n:02d}.key" not in printed, (
            f"secret-{n:02d}.key is printed by default; the owner ruled on "
            "2026-09-02 that a list of protected filenames is summarised unless "
            "it is asked for")
    # COUNTED, always. A person may never have to ask whether something was set
    # aside, and this is the half of the rule that did not change.
    assert "40 protected files" in printed, printed
    assert "none of them opened" in printed, printed
    # And REACHABLE, always. Omitting the command is what would turn a summary
    # into a concealment, so it is printed every time and not only when asked.
    assert "--show-protected" in printed, printed
    ordinary = [name for name in names.values()
                if name.startswith("note-") and name in printed]
    assert len(ordinary) < 40, "the ordinary list should still be shortened"
    assert printed.index("note-00.txt") < printed.index("40 protected files"), (
        "the report leads with protected material; ordinary work comes first so a "
        "shared screen does not open with a passport (`00`:201)")


@pytest.mark.xfail(strict=True, reason=PENDING_SHOW_PROTECTED)
def test_show_protected_lists_every_one():
    """The other half, and the one that keeps the summary honest.

    The expansion is COMPLETE. A `--show-protected` that listed the first ten and
    counted the rest would be the omission the standing rule forbids, wearing the
    fix's clothes -- so this asserts all forty and not "more than ten".
    """
    names = {f"prot-{n}": f"secret-{n:02d}.key" for n in range(40)}
    decisions = [_decision(outcome="mark_state", file_id=f"prot-{n}",
                           marked_state="protected", protected=True,
                           explanation="this is protected material and was "
                                       "marked rather than opened")
                 for n in range(40)]
    run = _fake_run(nodes=[_node("node_0", "Coursework")],
                    destinations=["node_0"], decisions=decisions)
    out = io.StringIO()
    cli.report(run, names, out=out, show_protected=True)
    printed = out.getvalue()

    for n in range(40):
        assert f"secret-{n:02d}.key" in printed, (
            f"--show-protected did not list secret-{n:02d}.key; the expansion "
            "is every one of them, not the first few")
    # And it does not then ALSO tell them to run the command they just ran.
    assert "--show-protected" not in printed, printed


@pytest.mark.xfail(strict=True, reason=PENDING_SHOW_PROTECTED)
def test_the_show_protected_command_the_report_prints_actually_shows_them(tmp_path):
    """`84` §6: what the screen tells a person to type has to be true.

    Four defects in this file were all a screen offering a command that did not
    work -- an unpasteable `--answer`, a `revoke` that needed an invisible id, a
    `--send-set` on a set that would always refuse it, and a `--send-set` broken
    across a line by the text wrapper. This is the gesture that decides whether a
    person can see their own protected files, so a fifth one here does not
    inconvenience them: it hides their passport behind a command that lies.

    The command is taken from the report VERBATIM, tokenised the way a shell
    would, and passed straight back in as arguments.
    """
    corpus = _mixed_sensitivity_corpus(tmp_path)
    argv = [str(corpus), "--situation", "academic.coursework", "--label",
            "Papers", "--user", "jy", "--database", str(tmp_path / "plan.sqlite")]

    first = io.StringIO()
    assert cli.main(argv, out=first) == 0
    summarised = first.getvalue()
    assert "Passport scan.txt" not in summarised, summarised
    assert "--show-protected" in summarised, summarised

    offered = next(line for line in summarised.splitlines()
                   if "--show-protected" in line)
    typed = shell_tokens(offered[offered.index("--show-protected"):])
    assert typed == ["--show-protected"], (
        f"the report offers {offered.strip()!r}, which a shell splits into "
        f"{typed!r}; pasting it would pass stray arguments")

    second = io.StringIO()
    assert cli.main(argv + typed, out=second) == 0
    shown = second.getvalue()
    assert "Passport scan.txt" in shown, (
        "the report told the person to type --show-protected and typing it did "
        f"not show them their own protected file:\n{shown}")
    # The count does not change when the names appear -- one fact, two views.
    assert "protected material" in shown, shown


def test_the_protected_containers_block_survives_the_regrouping():
    """Count, name, path and sentence, all four, unchanged.

    This is the standing rule made visible. Every other part of the report may be
    grouped, renamed or shortened; this one is what the grouping must not reach.

    The block now prints from `_print_protected_areas`, called the moment the scan
    knows the answer, because `report` runs only when the design SUCCEEDS and a
    refused run was dropping the count entirely. All four elements are asserted
    here, where they are produced; that it comes before the rest of the report is
    asserted by `test_a_refused_run_still_says_what_was_marked_and_counted` and by
    ordering in `main`.
    """
    printed = io.StringIO()
    cli._print_protected_areas(
        (_area("Notes.app", "/tmp/demo/Notes.app"),), printed)
    block = printed.getvalue()

    assert "Protected containers: 1 marked, none opened" in block
    assert "Notes.app  (untouched_protected)" in block
    assert "/tmp/demo/Notes.app" in block
    assert UNTOUCHED in block


def test_the_folder_list_is_not_headed_by_the_internal_plan_version():
    """§8.8's plan versions are real and are not the user's vocabulary.

    The identifier still has to be reachable -- a replay asks for it by name --
    so it is a provenance line at the end rather than the heading of the list of
    the user's own folders.
    """
    run, names = _coursework()
    printed = _printed(run, names)
    lines = printed.splitlines()

    heading = next(line for line in lines if "folders" in line)
    assert "version_2" not in heading, heading
    assert "Coursework" in printed
    footer = next(line for line in lines if line.startswith("Plan version:"))
    assert "version_2" in footer
    assert lines.index(footer) > lines.index(heading)


def test_the_review_set_is_not_a_second_count_of_the_same_files():
    """`Files: 4 decided, 0 placed` and `Not yet placed (4 files)` were one fact
    printed twice. The set's own reason is not the same fact and stays."""
    run, names = _coursework()
    printed = _printed(run, names)

    assert printed.count("4 files") == 1, printed
    assert "For review:" not in printed
    assert "no destination in this tree matched" in " ".join(printed.split())
    assert "Not yet placed" in printed


def test_a_review_set_covering_no_decided_file_is_still_printed():
    """Nothing may be dropped to make the output shorter. A set folded into a
    group it does not cover would be a set that vanished."""
    run, names = _coursework()
    run.placement.residual_sets += (
        _set("Left for you", ("id-elsewhere",), "nothing decided about these"),)
    printed = _printed(run, names)

    assert "Left for you" in printed, printed
    assert "nothing decided about these" in " ".join(printed.split())


def test_a_placement_names_the_folder_rather_than_printing_a_dash():
    """A bare `-` reads as a missing value. "Nowhere yet" is a decision."""
    names = {"id-0": "Syllabus.txt"}
    run = _fake_run(
        nodes=[_node("node_0", "Coursework")], destinations=["node_0"],
        decisions=[_decision(outcome="place", file_id="id-0",
                             node_id="node_0", explanation="matched")])
    printed = _printed(run, names)

    assert "Coursework" in printed
    assert not [line for line in printed.splitlines() if line.strip() == "-"]
    assert "Ready to file into Coursework" in printed


def test_file_names_are_read_from_the_database_and_shown_from_the_folder_read():
    """`files.current_path` is the source, and the name is shown relative to the
    folder the person typed -- which is what tells two `notes.txt` apart."""
    import sqlite3

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE files (file_id TEXT, current_path TEXT)")
    conn.executemany("INSERT INTO files VALUES (?, ?)", [
        ("id-0", "/tmp/demo/Syllabus.txt"),
        ("id-1", "/tmp/demo/term one/notes.txt"),
        ("id-2", "/elsewhere/stray.txt")])

    names = cli.file_names(conn, Path("/tmp/demo"))

    assert names["id-0"] == "Syllabus.txt"
    assert names["id-1"] == "term one/notes.txt"
    # Outside the folder read: the full path, never a guess and never dropped.
    assert names["id-2"] == "/elsewhere/stray.txt"


# ======================================================================================
# The one pattern that reads a course code, and what it used to miss
# ======================================================================================


def _identifiers(text):
    """What the deployment's finder claims about a piece of text, as strings."""
    return [text[found.start:found.end]
            for found in cli.find_structured_strings(text)]


def test_a_course_code_printed_with_a_space_is_the_same_identifier():
    """`65` §2.1: the first real run found nothing, and the corpus was right.

    The files said `PHYS 1401`. The pattern wanted `PHYS1401`. No match, no fact,
    no group, no tree -- and `63` §10 ruled that this is a READING failure and is
    fixed by widening what is read, not by asking the person a question: "No
    onboarding answer could have recovered that course code."

    A person writes one course code both ways in one term, so the two spellings
    must arrive as ONE identity or the grouping engine sees two courses.
    """
    assert _identifiers("Homework for PHYS 1401, due Friday") == ["PHYS 1401"]
    assert _identifiers("Homework for PHYS1401, due Friday") == ["PHYS1401"]
    canonical = cli.DIRECT_SLOTS.slots[0].canonical
    assert canonical("PHYS 1401") == canonical("PHYS1401")


def test_widening_the_pattern_did_not_widen_it_to_ordinary_prose():
    """The negative twin, and the reason the pattern is one line and not ten.

    `cli.py` states the posture the narrow pattern was chosen for: "A wider
    pattern would put more of the file's text into P4's observations, and a first
    run on somebody's disk is not the place to widen what gets read." Widening it
    to read `PHYS 1401` must not turn it into a reader of sentences, dates,
    money, or a person's initials followed by a year.
    """
    assert _identifiers("Meeting on 14 March 2026 about the 2026 budget") == []
    assert _identifiers("The total was 1401 dollars") == []
    assert _identifiers("see Appendix A for the 2026 figures") == []
    # Two words before the digits is prose, not an identifier token.
    assert _identifiers("SPRING TERM 1401") == ["TERM 1401"]


# ======================================================================================
# The handling policy: recognition is not classification
# ======================================================================================


def test_every_schema_the_product_recognises_has_a_class_to_be_given():
    """`71` cause B. Recognition worked and classification still failed.

    `SAFETY_DOMAIN_HANDLING` names a class for the four SAFETY schemas and marks
    them protected, which is the job it was written for and it does it correctly.
    It was never a general classification policy, and nothing else was supplied --
    so a coursework file, recognised perfectly from its own words, came back
    `Abstention(reason='unassigned_handling', ... "recognition is not
    classification")` and the run ended with every file unclassified.

    A deployment that recognises 23 schemas and can classify 4 of them is not
    making a privacy decision; it is dropping 19 answers it already computed.
    """
    from facts.domains import SCHEMA_IDS

    policy = cli.HANDLING_POLICY
    missing = sorted(set(SCHEMA_IDS) - set(policy))
    assert missing == [], missing


def test_the_safety_schemas_keep_their_protection_and_the_others_do_not_get_it():
    """The negative twin, and the one that matters.

    Widening the policy must not widen PROTECTION -- that would mark a person's
    coursework as sensitive and refuse to file it, which is the over-protection
    `cli.classifier` already records as a collapse: "an unreadable scan and a
    passport identical in P7's store". The four safety schemas keep exactly the
    handling they had; everything else gets the ordinary class this deployment
    already names for an ordinary file.
    """
    from recognition.vocabulary import SAFETY_DOMAIN_IDS

    policy = cli.HANDLING_POLICY
    for schema_id in SAFETY_DOMAIN_IDS:
        assert policy[schema_id].protected is True, schema_id
    for schema_id in set(policy) - set(SAFETY_DOMAIN_IDS):
        assert policy[schema_id].protected is False, schema_id
        assert policy[schema_id].handling_class == cli.ORDINARY_CLASS, schema_id


def test_a_placement_waiting_on_the_person_does_not_print_the_cleared_word():
    """The three review policies must not share one headline.

    `place` is P11's answer about WHERE the file belongs and is not permission to
    move it. Keyed on the outcome alone, a file nothing had classified printed
    "Ready to file into X" beside files that genuinely were -- eight of ten on
    the four-role persona -- and a person would have believed the product was
    ready to move a passport.
    """
    names = {"id-0": "Passport.txt"}
    run = _fake_run(
        nodes=[_node("node_0", "Coursework")], destinations=["node_0"],
        decisions=[_decision(outcome="place", file_id="id-0", node_id="node_0",
                             review_policy="blocked_pending_user")])
    printed = _printed(run, names)

    assert "Ready to file" not in printed, printed
    # The destination is still named. Not being ready is not a reason to withhold
    # the answer, and `00`'s standing rule is that nothing is silently omitted.
    assert "Coursework" in printed
    assert "Passport.txt" in printed
    assert "0 ready to file" in printed


def test_a_placement_the_person_may_approve_reads_differently_from_both():
    """`review_required` is its own answer -- not cleared, and not blocked."""
    names = {"id-0": "Efiling.txt"}
    run = _fake_run(
        nodes=[_node("node_0", "Coursework")], destinations=["node_0"],
        decisions=[_decision(outcome="place", file_id="id-0", node_id="node_0",
                             review_policy="review_required")])
    printed = _printed(run, names)

    assert "approve" in printed, printed
    assert "Ready to file into" not in printed
    assert "0 ready to file" in printed


# ======================================================================================
# The questions the freeze demands, and who actually answered them
# ======================================================================================


def test_the_report_names_the_decisions_nobody_was_asked_about():
    """`66`'s question registry is not built. What IS built is a freeze that
    REFUSES without five answers -- and a command that makes all five itself.

    `TreeDesignDecisions` requires `choose_option`, `refinement_for`,
    `shared_material`, `scoped_general` and the residual answers, each documented
    as the user's; `validate_for_freeze` refuses any legal destination with no
    refinement disposition. Run non-interactively there is nobody to ask, so
    `cli.py` answers all five -- and said nothing about having done so.

    The frozen tree then records `shallow-by-choice` with the reason "This branch
    holds few enough files that splitting it further would not help you find
    anything", in the user's own voice, on a branch nobody was asked about.
    `shallow-by-choice` LITERALLY MEANS the user chose it. A frozen tree is
    permanent and P13 will show that sentence back to them as their own.

    This does not build the registry. It stops the record being silently false.
    """
    run, names = _coursework()
    printed = _printed(run, names)

    assert "Decisions made for you" in printed, printed
    assert "nobody was at the screen" in " ".join(printed.split()), printed


def test_each_decision_made_for_the_person_says_what_was_taken():
    """A count is not an answer. The person has to be able to disagree with a
    specific choice, which means each one is named with the answer taken."""
    run, names = _coursework()
    printed = " ".join(_printed(run, names).split())

    for fragment in (
            "How deep each folder goes",
            "Where material that belongs to two folders goes",
            "Which nesting to use"):
        assert fragment in printed, f"{fragment!r} missing from:\n{printed}"


def test_the_report_says_the_persons_own_folders_are_in_the_proposal():
    """`00`:100 -- a folder the person made "should be treated as a strong
    expression of user intent" -- reaching the report.

    For most of this command's life the opposite was true and the report said so.
    `_upstream` read P3's directory inventory, `horizontal_candidates` turned each
    folder into a `BranchCandidate`, and the selection filter at `pipeline.py`
    kept only candidates whose `subject_id` appeared in `branch_group_ids`. A
    folder candidate's `subject_id` is a directory path; what `cli.py` passed was
    one synthetic id minted from `--label`. No folder could ever match, so every
    folder card was dropped unread -- measured on a corpus with four levels of a
    person's own structure and on a flat copy of the same ten files, the frozen
    trees were identical.

    What the person is told now is what is now true: their folders are in the
    proposal, and the thing still decided for them is WHICH, not whether.
    """
    run, names = _coursework()
    printed = " ".join(_printed(run, names).split())

    assert "folders you have already made" in printed, printed
    assert "all of them, exactly where they are" in printed, printed
    # The half that is still the person's to decide is still named as such.
    assert "merge two that overlap" in printed, printed


def test_an_adopted_folder_enters_as_the_persons_folder_not_as_a_proposal(tmp_path):
    """The negative twin, and the one that keeps the sentence above honest.

    Saying "your folders are in this proposal" is only true if the nodes are
    `00`:102's `existing` type carrying the real path. A `proposed` node wearing
    the folder's name is the OPPOSITE claim -- an offer to move the files out of
    the folder they are already in and into a new one that happens to share its
    label -- and `00`:100 forbids it in the same breath as it asks for adoption.
    That is why the tempting version of this feature (put the folder paths in
    `branch_group_ids` and change nothing else) was rejected: it would have
    flattened the person's hierarchy in the name of honouring it.

    So this reads the frozen tree rather than the prose, over a real run on a
    real nested corpus: the folders are `existing`, they carry their paths, and
    the child hangs off the parent instead of standing beside it at the root.
    """
    import sqlite3

    corpus = tmp_path / "corpus"
    (corpus / "Uni" / "PHYS1401").mkdir(parents=True)
    for name in ("a.txt", "b.txt"):
        (corpus / "Uni" / "PHYS1401" / name).write_text("PHYS1401\n")
    database = tmp_path / "plan.sqlite"
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=io.StringIO())

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT node_id, node_type, display_label, existing_path, parent_node_id "
        "FROM tree_nodes WHERE node_type = 'existing'")]
    conn.close()

    assert rows, ("no folder of the person's is in any version of the tree; "
                  "every directory the scan read was dropped again")
    assert all(row["existing_path"] for row in rows), (
        "an adopted node with no path is a proposal wearing a folder's name")

    by_path = {row["existing_path"]: row for row in rows}
    child = next((row for path, row in by_path.items()
                  if path.endswith("PHYS1401")), None)
    parent = next((row for path, row in by_path.items()
                   if path.endswith("Uni")), None)
    assert child is not None and parent is not None, sorted(by_path)
    assert child["parent_node_id"] == parent["node_id"], (
        "the person's own nesting was flattened: PHYS1401 was adopted as a "
        "sibling of Uni rather than as its child")


def test_a_file_is_not_offered_a_move_into_a_duplicate_of_its_own_folder(tmp_path):
    """`00`:100 -- the person's folder is "a strong expression of user intent" --
    against the engine's own proposal for the same material.

    Adopting folders created this problem, and it is worth stating plainly
    because it was measured: once `Uni/CHEM1500` was in the tree, the engine's
    `Coursework/CHEM1500` was still there too, both named CHEM1500 on screen, and
    the two tied at every file. §6.10 sent the tie to a model, offline mode
    forbids the call, and SIX files that had been placing fine went back to
    `privacy_blocked` -- the identical failure the ancestor collapse was written
    for, arriving from a different direction.

    The rule that resolves it is the ancestor rule's own: a candidate superseded
    by a MORE SPECIFIC form of itself is not a rival. The person's folder expects
    everything the proposal expects and one thing more (its files agree on the
    term as well as the subject), so the proposal is not a second home -- it is a
    vaguer copy of the home the person already built.
    """
    import sqlite3

    # TWO courses, because one is not a duplicate of anything: V2 skips a level
    # its files do not actually divide, so a single-course corpus never builds
    # the proposed `CHEM1500` this test is about.
    corpus = tmp_path / "corpus"
    for course, names in (("CHEM1500", ("Lab Report.txt", "Syllabus.txt")),
                          ("PHYS1401", ("Problem Set 2.txt", "Lecture Notes.txt"))):
        (corpus / "Uni" / course).mkdir(parents=True)
        for name in names:
            (corpus / "Uni" / course / name).write_text(
                f"{course} {name[:-4]}\nColumbia University, Spring 2026\n")
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=out)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    chosen = [dict(r) for r in conn.execute(
        "SELECT d.subject_ref, d.outcome, n.node_type, n.existing_path "
        "FROM placement_decisions d JOIN tree_nodes n ON n.node_id = d.node_id "
        "WHERE d.node_id IS NOT NULL AND d.superseded_by IS NULL")]
    conn.close()

    assert chosen, (
        "every file abstained; the person's own folder and the engine's "
        f"duplicate of it tied and the tie went nowhere:\n{out.getvalue()}")
    # And what they were placed into is the person's folder, not the copy.
    assert all(row["node_type"] == "existing" for row in chosen), chosen


def test_a_file_staying_in_its_own_folder_is_not_described_as_a_move(tmp_path):
    """Three truths, where the report had words for two.

    "Already in a folder CALLED CHEM1500; the plan would put it in the one it
    proposes" was written when a destination could only ever be a folder the
    engine had invented, so matching NAMES was the strongest thing that could be
    said. Once the person's own folder is adopted and wins the placement, that
    sentence describes a move out of a folder and back into it, which is not what
    the plan says and not something anybody would want to read.

    The destination now carries `existing_path`, so the report can say the true
    thing: this is that folder. The middle case is still real -- a file in
    `Downloads/PHYS1401` placed into a proposed `Coursework/PHYS1401` genuinely
    is a move between two folders of one name -- and keeps its own sentence.
    """
    corpus = tmp_path / "corpus"
    for course, names in (("CHEM1500", ("Lab Report.txt", "Syllabus.txt")),
                          ("PHYS1401", ("Problem Set 2.txt", "Lecture Notes.txt"))):
        (corpus / "Uni" / course).mkdir(parents=True)
        for name in names:
            (corpus / "Uni" / course / name).write_text(
                f"{course} {name[:-4]}\nColumbia University, Spring 2026\n")
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=out)
    printed = " ".join(out.getvalue().split())

    assert "would put it in the one it proposes" not in printed, printed
    assert "Already in CHEM1500" in printed or "Already in PHYS1401" in printed, (
        printed)


# ======================================================================================
# Who the record says decided
# ======================================================================================


def test_the_group_record_does_not_claim_a_person_chose_its_file_set(tmp_path):
    """Nobody saw which files went into that group, so nothing may say they did.

    `--label` and `--situation` really are the person's -- they are required flags
    and the command refuses to guess them. The FILE SET is not: the non-interactive
    review keeps every group P9 proposed and shows nobody. Writing `decided_by =
    'user'` and "the user confirmed these files are 'Coursework'" makes a record
    that a later part, a replay, or P13 will read as a human judgement.

    `DECIDED_BY` and `CREATED_BY` already carry `rules`, which is what actually
    decided, so the honest value was in the vocabulary at every one of these sites.
    """
    import sqlite3

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for name in ("a.txt", "b.txt"):
        (corpus / name).write_text("PHYS1401\n")
    database = tmp_path / "plan.sqlite"
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=io.StringIO())

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    groups = [dict(r) for r in conn.execute(
        "SELECT display_label, created_by, proposed_basis, supersede_reason "
        "FROM groups")]
    accept = [dict(r) for r in conn.execute(
        "SELECT decided_by FROM group_acceptance")]
    conn.close()

    reviewed = [g for g in groups if g["display_label"] == "Coursework"]
    assert reviewed, groups
    for group in reviewed:
        assert group["created_by"] != "user", (
            "the record says a person created this group's file set; nobody saw it")
        # The claim that must not survive is about the FILE SET. Mentioning the
        # user is not itself the defect -- the label really is theirs, and a
        # record scrubbed of them would lose the one thing they did supply.
        basis = group["proposed_basis"] or ""
        assert "the user confirmed these files" not in basis, basis
        assert "nobody was shown which files" in basis, (
            f"the basis does not admit that nobody saw the file set: {basis!r}")
        assert "the user named and categorised" not in (
            group["supersede_reason"] or ""), group["supersede_reason"]
    assert accept, "no acceptance was recorded at all"
    for row in accept:
        assert row["decided_by"] != "user", (
            "the acceptance says a person decided it; nobody was asked")


def test_the_label_is_still_recorded_as_the_persons_because_it_is(tmp_path):
    """The negative twin, and the reason this is not a blanket rename.

    `--label` IS the user's answer -- required, refused rather than guessed. A fix
    that scrubbed every trace of the person from the record would lose the one
    thing they really did supply, which is worse than the overclaim it replaces.
    """
    import sqlite3

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for name in ("a.txt", "b.txt"):
        (corpus / name).write_text("PHYS1401\n")
    database = tmp_path / "plan.sqlite"
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=io.StringIO())

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT display_label, label_source FROM groups "
        "WHERE display_label = 'Coursework'")]
    edited = [dict(r) for r in conn.execute(
        "SELECT user_edited_label FROM group_acceptance")]
    conn.close()

    assert rows, "the label the person typed is not on any group"
    assert all(r["label_source"] == "user-edited" for r in rows), rows
    assert any(r["user_edited_label"] == "Coursework" for r in edited), edited


def test_the_tree_record_does_not_claim_a_person_saw_a_canvas(tmp_path):
    """The same overclaim as the group record above, one part further downstream.

    P13 -- the review and approval surface -- is unbuilt, so this command draws
    no canvas and shows no plan-version list. It accepted every branch by rule
    and froze the version by rule. Written under `canvas`, §8.8's audit log said
    "The user accepted ... on the canvas surface" and "The user adopted plan
    version ...", under the login `--user` supplied, about a screen that does not
    exist.

    `SURFACE_UNATTENDED` is the third review surface, added with the owner's
    approval because a closed set that cannot say "nobody was shown anything"
    forces the log to say something untrue. What must NOT change is that the
    events survive: a branch was accepted and a version was frozen, and a log
    that lost those rows would be worse than one that overstated them.
    """
    import sqlite3

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for name in ("a.txt", "b.txt"):
        (corpus / name).write_text("PHYS1401\n")
    database = tmp_path / "plan.sqlite"
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=io.StringIO())

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    edits = [r["explanation"] for r in conn.execute(
        "SELECT explanation FROM events WHERE event_type = 'destination-tree edit'")]
    conn.close()

    assert edits, "the run recorded no tree edit at all"
    sentences = [e.splitlines()[0] for e in edits]
    for sentence in sentences:
        assert "surface" not in sentence, sentence
        assert not sentence.startswith("The user"), sentence
    # The two things that did happen are still on the record, with their detail.
    assert any("mandatory-review" in s for s in sentences), sentences
    assert any("adopted plan version" in s and "node(s)" in s
               for s in sentences), sentences


def test_a_passport_number_never_becomes_a_folder_name(tmp_path):
    """§5.11's V5, with the input it needs. A folder name is public.

    A folder name is visible in the filesystem and in every prompt that names a
    destination, so naming one after a passport number publishes the passport
    number. `X12345678` was a proposed folder on the litigator's corpus and on
    the four-role corpus.

    V5's own docstring settles the shape of the test: it asks about the VALUE
    STRING, not about the files under it -- "a university's name is not protected
    material; the passport is". So a value is suppressed only when EVERY file it
    came from carries safety-domain evidence. A course code shared with ordinary
    files stays a folder.

    The file is NOT classified and this does not classify it: `never_alone` still
    holds and the readings are still tied. Corroboration governs what the product
    CLAIMS; precaution governs what it EXPOSES.
    """
    import sqlite3

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    # The litigator's real corpus shape: several ordinary documents sharing one
    # matter number, and one passport carrying its own. Two values, so the level
    # really forms -- a one-value level is refused as a "meaningless one-child
    # level" (`00`:97) and would make this test pass for the wrong reason.
    (corpus / "Client Passport.txt").write_text(
        "Passport\n\nPassport number X12345678. Client identity document.\n")
    (corpus / "Motion.txt").write_text(
        "Motion to Compel\n\nIn re CV20261234. Plaintiff moves to compel "
        "discovery responses.\n")
    (corpus / "Privilege Log.txt").write_text(
        "Privilege Log\n\nPrivilege log for CV20261234.\n")
    (corpus / "Deposition.txt").write_text(
        "Deposition Transcript\n\nDeposition of the witness in CV20261234.\n")
    database = tmp_path / "plan.sqlite"

    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Matters", "--user", "jy",
              "--database", str(database)], out=out)
    printed = out.getvalue()

    conn = sqlite3.connect(database)
    labels = {r[0] for r in conn.execute("SELECT display_label FROM tree_nodes")}
    conn.close()

    assert "X12345678" not in labels, (
        f"a passport number is a proposed folder: {sorted(labels)}")
    # In the FOLDER LIST specifically. P15 may name the value when it asks the
    # person which of their own files is meant -- that is a question on their own
    # screen about their own document, and `66` §4 requires protected material to
    # be "present, not silently absent". What must never happen is the value
    # becoming a destination: a folder name is written to the filesystem and
    # travels in every prompt that names a place to put something.
    folders = printed.split("Folders in this plan:", 1)[1].split("Files:", 1)[0]
    assert "X12345678" not in folders, (
        f"a passport number is printed as a destination:\n{folders}")
    assert "CV20261234" in labels, (
        "the matter number was suppressed too, so this test would pass on a "
        f"tree that simply has no folders: {sorted(labels)}")


def test_a_value_shared_with_ordinary_files_is_still_allowed_to_name_a_folder(
        tmp_path):
    """The negative twin, and the failure V5's docstring records by name.

    V5 "used to read `handling_classes_by_value`, the union of every member
    file's class, which meant one passport scan under `Columbia` gave the string
    'Columbia' a protected class and V5 refused the branch. A university's name
    is not protected material; the passport is. The user lost the organisation
    and kept none of the protection."

    A rule that suppressed any value appearing in ANY safety-touched file would
    walk straight back into that. `CV20261234` above appears in two ordinary
    legal documents as well, so it stays.
    """
    import sqlite3

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    # Same corpus, one change: the passport names the SAME matter number the
    # ordinary documents do. A second value keeps the level alive.
    (corpus / "Client Passport.txt").write_text(
        "Passport\n\nPassport number CV20261234. Client identity document.\n")
    (corpus / "Motion.txt").write_text(
        "Motion to Compel\n\nIn re CV20261234. Plaintiff moves to compel "
        "discovery responses.\n")
    (corpus / "Privilege Log.txt").write_text(
        "Privilege Log\n\nPrivilege log for CV20261234.\n")
    (corpus / "Filing.txt").write_text(
        "Efiling Confirmation\n\nCourt e-filing receipt for AB99887.\n")
    database = tmp_path / "plan.sqlite"

    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Matters", "--user", "jy",
              "--database", str(database)], out=io.StringIO())

    conn = sqlite3.connect(database)
    labels = {r[0] for r in conn.execute("SELECT display_label FROM tree_nodes")}
    conn.close()

    assert "CV20261234" in labels, (
        "a matter number shared with two ordinary documents was suppressed "
        f"because one file also mentioned a passport: {sorted(labels)}")


# ======================================================================================
# P15 -- the question loop, closed
# ======================================================================================


def _ambiguous_corpus(tmp_path):
    """Files whose own words support two readings equally.

    'transcript' is authored by seven schemas and 'witness' by several, so a
    deposition is exactly the case `00` requires abstention on -- and exactly the
    case `66` §13 says a person can settle and evidence cannot.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "Deposition.txt").write_text(
        "Deposition Transcript\n\nDeposition of the witness in CV20261234.\n")
    (corpus / "Second Deposition.txt").write_text(
        "Deposition Transcript\n\nSecond transcript of a witness, CV20261234.\n")
    (corpus / "Notes.txt").write_text(
        "Lecture Notes\n\nLecture notes for PHYS1401.\n")
    return corpus


def test_the_run_asks_a_question_when_a_decision_is_actually_blocked(tmp_path):
    """`66` §12: ask "only when a specific decision is blocked", and §14: "narrow,
    evidence-linked", naming "the visible context and the precise consequence"."""
    corpus = _ambiguous_corpus(tmp_path)
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)
    printed = out.getvalue()

    assert "CV20261234" in printed
    joined = " ".join(printed.split())
    assert "readings equally" in joined, printed
    # §12: name the decision it unlocks, and what it will not do.
    assert "will not move, rename or delete anything" in joined, printed
    # §14: the answer must be givable, and the report must say how.
    assert "--answer" in printed, printed


def test_a_run_with_nothing_blocked_asks_nothing(tmp_path):
    """The twin that keeps §12's promise. A product that always finds something to
    ask is the questionnaire, whatever it calls itself.

    Scoped to the BLOCKING section since the nesting offer shipped, and the
    distinction is the point rather than a concession. A blocked reading stops
    something: until it is answered those files are classified as nothing and go
    nowhere. A nesting offer stops nothing -- the branch has a shape either way,
    and the question is `00`:78's "which of these shapes do you want", which the
    design assigns to the user and not to the engine. What §12 forbids is
    manufacturing questions ABOUT THE PERSON; offering a choice the design already
    says is theirs is the opposite of that, and is why the two print apart.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "a.txt").write_text("Lecture Notes\n\nLecture notes for PHYS1401.\n")
    (corpus / "b.txt").write_text("Lecture Notes\n\nMore lecture notes, PHYS2801.\n")
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)

    assert "Questions only you can answer" not in out.getvalue(), out.getvalue()


def test_an_answer_is_remembered_and_changes_the_next_run(tmp_path):
    """THE LOOP. This is the property `66` §12 asks for and the product had none
    of: an answer that outlives the run that asked for it.

    Run one asks. The person answers. Run two does not ask again, and the file it
    could not read now reads as what they said it was.
    """
    import sqlite3

    corpus = _ambiguous_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    first = io.StringIO()
    cli.main(argv, out=first)
    assert "--answer" in first.getvalue()

    answered = io.StringIO()
    code = cli.main(argv + ["--answer", "reading.organization:CV20261234=law_practice"],
                    out=answered)
    assert code == 0, answered.getvalue()

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT question_id, option_id, state FROM structural_answers")]
    classes = [dict(r) for r in conn.execute(
        "SELECT handling_class FROM classifications")]
    conn.close()

    assert rows and rows[0]["option_id"] == "law_practice", rows
    assert rows[0]["state"] == "confirmed"
    assert classes, (
        "the person said what these files are and nothing was classified; the "
        "answer was stored and never consumed")
    # And the question does not come back.
    assert ("Questions only you can answer" not in answered.getvalue()), (
        answered.getvalue())


def test_an_answer_naming_an_unknown_question_is_refused_rather_than_ignored(tmp_path):
    """A typo must not read as an answer, and must not vanish silently either --
    the person believes they have told the product something."""
    corpus = _ambiguous_corpus(tmp_path)
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite"),
                     "--answer", "reading.organization:NOPE=law_practice"], out=out)

    assert code != 0
    assert "NOPE" in out.getvalue()


def test_skipping_is_an_answer_and_the_question_does_not_come_back(tmp_path):
    """§14: "skip for now" is FIRST-CLASS. A skip that re-asked next run would be
    the pressure §12 forbids, dressed as helpfulness."""
    corpus = _ambiguous_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    cli.main(argv, out=io.StringIO())
    after = io.StringIO()
    cli.main(argv + ["--answer", "reading.organization:CV20261234=skip"], out=after)

    # Named exactly, because the run also OFFERS a nesting for the branch and an
    # offer is not a re-ask: the promise here is that THIS question, once
    # declined, does not come back.
    #
    # The promise is about being ASKED, so it is asserted against the prompt and
    # the options rather than against the bare id. The report also carries a
    # one-line offer to revoke, which exists because `revoke` needs an id that
    # was otherwise printed nowhere; that line reproduces nothing of the
    # question and re-asks nothing. Its own guard is
    # `test_the_reminder_line_is_not_the_question_asked_again`.
    printed = after.getvalue()
    assert "What kind of material is CV20261234?" not in printed, printed
    offered = [line for line in printed.splitlines()
               if "--answer reading.organization:CV20261234=" in line]
    assert all(line.strip().endswith("Ask me this again") for line in offered), (
        printed)


def test_a_file_already_in_a_folder_of_that_name_is_not_announced_as_a_move():
    """`00`:100: "Existing folders must not be automatically flattened, renamed, or
    reorganized simply because a template would produce a different structure."

    A person with `Uni/PHYS1401/lab-report.txt` runs this and is told "Ready to
    file into PHYS1401". The file is ALREADY in a folder of that name. Proposing
    to move it into a new one is the flattening `00`:100 forbids, and saying
    "ready to file" about it is the report describing a no-op as an action.

    This does not decide the owner's question -- whether an existing folder or a
    proposed branch wins is `00`:100's six gestures and it states no default. It
    reports a FACT the run already has: the file's immediate parent is named what
    the destination is named. No new state, no new vocabulary, no decision
    changed; the placement is what it was, described truthfully.
    """
    names = {"id-0": "Uni/PHYS1401/lab-report.txt"}
    run = _fake_run(
        nodes=[_node("node_0", "PHYS1401")], destinations=["node_0"],
        decisions=[_decision(outcome="place", file_id="id-0", node_id="node_0")])
    printed = _printed(run, names)

    assert "Ready to file into PHYS1401" not in printed, printed
    assert "already" in printed.lower(), printed
    assert "PHYS1401" in printed


def test_a_file_somewhere_else_entirely_is_still_announced_as_a_move():
    """The negative twin. A file that really would move must still say so, or the
    fix hides every genuine proposal behind a reassurance."""
    names = {"id-0": "Downloads/lab-report.txt"}
    run = _fake_run(
        nodes=[_node("node_0", "PHYS1401")], destinations=["node_0"],
        decisions=[_decision(outcome="place", file_id="id-0", node_id="node_0")])
    printed = _printed(run, names)

    assert "Ready to file into PHYS1401" in printed, printed


def test_a_file_loose_in_the_scanned_folder_is_a_move_not_a_no_op():
    """The other twin, and the one a naive implementation gets wrong: a file with
    no parent folder at all shares no name with anything and is a real move."""
    names = {"id-0": "lab-report.txt"}
    run = _fake_run(
        nodes=[_node("node_0", "PHYS1401")], destinations=["node_0"],
        decisions=[_decision(outcome="place", file_id="id-0", node_id="node_0")])
    printed = _printed(run, names)

    assert "Ready to file into PHYS1401" in printed, printed


def test_the_tree_shows_which_folders_are_already_yours(tmp_path):
    """`00`:100 in the last place it can still be lost -- on the screen.

    "The canvas should make the difference between existing structure and
    proposed structure visually clear, for example by showing existing nodes in
    one style and uncommitted suggestions in another." A terminal has no styles,
    so it says so in words; what it must not do is print the person's four
    folders and the engine's three under one heading reading "Proposed folders",
    which is a count of seven proposals where three were proposed and four are
    already on their disk.
    """
    corpus = tmp_path / "corpus"
    for course, names in (("CHEM1500", ("Lab Report.txt", "Syllabus.txt")),
                          ("PHYS1401", ("Problem Set 2.txt", "Lecture Notes.txt"))):
        (corpus / "Uni" / course).mkdir(parents=True)
        for name in names:
            (corpus / "Uni" / course / name).write_text(
                f"{course} {name[:-4]}\nColumbia University, Spring 2026\n")
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)
    printed = out.getvalue()

    assert "yours already" in printed, printed
    # The headline counts the two kinds separately rather than calling them all
    # proposals.
    assert "Folders in this plan:" in printed, printed


def test_a_file_whose_deterministic_pass_settled_nothing_gets_the_second_look():
    """R3. §3.6's usability verdict answered `True` unconditionally, so targeted
    OCR was unreachable and a scanned page with a broken text layer never got its
    second pass.

    The threshold itself is Deferred by name -- "the `no_usable_facts` threshold,
    M11, P5 OQ1" -- and this does not choose one. It answers the one case that
    needs no threshold to decide: a pass that produced NO fact and left NOTHING
    unresolved settled nothing at all, and "usable" is not a defensible word for
    it. Every other corpus keeps the deferred answer.

    The twin is what keeps it safe. A file that yielded even one fact is usable,
    so no text-bearing document is ever sent through Apple Vision on the strength
    of a number nobody authored -- which is the failure the unconditional `True`
    was protecting against, and it is still protected against.
    """
    assert cli._usable((), ()) is False
    assert cli._usable(({"field_key": "subject"},), ()) is True
    # An attempted field that ended in a recorded refusal is evidence too: the
    # pass ran and reached a conclusion, so it is not the empty case. A row
    # carries its reason -- `write_unresolved` checks it against
    # `UNRESOLVED_REASONS` and the table has the column -- and the reason is the
    # whole difference between the next two lines.
    assert cli._usable((), ({"field_key": "subject",
                             "reason": BELOW_MARGIN},)) is True
    # `no_candidate_evidence` is the one reason that does NOT count, and this is
    # the case the product exists for: a scanned page whose text layer is broken
    # yields no candidate for any field, so every attempted field ends in this
    # row. Counting them would call that file "usable" and it would never be
    # offered the second look -- the exact failure the unconditional `True` had.
    # It would also answer the question with itself: the reason IS "nothing was
    # there to read", which is what is being asked.
    assert cli._usable((), ({"field_key": "subject",
                             "reason": NO_CANDIDATE_EVIDENCE},)) is False
    # And a page that yielded nothing on one field but refused on another having
    # looked is still usable -- one real refusal is enough.
    assert cli._usable((), ({"field_key": "subject",
                             "reason": NO_CANDIDATE_EVIDENCE},
                            {"field_key": "term",
                             "reason": BELOW_MARGIN},)) is True


def _two_shape_corpus(tmp_path):
    """A branch whose facts support more than one nesting -- which is the only
    condition under which §12 permits the question to be asked at all."""
    corpus = tmp_path / "corpus"
    for course, names in (("CHEM1500", ("Lab Report.txt", "Syllabus.txt")),
                          ("PHYS1401", ("Problem Set 2.txt", "Lecture Notes.txt"))):
        (corpus / "Uni" / course).mkdir(parents=True)
        for name in names:
            (corpus / "Uni" / course / name).write_text(
                f"{course} {name[:-4]}\nColumbia University, Spring 2026\n")
    return corpus


def test_the_run_asks_how_the_branch_should_be_organised(tmp_path):
    """`00`:78 and :99 -- the engine proposes shapes, shows what each would
    create, and THE PERSON PICKS. §5.5 built those options all along and the
    command took `options[0]`, disclosing that it had: "a person looking at the
    counts and warnings would reasonably pick another."

    That disclosure was honest and is not the same as asking. This asks, during
    the freeze, with the counts in the option so the person is not choosing blind.
    """
    corpus = _two_shape_corpus(tmp_path)
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)
    printed = " ".join(out.getvalue().split())

    assert "How should Coursework be organised?" in printed, printed
    assert "--answer branch:Coursework=" in printed, printed
    # The counts are IN the option, which is what makes the question better than
    # the default it replaced rather than merely different from it.
    assert "CHEM1500 (2)" in printed, printed


def test_answering_it_changes_the_tree_on_the_same_run(tmp_path):
    """The half that makes it a mechanism rather than a questionnaire.

    `keep-as-it-is` is `00`:99's "keep this branch as it is", which §5.5 offers
    beside every composition and calls an answer rather than a fallback. Taking it
    must actually leave the branch unsplit -- and `apply_answers` runs before the
    run reads anything, so it takes effect immediately rather than next time.
    """
    corpus = _two_shape_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database)], out=io.StringIO())

    after = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(database),
              "--answer", "branch:Coursework=keep-as-it-is"], out=after)
    printed = after.getvalue()

    folders = printed.split("Folders in this plan:", 1)[1].split("Files:", 1)[0]
    assert "Coursework" in folders
    # The branch is not split, so neither course is a child of it. Both still
    # exist as the person's OWN folders, which is a different thing.
    proposed = [line for line in folders.splitlines()
                if line.strip() and "[yours already]" not in line]
    assert not any("CHEM1500" in line for line in proposed), folders


def test_an_unanswered_question_leaves_the_tree_exactly_as_it_was(tmp_path):
    """The twin, and the reason asking is safe to do here at all.

    If being asked changed the outcome, every first run would get a worse tree
    until somebody answered. The default is taken exactly as before, so the
    question costs the person nothing and the run they already had is the run
    they still get.
    """
    corpus = _two_shape_corpus(tmp_path)
    asked = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Coursework", "--user", "jy",
              "--database", str(tmp_path / "a.sqlite")], out=asked)

    folders = asked.getvalue().split(
        "Folders in this plan:", 1)[1].split("Files:", 1)[0]
    assert "CHEM1500" in folders and "PHYS1401" in folders, folders


def test_a_skipped_nesting_offer_does_not_come_back_either(tmp_path):
    """§14's "skip for now" is first-class for every question, not only the ones
    that block. An offer that reappeared each run after being declined would be
    the pressure §12 forbids, and would be worse than not offering at all."""
    corpus = _two_shape_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    cli.main(argv, out=io.StringIO())
    after = io.StringIO()
    cli.main(argv + ["--answer", "branch:Coursework=skip"], out=after)

    assert "How should Coursework be organised?" not in after.getvalue(), (
        after.getvalue())


def test_a_person_can_change_their_mind(tmp_path):
    """§12: an answer must be "edited, revoked, or re-run".

    `live_answer` has honoured revocation since P15 shipped -- a revoked answer
    reopens its question -- and there was no way to say it. `--answer` understood
    confirm and skip, so a person who chose wrongly could re-confirm a different
    option but could not withdraw the answer and be asked again.

    That gap matters most for the answer that is hardest to get right the first
    time: the one taken before the person had seen what it would do.
    """
    corpus = _two_shape_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    cli.main(argv, out=io.StringIO())
    kept = io.StringIO()
    cli.main(argv + ["--answer", "branch:Coursework=keep-as-it-is"], out=kept)
    assert "How should Coursework be organised?" not in kept.getvalue()

    reopened = io.StringIO()
    cli.main(argv + ["--answer", "branch:Coursework=revoke"], out=reopened)

    # The question comes back, and the tree is the one the engine proposes again.
    assert "How should Coursework be organised?" in reopened.getvalue(), (
        reopened.getvalue())
    folders = reopened.getvalue().split(
        "Folders in this plan:", 1)[1].split("Files:", 1)[0]
    assert "CHEM1500" in folders, folders


@pytest.mark.xfail(strict=True, reason=PENDING_SHOW_PROTECTED)
def test_a_protected_files_own_words_are_never_printed_back_to_the_person(tmp_path):
    """§8.4 and `00`:201 -- the whole point of marking a file protected.

    Found by running the product over a passport: its number, its date of birth and
    its expiry became `subject` values, and the date of birth was printed on the
    terminal as a question the person was invited to answer --

        What kind of material is JUN1998?
          --answer reading.organization:JUN1998=identity

    -- which also offers to make it a folder dimension. The file WAS correctly
    classified protected; nothing consulted that before asking.

    `_raise_questions` builds `subject_of` from every active `subject` fact with no
    reference to `classifications`, and by the time it runs the classification is
    already settled, so the guard costs nothing and needs no reordering. The tree
    side was already covered -- `materialise_branch` isolates protected files -- but
    isolation stops a value becoming a FOLDER, not a value being read aloud.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "Passport.txt").write_text(
        "Passport number X12345678. Date of birth JUN1998.\n", encoding="utf-8")
    (corpus / "Syllabus.txt").write_text(
        "PHYS1401 syllabus. Lecture notes for the semester.\n", encoding="utf-8")

    argv = [str(corpus), "--situation", "academic.coursework", "--label",
            "Coursework", "--user", "jy",
            "--database", str(tmp_path / "plan.sqlite")]
    out = io.StringIO()
    cli.main(argv, out=out)
    report = out.getvalue()
    # BOTH VIEWS, because a passport's own words must not appear in either. The
    # owner's 2026-09-02 ruling summarises protected FILENAMES by default, and
    # `--show-protected` prints them -- what it may never do is start printing
    # what is INSIDE one, which is a different thing and is what this guards.
    shown = io.StringIO()
    cli.main(argv + ["--show-protected"], out=shown)
    expanded = shown.getvalue()

    for view, text in (("default", report), ("--show-protected", expanded)):
        assert "X12345678" not in text, (
            f"a passport number was printed to the screen in the {view} view; "
            "it is protected material")
        assert "JUN1998" not in text, (
            "a date of birth read out of a protected file was printed to the "
            f"screen in the {view} view and offered as a folder dimension")
    # MARKED AND COUNTED, NEVER SILENTLY OMITTED -- the other half of the rule, and
    # the one a careless version of this guard would break. The file is still
    # decided and still carries its own reason; its NAME is behind the command the
    # default view prints, and only its CONTENTS are absent from both.
    assert "--show-protected" in report, report
    assert "Passport.txt" in expanded, (
        "the protected file vanished from the report; it must be marked and "
        "counted, not hidden")
    assert "protected material" in report, report
    assert "Syllabus.txt" in report, "the ordinary file stopped being reported"


def test_groups_of_different_categories_get_different_top_level_branches(tmp_path):
    """§5's first entry: a legal matter filed under "Coursework".

    `74` A5 states this task as "four accepted groups produce four branches under
    the named top level" -- and that is ALREADY TRUE, so shipping it as written
    would close the task and fix nothing. Measured on this corpus: `Coursework/`
    already holds `CV20261234`, `PHYS1401` and `Q3 2025` as three branches. The
    vertical pass rebuilds them from the subject dimension, exactly as
    `review_and_accept`'s docstring says.

    The defect is one level up. `review_and_accept` merges every group P9 produced
    into ONE accepted group stamped with the single `--situation`, so four
    CATEGORIES become one branch. P9 named them correctly and unaided; the merge
    discards the naming. The function says so itself:

        "What `--label` and `--situation` also do, and should not, is flatten four
        categories into one -- a legal matter number filed under 'Coursework'."

    So the unit is the CATEGORY, not the group. Accepting each GROUP separately is
    a different change and a worse one -- the same docstring records that it "would
    put four course codes at the ROOT and destroy the nesting".

    `xfail(strict=True)`: it states the gap today and turns the suite RED the day a
    second top-level branch appears, which forces the marker off.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "Syllabus.txt").write_text(
        "PHYS1401 syllabus. Lecture notes for the semester.\n", encoding="utf-8")
    (corpus / "Claim.txt").write_text(
        "CV20261234 claim form. Particulars of claim and defence bundle.\n",
        encoding="utf-8")
    (corpus / "Review.txt").write_text(
        "Q3 2025 performance review. Objectives and appraisal for the quarter.\n",
        encoding="utf-8")

    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework", "--label",
              "Coursework", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)
    folders = out.getvalue().split("Folders in this plan:", 1)[1].split("Files:", 1)[0]
    roots = [line for line in folders.splitlines()
             if line.startswith("  ") and not line.startswith("    ")]

    assert len(roots) > 1, (
        "every category was filed under one top-level branch; the person's legal "
        f"matter is inside a folder called Coursework. Roots: {roots}")


test_groups_of_different_categories_get_different_top_level_branches = (
    pytest.mark.xfail(
        strict=True,
        reason="`review_and_accept` merges every P9 group into one accepted group "
               "under a single `--label`/`--situation`, so a legal matter, a course "
               "and a performance review share one branch. XPASSes and fails the "
               "suite the moment per-category acceptance lands.",
    )(test_groups_of_different_categories_get_different_top_level_branches))


def test_a_refused_run_still_says_what_was_marked_and_counted(tmp_path):
    """The standing rule has no success-path exception.

    Protected containers are marked, counted, never opened AND NEVER SILENTLY
    OMITTED. The count was printed only by `report`, which `main` reaches only when
    the run succeeds; both refusal paths return before it. So a run that marked a
    protected container and then refused told the person nothing about it -- the
    verdict was in the database and absent from the screen, which is the omission
    the rule names.

    A corpus of one `.app` bundle and one contentless file refuses with
    `NothingToDesign`, and is the smallest case that has something to omit.
    """
    corpus = tmp_path / "corpus"
    (corpus / "Notes.app").mkdir(parents=True)
    (corpus / "Notes.app" / "index.txt").write_text("hello\n", encoding="utf-8")
    (corpus / "plain.txt").write_text("nothing here\n", encoding="utf-8")

    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework", "--label",
                     "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite")], out=out)
    printed = out.getvalue()

    assert code != 0 and "No plan was made" in printed, printed
    assert "Protected containers: 1 marked, none opened" in printed, (
        "the run marked a protected container and refused without ever saying so")
    assert "Notes.app" in printed, printed


def test_a_slot_reads_a_span_in_a_text_zone_and_never_a_whole_zone():
    """§3.5's slot names a LOCATION, and the location it named excluded every PDF.

    A locator is `zone[":" container][# span]`. `locator.startswith("body#")` --
    what both slots used -- therefore matched a span at the top of a document and
    missed one inside a page or an OCR region, which is how every PDF and every
    scan is addressed. They are P4's own worked examples
    (`tests/p4/test_p4_locator.py:34-35`). Measured over a 26-file corpus: 229
    observations, 2 reached the fact layer.

    The second half of this test is the reason the first half is safe. Admitting a
    zone wholesale also admits a whole PAGE and a whole TITLE, and a slot fed a
    page proposes a folder named after a paragraph.
    """
    reads = cli.reads_a_structured_string

    # Widened: a structured string is a structured string wherever it was found.
    assert reads("body#0-8"), "the plain-text reading that already worked"
    assert reads("heading#0-11"), "the docx heading that already worked"
    assert reads("body:page=1#62-72"), "§2.2's page reference -- every PDF"

    # Refused, and not by oversight. `direct_facts` writes `direct` unconditionally,
    # so an OCR region reaching a slot would promote a `possible` RECOGNITION to a
    # `direct` FACT and put a scanner's guess on a folder -- the laundering §3.6's
    # `PROPOSAL_ELIGIBLE_STATES` exists to stop. A PDF text layer is extracted text
    # and is admitted above; a recognition is promoted by a validation stage, a
    # model or the person, never by widening this list.
    assert not reads("ocr:page=4/region=2#0-24"), (
        "an OCR recognition reached a direct slot; §3.5 applies no reliability "
        "test, so this makes every scanner guess a `direct` fact")

    # Bounded: a whole zone is not a reading a slot may take.
    assert not reads("body"), "the whole body of a document"
    assert not reads("body:page=1"), "a whole page -- the folder-name-is-a-paragraph case"
    assert not reads("ocr:page=4/region=2"), "a whole OCR region"
    assert not reads("title"), "a title is said ABOUT a file, not in it"
    assert not reads("path"), "every file sits under some words; none are its own"
    assert not reads("filename#0-12"), "unchanged by this: still outside the slots"
    assert not reads("metadata:field=mime_type"), "machine metadata is not text"


def test_protected_material_is_not_the_first_thing_on_the_screen(tmp_path):
    """`00`:201 -- a summary of protected records may be safe on a shared screen,
    "a visible list of passport filenames" may not.

    The report sorted protected groups FIRST (`not shielded[key]`), so a run over a
    disk holding a passport opened with its filename. The rationale beside it is
    about not SUMMARISING a protected area away, which is a different rule and is
    untouched here: the names are still listed in full and nothing is elided. Only
    the order changes, so the first thing on screen is ordinary work.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "Passport Scan.txt").write_text(
        "Passport number X12345678 - scanned copy for records.\n", encoding="utf-8")
    (corpus / "Syllabus.txt").write_text(
        "PHYS1401 syllabus. Lecture notes for the semester.\n", encoding="utf-8")

    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework", "--label",
              "Coursework", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)
    report = out.getvalue()

    assert "protected material" in report, report
    assert "Ready to file into" in report, report
    assert report.index("Ready to file into") < report.index("protected material"), (
        "the report opens with the person's protected material; ordinary work "
        "should come first so a shared screen does not lead with a passport")


def test_answering_again_supersedes_the_earlier_answer_instead_of_racing_it(tmp_path):
    """§12's "edited, revoked, or re-run", and the link that makes an edit an edit.

    `apply_answers` reads the answer it is about to replace and writes
    `supersede_reason="the user answered this again"` -- and then passes
    `supersedes=None`, discarding the id `record_answer` returns for exactly this
    purpose ("so a later edit can supersede it"). `live_answer` defines the live
    answer as the one NOTHING supersedes, so with the link never written, every
    answer stays live and the winner falls to
    `ORDER BY recorded_at DESC, answer_id DESC`. `main` computes `now()` once, so
    the timestamps tie and a uuid4 breaks the tie.

    The person's own correction is therefore decided at random. This asserts the
    invariant that makes that impossible: one question, one scope, ONE live answer.
    """
    from database_agent.db import open_database

    corpus = _two_shape_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]
    answered = argv + ["--answer", "branch:Coursework=keep-as-it-is"]

    cli.main(argv, out=io.StringIO())
    cli.main(answered, out=io.StringIO())
    cli.main(answered, out=io.StringIO())

    conn = open_database(database)
    rows = conn.execute(
        "SELECT answer_id, supersedes FROM structural_answers "
        "WHERE question_id = ?", ("branch:Coursework",)).fetchall()
    superseded = {row["supersedes"] for row in rows} - {None}
    live = [row["answer_id"] for row in rows if row["answer_id"] not in superseded]

    assert len(rows) > 1, "the second answer must be recorded, not overwrite the first"
    assert len(live) == 1, (
        f"{len(rows)} answers to one question, {len(live)} of them live. A person "
        "who answers twice must not leave two answers governing at once")


# ======================================================================================
# The two oracles P6 and P8 each said were the other's (C-5)
# ======================================================================================


def test_the_normalizer_canonicalises_the_way_the_direct_slots_already_do():
    """§3.6 check 3: "the proposed value can be normalized safely".

    `facts/llm_seam.py` records the deadlock this closes: P8's SPEC names
    `normalize` and `contradicts` as P6's, P8's Deferred table files them back to
    P6, "so each part hands them to the other and neither builds them... The
    ruling is owed." Neither part owns them because they belong to the COMPOSITION
    ROOT -- the one place that chooses a policy -- and a test already forbids
    `facts` from publishing either.

    Nothing new is authored here. The model's value is canonicalised by the SAME
    rule the deterministic slot uses for that field, so `PHYS 1401` from a model
    and `PHYS1401` from a heading cannot become two courses. That failure is on
    the record: `65` §4.2, four files of one course became four one-file groups
    because one identity arrived as several spellings.
    """
    assert cli.normalize_for_model("subject", "PHYS 1401") == "PHYS1401"
    assert cli.normalize_for_model("subject", "PHYS1401") == "PHYS1401"
    assert cli.normalize_for_model("term", "Spring-2026") == "Spring2026"


def test_a_value_the_fields_own_predicate_rejects_is_not_normalizable():
    """The twin that gives check 3 something to reject.

    `DirectSlot.matches` is how this deployment tells a course code from a term
    over one body of text. A model proposing `Spring 2026` as a SUBJECT is
    proposing something the field's own rule says is not one, and answering with a
    canonical form would launder it into a folder name.
    """
    assert cli.normalize_for_model("subject", "Spring 2026") is None
    assert cli.normalize_for_model("term", "PHYS1401") is None


def test_a_value_that_canonicalises_to_nothing_is_not_normalizable():
    """Whitespace is not a value. An empty canonical form would be a folder with
    no name, and §3.6 would have passed it as normalized."""
    assert cli.normalize_for_model("subject", "   ") is None
    assert cli.normalize_for_model("subject", "") is None


def test_a_stronger_fact_with_a_different_value_contradicts():
    """§3.6 check 4: "no stronger direct or rule-validated fact contradicts it".

    `build_request` supplies only facts already STRONGER than an LLM conclusion,
    so reaching here means the model is disagreeing with something better
    supported than itself.
    """
    row = {"field_key": "subject", "canonical_value": "PHYS1401"}
    proposal = SimpleNamespace(field_key="subject", value="CHEM1500")

    assert cli.contradicts_stronger(proposal, row) is True


def test_two_spellings_of_one_value_do_not_contradict():
    """The twin that matters most, and the one this project has already been
    burned by. `PHYS 1401` and `PHYS1401` are one course. Comparing raw strings
    would make the model's own agreement read as a conflict and reject a correct
    answer -- with `CONTRADICTED_BY_STRONGER` on the record, which is a
    particularly misleading thing to be wrong about."""
    row = {"field_key": "subject", "canonical_value": "PHYS1401"}
    proposal = SimpleNamespace(field_key="subject", value="PHYS 1401")

    assert cli.contradicts_stronger(proposal, row) is False


def test_a_stronger_fact_about_another_field_is_not_a_contradiction():
    """The other twin. Knowing the term cannot contradict a claim about the
    subject; treating every stronger fact as a rival would let one settled field
    veto every proposal about the file."""
    row = {"field_key": "term", "canonical_value": "Spring2026"}
    proposal = SimpleNamespace(field_key="subject", value="PHYS1401")

    assert cli.contradicts_stronger(proposal, row) is False


#: The shell's own operators, which `shlex.split` does not know are operators.
SHELL_OPERATORS: frozenset[str] = frozenset({">", "<", ">>", "|", "||", "&", "&&", ";"})


def shell_tokens(line: str) -> list[str]:
    """One line, split THE WAY A SHELL SPLITS IT -- operators and all.

    `punctuation_chars=True` is the whole of this function and plain
    `shlex.split` is the trap it exists to avoid: `shlex.split("q=a>b")` returns
    one happy token, because the default lexer has no opinion about redirects.
    A guard written on it passes on the exact input `c17c76a` was about.

    `posix=True` so quotes are consumed the way a shell consumes them, which is
    what makes a correctly quoted line come back as ONE argument rather than as
    a token still wearing its quotes.
    """
    lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


@pytest.mark.parametrize("label", ["Legal Matters", "Coursework"])
def test_a_printed_answer_command_survives_being_pasted_into_a_shell(tmp_path, label):
    """The report tells the person exactly what to type. It must be typable.

    TWO HAZARDS, and this ran on one of them for a long time.

    The first is the SPACE. `--label` is the person's own words and it becomes
    the SCOPE of every branch question, so a person who files under "Legal
    Matters" gets `--answer branch:Legal Matters=subject`, which a shell splits
    at the space into two arguments -- one instruction, and it does not work, and
    it fails looking like the person's mistake.

    The second is the REDIRECT, and it is the one this test could not see. A
    nesting option id is `school>term>subject>work_type`, and `>` is the shell's
    output redirect: pasting that line unquoted does not fail, it silently writes
    files called `term`, `subject` and `work_type` into whatever directory the
    person happened to be in. `c17c76a` fixed that in `cli._typable`; this test
    was still measuring only the space, because its one corpus used a label that
    HAS a space and the louder hazard masked the quieter one.

    So it runs twice. `Legal Matters` fires the space with the redirect present;
    `Coursework` has no space at all, which leaves the redirect alone and
    unmasked. One fixture cannot tell a line that survives a shell from one that
    merely survives `shlex.split`, which is exactly how this got written.

    And the assertion had to change with the lexer. `"=" in tokens[1]` passes on
    the broken line too: unquoted, `branch:Coursework=school>term>...` lexes to
    `branch:Coursework=school` -- which still contains an `=` -- followed by a
    `>` operator. What is actually being asserted is that no operator survives
    into the command at all.
    """
    corpus = _two_shape_corpus(tmp_path)
    printed = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", label, "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=printed)
    report = printed.getvalue()

    offered = [line.strip() for line in report.splitlines()
               if line.strip().startswith("--answer ")]
    assert offered, report
    for line in offered:
        # The report prints the command and then a description after it, so only
        # the command's own two tokens are under test.
        tokens = shell_tokens(line)
        assert tokens[0] == "--answer", line
        assert "=" in tokens[1], (
            f"{line!r} splits into {tokens[:2]!r}: pasting it would pass "
            f"{tokens[1]!r} to --answer and leave the rest as stray arguments")
        stray = SHELL_OPERATORS & set(tokens)
        assert not stray, (
            f"{line!r} hands the shell {sorted(stray)}, which redirects or pipes "
            f"instead of running the command. It does not fail: pasting it writes "
            f"a file named after whatever followed. Tokens: {tokens!r}")


def test_a_skipped_question_can_still_be_found_afterwards(tmp_path):
    """A skip must be reversible by someone who no longer has the question id.

    §14 makes "skip for now" first-class and §12 forbids re-asking, and both are
    honoured: the question does not come back. But `revoke` -- the way back that
    `test_a_person_can_change_their_mind` proves works -- needs the question id,
    and once skipped the id is printed nowhere at all. So the door exists and
    the person cannot see it, which makes a decision taken in a hurry permanent
    in practice while the design says it is not.

    This is not a re-ask. It is one quiet line saying what was set aside and how
    to bring it back.

    The name of this test avoids the words "set aside" on purpose. `set aside`
    is a legal term, pytest names `tmp_path` after the test function, and an
    ancestor directory's name currently changes what the recogniser decides --
    so a test called `..._set_aside_...` silently reclassified its own corpus
    and never got asked the question it is about. That ancestor defect is real
    and is being fixed elsewhere; it is not this test's subject, and it should
    not be this test's outcome.
    """
    corpus = _ambiguous_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    cli.main(argv, out=io.StringIO())
    after = io.StringIO()
    cli.main(argv + ["--answer", "reading.organization:CV20261234=skip"],
             out=after)
    report = after.getvalue()

    assert "reading.organization:CV20261234" in report, (
        "the id the person needs in order to revoke is nowhere on the "
        f"screen:\n{report}")
    assert "revoke" in report, report


def test_the_reminder_line_is_not_the_question_asked_again(tmp_path):
    """The negative twin. §12 forbids the pressure of re-asking.

    A line that reprinted the prompt, the evidence and the options would be the
    question again wearing a different heading -- which is precisely what
    `test_skipping_is_an_answer_and_the_question_does_not_come_back` exists to
    stop. So the guard has to be that the PROMPT stays gone while the ID
    returns, and asserting only the id's presence would pass against a
    sabotaged version that simply reprinted everything.
    """
    corpus = _ambiguous_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    first = io.StringIO()
    cli.main(argv, out=first)
    lines = first.getvalue().splitlines()

    # The prompt belonging to THIS question, derived rather than hard-coded: the
    # last question line printed before its own options. The run also asks a
    # branch question that was never skipped, and that one is meant to stay.
    option = next(i for i, line in enumerate(lines)
                  if "--answer reading.organization:CV20261234=" in line)
    prompt = next(lines[i].strip() for i in range(option, -1, -1)
                  if lines[i].strip().endswith("?"))

    after = io.StringIO()
    cli.main(argv + ["--answer", "reading.organization:CV20261234=skip"],
             out=after)
    report = after.getvalue()

    assert prompt not in report, (
        f"{prompt!r} is the question being asked again:\n{report}")
    offered = [line.strip() for line in report.splitlines()
               if "--answer reading.organization:CV20261234=" in line]
    assert offered == [
        "--answer reading.organization:CV20261234=revoke   Ask me this again"], (
        f"the options are being offered again:\n{report}")
    # And the branch question, which was NOT skipped, is untouched by any of it.
    assert "How should Coursework be organised?" in report, report


def _everyday_corpus(tmp_path):
    """The material a person's disk is actually full of, and no template claims.

    `00`:120 names Memes among its residual areas by name. None of these files
    belongs to a domain, which is the point: the residual library is the
    design's answer to them, and until it is enabled the answer is unreachable.
    """
    corpus = tmp_path / "corpus"
    (corpus / "Screenshots").mkdir(parents=True)
    (corpus / "Memes").mkdir()
    (corpus / "Screenshots" / "Screenshot 2026-08-14 at 11.03.47.png").write_bytes(
        b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    (corpus / "Memes" / "drake-format.jpg").write_bytes(b"\xff\xd8\xff" + b"\x00" * 64)
    (corpus / "note-to-self.txt").write_text("Remember to renew the parking permit.\n")
    return corpus


def test_a_residual_area_the_person_enables_becomes_a_real_destination(tmp_path):
    """`00` §7.3's nine names exist in the code and have never once been offered.

    The library is built (`tree_design/residuals.py`), the enablement path is
    built (`tree_design/pipeline.py::_enable_residual_library`), the surfacing
    is built, and `cli.py` passed `{}` and `()` -- so every one of them is
    complete, tested and unreachable, which is this codebase's dominant defect.

    `--residual` is how a person says yes to one. §7.4 makes enablement the
    user's decision, so the flag names a template and nothing is enabled without
    it.
    """
    corpus = _everyday_corpus(tmp_path)
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "photos.screenshot-captures",
              "--label", "Pictures", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite"),
              "--residual", "Temporary Screenshots"], out=out)
    printed = out.getvalue()

    folders = printed.split("Folders in this plan:", 1)[1].split("Files:", 1)[0]
    assert "Temporary Screenshots" in folders, printed


def test_no_residual_area_is_created_unless_the_person_asks_for_it(tmp_path):
    """The negative twin, and it is `00` §7.4's own sentence.

    "These templates are not automatically created." A run that enabled the nine
    because they exist would be the product inventing nine folders nobody chose
    -- and `00`:99 separately forbids a catch-all becoming "the product's default
    answer to ambiguity". So the same corpus, without the flag, must produce
    none of the nine.
    """
    corpus = _everyday_corpus(tmp_path)
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "photos.screenshot-captures",
              "--label", "Pictures", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)
    printed = out.getvalue()

    folders = printed.split("Folders in this plan:", 1)[1].split("Files:", 1)[0]
    for name in RESIDUAL_TEMPLATE_NAMES:
        assert name not in folders, f"{name} was created without being asked for"


def test_a_residual_name_the_library_does_not_carry_is_refused_not_ignored(tmp_path):
    """A typo must not silently produce a run with nothing enabled.

    The whole point of the flag is that the person asked for something; a
    misspelling that quietly does nothing is the run reporting success for work
    it did not do.
    """
    corpus = _everyday_corpus(tmp_path)
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "photos.screenshot-captures",
                     "--label", "Pictures", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite"),
                     "--residual", "Temporary Screenshot"], out=out)
    printed = out.getvalue()

    assert code != 0, printed
    assert "Temporary Screenshots" in printed, (
        f"the refusal must name what the person could have meant:\n{printed}")


def test_an_enabled_residual_home_is_never_put_inside_a_folder_the_person_made(tmp_path):
    """`00`:100: existing folders "must not be automatically flattened, renamed,
    or reorganized simply because a template would produce a different
    structure."

    A residual home belongs inside a meaningful parent -- `00`:99 says a
    catch-all must not become "the product's default answer to ambiguity" -- and
    the parent it belongs inside is a branch THIS RUN proposed. The person's own
    `Memes` folder is not that. Nesting a product-created home inside it
    reorganises a folder the person made, on no evidence, as a side effect of
    enabling something else entirely.

    This corpus has no proposed top-level branch at all, so the honest answer is
    the root: no invented parent, and nobody's folder rearranged.
    """
    corpus = _everyday_corpus(tmp_path)
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "photos.screenshot-captures",
              "--label", "Pictures", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite"),
              "--residual", "Temporary Screenshots"], out=out)
    printed = out.getvalue()

    folders = printed.split("Folders in this plan:", 1)[1].split("Files:", 1)[0]
    lines = [line for line in folders.splitlines() if line.strip()]
    home = next(line for line in lines if "Temporary Screenshots" in line)
    adopted = [line for line in lines if "[yours already]" in line]
    assert adopted, folders
    shallowest_adopted = min(len(line) - len(line.lstrip()) for line in adopted)
    assert (len(home) - len(home.lstrip())) <= shallowest_adopted, (
        f"the residual home is nested inside a folder the person made:\n{folders}")


def test_importing_the_product_does_not_load_apples_vision_framework():
    """The first thing a person experiences is how long nothing happens.

    `readers/deployment.py` imported `readers.ocr_vision` at module scope, which
    pulls in Vision and Quartz. `python3 -X importtime` attributed 4.6s of
    `import cli`'s 7.3s warm to it, and about 75 of 77 seconds cold -- paid
    before one character reaches the screen, by every run, including
    `--list-situations` and every corpus with no image in it.

    A subprocess, because this process may already have imported it for some
    other reason, and then the assertion would pass for a reason that has
    nothing to do with the code under test.
    """
    source = ("import sys; import cli; "
              "print('Vision' in sys.modules or 'Quartz' in sys.modules)")
    result = subprocess.run(
        [sys.executable, "-c", source],
        cwd=str(Path(__file__).resolve().parents[1] / "src"),
        capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False", (
        "importing cli loads Apple's Vision framework again; the cost is paid "
        "by every run, including the ones with no image in them")


def test_the_ocr_engine_is_still_wired_after_being_imported_late():
    """The negative twin. Making the import lazy must not make OCR absent.

    An import moved into a function is a change nobody sees until the feature it
    hid stops working, so the wiring is asserted rather than assumed: the engine
    is present, and it is not `None`.
    """
    from readers.deployment import macos_readers
    readers = macos_readers(find_structured_strings=lambda _text: ())
    assert readers.ocr_engine is not None


def _mortgage_corpus(tmp_path, folder: str):
    """Two real documents inside a folder the person already made."""
    corpus = tmp_path / "corpus"
    theirs = corpus / folder
    theirs.mkdir(parents=True)
    (theirs / "agreement in principle.txt").write_text(
        "NORTHERN COUNTIES BUILDING SOCIETY\n"
        "MORTGAGE AGREEMENT IN PRINCIPLE\nReference: AIP-2026-778104\n"
        "Applicant: Mr Marcus Halloran\n"
        "Property: 8 Wolseley Gardens, Leeds LS6 1TG\n"
        "Purchase price 285,000 Deposit 42,750\n")
    (theirs / "statement jan.txt").write_text(
        "Statement of account\nAccount name M J HALLORAN\n"
        "Statement period 1 January 2026 to 31 January 2026\n"
        "Opening balance 4,118.22\nClosing balance 6,121.67\n")
    return corpus


def _top_level_folders(printed: str) -> list[str]:
    """The folder names the report prints at the first level of the tree."""
    lines = printed.split("Folders in this plan:", 1)[1].splitlines()[1:]
    names = []
    for line in lines:
        if not line.startswith("  "):
            break
        if line.startswith("    "):
            continue
        names.append(line.strip().split("   [")[0].strip())
    return names


@pytest.mark.xfail(strict=True, reason=(
    "The proposed top-level folder is allowed to have the same name as one the "
    "person already has, and the report prints the two as adjacent identical "
    "lines:\n\n    Mortgage\n    Mortgage   [yours already]\n\nBoth are "
    "destinations. Scanning a folder that already contains `Mortgage` and "
    "typing `--label Mortgage` is the most ordinary thing a person does -- it "
    "is what they would call it, which is why they called it that -- and the "
    "answer is a second folder of the same name beside their own. The person "
    "cannot tell the two apart on screen, and every later gesture that names "
    "the label is ambiguous. The standing ruling is that a gesture acting on "
    "something other than what the person named is worse than one that stops "
    "and asks: this should adopt their folder or refuse and say the name is "
    "taken. Reproduces with two files. Strict, so the suite turns red the day "
    "it is fixed."))
def test_the_proposed_folder_does_not_share_a_name_with_one_of_the_persons_own(tmp_path):
    """`--label Mortgage` over a disk that already has a `Mortgage` folder."""
    corpus = _mortgage_corpus(tmp_path, "Mortgage")
    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "finance.household-property",
                     "--label", "Mortgage", "--user", "m",
                     "--database", str(tmp_path / "plan.sqlite")], out=out) == 0
    printed = out.getvalue()

    names = _top_level_folders(printed)
    duplicated = [name for name in set(names) if names.count(name) > 1]
    assert not duplicated, (
        f"the plan has two top-level folders called {duplicated}:\n{printed}")


def test_a_label_that_collides_with_nothing_still_gets_its_folder(tmp_path):
    """The twin. Refusing to propose any top-level folder would pass the guard.

    The proposed folder is what `--label` is for. A fix that stopped creating
    it, or that renamed the person's own folder to make room, would make the
    names unique and take the feature away.
    """
    corpus = _mortgage_corpus(tmp_path, "House purchase")
    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "finance.household-property",
                     "--label", "Mortgage", "--user", "m",
                     "--database", str(tmp_path / "plan.sqlite")], out=out) == 0
    printed = out.getvalue()

    names = _top_level_folders(printed)
    assert "Mortgage" in names, (f"the label was not proposed at all: {names}\n{printed}")
    assert "House purchase" in names, (
        f"the person's own folder is gone from the picture: {names}\n{printed}")


@pytest.mark.xfail(strict=True, reason=(
    "`--reject` succeeds in silence. The run prints its ordinary report and "
    "not one word about the correction -- no confirmation, no 'that claim is "
    "retracted', nothing. The two REFUSAL paths are excellent and one of them "
    "states the principle this breaks: naming a value the file never carried "
    "answers 'refusing is the only answer that does not leave you believing "
    "you were heard'. A silent success leaves the person believing they were "
    "heard on exactly the same evidence -- an exit code of 0 and a report that "
    "still says what they just corrected. Measured on the real corpus: after "
    "rejecting `subject=BS7671` on an electrical certificate, the very next "
    "screen still proposes moving it into `Downloads` for that reason, and "
    "nothing on it acknowledges the rejection. Strict, so the suite turns red "
    "the day it is fixed."))
def test_rejecting_a_conclusion_says_so_on_screen(tmp_path):
    """A correction the person cannot see land is a correction they will retype.

    The rejection IS recorded -- the database gets a user-originated fact
    carrying the retraction -- so this is not about the mechanism. It is about
    the person, who typed a command that changes what the product believes and
    got back a screen identical to the one before it.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "EIC certificate.txt").write_text(
        "ELECTRICAL INSTALLATION CERTIFICATE\n"
        "BS 7671 Requirements for Electrical Installations\n"
        "Certificate number: EIC-2026-0341\n"
        "Installation address: 14 Ashgrove Terrace\n")
    argv = [str(corpus), "--situation", "construction_property.construction-project",
            "--label", "Jobs", "--user", "m",
            "--database", str(tmp_path / "plan.sqlite")]
    assert cli.main(argv, out=io.StringIO()) == 0

    out = io.StringIO()
    assert cli.main(argv + ["--reject", "EIC certificate.txt:subject=BS7671"],
                    out=out) == 0
    # The `Plan database:` line carries the tmp_path, which pytest names after
    # this function -- so searching the raw output for "reject" finds the TEST'S
    # OWN NAME and the guard passes against the defect. That is the trap
    # `84` §4 records: a test's name changing what the run appears to say.
    printed = "\n".join(line for line in out.getvalue().splitlines()
                        if not line.startswith("Plan database:"))

    assert any(word in printed.lower() for word in
               ("reject", "retract", "no longer", "took that back")), (
        "the run accepted the rejection and said nothing about it:\n" + printed)


def test_rejecting_something_the_file_never_said_is_still_refused(tmp_path):
    """The twin, and the behaviour that must survive any fix to the one above.

    Making the success path speak must not make the refusal paths stop
    refusing. Both messages are the product at its best and they are pinned
    here so a change to the reporting cannot quietly turn either into a
    reassuring sentence about nothing.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "EIC certificate.txt").write_text(
        "ELECTRICAL INSTALLATION CERTIFICATE\n"
        "BS 7671 Requirements for Electrical Installations\n"
        "Certificate number: EIC-2026-0341\n")
    argv = [str(corpus), "--situation", "construction_property.construction-project",
            "--label", "Jobs", "--user", "m",
            "--database", str(tmp_path / "plan.sqlite")]
    assert cli.main(argv, out=io.StringIO()) == 0

    out = io.StringIO()
    code = cli.main(argv + ["--reject", "EIC certificate.txt:subject=BANANA"], out=out)
    assert code != 0, out.getvalue()
    assert "carries no subject of 'BANANA'" in out.getvalue(), out.getvalue()

    absent = io.StringIO()
    code = cli.main(argv + ["--reject", "nosuchfile.pdf:subject=BS7671"], out=absent)
    assert code != 0, absent.getvalue()
    assert "is not a file in this plan" in absent.getvalue(), absent.getvalue()


#: The words are a real court filing's, so the recognition vocabulary has
#: something to fire on. They are shared by both files in the corpus below,
#: because the whole question is whether the FORMAT changes the answer.
_MOTION_LINES: tuple[str, ...] = (
    "IN THE SUPERIOR COURT OF THE STATE OF CALIFORNIA",
    "COUNTY OF ALAMEDA",
    "HENDRICKS v. NORTHRIDGE PROPERTY MANAGEMENT LLC",
    "Case No. CV20264417",
    "PLAINTIFF'S MOTION TO COMPEL FURTHER RESPONSES",
    "MEMORANDUM OF POINTS AND AUTHORITIES",
    "Code of Civil Procedure section 2031.310(b)(2)",
)


def _one_page_pdf(lines) -> bytes:
    """A real single-page PDF carrying `lines` as text, built with the stdlib.

    `reportlab` is not a dependency of this project and must not become one for a
    test. `pdfminer.six` IS -- it is in the `readers` extra, because the
    deployment layer chose it -- so what this has to produce is a file pdfminer
    will read: correct object offsets, a real xref table, and a content stream
    with `Tj` operators rather than bytes that merely start with `%PDF`.
    """
    def esc(text: str) -> str:
        return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

    body = ["BT", "/F1 12 Tf", "72 720 Td", "14 TL"]
    for line in lines:
        body += [f"({esc(line)}) Tj", "T*"]
    body.append("ET")
    stream = "\n".join(body).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, payload in enumerate(objects, start=1):
        offsets.append(len(out))
        out += str(number).encode() + b" 0 obj\n" + payload + b"\nendobj\n"
    xref_at = len(out)
    out += b"xref\n0 " + str(len(objects) + 1).encode() + b"\n0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (b"trailer\n<< /Size " + str(len(objects) + 1).encode()
            + b" /Root 1 0 R >>\nstartxref\n" + str(xref_at).encode() + b"\n%%EOF\n")
    return bytes(out)


def _one_motion_two_formats(tmp_path):
    """The same court filing, saved twice: once as .txt and once as a real PDF."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "motion.txt").write_text("\n".join(_MOTION_LINES) + "\n")
    (corpus / "motion.pdf").write_bytes(_one_page_pdf(_MOTION_LINES))
    return corpus


def _run_two_formats(tmp_path):
    corpus = _one_motion_two_formats(tmp_path)
    database = tmp_path / "plan.sqlite"
    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "law_practice.discovery",
                     "--label", "Matters", "--user", "jy",
                     "--database", str(database)], out=out) == 0
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    extractors = {}
    for row in conn.execute(
            "SELECT f.filename, e.extractor_name FROM files f "
            "JOIN evidence e ON e.file_id = f.file_id"):
        extractors.setdefault(row["filename"], set()).add(row["extractor_name"])
    conn.close()
    # Not vacuous: if the deployment shipped no PDF library the file would be
    # `unsupported` and this whole comparison would be about a missing install
    # rather than about the seam.
    assert "pdf.text" in extractors.get("motion.pdf", set()), (
        "no PDF reader ran, so nothing here is about classification: "
        f"{sorted(extractors.get('motion.pdf', ()))}")
    return out.getvalue()


@pytest.mark.xfail(strict=True, reason=(
    "The same court filing gets two different answers depending on whether it "
    "was saved as .txt or as PDF. The PDF is READ -- pdfminer runs and the page "
    "text lands in `text_units` -- and the person is then told 'This file has "
    "not been classified, nothing has yet said what kind of material it is', "
    "while the identical .txt is told 'Deciding this file needed a model'. "
    "Measured at the seam: `text.structured` writes TWO evidence rows for a "
    "text file, the whole `body` and the identifier span inside it; `pdf.text` "
    "writes only the span, `body:page=1#124-134`. The detector matches against "
    "evidence values, so a text file always reaches it with the document's "
    "words and a PDF reaches it with an identifier and some metadata. The "
    "consequence is not a weaker answer for PDFs, it is NO answer: every "
    "readable .txt in these runs got a classification from the detector -- "
    "including a bland one that got `personal_non_sensitive` -- and no PDF got "
    "one at all. Most documents on a real disk are PDFs, so this is the "
    "largest single cause of 'nobody got a file filed', and it sits UPSTREAM "
    "of the model: no amount of model wiring reaches a file the detector never "
    "classified. Verified to go green when the detector is given the PDF's "
    "words. Strict, so the suite turns red the day it is fixed."))
def test_a_pdf_and_a_txt_of_the_same_document_get_the_same_answer(tmp_path):
    """One document, two files, two sentences on the same screen.

    A person who prints a letter to PDF and keeps the draft as text has one
    thing, and the report tells them two different stories about it. The PDF is
    the copy they kept.
    """
    printed = _run_two_formats(tmp_path)

    pdf = _block_naming(printed, "motion.pdf")
    assert "has not been classified" not in pdf, (
        "the PDF was read and then reported as never classified, while the "
        f"identical .txt was not:\n{pdf}\n\nwhole report:\n{printed}")


def test_the_plain_text_copy_is_still_recognised(tmp_path):
    """The twin. Levelling the two down would satisfy the guard above.

    The .txt is the copy that works today. A fix that stopped recognising it --
    or one that classified everything regardless of evidence -- would make the
    two agree and make the product worse, so what the .txt gets is pinned here.
    """
    printed = _run_two_formats(tmp_path)

    txt = _block_naming(printed, "motion.txt")
    assert "has not been classified" not in txt, (
        f"the .txt is no longer recognised either:\n{txt}")


def _encrypted_container_corpus(tmp_path):
    """A password vault, an encrypted disk image, a passport and a holiday snap.

    The bytes are stand-ins -- a KeePass signature, a `koly` trailer, JFIF magic
    -- because the point is that NOTHING opens them. What identifies them to a
    person is the name and the extension, which is all the product has too.
    """
    corpus = tmp_path / "corpus"
    private = corpus / "Private"
    private.mkdir(parents=True)
    (private / "credentials.kdbx").write_bytes(
        b"\x03\xd9\xa2\x9agU\xfb\x4b" + b"\x00" * 4096)
    (private / "backup.dmg").write_bytes(b"\x00" * 512 + b"koly" + b"\x00" * 2048)
    (private / "passport bio page.txt").write_text(
        "PASSPORT\nUNITED STATES OF AMERICA\nPassport No. 517204418\n"
        "Surname ZHANG Given names WEI\nDate of birth 14 NOV 1991\n")
    (corpus / "holiday.jpg").write_bytes(
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01" + b"\x00" * 400)
    return corpus


def _block_naming(printed: str, filename: str) -> str:
    """The report block that names one file, blank-line delimited as printed."""
    blocks = [block for block in printed.split("\n\n") if filename in block]
    assert len(blocks) == 1, (
        f"{filename!r} is named in {len(blocks)} blocks, not one:\n{printed}")
    return blocks[0]


def test_nothing_opens_the_vault_the_disk_image_or_the_passport(tmp_path):
    """The standing rule's hardest clause, checked at the seam that would break it.

    Protected material is marked and counted, NEVER OPENED. This asserts the
    "never opened" half directly: the only evidence recorded about the vault,
    the disk image and the passport bytes may come from the filesystem record.
    An extractor name that is not `filesystem.record` means something read the
    file, and for a password vault that is the failure no amount of correct
    reporting afterwards would undo.

    The passport is in the list on purpose. Its TEXT is read -- it is a text
    file and that is how it is recognised -- so this test is about the two
    containers, and the passport is here to make the query prove it can tell
    the difference rather than passing because it found nothing anywhere.
    """
    corpus = _encrypted_container_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(database)], out=io.StringIO()) == 0

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    read_by = {}
    for row in conn.execute(
            "SELECT f.filename, e.extractor_name FROM files f "
            "JOIN evidence e ON e.file_id = f.file_id"):
        read_by.setdefault(row["filename"], set()).add(row["extractor_name"])
    conn.close()

    for sealed in ("credentials.kdbx", "backup.dmg"):
        assert read_by.get(sealed) == {"filesystem.record"}, (
            f"something read inside {sealed}: {sorted(read_by.get(sealed, ()))}")
    # The control. The passport IS read, so a query that returned
    # `{'filesystem.record'}` for everything would be measuring nothing.
    assert read_by.get("passport bio page.txt", set()) != {"filesystem.record"}, (
        "the passport's own words were not read either, so the assertion above "
        "proves nothing about the containers")


@pytest.mark.xfail(strict=True, reason=(
    "A KeePass vault and an encrypted disk image are put in an ordinary review "
    "set whose reason ends 'not marked sensitive and not judged on thin "
    "evidence', beside a holiday photo -- and that set IS offered `--send-set`, "
    "so a password vault can be filed in one bulk gesture. The passport in the "
    "same corpus is marked protected and correctly refused that gesture, so "
    "the mechanism works; what it has nothing for is a container whose "
    "sensitivity is in its FORMAT rather than in words it will not open. The "
    "shipped residual library already carries an area named 'Unsupported or "
    "Encrypted' and nothing routes to it. Nothing was opened -- "
    "`test_nothing_opens_the_vault_the_disk_image_or_the_passport` holds -- and "
    "nothing was omitted; what fails is the MARK, and the sentence a person "
    "reads about their own password vault is false. Strict, so the suite turns "
    "red the day it is fixed."))
def test_a_password_vault_is_not_reported_as_not_marked_sensitive(tmp_path):
    """What the screen says about the most sensitive file on the disk.

    "It is waiting for you to say what it is, not marked sensitive" is a
    reasonable sentence about `holiday.jpg` and a false one about
    `credentials.kdbx`. The two are printed under one heading, with one reason,
    and one command that files them together.
    """
    corpus = _encrypted_container_corpus(tmp_path)
    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite"),
                     "--residual", "Review Later"], out=out) == 0
    printed = out.getvalue()

    vault = _block_naming(printed, "credentials.kdbx")
    assert "not marked sensitive" not in vault, (
        "the report says the password vault is not marked sensitive:\n" + vault)
    assert "--send-set" not in vault, (
        "the report offers to file the password vault in one bulk gesture:\n"
        + vault)


@pytest.mark.xfail(strict=True, reason=PENDING_SHOW_PROTECTED)
def test_the_passport_in_the_same_corpus_is_still_marked_and_still_refused(tmp_path):
    """The twin. Marking everything protected would satisfy the guard above.

    A fix that swept every unclassified file into the protected set would pass
    the vault test and destroy the distinction the set exists to draw, so the
    passport has to keep being marked for its own reason -- and `holiday.jpg`
    has to keep NOT being marked.
    """
    corpus = _encrypted_container_corpus(tmp_path)
    out = io.StringIO()
    # `--show-protected`, because this test is addressed to a BLOCK BY FILENAME
    # and the owner's 2026-09-02 ruling summarises those by default. What is
    # under test is the mark and the refusal, neither of which the ruling
    # touched, so the flag restores exactly the view this was written against.
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Papers", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite"),
                     "--residual", "Review Later",
                     "--show-protected"], out=out) == 0
    printed = out.getvalue()

    passport = _block_naming(printed, "passport bio page.txt")
    assert "protected material" in passport, passport
    assert "--send-set" not in passport, passport
    holiday = _block_naming(printed, "holiday.jpg")
    assert "protected material" not in holiday, (
        "an ordinary photo is now protected material, so the mark no longer "
        f"means anything:\n{holiday}")


def _mixed_sensitivity_corpus(tmp_path):
    """Ordinary files and protected ones, none of which any template places."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "Passport scan.txt").write_text(
        "PASSPORT\n\nPassport No X12345678. Date of birth JUN1998.\n")
    (corpus / "notes.txt").write_text("Remember to buy milk.\n")
    (corpus / "receipt.txt").write_text("Thank you for your purchase.\n")
    return corpus


@pytest.mark.xfail(strict=True, reason=PENDING_SHOW_PROTECTED)
def test_a_review_set_says_truthfully_whether_it_holds_protected_material(tmp_path):
    """`residual_partition` declared every set `protected: False` and
    `sensitivity_status: "none"`, as literals, whatever it actually held.

    P11 builds a real refusal on that flag -- `require_set_actionable` checks
    `residual_set.protected` and raises BEFORE it reads any decision, so
    protection is decided independently of what the person chose. Declaring
    every set unprotected means that refusal can never fire, and the guard is
    complete, tested and unreachable.

    The standing rule is that protected material is marked and counted, never
    opened and never silently omitted. A set that holds a passport and says it
    holds nothing sensitive breaks the first clause while appearing to keep the
    third.
    """
    corpus = _mixed_sensitivity_corpus(tmp_path)
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Papers", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite")], out=out)
    printed = out.getvalue()

    # Present, not omitted -- which under the owner's 2026-09-02 ruling is the
    # count and the way to the name, rather than the name. The SET is what this
    # test is about and it is named either way.
    flat = " ".join(printed.split())
    assert "2 protected files, marked and counted" in flat, printed
    assert "--show-protected" in printed, printed
    # Asserted on the SET NAME and not on how many "Held for review" lines the
    # report prints. Counting lines passes against the defect: the report groups
    # DECISIONS by their reason, so a protected file and an unclassified one
    # already produce two lines while naming one and the same set. The property
    # is that the two kinds are in two SETS, because the set is what carries the
    # protected flag and what `--send-set` addresses.
    labels = {line.split('Held for review as "', 1)[1].split('"', 1)[0]
              for line in printed.splitlines() if "Held for review" in line}
    assert len(labels) >= 2, (
        "protected and ordinary unplaced files are in one undifferentiated "
        f"set, named {labels}:\n{printed}")


def test_a_protected_review_set_refuses_to_be_filed_in_one_gesture(tmp_path):
    """The negative twin, and the reason the flag above has to be truthful.

    `--send-set` files a whole set with no model call and no per-file look. Over
    protected material that is precisely the gesture the design refuses: §7.7's
    gate is checked before any decision is read. If the CLI can never surface a
    protected set, this refusal is unreachable from anything a person runs, and
    asserting it only in `tests/p11` would keep passing while the product
    shipped the opposite.
    """
    corpus = _mixed_sensitivity_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Papers", "--user", "jy", "--database", str(database)]

    first = io.StringIO()
    cli.main(argv + ["--residual", "Review Later"], out=first)
    label = next(
        line.split('Held for review as "', 1)[1].split('"', 1)[0]
        for line in first.getvalue().splitlines()
        if "Held for review" in line and "Protected" in line)

    out = io.StringIO()
    code = cli.main(argv + ["--residual", "Review Later",
                            "--send-set", f"{label}=Review Later"], out=out)
    printed = out.getvalue()
    assert code != 0, printed
    assert "Passport scan.txt" not in printed.split("refused", 1)[-1][:200], printed


def test_a_protected_set_is_not_offered_a_command_that_would_refuse(tmp_path):
    """The report may not print an instruction it will reject.

    `--send-set` files a whole set in one gesture, and a protected set refuses
    that by design. Offering the flag anyway prints a command that always
    fails -- and it contradicts the sentence directly above it, which has just
    said these are not filed in one gesture with everything else.

    This is the same defect as the unpasteable `--answer` line and the
    unreachable `revoke`: what the screen tells a person to type has to be true.
    """
    corpus = _mixed_sensitivity_corpus(tmp_path)
    out = io.StringIO()
    cli.main([str(corpus), "--situation", "academic.coursework",
              "--label", "Papers", "--user", "jy",
              "--database", str(tmp_path / "plan.sqlite"),
              "--residual", "Review Later"], out=out)
    printed = out.getvalue()

    protected = next(block for block in printed.split("Held for review as ")
                     if block.startswith('"Protected'))
    assert "--send-set" not in protected.split("\n\n", 1)[0], protected
    # The twin, in the same run: the ordinary set IS still offered it, so this
    # is a distinction and not the feature quietly being switched off.
    ordinary = next(block for block in printed.split("Held for review as ")
                    if block.startswith('"Not yet placed'))
    assert "--send-set" in ordinary.split("\n\n", 1)[0], ordinary


def test_a_printed_send_set_command_survives_being_pasted_into_a_shell(tmp_path):
    """The same rule as `--answer`, applied to the other flag the report offers.

    What the screen tells a person to type has to be true. A command split
    across two lines by a text wrapper is not a command: the quote never
    closes, so pasting it either hangs the shell waiting for the rest of the
    string or -- inside a quoted argument -- passes an area name the plan does
    not have and earns a refusal that looks like the person's mistake.

    Every shipped residual area is exercised rather than one, because the
    defect is a width accident: `Review Later` happens to fit and
    `Receipts and Confirmations` happens not to, and testing only the short one
    is how this survived the fix that repaired the identical defect in
    `--answer`.
    """
    argv = ["--situation", "academic.coursework", "--label", "Papers",
            "--user", "jy"]
    for index, area in enumerate(RESIDUAL_TEMPLATE_NAMES):
        holder = tmp_path / f"area{index}"
        holder.mkdir()
        corpus = _mixed_sensitivity_corpus(holder)
        out = io.StringIO()
        cli.main([str(corpus)] + argv
                 + ["--database", str(holder / "plan.sqlite"),
                    "--residual", area], out=out)
        printed = out.getvalue()
        offered = [line for line in printed.splitlines() if "--send-set" in line]
        assert offered, f"no --send-set was offered for {area!r}:\n{printed}"
        for line in offered:
            command = line[line.index("--send-set"):]
            try:
                # `shell_tokens` and not `shlex.split`, for the reason that
                # function's own docstring gives: the default lexer has no
                # opinion about `>`, so a redirect in a residual area's name
                # would come back as one happy token and this guard would pass
                # on a line that writes a file instead of filing a set.
                tokens = shell_tokens(command)
            except ValueError as unbalanced:
                raise AssertionError(
                    f"the report offers {command!r}, which a shell cannot "
                    f"parse ({unbalanced}). The command is wrapped onto the "
                    f"next line of:\n{printed}") from None
            assert tokens[0] == "--send-set", line
            assert len(tokens) == 2, (
                f"{command!r} splits into {tokens!r}: pasting it would pass "
                f"{tokens[1]!r} to --send-set and leave the rest as stray "
                f"arguments")
            assert tokens[1].endswith(f"={area}"), (
                f"the report offers {tokens[1]!r}, which does not name the "
                f"area {area!r} this plan actually has, so the command it "
                f"prints would be refused")


def _two_lives_one_semester_corpus(tmp_path):
    """One person, two lives, one word in common.

    A part-time law student who is also a parent. Her CONTRACTS files sit in the
    semester folder she made; her child's report cards sit in `Kid`. The only
    thing the two lives share is the word "Fall 2026", which is a `term` in one
    life and a school trimester in the other.

    Five files is the minimum that reproduces it: the branch has to resolve on
    `term`, which needs two distinct terms in the corpus, which is what the
    second report card supplies.
    """
    corpus = tmp_path / "corpus"
    semester = corpus / "School" / "Bayline College of Law" / "Fall 2026"
    semester.mkdir(parents=True)
    (semester / "CONTRACTS 210 syllabus.txt").write_text(
        "BAYLINE COLLEGE OF LAW\nCONTRACTS 210 - Section B\nFall 2026 Syllabus\n\n"
        "Instructor: Professor H. Nakamura\nCredits: 4\n"
        "Required text: Farnsworth, Cases and Materials on Contracts.\n"
        "GRADING Final examination 70 percent. Midterm 20 percent.\n")
    (semester / "CONTRACTS 210 problem set 2.txt").write_text(
        "CONTRACTS 210 - Problem Set 2\nBayline College of Law, Fall 2026\n"
        "Due: September 18, 2026\nProfessor H. Nakamura\n"
        "Answer all three. Cite to the casebook where relevant.\n")
    (semester / "CONTRACTS 210 problem set 2 FINAL FINAL.txt").write_text(
        "CONTRACTS 210 - Problem Set 2 - submission\n"
        "Bayline College of Law, Fall 2026\nProfessor H. Nakamura\n"
        "A contract was not formed on March 3.\n")
    kid = corpus / "Kid"
    kid.mkdir()
    (kid / "report card fall 2026.txt").write_text(
        "RIDGEWAY ELEMENTARY SCHOOL\n"
        "Student Progress Report - Fall 2026 Trimester\n"
        "Student: A. Brannigan-Okonjo\nGrade: 4\nTeacher: Mr. R. Halloway\n"
        "READING: Exceeds standard.\nMATHEMATICS: Meets standard.\n")
    (kid / "report card spring 2026.txt").write_text(
        "RIDGEWAY ELEMENTARY SCHOOL\n"
        "Student Progress Report - Spring 2026 Trimester\n"
        "Student: A. Brannigan-Okonjo\nGrade: 3\nTeacher: Ms. K. Duval\n"
        "READING: Meets standard.\nMATHEMATICS: Approaching standard.\n")
    return corpus


def _ready_to_file_blocks(printed: str) -> list[str]:
    """The blocks the report headed "Ready to file into ...".

    Read off the report rather than the database on purpose: what is under test
    is the sentence a person acts on, and a placement recorded but not printed
    would not move anything.
    """
    return [block for block in printed.split("\n\n")
            if block.strip().startswith("Ready to file into")]


@pytest.mark.xfail(strict=True, reason=(
    "The child's report cards are proposed for the parent's law school "
    "semester folders, and they are the ONLY two files in the corpus the "
    "product is confident enough to move. One course means `subject` does not "
    "divide, so the report leaves that level out -- correctly, by its own "
    "stated rule -- and the branch resolves on `term` alone. The destinations "
    "then expect exactly `term=Fall2026` and `term=Spring2026`, and a report "
    "card's whole recorded evidence is one `term` fact. So a semester word is "
    "a COMPLETE match: the file states nothing about a course and nothing "
    "asks it to. The anchoring field is absent and the file is placed on the "
    "period alone, which is 'absent means refuse, never guess' read the other "
    "way round. This is the north star's own case -- the person who is a "
    "student and a parent at once -- and the report's honesty about it is a "
    "line at the BOTTOM ('applied to EVERY file in the folder -- including any "
    "that are something else entirely'), while the line at the top says "
    "'Ready to file'. Whether the answer is a non-period field requirement, a "
    "category check, or a question, is the owner's call; the symptom is not. "
    "Verified to go green under the first of those. Strict, so the suite "
    "turns red the day it is fixed."))
def test_a_childs_report_card_is_not_filed_into_the_law_school_semester(tmp_path):
    """Two lives, one word, and the product moves the wrong one.

    Every other file in this corpus comes back "waiting for you to say what
    these are". The two the product WILL act on are the two it has no business
    acting on, which is worse than placing nothing: a person who trusts the one
    confident line on the screen ends up with their child's school record in
    their Contracts folder.
    """
    corpus = _two_lives_one_semester_corpus(tmp_path)
    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite")],
                    out=out) == 0
    printed = out.getvalue()

    misfiled = [block for block in _ready_to_file_blocks(printed)
                if "report card" in block]
    assert not misfiled, (
        "the report offers to move the child's report cards into the law "
        "school's semester folders:\n" + "\n\n".join(misfiled)
        + "\n\nwhole report:\n" + printed)


def test_the_coursework_the_semester_folder_does_hold_is_still_recognised(tmp_path):
    """The twin, and the reason the test above may not be satisfied by silence.

    Refusing to place anything at all would pass the guard above and destroy
    the product. The three CONTRACTS files really do belong in the semester
    folder they are already in, and the report has to keep saying so.
    """
    corpus = _two_lives_one_semester_corpus(tmp_path)
    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "plan.sqlite")],
                    out=out) == 0
    printed = out.getvalue()

    settled = [block for block in printed.split("\n\n")
               if block.strip().startswith("Already in Fall 2026")]
    named = [name for block in settled for name in block.splitlines()
             if "CONTRACTS 210" in name]
    assert len(named) == 3, (
        f"the semester folder's own coursework is no longer recognised as "
        f"being where it belongs; only {named} were:\n{printed}")


def _course_corpus(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor office hours.\n")
    (corpus / "PHYS 1401 homework 3.txt").write_text(
        "PHYS 1401 Homework 3\n\nSpring 2026 lecture notes.\n")
    (corpus / "PHYS 1401 lab.txt").write_text(
        "PHYS 1401 Lab\n\nSpring 2026 lab report.\n")
    return corpus


def test_a_second_run_after_the_person_deletes_a_file_still_produces_a_plan(tmp_path):
    """A disk changes between runs. That is the normal case, not an edge one.

    The merged group this command accepts was addressed `plan_0:<category>:<label>`
    -- and `PLAN_VERSION` is a fixed constant, so the address was completely
    stable across runs while its contents were the person's corpus, which is
    not. Delete one file and the next run raised `MalformedGroupRecord` with a
    traceback: "already recorded with different content; a revision supersedes
    rather than replaces".

    P9's store is right, and the address was wrong. Its own rule says a group id
    derived from its seed is an address, so a rerun over unchanged evidence is
    the same group and not a conflict. This id was derived from the label, which
    says nothing about what the group holds.

    This blocked every second-run mechanism at once -- answering a question,
    revoking one, sending a review set, rejecting a fact -- because all of them
    are a second run by definition.
    """
    corpus = _course_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    assert cli.main(argv, out=io.StringIO()) == 0

    (corpus / "PHYS 1401 lab.txt").unlink()
    after = io.StringIO()
    assert cli.main(argv, out=after) == 0, after.getvalue()
    printed = after.getvalue()
    # A plan, not a traceback. What the plan then SAYS about the file that is
    # gone is a separate defect and has its own test below; conflating the two
    # here would let either one mask the other.
    assert "Folders in this plan:" in printed, printed
    assert "PHYS 1401 syllabus.txt" in printed, printed


@pytest.mark.xfail(strict=True, reason=(
    "A file the person deleted is still named in the next run's plan. The scan "
    "does not find it; the report reads it back out of the database, which "
    "remembers it from the run before. So the product offers to file something "
    "that is not there. Found while fixing the crash that used to hide it -- "
    "until the second run stopped raising, nobody could see this. Strict, so "
    "the suite turns red the day it is fixed."))
def test_a_file_the_person_deleted_is_not_in_the_next_plan(tmp_path):
    corpus = _course_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    assert cli.main(argv, out=io.StringIO()) == 0
    (corpus / "PHYS 1401 lab.txt").unlink()
    after = io.StringIO()
    cli.main(argv, out=after)
    assert "PHYS 1401 lab.txt" not in after.getvalue(), after.getvalue()


def test_a_rerun_over_an_unchanged_corpus_is_the_same_group_and_not_a_new_one(tmp_path):
    """The negative twin, and the property the old address got right.

    Deriving the id from the contents must not make every run a fresh group: a
    rerun over unchanged evidence is the SAME group, which is what makes the
    record an address rather than a log. A fix that simply minted a new id each
    time would pass the test above and quietly destroy that.
    """
    corpus = _course_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    assert cli.main(argv, out=io.StringIO()) == 0
    assert cli.main(argv, out=io.StringIO()) == 0

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    accepted = [row["group_id"] for row in conn.execute(
        "SELECT group_id FROM groups WHERE label_source = 'user-edited'")]
    conn.close()
    assert len(set(accepted)) == 1, (
        f"two identical runs minted {len(set(accepted))} accepted groups: {accepted}")


def test_rejecting_a_conclusion_about_an_ambiguous_filename_is_refused(tmp_path):
    """Two folders, one filename. `--reject` must not guess which was meant.

    `notes.txt` in two directories is the most ordinary thing on a real disk.
    The lookup behind `--reject` reads `WHERE filename = ?` and takes the first
    row, so a person correcting the product about one of them would silently
    retract a conclusion about the other -- and the screen would say it worked.

    This is the same defect as a bare label naming a split review set, which
    refuses for the same reason: a gesture that acts on something other than
    what the person named is worse than one that stops and asks.
    """
    corpus = tmp_path / "corpus"
    (corpus / "PHYS 1401").mkdir(parents=True)
    (corpus / "CHEM 1500").mkdir(parents=True)
    (corpus / "PHYS 1401" / "notes.txt").write_text(
        "PHYS 1401 Lecture Notes\n\nSpring 2026 lecture notes.\n")
    (corpus / "CHEM 1500" / "notes.txt").write_text(
        "CHEM 1500 Lecture Notes\n\nSpring 2026 lecture notes.\n")
    database = tmp_path / "plan.sqlite"
    argv = [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy", "--database", str(database)]

    assert cli.main(argv, out=io.StringIO()) == 0

    out = io.StringIO()
    code = cli.main(argv + ["--reject", "notes.txt:subject=PHYS1401"], out=out)
    printed = out.getvalue()
    assert code != 0, printed
    # And it says which ones it could have meant, so the person can name one.
    assert "PHYS 1401" in printed and "CHEM 1500" in printed, printed
