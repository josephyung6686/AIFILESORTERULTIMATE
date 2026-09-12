# tests/test_cli_detects_extensionless_files.py
"""The nine files on the owner's disk with no extension at all, which read as nothing.

`.groundtruth/baseline/scorecard.txt`, 2026-09-04: `(none)  0 of 9  0.0%`. All nine
recorded `unsupported`, and the reason was mechanical rather than interesting --
`route()` keys on a format token, `detect_format` answered None, and the declared
extension of `LICENSE` is the empty string, which is a key in no table. Nothing ever
tried to read them.

Seven of the nine are named by a convention a tool requires by that exact spelling,
and that convention is what this detector reads. It is the SAME kind of statement as
`readers/text_documents._MARKERS_BY_FILENAME` -- "a statement about those tools and
not a judgement about a project" -- and it lives in `cli.py` because §2.9 puts the
mapping from a real-world signal onto the router's token space in the DEPLOYMENT:
"A real deployment maps libmagic's MIME type or macOS's UTType onto that token space,
and THAT mapping belongs to the reader."

THE OTHER TWO ARE NAMED BY NOTHING: a Google-Fonts stylesheet saved as `css2` and
Premiere's `LocateDialog Column Settings`. When this file was written, sniffing them
was not available -- reading bytes to decide a format would have opened a file before
`is_protected_container` had its say, and that guard is by PATH and runs after
routing -- so an honest `unsupported` was the answer for both.

**THAT CHANGED ON 2026-09-06 AND THE SECOND HALF OF THIS FILE IS THE CHANGE.** R-30:
`readers/signatures.py` was written for exactly these files and `94` F22 recorded
that it "is not wired into `cli._detect_format`". It is now, asked LAST -- after the
extension and after the name, both of which still answer without opening anything --
and it carries the protected-container predicate as an argument it cannot be built
without, so the reason above is obeyed rather than overturned. The stylesheet is
text and is now read as text; the Premiere file is nothing the reader knows and is
still `unsupported`, which is still the truth.
"""
from __future__ import annotations

import builtins
import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import cli  # noqa: E402
from extractors.router import route  # noqa: E402

HASH = "67e9bc3cfd2163c2978358dfe00d2f912cd4ee0c99f077c3583b39b48aebb124"

#: `104` SF-3. A group is a DRAFT until somebody decides it (see `test_cli.py`'s
#: own docstring for the ruling); the one test below that reads a frozen plan has
#: to type the accept, same as a person does, or there is no plan yet to freeze.
ACCEPTS_THE_PROPOSAL: tuple[str, ...] = ("--accept-groups",)


def routed(name: str):
    path = Path("/corpus") / name
    return route(file_id="f1", content_hash=HASH, path=path,
                 extension=path.suffix, detect_format=cli._detect_format)


# --------------------------------------------------------------------------- #
# the seven that are named by a convention
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name,token", [
    # Every one of these is a real path in `.groundtruth/corpus/`.
    ("LICENSE", "txt"),
    ("NOTICE", "txt"),
    ("AUTHORS", "txt"),
    ("THANKS", "txt"),
    ("LICENSE-CC-BY-NC-SA", "txt"),
    ("Dockerfile", "dockerfile"),
    ("Makefile", "makefile"),
])
def test_a_conventionally_named_extensionless_file_is_detected(name, token):
    assert cli._detect_format(Path("/corpus") / name) == token


@pytest.mark.parametrize("name", ["LICENSE", "NOTICE", "AUTHORS", "THANKS",
                                  "LICENSE-CC-BY-NC-SA", "Dockerfile", "Makefile"])
def test_each_of_the_seven_reaches_an_extractor_instead_of_stopping(name):
    decision = routed(name)
    assert decision.extractor_name == "text.structured"
    assert decision.unrouted_completeness is None
    assert decision.disagree is False, (
        "an absent extension is not a wrong one; recording these as disagreements "
        "would put seven false 'this file is misnamed' rows in extraction_routing")


