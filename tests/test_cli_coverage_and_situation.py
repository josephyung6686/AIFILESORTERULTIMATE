# tests/test_cli_coverage_and_situation.py
"""`104` §18.2 gaps 9 and 10: the two accounts of a run that reached nobody.

**Gap 9.** `cli.py` initialised `situation_cell`, the situation pass filled it, and
no line of the report ever read it. So site G -- the site that decides which
situation a file is asked under and whether it may reach the cloud at all -- ran on
every ordinary run and left nothing a person could see, and its `no_route` counter,
which is the protected-file count `00`:259 wanted surfaced, was a number in a list
nobody printed. Site G was also absent from the per-site question table and from
every posture branch, so the notice described the three sites that ACT on a file's
situation and never named the one that CHOOSES it.

**Gap 10.** `assert_every_file_accounted` -- P13's "no indexed file may be absent
from every entry" -- was reachable from `src/` only down `_nothing_could_be_read_
report`, the screen for a folder NOTHING could be read out of. The rule therefore
held on the one run where a person could check it by looking, and on no ordinary
run at all: a file the deterministic producers settled got no line anywhere, and
the report was a page of counts with no way to tell whether they covered the
folder. `00`:259 names the impression that leaves in as many words -- "that an
unprocessed file was understood and found unimportant".

Every test below names the SABOTAGE it exists to catch: the edit that would put the
defect back, and which assertion goes red when somebody makes it.
"""
from __future__ import annotations

import dataclasses
import io
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

import cli
from llm_harness.vocabulary import (
    A_FACT, C_PLACEMENT, D_RESIDUAL, G_SITUATION_SENSITIVITY,
)
from review_surface.progress import FileAbsentFromEveryEntry


# =====================================================================
# gap 9, first half: site G's seven counters reach the screen
# =====================================================================

def _a_pass(**over) -> cli.SituationPass:
    """A `SituationPass` with a different number in every counter.

    DIFFERENT NUMBERS ON PURPOSE. With `1` everywhere a test asserting "1 appears
    seven times" passes while six of the seven lines are missing, which is the
    exact defect these tests are about -- a count that reaches nobody.
    """
    return cli.SituationPass(**{
        "named": {"file-a": "academic.coursework", "file-b": "finance.records"},
        "nothing_to_read": 22, "declined": 33, "no_route": 44, "over_ceiling": 55,
        "recognised_by_rules": 66,
        "holds": cli.PrecautionHolds(0, 0, 0, 0),
        **over})


def _printed(situation: cli.SituationPass, *, files: int = 221) -> str:
    out = io.StringIO()
    cli._print_situation_pass(situation, files=files, model_id="qwen3:8b",
                              out=out)
    return " ".join(out.getvalue().split())


def test_all_seven_of_site_gs_counters_reach_the_screen():
    """`104` §18.2 gap 9, the defect stated as an assertion.

    SABOTAGE: delete any one line of `_print_situation_pass`'s loop, or make it
    `if not count_: continue` the way `_print_fact_pass` skips its empty causes.
    The number for that counter disappears from the block and its assertion here
    goes red. Deleting the whole call at the `situation_cell` write -- which is
    what the code did before this gap was closed -- takes all seven.
    """
    said = _printed(_a_pass())

    # The header carries the counter the pass exists to produce.
    assert "2 of 221 files were given their own situation by qwen3:8b" in said
    # EACH PHRASE IS DIFFERENT FROM EVERY OTHER, which is not decoration: two
    # counters whose lines both begin "not asked" print as two identical-looking
    # rows, and a reader scanning counts cannot tell which fact is which without
    # reading three lines of prose. Asserting the distinguishing words is what
    # keeps them distinguishable.
    # The phrases are the product's own table (`cli.SITUATION_SENTENCE`) and the
    # recognised-by-rules sentence; `00` amendment 7(c) removed `nothing_to_ask`
    # because every file is asked now.
    for count, field in ((22, 'nothing_to_read'), (33, 'declined'), (44, 'no_route'),
                         (55, 'over_ceiling'), (66, 'recognised_by_rules')):
        phrase = (cli.SITUATION_RECOGNISED_SENTENCE if field == 'recognised_by_rules'
                  else cli.SITUATION_SENTENCE[field])
        assert f"{count} {phrase[:30]}" in said, (count, field)


