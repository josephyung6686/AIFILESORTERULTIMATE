"""The reader that stopped a `.rtf` and a `.html` arriving as their own source code.

`deployment.py` wired `read_text_document = read_text_file`, which decoded the bytes
as UTF-8 and returned them. Measured over a real folder on 2026-09-03, that produced
a `complete` extraction whose prose observation -- the one the recogniser reads -- was
`{\\rtf1\\ansi\\ansicpg1252\\cocoartf2822` for a letter of recommendation, and
`<!DOCTYPE html><html><head><style>` for a registration confirmation, the page's
`<script>` body included. That is not missing information. It is false information,
stored as complete, about a file the product claims to have read.

Every heading asserted here comes from something the FORMAT says -- an ATX marker, an
`<h2>` element, ODF's `text:outline-level` -- and never from a line being short.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from readers.text_documents import stdlib_text_document_reader

read = stdlib_text_document_reader()


def headings(document) -> list[tuple[int, str, str]]:
    """Each heading as `(ordinal, label, the text the region actually covers)`.

    The third element is the one that matters: a `Region` is a pair of offsets into
    the document's own text, and a label that does not match its own span is a
    citation pointing at the wrong words.
    """
    return [(region.ordinal, region.label, document.text[region.start:region.end])
            for region in document.headings]


# --------------------------------------------------------------------------- #
# plain text and Markdown
# --------------------------------------------------------------------------- #

def test_plain_text_is_returned_unchanged_and_claims_no_headings(tmp_path):
    """The one format the old reader got right, and it stays right."""
    path = tmp_path / "syllabus.txt"
    path.write_text("PHYS 1401\nOffice hours: Tuesdays 14:00\n")

    document = read(path)

    assert document.text == "PHYS 1401\nOffice hours: Tuesdays 14:00\n"
    assert document.headings == ()
    assert document.markers == ()
    assert document.language is None


def test_markdown_headings_are_read_from_both_of_commonmarks_syntaxes(tmp_path):
    """§2.9 asks a text document for "headings". A `.md` yielded none: the previous
    reader "does not claim to be a Markdown reader", so every heading in every
    Markdown file on a person's disk was invisible to the product."""
    path = tmp_path / "lab notes.md"
    path.write_text("# Lab 4 -- Momentum\n\n"
                    "Some prose about the air track.\n\n"
                    "Apparatus\n=========\n\n"
                    "## Results ##\n\n"
                    "The coefficient was 0.98.\n")

    document = read(path)

    assert headings(document) == [
        (1, "Lab 4 -- Momentum", "Lab 4 -- Momentum"),
        (2, "Apparatus", "Apparatus"),
        (3, "Results", "Results"),
    ]
    assert document.text.startswith("# Lab 4 -- Momentum\n")


def test_a_hash_inside_a_fenced_code_block_is_not_a_heading(tmp_path):
    """CommonMark §4.5. A shell comment in a fenced block is a comment, and filing it
    as a document's structure would put a line of somebody's terminal in the outline."""
    path = tmp_path / "setup.md"
    path.write_text("# Install\n\n```sh\n# run this first\nmake\n```\n\n# Use\n")

    assert [region.label for region in read(path).headings] == ["Install", "Use"]


def test_a_setext_underline_under_nothing_is_not_a_heading(tmp_path):
    """A horizontal rule opens many documents. Read as a Setext underline it would
    make a heading out of the blank line above it."""
    path = tmp_path / "notes.md"
    path.write_text("\n---\n\nJust prose.\n")

    assert read(path).headings == ()


# --------------------------------------------------------------------------- #
# HTML
# --------------------------------------------------------------------------- #

PAGE = """<!DOCTYPE html>
<html><head><title>Registration Confirmation</title>
<style>body { font-family: Helvetica; }</style>
<script>var tracking = "do-not-extract-this";</script>
</head><body>
<h1>Registration Confirmation</h1>
<p>You are enrolled in <b>PHYS 1401</b> for Spring&nbsp;2026.</p>
<h2>Your schedule</h2>
<table><tr><td>PHYS 1401</td><td>Science Hall 120</td></tr></table>
</body></html>
"""