def test_the_licence_and_notice_files_are_prose_and_the_build_files_are_code():
    """§2.4's own split, kept. A LICENCE is a document a person reads; a Dockerfile
    is a recipe, and §2.4 asks for structural evidence from those "rather than
    forcing semantic analysis to infer a project from arbitrary code text"."""
    assert routed("LICENSE").source_type == "text_document"
    assert routed("NOTICE").source_type == "text_document"
    assert routed("Dockerfile").source_type == "code_structured"
    assert routed("Makefile").source_type == "code_structured"


def test_the_licence_variant_spellings_are_the_same_convention():
    """`LICENSE-CC-BY-NC-SA` is how Creative Commons and the GNU licences are
    conventionally spelled, and one is on this disk. The name before the first
    hyphen is what carries the convention."""
    assert cli._detect_format(Path("/x/LICENSE-CC-BY-NC-SA")) == "txt"
    assert cli._detect_format(Path("/x/LICENSE-APACHE")) == "txt"
    assert cli._detect_format(Path("/x/COPYING-LESSER")) == "txt"


def test_the_convention_is_read_case_insensitively():
    """`license`, `LICENSE` and `License` are one convention and three spellings,
    and a real disk holds all three."""
    for spelling in ("license", "LICENSE", "License", "makefile", "MAKEFILE"):
        assert cli._detect_format(Path("/x") / spelling) is not None, spelling


def test_every_name_in_the_table_has_a_file_behind_it_or_a_reason():
    """The rule `extractors/router.py`'s own additions follow: "nothing is here for
    a language the owner does not write". A table that grew by imagination would
    route files nobody has, and the first speculative entry is the one that makes
    the next reviewer stop checking. Seven were counted on the corpus; the two that
    were not are named here with the reason they are exceptions."""
    counted_on_the_corpus = {"license", "notice", "authors", "thanks",
                             "dockerfile", "makefile"}
    named_for_a_stated_reason = {
        "readme",    # `text_documents._markers_for` already knows it by stem
        "copying",   # the GNU spelling of `license`, in the same trees
    }
    assert set(cli._FORMAT_BY_EXTENSIONLESS_NAME) == (counted_on_the_corpus
                                                      | named_for_a_stated_reason)


# --------------------------------------------------------------------------- #
# the guards
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", ["css2", "LocateDialog Column Settings"])
def test_the_two_that_no_convention_names_are_unsupported_on_their_name_alone(name):
    """Both are real corpus files and neither is guessable from its NAME.

    THIS TEST USED TO SAY MORE THAN IT MEASURED. It asserted that these two "stay
    honestly unsupported" and gave the reason: reading bytes to decide a format
    "would open a file before `is_protected_container` has had its say". That
    reason was retired on 2026-09-06 -- `readers.signatures` takes the predicate as
    a required argument and answers `None` for a protected path without reading a
    byte -- and the assertion below survived the change only because `/corpus` does
    not exist, so there were no bytes to read either way. What it measures is the
    name, which is what its title now says. What the bytes add is the two tests
    below it.
    """
    assert cli._detect_format(Path("/corpus") / name) is None
    assert routed(name).unrouted_completeness == "unsupported"


def test_bytes_that_are_text_under_an_extension_nothing_knows_are_read(tmp_path):
    """`css2` is a Google-Fonts stylesheet and it is text, so now it is read.

    An extension the router has never heard of is not a routing signal, so there is
    nothing here for the bytes to overrule -- the same argument as an extensionless
    file, one step further out. §2.4's rule is unbroken in the direction that
    matters: nothing is treated as an empty document, and a file that IS text stops
    being called unsupported.
    """
    stylesheet = tmp_path / "css2"
    stylesheet.write_text("@font-face { font-family: 'Inter'; src: url(x.woff2); }")

    assert cli._detect_format(stylesheet) == "txt"


def test_bytes_that_are_nothing_the_reader_knows_stay_honestly_unsupported(tmp_path):
    """§2.4: "The system should never silently treat an unsupported format as an
    empty document" -- and it does not; it says `unsupported`, which is the truth.

    Premiere's `LocateDialog Column Settings` is the corpus file this stands for: no
    magic number, no text, no convention. Nothing here guesses.
    """
    opaque = tmp_path / "LocateDialog Column Settings"
    opaque.write_bytes(bytes(range(1, 32)) * 8)

    assert cli._detect_format(opaque) is None
    assert routed("LocateDialog Column Settings").unrouted_completeness == \
        "unsupported"