def test_a_zero_counter_still_prints_its_line():
    """The seven numbers are an arithmetic a person checks the block with.

    These counters PARTITION the roster -- every file the pass walked lands in
    exactly one of them -- so a line that disappears when it reads zero makes the
    sum unreadable and leaves a reader unable to tell a counter that was zero from
    a counter nobody printed. `104` §17.2 is what a number with no provenance
    costs; a missing line is the same cost paid silently.

    SABOTAGE: copy `_print_fact_pass`'s `if not count_: continue` into this
    printer. Every assertion below goes red at once.
    """
    said = _printed(_a_pass(recognised_by_rules=0, nothing_to_read=0,
                            declined=0, no_route=0, over_ceiling=0))

    for field in ('nothing_to_read', 'declined', 'no_route', 'over_ceiling'):
        assert f"0 {cli.SITUATION_SENTENCE[field][:30]}" in said, field


def test_the_four_hold_counts_reach_the_screen():
    """`104` §18 gap 24, point 3, stated as an assertion.

    The owner's ruling: "the posture sentences and the coverage table must tell
    the person: how many files the rules held, how many the local model released,
    how many it confirmed, how many it left held because it could not say."
    Measured on r19, the rules held 16 files, 5 of them rightly, and no line of
    any report said so -- a person read one word, "protected", and could not tell
    a hold the model had agreed with from a hold nothing had ever looked at.

    DIFFERENT NUMBERS ON PURPOSE, for `_a_pass`'s own reason: with `1` everywhere
    a test asserting "1 appears four times" passes while three lines are missing.

    SABOTAGE: delete the `_print_the_holds` call at the end of
    `_print_situation_pass`, or any one line of its loop.
    """
    said = _printed(_a_pass(holds=cli.PrecautionHolds(
        held=16, released=11, confirmed=2, still_held=3)))

    assert "the rules were holding 16 files on a safety term" in said
    assert "put to the model on this device" in said
    for count, phrase in ((11, "released by the model"),
                          (2, "confirmed by the model"),
                          (3, "still held because nothing could say")):
        assert f"{count} {phrase}" in said, (count, phrase)


def test_a_zero_hold_count_still_prints_its_line_where_anything_was_held():
    """The three divide `held`, so a line that vanishes at zero breaks the sum.

    The same argument as the six counters above, and it matters more here: "0
    released" and "0 confirmed" are what a person needs to see to know that every
    one of their held files is still held, rather than being left to infer it
    from a heading and two missing rows.

    SABOTAGE: add `if not count_: continue` to `_print_the_holds`' loop.
    """
    said = _printed(_a_pass(holds=cli.PrecautionHolds(
        held=4, released=0, confirmed=0, still_held=4)))

    assert "0 released by the model" in said
    assert "0 confirmed by the model" in said
    assert "4 still held because nothing could say" in said


def test_a_run_where_the_rules_held_nothing_prints_no_hold_block():
    """`_NOTHING_ASKED`'s rule, applied to this block: a heading over four zeros
    invites a person to wonder which of their files it is about, and the answer is
    none of them.

    The six counters above still print, because they are about every file the pass
    walked; this block is about a set that is empty.

    SABOTAGE: drop the `if not holds.held: return` guard, and every ordinary run
    gains a protected-holds heading about no file at all.
    """
    said = _printed(_a_pass())

    assert "Protected holds the model looked at" not in said
    assert "released by the model" not in said
    # And the block it sits under is untouched -- this is an addition, not a
    # replacement.
    assert f"22 {cli.SITUATION_SENTENCE['nothing_to_read'][:30]}" in said


def test_a_run_where_site_g_was_never_asked_prints_no_block_at_all():
    """`_NOTHING_ASKED`'s own ruling, one layer up, held to on the screen.

    "A run where site G was not asked and a run where it was asked and named
    nothing must not read the same downstream." Seven zeros under a header is
    precisely how the two would come to read the same, and the person would be
    told a model considered their files and declined -- about a run where no model
    was consulted at all.

    SABOTAGE: drop the `situation is _NOTHING_ASKED` guard. This assertion goes
    red, and the report starts claiming a pass that never ran.
    """
    assert _printed(cli._NOTHING_ASKED) == ""


