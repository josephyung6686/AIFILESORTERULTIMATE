"""The third leg: when the product cannot settle a FILE, it asks the person.

The product already asks about the SHAPE of a branch (`branch:Coursework`) and
about what a repeated identifier MEANS (`reading.organization:E1006`). It has
never asked about a file. On a 199-file corpus it left 73% of them unplaced and
raised zero questions about any of them -- and the report printed the heading
*"Waiting for you to say what these are"* over ninety-three filenames while
offering no gesture with which to say.

**Which files, and why these.** Measured on `.groundtruth/corpus` against the
labels, over the placement decisions of a real run:

    not placed                                   57 files, 27 'ask the person' (47%)
    not placed & nothing readable recovered       3 files,  3 'ask the person' (100%)

and with the trigger live, 7 files corpus-wide carry a question and 6 of them are
files the labeller independently marked "the right answer is ask the person" --
86%, against a base rate of 41%. The ground truth's own words for these are *"a
scan or export with no text layer and a filename that is a scanner counter or a
content hash. Nothing but the person knows what it is."* That is the trigger: the
product OPENED the file and no text-producing extractor recovered anything, so
there is nothing for it to be wrong about and nobody but the person to ask.

The count moves as extraction improves, and DOWN is the right direction: a file
whose text the product learns to recover stops being a question, because it stops
being one only the person can answer. It was 24 files before the extractors began
recovering prose from SVG and PNG; it is 7 now.

**What is deliberately NOT the trigger, and the measurement that killed it.** Every
abstaining decision carries a ranked `alternatives` list and `requires_review:
true`, which reads like a multiple-choice question with the answers already
computed. It is not one. On the real corpus all 181 abstentions score 0.286
against a support threshold of 0.5, and NO file anywhere has two candidates above
that threshold -- the score distribution is 0.286 or 0.714 and nothing between. So
`alternatives` is not a set of competing destinations; it is the person's own
existing top-level folders (`Desktop/MONEY`, `Desktop/Vaccine records`) tied at a
score none of them earned. Asking "which of these seven?" over 62 files would be
43% precise against a 41% base rate -- noise with a question mark on it, and worse
than the silence it replaced.

Those two scores are the measurement's own and are left in the units it was taken
in: it was read under `cli-support-v1`, whose scale reserved two sevenths for
channels nothing produced, and under `cli-support-v2` the same two populations read
0.4 and 1.0 (`104` §18.2 gap 13). What the finding turns on -- that the ties are
the person's own top-level folders rather than competing destinations -- is a fact
about `alternatives` and not about the denominator, so gap 13 does not touch it.
Re-measure before quoting either pair as current.

**THE FOURTH LEG, AND `104` §18.2 GAP 15 IS WHERE IT WAS MISSING.** Everything
above is about a file nothing could be read out of. §6.9 has a second kind of
question and it is the opposite case: a file the run read plenty about, which has
accepted membership in two packets, and which the tree offers no shared branch
for. `00`:113 permits two answers there -- "it should abstain OR ASK THE USER TO
CHOOSE A PRIMARY HOME" -- and this deployment wired `lambda node_ids: pv.ABSTAIN`,
so only one of them was ever reachable. The tests at the foot of this file are the
other one.

**One question per folder, not one per file.** `66` §14 asks for a question on a
"repeated ambiguity", and `triggers.tied_readings` already reads that as *"four
files of one course tying the same way is one ambiguity, asked once"*. Unreadable
assets sitting together in one folder are one ambiguity too, so the question is
scoped to the FOLDER and every file under it carries the same `Ask`. On the current
corpus that buys less than it looks: six questions cover seven files, because the
files the extractors still cannot read are scattered rather than clustered. It
bought more before extraction improved -- eight of them were one folder of saved
web-page assets -- and it is kept because a corpus with a folder of scans in it is
the ordinary case, not the exceptional one.
"""
from __future__ import annotations

import io
import sqlite3

import pytest

import cli

#: `104` SF-3. A group is a DRAFT until somebody decides it (see `test_cli.py`'s
#: own docstring for the ruling); the tests below that read placement decisions,
#: structural answers, or the "Waiting for you to choose" report have to type the
#: accept, same as a person does, or none of that is computed yet.
ACCEPTS_THE_PROPOSAL: tuple[str, ...] = ("--accept-groups",)


