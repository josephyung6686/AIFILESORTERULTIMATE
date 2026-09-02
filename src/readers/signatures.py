# src/readers/signatures.py
"""§2.9's other half of routing: the real file signature, not just the extension.

    "The engine should treat the file extension as a ROUTING SIGNAL rather than an
    assumption about meaning, INSPECT THE REAL MIME TYPE OR FILE SIGNATURE WHERE
    POSSIBLE, and dispatch each file to a type-specific extractor."

Only the first clause was implemented. `cli._detect_format` answered from the
extension alone, so a file with NO extension had no format, no `source_type` and no
extractor: `route()` returned `extractor_name=None` and the run recorded
`unsupported`. Measured 2026-09-03 by copying four real files to extensionless
names -- a syllabus, a PDF report, a scanned PNG and a spreadsheet -- and running
them through the shipped router:

    grades   source_type=None  extractor=None  unsupported
    report   source_type=None  extractor=None  unsupported
    scan     source_type=None  extractor=None  unsupported
    syllabus source_type=None  extractor=None  unsupported

A census of the owner's own disk puts **1,057 extensionless files** in Desktop,
Downloads and Documents -- against 2,684 routed document files in total. Every one
of them yields filesystem evidence and not one word of content.

**Where this lives, and why it is not in `src/extractors/`.** `router.py` says it
out loud: *"A real deployment maps libmagic's MIME type or macOS's UTType onto that
token space, and THAT mapping belongs to the reader: the MIME and UTType
vocabularies are external, versioned and enormous."* This is that mapping, from the
standard library, in the reader layer where P5's SPEC puts it.

**The protected-container predicate is a REQUIRED argument with no default, and
that is the whole safety story of this module.** `cli._detect_format`'s docstring
gives the reason extension-only was chosen: *"sniffing means opening the file, and
the one class of file this command must never open is decided by PATH
(`is_protected_container`) before any format question is asked."* That reasoning is
correct and is not overturned here -- it is OBEYED, by making it impossible to
build a detector that has not been given the predicate. A protected path is
answered `None` without a single byte read, before the file is opened.

**Strong and weak identifications are different, and conflating them would be a
regression.** A magic number is a POSITIVE identification and outranks the
extension, which is §2.9's rule and is what makes `extraction_routing.disagree`
mean something: a PDF named `notes.txt` is read as a PDF. But "these bytes decode
as text" identifies nothing in particular, and returning `txt` for it would
override the extension on every `.csv`, `.md` and `.ics` on the disk and route them
all to the plain-text handler. So the weak answer is given ONLY when the extension
supplied nothing the router knows. Measured consequence of getting this backwards:
`grades.csv` would stop reaching the spreadsheet reader.

**Nothing here guesses.** A signature this module does not recognise is `None`,
which leaves the file exactly where it was.
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Callable

from extractors.router import SOURCE_TYPE_BY_FORMAT

#: How many bytes a signature test may look at. Every magic number in use is inside
#: the first few dozen; the rest of the window is for the text tests, which need
#: enough of a document to see its opening element or header block.
HEAD_BYTES: int = 8192

#: A file this large is not parsed as JSON however it starts. The JSON test is the
#: one test here that must read the WHOLE file -- a truncated object does not parse
#: -- so it is the one test that needs a ceiling.
MAX_JSON_BYTES: int = 4 * 1024 * 1024

#: Byte-signature -> format token. Every token is a key of the router's own
#: `SOURCE_TYPE_BY_FORMAT`, checked at import below, so a token this table invents
#: is an ImportError rather than a file that routes nowhere.
_MAGIC: tuple[tuple[bytes, str], ...] = (
    (b"%PDF-", "pdf"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"BM", "bmp"),
    (b"II*\x00", "tiff"),
    (b"MM\x00*", "tiff"),
    (b"8BPS", "psd"),
    (b"ID3", "mp3"),
    (b"\xff\xfb", "mp3"),
    (b"\xff\xf3", "mp3"),
    (b"\xff\xf2", "mp3"),
)

#: ISO base-media brands (`ftyp` at offset 4), by the format token each means.
#: ISO/IEC 14496-12 §4.3. One container, many products: a `.heic` photo and a `.mov`
#: screen recording are the same box structure with a different brand.
_BRANDS: dict[bytes, str] = {
    b"heic": "heic", b"heix": "heic", b"heim": "heic", b"heis": "heic",
    b"mif1": "heic", b"msf1": "heif", b"hevc": "heif", b"hevx": "heif",
    b"avif": "avif", b"avis": "avif",
    b"qt  ": "mov",
    b"M4A ": "m4a", b"M4B ": "m4a",
    b"isom": "mp4", b"iso2": "mp4", b"mp41": "mp4", b"mp42": "mp4",
    b"avc1": "mp4", b"dash": "mp4", b"mmp4": "mp4",
}

#: OOXML and ODF are ZIP containers, told apart by which parts they hold. The
#: `mimetype` member is ODF's and EPUB's own answer (OASIS ODF 1.2 §3.3, EPUB OCF
#: §4.1); the OOXML entries are the part every document of that type must have.
_ZIP_MEMBERS: tuple[tuple[str, str], ...] = (
    ("word/document.xml", "docx"),
    ("xl/workbook.xml", "xlsx"),
    ("ppt/presentation.xml", "pptx"),
)
_ZIP_MIMETYPES: dict[bytes, str] = {
    b"application/epub+zip": "epub",
    b"application/vnd.oasis.opendocument.text": "odt",
    b"application/vnd.oasis.opendocument.spreadsheet": "ods",
    b"application/vnd.oasis.opendocument.presentation": "odp",
}

#: Openers that identify a TEXT format as positively as a magic number does. Each
#: one is the format's own required first line: RFC 6350 §6.1.1 for `BEGIN:VCARD`,
#: RFC 5545 §3.4 for `BEGIN:VCALENDAR`, RTF 1.9.1 for `{\\rtf`, and HTML's doctype.
_TEXT_OPENERS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^\s*\{\\rtf", re.IGNORECASE), "rtf"),
    (re.compile(r"^\s*BEGIN:VCARD\s*$", re.IGNORECASE | re.MULTILINE), "vcf"),
    (re.compile(r"^\s*BEGIN:VCALENDAR\s*$", re.IGNORECASE | re.MULTILINE), "ics"),
    (re.compile(r"^\s*<!DOCTYPE\s+html", re.IGNORECASE), "html"),
    (re.compile(r"^\s*<html[\s>]", re.IGNORECASE), "html"),
)

#: An mbox's first line, RFC 4155 §2: `From ` and a sender, with no colon. It is
#: checked before the RFC 5322 header test below, which would otherwise claim it.
_MBOX_OPENER = re.compile(r"^From \S+ ")

#: An RFC 5322 message: a header block of `Name: value` lines that includes at least
#: one of the three headers a message cannot be without, then a blank line. Requiring
#: the blank line is what stops a `key: value` configuration file being read as mail.
_MAIL_HEADERS = re.compile(
    r"\A(?:[A-Za-z][A-Za-z0-9\-]*:[^\n]*\n(?:[ \t][^\n]*\n)*)*"
    r"(?:From|To|Subject|Received|Message-ID):", re.IGNORECASE)

#: Control characters that do not occur in a text document. A byte stream holding
#: one is not text, whatever it decodes to -- this is the test `file(1)` makes and
#: it is the whole of the weak identification below.
_CONTROL = frozenset(range(0, 9)) | frozenset(range(11, 13)) | frozenset(range(14, 32))

_unknown = ({token for _, token in _MAGIC} | set(_BRANDS.values())
            | {token for _, token in _ZIP_MEMBERS} | set(_ZIP_MIMETYPES.values())
            | {token for _, token in _TEXT_OPENERS}
            | {"zip", "xml", "svg", "json", "mbox", "eml", "txt"})
_unknown -= set(SOURCE_TYPE_BY_FORMAT)
if _unknown:
    raise ImportError(
        f"this module names format tokens the router does not route: "
        f"{sorted(_unknown)}. `router.SOURCE_TYPE_BY_FORMAT` is the token space "
        "and a detector answering outside it produces a file that routes nowhere."
    )


def _iso_brand(head: bytes) -> str | None:
    if len(head) < 12 or head[4:8] != b"ftyp":
        return None
    return _BRANDS.get(head[8:12])


def _zip_format(path: Path) -> str:
    """Which ZIP this is. `zip` when it is just a ZIP, which §2.5 handles."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            for member, token in _ZIP_MEMBERS:
                if member in names:
                    return token
            if "mimetype" in names:
                declared = archive.read("mimetype").strip()
                token = _ZIP_MIMETYPES.get(declared)
                if token is not None:
                    return token
    except (zipfile.BadZipFile, OSError, KeyError):
        # A truncated or unreadable ZIP is still a ZIP by its own first four bytes,
        # and §2.5's archive handler is where a file that cannot be opened belongs:
        # it produces a `failed` run naming the reason, which is a fact about the
        # bytes. Returning `None` here would make it `unsupported` instead, which
        # says no reader exists -- a statement about the deployment, and false.
        return "zip"
    return "zip"