def test_html_yields_the_text_a_person_sees_and_not_the_page_source(tmp_path):
    path = tmp_path / "registration.html"
    path.write_text(PAGE)

    document = read(path)

    assert "<h1>" not in document.text
    assert "<!DOCTYPE" not in document.text
    assert "PHYS 1401" in document.text
    assert "Spring 2026" in document.text


def test_a_script_and_a_style_block_never_reach_the_documents_text(tmp_path):
    """The measured defect: a page's tracking snippet and its CSS were stored as the
    document's prose and read by the recogniser as if the author had written them."""
    path = tmp_path / "registration.html"
    path.write_text(PAGE)

    text = read(path).text

    assert "do-not-extract-this" not in text
    assert "font-family" not in text
    assert "tracking" not in text


def test_a_pages_title_is_the_one_line_of_it_a_person_always_sees(tmp_path):
    """`head` was suppressed WHOLESALE, and `<title>` is inside it.

    Measured on the owner's disk: of 207 `.html` files outside vendor directories,
    130 yielded not one character. Twenty of those are single-page-application
    shells whose body is an empty mount point and whose ONLY prose is the title --
    verbatim below, from `~/Desktop/Devfest/index.html`. The page's own name is what
    a browser puts in the tab and a bookmark, and it was the one thing thrown away.

    `script`, `style` and `noscript` stay suppressed by their OWN entries, which is
    why dropping `head` does not put a tracking snippet back into the prose --
    `test_a_script_and_a_style_block_never_reach_the_documents_text` is the guard.
    """
    path = tmp_path / "index.html"
    path.write_text(
        '<!doctype html>\n<html lang="en" class="dark">\n  <head>\n'
        '    <meta charset="UTF-8" />\n'
        '    <title>Third Eye - AI-Powered Learning Assistant</title>\n'
        '    <script src="https://cdn.example/three.min.js"></script>\n'
        '  </head>\n  <body>\n'
        '    <div id="root"><!-- React will mount here --></div>\n'
        '    <script type="module" src="/src/main.tsx"></script>\n'
        '  </body>\n</html>\n')

    text = read(path).text

    assert "Third Eye - AI-Powered Learning Assistant" in text
    assert "three.min.js" not in text          # the head's <script> is still dropped
    assert "charset" not in text               # and <meta> is void, so it says nothing


def test_html_headings_are_its_h_elements_with_spans_over_the_real_text(tmp_path):
    path = tmp_path / "registration.html"
    path.write_text(PAGE)

    assert headings(read(path)) == [
        (1, "Registration Confirmation", "Registration Confirmation"),
        (2, "Your schedule", "Your schedule"),
    ]


def test_adjacent_table_cells_do_not_run_into_one_invented_word(tmp_path):
    """`<td>A</td><td>B</td>` read without block boundaries is `AB` -- a word that is
    in no document, and one `find_structured_strings` would happily match on."""
    path = tmp_path / "schedule.html"
    path.write_text("<table><tr><td>PHYS</td><td>1401</td></tr></table>")

    assert "PHYS1401" not in read(path).text
    assert "PHYS" in read(path).text and "1401" in read(path).text


def test_a_line_break_element_separates_the_words_it_sits_between(tmp_path):
    """`<br>` has no closing tag, so an end-tag rule alone never fires for it and
    `Amara<br>Chen` reads as one name that is in no document."""
    path = tmp_path / "card.html"
    path.write_text("<span>Amara<br>Chen<br/>Physics</span>")

    assert read(path).text == "Amara\nChen\nPhysics"


def test_a_declared_character_set_is_honoured_rather_than_assumed(tmp_path):
    """The page states its own encoding. Ignoring it turns every accented character
    in a Windows-1252 document into a replacement character."""
    path = tmp_path / "latin.html"
    path.write_bytes('<html><head><meta charset="windows-1252"></head>'
                     '<body><p>Amara Chén</p></body></html>'.encode("cp1252"))

    assert "Amara Chén" in read(path).text


