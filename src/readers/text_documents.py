# src/readers/text_documents.py
"""`read_text_document` for §2.9's eight text formats and §2.4's structured text.

`deployment.py` wired `read_text_document = read_text_file`, which decoded the bytes
as UTF-8 and returned them. For a `.txt` that is right and stays right. For every
other format routed to this reader it was measurably wrong, and wrong in the
direction the design calls the worst one -- not missing information but false
information, stored as `complete` and read by the recogniser as the document's prose:

    recommendation.rtf   `{\\rtf1\\ansi\\ansicpg1252\\cocoartf2822 ...`  3,257 chars
    registration.html    `<!DOCTYPE html><html><head><style>body {...`     646 chars

The `.rtf` observation was RTF's control words. The `.html` observation carried the
page's `<style>` block and the contents of a `<script>` element -- text no person ever
sees, on a file it now claims to have read. An `.epub` or an `.odt`, both ZIP
containers, decoded to mojibake and were stored the same way. And a `.md` yielded no
headings at all, because the reader that read it *"does not claim to be a Markdown
reader"*: §2.9 asks a text document for "full text, headings, metadata, links, and
structural information", and headings were the half that never arrived.

**Eight formats, because §2.9 names eight.** *"Text documents such as PDF, DOCX, RTF,
TXT, Markdown, HTML, EPUB, and OpenDocument files"* -- PDF and DOCX have extractors of
their own (§2.2, §2.3), and the remaining six are here.

**Standard library only.** HTML is `html.parser`, EPUB and ODT are `zipfile` plus the
same parser, RTF is its own control-word grammar, Markdown is two heading syntaxes.
`pyproject.toml` keeps `dependencies = []` and the `readers` extra does not grow.

**What is decided here and what is not.** A heading style, a tag, an escape sequence,
a declared character set: all library knowledge, and `Region`'s contract puts them in
the reader. Nothing here decides a source type, a completeness, an analysis tier, a
reliability or a zone that is not `heading` -- those are P4's and P5's vocabularies.
"""
from __future__ import annotations

import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable
from xml.etree import ElementTree

from extractors.reading import Region
from extractors.structured_text import StructuralMarker, TextDocument

from readers.long_tail_stdlib import MAX_PART_BYTES, PartTooLarge, UnsafeXml

#: HTML elements whose content is code or styling, never text a person reads. Their
#: contents are dropped rather than emitted: a `<script>` body stored as the
#: document's prose is the recogniser reading a page's tracking snippet as if the
#: author had written it.
#:
#: `head` IS NOT ONE OF THEM, and used to be. Suppressing it wholesale threw away
#: `<title>` -- the page's own name, the line a browser shows in the tab and saves in
#: a bookmark. Measured on the owner's disk: of 207 `.html` files outside vendor
#: directories, 130 yielded not one character, and twenty of those are
#: single-page-application shells whose body is an empty mount point and whose title
#: is the only prose they have. Dropping `head` from this set puts no markup back
#: into the text: `script`, `style` and `noscript` are suppressed by their own
#: entries wherever they sit, and `meta`, `link` and `base` are void elements with no
#: content to emit.
_INVISIBLE_ELEMENTS: frozenset[str] = frozenset(
    {"script", "style", "noscript", "template", "svg"})

#: Elements after which running text starts a new line. Without them `<td>A</td>
#: <td>B</td>` reads as `AB`, which invents a word that is in no document.
_BLOCK_ELEMENTS: frozenset[str] = frozenset({
    "address", "article", "aside", "blockquote", "br", "caption", "div", "dd", "dl",
    "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2", "h3",
    "h4", "h5", "h6", "header", "hr", "li", "main", "nav", "ol", "option", "p",
    "pre", "section", "table", "tbody", "td", "tfoot", "th", "thead", "title", "tr",
    "ul"})

_HEADING_ELEMENTS: tuple[str, ...] = ("h1", "h2", "h3", "h4", "h5", "h6")

#: `<meta charset=...>` and `<meta http-equiv="content-type" content="...">`. The
#: declared encoding is the document's own statement about its bytes, and honouring
#: it is what keeps a Windows-1252 page from arriving full of replacement characters.
_META_CHARSET = re.compile(
    rb"""<meta[^>]*?charset\s*=\s*["']?\s*([A-Za-z0-9_\-]+)""", re.IGNORECASE)

