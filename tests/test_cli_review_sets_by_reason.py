# tests/test_cli_review_sets_by_reason.py
"""`104` R-115. What a person is asked to review, and how it is divided.

`00` §residual: the residual screen "should divide these files into
understandable review sets using reliable characteristics, rather than
presenting a single intimidating pile", and it names its examples by what the
files SHARE -- "encrypted, unreadable, or unsupported", "multiple plausible
destinations", "no extractable text".

What shipped was the pile, called "Not yet placed", cut into eight-file batches
by the spend ceiling. A batch index is a ceiling and not a characteristic: six
files that stopped for one reason were told "3 review sets of it have files
under this heading" and nothing on the screen said which set held which file,
so the one gesture the screen offers -- `--send-set` -- named a batch the
person could not see the boundaries of.

These tests are about the division and about the four things that may not
change with it: every unplaced file is in exactly one set, `--send-set` still
addresses one set by the name printed beside it, the screenful still splits a
set rather than truncating it, and protected material is still its own set --
named, counted, never opened.

`104` R-93 answered the NUMBER since: `cli.FILES_PER_REVIEW_SCREEN` is 25 and
not 8, and a set of 25 or fewer is unnumbered. The two tests at the foot of
this file hold both halves.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from placement import vocabulary as pv  # noqa: E402
from placement.store import decisions_for_plan  # noqa: E402

AREA = "Review Later"
#: `104` SF-3: `--accept-groups` is the person's accept, and a review set is
#: something a PLAN has -- a run that accepts nothing designs no tree, places no
#: file and surfaces no set, so every test in this file is about a decided run.
ARGV = ["--situation", "academic.coursework", "--label", "Papers", "--user", "jy",
        "--accept-groups"]

#: One set `_three_reason_corpus` always surfaces, unprotected, named exactly as
#: the report names it. Measured rather than assumed: the corpus's three sets are
#: this one, "Waiting on a question you have been asked" and the protected one,
#: and `test_files_held_for_three_reasons_are_three_sets_a_person_can_tell_apart`
#: is what fails first if that stops being true.
HELD_SET = "Not yet said what kind of material"


def _three_reason_corpus(tmp_path):
    """One corpus whose unplaced files stopped for three different reasons.

    The bytes of the vault are a stand-in -- a KeePass signature over zeroes --
    because the point is that nothing opens it, which is all the product knows
    about it too. It is the same fixture shape
    `test_nothing_opens_the_vault_the_disk_image_or_the_passport` uses.

    Three reasons, and each of them a different sentence on the screen: nothing
    has said what kind of material the photo and the note are; the vault is a
    question the report puts to the person; the passport is protected.
    """
    corpus = tmp_path / "corpus"
    private = corpus / "Private"
    private.mkdir(parents=True)
    (private / "credentials.kdbx").write_bytes(
        b"\x03\xd9\xa2\x9agU\xfb\x4b" + b"\x00" * 4096)
    (private / "passport bio page.txt").write_text(
        "PASSPORT\nUNITED STATES OF AMERICA\nPassport No. 517204418\n"
        "Surname ZHANG Given names WEI\nDate of birth 14 NOV 1991\n")
    (corpus / "holiday.jpg").write_bytes(
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01" + b"\x00" * 400)
    (corpus / "misc.txt").write_text("Nothing in particular about anything.\n")
    return corpus


#: The files this corpus contributes to "No folder matched" besides the `misc`
#: ones. Measured, not assumed: the three shopping notes stop for the same reason
#: the `misc` files do, and the receipt is protected and is its own set. Both
#: tests below assert the resulting count, so a corpus that stops behaving this
#: way fails there rather than silently testing the wrong number.
_NOTES_UNDER_THE_SAME_REASON = 3


def _one_reason_corpus(tmp_path, *, held: int):
    """A corpus whose "No folder matched" set holds exactly `held` files.

    The three notes and the receipt are not decoration: without a file the tree
    can actually place, `--situation academic.coursework` builds no branch at
    all and the run ends before any set is surfaced.

    `held` is the only thing the two tests below vary. At
    `cli.FILES_PER_REVIEW_SCREEN` the set is one screen and is unnumbered; at
    one more it is two, and both are named.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for index in range(_NOTES_UNDER_THE_SAME_REASON):
        (corpus / f"notes{index}.txt").write_text(
            f"Remember to buy milk {index}.\n")
    (corpus / "receipt.txt").write_text("Thank you for your purchase.\n")
    for index in range(held - _NOTES_UNDER_THE_SAME_REASON):
        (corpus / f"misc{index:02d}.txt").write_text(
            f"Nothing in particular about anything {index}.\n")
    return corpus