def test_an_empty_heading_element_does_not_consume_an_ordinal(tmp_path):
    """A spacer `<h2></h2>` is common in generated pages. Counting it would make the
    next heading's ordinal disagree with what a person reading the page would count."""
    path = tmp_path / "spacer.html"
    path.write_text("<h1>First</h1><h2></h2><h2>Second</h2>")

    assert [(r.ordinal, r.label) for r in read(path).headings] == [
        (1, "First"), (2, "Second")]


# --------------------------------------------------------------------------- #
# RTF
# --------------------------------------------------------------------------- #

#: A real RTF header, as TextEdit writes one. The control words are separated from
#: the text the way the format requires -- `\\par` followed by a letter is the single
#: control word `\\parJordan`, which is a property of RTF and not of this reader.
RTF = (r"{\rtf1\ansi\ansicpg1252\cocoartf2822"
       r"{\fonttbl\f0\fswiss\fcharset0 Helvetica;}"
       r"{\colortbl;\red255\green255\blue255;}"
       r"{\*\expandedcolortbl;;}"
       r"{\info{\author Amara Chen}}"
       r"\pard\f0\fs24 Letter of Recommendation\par "
       r"Jordan Ellis earned an A in PHYS 1401.\par "
       r"Caf\'e9 hours are Tuesdays.\par "
       r"A \uc1\u8212 ? dash and a \{brace\}.\par "
       "}")


def test_rtf_yields_the_letter_and_not_its_control_words(tmp_path):
    """The measured defect. `recommendation.rtf` stored 3,257 characters beginning
    `{\\rtf1\\ansi\\ansicpg1252\\cocoartf2822`, and that string was the prose
    observation the recogniser read."""
    path = tmp_path / "recommendation.rtf"
    path.write_text(RTF)

    text = read(path).text

    assert "\\rtf1" not in text
    assert "Helvetica" not in text
    assert "cocoartf" not in text
    assert "Letter of Recommendation" in text
    assert "Jordan Ellis earned an A in PHYS 1401." in text


def test_an_rtf_hex_escape_is_decoded_in_the_documents_own_code_page(tmp_path):
    """`\\'e9` is `é` in 1252 and `й` in 1251. The file states which, so nothing is
    guessed -- and a reader that assumed would put the wrong letter in a word."""
    path = tmp_path / "recommendation.rtf"
    path.write_text(RTF)

    assert "Café hours are Tuesdays." in read(path).text


def test_an_rtf_code_page_other_than_1252_is_read_from_the_document(tmp_path):
    """The same byte, two letters. `\\'e9` is `é` under `\\ansicpg1252` and `й` under
    `\\ansicpg1251`, and only the file knows which -- so a reader that defaults rather
    than reads puts a plausible WRONG letter in the middle of a word, unmarked."""
    path = tmp_path / "cyrillic.rtf"
    path.write_text(r"{\rtf1\ansi\ansicpg1251 Bo\'e9ko\par }")

    assert read(path).text == "Boйko\n"


def test_an_rtf_unicode_escape_and_an_escaped_brace_survive(tmp_path):
    path = tmp_path / "recommendation.rtf"
    path.write_text(RTF)

    assert "A — dash and a {brace}." in read(path).text


def test_a_skipped_destination_keeps_its_contents_out_of_the_text(tmp_path):
    """A font table, a colour table and an `{\\*\\...}` extension are not text a
    person wrote. `\\info`'s author is document metadata, and putting it in the body
    would make the letter appear to open with its writer's name twice."""
    path = tmp_path / "recommendation.rtf"
    path.write_text(RTF)

    text = read(path).text

    assert "fswiss" not in text
    assert "expandedcolortbl" not in text
    assert "Amara Chen" not in text


def test_rtf_claims_no_headings_because_it_states_none_it_can_read(tmp_path):
    """A heading in RTF is a paragraph STYLE, and resolving one means reading the
    stylesheet destination this reader skips. Less than a `.docx` gives, and true --
    inventing a heading from a font size is the judgement a reader may not make."""
    path = tmp_path / "recommendation.rtf"
    path.write_text(RTF)

    assert read(path).headings == ()