#: Markdown's two heading syntaxes. ATX is `## Heading`, optionally closed with more
#: hashes; Setext underlines the previous line with `===` or `---`. Both are
#: CommonMark §4.2 and §4.3, and neither is a guess about a short line.
_ATX_HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")
_SETEXT_UNDERLINE = re.compile(r"^(=+|-{2,})[ \t]*$")

#: A fenced code block. Its `# comment` lines are not headings, and a reader that
#: missed that would file a shell comment as a document's structure (CommonMark §4.5).
_CODE_FENCE = re.compile(r"^[ \t]*(```|~~~)")

#: §2.4's four structural-indicator classes are `structured_text.py`'s; WHICH FILES
#: are members is Deferred there *"and the reader supplies them"*. These are the
#: supply. Every name is a filename a tool requires by that exact spelling, so the
#: table is a statement about those tools and not a judgement about a project.
_MARKERS_BY_FILENAME: dict[str, str] = {
    ".gitignore": "repository marker", ".gitattributes": "repository marker",
    ".gitmodules": "repository marker", ".hgignore": "repository marker",
    "package.json": "package manifest", "package-lock.json": "package manifest",
    "pyproject.toml": "package manifest", "setup.py": "package manifest",
    "setup.cfg": "package manifest", "requirements.txt": "package manifest",
    "pipfile": "package manifest", "poetry.lock": "package manifest",
    "cargo.toml": "package manifest", "cargo.lock": "package manifest",
    "gemfile": "package manifest", "go.mod": "package manifest",
    "pom.xml": "package manifest", "build.gradle": "package manifest",
    "composer.json": "package manifest", "podfile": "package manifest",
}

#: §2.4's "language where relevant", from the extension. An extension-to-language
#: map is exactly what `Region`'s contract calls library knowledge, and the slot it
#: fills (`structured_text.LANGUAGE_FIELD`) was reachable and permanently empty:
#: no reader had ever supplied a language, so the observation never existed.
_LANGUAGE_BY_EXTENSION: dict[str, str] = {
    ".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".jsx": "JavaScript",
    ".sql": "SQL", ".sh": "Shell", ".rb": "Ruby", ".go": "Go", ".rs": "Rust",
    ".java": "Java", ".c": "C", ".h": "C", ".cpp": "C++", ".cs": "C#",
    ".swift": "Swift", ".m": "Objective-C", ".r": "R", ".php": "PHP",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML", ".toml": "TOML",
    ".xml": "XML", ".css": "CSS", ".ipynb": "Jupyter notebook",
}

#: OpenDocument's text namespace (OASIS ODF 1.2 §3). `text:h` carries the outline
#: level, which is what makes an ODT heading a heading rather than a bold paragraph.
_ODF_TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
_ODF_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"

#: EPUB's container and package namespaces (EPUB 3.2, OCF §3.5 and §5.4).
_OCF = "urn:oasis:names:tc:opendocument:xmlns:container"
_OPF = "http://www.idpf.org/2007/opf"

#: RTF destinations whose contents are never document text: font and colour tables,
#: stylesheets, embedded pictures and objects, and the generator's own signature.
#: RTF 1.9.1 §"Destinations". A reader that emitted them would put a font name and a
#: run of hexadecimal picture data into the text of a letter.
_RTF_SKIPPED_DESTINATIONS: frozenset[str] = frozenset({
    "fonttbl", "colortbl", "stylesheet", "listtable", "listoverridetable",
    "revtbl", "rsidtbl", "generator", "info", "pict", "object", "themedata",
    "colorschememapping", "latentstyles", "datastore", "xmlnstbl", "filetbl",
    "mmathPr", "wgrffmtfilter", "pgptbl", "protusertbl"})

#: RTF control words that produce whitespace rather than a character.
_RTF_WHITESPACE: dict[str, str] = {
    "par": "\n", "line": "\n", "sect": "\n", "page": "\n", "row": "\n",
    "tab": "\t", "cell": "\t", "nestcell": "\t", "lquote": "\u2018",
    "rquote": "\u2019", "ldblquote": "\u201c", "rdblquote": "\u201d",
    "emdash": "\u2014", "endash": "\u2013", "bullet": "\u2022",
    "enspace": " ", "emspace": " ", "~": "\u00a0", "-": "", "_": "\u2011"}