def test_the_protected_counter_says_what_the_fact_pass_says_about_the_same_files():
    """`104` §18.2 gap 9: `no_route` "is the protected-file count the design
    wanted surfaced", and the fact pass already had a sentence for that fact.

    `target_for` returns nothing for a file P7 marked, on every locality, so
    nothing about it was assembled for site G either -- the same fact about the
    same files the fact pass's `WITHHELD_PROTECTED` line describes. Two sentences
    about one fact are how two blocks on one screen come to disagree.

    SABOTAGE: write `no_route` a sentence of its own. This assertion goes red the
    moment the two texts stop being one text.
    """
    # `104` §18.7 (9 Sep 2026): protected material reaches the local model, so
    # `no_route` stopped being the protected count and its sentence says what it
    # now is -- no target this site may use could take them.
    assert cli.SITUATION_SENTENCE["no_route"].startswith("no target")
    assert "protected" in cli.SITUATION_SENTENCE["no_route"]


def test_every_counter_site_g_leaves_behind_earns_a_sentence():
    """A counter with no sentence is a number this report silently drops.

    That is the defect gap 9 is about, so the check is made mechanical rather than
    remembered: `SITUATION_SENTENCE` is asserted against `SituationPass`'s own
    fields at import time, and this test says the same thing where a reader can
    see it fail.

    SABOTAGE: add an eighth counter to `SituationPass` and no sentence for it.
    `cli` fails to import and every test in this file errors -- which is the point:
    it cannot go unprinted quietly.
    """
    fields = {field.name for field in dataclasses.fields(cli.SituationPass)}
    # `104` §18 gap 24 added `holds`, a RECORD, not a counter: it does not
    # partition the roster the way the six do, so it is excused here and pinned
    # against its own sentences one test down.
    assert set(cli.SITUATION_SENTENCE) | {"named", "holds", "recognised_by_rules"} == fields
    # five since `00` amendment 7(c): every file is asked, so `nothing_to_ask` is gone
    assert len(cli.SITUATION_SENTENCE) == 4, (
        "six counted outcomes plus `named` in the header. Five when gap 9 was "
        "closed; `104` R-175 added `over_ceiling`, because a file skipped for time "
        "is a file this run did not decide about and the partition has to hold it")


def test_every_hold_the_rules_took_earns_a_sentence_too():
    """`104` §18 gap 24: the same rule, one record along.

    The owner's ruling is that the posture must tell a person how many files the
    rules held, how many the local model released, how many it confirmed and how
    many it left held because it could not say. A count with no sentence is the
    gap 9 defect wearing a protected file's clothes -- worse, because these four
    are the numbers that say whether somebody's medical record was let go.

    SABOTAGE: add a field to `PrecautionHolds` with no sentence for it. `cli`
    fails to import and every test in this file errors.
    """
    fields = {field.name for field in dataclasses.fields(cli.PrecautionHolds)}
    assert set(cli.HOLD_SENTENCE) | {"held"} == fields
    assert len(cli.HOLD_SENTENCE) == 3, (
        "three outcomes that partition `held`, with `held` itself in the block's "
        "own header -- exactly as `named` heads the block above")


# =====================================================================
# gap 9, second half: site G is named in the posture notice
# =====================================================================

class _Routing:
    """Enough of `TierRouting` to be announced, with the locality as a knob.

    Shaped on `tests/integration/test_cli_cloud_announcement.py`'s stub and never
    called for anything but a sentence: printing a notice opens no socket. The
    knob is what the other file's stub does not have -- it answers `"cloud"` for
    everything, which is right for the tests it was written for and cannot say
    anything about a site that only ever runs on this device.
    """

    def __init__(self, *, local: bool):
        self._local = local

    @property
    def locality(self) -> str:
        return cli.LOCAL if self._local else cli.CLOUD

    def model_id_for(self, site):
        return f"model-for-{site}"

    def locality_for(self, site):
        return self.locality

    def route_for(self, site, *, cloud_permitted: bool):
        from privacy.release import ModelTarget

        target = ModelTarget(locality=self.locality,
                             model_id=self.model_id_for(site),
                             provider="ollama" if self._local else "deepseek")
        return SimpleNamespace(model_target=target), target


