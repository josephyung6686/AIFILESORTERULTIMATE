"""The reader that made §2.9's six families reachable at all.

`deployment.py` wired `read_long_tail = _no_reader`, so `extract_long_tail` returned
`unsupported` on its fourth line and every spreadsheet, presentation, email, calendar
and contact file in a corpus recorded `coverage {"processed": 0, "total": 1}` -- the
bytes never looked at. Measured over a real folder: seven of seventeen files yielded
zero observations, zero text units and zero characters, and nothing said so.

Every fixture here is built from the standard library, so the suite proves the FORMAT
and not a library's opinion of it: a `.xlsx` and a `.pptx` are written as the ZIP of
XML parts they are, which is also what pins the contract these readers claim to hold.
"""
from __future__ import annotations

import struct
import zipfile
from pathlib import Path

import pytest

from extractors.long_tail import LongTailFile
from readers.long_tail_stdlib import (
    MAX_PART_BYTES, NotAWaveFile, PartTooLarge, UnsafeXml,
    stdlib_long_tail_reader,
)

read = stdlib_long_tail_reader()


def cells(document: LongTailFile) -> dict[tuple[int, int, int], str]:
    """Every table cell, addressed the way its container path will address it."""
    return {(text.entry_ordinal, text.row, text.column): text.text
            for text in document.texts if text.zone == "table"}


def values(document: LongTailFile) -> list[tuple[str, str]]:
    return [(value.name, value.value) for value in document.values]


# --------------------------------------------------------------------------- #
# spreadsheets
# --------------------------------------------------------------------------- #

def test_a_csv_yields_every_visible_cell_with_its_column_header(tmp_path):
    """§2.9: "column headers, visible cell values". A `.csv` used to yield nothing."""
    path = tmp_path / "grades.csv"
    path.write_text("student_id,course,grade\n"
                    "S1001,PHYS 1401,A\n"
                    "S1002,MATH 2318,B+\n")

    document = read(path)

    assert cells(document) == {
        (1, 1, 1): "student_id", (1, 1, 2): "course", (1, 1, 3): "grade",
        (1, 2, 1): "S1001", (1, 2, 2): "PHYS 1401", (1, 2, 3): "A",
        (1, 3, 1): "S1002", (1, 3, 2): "MATH 2318", (1, 3, 3): "B+",
    }
    assert [text.column_header for text in document.texts] == [
        "student_id", "course", "grade"] * 3
    assert [(entry.kind, entry.index, entry.label) for entry in document.entries] == [
        ("sheet", 1, None)]


def test_a_tsv_is_read_on_tabs_and_an_empty_cell_is_not_a_row(tmp_path):
    """An absent cell is an absence. P4 forbids an extractor writing one as evidence,
    and a reader that returned `""` would push exactly that onto it."""
    path = tmp_path / "readings.tsv"
    path.write_text("week\ttopic\tchapter\n1\t\t2\n")

    assert cells(read(path)) == {
        (1, 1, 1): "week", (1, 1, 2): "topic", (1, 1, 3): "chapter",
        (1, 2, 1): "1", (1, 2, 3): "2",
    }


def test_a_byte_order_mark_does_not_survive_into_the_first_column_header(tmp_path):
    """A spreadsheet application writes a BOM. Kept, it puts an invisible character
    on the front of the header, where it stops that header matching anything."""
    path = tmp_path / "export.csv"
    path.write_bytes("﻿course,term\nPHYS 1401,Spring 2026\n".encode("utf-8"))

    assert cells(read(path))[(1, 1, 1)] == "course"


def sheet_xml(rows: str) -> str:
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{rows}</sheetData></worksheet>')


def xlsx(path: Path, *, sheets, shared=(), styles=None, core=None,
         date1904=False) -> Path:
    """A real `.xlsx`: the OPC package `_read_xlsx` claims to read, written by hand."""
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>')
        archive.writestr("xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
            f' xmlns:r="{rel}">'
            + (f'<workbookPr date1904="{"1" if date1904 else "0"}"/>')
            + '<sheets>'
            + "".join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>'
                      for i, (name, _) in enumerate(sheets, 1))
            + '</sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f'<Relationship Id="rId{i}" Type="{rel}/worksheet" '
                      f'Target="worksheets/sheet{i}.xml"/>'
                      for i in range(1, len(sheets) + 1))
            + '</Relationships>')
        for i, (_, rows) in enumerate(sheets, 1):
            archive.writestr(f"xl/worksheets/sheet{i}.xml", sheet_xml(rows))
        if shared:
            archive.writestr("xl/sharedStrings.xml",
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                + "".join(f"<si><t>{s}</t></si>" for s in shared) + '</sst>')
        if styles is not None:
            archive.writestr("xl/styles.xml", styles)
        if core is not None:
            archive.writestr("docProps/core.xml", core)
    return path