def test_a_file_that_HAS_an_extension_is_never_renamed_by_this_table():
    """The table answers for extensionless files only. `license.py` is Python and
    `Makefile.md` is Markdown, and letting a stem override a real extension would
    be the detector overruling the thing §2.9 calls the routing signal.

    THE ASSERTIONS CHANGED SHAPE AND THE QUESTION DID NOT. They used to read
    `is None`, which was a PROXY for "the name table did not fire" that only held
    while `_detect_format` returned None for every extension outside its five-entry
    map. `104` §18.2 gap 21 deleted that map, so a missing file now falls through to
    `signature_detector`'s own OSError arm, which answers with the extension the
    router already knows. What this test is about is the word `txt`: none of these
    six may come back as the licence convention's answer.

    SABOTAGE: drop the `if not path.suffix` guard from `_detect_format` and
    `license.py` comes back `txt` -- a Python module renamed by half its filename.
    """
    for name, token in (("license.py", "py"), ("Makefile.md", "md"),
                        ("notice.pdf", "pdf"),
                        # The hyphen rule is the one with teeth here.
                        # `license-loader.py` starts with a word the table knows, and
                        # without the `path.suffix` guard the split would hand a
                        # Python module back as `txt`.
                        ("license-loader.py", "py"),
                        ("readme-generator.sh", "sh"),
                        ("makefile-helper.js", "js")):
        detected = cli._detect_format(Path("/x") / name)
        assert detected == token, name
        assert detected != cli._FORMAT_BY_EXTENSIONLESS_NAME.get(
            name.split(".")[0].split("-")[0].lower()), name


def test_a_file_that_cannot_be_opened_at_all_is_still_routed_by_its_path():
    """The detector opens files now, and neither of these two needs it to.

    THE OLD TITLE WAS "the detector still opens nothing" and that is no longer
    true; what stayed true is the property it was protecting. An extension the
    router knows and a name a convention claims are both answered before any byte
    is read, so a file that is missing, unreadable or on a volume that has gone
    away still reaches its extractor. Handed paths that do not exist to prove it.

    The rule that made the old form necessary is enforced where it belongs now:
    `signature_detector` takes `is_protected_container` as an argument it cannot be
    built without, and `test_a_protected_container_is_not_opened_to_name_its_format`
    below is that guard.
    """
    assert cli._detect_format(Path("/nowhere/at/all/LICENSE")) == "txt"
    assert cli._detect_format(Path("/nowhere/at/all/thing.pdf")) == "pdf"


# --------------------------------------------------------------------------- #
# R-30: the ones no name answers for, which is what the signature is for
# --------------------------------------------------------------------------- #
#
# `94` F22, measured 2026-09-03: a plain text file called `noextension` appeared in
# NEITHER list of the freeze block. The omission half of that is fixed -- it is named
# under "Not frozen" with a reason -- and the routing half was not: the reason it
# gives is "nothing has looked inside this one yet", and nothing ever would.
# `readers/signatures.py` was written for exactly this and F22 records that it "is
# not wired into `cli._detect_format`".
#
# THE SIGNATURE IS NOW ASKED FOR EVERY FILE, AND `104` §18.2 GAP 21 IS WHY. What
# stood here said it was "asked LAST and ONLY where the other two answer nothing",
# on a measurement: asking it first changed seven operative formats on the owner's
# 21-file sample, five `.ipynb` and a `.code-workspace` to `json` and a `.jpeg` to
# `jpg`, and recorded seven disagreements in a column `router.py` keeps precisely so
# the disagreement "is not manufactured".
#
# THE MEASUREMENT SURVIVES AND THE CONCLUSION DOES NOT. Checked against the router's
# tables rather than against the tokens: `ipynb`, `code-workspace` and `json` all
# carry `code_structured` and `text.structured`; `jpeg` and `jpg` both carry `image`
# and `image.metadata`. Not one of the seven changes where the file goes -- they gain
# a true row saying the name and the bytes spell one format two ways.
#
# What the extension shortcut cost, on every OTHER file: `detected_format` NULL (the
# map held five suffixes and the router knows sixty), a `disagree` column that could
# not fire because a value read off the extension cannot contradict the extension,
# and §2.9's indexed-but-unreadable `format` observation, which
# `filesystem.unrouted_result` writes only `if detected:`.
#
# The name table is still asked before the signature, for an extensionless file: a
# real `Dockerfile` is text, so the sniffer's weak answer is `txt`, and taking it
# would move every Dockerfile on a disk from `code_structured` to `text_document`. A
# file named by a convention has said what it is.