# --------------------------------------------------------------------------- #
# OpenDocument and EPUB -- the last two of §2.9's eight
# --------------------------------------------------------------------------- #

def odt(path: Path, body: str) -> Path:
    text = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    office = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/vnd.oasis.opendocument.text")
        archive.writestr("content.xml",
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<office:document-content xmlns:office="{office}" xmlns:text="{text}">'
            f'<office:body><office:text>{body}</office:text></office:body>'
            '</office:document-content>')
    return path


def test_an_odt_yields_its_paragraphs_and_its_outlined_headings(tmp_path):
    """§2.9 names OpenDocument among its eight text formats. Read as UTF-8 bytes -- a
    ZIP container -- it produced mojibake stored as `complete`."""
    path = odt(tmp_path / "thesis.odt",
               '<text:h text:outline-level="1">Introduction</text:h>'
               '<text:p>Momentum is conserved.</text:p>'
               '<text:h text:outline-level="2">Method</text:h>'
               '<text:p>Air<text:s text:c="3"/>track.</text:p>')

    document = read(path)

    assert document.text == ("Introduction\nMomentum is conserved.\n"
                             "Method\nAir   track.\n")
    assert headings(document) == [(1, "Introduction", "Introduction"),
                                  (2, "Method", "Method")]


def test_an_odt_space_run_is_not_collapsed_into_one_space(tmp_path):
    """ODF writes a run of spaces as `<text:s text:c="4"/>`. A reader taking
    `itertext()` alone joins the two words either side of it."""
    path = odt(tmp_path / "spaced.odt", '<text:p>Air<text:s text:c="4"/>track</text:p>')

    assert read(path).text == "Air    track\n"


def epub(path: Path, chapters) -> Path:
    opf = "http://www.idpf.org/2007/opf"
    ocf = "urn:oasis:names:tc:opendocument:xmlns:container"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("mimetype", "application/epub+zip")
        archive.writestr("META-INF/container.xml",
            f'<container xmlns="{ocf}"><rootfiles>'
            '<rootfile full-path="OEBPS/book.opf"/></rootfiles></container>')
        # The spine lists chapter 2 FIRST. A reader sorting the namelist would put
        # chapter 1 first and read the book in the wrong order.
        archive.writestr("OEBPS/book.opf",
            f'<package xmlns="{opf}"><manifest>'
            + "".join(f'<item id="c{i}" href="chapter{i}.xhtml"/>'
                      for i in range(1, len(chapters) + 1))
            + '</manifest><spine>'
            + "".join(f'<itemref idref="c{i}"/>'
                      for i in reversed(range(1, len(chapters) + 1)))
            + '</spine></package>')
        for i, (title, body) in enumerate(chapters, 1):
            archive.writestr(f"OEBPS/chapter{i}.xhtml",
                f"<html><body><h1>{title}</h1><p>{body}</p></body></html>")
    return path


def test_an_epub_is_read_in_spine_order_with_its_headings_renumbered(tmp_path):
    """§2.9's eighth text format. Reading order is the spine's, not the filenames':
    chapter 10 sorts before chapter 2, and a book read out of order numbers its
    headings against the wrong text."""
    path = epub(tmp_path / "mechanics.epub",
                [("Kinematics", "Position and time."),
                 ("Newton's laws", "Force and mass.")])

    document = read(path)

    assert headings(document) == [(1, "Newton's laws", "Newton's laws"),
                                  (2, "Kinematics", "Kinematics")]
    assert "Force and mass." in document.text
    assert document.text.index("Force and mass.") < document.text.index(
        "Position and time.")


# --------------------------------------------------------------------------- #
# notebooks
# --------------------------------------------------------------------------- #

#: A notebook whose markdown cell is NOT the first one, so the heading's offset into
#: the joined text is not zero and a miscounted cell separator moves it. Its code
#: cell carries an output, which is the notebook's result and not its author's
#: writing.
NOTEBOOK = {
    "nbformat": 4,
    "metadata": {},
    "cells": [
        {"cell_type": "code",
         "source": "import math\nmass = 0.51\n",
         "outputs": [{"output_type": "stream",
                      "text": ["cell ran in 0.4 seconds\n"]}]},
        {"cell_type": "markdown",
         "source": ["# Air track lab\n", "\n", "Cart mass was 0.51 kg.\n"]},
        {"cell_type": "raw", "source": "\\begin{abstract}\n"},
    ],
}