def test_an_xlsx_yields_sheet_names_and_every_cell_of_every_sheet(tmp_path):
    """§2.9: "sheet names ... visible cell values". Both sheets, in workbook order --
    `sorted(namelist())` would put sheet10 before sheet2 and is not used."""
    path = xlsx(tmp_path / "budget.xlsx",
                sheets=[("Spring 2026",
                         '<row r="1"><c r="A1" t="s"><v>0</v></c>'
                         '<c r="B1" t="s"><v>1</v></c></row>'
                         '<row r="2"><c r="A2" t="s"><v>2</v></c>'
                         '<c r="B2"><v>4200</v></c></row>'),
                        ("Notes",
                         '<row r="1"><c r="A1" t="inlineStr"><is><t>Aid pending</t>'
                         '</is></c></row>')],
                shared=["Item", "Amount", "Tuition"])

    document = read(path)

    assert [(entry.kind, entry.index, entry.label) for entry in document.entries] == [
        ("sheet", 1, "Spring 2026"), ("sheet", 2, "Notes")]
    assert cells(document) == {
        (1, 1, 1): "Item", (1, 1, 2): "Amount",
        (1, 2, 1): "Tuition", (1, 2, 2): "4200",
        (2, 1, 1): "Aid pending",
    }


def test_a_boolean_cell_reads_as_the_word_the_person_saw(tmp_path):
    """ECMA-376 §18.18.11 stores 0 or 1 and DISPLAYS FALSE or TRUE. Emitting the digit
    would put a number where the person read a word."""
    path = xlsx(tmp_path / "flags.xlsx",
                sheets=[("Sheet1", '<row r="1"><c r="A1" t="b"><v>1</v></c>'
                                   '<c r="B1" t="b"><v>0</v></c></row>')])

    assert cells(read(path)) == {(1, 1, 1): "TRUE", (1, 1, 2): "FALSE"}


DATE_STYLES = ('<?xml version="1.0" encoding="UTF-8"?>'
               '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
               '<numFmts count="1">'
               '<numFmt numFmtId="180" formatCode="dd\\-mmm\\-yyyy"/>'
               '<numFmt numFmtId="181" formatCode="&quot;May&quot;\\ #,##0"/>'
               '</numFmts>'
               '<cellXfs count="4">'
               '<xf numFmtId="0"/><xf numFmtId="14"/>'
               '<xf numFmtId="180"/><xf numFmtId="181"/>'
               '</cellXfs></styleSheet>')


def test_a_date_cell_reads_as_a_date_and_not_as_a_count_of_days(tmp_path):
    """§2.9 asks a spreadsheet for "dates ... from labeled cells". A date cell stores
    46037; emitting that is the wrong value, which is worse than no value.

    Style 1 is built-in format 14, style 2 a custom code whose tokens say date, style
    3 a custom code whose only letters are inside quotes, and style 0 no format at
    all -- the last two must stay numbers.
    """
    path = xlsx(tmp_path / "dates.xlsx",
                sheets=[("Sheet1",
                         '<row r="1">'
                         '<c r="A1" s="1"><v>46037</v></c>'
                         '<c r="B1" s="2"><v>46037</v></c>'
                         '<c r="C1" s="3"><v>46037</v></c>'
                         '<c r="D1" s="0"><v>46037</v></c></row>')],
                styles=DATE_STYLES)

    assert cells(read(path)) == {
        (1, 1, 1): "2026-01-15", (1, 1, 2): "2026-01-15",
        (1, 1, 3): "46037", (1, 1, 4): "46037",
    }


def test_the_1904_epoch_is_read_from_the_workbook_and_not_assumed(tmp_path):
    """ECMA-376 §18.17.4.1 allows two epochs. A workbook saved by Excel for Mac in
    the 1904 system reads four years and a day out under the other one."""
    path = xlsx(tmp_path / "mac.xlsx",
                sheets=[("Sheet1", '<row r="1"><c r="A1" s="1"><v>44575</v></c></row>')],
                styles=DATE_STYLES, date1904=True)

    assert cells(read(path)) == {(1, 1, 1): "2026-01-15"}


def test_the_phantom_1900_leap_day_is_rendered_as_no_date_at_all(tmp_path):
    """Serial 60 in the 1900 system is 1900-02-29, a day that did not exist. There is
    no correct answer, so the raw value stands rather than a wrong date."""
    path = xlsx(tmp_path / "lotus.xlsx",
                sheets=[("Sheet1", '<row r="1"><c r="A1" s="1"><v>60</v></c>'
                                   '<c r="B1" s="1"><v>59</v></c></row>')],
                styles=DATE_STYLES)

    assert cells(read(path)) == {(1, 1, 1): "60", (1, 1, 2): "1900-02-28"}


