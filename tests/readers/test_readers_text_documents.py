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