def test_a_notebooks_cells_arrive_as_their_own_text_and_not_as_json(tmp_path):
    """`.ipynb` had no entry in the reader's table, so `_plain` decoded the file and
    the whole notebook JSON became the document's prose. Measured over 199 of the
    owner's files: eleven notebooks, each one unit of 50,000 to 118,000 characters,
    and what the model was shown of a notebook was `    "# Heading\\n",` -- the
    quotes and the escape included. A cell's source is what the person wrote."""
    path = tmp_path / "lab4.ipynb"
    path.write_text(json.dumps(NOTEBOOK))

    document = read(path)

    assert "import math" in document.text
    assert "# Air track lab" in document.text
    assert "Cart mass was 0.51 kg." in document.text
    assert "\\begin{abstract}" in document.text
    assert '"cell_type"' not in document.text
    assert '"source"' not in document.text
    assert "cell ran in 0.4 seconds" not in document.text


def test_a_notebook_heading_addresses_the_joined_cell_text(tmp_path):
    """A `Region` is a pair of offsets into the document's own text, and
    `structured_text.py` slices `document.text` with them to store the heading's own
    words. The heading is in the second cell, so its span is only right if the cell
    before it was counted, its separator included."""
    path = tmp_path / "lab4.ipynb"
    path.write_text(json.dumps(NOTEBOOK))

    document = read(path)

    assert headings(document) == [(1, "Air track lab", "Air track lab")]
    assert document.headings[0].start > 0


def test_a_notebooks_markdown_cell_is_reported_as_a_cell_and_its_code_cells_are_not(
        tmp_path):
    """`104` R-160. Headings alone were never the row.

    `.ipynb` is `code_structured`, and E3 emits its whole-text body reading for
    `text_document` only -- so a notebook whose cells were read still yielded its
    headings and NOT ONE WORD of the prose under them. The recogniser scans evidence,
    so a lab report's own sentences were stored and unreachable exactly as the JSON
    had been. A markdown cell is the prose a person typed into a prose cell, and it
    is reported here as one `body` region so the extractor can make a unit of it.

    CODE CELLS ARE NOT REPORTED, and this asserts it rather than trusting it. §2.4
    asks code for structural evidence "rather than forcing semantic analysis to infer
    a project from arbitrary code text", and P4's fifteen zones carry no `code`, so
    reporting a code cell as `body` would file source text in the zone that means the
    opposite. The zone P4 would need is a vocabulary revision and the owner's.

    THE ORDINAL IS THE NOTEBOOK'S OWN CELL NUMBER, not the markdown cells' own count,
    and `NOTEBOOK` is built to tell the two apart: its markdown cell is the SECOND of
    three. A person who opens the file counts cell 2, and an address that said
    `cell=1` would name a cell holding somebody else's characters.
    """
    path = tmp_path / "lab4.ipynb"
    path.write_text(json.dumps(NOTEBOOK))

    document = read(path)

    assert [(cell.zone, cell.ordinal) for cell in document.cells] == [("body", 2)]
    cell = document.cells[0]
    assert document.text[cell.start:cell.end] == (
        "# Air track lab\n\nCart mass was 0.51 kg.\n")
    assert "import math" not in document.text[cell.start:cell.end], (
        "a code cell's source is inside the cell reported as prose")


def test_a_notebook_that_is_not_json_is_still_read_as_its_own_bytes(tmp_path):
    """A truncated notebook is a file whose cells could not be read, not a file with
    no text. It falls back to what an unregistered extension already gets -- the
    bytes are the text -- and raises nothing on the way."""
    path = tmp_path / "broken.ipynb"
    path.write_text('{"nbformat": 4, "cells": [')

    document = read(path)

    assert document.text == '{"nbformat": 4, "cells": ['
    assert document.headings == ()
    assert document.cells == ()


