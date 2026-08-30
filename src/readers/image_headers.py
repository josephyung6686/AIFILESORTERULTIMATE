# src/readers/image_headers.py
"""E5's `read_image`, from the container header and nothing else.

`readers/deployment.py` wired `read_image` to `_no_reader`, so `extract_image`
returned `unsupported` on its second line -- before `filename_pattern` was called and
before `dimension_signal` was called. Both are required keywords P5 declares with no
default precisely so the catalogues can be injected, and in the shipped deployment
they were dead code behind a missing library. Catalogues 02, 03 and 04 need exactly
two things from an image: what format it is, and how many pixels across. This reads
those, from the header, with the standard library.

**What it deliberately does not read.** No EXIF. §2.6's tier-1 band -- "camera EXIF is
strong photo evidence" -- and the capture-time and GPS halves of tier 2 are therefore
unavailable in this deployment. Saying so is safe because §2.6 already forbids the
inference that would make it dangerous: "the system must not mistake the absence of
EXIF for proof that an image is a screenshot." An absence is read here to route and is
written nowhere (M2). Adding EXIF is a reader change and nothing else: `ImageRecord`
already carries `exif` and `software`, and `ExifValue.kind` is where §2.6's tier is
assigned by the reader, because "WHICH TAG IS WHICH is library knowledge".

**A format with no branch returns `None`, never an exception** -- §2.4's `unsupported`,
which means the bytes were never looked at, as against `failed`, which means a reader
ran and raised. A truncated header is `None` for the same reason: a record with a zero
dimension would hand `dimension_signal` a pair it must have an opinion about and would
put a number nothing measured into `raw_value`.
"""
from __future__ import annotations

import struct
from pathlib import Path
from typing import Callable

from extractors.image import ImageRecord

#: The format tokens this reader answers with. §2.6 names "PNG format" as a tier-3
#: signal and `extract_image` folds case on that one word, so the token has to be the
#: format's customary name and not a MIME type.
PNG, JPEG, GIF, WEBP = "PNG", "JPEG", "GIF", "WEBP"

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


def header_image_reader() -> Callable[[Path], ImageRecord | None]:
    """The injected `read_image`. Returns `None` for anything it has no branch for."""

    def read_image(path: Path) -> ImageRecord | None:
        with open(path, "rb") as handle:
            data = handle.read(_HEADER_BYTES)
        try:
            if data.startswith(_PNG_SIGNATURE):
                return _png(data)
            if data.startswith(_GIF_SIGNATURES):
                return _gif(data)
            if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
                return _webp(data)
            if data[:2] == b"\xff\xd8":
                return _jpeg(data)
        except (_Truncated, struct.error):
            # §2.4: the bytes stopped being a header this reader can read. That is
            # the same answer as "no library ships for this format" -- nothing was
            # understood -- and it is emphatically not `failed`, which would report
            # a truncated download as a reader defect.
            return None
        return None

    return read_image