def test_a_workbooks_core_properties_are_its_file_metadata(tmp_path):
    """§2.9's "workbook or file metadata", under the format's own slot names."""
    path = xlsx(tmp_path / "meta.xlsx",
                sheets=[("Sheet1", "")],
                core='<?xml version="1.0" encoding="UTF-8"?>'
                     '<cp:coreProperties '
                     'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                     'xmlns:dc="http://purl.org/dc/elements/1.1/" '
                     'xmlns:dcterms="http://purl.org/dc/terms/">'
                     '<dc:creator>Amara Chen</dc:creator>'
                     '<dc:title>Spring budget</dc:title>'
                     '<dcterms:created>2026-01-04T09:00:00Z</dcterms:created>'
                     '</cp:coreProperties>')

    document = read(path)

    assert values(document) == [("creator", "Amara Chen"),
                                ("title", "Spring budget"),
                                ("created", "2026-01-04T09:00:00Z")]
    assert document.iso_dates == {"created": "2026-01-04T09:00:00+00:00"}


def test_a_cell_reference_past_z_addresses_the_column_it_names(tmp_path):
    """Columns are base-26 with no zero digit: AA is 27, and a reader that took the
    first letter alone would file the twenty-eighth column under the second."""
    path = xlsx(tmp_path / "wide.xlsx",
                sheets=[("Sheet1", '<row r="1"><c r="AB1" t="s"><v>0</v></c></row>')],
                shared=["far right"])

    assert cells(read(path)) == {(1, 1, 28): "far right"}


# --------------------------------------------------------------------------- #
# presentations
# --------------------------------------------------------------------------- #