def _report(corpus, database, *extra):
    out = io.StringIO()
    code = cli.main([str(corpus), *ARGV, "--database", str(database),
                     "--residual", AREA, *extra], out=out)
    printed = out.getvalue()
    assert code == 0, printed
    return printed


def _labels(printed: str) -> list[str]:
    """Every set name the screen prints, in the order it prints them."""
    return [line.split('Held for review as "', 1)[1].split('"', 1)[0]
            for line in printed.splitlines() if "Held for review as " in line]


def _surfaced(database):
    """The review sets this run recorded, as `(label, member_file_ids)` pairs."""
    import json
    import sqlite3

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        return [(row["label"], tuple(json.loads(row["payload"])["member_file_ids"]))
                for row in conn.execute(
                    "SELECT label, payload FROM residual_sets ORDER BY rowid")]
    finally:
        conn.close()


def _plan_version(database) -> str:
    import sqlite3

    conn = sqlite3.connect(database)
    try:
        return conn.execute(
            "SELECT plan_version FROM residual_sets LIMIT 1").fetchone()[0]
    finally:
        conn.close()


def _decisions(database):
    import sqlite3

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        return decisions_for_plan(conn, plan_version=_plan_version(database))
    finally:
        conn.close()


# ======================================================================================
# The division
# ======================================================================================

def test_files_held_for_three_reasons_are_three_sets_a_person_can_tell_apart(
        tmp_path):
    """The defect, stated as the property that fixes it.

    Before R-115 this corpus produced "Not yet placed" and one protected set,
    and the photo, the note and the password vault were in the first one
    together -- three different sentences under one name, addressed by one
    `--send-set`. The screen already knew they were different: it printed a
    different "Same reason for each" over each of them.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    labels = _labels(printed)
    assert len(set(labels)) == 3, (
        f"three reasons produced {sorted(set(labels))}:\n{printed}")
    assert "Not yet placed" not in labels, (
        "the one pile is back, under its own name:\n" + printed)
    # And the names are the reasons rather than a count, which is the whole of
    # `00` §residual's "reliable characteristics".
    assert "Not yet said what kind of material" in labels, labels
    assert "Waiting on a question you have been asked" in labels, labels
    assert "Protected, and not filed in bulk" in labels, labels


def test_every_unplaced_file_is_in_exactly_one_set_and_no_other_file_is(tmp_path):
    """The rule `surface_residual_sets` refuses a partition for breaking.

    A file in no set is never shown on the last screen that could mention it,
    and a file in two is counted twice and can be filed twice.

    **`104` R-113 EXTENDED THIS.** It used to read "every unplaced file", and
    said in as many words that a placement with a destination and a blocked
    policy was in no set and was a separate row. The ruling closed that: every
    non-`place` decision AND every placement a policy is holding is in exactly
    one set, so what a placement has to be to stay OUT of the sets is a
    placement nothing is holding. The blocked halves are pinned on the corpora
    that produce them, in
    `tests/integration/test_cli_a_blocked_placement_is_in_a_review_set.py`;
    this corpus produces none, so the second assertion below reads here as it
    always did.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    _report(corpus, database)

    surfaced = _surfaced(database)
    members = [file_id for _, files in surfaced for file_id in files]
    assert len(members) == len(set(members)), (
        f"a file is in two review sets: {sorted(members)}")

    decisions = _decisions(database)
    held = {d.subject.file_id for d in decisions
            if d.subject.file_id and (
                d.outcome != pv.PLACE
                or d.review_policy == pv.BLOCKED_PENDING_USER)}
    assert set(members) == held, (
        f"the sets cover {sorted(set(members))} and the files owed a set are "
        f"{sorted(held)}")
    free = {d.subject.file_id for d in decisions
            if d.outcome == pv.PLACE and d.subject.file_id
            and d.review_policy != pv.BLOCKED_PENDING_USER}
    assert not (free & set(members)), (
        "a placement nothing is holding is being shown as held for review")


