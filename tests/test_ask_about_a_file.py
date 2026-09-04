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
    _, printed = _run(_argv(corpus, tmp_path / "plan.sqlite"))

    joined = " ".join(printed.split())
    assert "scans" in joined, printed
    assert "--answer home:scans=" in joined, printed
    # §14: the person can see WHY it arose, and §12: what it will not do.
    assert "nothing readable" in joined, printed
    assert "will not move, rename or delete anything" in joined, printed


def test_one_question_covers_the_whole_folder(tmp_path):
    """§14's "repeated ambiguity", asked once.

    Three files, one question. A product that asked three times would be asking
    the same thing three times, and a person answering it three times would
    rightly conclude nobody was listening.
    """
    corpus = _unreadable_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    _run(_argv(corpus, database))

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
    _run(_argv(corpus, database))

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
    """
    corpus = tmp_path / "corpus"
    (corpus / "scans").mkdir(parents=True)
    for name in ("IMG_0001.png", "IMG_0002.png"):
        (corpus / "scans" / name).write_bytes(
            b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    # A name P7's own path rule marks protected before anything is read.
    (corpus / "scans" / "passport scan.png").write_bytes(
        b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
    (corpus / "Notes.txt").write_text(
        "Lecture Notes\n\nLecture notes for PHYS1401.\n")

    import json

    database = tmp_path / "plan.sqlite"
    _, printed = _run(_argv(corpus, database))

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
    argv = _argv(corpus, database)

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
