"""`104` §18.43, the audit's item 10: the two families, formed.

"Version families and near-duplicates never form (`version_family` uncalled,
`near_match=lambda: False`, no perceptual hash carrier; the rules are `97` and
`98`)." Both proposals were ratified as written on 2026-09-11 (`00`, Amendments of
2026-09-11, item 4) and AS WRITTEN NEITHER AUTHORED A RULE -- each carries the
status line "OWED TO THE OWNER. Nothing is authored here and nothing is bound", and
each spends its §3 naming the word the owner still had to say. `97` §3 introduces
its four candidate signals as "Candidate signals, none of them ruled"; `98` §3.1
records that `00` "names no algorithm" and §3.2 that "the number is the owner's".

**The owner then ruled, in session on 11 Sep 2026, and this file measures the two
rulings end to end through `cli.main` over a real corpus.**

`97`: two files are two versions of one document when they share a document title --
the `title` observation, or the first `heading` where there is none -- and their
content hashes differ; filenames are never a basis; the family's stored name is the
shared title; the blocking key is that title's canonical form.
`facts/lineage.py` holds it.

`98`: a 64-bit difference hash over an 8x9 greyscale thumbnail decoded through the
ImageIO the reader already uses, and two images are near-duplicates at a Hamming
distance of at most 5. `readers/perceptual_hash.py` holds the hash, the distance and
the banded blocking key together, as `98` §3.1 requires.

**Every pin has a twin that says the opposite, and the twins are why the numbers
matter.** `98` §3.2 is explicit that the two errors are not symmetric -- "too loose
-> two different photographs are called near-duplicates, and the review screen
invites the owner to delete one of them" -- so a threshold wide enough to join every
JPEG in a corpus, or a lineage rule that answered for every pair, would satisfy the
positive half of each pair and be worse than the refusal it replaced. Both negatives
were green before the rules shipped, when nothing formed at all; they are green now
against rules that DO form families, which is the measurement that was missing.

**One thing the ruling does not reach, recorded because the corpus below shows it.**
The rule reads the `title` or `heading` zone, and a plain `.txt` file produces
neither: `readers/text_documents.py` detects heading regions for Markdown, docx and
the structured formats, and a bare first line of a text file is `zone="body"`. So
three drafts saved as `.txt` state no title and form no version family. The drafts
here are Markdown for that reason, and it is stated rather than worked around: a
fallback to the first body paragraph would be this file inventing the half of the
rule the owner did not say.
"""
from __future__ import annotations

import io
import sqlite3
from pathlib import Path

import pytest

import cli
from facts.families import DUPLICATE_FAMILY_FIELD, VERSION_FAMILY_FIELD

Quartz = pytest.importorskip(
    "Quartz",
    reason="ImageIO is this deployment's image library (pyproject's `readers` "
           "extra, macOS only); without it the near-duplicate pins below would "
           "pass by measuring a corpus with no readable image in it")
NSURL = pytest.importorskip("Foundation").NSURL

SITUATION = "academic.coursework"
LABEL = "Coursework"

#: One document's title, printed on all three drafts. `97`'s table puts "a shared
#: document title in `title`/`heading`, plus different content hashes" first among
#: its four candidates and rules it no more than the other three; the corpus states
#: the evidence a rule would have to read, not the rule.
TITLE = "Thesis Proposal - Tidal Mixing in the Pearl River Estuary"


def _run(corpus: Path, database: Path, *extra: str) -> tuple[int, str]:
    out = io.StringIO()
    code = cli.main([str(corpus), "--situation", SITUATION, "--label", LABEL,
                     "--user", "jy", "--database", str(database), *extra],
                    out=out)
    return code, out.getvalue()


def _family(database: Path, field_key: str) -> dict[str, tuple[str, str]]:
    """Every active family fact in the produced plan, by filename.

    Read from the database rather than from the report on purpose: no screen
    sentence for either of these is ratified, and asserting on one would pin a
    sentence nobody has written instead of the fact that is missing.
    """
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            'SELECT fi.filename AS filename, f.reliability_state AS state, '
            '       v.canonical_value AS value '
            'FROM file_facts AS f '
            'JOIN "values" AS v ON v.value_id = f.value_id '
            'JOIN files AS fi ON fi.file_id = f.file_id '
            'WHERE f.field_key = ? AND f.active = 1',
            (field_key,)).fetchall()
    finally:
        conn.close()
    return {row["filename"]: (row["value"], row["state"]) for row in rows}


def _extractors(database: Path) -> dict[str, set[str]]:
    """Which extractors completed on each file, so a twin can prove the corpus read.

    A negative pin -- "these two are NOT one family" -- passes just as happily over
    a corpus nothing opened as over one the rules considered and separated. The two
    twins below assert the corpus was read, so the difference cannot be swallowed.
    """
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            'SELECT fi.filename AS filename, r.extractor_name AS extractor '
            'FROM extraction_runs AS r '
            'JOIN files AS fi ON fi.file_id = r.file_id '
            "WHERE r.completeness = 'complete'").fetchall()
    finally:
        conn.close()
    found: dict[str, set[str]] = {}
    for row in rows:
        found.setdefault(row["filename"], set()).add(row["extractor"])
    return found