_SYLLABUS = (
    "PHYS 1401 Syllabus",
    "Spring 2026. Instructor: Dr. Lee. Credits: 3.",
    "Assessment: midterm 30 percent, final examination 50 percent.",
)
#: Both lectures carry the course, the semester and the instructor, and both say
#: `lecture` more than once. That is not decoration: a thinner draft of these two --
#: the title, the term and one sentence of physics -- reached the same three
#: validated facts and was never CLASSIFIED, so both lectures came back "nothing has
#: looked inside this one yet" and the comparison was between two blanks. A fixture
#: has to clear every gate that stands between the bytes and the freeze block or it
#: is not measuring the one this file is about.
_LECTURE_08 = (
    "PHYS 1401 Lecture 08 - Rotational Dynamics",
    "Course: PHYS 1401. Semester: Spring 2026. Instructor: Dr. Lee.",
    "Lecture notes. Torque and angular momentum.",
    "Reading for this lecture is in the course syllabus; homework 3 follows.",
)
_LECTURE_09 = (
    "PHYS 1401 Lecture 09 - Simple Harmonic Motion",
    "Course: PHYS 1401. Semester: Spring 2026. Instructor: Dr. Lee.",
    "Lecture notes. Springs, pendulums and the small-angle approximation.",
    "Reading for this lecture is in the course syllabus; homework 4 follows.",
)