class _Consent:
    permits_sending = True
    user_id = "jy"
    decided_at = "2026-06-14"


def _posture(routing, consent=None) -> str:
    out = io.StringIO()
    cli.announce_cloud_posture(routing, consent,
                               corpus_root=Path("/Users/jy/Desktop/Files"),
                               out=out)
    return " ".join(out.getvalue().split())


@pytest.mark.parametrize("consent", [None, _Consent()],
                         ids=["sending-off", "sending-on"])
def test_the_notice_names_the_site_that_decides_whether_a_file_may_be_sent(consent):
    """`104` §18.2 gap 9: site G was in no posture branch.

    `104` §17.14: G "is the site that decides whether a file may go to the cloud at
    all". A person deciding about sending was being shown every consequence of that
    decision and never the decision, and it is the same site doing the same work
    whether this folder's sending is on or off -- so it is named in both branches.
    A person who read it only on the runs where sending is on would have been told
    it is a thing about sending.

    SABOTAGE: delete either `_situation_site_sentence` call in
    `announce_cloud_posture`, and one half of this parametrisation goes red.
    Reverting `_QUESTION_OF_SITE` to its three cloud-eligible sites takes both.
    """
    said = _posture(_Routing(local=True), consent)

    assert "which situation a file is asked under" in said
    # `00` amendment 7(c): the clause about reaching the cloud belongs to the
    # GATE's sentence now; site G's says which situation, and where it is asked.
    assert "whether anything about it may be sent at all" in said or "SITUATION judgement" in said
    # The vocabulary of the branches around it, and the MODEL named -- a person
    # told "a model on your device" has been told less than one told which model.
    assert f"model-for-{G_SITUATION_SENSITIVITY} on this device" in said
    assert "do not leave it" in said


def test_a_deployment_with_no_model_on_this_device_is_told_nothing_about_site_g():
    """A sentence about work that did not happen, on the screen where being
    believed is the whole point.

    G's row is `ratified_local` (`104` §17.14), so `target_for` drops its cloud
    candidate for every file: a deployment with a key and no local model does not
    run this site, the pass is `_NOTHING_ASKED`, and no file is asked its own
    situation. Claiming G decided anything there would be the notice describing a
    decision nobody made.

    SABOTAGE: drop the `target.locality != LOCAL` guard from
    `_situation_site_sentence` and return the sentence unconditionally. Both
    assertions go red, and a cloud-only run starts being told a local model
    classified its files.
    """
    said = _posture(_Routing(local=False), _Consent())

    assert "which situation a file is asked under" not in said
    assert f"model-for-{G_SITUATION_SENSITIVITY}" not in said


def test_site_g_is_never_among_the_recipients_the_notice_names():
    """Naming G as a recipient would be the one untruth with a privacy cost.

    `observe_locality_permits` refuses G the internet under its own row, so it has
    no recipient to name; it earns a sentence of its own and no place in the list
    of models a file may be SENT to. `_SITES_THAT_MAY_SEND` is that list, spelled
    once because two lines read it -- a fourth member arriving in one and not the
    other is how site C came to be hidden for a day (`104` §17.13).

    SABOTAGE: add `G_SITUATION_SENSITIVITY` to `_SITES_THAT_MAY_SEND`. The first
    assertion goes red immediately; without it the notice would print "files that
    need a SITUATION judgement may be sent to ..." about a site whose text may not
    cross the internet, or name it under the cloud half's model id.
    """
    assert G_SITUATION_SENSITIVITY not in cli._SITES_THAT_MAY_SEND
    assert cli._SITES_THAT_MAY_SEND == (A_FACT, C_PLACEMENT, D_RESIDUAL)
    # `00` amendment 7(c): G's whole-library row is ratified for the cloud; the
    # site whose text never crosses is the gate.
    assert cli.observe_locality_permits(G_SITUATION_SENSITIVITY, cli.CLOUD)
    from llm_harness.vocabulary import H_RESTRICTED_KIND
    assert not cli.observe_locality_permits(H_RESTRICTED_KIND, cli.CLOUD)

    said = _posture(_Routing(local=True), _Consent())
    assert f"may be sent to model-for-{G_SITUATION_SENSITIVITY}" not in said


# =====================================================================
# gap 10: one closed sum over every indexed file
# =====================================================================

