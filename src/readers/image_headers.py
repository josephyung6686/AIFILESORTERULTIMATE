# src/readers/image_headers.py
"""E5's `read_image`: the container header, and the properties the image stack reads.

`readers/deployment.py` wired `read_image` to `_no_reader`, so `extract_image`
returned `unsupported` on its second line -- before `filename_pattern` was called and
before `dimension_signal` was called. Both are required keywords P5 declares with no
default precisely so the catalogues can be injected, and in the shipped deployment
they were dead code behind a missing library. Catalogues 02, 03 and 04 need exactly
two things from an image: what format it is, and how many pixels across. The header
parsers below read those, from the first bytes, with the standard library.

**EXIF ARRIVES NOW, and `104` §18.2 gap 18 is why it had to.** The paragraph this
replaces said "What it deliberately does not read. No EXIF", so §2.6's tier-1 band --
*"camera EXIF is strong photo evidence"* -- and the capture-time and GPS halves of
tier 2 were unavailable, while `extract_image` was complete and waiting for them:
`ImageRecord` has carried `exif`, `color` and `software` since it was written and
`ExifValue.kind` is where §2.6's tier is assigned BY THE READER, "because WHICH TAG
IS WHICH is library knowledge". The library is ImageIO, reached through `Quartz`,
which this deployment already ships for `readers/ocr_vision.py` -- so no dependency
is added, no EXIF tag-number table is authored here, and the tag names are the
external vocabulary's own. `00`:32 asks for exactly what it publishes: "EXIF camera
make and model, lens data, ISO, focal length, capture time, GPS, orientation,
software metadata" and "color information where useful".

**HEIC, HEIF, AVIF, TIFF and BMP have branches now, and they are the signature
reader's.** §2.6 requires HEIC explicitly -- "failing to configure the image stack
for HEIC can silently exclude a meaningful portion of an Apple-centric corpus" -- and
`router.SOURCE_TYPE_BY_FORMAT` has routed all five to E5 for a while; what was
missing was a reader that answered for them, so every one fell through to OCR.
`readers/signatures.format_from_magic` already names them from their own bytes and
the router already says which of its tokens are images, so neither a second brand
table nor a format list of this module's own exists here.

**ONE SLOT DECODES PIXELS AND THE REST STILL DO NOT (`98`, the owner's ruling of
11 Sep 2026).** `_published_properties` below still reads properties only and says
why: "decoding the pixels to read a camera's `Make` would spend a 50-megapixel
decode on a string, on every image in a corpus." That argument governs EXIF, colour,
software and orientation exactly as before. §2.6's perceptual hash is the one slot
that is about the pixels and cannot be read from a header at all, so
`readers/perceptual_hash.py` takes the cheap route -- a thumbnail at the nine columns
the hash needs, decoded at a reduced scale by the same ImageIO -- and that module
states the algorithm and the threshold together, as `98` §3.1 requires.

**Quartz is imported inside the call, never at module scope.** `deployment.py`
imports this module eagerly and says at length why it does not import
`readers/ocr_vision.py` that way: Apple's frameworks cost about 4.6s warm and 75s
cold, and a person typing `--list-situations` used to pay all of it. The cost is
paid on the first image and not on `import cli`. The import is NOT guarded: a
missing wheel must arrive by its own name (`tests/test_packaging_declares_what_the_
readers_import.py`), never as §2.4's `unsupported`.

**An absence is still written nowhere (M2), and what IS written is on the run.** P4
forbids an "EXIF absent" observation -- "the run record already says it, and an
absence written as evidence is a value P6 can rank" -- and §2.6 forbids the inference
that would make one dangerous: "the system must not mistake the absence of EXIF for
proof that an image is a screenshot." So a photograph stripped by a messaging app and
a BMP, whose container has nowhere to put EXIF at all, both yield no tags and no row
about it. What this reader CAN say honestly is whether the metadata route ran at all,
and `unread_reason` is that sentence: `extract_image` records it on the extraction run
and marks the run `partial` (see `extractors/image.py`), so a file whose §2.6 slots
were never looked at is never silently a file that had none.

**A format with no branch returns `None`, never an exception** -- §2.4's `unsupported`,
which means the bytes were never looked at, as against `failed`, which means a reader
ran and raised. A truncated header is `None` for the same reason: a record with a zero
dimension would hand `dimension_signal` a pair it must have an opinion about and would
put a number nothing measured into `raw_value`.
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path
from typing import Any, Callable, Mapping

from extractors.image import ExifValue, ImageRecord
from extractors.router import SOURCE_TYPE_BY_FORMAT
from readers.perceptual_hash import perceptual_hash
from readers.signatures import format_from_magic

#: The format tokens this reader answers with. §2.6 names "PNG format" as a tier-3
#: signal and `extract_image` folds case on that one word, so the token has to be the
#: format's customary name and not a MIME type.
PNG, JPEG, GIF, WEBP, SVG = "PNG", "JPEG", "GIF", "WEBP", "SVG"

#: Which of the router's format tokens this reader will answer for when the header
#: parsers below cannot size the file themselves. DERIVED and never a list: the
#: router's operative candidate is the FIRST, which is §2.9's own document order, so
#: `heic`, `heif`, `avif`, `tiff`, `tif` and `bmp` arrive here because the routing
#: table already sends them to E5 -- and `pdf`, `psd` and `mp3`, whose magic numbers
#: `format_from_magic` also knows, do not.
IMAGE_SOURCE_TYPE = "image"

#: §2.6's own names for the three signals a metadata tag can carry. Spelled here
#: because the reader is where the design puts the classification -- `ExifValue.kind`
#: is assigned by the reader, "because WHICH TAG IS WHICH is library knowledge" --
#: and `extractors.image.SIGNAL_TIER` is the gate that holds the spelling: a fourth
#: name, or a misspelling of one of these, raises `UnknownSignal` rather than
#: producing a silently untiered row.
CAMERA_EXIF, CAPTURE_TIME, GPS = "camera EXIF", "capture time", "GPS"

#: The router's spelling of a format, against THIS module's spelling of the same one.
#: Not a format list: it is the correspondence between two vocabularies that already
#: exist, and it exists so one format never gets two names in `image_format`. A JPEG
#: whose start-of-frame sits past the 64 KiB window -- an iPhone photo with a large
#: APP1, XMP and ICC run does -- falls past `_jpeg` to the signature branch, and
#: without this line that file would say `JPG` while every other JPEG said `JPEG`.
#: The formats with no entry take their token upper-cased, which IS their customary
#: name (`heic`, `tiff`, `bmp`).
_OWN_SPELLING: dict[str, str] = {"jpg": JPEG, "jpeg": JPEG, "png": PNG, "gif": GIF,
                                 "webp": WEBP, "svg": SVG}

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_GIF_SIGNATURES = (b"GIF87a", b"GIF89a")

#: JPEG start-of-frame markers. Every SOFn carries the frame header this reader
#: wants; the four excluded values reuse the 0xC. range for tables and restarts and
#: carry no dimensions. Spelled as the standard spells them.
_SOF_MARKERS = frozenset(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}

#: How many bytes of the front of the file any of these headers can need. A JPEG's
#: SOF sits after an arbitrary run of application segments, so the whole file is read
#: only for JPEG, and only up to this ceiling.
_HEADER_BYTES = 1 << 16


class _Truncated(Exception):
    """The bytes ran out inside a header this reader had started to read."""


def _record(image_format: str, width: int, height: int) -> ImageRecord | None:
    if width <= 0 or height <= 0:
        return None
    # `dimensions` is the raw value P5 emits, and the pair has no rendering of its
    # own in any of these headers -- it is two integers in a struct. So the reader
    # renders it, which is the reader's job (P4 D7: the format's own slot name and
    # value come from the library), and renders it one way for every format so that
    # two images of one size never read as two different values.
    return ImageRecord(image_format=image_format, dimensions=f"{width}x{height}",
                       width=width, height=height)


def _png(data: bytes) -> ImageRecord | None:
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise _Truncated("a PNG signature with no IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return _record(PNG, width, height)


def _gif(data: bytes) -> ImageRecord | None:
    if len(data) < 10:
        raise _Truncated("a GIF signature with no logical screen descriptor")
    width, height = struct.unpack("<HH", data[6:10])
    return _record(GIF, width, height)


def _webp(data: bytes) -> ImageRecord | None:
    if len(data) < 30:
        raise _Truncated("a RIFF/WEBP header with no VP8 chunk")
    chunk = data[12:16]
    if chunk == b"VP8 ":
        width, height = struct.unpack("<HH", data[26:30])
        return _record(WEBP, width & 0x3FFF, height & 0x3FFF)
    if chunk == b"VP8L":
        bits = int.from_bytes(data[21:25], "little")
        return _record(WEBP, (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
    if chunk == b"VP8X":
        width = int.from_bytes(data[24:27], "little") + 1
        height = int.from_bytes(data[27:30], "little") + 1
        return _record(WEBP, width, height)
    raise _Truncated(f"a RIFF/WEBP header with an unreadable chunk {chunk!r}")


def _jpeg(data: bytes) -> ImageRecord | None:
    position = 2
    while position + 4 <= len(data):
        if data[position] != 0xFF:
            position += 1
            continue
        marker = data[position + 1]
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            position += 2
            continue
        length = struct.unpack(">H", data[position + 2:position + 4])[0]
        if marker in _SOF_MARKERS:
            if position + 9 > len(data):
                raise _Truncated("a JPEG frame header cut short")
            height, width = struct.unpack(">HH", data[position + 5:position + 9])
            return _record(JPEG, width, height)
        position += 2 + length
    raise _Truncated("a JPEG with no start-of-frame marker in the first 64 KiB")


#: The root element of an SVG document, with whatever a real editor puts in front of
#: it -- an XML declaration, comments, a DOCTYPE -- skipped. Anchored at the START of
#: that run, so a `<svg>` buried inside some other XML document does not make that
#: document an SVG.
_SVG_ROOT = re.compile(
    rb"\A(?:\s|<\?[^>]*\?>|<!--.*?-->|<!DOCTYPE[^\[>]*(?:\[.*?\])?[^>]*>)*"
    rb"<svg(?P<attributes>\s[^>]*)?>", re.DOTALL | re.IGNORECASE)

#: One attribute of that root element. XML allows space either side of the equals and
#: either quote character, and every one of those spellings is on a real disk.
_SVG_ATTRIBUTE = re.compile(
    rb"""(?P<name>[A-Za-z:_][-A-Za-z0-9:_.]*)\s*=\s*(?P<quote>["'])"""
    rb"(?P<value>[\s\S]*?)(?P=quote)")

#: A length SVG states in pixels. `px` is the only unit that is already a pixel count
#: -- `pt`, `mm`, `em` and `%` all need a rendering context this reader does not have,
#: and converting one with an assumed DPI would put a number nothing measured into
#: `raw_value`. Those fall through to the `viewBox`.
_SVG_PIXELS = re.compile(rb"\A\s*([0-9]+(?:\.[0-9]+)?)\s*(?:px)?\s*\Z",
                         re.IGNORECASE)


def _svg_lengths(attributes: bytes) -> tuple[int, int] | None:
    """The canvas, from `width`/`height` and falling back to `viewBox`.

    §2.9's design-and-creative bullet asks for "dimensions **or canvas properties**",
    and an SVG is the format that has both: `width` and `height` are how large it
    should be drawn, `viewBox` is the coordinate space it is drawn in. A percentage
    width is a fraction of a container nothing here can see, so the viewBox answers
    for it -- and when neither states a size, the answer is `None` rather than a zero.
    """
    found = {match.group("name").lower(): match.group("value")
             for match in _SVG_ATTRIBUTE.finditer(attributes)}
    width, height = found.get(b"width"), found.get(b"height")
    if width is not None and height is not None:
        pair = (_SVG_PIXELS.match(width), _SVG_PIXELS.match(height))
        if all(pair):
            return int(float(pair[0].group(1))), int(float(pair[1].group(1)))
    box = found.get(b"viewbox")
    if box is not None:
        numbers = box.replace(b",", b" ").split()
        if len(numbers) == 4:
            try:
                return int(float(numbers[2])), int(float(numbers[3]))
            except ValueError:
                return None
    return None


def _svg(data: bytes) -> ImageRecord | None:
    """An SVG's canvas, read out of the root element's own attributes.

    NO XML PARSER. `xml.etree.ElementTree` is documented as not secure against
    maliciously constructed data and this module's whole contract is that it reads a
    header -- so the root element is matched in the head of the file and an entity
    declaration is bytes walked past, not something a parser expands.
    """
    match = _SVG_ROOT.match(data)
    if match is None:
        return None
    size = _svg_lengths(match.group("attributes") or b"")
    return None if size is None else _record(SVG, *size)


def _from_header(data: bytes) -> ImageRecord | None:
    """Format and pixel dimensions from the first bytes, with the standard library."""
    try:
        if data.startswith(_PNG_SIGNATURE):
            return _png(data)
        if data.startswith(_GIF_SIGNATURES):
            return _gif(data)
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return _webp(data)
        if data[:2] == b"\xff\xd8":
            return _jpeg(data)
        # LAST, because it is the one test that is not a magic number: an SVG is
        # XML text and only its ROOT ELEMENT identifies it. `.psd` and `.ai` are
        # not routed here at all -- `router.IMAGE_CAPABLE_DESIGN_FORMATS` names
        # svg alone, and this is the branch that makes that routing true.
        if _SVG_ROOT.match(data) is not None:
            return _svg(data)
    except (_Truncated, struct.error):
        # §2.4: the bytes stopped being a header this reader can read. That is
        # the same answer as "no library ships for this format" -- nothing was
        # understood -- and it is emphatically not `failed`, which would report
        # a truncated download as a reader defect.
        return None
    return None


def _image_format(data: bytes) -> str | None:
    """The format token these bytes name, when the router calls that token an image.

    This is the HEIC/HEIF/AVIF/TIFF/BMP branch (`104` §18.2 gap 18) and it holds no
    table: `format_from_magic` is the signature reader's own `_MAGIC` and `_BRANDS`,
    which item 21 already made the product's single answer to "what are these bytes",
    and the router's own routing table decides which of those tokens is an image. The
    token is upper-cased because `ImageRecord.image_format` carries the format's
    customary name, which is what §2.6 compares ("PNG format") and what the header
    branches above already answer with.
    """
    token = format_from_magic(data)
    if token is None:
        return None
    candidates = SOURCE_TYPE_BY_FORMAT.get(token, ())
    if candidates[:1] != (IMAGE_SOURCE_TYPE,):
        return None
    return _OWN_SPELLING.get(token, token.upper())


def _rendered(value: Any) -> str:
    """One published value as ONE string, so two images of one value read alike.

    P4 D7 puts the format's own slot name and value in the reader, and RAW-1 forbids
    P5 constructing a raw value -- so the rendering happens once, here, and the same
    way for every tag. A list-valued tag (`ISOSpeedRatings` is one) arrives as an
    `NSArray`, which is iterable and is neither a `list` nor a `tuple`, and whose own
    `str()` is a multi-line Objective-C description; it is joined element by element
    instead. Bytes -- a thumbnail, a maker note -- render as nothing: they are not one
    of §2.6's slots and a raw value of `b'\\xff\\xd8...'` is not evidence about a file.
    """
    if value is None or isinstance(value, (bytes, bytearray, memoryview)):
        return ""
    if isinstance(value, str):
        return value.strip()
    if hasattr(value, "__iter__"):
        return ", ".join(part for part in (_rendered(item) for item in value) if part)
    return str(value).strip()


def _published_properties(path: Path) -> tuple[Mapping[Any, Any] | None, str | None]:
    """What the image stack publishes about this file, or the reason it published none.

    `CGImageSourceGetType` is the same discriminator `readers/ocr_vision.py` argues at
    length: it returns the type identifier ImageIO recognised, or NULL when the bytes
    match no format it knows. NOTHING HERE NAMES A FORMAT, so an `.svg`, an `.eps` or
    a container invented next year is answered without a line being added.

    **Properties only, never `CGImageSourceCreateImageAtIndex`.** The metadata sits in
    the container's header; decoding the pixels to read a camera's `Make` would spend
    a 50-megapixel decode on a string, on every image in a corpus.

    The reason returned on the other branch is `ImageRecord.unread_reason`, which
    `extract_image` puts on the extraction run. It is a statement about the ROUTE --
    "these slots were never looked at" -- and never about the file's contents: a
    container that published no `{Exif}` dictionary and a photograph a messaging app
    stripped are indistinguishable here, and §2.6's own trap 1 is that they must not
    be told apart by guessing.

    Off macOS there is no ImageIO. The header parsers above still size the
    formats they know; this route says the metadata slots were never looked at
    rather than importing a framework that cannot be installed. On darwin a
    missing wheel still raises by name — this function does not catch
    `ImportError`.
    """
    if sys.platform != "darwin":
        return None, (
            "Apple ImageIO is not on this platform, so §2.6's EXIF, "
            "capture-time, GPS, colour and software slots were never looked at")
    import Quartz                                      # noqa: PLC0415 -- see the module docstring
    from Foundation import NSURL                       # noqa: PLC0415

    source = Quartz.CGImageSourceCreateWithURL(
        NSURL.fileURLWithPath_(str(path)), None)
    if source is None or Quartz.CGImageSourceGetType(source) is None:
        return None, ("the image stack recognises no image format in these bytes, so "
                      "§2.6's EXIF, capture-time, GPS, colour and software slots were "
                      "never looked at")
    published = Quartz.CGImageSourceCopyPropertiesAtIndex(source, 0, None)
    if published is None:
        return None, ("the image stack named this file's format but published no "
                      "properties for it, so §2.6's EXIF, capture-time, GPS, colour "
                      "and software slots were never looked at")
    return published, None


def _pixels(published: Mapping[Any, Any] | None) -> tuple[int, int]:
    """§2.6's pixel dimensions, for the formats no header parser above sizes."""
    if published is None:
        return 0, 0
    import Quartz                                      # noqa: PLC0415

    width = published.get(Quartz.kCGImagePropertyPixelWidth)
    height = published.get(Quartz.kCGImagePropertyPixelHeight)
    if width is None or height is None:
        return 0, 0
    return int(width), int(height)


def _metadata(published: Mapping[Any, Any] | None) -> tuple[
        tuple[ExifValue, ...], dict[str, str], dict[str, str]]:
    """§2.6's metadata slots, at the library's own key names, sorted into P5's three.

    **Every key here is `Quartz`'s own published constant, and every ranked kind is
    §2.6's own word.** No tag-number table and no spelling of a tag name is authored
    in this module, which is the condition `ExifValue`'s docstring sets: "EXIF tag
    names are an external, versioned vocabulary - so the reader classifies and P5
    places."

      * `{GPS}` -- §2.6's own tier-2 signal, whole dictionary, every entry, ranked by
        the dictionary it came out of and not by any tag name.
      * Tier 1 is §2.6's OWN FIVE NOUNS and nothing else: "EXIF camera make and
        model, LENS DATA, ISO, FOCAL LENGTH". `camera_tags` below is those five at
        the library's constants for them.

        **AND THE REST OF `{Exif}` IS DELIBERATELY NOT TIER 1.** Defaulting the
        whole dictionary to "camera EXIF" was the first shape of this function and
        it is wrong in the one case §2.6 spends a paragraph on: a macOS screenshot
        PNG carries `{Exif}` holding `PixelXDimension`, `PixelYDimension` and
        `UserComment`, which every encoder writes and no camera is needed for. Under
        the default, that screenshot emitted "strong photo evidence" at tier 1
        beside its tier-3 "PNG format" -- so §2.6's conflicting-signals rule made P6
        abstain on every screenshot in the corpus, which is exactly the file the
        `photos.screenshot-captures` situation exists for.
      * The two date tags §2.6 ranks separately are "capture time".
      * `{TIFF}` -- shared by cameras and by every writer of a TIFF-headed file, so
        `Make` and `Model` are tier 1 through the same five nouns and the rest carry
        no tier, exactly as `ExifValue`'s own `orientation` example does.
      * `Software`, from whichever dictionary carries it -- §2.6's tier-3 screenshot
        signal, and NOT an EXIF tag, so it goes to `software`, the slot
        `extract_image` already tiers. `{PNG}` is walked for this key alone: a
        screenshot is a PNG and this is the one §2.6 slot a PNG chunk carries.
      * `ColorModel`, `Depth`, `ProfileName` -- §2.6's "color information where
        useful".

    Everything else is emitted with `kind=None`: still a row, still §8.4's
    always-local EXIF (`extract_image` signals every member of `exif`, not the
    ranked kinds only), and simply not one of §2.6's three ranked signals.

    Sorted by key so one file always produces one order (`extract_image` already
    sorts `color` and `software`; the EXIF tuple's order is this function's).

    **One name, one row.** `Orientation` is published twice on a HEIC and a TIFF --
    once at the top level and once inside `{TIFF}` -- and `extract_image` addresses
    every metadata row by its tag name, which is the address a model cites with
    `metadata_field_name`. Two rows at one address is an ambiguous citation, so the
    first occurrence wins and the repeat is dropped rather than emitted for P4's D10
    to collapse afterwards.
    """
    if published is None:
        return (), {}, {}
    import Quartz                                      # noqa: PLC0415

    software_key = Quartz.kCGImagePropertyTIFFSoftware
    capture_time_tags = (Quartz.kCGImagePropertyExifDateTimeOriginal,
                         Quartz.kCGImagePropertyExifDateTimeDigitized)
    #: §2.6's five nouns for tier 1 -- "EXIF camera make and model, lens data, ISO,
    #: focal length" -- at the library's own constants. Nothing wider: see the
    #: screenshot paragraph above.
    camera_tags = (Quartz.kCGImagePropertyTIFFMake,
                   Quartz.kCGImagePropertyTIFFModel,
                   Quartz.kCGImagePropertyExifLensMake,
                   Quartz.kCGImagePropertyExifLensModel,
                   Quartz.kCGImagePropertyExifLensSpecification,
                   Quartz.kCGImagePropertyExifISOSpeedRatings,
                   Quartz.kCGImagePropertyExifFocalLength)
    png_dictionary = Quartz.kCGImagePropertyPNGDictionary

    exif: list[ExifValue] = []
    color: dict[str, str] = {}
    software: dict[str, str] = {}

    for key in (Quartz.kCGImagePropertyColorModel, Quartz.kCGImagePropertyDepth,
                Quartz.kCGImagePropertyProfileName):
        value = _rendered(published.get(key))
        if value:
            color[str(key)] = value

    named: set[str] = set()

    def keep(name: str, value: str, kind: str | None) -> None:
        if name in named:
            return
        named.add(name)
        exif.append(ExifValue(name=name, value=value, kind=kind))

    orientation = _rendered(published.get(Quartz.kCGImagePropertyOrientation))
    if orientation:
        keep(str(Quartz.kCGImagePropertyOrientation), orientation, None)

    for dictionary_key, default_kind in (
            (Quartz.kCGImagePropertyExifDictionary, None),
            (Quartz.kCGImagePropertyTIFFDictionary, None),
            (png_dictionary, None),
            (Quartz.kCGImagePropertyGPSDictionary, GPS)):
        tags = published.get(dictionary_key)
        if not tags:
            continue
        for tag in sorted(tags, key=str):
            value = _rendered(tags[tag])
            if not value:
                continue
            if tag == software_key:
                software[str(tag)] = value
                continue
            if dictionary_key == png_dictionary:
                continue                    # walked for `Software` and nothing else
            kind = default_kind
            if tag in capture_time_tags:
                kind = CAPTURE_TIME
            elif tag in camera_tags:
                kind = CAMERA_EXIF
            keep(str(tag), value, kind)

    return tuple(exif), color, software


def header_image_reader() -> Callable[[Path], ImageRecord | None]:
    """The injected `read_image`. Returns `None` for anything it has no branch for."""

    def read_image(path: Path) -> ImageRecord | None:
        with open(path, "rb") as handle:
            data = handle.read(_HEADER_BYTES)
        sized = _from_header(data)
        named = _image_format(data)
        if sized is None and named is None:
            # No header parser recognised these bytes AND their magic number is not
            # one the router calls an image. §2.4's `unsupported`: nothing was
            # understood, and the file is not opened a second time to guess.
            return None

        published, unread_reason = _published_properties(path)
        width, height = ((sized.width, sized.height) if sized is not None
                         else _pixels(published))
        if width <= 0 or height <= 0:
            # The same refusal `_record` makes above, for the formats sized by the
            # image stack rather than by a header parser: a file that claims a brand
            # and holds no image has no dimensions, and `0x0` would be a number
            # nothing measured.
            return None

        exif, color, software = _metadata(published)
        return ImageRecord(
            image_format=sized.image_format if sized is not None else named,
            dimensions=f"{width}x{height}", width=width, height=height,
            exif=exif, color=color, software=software,
            # §2.6's OTHER HASH, and the one slot on this record that is about the
            # pixels rather than the container. `readers/perceptual_hash.py` states
            # the algorithm, the threshold and why this one decode is an exception
            # to the rule two paragraphs of this module's docstring set out. `None`
            # when ImageIO will not decode the bytes, which is one fewer carrier for
            # `_near_families` and never a hash of nothing.
            perceptual_hash=perceptual_hash(path),
            unread_reason=unread_reason)

    return read_image
