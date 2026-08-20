# src/extractors/router.py
"""R - the router (section 2.9).

"The engine should treat the file extension as a ROUTING SIGNAL rather than an
assumption about meaning, inspect the real MIME type or file signature where
possible, and dispatch each file to a type-specific extractor."

`detect_format` is injected and returns one of the format tokens below. A real
deployment maps libmagic's MIME type or macOS's UTType onto that token space, and
THAT mapping belongs to the reader: the MIME and UTType vocabularies are external,
versioned and enormous, and copying a slice of one in here would be an invented table
with no section behind it. What P5 owns is the table P4 explicitly defers to it -
"MIME/signature -> extractor routing table | section 2.9 | P5".

Every key below is a format section 2.9 or section 2.6 names, with ONE exception that
says so out loud: the image and audio/video tokens neither section spells, which are
here on ratification B6 (2026-08-20) and carry a comment marking which part is design
text and which part is inference. Nothing else is a key, and the test that walks this
table makes a silent addition fail rather than a reviewer catch it.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

#: The router's own version, part of the routing decision's identity. Bumped when the
#: table changes: eleven formats that were `unsupported` under 0.1.0 now route, and two
#: tables both stamping "0.1.0" into `extraction_routing.router_version` is exactly the
#: ambiguity section 3.4's cache key exists to prevent.
VERSION = "0.2.0"

#: Section 2.9's eleven bullets and section 2.6's images, as (format token ->
#: source_type candidates). The value is a TUPLE because section 2.9 lists two
#: formats twice and gives each a different field list with no tiebreak - SPEC Open
#: question 2. The operative choice is the FIRST candidate, which is section 2.9's
#: own document order and not a preference of P5's.
SOURCE_TYPE_BY_FORMAT: dict[str, tuple[str, ...]] = {
    # Text documents - "PDF, DOCX, RTF, TXT, Markdown, HTML, EPUB, OpenDocument"
    "pdf": ("text_document", "presentation"),   # also "PDF slide decks" - OQ2
    "docx": ("text_document",),
    "rtf": ("text_document",),
    "txt": ("text_document",),
    "md": ("text_document",),
    "html": ("text_document",),
    "epub": ("text_document",),
    "odt": ("text_document",),
    # Spreadsheets - "XLSX, XLS, CSV, TSV, ODS, Numbers exports"
    "xlsx": ("spreadsheet",),
    "xls": ("spreadsheet",),
    "csv": ("spreadsheet", "code_structured"),  # listed under both - OQ2
    "tsv": ("spreadsheet",),
    "ods": ("spreadsheet",),
    "numbers": ("spreadsheet",),
    # Presentations - "PPTX, PPT, ODP, PDF slide decks"
    "pptx": ("presentation",),
    "ppt": ("presentation",),
    "odp": ("presentation",),
    # Email - "EML, MBOX, MSG, exported mail archives"
    "eml": ("email",),
    "mbox": ("email",),
    "msg": ("email",),
    # Calendar - "ICS"; Contacts - "VCF"
    "ics": ("calendar",),
    "vcf": ("contacts",),
    # Code, notebooks, config, structured data - "Python, JavaScript, SQL, Jupyter
    # notebooks, JSON, YAML, TOML, XML, CSV"
    "py": ("code_structured",),
    "js": ("code_structured",),
    "sql": ("code_structured",),
    "ipynb": ("code_structured",),
    "json": ("code_structured",),
    "yaml": ("code_structured",),
    "yml": ("code_structured",),
    "toml": ("code_structured",),
    "xml": ("code_structured",),
    # Design and creative - "PSD, AI, SVG, Figma exports, CAD files, 3D files".
    # Figma exports, CAD and 3D name no single format token, so none is invented.
    "psd": ("design_creative",),
    "ai": ("design_creative",),
    "svg": ("design_creative",),
    # Images - section 2.6 names HEIC and PNG; the SPEC's fixture set names .jpg.
    "heic": ("image",),
    "png": ("image",),
    "jpg": ("image",),
    "jpeg": ("image",),
    # The rest of a real Mac corpus's images. NOTHING BELOW IS QUOTED FROM THE DESIGN:
    # section 2.6's only two format sentences are "HEIC support must be included
    # explicitly, because failing to configure the image stack for HEIC can silently
    # exclude a meaningful portion of an Apple-centric corpus" and, as a screenshot
    # signal, "exact display resolutions, PNG format, and software metadata may support
    # a screenshot hypothesis". Neither names WebP, GIF, TIFF, BMP, AVIF or HEIF, and
    # section 2.9's own image handling is section 2.6's by reference.
    #
    # They are keys on RATIFICATION grounds instead. B6 (2026-08-20): "Every file type
    # is extracted, and extracted correctly for its own type" - and E5 IS the extractor
    # for their own type, so leaving them `unsupported` asserts something B6's own
    # consequence column calls false ("`unsupported` now means a format genuinely has
    # no extractor, not one deferred by choice"). The corpus argument is section 2.6's:
    # "Messaging platforms and downloaded web images often strip metadata from real
    # photographs" is about the WhatsApp and browser saves that arrive as WebP and GIF,
    # and until they route, section 2.7's OCR policy has no image/native result to key
    # off. INFERENCE, marked as such: B6 was asked about spreadsheets and
    # presentations, and applying its "every file type" clause here is P5 reading a
    # ratification wider than the question that produced it. Raised as product scope
    # by 19-p4-p5-stress.md, "Routing: images and media".
    "webp": ("image",),
    "gif": ("image",),
    "tiff": ("image",),
    "tif": ("image",),      # one format, two customary extensions - as jpg/jpeg above
    "bmp": ("image",),
    "heif": ("image",),     # HEIC's own container; the HEIC sentence is the nearest
    "avif": ("image",),     # design text either of these two has
    # Compressed archives - "Yield their manifests without extraction."
    "zip": ("archive",),
    # Disk images, executables, databases, encrypted containers, damaged files,
    # unknown binary. Section 2.9 names no format; the SPEC's fixtures name two.
    "dmg": ("opaque_binary",),
    "bin": ("opaque_binary",),
    # Audio and video. Section 2.9 names a family and NO format - its bullet is "Audio
    # and video files should yield duration, container and codec metadata, creation
    # time, embedded tags, subtitles or captions where present, and - only under an
    # explicit privacy and compute policy - speech-to-text transcripts" (the design's
    # em dashes rendered as hyphens, as everywhere else here) - and the P5
    # SPEC's routing table records that absence as a literal "-" in its format column
    # while still naming E3 as the family's handler. That was the NEEDS JOSEPH item
    # this comment used to point at, and B6 ANSWERED it on 2026-08-20: "Every file type
    # is extracted, and extracted correctly for its own type - except audio and video,
    # which stop at container metadata for v1", with NEEDS JOSEPH 7 answered the same
    # day - "Speech-to-text is OUT OF SCOPE for v1... Audio and video stop at container
    # metadata." So the family routes, to the handler the SPEC's table already names.
    #
    # `metadata_only` would be the WRONG stop. P4 spells that value as ZERO
    # observations - section 2.9's safe stop for disk images, executables and unknown
    # binaries, which is `opaque_binary` below - and zero observations cannot carry the
    # duration, codec, creation-time and tag fields the bullet above asks for. "Stops
    # at container metadata" is E3 running with `transcription_authorized()` false, not
    # a run that never opened the file.
    #
    # The five tokens are INFERENCE: B6 names no extension any more than section 2.9
    # does. They are what a Mac corpus holds, and deliberately not a codec catalogue.
    "mp3": ("audio_video",),
    "m4a": ("audio_video",),
    "wav": ("audio_video",),
    "mp4": ("audio_video",),
    "mov": ("audio_video",),
}

#: Two formats have a dedicated extractor of their own (sections 2.2 and 2.3).
HANDLER_BY_FORMAT: dict[str, str] = {
    "pdf": "pdf.text",
    "docx": "docx.structure",
}

#: Everything else routes by family. `None` means "no extractor exists for this
#: family", which is a statement about the product, not about the file.
HANDLER_BY_SOURCE_TYPE: dict[str, str | None] = {
    "text_document": "text.structured",
    "spreadsheet": "text.structured",
    "presentation": "text.structured",
    "email": "text.structured",
    "calendar": "text.structured",
    "contacts": "text.structured",
    "code_structured": "text.structured",
    "audio_video": "text.structured",  # E3's long-tail half; the SPEC routing table's
                                       # own handler for the family, kept by B6
    "archive": "archive.manifest",
    "image": "image.metadata",
    "design_creative": None,          # raster and SVG are re-routed below
    "opaque_binary": None,
}

#: Section 2.9's design-and-creative bullet: "at minimum yield filename, format,
#: dimensions ... unsupported proprietary formats should be recorded as
#: indexed-but-unreadable rather than silently treated as empty." The SPEC's routing
#: table reads "E5 (raster/SVG), else `unreadable`".
IMAGE_CAPABLE_DESIGN_FORMATS: tuple[str, ...] = ("svg",)

#: Which of P4's values a file with no handler carries. Section 2.4: an unsupported
#: format is never silently an empty document.
UNROUTED_COMPLETENESS: dict[str, str] = {
    "design_creative": "unreadable",     # M3 - and it still carries metadata rows
    "opaque_binary": "metadata_only",    # section 2.9's deliberate safe stop
}


@dataclass(frozen=True)
class RoutingDecision:
    """Contract out R - "Every file leaves the router with exactly one routing
    decision"."""
    file_id: str
    content_hash: str
    detected_format: str | None
    declared_extension: str
    disagree: bool
    source_type: str | None
    source_type_candidates: tuple[str, ...]
    extractor_name: str | None
    router_version: str
    unrouted_completeness: str | None