def _roster(monkeypatch, rows, *, protected=(), runs=(), unread=()):
    """Point the reconciliation at a roster with no database behind it.

    `_reconcile_the_roster` asks four questions of the connection -- the roster,
    the protected set, which files something was read out of, P4's runs for a
    content hash -- and NOTHING else, which is what makes it testable without
    building a corpus. Stubbing the four is cheaper than a scan and says more:
    each test states one shape of run and reads exactly the block a person sees.

    `unread` and not `read`, so a test names only the exception. Every file in a
    real roster has usually been read out of, and a helper whose default was the
    empty set would make every test that forgot the argument report a corpus of
    unreadable files -- passing for the wrong reason.
    """
    monkeypatch.setattr(cli, "corpus_roster", lambda conn, run_id: tuple(rows))
    monkeypatch.setattr(cli, "_protected_file_ids", lambda conn: set(protected))
    monkeypatch.setattr(cli, "_files_something_was_read_out_of",
                        lambda conn: {file_id for file_id, _hash in rows
                                      if file_id not in unread})
    monkeypatch.setattr(cli, "runs_for_content",
                        lambda conn, content_hash: tuple(
                            run for run in runs if run.hash == content_hash))


def _p4_run(file_id: str, content_hash: str, completeness: str,
            extractor_name: str = "pdf.text"):
    """One P4 run, as much of it as the reconciliation reads.

    `extractor_name` arrived with `104` §18.2 gap 22: `_runs_that_still_stand`
    drops a `deferred` run once the SAME extractor has produced a real one, so
    the double has to carry the field the rule keys on. It is defaulted because
    every test above this line is about one run per file, where the name cannot
    matter; the deferral tests below pass it explicitly.
    """
    return SimpleNamespace(file_id=file_id, hash=content_hash,
                           completeness=completeness,
                           extractor_name=extractor_name)


def _reconciled(monkeypatch, rows, *, verdicts=None, not_run=None,
                protected=(), runs=(), unread=()) -> str:
    _roster(monkeypatch, rows, protected=protected, runs=runs, unread=unread)
    out = io.StringIO()
    cli._reconcile_the_roster(None, run_id="scan-1", verdicts=verdicts or {},
                              not_run=not_run, out=out)
    return out.getvalue()


def _counts(printed: str) -> dict:
    """The six bucket lines, read out of the block and not off the whole report.

    THE BLOCK IS FOUND BY ITS OWN HEADER AND ENDED BY ITS OWN SUM. A report has
    other four-space-indented lines with a number at the front -- the plan's own
    folder lines are the ones that broke a first version of this helper -- and a
    test that scraped them would report buckets this build does not have and pass
    or fail for reasons that have nothing to do with coverage.
    """
    block = printed.split("Coverage: ")[-1].split(" = ")[0]
    return {label.strip(): int(count) for count, label in re.findall(
        r"^ {4}(\d+) (.+)$", block, flags=re.MULTILINE)}


def test_every_indexed_file_lands_in_exactly_one_bucket_and_the_sum_closes(
        monkeypatch):
    """`104` §18.2 gap 10, and the constitution's "coverage is sacred".

    Six files, one in each bucket, and the printed line adds up to six. The
    arithmetic is ON THE SCREEN and not only inside an assertion nobody sees pass:
    the rule this block enforces is one a person has to be able to CHECK, and six
    numbers with no sum beneath them is six numbers they would have to add up
    themselves to find out whether their folder was covered.

    SABOTAGE: make the reconciliation conditional the way it used to be -- called
    only from `_nothing_could_be_read_report`, so the rule holds on the one run
    where nothing was readable and on no ordinary run. Every assertion here goes
    red because the block is not printed at all.
    """
    rows = [(f"f{i}", f"h{i}") for i in range(6)]
    printed = _reconciled(
        monkeypatch, rows,
        protected=("f3",), unread=("f4",),
        # `104` §18.7: a protected file the pass ASKED is "asked a model" now, so
        # the one that lands on the protected line is one the pass never reached.
        verdicts={"f0": (cli.COVERAGE_SETTLED, None),
                  "f1": (cli.COVERAGE_ASKED, None),
                  "f2": (cli.COVERAGE_NOT_ASKED, cli.WITHHELD_UNCLASSIFIED),
                  "f5": (cli.DEFERRED, cli.BUDGET_DEFERRED)},
        runs=(_p4_run("f4", "h4", "unreadable"),))

    assert "Coverage: 6 files indexed." in printed
    assert _counts(printed) == {
        cli.COVERAGE_SETTLED: 1, cli.COVERAGE_ASKED: 1,
        cli.COVERAGE_NOT_ASKED: 1, cli.WITHHELD_PROTECTED: 1,
        cli.UNREADABLE: 1, cli.DEFERRED: 1}
    assert "1 + 1 + 1 + 1 + 1 + 1 = 6" in printed
    assert "every file is on exactly one line above" in printed


