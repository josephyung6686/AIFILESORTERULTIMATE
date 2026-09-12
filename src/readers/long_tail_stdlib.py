# src/readers/long_tail_stdlib.py
"""`read_long_tail` for §2.9's six families, from the standard library.

`deployment.py` wired `read_long_tail = _no_reader`, whose docstring says *"this
deployment ships no library for the format"*. Measured against a real folder on
2026-09-03, that one line was the largest single loss of information in the
product: **every** spreadsheet, presentation, email, calendar entry and contact
card on a person's disk recorded `unsupported` with `coverage {"processed": 0}` --
the bytes never looked at -- and every count downstream agreed those files held
nothing. A `grades.csv` of four students and five columns produced zero
observations, zero text units and zero characters.

The design does not treat these as a long tail of exotica. §2.9 gives each family
its own field list, and this module fills them:

    spreadsheet   "workbook or file metadata, sheet names, column headers, visible
                   cell values, table-like regions, formulas only when useful, and
                   dates or identifiers from labeled cells"
    presentation  "slide titles, text boxes, speaker notes where available,
                   hyperlinks, embedded tables, and slide-level page boundaries"
    email         "sender, recipients, subject, sent date, thread identifiers,
                   message body, attachment names, and reply-chain context"
    calendar      "event title, start and end time, location, organizer, attendees,
                   and recurrence metadata"
    contacts      "names, organizations, email addresses, phone numbers, and
                   address-book metadata"
    audio/video   "duration, container and codec metadata, creation time, embedded
                   tags, subtitles or captions where present" -- and B6 (2026-08-20)
                   stops v1 there: "Audio and video stop at container metadata."

**Standard library only, and that is the whole point.** `.xlsx` and `.pptx` are ZIP
containers of XML, `.eml` and `.mbox` are `email` and `mailbox`, `.ics` and `.vcf`
are line-folded text, `.csv` is `csv`, and an MP4's duration is four fields of a
`moov/mvhd` atom. None of that needs a dependency, so none is added: `pyproject.toml`
keeps `dependencies = []` and the `readers` extra does not grow.

**A format with no branch returns `None`, never an exception.** §2.4's `unsupported`
means no reader exists and the bytes were never looked at; `failed` means a reader
ran and raised. `.xls`, `.ppt`, `.msg`, `.ods`, `.odp`, `.numbers` and `.mp3` are
`None` here -- a legacy binary or an ODF package needs a library this deployment does
not ship, and claiming otherwise would report a missing library as an empty document.

**What is read is what is there.** No cell is computed, no formula is evaluated, no
date is guessed. The one conversion this module performs is `NUMBER-FORMAT-AS-DATE`
below, and it exists to stop a *wrong* value reaching a person: an Excel date cell
stores `45678`, and emitting that as the visible value would be worse than emitting
nothing.
"""
from __future__ import annotations

import codecs
import csv
import email.utils
import mailbox
import struct
import zipfile
from datetime import datetime, timedelta, timezone
from email import policy as email_policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Callable, Iterator
from xml.etree import ElementTree

from extractors.long_tail import LongTailEntry, LongTailFile, LongTailText, LongTailValue
from readers.signatures import HEAD_BYTES, looks_like_text

#: OOXML namespaces, by the prefix this module uses for them. Written out rather
#: than read from the document, because a part that declares a DIFFERENT namespace
#: under the same prefix is not the format we are claiming to read.
_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
}

#: A ceiling on ONE part of a ZIP container, and the only ceiling in this module.
#: It exists because a `.xlsx` is a ZIP and a ZIP declares its own uncompressed size:
#: a 40 KB file can announce a 5 GB sheet, and `zipfile` will honour it. Passing the
#: ceiling RAISES rather than truncating, which §2.4 makes the honest of the two --
#: a truncated read recorded as `complete` is the "silently an empty document" defect
#: wearing a larger number. Row counts are NOT capped: §2.9 asks for "visible cell
#: values" with no sampling clause, and `zipfile_reader` set the precedent out loud
#: ("this deployment would rather carry a long manifest than a truncated one it has
#: to explain").
MAX_PART_BYTES: int = 256 * 1024 * 1024

#: Excel's built-in number formats that mean a date or a time, by `numFmtId`. ECMA-376
#: part 1, §18.8.30 fixes these ids; a workbook cannot redefine them. Anything else is
#: a date only if its own format code says so (`_is_date_format`).
_BUILTIN_DATE_FORMATS: frozenset[int] = frozenset(
    list(range(14, 23)) + list(range(27, 37)) + list(range(45, 48))
    + list(range(50, 59)))

#: The serial-date epochs ECMA-376 §18.17.4.1 allows. The 1900 system counts day 1 as
#: 1899-12-31 rather than 1900-01-01 because Lotus 1-2-3 believed 1900 was a leap year
#: and Excel kept the bug for compatibility; serial 60 IS that phantom 1900-02-29 and
#: is the one value this reader will not render.
_EPOCH_1900 = datetime(1899, 12, 30, tzinfo=timezone.utc)
_EPOCH_1904 = datetime(1904, 1, 1, tzinfo=timezone.utc)

#: QuickTime and MP4 count seconds from 1904-01-01 UTC (ISO/IEC 14496-12 §8.2.2).
_QUICKTIME_EPOCH = datetime(1904, 1, 1, tzinfo=timezone.utc)

#: RFC 5322 header slots whose value is a mailbox address. §2.9 names addresses as
#: potentially sensitive and `long_tail.SENSITIVE_EMAIL_VALUE_KINDS` acts on the
#: `kind`, so WHICH SLOT holds an address has to be said here -- it is format
#: knowledge (RFC 5322 §3.6.2 and §3.6.3), and P5 must not pattern-match a header name.
_ADDRESS_HEADERS: tuple[str, ...] = (
    "From", "Sender", "To", "Cc", "Bcc", "Reply-To", "Resent-From", "Resent-To")

#: The rest of §2.9's email field list. `In-Reply-To` and `References` are its
#: "thread identifiers" and "reply-chain context"; RFC 5322 §3.6.4 is where they live.
_MESSAGE_HEADERS: tuple[str, ...] = (
    "Subject", "Date", "Message-ID", "In-Reply-To", "References")

#: §2.9's calendar list, in RFC 5545's own property names. `DESCRIPTION` is not on
#: §2.9's list and is carried as a NOTE rather than a value: it is prose a person
#: wrote, so it belongs with the other bulk text, and dropping it would throw away
#: the half of an event that says what it is for.
_EVENT_PROPERTIES: tuple[str, ...] = (
    "UID", "SUMMARY", "DTSTART", "DTEND", "DURATION", "LOCATION", "ORGANIZER",
    "ATTENDEE", "RRULE", "RDATE", "EXDATE", "STATUS", "CATEGORIES")

