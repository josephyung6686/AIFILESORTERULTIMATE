# tests/test_cli.py
"""The command a person actually types.

`--situation` and `--label` are required on a real run and that is deliberate:
nothing upstream can answer them and the command will not guess. But a flag whose
whole purpose is to tell you what to pass to `--situation` cannot itself require
`--situation`, or there is no way in.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402


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
    assert "academic.coursework" in lines, lines[:20]
    # Printed for a human to copy into `--situation`, so no internal prefix.
    assert not [line for line in lines if line.startswith("recognition:")]


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
    assert "never summarised away" in printed, printed


def test_a_protected_group_is_never_the_one_summarised_away():
    """The negative twin, and the standing rule arriving as a usability change.

    Shortening the list is fine. Shortening the part that says what was marked
    protected and left alone is the exact harm the rule forbids -- so a protected
    group is listed in full however long it is, and sorts first.
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

    for n in range(40):
        assert f"secret-{n:02d}.key" in printed, (
            f"secret-{n:02d}.key was summarised away; a protected file is "
            "marked and counted and never silently omitted")
    ordinary = [name for name in names.values()
                if name.startswith("note-") and name in printed]
    assert len(ordinary) < 40, "the ordinary list should still be shortened"
    assert printed.index("secret-00.key") < printed.index("note-00.txt")


def test_the_protected_containers_block_survives_the_regrouping():
    """Count, name, path and sentence, all four, unchanged.

    This is the standing rule made visible. Every other part of the report may be
    grouped, renamed or shortened; this one is what the grouping must not reach.
    """
    run, names = _coursework()
    run.protected_areas = (_area("Notes.app", "/tmp/demo/Notes.app"),)
    printed = _printed(run, names)

    assert "Protected containers: 1 marked, none opened" in printed
    assert "Notes.app  (untouched_protected)" in printed
    assert "/tmp/demo/Notes.app" in printed
    assert UNTOUCHED in printed
    # And it is the first thing, not a line at the bottom of a long report.
    assert printed.index("Protected containers") < printed.index("Coursework")


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
    assert "X12345678" not in printed, (
        f"a passport number is printed as a destination:\n{printed}")
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