def test_a_protected_file_the_pass_never_reached_is_counted_protected(monkeypatch):
    """The standing rule: marked and counted, never silently omitted -- and never
    filed under somebody else's word. Amended by `104` §18.7 (9 Sep 2026):
    protected material reaches the LOCAL model, so a protected file the pass ASKED
    is "asked a model" (the second half below), and the protected line is for a
    protected file the pass never reached. Reported as "unreadable" it would say
    the product tried to read it and failed; reported as "settled by rule" it
    would vanish into the largest bucket on the screen.

    SABOTAGE: drop the `file_id in protected` arm from `_reconcile_the_roster`.
    The first half's protected count goes to zero and the file reappears as
    unreadable. Put that arm back ABOVE `file_id in verdicts` and the second
    half goes red instead: the file the local model was asked about is hidden
    under "protected", which says bytes never reached a model when they did.
    """
    unreached = _reconciled(
        monkeypatch, [("f0", "h0")], protected=("f0",), unread=("f0",),
        verdicts={}, runs=(_p4_run("f0", "h0", "unreadable"),))
    counts = _counts(unreached)
    assert counts[cli.WITHHELD_PROTECTED] == 1
    assert counts[cli.COVERAGE_ASKED] == 0
    assert counts[cli.UNREADABLE] == 0

    asked = _reconciled(
        monkeypatch, [("f0", "h0")], protected=("f0",), unread=("f0",),
        verdicts={"f0": (cli.COVERAGE_ASKED, None)},
        runs=(_p4_run("f0", "h0", "unreadable"),))
    counts = _counts(asked)
    assert counts[cli.COVERAGE_ASKED] == 1
    assert counts[cli.WITHHELD_PROTECTED] == 0


def test_the_sum_and_the_sent_line_above_it_agree_about_one_file(monkeypatch):
    """Two blocks on one screen must not contradict each other about a file.

    A file the fact pass counted among "N files sent" and this block called
    "unreadable" would leave a person with two statements about their file and no
    way to tell which was lying. So the fact pass's own verdict outranks P4's
    record, and P4's record answers only for files the pass never reached.

    SABOTAGE: read `runs_for_content` before `verdicts` in
    `_reconcile_the_roster`. This file moves to `unreadable`, the sum still
    closes -- which is why the sum alone is not enough of a test -- and the screen
    starts disagreeing with itself.
    """
    printed = _reconciled(
        monkeypatch, [("f0", "h0")], unread=("f0",),
        verdicts={"f0": (cli.COVERAGE_ASKED, None)},
        runs=(_p4_run("f0", "h0", "unreadable"),))

    assert _counts(printed)[cli.COVERAGE_ASKED] == 1
    assert _counts(printed)[cli.UNREADABLE] == 0


def test_a_run_with_no_model_says_so_instead_of_calling_the_files_settled(
        monkeypatch):
    """The four early returns of `_model_fact_pass` are ordinary ways for a run to
    go, and the sum has to print on every one of them.

    "Settled by rule" would be false about those files' open fields -- nothing
    settled them -- and `00`:259 names that exact untruth: "the false impression
    that an unprocessed file was understood and found unimportant". The reason
    leaves the pass with the return instead of being dropped at it.

    SABOTAGE: drop `fact_pass_not_run[0] = NOT_RUN_NO_MODEL` from the `routing is
    None` return. The files then reach no bucket at all and the run refuses with
    `FileAbsentFromEveryEntry` -- which is the honest failure, and this test's
    assertions still go red.
    """
    printed = _reconciled(
        monkeypatch, [("f0", "h0"), ("f1", "h1")],
        not_run=cli.NOT_RUN_NO_MODEL,
        runs=(_p4_run("f0", "h0", "complete"),
              _p4_run("f1", "h1", "complete")))

    counts = _counts(printed)
    assert counts[cli.COVERAGE_NOT_ASKED] == 2
    assert counts[cli.COVERAGE_SETTLED] == 0
    assert "no model is configured for this run" in " ".join(printed.split())
    assert cli.NOT_RUN_NO_MODEL in printed