def _decoded(head: bytes) -> str | None:
    """The head as text, or None if these bytes are not text.

    A UTF-16 document is text and its bytes are full of NULs, so the BOM is read
    before the control-character test rather than after it.
    """
    for bom, encoding in ((b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be")):
        if head.startswith(bom):
            try:
                return head[2:len(head) // 2 * 2].decode(encoding, errors="strict")
            except UnicodeDecodeError:
                return None
    if any(byte in _CONTROL for byte in head):
        return None
    body = head[3:] if head.startswith(b"\xef\xbb\xbf") else head
    # A multi-byte character cut in half by the window's edge is not a binary file.
    # Each trim is tried in turn rather than three bytes dropped at once: a UTF-8
    # sequence can be short by one, two or three bytes, and dropping a fixed three
    # simply moves the break when the cut was one byte deep. Measured on a document
    # of CJK text, where the fixed drop still failed and called it binary.
    for trim in (0, 1, 2, 3):
        try:
            return body[:len(body) - trim].decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            continue
    return None


def _text_format(text: str, path: Path, size: int) -> str | None:
    """A POSITIVE identification of a text format, or None for "text of some kind"."""
    for pattern, token in _TEXT_OPENERS:
        if pattern.search(text):
            return token
    stripped = text.lstrip()
    if stripped.startswith("<?xml"):
        return "svg" if re.search(r"<svg[\s>]", text, re.IGNORECASE) else "xml"
    if stripped.startswith("<svg"):
        return "svg"
    if _MBOX_OPENER.match(text):
        return "mbox"
    # `\r?\n` on BOTH sides: mail is transmitted with CRLF line endings, so the
    # blank line that ends a header block is `\r\n\r\n` and a pattern looking for
    # `\n[ \t]*\n` finds a `\r` between them and says no. Measured on an RFC 5322
    # message written exactly as a mail client writes one.
    if _MAIL_HEADERS.match(text) and re.search(r"\r?\n[ \t]*\r?\n", text):
        return "eml"
    if stripped[:1] in ("{", "[") and 0 < size <= MAX_JSON_BYTES:
        try:
            json.loads(path.read_text(encoding="utf-8", errors="strict"))
        except (ValueError, OSError, UnicodeDecodeError):
            return None
        return "json"
    return None


def signature_detector(
        *, is_protected_container: Callable[[Path], bool]
) -> Callable[[Path], str | None]:
    """Build the `detect_format` callable `extractors.router.route` takes.

    `is_protected_container` has NO DEFAULT and cannot be omitted. This function
    opens files, and the one class of file that is never opened is decided by PATH
    (11-ops-runtime.md §4b). A default -- even `lambda path: False` -- would be a
    caller who never made the choice, which is the shape of failure the rest of
    this product spells out every time it declines to default a predicate.
    """

    def detect_format(path: Path) -> str | None:
        path = Path(path)
        if is_protected_container(path):
            # Not one byte. §4b: "What is recorded is the container, not its
            # contents", and asking a question about the bytes IS entering it.
            return None

        declared = path.suffix.lower().lstrip(".")
        try:
            size = path.stat().st_size
            with open(path, "rb") as handle:
                head = handle.read(HEAD_BYTES)
        except OSError:
            # Unreadable for a reason that is not this module's to diagnose. The
            # extension still routes, and the extractor that opens it will raise
            # and record §2.4's `failed`, which is the honest place for it.
            return declared if declared in SOURCE_TYPE_BY_FORMAT else None
        if not head:
            return declared if declared in SOURCE_TYPE_BY_FORMAT else None

        for magic, token in _MAGIC:
            if head.startswith(magic):
                return token
        brand = _iso_brand(head)
        if brand is not None:
            return brand
        if head.startswith(b"PK\x03\x04"):
            return _zip_format(path)
        if head.startswith(b"RIFF") and len(head) >= 12:
            return {b"WAVE": "wav", b"WEBP": "webp"}.get(head[8:12])
        if head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            # An OLE compound file: a legacy `.doc`, `.xls`, `.ppt` or `.msg`. WHICH
            # of them is written in the OLE directory's stream names, which this
            # module does not parse. `None` rather than a guess -- and nothing is
            # lost by it, because this deployment ships no reader for any of the
            # four, so a precise answer and no answer both end at `unsupported`.
            return None

        text = _decoded(head)
        if text is None:
            return None
        positive = _text_format(text, path, size)
        if positive is not None:
            return positive
        # THE WEAK ANSWER, and it defers. "These bytes are text" identifies no
        # format, so it must never outrank an extension that does: returning `txt`
        # here unconditionally would route every `.csv`, `.md`, `.ics` and `.vcf`
        # on the disk to the plain-text handler and undo the readers that read them.
        return None if declared in SOURCE_TYPE_BY_FORMAT else "txt"

    return detect_format
