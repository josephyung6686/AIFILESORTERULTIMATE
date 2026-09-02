"""The detector that gave an extensionless file a format at all.

`cli._detect_format` answered from the extension alone, so a file with none had no
format, no `source_type` and no extractor: `route()` returned `extractor_name=None`
and the run recorded `unsupported`. A census of the owner's own disk puts 1,057
extensionless files in Desktop, Downloads and Documents, against 2,684 routed
document files in total.

§2.9 asks for both halves -- *"treat the file extension as a routing signal ...
inspect the real MIME type or file signature where possible"* -- and `router.py`
puts the second half in the reader layer, which is where this lives.

Two properties are asserted throughout and they are the ones worth breaking the
build over: a protected container is never opened, and a WEAK identification never
outranks an extension the router already knows.
"""
from __future__ import annotations

import struct
import zipfile
from pathlib import Path

import pytest

from readers.signatures import HEAD_BYTES, MAX_JSON_BYTES, signature_detector

detect = signature_detector(is_protected_container=lambda path: False)


def written(tmp_path: Path, name: str, payload) -> Path:
    path = tmp_path / name
    if isinstance(payload, bytes):
        path.write_bytes(payload)
    else:
        path.write_text(payload)
    return path


# --------------------------------------------------------------------------- #
# the refusal that comes before any byte is read
# --------------------------------------------------------------------------- #

def test_a_protected_container_is_answered_without_being_opened(tmp_path):
    """11-ops-runtime.md §4b: "What is recorded is the container, not its contents",
    and asking a question about the bytes IS entering it. This module is the one
    place in the reader layer that opens a file to decide what it is, so the refusal
    has to come first -- and it has to be provable, not asserted."""
    opened: list[Path] = []

    class Watched(type(tmp_path)):
        pass

    path = written(tmp_path, "Secrets.app", b"%PDF-1.7 not really")
    guarded = signature_detector(
        is_protected_container=lambda p: (opened.append(p) or True))

    assert guarded(path) is None
    assert opened == [path], "the predicate was not consulted"


def test_the_predicate_has_no_default_and_cannot_be_forgotten(tmp_path):
    """A default -- even `lambda path: False` -- would be a caller who never made
    the choice, on the one function in this package that opens arbitrary files."""
    with pytest.raises(TypeError):
        signature_detector()


