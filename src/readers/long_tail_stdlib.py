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

import csv
import email.utils
import mailbox
import struct
import wave
import zipfile
from datetime import datetime, timedelta, timezone
from email import policy as email_policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Callable, Iterator
from xml.etree import ElementTree

from extractors.long_tail import LongTailEntry, LongTailFile, LongTailText, LongTailValue

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


class PartTooLarge(Exception):
    """A ZIP member declares more uncompressed bytes than this reader will read.

    A statement about the bytes, so it becomes P5's one `failed` run and the scan
    continues -- not a `ContractViolation`, which is a statement about the caller.
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
    return {node.get("Id"): node.get("Target") or ""
            for node in tree.findall(_tag("pkgrel", "Relationship"))}


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
            try:
                custom[int(node.get("numFmtId"))] = node.get("formatCode") or ""
            except (TypeError, ValueError):
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


def _read_xlsx(path: Path) -> LongTailFile:
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
                target = links.get(node.get(_tag("rel", "id")))
                if target:
                    sheets.append((node.get("name") or "",
                                   _resolve("xl/workbook.xml", target)))

        entries: list[LongTailEntry] = []
        texts: list[LongTailText] = []
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
                    if row_number == 1:
                        headers[column] = rendered
                    texts.append(LongTailText(
                        zone="table", text=rendered, entry_ordinal=ordinal,
                        row=row_number, column=column,
                        column_header=headers.get(column)))

        values, iso_dates = _package_properties(archive)
    return LongTailFile(entries=tuple(entries), values=tuple(values),
                        texts=tuple(texts), iso_dates=iso_dates)


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


def _read_delimited(path: Path, delimiter: str) -> LongTailFile:
    """A `.csv` or `.tsv`: one unnamed sheet, every visible cell.

    `utf-8-sig` because a spreadsheet application writes a BOM and a reader that
    keeps it puts an invisible character on the front of the first column header,
    where it silently stops that header matching anything.
    """
    texts: list[LongTailText] = []
    headers: dict[int, str] = {}
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as handle:
        for row_number, row in enumerate(csv.reader(handle, delimiter=delimiter), 1):
            for column, cell in enumerate(row, 1):
                cell = cell.strip()
                if not cell:
                    continue
                if row_number == 1:
                    headers[column] = cell
                texts.append(LongTailText(
                    zone="table", text=cell, entry_ordinal=1, row=row_number,
                    column=column, column_header=headers.get(column)))
    return LongTailFile(entries=(LongTailEntry(kind="sheet", index=1),),
                        texts=tuple(texts))


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
        target = links.get(node.get(_tag("rel", "id")))
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
    for ordinal, message in enumerate(messages, 1):
        identifier = str(message.get("Message-ID") or f"message {ordinal}").strip()
        entries.append(LongTailEntry(kind="entry", label=identifier))
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
    for ordinal, block in enumerate(events, 1):
        properties = [pair for pair in (_property(line) for line in block)
                      if pair is not None]
        identifier = next((v for n, v in properties if n == "UID"), f"event {ordinal}")
        entries.append(LongTailEntry(kind="entry", label=identifier.strip()))
        for name, value in properties:
            rendered = _unescape(value).strip()
            if not rendered:
                continue
            if name == "DESCRIPTION":
                texts.append(LongTailText(zone="notes", text=rendered,
                                          entry_ordinal=ordinal, region=1))
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
    for ordinal, block in enumerate(_blocks(lines, "VCARD"), 1):
        properties = [pair for pair in (_property(line) for line in block)
                      if pair is not None]
        name = next((v for n, v in properties if n == "FN"), None)
        identifier = next((v for n, v in properties if n == "UID"), None)
        entries.append(LongTailEntry(
            kind="entry", label=(identifier or name or f"card {ordinal}").strip()))
        for slot, value in properties:
            rendered = _unescape(value).strip()
            if not rendered:
                continue
            if slot == "NOTE":
                texts.append(LongTailText(zone="notes", text=rendered,
                                          entry_ordinal=ordinal, region=1))
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


def _read_wav(path: Path) -> LongTailFile:
    with wave.open(str(path), "rb") as handle:
        rate = handle.getframerate()
        values = [
            LongTailValue(name="channels", value=str(handle.getnchannels())),
            LongTailValue(name="sample_rate", value=str(rate)),
            LongTailValue(name="sample_width", value=str(handle.getsampwidth())),
        ]
        if rate:
            values.append(LongTailValue(
                name="duration", value=f"{handle.getnframes() / rate:.3f}"))
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
    ".csv": lambda path: _read_delimited(path, ","),
    ".tsv": lambda path: _read_delimited(path, "\t"),
    ".xlsx": _read_xlsx,
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


def stdlib_long_tail_reader() -> Callable[..., LongTailFile | None]:
    """Build the `read_long_tail` callable `extractors.dispatch.Readers` takes.

    `transcribe` is accepted and ignored, and that is §2.9 being obeyed rather than
    a stub: speech-to-text runs only under P7's explicit privacy and compute policy,
    and B6 (2026-08-20) puts it OUT OF SCOPE for v1 -- "Audio and video stop at
    container metadata." No text this reader returns is `from_speech`, so the
    authorization has nothing to authorize and `UnauthorizedTranscription` cannot
    fire on anything it produced.
    """

    def read_long_tail(path: Path, *, transcribe: bool = False
                       ) -> LongTailFile | None:
        reader = _BY_EXTENSION.get(Path(path).suffix.lower())
        return None if reader is None else reader(Path(path))

    return read_long_tail