def test_every_abstention_reason_has_a_review_set_of_its_own(tmp_path):
    """The two vocabularies, pinned together.

    The division is `PlacementDecision.abstention_reason`, which is closed
    (`ABSTENTION_REASONS`). A member added to it with no row in
    `REVIEW_SET_REASONS` would fall into the last row and be filed under the
    name the one pile had -- silently, because the fallback exists so that a
    file is never dropped, not so that a reason can go unnamed.
    """
    named = {key for key, _, _ in cli.REVIEW_SET_REASONS}
    missing = sorted(set(pv.ABSTENTION_REASONS) - named - {pv.PRIVACY_BLOCKED})
    assert not missing, (
        f"{missing} are abstention reasons with no review set of their own; "
        "they would arrive on the screen inside the fallback set")
    # `privacy_blocked` is the one code that is TWO sets, for the reason
    # `_abstention_explanation` splits it: "nothing has said what this is" and
    # "a model was not allowed to look" are different facts and `66` §4 forbids
    # them sharing a message.
    assert cli.NOT_YET_CLASSIFIED in named and cli.NO_MODEL_ALLOWED in named
    labels = [label for _, label, _ in cli.REVIEW_SET_REASONS]
    assert len(labels) == len(set(labels)), (
        f"two review sets share a name, so `--send-set` cannot tell them "
        f"apart: {labels}")


def test_each_set_says_what_is_in_it_beyond_its_count(tmp_path):
    """§7.5's other fields, which were empty tuples whatever the set held.

    `00` §residual: "Each set should display representative examples, file-type
    distribution, age range ...". The examples were filled and the other two
    were literals, so a person deciding what happens to a whole set in one
    gesture had a count and three filenames.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    _report(corpus, database)

    import json
    import sqlite3

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    payloads = [json.loads(row["payload"])
                for row in conn.execute("SELECT payload FROM residual_sets")]
    conn.close()
    assert payloads
    for item in payloads:
        assert item["representative_examples"], item["label"]
        assert item["file_type_distribution"], (
            f'{item["label"]!r} says nothing about what kind of files it holds')
        counted = sum(count for _, count in item["file_type_distribution"])
        assert counted == item["file_count"], (
            f'{item["label"]!r} distributes {counted} of {item["file_count"]}')
        # Two dates, both readable, and never invented: a set whose files carry
        # no recorded mtime leaves this empty rather than dating them.
        assert len(item["age_range"]) == 2, item["label"]
        assert item["age_range"][0] <= item["age_range"][1], item["age_range"]


# ======================================================================================
# What may not change with it
# ======================================================================================

def test_send_set_with_a_reason_label_sends_exactly_that_set(tmp_path):
    """The one gesture this screen exists to offer, on the new names.

    `act_on_residual_sets` addresses a set by the label the report printed, so
    renaming the sets is renaming what a person types. The property is not that
    the flag is accepted -- it is that it moves the set it names and nothing
    else, which is what made the old batch names unusable: the person could see
    the name and not the boundary.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    first = _report(corpus, database)
    label = next(name for name in _labels(first)
                 if name == "Not yet said what kind of material")

    printed = _report(corpus, tmp_path / "sent.sqlite",
                      "--send-set", f"{label}={AREA}")
    sent = {name: files for name, files in _surfaced(tmp_path / "sent.sqlite")}
    moved = {d.subject.file_id for d in _decisions(tmp_path / "sent.sqlite")
             if d.residual is not None and d.subject.file_id}
    assert moved == set(sent[label]), (
        f"{label!r} holds {sorted(sent[label])} and the run acted on "
        f"{sorted(moved)}:\n{printed}")
    # The twin: every other set is untouched and still held.
    for other, files in sent.items():
        if other == label:
            continue
        assert not (moved & set(files)), (
            f"sending {label!r} also acted on {other!r}:\n{printed}")
        assert f'Held for review as "{other}"' in printed, printed