#: §2.9's contacts list, in RFC 6350's property names. Every one of them is marked
#: potentially sensitive by `long_tail.FULLY_SENSITIVE_SOURCE_TYPES` on arrival --
#: this module raises no signal of its own and needs none.
_CARD_PROPERTIES: tuple[str, ...] = (
    "UID", "FN", "N", "NICKNAME", "ORG", "TITLE", "ROLE", "EMAIL", "TEL", "ADR",
    "URL", "BDAY", "CATEGORIES")


#: The byte-order marks Unicode defines, and the codec that consumes each one.
#: LONGEST FIRST, because `FF FE 00 00` begins a UTF-32LE document AND begins with
#: UTF-16LE's `FF FE`: tested the other way round, every UTF-32 file is read as
#: UTF-16 and comes back as letters separated by NULs -- the exact failure this
#: table exists to end, wearing the fix.
#:
#: The codec is `utf-16` and `utf-32` rather than the endian-specific spelling
#: because those two CONSUME the mark while the `-le`/`-be` forms leave it in the
#: text as a `\ufeff`, which is invisible in a viewer and is a character in every
#: match. `utf-8-sig` does the same for the three-byte mark.
_BOMS: tuple[tuple[bytes, str], ...] = (
    (codecs.BOM_UTF32_LE, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32"),
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16"),
)


def declared_encoding(prefix: bytes) -> str | None:
    """The encoding a document DECLARES in its first bytes, or None if it declares
    none.

    A byte-order mark is a statement the document makes about itself, in the same
    class as HTML's `<meta charset>` and RTF's `\ansicpg` -- both of which the
    readers here already honour -- and nothing like guessing a codepage from
    statistics. `text_documents._decode`'s standing rule is that bytes which fail as
    UTF-8 become replacement characters rather than a plausible wrong letter, and
    that rule is untouched: this reads a declaration, it does not infer one.

    IT MATTERS BECAUSE OF WHAT WRITES THESE FILES. Windows Notepad's "Unicode" save
    and Excel's own "Unicode Text (*.txt)" export are UTF-16LE with a mark, and so
    are a great many `.tsv` exports. Decoded as UTF-8 they came back as
    `'\ufffd\ufffdc\x00o\x00u\x00r\x00s\x00e\x00'` -- stored `complete`, and
    handed to the recogniser as the document's prose. Not missing information but
    false information, which §2.4 treats as the worse of the two.

    Shared with `readers/text_documents.py`, which already imports this module for
    the other things that are true of bytes rather than of a format.
    """
    for mark, encoding in _BOMS:
        if prefix.startswith(mark):
            return encoding
    return None


class PartTooLarge(Exception):
    """A ZIP member declares more uncompressed bytes than this reader will read.

    A statement about the bytes, so it becomes P5's one `failed` run and the scan
    continues -- not a `ContractViolation`, which is a statement about the caller.
    """


class NotAWaveFile(Exception):
    """The bytes are not a RIFF/WAVE container, or are one with no `fmt ` chunk.

    §2.4's `failed`, deliberately, and not `unsupported`: a reader ran, opened the
    bytes and found they are not what the extension claims. Measured on the owner's
    disk, 704 of 804 `.wav` files are `RIFF`, `WAVE`, then the literal ASCII
    `fake-pcm-bytes` -- a test fixture some tool wrote, with no `fmt ` chunk and no
    audio in it. Recording those `unsupported` would say this deployment ships no
    reader for `.wav`, which is the opposite of true.
    """


class UnsafeXml(Exception):
    """An OOXML part carries a DTD or an entity declaration.

    `xml.etree.ElementTree` is documented as not secure against maliciously
    constructed data: an entity that expands into itself a few times over is enough
    to exhaust memory before any content is read. No legitimate `.xlsx` or `.pptx`
    part declares one, so the presence of a declaration is refused rather than parsed
    -- and refused by looking at the BYTES, before a parser sees them.
    """


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #

def _part(archive: zipfile.ZipFile, name: str) -> bytes | None:
    """One ZIP member's bytes, or None if the container has no such part."""
    try:
        info = archive.getinfo(name)
    except KeyError:
        return None
    if info.file_size > MAX_PART_BYTES:
        raise PartTooLarge(
            f"{name} declares {info.file_size} uncompressed bytes, over this "
            f"reader's {MAX_PART_BYTES}")
    return archive.read(info)


def _xml(payload: bytes | None):
    """Parse one OOXML part, after refusing a DTD or an entity declaration."""
    if payload is None:
        return None
    head = payload[:4096].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in payload.upper():
        raise UnsafeXml("an OOXML part declares a DTD or an entity; refused unparsed")
    return ElementTree.fromstring(payload)


def _tag(prefix: str, name: str) -> str:
    return f"{{{_NS[prefix]}}}{name}"


def _text_of(node) -> str:
    """Every `<a:t>` run under a node, joined -- DrawingML's text is per-run."""
    return "".join(t.text or "" for t in node.iter(_tag("a", "t")))


def _relationships(archive: zipfile.ZipFile, part: str) -> dict[str, str]:
    """`rId -> target` for one part, from its `_rels` sidecar. Targets stay relative;
    the caller resolves them against the part's own directory."""
    folder, _, name = part.rpartition("/")
    tree = _xml(_part(archive, f"{folder}/_rels/{name}.rels" if folder
                      else f"_rels/{name}.rels"))
    if tree is None:
        return {}
    # `Id` FILTERED, not defaulted. Every valid relationship carries one; a part
    # damaged enough to omit it used to become the key `None`, which no lookup
    # can hit -- so the entry was dead weight that only made the map look
    # complete. Skipping it says what is true: that relationship is unusable.
    return {identifier: node.get("Target") or ""
            for node in tree.findall(_tag("pkgrel", "Relationship"))
            if (identifier := node.get("Id")) is not None}


def _resolve(base: str, target: str) -> str:
    """A relationship target as a package path. `../` is legal and common."""
    if target.startswith("/"):
        return target.lstrip("/")
    parts = base.rpartition("/")[0].split("/") if "/" in base else []
    for step in target.split("/"):
        if step == "..":
            if parts:
                parts.pop()
        elif step not in ("", "."):
            parts.append(step)
    return "/".join(parts)


def _unfold(text: str) -> list[str]:
    """RFC 5545 §3.1 and RFC 6350 §3.2 line unfolding.

    Both formats break a long line by inserting CRLF and one leading space or tab;
    a reader that splits on newlines alone cuts values in half, which is exactly the
    "incomplete data" failure. Folding is undone before anything is parsed.
    """
    lines: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _property(line: str) -> tuple[str, str] | None:
    """One `NAME;PARAM=x:value` line as `(NAME, value)`, or None if it is not one.

    The colon that ends the name may be preceded by parameters, and a parameter's
    value may itself be a quoted string containing a colon (RFC 6350 §3.3), so the
    split is a scan rather than a `partition`.
    """
    quoted = False
    for index, character in enumerate(line):
        if character == '"':
            quoted = not quoted
        elif character == ":" and not quoted:
            name = line[:index].split(";")[0].strip().upper()
            return (name, line[index + 1:]) if name else None
    return None


def _unescape(value: str) -> str:
    """RFC 5545 §3.3.11 / RFC 6350 §3.4 text escaping, undone."""
    out: list[str] = []
    index = 0
    while index < len(value):
        character = value[index]
        if character == "\\" and index + 1 < len(value):
            nxt = value[index + 1]
            out.append({"n": "\n", "N": "\n"}.get(nxt, nxt))
            index += 2
        else:
            out.append(character)
            index += 1
    return "".join(out)


# --------------------------------------------------------------------------- #
# spreadsheets
# --------------------------------------------------------------------------- #

def _column_index(reference: str) -> int:
    """`AB12` -> 28. Spreadsheet columns are base-26 with no zero digit."""
    index = 0
    for character in reference:
        if not character.isalpha():
            break
        index = index * 26 + (ord(character.upper()) - 64)
    return index


def _is_date_format(code: str) -> bool:
    """Does this `numFmt` format code render a date or a time?

    ECMA-376 §18.8.31 codes mix literals in quotes with the date tokens `y m d h s`,
    so the quoted runs and the escaped characters are removed first: `"May"` in a
    currency format must not make it a date.
    """
    stripped: list[str] = []
    quoted = False
    index = 0
    while index < len(code):
        character = code[index]
        if character == '"':
            quoted = not quoted
        elif character == "\\":
            index += 1
        elif character == "[":
            end = code.find("]", index)
            index = len(code) if end < 0 else end
        elif not quoted:
            stripped.append(character)
        index += 1
    return any(token in "".join(stripped).lower() for token in "ymdhs")


def _serial_to_iso(serial: float, *, epoch: datetime) -> str | None:
    """An Excel serial date as ISO-8601, or None where the value is not a date.

    Serial 60 in the 1900 system is 1900-02-29, a day that did not exist; it is the
    Lotus compatibility bug and there is no correct answer, so none is given.
    """
    if serial < 0:
        return None
    if epoch is _EPOCH_1900 and serial == 60:
        return None
    if epoch is _EPOCH_1900 and serial < 60:
        serial += 1                    # before the phantom day, the offset is one out
    moment = epoch + timedelta(days=serial)
    if serial >= 1 and abs(serial - round(serial)) < 1e-9:
        return moment.date().isoformat()
    return moment.replace(tzinfo=None).isoformat(timespec="seconds")


def _date_styles(archive: zipfile.ZipFile) -> tuple[frozenset[int], bool]:
    """Which cell-style indices format their value as a date, and the epoch flag.

    Without this, a date cell reaches a person as `45678`. §2.9 asks a spreadsheet
    for "dates or identifiers from labeled cells", and a five-digit count of days is
    neither -- it is the wrong value, which is the one outcome worse than no value.
    """
    workbook = _xml(_part(archive, "xl/workbook.xml"))
    date1904 = False
    if workbook is not None:
        properties = workbook.find(_tag("main", "workbookPr"))
        if properties is not None:
            date1904 = properties.get("date1904") in ("1", "true")

    styles = _xml(_part(archive, "xl/styles.xml"))
    if styles is None:
        return frozenset(), date1904

    custom: dict[int, str] = {}
    formats = styles.find(_tag("main", "numFmts"))
    if formats is not None:
        for node in formats.findall(_tag("main", "numFmt")):
            # The absent attribute is checked rather than caught: `TypeError` from
            # `int(None)` and `ValueError` from `int("x")` are the same line to an
            # `except`, and only the second is about the file's CONTENT.
            declared = node.get("numFmtId")
            if declared is None:
                continue
            try:
                custom[int(declared)] = node.get("formatCode") or ""
            except ValueError:
                continue

    dated: set[int] = set()
    cell_formats = styles.find(_tag("main", "cellXfs"))
    if cell_formats is not None:
        for position, node in enumerate(cell_formats.findall(_tag("main", "xf"))):
            try:
                fmt = int(node.get("numFmtId") or 0)
            except ValueError:
                continue
            if fmt in _BUILTIN_DATE_FORMATS or _is_date_format(custom.get(fmt, "")):
                dated.add(position)
    return frozenset(dated), date1904


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    tree = _xml(_part(archive, "xl/sharedStrings.xml"))
    if tree is None:
        return []
    return [_shared_text(item) for item in tree.findall(_tag("main", "si"))]


def _shared_text(item) -> str:
    return "".join(node.text or "" for node in item.iter(_tag("main", "t")))


def _cell_value(cell, *, shared: list[str], dated: frozenset[int],
                epoch: datetime) -> str:
    """One cell as the string a person sees, or "" where the cell holds nothing.

    A formula's TEXT is not emitted: §2.9 wants "formulas only when useful" and does
    not say when, so what is stored is the cached RESULT the file already holds --
    the value the person last saw in the sheet. `.numbers` in the routing table is a
    different format and is not read here.
    """
    kind = cell.get("t")
    if kind == "inlineStr":
        node = cell.find(_tag("main", "is"))
        return _shared_text(node) if node is not None else ""
    value = cell.find(_tag("main", "v"))
    raw = (value.text or "") if value is not None else ""
    if not raw:
        return ""
    if kind == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return ""
    if kind == "b":
        # ECMA-376 §18.18.11: a boolean cell stores 0 or 1 and DISPLAYS FALSE or
        # TRUE. Emitting the digit would put a number where the person read a word.
        return "TRUE" if raw not in ("0", "") else "FALSE"
    if kind in (None, "n"):
        try:
            style = int(cell.get("s") or -1)
        except ValueError:
            style = -1
        if style in dated:
            try:
                rendered = _serial_to_iso(float(raw), epoch=epoch)
            except ValueError:
                rendered = None
            if rendered is not None:
                return rendered
    return raw


def _read_xlsx(path: Path, max_cells: int) -> LongTailFile:
    """Every sheet, every visible cell, up to `max_cells` across the WHOLE workbook.

    The ceiling bounds the DATABASE, which grows per file, so a workbook of forty
    sheets does not get forty ceilings. Past it the cells are still counted and no
    longer stored: `cells_total` is what makes the resulting `capped` run carry a
    real coverage instead of claiming the sheet was as short as the ceiling.

    Sheet NAMES are never capped. §2.9 asks for them separately from "visible cell
    values", they are one row each, and they are most of what says what a workbook is.
    """
    with zipfile.ZipFile(path) as archive:
        shared = _shared_strings(archive)
        dated, date1904 = _date_styles(archive)
        epoch = _EPOCH_1904 if date1904 else _EPOCH_1900

        workbook = _xml(_part(archive, "xl/workbook.xml"))
        links = _relationships(archive, "xl/workbook.xml")
        sheets: list[tuple[str, str]] = []
        if workbook is not None:
            container = workbook.find(_tag("main", "sheets"))
            for node in (container if container is not None else []):
                # A `<sheet>` with no `r:id` names no part; skipped, not looked up
                # under a None key.
                reference = node.get(_tag("rel", "id"))
                target = links.get(reference) if reference is not None else None
                if target:
                    sheets.append((node.get("name") or "",
                                   _resolve("xl/workbook.xml", target)))

        entries: list[LongTailEntry] = []
        texts: list[LongTailText] = []
        seen = 0
        for ordinal, (name, part) in enumerate(sheets, 1):
            entries.append(LongTailEntry(kind="sheet", index=ordinal,
                                         label=name or None))
            tree = _xml(_part(archive, part))
            if tree is None:
                continue
            data = tree.find(_tag("main", "sheetData"))
            headers: dict[int, str] = {}
            for row_number, row in enumerate(
                    data.findall(_tag("main", "row")) if data is not None else [], 1):
                for cell in row.findall(_tag("main", "c")):
                    column = _column_index(cell.get("r") or "")
                    if column < 1:
                        continue
                    rendered = _cell_value(cell, shared=shared, dated=dated,
                                           epoch=epoch)
                    if not rendered:
                        continue
                    seen += 1
                    if seen > max_cells:
                        # COUNTED AND DROPPED. The count is what `coverage` needs and
                        # the drop is what the ceiling is for; rendering the cell to
                        # find out it is non-empty is the same work the line above
                        # already did, so nothing is spent twice.
                        continue
                    if row_number == 1:
                        headers[column] = rendered
                    texts.append(LongTailText(
                        zone="table", text=rendered, entry_ordinal=ordinal,
                        row=row_number, column=column,
                        column_header=headers.get(column)))

        values, iso_dates = _package_properties(archive)
    return LongTailFile(entries=tuple(entries), values=tuple(values),
                        texts=tuple(texts), iso_dates=iso_dates,
                        cells_total=seen, capped=seen > max_cells)


def _package_properties(archive: zipfile.ZipFile
                        ) -> tuple[list[LongTailValue], dict[str, str]]:
    """§2.9's "workbook or file metadata", from OPC core properties.

    The slot names are the XML element's own local names (`creator`, `title`,
    `created`), which is P4 D7's "the format's own slot name, verbatim".
    """
    tree = _xml(_part(archive, "docProps/core.xml"))
    if tree is None:
        return [], {}
    values: list[LongTailValue] = []
    iso_dates: dict[str, str] = {}
    for node in tree:
        name = node.tag.rpartition("}")[2]
        text = (node.text or "").strip()
        if not text:
            continue
        values.append(LongTailValue(name=name, value=text))
        if name in ("created", "modified"):
            stamp = text[:-1] + "+00:00" if text.endswith("Z") else text
            try:
                iso_dates[name] = datetime.fromisoformat(stamp).isoformat()
            except ValueError:
                pass
    return values, iso_dates


def _delimited_sheet(handle, delimiter: str, max_cells: int) -> LongTailFile:
    """One unnamed sheet, every visible cell up to `max_cells`, from an open handle.

    Past the ceiling the rows keep streaming and the cells keep being counted; only
    the storing stops. `csv.reader` is a generator, so the tail of a million-row
    export is never held in memory -- what the ceiling saves is the two database rows
    per cell downstream, which is where the cost actually was.
    """
    texts: list[LongTailText] = []
    headers: dict[int, str] = {}
    seen = 0
    for row_number, row in enumerate(csv.reader(handle, delimiter=delimiter), 1):
        for column, cell in enumerate(row, 1):
            cell = cell.strip()
            if not cell:
                continue
            seen += 1
            if seen > max_cells:
                continue
            if row_number == 1:
                headers[column] = cell
            texts.append(LongTailText(
                zone="table", text=cell, entry_ordinal=1, row=row_number,
                column=column, column_header=headers.get(column)))
    return LongTailFile(entries=(LongTailEntry(kind="sheet", index=1),),
                        texts=tuple(texts),
                        cells_total=seen, capped=seen > max_cells)


def _read_delimited(path: Path, delimiter: str,
                    max_cells: int) -> LongTailFile:
    """A `.csv` or `.tsv`: one unnamed sheet, every visible cell.

    `utf-8-sig` because a spreadsheet application writes a BOM and a reader that
    keeps it puts an invisible character on the front of the first column header,
    where it silently stops that header matching anything.

    AND THE MARK MAY NOT BE A UTF-8 ONE. "Unicode Text (*.txt)" is one of Excel's own
    save formats and it is UTF-16LE; `utf-8-sig` reads such a file as NUL-interleaved
    mojibake and records it `complete`. `declared_encoding` reads whichever mark is
    there -- it is the document's own statement, not a guess -- and a file with no
    mark decodes exactly as it did before.

    `errors="replace"` is right HERE and only here: these two extensions declare
    themselves as text, so a byte that will not decode is one damaged character in
    a document that is otherwise readable, and a replacement character is the
    honest rendering of it. `_read_delimited_if_text` below is the same reader for
    the extensions that make no such declaration.
    """
    with open(path, "rb") as probe:
        encoding = declared_encoding(probe.read(4)) or "utf-8-sig"
    with open(path, newline="", encoding=encoding, errors="replace") as handle:
        return _delimited_sheet(handle, delimiter, max_cells)


def _read_delimited_if_text(path: Path, delimiter: str,
                            max_cells: int) -> LongTailFile | None:
    """The same sheet, but only if the bytes really are text. Otherwise None.

    For extensions whose NAME does not promise text. `.raw` is Instron's tensile-test
    export on this disk and a camera raw on a photographer's, and the router cannot
    tell those apart without opening the file -- so the tiebreak is here, at the
    bytes, where it can be answered instead of guessed.

    TWO CHECKS, AND STRICT DECODING IS ONLY THE SECOND. This used to say decoding
    was the whole of it -- "text decodes, a photograph does not" -- which is true of
    an invalid-UTF-8 header and false of the C0 control block, every byte of which
    is valid UTF-8. R-33, measured 2026-09-06: a `capture.raw` of
    `\x00\x01\x02rawsensor\x03` decoded, became a one-cell sheet holding its own
    raw bytes, and was recorded `complete`. So the head is asked `looks_like_text`
    first -- `readers.signatures`' own rule, which is `file(1)`'s and is published
    for this caller rather than restated here.

    §2.4's two outcomes stay apart -- None is `unsupported`, "no reader exists for
    this format in this deployment", which is exactly true of a camera raw. With
    `errors="replace"` the same photograph would have become a sheet of replacement
    characters recorded `complete`, and nothing downstream could have told that from
    a file the product had genuinely read.

    Streaming rather than `read_bytes().decode(...)`: a raw frame is tens of
    megabytes and there is no reason to hold one in memory to find out it is not a
    spreadsheet. `csv.reader` raises on the first undecodable byte.
    """
    try:
        with open(path, "rb") as probe:
            # A camera raw begins `FF D8 FF` (JPEG), `II*\0` or `MM\0*` (TIFF), none
            # of which is a byte-order mark -- so this reads the mark of a real
            # UTF-16 export and leaves the strict decode below to answer for
            # everything else, exactly as before.
            head = probe.read(HEAD_BYTES)
            if not looks_like_text(head):
                return None
            encoding = declared_encoding(head[:4]) or "utf-8-sig"
        with open(path, newline="", encoding=encoding) as handle:
            return _delimited_sheet(handle, delimiter, max_cells)
    except UnicodeDecodeError:
        return None


# --------------------------------------------------------------------------- #
# presentations
# --------------------------------------------------------------------------- #

def _slide_parts(archive: zipfile.ZipFile) -> list[str]:
    """Slide parts in the presentation's own order, from `sldIdLst`.

    Not `sorted(namelist())`: `slide10.xml` sorts before `slide2.xml`, and §2.9 asks
    for "slide-level page boundaries", which are worth nothing in the wrong order.
    """
    tree = _xml(_part(archive, "ppt/presentation.xml"))
    if tree is None:
        return []
    links = _relationships(archive, "ppt/presentation.xml")
    order: list[str] = []
    container = tree.find(_tag("p", "sldIdLst"))
    for node in (container if container is not None else []):
        # As in `_read_xlsx` above: a slide reference with no `r:id` names no part.
        reference = node.get(_tag("rel", "id"))
        target = links.get(reference) if reference is not None else None
        if target:
            order.append(_resolve("ppt/presentation.xml", target))
    return order


def _placeholder_type(shape) -> str | None:
    holder = shape.find(f'./{_tag("p", "nvSpPr")}/{_tag("p", "nvPr")}/'
                        f'{_tag("p", "ph")}')
    return holder.get("type") if holder is not None else None


def _read_pptx(path: Path) -> LongTailFile:
    entries: list[LongTailEntry] = []
    texts: list[LongTailText] = []
    values: list[LongTailValue] = []
    with zipfile.ZipFile(path) as archive:
        for ordinal, part in enumerate(_slide_parts(archive), 1):
            entries.append(LongTailEntry(kind="slide", index=ordinal))
            tree = _xml(_part(archive, part))
            if tree is None:
                continue
            region = 0
            for shape in tree.iter(_tag("p", "sp")):
                rendered = "\n".join(
                    _text_of(paragraph) for paragraph in shape.iter(_tag("a", "p")))
                if not rendered.strip():
                    continue
                region += 1
                kind = _placeholder_type(shape)
                # A slide's title is a HEADING, not P4's `title` zone: `title` is the
                # document's own metadata slot (§2.3's core property, §2.2's PDF
                # info dictionary), and a deck has one of those and many slide titles.
                zone = "heading" if kind in ("title", "ctrTitle") else "body"
                texts.append(LongTailText(zone=zone, text=rendered,
                                          entry_ordinal=ordinal, region=region))
            for link in _relationships(archive, part).values():
                if link.startswith(("http://", "https://", "mailto:")):
                    values.append(LongTailValue(name="hyperlink", value=link,
                                                entry_ordinal=ordinal))
            notes = _notes_part(archive, part)
            if notes is not None:
                rendered = "\n".join(
                    _text_of(paragraph) for paragraph in notes.iter(_tag("a", "p")))
                if rendered.strip():
                    region += 1
                    texts.append(LongTailText(zone="notes", text=rendered,
                                              entry_ordinal=ordinal, region=region))
        package, iso_dates = _package_properties(archive)
    return LongTailFile(entries=tuple(entries), values=tuple(package + values),
                        texts=tuple(texts), iso_dates=iso_dates)


def _notes_part(archive: zipfile.ZipFile, slide: str):
    for target in _relationships(archive, slide).values():
        if "notesSlide" in target:
            return _xml(_part(archive, _resolve(slide, target)))
    return None


# --------------------------------------------------------------------------- #
# email
# --------------------------------------------------------------------------- #

def _message_values(message, ordinal: int) -> list[LongTailValue]:
    values: list[LongTailValue] = []
    for header in _ADDRESS_HEADERS:
        for raw in message.get_all(header, []):
            rendered = str(raw).strip()
            if rendered:
                values.append(LongTailValue(name=header, value=rendered,
                                            entry_ordinal=ordinal, kind="address"))
    for header in _MESSAGE_HEADERS:
        for raw in message.get_all(header, []):
            rendered = str(raw).strip()
            if rendered:
                values.append(LongTailValue(name=header, value=rendered,
                                            entry_ordinal=ordinal))
    for part in message.walk():
        name = part.get_filename()
        if name:
            values.append(LongTailValue(name="attachment", value=str(name),
                                        entry_ordinal=ordinal))
    return values


def _message_bodies(message, ordinal: int, region_from: int
                    ) -> tuple[list[LongTailText], int]:
    """Every `text/plain` part of one message, each its own addressable region.

    HTML-only mail yields no body here. Stripping tags is `text_documents.py`'s job
    and calling into it would put one format's parser inside another's reader; what
    an HTML-only message loses is its body text, and it keeps every header.
    """
    texts: list[LongTailText] = []
    region = region_from
    for part in message.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get_content_type() != "text/plain" or part.get_filename():
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            rendered = payload.decode(charset, errors="replace")
        except LookupError:
            rendered = payload.decode("utf-8", errors="replace")
        if not rendered.strip():
            continue
        region += 1
        texts.append(LongTailText(zone="body", text=rendered,
                                  entry_ordinal=ordinal, region=region))
    return texts, region


def _sent_iso(message) -> str | None:
    raw = message.get("Date")
    if not raw:
        return None
    try:
        return email.utils.parsedate_to_datetime(str(raw)).isoformat()
    except (TypeError, ValueError):
        return None


def _unique_label(label: str, taken: set[str], ordinal: int) -> str:
    """One entry, one label. An entry is label-addressed (P4 segment-kind rule 2),
    and `text_units` is keyed by the container path, so two entries wearing one
    label lose the second's text to `DuplicateUnit` (`104` R-178: a recurring
    calendar event's exceptions share its UID; two exported calendars on the owner's
    second corpus failed whole). The format's own identifier stays the label and the
    second wearer is told apart by its position."""
    if label not in taken:
        taken.add(label)
        return label
    disambiguated = f"{label} #{ordinal}"
    taken.add(disambiguated)
    return disambiguated


def _assemble_mail(messages: list[Any]) -> LongTailFile:
    """The shared shape for one `.eml` and for an `.mbox` of many.

    `iso_dates` is keyed by SLOT NAME, so a mailbox of forty messages has forty
    values named `Date` and one key to normalize them all. The ISO date is therefore
    supplied only when the file holds exactly one message. Attaching message one's
    date to message forty would be a wrong value where an absent one costs nothing --
    the raw `Date` header is stored either way.
    """
    entries: list[LongTailEntry] = []
    values: list[LongTailValue] = []
    texts: list[LongTailText] = []
    taken: set[str] = set()
    for ordinal, message in enumerate(messages, 1):
        identifier = str(message.get("Message-ID") or f"message {ordinal}").strip()
        entries.append(LongTailEntry(kind="entry",
                                     label=_unique_label(identifier, taken, ordinal)))
        values.extend(_message_values(message, ordinal))
        body, _ = _message_bodies(message, ordinal, 0)
        texts.extend(body)
    iso_dates: dict[str, str] = {}
    if len(messages) == 1:
        stamp = _sent_iso(messages[0])
        if stamp is not None:
            iso_dates["Date"] = stamp
    return LongTailFile(entries=tuple(entries), values=tuple(values),
                        texts=tuple(texts), iso_dates=iso_dates)


def _read_eml(path: Path) -> LongTailFile:
    with open(path, "rb") as handle:
        return _assemble_mail([BytesParser(policy=email_policy.default).parse(handle)])


def _read_mbox(path: Path) -> LongTailFile:
    box = mailbox.mbox(str(path))
    try:
        return _assemble_mail(list(box))
    finally:
        box.close()


# --------------------------------------------------------------------------- #
# calendar and contacts
# --------------------------------------------------------------------------- #

def _icalendar_datetime(value: str) -> str | None:
    """RFC 5545 §3.3.5 `DATE-TIME` or §3.3.4 `DATE` as ISO-8601.

    A local time with no `Z` and no `TZID` is FLOATING (§3.3.5): it has no offset,
    and inventing UTC would move a 9 a.m. appointment by up to half a day. It is
    rendered without one.
    """
    text = value.strip()
    try:
        if text.endswith("Z"):
            return (datetime.strptime(text, "%Y%m%dT%H%M%SZ")
                    .replace(tzinfo=timezone.utc).isoformat())
        if "T" in text:
            return datetime.strptime(text, "%Y%m%dT%H%M%S").isoformat()
        return datetime.strptime(text, "%Y%m%d").date().isoformat()
    except ValueError:
        return None


def _blocks(lines: list[str], component: str) -> Iterator[list[str]]:
    current: list[str] | None = None
    for line in lines:
        upper = line.strip().upper()
        if upper == f"BEGIN:{component}":
            current = []
        elif upper == f"END:{component}":
            if current is not None:
                yield current
            current = None
        elif current is not None:
            current.append(line)


def _read_ics(path: Path) -> LongTailFile:
    lines = _unfold(path.read_text(encoding="utf-8", errors="replace"))
    entries: list[LongTailEntry] = []
    values: list[LongTailValue] = []
    texts: list[LongTailText] = []
    iso_dates: dict[str, str] = {}
    events = list(_blocks(lines, "VEVENT"))
    taken: set[str] = set()
    for ordinal, block in enumerate(events, 1):
        properties = [pair for pair in (_property(line) for line in block)
                      if pair is not None]
        identifier = next((v for n, v in properties if n == "UID"), f"event {ordinal}")
        # A recurrence exception shares the series' UID and differs by RECURRENCE-ID;
        # that pair is the event's own identifier, and only when a file repeats
        # even that does position tell them apart.
        recurrence = next((v for n, v in properties if n == "RECURRENCE-ID"), None)
        label = identifier.strip() + (f" / {recurrence.strip()}" if recurrence else "")
        entries.append(LongTailEntry(kind="entry",
                                     label=_unique_label(label, taken, ordinal)))
        region = 0
        for name, value in properties:
            rendered = _unescape(value).strip()
            if not rendered:
                continue
            if name == "DESCRIPTION":
                # A second DESCRIPTION in one event is a second region, not the
                # first one's twin.
                region += 1
                texts.append(LongTailText(zone="notes", text=rendered,
                                          entry_ordinal=ordinal, region=region))
                continue
            if name not in _EVENT_PROPERTIES:
                continue
            values.append(LongTailValue(name=name, value=rendered,
                                        entry_ordinal=ordinal))
            if len(events) == 1 and name in ("DTSTART", "DTEND"):
                stamp = _icalendar_datetime(rendered)
                if stamp is not None:
                    iso_dates[name] = stamp
    return LongTailFile(entries=tuple(entries), values=tuple(values),
                        texts=tuple(texts), iso_dates=iso_dates)


def _read_vcf(path: Path) -> LongTailFile:
    lines = _unfold(path.read_text(encoding="utf-8", errors="replace"))
    entries: list[LongTailEntry] = []
    values: list[LongTailValue] = []
    texts: list[LongTailText] = []
    taken: set[str] = set()
    for ordinal, block in enumerate(_blocks(lines, "VCARD"), 1):
        properties = [pair for pair in (_property(line) for line in block)
                      if pair is not None]
        name = next((v for n, v in properties if n == "FN"), None)
        identifier = next((v for n, v in properties if n == "UID"), None)
        entries.append(LongTailEntry(kind="entry", label=_unique_label(
            (identifier or name or f"card {ordinal}").strip(), taken, ordinal)))
        region = 0
        for slot, value in properties:
            rendered = _unescape(value).strip()
            if not rendered:
                continue
            if slot == "NOTE":
                region += 1
                texts.append(LongTailText(zone="notes", text=rendered,
                                          entry_ordinal=ordinal, region=region))
                continue
            if slot not in _CARD_PROPERTIES:
                continue
            values.append(LongTailValue(name=slot, value=rendered,
                                        entry_ordinal=ordinal))
    return LongTailFile(entries=tuple(entries), values=tuple(values),
                        texts=tuple(texts))


# --------------------------------------------------------------------------- #
# audio and video -- container metadata, and B6 stops there
# --------------------------------------------------------------------------- #

def _atoms(payload: bytes, start: int, end: int) -> Iterator[tuple[bytes, int, int]]:
    """ISO/IEC 14496-12 §4.2 boxes at one level: `(type, body start, body end)`."""
    cursor = start
    while cursor + 8 <= end:
        size = int.from_bytes(payload[cursor:cursor + 4], "big")
        kind = payload[cursor + 4:cursor + 8]
        body = cursor + 8
        if size == 1:                                   # 64-bit `largesize`
            if body + 8 > end:
                return
            size = int.from_bytes(payload[body:body + 8], "big")
            body += 8
        elif size == 0:                                 # runs to the end of the file
            size = end - cursor
        if size < 8 or cursor + size > end:
            return
        yield kind, body, cursor + size
        cursor += size


def _find_atom(payload: bytes, path: tuple[bytes, ...], start: int,
               end: int) -> tuple[int, int] | None:
    head, rest = path[0], path[1:]
    for kind, body, stop in _atoms(payload, start, end):
        if kind != head:
            continue
        return (body, stop) if not rest else _find_atom(payload, rest, body, stop)
    return None


def _read_mp4(path: Path) -> LongTailFile | None:
    payload = path.read_bytes()
    values: list[LongTailValue] = []
    iso_dates: dict[str, str] = {}

    brand = _find_atom(payload, (b"ftyp",), 0, len(payload))
    if brand is None:
        return None                                   # not an ISO base-media file
    major = payload[brand[0]:brand[0] + 4].decode("ascii", errors="replace").strip()
    if major:
        values.append(LongTailValue(name="major_brand", value=major))

    header = _find_atom(payload, (b"moov", b"mvhd"), 0, len(payload))
    if header is not None:
        start, _ = header
        version = payload[start]
        if version == 1:
            created, modified, timescale, duration = struct.unpack(
                ">QQIQ", payload[start + 4:start + 32])
        else:
            created, modified, timescale, duration = struct.unpack(
                ">IIII", payload[start + 4:start + 20])
        if timescale:
            values.append(LongTailValue(name="duration",
                                        value=f"{duration / timescale:.3f}"))
            values.append(LongTailValue(name="timescale", value=str(timescale)))
        for slot, seconds in (("creation_time", created),
                              ("modification_time", modified)):
            if not seconds:
                continue
            stamp = (_QUICKTIME_EPOCH + timedelta(seconds=seconds)).isoformat()
            values.append(LongTailValue(name=slot, value=str(seconds)))
            iso_dates[slot] = stamp

    # `codec metadata`: the sample-entry type of each track, which is where a
    # container names its codec (`avc1`, `mp4a`). Read from the boxes it is in and
    # not from the extension, which says nothing about what is inside.
    moov = _find_atom(payload, (b"moov",), 0, len(payload))
    if moov is not None:
        for kind, body, stop in _atoms(payload, *moov):
            if kind != b"trak":
                continue
            table = _find_atom(payload, (b"mdia", b"minf", b"stbl", b"stsd"),
                               body, stop)
            if table is None:
                continue
            for entry, _, _ in _atoms(payload, table[0] + 8, table[1]):
                values.append(LongTailValue(
                    name="codec", value=entry.decode("ascii", errors="replace")))
    return LongTailFile(values=tuple(values), iso_dates=iso_dates)


#: WAVE format tags, by the name the registry gives them (RFC 2361; Microsoft's
#: `mmreg.h`). Only the tags a real disk holds are here, because a tag this table
#: does not carry is emitted as its NUMBER and given no `codec` name at all -- an
#: unnamed codec costs a word, and a wrongly named one is a false statement about
#: the file. `0xFFFE` is not audio at all: it is a wrapper, resolved below.
_WAVE_CODECS: dict[int, str] = {
    0x0001: "PCM",
    0x0002: "ADPCM",
    0x0003: "IEEE_FLOAT",
    0x0006: "ALAW",
    0x0007: "MULAW",
    0x0011: "IMA_ADPCM",
    0x0031: "GSM610",
    0x0050: "MPEG",
    0x0055: "MPEGLAYER3",
    0x2000: "DOLBY_AC3_SPDIF",
}

#: `WAVE_FORMAT_EXTENSIBLE`. Its `fmt ` chunk holds a 16-byte SubFormat GUID whose
#: first two bytes ARE the real format tag, which is why the tag alone identifies
#: nothing: four of the owner's files carry it and every one of them is ordinary PCM
#: or float audio wearing the wrapper a multichannel-capable encoder puts on.
_WAVE_FORMAT_EXTENSIBLE = 0xFFFE

#: `LIST`/`INFO` four-character codes, RIFF's own tag block (IBM/Microsoft
#: Multimedia Programming Interface 1.0, §2). §2.9 asks audio for "creation time,
#: embedded tags"; this is where a WAVE file keeps them. Restricted to the codes
#: that name a thing a person would recognise -- the rest of the registry is
#: encoder bookkeeping.
_INFO_TAGS: frozenset[bytes] = frozenset({
    b"INAM", b"IART", b"IPRD", b"ICMT", b"ICRD", b"ISFT", b"IGNR", b"ICOP",
    b"IENG", b"ISBJ", b"ITRK", b"ILNG",
})


def _riff_chunks(payload: bytes, start: int, end: int, *, big: bool
                 ) -> Iterator[tuple[bytes, int, int]]:
    """RIFF chunks at one level: `(four-character code, body start, body end)`.

    The same shape as `_atoms` above and for the same reason -- a container is read
    as a container. A chunk whose declared size runs past the end of the file ends
    the walk rather than raising: what was already read is real, and a truncated tail
    is not a reason to discard a `fmt ` chunk that parsed.
    """
    order = ">" if big else "<"
    cursor = start
    while cursor + 8 <= end:
        identifier = payload[cursor:cursor + 8][:4]
        size = struct.unpack(order + "I", payload[cursor + 4:cursor + 8])[0]
        body = cursor + 8
        if body + size > end:
            return
        yield identifier, body, body + size
        cursor = body + size + (size % 2)          # chunks are word-aligned


def _wave_format(payload: bytes, start: int, end: int, *, big: bool
                 ) -> tuple[list[LongTailValue], float]:
    """The `fmt ` chunk's own fields, and the bytes-per-second needed for duration.

    PCMWAVEFORMAT is the first sixteen bytes and every WAVE file has them whatever
    its codec is -- which is the whole point: Python's `wave` module refuses to open
    anything but PCM, so a mu-law recording was recorded as a corrupt file.
    """
    order = ">" if big else "<"
    if end - start < 16:
        raise NotAWaveFile("a `fmt ` chunk shorter than PCMWAVEFORMAT's 16 bytes")
    tag, channels, rate, byte_rate, _align, bits = struct.unpack(
        order + "HHIIHH", payload[start:start + 16])

    codec_tag = tag
    if tag == _WAVE_FORMAT_EXTENSIBLE and end - start >= 40:
        # The SubFormat GUID begins at offset 24 of the chunk and its `Data1` field
        # -- FOUR bytes, stored in the container's own byte order -- is the format
        # tag the wrapper stands for. Reading two bytes instead works on `RIFF` by
        # accident, because the low half of a little-endian word comes first, and
        # reads `0` on `RIFX`, where the high half does.
        codec_tag = struct.unpack(order + "I", payload[start + 24:start + 28])[0]

    values = [LongTailValue(name="format_tag", value=str(tag))]
    codec = _WAVE_CODECS.get(codec_tag)
    if codec is not None:
        values.append(LongTailValue(name="codec", value=codec))
    if channels:
        values.append(LongTailValue(name="channels", value=str(channels)))
    if rate:
        values.append(LongTailValue(name="sample_rate", value=str(rate)))
    if bits:
        values.append(LongTailValue(name="bits_per_sample", value=str(bits)))
    return values, float(byte_rate)


def _info_tags(payload: bytes, start: int, end: int, *, big: bool
               ) -> list[LongTailValue]:
    if payload[start:start + 4] != b"INFO":
        return []                       # a LIST of something else -- `adtl`, `wavl`
    values = []
    for identifier, body, stop in _riff_chunks(payload, start + 4, end, big=big):
        if identifier not in _INFO_TAGS:
            continue
        # An INFO value is a NUL-terminated string. Decoded latin-1 rather than
        # utf-8: the block is defined as bytes and this is the one decoding that
        # cannot raise on a tag some encoder wrote in its own code page.
        text = payload[body:stop].split(b"\x00")[0].decode(
            "latin-1", errors="replace").strip()
        if text:
            values.append(LongTailValue(name=identifier.decode("ascii"), value=text))
    return values


def _read_wav(path: Path) -> LongTailFile:
    """The RIFF container, read as a container.

    WAS `wave.open`, which is a PCM DECODER front-end and refuses every other
    encoding -- `unknown format: 7` on a mu-law file, `not a WAVE file` on a
    big-endian `RIFX`. P5 wrote both down as §2.4's `failed`: a statement that the
    bytes are corrupt, about files nothing is wrong with. Every field §2.9's audio
    bullet names -- "duration, container and codec metadata, creation time, embedded
    tags" -- lives in the `fmt `, `data` and `LIST`/`INFO` chunks, and none of them
    needs the samples decoded.
    """
    payload = path.read_bytes()
    if len(payload) < 12 or payload[:4] not in (b"RIFF", b"RIFX"):
        raise NotAWaveFile(f"{path.name} does not begin with a RIFF header")
    big = payload[:4] == b"RIFX"
    if payload[8:12] != b"WAVE":
        raise NotAWaveFile(
            f"{path.name} is a RIFF container whose form is "
            f"{payload[8:12].decode('ascii', errors='replace')!r}, not WAVE")

    values = [LongTailValue(name="container", value="WAVE")]
    format_values: list[LongTailValue] = []
    tag_values: list[LongTailValue] = []
    byte_rate = 0.0
    data_bytes: int | None = None
    for identifier, start, end in _riff_chunks(payload, 12, len(payload), big=big):
        if identifier == b"fmt " and not format_values:
            format_values, byte_rate = _wave_format(payload, start, end, big=big)
        elif identifier == b"data" and data_bytes is None:
            data_bytes = end - start
        elif identifier == b"LIST":
            tag_values.extend(_info_tags(payload, start, end, big=big))
    if not format_values:
        raise NotAWaveFile(
            f"{path.name} declares a WAVE form and carries no `fmt ` chunk; there "
            "is no channel count, sample rate or codec in it to read")

    values.extend(format_values)
    if data_bytes is not None and byte_rate:
        values.append(LongTailValue(name="duration",
                                    value=f"{data_bytes / byte_rate:.3f}"))
    values.extend(tag_values)
    return LongTailFile(values=tuple(values))


# --------------------------------------------------------------------------- #
# the reader
# --------------------------------------------------------------------------- #

#: Extension -> the function that reads it. Extensions this deployment does not read
#: are absent rather than mapped to a stub, so `read_long_tail` returns `None` for
#: them and P5 records §2.4's `unsupported`. Absent on purpose, each for one reason:
#: `.xls`, `.ppt` and `.msg` are legacy Microsoft binaries (OLE compound files);
#: `.ods`, `.odp` and `.numbers` are packages this deployment ships no reader for;
#: `.mp3` has no container parser in the standard library.
_BY_EXTENSION: dict[str, Callable[[Path], LongTailFile | None]] = {
    ".pptx": _read_pptx,
    ".eml": _read_eml,
    ".mbox": _read_mbox,
    ".ics": _read_ics,
    ".vcf": _read_vcf,
    ".mp4": _read_mp4,
    ".m4a": _read_mp4,
    ".mov": _read_mp4,
    ".wav": _read_wav,
}


#: The spreadsheet half of the same table, kept SEPARATE because these four are the
#: formats that take a ceiling. §2.9 asks a spreadsheet for "visible cell values" and
#: names no limit, and every one of those cells becomes a `text_units` row AND an
#: `evidence` row -- so a data export is the one shape in §2.9's six families that can
#: cost more database than every document a person owns. Which formats have a cell
#: count is format knowledge and belongs here; HOW MANY is a policy and belongs in
#: `cli.py`.
_SPREADSHEETS_BY_EXTENSION: dict[str, Callable[[Path, int], LongTailFile | None]] = {
    ".csv": lambda path, ceiling: _read_delimited(path, ",", ceiling),
    ".tsv": lambda path, ceiling: _read_delimited(path, "\t", ceiling),
    # Instron's tensile-test exports. Comma-delimited and fully quoted, but under an
    # extension that does not declare itself as text -- so `_read_delimited_if_text`,
    # which answers None rather than mojibake when the bytes are something else.
    ".rlt": lambda path, ceiling: _read_delimited_if_text(path, ",", ceiling),
    ".raw": lambda path, ceiling: _read_delimited_if_text(path, ",", ceiling),
    ".xlsx": _read_xlsx,
}


def stdlib_long_tail_reader(*, max_cells: int) -> Callable[..., LongTailFile | None]:
    """Build the `read_long_tail` callable `extractors.dispatch.Readers` takes.

    `max_cells` is REQUIRED AND HAS NO DEFAULT. It is §8.6's kind of number -- a
    ceiling that trades completeness for cost -- and this product keeps every one of
    those in `cli.py`, where the rationale can sit above the value. A default here
    would be a second ceiling nobody tuned, quietly governing the behaviour while the
    documented one governed nothing. Absent means refuse, never guess.

    It applies to spreadsheets and to nothing else, because a spreadsheet is the only
    one of §2.9's six families whose size is unbounded in the unit that costs: a
    presentation has slides, an email has one body, a calendar has events, and a cell
    is a database row. A format with no cells reports `cells_total = None` and its run
    keeps counting entries exactly as before.

    `transcribe` is accepted and ignored, and that is §2.9 being obeyed rather than
    a stub: speech-to-text runs only under P7's explicit privacy and compute policy,
    and B6 (2026-08-20) puts it OUT OF SCOPE for v1 -- "Audio and video stop at
    container metadata." No text this reader returns is `from_speech`, so the
    authorization has nothing to authorize and `UnauthorizedTranscription` cannot
    fire on anything it produced.
    """
    if max_cells < 1:
        raise ValueError(
            f"max_cells={max_cells} would store no cell of any spreadsheet while "
            "still recording the run as `capped`, which reads as a ceiling that was "
            "reached rather than one that admits nothing")

    def read_long_tail(path: Path, *, transcribe: bool = False
                       ) -> LongTailFile | None:
        extension = Path(path).suffix.lower()
        spreadsheet = _SPREADSHEETS_BY_EXTENSION.get(extension)
        if spreadsheet is not None:
            return spreadsheet(Path(path), max_cells)
        reader = _BY_EXTENSION.get(extension)
        return None if reader is None else reader(Path(path))

    return read_long_tail