_RTF_CONTROL = re.compile(r"\\([a-zA-Z]+)(-?\d+)? ?|\\'([0-9a-fA-F]{2})|\\(.)")


# --------------------------------------------------------------------------- #
# plain text and Markdown
# --------------------------------------------------------------------------- #

def _decode(payload: bytes, encoding: str = "utf-8") -> str:
    """Bytes as text. `replace` rather than a fallback codec, and deliberately.

    Guessing Windows-1252 for bytes that failed as UTF-8 turns an unreadable
    character into a WRONG one -- a plausible letter in the middle of a word, with
    nothing to mark it. A replacement character is the honest rendering of a byte
    this reader could not name, and it is visible to anything that reads the text.
    Where a format DECLARES its encoding (HTML's `<meta charset>`, RTF's `\\ansicpg`)
    that declaration is used instead, because then nothing is being guessed.
    """
    return payload.decode(encoding, errors="replace")


def _markdown_headings(text: str) -> tuple[Region, ...]:
    """CommonMark's ATX and Setext headings, as `Region`s over `text`.

    Two syntaxes and no third: a heading is a heading because Markdown says so, never
    because a line is short or in title case. Fenced code is skipped, so a shell
    comment inside a block is not filed as a document's structure.
    """
    regions: list[Region] = []
    ordinal = 0
    offset = 0
    fence: str | None = None
    lines = text.split("\n")
    for index, line in enumerate(lines):
        length = len(line) + 1
        opened = _CODE_FENCE.match(line)
        if fence is not None:
            if opened is not None and opened.group(1) == fence:
                fence = None
            offset += length
            continue
        if opened is not None:
            fence = opened.group(1)
            offset += length
            continue

        atx = _ATX_HEADING.match(line)
        if atx is not None and atx.group(2):
            ordinal += 1
            start = offset + line.index(atx.group(2), len(atx.group(1)))
            regions.append(Region(zone="heading", start=start,
                                  end=start + len(atx.group(2)),
                                  ordinal=ordinal, label=atx.group(2)))
        elif (_SETEXT_UNDERLINE.match(line) and index and lines[index - 1].strip()
                and not _ATX_HEADING.match(lines[index - 1])):
            previous = lines[index - 1]
            label = previous.strip()
            ordinal += 1
            start = (offset - length_of(previous)
                     + len(previous) - len(previous.lstrip()))
            regions.append(Region(zone="heading", start=start,
                                  end=start + len(label), ordinal=ordinal,
                                  label=label))
        offset += length
    return tuple(regions)


def length_of(line: str) -> int:
    """One line's span in the source text, its newline included."""
    return len(line) + 1


# --------------------------------------------------------------------------- #
# HTML, and the EPUB documents that are HTML
# --------------------------------------------------------------------------- #