def test_a_set_over_one_screen_is_still_split_by_the_screenful(tmp_path):
    """`104` R-93's number, applied WITHIN a reason set and doing nothing else.

    §8.6 splits a set over the ceiling rather than truncating it, and the
    numbering a person reads is `(i of n)` on the set's own name. R-115 changed
    what a set IS; R-93 changed the number the set splits at, from the spend
    ceiling's eight to one screen's 25. Twenty-six files under one reason is the
    smallest corpus that still splits, and it is what this builds.
    """
    corpus = _one_reason_corpus(tmp_path, held=cli.FILES_PER_REVIEW_SCREEN + 1)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    surfaced = dict(_surfaced(database))
    batches = {label: files for label, files in surfaced.items()
               if label.startswith("No folder matched")}
    assert sorted(batches) == ["No folder matched (1 of 2)",
                               "No folder matched (2 of 2)"], (
        f"{cli.FILES_PER_REVIEW_SCREEN + 1} files under one reason surfaced as "
        f"{sorted(surfaced)}:\n{printed}")
    for label, files in batches.items():
        assert len(files) <= cli.FILES_PER_REVIEW_SCREEN, (label, len(files))
    joined = [file_id for files in batches.values() for file_id in files]
    assert len(joined) == cli.FILES_PER_REVIEW_SCREEN + 1, (
        f"{len(joined)} files stopped for this reason, so this corpus is no "
        "longer one file over one screen")
    assert len(joined) == len(set(joined)), "a file is in two batches of one set"
    # Split, never truncate: what the batches hold together is every unplaced
    # file this run has for that reason, and the run's other sets hold the rest.
    everything = {file_id for files in surfaced.values() for file_id in files}
    unplaced = {d.subject.file_id for d in _decisions(database)
                if d.outcome != pv.PLACE and d.subject.file_id}
    assert everything == unplaced, (
        f"the ceiling dropped {sorted(unplaced - everything)}")
    # Both halves are addressable by the name printed beside them, which is what
    # a split costs and what it may not cost more than.
    for label in batches:
        assert f"--send-set '{label}={AREA}'" in printed, printed


def test_a_set_of_one_screenful_is_not_numbered(tmp_path):
    """`104` R-93's second clause: "(1 of 1)" names a split that did not happen.

    One fewer file than the test above, and the whole shape goes: one set, no
    index on its name, and the `--send-set` line beneath it carries the bare
    name. A person who is shown every file they have under one reason is not
    being shown the first page of anything, and a name that says otherwise is
    the kind of number nobody chose that R-93 exists to take out.
    """
    corpus = _one_reason_corpus(tmp_path, held=cli.FILES_PER_REVIEW_SCREEN)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    surfaced = dict(_surfaced(database))
    sets = {label: files for label, files in surfaced.items()
            if label.startswith("No folder matched")}
    assert sorted(sets) == ["No folder matched"], (
        f"{cli.FILES_PER_REVIEW_SCREEN} files under one reason surfaced as "
        f"{sorted(surfaced)}:\n{printed}")
    held = sets["No folder matched"]
    assert len(held) == cli.FILES_PER_REVIEW_SCREEN, (
        f"a screenful holds {len(held)} of the "
        f"{cli.FILES_PER_REVIEW_SCREEN} files under that reason")
    assert " of " not in "".join(sets), sorted(sets)
    # And the gesture names what the screen named, with no index to mistype.
    assert f"--send-set 'No folder matched={AREA}'" in printed, printed