def route(*, file_id: str, content_hash: str, path: Path, extension: str,
          detect_format: Callable[[Path], str | None]) -> RoutingDecision:
    """Decide which extractor family handles this file. Reads nothing itself.

    Section 2.9: the detected format wins over the declared extension, and the
    disagreement is recorded rather than discarded.
    """
    detected = detect_format(path)
    declared = extension.lower().lstrip(".")
    operative = detected if detected is not None else declared
    disagree = detected is not None and detected != declared

    candidates = SOURCE_TYPE_BY_FORMAT.get(operative, ())
    source_type = candidates[0] if candidates else None

    handler = HANDLER_BY_FORMAT.get(operative)
    if handler is None and source_type is not None:
        handler = HANDLER_BY_SOURCE_TYPE.get(source_type)
        if (handler is None and source_type == "design_creative"
                and operative in IMAGE_CAPABLE_DESIGN_FORMATS):
            handler = HANDLER_BY_SOURCE_TYPE["image"]

    unrouted = None
    if handler is None:
        unrouted = UNROUTED_COMPLETENESS.get(source_type, "unsupported")

    return RoutingDecision(
        file_id=file_id,
        content_hash=content_hash,
        detected_format=detected,
        declared_extension=extension,
        disagree=disagree,
        source_type=source_type,
        source_type_candidates=candidates,
        extractor_name=handler,
        router_version=VERSION,
        unrouted_completeness=unrouted,
    )