def pptx(path: Path, slides, *, notes=None) -> Path:
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    drawing = "http://schemas.openxmlformats.org/drawingml/2006/main"
    presentation = "http://schemas.openxmlformats.org/presentationml/2006/main"

    def shape(kind, text):
        holder = f'<p:ph type="{kind}"/>' if kind else ""
        return (f'<p:sp><p:nvSpPr><p:cNvPr id="2"/><p:nvPr>{holder}</p:nvPr>'
                '</p:nvSpPr><p:txBody>'
                + "".join(f"<a:p><a:r><a:t>{line}</a:t></a:r></a:p>"
                          for line in text)
                + '</p:txBody></p:sp>')

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("_rels/.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            f'<Relationship Id="rId1" Type="{rel}/officeDocument" Target="ppt/presentation.xml"/>'
            '</Relationships>')
        # DELIBERATELY out of filename order: rId1 points at slide2.xml. A reader
        # that sorted the namelist would report these two the wrong way round.
        order = list(reversed(range(1, len(slides) + 1)))
        archive.writestr("ppt/presentation.xml",
            f'<p:presentation xmlns:p="{presentation}" xmlns:r="{rel}"><p:sldIdLst>'
            + "".join(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>'
                      for i in range(1, len(slides) + 1))
            + '</p:sldIdLst></p:presentation>')
        archive.writestr("ppt/_rels/presentation.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(f'<Relationship Id="rId{i}" Type="{rel}/slide" '
                      f'Target="slides/slide{order[i - 1]}.xml"/>'
                      for i in range(1, len(slides) + 1))
            + '</Relationships>')
        for position, (title, body) in enumerate(slides, 1):
            number = order[position - 1]
            archive.writestr(f"ppt/slides/slide{number}.xml",
                f'<p:sld xmlns:a="{drawing}" xmlns:p="{presentation}"><p:cSld>'
                f'<p:spTree>{shape("title", [title])}{shape(None, body)}'
                '</p:spTree></p:cSld></p:sld>')
            sidecar = []
            if notes and position in notes:
                archive.writestr(f"ppt/notesSlides/notesSlide{number}.xml",
                    f'<p:notes xmlns:a="{drawing}" xmlns:p="{presentation}">'
                    f'<a:p><a:r><a:t>{notes[position]}</a:t></a:r></a:p></p:notes>')
                sidecar.append(f'<Relationship Id="rId9" Type="{rel}/notesSlide" '
                               f'Target="../notesSlides/notesSlide{number}.xml"/>')
            sidecar.append(f'<Relationship Id="rId8" Type="{rel}/hyperlink" '
                           'Target="https://example.edu/lab4" TargetMode="External"/>')
            archive.writestr(f"ppt/slides/_rels/slide{number}.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                + "".join(sidecar) + '</Relationships>')
    return path


def test_a_pptx_yields_slide_titles_text_boxes_and_speaker_notes(tmp_path):
    """§2.9: "slide titles, text boxes, speaker notes where available, hyperlinks
    ... and slide-level page boundaries", all five in one file."""
    path = pptx(tmp_path / "defence.pptx",
                [("Conservation of Momentum", ["Jordan Ellis", "PHYS 1401"]),
                 ("Method", ["Air track", "Twelve trials"])],
                notes={2: "Remember the uncertainty slide"})

    document = read(path)

    assert [(entry.kind, entry.index) for entry in document.entries] == [
        ("slide", 1), ("slide", 2)]
    assert [(text.entry_ordinal, text.zone, text.text) for text in document.texts] == [
        (1, "heading", "Conservation of Momentum"),
        (1, "body", "Jordan Ellis\nPHYS 1401"),
        (2, "heading", "Method"),
        (2, "body", "Air track\nTwelve trials"),
        (2, "notes", "Remember the uncertainty slide"),
    ]
    assert values(document) == [("hyperlink", "https://example.edu/lab4"),
                                ("hyperlink", "https://example.edu/lab4")]


def test_two_text_boxes_on_one_slide_get_two_addresses(tmp_path):
    """`extract_long_tail` raises `DuplicateUnit` when two texts claim one container
    path, and that raise becomes a `failed` run for the whole file. A slide's title
    and its body differ only by `region`."""
    path = pptx(tmp_path / "one.pptx", [("Title", ["Body"])])

    regions = [text.region for text in read(path).texts]

    assert regions == [1, 2]


# --------------------------------------------------------------------------- #
# email
# --------------------------------------------------------------------------- #

MESSAGE = ("From: Amara Chen <achen@example.edu>\r\n"
           "To: Jordan Ellis <jellis@example.edu>\r\n"
           "Cc: registrar@example.edu\r\n"
           "Subject: PHYS 1401 midterm results\r\n"
           "Date: Fri, 13 Mar 2026 08:41:02 -0500\r\n"
           "Message-ID: <a41b@example.edu>\r\n"
           "In-Reply-To: <9f02@example.edu>\r\n"
           "MIME-Version: 1.0\r\n"
           "Content-Type: text/plain; charset=utf-8\r\n\r\n"
           "Your midterm score was 88 out of 100.\r\n")


def test_an_eml_yields_every_slot_section_2_9_names(tmp_path):
    """"sender, recipients, subject, sent date, thread identifiers, message body,
    attachment names, and reply-chain context" -- and the address slots carry
    `kind="address"`, which is what raises §2.9's sensitivity signal downstream."""
    path = tmp_path / "results.eml"
    path.write_text(MESSAGE)

    document = read(path)

    assert values(document) == [
        ("From", "Amara Chen <achen@example.edu>"),
        ("To", "Jordan Ellis <jellis@example.edu>"),
        ("Cc", "registrar@example.edu"),
        ("Subject", "PHYS 1401 midterm results"),
        ("Date", "Fri, 13 Mar 2026 08:41:02 -0500"),
        ("Message-ID", "<a41b@example.edu>"),
        ("In-Reply-To", "<9f02@example.edu>"),
    ]
    assert [value.name for value in document.values if value.kind == "address"] == [
        "From", "To", "Cc"]
    assert [(text.zone, text.text) for text in document.texts] == [
        ("body", "Your midterm score was 88 out of 100.\n")]
    assert document.iso_dates == {"Date": "2026-03-13T08:41:02-05:00"}
    assert [(entry.kind, entry.label) for entry in document.entries] == [
        ("entry", "<a41b@example.edu>")]


def test_an_attachment_is_named_and_its_bytes_are_not_read(tmp_path):
    """§2.9 asks for "attachment names". The part is never decoded: an attachment is
    a file of its own and reading it here would extract it without a routing decision
    and without the protected-container gate that a routed file passes through."""
    path = tmp_path / "with-attachment.eml"
    path.write_text(
        "From: achen@example.edu\r\nSubject: Marked script\r\n"
        "MIME-Version: 1.0\r\n"
        'Content-Type: multipart/mixed; boundary="X"\r\n\r\n'
        "--X\r\nContent-Type: text/plain\r\n\r\nSee attached.\r\n"
        "--X\r\nContent-Type: application/pdf\r\n"
        'Content-Disposition: attachment; filename="script.pdf"\r\n\r\n'
        "%PDF-1.4 not read\r\n"
        "--X\r\nContent-Type: text/plain\r\n"
        'Content-Disposition: attachment; filename="marks.csv"\r\n\r\n'
        "S1001,88\r\n--X--\r\n")

    document = read(path)

    # A `text/plain` attachment is the case that matters: it is the one an
    # attachment filter built on content type alone lets through, and its bytes
    # would then be filed as the MESSAGE's body -- a marks file becoming the text
    # of the email that carried it.
    assert [value for value in values(document) if value[0] == "attachment"] == [
        ("attachment", "script.pdf"), ("attachment", "marks.csv")]
    assert [text.text for text in document.texts] == ["See attached."]


def test_a_mailbox_of_many_messages_gets_no_shared_normalized_date(tmp_path):
    """`iso_dates` is keyed by SLOT NAME, so forty messages have forty values named
    `Date` and one key. Attaching message one's date to message forty would be a
    wrong value; an absent one costs nothing, because every raw header is stored."""
    path = tmp_path / "archive.mbox"
    path.write_text(
        "From achen@example.edu Fri Mar 13 08:41:02 2026\r\n" + MESSAGE + "\r\n"
        "From achen@example.edu Sat Mar 14 09:00:00 2026\r\n"
        "From: achen@example.edu\r\nSubject: Second\r\n"
        "Date: Sat, 14 Mar 2026 09:00:00 -0500\r\n"
        "Message-ID: <b52c@example.edu>\r\n\r\nA follow-up.\r\n")

    document = read(path)

    assert [entry.label for entry in document.entries] == [
        "<a41b@example.edu>", "<b52c@example.edu>"]
    assert [value.value for value in document.values if value.name == "Subject"] == [
        "PHYS 1401 midterm results", "Second"]
    assert document.iso_dates == {}


# --------------------------------------------------------------------------- #
# calendar and contacts
# --------------------------------------------------------------------------- #

def test_an_ics_yields_every_field_section_2_9_names_and_unfolds_them(tmp_path):
    """"event title, start and end time, location, organizer, attendees, and
    recurrence metadata". RFC 5545 §3.1 folds a long line; a reader that split on
    newlines would cut the summary in half."""
    path = tmp_path / "advising.ics"
    path.write_text(
        "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\n"
        "UID:9c1a@example.edu\r\n"
        "SUMMARY:Advising meeting for the PHYS 1401\r\n  midterm review\r\n"
        "DTSTART:20260312T140000Z\r\nDTEND:20260312T143000Z\r\n"
        "LOCATION:Science Hall 210\r\n"
        "ORGANIZER;CN=\"Chen, Amara\":mailto:achen@example.edu\r\n"
        "ATTENDEE:mailto:jellis@example.edu\r\n"
        "ATTENDEE:mailto:registrar@example.edu\r\n"
        "RRULE:FREQ=WEEKLY;COUNT=4\r\n"
        "DESCRIPTION:Bring the graded problem sets.\r\n"
        "END:VEVENT\r\nEND:VCALENDAR\r\n")

    document = read(path)

    assert values(document) == [
        ("UID", "9c1a@example.edu"),
        ("SUMMARY", "Advising meeting for the PHYS 1401 midterm review"),
        ("DTSTART", "20260312T140000Z"),
        ("DTEND", "20260312T143000Z"),
        ("LOCATION", "Science Hall 210"),
        ("ORGANIZER", "mailto:achen@example.edu"),
        ("ATTENDEE", "mailto:jellis@example.edu"),
        ("ATTENDEE", "mailto:registrar@example.edu"),
        ("RRULE", "FREQ=WEEKLY;COUNT=4"),
    ]
    assert document.iso_dates == {"DTSTART": "2026-03-12T14:00:00+00:00",
                                 "DTEND": "2026-03-12T14:30:00+00:00"}
    assert [(text.zone, text.text) for text in document.texts] == [
        ("notes", "Bring the graded problem sets.")]


def test_a_floating_local_time_is_not_given_an_offset_it_does_not_have(tmp_path):
    """RFC 5545 §3.3.5: a DATE-TIME with no `Z` and no `TZID` is floating. Inventing
    UTC would move a nine o'clock appointment by up to half a day."""
    path = tmp_path / "floating.ics"
    path.write_text("BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nUID:x\r\n"
                    "DTSTART:20260312T090000\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n")

    assert read(path).iso_dates == {"DTSTART": "2026-03-12T09:00:00"}


def test_two_events_in_one_file_are_two_addressable_entries(tmp_path):
    path = tmp_path / "term.ics"
    path.write_text("BEGIN:VCALENDAR\r\n"
                    "BEGIN:VEVENT\r\nUID:a@x\r\nSUMMARY:Midterm\r\nEND:VEVENT\r\n"
                    "BEGIN:VEVENT\r\nUID:b@x\r\nSUMMARY:Final\r\nEND:VEVENT\r\n"
                    "END:VCALENDAR\r\n")

    document = read(path)

    assert [entry.label for entry in document.entries] == ["a@x", "b@x"]
    assert [(value.name, value.value, value.entry_ordinal)
            for value in document.values] == [
        ("UID", "a@x", 1), ("SUMMARY", "Midterm", 1),
        ("UID", "b@x", 2), ("SUMMARY", "Final", 2)]


def test_a_vcf_yields_names_organizations_addresses_and_numbers(tmp_path):
    """§2.9's contact list. Every one of these values is marked potentially sensitive
    by `long_tail.FULLY_SENSITIVE_SOURCE_TYPES` on arrival, so this reader raises no
    signal of its own -- what it must not do is fail to READ them."""
    path = tmp_path / "adviser.vcf"
    path.write_text("BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Amara Chen\r\n"
                    "N:Chen;Amara;;Dr.;\r\n"
                    "ORG:Example University;Department of Physics\r\n"
                    "TITLE:Associate Professor\r\n"
                    "EMAIL;TYPE=WORK:achen@example.edu\r\n"
                    "TEL;TYPE=WORK:+1-555-0142\r\n"
                    "ADR;TYPE=WORK:;;210 Science Hall;Springfield;IL;62704;USA\r\n"
                    "NOTE:Prefers email over telephone.\r\n"
                    "END:VCARD\r\n")

    document = read(path)

    assert values(document) == [
        ("FN", "Amara Chen"),
        ("N", "Chen;Amara;;Dr.;"),
        ("ORG", "Example University;Department of Physics"),
        ("TITLE", "Associate Professor"),
        ("EMAIL", "achen@example.edu"),
        ("TEL", "+1-555-0142"),
        ("ADR", ";;210 Science Hall;Springfield;IL;62704;USA"),
    ]
    assert [(text.zone, text.text) for text in document.texts] == [
        ("notes", "Prefers email over telephone.")]
    assert [entry.label for entry in document.entries] == ["Amara Chen"]


# --------------------------------------------------------------------------- #
# audio and video -- container metadata, and B6 stops there
# --------------------------------------------------------------------------- #

def mp4(path: Path, *, created: int, duration: int, timescale: int) -> Path:
    def atom(kind, payload):
        return struct.pack(">I", len(payload) + 8) + kind + payload

    mvhd = atom(b"mvhd", bytes([0, 0, 0, 0])
                + struct.pack(">IIII", created, created, timescale, duration)
                + b"\x00" * 80)
    stsd = atom(b"stsd", struct.pack(">II", 0, 1) + atom(b"avc1", b"\x00" * 8))
    trak = atom(b"trak", atom(b"mdia", atom(b"minf", atom(b"stbl", stsd))))
    path.write_bytes(atom(b"ftyp", b"isom" + b"\x00" * 8)
                     + atom(b"moov", mvhd + trak))
    return path


def test_an_mp4_yields_duration_codec_and_creation_time(tmp_path):
    """§2.9's audio/video bullet, stopped where B6 stops it: "Audio and video stop at
    container metadata." The 1904 epoch is ISO/IEC 14496-12 §8.2.2's, not a guess."""
    path = mp4(tmp_path / "lecture.mp4", created=3_855_476_000,
               duration=180_000, timescale=1000)

    document = read(path)

    assert values(document) == [
        ("major_brand", "isom"), ("duration", "180.000"), ("timescale", "1000"),
        ("creation_time", "3855476000"), ("modification_time", "3855476000"),
        ("codec", "avc1"),
    ]
    assert document.iso_dates == {"creation_time": "2026-03-04T13:33:20+00:00",
                                 "modification_time": "2026-03-04T13:33:20+00:00"}


# --------------------------------------------------------------------------- #
# RIFF/WAVE -- the container, not the PCM decoder
# --------------------------------------------------------------------------- #

def chunk(identifier: bytes, payload: bytes, *, big: bool = False) -> bytes:
    """One RIFF chunk, padded to an even length as the format requires."""
    order = ">" if big else "<"
    return (identifier + struct.pack(order + "I", len(payload)) + payload
            + (b"\x00" if len(payload) % 2 else b""))


def riff(*chunks: bytes, big: bool = False, form: bytes = b"WAVE") -> bytes:
    body = form + b"".join(chunks)
    return (b"RIFX" if big else b"RIFF") + struct.pack(
        ">I" if big else "<I", len(body)) + body


def fmt_chunk(*, tag: int = 1, channels: int = 2, rate: int = 44100,
              bits: int = 16, extension: bytes = b"", big: bool = False) -> bytes:
    """A `fmt ` chunk as ECMA / RFC 2361 lays it out: PCMWAVEFORMAT, plus whatever
    extension the tag carries."""
    order = ">" if big else "<"
    block_align = channels * (bits // 8) or 1
    payload = struct.pack(order + "HHIIHH", tag, channels, rate,
                          rate * block_align, block_align, bits) + extension
    return chunk(b"fmt ", payload, big=big)


def wav(path: Path, *chunks: bytes, big: bool = False) -> Path:
    path.write_bytes(riff(*chunks, big=big))
    return path


def test_a_wav_yields_its_container_metadata(tmp_path):
    """The four the `wave` module could reach, plus the two §2.9 asks for by name
    and the PCM decoder could not give: "container and codec metadata"."""
    path = wav(tmp_path / "interview.wav", fmt_chunk(),
               chunk(b"data", b"\x00" * 44100 * 4))

    assert values(read(path)) == [
        ("container", "WAVE"), ("format_tag", "1"), ("codec", "PCM"),
        ("channels", "2"), ("sample_rate", "44100"), ("bits_per_sample", "16"),
        ("duration", "1.000"),
    ]


@pytest.mark.parametrize("tag,codec", [(7, "MULAW"), (6, "ALAW"),
                                       (3, "IEEE_FLOAT"), (0x11, "IMA_ADPCM")])
def test_a_wav_that_is_not_pcm_is_read_rather_than_recorded_as_a_failure(
        tmp_path, tag, codec):
    """Python's `wave` is a PCM DECODER front-end: it raises `unknown format: 7` on a
    perfectly good mu-law file, and P5 wrote that down as §2.4's `failed` -- a
    statement that the bytes are corrupt, about a file nothing is wrong with. Every
    field §2.9's audio bullet names lives in the `fmt ` chunk whatever the codec is."""
    path = wav(tmp_path / "call.wav", fmt_chunk(tag=tag, channels=1, rate=8000,
                                                bits=8),
               chunk(b"data", b"\x00" * 16000))

    assert values(read(path)) == [
        ("container", "WAVE"), ("format_tag", str(tag)), ("codec", codec),
        ("channels", "1"), ("sample_rate", "8000"), ("bits_per_sample", "8"),
        ("duration", "2.000"),
    ]


def test_an_unregistered_format_tag_keeps_the_number_and_claims_no_codec(tmp_path):
    """Nothing is guessed. The container's own number is emitted verbatim and the
    `codec` slot is simply absent, which is different from naming it wrongly."""
    path = wav(tmp_path / "odd.wav", fmt_chunk(tag=0x7abc),
               chunk(b"data", b"\x00" * 176400))

    assert [name for name, _ in values(read(path))] == [
        "container", "format_tag", "channels", "sample_rate", "bits_per_sample",
        "duration"]


def test_wave_format_extensible_reports_the_subformat_it_actually_holds(tmp_path):
    """Tag 65534 is a wrapper: the real format is the first two bytes of the
    SubFormat GUID (RFC 2361 / Microsoft's WAVEFORMATEXTENSIBLE). Reporting
    `format_tag` 65534 and nothing else would name the wrapper and not the audio."""
    guid = struct.pack("<H", 3) + b"\x00\x00" + bytes.fromhex(
        "00001000800000aa00389b71")
    extension = struct.pack("<HHI", 22, 32, 0x3) + guid
    path = wav(tmp_path / "float.wav",
               fmt_chunk(tag=0xFFFE, bits=32, extension=extension),
               chunk(b"data", b"\x00" * 705600))

    assert dict(values(read(path)))["format_tag"] == "65534"
    assert dict(values(read(path)))["codec"] == "IEEE_FLOAT"


def test_the_subformat_guid_is_read_as_a_four_byte_field_not_a_two_byte_one(tmp_path):
    """A GUID's `Data1` is FOUR bytes wide, stored in the container's byte order.

    Reading only its first two works on `RIFF` by accident -- the low half of a
    little-endian word comes first -- and reads `0` on `RIFX`, where the high half
    does. Measured: scipy's `test-44100Hz-be-1ch-4bytes.wav` carries the GUID
    `00000001-...`, which is PCM, and the two-byte read called it format `0` and
    named no codec at all. The wrapper was unwrapped to nothing.
    """
    guid = struct.pack(">I", 1) + bytes.fromhex("00001000800000aa00389b71")
    extension = struct.pack(">HHI", 22, 32, 0x3) + guid
    path = wav(tmp_path / "be-wavex.wav",
               fmt_chunk(tag=0xFFFE, channels=1, rate=44100, bits=32,
                         extension=extension, big=True),
               chunk(b"data", b"\x00" * 176400, big=True), big=True)

    assert dict(values(read(path)))["codec"] == "PCM"


def test_a_big_endian_rifx_file_is_read_as_the_same_container(tmp_path):
    """`RIFX` is RIFF with every field big-endian. The `wave` module answers "not a
    WAVE file" and the run recorded `failed` for a file that is exactly a WAVE
    file."""
    path = wav(tmp_path / "be.wav", fmt_chunk(channels=1, rate=44100, bits=32,
                                              big=True),
               chunk(b"data", b"\x00" * 176400, big=True), big=True)

    assert dict(values(read(path))) == {
        "container": "WAVE", "format_tag": "1", "codec": "PCM", "channels": "1",
        "sample_rate": "44100", "bits_per_sample": "32", "duration": "1.000"}


def test_the_list_info_chunk_becomes_the_embedded_tags_2_9_asks_for(tmp_path):
    """§2.9's audio bullet: "duration, container and codec metadata, creation time,
    embedded tags". `LIST`/`INFO` is where a WAVE file keeps all three of the last
    ones, and the tag names are the format's own four-character codes."""
    info = b"INFO" + chunk(b"INAM", b"Lecture 4\x00") + chunk(
        b"IART", b"J Yung\x00") + chunk(b"ICRD", b"2026-02-14\x00")
    path = wav(tmp_path / "tagged.wav", fmt_chunk(),
               chunk(b"LIST", info), chunk(b"data", b"\x00" * 176400))

    read_values = dict(values(read(path)))
    assert read_values["INAM"] == "Lecture 4"
    assert read_values["IART"] == "J Yung"
    assert read_values["ICRD"] == "2026-02-14"


def test_a_riff_wave_with_no_fmt_chunk_raises_rather_than_returning_nothing(tmp_path):
    """704 of the 804 `.wav` files on the owner's disk are these: `RIFF`, `WAVE`, then
    the literal bytes `fake-pcm-bytes` and nothing else. §2.4 keeps the two words
    apart and `failed` is the right one -- a reader ran and the bytes really are not a
    WAVE file. Returning `None` here would say the opposite: that this deployment
    ships no reader for `.wav`."""
    path = tmp_path / "stub.wav"
    path.write_bytes(b"RIFF" + b"\x00" * 4 + b"WAVEfake-pcm-bytes")

    with pytest.raises(NotAWaveFile):
        read(path)


def test_bytes_that_are_not_riff_at_all_raise(tmp_path):
    path = tmp_path / "mislabelled.wav"
    path.write_bytes(b"\x00\x01\x02\x03 not a riff container at all")

    with pytest.raises(NotAWaveFile):
        read(path)


def test_a_riff_file_that_is_not_a_wave_form_raises(tmp_path):
    """A `.webp` renamed `.wav` is a RIFF file whose form is `WEBP`. Reading its
    chunks as audio would put invented numbers on a picture.

    The fixture carries a `fmt ` chunk ON PURPOSE. Without one the file is refused
    for the other reason -- no `fmt ` -- and deleting the form check entirely leaves
    every test green, which is what the first version of this test did.
    """
    path = tmp_path / "picture.wav"
    path.write_bytes(riff(fmt_chunk(), chunk(b"VP8 ", b"\x00" * 16), form=b"WEBP"))

    with pytest.raises(NotAWaveFile, match="WEBP"):
        read(path)


def test_a_transcript_is_never_returned_whatever_the_authorization_says(tmp_path):
    """B6: "Speech-to-text is OUT OF SCOPE for v1". `transcribe=True` is accepted and
    changes nothing, so `UnauthorizedTranscription` cannot fire on this reader's
    output and no `from_speech` text exists to authorize."""
    path = mp4(tmp_path / "lecture.mp4", created=0, duration=1000, timescale=1000)

    document = read(path, transcribe=True)

    assert [text.from_speech for text in document.texts] == []


# --------------------------------------------------------------------------- #
# the two outcomes §2.4 keeps apart
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("extension", [".xls", ".ppt", ".msg", ".ods", ".odp",
                                       ".numbers", ".mp3"])
def test_a_format_this_deployment_cannot_read_returns_none(tmp_path, extension):
    """§2.4's `unsupported`: no reader exists and the bytes were never looked at --
    as against `failed`, which means a reader ran and raised. A legacy binary or an
    ODF package needs a library this deployment does not ship, and returning an
    empty document would report the missing library as an empty file."""
    path = tmp_path / f"legacy{extension}"
    path.write_bytes(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")

    assert read(path) is None


def test_an_ooxml_part_declaring_an_entity_is_refused_before_it_is_parsed(tmp_path):
    """`ElementTree` is documented as not secure against maliciously constructed
    data. No legitimate `.xlsx` declares an entity, so the bytes are checked and the
    parser never sees them. The raise becomes P5's one `failed` run."""
    path = tmp_path / "bomb.xlsx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml",
            '<?xml version="1.0"?><!DOCTYPE workbook [<!ENTITY a "aaaaaaaaaa">]>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets/></workbook>')

    with pytest.raises(UnsafeXml):
        read(path)


def test_a_zip_member_declaring_more_bytes_than_the_ceiling_is_refused(tmp_path):
    """A 40 KB `.xlsx` can declare a 5 GB sheet, and `zipfile` will honour it. Passing
    the ceiling raises rather than truncating: a truncated read recorded as `complete`
    is §2.4's "silently an empty document" wearing a larger number."""
    path = tmp_path / "bomb.xlsx"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml", " " * (MAX_PART_BYTES + 1))

    with pytest.raises(PartTooLarge):
        read(path)


def test_a_corrupt_container_raises_rather_than_reading_as_empty(tmp_path):
    """§2.4 keeps `failed` and `unsupported` apart, and this reader must not collapse
    them: a truncated `.xlsx` is a fact about the bytes, not about the deployment."""
    path = tmp_path / "truncated.xlsx"
    path.write_bytes(b"PK\x03\x04 truncated")

    with pytest.raises(zipfile.BadZipFile):
        read(path)