def _drafts(root: Path) -> Path:
    """Three drafts of one document, and one document that is not of it.

    The three share a title line and share no bytes; the fourth shares neither.
    Successive drafts are what `97` §5 says the refusal costs -- "the case where
    the owner has two genuinely different drafts of one document, common on this
    disk, and currently invisible to the product".
    """
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "Proposal draft.md").write_text(
        f"# {TITLE}\n\nSpring 2026. Supervisor: Dr. Lee.\n"
        "Section 1. The estuary is stratified for most of the year.\n")
    (corpus / "Proposal draft 2.md").write_text(
        f"# {TITLE}\n\nSpring 2026. Supervisor: Dr. Lee.\n"
        "Section 1. The estuary is stratified for most of the year.\n"
        "Section 2. Spring tides break the stratification down.\n")
    (corpus / "Proposal final.md").write_text(
        f"# {TITLE}\n\nSpring 2026. Supervisor: Dr. Lee.\n"
        "Section 1. The estuary is stratified for most of the year.\n"
        "Section 2. Spring tides break the stratification down.\n"
        "Section 3. Mixing is strongest at the mouth.\n")
    (corpus / "Electricity invoice March 2026.md").write_text(
        "# CLP Power Hong Kong Limited\n\nInvoice for March 2026.\n"
        "Amount due: HKD 412.60. Account 8813-5521.\n")
    return corpus


def _raster(width: int, height: int, boxes):
    """A raster with real structure in it, so two of them can genuinely differ."""
    context = Quartz.CGBitmapContextCreate(
        None, width, height, 8, 0, Quartz.CGColorSpaceCreateDeviceRGB(),
        Quartz.kCGImageAlphaPremultipliedLast)
    Quartz.CGContextSetRGBFillColor(context, 1, 1, 1, 1)
    Quartz.CGContextFillRect(context, Quartz.CGRectMake(0, 0, width, height))
    Quartz.CGContextSetRGBFillColor(context, 0, 0, 0, 1)
    for left, bottom, wide, high in boxes:
        Quartz.CGContextFillRect(
            context, Quartz.CGRectMake(left, bottom, wide, high))
    return Quartz.CGBitmapContextCreateImage(context)


def _jpeg(path: Path, image, quality: float) -> Path:
    destination = Quartz.CGImageDestinationCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), "public.jpeg", 1, None)
    assert destination is not None, "this ImageIO cannot write JPEG"
    Quartz.CGImageDestinationAddImage(
        destination, image,
        {Quartz.kCGImageDestinationLossyCompressionQuality: quality})
    assert Quartz.CGImageDestinationFinalize(destination), path
    return path


def _photos(root: Path) -> Path:
    """One photograph, a re-saved copy of it, and a different photograph.

    The re-save is the same raster written again at a second JPEG quality, which is
    what `98` §4 names as the material byte identity cannot catch -- "resized
    exports, screenshots of screenshots, and messaging-app re-encodes". The two
    files hold the same picture and different bytes, so P1's content hashes differ
    and the exact half of `duplicate_family` correctly says nothing about them.
    """
    corpus = root / "holder" / "corpus"
    corpus.mkdir(parents=True)
    (corpus / "PHYS1401 Syllabus Spring 2026.txt").write_text(
        "PHYS 1401 Syllabus\n\nSpring 2026. Instructor: Dr. Lee. Credits: 3.\n")
    one = _raster(640, 480, ((40, 40, 200, 160), (400, 300, 180, 120)))
    other = _raster(640, 480, ((300, 60, 90, 380), (60, 380, 500, 60)))
    _jpeg(corpus / "IMG_4821.jpg", one, 1.0)
    _jpeg(corpus / "IMG_4821 resaved.jpg", one, 0.55)
    _jpeg(corpus / "IMG_5106.jpg", other, 1.0)
    assert (corpus / "IMG_4821.jpg").read_bytes() != (
        corpus / "IMG_4821 resaved.jpg").read_bytes(), (
        "the re-save produced identical bytes; the exact half would cover it and "
        "the pin below would measure nothing")
    return corpus


# --- `97`: version families -----------------------------------------------------