def test_a_notebooks_metadata_still_arrives_once_its_cells_are_read(tmp_path):
    """§2.4's one in-file marker class is read out of the notebook's JSON, and the
    cell reader replaced the document's text with the cells' prose. `nbformat` and
    the kernel's name are facts about the FILE, so they are still read from it."""
    path = tmp_path / "lab4.ipynb"
    path.write_text(json.dumps(NOTEBOOK | {"metadata": {
        "kernelspec": {"display_name": "Python 3.12"},
        "language_info": {"name": "python"}}}))

    document = read(path)

    assert [(marker.kind, marker.value) for marker in document.markers] == [
        ("notebook metadata", "nbformat: 4"),
        ("notebook metadata", "kernelspec: Python 3.12"),
        ("notebook metadata", "language_info: python"),
    ]


# --------------------------------------------------------------------------- #
# §2.4's structural indicators and "language where relevant"
# --------------------------------------------------------------------------- #

def test_a_source_files_language_is_supplied_and_was_never_supplied_before(tmp_path):
    """`structured_text.LANGUAGE_FIELD` is a reachable slot that no reader had ever
    filled, so §2.4's "language where relevant" produced no observation on any file
    in any corpus. An extension-to-language map is library knowledge, which is where
    `Region`'s contract puts it."""
    path = tmp_path / "analysis.py"
    path.write_text("import math\n")

    assert read(path).language == "Python"
    assert read(tmp_path / "analysis.py").text == "import math\n"


def test_a_format_with_no_language_claims_none(tmp_path):
    path = tmp_path / "syllabus.txt"
    path.write_text("PHYS 1401\n")

    assert read(path).language is None


@pytest.mark.parametrize("name,kind", [
    ("pyproject.toml", "package manifest"),
    ("package.json", "package manifest"),
    ("go.mod", "package manifest"),
    (".gitignore", "repository marker"),
    ("README.md", "README file"),
    ("readme", "README file"),
])
def test_section_2_4s_structural_indicators_are_supplied_by_the_reader(
        tmp_path, name, kind):
    """`structured_text.py` says WHICH FILES are members of each class is Deferred
    "and the reader supplies them". Nothing had supplied them, so all four classes
    were empty on every file. Every name here is one a tool requires by that exact
    spelling."""
    path = tmp_path / name
    path.write_text("{}\n")

    assert [(marker.kind, marker.value) for marker in read(path).markers] == [
        (kind, name)]


def test_a_notebooks_metadata_is_read_out_of_the_notebook(tmp_path):
    """"notebook metadata" is one of §2.4's four classes and is the one that is not a
    filename: it is inside the file, and this is where it is read from."""
    path = tmp_path / "lab4.ipynb"
    path.write_text('{"nbformat": 4, "cells": [], "metadata": '
                    '{"kernelspec": {"display_name": "Python 3.12"}, '
                    '"language_info": {"name": "python"}}}')

    document = read(path)

    assert [(marker.kind, marker.value) for marker in document.markers] == [
        ("notebook metadata", "nbformat: 4"),
        ("notebook metadata", "kernelspec: Python 3.12"),
        ("notebook metadata", "language_info: python"),
    ]
    assert document.language == "Jupyter notebook"


def test_a_notebook_that_is_not_valid_json_yields_no_invented_metadata(tmp_path):
    """A truncated notebook is a file whose metadata could not be read. Reporting a
    default would put a kernel name nothing observed onto a person's evidence."""
    path = tmp_path / "broken.ipynb"
    path.write_text('{"nbformat": 4, "cells": [')

    assert read(path).markers == ()


def test_a_file_that_is_neither_a_marker_nor_a_language_carries_neither(tmp_path):
    """Every slot this reader fills is one the file actually answered."""
    path = tmp_path / "letter.txt"
    path.write_text("Dear committee,\n")

    document = read(path)

    assert document.markers == ()
    assert document.language is None
    assert document.headings == ()


# --------------------------------------------------------------------------- #
# the format this reader does not read by itself
# --------------------------------------------------------------------------- #