def test_a_file_a_per_scan_ceiling_deferred_is_deferred_and_not_unreadable(
        monkeypatch):
    """`104` §18.2 gap 22, on the line a person actually reads.

    `00`:259 asks the interface to keep two sentences apart: *"89 scanned PDFs
    deferred after the OCR limit; 18 files remain unreadable."* One says a budget
    ran out. The other says the product tried and could not.

    §8.6's per-scan ceilings produce a file whose only routed run is the
    deferral, and a deferral carries no observations at all (P4's
    `ZERO_OBSERVATION_COMPLETENESS`). So the reconciliation's "was anything read
    out of it" test finds nothing for it -- `unread` below -- and before this
    patch it would have landed on the unreadable line. That tells a person their
    photo is corrupt when it was never opened, which is the precise false
    impression `00`:259 exists to prevent.

    SABOTAGE: drop the `_budget_deferred` half of the `file_id not in read`
    clause. The deferred count goes to zero, the unreadable count goes to one,
    and the sum still closes -- which is why this needs its own test rather than
    resting on the closed-sum check.
    """
    printed = _reconciled(
        monkeypatch, [("f0", "h0")], not_run=None, unread=("f0",),
        runs=(_p4_run("f0", "h0", "complete", extractor_name="filesystem"),
              _p4_run("f0", "h0", "deferred", extractor_name="image.metadata")))

    counts = _counts(printed)
    assert counts[cli.DEFERRED] == 1
    assert counts[cli.UNREADABLE] == 0


def test_a_deferral_a_later_scan_answered_stops_speaking_for_the_file(
        monkeypatch):
    """The same line, one scan later, and the false sentence in the other
    direction.

    P4 supersedes runs and never deletes them, so the ceiling's `deferred` row is
    still there after a scan with the ceiling lifted reads the file in full. And
    `WORST_FIRST` ranks `deferred` above `complete`, so without
    `_runs_that_still_stand` the coverage line would call a fully-read file
    deferred for the rest of the database's life. `00`:259's buckets describe
    what is true now.

    The pairing with `orchestrator._already_extracted` is the point: that
    function refuses to let a deferral settle a file, precisely so the next scan
    re-reads it. If the report then kept saying "deferred", the product would be
    doing the work and denying it.

    SABOTAGE: have `_runs_that_still_stand` return `mine` unfiltered. The
    deferred count goes to one and the settled line loses the file.
    """
    printed = _reconciled(
        monkeypatch, [("f0", "h0")], not_run=cli.NOT_RUN_NO_MODEL,
        runs=(_p4_run("f0", "h0", "deferred", extractor_name="image.metadata"),
              _p4_run("f0", "h0", "complete", extractor_name="image.metadata")))

    counts = _counts(printed)
    assert counts[cli.DEFERRED] == 0
    assert counts[cli.COVERAGE_NOT_ASKED] == 1


def test_a_deferral_by_one_extractor_is_not_answered_by_another(monkeypatch):
    """Per `extractor_name`, and that is the whole restraint on the rule above.

    An OCR deferral says nothing about whether the IMAGE extractor ran, and a
    completed image run cannot speak to it. Folding the two would let any file
    with one successful extractor hide every ceiling that ever stopped a
    different one -- which is the silence §8.6 exists to break.

    SABOTAGE: drop the `extractor_name` condition from `_runs_that_still_stand`
    and answer a deferral with any non-deferred run. This test's deferred count
    goes to zero and the file's OCR ceiling vanishes from the report.
    """
    printed = _reconciled(
        monkeypatch, [("f0", "h0")], not_run=None, unread=("f0",),
        runs=(_p4_run("f0", "h0", "complete", extractor_name="image.metadata"),
              _p4_run("f0", "h0", "deferred", extractor_name="ocr")))

    assert _counts(printed)[cli.DEFERRED] == 1