def _unreadable_corpus(tmp_path):
    """A folder the product can open and read nothing out of, beside one it can.

    The bytes matter. `Notes.txt` gives the run a file it CAN read, so a report
    that asked about everything would be caught by the same fixture that proves
    it asks about something.
    """
    corpus = tmp_path / "corpus"
    (corpus / "scans").mkdir(parents=True)
    # PNG magic and nothing else: opened, recognised as an image, no text.
    for name in ("IMG_0001.png", "IMG_0002.png", "IMG_0003.png"):
        (corpus / "scans" / name).write_bytes(
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    (corpus / "Notes.txt").write_text(
        "Lecture Notes\n\nLecture notes for PHYS1401.\n")
    return corpus


def _run(argv, out=None):
    out = out if out is not None else io.StringIO()
    code = cli.main(argv, out=out)
    return code, out.getvalue()


def _argv(corpus, database, *extra):
    return [str(corpus), "--situation", "academic.coursework",
            "--label", "Coursework", "--user", "jy",
            "--database", str(database), *extra]


def test_a_file_the_product_could_not_read_becomes_a_question(tmp_path):
    """The defect, stated as a property: the product opened three files, got
    nothing readable out of any of them, and said nothing to the person.

    `66` §12 permits a question "only when a specific decision is blocked". A file
    whose every extractor came back empty blocks the most specific decision there
    is -- what the thing IS -- and the product's own report already says so under
    "Waiting for you to say what these are". This asserts the sentence has a
    gesture under it.
    """
    corpus = _unreadable_corpus(tmp_path)
    _, printed = _run(_argv(corpus, tmp_path / "plan.sqlite", *ACCEPTS_THE_PROPOSAL))

    joined = " ".join(printed.split())
    assert "scans" in joined, printed
    assert "--answer home:scans=" in joined, printed
    # §14: the person can see WHY it arose, and §12: what it will not do.
    assert "nothing readable" in joined, printed
    assert "will not move, rename or delete anything" in joined, printed


def test_a_question_about_the_folder_that_was_scanned_names_that_folder(tmp_path):
    """Unreadable files at the TOP of the scanned folder are scoped to `.`, and
    `.` is what a real screen printed: "Where should the files in . go?" The
    scope stays `.` -- the answer is stored against it -- and the words a person
    reads name the folder they typed."""
    corpus = tmp_path / "Downloads"
    corpus.mkdir()
    for name in ("IMG_0001.png", "IMG_0002.png"):
        (corpus / name).write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    # Two readable files of two kinds, so the plan has two folders to offer:
    # one destination is not a choice and raises no question at all.
    (corpus / "Notes.txt").write_text("Lecture Notes\n\nLecture notes for PHYS1401.\n")
    (corpus / "PHYS1401 syllabus.txt").write_text(
        "PHYS1401 Syllabus\n\nSpring 2026. Course syllabus for PHYS1401.\n")

    _, printed = _run(_argv(corpus, tmp_path / "plan.sqlite", *ACCEPTS_THE_PROPOSAL))

    joined = " ".join(printed.split())
    assert "Where should the files in Downloads go?" in joined, printed
    assert "2 files in Downloads were opened" in joined, printed
    assert "files in . " not in joined, printed
    # The answer still records against the scope the product scans by.
    assert "--answer home:.=" in joined, printed


def test_one_question_covers_the_whole_folder(tmp_path):
    """§14's "repeated ambiguity", asked once.

    Three files, one question. A product that asked three times would be asking
    the same thing three times, and a person answering it three times would
    rightly conclude nobody was listening.
    """
    corpus = _unreadable_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    _run(_argv(corpus, database, *ACCEPTS_THE_PROPOSAL))

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    homes = [dict(r) for r in conn.execute(
        "SELECT question_id, scope FROM structural_questions "
        "WHERE question_id LIKE 'home:%'")]
    conn.close()

    assert len(homes) == 1, homes
    assert homes[0]["scope"] == "folder:scans", homes


def test_every_file_the_question_covers_carries_it_on_its_own_decision(tmp_path):
    """The question is about a FILE, and each file's record has to say so.

    A question printed on a screen and recorded nowhere against the files it is
    about is a question the rest of the product cannot see. `placement_decisions`
    has carried an `ask` slot and an `ask_user` outcome since P11 was built, and
    nothing has ever filled either.
    """
    import json

    corpus = _unreadable_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    _run(_argv(corpus, database, *ACCEPTS_THE_PROPOSAL))

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    asked = [json.loads(r["payload"]) for r in conn.execute(
        "SELECT payload FROM placement_decisions WHERE superseded_by IS NULL")]
    conn.close()

    carrying = [d for d in asked if d["ask"] is not None]
    assert len(carrying) == 3, [d["outcome"] for d in asked]
    for decision in carrying:
        assert decision["outcome"] == "ask_user", decision["outcome"]
        assert len(decision["ask"]["options"]) >= 2, decision["ask"]


def test_a_run_that_can_read_everything_asks_about_no_file(tmp_path):
    """The twin that keeps §12's promise. 73% of a real corpus goes unplaced, and
    a product that turned that into 145 questions would be worse than the silence
    it replaced -- nobody answers 145 questions.

    So the trigger is not "unplaced". It is "opened, and nothing readable came
    out", and a corpus where everything reads must produce no file question at
    all however little of it gets placed.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "Notes.txt").write_text(
        "Lecture Notes\n\nLecture notes for PHYS1401.\n")
    (corpus / "Essay.txt").write_text(
        "Essay\n\nAn essay written for ENGL2001.\n")

    database = tmp_path / "plan.sqlite"
    _, printed = _run(_argv(corpus, database))

    conn = sqlite3.connect(database)
    homes = list(conn.execute("SELECT question_id FROM structural_questions "
                              "WHERE question_id LIKE 'home:%'"))
    conn.close()
    assert homes == [], (homes, printed)


def test_a_protected_file_is_counted_in_the_question_and_never_named(tmp_path):
    """PRIVACY. A question is printed on a screen somebody else can see.

    The report already draws this line for the protected files it holds: "Their
    names are not printed here, because a list of them is the part of this report
    least safe to have on a screen somebody else can see." A question about a
    folder holding a protected file must keep the same line -- and must not
    silently drop it either, because "marked and counted, never opened, never
    silently omitted" is the standing rule.

    13 Sep 2026 (`3b4ac747`, `104` §18.60): the ABSTENTION arm's rules hold now
    needs a corroborated body term or a checksummed identifier -- one filename
    term alone (`passport scan.png`) matches `identity` on exactly one authored
    term, `never_alone`'s arity gate leaves it an `Abstention("no_corroboration",
    ...)`, and `_precaution`'s new `readings` comprehension is zone-blind: it asks
    `_corroborated` of that term regardless of where it sat, and a bare filename
    has no second finding to offer. So the file reaches no verdict at all -- not
    held, not ordinary -- rather than the protected row this pin means to
    exercise. Two of `identity`'s own work-type terms in the same naming zone
    (the filename) is arity two instead: `explain` RECOGNISES the schema outright
    on the file's own words, and the hold is the winning schema's own handling
    (`_recognised_hold`'s first branch, `basis='safety_domain'`) -- a path the 13
    Sep change never touched, because it never reaches the abstention arm at all.
    """
    corpus = tmp_path / "corpus"
    (corpus / "scans").mkdir(parents=True)
    for name in ("IMG_0001.png", "IMG_0002.png"):
        (corpus / "scans" / name).write_bytes(
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    # Two of `identity`'s own work-type terms in one naming zone (the filename)
    # -- `passport` and `identity card` -- so the schema is RECOGNISED outright
    # (arity two) and protected without needing corroboration.
    (corpus / "scans" / "passport identity card scan.png").write_bytes(
        b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    (corpus / "Notes.txt").write_text(
        "Lecture Notes\n\nLecture notes for PHYS1401.\n")

    import json

    database = tmp_path / "plan.sqlite"
    _, printed = _run(_argv(corpus, database, *ACCEPTS_THE_PROPOSAL))

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        "SELECT prompt, evidence_context, unlocks, options FROM "
        "structural_questions WHERE question_id LIKE 'home:%'")]
    protected = [dict(r) for r in conn.execute(
        "SELECT file_id FROM classifications "
        "WHERE protected = 1 AND superseded_by IS NULL")]
    conn.close()

    assert protected, "the fixture must actually produce a protected file"
    for row in rows:
        blob = " ".join(str(value) for value in row.values())
        assert "passport" not in blob.lower(), row
        assert "IMG_0001" not in blob, row
    # It is COUNTED, though. "Marked and counted, never opened, never silently
    # omitted" is the whole rule; a question that quietly described a folder of
    # three files as a folder of two would be keeping the last third of it.
    assert any("1 more is protected material" in row["evidence_context"]
               for row in rows), rows
    # And the file itself must not carry the question. This is the half the
    # question TEXT cannot protect: an `ask_user` decision is a request for
    # attention, and the report lists what it holds BY NAME under "Waiting for
    # you to choose where these go". A protected file reaching that list is its
    # name on the screen however carefully the prompt was written.
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    decisions = [json.loads(r["payload"]) for r in conn.execute(
        "SELECT payload FROM placement_decisions WHERE superseded_by IS NULL")]
    conn.close()
    for decision in decisions:
        if decision["ask"] is None:
            continue
        assert not decision["privacy"]["protected"], (
            "a protected file was asked about; the report prints the name of "
            "everything under that heading", decision)


def test_an_answer_about_a_folder_is_remembered_and_places_the_files(tmp_path):
    """THE LOOP, for a file question. `66` §12: an answer outlives the run.

    Modelled on `test_an_answer_is_remembered_and_changes_the_next_run`, which is
    the same property for a reading question. Run one asks. The person answers.
    Run two does not ask again, and the files the product could not read are
    filed where the person said.
    """
    import json

    corpus = _unreadable_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    argv = _argv(corpus, database, *ACCEPTS_THE_PROPOSAL)

    _, first = _run(argv)
    assert "--answer home:scans=" in " ".join(first.split()), first

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    options = json.loads([dict(r) for r in conn.execute(
        "SELECT options FROM structural_questions "
        "WHERE question_id = 'home:scans'")][0]["options"])
    conn.close()
    chosen = options[0]["option_id"]

    code, answered = _run(argv + ["--answer", f"home:scans={chosen}"])
    assert code == 0, answered

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    stored = [dict(r) for r in conn.execute(
        "SELECT question_id, option_id, state FROM structural_answers")]
    decisions = [json.loads(r["payload"]) for r in conn.execute(
        "SELECT payload FROM placement_decisions WHERE superseded_by IS NULL")]
    # The answer stores a folder CHAIN, and every run mints new node ids for the
    # same folders -- so the check has to be that the file landed in the folder
    # the person named, not that it landed on the id they were shown.
    nodes = {r["node_id"]: (r["display_label"], r["parent_node_id"])
             for r in conn.execute("SELECT node_id, display_label, "
                                   "parent_node_id FROM tree_nodes")}
    conn.close()

    def chain_of(node_id):
        parts, walk = [], node_id
        while walk is not None and walk in nodes:
            label, walk = nodes[walk]
            parts.append(label)
        return "/".join(reversed(parts))

    assert any(r["question_id"] == "home:scans" and r["state"] == "confirmed"
               and r["option_id"] == chosen for r in stored), stored
    # The record has to SAY the person decided. `exact fact match` here would be
    # the product telling somebody it found something when what it did was ask
    # them, and P13 shows a confidence class back as the reason a file moved.
    placed = [d for d in decisions
              if d["confidence_class"] == "user chose the destination"]
    assert len(placed) == 3, (
        "the person said where these go and nothing was filed there; the "
        "answer was stored and never consumed")
    for decision in placed:
        assert decision["outcome"] == "place", decision
        assert decision["evidence_type"] == "user_confirmed", decision
        assert chain_of(decision["destination"]["node_id"]) == chosen, decision
    # And the question does not come back.
    assert "--answer home:scans=" not in " ".join(answered.split()), answered


# --- `104` §18.2 gap 15: the two-homes case is a question ------------------------


def test_the_two_homes_selector_asks_when_there_are_two_homes_to_offer():
    """§6.9's selector, which used to be `lambda node_ids: pv.ABSTAIN`.

    `104` §18.2 gap 15. The comment above the lambda read "there is no screen here
    to ask on", which stopped being true when `WAITING_ON_AN_ANSWER` became a
    review set of its own and `review_surface.items.render_state_for` gained
    `ask_user_state`. A file with accepted membership in two packets is the case
    `00`:113 names, and abstaining on it told the person "no folder matched" about
    a file two folders matched.

    SABOTAGE: put the unconditional `pv.ABSTAIN` back -- a file in two packets is
    recorded `no_shared_branch`, joins the pile of files nothing could be said
    about, and the person is never offered the choice that is theirs to make.
    """
    from placement import vocabulary as pv

    assert cli._ask_when_there_are_two_homes_to_offer(
        ("n-columbia", "n-duke")) == pv.ASK_USER
    assert cli._ask_when_there_are_two_homes_to_offer(
        ("n-columbia", "n-duke", "n-nyu")) == pv.ASK_USER


def test_a_question_with_one_option_is_a_placement_wearing_a_question_mark():
    """The abstention that survives gap 15, and `placement.records.Ask`'s own words.

    `Ask.__post_init__` refuses fewer than two options, so a question this
    deployment cannot put honestly is not put -- §6.9's abstention is still one of
    its three legal answers and this is where it is chosen.

    SABOTAGE: return `pv.ASK_USER` unconditionally -- `resolve_multi_home` hands
    the ids to `_multi_home_decision`, which mints an `Ask`, and
    `MalformedPlacementRecord` ends the run on a file that should simply have
    abstained.
    """
    from placement import vocabulary as pv

    assert cli._ask_when_there_are_two_homes_to_offer(("n-columbia",)) == pv.ABSTAIN
    assert cli._ask_when_there_are_two_homes_to_offer(()) == pv.ABSTAIN


def test_gap15_a_question_can_be_scoped_to_the_one_file_a_two_homes_ask_is_about():
    """DESIGN: a two-homes question is about ONE FILE, so the scope it is
    recorded under names one file and nothing else.

    MEASUREMENT: `questions.vocabulary.SCOPES` carries `file`. It used to be
    corpus, organization, branch and folder, and `HOME_KIND` -- the kind whose
    answer `chosen_destination` reads back into a destination -- is
    `SCOPE_FOLDER`. Recording a two-homes question under the file's folder would
    make one answer govern every file in that folder, which
    `chosen_destination`'s own docstring rules out in as many words and which
    `104` R-86 was raised to fix.

    THE BLOCKER THIS PINNED IS GONE and the rest of the shape landed with it:
    `cli._two_home_questions` mints a `home:`-kind question per file after
    placement, with the two node ids resolved to folder chains through the same
    map `already_answered` reads an answer back through, so the panel's existing
    `--answer <id>=<option>` line settles it. The two tests below measure that
    end of it; this one measures the vocabulary member it stands on.
    """
    from questions.vocabulary import SCOPE_FILE, SCOPES

    assert SCOPE_FILE in SCOPES
    assert SCOPE_FILE == "file"


def _two_homed_run(node_ids=("n-course", "n-thesis"), file_id="f-thesis"):
    """A finished run with one `ask_user` decision, and nothing else it needs.

    `_two_home_questions` reads exactly three things -- the frozen tree's nodes,
    the run's decisions, and each decision's `ask` -- so the double is those and
    no more. A fuller fixture would make the test pass for reasons the function
    does not have.
    """
    import types

    def node(node_id, label, parent):
        return types.SimpleNamespace(node_id=node_id, display_label=label,
                                     parent_node_id=parent,
                                     accepts_placement=True)

    frozen = types.SimpleNamespace(nodes=(
        node("n-cw", "Coursework", None),
        node("n-course", "W3134", "n-cw"),
        node("n-res", "Research", None),
        node("n-thesis", "Thesis", "n-res"),
    ))
    from placement import vocabulary as pv
    from placement.records import Ask

    decision = types.SimpleNamespace(
        outcome=pv.ASK_USER,
        ask=Ask(question="Which of these two is the home for this file?",
                options=tuple(node_ids)),
        subject=types.SimpleNamespace(file_id=file_id, member_file_ids=()))
    return types.SimpleNamespace(
        tree=types.SimpleNamespace(tree=frozen),
        placement=types.SimpleNamespace(decisions=(decision,)))


def test_gap15_the_two_homes_question_is_scoped_to_its_file_and_offers_chains():
    """DESIGN: the Ask reaches the panel as a recorded question whose options are
    folder chains, and whose answer reaches ONLY the file it was asked about.

    MEASUREMENT: given one `ask_user` decision carrying two node ids,
    `cli._two_home_questions` records a `home:`-kind question scoped
    `file:<file id>`, whose options are the two DISPLAY PATHS rather than the raw
    node ids, and answering one makes `chosen_destination` return that chain for
    this file and `None` for the file beside it. That last pair is the loop
    closing: the option a person picks resolves back through the same chain map
    the run places on, and an answer about one file does not travel to another.

    SABOTAGE: record the question under `folder:<its folder>` -- every assertion
    about the option ids still passes and the last two fail, because the answer
    now reaches a file nobody asked about.
    """
    from questions.records import StructuralAnswer
    from questions.schema import create_questions_schema
    from questions.store import (
        chosen_destination, open_questions, record_answer, questions_for,
    )
    from questions.vocabulary import CONFIRMED, SCOPE_FILE

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_questions_schema(conn)

    cli._two_home_questions(conn, _two_homed_run(),
                            asked_at="2026-09-10T00:00:00Z")

    question = questions_for(conn, (f"home:f-thesis",))[0]
    assert question.scope == f"{SCOPE_FILE}:f-thesis"
    # CHAINS, NOT NODE IDS. `n-course` in the panel is a string nobody can read
    # and an answer `chosen_destination` resolves to nothing.
    assert [option.option_id for option in question.options] == [
        "Coursework/W3134", "Research/Thesis"]
    assert [option.chooses_destination for option in question.options] == [
        "Coursework/W3134", "Research/Thesis"]
    # It reaches the panel at all, which is the half gap 15 was missing.
    assert question.question_id in {
        asked.question_id for asked in open_questions(conn)}

    record_answer(conn, StructuralAnswer(
        question_id="home:f-thesis", option_id="Research/Thesis",
        state=CONFIRMED, scope=f"{SCOPE_FILE}:f-thesis",
        user_id="jy", recorded_at="2026-09-10T00:01:00Z"))

    assert chosen_destination(
        conn, scope=f"{SCOPE_FILE}:f-thesis") == "Research/Thesis"
    assert chosen_destination(conn, scope=f"{SCOPE_FILE}:f-other") is None


def test_gap15_an_ask_this_tree_no_longer_offers_is_not_half_asked():
    """DESIGN: a question offers the person somewhere to choose BETWEEN, and one
    option is a placement wearing a question mark.

    MEASUREMENT: an `Ask` one of whose nodes the frozen tree does not carry
    records NO question at all, rather than a one-option question the panel would
    print as a choice. `StructuralQuestion` would take it; `Ask` and
    `question_for_unreadable_folder` both refuse the same shape by name, and this
    refuses it a third time at the only new place it can arise.
    """
    from questions.schema import create_questions_schema
    from questions.store import open_questions

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_questions_schema(conn)

    cli._two_home_questions(conn,
                            _two_homed_run(node_ids=("n-course", "n-gone")),
                            asked_at="2026-09-10T00:00:00Z")

    assert open_questions(conn) == ()


def test_the_run_hands_the_placement_pipeline_the_asking_selector(tmp_path,
                                                                  monkeypatch):
    """The wiring, not the function. `104` §18.2 gap 15 was one lambda.

    The selector above can be correct and reach nothing, which is exactly the
    state the gap describes: `placement/records.py` has required two options for
    an `Ask` since it was written, `pipeline._multi_home_decision` has built one
    since it was written, and the composition root passed an answer that made both
    unreachable. So this asserts what the run actually hands the pipeline.

    SABOTAGE: rewire `ask_or_abstain` to `lambda node_ids: pv.ABSTAIN` -- every
    unit test above still passes and this one fails, which is the whole point of
    testing the seam rather than the policy.
    """
    import production

    from placement import vocabulary as pv

    seen = {}
    real = production.run_corpus

    def _capture(conn, **kwargs):
        seen["ask_or_abstain"] = kwargs["inputs"].ask_or_abstain
        return real(conn, **kwargs)

    monkeypatch.setattr(production, "run_corpus", _capture)
    corpus = _unreadable_corpus(tmp_path)
    _run(_argv(corpus, tmp_path / "plan.sqlite"))

    assert "ask_or_abstain" in seen, "the placement pipeline was never reached"
    assert seen["ask_or_abstain"] is cli._ask_when_there_are_two_homes_to_offer
    assert seen["ask_or_abstain"](("n-a", "n-b")) == pv.ASK_USER