def test_a_legacy_doc_is_unsupported_when_no_doc_reader_is_wired(tmp_path):
    """§2.4's `unsupported`, and the first time this reader has ever returned None.

    Its contract used to be "It never returns `None`", which was true while every
    extension the router sent here had text for bytes. `.doc` does not: it is an OLE
    compound document, and a deployment without a converter for it has no reader --
    which is a statement about the deployment and is what `None` says. The bytes
    below are the OLE signature, so this is not "the file was broken".
    """
    path = tmp_path / "1403.Sample.Exam.doc"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 32)

    assert stdlib_text_document_reader()(path) is None


def test_a_wired_doc_reader_is_the_one_that_answers(tmp_path):
    """The socket, not the converter. `readers/doc_cocoa.py` has its own file of
    tests; this one proves the reader is REACHED, which is the half that was missing
    when `read_long_tail` sat wired to `_no_reader` and nobody noticed for a week."""
    path = tmp_path / "1403.Sample.Exam.doc"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")
    from extractors.structured_text import TextDocument

    read_it = stdlib_text_document_reader(
        read_doc=lambda p: TextDocument(text="General Chemistry I 1403"))

    assert read_it(path).text == "General Chemistry I 1403"


def test_wiring_a_doc_reader_changes_nothing_for_any_other_format(tmp_path):
    """A socket that swallowed `.txt` would be worse than an empty one."""
    path = tmp_path / "syllabus.txt"
    path.write_text("PHYS 1403\n")

    read_it = stdlib_text_document_reader(read_doc=lambda p: None)

    assert read_it(path).text == "PHYS 1403\n"


# --------------------------------------------------------------------------- #
# byte-order marks
# --------------------------------------------------------------------------- #
#
# The same defect this whole module was written to fix, one layer down. A `.rtf`
# arriving as its own control words is false information stored as `complete`; a
# UTF-16 `.txt` arriving as NUL-interleaved mojibake is the identical failure and was
# still here. Windows Notepad's "Unicode" save and Excel's "Unicode Text (*.txt)"
# export both write UTF-16LE with a BOM, and both came back as
# `'��C\x00o\x00u\x00r\x00s\x00e\x00'` -- recorded `complete`, handed to
# the recogniser as the document's prose.
#
# A BOM IS NOT A GUESS. `_decode`'s docstring rules out inferring Windows-1252 from
# bytes that failed as UTF-8, and that reasoning is kept exactly: a byte-order mark
# is the document's OWN statement about its encoding, in the same class as HTML's
# `<meta charset>` and RTF's `\ansicpg`, which this reader already honours. Nothing
# below sniffs statistics, counts NULs or scores a codec.

def test_a_utf16_text_file_is_read_as_text_and_not_as_interleaved_nulls(tmp_path):
    """The measured failure, pinned. Notepad's "Unicode" and Excel's "Unicode Text"
    are both this."""
    path = tmp_path / "grades.txt"
    path.write_bytes("Course: PHYS 1403\nGrade: A\n".encode("utf-16"))  # BOM + LE
    assert read(path).text == "Course: PHYS 1403\nGrade: A\n"


def test_a_big_endian_utf16_text_file_reads_the_same(tmp_path):
    """Both byte orders, because the BOM is what says which and reading only one
    would leave the other broken in a way nothing distinguishes."""
    path = tmp_path / "grades.txt"
    path.write_bytes(b"\xfe\xff" + "Course: PHYS 1403\n".encode("utf-16-be"))
    assert read(path).text == "Course: PHYS 1403\n"


def test_a_utf32_text_file_is_not_mistaken_for_utf16(tmp_path):
    """`FF FE 00 00` starts UTF-32LE and also starts with UTF-16LE's `FF FE`, so the
    longer mark has to be tested first. Read as UTF-16 this file would be a string of
    NULs between the letters -- the very failure above, wearing the fix."""
    path = tmp_path / "notes.txt"
    path.write_bytes("Lab 4\n".encode("utf-32"))
    assert read(path).text == "Lab 4\n"