def test_protected_files_are_their_own_set_named_counted_and_never_opened(
        tmp_path):
    """The line the division may not cross.

    `require_set_actionable` reads `residual_set.protected` and raises before it
    reads any decision, so the flag has to be true of what the set holds. A
    reason-based division that let a passport fall into "No folder matched"
    because that is also true of it would make the refusal unreachable -- and
    would file it in one bulk gesture with a holiday photo.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    import json
    import sqlite3

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    payloads = {row["label"]: json.loads(row["payload"])
                for row in conn.execute("SELECT label, payload FROM residual_sets")}
    protected = payloads["Protected, and not filed in bulk"]
    assert protected["protected"] is True, protected
    assert protected["sensitivity_status"] == "protected", protected
    assert protected["file_count"] == len(protected["member_file_ids"]) == 1
    for label, item in payloads.items():
        if label != "Protected, and not filed in bulk":
            assert item["protected"] is False, (
                f"{label!r} claims to hold protected material")
            assert not (set(item["member_file_ids"])
                        & set(protected["member_file_ids"])), label

    # Counted on the screen, and offered no gesture that would refuse.
    assert "Protected: 1 marked and counted" in printed, printed
    block = next(part for part in printed.split("Held for review as ")
                 if part.startswith('"Protected'))
    assert "--send-set" not in block.split("\n\n", 1)[0], block

    conn.close()

    # And never opened, at the seam a review set is FOR: `--send-set` is the one
    # gesture that files a whole set with no per-file look, and the refusal over
    # protected material now arrives before any decision is READ or WRITTEN. The
    # refusal is the "never opened" clause here -- the byte-level half is
    # `test_nothing_opens_the_vault_the_disk_image_or_the_passport`.
    #
    # `104` R-26 MOVED THE REFUSAL AND THE PLAN NOW SURVIVES IT. Until it landed,
    # `act_on_residual_sets` wrote a `residual_set_decisions` row saying protected
    # material was to be filed in bulk and `review_residual_sets` only then raised
    # `ProtectedSetNotReadable`, which nothing caught -- so the run ended "No plan
    # was made", the person lost the whole proposal, and the decision row about
    # their protected material outlived it. `review_gestures.collect_set_sends`
    # now collects the gesture first, so P13's own `ProtectedContainerHasNoAction`
    # fires before P11 is called at all: nothing is decided, nothing is recorded,
    # and the plan the person asked for is still printed.
    out = io.StringIO()
    code = cli.main([str(corpus), *ARGV, "--database", str(tmp_path / "sent.sqlite"),
                     "--residual", AREA, "--send-set",
                     f"Protected, and not filed in bulk={AREA}"], out=out)
    refused = out.getvalue()
    assert code == 0, refused
    assert "That send was refused" in refused, refused
    assert "Nothing was filed in bulk" in refused, refused
    acted = [d for d in _decisions(tmp_path / "sent.sqlite") if d.residual is not None]
    assert not acted, (
        f"a protected set was acted on after the refusal: {acted}")
    sent = sqlite3.connect(tmp_path / "sent.sqlite")
    try:
        assert sent.execute(
            "SELECT COUNT(*) FROM residual_set_decisions").fetchone()[0] == 0, (
            "a decision row was written for a set P13 carries no action for")
    finally:
        sent.close()


# ======================================================================================
# `104` R-42, item 2: the design's own named sets
#
# `00` §residual names its review sets by what their files SHARE -- "58 screenshots
# with no accepted project or event", "21 standalone PDFs and forms", "14
# spreadsheets and presentations with unclear purpose". R-115 divided by the reason
# code, which is a reliable characteristic and is not that one: every one of those
# three files stops for the same reason ("no folder matched") and lands under one
# heading. The characteristic REFINES that pile and only that pile -- a reason that
# says what is BLOCKING a file (a model was not allowed to look, you have been asked
# a question) is a set of its own and stays one.
# ======================================================================================

def test_spreadsheets_that_no_folder_matched_are_the_design_s_own_set(tmp_path):
    """The router already knows: `source_type` is `spreadsheet` for a `.csv`.

    Before this the person read "No folder matched -- 4 files" over a mixture of
    a spreadsheet and three notes, which is `00`'s "single intimidating pile"
    one level down.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr Lee. Credits: 3.\n")
    (corpus / "misc.txt").write_text("Nothing in particular about anything.\n")
    (corpus / "unclear.csv").write_text("a,b,c\n1,2,3\n")
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    surfaced = dict(_surfaced(database))
    assert "Spreadsheets and presentations with unclear purpose" in surfaced, (
        f"the spreadsheet is still inside the reason pile {sorted(surfaced)}")
    spreadsheets = surfaced["Spreadsheets and presentations with unclear purpose"]
    assert len(spreadsheets) == 1, surfaced
    assert "Spreadsheets and presentations with unclear purpose" in printed, printed
    # And the notes it was gathered with are still their own set, under the
    # reason both stopped for. A division that swallowed the remainder would be
    # a set of everything the characteristic happened to recognise.
    assert "No folder matched" in surfaced, sorted(surfaced)