class _VisibleText(HTMLParser):
    """The text a person sees, with `h1`-`h6` recorded as headings.

    `convert_charrefs` is left on, so `&amp;` and `&#8217;` arrive as the characters
    the page displays rather than as their source spelling.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.length = 0
        self.regions: list[Region] = []
        self._suppress = 0
        self._heading: tuple[int, int] | None = None   # (start offset, ordinal)
        self._ordinal = 0

    def _append(self, text: str) -> None:
        if not text:
            return
        self.parts.append(text)
        self.length += len(text)

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _INVISIBLE_ELEMENTS:
            self._suppress += 1
            return
        if tag in _BLOCK_ELEMENTS:
            self._append("\n")
        if tag in _HEADING_ELEMENTS and self._heading is None:
            self._ordinal += 1
            self._heading = (self.length, self._ordinal)

    def handle_startendtag(self, tag: str, attrs) -> None:
        if tag in _BLOCK_ELEMENTS:
            self._append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _INVISIBLE_ELEMENTS:
            self._suppress = max(0, self._suppress - 1)
            return
        if tag in _HEADING_ELEMENTS and self._heading is not None:
            start, ordinal = self._heading
            self._heading = None
            label = "".join(self.parts)[start:self.length].strip()
            if label:
                head = "".join(self.parts)[start:self.length]
                lead = len(head) - len(head.lstrip())
                self.regions.append(Region(zone="heading", start=start + lead,
                                           end=start + lead + len(label),
                                           ordinal=ordinal, label=label))
            else:
                self._ordinal -= 1
        if tag in _BLOCK_ELEMENTS:
            self._append("\n")

    def handle_data(self, data: str) -> None:
        if not self._suppress:
            self._append(data)

    def document(self) -> TextDocument:
        return TextDocument(text="".join(self.parts),
                            headings=tuple(self.regions))


def _html_encoding(payload: bytes) -> str:
    match = _META_CHARSET.search(payload[:4096])
    if match is None:
        return "utf-8"
    declared = match.group(1).decode("ascii", errors="replace")
    try:
        "".encode(declared)
    except LookupError:
        return "utf-8"
    return declared


def _read_html_bytes(payload: bytes, encoding: str | None = None) -> TextDocument:
    parser = _VisibleText()
    parser.feed(_decode(payload, encoding or _html_encoding(payload)))
    parser.close()
    return parser.document()


def _read_html(path: Path) -> TextDocument:
    return _read_html_bytes(path.read_bytes())


# --------------------------------------------------------------------------- #
# RTF
# --------------------------------------------------------------------------- #

def _rtf_codepage(payload: bytes) -> str:
    """RTF's `\\ansicpgN` header, as a Python codec name (RTF 1.9.1 §"Header").

    The document states its own code page, so nothing is guessed: `\\'e9` is `é` in
    1252 and `й` in 1251, and the file is the only thing that knows which.
    """
    match = re.search(rb"\\ansicpg(\d+)", payload[:2048])
    if match is None:
        return "cp1252"
    name = f"cp{int(match.group(1))}"
    try:
        "".encode(name)
    except LookupError:
        return "cp1252"
    return name


def _read_rtf(path: Path) -> TextDocument:
    """RTF's control-word grammar, reduced to the text a person reads.

    No headings: RTF marks one with a paragraph STYLE, and resolving a style means
    reading the stylesheet destination this reader skips. Claiming heading structure
    from a font size would be the inference `Region`'s contract forbids a reader to
    make, so the document arrives as text with no heading regions -- less than a
    `.docx` gives, and true.
    """
    payload = path.read_bytes()
    source = _decode(payload, "latin-1")          # bytes 1:1; \\'hh decoded below
    codepage = _rtf_codepage(payload)

    out: list[str] = []
    pending: bytearray = bytearray()
    # One frame per `{`: how many characters a `\\uN` tells us to skip, and whether
    # this group's text is discarded.
    stack: list[tuple[int, bool]] = [(1, False)]
    skip_chars = 0
    index = 0
    length = len(source)

    def flush() -> None:
        if pending:
            out.append(pending.decode(codepage, errors="replace"))
            pending.clear()

    while index < length:
        character = source[index]
        if character == "{":
            flush()
            stack.append(stack[-1])
            index += 1
            continue
        if character == "}":
            flush()
            if len(stack) > 1:
                stack.pop()
            index += 1
            continue
        if character == "\\":
            match = _RTF_CONTROL.match(source, index)
            if match is None:
                index += 1
                continue
            index = match.end()
            word, parameter, hexed, literal = match.groups()
            if hexed is not None:
                if skip_chars > 0:
                    skip_chars -= 1
                elif not stack[-1][1]:
                    pending.append(int(hexed, 16))
                continue
            if literal is not None:
                flush()
                if literal in ("\\", "{", "}"):
                    if not stack[-1][1]:
                        out.append(literal)
                elif literal == "*":
                    # `{\*\destination ...}` -- an extension whose contents a reader
                    # that does not understand it is required to ignore.
                    stack[-1] = (stack[-1][0], True)
                elif literal == "\n":
                    if not stack[-1][1]:
                        out.append("\n")
                continue
            flush()
            if word == "uc":
                stack[-1] = (int(parameter or 1), stack[-1][1])
                continue
            if word == "u" and parameter is not None:
                code = int(parameter)
                if code < 0:
                    code += 0x10000
                if not stack[-1][1]:
                    out.append(chr(code))
                skip_chars = stack[-1][0]
                continue
            if word in _RTF_SKIPPED_DESTINATIONS:
                stack[-1] = (stack[-1][0], True)
                continue
            if word in _RTF_WHITESPACE and not stack[-1][1]:
                out.append(_RTF_WHITESPACE[word])
            continue
        if character in "\r\n":
            index += 1
            continue
        if skip_chars > 0:
            skip_chars -= 1
            index += 1
            continue
        if not stack[-1][1]:
            pending.extend(character.encode("latin-1"))
        index += 1
    flush()
    return TextDocument(text="".join(out))


# --------------------------------------------------------------------------- #
# OpenDocument and EPUB
# --------------------------------------------------------------------------- #

def _member(archive: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        info = archive.getinfo(name)
    except KeyError:
        return None
    if info.file_size > MAX_PART_BYTES:
        raise PartTooLarge(f"{name} declares {info.file_size} uncompressed bytes")
    return archive.read(info)


def _safe_xml(payload: bytes | None):
    if payload is None:
        return None
    if b"<!DOCTYPE" in payload[:4096].upper() or b"<!ENTITY" in payload.upper():
        raise UnsafeXml("an XML part declares a DTD or an entity; refused unparsed")
    return ElementTree.fromstring(payload)


def _odf_text(node) -> str:
    """One ODF paragraph's text, `text:s` and `text:tab` included.

    ODF encodes a run of spaces as `<text:s text:c="4"/>` rather than as spaces, so a
    reader that took `itertext()` alone would join two words that are apart on screen.
    """
    parts: list[str] = []

    def walk(element) -> None:
        for child in element:
            tag = child.tag
            if tag == f"{{{_ODF_TEXT}}}s":
                parts.append(" " * int(child.get(f"{{{_ODF_TEXT}}}c") or 1))
            elif tag == f"{{{_ODF_TEXT}}}tab":
                parts.append("\t")
            elif tag == f"{{{_ODF_TEXT}}}line-break":
                parts.append("\n")
            else:
                if child.text:
                    parts.append(child.text)
                walk(child)
            if child.tail:
                parts.append(child.tail)

    if element_text := (node.text or ""):
        parts.append(element_text)
    walk(node)
    return "".join(parts)


def _read_odt(path: Path) -> TextDocument:
    """OASIS ODF 1.2: `content.xml`, `text:h` as headings, `text:p` as paragraphs.

    `text:h` carries `text:outline-level`, which is the document's own statement that
    a paragraph is a heading -- the same footing as a Word heading style, and not a
    guess from its size.
    """
    with zipfile.ZipFile(path) as archive:
        tree = _safe_xml(_member(archive, "content.xml"))
    if tree is None:
        return TextDocument(text="")

    parts: list[str] = []
    regions: list[Region] = []
    offset = 0
    ordinal = 0
    for node in tree.iter():
        if node.tag == f"{{{_ODF_TEXT}}}h":
            rendered = _odf_text(node).strip()
            if rendered:
                ordinal += 1
                regions.append(Region(zone="heading", start=offset,
                                      end=offset + len(rendered),
                                      ordinal=ordinal, label=rendered))
                parts.append(rendered + "\n")
                offset += len(rendered) + 1
        elif node.tag in (f"{{{_ODF_TEXT}}}p", f"{{{_ODF_TABLE}}}table-cell"):
            rendered = _odf_text(node)
            if rendered.strip():
                parts.append(rendered + "\n")
                offset += len(rendered) + 1
    return TextDocument(text="".join(parts), headings=tuple(regions))


def _epub_documents(archive: zipfile.ZipFile) -> list[str]:
    """The EPUB's content documents in SPINE order (OCF §3.5, EPUB packages §5.4).

    Reading-order matters: `sorted(namelist())` puts chapter 10 before chapter 2, and
    a book read out of order has its headings numbered against the wrong text.
    """
    container = _safe_xml(_member(archive, "META-INF/container.xml"))
    if container is None:
        return []
    rootfile = container.find(f".//{{{_OCF}}}rootfile")
    if rootfile is None or not rootfile.get("full-path"):
        return []
    opf_path = rootfile.get("full-path")
    package = _safe_xml(_member(archive, opf_path))
    if package is None:
        return []
    base = opf_path.rpartition("/")[0]
    manifest = {item.get("id"): item.get("href") or ""
                for item in package.iter(f"{{{_OPF}}}item")}
    order: list[str] = []
    for reference in package.iter(f"{{{_OPF}}}itemref"):
        href = manifest.get(reference.get("idref"))
        if href:
            order.append(f"{base}/{href}" if base else href)
    return order


def _read_epub(path: Path) -> TextDocument:
    parts: list[str] = []
    regions: list[Region] = []
    offset = 0
    ordinal = 0
    with zipfile.ZipFile(path) as archive:
        for name in _epub_documents(archive):
            payload = _member(archive, name)
            if payload is None:
                continue
            document = _read_html_bytes(payload)
            for region in document.headings:
                ordinal += 1
                regions.append(Region(zone="heading", start=offset + region.start,
                                      end=offset + region.end, ordinal=ordinal,
                                      label=region.label))
            parts.append(document.text)
            offset += len(document.text)
    return TextDocument(text="".join(parts), headings=tuple(regions))


# --------------------------------------------------------------------------- #
# §2.4's structural indicators
# --------------------------------------------------------------------------- #

def _markers_for(path: Path, text: str) -> tuple[StructuralMarker, ...]:
    """§2.4's four classes, for the file in hand. The value is the marker itself.

    A README is recognised by STEM, because `README`, `README.md` and `README.rst`
    are the same convention; a manifest and a repository marker are recognised by
    the whole filename, because those tools require that exact spelling. Notebook
    metadata is read out of the notebook, which is where it is.
    """
    name = path.name.lower()
    markers: list[StructuralMarker] = []
    kind = _MARKERS_BY_FILENAME.get(name)
    if kind is not None:
        markers.append(StructuralMarker(kind=kind, value=path.name))
    elif path.stem.lower() == "readme":
        markers.append(StructuralMarker(kind="README file", value=path.name))

    if path.suffix.lower() == ".ipynb":
        try:
            notebook = json.loads(text)
        except (ValueError, TypeError):
            return tuple(markers)
        if not isinstance(notebook, dict):
            return tuple(markers)
        metadata = notebook.get("metadata")
        metadata = metadata if isinstance(metadata, dict) else {}
        for slot, value in (
                ("nbformat", notebook.get("nbformat")),
                ("kernelspec", (metadata.get("kernelspec") or {}).get("display_name")
                 if isinstance(metadata.get("kernelspec"), dict) else None),
                ("language_info", (metadata.get("language_info") or {}).get("name")
                 if isinstance(metadata.get("language_info"), dict) else None)):
            if value not in (None, ""):
                markers.append(StructuralMarker(kind="notebook metadata",
                                                value=f"{slot}: {value}"))
    return tuple(markers)


# --------------------------------------------------------------------------- #
# the reader
# --------------------------------------------------------------------------- #

#: Extension -> the function that turns those bytes into text and headings. An
#: extension that is absent falls through to plain UTF-8 text, which is the right
#: answer for `.txt` and for every source-code and configuration file §2.4 routes
#: here -- their bytes ARE their text.
_BY_EXTENSION: dict[str, Callable[[Path], TextDocument]] = {}


def _plain(path: Path) -> TextDocument:
    return TextDocument(text=_decode(path.read_bytes()))


def _markdown(path: Path) -> TextDocument:
    text = _decode(path.read_bytes())
    return TextDocument(text=text, headings=_markdown_headings(text))


_BY_EXTENSION.update({
    ".md": _markdown, ".markdown": _markdown, ".mdown": _markdown,
    ".html": _read_html, ".htm": _read_html, ".xhtml": _read_html,
    ".rtf": _read_rtf,
    ".odt": _read_odt,
    ".epub": _read_epub,
})


def stdlib_text_document_reader() -> Callable[[Path], TextDocument]:
    """Build the `read_text_document` callable `extractors.dispatch.Readers` takes.

    It never returns `None`. Every extension the router sends to this reader is one
    whose bytes are text or a container this module opens, so §2.4's `unsupported`
    outcome does not arise here -- and a format that failed to open raises, which is
    §2.4's `failed`: a fact about the bytes, recorded as one, with the scan
    continuing.
    """

    def read_text_document(path: Path) -> TextDocument:
        path = Path(path)
        document = _BY_EXTENSION.get(path.suffix.lower(), _plain)(path)
        markers = _markers_for(path, document.text)
        language = _LANGUAGE_BY_EXTENSION.get(path.suffix.lower())
        if not markers and language is None:
            return document
        return TextDocument(text=document.text, language=language,
                            headings=document.headings,
                            markers=document.markers + markers)

    return read_text_document