def test_three_drafts_of_one_document_form_one_version_family(tmp_path):
    """`97` §5's own measurement, as a corpus: three drafts, one family.

    "What is lost is the case where the owner has two genuinely different drafts of
    one document -- common on this disk, and currently invisible to the product."
    The three share a title and no bytes; under the owner's ruling they are one
    family, and every clause of that ruling is asserted here rather than the count
    alone.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(_drafts(tmp_path), database)
    assert code == 0, report

    found = _family(database, VERSION_FAMILY_FIELD)
    drafts = {name: found[name] for name in
              ("Proposal draft.md", "Proposal draft 2.md", "Proposal final.md")
              if name in found}
    assert len(drafts) == 3, f"only {sorted(drafts)} carry a version family: {found}"

    values = {value for value, _state in drafts.values()}
    assert len(values) == 1, drafts
    value = values.pop()

    # `97` §3's SECOND DECISION: "it must not be a file hash ... whatever names a
    # version family must be safe to show and to send." The owner ruled the name is
    # the shared title, so it is the title -- content, releasable, and neither a
    # hash nor a filename. §8.3 is the other half, "a filename match alone does
    # not", and no member's name appears in the value either.
    assert value == TITLE, value
    for name in drafts:
        assert name not in value, (name, value)

    # §3.13 through `facts.states`: a deterministic rule with no contextual check
    # beside it is the weaker half. `possible` keeps the family out of
    # `grouping.seeds.ANCHOR_STATES`, so a disk of documents whose first heading is
    # `Notes` cannot become one group on this evidence alone.
    assert {state for _value, state in drafts.values()} == {"possible"}, drafts

    # THE FAMILY IS UNORDERED, and the owner ruled it so: "if nothing in the
    # evidence orders them, record the family unordered and say so." Nothing in the
    # shared evidence does -- a title carries no sequence -- so the three rows are
    # indistinguishable except by which file they are on. A draft is not recorded as
    # preceding a final, and this says the plan does not pretend otherwise.
    assert len(set(drafts.values())) == 1, drafts


def test_two_unrelated_documents_are_not_one_version_family(tmp_path):
    """The twin. A rule that answered for every pair would satisfy the pin above.

    A thesis proposal and an electricity bill share a corpus and nothing else, and
    the rule reads the one thing that separates them: their titles. `97` §3 requires
    the rule to cite real observations precisely so that a family nobody can point
    at is not written, and §8.3 forbids the rule that would join these two -- both
    files' names end in `.md` and both sit in one folder.

    It ran green before the ruling too, when nothing formed at all. It is green now
    against a rule that DOES form a family three files wide in the same corpus,
    which is the measurement that was missing.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(_drafts(tmp_path), database)
    assert code == 0, report

    found = _family(database, VERSION_FAMILY_FIELD)
    draft = found.get("Proposal draft.md")
    invoice = found.get("Electricity invoice March 2026.md")
    assert draft is None or invoice is None or draft[0] != invoice[0], found

    # And the four documents were read: the pin above waits on a rule, not on a
    # file nothing opened.
    read = _extractors(database)
    for name in ("Proposal draft.md", "Proposal draft 2.md",
                 "Proposal final.md", "Electricity invoice March 2026.md"):
        assert "text.structured" in read.get(name, set()), (name, read)

    # And the corpus really did form the family this one is the negative of, so a
    # rule that stopped answering at all could not make this test pass.
    assert len(found) == 3, found


# --- `98`: near-duplicates ------------------------------------------------------


def test_a_resaved_copy_of_one_image_is_a_near_duplicate_of_it(tmp_path):
    """`98` §4's own material: one picture, two encodings, two content hashes.

    "The cost of leaving this open is low today and rises with the photo library:
    resized exports, screenshots of screenshots, and messaging-app re-encodes are
    exactly the material §2.6 names and exactly what byte identity cannot catch."
    """
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(_photos(tmp_path), database)
    assert code == 0, report

    found = _family(database, DUPLICATE_FAMILY_FIELD)
    original = found.get("IMG_4821.jpg")
    resaved = found.get("IMG_4821 resaved.jpg")
    assert original is not None and resaved is not None, (
        f"neither re-encoding carries a duplicate family: {found}")
    assert original[0] == resaved[0], found
    # §3.13 and `98` §2: anything weaker than byte identity is below `direct`.
    assert original[1] == "possible", found


def test_two_different_pictures_are_not_near_duplicates(tmp_path):
    """The twin, and the error `98` §3.2 says is the worse of the two.

    "Too loose -> two different photographs are called near-duplicates, and the
    review screen invites the owner to delete one of them." A threshold wide
    enough to join every JPEG in a corpus would satisfy the pin above, and `00`:128
    is what it would cost: the product "may use ... duplicate status ... to surface
    review suggestions" over files it must never delete.

    Green before the metric shipped, when no near family formed at all. Green now
    against a threshold that DOES join the two encodings above, in the same corpus
    and the same run -- which is what makes it a measurement of the number rather
    than of its absence.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(_photos(tmp_path), database)
    assert code == 0, report

    found = _family(database, DUPLICATE_FAMILY_FIELD)
    original = found.get("IMG_4821.jpg")
    other = found.get("IMG_5106.jpg")
    assert original is None or other is None or original[0] != other[0], found

    # And every image went through the image reader and came back complete, so the
    # pin above is waiting on `98`'s two words and not on an unread corpus.
    read = _extractors(database)
    for name in ("IMG_4821.jpg", "IMG_4821 resaved.jpg", "IMG_5106.jpg"):
        assert "image.metadata" in read.get(name, set()), (name, read)

    # And the near family this one is the negative of DID form in this same run:
    # the original is in a family, and the different picture is not in its family.
    assert original is not None, found