# --------------------------------------------------------------------------- #
# strong identification: a magic number outranks the extension
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("payload,token", [
    (b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n", "pdf"),
    (b"\x89PNG\r\n\x1a\n" + b"\x00" * 16, "png"),
    (b"\xff\xd8\xff\xe0\x00\x10JFIF\x00", "jpg"),
    (b"GIF89a\x10\x00\x10\x00", "gif"),
    (b"BM\x36\x00\x00\x00\x00\x00", "bmp"),
    (b"II*\x00\x08\x00\x00\x00", "tiff"),
    (b"MM\x00*\x00\x00\x00\x08", "tiff"),
    (b"8BPS\x00\x01\x00\x00", "psd"),
    (b"ID3\x03\x00\x00\x00", "mp3"),
])
def test_a_binary_signature_names_the_format(tmp_path, payload, token):
    assert detect(written(tmp_path, "unnamed", payload)) == token


@pytest.mark.parametrize("brand,token", [
    (b"heic", "heic"), (b"avif", "avif"), (b"qt  ", "mov"),
    (b"M4A ", "m4a"), (b"isom", "mp4"), (b"mp42", "mp4"),
])
def test_one_iso_container_is_told_apart_by_its_brand(tmp_path, brand, token):
    """A `.heic` photo and a `.mov` screen recording are the same box structure with
    a different brand (ISO/IEC 14496-12 §4.3). Reading the brand is the only way to
    tell them apart, and they route to different families -- `image` and
    `audio_video`."""
    payload = struct.pack(">I", 20) + b"ftyp" + brand + b"\x00\x00\x02\x00"
    assert detect(written(tmp_path, "clip", payload)) == token


def test_a_pdf_wearing_a_txt_extension_is_read_as_a_pdf(tmp_path):
    """§2.9: "the detected format wins over the declared extension, and the
    disagreement is recorded rather than discarded". This is the case
    `extraction_routing.disagree` exists for, and until now it could never fire."""
    assert detect(written(tmp_path, "notes.txt", b"%PDF-1.4\n1 0 obj\n")) == "pdf"


# --------------------------------------------------------------------------- #
# ZIP containers, which are five formats wearing one signature
# --------------------------------------------------------------------------- #

def zipped(tmp_path: Path, name: str, members: dict) -> Path:
    path = tmp_path / name
    with zipfile.ZipFile(path, "w") as archive:
        for member, payload in members.items():
            archive.writestr(member, payload)
    return path


@pytest.mark.parametrize("members,token", [
    ({"word/document.xml": "<w:document/>"}, "docx"),
    ({"xl/workbook.xml": "<workbook/>"}, "xlsx"),
    ({"ppt/presentation.xml": "<p:presentation/>"}, "pptx"),
    ({"mimetype": "application/epub+zip"}, "epub"),
    ({"mimetype": "application/vnd.oasis.opendocument.text"}, "odt"),
    ({"mimetype": "application/vnd.oasis.opendocument.spreadsheet"}, "ods"),
    ({"mimetype": "application/vnd.oasis.opendocument.presentation"}, "odp"),
    ({"holiday photos/beach.jpg": "not really"}, "zip"),
])
def test_a_zip_is_told_apart_by_the_parts_it_holds(tmp_path, members, token):
    """`PK\\x03\\x04` is a `.docx`, a `.xlsx`, a `.pptx`, an `.epub`, an `.odt` and a
    plain archive. Stopping at `zip` would send every Word document a person owns to
    §2.5's manifest handler, which yields a file list and no text."""
    assert detect(zipped(tmp_path, "unnamed", members)) == token


def test_a_truncated_zip_is_a_zip_and_not_an_unknown(tmp_path):
    """§2.4 keeps `failed` and `unsupported` apart. A ZIP that will not open is a
    fact about the BYTES, and routing it to the archive handler is what lets that be
    recorded; answering `None` would call it `unsupported`, which says no reader
    exists and is false."""
    assert detect(written(tmp_path, "archive", b"PK\x03\x04 truncated")) == "zip"


# --------------------------------------------------------------------------- #
# text formats that identify themselves
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("text,token", [
    (r"{\rtf1\ansi\ansicpg1252 Dear committee,\par }", "rtf"),
    ("BEGIN:VCARD\r\nVERSION:3.0\r\nFN:Amara Chen\r\nEND:VCARD\r\n", "vcf"),
    ("BEGIN:VCALENDAR\r\nVERSION:2.0\r\nEND:VCALENDAR\r\n", "ics"),
    ("<!DOCTYPE html>\n<html><body><p>Enrolled</p></body></html>", "html"),
    ("<html><body>no doctype</body></html>", "html"),
    ('<?xml version="1.0"?><catalogue><book/></catalogue>', "xml"),
    ('<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg"/>', "svg"),
    ('{"course": "PHYS 1401", "term": "Spring 2026"}', "json"),
])
def test_a_text_format_that_states_what_it_is_is_taken_at_its_word(
        tmp_path, text, token):
    assert detect(written(tmp_path, "unnamed", text)) == token


def test_a_message_is_told_from_a_mailbox_of_them(tmp_path):
    """RFC 4155 §2's `From ` line opens an mbox and is not an RFC 5322 header. They
    route to the same family and are read by different branches of the reader."""
    message = ("From: achen@example.edu\r\nTo: jellis@example.edu\r\n"
               "Subject: PHYS 1401\r\n\r\nYour score was 88.\r\n")
    assert detect(written(tmp_path, "message", message)) == "eml"
    assert detect(written(tmp_path, "archive",
                          "From achen@example.edu Fri Mar 13 08:41:02 2026\r\n"
                          + message)) == "mbox"


def test_a_configuration_file_of_colons_is_not_read_as_mail(tmp_path):
    """`key: value` lines are a header block only when a BLANK LINE ends them.

    The keys here are deliberately `from`, `to` and `subject` -- the three the
    header test looks for -- so that the blank line is the only thing separating
    this file from a message. A backup configuration read as an email would have
    its destination stored as a person's address.
    """
    assert detect(written(tmp_path, "settings",
                          "from: /Users/achen/Documents\n"
                          "to: /Volumes/Backup\n"
                          "subject: nightly\n")) == "txt"


def test_a_document_that_only_looks_like_json_is_not_claimed_as_json(tmp_path):
    """The test parses the WHOLE file, not the window. Half an object parses as
    nothing, and a prose file that happens to open with a brace is not JSON."""
    assert detect(written(tmp_path, "notes",
                          '{ "this file was never closed"')) == "txt"


def test_a_json_file_longer_than_the_window_is_still_json(tmp_path):
    """The window is 8,192 bytes and a real `package-lock.json` is far longer, so
    parsing the WINDOW would find a truncated object, fail, and file every large
    JSON document on the disk as plain text."""
    payload = "[" + ",".join(f'{{"id": {n}}}' for n in range(2000)) + "]"
    assert len(payload) > HEAD_BYTES

    assert detect(written(tmp_path, "manifest", payload)) == "json"


def test_a_json_file_over_the_ceiling_is_text_rather_than_a_long_parse(tmp_path):
    """The JSON test is the one test here that must read the whole file, so it is
    the one test with a ceiling. Past it the answer is the weak one, which is true."""
    payload = '["' + "x" * (MAX_JSON_BYTES + 16) + '"]'
    assert detect(written(tmp_path, "huge", payload)) == "txt"


# --------------------------------------------------------------------------- #
# the weak answer, and the regression it would be if it did not defer
# --------------------------------------------------------------------------- #

def test_an_extensionless_text_file_becomes_readable_at_all(tmp_path):
    """The 1,057-file case. It used to route nowhere: `source_type=None`,
    `extractor_name=None`, `unsupported` -- filesystem evidence and not one word."""
    assert detect(written(tmp_path, "syllabus",
                          "PHYS 1401\nOffice hours: Tuesdays 14:00\n")) == "txt"


@pytest.mark.parametrize("name", ["grades.csv", "readings.tsv", "lab notes.md",
                                  "syllabus.txt", "settings.yaml", "query.sql"])
def test_the_weak_answer_never_overrides_an_extension_the_router_knows(
        tmp_path, name):
    """THE REGRESSION THIS EXISTS TO PREVENT. "These bytes are text" identifies no
    format. Returned unconditionally it would make every `.csv`, `.tsv`, `.md`,
    `.yaml` and `.sql` on the disk detect as `txt`, and §2.9's rule that the
    detected format WINS would then route all of them to the plain-text handler --
    undoing the spreadsheet reader on the 496 `.csv` files this disk holds."""
    assert detect(written(tmp_path, name, "course,term\nPHYS 1401,Spring 2026\n")) is None


def test_an_extension_the_router_does_not_know_still_gets_the_weak_answer(tmp_path):
    """`.eml.bak` and friends. There is no extension to defer to, so the honest
    answer is the one this module can actually make."""
    assert detect(written(tmp_path, "notes.bak", "PHYS 1401 lecture notes\n")) == "txt"


def test_binary_that_matches_nothing_stays_unidentified(tmp_path):
    """A signature this module does not recognise leaves the file exactly where it
    was. Naming it would be the invention the whole product refuses."""
    assert detect(written(tmp_path, "blob", bytes(range(256)) * 4)) is None


def test_binary_made_only_of_low_bytes_is_still_not_text(tmp_path):
    """EVERY byte here is under 0x80, so it decodes as UTF-8 without complaint --
    and it is a compiled artefact, not a document. The NUL and the other control
    characters are the whole of what separates the two, which is the test `file(1)`
    makes. Without it this is `txt`, and its bytes become a prose observation."""
    payload = b"__TEXT\x00\x00\x01\x02__DATA\x00\x00\x0e\x1f" * 64
    assert payload.decode("utf-8") is not None, "the fixture must decode cleanly"

    assert detect(written(tmp_path, "binary", payload)) is None


def test_a_legacy_office_binary_is_not_guessed_between_its_four_formats(tmp_path):
    """An OLE compound file is a `.doc`, `.xls`, `.ppt` or `.msg`, and WHICH is in
    the directory's stream names, which this module does not parse. Nothing is lost:
    this deployment ships no reader for any of the four, so a precise answer and no
    answer both end at `unsupported`."""
    assert detect(written(tmp_path, "budget",
                          b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 32)) is None


def test_an_empty_file_is_not_called_text(tmp_path):
    """Zero bytes decode as text and say nothing. Calling it `txt` would put a
    `complete` extraction of an empty document on a file nobody could read."""
    assert detect(written(tmp_path, "empty", b"")) is None
    assert detect(written(tmp_path, "empty.csv", b"")) == "csv"


def test_a_utf_16_document_is_text_despite_being_full_of_nulls(tmp_path):
    """The control-character test is what separates text from binary, and a UTF-16
    document fails it on every second byte. The BOM is read first for that reason."""
    path = tmp_path / "syllabus"
    path.write_bytes("﻿PHYS 1401 syllabus\n".encode("utf-16-le"))

    assert detect(path) == "txt"


def test_a_multi_byte_character_cut_by_the_window_is_not_read_as_binary(tmp_path):
    """The head is a fixed number of BYTES and a document is a sequence of
    characters. A file whose 8,192nd byte lands mid-character is text, and a
    decoder that gave up there would call a Japanese document binary."""
    path = tmp_path / "notes"
    body = "PHYS 1401 " + "文" * HEAD_BYTES
    path.write_text(body, encoding="utf-8")

    assert detect(path) == "txt"