def _one_page_pdf(lines) -> bytes:
    """A real single-page PDF carrying `lines` as text, built with the stdlib.

    The same construction `tests/test_cli.py` uses and for the same reason: what a
    magic-number test needs is a file the shipped reader will actually READ, not
    bytes that merely start with `%PDF`. Spelled out here rather than imported
    across test modules.
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


def test_an_extensionless_pdf_is_detected_by_its_signature(tmp_path):
    """The bytes say PDF and no name does. Today nothing asks the bytes."""
    report = tmp_path / "PHYS 1401 lecture 09"
    report.write_bytes(_one_page_pdf(_LECTURE_09))

    assert cli._detect_format(report) == "pdf"


def test_an_extensionless_text_file_is_detected_as_text(tmp_path):
    """`94` F22's own file, by name. The weak answer is right when nothing else
    answered: `noextension` decodes as text and no extension is being overruled."""
    noextension = tmp_path / "noextension"
    noextension.write_text("Lecture 08 - Rotational Dynamics\nPHYS 1401\n")

    assert cli._detect_format(noextension) == "txt"


def test_an_extensionless_pdf_is_frozen_and_placed_like_its_named_twin(tmp_path):
    """R-30 end to end: the same document, one named `.pdf` and one named nothing.

    Both are lectures of the same course, so both belong in the same branch, and a
    syllabus is there to give the branch a second leaf to be distinguished from.
    Before the wiring the extensionless one is named under "Not frozen" as a file
    nothing has looked inside -- which is `84` §1's rule honoured and §2.9's routing
    signal still missing.
    """
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "PHYS 1401 syllabus.pdf").write_bytes(_one_page_pdf(_SYLLABUS))
    (corpus / "PHYS 1401 lecture 08.pdf").write_bytes(_one_page_pdf(_LECTURE_08))
    (corpus / "PHYS 1401 lecture 09").write_bytes(_one_page_pdf(_LECTURE_09))

    out = io.StringIO()
    assert cli.main([str(corpus), "--situation", "academic.coursework",
                     "--label", "Coursework", "--user", "t",
                     "--database", str(tmp_path / "plan.sqlite"),
                     "--freeze", *ACCEPTS_THE_PROPOSAL], out=out) == 0
    printed = out.getvalue()

    frozen = printed.split("Frozen:", 1)[-1].split("Not frozen", 1)[0]
    lectures = frozen.split("Coursework/lecture", 1)[-1].split("Move these:", 1)[0]

    assert "PHYS 1401 lecture 08.pdf" in lectures, printed
    assert "PHYS 1401 lecture 09" in lectures, (
        "the extensionless twin of a file that WAS frozen is still unread, so it "
        "is named under 'Not frozen' as a file nothing has looked inside:\n"
        + printed)
    assert "PHYS 1401 syllabus.pdf" in frozen, (
        "the branch the two lectures had to be told apart from is gone, so they "
        "could have landed together for a reason that is not this one:\n" + printed)


def test_a_protected_container_is_not_opened_to_name_its_format(tmp_path):
    """The one rule with no override, and the reason the old detector read nothing.

    These bytes are a PDF and saying so would require opening them. §4b: the
    contents of an application bundle are never examined, and the judgement is made
    by PATH before any format question is asked.
    """
    bundle = tmp_path / "Notes.app" / "Contents"
    bundle.mkdir(parents=True)
    inside = bundle / "manual"
    inside.write_bytes(_one_page_pdf(_SYLLABUS))

    assert cli._detect_format(inside) is None


def test_a_conventional_name_still_beats_the_bytes(tmp_path):
    """A real `Dockerfile` and a real `LICENSE`, on disk, with content to sniff.

    Both decode as text, so the signature's weak answer for both is `txt`. Taking
    it would move every Dockerfile on a disk out of `code_structured`, which is the
    measurement that fixed this order.
    """
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\nRUN pip install .\n")
    (tmp_path / "LICENSE").write_text("MIT License\n\nPermission is hereby granted")

    assert cli._detect_format(tmp_path / "Dockerfile") == "dockerfile"
    assert cli._detect_format(tmp_path / "LICENSE") == "txt"


# --------------------------------------------------------------------------- #
# `104` §18.2 gap 21: the signature runs for every file
# --------------------------------------------------------------------------- #

_PNG = (b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR"
        + b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        + b"\x1f\x15\xc4\x89")
#: Photoshop's magic number (`8BPS`). §2.9 routes `psd` to `design_creative`, which
#: has no extractor, which is the M3 "indexed-but-unreadable" case.
_PSD = b"8BPS\x00\x01" + b"\x00" * 32


def _minimal_docx(path: Path) -> Path:
    """A ZIP holding `word/document.xml`, which is what OOXML says a `.docx` IS.

    Built with `zipfile` rather than python-docx on purpose: the question here is
    what `readers/signatures.py` reads out of the container, and a real library
    would make the fixture depend on a package this test file does not otherwise
    need.
    """
    import zipfile
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml",
                         "<w:document><w:body/></w:document>")
    return path


def test_a_pdf_named_txt_is_detected_by_its_bytes_and_the_lie_is_recorded(tmp_path):
    """`104` §18.2 gap 21. A file whose extension lies, which is what §2.9 is for.

    `readers/signatures.py` opens with the promise that "a PDF named `notes.txt` is
    read as a PDF ... which is what makes `extraction_routing.disagree` mean
    something", and until this it was false in the shipped product: `_detect_format`
    returned `txt` from a five-entry extension map and the signature reader never
    ran. The file was handed to the plain-text reader, agreed with itself, and the
    person was never told.

    SABOTAGE: put back `if declared in SOURCE_TYPE_BY_FORMAT: return
    _FORMAT_BY_EXTENSION.get(...)` at the top of `_detect_format`. Every assertion
    below goes red at once, and the routing one is the one that matters: the
    document reaches `text.structured` and its pages are never read.
    """
    misnamed = tmp_path / "PHYS 1401 notes.txt"
    misnamed.write_bytes(_one_page_pdf(_LECTURE_08))

    assert cli._detect_format(misnamed) == "pdf"

    decision = route(file_id="f1", content_hash=HASH, path=misnamed,
                     extension=misnamed.suffix, detect_format=cli._detect_format)
    assert decision.detected_format == "pdf"
    # The extension is the HINT, recorded beside the detected format rather than
    # instead of it. §2.9: "treat the file extension as a ROUTING SIGNAL."
    assert decision.declared_extension == ".txt"
    assert decision.disagree is True, (
        "the bytes and the name spell different formats and the router's own record "
        "is where §2.9 keeps that, 'rather than discarded'")
    # And the consequence, which is the point of recording it at all.
    assert decision.extractor_name == "pdf.text"


def test_the_detected_format_is_written_for_a_pdf_a_docx_and_a_png(tmp_path):
    """`104` §18.2 gap 21: "detected format null for most files".

    Three real fixtures whose bytes identify them positively. Before the patch the
    PDF and the DOCX answered from the extension map (the same token, never looked
    at) and the PNG answered NOTHING -- `.png` is a format the router routes and was
    not one of the map's five, so `.get()` missed and `detected_format` was NULL for
    every image on the disk.

    SABOTAGE: restore the extension shortcut and the PNG line goes red on its own,
    which is the honest signal -- the two that pass either way are the two the old
    map happened to name.
    """
    report = tmp_path / "report.pdf"
    report.write_bytes(_one_page_pdf(_SYLLABUS))
    document = _minimal_docx(tmp_path / "essay.docx")
    image = tmp_path / "scan.png"
    image.write_bytes(_PNG)

    for path, token in ((report, "pdf"), (document, "docx"), (image, "png")):
        decision = route(file_id="f1", content_hash=HASH, path=path,
                         extension=path.suffix, detect_format=cli._detect_format)
        assert decision.detected_format == token, path.name
        assert decision.disagree is False, (
            f"{path.name} is named exactly what it is; a disagreement here would be "
            "manufactured")


def test_a_plain_text_file_still_records_no_detected_format(tmp_path):
    """The limit of gap 21's patch, asserted so it is not mistaken for a bug.

    `signature_detector` returns None rather than its weak `txt` whenever the router
    already knows the extension, and its own docstring gives the measured reason:
    "these bytes are text" identifies no format, so returning `txt` "would override
    the extension on every `.csv`, `.md` and `.ics` on the disk and route them all to
    the plain-text handler ... `grades.csv` would stop reaching the spreadsheet
    reader". A null here is the truthful answer -- nothing about these bytes named a
    format -- and the file still routes on its extension.

    SABOTAGE: drop the `declared in SOURCE_TYPE_BY_FORMAT` guard from
    `signature_detector`'s final line and a spreadsheet becomes a text document.
    """
    notes = tmp_path / "notes.txt"
    notes.write_text("Lecture 08 - Rotational Dynamics\n")
    sheet = tmp_path / "grades.csv"
    sheet.write_text("student,mark\nA,91\n")

    for path, source_type in ((notes, "text_document"), (sheet, "spreadsheet")):
        decision = route(file_id="f1", content_hash=HASH, path=path,
                         extension=path.suffix, detect_format=cli._detect_format)
        assert decision.detected_format is None, path.name
        assert decision.disagree is False
        assert decision.source_type == source_type


def test_the_unreadable_files_format_observation_is_written(tmp_path):
    """`104` §18.2 gap 21's third casualty: §2.9's M3 clause, dead on arrival.

    "Unsupported proprietary formats should be recorded as indexed-but-unreadable
    rather than silently treated as empty", and `filesystem.unrouted_result` spells
    "indexed" as two metadata-level rows -- the filename and the FORMAT. The format
    row is guarded by `if detected:`, and `.psd` was not one of the extension map's
    five, so the one file class that clause exists for recorded its name and nothing
    else. The `failure_reason` said "no extractor exists for THIS FORMAT" because
    there was no format to name.

    SABOTAGE: restore the extension shortcut. `detected_format` goes null, the
    format observation disappears, and the sentence the person reads loses the only
    word in it that says what the file is.
    """
    from extractors.filesystem import unrouted_result

    artwork = tmp_path / "poster.psd"
    artwork.write_bytes(_PSD)

    decision = route(file_id="f1", content_hash=HASH, path=artwork,
                     extension=artwork.suffix, detect_format=cli._detect_format)
    assert decision.detected_format == "psd"
    assert decision.unrouted_completeness == "unreadable"

    result = unrouted_result(
        file_row={"file_id": "f1", "content_hash": HASH, "filename": "poster.psd"},
        decision=decision, now="2026-09-09T00:00:00Z")
    formats = [o for o in result.observations
               if o["location"]["container_path"]
               and o["location"]["container_path"][-1].get("label") == "format"]
    assert [o["raw_value"] for o in formats] == ["psd"]
    assert "psd" in result.run["failure_reason"]


def test_the_seven_spelling_variants_disagree_and_route_identically(tmp_path):
    """The measurement that argued for the extension shortcut, now made a guard.

    A notebook IS JSON and a `.jpeg` IS a `jpg`. The old function refused to look at
    them because looking would record a disagreement, and the disagreement was
    called false. It is not false -- the name and the bytes really do spell one
    format two ways -- it is merely HARMLESS, and this is what "harmless" means
    precisely: the same `source_type` and the same extractor either way, so the row
    tells the owner about a spelling and changes nothing about the file.

    SABOTAGE: give `route()` a precedence rule that prefers the extension. The
    disagreement stops being recorded and gap 21 is back with a different shape.
    """
    notebook = tmp_path / "lecture01_introduction.ipynb"
    notebook.write_text('{"cells": [], "nbformat": 4}')
    photo = tmp_path / "booster.jpeg"
    photo.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00")

    for path, detected, family, handler in (
            (notebook, "json", "code_structured", "text.structured"),
            (photo, "jpg", "image", "image.metadata")):
        decision = route(file_id="f1", content_hash=HASH, path=path,
                         extension=path.suffix, detect_format=cli._detect_format)
        assert decision.detected_format == detected, path.name
        assert decision.disagree is True, path.name
        assert decision.source_type == family, path.name
        assert decision.extractor_name == handler, path.name


def test_an_evicted_file_is_never_opened_to_name_its_format(tmp_path, monkeypatch):
    """11 §5, and the rule the deleted extension shortcut was accidentally enforcing.

    "P3 detects a dataless / not-downloaded ubiquitous item before hashing ... DO NOT
    MATERIALIZE, hash, or extract." `_detect_format` opens files now, and opening an
    iCloud-evicted one does not raise -- it DOWNLOADS it, which is the exact event
    the rule exists to prevent. `SafetyPolicy.is_dataless` does not cover this: it
    guards `admit()`, inside the extractor, and `orchestrator.py`'s pass 2b routes
    every evicted file before any extractor is chosen.

    `SF_DATALESS` is outside macOS's `SF_SETTABLE` mask, so no test can set it on a
    real file and the predicate is substituted instead -- `scan_agent.dataless`'s own
    docstring names that constraint.

    SABOTAGE: delete the `is_dataless` guard at the top of `_detect_format`. `open()`
    is spied on here rather than asserted about afterwards, because on a real machine
    the download is the damage and it has already happened by the time anything could
    be checked.
    """
    evicted = tmp_path / "thesis-final.pdf"
    evicted.write_bytes(_one_page_pdf(_SYLLABUS))

    monkeypatch.setattr(cli, "is_dataless", lambda stat_result: True)
    opened: list[str] = []
    real_open = builtins.open

    def spy(target, *args, **kwargs):
        opened.append(str(target))
        return real_open(target, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", spy)

    assert cli._detect_format(evicted) is None
    assert str(evicted) not in opened, (
        "an evicted file was opened to name its format, which on a real disk is the "
        "iCloud download 11 §5 forbids")

    # And it still routes, on the extension, exactly as it did before the bytes were
    # ever consulted -- the `dataless` run C4 exists for needs a `source_type`.
    decision = route(file_id="f1", content_hash=HASH, path=evicted,
                     extension=evicted.suffix, detect_format=cli._detect_format)
    assert decision.source_type == "text_document"
    assert decision.disagree is False


def test_a_known_extension_is_still_answered_when_the_file_cannot_be_opened():
    """A missing, unreadable or gone-away file still reaches its extractor.

    This is the half of the old `test_a_known_extension_is_still_answered_without_
    reading_the_file` that survives gap 21. The bytes ARE consulted now, and when
    there are none to consult `signature_detector` falls back to the extension the
    router knows rather than to None -- its own comment says why: the file is
    "unreadable for a reason that is not this module's to diagnose", and the
    extractor that opens it will raise and record §2.4's `failed`, which is the
    honest place for it.
    """
    assert cli._detect_format(Path("/nowhere/at/all/thing.pdf")) == "pdf"
    assert cli._detect_format(Path("/nowhere/at/all/sheet.csv")) == "csv"
    assert cli._detect_format(Path("/nowhere/at/all/thing.wat")) is None