def _write_a_screenshot_fact(conn, file_id: str) -> None:
    """One `media_type = screenshot` row, written the way P6 writes one.

    Written here rather than produced by the run because producing one needs a
    real photograph's EXIF beside a real screenshot's: `media_type` refuses a
    file whose only tiered observations are in the screenshot band, which is
    §2.6's "the absence of EXIF is not proof". What is under test is the READ.
    """
    row = conn.execute(
        "SELECT content_hash FROM files WHERE file_id = ?", (file_id,)).fetchone()
    conn.execute(
        'INSERT OR IGNORE INTO "values" (value_id, field_key, canonical_value, '
        'raw_variants, display_label, aliases, origin) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        ("value-screenshot-pin", "media_type", "screenshot", "[]", "screenshot",
         "[]", "found"))
    conn.execute(
        "INSERT INTO file_facts (fact_id, file_id, content_hash, field_key, "
        "value_id, reliability_state, origin, evidence_refs, cited_quote_refs, "
        "cache_key, active, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        ("fact-screenshot-pin", file_id, row["content_hash"], "media_type",
         "value-screenshot-pin", "validated", "rule", "[]", "[]",
         "cache-screenshot-pin", 1, "2026-09-11T00:00:00+00:00"))
    conn.commit()


def test_a_screenshot_is_read_off_the_image_reader_s_own_signal(tmp_path):
    """§2.6's `media_type`, and nothing that guesses from a filename.

    The fact is the image reader's: `facts.photo_event.media_type` ranks the
    EXIF bands and writes `screenshot` or refuses. This reads that row back. A
    file with no such fact has no characteristic and keeps its reason's set,
    which is what stops this from being a detector.
    """
    import sqlite3

    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "syllabus.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr Lee. Credits: 3.\n")
    (corpus / "misc.txt").write_text("Nothing in particular about anything.\n")
    database = tmp_path / "plan.sqlite"
    _report(corpus, database)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        held = [row["file_id"] for row in conn.execute(
            "SELECT file_id, filename FROM files WHERE filename = 'misc.txt'")]
        assert held, "the corpus changed shape"
        assert cli.residual_characteristics(conn, held) == {}, (
            "a file with no media_type fact was given a characteristic")
        _write_a_screenshot_fact(conn, held[0])
        assert cli.residual_characteristics(conn, held) == {
            held[0]: cli.SCREENSHOT_REVIEW_SET}, (
            "the image reader's own screenshot signal is not read")
    finally:
        conn.close()


def test_a_blocking_reason_is_still_a_set_of_its_own():
    """The characteristic refines "no folder matched" and nothing else.

    A spreadsheet a model was not allowed to look at has not been matched
    against anything; calling it "a spreadsheet with unclear purpose" would
    tell somebody the product looked and could not tell, when what happened is
    that it was not allowed to look. `66` §4 forbids the two sharing a message.
    """
    assert cli.NO_MODEL_ALLOWED not in cli.REFINED_BY_CHARACTERISTIC
    assert cli.NOT_YET_CLASSIFIED not in cli.REFINED_BY_CHARACTERISTIC
    assert cli.WAITING_ON_AN_ANSWER not in cli.REFINED_BY_CHARACTERISTIC
    assert cli.NOT_ALLOWED_TO_CROSS not in cli.REFINED_BY_CHARACTERISTIC
    assert pv.NO_SUPPORTED_DESTINATION in cli.REFINED_BY_CHARACTERISTIC


