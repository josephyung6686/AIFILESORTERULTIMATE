"""`104` §18.43, the audit's item 10: the two families that never form.

"Version families and near-duplicates never form (`version_family` uncalled,
`near_match=lambda: False`, no perceptual hash carrier; the rules are `97` and
`98`)." The owner ratified both on 2026-09-11 (`00`, Amendments of 2026-09-11,
item 4: "`97` (version lineage) and `98` (near-duplicate metric) are ratified as
written").

**Ratified as written, and as written neither authors a rule.** Both documents
carry the same status line -- "OWED TO THE OWNER. Nothing is authored here and
nothing is bound" -- and both spend their §3 saying which word the owner still has
to say. `97` §3 is titled "The decision the owner has to make" and introduces its
four candidate signals as "Candidate signals, **none of them ruled**"; §4 says why
an agent must not pick one ("`84` §1: absent means refuse, never guess ...
Authoring a version rule from a reading of the word 'version' would be an
implementation answering a deferred design question"). `98` §3.1 says `00` "names
no algorithm" and §3.2 says of the threshold that "the number is the owner's".

So the two pins below are red and stay red until a word arrives, and each xfail
names the word it is waiting for. The twin beside each one is the guard on the
other side: a rule that joined every pair, or a threshold that called every
photograph a near-duplicate of every other, would satisfy the xfail and be worse
than the refusal. They pass vacuously today -- nothing forms, so nothing over-forms
-- and they are what stops the eventual fix from passing by over-forming.

What is NOT waiting on a word, and is built: the blocking step `00`'s item 4
ratifies in the same sentence ("the comparison is kept sub-quadratic by a blocking
step"). `facts.families.version_family` takes `block_key` beside `lineage_rule`,
both required, and `tests/p6/test_p6_families.py` measures the bound with a
counting fake. A blocking key is a property of whichever rule ships, so the seam in
`cli.py` stays held: injecting a refusing rule and a refusing key would be `104`
§18.6's S6 dead arm in a second spelling.
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

    A pin that is waiting on a word must not be able to turn into a pin that is
    waiting on a file nobody opened. The two green twins assert this; the two
    xfails cannot, because a strict xfail is satisfied by ANY failure and would
    swallow the difference.
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
    (corpus / "Proposal draft.txt").write_text(
        f"{TITLE}\n\nSpring 2026. Supervisor: Dr. Lee.\n"
        "Section 1. The estuary is stratified for most of the year.\n")
    (corpus / "Proposal draft 2.txt").write_text(
        f"{TITLE}\n\nSpring 2026. Supervisor: Dr. Lee.\n"
        "Section 1. The estuary is stratified for most of the year.\n"
        "Section 2. Spring tides break the stratification down.\n")
    (corpus / "Proposal final.txt").write_text(
        f"{TITLE}\n\nSpring 2026. Supervisor: Dr. Lee.\n"
        "Section 1. The estuary is stratified for most of the year.\n"
        "Section 2. Spring tides break the stratification down.\n"
        "Section 3. Mixing is strongest at the mouth.\n")
    (corpus / "Electricity invoice March 2026.txt").write_text(
        "CLP Power Hong Kong Limited\n\nInvoice for March 2026.\n"
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


@pytest.mark.xfail(strict=True, reason=(
    "`facts.families.version_family` is never called. `cli.py`'s `_family_pass` "
    "states the refusal and defers: '§2.9 lists duplicate and version-family "
    "signals among what extraction produces and defines none of them, so there is "
    "no lineage rule to bind ... When a lineage rule is ruled, it arrives here "
    "with the call.' `97` was ratified as written on 2026-09-11 and AS WRITTEN IT "
    "RULES NOTHING. Its §3 is titled 'The decision the owner has to make'; it "
    "introduces its four candidates as 'Candidate signals, none of them ruled'; "
    "and of the four, §8.3 forbids one outright ('a filename match alone does "
    "not'), one needs 'a marker vocabulary, which does not exist', and one needs a "
    "'near-identical' prose threshold, which is a second number nobody ruled. §4 "
    "says why an agent may not pick from among them: 'Authoring a version rule "
    "from a reading of the word version would be an implementation answering a "
    "deferred design question.' FOUR WORDS ARE OWED, all of them `97`'s own: (1) "
    "THE RULE -- which evidence makes two files two versions of one document; (2) "
    "THE STATE -- `97` §2 lists `validated` and `possible` and rules neither, and "
    "the difference is whether P9 may anchor a group on the family at all "
    "(`grouping.seeds.ANCHOR_STATES` admits `validated` and not `possible`); (3) "
    "THE NAME -- `97` §3 calls this 'a second decision' and constrains it only "
    "negatively ('it must not be a file hash ... whatever names a version family "
    "must be safe to show and to send'), and `duplicate_family`'s own answer "
    "cannot be reused, because it names a family after the observation keys its "
    "members SHARE and an `observation_key` hashes the content hash, so two files "
    "with different bytes share none by construction; (4) THE ORDER -- a version "
    "family is ordered (a draft precedes a final) and `97` says nothing about "
    "ordering one anywhere, nor about timestamps, which is the evidence an order "
    "would have to read. The blocking step the same amendment ratifies is NOT "
    "waiting on any of that and is built: `version_family` takes `block_key` "
    "beside `lineage_rule`, measured in `tests/p6/test_p6_families.py`. Strict, so "
    "the suite turns red the day a rule is bound."))
def test_three_drafts_of_one_document_form_one_version_family(tmp_path):
    """`97` §5's own measurement, as a corpus: three drafts, one family."""
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(_drafts(tmp_path), database)
    assert code == 0, report

    found = _family(database, VERSION_FAMILY_FIELD)
    drafts = {name: found[name] for name in
              ("Proposal draft.txt", "Proposal draft 2.txt", "Proposal final.txt")
              if name in found}
    assert len(drafts) == 3, f"only {sorted(drafts)} carry a version family: {found}"
    assert len({value for value, _state in drafts.values()}) == 1, drafts