def test_a_file_that_reaches_no_bucket_refuses_the_report(monkeypatch):
    """`assert_every_file_accounted`, reachable at last, and raising.

    `review_surface/progress.py`'s own docstring gives the reason it raises rather
    than logs: "a file that reaches no entry has been silently dropped from the
    user's picture of their own corpus, and a progress line that omits it looks
    complete". `104` §18.2 gap 10 is that function being reachable only when
    nothing was readable; this is it doing its job on an ordinary roster.

    SABOTAGE: replace the `assert_every_file_accounted` call with the local sum
    check alone, or drop it entirely. This test stops raising and a short sum
    prints as though it were closed.
    """
    with pytest.raises(FileAbsentFromEveryEntry) as refused:
        _reconciled(monkeypatch, [("f0", "h0")], not_run=None,
                    runs=(_p4_run("f0", "h0", "complete"),))

    assert "f0" in str(refused.value)


def test_one_file_counted_twice_refuses_the_report_as_well(monkeypatch):
    """The other direction, which P13's rule cannot see.

    Two entries that both hold one file satisfy "no indexed file is absent from
    every entry" and still make the printed sum overshoot the roster, and a sum a
    person cannot trust is worse than no sum. `FileInTwoBuckets` is the mirror
    refusal, and a duplicated bucket in `_COVERAGE_ORDER` is the cheapest way to
    produce the shape it guards against.

    SABOTAGE: delete the `counted != total` check and keep only
    `assert_every_file_accounted`. This test stops raising, and a run whose buckets
    overlap prints `1 + 1 + ... = 6` over a roster of five.
    """
    monkeypatch.setattr(cli, "_COVERAGE_ORDER",
                        (cli.COVERAGE_SETTLED, *cli._COVERAGE_ORDER))

    with pytest.raises(cli.FileInTwoBuckets) as refused:
        _reconciled(monkeypatch, [("f0", "h0")],
                    verdicts={"f0": (cli.COVERAGE_SETTLED, None)})

    assert "exactly one" in str(refused.value)


def test_an_empty_bucket_still_prints_its_zero(monkeypatch):
    """All six lines, always, for the reason the situation block prints its zeros.

    The sum is what a person checks the report with, and a bucket that vanishes
    when it is empty leaves them unable to tell "no file was protected" from "this
    build does not report protected files".

    SABOTAGE: skip empty buckets in the print loop. Five of these six assertions
    go red on this one-file run.
    """
    printed = _reconciled(monkeypatch, [("f0", "h0")],
                          verdicts={"f0": (cli.COVERAGE_SETTLED, None)})

    assert set(_counts(printed)) == set(cli._COVERAGE_ORDER)
    assert "1 + 0 + 0 + 0 + 0 + 0 = 1" in printed


def test_an_ordinary_run_with_no_key_prints_the_closed_sum(tmp_path, monkeypatch):
    """END TO END, because the unit tests above stub the connection.

    `104` §18.2 gap 10 is about the ORDINARY run, so one of these tests has to be
    one: a real corpus, a real scan, no key, and the block on the real screen.
    Without it every assertion above could hold while the reconciliation was never
    wired into `downstream` at all.

    SABOTAGE: delete the `_reconcile_the_roster` call after `_model_fact_pass` in
    `downstream`. The unit tests all still pass; this one goes red.
    """
    from readers.model_deepseek import CREDENTIAL_NAME
    from readers.model_routing import MODEL_NAME_OF_TIER

    for name in (CREDENTIAL_NAME, *MODEL_NAME_OF_TIER.values()):
        monkeypatch.delenv(name, raising=False)
    corpus = tmp_path / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS 1401 syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026.\n")
    (corpus / "PHYS 1401 homework 2.txt").write_text(
        "PHYS 1401 Homework 2\n\nSpring 2026.\n")

    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "jy",
                     "--database", str(tmp_path / "holder" / "plan.sqlite")],
                    out=out)
    printed = out.getvalue()

    assert code == 0
    assert "Coverage: 2 files indexed." in printed
    counts = _counts(printed)
    assert set(counts) == set(cli._COVERAGE_ORDER)
    assert sum(counts.values()) == 2
    assert "= 2, and every file is on exactly one line above" in printed