def test_no_two_review_sets_share_a_name():
    """`--send-set` addresses a set by the name printed beside it.

    The characteristics are a second table of set names, so the uniqueness the
    reason table already holds for itself has to hold ACROSS the two.
    """
    labels = ([label for _, label, _ in cli.REVIEW_SET_REASONS]
              + [label for _, label, _ in cli.REVIEW_SET_CHARACTERISTICS]
              + [cli.PROTECTED_REVIEW_SET_WORDS[0]])
    assert len(labels) == len(set(labels)), labels
    keys = ([key for key, _, _ in cli.REVIEW_SET_REASONS]
            + [key for key, _, _ in cli.REVIEW_SET_CHARACTERISTICS]
            + [cli.PROTECTED_REVIEW_SET])
    assert len(keys) == len(set(keys)), keys


def test_a_receipt_set_needs_a_fact_that_names_one():
    """§7.3's `Receipts and Confirmations` has a residual TEMPLATE and no producer.

    `00` names "17 receipts, tickets, and confirmations" as a review set, and
    nothing in this product concludes that a file is a receipt: `privacy/
    vocabulary.py` publishes `ALWAYS_LOCAL_KIND_RECEIPT` as *a name a detector
    writes* and says in as many words that "how a receipt is recognised as a
    receipt is hand-authored elsewhere". Dividing a review set on a word found
    in a filename is the invention this whole file exists to refuse, so the set
    waits for the fact.
    """
    import pytest
    pytest.xfail(
        "no producer writes a receipt fact: the word owed is a `file_facts` "
        "field naming a transactional document, and `privacy.vocabulary."
        "ALWAYS_LOCAL_KIND_RECEIPT` is a detector's output name, not one")


# ======================================================================================
# `104` R-42, item 1: the per-set card, and the two set answers that had no gesture
#
# `00` §residual: "Each set should display representative examples, file-type
# distribution, age range, available OCR or text evidence, sensitivity status, any
# weak graph neighbors, and the reason the system could not safely place the
# files." `review_surface/residual.py` computed exactly that and had no caller --
# the audit of 11 Sep (§18.42) lists it under "finished, tested code with no
# caller". The screen printed a count, a name and a reason, and the person decided
# what happened to a whole set from three of the seven.
#
# §7.6 puts four choices to the person and `SET_CHOICES` carries all four. One had
# a gesture: `--send-set`. "Leave them in place" and "review them with AI against
# your approved residual folders" were legal decisions no command could make.
# ======================================================================================

def test_every_review_set_prints_its_card(tmp_path):
    """The seven, on the screen, for every set the run surfaced.

    The reason is the seventh and was already printed; the other six were not.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    for label, members in _surfaced(database):
        assert f'"{label}"' in printed, (
            f"{label!r} is a set nobody can name, so no gesture reaches it:"
            f"\n{printed}")
    # The card's own words, each of them `00`'s.
    assert "File types:" in printed, printed
    assert "Age range:" in printed, printed
    assert "Available OCR or text evidence:" in printed, printed
    assert "Sensitivity:" in printed, printed
    # And an example is a FILENAME, because a file id is not something a person
    # can look for on their own disk.
    assert "Examples: " in printed, printed
    assert "holiday.jpg" in printed.split("Examples: ", 1)[1], printed


def test_a_protected_set_s_card_does_not_name_its_files(tmp_path):
    """The owner's 2026-09-02 ruling reaches the card too.

    A protected set is named, counted and carries the rest of its card. Its
    example FILENAMES are the part of the report least safe to have on a screen
    somebody else can see, and `--show-protected` is where they live.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    assert '"Protected, and not filed in bulk"' in printed, printed
    assert "passport bio page.txt" not in printed, printed
    block = printed.split('"Protected, and not filed in bulk"', 1)[1]
    assert "File types:" in block.split("\n\n", 1)[0], block