ROUTING_DDL = """
CREATE TABLE IF NOT EXISTS extraction_routing (
    routing_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id                TEXT NOT NULL,
    content_hash           TEXT NOT NULL,
    detected_format        TEXT,
    declared_extension     TEXT NOT NULL,
    disagree               INTEGER NOT NULL,
    source_type            TEXT,
    source_type_candidates TEXT NOT NULL,
    extractor_name         TEXT,
    router_version         TEXT NOT NULL,
    unrouted_completeness  TEXT,
    observed_at            TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS extraction_routing_file
    ON extraction_routing (file_id, content_hash);
"""


def record_routing_decision(conn: sqlite3.Connection,
                            decision: RoutingDecision) -> int:
    """Persist the decision. This is P5's own record, not one of P4's three."""
    cursor = conn.execute(
        "INSERT INTO extraction_routing (file_id, content_hash, detected_format, "
        "declared_extension, disagree, source_type, source_type_candidates, "
        "extractor_name, router_version, unrouted_completeness, observed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (decision.file_id, decision.content_hash, decision.detected_format,
         decision.declared_extension, int(decision.disagree), decision.source_type,
         ",".join(decision.source_type_candidates), decision.extractor_name,
         decision.router_version, decision.unrouted_completeness,
         datetime.now(timezone.utc).isoformat()),
    )
    return cursor.lastrowid


def routing_decisions(conn: sqlite3.Connection, file_id: str,
                      content_hash: str) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM extraction_routing WHERE file_id = ? AND content_hash = ? "
        "ORDER BY routing_id", (file_id, content_hash),
    ).fetchall()