def test_the_utf8_mark_does_not_survive_into_the_text(tmp_path):
    """A `\\ufeff` left on the front is invisible in a viewer and is a character in
    every match. It sat in front of the first word of every BOM-marked `.txt` -- and
    of every Markdown heading, where `_markdown_headings` reads the line's first
    character to decide whether it is a heading at all."""
    path = tmp_path / "syllabus.txt"
    path.write_bytes(b"\xef\xbb\xbf" + "PHYS 1403\n".encode("utf-8"))
    text = read(path).text
    assert text == "PHYS 1403\n"
    assert "﻿" not in text


def test_a_bom_marked_markdown_file_still_finds_its_first_heading(tmp_path):
    """Why the mark mattered beyond tidiness: `# Lab 4` behind a BOM is
    `\\ufeff# Lab 4`, and CommonMark's ATX rule anchors at the start of the line."""
    path = tmp_path / "lab.md"
    path.write_bytes(b"\xef\xbb\xbf" + "# Lab 4\n\nAir track.\n".encode("utf-8"))
    document = read(path)
    assert [region.label for region in document.headings] == ["Lab 4"]


def test_plain_utf8_is_untouched_and_cjk_still_arrives_whole(tmp_path):
    """The ordinary file has no mark and must not be changed by the sniff. CJK is
    here because it is the case a byte-counting fix would break -- and because it is
    what a real corpus holds; nothing in this reader is keyed to a script."""
    path = tmp_path / "report.txt"
    path.write_bytes("外泌體 exosome report\n".encode("utf-8"))
    assert read(path).text == "外泌體 exosome report\n"


def test_bytes_that_declare_nothing_still_get_the_honest_replacement(tmp_path):
    """`_decode`'s standing rule, unchanged: no BOM and not UTF-8 means a replacement
    character, never a guessed codepage. Guessing Windows-1252 would turn an
    unreadable byte into a WRONG letter with nothing to mark it."""
    path = tmp_path / "old.txt"
    path.write_bytes("Café\n".encode("cp1252"))
    assert read(path).text == "Caf�\n"


def test_a_utf16_html_page_is_read_as_a_page_and_not_as_interleaved_nulls(tmp_path):
    """HTML needed the byte-order mark MORE than plain text did, and was the one
    format the first version of this fix could not reach.

    `_html_encoding` answers `"utf-8"` when it finds no `<meta charset>`, never
    `None` -- so `_decode(payload, encoding or _html_encoding(payload))` always
    arrived with an encoding already chosen and the mark was never consulted. And the
    meta tag CANNOT be found in a UTF-16 document: the regex runs over bytes, and
    `<meta charset=...>` in UTF-16 is NUL-interleaved. So a UTF-16 page was
    guaranteed to fall through to UTF-8 and arrive as mojibake, `<title>` included.

    HTML5's own precedence is BOM, then `<meta charset>`, then the default -- so the
    mark winning here is the standard's order, not a preference of this reader's.
    """
    path = tmp_path / "confirmation.html"
    path.write_bytes(
        "<html><head><title>Registration confirmed</title></head>"
        "<body><h1>PHYS 1403</h1><p>Seat 12.</p></body></html>".encode("utf-16"))
    text = read(path).text
    assert "Registration confirmed" in text
    assert "PHYS 1403" in text
    assert "\x00" not in text


def test_a_bom_marked_html_page_does_not_emit_the_mark_as_its_first_character(tmp_path):
    """A `\\ufeff` ahead of the page's own first word is a character in every match
    and is invisible to whoever is reading the output."""
    path = tmp_path / "page.html"
    path.write_bytes(b"\xef\xbb\xbf"
                     + "<html><body><p>Air track lab.</p></body></html>".encode())
    assert read(path).text.strip().startswith("Air track")


def test_a_declared_charset_still_wins_over_the_default(tmp_path):
    """The guard: an ordinary page with no mark and a real `<meta charset>` is
    decoded by its declaration exactly as before."""
    path = tmp_path / "old.html"
    path.write_bytes(b'<html><head><meta charset="windows-1252"></head>'
                     + "<body><p>Caf\xe9 list</p></body></html>".encode("cp1252"))
    assert "Café list" in read(path).text