def test_the_screen_offers_leave_in_place_and_review_with_ai(tmp_path):
    """§7.6's other two choices, as lines a person can paste.

    Beside `--send-set`, which was the only one of the four with a route.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    assert "--leave-set " in printed, printed
    assert "--review-set " in printed, printed
    # A protected set is offered neither, for the reason it is offered no
    # `--send-set`: P13 carries no action over one at all.
    block = printed.split('"Protected, and not filed in bulk"', 1)[1]
    first = block.split("\n\n", 1)[0]
    assert "--leave-set" not in first and "--review-set" not in first, first


def test_leave_set_records_the_choice_and_moves_nothing(tmp_path):
    """`leave_in_place`, which `SET_CHOICES` has always carried.

    §7.6: a set the person left in place costs zero model calls and moves no
    file. What was missing was any way to SAY it.
    """
    import sqlite3

    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database, "--leave-set", HELD_SET)
    assert "That send was refused" not in printed, printed

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in conn.execute(
            "SELECT * FROM residual_set_decisions")]
    finally:
        conn.close()
    assert rows, printed
    assert {row["choice"] for row in rows} == {"leave_in_place"}, rows
    assert all(row["node_id"] is None for row in rows), rows
    acted = [d for d in _decisions(database) if d.residual is not None]
    assert not acted, f"a set left in place produced placement work: {acted}"


def test_leave_set_is_collected_as_the_gesture_p13_already_has_a_word_for(
        tmp_path):
    """`leave_untouched`, and the audit trail R-26 built for `--send-set`.

    P13 "presents and collects; it never decides", and the one bulk gesture this
    command had was the only one that reached `review_actions`.
    """
    import json
    import sqlite3

    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    _report(corpus, database, "--leave-set", HELD_SET)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        actions = [dict(row) for row in conn.execute(
            "SELECT * FROM review_actions")]
    finally:
        conn.close()
    left = [row for row in actions if row["action"] == "leave_untouched"]
    assert left, actions
    assert json.loads(left[0]["bulk_member_refs"]), left


def test_review_set_records_the_choice_and_site_d_does_not_act(tmp_path):
    """§7.6's third choice, recorded, with the judgement it asks for deferred.

    Site D's text is a DRAFT. `104` §7 Phase 1 step 6 records a verdict and
    applies nothing while it is one, and `cli._must_not_apply` is what a run
    injects in place of the real resolver. So the person's decision is written
    down -- it is theirs, it belongs to this plan version, and a run that
    refused to record it would be asking them again for an answer they gave --
    and the model is not asked. The run says so rather than looking as though it
    did the work.
    """
    import sqlite3

    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database, "--review-set", HELD_SET)

    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in conn.execute(
            "SELECT * FROM residual_set_decisions")]
    finally:
        conn.close()
    assert {row["choice"] for row in rows} == {
        "review_with_model_against_approved_residual_folders"}, rows
    acted = [d for d in _decisions(database) if d.residual is not None]
    assert not acted, f"site D acted under a draft text: {acted}"
    assert "has not been approved" in printed, printed


def test_one_set_cannot_be_answered_two_ways_in_one_run(tmp_path):
    """Three gestures, one set: the run refuses rather than picking.

    `act_on_residual_sets` already resolves every pair before recording any, so
    that a refusal cannot half happen. Two answers about one set is the same
    hazard from the other side: whichever was recorded second would silently be
    the one that stood.
    """
    corpus = _three_reason_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database, "--leave-set", HELD_SET,
                      "--review-set", HELD_SET)
    assert "That send was refused" in printed, printed
    assert HELD_SET in printed, printed


def test_the_review_gesture_has_no_word_of_its_own_in_p13_yet():
    """The word this build needed and did not have.

    `--send-set` is collected as `accept_bulk` and `--leave-set` as
    `leave_untouched`, both of them members of `review_surface.vocabulary.
    ACTIONS`. There is no member meaning *ask a model about these against my
    approved residual folders*, and using `accept_bulk` for it would record the
    person as having ACCEPTED a destination they were never shown. So
    `--review-set` writes P11's decision row and no `review_action`, and the
    audit trail of that one gesture is the hole this xfail names.
    """
    import pytest

    from review_surface import vocabulary as rv

    pytest.xfail(
        "P13 has no action word for `review_with_model_against_approved_"
        f"residual_folders`; its {len(rv.ACTIONS)} actions are the owner's to "
        "add one to")