def test_two_unrelated_documents_are_not_one_version_family(tmp_path):
    """The twin, and the reason it is here before there is anything to catch.

    A lineage rule that answered for every pair would satisfy the pin above and be
    worse than the refusal it replaces: `97` §3 requires the rule to cite real
    observations precisely so a family nobody can point at is not written. A
    thesis proposal and an electricity bill share a corpus and nothing else.

    It passes vacuously today -- no version family forms at all -- which is stated
    rather than hidden: what it is for is the day the pin above goes green.
    """
    database = tmp_path / "holder" / "plan.sqlite"
    code, report = _run(_drafts(tmp_path), database)
    assert code == 0, report

    found = _family(database, VERSION_FAMILY_FIELD)
    draft = found.get("Proposal draft.txt")
    invoice = found.get("Electricity invoice March 2026.txt")
    assert draft is None or invoice is None or draft[0] != invoice[0], found

    # And the four documents were read: the pin above waits on a rule, not on a
    # file nothing opened.
    read = _extractors(database)
    for name in ("Proposal draft.txt", "Proposal draft 2.txt",
                 "Proposal final.txt", "Electricity invoice March 2026.txt"):
        assert "text.structured" in read.get(name, set()), (name, read)


# --- `98`: near-duplicates ------------------------------------------------------


@pytest.mark.xfail(strict=True, reason=(
    "`near_match` is `lambda left, right: False` at `cli.py` ~13826 and the wired "
    "`readers.image_headers` supplies no perceptual hash, so `_near_families` "
    "counts fewer than two carriers and returns before its loop -- 0 carriers "
    "measured on both real corpora. `98` was ratified as written on 2026-09-11 and "
    "AS WRITTEN IT NAMES NEITHER HALF. §3.1: `00` 'names no algorithm', and "
    "'whatever ships must be stated together with the hash it assumes'. §3.2: the "
    "threshold 'is a judgement about the owner's tolerance, not a technical "
    "constant ... the number is the owner's', and it trades two errors that are "
    "not symmetric -- 'too loose, two different photographs are called "
    "near-duplicates, and the review screen invites the owner to delete one of "
    "them; too tight, a resized or re-exported copy of one photo is treated as two "
    "files'. §3 closes the escape hatch: 'Equality is not a way out ... it is a "
    "threshold of zero, and zero is a number nobody ruled.' TWO WORDS ARE OWED: "
    "the hash, and the distance. Both halves are one constant each once they are "
    "said, and no dependency arrives with them -- "
    "`CGImageSourceCreateThumbnailAtIndex` decodes a small raster through the "
    "ImageIO `readers/image_headers.py` already imports. Strict, so the suite "
    "turns red the day the metric ships."))
def test_a_resaved_copy_of_one_image_is_a_near_duplicate_of_it(tmp_path):
    """`98` §4's own material: one picture, two encodings, two content hashes."""
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

    Vacuous today for the same reason as its counterpart above, and here for the
    same day.
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
