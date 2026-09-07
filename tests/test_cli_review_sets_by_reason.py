# tests/test_cli_review_sets_by_reason.py
"""`104` R-115. What a person is asked to review, and how it is divided.

`00` §residual: the residual screen "should divide these files into
understandable review sets using reliable characteristics, rather than
presenting a single intimidating pile", and it names its examples by what the
files SHARE -- "encrypted, unreadable, or unsupported", "multiple plausible
destinations", "no extractable text".

What shipped was the pile, called "Not yet placed", cut into eight-file batches
by `RESIDUAL_REVIEW_BATCH`. A batch index is a ceiling and not a
characteristic: six files that stopped for one reason were told "3 review sets
of it have files under this heading" and nothing on the screen said which set
held which file, so the one gesture the screen offers -- `--send-set` -- named
a batch the person could not see the boundaries of.

These tests are about the division and about the four things that may not
change with it: every unplaced file is in exactly one set, `--send-set` still
addresses one set by the name printed beside it, the batch ceiling still splits
a set rather than truncating it (R-93 is the owner's question about the NUMBER
and nothing else), and protected material is still its own set -- named,
counted, never opened.
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
ARGV = ["--situation", "academic.coursework", "--label", "Papers", "--user", "jy"]


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


def _over_the_cap_corpus(tmp_path):
    """More files stopped for ONE reason than a single batch may hold.

    Nine `misc` files share one reason, and the ceiling is eight, so the set has
    to split. The three notes and the receipt are not decoration: without a file
    the tree can actually place, `--situation academic.coursework` builds no
    branch at all and the run ends before any set is surfaced.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    for index in range(3):
        (corpus / f"notes{index}.txt").write_text(
            f"Remember to buy milk {index}.\n")
    (corpus / "receipt.txt").write_text("Thank you for your purchase.\n")
    for index in range(9):
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


def test_a_set_over_the_batch_cap_is_still_split_by_the_cap(tmp_path):
    """R-93's number, applied WITHIN a set and doing nothing else.

    §8.6 splits a set over the ceiling rather than truncating it, and the
    numbering a person reads is `(i of n)` on the set's own name. R-115 changes
    what a set IS and leaves the ceiling exactly where it was: the owner's
    question is still how many files a batch should hold, and it is not
    answered here.
    """
    corpus = _over_the_cap_corpus(tmp_path)
    database = tmp_path / "plan.sqlite"
    printed = _report(corpus, database)

    surfaced = dict(_surfaced(database))
    batches = {label: files for label, files in surfaced.items()
               if label.startswith("No folder matched")}
    assert sorted(batches) == ["No folder matched (1 of 2)",
                               "No folder matched (2 of 2)"], (
        f"nine files under one reason surfaced as {sorted(surfaced)}:\n{printed}")
    for label, files in batches.items():
        assert len(files) <= cli.RESIDUAL_REVIEW_BATCH, (label, len(files))
    joined = [file_id for files in batches.values() for file_id in files]
    assert len(joined) > cli.RESIDUAL_REVIEW_BATCH, (
        f"{len(joined)} files did not exceed the ceiling, so this corpus is no "
        "longer testing a split")
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
    # gesture that files a whole set with no per-file look, and P11 refuses it
    # over protected material before it reads any decision. The refusal is the
    # "never opened" clause here -- the byte-level half is
    # `test_nothing_opens_the_vault_the_disk_image_or_the_passport`.
    out = io.StringIO()
    code = cli.main([str(corpus), *ARGV, "--database", str(tmp_path / "sent.sqlite"),
                     "--residual", AREA, "--send-set",
                     f"Protected, and not filed in bulk={AREA}"], out=out)
    refused = out.getvalue()
    assert code != 0, refused
    acted = [d for d in _decisions(tmp_path / "sent.sqlite") if d.residual is not None]
    assert not acted, (
        f"a protected set was acted on after the refusal: {acted}")
